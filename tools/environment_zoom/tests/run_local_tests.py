"""Run real JVM policy tests and the Android bridge with explicitly mocked platform/JNI APIs.
No browser build, network access or keystore access. Requires javac, or --ecj PATH.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

STUBS = {
'android/content/Context.java': '''package android.content;
public class Context {
 public static final int MODE_PRIVATE=0; public static final String DISPLAY_SERVICE="display";
 public int displayId; public boolean privateProfile; public String profileKey="Default";
 public android.content.res.Resources getResources(){return new android.content.res.Resources();}
 public Object getSystemService(String name){return new android.hardware.display.DisplayManager();}
 public SharedPreferences getSharedPreferences(String name,int mode){return Preferences.get(name);}
}''',
'android/content/SharedPreferences.java': '''package android.content; import java.util.Map;
public interface SharedPreferences {
 Map<String,?> getAll(); String getString(String k,String fallback); Editor edit();
 interface Editor { Editor clear(); Editor putString(String k,String v); boolean commit(); void apply(); }
}''',
'android/content/Preferences.java': '''package android.content; import java.util.*;
public class Preferences implements SharedPreferences {
 static final Map<String,Preferences> FILES=new HashMap<>(); final Map<String,String> data=new LinkedHashMap<>();
 public int writes; public static Preferences get(String key){return FILES.computeIfAbsent(key,k->new Preferences());}
 public Map<String,?> getAll(){return new LinkedHashMap<>(data);}
 public String getString(String k,String fallback){return data.getOrDefault(k,fallback);}
 public Editor edit(){return new Editor(){Map<String,String> next=new LinkedHashMap<>(data);
 public Editor clear(){next.clear();return this;} public Editor putString(String k,String v){next.put(k,v);return this;}
 public boolean commit(){data.clear();data.putAll(next);writes++;return true;} public void apply(){commit();}};}
}''',
'android/content/ComponentCallbacks.java': '''package android.content; public interface ComponentCallbacks {
 void onConfigurationChanged(android.content.res.Configuration c);void onLowMemory();}''',
'android/content/res/Configuration.java': '''package android.content.res;public class Configuration {public float fontScale=1;}''',
'android/content/res/Resources.java': '''package android.content.res;public class Resources {
 public Configuration getConfiguration(){return new Configuration();}}''',
'android/app/Activity.java': '''package android.app;import java.util.*;import android.content.*;
public class Activity extends Context {
 final List<ComponentCallbacks> callbacks=new ArrayList<>();
 public Activity(int id){displayId=id;} public boolean isDestroyed(){return false;} public boolean isFinishing(){return false;} public void registerComponentCallbacks(ComponentCallbacks c){callbacks.add(c);}
 public void moveTo(int id){displayId=id;for(ComponentCallbacks c:callbacks)c.onConfigurationChanged(getResources().getConfiguration());}
}''',
'android/view/Display.java': 'package android.view;public class Display {public static final int DEFAULT_DISPLAY=0;}',
'android/hardware/display/DisplayManager.java': '''package android.hardware.display;public class DisplayManager {
 public interface DisplayListener{void onDisplayAdded(int id);void onDisplayRemoved(int id);void onDisplayChanged(int id);}
 public void registerDisplayListener(DisplayListener listener,android.os.Handler h){}
}''',
'android/os/Looper.java': 'package android.os;public class Looper {public static Looper getMainLooper(){return new Looper();}}',
'android/os/Handler.java': """package android.os;import java.util.*;import java.util.concurrent.*;
public class Handler {
 static final Queue<Runnable> MAIN=new ConcurrentLinkedQueue<>();
 static final Map<Runnable,Integer> DELAYED=new LinkedHashMap<>();
 public Handler(Looper l){} public boolean post(Runnable r){MAIN.add(r);return true;}
 public boolean postDelayed(Runnable r,long delay){DELAYED.put(r,(int)delay);return true;}
 public void removeCallbacks(Runnable r){DELAYED.remove(r);MAIN.remove(r);}
 public static void drain(){Runnable r;while((r=MAIN.poll())!=null)r.run();}
}
""",
'org/chromium/base/StrictModeContext.java': 'package org.chromium.base;public class StrictModeContext implements AutoCloseable {public static StrictModeContext allowDiskReads(){return new StrictModeContext();}public void close(){}}',
'org/chromium/base/ThreadUtils.java': 'package org.chromium.base;public class ThreadUtils {static final Thread MAIN=Thread.currentThread();public static void assertOnUiThread(){if(Thread.currentThread()!=MAIN)throw new AssertionError("Not UI thread");}}',
'org/chromium/base/Log.java': 'package org.chromium.base;public class Log {public static void e(String tag,String msg){}}',
'android/widget/Toast.java': 'package android.widget;public class Toast {public static final int LENGTH_LONG=1;public static Toast makeText(android.content.Context c,CharSequence s,int duration){return new Toast();}public void show(){}}',

'org/chromium/base/ContextUtils.java': '''package org.chromium.base;public class ContextUtils {
 static final android.content.Context APP=new android.content.Context();
 public static android.content.Context getApplicationContext(){return APP;}
 public static android.content.SharedPreferences getAppSharedPreferences(){return APP.getSharedPreferences("app",0);}}''',
'org/chromium/ui/base/WindowAndroid.java': '''package org.chromium.ui.base;import java.lang.ref.WeakReference;
public class WindowAndroid {public android.app.Activity activity;public WindowAndroid(android.app.Activity a){activity=a;}
 public WeakReference<android.app.Activity> getActivity(){return new WeakReference<>(activity);}}''',
'org/chromium/ui/display/DisplayAndroid.java': '''package org.chromium.ui.display;public class DisplayAndroid {
 int id;DisplayAndroid(int i){id=i;}public int getDisplayId(){return id;}
 public static DisplayAndroid getNonMultiDisplay(android.content.Context c){return new DisplayAndroid(c.displayId);}}''',
'org/chromium/content_public/browser/BrowserContextHandle.java': '''package org.chromium.content_public.browser;
public class BrowserContextHandle {public boolean privateProfile;public String key="Default";public long getNativeBrowserContextPointer(){return 1;}}''',
'org/chromium/content_public/browser/WebContents.java': '''package org.chromium.content_public.browser;
public class WebContents {public String host="example.test";public boolean destroyed;public double rendered;
 public org.chromium.ui.base.WindowAndroid window;
 public boolean isFinishing(){return false;} public boolean isDestroyed(){return destroyed;}public org.chromium.ui.base.WindowAndroid getTopLevelNativeWindow(){return window;}}''',
'org/chromium/content_public/browser/HostZoomMap.java': '''package org.chromium.content_public.browser;import java.util.*;
public class HostZoomMap {public static double getDefaultZoomLevel(BrowserContextHandle c){return 0;}
 public static Map<String,Double> getAllHostZoomLevels(BrowserContextHandle c){return Map.of();}
 public static boolean shouldAdjustForOSLevel(){return false;}}''',
'org/chromium/content/browser/HostZoomMapImpl.java': '''package org.chromium.content.browser;import org.chromium.content_public.browser.*;
public class HostZoomMapImpl {public static String getEnvironmentProfileKey(BrowserContextHandle c){return c.key;}
 public static boolean isEnvironmentPrivate(BrowserContextHandle c){return c.privateProfile;}
 public static String getEnvironmentHost(WebContents c){return c.host;}
 public static void refreshEnvironmentZoom(WebContents c){c.rendered=EnvironmentZoom.rendered(c,c.host);}}''',
}


def run(ecj=None, android_json=None):
    bundle = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='titanium-zoom-jvm-') as temporary:
        root = Path(temporary)
        for relative, text in STUBS.items():
            target = root/'stubs'/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        sources = list((root/'stubs').rglob('*.java'))
        sources += list((bundle/'java/org/chromium/content_public/browser').glob('*.java'))
        sources += list((bundle/'tests').glob('*Test.java'))
        if android_json is None:
            sources=[s for s in sources if s.name not in ('EnvironmentZoomBackup.java','EnvironmentZoomBackupTest.java')]
        command = ['java', '-jar', str(ecj), '-21'] if ecj else ['javac', '--release', '21']
        subprocess.run(command+(['-cp',str(android_json)] if android_json else [])+['-d',str(root/'classes')]+[str(s) for s in sources],check=True)
        for test in ['EnvironmentZoomPolicyTest','EnvironmentZoomBridgeTest','EnvironmentZoomPersistenceTest']+(['EnvironmentZoomBackupTest'] if android_json else []):
            subprocess.run(['java','-cp',str(root/'classes')+(':'+str(android_json) if android_json else ''),test],check=True)
        print('Renderer / JNI / Android lifecycle are MOCKED in bridge test; APK verification is still required.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ecj',type=Path)
    parser.add_argument('--android-json',type=Path)
    args=parser.parse_args()
    if not args.ecj and not shutil.which('javac'):
        parser.error('Install JDK 21, or supply --ecj with a trusted ECJ 3.40.0 jar')
    run(args.ecj,args.android_json)
