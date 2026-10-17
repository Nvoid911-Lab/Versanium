"""Compile production content classes against actual Android classes and SOURCE-DECLARATION-ONLY Chromium projections. No behavioral doubles are executed; no full Chromium/NullAway claim."""
from pathlib import Path
import re,subprocess,hashlib
import argparse, tempfile, zipfile
parser=argparse.ArgumentParser(description="Limited Android type check. Chromium dependencies are declaration-only projections, NOT a full Chromium type check.")
parser.add_argument('--source-tree',type=Path,required=True)
parser.add_argument('--android-jar',type=Path,required=True)
parser.add_argument('--ecj',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
source=args.source_tree;output=args.output_dir;out=output/'api-declarations'
output.mkdir(parents=True,exist_ok=True)
platform=output/'android-platform-classes.jar'
with zipfile.ZipFile(args.android_jar) as src,zipfile.ZipFile(platform,'w',zipfile.ZIP_DEFLATED) as target:
 for name in src.namelist():
  if name.endswith('.class') and (name.startswith('android/') or name.startswith('com/android/') or name.startswith('org/xmlpull/')):
   target.writestr(name,src.read(name))
base='base/android/java/src/org/chromium/base/'
content='content/public/android/java/src/'
records=[
(base+'ContextUtils.java','org.chromium.base','ContextUtils',['getApplicationContext','getAppSharedPreferences'],['android.content.*']),
(base+'ThreadUtils.java','org.chromium.base','ThreadUtils',['assertOnUiThread'],[]),
(base+'Log.java','org.chromium.base','Log',['e'],[]),
(base+'StrictModeContext.java','org.chromium.base','StrictModeContext',['allowDiskReads','close'],[]),
(content+'org/chromium/content_public/browser/WebContents.java','org.chromium.content_public.browser','WebContents',['isDestroyed','getTopLevelNativeWindow'],['org.chromium.ui.base.WindowAndroid']),
(content+'org/chromium/content_public/browser/BrowserContextHandle.java','org.chromium.content_public.browser','BrowserContextHandle',['getNativeBrowserContextPointer'],[]),
(content+'org/chromium/content_public/browser/HostZoomMap.java','org.chromium.content_public.browser','HostZoomMap',['getDefaultZoomLevel','getAllHostZoomLevels','shouldAdjustForOSLevel'],['java.util.Map']),
(content+'org/chromium/content/browser/HostZoomMapImpl.java','org.chromium.content.browser','HostZoomMapImpl',['getEnvironmentHost','getEnvironmentProfileKey','isEnvironmentPrivate','refreshEnvironmentZoom'],['org.chromium.content_public.browser.*']),
('ui/android/java/src/org/chromium/ui/base/WindowAndroid.java','org.chromium.ui.base','WindowAndroid',['getActivity'],['android.app.Activity','java.lang.ref.WeakReference']),
('ui/android/java/src/org/chromium/ui/display/DisplayAndroid.java','org.chromium.ui.display','DisplayAndroid',['getNonMultiDisplay','getDisplayId'],['android.content.Context']),
]
manifest=[]
for path,package,name,methods,imports in records:
 s=(source/path).read_text();decl=[]
 if name=='HostZoomMapImpl':s=s.split('@NativeMethods')[0]
 for method in methods:
  pattern=r'(?m)^\s*((?:public\s+)?(?:static\s+)?[\w<>, ?@.\[\]]+\s+'+method+r'\s*\([^)]*\))\s*(?:\{|;)'
  matches=re.findall(pattern,s)
  assert matches,(path,method)
  matches=list(dict.fromkeys(" ".join(m.split()) for m in matches))
  for match in matches:
   sig=re.sub(r'@\w+(?:\([^)]*\))?\s*','',match).strip()
   sig=' '.join(sig.split())
   if not sig.startswith('public'):sig='public '+sig
   decl.append(sig+' { throw new UnsupportedOperationException("signature-only"); }')
   manifest.append(path+' :: '+sig)
 class_decl='public class '+name+(' implements AutoCloseable' if name=='StrictModeContext' else '')
 target=out/Path(package.replace('.','/'))/(name+'.java');target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text('package '+package+';\n'+''.join('import '+i+';\n' for i in imports)+class_decl+' {\n'+'\n'.join(decl)+'\n}\n')
(output/'java-api-signatures.txt').write_text('\n'.join(manifest)+'\n')
production=Path(__file__).resolve().parents[1]/'java/org/chromium/content_public/browser'
cmd=['java','-jar',str(args.ecj),'-21','-cp',str(platform),'-d',str(output/'classes')]
subprocess.run(cmd+[str(p) for p in out.rglob('*.java')]+[str(p) for p in production.glob('*.java')],check=True)
print('Actual Android API + 3 production content Java classes: limited type compile PASS')
print('Chromium dependencies are declaration-only projections from pinned source; NOT full Chromium/NullAway type checking')
