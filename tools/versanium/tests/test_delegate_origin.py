"""Real fixed Java method fragments + doubles, not chrome_java/NullAway integration."""
from pathlib import Path
import hashlib
import json
import importlib.util
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('delegate_origin', ROOT/'tools/apply_fullscreen_delegate_origin.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class DelegateOriginTests(unittest.TestCase):
    def test_manifest_is_aorigin_plus_three_files_without_b(self):
        previous=json.loads((ROOT/'docs/versanium/config-a-origin-manifest.json').read_text())['files']['AOrigin']
        manifest=json.loads((ROOT/'docs/versanium/config-a-origin-forward-manifest.json').read_text())
        before=manifest['files']['AOrigin'];after=manifest['files']['AOriginForward']
        self.assertEqual(len(before),43)
        for n,h in previous.items():self.assertEqual(before[n],h)
        self.assertEqual({n for n in before if before[n]!=after[n]}, {m.WRAPPER,m.ACTIVITY,m.CONTROLLER})
        for n,s in self.sources().items():
            self.assertEqual(before[n],hashlib.sha256(s.encode()).hexdigest())
            self.assertEqual(after[n],hashlib.sha256(m.transform(n,s).encode()).hexdigest())
    def sources(self):
        paths = {
            m.WRAPPER: Path('/tmp/origin-next')/m.WRAPPER,
            m.ACTIVITY: Path('/tmp/origin-next/ActivityTabWebContentsDelegateAndroid.java'),
            m.CONTROLLER: Path('/tmp/versanium156/config-a-origin-selected')/m.CONTROLLER,
        }
        if not all(p.exists() for p in paths.values()):
            self.skipTest('fixed/AOrigin selected source snapshots unavailable')
        data = {n:p.read_text() for n,p in paths.items()}
        expected = {m.WRAPPER:'c2c49994544fe08b30a751b8930567d68a84560703d91c87e4a401d61f142c92',
                    m.ACTIVITY:'76e8e619408d0ec0af592870a12b257a95b7121452019303757a25b3ff9078cc',
                    m.CONTROLLER:'ad3efea4a6b741de0816240ac87c4f0784dd4b1fb77c396be9ad67f4822366b7'}
        for n,s in data.items(): self.assertEqual(hashlib.sha256(s.encode()).hexdigest(), expected[n])
        return data

    def test_exact_removal_and_rejection(self):
        for n,s in self.sources().items():
            changed = m.transform(n,s)
            restored = changed.replace(m.BRIDGE,'') if n==m.CONTROLLER else ''.join(
                line for line in changed.splitlines(keepends=True) if 'reportFullscreenDelegateOrigin(mTab,' not in line)
            self.assertEqual(s,restored)
            with self.assertRaises(RuntimeError):m.transform(n,changed)
            with self.assertRaises(RuntimeError):m.transform(n,'no anchors')

    def test_actual_methods_and_scope_java_doubles(self):
        sources = self.sources()
        if not Path('/tmp/ecj.jar').exists():self.skipTest('ECJ unavailable')
        def method(path):
            s=m.transform(path,sources[path]);sig='public void exitFullscreenModeForTab() {'
            return (sig+s.split(sig,1)[1].split('\n    }',1)[0]+'\n}').replace(
                'org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController.', 'Test.')
        java='''import java.util.*;
public class Test {
static class Tab {boolean dead,privateMode; Object getWebContents(){return this;} boolean isDestroyed(){return dead;} boolean isOffTheRecord(){return privateMode;}}
static class Provider {Tab tab;Tab get(){return tab;}}
static class FullscreenVideoPictureInPictureController {Provider mActivityTabProvider=new Provider(); void reportTitaniumYoutubePip(String s){events.add(s);}}
static Map<Object,FullscreenVideoPictureInPictureController> sControllers=new HashMap<>();
static List<String> events=new ArrayList<>();
'''+m.BRIDGE.replace('@Nullable ','')+'''
static class Flag {boolean value;int reads;boolean isEnabled(){reads++;return value;}}
static class ChromeFeatureList {static Flag sEnableExclusiveAccessManager=new Flag();}
static class Manager {int exits;void exitFullscreenModeForTab(Object x){exits++;}void onExitFullscreen(Tab t){exits++;}}
static class ActivityDelegate {Tab mTab;Manager mExclusiveAccessManager,mFullscreenManager;
'''+method(m.ACTIVITY)+'''
}
static class Wrapper {Tab mTab;ActivityDelegate mDelegate;
'''+method(m.WRAPPER)+'''
}
public static void main(String[] args){int count=0;
for(int bits=0;bits<32;bits++){
 events.clear();sControllers.clear();Tab tab=new Tab();tab.dead=(bits&8)!=0;tab.privateMode=(bits&16)!=0;
 FullscreenVideoPictureInPictureController c=new FullscreenVideoPictureInPictureController();c.mActivityTabProvider.tab=tab;sControllers.put(new Object(),c);
 ActivityDelegate a=new ActivityDelegate();a.mTab=tab;a.mExclusiveAccessManager=(bits&2)!=0?new Manager():null;a.mFullscreenManager=(bits&4)!=0?new Manager():null;
 ChromeFeatureList.sEnableExclusiveAccessManager.value=(bits&1)!=0;ChromeFeatureList.sEnableExclusiveAccessManager.reads=0;
 Wrapper w=new Wrapper();w.mTab=tab;w.mDelegate=a;w.exitFullscreenModeForTab();
 boolean enabled=(bits&1)!=0;Manager selected=enabled?a.mExclusiveAccessManager:a.mFullscreenManager;
 if(ChromeFeatureList.sEnableExclusiveAccessManager.reads!=1)throw new AssertionError("getter repeated");
 if(a.mExclusiveAccessManager!=null&&a.mExclusiveAccessManager.exits!=(enabled?1:0))throw new AssertionError();
 if(a.mFullscreenManager!=null&&a.mFullscreenManager.exits!=(!enabled?1:0))throw new AssertionError();
 boolean scope=!tab.dead&&!tab.privateMode;int expected=scope?(selected==null?1:2):0;
 if(events.size()!=expected)throw new AssertionError("labels "+bits);
 if(expected==2&&!events.get(1).equals(enabled?"origin6_activity_delegate_exclusive_forward":"origin6_activity_delegate_fullscreen_forward"))throw new AssertionError();count++;
}
events.clear();sControllers.clear();FullscreenVideoPictureInPictureController c=new FullscreenVideoPictureInPictureController();c.mActivityTabProvider.tab=new Tab();sControllers.put(new Object(),c);
reportFullscreenDelegateOrigin(null,"x");reportFullscreenDelegateOrigin(new Tab(),"x");if(!events.isEmpty())throw new AssertionError("null/mismatch");
System.out.println(count+" actual Java forwarding branches + null/mismatch PASS (doubles only)");
}}
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'Test.java';p.write_text(java)
            subprocess.run(['java','-jar','/tmp/ecj.jar','-21',str(p)],check=True)
            subprocess.run(['java','-cp',d,'Test'],check=True)
