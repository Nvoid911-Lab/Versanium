"""Execute the actual two overlay classes against explicit platform doubles.

This is NOT chrome_java, Android, JNI, ErrorProne or NullAway compilation.
The integration gate is enabled only in a temporary test copy.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

BUNDLE=Path(__file__).resolve().parents[1]
STUBS={
'android/app/Activity.java': '''package android.app;
public class Activity {public boolean pip,finishing,destroyed,changing;public int state=3;
public boolean isInPictureInPictureMode(){return pip;}
public boolean isFinishing(){return finishing;}public boolean isDestroyed(){return destroyed;}
public boolean isChangingConfigurations(){return changing;}public int moves;
public boolean moveTaskToBack(boolean value){moves++;return true;}}''',
'android/os/SystemClock.java': '''package android.os;public class SystemClock {
public static long now=100;public static long elapsedRealtime(){return now;}}''',
'android/net/Uri.java': '''package android.net;import java.net.*;import java.nio.charset.StandardCharsets;
public class Uri {URI u;private Uri(String s){try{u=new URI(s);}catch(Exception e){u=URI.create("");}}
public static Uri parse(String s){return new Uri(s);} public String getScheme(){return u.getScheme();}
public String getHost(){return u.getHost();}public String getPath(){return u.getPath();}
public String getUserInfo(){return u.getUserInfo();}public int getPort(){return u.getPort();}
public String getQueryParameter(String key){String q=u.getRawQuery();if(q==null)return null;
for(String part:q.split("&")){String[] pair=part.split("=",2);
if(URLDecoder.decode(pair[0],StandardCharsets.UTF_8).equals(key))
return pair.length==1?"":URLDecoder.decode(pair[1],StandardCharsets.UTF_8);}return null;}}''',
'org/chromium/base/ThreadUtils.java': '''package org.chromium.base;public class ThreadUtils {
public static void assertOnUiThread(){}}''',
'org/chromium/base/ActivityState.java': '''package org.chromium.base;public class ActivityState {
public static final int RESUMED=3,STOPPED=5;}''',
'org/chromium/base/ApplicationStatus.java': '''package org.chromium.base;public class ApplicationStatus {
public static int getStateForActivity(android.app.Activity a){return a.state;}}''',
'org/chromium/base/task/TaskTraits.java': '''package org.chromium.base.task;
public class TaskTraits {public static final int UI_DEFAULT=0,UI_USER_BLOCKING=1;}''',
'org/chromium/base/task/PostTask.java': '''package org.chromium.base.task;import java.util.*;
public class PostTask {static class Task {long at;Runnable r;Task(long a,Runnable v){at=a;r=v;}}
static List<Task> tasks=new ArrayList<>();public static void reset(){tasks.clear();android.os.SystemClock.now=100;}
public static void postDelayedTask(int traits,Runnable r,long delay){
tasks.add(new Task(android.os.SystemClock.now+delay,r));}
public static void advance(long ms){long end=android.os.SystemClock.now+ms;
while(true){Task next=null;for(Task t:tasks)if(t.at<=end&&(next==null||t.at<next.at))next=t;
if(next==null)break;tasks.remove(next);android.os.SystemClock.now=next.at;next.r.run();}
android.os.SystemClock.now=end;}}''',
'org/chromium/chrome/browser/ChromeTabbedActivity.java': '''package org.chromium.chrome.browser;
public class ChromeTabbedActivity extends android.app.Activity {}''',
'org/chromium/chrome/browser/ActivityTabProvider.java': '''package org.chromium.chrome.browser;
public class ActivityTabProvider {public org.chromium.chrome.browser.tab.Tab tab;
public org.chromium.chrome.browser.tab.Tab get(){return tab;}}''',
'org/chromium/chrome/browser/fullscreen/FullscreenManager.java': '''package org.chromium.chrome.browser.fullscreen;
import java.util.*;import org.chromium.chrome.browser.tab.Tab;
public class FullscreenManager {public int exits;public Tab last;public boolean persistent=true;
public interface Observer {default void onEnterFullscreen(Tab t,FullscreenOptions o){}
default void onExitFullscreen(Tab t){}}
public List<Observer> observers=new ArrayList<>();
public void addObserver(Observer o){observers.add(o);}public void removeObserver(Observer o){observers.remove(o);}
public boolean getPersistentFullscreenMode(){return persistent;}
public void enter(Tab t){for(Observer o:new ArrayList<>(observers))o.onEnterFullscreen(t,new FullscreenOptions());}
public void onExitFullscreen(Tab t){exits++;last=t;for(Observer o:new ArrayList<>(observers))o.onExitFullscreen(t);}}''',
'org/chromium/chrome/browser/fullscreen/FullscreenOptions.java': '''package org.chromium.chrome.browser.fullscreen;
public class FullscreenOptions {}''',
'org/chromium/chrome/browser/tab/Tab.java': '''package org.chromium.chrome.browser.tab;
import java.util.*;import org.chromium.content_public.browser.*;import org.chromium.ui.base.WindowAndroid;
public class Tab {public int id=1;public boolean destroyed;public WebContents wc=new WebContents();
public WindowAndroid window;public String url="https://m.youtube.com/watch?v=one";
public List<TabObserver> observers=new ArrayList<>();
public int getId(){return id;}public boolean isDestroyed(){return destroyed;}
public WebContents getWebContents(){return wc;}public WindowAndroid getWindowAndroid(){return window;}
public org.chromium.url.GURL getUrl(){return new org.chromium.url.GURL(url);}
public void addObserver(TabObserver o){observers.add(o);}public void removeObserver(TabObserver o){observers.remove(o);}
public void commit(boolean same,String next){url=next;for(TabObserver o:new ArrayList<>(observers))
o.onDidFinishNavigationInPrimaryMainFrame(this,new NavigationHandle(same,next));}
public void hide(int reason){for(TabObserver o:new ArrayList<>(observers))o.onHidden(this,reason);}}''',
'org/chromium/chrome/browser/tab/TabObserver.java': '''package org.chromium.chrome.browser.tab;
import org.chromium.content_public.browser.NavigationHandle;import org.chromium.ui.base.WindowAndroid;
public interface TabObserver {
default void onDidFinishNavigationInPrimaryMainFrame(Tab t,NavigationHandle n){}
default void onUrlUpdated(Tab t){}default void onContentChanged(Tab t){}
default void onActivityAttachmentChanged(Tab t,WindowAndroid w){}default void onHidden(Tab t,int r){}
default void onClosingStateChanged(Tab t,boolean c){}default void onCrash(Tab t){}
default void onDestroyed(Tab t){}}''',
'org/chromium/chrome/browser/tab/TabHidingType.java': '''package org.chromium.chrome.browser.tab;
public interface TabHidingType {int CHANGED_TABS=0,ACTIVITY_HIDDEN=1,REPARENTED=2,TAB_SWITCHER_SHOWN=3;}''',
'org/chromium/content_public/browser/WebContents.java': '''package org.chromium.content_public.browser;
import java.util.*;public class WebContents {public boolean destroyed,synchronousExit;
public int domExits;public MediaSession session=new MediaSession();
public org.chromium.ui.base.WindowAndroid window;
public List<WebContentsObserver> observers=new ArrayList<>();
public boolean isDestroyed(){return destroyed;}
public org.chromium.ui.base.WindowAndroid getTopLevelNativeWindow(){return window;}
public void exitFullscreen(){domExits++;if(synchronousExit)signalExit();}
public void signalExit(){for(WebContentsObserver o:new ArrayList<>(observers))
o.didToggleFullscreenModeForTab(false,false);}}''',
'org/chromium/content_public/browser/WebContentsObserver.java': '''package org.chromium.content_public.browser;
public class WebContentsObserver {WebContents wc;
public WebContentsObserver(WebContents w){observe(w);}
public void observe(WebContents w){if(wc!=null)wc.observers.remove(this);wc=w;if(w!=null)w.observers.add(this);}
public void didToggleFullscreenModeForTab(boolean entered,boolean resized){}}''',
'org/chromium/content_public/browser/NavigationHandle.java': '''package org.chromium.content_public.browser;
public class NavigationHandle {public boolean committed=true;boolean same;String url;public NavigationHandle(boolean s,String u){same=s;url=u;}
public boolean hasCommitted(){return committed;}public boolean isSameDocument(){return same;}
public org.chromium.url.GURL getUrl(){return new org.chromium.url.GURL(url);}}''',
'org/chromium/content_public/browser/MediaSession.java': '''package org.chromium.content_public.browser;
public class MediaSession {public int suspends,resumes;public static MediaSession fromWebContents(WebContents w){return w.session;}
public void suspend(int type){suspends++;}public void resume(int type){resumes++;}}''',
'org/chromium/media_session/mojom/MediaSession.java': '''package org.chromium.media_session.mojom;
public class MediaSession {public interface SuspendType {int SYSTEM=1;}}''',
'org/chromium/ui/base/WindowAndroid.java': '''package org.chromium.ui.base;import java.lang.ref.WeakReference;
public class WindowAndroid {public android.app.Activity activity;public WindowAndroid(android.app.Activity a){activity=a;}
public WeakReference<android.app.Activity> getActivity(){return new WeakReference<>(activity);}}''',
'org/chromium/url/GURL.java': '''package org.chromium.url;public class GURL {String s;public GURL(String v){s=v;}
public String getSpec(){return s;}}''',
'org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java': '''package org.chromium.chrome.browser.media;
public class FullscreenVideoPictureInPictureController {public interface MetricsEndReason {
int RESUME=0,CLOSE=2,CRASH=3,NEW_TAB=4,REPARENT=5,LEFT_FULLSCREEN=6,WEB_CONTENTS_LEFT_FULLSCREEN=7,START=8;}}''',
}

def run(jdk, gate_off=False):
    with tempfile.TemporaryDirectory(prefix='versanium-pip-fixture-') as d:
        root=Path(d)
        for path,text in STUBS.items():
            p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        # Execute the exact composed VIDEO dismiss methods, rather than a copied routing model.
        from test_bundle import BundleTest
        composed=root/'composed';composed.mkdir()
        test=BundleTest();test.fixture(composed);test.installer().apply(composed)
        video=(composed/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text(encoding='utf-8')
        start=video.index('    private void dismissActivityIfNeeded(')
        end=video.index('    /**',start)
        methods=video[start:end].replace('@MetricsEndReason ', '')
        stub=root/'org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'
        header=stub.read_text()[:-1]
        imports='''import android.app.Activity;import android.os.SystemClock;
import org.chromium.build.annotations.Nullable;import org.chromium.chrome.browser.tab.Tab;
import org.chromium.content_public.browser.*;import org.chromium.base.task.*;
import org.chromium.media_session.mojom.MediaSession.SuspendType;
'''
        header=header.replace('public class FullscreenVideo',imports+'public class FullscreenVideo')
        stub.write_text(header+'''
static final String TAG="fixture";static final long MIN_EXIT_DELAY_MILLIS=500;
static class Log {static void i(String tag,String message){}}
static class Power {boolean interactive=true;boolean isInteractive(){return interactive;}}
final Power mPowerManager=new Power();boolean mDismissPending,mIsSuspendedForStash,mIsPlaying=true;
long mLastOnEnteredTimeMillis=100;VersaniumYouTubePictureInPictureController mVersaniumPip;
java.util.List<Runnable> callbacks=new java.util.ArrayList<>();int dismisses;
Runnable update=()->{};boolean isPipSessionActive(){return !callbacks.isEmpty();}
void updateAutoPictureInPictureStatusIfNeeded(){update.run();}
MediaSession getMediaSession(){return mVersaniumPip.ownerMediaSession();}
void onExitedPictureInPicture(int reason){dismisses++;leave();}
void leave(){mVersaniumPip.drainLeaveCallbacks(callbacks);}
void dismiss(Activity a,int reason,Tab tab,WebContents wc){dismissActivityIfNeeded(a,reason,tab,wc);}
'''+methods+'}')
        shutil.rmtree(composed)
        for name in ('NullMarked','Nullable'):
            p=root/f'org/chromium/build/annotations/{name}.java';p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('package org.chromium.build.annotations;import java.lang.annotation.*;'
                         '@Target({ElementType.TYPE_USE,ElementType.TYPE,ElementType.METHOD,ElementType.FIELD,ElementType.PARAMETER})'
                         f'public @interface {name} {{}}')
        for src in (BUNDLE/'java').rglob('*.java'):
            p=root/src.relative_to(BUNDLE/'java');p.parent.mkdir(parents=True,exist_ok=True)
            text=src.read_text()
            for value in ('true','false'):
                text=text.replace('static final boolean ENABLED = '+value+';',
                                  'static final boolean ENABLED = '+('false' if gate_off else 'true')+';')
            p.write_text(text)
        target=root/'org/chromium/chrome/browser/media/Phase1FixtureTest.java'
        if gate_off:
            target.write_text('''package org.chromium.chrome.browser.media;
import org.chromium.chrome.browser.*;import org.chromium.chrome.browser.tab.*;
import org.chromium.chrome.browser.fullscreen.*;import org.chromium.ui.base.*;
public class Phase1FixtureTest {public static void main(String[] a){
ChromeTabbedActivity h=new ChromeTabbedActivity();ActivityTabProvider tabs=new ActivityTabProvider();
Tab t=new Tab();t.window=new WindowAndroid(h);t.wc.window=t.window;tabs.tab=t;
FullscreenManager fm=new FullscreenManager();
VersaniumYouTubePictureInPictureController c=new VersaniumYouTubePictureInPictureController(
h,tabs,fm,()->{throw new AssertionError("gate-off cleanup");},
()->{throw new AssertionError("gate-off confirmation");},
(reason,tab,wc)->{throw new AssertionError("gate-off terminal");});
assert c.beginEntry(t,true)==0;assert fm.observers.isEmpty();
c.updateCandidate(t,true);h.pip=true;assert c.onFrameworkEntered(true);
assert !VersaniumYouTubePictureInPictureController.preserveOnHidden(h,t,t,1);
assert !c.ownsMediaRouting();assert c.entryTab(t)==t;
c.onStop();c.onResume();c.onDestroy();assert t.wc.domExits==0;assert t.wc.session.suspends==0;
System.out.println("PASS: default-off fixture");}}''')
        else:
            shutil.copyfile(Path(__file__).with_name('Phase1FixtureTest.java'),target)
        args=root/'sources.txt'
        args.write_text('\n'.join('"'+p.as_posix()+'"' for p in root.rglob('*.java')))
        subprocess.run([str(jdk/'bin/javac.exe'),'-Xlint:all','-Werror','-d',str(root/'classes'),
                        '@'+str(args)],check=True)
        subprocess.run([str(jdk/'bin/java.exe'),'-ea','-cp',str(root/'classes'),
                        'org.chromium.chrome.browser.media.Phase1FixtureTest'],check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--jdk',required=True,type=Path)
    parser.add_argument('--gate-off',action='store_true')
    args=parser.parse_args();run(args.jdk,args.gate_off)
