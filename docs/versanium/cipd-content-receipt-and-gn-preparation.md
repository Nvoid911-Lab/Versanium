# CIPD content receipt and verification GN preparation — 2026-10-26 JST

User report v2-5N3hJj confirms actual/expected depot4be4e4628e093c4ad50210db5dcfa05a88280bda,
tracked clean, three jar hashes match, central root workspace/chromium, and exact
DEPS package/subdir/current instances. Earlier metadata-location uncertainty is
resolved by that HOST report, not by a locally executed collector. Candidate58
apply/verify and Default invariance remain user-confirmed; no NullAway/output.

## Primary-source hash format

At LUCI494fe33d1585f712aedcd0e09b82e646d9c1d8ca:
- [common/iid.go](https://github.com/luci/luci-go/blob/494fe33d1585f712aedcd0e09b82e646d9c1d8ca/cipd/common/iid.go): ObjectRefToInstanceID/encode use raw URL Base64(digest followed by algorithm byte), except legacy SHA1 hex. Decoder uses final byte as algorithm.
- [caspb/cas.pb.go](https://github.com/luci/luci-go/blob/494fe33d1585f712aedcd0e09b82e646d9c1d8ca/cipd/api/cipd/v1/caspb/cas.pb.go): HashAlgo_SHA256=2.
- [pkg/manifest.go](https://github.com/luci/luci-go/blob/494fe33d1585f712aedcd0e09b82e646d9c1d8ca/cipd/client/cipd/pkg/manifest.go): FileInfo.Hash uses this format for extracted file content, not the entire package.

All3 supplied manifest hashes decode to33 bytes,32-byte reported SHA256 +02.
Local decoder checks PASS plus wrong-tag/truncated rejection. This does not
execute CIPD/Java or authenticate local records. Matching description/current/
manifest and jar bytes establishes LOCAL_RECORD_CONTENT_CONSISTENT, not independent
archive/service/signed attestation. Package instance is still a package digest,
not jar digest. No independent authenticity PASS is claimed or silently required
as an unattainable replacement for the scoped local consistency review.

## New external receipt: reread actual files, no bootstrap/network

Complete command below writes only NEW external receipt evidence. It rechecks
collected report/depot record, exact package/subdir/instance, metadata file hashes,
current links, manifest entry, actual jar size/hash and input stability. It does
not parse/print giant applied inventory; only streams its hash to bind the report.
Keep applying controller7b60873, prior records and collectors untouched. Run
original helper --verify first, per existing documentation, with builders idle.
The receipt is not a substitute for actual58-source/Default verification.

```sh
(
  set -eu
  CIPD_RECEIPT=$(mktemp -d /home/takuma/versanium/cipd-content-receipt-XXXXXX)
  printf 'Evidence: %s\n' "$CIPD_RECEIPT"
  cat > "$CIPD_RECEIPT/verify-content.py" <<'PY'
import base64,hashlib,json,os,re,subprocess
from pathlib import Path
w=Path('/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951')
root=w/'chromium';s=root/'src'
source=Path('/home/takuma/versanium/cipd-review-evidence-v2-5N3hJj/report.json')
applied=Path('/home/takuma/versanium/content-origin-evidence-TQNw0X/applied.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):
 if not p.is_file() or p.stat().st_size>16*1024*1024:raise ValueError('bounded metadata size/type')
 return json.loads(p.read_text(encoding='utf-8'))
def decode_sha256(value):
 if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{44}',value):raise ValueError('unsupported digest encoding')
 b=base64.b64decode(value,altchars=b'-_',validate=True)
 if len(b)!=33 or b[-1]!=2 or base64.urlsafe_b64encode(b).decode()!=value:raise ValueError('unsupported hash algorithm/canonical encoding')
 return b[:-1].hex()
expected={
 'error_prone':('error_prone_core.jar',16357860,'TP-iwhtizFRV0x62m6MtiWtm4Wh9cYsTCOTYQM0zIiYC','d4c5ac21642d596832ae11078fdf261d594d996acedd39354f6c947e16647691'),
 'error_prone_javac':('javac.jar',2843745,'7EcHxlEXEaLRWEyHIAxf0ouPjkmN1Od6jkutuo0sfBIC','165a749cf271381e271dc59069b59dcd5687dcc9427bd21b96aea71534555c56'),
 'nullaway':('nullaway.jar',6072785,'ds9Vm6LkQNc9O9nuG0_FbrsNQ5VoGPpFIWKur53l3wUC','7ab6bd9885590568bb1812f56fa1e9ecdd04cb8f4bb92c08e96e9f25db6dddb7')}
report_hash=sha(source);r=read(source)
pin='4be4e4628e093c4ad50210db5dcfa05a88280bda'
assert r['expected_depot_commit']==r['actual_depot_commit']==pin and r['depot_tracked_dirty'] is False
def depot_git(*args):return subprocess.check_output(['git','-C',str(w/'depot_tools'),*args],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),text=True).strip()
assert depot_git('rev-parse','HEAD')==pin and depot_git('status','--porcelain','--untracked-files=no')==''
assert r['applying_controller']=='7b608732d56f3885d5c950715d10709405695e70'
assert sha(applied)==r['applied_sha256']
rows=[row for rr in r['roots'] if rr['root']==str(root) for row in rr['matching_packages']]
verified=[]
for name,(filename,size,instance,reported_sha) in expected.items():
 package='chromium/third_party/android_build_tools/'+name
 subdir='src/third_party/android_build_tools/'+name+'/cipd'
 matches=[row for row in rows if row['package_name']==package]
 assert len(matches)==1,'missing/ambiguous package'
 row=matches[0];desc=Path(row['description_path'])
 assert desc.parent.parent==root/'.cipd/pkgs' and row['subdir']==subdir and row['current']==instance
 assert sha(desc)==row['description_sha256']
 d=read(desc);assert d['package_name']==package and d['subdir']==subdir
 assert (desc.parent/'_current').is_symlink() and os.readlink(desc.parent/'_current')==instance
 manifest=desc.parent/instance/'.cipdpkg/manifest.json'
 assert str(manifest)==row['manifest']['path'] and sha(manifest)==row['manifest']['sha256']
 md=read(manifest);assert md['package_name']==package
 files=[f for f in md['files'] if f['name']==filename];assert len(files)==1
 entry=files[0];recorded=[f for f in row['manifest']['jar_files'] if f['name']==filename];assert recorded==files
 jar=root/subdir/filename;st=jar.stat();actual=sha(jar)
 assert entry['size']==st.st_size==size and decode_sha256(entry['hash'])==actual==reported_sha
 assert r['jars'][name]['sha256']==actual and r['jars'][name]['size']==size
 assert sha(desc)==row['description_sha256'] and sha(manifest)==row['manifest']['sha256']
 assert (jar.stat().st_size,jar.stat().st_mtime_ns)==(st.st_size,st.st_mtime_ns)
 verified.append({'package':package,'subdir':subdir,'instance':instance,'size':size,'jar_sha256':actual,'manifest_file_hash':entry['hash'],'description_sha256':sha(desc),'manifest_sha256':sha(manifest)})
assert sha(source)==report_hash and sha(applied)==r['applied_sha256']
receipt={'result':'LOCAL_RECORD_CONTENT_CONSISTENT','independent_authenticity_proven':False,'collection_report_sha256':report_hash,'applied_sha256':r['applied_sha256'],'applying_controller':r['applying_controller'],'depot_commit':pin,'packages':verified,'nullaway_executed':False,'verification_output_created':False}
print(json.dumps(receipt,indent=2))
PY
  if PYTHONDONTWRITEBYTECODE=1 python3 "$CIPD_RECEIPT/verify-content.py" > "$CIPD_RECEIPT/receipt.json" 2> "$CIPD_RECEIPT/stderr.log"; then
    printf '0\n' > "$CIPD_RECEIPT/status"
    printf 'Local content receipt: %s/receipt.json\n' "$CIPD_RECEIPT"
  else
    CIPD_STATUS=$?
    printf '%s\n' "$CIPD_STATUS" > "$CIPD_RECEIPT/status"
    cat "$CIPD_RECEIPT/stderr.log"
    exit "$CIPD_STATUS"
  fi
)
```

## Future authorized sequence: isolated output through GN ONLY

NOT executed/authorized in this task. Review receipt before proceeding. First
retain original controller7b60873 and rerun original --verify with TQNw0X/applied.json;
no checkout/reapply. New review commits since7b60873 must remain Markdown-only,
ancestor proof and identical helper/product/selection (existing compatibility
command); never rewrite old controller fields. No source/output mutation allowed.

Physical backing-volume/C free226.6GiB limits growth, not virtual WSL815GiB;
RAM11GiB/swap32GiB are last reported observations. Refresh host free space/inodes,
backing VHD location, RAM and idle status. Full candidate58/provenance, processor
hashes and Default output inventory must be recorded before and after every stage.
Use original helper state(out) function for read-only full inventory if desired;
keep inventories externally and compare ALL entries/hash/mode/mtime/link, not
only args/build.ninja. Save args/tools/source hashes, include depot commit above.
Actual working set/extra capacity/time still UNMEASURED. No packages/sync/hooks.

After explicit approval, set CONTENT_SOURCE to existing saved chromium/src,
CONTENT_EVIDENCE to a NEW external evidence directory. These commands create
verification files only, never overwrite Default or copy its generated artifacts.
Exactly3 changed/added args: ErrorProne=true, static_analysis="on", warnings-as-errors=true.
All other saved args remain byte-preserved apart from those explicit line changes.
Do not print raw args. On unsupported expressions/duplicates stop, not append blindly.

```sh
# FUTURE ONLY. Set CONTENT_SOURCE and CONTENT_EVIDENCE explicitly first.
# Evidence is external to saved workspace; directory must be NEW.
export CONTENT_SOURCE CONTENT_EVIDENCE
python3 - <<'PY'
import hashlib,json,os,re
from pathlib import Path
s=Path(os.environ['CONTENT_SOURCE']).resolve()
e=Path(os.environ['CONTENT_EVIDENCE']).resolve()
assert not e.is_relative_to(s) and e.is_dir()
old=s/'out/Default/args.gn';raw=old.read_bytes();text=raw.decode('utf-8')
# Fail closed on conditional/imported/complex settings, never append overrides blindly.
assert not re.search(r'^\s*(import\s*\(|if\s*\(|declare_args\s*\(|[{}])',text,re.M)
values={'use_errorprone_java_compiler':'true','android_static_analysis':'"on"','treat_warnings_as_errors':'true'}
for key,value in values.items():
    pattern=r'(?m)^([ \t]*)'+key+r'[ \t]*=[ \t]*(true|false|"[^"\n]*")[ \t]*(#[^\n]*)?$'
    n=len(re.findall(pattern,text));assert n<=1,(key,'duplicate')
    assignments=re.findall(r'(?m)^\s*'+key+r'\s*=',text);assert len(assignments)==n,(key,'unsupported expression')
    if n:text=re.sub(pattern,lambda m:m[1]+key+' = '+value+(' '+m[3] if m[3] else ''),text)
    else:text+=('' if text.endswith('\n') else '\n')+key+' = '+value+'\n'
out=Path(__import__('tempfile').mkdtemp(prefix='NullAwayContent-415f6df-',dir=s/'out'))
(out/'args.gn').write_bytes(text.encode('utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
record={'purpose':'NULLAWAY_ONLY_NO_APK_NO_SIGNING','source':str(s),'output':str(out),'saved_args_sha256':sha(raw),'verification_args_sha256':sha((out/'args.gn').read_bytes()),'overrides':values}
with (e/'verification-config.json').open('x') as f:json.dump(record,f,indent=2)
assert old.read_bytes()==raw
print('Verification output:',out)
PY
```

Set/export CONTENT_VERIFY_OUT to the printed absolute new directory. Confirm it
is a fresh canonical child of the same src/out and is NOT Default; retain
verification-config.json and compare exact3 overrides privately. No APK identity/
signing/toolchain options may change. Before GN, save Default snapshot and compare
it to post-apply state; if processor/args/source drift STOP.

```sh
# FUTURE ONLY, separate authorization required.
export DEPOT_TOOLS_UPDATE=0
export PATH="$CONTENT_SOURCE/buildtools/linux64:$CONTENT_SOURCE/../../depot_tools:$PATH"
(
  cd "$CONTENT_SOURCE" || exit 1
  if (set -o noclobber; ./buildtools/linux64/gn gen "$CONTENT_VERIFY_OUT" > "$CONTENT_EVIDENCE/nullaway-gn.log" 2>&1); then
    printf '0\n' > "$CONTENT_EVIDENCE/nullaway-gn.status"
  else
    CONTENT_GN_STATUS=$?
    printf '%s\n' "$CONTENT_GN_STATUS" > "$CONTENT_EVIDENCE/nullaway-gn.status"
    exit "$CONTENT_GN_STATUS"
  fi
)
```

GN success is ONLY graph generation. Check source58/provenance/depot/processor
and entire saved Default inventories unchanged. Retain GN status/log, new args,
GN graph/source/tool hashes and full new-output inventory externally. Partial
failure: retain everything and stop, no cleanup/reset or implicit continuation.
Do not execute autoninja, build.sh, normal Java, analysis or APK targets yet.

Then use these READ-ONLY queries on the NEW output, save outputs externally:

```sh
# FUTURE, only after authorized isolated GN success.
cd "$CONTENT_SOURCE"
./buildtools/linux64/gn ls "$CONTENT_VERIFY_OUT" '//content/public/android:content_full_java__errorprone*'
./buildtools/linux64/gn ls "$CONTENT_VERIFY_OUT" '//chrome/android:chrome_java__errorprone*'
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" --format=json
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" deps --all
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" outputs
```

CONTENT_ANALYSIS_LABEL must come from actual query, never a guessed object.
STOP HERE for graph/dependency/resource review: exact default arm64 rules, JNI/
headers/srcjars/jars, actual NullAway processor flag + synchronous warnings-as-errors,
all family .sources/shard coverage, closures and projected resource use. See the
isolated-output plan's detailed audit criteria. Do not call GN flags discovery
NullAway success. No target execution until separate review of actual graph and
capacity. Verification outputs must never be packaged/signed or substituted into
Default. Original NOT_PROVEN gate remains factual; later real-source execution
receipt is separate from normal Java success.

## Validation boundary

Three supplied hashes +two negative decoder checks PASS; documented shell/Python
syntax and diff/actionlint checks only. No real host receipt, new output, GN,
capacity/time measurement, Java/NullAway/native compilation or signature performed.
Existing helpers/product/selection and original evidence unchanged. Local metadata
integrity cannot independently authenticate the entire acquisition chain.
