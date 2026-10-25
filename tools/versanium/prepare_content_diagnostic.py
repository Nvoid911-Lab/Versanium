"""Native→content product host preparation. No old apply helpers, GN gen or build."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
import content_diagnostic_graph as graph
os.environ['GIT_OPTIONAL_LOCKS']='0'

PRODUCT='415f6df9bb70d1e3c062c398c05ebebc997772ee'
BASE='7d9102f4f0e35dec9f69425de44cd889836a88ac'
NATIVE='AOriginForwardNative'
NEXT='NativeContentOrigin'
APK='fba3cbd639abdb0c00d9e7c1d4621e61580efde1fb9126ce8545437261923bc7'
UNSIGNED='fa495a0ff390facf02c7e62b4f7ddc384ea502ce6b397b566bb222b8388659f9'
CERT='2e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120'
SOURCE_HASH='5934cc6dd0074b66d95cd6ae8f94236de7977e453b93a5db910cdcfe23c920d4'
PROVENANCE_HASH='7331a3d310403149b05d705ffa5f07b699db4138969936a602e597b3699a03b3'
SELECTION='docs/versanium/content-fullscreen-diagnostic-selection.json'
TRANSFORM='tools/apply_content_fullscreen_origin.py'
NATIVE_MANIFEST='docs/versanium/config-a-origin-forward-native-manifest.json'
PIP='chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'
RFH='content/browser/renderer_host/render_frame_host_impl.cc'
WC='content/browser/web_contents/web_contents_impl.cc'
def need(ok,message):
    if not ok:raise RuntimeError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def blob(c,rev,name):return git(c,'show',rev+':'+name)
def read(path):return json.loads(path.read_text())
def create(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2)
def require_files(root,values):
    for n,h in values.items():
        p=root/n;need(p.is_file() and not p.is_symlink() and p.resolve()==p,'Missing/aliased selected input: '+n)
        need(digest(p)==h,'Selected input mismatch: '+n)
def load_selection(c):
    raw=blob(c,PRODUCT,SELECTION);need((c/SELECTION).read_bytes()==raw,'Product selection changed')
    data=json.loads(raw);before=dict(data['preserved_baseline'],**data['before']);after=dict(data['preserved_baseline'],**data['after'])
    native=json.loads(blob(c,PRODUCT,NATIVE_MANIFEST))['files'][NATIVE]
    need(len(before)==len(after)==58 and len(data['before'])==len(data['after'])==10,'Wrong selection shape')
    need(all(before[n]==h for n,h in native.items()),'Native51 baseline/B exclusion differs')
    need(set(before)==set(after) and {n for n in before if before[n]!=after[n]}==set(data['before']),'Wrong changed paths')
    return data,before,after,sha(raw)
def product_module(c,name,rev=PRODUCT):
    path=c/name;need(path.read_bytes()==blob(c,rev,name),'Pinned transform drift: '+name)
    spec=importlib.util.spec_from_file_location('content_pinned_'+path.stem,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def reproduce(source,c,data):
    with tempfile.TemporaryDirectory(prefix='content-fixed-reproduce-') as d:
        r=Path(d)
        for name in data['before']:
            p=r/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git(source,'show','HEAD:'+name))
        for rev,patch,name in [('5faa9ad43438e1b696ed79f1ccff6effe4c2a3fb','tools/youtube_pip/diagnostics.patch',PIP),('16eca84b6014b3f34cef4908c4072db3cfa7323b','tools/youtube_pip/execution_scope.patch',RFH),('60b00375def663584dfd5c6fd249d25498eeafb2','tools/environment_zoom/chromium.patch',WC)]:
            subprocess.run(['git','apply','--include='+name,'-'],cwd=r,input=blob(c,rev,patch),check=True)
        forward=product_module(c,'tools/apply_fullscreen_delegate_origin.py')
        p=r/PIP;p.write_text(forward.transform(PIP,p.read_text()))
        # One exact reviewed patch.sh product command, scratch only, never patch.sh itself.
        commands=[line for line in blob(c,PRODUCT,'patch.sh').decode().splitlines() if line.startswith('sed -i ') and ' '+WC in line]
        need(len(commands)==1,'WC common-pipeline command coverage changed')
        subprocess.run(['bash','-eu','-c',commands[0]],cwd=r,check=True)
        require_files(r,data['before']);product_module(c,TRANSFORM).apply(r);require_files(r,data['after'])
        return {n:(r/n).read_bytes() for n in data['after']}
def ancestry(c,start,end):subprocess.run(['git','-C',str(c),'merge-base','--is-ancestor',start,end],check=True)
def controller_chain(c,source,ga):
    need(not git(c,'status','--porcelain').strip(),'Dirty separate controller')
    old=source['controller'];compat=ga['controller_compatibility'];audit=compat['audit_controller']
    for value in [old,audit]:need(len(value)==40 and all(x in '0123456789abcdef' for x in value),'Invalid recorded controller')
    need(compat['recorded_controller']==old,'Graph controller/source controller link mismatch')
    for start,end in [('830fef60cec065a40b468d460089fc50dc9fb49d',old),(old,audit),(audit,PRODUCT),(PRODUCT,'HEAD')]:ancestry(c,start,end)
    def paths(a,b):return git(c,'diff','--no-renames','--name-only',a,b).decode().splitlines()
    base_docs={'PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md'}
    repair=paths(old,audit)
    for n in repair:need(n in base_docs|{'tools/versanium/audit_native_graph.py','tools/versanium/tests/test_native_preparation.py'} or (n.startswith('docs/') and n.endswith('.md')),'Unexpected historical audit delta: '+n)
    need(compat['changed_paths']==repair and compat['diff_sha256']==sha(git(c,'diff','--binary',old,audit)),'Stored historical controller proof mismatch')
    allowed_product={'tools/apply_content_fullscreen_origin.py','tools/apply_youtube_candidates.py','tools/youtube_pip/tests/check_source_integration.py','tools/versanium/tests/test_content_origin.py',SELECTION,'docs/versanium/native-diagnostic-device-2026-10-25.log'}
    for n in paths(audit,PRODUCT):need(n in base_docs|allowed_product or (n.startswith('docs/') and n.endswith('.md')),'Unreviewed baseline→product controller delta: '+n)
    preparation={'tools/versanium/prepare_content_diagnostic.py','tools/versanium/content_diagnostic_graph.py','tools/versanium/tests/test_content_preparation.py'}
    for n in paths(PRODUCT,'HEAD'):need(n in base_docs|preparation or (n.startswith('docs/') and n.endswith('.md')),'Unreviewed preparation delta: '+n)
    for n in [NATIVE_MANIFEST,'tools/apply_fullscreen_native_origin.py','tools/versanium/prepare_native_diagnostic.py']:
        need(blob(c,old,n)==blob(c,PRODUCT,n)==(c/n).read_bytes(),'Native product/source-helper invariant failed: '+n)
    for n in [SELECTION,TRANSFORM,'tools/apply_youtube_candidates.py','tools/apply_fullscreen_delegate_origin.py','tools/youtube_pip/tests/check_source_integration.py']:
        need(blob(c,PRODUCT,n)==(c/n).read_bytes(),'Content product changed: '+n)
    return {'source_controller':old,'graph_audit_controller':audit,'product_controller':PRODUCT,'preparation_controller':git(c,'rev-parse','HEAD').decode().strip(),'audit_proof_sha256':sha(git(c,'diff','--binary',old,audit)),'preparation_diff_sha256':sha(git(c,'diff','--binary',PRODUCT,'HEAD'))}
def records(a):
    paths={'source':a.native_source_record,'graph':a.build_evidence/'graph-audited.json','provenance':a.build_evidence/'after-apk-provenance.json','signed':a.build_evidence/'signed-apk-record.json'}
    hashes={k:digest(v) for k,v in paths.items()};s,g,p,signed=(read(paths[k]) for k in ['source','graph','provenance','signed'])
    need(hashes['source']==SOURCE_HASH and hashes['provenance']==PROVENANCE_HASH,'Not confirmed Native source/APK provenance evidence')
    need(s.get('configuration')==NATIVE and s.get('source_applied') is True and s.get('phase')=='SOURCE_ONLY_GRAPH_UNCHANGED','Need actual completed Native source record, not Forward')
    need(s.get('paths')==[str(a.workspace),str(a.workspace/'chromium/src'),str(a.workspace/'chromium/src/out/Default')],'Native evidence saved paths mismatch')
    need(g.get('configuration')==NATIVE and g.get('phase')=='GRAPH_AUDITED_NOT_COMPILED','Need Native graph audit')
    need(g['source_record_sha256']==hashes['source'] and g['provenance']==s['updated_provenance']==p,'Native source/graph/after-apk link mismatch')
    need(p.get('repository_commit')==BASE and p.get('chromium_input')=='1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775' and p.get('vanadium_input')=='2ae4335402eabcc6e025f3400185fe25094d8521','Wrong Native pins')
    need(signed.get('configuration')==NATIVE and signed.get('source_record_sha256')==hashes['source'] and signed.get('after_apk_provenance_sha256')==hashes['provenance'],'Signed record source/provenance mismatch')
    need(signed.get('signed_sha256')==APK and signed.get('certificate_sha256')==CERT and signed.get('unsigned_sha256')==UNSIGNED,'Signed record hash/certificate mismatch')
    need(Path(signed['signed_apk']).resolve()==a.signed_apk.resolve() and digest(a.signed_apk)==APK,'Signed Native APK mismatch')
    unsigned=a.workspace/'chromium/src/out/Default/apks/ChromePublic.apk'
    need(Path(signed['unsigned_apk']).resolve()==unsigned.resolve() and digest(unsigned)==UNSIGNED,'Native unsigned APK mismatch')
    hashes.update(signed_apk=APK,unsigned_apk=UNSIGNED)
    return s,g,p,signed,hashes
def state(root):
    data={}
    for f in sorted(root.rglob('*')):
        name=str(f.relative_to(root))
        if f.is_symlink():data[name]={'link':os.readlink(f)}
        elif f.is_file():
            st=f.stat();data[name]={'sha256':digest(f),'mode':st.st_mode,'size':st.st_size,'mtime_ns':st.st_mtime_ns}
    for n in ['args.gn','build.ninja','.ninja_log','.siso_deps']:need(n in data and 'sha256' in data[n],'Missing saved output state: '+n)
    return data
def other_sources(source,names):
    return {'tracked_diff':sha(git(source,'diff','HEAD','--','.',*[':(exclude)'+n for n in names])),'untracked_names':sha(git(source,'ls-files','--others','--exclude-standard','-z'))}
def original_recorder(w,c,source):
    for n in ['tools/versanium/write_build_provenance.py','tools/check_environment_zoom_revision.py']:need((w/n).read_bytes()==blob(c,BASE,n),'Original recorder/validator changed')
    need((source/'buildtools/linux64/gn').is_file(),'Saved GN absent; no bootstrap')
    need(not git(w/'depot_tools','status','--porcelain','--untracked-files=no').strip(),'depot_tools tracked drift')
    os.environ['DEPOT_TOOLS_UPDATE']='0';os.environ['PATH']=str(source/'buildtools/linux64')+os.pathsep+str(w/'depot_tools')+os.pathsep+os.environ['PATH'];sys.path.insert(0,str(w/'tools'))
    spec=importlib.util.spec_from_file_location('content_original_build_record',w/'tools/versanium/write_build_provenance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def inputs(a,baseline,mode):
    w=a.workspace;c=a.control;s=w/'chromium/src';out=s/'out/Default'
    need(w.name=='versanium-next-test-39951209951' and all(p.resolve()==p for p in [w,s,out]),'Wrong/aliased saved paths')
    need(c!=w and w not in c.parents and git(w,'rev-parse','HEAD').decode().strip()==BASE,'Separate controller / original repository required')
    data,before,after,selection_hash=load_selection(c);require_files(s,after if mode=='after' else before)
    mod=original_recorder(w,c,s);need(mod.record(w,s)==baseline,'Current source/args/toolchain/provenance mismatch')
    return s,out,data,before,after,selection_hash,mod
def tools_and_config(a,s,source_record,g):
    tools={n:digest(s/n) for n in source_record['tools']};need(tools==source_record['tools']==g['tools'],'Toolchain hash drift')
    need(set(tools)=={'buildtools/linux64/gn','third_party/llvm-build/Release+Asserts/bin/clang','third_party/llvm-build/Release+Asserts/bin/clang++'},'Unexpected toolchain evidence shape')
    signing={n:digest(a.workspace/n) for n in source_record['signing']};need(signing==source_record['signing'],'Signing/identity source drift')
    need(set(signing)=={'common.sh','tools/configure_f11_identity.py'},'Unexpected signing source shape')
    args=(s/'out/Default/args.gn').read_text();need('target_cpu = "arm64"' in args and 'is_component_build = false' in args and 'chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,'Wrong Test identity/ABI/component args')
    return tools,signing
def graph_plan(out,source,g,selection,require_native_graph=True):
    current=graph.load(out)
    if require_native_graph:need(current['files']==g['graph']['loaded_graphs'],'Compiled Native graph bytes differ from audited graph')
    toolchains={v['toolchain'] for v in g['graph']['objects']};need(toolchains=={'//build/toolchain/android:android_clang_arm64'},'Recorded toolchain ambiguous')
    plan=graph.coverage(current,out,source,next(iter(toolchains)))
    immutable={};changing={};virtual={}
    for name in plan['jni']['inputs']:
        path=(out/name).resolve()
        need(path.is_relative_to(source.resolve()),'Outside JNI action input: '+name)
        if not path.is_file():
            producer=current['outputs'].get(os.fsencode(name))
            need(producer is not None and producer['rule']==b'phony','Missing JNI action artifact/input: '+name)
            virtual[name]=sha(graph.recipe(current,producer));continue
        relative=str(path.relative_to(source))
        if relative in selection['before']:
            changing[relative]={'before':selection['before'][relative],'after':selection['after'][relative]}
        else:immutable[name]=digest(path)
    plan['immutable_jni_inputs_sha256']=immutable;plan['changing_jni_inputs']=changing;plan['virtual_jni_dependencies']=virtual
    regeneration=[];changed={str((source/n).resolve()) for n in selection['before']}
    decision='REVIEW_REQUIRED_DYNAMIC_GN_DEPENDENCIES_NOT_PROVEN'
    for edge in current['edges']:
        if edge['rule']==b'phony' or not any(t in (b'build.ninja',b'build.ninja.stamp') for t in edge['outputs']):continue
        item={'outputs':[os.fsdecode(t) for t in edge['outputs']],'rule':os.fsdecode(edge['rule']),'ninja':edge['ninja'],'recipe_sha256':sha(graph.recipe(current,edge)),'direct_changed_inputs':[os.fsdecode(i) for i in edge['inputs'] if str(graph.path_at(out,i)) in changed],'depfile_proven':False}
        if item['direct_changed_inputs']:decision='SEPARATE_GN_UPDATE_REQUIRED'
        # Inspect the real generator's depfile, when still present. Ninja/Siso
        # may have consumed it; do not pretend absence proves no regeneration.
        depfiles=[]
        for line in graph.recipe(current,edge).split(b'\n'):
            match=re.fullmatch(rb'\s*depfile\s*=\s*(.+)',line)
            if match:depfiles.append(match.group(1))
        if len(depfiles)==1:
            value=graph.lex(depfiles[0])
            if len(value)==1 and isinstance(value[0],bytes):
                path=graph.path_at(out,value[0]);need(path.is_relative_to(out),'GN depfile outside saved output')
                item['depfile']=str(path.relative_to(out))
                if path.is_file():
                    raw=path.read_bytes().replace(b'\\\r\n',b'').replace(b'\\\n',b'')
                    # This is Make depfile syntax, not Ninja path syntax.
                    # Complex escapes are explicitly unproven, never removed.
                    item['depfile_sha256']=digest(path)
                    if b'\\' not in raw and b'$' not in raw and raw.count(b':')==1:
                        deps=raw.split(b':',1)[1].split();hit=[os.fsdecode(i) for i in deps if str(graph.path_at(out,i)) in changed]
                        item['depfile_changed_inputs']=hit
                        item['depfile_proven']=True
                        if hit:decision='SEPARATE_GN_UPDATE_REQUIRED'
                        elif decision!='SEPARATE_GN_UPDATE_REQUIRED':decision='NO_REGEN_INDICATED_BY_GRAPH_AND_DEPFILE'
        regeneration.append(item)
    if decision!='SEPARATE_GN_UPDATE_REQUIRED':
        decision='NO_REGEN_INDICATED_BY_GRAPH_AND_DEPFILE' if regeneration and all(v['depfile_proven'] for v in regeneration) else 'REVIEW_REQUIRED_DYNAMIC_GN_DEPENDENCIES_NOT_PROVEN'
    plan['gn_generator_edges']=regeneration;plan['gn_regeneration_decision']=decision
    # Actual GN membership is read, not executed; bindings and graph outputs are the build authority.
    gn={'content/browser/BUILD.gn':['source_set("browser")','"media/media_web_contents_observer.cc"','"android/web_contents_observer_proxy.cc"','"renderer_host/render_frame_host_impl.cc"','"web_contents/web_contents_impl.cc"'],
        'content/public/android/BUILD.gn':['android_library("content_full_java")','generate_jni("content_jni_headers")','WebContentsObserverProxy.java','content_public/browser/WebContentsObserver.java'],
        'chrome/android/chrome_java_sources.gni':['FullscreenVideoPictureInPictureController.java']}
    for n,anchors in gn.items():
        raw=(source/n).read_text()
        for anchor in anchors:need(anchor in raw,'GN membership anchor missing: '+n+' '+anchor)
    assignments=re.findall(r'^\s*use_errorprone_java_compiler\s*=\s*(true|false)\s*(?:#.*)?$',(out/'args.gn').read_text(),re.M)
    need(len(assignments)<=1,'Ambiguous saved ErrorProne argument')
    plan['saved_errorprone_assignment']=assignments[0] if assignments else 'NOT_EXPLICIT'
    proven={v['source'] for v in plan['errorprone'] if v['nullaway_flag_observed']}
    expected={v['source'] for v in plan['java']}
    plan['nullaway_gate']='ACTUAL_ACTION_EXECUTION_STILL_REQUIRED' if proven==expected else 'NOT_PROVEN_REQUIRES_SEPARATE_REVIEW_ARGS_UNCHANGED'
    plan['gn_inputs_sha256']={n:digest(source/n) for n in gn};plan['graph_hashes']=current['files'];return plan
def run(a):
    source_record,g,baseline,signed,evidence_hashes=records(a);proof=controller_chain(a.control,source_record,g)
    evidence=a.evidence.parent.resolve()/a.evidence.name;need(a.workspace not in evidence.parents and evidence!=a.workspace,'Evidence must be external')
    after_gn=getattr(a,'audit_after_gn',False)
    previous=read(a.application_record) if after_gn else (read(evidence) if a.verify else None)
    if previous:
        need(previous.get('configuration')==NEXT and previous.get('applied') is True and previous.get('phase')=='SOURCE_APPLIED_GRAPH_UNCHANGED','No completed content application')
        need(previous['baseline_hashes']==evidence_hashes and previous['controller_proof']==proof,'Baseline/controller evidence changed')
    expected=previous['updated_provenance'] if previous else baseline
    s,out,data,before,after,selection_hash,mod=inputs(a,expected,'after' if previous else 'before')
    tools,signing=tools_and_config(a,s,source_record,g);plan=graph_plan(out,s,g,data,require_native_graph=not after_gn);outputs=state(out)
    if after_gn:
        need(not evidence.exists(),'Never overwrite post-GN evidence')
        need(previous['paths']==[str(a.workspace),str(s),str(out)] and previous['selection_hash']==selection_hash and previous['tools']==tools and previous['signing']==signing,'Application paths/selection/tools/config changed')
        need(previous['other_sources']==other_sources(s,list(data['before'])),'Other source changed after apply')
        for key in ['objects','jni','java','errorprone','immutable_jni_inputs_sha256','changing_jni_inputs','virtual_jni_dependencies','saved_errorprone_assignment','gn_inputs_sha256']:
            need(previous['graph_plan'].get(key)==plan.get(key),'Post-GN action/flags/dependencies changed; review required: '+key)
        need(a.gn_status.read_text().strip()=='0','Reviewed GN command did not report success')
        generated=[out/name for item in plan.get('gn_generator_edges',[]) for name in item['outputs']]
        generated=[f for f in generated if f.is_file()]
        need(generated and max(f.stat().st_mtime_ns for f in generated)>=max((s/n).stat().st_mtime_ns for n in data['before']),'No fresh GN output timestamp after source application; review required')
        delta=[]
        for n in set(previous['outputs'])|set(outputs):
            if previous['outputs'].get(n)!=outputs.get(n):
                need(n.endswith(('.ninja','.ninja.d')) or n=='build.ninja.stamp','Non-graph output changed during GN: '+n);delta.append(n)
        backup=evidence.with_suffix('.graphs');backup.mkdir()
        for n in set(plan['graph_hashes'])|{n for n in delta if n in outputs}:
            q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/n,q);need(digest(q)==outputs[n]['sha256'],'Graph moved while copying')
        plan['source_application_gn_requirement']=plan.get('gn_regeneration_decision');plan['gn_regeneration_decision']='COMPLETED_BY_RECORDED_MANUAL_GN_NOT_BY_HELPER'
        r={'configuration':NEXT,'phase':'GRAPH_AFTER_GN_AUDITED_NOT_COMPILED','application_record_sha256':digest(a.application_record),'baseline_hashes':evidence_hashes,'controller_proof':proof,'gn_log_sha256':digest(a.gn_log),'gn_status_sha256':digest(a.gn_status),'graph_delta':sorted(delta),'graph_plan':plan,'outputs':outputs,'updated_provenance':expected,'graph_backup':str(backup)}
        create(evidence,r);need(state(out)==outputs and records(a)[4]==evidence_hashes,'State/evidence moved during post-GN audit')
        print('Post-GN read-only audit complete; GN not invoked by helper, compilation not run');return
    if previous:
        need(previous['paths']==[str(a.workspace),str(s),str(out)] and previous['selection_hash']==selection_hash and previous['tools']==tools and previous['signing']==signing and previous['graph_plan']==plan,'Paths/selection/graph/tools/config changed')
        need(previous['outputs']==outputs and previous['other_sources']==other_sources(s,list(data['before'])),'Output/other source drift')
        need(records(a)[4]==evidence_hashes,'Baseline evidence moved during verification')
        print('Content applied verify PASS; no GN or compilation');return
    need(not evidence.exists(),'Never overwrite evidence');changed=reproduce(s,a.control,data);old={n:(s/n).read_bytes() for n in changed}
    r={'format':1,'configuration':NEXT,'applied':False,'phase':'INTENT','baseline_hashes':evidence_hashes,'baseline_provenance':baseline,'device_apk_extraction_verified':False,'certificate_basis':'user-confirmed signing record plus exact signed-file SHA256; no new signing or device extraction','controller_proof':proof,'selection_hash':selection_hash,'before_sha256':data['before'],'after_sha256':data['after'],'graph_plan':plan,'outputs':outputs,'other_sources':other_sources(s,list(changed)),'tools':tools,'signing':signing,'paths':[str(a.workspace),str(s),str(out)],'gn_executed':False,'compile_executed':False}
    if a.apply:
        for n in ['Runner.Worker','gn','ninja','siso','clang++']:need(subprocess.run(['pgrep','-x',n],stdout=subprocess.DEVNULL).returncode==1,'Builder active/process check failed: '+n)
        backup=evidence.with_suffix('.before');backup.mkdir()
        for name,path in [('source-applied.json',a.native_source_record),('graph-audited.json',a.build_evidence/'graph-audited.json'),('after-apk-provenance.json',a.build_evidence/'after-apk-provenance.json'),('signed-apk-record.json',a.build_evidence/'signed-apk-record.json')]:
            q=backup/'evidence'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,q)
        unsigned=s/'out/Default/apks/ChromePublic.apk';shutil.copy2(unsigned,backup/'Native-unsigned.apk')
        need(digest(backup/'Native-unsigned.apk')==UNSIGNED,'Native unsigned backup mismatch')
        for n in old:
            p=backup/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s/n,p);need(digest(p)==data['before'][n],'Source backup drift')
        for n in outputs:
            if n.endswith(('.ninja','.ninja.d')) or n in ['args.gn','build.ninja.stamp'] or any(x.startswith(('.ninja_','.siso')) for x in Path(n).parts):
                need('sha256' in outputs[n],'Aliased graph/state backup');p=backup/'output'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/n,p);need(digest(p)==outputs[n]['sha256'],'Graph/state backup drift')
        r['backup']=str(backup);create(evidence,r)
        for n,b in changed.items():
            need((s/n).read_bytes()==old[n],'Concurrent input drift: '+n)
            (s/n).write_bytes(b)
        require_files(s,after);updated=mod.record(a.workspace,s);x=dict(baseline);y=dict(updated);x.pop('tracked_source_diff_sha256');y.pop('tracked_source_diff_sha256');need(x==y,'Non-source provenance changed')
        need(state(out)==outputs and other_sources(s,list(changed))==r['other_sources'],'Output/other source moved; STOP, no rollback')
        need(tools_and_config(a,s,source_record,g)==(tools,signing) and graph_plan(out,s,g,data)==plan,'Tools/config/graph moved')
        need(records(a)[4]==evidence_hashes and controller_chain(a.control,source_record,g)==proof,'Baseline/controller moved during apply')
        r.update(applied=True,phase='SOURCE_APPLIED_GRAPH_UNCHANGED',updated_provenance=updated)
    else:
        create(evidence,r)
        need(all((s/n).read_bytes()==b for n,b in old.items()) and state(out)==outputs and other_sources(s,list(changed))==r['other_sources'],'Read-only source/output moved')
        need(records(a)[4]==evidence_hashes and controller_chain(a.control,source_record,g)==proof,'Baseline/controller moved during read-only check')
        r['phase']='READ_ONLY_COMPLETE'
    evidence.write_text(json.dumps(r,indent=2)+'\n');print(r['phase']+'; no GN/compiler/signing; installed-device APK not extracted')
    print('GN decision:',plan.get('gn_regeneration_decision','NOT_PROVEN'))
    print('NullAway gate:',plan.get('nullaway_gate','NOT_PROVEN'))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ['workspace','control','native-source-record','build-evidence','signed-apk','evidence']:parser.add_argument('--'+n,type=Path,required=True)
    group=parser.add_mutually_exclusive_group();group.add_argument('--apply',action='store_true');group.add_argument('--verify',action='store_true');group.add_argument('--audit-after-gn',action='store_true')
    for n in ['application-record','gn-log','gn-status']:parser.add_argument('--'+n,type=Path)
    a=parser.parse_args()
    if a.audit_after_gn and not all([a.application_record,a.gn_log,a.gn_status]):parser.error('--audit-after-gn requires --application-record, --gn-log, --gn-status')
    a.workspace=a.workspace.absolute();a.control=a.control.resolve();run(a)
