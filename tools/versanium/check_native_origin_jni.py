"""Generate diagnostic JNI from pinned Python generator; no GN or Chromium compile."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

ROOT=Path(__file__).resolve().parents[2]
JAVA='chrome/android/java/src/org/chromium/chrome/browser/ui/ExclusiveAccessContext.java'

def run(generator,source,output):
    if source.resolve() in output.resolve().parents or generator.resolve() in output.resolve().parents:
        raise RuntimeError('JNI outputs must be separate from input/generator trees')
    ledger=json.loads((ROOT/'docs/versanium/native-origin-jni-generator-hashes.json').read_text())
    for n,h in ledger.items():
        if hashlib.sha256((generator/n).read_bytes()).hexdigest()!=h:
            raise RuntimeError('Generator not fixed156: '+n)
    manifest=json.loads((ROOT/'docs/versanium/config-a-origin-forward-native-manifest.json').read_text())
    expected=manifest['files']['AOriginForwardNative'][JAVA]
    if hashlib.sha256((source/JAVA).read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Not selected diagnostic Java bytes')
    # Generator removes stale headers in its output directory: permit NEW dirs only.
    output.mkdir(parents=False,exist_ok=False)
    subprocess.run(['python3',str(generator/'jni_zero.py'),'from-source',
                    '--input-file',str(source/JAVA),
                    '--shared-header-name','ExclusiveAccessContext_shared_jni.h',
                    '--unshared-header-name','ExclusiveAccessContext_jni.h',
                    '--output-dir',str(output)],check=True,
                   env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    header=(output/'ExclusiveAccessContext_jni.h').read_text()
    start=header.index('static void Java_ExclusiveAccessContext_reportNativeFullscreenDiagnostic(')
    body=header[start:header.index('\n}',start)]
    for expected in ['const ::jni_zero::JavaRef<jobject>& obj',
                     'const ::jni_zero::JavaRef<jobject>& contents',
                     'JniIntWrapper stage','JniIntWrapper depth',
                     '(Lorg/chromium/content_public/browser/WebContents;II)V']:
        if expected not in body:raise RuntimeError('Unexpected JNI signature: '+expected)
    print('Fixed156 generator20 files + diagnostic JNI signature PASS; C++ integration NOT compiled')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['generator-tree','source-tree','output-dir']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();run(a.generator_tree,a.source_tree,a.output_dir)
