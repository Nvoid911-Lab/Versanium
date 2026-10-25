"""Content host preparation fixtures. Never real host evidence/graph/build validation."""
from pathlib import Path
from unittest.mock import patch
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/versanium'))
import prepare_content_diagnostic as m
import content_diagnostic_graph as g

class ContentPreparationTests(unittest.TestCase):
 def test_separate_post_gn_audit_rejects_non_graph_changes(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);a,p,h=self.evidence(r);s=a.workspace/'chromium/src';out=s/'out/Default'
   for name in ['args.gn','build.ninja','.ninja_log','.siso_deps']:(out/name).write_bytes(b'old')
   (s/'one.cc').write_bytes(b'old');before={'one.cc':m.sha(b'old')};after={'one.cc':m.sha(b'new')};data={'before':before,'after':after}
   updated=dict(p,tracked_source_diff_sha256='Content');rec=types.SimpleNamespace(record=lambda *args:updated)
   def inputs(args,expected,mode):
    m.require_files(s,after if mode=='after' else before);return s,out,data,before,after,'selected',rec
   def plan(*args,**kwargs):return {'graph_hashes':{'build.ninja':m.digest(out/'build.ninja')},'gn_generator_edges':[{'outputs':['build.ninja']}]} 
   with patch.multiple(m,SOURCE_HASH=h['src'],PROVENANCE_HASH=h['prov'],APK=m.sha(b'signed'),UNSIGNED=m.sha(b'unsigned')),patch.object(m,'controller_chain',return_value={'proof':'fixed'}),patch.object(m,'inputs',side_effect=inputs),patch.object(m,'tools_and_config',return_value=({},{})),patch.object(m,'graph_plan',side_effect=plan),patch.object(m,'reproduce',return_value={'one.cc':b'new'}),patch.object(m,'other_sources',return_value={'same':'sources'}),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=1)):
    a.apply=True;a.evidence=r/'applied.json';m.run(a);application=a.evidence
    (out/'build.ninja').write_bytes(b'new graph')
    a.apply=False;a.audit_after_gn=True;a.application_record=application;a.gn_status=r/'gn.status';a.gn_status.write_text('0\n');a.gn_log=r/'gn.log';a.gn_log.write_text('fixture success');a.evidence=r/'after-gn.json'
    m.run(a);self.assertEqual(m.read(a.evidence)['phase'],'GRAPH_AFTER_GN_AUDITED_NOT_COMPILED');self.assertEqual((s/'one.cc').read_bytes(),b'new')
    (out/'args.gn').write_bytes(b'unexpected');a.evidence=r/'refused.json'
    with self.assertRaisesRegex(RuntimeError,'Non-graph'):m.run(a)
    self.assertFalse(a.evidence.exists())
 def test_gn_regeneration_decision_needs_real_generator_dependencies(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d);out=source/'out/Default';out.mkdir(parents=True)
   gntexts={
    'content/browser/BUILD.gn':'source_set("browser") media/media_web_contents_observer.cc android/web_contents_observer_proxy.cc renderer_host/render_frame_host_impl.cc web_contents/web_contents_impl.cc',
    'content/public/android/BUILD.gn':'android_library("content_full_java") generate_jni("content_jni_headers") WebContentsObserverProxy.java content_public/browser/WebContentsObserver.java',
    'chrome/android/chrome_java_sources.gni':'FullscreenVideoPictureInPictureController.java'}
   for name,text in gntexts.items():
    p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
   # Quoted source entries match the fixed membership checks.
   (source/'content/browser/BUILD.gn').write_text('source_set("browser") '+ ' '.join('"'+x+'"' for x in ['media/media_web_contents_observer.cc','android/web_contents_observer_proxy.cc','renderer_host/render_frame_host_impl.cc','web_contents/web_contents_impl.cc']))
   (out/'args.gn').write_text('use_errorprone_java_compiler = false\n')
   (out/'build.ninja').write_bytes(b'rule gn\n command = gn gen .\n depfile = build.ninja.d\nbuild build.ninja.stamp: gn ../../BUILD.gn\n')
   selected={'before':{'changed.cc':'before'},'after':{'changed.cc':'after'}}
   metadata={'graph':{'loaded_graphs':g.load(out)['files'],'objects':[{'toolchain':'//build/toolchain/android:android_clang_arm64'}]}}
   def coverage(*args):return {'jni':{'inputs':[]},'errorprone':[],'java':[{'source':'test'}]}
   with patch.object(g,'coverage',side_effect=coverage):
    plan=m.graph_plan(out,source,metadata,selected);self.assertIn('REVIEW_REQUIRED',plan['gn_regeneration_decision']);self.assertIn('NOT_PROVEN',plan['nullaway_gate'])
    (out/'build.ninja.d').write_bytes(b'build.ninja.stamp: ../../BUILD.gn\n')
    self.assertEqual(m.graph_plan(out,source,metadata,selected)['gn_regeneration_decision'],'NO_REGEN_INDICATED_BY_GRAPH_AND_DEPFILE')
    (out/'build.ninja.d').write_bytes(b'build.ninja.stamp: ../../changed.cc\n')
    self.assertEqual(m.graph_plan(out,source,metadata,selected)['gn_regeneration_decision'],'SEPARATE_GN_UPDATE_REQUIRED')
    (out/'build.ninja.d').write_bytes(b'build.ninja.stamp: ../../escaped\\ file\n')
    self.assertIn('REVIEW_REQUIRED',m.graph_plan(out,source,metadata,selected)['gn_regeneration_decision'])
 def test_controller_history_proof_and_unreviewed_product_delta(self):
  old='830fef60cec065a40b468d460089fc50dc9fb49d';audit='fdb8605f28ff870f91d87f41817c7b8d72794550'
  source={'controller':old};real=m.git
  compat={'recorded_controller':old,'audit_controller':audit,'changed_paths':real(ROOT,'diff','--no-renames','--name-only',old,audit).decode().splitlines(),'diff_sha256':m.sha(real(ROOT,'diff','--binary',old,audit))}
  def controlled(root,*args):
   if args[:2]==('status','--porcelain'):return b''
   return real(root,*args)
  with patch.object(m,'git',side_effect=controlled):
   result=m.controller_chain(ROOT,source,{'controller_compatibility':compat});self.assertEqual(result['source_controller'],old)
   def bad(root,*args):
    if args==('diff','--no-renames','--name-only',m.PRODUCT,'HEAD'):return b'tools/apply_content_fullscreen_origin.py\n'
    return controlled(root,*args)
   with patch.object(m,'git',side_effect=bad):
    with self.assertRaisesRegex(RuntimeError,'Unreviewed preparation delta'):m.controller_chain(ROOT,source,{'controller_compatibility':compat})
   wrong=dict(compat,diff_sha256='wrong')
   with self.assertRaisesRegex(RuntimeError,'Stored historical'):m.controller_chain(ROOT,source,{'controller_compatibility':wrong})
 def test_fixed_head_reconstruction(self):
  data,before,after,h=m.load_selection(ROOT);fixed=Path('/tmp/versanium156/source')
  if not all((fixed/n).exists() for n in data['before']):self.skipTest('fixed source snapshots unavailable')
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   for n in data['before']:
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((fixed/n).read_bytes())
   subprocess.run(['git','init','-q',str(r)],check=True);subprocess.run(['git','-C',str(r),'add','.'],check=True)
   subprocess.run(['git','-C',str(r),'-c','user.name=test','-c','user.email=test@example.invalid','commit','-qm','fixed156 fixture'],check=True)
   result=m.reproduce(r,ROOT,data)
   self.assertEqual(len(result),10)
   for n,b in result.items():self.assertEqual(m.sha(b),data['after'][n])
   data['before'][m.WC]='wrong'
   with self.assertRaisesRegex(RuntimeError,'mismatch'):m.reproduce(r,ROOT,data)
 def evidence(self,r):
  w=r/'saved';out=w/'chromium/src/out/Default';out.mkdir(parents=True)
  a=types.SimpleNamespace(workspace=w,control=ROOT,native_source_record=r/'source.json',build_evidence=r/'build',signed_apk=r/'signed.apk',evidence=r/'new.json',apply=False,verify=False)
  a.build_evidence.mkdir();a.signed_apk.write_bytes(b'signed');unsigned=out/'apks/ChromePublic.apk';unsigned.parent.mkdir();unsigned.write_bytes(b'unsigned')
  p={'repository_commit':m.BASE,'chromium_input':'1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775','vanadium_input':'2ae4335402eabcc6e025f3400185fe25094d8521','tracked_source_diff_sha256':'Native'}
  source={'configuration':m.NATIVE,'source_applied':True,'phase':'SOURCE_ONLY_GRAPH_UNCHANGED','updated_provenance':p,'controller':'830fef60cec065a40b468d460089fc50dc9fb49d','paths':[str(w),str(w/'chromium/src'),str(out)]}
  a.native_source_record.write_text(json.dumps(source));(a.build_evidence/'after-apk-provenance.json').write_text(json.dumps(p))
  hashes={'src':m.digest(a.native_source_record),'prov':m.digest(a.build_evidence/'after-apk-provenance.json')}
  graph={'configuration':m.NATIVE,'phase':'GRAPH_AUDITED_NOT_COMPILED','source_record_sha256':hashes['src'],'provenance':p}
  (a.build_evidence/'graph-audited.json').write_text(json.dumps(graph))
  signed={'configuration':m.NATIVE,'source_record_sha256':hashes['src'],'after_apk_provenance_sha256':hashes['prov'],'signed_sha256':m.digest(a.signed_apk),'unsigned_sha256':m.digest(unsigned),'certificate_sha256':m.CERT,'signed_apk':str(a.signed_apk),'unsigned_apk':str(unsigned),'windows_copy':'not-read'}
  (a.build_evidence/'signed-apk-record.json').write_text(json.dumps(signed))
  return a,p,hashes
 def test_native_record_graph_signed_links_and_wrong_configuration(self):
  with tempfile.TemporaryDirectory() as d:
   a,p,h=self.evidence(Path(d))
   with patch.multiple(m,SOURCE_HASH=h['src'],PROVENANCE_HASH=h['prov'],APK=m.sha(b'signed'),UNSIGNED=m.sha(b'unsigned')):
    old=a.native_source_record.read_bytes();m.records(a);self.assertEqual(old,a.native_source_record.read_bytes())
    graphfile=a.build_evidence/'graph-audited.json';value=m.read(graphfile);value['source_record_sha256']='wrong';graphfile.write_text(json.dumps(value))
    with self.assertRaisesRegex(RuntimeError,'link mismatch'):m.records(a)
    value['source_record_sha256']=h['src'];graphfile.write_text(json.dumps(value))
    signed=a.build_evidence/'signed-apk-record.json';v=m.read(signed);v['certificate_sha256']='wrong';signed.write_text(json.dumps(v))
    with self.assertRaisesRegex(RuntimeError,'certificate'):m.records(a)
    v['certificate_sha256']=m.CERT;v['configuration']='AOriginForward';signed.write_text(json.dumps(v))
    with self.assertRaisesRegex(RuntimeError,'Signed record'):m.records(a)
    a.signed_apk.write_bytes(b'wrong')
    v['configuration']=m.NATIVE;signed.write_text(json.dumps(v))
    with self.assertRaisesRegex(RuntimeError,'APK mismatch'):m.records(a)
 def test_source_transaction_read_apply_verify_partial_and_output_drift(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);a,p,h=self.evidence(r);s=a.workspace/'chromium/src';out=s/'out/Default'
   for name in ['args.gn','build.ninja','.ninja_log','.siso_deps']:(out/name).write_bytes(b'stable')
   for name in ['a.cc','b.java']:(s/name).write_bytes(b'old')
   before={n:m.sha(b'old') for n in ['a.cc','b.java']};after={n:m.sha(b'new') for n in before};data={'before':before,'after':after};updated=dict(p,tracked_source_diff_sha256='Content');rec=types.SimpleNamespace(record=lambda *args:updated)
   def inputs(args,expected,mode):
    m.require_files(s,after if mode=='after' else before);return s,out,data,before,after,'selection',rec
   kwargs={'SOURCE_HASH':h['src'],'PROVENANCE_HASH':h['prov'],'APK':m.sha(b'signed'),'UNSIGNED':m.sha(b'unsigned')}
   with patch.multiple(m,**kwargs),patch.object(m,'controller_chain',return_value={'proof':'fixed'}),patch.object(m,'inputs',side_effect=inputs),patch.object(m,'tools_and_config',return_value=({},{})),patch.object(m,'graph_plan',return_value={'checked':'fixture'}),patch.object(m,'reproduce',return_value={n:b'new' for n in before}),patch.object(m,'other_sources',return_value={'same':'tracked'}),patch.object(m.subprocess,'run',return_value=types.SimpleNamespace(returncode=1)):
    m.run(a);self.assertEqual(m.read(a.evidence)['phase'],'READ_ONLY_COMPLETE');self.assertEqual((s/'a.cc').read_bytes(),b'old')
    a.apply=True;a.evidence=r/'applied.json';m.run(a);self.assertTrue(m.read(a.evidence)['applied'])
    self.assertEqual((a.evidence.with_suffix('.before')/'evidence/signed-apk-record.json').read_bytes(),(a.build_evidence/'signed-apk-record.json').read_bytes())
    a.apply=False;a.verify=True;m.run(a)
    (out/'args.gn').write_bytes(b'drift')
    with self.assertRaisesRegex(RuntimeError,'Output'):m.run(a)
    (out/'args.gn').write_bytes(b'stable');a.verify=False;a.evidence=r/'repeat.json'
    with self.assertRaisesRegex(RuntimeError,'mismatch'):m.run(a)
    for n in before:(s/n).write_bytes(b'old')
    a.apply=True;a.evidence=r/'partial.json';write=Path.write_bytes
    def fail(path,value):
     if path==s/'b.java':raise OSError('fixture partial failure')
     return write(path,value)
    with patch.object(Path,'write_bytes',fail):
     with self.assertRaises(OSError):m.run(a)
    self.assertFalse(m.read(a.evidence)['applied']);self.assertEqual((s/'a.cc').read_bytes(),b'new');self.assertEqual((s/'b.java').read_bytes(),b'old')
    self.assertEqual((a.evidence.with_suffix('.before')/'source/a.cc').read_bytes(),b'old')
 def make_java_graph(self,d):
  source=Path(d);out=source/'out/Default';out.mkdir(parents=True)
  proxy='content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsObserverProxy.java'
  observer='content/public/android/java/src/org/chromium/content_public/browser/WebContentsObserver.java'
  pip=m.PIP
  cpp=[m.RFH,m.WC,'content/browser/media/media_web_contents_observer.cc','content/browser/android/web_contents_observer_proxy.cc']
  header=b'gen/jni_headers/content/public/android/content_jni_headers/WebContentsObserverProxy_jni.h'
  jni_rule=b'__content_public_android_content_jni_headers__action___build_toolchain_android_android_clang_arm64__rule'
  lines=[b'# nonUTF8 \xff\xfe',b'rule cxx',b' command = clang++ $in',b'rule '+jni_rule,b' command = python ../../third_party/jni_zero/jni_zero.py $in',b'build $:all_rust: phony']
  jni_line=b'build '+header+b' gen/content.srcjar: '+jni_rule+b' ../../'+proxy.encode()+b' ../../third_party/jni_zero/jni_zero.py\n'
  java_rules=[b'__content_public_android_content_full_java__compile_java___build_toolchain_android_android_clang_arm64__rule',b'__chrome_android_chrome_java__compile_java___build_toolchain_android_android_clang_arm64__rule']
  java_lines=b''
  for rule in java_rules:java_lines+=b'rule '+rule+b'\n command = python ../../build/android/gyp/compile_java.py $in\n'
  java_lines+=b'build obj/content/public/android/content_full_java.javac.jar obj/content/public/android/content_full_java.javac.jar.info obj/content/public/android/content_full_java.compliment.jar: '+java_rules[0]+b' ../../'+proxy.encode()+b' ../../'+observer.encode()+b' gen/content.srcjar\n'
  java_lines+=b'build obj/chrome/android/chrome_java.javac.jar obj/chrome/android/chrome_java.javac.jar.info: '+java_rules[1]+b' ../../'+pip.encode()+b' obj/content/public/android/content_full_java.javac.jar\n'
  (out/'toolchain.ninja').write_bytes(jni_line+java_lines)
  lines.append(b'include toolchain.ninja')
  for i,n in enumerate(cpp):lines.append(b'build obj/actual'+str(i).encode()+b'.o: cxx ../../'+n.encode()+b' || '+header)
  lines.append(b'subninja other.ninja');(out/'build.ninja').write_bytes(b'\n'.join(lines)+b'\n')
  (out/'other.ninja').write_bytes(b'rule cxx\n command = othercompiler $in\nbuild other/obj/x.o: cxx ../../'+cpp[0].encode()+b'\n')
  return source,out,proxy,observer,pip,cpp,header,jni_rule,jni_line,java_lines,java_rules
 def test_literal_graph_jni_java_native_dependencies_and_scope(self):
  with tempfile.TemporaryDirectory() as d:
   source,out,proxy,observer,pip,cpp,header,jni_rule,jni_line,java_lines,java_rules=self.make_java_graph(d)
   data=g.load(out);plan=g.coverage(data,out,source,'//build/toolchain/android:android_clang_arm64')
   self.assertEqual(len(plan['objects']),4);self.assertEqual(plan['jni']['target'],header.decode())
   self.assertTrue(all(x['target'].startswith('obj/') for x in plan['objects']))
   # Same basename/recipe is insufficient: exact layout/action/default toolchain/input required.
   for wrong in [
    jni_line.replace(b'gen/jni_headers/',b'gen/'),
    jni_line.replace(jni_rule,jni_rule.replace(b'arm64',b'arm')),
    jni_line.replace(jni_rule,b'another_action'),
    jni_line.replace(proxy.encode(),observer.encode()),
   ]:
    (out/'toolchain.ninja').write_bytes(wrong+java_lines)
    with self.assertRaises(g.MissingCoverage):g.coverage(g.load(out),out,source,'//build/toolchain/android:android_clang_arm64')
   (out/'toolchain.ninja').write_bytes(jni_line+java_lines)
   recipe_data=g.load(out)
   recipe_data['rules'][(0,jni_rule)]=[b' command = other_generator.py $in']
   recipe_data['outputs'][header]['inputs']=[b'../../'+proxy.encode()]
   with self.assertRaises(g.MissingCoverage):g.coverage(recipe_data,out,source,'//build/toolchain/android:android_clang_arm64')
   with self.assertRaises(g.UnsupportedGraph):g.coverage(g.load(out),out,source,'//build/toolchain/android:android_clang_arm')
   ambiguous=g.load(out)
   edge=ambiguous['outputs'][header]
   ambiguous['edges'].append(dict(edge))
   with self.assertRaisesRegex(g.MissingCoverage,'ambiguous'):g.coverage(ambiguous,out,source,'//build/toolchain/android:android_clang_arm64')
   (out/'toolchain.ninja').write_bytes(jni_line+jni_line+java_lines)
   with self.assertRaisesRegex(g.UnsupportedGraph,'Duplicate decoded'):g.load(out)
   (out/'toolchain.ninja').write_bytes(jni_line+java_lines)

   for java_file,dependency in [('toolchain.ninja',b' gen/content.srcjar'),('toolchain.ninja',b' obj/content/public/android/content_full_java.javac.jar')]:
    f=out/java_file;original_java=f.read_bytes();f.write_bytes(original_java.replace(dependency+b'\n',b'\n'))
    with self.assertRaisesRegex(g.MissingCoverage,'dependency'):g.coverage(g.load(out),out,source,'//build/toolchain/android:android_clang_arm64')
    f.write_bytes(original_java)
   original=(out/'build.ninja').read_bytes();(out/'build.ninja').write_bytes(original.replace(b' || '+header,b''))
   with self.assertRaisesRegex(g.MissingCoverage,'dependency'):g.coverage(g.load(out),out,source,'//build/toolchain/android:android_clang_arm64')
   (out/'build.ninja').write_bytes(original+b'build $:all_rust: phony\n')
   with self.assertRaisesRegex(g.UnsupportedGraph,'Duplicate decoded'):g.load(out)
   with self.assertRaises(g.UnsupportedGraph):g.parse_edge(b'$unknown: phony')
   self.assertEqual(g.parse_edge(b'a$ b$$$:c | implicit$:x: phony in$ file')['outputs'],[b'a b$:c',b'implicit:x'])

 def test_java_rule_identity_outputs_and_unique_production_candidates(self):
  with tempfile.TemporaryDirectory() as d:
   source,out,proxy,observer,pip,cpp,header,jni_rule,jni_line,java_lines,rules=self.make_java_graph(d)
   toolchain='//build/toolchain/android:android_clang_arm64'
   good=jni_line+java_lines
   for rule in rules:
    for wrong in [rule.replace(b'arm64',b'arm'),rule.replace(b'__compile_java',b'_test__compile_java'),rule.replace(b'__compile_java',b'_similar__compile_java')]:
     (out/'toolchain.ninja').write_bytes(good.replace(rule,wrong))
     with self.assertRaises(g.MissingCoverage):g.coverage(g.load(out),out,source,toolchain)
   for wrong in [jni_line+java_lines.replace(name.encode(),b'other.java') for name in [proxy,observer,pip]]+[good.replace(b'content_full_java.javac.jar.info',b'content_full_java.wrong.info'),good.replace(b'compile_java.py',b'turbine.py')]:
    (out/'toolchain.ninja').write_bytes(wrong)
    with self.assertRaises((g.MissingCoverage,g.UnsupportedGraph)):g.coverage(g.load(out),out,source,toolchain)
   # Distracting toolchain/test/similar-name actions do not establish membership.
   distractors=b''
   for wrong in [rules[0].replace(b'arm64',b'arm'),rules[0].replace(b'__compile_java',b'_test__compile_java'),rules[0].replace(b'__compile_java',b'_similar__compile_java')]:
    distractors+=b'rule '+wrong+b'\n command = python compile_java.py $in\nbuild obj/'+wrong+b'.jar: '+wrong+b' ../../'+proxy.encode()+b'\n'
   (out/'toolchain.ninja').write_bytes(good+distractors)
   self.assertEqual(len(g.coverage(g.load(out),out,source,toolchain)['java']),3)
   (out/'toolchain.ninja').write_bytes(good)
   duplicate=g.load(out);duplicate['edges'].append(dict(duplicate['outputs'][b'obj/chrome/android/chrome_java.javac.jar']))
   with self.assertRaisesRegex(g.MissingCoverage,'ambiguous'):g.coverage(duplicate,out,source,toolchain)
   # Membership is rule/output based, not a Ninja file basename.
   (out/'renamed-action-storage.ninja').write_bytes(java_lines)
   (out/'toolchain.ninja').write_bytes(jni_line+b'include renamed-action-storage.ninja\n')
   self.assertEqual(len(g.coverage(g.load(out),out,source,toolchain)['java']),3)
 def test_separate_errorprone_actions_nullaway_shards_and_validation(self):
  with tempfile.TemporaryDirectory() as d:
   source,out,proxy,observer,pip,cpp,header,jni_rule,jni_line,java_lines,rules=self.make_java_graph(d)
   toolchain='//build/toolchain/android:android_clang_arm64'
   baseline=g.coverage(g.load(out),out,source,toolchain)
   self.assertEqual(baseline['errorprone'],[])
   self.assertFalse(any(x['compiler_nullaway_flag_observed'] for x in baseline['java']))
   ep=b'';stamps=[]
   for rule,directory,family,names in [(rules[0],b'content/public/android',b'content_full_java',[proxy,observer]),(rules[1],b'chrome/android',b'chrome_java',[pip])]:
    # Content uses two shards, chrome the unsharded target.
    for index,name in enumerate(names):
     suffix=b'_shard'+str(index).encode() if len(names)>1 else b''
     label=family+b'__errorprone'+suffix;stamp=b'obj/'+directory+b'/'+label+b'.stamp';stamps.append(stamp)
     ep_rule=rule.replace(b'__compile_java',b'__errorprone'+suffix)
     ep+=b'rule '+ep_rule+b'\n command = python ../../build/android/gyp/errorprone.py --enable-nullaway $in\n'
     ep+=b'build '+stamp+b': '+ep_rule+b' ../../'+name.encode()+b'\n'
   validated=java_lines.replace(b' gen/content.srcjar\n',b' gen/content.srcjar |@ '+b' '.join(stamps[:2])+b'\n').replace(b' obj/content/public/android/content_full_java.javac.jar\n',b' obj/content/public/android/content_full_java.javac.jar |@ '+stamps[2]+b'\n')
   good=jni_line+validated+ep;(out/'toolchain.ninja').write_bytes(good)
   plan=g.coverage(g.load(out),out,source,toolchain)
   self.assertEqual(len(plan['errorprone']),3);self.assertTrue(all(x['nullaway_flag_observed'] for x in plan['errorprone']))
   self.assertTrue(all('compile_java' in x['rule'] for x in plan['java']))
   for unrelated in [ep.replace(b'arm64',b'arm'),ep.replace(b'__errorprone',b'_test__errorprone'),ep.replace(b'__errorprone',b'_similar__errorprone')]:
    (out/'toolchain.ninja').write_bytes(jni_line+validated+unrelated)
    unrelated_plan=g.coverage(g.load(out),out,source,toolchain)
    self.assertEqual(unrelated_plan['errorprone'],[])
    self.assertEqual(unrelated_plan['nullaway_status'],'NOT_PROVEN_NO_ACTIONS_FOUND')
   (out/'toolchain.ninja').write_bytes(good.replace(b'--enable-nullaway',b''))
   self.assertTrue(all(not x['nullaway_flag_observed'] for x in g.coverage(g.load(out),out,source,toolchain)['errorprone']))
   (out/'toolchain.ninja').write_bytes(good.replace(b'../../'+observer.encode()+b'\n',b'../../other.java\n'))
   with self.assertRaisesRegex(g.UnsupportedGraph,'membership'):g.coverage(g.load(out),out,source,toolchain)
   (out/'toolchain.ninja').write_bytes(jni_line+java_lines+ep)
   with self.assertRaisesRegex(g.UnsupportedGraph,'validations'):g.coverage(g.load(out),out,source,toolchain)
   (out/'toolchain.ninja').write_bytes(good.replace(b'content_full_java__errorprone_shard0.stamp',b'content_full_java__errorprone_shard0.wrong'))
   with self.assertRaisesRegex(g.UnsupportedGraph,'output'):g.coverage(g.load(out),out,source,toolchain)
   (out/'toolchain.ninja').write_bytes(good)
   duplicate=g.load(out);duplicate['edges'].append(dict(duplicate['outputs'][stamps[0]]))
   with self.assertRaisesRegex(g.UnsupportedGraph,'Ambiguous'):g.coverage(duplicate,out,source,toolchain)
