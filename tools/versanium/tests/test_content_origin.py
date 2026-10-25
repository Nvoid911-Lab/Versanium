"""Selected source/JNI/Java-fragment checks, not Chromium integration compilation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('content_origin',ROOT/'tools/apply_content_fullscreen_origin.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ContentOriginTests(unittest.TestCase):
 def test_nullable_proxy_lookup_actual_java_fragment(self):
  selection,sources=self.sources();s=m.transform(m.JPROXY,sources[m.JPROXY]);sig='    static @Nullable WebContentsObserverProxy getForVersaniumDiagnostic('
  body=re.sub(r'\bWebContentsObserverProxy\b','ProxyLookupTest',(sig+s.split(sig,1)[1].split('\n    }',1)[0]+'\n    }').replace('@Nullable ','').replace('@JniType("content::WebContents*") ',''))
  old=sources[m.JPROXY].split('private static WebContentsObserverProxy getFromWebContents(',1)[1].split('\n    }',1)[0]
  self.assertEqual(s.split('private static WebContentsObserverProxy getFromWebContents(',1)[1].split('\n    }',1)[0],old)
  cpp=m.transform(m.PROXY+'.cc',sources[m.PROXY+'.cc']).split('void WebContentsObserverProxy::VersaniumContentFullscreenDiagnostic(int stage) {',1)[1].split('\n}',1)[0]
  self.assertNotIn('GetJavaObjectChecked',cpp);self.assertIn('getForVersaniumDiagnostic',cpp)
  if not Path('/tmp/ecj.jar').exists():self.skipTest('ECJ unavailable')
  java='''public class ProxyLookupTest {
long mNativeWebContentsObserverProxy;
static class WebContents{}
static class WebContentsImpl extends WebContents{ProxyLookupTest proxy;ProxyLookupTest getWebContentsObserverProxy(){return proxy;}}
'''+body+'''
public static void main(String[] args){for(int mode=0;mode<4;mode++){
WebContentsImpl w=new WebContentsImpl();if(mode>0)w.proxy=new ProxyLookupTest();if(mode==2)w.proxy.mNativeWebContentsObserverProxy=1;
if(mode==3)w=null;
ProxyLookupTest actual=getForVersaniumDiagnostic(w);if((actual!=null)!=(mode==2))throw new AssertionError();
}System.out.println("4 actual nullable proxy lookup fragment cases PASS");}}
'''
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);f=r/'ProxyLookupTest.java';f.write_text(java);subprocess.run(['java','-jar','/tmp/ecj.jar','-21',str(f)],check=True);subprocess.run(['java','-cp',d,f.stem],check=True)
 def test_complete_58_input_selection_preserves_native_and_zoom(self):
  selection,sources=self.sources()
  native=json.loads((ROOT/'docs/versanium/config-a-origin-forward-native-manifest.json').read_text())['files']['AOriginForwardNative']
  for n,h in native.items():self.assertEqual(dict(selection['preserved_baseline'],**selection['before'])[n],h,n)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   for n,h in selection['preserved_baseline'].items():
    paths=[Path(p)/n for p in ['/tmp/native-origin156','/tmp/versanium156/config-a-origin-selected','/tmp/versanium156/forward-reviewed']]
    src=next((p for p in paths if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h),None)
    if src is None:self.skipTest('Native selected snapshot unavailable')
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(src.read_bytes())
   for n,s in sources.items():
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
   self.assertEqual(len(selection['before'])+len(selection['preserved_baseline']),58)
   m.apply(r)
   for n,h in dict(selection['after'],**selection['preserved_baseline']).items():self.assertEqual(hashlib.sha256((r/n).read_bytes()).hexdigest(),h,n)
 def sources(self):
  selection=json.loads((ROOT/'docs/versanium/content-fullscreen-diagnostic-selection.json').read_text())
  result={}
  for n,h in selection['before'].items():
   candidates=[Path(p)/n for p in ['/tmp/versanium156/config-a-origin-selected','/tmp/native-origin156','/tmp/versanium156/forward-reviewed','/tmp/versanium156/source']]
   p=next((p for p in candidates if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h),None)
   if p is None:self.skipTest('fixed selected source snapshot unavailable: '+n)
   result[n]=p.read_text()
  return selection,result
 def test_selection_repeat_drift_no_existing_check_or_permission_changes(self):
  selection,sources=self.sources()
  for n,s in sources.items():
   changed=m.transform(n,s)
   self.assertEqual(hashlib.sha256(changed.encode()).hexdigest(),selection['after'][n])
   for call in ['CHECK(', 'DCHECK(', 'CanEnterFullscreenMode(', 'IsFullscreen()', 'ShouldPausePlaybackWhenHidden(', 'canDoPictureInPicture(']:
    self.assertEqual(s.count(call),changed.count(call),n+' '+call)
   if n.startswith('content/'):
    self.assertNotIn('chrome/browser/',changed)
    self.assertNotIn('versanium_fullscreen_diagnostic_scope.h',changed)
   if n==m.PIP:
    signature='private void reportTitaniumYoutubePip(String stage) {'
    self.assertEqual(s.split(signature,1)[1].split('\n    }',1)[0],changed.split(signature,1)[1].split('\n    }',1)[0])
   if n==m.WC+'.cc':
    for signature in ['double WebContentsImpl::GetPendingZoomLevel(', 'void WebContentsImpl::MediaEffectivelyFullscreenChanged(']:
     self.assertEqual(s.split(signature,1)[1].split('\n}',1)[0],changed.split(signature,1)[1].split('\n}',1)[0])
   with self.assertRaises(RuntimeError):m.transform(n,changed)
   with self.assertRaises(RuntimeError):m.transform(n,'wrong anchors')
 def test_fixed_jni_generation(self):
  selection,sources=self.sources();generator=Path('/tmp/versanium156/applied-transfer/third_party/jni_zero')
  if not (generator/'jni_zero.py').exists():self.skipTest('fixed generator snapshot unavailable')
  ledger=json.loads((ROOT/'docs/versanium/native-origin-jni-generator-hashes.json').read_text())
  for n,h in ledger.items():self.assertEqual(hashlib.sha256((generator/n).read_bytes()).hexdigest(),h)
  gni=Path('/tmp/content-origin156/jni_zero.gni')
  if not gni.exists():self.skipTest('fixed GN template unavailable')
  self.assertEqual(hashlib.sha256(gni.read_bytes()).hexdigest(),'f76110787aca6cdf9d39c500cd37c6be3bd56feb95ae83aa8e07f95b54277beb')
  self.assertIn('allow_private_called_by_natives = true',gni.read_text())
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);java=r/'WebContentsObserverProxy.java';java.write_text(m.transform(m.JPROXY,sources[m.JPROXY]));out=r/'generated';out.mkdir()
   subprocess.run(['python3',str(generator/'jni_zero.py'),'from-source','--input-file',str(java),'--shared-header-name','Proxy_shared_jni.h','--unshared-header-name','Proxy_jni.h','--output-dir',str(out),'--allow-private-called-by-natives'],check=True)
   h=(out/'Proxy_jni.h').read_text();start=h.index('static void Java_WebContentsObserverProxy_versaniumContentFullscreenDiagnostic(');body=h[start:h.index('\n}',start)]
   for token in ['JavaRef<jobject>& obj','JniIntWrapper stage','"(I)V"']:self.assertIn(token,body)
   lookup=h[h.index('Java_WebContentsObserverProxy_getForVersaniumDiagnostic('):]
   self.assertIn('content::WebContents* const& webContents',lookup.split('\n}',1)[0])
 def test_actual_java_current_contents_and_stage_routing_fragment(self):
  selection,sources=self.sources();source=m.transform(m.PIP,sources[m.PIP]);sig='        public void versaniumContentFullscreenDiagnostic(int stage) {'
  body=sig+source.split(sig,1)[1].split('\n        }',1)[0]+'\n        }'
  if not Path('/tmp/ecj.jar').exists():self.skipTest('ECJ unavailable')
  labels=', '.join('"content_diag_'+m.LABELS[i]+'"' for i in sorted(m.LABELS))
  java='''public class FullscreenVideoPictureInPictureController {
static class WebContents{boolean dead;boolean isDestroyed(){return dead;}}
static class Observer{WebContents actual;WebContents getWebContents(){return actual;}}
WebContents current;int calls;String label;
WebContents getWebContents(){return current;}
void reportTitaniumYoutubePip(String s){calls++;label=s;}
class SelectedObserver extends Observer{
'''+body+'''
}
public static void main(String[] args){String[] labels={'''+labels+'''};int count=0;
for(int mode=0;mode<4;mode++)for(int stage=0;stage<=15;stage++){
 FullscreenVideoPictureInPictureController c=new FullscreenVideoPictureInPictureController();c.current=new WebContents();SelectedObserver o=c.new SelectedObserver();o.actual=c.current;
 if(mode==1)o.actual=null;if(mode==2)o.actual.dead=true;if(mode==3)o.actual=new WebContents();
 o.versaniumContentFullscreenDiagnostic(stage);boolean expected=mode==0&&stage>=1&&stage<=14;
 if(c.calls!=(expected?1:0))throw new AssertionError();
 if(expected&&!c.label.equals(labels[stage-1]))throw new AssertionError();count++;
}System.out.println(count+" actual Java observer fragment cases PASS; downstream logger gates separately unchanged");}}
'''
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);f=r/'FullscreenVideoPictureInPictureController.java';f.write_text(java)
   subprocess.run(['java','-jar','/tmp/ecj.jar','-21',str(f)],check=True);subprocess.run(['java','-cp',d,f.stem],check=True)
 def test_return_lifetime_and_false_send_sites(self):
  selection,sources=self.sources()
  r=m.transform(m.RFH,sources[m.RFH]);b=r.split('void RenderFrameHostImpl::ExitFullscreen() {',1)[1].split('\n}',1)[0]
  self.assertIn('if (!weak_ptr) return;',b);self.assertIn('weak_ptr.get() == static_cast<WebContentsImpl*>',b)
  s=m.transform(m.MEDIA,sources[m.MEDIA]);b=s.split('void MediaWebContentsObserver::RequestPersistentVideo(bool value) {',1)[1].split('\n}',1)[0]
  self.assertLess(b.index('Diagnostic(12)'),b.index('SetPersistentState(value)'))
  self.assertGreater(b.index('Diagnostic(13)'),b.index('SetPersistentState(value)'))
  self.assertIn('if (!fullscreen_player_) {',b);self.assertIn('if (!content_diag_contents) return;',b)
