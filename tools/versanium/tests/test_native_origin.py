"""Selected real-source/JNI mapping and isolated scope tests, not Chromium compile."""
from pathlib import Path
import importlib.util
import json
import hashlib
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('native_origin',ROOT/'tools/apply_fullscreen_native_origin.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class NativeOriginTests(unittest.TestCase):
 def test_fixed_generator_and_actual_signature(self):
  generator=Path('/tmp/versanium156/applied-transfer/third_party/jni_zero')
  if not (generator/'jni_zero.py').exists():self.skipTest('fixed generator snapshot unavailable')
  spec=importlib.util.spec_from_file_location('native_jni_check',ROOT/'tools/versanium/check_native_origin_jni.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);source=r/'source';p=source/m.JAVA;p.parent.mkdir(parents=True);p.write_text(m.transform(m.JAVA,self.sources()[m.JAVA]))
   j.run(generator,source,r/'generated')
   p.write_text(p.read_text().replace('void reportNativeFullscreenDiagnostic(', 'private void reportNativeFullscreenDiagnostic('))
   with self.assertRaisesRegex(RuntimeError,'Not selected'):j.run(generator,source,r/'rejected')
   self.assertFalse((r/'rejected').exists())
 def test_selected_manifest_reproduction_without_b(self):
  source=self.sources();selected=Path('/tmp/versanium156/config-a-origin-selected');fixed=Path('/tmp/versanium156/source')
  old=json.loads((ROOT/'docs/versanium/config-a-origin-forward-manifest.json').read_text())['files']['AOriginForward']
  manifest=json.loads((ROOT/'docs/versanium/config-a-origin-forward-native-manifest.json').read_text())['files']
  self.assertEqual(len(manifest['AOriginForward']),50);self.assertEqual(len(manifest['AOriginForwardNative']),51)
  for n,h in old.items():self.assertEqual(manifest['AOriginForward'][n],h)
  spec=importlib.util.spec_from_file_location('forward',ROOT/'tools/apply_fullscreen_delegate_origin.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   for n in old:
    p=selected/n if (selected/n).exists() else fixed/n
    if not p.exists():self.skipTest('selected baseline unavailable')
    q=r/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
   f.apply(r)
   for n,s in source.items():
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
   def check(mode):
    for n,h in manifest[mode].items():self.assertEqual(hashlib.sha256((r/n).read_bytes()).hexdigest(),h,n)
   check('AOriginForward');m.apply(r);check('AOriginForwardNative')
   for n,h in old.items():self.assertEqual(hashlib.sha256((r/n).read_bytes()).hexdigest(),h)
   with self.assertRaises(RuntimeError):m.apply(r)
 def sources(self):
  root=Path('/tmp/exclusive156')
  if not all((root/n).exists() for n in m.FILES):self.skipTest('fixed source snapshots unavailable')
  return {n:(root/n).read_text() for n in m.FILES}
 def test_original_statements_remain_and_repeat_rejects(self):
  for n,s in self.sources().items():
   changed=m.transform(n,s);lines=iter(changed.splitlines())
   for old in s.splitlines():
    self.assertTrue(any(line==old for line in lines),'original line deleted/reordered: '+n+' '+old)
   # Added state observations are diagnostic-only, never repeat permission decisions.
   for getter in ['IsFullscreen()', 'IsWindowFullscreenForTabOrPending()',
                  'MaybeToggleFullscreenWithinTab(web_contents, false)', 'IsFullscreenCausedByTab()']:
    self.assertEqual(s.count(getter),changed.count(getter))
   with self.assertRaises(RuntimeError):m.transform(n,changed)
   with self.assertRaises(RuntimeError):m.transform(n,'changed anchors')
 def test_scope_across_translation_units_and_owner_deletion(self):
  if not shutil.which('c++'):self.skipTest('C++ compiler unavailable')
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'scope.h').write_text(m.SCOPE_TEXT)
   (r/'other.cc').write_text('#include "scope.h"\nint nested(){versanium_fullscreen_diagnostic::Scope s;return versanium_fullscreen_diagnostic::depth;}\n')
   (r/'main.cc').write_text('''#include "scope.h"
#include <cassert>
int nested();
int main(){using namespace versanium_fullscreen_diagnostic;
assert(depth==0);{Scope a;auto* owner=new int(1);delete owner;
assert(depth==1);assert(nested()==2);assert(depth==1);}
assert(depth==0);{Scope b;assert(depth==1);}assert(depth==0);}
''')
   subprocess.run(['c++','-std=c++20',str(r/'main.cc'),str(r/'other.cc'),'-o',str(r/'scope-test')],check=True)
   subprocess.run([str(r/'scope-test')],check=True)
 def test_actual_java_native_reporter_gates(self):
  s=m.transform(m.JAVA,self.sources()[m.JAVA]);signature='    void reportNativeFullscreenDiagnostic('
  body=signature+s.split(signature,1)[1].split('\n    }',1)[0]+'\n    }'
  body=body.replace('@Nullable ','').replace('org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController','Reporter')
  if not Path('/tmp/ecj.jar').exists():self.skipTest('ECJ unavailable')
  java='''public class NativeScopeTest {
static class WebContents{boolean dead;boolean isDestroyed(){return dead;}}
static class Tab{WebContents contents;boolean dead,privateMode;boolean isDestroyed(){return dead;}boolean isOffTheRecord(){return privateMode;}WebContents getWebContents(){return contents;}}
static class Reporter{static int count;static String label;static void reportFullscreenDelegateOrigin(Tab t,String s){count++;label=s;}}
long mNativeExclusiveAccessContextAndroid=1;Tab mActiveTab;
'''+body+'''
public static void main(String[] args){int cases=0;
String[] labels={"", "eam_jni_entry", "controller_entry", "within_tab_return",
"window_or_tab_return", "context_not_fullscreen_return", "tab_caused_exit",
"browser_state_loss", "notify_access_lost", "context_exit_call"};
for(int mode=0;mode<10;mode++)for(int stage=0;stage<=10;stage++){
 NativeScopeTest c=new NativeScopeTest();WebContents w=new WebContents();Tab t=new Tab();t.contents=w;c.mActiveTab=t;int depth=2;
 if(mode==1)c.mNativeExclusiveAccessContextAndroid=0;
 if(mode==2)c.mActiveTab=null;if(mode==3)w.dead=true;if(mode==4)t.dead=true;
 if(mode==5)t.privateMode=true;if(mode==6)t.contents=new WebContents();
 if(mode==7)w=null;if(mode==8)depth=-1;if(mode==9)depth=65;
 Reporter.count=0;c.reportNativeFullscreenDiagnostic(w,stage,depth);
 int expected=mode==0&&stage>=1&&stage<=9?1:0;
 if(Reporter.count!=expected)throw new AssertionError("scope "+mode+" "+stage);
 if(expected==1&&!Reporter.label.equals("origin6_native_"+labels[stage]+"_d2"))throw new AssertionError();cases++;
}System.out.println(cases+" actual Java reporter fragment cases PASS; downstream gates separately retained");}}
'''
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);f=r/'NativeScopeTest.java';f.write_text(java)
   subprocess.run(['java','-jar','/tmp/ecj.jar','-21',str(f)],check=True)
   subprocess.run(['java','-cp',d,'NativeScopeTest'],check=True)
