"""Execute the actual generated Java observer/calculation against explicit Android doubles."""
from pathlib import Path
import argparse
import os
import subprocess
import tempfile
from test_diagnostics import B,composed,load

zoom=B.parent/'environment_zoom'
stubs=dict(load('zoom_stubs',zoom/'tests/run_local_tests.py').STUBS)
stubs['org/chromium/base/CommandLine.java']='''package org.chromium.base;public class CommandLine {
 public static boolean enabled=false;public static boolean isInitialized(){return true;}
 public static CommandLine getInstance(){return new CommandLine();} public boolean hasSwitch(String s){return enabled;}}'''
stubs['org/chromium/base/Log.java']='''package org.chromium.base;import java.util.*;public class Log {
 public static List<String> events=new ArrayList<>();public static void e(String t,String m){}
 public static void i(String t,String m,Object... v){events.add(String.format(m,v));}}'''
stubs['org/chromium/content_public/browser/RenderFrameHost.java']='''package org.chromium.content_public.browser;
public class RenderFrameHost {public GlobalRenderFrameHostId getGlobalRenderFrameHostId(){return new GlobalRenderFrameHostId();}}'''
stubs['org/chromium/content_public/browser/GlobalRenderFrameHostId.java']='''package org.chromium.content_public.browser;
public class GlobalRenderFrameHostId {public int childId(){return 2;}public int frameRoutingId(){return 7;}}'''
k='org/chromium/content_public/browser/WebContents.java'
stubs[k]=stubs[k].replace('public String host=', 'public int observations; public RenderFrameHost getMainFrame(){observations++;return new RenderFrameHost();} public String host=')
k='android/app/Activity.java';stubs[k]=stubs[k].replace('final List<ComponentCallbacks>', 'public android.view.Window getWindow(){return new android.view.Window();} final List<ComponentCallbacks>')
stubs['android/view/Window.java']='package android.view;public class Window {public View getDecorView(){return new View();}}'
stubs['android/view/View.java']='package android.view;public class View {public int getWidth(){return 1080;}public int getHeight(){return 1920;}}'
stubs['android/graphics/Point.java']='package android.graphics;public class Point {public int x,y;}'
stubs['android/view/Display.java']='''package android.view;public class Display {public static final int DEFAULT_DISPLAY=0;
 public void getRealSize(android.graphics.Point p){p.x=1080;p.y=1920;}}'''
stubs['android/hardware/display/DisplayManager.java']=stubs['android/hardware/display/DisplayManager.java'].replace('public interface DisplayListener', 'public android.view.Display getDisplay(int id){return new android.view.Display();} public interface DisplayListener')
TEST=r'''
import android.app.Activity;import org.chromium.content_public.browser.*;import org.chromium.base.*;
import org.chromium.ui.base.WindowAndroid;
public class ZoomFullscreenTest {
 static int checks;static void check(boolean b){if(!b)throw new AssertionError("check "+checks);checks++;}
 static boolean has(String s){return Log.events.stream().anyMatch(e->e.contains(s));}
 public static void main(String[] args){
  BrowserContextHandle profile=new BrowserContextHandle();WebContents wc=new WebContents();
  wc.window=new WindowAndroid(new Activity(0));EnvironmentZoom.attach(wc,profile);
  for(boolean gate:new boolean[]{false,true})for(int pct:new int[]{50,100,200}){
   CommandLine.enabled=gate;Log.events.clear();wc.observations=0;
   double factor=EnvironmentZoomPolicy.factor(pct);
   check(EnvironmentZoom.save(wc,wc.host,factor));
   double before=EnvironmentZoom.resolve(wc,wc.host);
   double rendered=EnvironmentZoom.rendered(wc,wc.host);
   EnvironmentZoom.vsZoomFullscreen(wc,4,true);
   check(Double.doubleToRawLongBits(rendered)==Double.doubleToRawLongBits(EnvironmentZoom.rendered(wc,wc.host)));
   check(Double.doubleToRawLongBits(before)==Double.doubleToRawLongBits(EnvironmentZoom.resolve(wc,wc.host)));
   EnvironmentZoom.vsZoomFullscreen(wc,4,false);
   EnvironmentZoom.rendered(wc,wc.host);
   check(Double.doubleToRawLongBits(before)==Double.doubleToRawLongBits(EnvironmentZoom.resolve(wc,wc.host)));
   if(gate){check(has("event=ZOOM_STATE"));check(has("event=FULLSCREEN_ENTER"));
    check(has("event=FULLSCREEN_EXIT"));check(has("restore_action=none stored_zoom_unchanged=true"));
    check(!has(wc.host));check(has("wc_main_child=2 wc_main_route=7"));
   }else{check(Log.events.isEmpty());check(wc.observations==0);}
  }
  Log.events.clear();wc.destroyed=true;EnvironmentZoom.vsZoomFullscreen(wc,4,true);
  EnvironmentZoom.vsZoomFullscreen(null,4,false);check(Log.events.isEmpty());
  System.out.println("Zoom fullscreen Java checks="+checks+" PASS (platform doubles, no APK)");
 }
}'''
def run(jdk):
    javac=str(jdk/'bin'/('javac.exe' if os.name=='nt' else 'javac'))
    java=str(jdk/'bin'/('java.exe' if os.name=='nt' else 'java'))
    with tempfile.TemporaryDirectory(prefix='zoomfs-java-') as d:
        root=Path(d);sources=composed(root)
        for p,s in stubs.items():
            t=root/'stubs'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_text(s)
        test=root/'ZoomFullscreenTest.java';test.write_text(TEST)
        inputs=list((root/'stubs').rglob('*.java'))+[test]
        inputs += [root/p for p in sources if p.endswith('.java')]
        inputs += [zoom/'java/org/chromium/content_public/browser'/p for p in ('EnvironmentZoomPolicy.java','EnvironmentZoomPersistence.java')]
        subprocess.run([javac,'--release','21','-d',str(root/'classes')]+[str(p) for p in inputs],check=True)
        subprocess.run([java,'-cp',str(root/'classes'),'ZoomFullscreenTest'],check=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--jdk',type=Path,required=True);run(p.parse_args().jdk)
