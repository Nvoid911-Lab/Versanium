"""Compile actual applied decision/dismiss methods with Java doubles; not Android."""
from pathlib import Path
import argparse
import subprocess
import tempfile

p=argparse.ArgumentParser()
p.add_argument('--applied-tree',type=Path,required=True)
p.add_argument('--ecj',type=Path,required=True)
a=p.parse_args()
s=(a.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text()
def method(signature):
    return signature+s.split(signature,1)[1].split('\n    }',1)[0]+'\n    }'
decision=method('private boolean canDoPictureInPicture(boolean checkCurrentMode) {')
dismiss=method('private void dismissActivityIfNeeded(Activity activity, @MetricsEndReason int reason) {').replace('@MetricsEndReason ','')
assert decision.count('webContents.hasActiveEffectivelyFullscreenVideo()')==1
assert decision.count('webContents.isPictureInPictureAllowedForFullscreenVideo()')==1
assert decision.count('canStartPipBasedOnRecentTasks()')==1
assert 'MIN_EXIT_DELAY_MILLIS' in dismiss and 'isPipSessionActive()' in dismiss
fixture='''import java.util.*;
public class PipBranchTest {
static class PackageManager {static String FEATURE_PICTURE_IN_PICTURE="pip";boolean supported=true;boolean hasSystemFeature(String s){return supported;}}
static class Activity {boolean pip,changing,finishing,moved=true;int moves;PackageManager pm=new PackageManager();PackageManager getPackageManager(){return pm;}boolean isInPictureInPictureMode(){return pip;}boolean isChangingConfigurations(){return changing;}boolean isFinishing(){return finishing;}boolean moveTaskToBack(boolean b){moves++;return moved;}}
static class WebContents {boolean full=true,allowed=true;int fullReads,permissionReads;boolean hasActiveEffectivelyFullscreenVideo(){fullReads++;return full;}boolean isPictureInPictureAllowedForFullscreenVideo(){permissionReads++;if(!full)throw new AssertionError("unsafe permission probe");return allowed;}}
static class Log {static void d(Object... a){}static void i(Object... a){}}
static class SystemClock {static long now=100;static long elapsedRealtime(){return now;}}
static class TaskTraits {static int UI_USER_BLOCKING=1;}
static class PostTask {static int posts;static void postDelayedTask(int t,Runnable r,long d){posts++;}}
static class Power {boolean interactive=true;boolean isInteractive(){return interactive;}}
static class SuspendType {static int SYSTEM=1;}
static class MediaSession {int suspends;void suspend(int t){suspends++;}}
Activity mActivity=new Activity();WebContents contents=new WebContents();Power mPowerManager=new Power();MediaSession session=new MediaSession();
boolean recent=true,active=true,mDismissPending,mIsSuspendedForStash,mIsPlaying=true;long mLastOnEnteredTimeMillis;static long MIN_EXIT_DELAY_MILLIS=50;static String TAG="test";
int autoUpdates,exits;List<String> events=new ArrayList<>();
WebContents getWebContents(){return contents;}void assertLibraryLoaderIsInitialized(){}boolean canStartPipBasedOnRecentTasks(){return recent;}
void reportTitaniumYoutubePip(String s){events.add(s);}void updateAutoPictureInPictureStatusIfNeeded(){autoUpdates++;}boolean isPipSessionActive(){return active;}
void onExitedPictureInPicture(int reason){exits++;}MediaSession getMediaSession(){return session;}
'''+decision+dismiss+'''
public static void main(String[] args){int checks=0;
String[] reasons={"decision_no_contents","decision_no_active_fullscreen","decision_video_disallows","decision_device_unsupported","decision_already_in_pip","decision_changing","decision_finishing","decision_recent_task"};
for(int mode=0;mode<9;mode++){PipBranchTest t=new PipBranchTest();switch(mode){case 0:t.contents=null;break;case 1:t.contents.full=false;break;case 2:t.contents.allowed=false;break;case 3:t.mActivity.pm.supported=false;break;case 4:t.mActivity.pip=true;break;case 5:t.mActivity.changing=true;break;case 6:t.mActivity.finishing=true;break;case 7:t.recent=false;break;}
 if(t.canDoPictureInPicture(true)!=(mode==8))throw new AssertionError("decision "+mode);
 if(mode<8&&!t.events.equals(List.of(reasons[mode])))throw new AssertionError(t.events);
 if(t.contents!=null&&(t.contents.fullReads!=1||t.contents.permissionReads!=(mode==1?0:1)))throw new AssertionError("getter count");checks++;
}
PipBranchTest t=new PipBranchTest();t.mActivity.pip=true;if(!t.canDoPictureInPicture(false))throw new AssertionError();checks++;
for(int mode=0;mode<5;mode++){t=new PipBranchTest();PostTask.posts=0;SystemClock.now=100;t.mLastOnEnteredTimeMillis=0;
 if(mode==0)t.active=false;if(mode==1)t.mLastOnEnteredTimeMillis=80;if(mode==3)t.mActivity.moved=false;if(mode==4)t.mPowerManager.interactive=false;
 t.dismissActivityIfNeeded(t.mActivity,6);
 if(t.autoUpdates!=1)throw new AssertionError("extra decision update");
 if(t.mActivity.moves!=((mode==2||mode==3)?1:0))throw new AssertionError("move branch");
 if(t.exits!=((mode==2||mode==3)?1:0))throw new AssertionError("exit branch");
 if(PostTask.posts!=(mode==1?1:0))throw new AssertionError("delay");
 if(t.session.suspends!=(mode==4?1:0))throw new AssertionError("suspend branch");checks++;
}
System.out.println(checks+" actual applied decision/dismiss Java-double cases PASS; not Android integration");
}}
'''
with tempfile.TemporaryDirectory() as directory:
    f=Path(directory)/'PipBranchTest.java';f.write_text(fixture)
    subprocess.run(['java','-jar',str(a.ecj),'-21',str(f)],check=True)
    subprocess.run(['java','-cp',directory,'PipBranchTest'],check=True)
stop=method('public void onStop() {')
assert stop.index('mediaSession.suspend(SuspendType.SYSTEM);') < stop.index('reportTitaniumYoutubePip("stop_suspend_called")')
print('Getter short circuit/count and unchanged dismissal branches verified; suspend completion log is after call')
