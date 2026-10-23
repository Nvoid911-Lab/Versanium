"""Run the actual native scope predicate with model RFH/command-line objects.
This validates policy behavior, NOT Chromium C++ API/ABI or object-body compilation.
"""
from pathlib import Path
import argparse,re,subprocess,tempfile,hashlib
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--applied-tree',type=Path,required=True);p.add_argument('--cxx',default='g++');a=p.parse_args()
header=a.applied_tree/'url/gurl.h'
if hashlib.sha256(header.read_bytes()).hexdigest() != '64379fac91a7d4949e7b0c2da12e26952f36ed98dbbd5506fc4480bf8c3f88aa':
 raise RuntimeError('Missing/changed pinned GURL header; model is not an API check')
actual=header.read_text()
assert 'std::string_view host() const LIFETIME_BOUND' in actual and 'host_piece()' not in actual
print('Exact pinned GURL header digest/declaration matched; NOT header/native compilation')
s=(a.applied_tree/'content/browser/renderer_host/render_frame_host_impl.cc').read_text()
body=re.search(r'bool RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed\(RenderFrameHost\* frame\) \{[\s\S]*?\n\}',s).group()
fixture=r'''
#include <string>
#include <string_view>
#include <set>
#include <cassert>
#include <iostream>
namespace base {
class CommandLine {public:
 static bool initialized;static CommandLine current;std::set<std::string> flags;
 static bool InitializedForCurrentProcess(){return initialized;}
 static CommandLine* ForCurrentProcess(){return &current;}
 bool HasSwitch(std::string_view value)const{return flags.contains(std::string(value));}
};bool CommandLine::initialized=true;CommandLine CommandLine::current;
}
namespace content {
class GURL {public:std::string scheme="https",hostname="www.youtube.com";
 bool SchemeIs(const char* s)const{return scheme==s;}std::string_view host()const{return hostname;}};
class BrowserContext {public:bool privateMode=false,shutdown=false;
 bool IsOffTheRecord()const{return privateMode;}bool ShutdownStarted()const{return shutdown;}};
class RenderProcessHost {public:BrowserContext context;BrowserContext* GetBrowserContext(){return &context;}};
class RenderFrameHost {public:bool live=true,active=true;RenderFrameHost* parent=nullptr;GURL url;RenderProcessHost process;
 bool IsRenderFrameLive(){return live;}bool IsActive()const{return active;}
 RenderFrameHost* GetParentOrOuterDocumentOrEmbedder()const{return parent;}
 RenderProcessHost* GetProcess(){return &process;}const GURL& GetLastCommittedURL()const{return url;}};
class RenderFrameHostImpl {public:static bool IsVersaniumYoutubeScopeAllowed(RenderFrameHost*);};
'''+body+r'''
}
int main(){using namespace content;RenderFrameHost frame;int checks=0;
 auto check=[&](bool expected){assert(RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed(&frame)==expected);++checks;};
 assert(!RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed(nullptr));++checks;
 check(false);
 for(auto flag:{"versanium-youtube-pip-candidate","versanium-youtube-background-candidate","versanium-youtube-diagnostics"}){
  base::CommandLine::current.flags={flag};check(true);
 }
 frame.url.scheme="http";check(false);frame.url.scheme="https";
 frame.url.hostname="youtube.com.attacker.test";check(false);frame.url.hostname="twitch.tv";check(false);
 for(auto host:{"youtube.com","www.youtube.com","m.youtube.com"}){frame.url.hostname=host;check(true);}
 frame.process.context.privateMode=true;check(false);frame.process.context.privateMode=false;
 frame.process.context.shutdown=true;check(false);frame.process.context.shutdown=false;
 frame.parent=&frame;check(false);frame.parent=nullptr;
 frame.live=false;check(false);frame.live=true;
 frame.active=false;check(false);frame.active=true;
 base::CommandLine::initialized=false;check(false);
 std::cout<<"Native YouTube scope: "<<checks<<" model cases PASS; not Chromium compilation\n";
}
'''
with tempfile.TemporaryDirectory() as t:
 root=Path(t);(root/'scope.cc').write_text(fixture)
 subprocess.run([a.cxx,'-std=c++20','-Wall','-Werror',str(root/'scope.cc'),'-o',str(root/'scope')],check=True)
 subprocess.run([str(root/'scope')],check=True)
