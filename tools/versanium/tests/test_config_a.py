"""Actual one-file A reconstruction plus mocked host gate transaction tests."""
from pathlib import Path
from unittest.mock import patch
import importlib.util,subprocess,tempfile,json,unittest,types
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('configa',ROOT/'tools/versanium/prepare_config_a.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ConfigATests(unittest.TestCase):
 def test_fixed_source_reproduction(self):
  original=Path('/tmp/versanium156/source')/m.JAVA
  if not original.exists():self.skipTest('fixed Chromium selected input unavailable')
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);p=root/m.JAVA;p.parent.mkdir(parents=True);p.write_bytes(original.read_bytes())
   subprocess.run(['git','init','-q',str(root)],check=True)
   subprocess.run(['git','-C',str(root),'add','.'],check=True)
   subprocess.run(['git','-C',str(root),'-c','user.name=test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
   manifest=json.loads((ROOT/m.MANIFEST).read_text())['files']
   result=m.reproduce(root,ROOT,manifest)
   self.assertEqual(m.digest(result),manifest['A'][m.JAVA])
   manifest['A'][m.JAVA]='wrong'
   with self.assertRaises(RuntimeError):m.reproduce(root,ROOT,manifest)
 def test_transaction_read_apply_recheck_and_drift(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);w=root/'saved';s=w/'chromium/src';out=s/'out/Default';out.mkdir(parents=True);target=s/m.JAVA;target.parent.mkdir(parents=True);target.write_bytes(b'old')
   baseline={'repository_commit':m.BASE,'chromium_input':'1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775','vanadium_input':'2ae4335402eabcc6e025f3400185fe25094d8521','tracked_source_diff_sha256':'old'}
   after=dict(baseline,tracked_source_diff_sha256='A')
   prior={'applied':True,'target_controller':m.PRODUCT,'post_update_provenance':baseline,'post_update_source_sha256':{m.JAVA:m.digest(b'old')}}
   a=types.SimpleNamespace(workspace=w,control=ROOT,after_apk=root/'after.json',baseline_applied=root/'prior.json',evidence=root/'dry.json',apply=False,verify=False)
   a.after_apk.write_text(json.dumps(baseline));a.baseline_applied.write_text(json.dumps(prior))
   manifests={'installed':{m.JAVA:m.digest(b'old')},'A':{m.JAVA:m.digest(b'new')}}
   mod=types.SimpleNamespace(record=lambda *args:after)
   def validate(args,config,provenance):
    m.hashes(s,manifests[config]);return s,out,manifests,mod,provenance,{},'manifest'
   with patch.object(m,'validate',side_effect=validate),patch.object(m,'reproduce',return_value=b'new'),patch.object(m,'output_state',return_value={'state':'same'}),patch.object(m,'git',return_value=b'controller'),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=1)):
    m.run(a);self.assertEqual(target.read_bytes(),b'old')
    a.evidence=root/'apply.json';a.apply=True;m.run(a);self.assertEqual(target.read_bytes(),b'new')
    self.assertEqual(a.evidence.with_suffix('.before.java').read_bytes(),b'old')
    a.apply=False;a.verify=True;m.run(a)
    target.write_bytes(b'unexpected')
    with self.assertRaises(RuntimeError):m.run(a)
    a.verify=False;a.evidence=root/'repeat.json'
    with self.assertRaises(RuntimeError):m.run(a)
    target.write_bytes(b'old');a.evidence=root/'partial.json';a.apply=True
    with patch.object(m,'output_state',side_effect=[{'state':'same'},{'state':'drift'}]):
     with self.assertRaises(RuntimeError):m.run(a)
    self.assertEqual(target.read_bytes(),b'new')  # No automatic rollback.
    self.assertFalse(json.loads(a.evidence.read_text())['applied'])
    self.assertEqual(a.evidence.with_suffix('.before.java').read_bytes(),b'old')
 def test_hash_mismatch_and_unchanged_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x';p.write_bytes(b'bad')
   with self.assertRaises(RuntimeError):m.hashes(Path(d),{'x':'wrong'})
  with self.assertRaises(RuntimeError):m.same_inputs({'tracked_source_diff_sha256':'a','gn':'old'},{'tracked_source_diff_sha256':'b','gn':'new'})
 def test_partial_failure_keeps_intent(self):
  # Whole output byte inventory catches payload drift, not only Ninja graph changes.
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for n in ['args.gn','build.ninja','.ninja_log','.siso_deps','apks/Test.apk']:
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'original')
   old=m.output_state(root);(root/'apks/Test.apk').write_bytes(b'changed')
   self.assertNotEqual(old,m.output_state(root))
if __name__=='__main__':unittest.main()
