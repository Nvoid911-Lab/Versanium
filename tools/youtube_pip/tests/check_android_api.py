"""Limited compile of the production diagnostic method against real Android API classes.
Chromium dependencies are declaration-only projections from supplied pinned source.
This does NOT compile the full Controller/Chromium or execute Android lifecycle.
"""
from pathlib import Path
import argparse,re,subprocess,tempfile,zipfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--applied-tree',type=Path,required=True)
p.add_argument('--source-tree',type=Path,required=True)
p.add_argument('--extra-source-tree',type=Path,required=True)
p.add_argument('--android-jar',type=Path,required=True)
p.add_argument('--ecj',type=Path,required=True)
a=p.parse_args()
s=(a.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text()
method=s[s.index('    private String mLastTitaniumPipDiagnostic'):s.index('    private boolean canStartPipBasedOnRecentTasks()')]
records=[
 ('base/android/java/src/org/chromium/base/CommandLine.java','org.chromium.base','CommandLine',['isInitialized','getInstance','hasSwitch'],[]),
 ('base/android/java/src/org/chromium/base/library_loader/LibraryLoader.java','org.chromium.base.library_loader','LibraryLoader',['getInstance','isInitialized'],[]),
 ('base/android/java/src/org/chromium/base/Log.java','org.chromium.base','Log',['i'],[]),
 ('chrome/browser/tab/java/src/org/chromium/chrome/browser/tab/Tab.java','org.chromium.chrome.browser.tab','Tab',['isOffTheRecord'],[]),
 ('content/public/android/java/src/org/chromium/content_public/browser/WebContents.java','org.chromium.content_public.browser','WebContents',['isDestroyed','getLastCommittedUrl','hasActiveEffectivelyFullscreenVideo','isPictureInPictureAllowedForFullscreenVideo'],['org.chromium.url.GURL']),
 ('url/android/java/src/org/chromium/url/GURL.java','org.chromium.url','GURL',['getHost','getScheme'],[]),
]
with tempfile.TemporaryDirectory(prefix='youtube-pip-api-') as d:
 root=Path(d);platform=root/'android.jar'
 with zipfile.ZipFile(a.android_jar) as original,zipfile.ZipFile(platform,'w',zipfile.ZIP_DEFLATED) as filtered:
  for name in original.namelist():
   if name.endswith('.class') and name.startswith(('android/','com/android/','org/xmlpull/')):filtered.writestr(name,original.read(name))
 for path,package,name,methods,imports in records:
  file=a.source_tree/path
  if not file.exists():file=a.extra_source_tree/path
  text=file.read_text();decl=[]
  for function in methods:
   signatures=re.findall(r'(?m)^\s*((?:public\s+)?(?:static\s+)?(?:boolean|String|GURL|CommandLine|LibraryLoader|void)\s+'+function+r'\s*\([^)]*\))\s*(?:\{|;)',text)
   assert signatures,(path,function)
   for signature in dict.fromkeys(' '.join(x.split()) for x in signatures):
    signature=re.sub(r'@\w+\s*','',signature).strip()
    if not signature.startswith('public'):signature='public '+signature
    decl.append(signature+' {throw new UnsupportedOperationException("declaration-only");}')
  target=root/Path(package.replace('.','/'))/(name+'.java');target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text('package '+package+';\n'+''.join('import '+i+';\n' for i in imports)+'public class '+name+' {\n'+'\n'.join(decl)+'\n}')
 wrapper='''import android.app.Activity;
import android.content.pm.PackageManager;
import org.chromium.base.Log;
import org.chromium.base.library_loader.LibraryLoader;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.content_public.browser.WebContents;
public class DiagnosticApi {Activity mActivity; Provider mActivityTabProvider; WebContents getWebContents(){throw new UnsupportedOperationException();} static class Provider {Tab get(){throw new UnsupportedOperationException();}}
'''+method+'\n}'
 (root/'DiagnosticApi.java').write_text(wrapper)
 subprocess.run(['java','-jar',str(a.ecj),'-21','-cp',str(platform),'-d',str(root/'classes'),*[str(x) for x in root.rglob('*.java')]],check=True)
 print('Production diagnostic method + actual Android API + pinned Chromium DECLARATION-ONLY projections: limited compile PASS')
 print('Full Controller / NullAway / Chromium type checking / device behavior NOT verified')
