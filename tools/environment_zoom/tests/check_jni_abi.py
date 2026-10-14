"""Run pinned jni_zero and compile six JNI signature assertions.
This compiles real generated headers + declaration signatures, NOT Chromium .cc bodies.
Requires a locally supplied patched source tree, JDK/NDK JNI includes, and g++ with C++23.
"""
from pathlib import Path
import argparse
import re
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-tree',type=Path,required=True)
parser.add_argument('--jni-include',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--cxx',default='g++')
args=parser.parse_args();root=args.source_tree;out=args.output_dir
out.mkdir(parents=True,exist_ok=True)
source=root/'content/public/android/java/src/org/chromium/content/browser/HostZoomMapImpl.java'
subprocess.run(['python3',str(root/'third_party/jni_zero/jni_zero.py'),'from-source','--allow-private-called-by-natives',
 '--input-file',str(source),'--shared-header-name','HostZoomMapImpl_shared_jni.h',
 '--unshared-header-name','HostZoomMapImpl_jni.h','--output-dir',str(out),
 '--srcjar-path',str(out/'sources.srcjar')],check=True)
cpp=(root/'content/browser/host_zoom_map_impl.cc').read_text()
signatures=[]
for name in ['GetEnvironmentHost','GetEnvironmentProfileKey','IsEnvironmentPrivate','RefreshEnvironmentZoom']:
 match=re.search(r'static [^\n]+ JNI_HostZoomMapImpl_'+name+r'\([\s\S]*?\)\s*\{',cpp)
 if match is None:raise RuntimeError('Native signature missing: '+name)
 signatures.append(match.group(0).rsplit('{',1)[0].strip()+';')
unit='''#include <string>
#include <type_traits>
#include "base/android/scoped_java_ref.h"
// Forward specialization declaration matched to base/android/jni_string.h; no conversion body test.
namespace jni_zero {
template <> ScopedJavaLocalRef<jobject> ToJniType<std::string>(JNIEnv*, const std::string&);
}
#include "HostZoomMapImpl_jni.h"
namespace content {
'''+ '\n'.join(signatures)+'''
static_assert(std::is_invocable_r_v<std::string, decltype(&JNI_HostZoomMapImpl_GetEnvironmentHost), JNIEnv*, const jni_zero::JavaRef<JWebContents>&>);
static_assert(std::is_invocable_r_v<std::string, decltype(&JNI_HostZoomMapImpl_GetEnvironmentProfileKey), JNIEnv*, const jni_zero::JavaRef<JBrowserContextHandle>&>);
static_assert(std::is_invocable_r_v<bool, decltype(&JNI_HostZoomMapImpl_IsEnvironmentPrivate), JNIEnv*, const jni_zero::JavaRef<JBrowserContextHandle>&>);
static_assert(std::is_invocable_r_v<void, decltype(&JNI_HostZoomMapImpl_RefreshEnvironmentZoom), JNIEnv*, const jni_zero::JavaRef<JWebContents>&>);
static_assert(std::is_invocable_r_v<double, decltype(&Java_HostZoomMapImpl_getEnvironmentZoomLevel), JNIEnv*, const base::android::JavaRef<jobject>&, const std::string&>);
static_assert(std::is_invocable_r_v<bool, decltype(&Java_HostZoomMapImpl_saveEnvironmentZoomLevel), JNIEnv*, const base::android::JavaRef<jobject>&, const std::string&, double>);
}
'''
(out/'abi.cc').write_text(unit)
subprocess.run([args.cxx,'-std=c++23','-fsyntax-only','-I'+str(args.jni_include),
 '-I'+str(root),'-I'+str(out),str(out/'abi.cc')],check=True)
print('Actual JNI generation + six C++ signature checks PASS. .cc body / Android toolchain compilation NOT performed.')
