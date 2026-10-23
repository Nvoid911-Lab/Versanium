"""Validate and optionally apply ONLY Run9's three GURL accessor replacements.
Never compiles, cleans, resets, moves a tree, regenerates GN, or synchronizes dependencies.
Run from a separate reviewed controller; retain the original Run9 checkout and output.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,subprocess,zipfile,difflib,sys
sys.dont_write_bytecode=True

BASE='7d9102f4f0e35dec9f69425de44cd889836a88ac'
PIN='1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775'
VANADIUM='2ae4335402eabcc6e025f3400185fe25094d8521'
ARCHIVE_SHA='101cc6e2b6e0c18d1ca56993b16d9bd5176a02e3451b2ea065842937fdeda0b6'
GURL_SHA='64379fac91a7d4949e7b0c2da12e26952f36ed98dbbd5506fc4480bf8c3f88aa'
TARGET='content/browser/renderer_host/render_frame_host_impl.cc'

def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def require(ok,message):
    if not ok:raise RuntimeError(message)

def original_manifest(archive):
    require(sha(archive.read_bytes())==ARCHIVE_SHA,'Run9 provenance archive SHA256 mismatch; do not relax')
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith('build-provenance.json')]
        require(len(names)==1,'Expected exactly one original provenance JSON')
        require(z.getinfo(names[0]).file_size<1024*1024,'Unexpected provenance size')
        return json.loads(z.read(names[0]))

def replacement(text,original_patch):
    lines=original_patch.splitlines()
    start=next(i for i,l in enumerate(lines) if l.startswith('+bool RenderFrameHostImpl::IsVersaniumYoutubeScopeAllowed('))
    end=next(i for i in range(start,len(lines)) if lines[i]=='+}')
    old='\n'.join(l[1:] for l in lines[start:end+1])
    require(old.count('candidate_url.host_piece()')==3,'Original scope changed')
    require(text.count(old)==1,'Native file differs from exact original scope; stop')
    new=old.replace('candidate_url.host_piece()','candidate_url.host()')
    return text.replace(old,new,1)

def object_target(output):
    matches=[]
    for path in output.rglob('*.ninja'):
        for line in path.read_text(errors='strict').splitlines():
            m=re.match(r'^build ([^ :]+/render_frame_host_impl\.o): \S+ (.*)$',line)
            if m and TARGET in m[2]:matches.append(m[1])
    require(len(set(matches))==1,'Cannot uniquely identify failed RFH object from existing Ninja files')
    return matches[0]

def validate(workspace,control,baseline):
    require(workspace.name=='versanium-next-test-39951209951','Not the original Run9 directory')
    require(workspace.absolute()==workspace.resolve(),'Symlinked workspace refused')
    source=workspace/'chromium/src';out=source/'out/Default'
    require(source.resolve()==source and out.resolve()==out,'Source/output path alias refused')
    require(control!=workspace and workspace not in control.parents,'Use a separate controller checkout')
    require(git(workspace,'rev-parse','HEAD')==BASE,'Saved repository HEAD changed')
    require(not git(control,'status','--porcelain'),'Controller must be a clean reviewed checkout')
    subprocess.run(['git','-C',str(control),'merge-base','--is-ancestor',BASE,'HEAD'],check=True)
    allowed={'PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md','RULES.md',
      'tools/youtube_pip/execution_scope.patch','tools/youtube_pip/tests/check_execution_scope.py',
      'tools/youtube_pip/tests/check_source_integration.py','tools/versanium/prepare_run9.py'}
    for name in git(control,'diff','--name-only',BASE,'HEAD').splitlines():
        require(name in allowed or name.startswith(('docs/','tools/versanium/tests/test_run9')),
                'Unreviewed build input changed: '+name)
    require(baseline['repository_commit']==BASE and baseline['chromium_input']==PIN
            and baseline['vanadium_input']==VANADIUM and baseline['version']=='156.0.8078.47','Wrong baseline')
    # Import ORIGINAL recorder, not a changed controller recorder. No GN generation occurs.
    old=workspace/'tools/versanium/write_build_provenance.py'
    require(old.read_bytes()==subprocess.check_output(['git','-C',str(control),'show',BASE+':tools/versanium/write_build_provenance.py']), 'Original recorder changed')
    pin_validator=workspace/'tools/check_environment_zoom_revision.py'
    require(pin_validator.read_bytes()==subprocess.check_output(['git','-C',str(control),'show',BASE+':tools/check_environment_zoom_revision.py']), 'Original pin validator changed')
    os.environ['DEPOT_TOOLS_UPDATE']='0'
    os.environ['PATH']=str(workspace/'depot_tools')+os.pathsep+os.environ['PATH']
    require((source/'buildtools/linux64/gn').is_file(),'Preserved GN binary missing; do not bootstrap')
    spec=importlib.util.spec_from_file_location('original_run9_record',old)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    require(not git(workspace/'depot_tools','status','--porcelain','--untracked-files=no'),'Preserved depot_tools has tracked changes')
    actual=module.record(workspace,source)
    require(actual==baseline,'Original provenance differs (pins/GN/toolchain/depot/source/overlays); stop')
    require(file_sha(source/'third_party/llvm-build/Release+Asserts/bin/clang++')==baseline['inputs_sha256']['clang_binary'],'Actual clang++ does not match recorded clang toolchain')
    require(sha((source/'url/gurl.h').read_bytes())==GURL_SHA,'Real fixed GURL header changed')
    args=(out/'args.gn').read_text()
    require(re.search(r'^target_cpu\s*=\s*"arm64"',args,re.M) is not None,'Not arm64')
    require('chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,'Not isolated Test identity')
    for name in ['build.ninja','.ninja_log','.siso_deps']:
        require((out/name).is_file(),'Missing preserved incremental state: '+name)
    return source,out,actual

def prepare(workspace,control,archive,evidence,apply=False):
    evidence=evidence.parent.resolve()/evidence.name
    baseline=original_manifest(archive)
    source,out,actual=validate(workspace,control,baseline)
    require(not evidence.exists(),'Evidence path already exists; never overwrite it')
    require(workspace not in evidence.parents and evidence!=workspace,'Evidence must be outside preserved tree')
    path=source/TARGET;before=path.read_bytes()
    patch=subprocess.check_output(['git','-C',str(control),'show',BASE+':tools/youtube_pip/execution_scope.patch'],text=True)
    after=replacement(before.decode(),patch).encode()
    # Verify controller's build patch is exactly the three-token correction, no scope relaxation.
    require((control/'tools/youtube_pip/execution_scope.patch').read_text()==patch.replace('candidate_url.host_piece()','candidate_url.host()'), 'Controller patch exceeds three accessor corrections')
    obj=object_target(out)
    names={'args.gn','build.ninja','.ninja_log','.siso_deps'}
    names.update(str(p.relative_to(out)) for p in out.rglob('*.ninja'))
    names.update(name for name in ['.ninja_deps','.siso_log'] if (out/name).is_file())
    state={name:file_sha(out/name) for name in sorted(names)}
    result={'format':1,'run_id':39951209951,'artifact_id':12524821969,
      'baseline_archive_sha256':ARCHIVE_SHA,'original_repository_commit':BASE,
      'controller_commit':git(control,'rev-parse','HEAD'),'chromium_pin':PIN,
      'workspace':str(workspace),'source':str(source),'output':str(out),
      'original_provenance':actual,'original_native_sha256':sha(before),
      'corrected_native_sha256':sha(after),'gurl_header_sha256':GURL_SHA,
      'native_diff':''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile=TARGET,tofile=TARGET)),
      'original_incremental_state_sha256':state,'object_target':obj,
      'preserved_gn_binary_sha256':file_sha(source/'buildtools/linux64/gn'),
      'object_compile':'NOT RUN','applied':False}
    # Read-only preflight is the default. Explicit apply never runs a compiler.
    if apply:
        for name in ['Runner.Worker','clang++','ninja','siso']:
            status=subprocess.run(['pgrep','-x',name],stdout=subprocess.DEVNULL).returncode
            require(status==1,'Builder/runner process present, or pgrep unavailable: '+name)
        require(path.read_bytes()==before,'Native file changed during validation')
        # Keep an exact public-source backup OUTSIDE the saved checkout.
        backup=evidence.with_suffix('.native-before.cc')
        with backup.open('xb') as f:f.write(before)
        result['native_backup']=str(backup)
        # Record intent before the only source mutation; retain evidence on I/O failure.
        with evidence.open('x') as f:json.dump(result,f,indent=2)
        path.write_bytes(after)
        require(all(file_sha(out/name)==h for name,h in state.items()),'Incremental state changed concurrently; stop')
        require(sha(path.read_bytes())==sha(after),'Native write failed; stop')
        result['applied']=True
        result['corrected_tracked_source_diff_sha256']=sha(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--']))
        evidence.write_text(json.dumps(result,indent=2)+'\n')
    else:
        with evidence.open('x') as f:json.dump(result,f,indent=2)
    print('APPLIED limited source fix' if apply else 'READ-ONLY preflight PASS (no source mutation)')
    print('Object target from existing Ninja graph:',obj)
    print('Evidence:',evidence)

def verify_applied(workspace,control,archive,evidence):
    baseline=original_manifest(archive)
    recorded=json.loads(evidence.read_text())
    require(recorded.get('applied') is True,'Evidence does not confirm an applied correction')
    require(recorded['controller_commit']==git(control,'rev-parse','HEAD'),'Controller changed since apply')
    require(recorded['baseline_archive_sha256']==ARCHIVE_SHA,'Wrong baseline evidence')
    require(recorded['original_provenance']==baseline,'Original provenance link changed')
    expected=dict(baseline)
    expected['tracked_source_diff_sha256']=recorded['corrected_tracked_source_diff_sha256']
    source,out,_=validate(workspace,control,expected)
    require(str(source)==recorded['source'] and str(out)==recorded['output'],'Applied paths changed')
    require(file_sha(source/TARGET)==recorded['corrected_native_sha256'],'Native file changed since apply')
    require(file_sha(source/'buildtools/linux64/gn')==recorded['preserved_gn_binary_sha256'],'GN binary changed since apply')
    for name,digest in recorded['original_incremental_state_sha256'].items():
        require(file_sha(out/name)==digest,'Output state changed since apply: '+name)
    require(object_target(out)==recorded['object_target'],'Object graph changed since apply')
    print('Applied correction/source/toolchain/output recheck PASS; no compilation or writes')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--provenance-zip',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True)
    actions=p.add_mutually_exclusive_group()
    actions.add_argument('--apply',action='store_true')
    actions.add_argument('--verify-applied',action='store_true')
    a=p.parse_args()
    if a.verify_applied:
        verify_applied(a.workspace.absolute(),a.control.resolve(),a.provenance_zip.resolve(),a.evidence.absolute())
    else:
        prepare(a.workspace.absolute(),a.control.resolve(),a.provenance_zip.resolve(),a.evidence.absolute(),a.apply)
