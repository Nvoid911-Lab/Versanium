"""Actual transformed Java fragments + doubles; not Chromium Android integration."""
from pathlib import Path
import argparse,importlib.util,subprocess,tempfile
p=argparse.ArgumentParser();p.add_argument('--applied-tree',type=Path,required=True);p.add_argument('--original',type=Path,required=True);p.add_argument('--ecj',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('origin',repo/'tools/apply_fullscreen_origin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=a.original.read_text();actual=(a.applied_tree/m.BASE_PATH).read_text()
assert m.transform(original)==actual
try:m.transform(actual);raise AssertionError('repeat accepted')
except RuntimeError:pass
try:m.transform(original.replace('mFullscreenManagerDelegate.onExitFullscreen(mTab);','changed();'));raise AssertionError('drift accepted')
except RuntimeError:pass
remaining='\n'.join(line for line in actual.splitlines() if 'reportFullscreenExitOrigin(mActivity,' not in line)+'\n'
assert remaining==original  # Every behavior statement/condition remains byte-identical.
for needle in ['isInPictureInPictureMode()', 'isDisplayEdgeToEdgeFullscreenFeatureEnabledOn2DDevice()', 'sEnableExclusiveAccessManager.isEnabled()']:
 assert actual.count(needle)==original.count(needle)
signature='public void onMultiWindowModeChanged(boolean isInMultiWindowMode) {'
method=signature+actual.split(signature,1)[1].split('\n        }',1)[0]+'\n}'
method=method.replace('org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController.','Reporter.')
java='''import java.util.*;
public class OriginTest {
static class Reporter {static List<String> events=new ArrayList<>();static void reportFullscreenExitOrigin(Object a,Object t,String label){events.add(label);}}
static class Flag {boolean enabled;boolean isEnabled(){return enabled;}}
static class ChromeFeatureList {static Flag sEnableExclusiveAccessManager=new Flag();}
static class Activity {boolean pip;int reads;boolean isInPictureInPictureMode(){reads++;return pip;}}
static class Delegate {int exits;void onExitFullscreen(Object t){exits++;}}
Activity mActivity=new Activity();Object mTab=new Object(),mTabInFullscreen=mTab;boolean mIsInMultiWindowMode,edge=true;Delegate mFullscreenManagerDelegate=new Delegate();
boolean isDisplayEdgeToEdgeFullscreenFeatureEnabledOn2DDevice(){return edge;}
'''+method+'''
public static void main(String[] args){int count=0;
 for(int bits=0;bits<64;bits++){
  OriginTest t=new OriginTest();t.edge=(bits&1)!=0;ChromeFeatureList.sEnableExclusiveAccessManager.enabled=(bits&2)!=0;
  if((bits&4)!=0)t.mTab=null;t.mActivity.pip=(bits&8)!=0;t.mIsInMultiWindowMode=(bits&16)!=0;boolean incoming=(bits&32)!=0;
  Reporter.events.clear();boolean expected=t.edge&&!ChromeFeatureList.sEnableExclusiveAccessManager.enabled&&t.mTab!=null&&!t.mActivity.pip&&!t.mIsInMultiWindowMode&&incoming;
  boolean read=t.edge&&!ChromeFeatureList.sEnableExclusiveAccessManager.enabled&&t.mTab!=null;
  t.onMultiWindowModeChanged(incoming);
  if(t.mFullscreenManagerDelegate.exits!=(expected?1:0)||t.mActivity.reads!=(read?1:0)||t.mIsInMultiWindowMode!=incoming)throw new AssertionError("behavior "+bits);
  if(Reporter.events.contains("origin6_multiwindow_guard_passed")!=expected)throw new AssertionError("marker "+bits);count++;
 }
 System.out.println(count+" actual multiwindow Java-double branches PASS; no extra PiP getter calls");
}}
'''
controller=(a.applied_tree/'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java').read_text()
sig='public static void reportFullscreenExitOrigin(Activity activity, @Nullable Tab originTab, String origin) {'
entry=sig+controller.split(sig,1)[1].split('\n    }',1)[0]+'\n}'
entry=entry.replace('@Nullable ','')
entry_test='''import java.util.*;
public class FullscreenVideoPictureInPictureController {
static class Activity{} static class Tab{boolean dead,privateMode;boolean isDestroyed(){return dead;}boolean isOffTheRecord(){return privateMode;}}
static class Provider{Tab tab;Tab get(){return tab;}}
static Map<Activity,FullscreenVideoPictureInPictureController> sControllers=new HashMap<>();Provider mActivityTabProvider=new Provider();int reports;
void reportTitaniumYoutubePip(String s){reports++;}
'''+entry+'''
public static void main(String[] args){
 for(int mode=0;mode<6;mode++){
  Activity a=new Activity();FullscreenVideoPictureInPictureController c=new FullscreenVideoPictureInPictureController();Tab tab=new Tab();c.mActivityTabProvider.tab=tab;
  sControllers.clear();if(mode!=1)sControllers.put(a,c);
  if(mode==2)tab=null;if(mode==3)tab.dead=true;if(mode==4)tab.privateMode=true;if(mode==5)tab=new Tab();
  reportFullscreenExitOrigin(a,tab,"origin6_tab_hidden");if(c.reports!=(mode==0?1:0))throw new AssertionError("scope "+mode);
 }
 System.out.println("6 actual origin bridge Java-double scope cases PASS");
}}
'''
with tempfile.TemporaryDirectory() as d:
 root=Path(d);f=root/'OriginTest.java';f.write_text(java);g=root/'FullscreenVideoPictureInPictureController.java';g.write_text(entry_test)
 subprocess.run(['java','-jar',str(a.ecj),'-21',str(f),str(g)],check=True)
 for name in ['OriginTest','FullscreenVideoPictureInPictureController']:subprocess.run(['java','-cp',d,name],check=True)
print('Repeated/drifted anchors rejected; removing fixed log calls restores exact original Base source')
