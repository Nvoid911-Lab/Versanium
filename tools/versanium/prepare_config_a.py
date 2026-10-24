"""Configuration A only: default read-only, explicit single-Java-file apply.
Never compiles, cleans, resets, synchronizes or regenerates GN. No B support.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,tempfile
sys.dont_write_bytecode=True
BASE='7d9102f4f0e35dec9f69425de44cd889836a88ac'
PRODUCT='60b00375def663584dfd5c6fd249d25498eeafb2'
SELECTION='257b37413ef119e249d9d903b8712af5ba919b7b'
REVIEW='b341e67902e3398cf0cc12b4b17b737d73d83c31'
JAVA='chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'
MANIFEST='docs/versanium/ab-selection-manifest.json'
def require(ok,message):
    if not ok:raise RuntimeError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def file_hash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def blob(root,rev,name):return git(root,'show',rev+':'+name)
def hashes(root,expected):
    for name,value in expected.items():
        path=root/name
        require(not path.is_symlink() and path.is_file(),'Missing/aliased selected source: '+name)
        require(file_hash(path)==value,'Configuration hash mismatch: '+name)
def output_state(root):
    # Full generated-output byte inventory, not only Ninja logs. Can be I/O heavy.
    result={}
    for path in sorted(root.rglob('*')):
        name=str(path.relative_to(root))
        if path.is_symlink():result[name]={'link':os.readlink(path)}
        elif path.is_file():result[name]={'sha256':file_hash(path),'mode':path.stat().st_mode}
    for name in ['args.gn','build.ninja','.ninja_log','.siso_deps']:
        require(name in result,'Missing output state: '+name)
    return result
def reproduce(source,control,manifest):
    # Reproduce from the saved fixed source HEAD, not from an observed-file edit.
    data=git(source,'show','HEAD:'+JAVA)
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);p=root/JAVA;p.parent.mkdir(parents=True);p.write_bytes(data)
        subprocess.run(['git','apply','--include='+JAVA,'-'],input=blob(control,PRODUCT,'tools/youtube_pip/diagnostics.patch'),cwd=root,check=True)
        require(file_hash(p)==manifest['installed'][JAVA],'Fixed-source installed reproduction mismatch')
        subprocess.run(['git','apply','-R','--include='+JAVA,'-'],input=blob(control,PRODUCT,'tools/youtube_pip/diagnostics.patch'),cwd=root,check=True)
        subprocess.run(['git','apply','--include='+JAVA,'-'],input=blob(control,SELECTION,'tools/youtube_pip/diagnostics.patch'),cwd=root,check=True)
        result=p.read_bytes()
    require(digest(result)==manifest['A'][JAVA],'Fixed-source A reproduction mismatch')
    return result
def recorder(workspace,control,source):
    old=workspace/'tools/versanium/write_build_provenance.py'
    for name in ['tools/versanium/write_build_provenance.py','tools/check_environment_zoom_revision.py']:
        require((workspace/name).read_bytes()==blob(control,BASE,name),'Original validator/recorder drift: '+name)
    require((source/'buildtools/linux64/gn').is_file(),'Missing preserved GN; no bootstrap')
    os.environ['DEPOT_TOOLS_UPDATE']='0'
    os.environ['PATH']=str(workspace/'depot_tools')+os.pathsep+os.environ['PATH']
    require(not git(workspace/'depot_tools','status','--porcelain','--untracked-files=no').strip(),'Tracked depot_tools changes')
    spec=importlib.util.spec_from_file_location('config_a_original_record',old)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
def validate(a,configuration,expected_provenance):
    w=a.workspace;c=a.control;s=w/'chromium/src';out=s/'out/Default'
    require(w.name=='versanium-next-test-39951209951' and w.resolve()==w,'Wrong or aliased workspace')
    require(s.resolve()==s and out.resolve()==out,'Aliased source/output')
    require(w not in c.parents and c!=w,'Use separate controller')
    require(git(w,'rev-parse','HEAD').decode().strip()==BASE,'Original repository HEAD changed')
    require(not git(c,'status','--porcelain').strip(),'Dirty controller')
    subprocess.run(['git','-C',str(c),'merge-base','--is-ancestor',REVIEW,'HEAD'],check=True)
    for name in git(c,'diff','--name-only',REVIEW,'HEAD').decode().splitlines():
        require(name in {'tools/versanium/prepare_config_a.py','PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md'} or name.startswith(('docs/','tools/versanium/tests/test_config_a')),'Unexpected controller change: '+name)
    raw=(c/MANIFEST).read_bytes()
    require(raw==blob(c,REVIEW,MANIFEST),'Manifest changed since reviewed 40/40 baseline')
    m=json.loads(raw)['files'];require(len(m['installed'])==40 and len(m['A'])==40,'Expected 40 files')
    require({n for n in m['A'] if m['A'][n]!=m['installed'][n]}=={JAVA},'A must change only controller Java')
    hashes(s,m[configuration])
    mod=recorder(w,c,s);actual=mod.record(w,s)
    require(actual==expected_provenance,'Current source/GN/toolchain/provenance mismatch')
    require(file_hash(s/'third_party/llvm-build/Release+Asserts/bin/clang++')==actual['inputs_sha256']['clang_binary'],'clang++ toolchain mismatch')
    args=(out/'args.gn').read_text()
    require('target_cpu = "arm64"' in args and 'chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,'Wrong arm64 Test identity')
    tools={}
    for name in ['buildtools/linux64/gn','third_party/llvm-build/Release+Asserts/bin/clang','third_party/llvm-build/Release+Asserts/bin/clang++']:
        tools[name]=file_hash(s/name)
    return s,out,m,mod,actual,tools,digest(raw)
def same_inputs(before,after):
    b=dict(before);n=dict(after);b.pop('tracked_source_diff_sha256');n.pop('tracked_source_diff_sha256')
    require(b==n,'Non-source provenance changed')
def other_diff(source):
    return digest(git(source,'diff','HEAD','--','.',':(exclude)'+JAVA))
def run(a):
    baseline=json.loads(a.after_apk.read_text());prior=json.loads(a.baseline_applied.read_text())
    require(prior.get('applied') is True and prior.get('target_controller')==PRODUCT,'Wrong diagnostic applied evidence')
    require(prior.get('post_update_provenance')==baseline,'Applied/after-APK provenance mismatch')
    require(baseline.get('repository_commit')==BASE and baseline.get('chromium_input')=='1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775' and baseline.get('vanadium_input')=='2ae4335402eabcc6e025f3400185fe25094d8521','Wrong baseline pins')
    path=a.evidence.parent.resolve()/a.evidence.name
    require(a.workspace not in path.parents and path!=a.workspace,'Evidence must be external')
    if a.verify:
        r=json.loads(path.read_text());require(r.get('applied') is True,'No completed A apply record')
        require(r['controller']==git(a.control,'rev-parse','HEAD').decode().strip(),'Controller changed')
        require(r['baseline']==baseline,'Baseline chain changed')
        require(r['baseline_applied_sha256']==file_hash(a.baseline_applied) and r['after_apk_sha256']==file_hash(a.after_apk),'Evidence inputs changed')
        s,out,m,mod,actual,tools,mhash=validate(a,'A',r['updated_provenance'])
        require(r['paths']==[str(a.workspace),str(s),str(out)] and r['manifest_sha256']==mhash,'Paths/manifest changed')
        require(r['tools']==tools and r['output_state']==output_state(out),'Toolchain/generated output changed')
        require(r['other_tracked_diff']==other_diff(s),'Other tracked source changed')
        print('A applied recheck PASS; no writes or compilation');return
    require(not path.exists(),'Never overwrite evidence')
    s,out,m,mod,actual,tools,mhash=validate(a,'installed',baseline)
    for name,value in prior['post_update_source_sha256'].items():require(file_hash(s/name)==value,'Prior four-file applied hash mismatch: '+name)
    changed=reproduce(s,a.control,m);before=(s/JAVA).read_bytes();state=output_state(out)
    r={'format':1,'configuration':'A','applied':False,'controller':git(a.control,'rev-parse','HEAD').decode().strip(),'paths':[str(a.workspace),str(s),str(out)],'manifest_sha256':mhash,'baseline':baseline,'baseline_applied_sha256':file_hash(a.baseline_applied),'after_apk_sha256':file_hash(a.after_apk),'before_sha256':digest(before),'after_sha256':digest(changed),'tools':tools,'output_state':state,'compilation':'NOT RUN'}
    r['other_tracked_diff']=other_diff(s)
    if a.apply:
        for process in ['Runner.Worker','clang++','ninja','siso']:
            require(subprocess.run(['pgrep','-x',process],stdout=subprocess.DEVNULL).returncode==1,'Builder active or process check failed: '+process)
        backup=path.with_suffix('.before.java')
        with backup.open('xb') as f:f.write(before)
        r['backup']=str(backup)
        with path.open('x') as f:json.dump(r,f,indent=2)
        require((s/JAVA).read_bytes()==before,'Source changed before write')
        (s/JAVA).write_bytes(changed)
        hashes(s,m['A'])
        updated=mod.record(a.workspace,s);same_inputs(baseline,updated)
        require(other_diff(s)==r['other_tracked_diff'],'Other tracked source changed; STOP')
        require(all(file_hash(s/name)==value for name,value in tools.items()),'Tool binary changed; STOP')
        # Whole tracked-source diff must be exactly the old diff plus this one-file change.
        # Other selected inputs and ALL generated output bytes are checked again.
        require(output_state(out)==state,'Generated output changed; STOP with intent/backup retained')
        r['updated_provenance']=updated;r['applied']=True
        path.write_text(json.dumps(r,indent=2)+'\n')
        print('A one-file apply PASS; no build')
    else:
        with path.open('x') as f:json.dump(r,f,indent=2)
        require((s/JAVA).read_bytes()==before and output_state(out)==state and other_diff(s)==r['other_tracked_diff'],'Read-only state moved')
        print('A read-only preflight PASS; no saved source/output mutation')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['workspace','control','baseline-applied','after-apk','evidence']:p.add_argument('--'+name,type=Path,required=True)
    group=p.add_mutually_exclusive_group();group.add_argument('--apply',action='store_true');group.add_argument('--verify',action='store_true')
    a=p.parse_args();a.workspace=a.workspace.absolute();a.control=a.control.resolve();run(a)
