"""Execute the patched production diagnostic method with explicit Android/Chromium doubles.
Not a Settings/PiP/MediaSession device test or full Chromium type check.
"""
from pathlib import Path
import argparse,subprocess,tempfile
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--applied-tree',required=True,type=Path)
parser.add_argument('--ecj',required=True,type=Path)
args=parser.parse_args()
s=(args.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text()
method=s[s.index('    private String mLastTitaniumPipDiagnostic'):s.index('    private boolean canStartPipBasedOnRecentTasks()')]
with tempfile.TemporaryDirectory(prefix='youtube-pip-diagnostics-') as d:
 root=Path(d)
 support={
 'org/chromium/base/CommandLine.java':'''package org.chromium.base; public class CommandLine { public static boolean ready=true,enabled=false; public static boolean isInitialized(){return ready;} public static CommandLine getInstance(){return new CommandLine();} public boolean hasSwitch(String name){if(!name.equals("titanium-youtube-pip-diagnostics"))throw new AssertionError(name);return enabled;} }''',
 'org/chromium/url/GURL.java':'''package org.chromium.url; public class GURL { public String host="m.youtube.com",scheme="https"; public String getHost(){return host;} public String getScheme(){return scheme;} }''',
 }
 for path,text in support.items():
  p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 harness='''import java.util.*;
class Log {static List<String> entries=new ArrayList<>();static void i(String tag,String format,String record){if(!tag.equals("TitaniumPiP")||!format.equals("%s"))throw new AssertionError();entries.add(record);}}
class LibraryLoader {static boolean ready=true;static LibraryLoader getInstance(){return new LibraryLoader();}boolean isInitialized(){return ready;}}
class PackageManager {static final String FEATURE_PICTURE_IN_PICTURE="pip";boolean hasSystemFeature(String f){return true;}}
class Activity {PackageManager getPackageManager(){return new PackageManager();}boolean isInPictureInPictureMode(){return false;}boolean isChangingConfigurations(){return false;}boolean isFinishing(){return false;}}
class Tab {boolean privateTab;boolean isOffTheRecord(){return privateTab;}}
class Provider {Tab tab=new Tab();int reads;Tab get(){reads++;return tab;}}
class WebContents {boolean destroyed;int reads;org.chromium.url.GURL url=new org.chromium.url.GURL();boolean isDestroyed(){return destroyed;}org.chromium.url.GURL getLastCommittedUrl(){reads++;return url;}boolean hasActiveEffectivelyFullscreenVideo(){return true;}boolean isPictureInPictureAllowedForFullscreenVideo(){return false;}}
public class Harness {Provider mActivityTabProvider=new Provider();Activity mActivity=new Activity();WebContents contents=new WebContents();WebContents getWebContents(){return contents;}
'''+method+'''
static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
public static void main(String[] a){
 Harness h=new Harness();h.reportTitaniumYoutubePip("attempt_blocked");check(h.mActivityTabProvider.reads==0);check(Log.entries.isEmpty());
 org.chromium.base.CommandLine.enabled=true;LibraryLoader.ready=false;h.reportTitaniumYoutubePip("attempt_blocked");check(h.mActivityTabProvider.reads==0);LibraryLoader.ready=true;
 h.mActivityTabProvider.tab.privateTab=true;h.reportTitaniumYoutubePip("attempt_blocked");check(h.contents.reads==0);check(Log.entries.isEmpty());h.mActivityTabProvider.tab.privateTab=false;
 h.contents.destroyed=true;h.reportTitaniumYoutubePip("attempt_blocked");check(h.contents.reads==0);h.contents.destroyed=false;
 for(String host:new String[]{"twitch.tv","youtube.com.evil.test","evil.youtube.com",""}){h.contents.url.host=host;h.reportTitaniumYoutubePip("attempt_blocked");check(Log.entries.isEmpty());}
 h.contents.url.host="m.youtube.com";h.contents.url.scheme="http";h.reportTitaniumYoutubePip("attempt_blocked");check(Log.entries.isEmpty());h.contents.url.scheme="https";
 for(String host:new String[]{"m.youtube.com","www.youtube.com","youtube.com"}){Harness x=new Harness();x.contents.url.host=host;int before=Log.entries.size();x.reportTitaniumYoutubePip("attempt_blocked");check(Log.entries.size()==before+1);x.reportTitaniumYoutubePip("attempt_blocked");check(Log.entries.size()==before+1);x.reportTitaniumYoutubePip("resume");check(Log.entries.size()==before+2);}
 for(String line:Log.entries){check(line.matches("(attempt_blocked|resume) full=true videoAllows=false devicePip=true inPip=false changing=false finishing=false"));}
 System.out.println("Diagnostic method: "+checks+" checks PASS with explicit Android/Chromium doubles; NOT real PiP/Activity verification");
}}
'''
 (root/'Harness.java').write_text(harness)
 subprocess.run(['java','-jar',str(args.ecj),'-21','-d',str(root/'classes'),*[str(p) for p in root.rglob('*.java')]],check=True)
 subprocess.run(['java','-cp',str(root/'classes'),'Harness'],check=True)
