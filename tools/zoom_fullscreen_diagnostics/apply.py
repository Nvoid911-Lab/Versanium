"""Independent generated-source diagnostic overlay. Default is read-only verification."""
from pathlib import Path
import argparse,hashlib,json,subprocess

BUNDLE=Path(__file__).resolve().parent
def verify(root):
    root=root.resolve()
    manifest=json.loads((BUNDLE/'tests/fixtures/manifest.json').read_text())
    status={}
    for relative,entry in manifest['files'].items():
        target=root/relative
        if not target.is_file(): raise RuntimeError('Missing diagnostic input: '+relative)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        if digest==entry['before_sha256']:status[relative]='before'
        elif digest==entry['after_sha256']:status[relative]='after'
        else:raise RuntimeError('Diagnostic input drift: '+relative)
    if len(set(status.values()))!=1:raise RuntimeError('Partial diagnostic installation; refusing mutation')
    return next(iter(status.values()))

def apply(root,write=False):
    root=root.resolve();state=verify(root)
    if state=='after':return 'already_applied'
    patch=(BUNDLE/'diagnostics.patch').read_bytes().replace(b'\r\n',b'\n')
    subprocess.run(['git','-c','core.autocrlf=false','apply','--check','-'],cwd=root,input=patch,check=True)
    if write:
        subprocess.run(['git','-c','core.autocrlf=false','apply','-'],cwd=root,input=patch,check=True)
        if verify(root)!='after':raise RuntimeError('Post-apply bytes mismatch')
    return 'applied' if write else 'verified_not_applied'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--apply',action='store_true');a=p.parse_args()
    print(apply(a.root,a.apply))
