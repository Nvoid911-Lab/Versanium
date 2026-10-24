"""Independent Forward→native preparation. Never invokes GN, compiler or old helpers."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True

PRODUCT='16eca84b6014b3f34cef4908c4072db3cfa7323b'
BASE='7d9102f4f0e35dec9f69425de44cd889836a88ac'
CHROMIUM='1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775'
VANADIUM='2ae4335402eabcc6e025f3400185fe25094d8521'
APK='0264aec79e1389a9165b639e0ce62a92f62818f6d3514b26c34f86017998bce1'
MANIFEST='docs/versanium/config-a-origin-forward-native-manifest.json'
TRANSFORM='tools/apply_fullscreen_native_origin.py'
BEFORE='AOriginForward';AFTER='AOriginForwardNative'

def require(ok,message):
    if not ok:raise RuntimeError(message)
def digest(b):return hashlib.sha256(b).hexdigest()
def file_hash(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def git(p,*args):return subprocess.check_output(['git','-C',str(p),*args])
def blob(c,rev,n):return git(c,'show',rev+':'+n)
def write_json(p,value):
    with p.open('x') as f:json.dump(value,f,indent=2)
def check_files(root,expected):
    for n,h in expected.items():
        p=root/n
        require(p.is_file() and not p.is_symlink() and p.resolve()==p,'Missing/aliased selected input: '+n)
        require(file_hash(p)==h,'Selected input mismatch: '+n)
def inventory(root):
    result={}
    for p in sorted(root.rglob('*')):
        n=str(p.relative_to(root))
        if p.is_symlink():result[n]={'link':os.readlink(p)}
        elif p.is_file():
            stat=p.stat();result[n]={'sha256':file_hash(p),'mode':stat.st_mode,'size':stat.st_size,'mtime_ns':stat.st_mtime_ns}
    for n in ['args.gn','build.ninja','.ninja_log','.siso_deps']:
        require(n in result and 'sha256' in result[n],'Missing preserved output state: '+n)
    return result
def graph_file(n):
    return n.endswith(('.ninja','.ninja.d')) or n in ['build.ninja.stamp']
def backup_file(n):
    return graph_file(n) or n=='args.gn' or n.startswith(('.ninja_','.siso')) or any(x.startswith('.siso') for x in Path(n).parts)
def selected(c):
    raw=blob(c,PRODUCT,MANIFEST)
    require((c/MANIFEST).read_bytes()==raw,'Native manifest changed')
    data=json.loads(raw);before=data['files'][BEFORE];after=data['files'][AFTER]
    old=json.loads(blob(c,PRODUCT,'docs/versanium/config-a-origin-forward-manifest.json'))['files'][BEFORE]
    require(len(old)==43 and len(before)==50 and len(after)==51,'Wrong input count')
    require(all(before[n]==h and after[n]==h for n,h in old.items()),'Forward43/B exclusion changed')
    changed=[n for n in before if before[n]!=after[n]]
    require(len(changed)==7 and set(after)-set(before)==set(data['absent_before']) and len(data['absent_before'])==1,'Wrong native selection shape')
    return data,changed,digest(raw)
def reproduce(s,c,data,changed):
    require((c/TRANSFORM).read_bytes()==blob(c,PRODUCT,TRANSFORM),'Native transform changed')
    with tempfile.TemporaryDirectory(prefix='native-source-reproduce-') as d:
        root=Path(d)
        for n in changed:
            p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git(s,'show','HEAD:'+n))
        check_files(root,{n:data['files'][BEFORE][n] for n in changed})
        spec=importlib.util.spec_from_file_location('pinned_native_product',c/TRANSFORM)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.apply(root)
        names=changed+data['absent_before']
        check_files(root,{n:data['files'][AFTER][n] for n in names})
        return {n:(root/n).read_bytes() for n in names}
def recorder(w,c,s):
    # Original build recorder, not any historical apply/preflight helper.
    for n in ['tools/versanium/write_build_provenance.py','tools/check_environment_zoom_revision.py']:
        require((w/n).read_bytes()==blob(c,BASE,n),'Original recorder/validator drift: '+n)
    require((s/'buildtools/linux64/gn').is_file(),'Missing saved GN; no bootstrap')
    require(not git(w/'depot_tools','status','--porcelain','--untracked-files=no').strip(),'Tracked depot_tools drift')
    os.environ['DEPOT_TOOLS_UPDATE']='0'
    os.environ['PATH']=str(s/'buildtools/linux64')+os.pathsep+str(w/'depot_tools')+os.pathsep+os.environ['PATH']
    sys.path.insert(0,str(w/'tools'))
    spec=importlib.util.spec_from_file_location('original_native_provenance',w/'tools/versanium/write_build_provenance.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
def nonselected_diff(s,names):
    return digest(git(s,'diff','HEAD','--','.',*[':(exclude)'+n for n in names]))
def baseline(a):
    prior=json.loads(a.forward_applied.read_text());p=json.loads(a.after_apk.read_text())
    require(prior.get('configuration')==BEFORE and prior.get('applied') is True,'Need completed built Forward, not A/AOrigin/installed')
    require(prior.get('updated_provenance')==p,'Forward applied/after-apk provenance mismatch')
    require(p.get('repository_commit')==BASE and p.get('chromium_input')==CHROMIUM and p.get('vanadium_input')==VANADIUM,'Wrong baseline pins')
    require(file_hash(a.forward_apk)==APK,'Forward distribution APK hash mismatch')
    return prior,p
def environment(a,mode,expected):
    w=a.workspace;c=a.control;s=w/'chromium/src';out=s/'out/Default'
    require(w.name=='versanium-next-test-39951209951' and all(p.resolve()==p for p in [w,s,out]),'Wrong/aliased saved paths')
    require(w!=c and w not in c.parents,'Use separate controller')
    require(git(w,'rev-parse','HEAD').decode().strip()==BASE,'Saved repository HEAD drift')
    require(not git(c,'status','--porcelain').strip(),'Dirty controller')
    subprocess.run(['git','-C',str(c),'merge-base','--is-ancestor',PRODUCT,'HEAD'],check=True)
    allowed={'PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md','tools/versanium/prepare_native_diagnostic.py','tools/versanium/audit_native_graph.py','tools/versanium/tests/test_native_preparation.py'}
    for n in git(c,'diff','--name-only',PRODUCT,'HEAD').decode().splitlines():
        require(n in allowed or n.startswith('docs/'),'Unexpected controller input: '+n)
    data,changed,mhash=selected(c)
    check_files(s,data['files'][mode])
    if mode==BEFORE:
        for n in data['absent_before']:require(not os.path.lexists(s/n),'New header already exists: '+n)
    mod=recorder(w,c,s);actual=mod.record(w,s)
    require(actual==expected,'Current source/GN args/toolchain provenance mismatch')
    args=(out/'args.gn').read_text()
    require('target_cpu = "arm64"' in args and 'chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,'Wrong Test identity/ABI')
    require('is_component_build = false' in args,'Unreviewed component build for TLS diagnostic')
    tools={n:file_hash(s/n) for n in ['buildtools/linux64/gn','third_party/llvm-build/Release+Asserts/bin/clang','third_party/llvm-build/Release+Asserts/bin/clang++']}
    require(tools['third_party/llvm-build/Release+Asserts/bin/clang++']==actual['inputs_sha256']['clang_binary'],'clang++ mismatch')
    # No keys/local.properties read. Pin only repository signing/config source.
    signing={}
    for n in ['common.sh','tools/configure_f11_identity.py']:
        require((w/n).read_bytes()==blob(c,BASE,n),'Signing/identity configuration drift: '+n)
        signing[n]=file_hash(w/n)
    return s,out,data,changed,mhash,mod,tools,signing
def same_provenance(old,new):
    a=dict(old);b=dict(new);a.pop('tracked_source_diff_sha256');b.pop('tracked_source_diff_sha256')
    require(a==b,'Non-source provenance changed')
def run(a):
    prior,p=baseline(a)
    evidence=a.evidence.parent.resolve()/a.evidence.name
    require(a.workspace not in evidence.parents and evidence!=a.workspace,'Evidence must be external')
    hashes={'forward_applied':file_hash(a.forward_applied),'after_apk':file_hash(a.after_apk),'forward_apk':file_hash(a.forward_apk)}
    if a.verify_source:
        r=json.loads(evidence.read_text())
        require(r.get('source_applied') is True and r.get('phase')=='SOURCE_ONLY_GRAPH_UNCHANGED','Need complete source-only record')
        require(r['controller']==git(a.control,'rev-parse','HEAD').decode().strip() and r['baseline']==p and r['baseline_hashes']==hashes,'Controller/baseline drift')
        s,out,data,names,mhash,mod,tools,signing=environment(a,AFTER,r['updated_provenance'])
        require(r['paths']==[str(a.workspace),str(s),str(out)] and r['manifest']==mhash and r['tools']==tools and r['signing']==signing,'Path/manifest/config/tool drift')
        require(nonselected_diff(s,r['changed'])==r['other_diff'] and inventory(out)==r['output'],'Other source/output drift')
        print('Native source-only verification PASS; GN/compile NOT RUN');return
    require(not evidence.exists(),'Never overwrite evidence')
    s,out,data,changed,mhash,mod,tools,signing=environment(a,BEFORE,p)
    require(prior.get('tools')==tools,'GN/clang tools differ from built Forward evidence')
    for n,h in prior.get('after_sha256',{}).items():
        require(n in data['files'][BEFORE] and data['files'][BEFORE][n]==h,'Forward applied file hash mismatch: '+n)
    require(len(prior.get('after_sha256',{}))==3,'Need Forward three-file applied hashes')
    new=reproduce(s,a.control,data,changed);state=inventory(out)
    old={n:(s/n).read_bytes() for n in changed}
    r={'format':1,'configuration':AFTER,'source_applied':False,'phase':'INTENT_ONLY','controller':git(a.control,'rev-parse','HEAD').decode().strip(),'product':PRODUCT,'paths':[str(a.workspace),str(s),str(out)],'baseline':p,'baseline_hashes':hashes,'manifest':mhash,'tools':tools,'signing':signing,'changed':list(new),'before_sha256':{n:digest(v) for n,v in old.items()},'absent_before':data['absent_before'],'after_sha256':{n:digest(v) for n,v in new.items()},'other_diff':nonselected_diff(s,list(new)),'output':state,'gn_command':[str(s/'buildtools/linux64/gn'),'gen','out/Default'],'gn_executed':False,'compile_executed':False}
    if a.apply_source:
        for name in ['Runner.Worker','clang++','ninja','siso','gn']:
            require(subprocess.run(['pgrep','-x',name],stdout=subprocess.DEVNULL).returncode==1,'Builder/process check failed: '+name)
        backup=evidence.with_suffix('.before');backup.mkdir()
        for n,b in old.items():
            q=backup/'source'/n;q.parent.mkdir(parents=True,exist_ok=True)
            with q.open('xb') as f:f.write(b)
            shutil.copystat(s/n,q)
        for n in state:
            if backup_file(n):
                require('sha256' in state[n],'Aliased graph/state backup: '+n)
                q=backup/'output'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/n,q)
                require(file_hash(q)==state[n]['sha256'],'Graph backup moved: '+n)
        r['backup']=str(backup);write_json(evidence,r)
        for n,b in new.items():
            if n in old:require((s/n).read_bytes()==old[n],'Concurrent source drift: '+n)
            else:require(not os.path.lexists(s/n),'New header unexpectedly exists')
            (s/n).parent.mkdir(parents=True,exist_ok=True)
            with (s/n).open('wb' if n in old else 'xb') as f:f.write(b)
        check_files(s,data['files'][AFTER]);updated=mod.record(a.workspace,s);same_provenance(p,updated)
        require(nonselected_diff(s,list(new))==r['other_diff'],'Other source changed')
        require(all(file_hash(s/n)==h for n,h in tools.items()) and all(file_hash(a.workspace/n)==h for n,h in signing.items()),'Tools/config changed')
        require(inventory(out)==state,'Output moved: STOP, no automatic rollback')
        r.update(source_applied=True,phase='SOURCE_ONLY_GRAPH_UNCHANGED',updated_provenance=updated)
        evidence.write_text(json.dumps(r,indent=2)+'\n')
        print('Native source-only apply PASS; graph/output unchanged; GN/compile NOT RUN')
    else:
        write_json(evidence,r)
        require(all((s/n).read_bytes()==b for n,b in old.items()) and all(not os.path.lexists(s/n) for n in data['absent_before']),'Read-only source moved')
        require(nonselected_diff(s,list(new))==r['other_diff'] and inventory(out)==state,'Read-only source/output moved')
        r['phase']='READ_ONLY_COMPLETE';evidence.write_text(json.dumps(r,indent=2)+'\n')
        print('Native read-only PASS; no source/output mutation, GN/compile NOT RUN')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ['workspace','control','forward-applied','after-apk','forward-apk','evidence']:parser.add_argument('--'+n,type=Path,required=True)
    flags=parser.add_mutually_exclusive_group();flags.add_argument('--apply-source',action='store_true');flags.add_argument('--verify-source',action='store_true')
    args=parser.parse_args();args.workspace=args.workspace.absolute();args.control=args.control.resolve();run(args)
