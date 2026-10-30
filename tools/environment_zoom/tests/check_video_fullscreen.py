"""Run the applied rendering decision with C++ doubles; NOT Chromium compilation."""
from pathlib import Path
import argparse
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument('--applied-tree', type=Path, required=True)
a = p.parse_args()
wc = (a.applied_tree/'content/browser/web_contents/web_contents_impl.cc').read_text()
start = wc.index('  if (!rfh->GetParentOrOuterDocument()) {\n    auto* zoom_map')
end = wc.index('  return HostZoomMapForRenderFrameHost(rfh)', start)
decision = wc[start:end]
host = (a.applied_tree/'content/browser/host_zoom_map_impl.cc').read_text()
for name in ['GetZoomLevelForWebContents', 'SetZoomLevelForWebContents']:
    signature = ('double ' if name.startswith('Get') else 'void ')+'HostZoomMapImpl::'+name+'('
    body = host.rsplit(signature, 1)[1].split('\n}', 1)[0]
    assert '!UsesTemporaryZoomLevel(rfh_id)' in body
jni = host.split('static void JNI_HostZoomMapImpl_SetZoomLevel(', 1)[1].split('\n}', 1)[0]
assert jni.index('UsesTemporaryZoomLevel') < jni.index('saveEnvironmentZoomLevel')
assert 'SetTemporaryZoomLevel(rfh_id, adjusted_zoom_level);\n    return;' in jni
event = wc.split('void WebContentsImpl::MediaEffectivelyFullscreenChanged(bool is_fullscreen)', 1)[1].split('\n}', 1)[0]
assert event.index('UpdateZoom();') < event.index('NotifyObservers')
assert 'if (is_fullscreen)' not in event  # Exit must re-evaluate too.
fixture = r'''
#include <cassert>
#include <cmath>
#include <iostream>
struct RFH { bool child=false; bool GetParentOrOuterDocument(){return child;} int GetGlobalId(){return 1;} };
struct Map {bool temp=false; double value=2.5; bool UsesTemporaryZoomLevel(int){return temp;}};
struct Observer {bool video=false; bool GetFullscreenVideoMediaPlayerId(){return video;}};
struct Contents;
struct HostZoomMap {static double GetZoomLevel(Contents*,int);static double GetEnvironmentZoomLevel(Contents*,int);};
struct Contents {
 Map map; Observer observer; Observer* media_web_contents_observer_=&observer;
 bool fullscreen=false; double stored=-2.0;
 bool IsFullscreen(){return fullscreen;} Map* HostZoomMapForRenderFrameHost(RFH*){return &map;}
 double render(RFH* rfh){int url=0;
'''+decision+r'''
 return -99; }
};
double HostZoomMap::GetZoomLevel(Contents* c,int){return c->map.value;}
double HostZoomMap::GetEnvironmentZoomLevel(Contents* c,int){return c->stored;}
int main(){int checks=0;RFH frame;
 for(double saved:{-2.0,0.0,2.0}){
  Contents c;c.stored=saved;
  for(int repeat=0;repeat<3;repeat++){
   assert(c.render(&frame)==saved);++checks;
   c.fullscreen=true;assert(c.render(&frame)==saved);++checks; // F11 alone
   c.observer.video=true;assert(c.render(&frame)==0);++checks;
   c.map.temp=true;assert(c.render(&frame)==2.5);++checks;
   c.map.temp=false;c.stored=saved+1;assert(c.render(&frame)==0);++checks; // environment/settings refresh
   c.observer.video=false;assert(c.render(&frame)==saved+1);++checks;
   c.fullscreen=false;assert(c.render(&frame)==saved+1);++checks;
   c.stored=saved;
  }
  assert(c.stored==saved);++checks;
 }
 Contents other;other.stored=4;assert(other.render(&frame)==4);++checks;
 std::cout<<checks<<" applied-decision MODEL checks PASS; not Chromium/device validation\n";
}
'''
with tempfile.TemporaryDirectory() as d:
    f=Path(d)/'decision.cc';f.write_text(fixture)
    subprocess.run(['g++','-std=c++20',str(f),'-o',str(Path(d)/'test')],check=True)
    subprocess.run([str(Path(d)/'test')],check=True)
print('Applied temporary setter/read precedence and entry/exit refresh source checks PASS')
