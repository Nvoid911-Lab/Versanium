"""AOrigin selected bytes and transactions; full host gates mocked in fixtures."""
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,subprocess,tempfile,types,unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('aorigin',ROOT/'tools/versanium/prepare_config_a_origin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
u=m.u
class AOriginTests(unittest.TestCase):
 def test_manifest_preserves_a39_and_adds_base(self):
  data=m.selection(ROOT);self.assertEqual(data,json.loads((ROOT/m.MANIFEST).read_text()))
  original=json.loads((ROOT/u.MANIFEST).read_text())['files']['A']
  self.assertEqual(len(data['files']['A']),41)
  for n,h in original.items():self.assertEqual(data['files']['A'][n],h)
  self.assertEqual({n for n in data['files']['A'] if data['files']['A'][n]!=data['files']['AOrigin'][n]},set(m.FILES))
 def test_actual_fixed_source_selection(self):
  source=Path('/tmp/versanium156/source')
  if not all((source/n).exists() for n in m.FILES):self.skipTest('fixed source snapshot unavailable')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for n in m.FILES:
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((source/n).read_bytes())
   subprocess.run(['git','init','-q',str(root)],check=True)
   subprocess.run(['git','-C',str(root),'add','.'],check=True)
   subprocess.run(['git','-C',str(root),'-c','user.name=test','-c','user.email=test@example.invalid','commit','-qm','fixed-source fixture'],check=True)
   data=m.selection(ROOT)['files'];changed=m.reproduce(root,ROOT,data)
   for n,b in changed.items():self.assertEqual(u.digest(b),data['AOrigin'][n])
   data['A'][m.BASE_PATH]='wrong'
   with self.assertRaises(RuntimeError):m.reproduce(root,ROOT,data)
 def test_read_apply_verify_repetition_and_partial_failure(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);w=root/'saved';s=w/'chromium/src';out=s/'out/Default';out.mkdir(parents=True)
   for n in m.FILES:
    p=s/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old')
   baseline={'repository_commit':u.BASE,'chromium_input':'1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775','vanadium_input':'2ae4335402eabcc6e025f3400185fe25094d8521','tracked_source_diff_sha256':'A'}
   prior={'configuration':'A','applied':True,'updated_provenance':baseline,'after_sha256':u.digest(b'old')}
   a=types.SimpleNamespace(workspace=w,control=ROOT,a_applied=root/'prior.json',after_apk=root/'after.json',evidence=root/'dry.json',apply=False,verify=False)
   a.a_applied.write_text(json.dumps(prior));a.after_apk.write_text(json.dumps(baseline))
   maps={'A':{n:u.digest(b'old') for n in m.FILES},'AOrigin':{n:u.digest(b'new') for n in m.FILES}}
   new=dict(baseline,tracked_source_diff_sha256='AOrigin');mod=types.SimpleNamespace(record=lambda *args:new)
   def validate(args,mode,p):u.hashes(s,maps[mode]);return s,out,maps,mod,{},'manifest'
   with patch.object(m,'validate',side_effect=validate),patch.object(m,'reproduce',return_value={n:b'new' for n in m.FILES}),patch.object(u,'git',return_value=b'controller'),patch.object(u,'output_state',return_value={'state':'same'}),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=1)):
    m.run(a);self.assertTrue(all((s/n).read_bytes()==b'old' for n in m.FILES))
    a.apply=True;a.evidence=root/'apply.json';m.run(a)
    for n in m.FILES:self.assertEqual((a.evidence.with_suffix('.before')/n).read_bytes(),b'old')
    a.apply=False;a.verify=True;m.run(a)
    (s/m.BASE_PATH).write_bytes(b'drift')
    with self.assertRaises(RuntimeError):m.run(a)
    a.verify=False;a.evidence=root/'repeat.json'
    with self.assertRaises(RuntimeError):m.run(a)
    for n in m.FILES:(s/n).write_bytes(b'old')
    a.apply=True;a.evidence=root/'partial.json'
    original_write=Path.write_bytes
    def fail_second(path,data):
     if path==s/m.BASE_PATH:raise OSError('fixture second write failed')
     return original_write(path,data)
    with patch.object(Path,'write_bytes',fail_second):
     with self.assertRaises(OSError):m.run(a)
    self.assertFalse(json.loads(a.evidence.read_text())['applied'])
    self.assertEqual((s/u.JAVA).read_bytes(),b'new');self.assertEqual((s/m.BASE_PATH).read_bytes(),b'old')
    for n in m.FILES:self.assertEqual((a.evidence.with_suffix('.before')/n).read_bytes(),b'old')
 def test_installed_record_is_not_a_baseline(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'after').write_text('{}');(p/'prior').write_text(json.dumps({'applied':True,'target_controller':u.PRODUCT}))
   a=types.SimpleNamespace(after_apk=p/'after',a_applied=p/'prior')
   with self.assertRaisesRegex(RuntimeError,'ConfigA'):m.run(a)
if __name__=='__main__':unittest.main()
