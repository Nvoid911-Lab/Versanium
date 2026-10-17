"""Name an existing signed APK without altering its bytes or publishing anything."""
from pathlib import Path
import argparse,re,shutil


def package(source,output,version,test):
    if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',version):raise ValueError('Invalid Chromium version')
    apks=list(source.glob('*arm64-v8a.apk'))
    if len(apks)!=1 or apks[0].name!=f'{version}-arm64-v8a.apk':
        raise ValueError('Expected exactly the signed arm64 APK for this version')
    if apks[0].stat().st_size==0:raise ValueError('Empty APK')
    output.mkdir(parents=True,exist_ok=True)
    name=f'Versanium-{version}_'+('Test.apk' if test else 'arm64-v8a.apk')
    target=output/name
    if target.exists():raise ValueError('Refusing to overwrite an existing staged APK')
    shutil.copy2(apks[0],target)
    print(target)
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('dist'));p.add_argument('--version',required=True);p.add_argument('--test',action='store_true');a=p.parse_args();package(a.source,a.output,a.version,a.test)
