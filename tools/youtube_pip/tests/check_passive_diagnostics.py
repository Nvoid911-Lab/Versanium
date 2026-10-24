"""Compile/run the actual added logger method with bounded Java doubles, NOT Android.
Also inspect generated real-source hooks. Does not compile Chromium/JNI or prove device safety.
"""
from pathlib import Path
import argparse,re,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('--applied-tree',type=Path,required=True);p.add_argument('--ecj',type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[3]
s=(a.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text()
method=s.split('    private void reportTitaniumYoutubePip(String stage) {',1)[1].split('\n    private boolean canStartPipBasedOnRecentTasks',1)[0]
method='private void reportTitaniumYoutubePip(String stage) {'+method
for qualified in ['org.chromium.base.CommandLine','org.chromium.url.GURL']:
 method=method.replace(qualified,qualified.rsplit('.',1)[1])
# Deliberately no fullscreen permission, AppOps or task-query API in the doubles:
# the pre-fix diagnostic method fails to compile against this passive boundary.
fixture='''public class DiagnosticTest {
static class CommandLine {static boolean enabled=true;static boolean isInitialized(){return true;}static CommandLine getInstance(){return new CommandLine();}boolean hasSwitch(String s){return enabled;}}
static class LibraryLoader {static LibraryLoader getInstance(){return new LibraryLoader();}boolean isInitialized(){return true;}}
static class GURL {String scheme="https",host="youtube.com";String getScheme(){return scheme;}String getHost(){return host;}}
static class Activity {boolean dead,finishing;boolean isDestroyed(){return dead;}boolean isFinishing(){return finishing;}boolean isInPictureInPictureMode(){return false;}boolean isChangingConfigurations(){return false;}}
static class Tab {boolean dead,privateMode;boolean isDestroyed(){return dead;}boolean isOffTheRecord(){return privateMode;}}
static class Provider {Tab tab=new Tab();Tab get(){return tab;}}
static class WebContents {boolean dead;GURL url=new GURL();boolean isDestroyed(){return dead;}GURL getLastCommittedUrl(){return url;}}
static class Log {static int count;static void i(String tag,String format,Object... args){count++;}}
Activity mActivity=new Activity();Provider mActivityTabProvider=new Provider();WebContents contents=new WebContents();WebContents getWebContents(){return contents;}
String mLastTitaniumPipDiagnostic="";
'''+method+'''
public static void main(String[] args){
for(int mode=0;mode<9;mode++){
 DiagnosticTest d=new DiagnosticTest();Log.count=0;CommandLine.enabled=true;
 switch(mode){case 1:CommandLine.enabled=false;break;case 2:d.mActivity.dead=true;break;case 3:d.mActivity.finishing=true;break;case 4:d.mActivityTabProvider.tab.privateMode=true;break;case 5:d.contents.dead=true;break;case 6:d.contents.url.host="youtube.com.attacker.test";break;case 7:d.contents.url.scheme="http";break;case 8:d.mActivityTabProvider.tab.dead=true;break;}
 d.reportTitaniumYoutubePip("auto_blocked");d.reportTitaniumYoutubePip("auto_blocked");
 if(Log.count!=(mode==0?1:0))throw new AssertionError("mode="+mode);
}
System.out.println("Actual logger method / Java doubles: 9 lifecycle/scope/dedup cases PASS; NOT Android integration");
}}
'''
with tempfile.TemporaryDirectory() as d:
 f=Path(d)/'DiagnosticTest.java';f.write_text(fixture)
 compiler=['java','-jar',str(a.ecj),'-21'] if a.ecj else ['javac']
 subprocess.run(compiler+[str(f)],check=True)
 subprocess.run(['java','-cp',d,'DiagnosticTest'],check=True)
tab=(a.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java').read_text().split('private void applyVersaniumYoutubeCandidate(String stage)',1)[1].split('void didFinishPageLoad',1)[0]
assert 'versanium-youtube-diagnostics' not in tab
assert 'if (!pip && !background) return;' in tab
assert 'contents.applyVersaniumYoutubeCandidate(mobile, null);' in tab
native=(a.applied_tree/'content/browser/renderer_host/render_frame_host_impl.cc').read_text()
scope=native.split('bool RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed',1)[1].split('\n}',1)[0]
assert 'versanium-youtube-diagnostics' not in scope
fixed=native.split('void RenderFrameHostImpl::ExecuteVersaniumYoutubeCandidate',1)[1].split('\n}',1)[0]
assert 'options += u"false";  // Diagnostics is passive Java event logging only.' in fixed
assert 'isPictureInPictureAllowedForFullscreenVideo' not in method
assert 'canStartPipBasedOnRecentTasks' not in method
print('Applied Tab/JNI scope: diagnostics does not authorize injection or callback; source checks PASS')
