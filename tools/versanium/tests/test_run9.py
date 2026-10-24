"""Limited Run9 recovery tests. No preserved host tree or compiler is invoked."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest,json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('run9',ROOT/'tools/versanium/prepare_run9.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
BASEPATCH=subprocess.check_output(['git','-C',str(ROOT),'show',r.BASE+':tools/youtube_pip/execution_scope.patch'],text=True)
lines=BASEPATCH.splitlines();start=next(i for i,l in enumerate(lines) if l.startswith('+bool RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed('));end=next(i for i in range(start,len(lines)) if lines[i]=='+}')
OLD='\n'.join(l[1:] for l in lines[start:end+1])
EDGE=('build '+r.OBJECT_TARGET+': cxx ../../'+r.TARGET+'\n').encode('ascii')
class Run9Tests(unittest.TestCase):
 def test_exact_three_only(self):
  before='// unrelated host_piece() stays\n'+OLD+'\n'
  self.assertEqual(r.replacement(before,BASEPATCH),before.replace('candidate_url.host_piece()','candidate_url.host()'))
  self.assertEqual(subprocess.check_output(['git','-C',str(ROOT),'show','ebfc81cf6ef4388f0f1b29be86e0eb212bc7bce1:tools/youtube_pip/execution_scope.patch'],text=True),BASEPATCH.replace('candidate_url.host_piece()','candidate_url.host()'))
 def test_scope_edits_rejected(self):
  for altered in [OLD.replace('https','http'),OLD.replace('www.youtube.com','twitch.tv'),OLD.replace('IsOffTheRecord()','IsGuest()'),OLD.replace('IsActive()','Other()')]:
   with self.assertRaises(RuntimeError):r.replacement(altered,BASEPATCH)
 def test_forged_gurl_header_rejected_before_model(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'url').mkdir();(root/'url/gurl.h').write_text('std::string_view host() const LIFETIME_BOUND {}')
   check=subprocess.run(['python3',str(ROOT/'tools/youtube_pip/tests/check_execution_scope.py'),'--applied-tree',str(root)],capture_output=True,text=True)
   self.assertNotEqual(check.returncode,0)
   self.assertIn('pinned GURL header',check.stderr)
 def test_wrong_workspace_rejected(self):
  with self.assertRaises(RuntimeError):r.validate(Path('/tmp/not-run9'),Path('/tmp/control'),{})
 def test_wrong_saved_head_rejected(self):
  ws=Path('/tmp/versanium-next-test-39951209951')
  with patch.object(r,'git',return_value='wrong'):
   with self.assertRaises(RuntimeError):r.validate(ws,Path('/tmp/control'),{})
 def test_repeat_rejected(self):
  with self.assertRaises(RuntimeError):r.replacement(OLD.replace('host_piece()','host()'),BASEPATCH)
 def test_artifact_digest_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'zip';p.write_bytes(b'not the original artifact')
   with self.assertRaises(RuntimeError):r.original_manifest(p)
 def test_unique_real_object(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'browser.ninja';p.write_bytes(EDGE)
   self.assertEqual(r.object_target(Path(d)),r.OBJECT_TARGET)
 def test_non_utf8_unrelated_ninja_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'browser.ninja').write_bytes(EDGE)
   p=root/'android_clang_arm/obj/third_party/rust/lazy_static/v1/lib.ninja'
   p.parent.mkdir(parents=True)
   p.write_bytes(b'#'+b'x'*1318+b'\xff\xfe\n'+b'build obj/unrelated.o: cxx non-utf8-\xff.cc\n')
   before={f:f.read_bytes() for f in root.rglob('*.ninja')}
   self.assertEqual(r.object_target(root),r.OBJECT_TARGET)
   self.assertEqual(before,{f:f.read_bytes() for f in root.rglob('*.ninja')})
 def test_multiple_toolchains_choose_exact_log_target(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   (root/'browser.ninja').write_bytes(EDGE)
   for toolchain in ['android_clang_arm','clang_x64']:
    p=root/toolchain/'browser.ninja';p.parent.mkdir()
    p.write_bytes(EDGE.replace(b'build obj/',('build '+toolchain+'/obj/').encode('ascii')))
   self.assertEqual(r.object_target(root),r.OBJECT_TARGET)
 def test_missing_log_target_rejected_even_with_other_toolchain(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(RuntimeError):r.object_target(Path(d))
   (Path(d)/'x.ninja').write_bytes(EDGE.replace(b'build obj/',b'build android_clang_arm/obj/'))
   with self.assertRaises(RuntimeError):r.object_target(Path(d))
 def test_duplicate_exact_target_rejected(self):
  for separate_file in [False,True]:
   with self.subTest(separate_file=separate_file),tempfile.TemporaryDirectory() as d:
    root=Path(d);(root/'browser.ninja').write_bytes(EDGE if separate_file else EDGE+EDGE)
    if separate_file:(root/'duplicate.ninja').write_bytes(EDGE)
    with self.assertRaisesRegex(RuntimeError,'found 2'):r.object_target(root)
 def test_wrong_rule_source_or_output_shape_rejected(self):
  source=('../../'+r.TARGET).encode('ascii')
  cases=[EDGE.replace(b': cxx ',b': cc '),
         EDGE.replace(source,source+b'.other'),
         EDGE.replace(source,b'other/'+source),
         EDGE.replace(source,b'other.cc | '+source),
         EDGE.replace(source,source+b' other.cc'),
         EDGE.replace(b': cxx ',b' other.o: cxx '),
         EDGE.replace(b': cxx ',b' | other.o: cxx '),
         EDGE.replace(b': cxx ',b' cxx '),
         EDGE.replace(source,source+b'\xff')]
  for edge in cases:
   with self.subTest(edge=edge),tempfile.TemporaryDirectory() as d:
    (Path(d)/'browser.ninja').write_bytes(edge)
    with self.assertRaises(RuntimeError):r.object_target(Path(d))
 def test_continuations_and_dependency_sections(self):
  for newline in [b'\n',b'\r\n']:
   with self.subTest(newline=newline),tempfile.TemporaryDirectory() as d:
    edge=(b'build '+r.OBJECT_TARGET.encode('ascii')+b': cxx $'+newline+
          b'  ../../'+r.TARGET.encode('ascii')+b' | generated.h $'+newline+
          b'  || stamp |@ validation'+newline)
    (Path(d)/'browser.ninja').write_bytes(edge)
    self.assertEqual(r.object_target(Path(d)),r.OBJECT_TARGET)
 def test_literal_dollar_does_not_hide_duplicate_edge(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'browser.ninja').write_bytes(EDGE+b'value = literal$$\n'+EDGE)
   with self.assertRaisesRegex(RuntimeError,'found 2'):r.object_target(Path(d))
 def test_comment_dollar_does_not_hide_target_or_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'browser.ninja';p.write_bytes(b'# unrelated comment $\n'+EDGE)
   self.assertEqual(r.object_target(Path(d)),r.OBJECT_TARGET)
   p.write_bytes(EDGE+b'  # unrelated comment $\n'+EDGE)
   with self.assertRaisesRegex(RuntimeError,'found 2'):r.object_target(Path(d))
 def test_incomplete_continuation_rejected(self):
  for suffix in [b'$\n',b' | dep$\n']:
   with self.subTest(suffix=suffix),tempfile.TemporaryDirectory() as d:
    (Path(d)/'browser.ninja').write_bytes(EDGE.rstrip(b'\n')+suffix)
    with self.assertRaises(RuntimeError):r.object_target(Path(d))
 def test_dry_run_and_apply_preserve_state(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);ws=root/'saved';control=root/'control';control.mkdir();source=ws/'chromium/src';out=source/'out/Default';out.mkdir(parents=True)
   gn=source/'buildtools/linux64/gn';gn.parent.mkdir(parents=True);gn.write_bytes(b'fixture gn')
   target=source/r.TARGET;target.parent.mkdir(parents=True);target.write_text(OLD)
   for name in ['args.gn','build.ninja','.ninja_log','.siso_deps']:(out/name).write_text('saved-'+name)
   (out/'build.ninja').write_bytes(EDGE)
   extra=out/'android_clang_arm/obj/third_party/rust/lazy_static/v1/lib.ninja'
   extra.parent.mkdir(parents=True)
   extra.write_bytes(b'# invalid UTF-8: \xff\n'+EDGE.replace(b'build obj/',b'build android_clang_arm/obj/'))
   state={p:p.read_bytes() for p in out.rglob('*') if p.is_file()}
   (control/'tools/youtube_pip').mkdir(parents=True)
   (control/'tools/youtube_pip/execution_scope.patch').write_text(BASEPATCH.replace('host_piece()','host()'))
   fake=lambda args,**kw: BASEPATCH if 'show' in args else b'new tracked diff'
   with patch.object(r,'original_manifest',return_value={}),patch.object(r,'validate',return_value=(source,out,{})),patch.object(r,'git',return_value='controller'),patch.object(r.subprocess,'check_output',side_effect=fake),patch.object(r.subprocess,'run') as run:
    run.return_value.returncode=1
    r.prepare(ws,control,root/'zip',root/'dry.json',False)
    self.assertEqual(target.read_text(),OLD)
    run.return_value.returncode=0
    with self.assertRaises(RuntimeError):r.prepare(ws,control,root/'zip',root/'busy.json',True)
    self.assertEqual(target.read_text(),OLD)
    self.assertFalse((root/'busy.json').exists())
    run.return_value.returncode=1
    r.prepare(ws,control,root/'zip',root/'apply.json',True)
    self.assertEqual(target.read_text(),OLD.replace('host_piece()','host()'))
    self.assertTrue(json.loads((root/'apply.json').read_text())['applied'])
    self.assertEqual(json.loads((root/'apply.json').read_text())['object_target'],r.OBJECT_TARGET)
    self.assertEqual((root/'apply.native-before.cc').read_text(),OLD)
    r.verify_applied(ws,control,root/'zip',root/'apply.json')
    (out/'args.gn').write_text('unexpected drift')
    with self.assertRaises(RuntimeError):r.verify_applied(ws,control,root/'zip',root/'apply.json')
    (out/'args.gn').write_bytes(state[out/'args.gn'])
   self.assertEqual(state,{p:p.read_bytes() for p in out.rglob('*') if p.is_file()})
if __name__=='__main__':unittest.main()
