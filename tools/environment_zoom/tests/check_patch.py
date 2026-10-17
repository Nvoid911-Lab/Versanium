"""Validate against a locally supplied Chromium 155.0.8059.79 source snapshot.
Apply the repository's selected Vanadium patches only to files touched by zoom,
then check/apply the actual overlay. This is NOT GN/JNI/native compilation.
"""
from pathlib import Path
import argparse
import fnmatch
import importlib.util
import sys
sys.dont_write_bytecode = True
import subprocess
import tempfile
import shutil
import xml.etree.ElementTree as ET

repo = Path(__file__).resolve().parents[3]
bundle = repo/'tools/environment_zoom'
removed = ['*trichrome-apk-build-targets.patch','*trichrome-browser-apk-targets.patch',
 '*detailed-language*.patch','*supported-language*.patch','*javascript-optimizer-site-setting.patch',
 '*javascript-optimizer-settings-UI.patch','*component-updates.patch','*pdf*.patch','*PDF*.patch',
 '*for-content-public*.patch','*toolbar-button*.patch','*configs-from-config-app*.patch',
 '*config-app-parsing*.patch','*new-tab-card*.patch','*predictive-back*.patch']


def run(source,vanadium,output=None):
    paths = [line[len('--- a/'):] for line in (bundle/'chromium.patch').read_text().splitlines()
             if line.startswith('--- a/')]
    spec=importlib.util.spec_from_file_location('apply_environment_zoom',repo/'tools/apply_environment_zoom.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='titanium-zoom-patch-') as temporary:
        root=Path(temporary)
        for path in paths:
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/path,target)
        includes=['--include='+p for p in paths]
        for patch in sorted(vanadium.glob('*.patch')):
            if any(fnmatch.fnmatch(patch.name,p) for p in removed): continue
            text=patch.read_text().replace('VANADIUM','TITANIUM').replace('Vanadium','Titanium').replace('vanadium','titanium')
            result=subprocess.run(['git','apply',*includes,'-'],input=text,text=True,cwd=root,capture_output=True)
            if result.returncode: raise RuntimeError(patch.name+'\n'+result.stderr)
        # A changed anchor must be rejected before ANY file or overlay is written.
        native=root/'content/browser/host_zoom_map_impl.cc'
        pristine=native.read_text();native.write_text(pristine.replace('static void JNI_HostZoomMapImpl_SetZoomLevelForHost(',
              'static void JNI_HostZoomMapImpl_ChangedZoomAnchor('))
        before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
        try:
            module.apply(root,bundle)
        except subprocess.CalledProcessError:
            assert before=={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
        else: raise AssertionError('Changed anchor was silently accepted')
        native.write_text(pristine)
        module.apply(root,bundle)
        for xml in root.rglob('*.xml'): ET.parse(xml)
        assert (root/'content/public/android/java/src/org/chromium/content_public/browser/EnvironmentZoom.java').exists()
        assert (root/'components/browser_ui/accessibility/android/java/src/org/chromium/components/browser_ui/accessibility/EnvironmentZoomSettings.java').exists()
        result=subprocess.run(['git','apply','--reverse','--check',str(bundle/'chromium.patch')],cwd=root)
        assert result.returncode==0
        if output is not None:
            shutil.copytree(root, output)  # Refuse an existing destination; preserve review evidence.
        print('Vanadium-selected patch + environment overlay + XML + changed-anchor rejection PASS')
        print('Native/JNI/GN compilation and real Android behavior remain UNVERIFIED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-tree',required=True,type=Path)
    parser.add_argument('--vanadium-patches',required=True,type=Path)
    parser.add_argument('--output-dir',type=Path,help='Keep the selectively patched files for source/resource review; destination must not exist')
    args=parser.parse_args();run(args.source_tree,args.vanadium_patches,args.output_dir)
