"""Install reviewed display assets in the generated Chromium tree; retain all identities."""
from pathlib import Path
import argparse,hashlib,json,shutil
from branding import text_edits

REPO=Path(__file__).resolve().parents[2]

def check_assets(repo):
    manifest=repo/'res/versanium/assets.json'
    if not manifest.is_file():
        raise RuntimeError('Original Versanium PNG is not available as a file. Supply it and run tools/versanium/generate_icons.py; do not build with the old/recreated logo.')
    values=json.loads(manifest.read_text())
    for relative,expected in values['files'].items():
        p=(repo/relative).resolve()
        if not p.is_relative_to(repo.resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise RuntimeError(f'Missing or changed Versanium asset: {relative}')
    if hashlib.sha256((repo/'res/versanium/master.png').read_bytes()).hexdigest()!=values['master_sha256']:
        raise RuntimeError('Master PNG digest changed')
    return values


def apply(root,repo):
    values=check_assets(repo)
    edits=text_edits(root,repo)
    # Existing adaptive icon and round icon keep their names, GN entries, and notices.
    launcher=root/'chrome/android/java/res_base/drawable/ic_launcher.xml'
    original=launcher.read_text();anchor='android:drawable="@android:color/white"'
    if original.count(anchor)!=1:raise RuntimeError('Adaptive launcher background anchor changed')
    edits[launcher]=original.replace(anchor,'android:drawable="@android:color/black"')
    round_launcher=(root/'chrome/android/java/res_base/drawable/ic_launcher_round.xml').read_text()
    for ref in ('@mipmap/layered_app_icon_background','@mipmap/layered_app_icon_foreground','@drawable/themed_app_icon'):
        if ref not in round_launcher:raise RuntimeError('Round adaptive icon references changed')
    copies={}
    for relative in values['files']:
        prefix='res/versanium/android/'
        if relative.startswith(prefix):
            destination=root/'chrome/android/java/res_titanium_base'/relative[len(prefix):]
            if not destination.is_file():raise RuntimeError(f'Expected existing GN resource: {destination}')
            copies[destination]=repo/relative
    # All checks precede writes. Namespaces, manifest and signing inputs are never modified.
    for p,s in edits.items():p.write_text(s)
    for target,source in copies.items():shutil.copyfile(source,target)
    print('Versanium resource files updated:',len(edits),'text,',len(copies),'icon files')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-assets',action='store_true');p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args()
    if a.check_assets:check_assets(REPO)
    else:apply(a.root,REPO)
