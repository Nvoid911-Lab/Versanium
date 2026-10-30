"""Entire actual GetPendingZoomLevel, including no-pending, with API doubles.

Standalone fixture executable only: never a Chromium target or production build.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile
from test_diagnostics import baseline,composed,method

PREFIX=r'''
#include <cassert>
#include <cmath>
#include <optional>
#include <sstream>
#include <string>
#include <vector>
#include <iostream>
#define BUILDFLAG(x) 1
bool enabled=false; std::vector<std::string> events;
bool VSZoomEnabled(){return enabled;}
std::ostringstream VSZoomFields(){return std::ostringstream();}
void VSZoomLog(const char* e,const std::string&,const std::string& f){events.push_back(std::string(e)+" "+f);}
struct ID {int value(){return 1;}};
struct Process {ID GetID(){return {};}};
struct RenderWidgetHostImpl {Process p;Process* GetProcess(){return &p;}int GetRoutingID(){return 2;}};
struct GURL {int GetScheme(){return 0;}};
namespace net {int GetHostOrSpecFromURL(GURL){return 0;}}
struct NavigationEntry {GURL GetURL(){return {};}};
struct Controller {NavigationEntry entry;bool pending=false;NavigationEntry* GetPendingEntry(){return pending?&entry:nullptr;}};
struct Token {std::string ToString(){return "frame";}};
struct RenderFrameHost {enum class FrameIterationAction{kStop,kContinue};};
struct RenderFrameHostImpl {
 RenderWidgetHostImpl* widget=nullptr;RenderFrameHostImpl* parent=nullptr;Controller controller;
 bool cached=false,independent=true;
 RenderWidgetHostImpl* GetRenderWidgetHost(){return widget;}
 RenderFrameHostImpl* GetParentOrOuterDocument(){return parent;}
 RenderFrameHostImpl* GetParent(){return parent;}
 int GetFrameTreeNodeId(){return independent?1:0;}
 int GetGlobalId(){return 1;} Token GetFrameToken(){return {};}
 bool IsInBackForwardCache(){return cached;}GURL GetLastCommittedURL(){return {};}
 Controller& GetController(){return controller;}
};
std::string VSZoomBrowserFields(RenderFrameHostImpl*){return "frame=frame";}
struct Map {bool temporary=false;double value=3;int reads=0;
 bool IsIndependentZoomFrameTreeNode(int n){return n!=0;}
 bool UsesTemporaryZoomLevel(int){return temporary;}
 double GetZoomLevelForHostAndSchemeAndroid(int,int){reads++;return value;}
};
struct Observer {bool video=false;std::optional<int> GetFullscreenVideoMediaPlayerId(){return video?std::optional<int>(1):std::nullopt;}};
struct WebContentsImpl;
struct HostZoomMap {static double GetZoomLevel(WebContentsImpl*);static double GetZoomLevel(WebContentsImpl*,int);static double GetEnvironmentZoomLevel(WebContentsImpl*,GURL);};
struct WebContentsImpl {
 std::vector<RenderFrameHostImpl*> frames;Map map;Observer observer;Observer* media_web_contents_observer_=&observer;
 bool fullscreen=false;double stored=0;int selected_reads=0,environment_reads=0;
 bool IsFullscreen(){return fullscreen;}
 Map* HostZoomMapForRenderFrameHost(RenderFrameHostImpl*){return &map;}
 template<class F>void ForEachRenderFrameHostImplWithAction(F f){for(auto* frame:frames)if(f(frame)==RenderFrameHost::FrameIterationAction::kStop)break;}
 double GetPendingZoomLevel(RenderWidgetHostImpl*);double original(RenderWidgetHostImpl*);
};
double HostZoomMap::GetZoomLevel(WebContentsImpl* c){c->selected_reads++;return c->stored;}
double HostZoomMap::GetZoomLevel(WebContentsImpl* c,int){c->selected_reads++;return c->stored;}
double HostZoomMap::GetEnvironmentZoomLevel(WebContentsImpl* c,GURL){c->environment_reads++;return c->stored;}
'''
MAIN=r'''
int main(){int checks=0;
 for(int pct:{50,100,200})for(int gate:{0,1})for(int path=0;path<8;path++)for(int repeat=0;repeat<3;repeat++){
  enabled=gate;events.clear();RenderWidgetHostImpl widget;RenderFrameHostImpl frame,parent;
  frame.widget=&widget;parent.widget=&widget;
  WebContentsImpl actual,old; actual.stored=std::log(pct/100.0)/std::log(1.2);
  actual.fullscreen=true;actual.observer.video=true;
  frame.controller.pending=path!=0;
  if(path==2)actual.map.temporary=true;
  if(path==3)actual.observer.video=false;
  if(path==4)actual.fullscreen=false;
  if(path==5)frame.parent=&parent;
  if(path==6)frame.cached=true;
  if(path!=7)actual.frames={&frame};
  old=actual;old.media_web_contents_observer_=&old.observer;
  double before=actual.stored;
  double wanted=old.original(&widget);double result=actual.GetPendingZoomLevel(&widget);
  assert(result==wanted);++checks;
  assert(actual.selected_reads==old.selected_reads&&actual.environment_reads==old.environment_reads);++checks;
  assert(actual.stored==before);++checks;
  if(!gate){assert(events.empty());++checks;}
  if(path==0){
   assert(result==before&&actual.environment_reads==0);++checks;
   if(gate){bool skip=false;for(auto&e:events){if(e.find("reason=no_pending")!=std::string::npos)skip=true;assert(e.find("CORRECTION_SELECTED")==std::string::npos);}assert(skip);++checks;}
  }
  actual.fullscreen=false;actual.observer.video=false;
  assert(actual.stored==before);++checks;
 }
 std::cout<<"Full selector fixture checks="<<checks<<" PASS (API doubles, not Chromium build)\n";
}
'''
def run(cxx='g++'):
    path='content/browser/web_contents/web_contents_impl.cc'
    with tempfile.TemporaryDirectory(prefix='zoomfs-selector-') as d:
        root=Path(d);actual=composed(root)[path]
        old=method(baseline()[path].decode(),'double WebContentsImpl::GetPendingZoomLevel(')
        new=method(actual,'double WebContentsImpl::GetPendingZoomLevel(')
        code=PREFIX+old.replace('WebContentsImpl::GetPendingZoomLevel','WebContentsImpl::original')+'\n'+new+'\n'+MAIN
        source=root/'selector.cc';source.write_text(code)
        binary=root/'selector';subprocess.run([cxx,'-std=c++20','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cxx',default='g++');run(p.parse_args().cxx)
