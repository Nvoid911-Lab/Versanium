"""A+Origin only; default read-only, explicit two-Java-file transaction, never build."""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys,tempfile
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_config_a as u  # Utilities only; old validation/apply conditions unchanged.
REVIEW='5faa9ad43438e1b696ed79f1ccff6effe4c2a3fb'
BASE_PATH='chrome/android/java/src/org/chromium/chrome/browser/fullscreen/FullscreenHtmlApiHandlerBase.java'
FILES=(u.JAVA,BASE_PATH)
MANIFEST='docs/versanium/config-a-origin-manifest.json'
def selection(control):
    a=json.loads(u.blob(control,REVIEW,u.MANIFEST))['files']['A']
    a[BASE_PATH]='f14c40e9046171345d2db39ba8c32c7317a3ebe5652cbf78e6f8e2d43e0c2926'
    after=dict(a)
    after[u.JAVA]='ad3efea4a6b741de0816240ac87c4f0784dd4b1fb77c396be9ad67f4822366b7'
    after[BASE_PATH]='ec1fcc104a40232af1fea47b59e0998571ec51c0c53bc91734d454394a9c3218'
    return {'format':1,'selection':REVIEW,'configuration':'ConfigAOrigin','files':{'A':a,'AOrigin':after}}
def reproduce(source,control,m):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        for name in FILES:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(u.git(source,'show','HEAD:'+name))
        original=(root/u.JAVA).read_bytes()
        subprocess.run(['git','apply','--include='+u.JAVA,'-'],cwd=root,input=u.blob(control,u.SELECTION,'tools/youtube_pip/diagnostics.patch'),check=True)
        u.hashes(root,{n:m['A'][n] for n in FILES})
        (root/u.JAVA).write_bytes(original)
        subprocess.run(['git','apply','--include='+u.JAVA,'-'],cwd=root,input=u.blob(control,REVIEW,'tools/youtube_pip/diagnostics.patch'),check=True)
        name='tools/apply_fullscreen_origin.py';script=control/name
        u.require(script.read_bytes()==u.blob(control,REVIEW,name),'Origin applicator changed')
        spec=importlib.util.spec_from_file_location('reviewed_origin_transform',script)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.apply(root)
        u.hashes(root,{n:m['AOrigin'][n] for n in FILES})
        return {n:(root/n).read_bytes() for n in FILES}
def others(source):
    return u.digest(u.git(source,'diff','HEAD','--','.',*[':(exclude)'+n for n in FILES]))
def validate(a,mode,expected):
    w=a.workspace;c=a.control;s=w/'chromium/src';out=s/'out/Default'
    u.require(w.name=='versanium-next-test-39951209951' and w.resolve()==w and s.resolve()==s and out.resolve()==out,'Wrong/aliased saved paths')
    u.require(w not in c.parents and w!=c,'Use separate controller')
    u.require(u.git(w,'rev-parse','HEAD').decode().strip()==u.BASE,'Saved repository HEAD changed')
    u.require(not u.git(c,'status','--porcelain').strip(),'Dirty controller')
    subprocess.run(['git','-C',str(c),'merge-base','--is-ancestor',REVIEW,'HEAD'],check=True)
    allowed={'PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md','tools/versanium/prepare_config_a_origin.py'}
    for n in u.git(c,'diff','--name-only',REVIEW,'HEAD').decode().splitlines():
        u.require(n in allowed or n.startswith(('docs/','tools/versanium/tests/test_config_a_origin')),'Unreviewed controller input: '+n)
    m=selection(c);u.require(json.loads((c/MANIFEST).read_text())==m,'Manifest differs from reviewed selection')
    u.require(len(m['files']['A'])==41 and {n for n in m['files']['A'] if m['files']['A'][n]!=m['files']['AOrigin'][n]}==set(FILES),'Wrong selection shape')
    u.hashes(s,m['files'][mode])
    mod=u.recorder(w,c,s);actual=mod.record(w,s)
    u.require(actual==expected,'Current source/GN/toolchain provenance mismatch')
    args=(out/'args.gn').read_text()
    u.require('target_cpu = "arm64"' in args and 'chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,'Wrong arm64/Test identity')
    u.require(u.file_hash(s/'third_party/llvm-build/Release+Asserts/bin/clang++')==actual['inputs_sha256']['clang_binary'],'clang++ mismatch')
    tools={n:u.file_hash(s/n) for n in ['buildtools/linux64/gn','third_party/llvm-build/Release+Asserts/bin/clang','third_party/llvm-build/Release+Asserts/bin/clang++']}
    return s,out,m['files'],mod,tools,u.file_hash(c/MANIFEST)
def run(a):
    baseline=json.loads(a.after_apk.read_text());prior=json.loads(a.a_applied.read_text())
    u.require(prior.get('configuration')=='A' and prior.get('applied') is True,'Need completed ConfigA record, not installed60b')
    u.require(prior.get('updated_provenance')==baseline,'A applied/after-apk mismatch')
    u.require(baseline.get('repository_commit')==u.BASE and baseline.get('chromium_input')== '1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775' and baseline.get('vanadium_input')=='2ae4335402eabcc6e025f3400185fe25094d8521','Wrong baseline pins')
    evidence=a.evidence.parent.resolve()/a.evidence.name
    u.require(a.workspace not in evidence.parents and evidence!=a.workspace,'Evidence must be external')
    if a.verify:
        r=json.loads(evidence.read_text());u.require(r.get('applied') is True and r.get('configuration')=='AOrigin' and r.get('compilation')=='NOT RUN','No completed uncompiled origin record')
        u.require(r['controller']==u.git(a.control,'rev-parse','HEAD').decode().strip(),'Controller changed')
        u.require(r['baseline']==baseline and r['a_applied_sha256']==u.file_hash(a.a_applied) and r['after_apk_sha256']==u.file_hash(a.after_apk),'Baseline evidence changed')
        s,out,m,mod,tools,mhash=validate(a,'AOrigin',r['updated_provenance'])
        u.require(r['paths']==[str(a.workspace),str(s),str(out)] and r['manifest_sha256']==mhash and r['tools']==tools,'Paths/manifest/tools drift')
        u.require(others(s)==r['other_diff'] and u.output_state(out)==r['output_state'],'Other source/output drift')
        print('AOrigin applied recheck PASS; no writes/compile');return
    u.require(not evidence.exists(),'Never overwrite evidence')
    s,out,m,mod,tools,mhash=validate(a,'A',baseline)
    u.require(u.file_hash(s/u.JAVA)==prior['after_sha256'],'Applied A Java hash mismatch')
    changed=reproduce(s,a.control,m);before={n:(s/n).read_bytes() for n in FILES};state=u.output_state(out)
    r={'format':1,'configuration':'AOrigin','applied':False,'compilation':'NOT RUN','controller':u.git(a.control,'rev-parse','HEAD').decode().strip(),'selection':REVIEW,'paths':[str(a.workspace),str(s),str(out)],'manifest_sha256':mhash,'baseline':baseline,'a_applied_sha256':u.file_hash(a.a_applied),'after_apk_sha256':u.file_hash(a.after_apk),'before_sha256':{n:u.digest(v) for n,v in before.items()},'after_sha256':{n:u.digest(v) for n,v in changed.items()},'tools':tools,'other_diff':others(s),'output_state':state}
    if a.apply:
        for process in ['Runner.Worker','clang++','ninja','siso']:
            u.require(subprocess.run(['pgrep','-x',process],stdout=subprocess.DEVNULL).returncode==1,'Builder active/process check failed: '+process)
        backup=evidence.with_suffix('.before');backup.mkdir()
        for n,v in before.items():
            p=backup/n;p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(v)
        r['backup']=str(backup)
        with evidence.open('x') as f:json.dump(r,f,indent=2)
        for n,v in changed.items():
            u.require((s/n).read_bytes()==before[n],'Concurrent source drift: '+n)
            (s/n).write_bytes(v)
        u.hashes(s,m['AOrigin']);updated=mod.record(a.workspace,s);u.same_inputs(baseline,updated)
        u.require(others(s)==r['other_diff'] and all(u.file_hash(s/n)==h for n,h in tools.items()),'Other inputs changed; STOP')
        u.require(u.output_state(out)==state,'Generated output changed; STOP; no automatic rollback')
        r['updated_provenance']=updated;r['applied']=True;evidence.write_text(json.dumps(r,indent=2)+'\n')
        print('AOrigin two-file apply PASS; no compile')
    else:
        with evidence.open('x') as f:json.dump(r,f,indent=2)
        u.require(all((s/n).read_bytes()==v for n,v in before.items()) and others(s)==r['other_diff'] and u.output_state(out)==state,'Read-only state moved')
        print('AOrigin read-only preflight PASS; no saved-source/output mutation')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['workspace','control','a-applied','after-apk','evidence']:p.add_argument('--'+name,type=Path,required=True)
    g=p.add_mutually_exclusive_group();g.add_argument('--apply',action='store_true');g.add_argument('--verify',action='store_true')
    a=p.parse_args();a.workspace=a.workspace.absolute();a.control=a.control.resolve();run(a)
