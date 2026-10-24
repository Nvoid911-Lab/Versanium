"""Detect omission of the six real patch.sh edits in scratch selected fixtures."""
from pathlib import Path
import importlib.util,subprocess,tempfile,shutil,hashlib,unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('selected',ROOT/'tools/versanium/selected_patch_pipeline.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OLD=Path('/tmp/versanium-ab-reviewed-final/installed')
EXPECTED=dict(zip(m.FILES,[
 'ed5c624ed5786aa8eb579b721a32cac06c417b54428aa256f9e9b8abf020e44b',
 '04f821ef52189aa3274ac117cbc73b90f288ab084bd23e3821196a901c258160',
 'd21836bfcdf68768e7b0b962c71a5effd970d7af4d080aa423a477d3748b388e']))
class SelectedPipelineTests(unittest.TestCase):
 def fixture(self,root):
  if not OLD.is_dir():self.skipTest('historical incomplete selected fixture unavailable')
  for name in m.FILES:
   dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/name,dest)
 def hashes(self,root):return {n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in m.FILES}
 def test_real_commands_reproduce_host_report(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);m.apply(root,ROOT)
   self.assertEqual(self.hashes(root),EXPECTED)
 def test_each_missing_operation_is_detected(self):
  commands=m.commands((ROOT/'patch.sh').read_text())
  for omitted in range(len(commands)):
   with self.subTest(omitted=omitted),tempfile.TemporaryDirectory() as d:
    root=Path(d);self.fixture(root)
    for i,line in enumerate(commands):
     if i!=omitted:subprocess.run(['bash','-eu','-c',line],cwd=root,check=True)
    self.assertNotEqual(self.hashes(root),EXPECTED)
 def test_new_target_operation_requires_coverage_review(self):
  text=(ROOT/'patch.sh').read_text()+'\nsed -i s/a/b/ '+m.FILES[0]+'\n'
  with self.assertRaises(RuntimeError):m.commands(text)
 def test_native_edit_order_commutes_with_overlay(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root)
   patch=subprocess.check_output(['git','-C',str(ROOT),'show','60b0037:tools/environment_zoom/chromium.patch'])
   # Undo only the scratch native overlay, then replay real common-edit→overlay order.
   subprocess.run(['git','apply','-R','--include='+m.FILES[0],'-'],input=patch,cwd=root,check=True)
   m.apply(root,ROOT)
   subprocess.run(['git','apply','--include='+m.FILES[0],'-'],input=patch,cwd=root,check=True)
   self.assertEqual(self.hashes(root),EXPECTED)
if __name__=='__main__':unittest.main()
