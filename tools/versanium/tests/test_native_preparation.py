"""New transaction/graph fixtures; no real host validation or integration compile."""
from pathlib import Path
from unittest.mock import patch
import json
import sys
import tempfile
import types
import unittest
import subprocess
import shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/versanium'))
import prepare_native_diagnostic as m
import audit_native_graph as g

class NativePreparationTests(unittest.TestCase):
 def test_post_gn_delta_refuses_args_objects_and_history_even_mtime(self):
  before={'build.ninja':{'sha256':'old'},'args.gn':{'sha256':'args','mtime_ns':1},'.siso_deps':{'sha256':'state'}}
  after=dict(before,**{'build.ninja':{'sha256':'new'}})
  self.assertEqual(g.graph_delta(before,after),['build.ninja'])
  for n,v in [('args.gn',{'sha256':'args','mtime_ns':2}),('new.o',{'sha256':'new'}),('.siso_deps',{'sha256':'changed'})]:
   changed=dict(after);changed[n]=v
   with self.assertRaisesRegex(RuntimeError,'Non-graph'):g.graph_delta(before,changed)
 def test_fixed_reproduction_and_manifest(self):
  data,changed,h=m.selected(ROOT);fixed=Path('/tmp/exclusive156')
  if not all((fixed/n).exists() for n in changed):self.skipTest('fixed snapshot unavailable')
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   for n in changed:
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((fixed/n).read_bytes())
   subprocess.run(['git','init','-q',str(r)],check=True);subprocess.run(['git','-C',str(r),'add','.'],check=True)
   subprocess.run(['git','-C',str(r),'-c','user.name=test','-c','user.email=test@example.invalid','commit','-qm','fixed156 source'],check=True)
   after=m.reproduce(r,ROOT,data,changed)
   self.assertEqual(len(after),8)
   for n,b in after.items():self.assertEqual(m.digest(b),data['files'][m.AFTER][n])
   data['files'][m.BEFORE][changed[0]]='wrong'
   with self.assertRaisesRegex(RuntimeError,'mismatch'):m.reproduce(r,ROOT,data,changed)
 def test_read_apply_verify_partial_failure_and_output_drift(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);w=r/'saved';s=w/'chromium/src';out=s/'out/Default';out.mkdir(parents=True)
   old=['a','b'];new=['c'];maps={m.BEFORE:{n:m.digest(b'old') for n in old},m.AFTER:{n:m.digest(b'new') for n in old+new}}
   data={'files':maps,'absent_before':new}
   for n in old:(s/n).write_bytes(b'old')
   for n in ['args.gn','build.ninja','.ninja_log','.siso_deps']:(out/n).write_bytes(b'graph')
   baseline={'repository_commit':m.BASE,'chromium_input':m.CHROMIUM,'vanadium_input':m.VANADIUM,'tracked_source_diff_sha256':'before'}
   prior={'configuration':m.BEFORE,'applied':True,'updated_provenance':baseline,'tools':{},'after_sha256':{n:maps[m.BEFORE]['a'] for n in ['a','b','extra']}}
   maps[m.BEFORE]['extra']=m.digest(b'old');maps[m.AFTER]['extra']=m.digest(b'old');(s/'extra').write_bytes(b'old')
   a=types.SimpleNamespace(workspace=w,control=ROOT,forward_applied=r/'prior',after_apk=r/'after',forward_apk=r/'apk',evidence=r/'dry',apply_source=False,verify_source=False)
   a.forward_applied.write_text(json.dumps(prior));a.after_apk.write_text(json.dumps(baseline));a.forward_apk.write_bytes(b'apk')
   updated=dict(baseline,tracked_source_diff_sha256='after');mod=types.SimpleNamespace(record=lambda *args:updated)
   def env(args,mode,p):
    m.check_files(s,maps[mode])
    if mode==m.BEFORE:self.assertFalse((s/'c').exists())
    return s,out,data,old,'manifest',mod,{},{}
   with patch.object(m,'APK',m.digest(b'apk')),patch.object(m,'environment',side_effect=env),patch.object(m,'reproduce',return_value={n:b'new' for n in old+new}),patch.object(m,'nonselected_diff',return_value='other'),patch.object(m,'git',return_value=b'controller'),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=1)):
    m.run(a);self.assertFalse((s/'c').exists())
    a.apply_source=True;a.evidence=r/'applied';m.run(a)
    self.assertEqual((a.evidence.with_suffix('.before')/'output/build.ninja').read_bytes(),b'graph')
    a.apply_source=False;a.verify_source=True;m.run(a)
    a.verify_source=False;a.evidence=r/'repeat'
    with self.assertRaises(RuntimeError):m.run(a)
    for n in old:(s/n).write_bytes(b'old')
    (s/'c').unlink();a.apply_source=True;a.evidence=r/'partial'
    original=Path.open
    def fail(path,*args,**kwargs):
     if path==s/'b' and args and args[0]=='wb':raise OSError('partial fixture')
     return original(path,*args,**kwargs)
    with patch.object(Path,'open',fail):
     with self.assertRaises(OSError):m.run(a)
    self.assertEqual((s/'a').read_bytes(),b'new');self.assertEqual((s/'b').read_bytes(),b'old')
    self.assertFalse(json.loads(a.evidence.read_text())['source_applied'])
    for n in old:(s/n).write_bytes(b'old')
    a.evidence=r/'output-drift';real=m.inventory;calls=0
    def moved(path):
     nonlocal calls
     calls+=1;value=real(path)
     if calls==2:value['unexpected.o']={'sha256':'drift'}
     return value
    with patch.object(m,'inventory',side_effect=moved):
     with self.assertRaisesRegex(RuntimeError,'Output moved'):m.run(a)
    self.assertFalse(json.loads(a.evidence.read_text())['source_applied'])
 def test_wrong_baseline_and_apk_reject(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);a=types.SimpleNamespace(forward_applied=r/'prior',after_apk=r/'after',forward_apk=r/'apk')
   a.after_apk.write_text('{}');a.forward_apk.write_bytes(b'wrong')
   for config in ['A','AOrigin','installed']:
    a.forward_applied.write_text(json.dumps({'configuration':config,'applied':True,'updated_provenance':{}}))
    with self.assertRaisesRegex(RuntimeError,'Forward'):m.baseline(a)
   pins={'repository_commit':m.BASE,'chromium_input':m.CHROMIUM,'vanadium_input':m.VANADIUM}
   a.after_apk.write_text(json.dumps(pins));a.forward_applied.write_text(json.dumps({'configuration':m.BEFORE,'applied':True,'updated_provenance':pins}))
   with self.assertRaisesRegex(RuntimeError,'APK hash'):m.baseline(a)
 def test_binary_graph_multi_toolchain_and_duplicates(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out/Default';out.mkdir(parents=True);tc='//build/toolchain/android:actual_from_gn'
   descriptions={};lines=[]
   for i,(src,label) in enumerate(g.SOURCES.items()):
    descriptions.setdefault(label,{'sources':[],'toolchain':tc})['sources'].append('//'+src)
    lines.append(f'build obj/exact{i}.o: cxx ../../{src}\n'.encode())
    lines.append(f'build android_clang_arm/obj/exact{i}.o: cxx ../../{src}\n'.encode())
   (out/'build.ninja').write_bytes(b'subninja loaded.ninja\n');(out/'loaded.ninja').write_bytes(b'# binary \xff\xfe\n'+b''.join(lines));(out/'unloaded.ninja').write_bytes(b'\xff\xfe')
   result=g.objects(out,r,[descriptions],tc);self.assertEqual(len(result['objects']),3)
   self.assertTrue(all(x['target'].startswith('obj/') for x in result['objects']))
   backup=r/'external-graph';shutil.copytree(out,backup)
   self.assertEqual(g.objects(backup,r,[descriptions],tc,edge_base=out)['objects'],result['objects'])
   with self.assertRaisesRegex(RuntimeError,'toolchain'):g.objects(out,r,[descriptions],'wrong')
   (out/'loaded.ninja').write_bytes(b''.join(lines)+lines[0])
   with self.assertRaisesRegex(RuntimeError,'Duplicate'):g.objects(out,r,[descriptions],tc)
