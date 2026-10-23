"""Record reviewed build inputs only; never read keys, env contents or browsing data."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_environment_zoom_revision import validate,CHROMIUM,VANADIUM,VERSION

def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def record(repository,source):
    validate(source,repository)
    args=source/'out/Default/args.gn'
    inputs={}
    for path in ['build.sh','patch.sh','args.gn','tools/check_environment_zoom_revision.py','tools/environment_zoom/chromium.patch','tools/configure_f11_identity.py']:
        inputs[path]=hashlib.sha256((repository/path).read_bytes()).hexdigest()
    for path in sorted((repository/'tools/environment_zoom/java').rglob('*.java')):
        relative=path.relative_to(repository/'tools/environment_zoom/java')
        prefix='content/public/android/java/src' if relative.parts[:4]==('org','chromium','content_public','browser') else 'components/browser_ui/accessibility/android/java/src'
        inputs[str(relative)]=hashlib.sha256((source/prefix/relative).read_bytes()).hexdigest()
    for path in sorted((repository/'tools/environment_zoom/res').rglob('*.xml')):
        relative=path.relative_to(repository/'tools/environment_zoom/res')
        inputs['zoom_resource/'+str(relative)]=hashlib.sha256((source/'components/browser_ui/accessibility/android/java/res'/relative).read_bytes()).hexdigest()
    inputs['bundled_extensions_index']=hashlib.sha256((source/'titanium/dist/bundled.json').read_bytes()).hexdigest()
    for path in sorted((repository/'tools/youtube_pip').glob('*')):
        if path.is_file():inputs[str(path.relative_to(repository))]=hashlib.sha256(path.read_bytes()).hexdigest()
    inputs['clang_binary']=hashlib.sha256((source/'third_party/llvm-build/Release+Asserts/bin/clang').read_bytes()).hexdigest()
    inputs['DEPS']=hashlib.sha256((source/'DEPS').read_bytes()).hexdigest()
    return {'format':1,'version':VERSION,'repository_commit':git(repository,'rev-parse','HEAD').decode().strip(),'chromium_input':CHROMIUM,'vanadium_input':VANADIUM,'patched_chromium_commit':git(source,'rev-parse','HEAD').decode().strip(),'depot_tools_commit':git(repository/'depot_tools','rev-parse','HEAD').decode().strip(),'gn_version':subprocess.check_output(['gn','--version'],cwd=source,text=True).strip(),'generated_gn_sha256':hashlib.sha256(args.read_bytes()).hexdigest(),'tracked_source_diff_sha256':hashlib.sha256(git(source,'diff','HEAD','--')).hexdigest(),'inputs_sha256':inputs}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.write_text(json.dumps(record(a.repository,a.source),indent=2)+'\n')
