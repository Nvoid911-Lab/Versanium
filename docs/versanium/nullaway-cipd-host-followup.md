# Applied candidate / CIPD provenance follow-up — 2026-10-26 JST

Preparation69241df; actual applying controller remains7b60873. This is research/
preparation only. No host command, output creation, GN, build or package acquisition
was run by Codex. Existing product/helpers/selections/receipts are unchanged.

## User-confirmed state

- content58-after / changed10 source-only apply and verify PASS under7b60873.
  Record: `/home/takuma/versanium/content-origin-evidence-TQNw0X/applied.json`.
- Default graph/generated outputs unchanged; verification output absent; GN and
  compilation not run. The original read-only receipt remains alongside apply.
- Windows C free226.6GiB; WSL virtual filesystem free815GiB; RAM available11GiB,
  swap32GiB. These are user-reported observations, not locally measured. C free
  space limits future VHD growth; WSL815GiB is NOT physical host capacity.
- Actual reported jars under src/third_party/android_build_tools:

|File|Reported SHA256|
|---|---|
|error_prone/cipd/error_prone_core.jar|d4c5ac21642d596832ae11078fdf261d594d996acedd39354f6c947e16647691|
|error_prone_javac/cipd/javac.jar|165a749cf271381e271dc59069b59dcd5687dcc9427bd21b96aea71534555c56|
|nullaway/cipd/nullaway.jar|7ab6bd9885590568bb1812f56fa1e9ecdd04cb8f4bb92c08e96e9f25db6dddb7|

No .cipd or *.manifest was found in the previously tested source/package paths.
That alone proves neither a corrupt jar nor a wrong CIPD instance.

## Acquisition path and evidence limits

Fixed Chromium1d17 DEPS installs the three pinned CIPD packages into the named
`src/third_party/android_build_tools/*/cipd` subdirs when checkout_android and
non_git_source are true. Immutable instance IDs are in the isolated-output plan.
Versanium's pinned build.sh invokes gclient sync after Vanadium patches; it copies
.gclient to chromium/.gclient. That is why the gclient client root can be the
parent of src, NOT necessarily src or each package's directory.

The exact saved depot_tools revision is recorded in applied.json.updated_provenance
and must be verified against actual depot_tools HEAD/files. It was not supplied
here. Official depot_tools Gitiles returned HTTP403 in this research environment.
For layout research ONLY, inspected GitHub mirror angelobreuer/depot_tools at
5786e1ee10664e011c9b65e438e584468524441f (2024 mirror, NOT asserted to equal host):
GClient.GetCipdRoot uses self.root_dir; CipdRoot.ensure uses that root with @Subdir
entries. Its ensure file is temporary and removed in finally; lack of a retained
.ensure file is expected in that implementation. Actual saved source excerpts
must confirm this before making claims about the host's acquisition behavior.
No mirror tool is executed, installed or substituted for the saved toolchain.

For format research ONLY, inspected LUCI client source via GitHub luci/luci-go:
`cipd/client/cipd/deployer/deployer.go`, `pkg/manifest.go`; research revision
494fe33d1585f712aedcd0e09b82e646d9c1d8ca (NOT proven host client revision).
The documented client layout is root/.cipd/pkgs/<arbitrary index>/description.json
(package_name/subdir), _current symlink (Linux) or _current.txt (Windows), then
<instance>/.cipdpkg/manifest.json. Copy mode keeps jar payload at package subdir
and metadata centrally; symlink mode keeps payload beneath the instance directory.
There need not be a *.manifest file or package-local .cipd. Manifest version_file,
if requested by that package, is another record, not guaranteed to exist.
The batch below enumerates bounded related roots and indexed descriptions once;
it does not guess numbered paths or search the whole home/drive/cache.

|Evidence|Can establish|Cannot establish by itself|
|---|---|---|
|Actual SHA256 matching reported value|Same bytes as this user's reported jar|CIPD instance→jar binding; these are not independently trusted reference hashes|
|Embedded MANIFEST.MF/pom.properties version|Self-declared version/build identity|CIPD package instance; repacks can contain same version or different byte metadata|
|DEPS fixed package/instance|Requested immutable dependency pin|Successful install or unchanged current files|
|gclient entries/ensure/log references|Configured/requested package/version, possibly successful command if retained|Current payload integrity; temporary ensure file may be gone|
|Matching local description + current instance + deployment manifest|Recorded deployment of package/instance/subdir; file map if retained|Untampered current jars without file-content verification; local records are mutable|
|Manifest file digest with verified algorithm checked against current jar|Current file matches recorded deployment content|Independent authenticity if all local metadata is untrusted|
|Existing original CIPD archive whose digest is verified as pinned instance, plus extracted member comparison|Strong offline package→current jar linkage|Nothing if archive/algorithm/origin is not actually validated|

CIPD instance ID is an encoded digest of the PACKAGE, not hex SHA256 of one jar.
Do not compare these strings or infer equality from Maven version. Manifest file
hashes can use CIPD's algorithm+digest encoding; do not silently treat them as hex.
If records are absent/removed in this checkout, report **instance binding unproven**,
not mismatch. Alternatives without acquisition: a retained local original package
archive verified with the reviewed CIPD digest algorithm, or an independently
trusted prior receipt mapping exact package+instance+member to SHA256. Existing
jar hash/version alone is insufficient. No describe/resolve/ensure/sync or package
download is proposed now. If no binding is possible, stop the provenance gate for
review; do not turn absence into automatic permission or declare a mismatch.

## One bounded read-only host collection (no tool bootstrap/network)

This prints only selected metadata; no .gclient execution, shell history, env,
user URLs/tokens, credential stores, arbitrary logs or complete jar contents. It reads
jar metadata but never loads Java classes. It can be saved to a NEW external
receipt by the user; never overwrite old applied/signature evidence. Unknown
schema/permissions are reported, not coerced into PASS. Before running, ensure
no builder/runner is modifying the workspace. This command was syntax-checked
here, not run against the host.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import ast,hashlib,json,os,re,subprocess,zipfile
from pathlib import Path
w=Path('/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951')
s=w/'chromium/src';depot=w/'depot_tools'
a=Path('/home/takuma/versanium/content-origin-evidence-TQNw0X/applied.json')
expected={
 'error_prone':('error_prone_core.jar','d4c5ac21642d596832ae11078fdf261d594d996acedd39354f6c947e16647691'),
 'error_prone_javac':('javac.jar','165a749cf271381e271dc59069b59dcd5687dcc9427bd21b96aea71534555c56'),
 'nullaway':('nullaway.jar','7ab6bd9885590568bb1812f56fa1e9ecdd04cb8f4bb92c08e96e9f25db6dddb7')}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def small(p,limit=1024*1024):
 if p.stat().st_size>limit:raise ValueError('metadata too large: '+str(p))
 return p.read_bytes()
def git(*args):return subprocess.check_output(['git','-C',str(depot),*args],env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'),text=True).strip()
record=json.loads(small(a));prov=record['updated_provenance']
report={'applied_sha256':sha(a),'applying_controller':record['controller_proof']['preparation_controller'],
 'expected_depot_commit':prov['depot_tools_commit'],'actual_depot_commit':git('rev-parse','HEAD'),
 'depot_tracked_dirty':bool(git('status','--porcelain','--untracked-files=no')),'tool_excerpts':{},'jars':{},'roots':[]}
report['cipd_tool_files']=[{'name':p.name,'sha256':sha(p),'size':p.stat().st_size} for p in depot.iterdir() if p.is_file() and (p.name.startswith('cipd') or p.name.startswith('.cipd'))]
report['actual_deps_packages']={}
deps=ast.parse(small(s/'DEPS',4*1024*1024).decode('utf-8'))
for node in ast.walk(deps):
 if isinstance(node,ast.Dict):
  for key,value in zip(node.keys,node.values):
   if isinstance(key,ast.Constant) and key.value in {'src/third_party/android_build_tools/'+n+'/cipd' for n in expected}:
    report['actual_deps_packages'][key.value]=ast.literal_eval(value)
for filename,classes in [('gclient.py',{'GClient'}),('gclient_scm.py',{'CipdRoot'})]:
 p=depot/filename;raw=small(p,4*1024*1024).decode('utf-8');tree=ast.parse(raw);segments=[]
 for cls in tree.body:
  if isinstance(cls,ast.ClassDef) and cls.name in classes:
   for fn in cls.body:
    if isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)) and fn.name in {'GetCipdRoot','_create_ensure_file','ensure','clobber'}:
     segments.append({'class':cls.name,'method':fn.name,'line':fn.lineno,'source':ast.get_source_segment(raw,fn).splitlines()[:90]})
 report['tool_excerpts'][filename]={'sha256':sha(p),'functions':segments}
for name,(jarname,wanted) in expected.items():
 p=s/'third_party/android_build_tools'/name/'cipd'/jarname
 item={'path':str(p),'exists':p.is_file(),'reported_sha256':wanted}
 if p.is_file():
  item.update(sha256=sha(p),size=p.stat().st_size,symlink=p.is_symlink(),resolved_path=str(p.resolve()))
  item['matches_user_report']=item['sha256']==wanted;metadata=[]
  with zipfile.ZipFile(p) as z:
   for entry in z.infolist():
    n=entry.filename
    wanted_pom=any(n=='META-INF/maven/'+g+'/'+artifact+'/pom.properties' for g,artifact in [('com.google.errorprone','error_prone_core'),('com.google.errorprone','javac'),('com.uber.nullaway','nullaway')])
    if n=='META-INF/MANIFEST.MF' or wanted_pom:
     if entry.file_size>65536:raise ValueError('oversized embedded metadata')
     text=z.read(entry).decode('utf-8');fields={}
     for line in text.splitlines():
      m=re.fullmatch(r'(Implementation-Version|Specification-Version|Bundle-Version|Automatic-Module-Name|groupId|artifactId|version)\s*[:=]\s*(.*)',line)
      if m:fields[m[1]]=m[2]
     metadata.append({'entry':n,'fields':fields})
  item['embedded_versions']=metadata
 report['jars'][name]=item
# Bounded ancestors + the three known package/subdirs; no recursive home scan.
roots=[w,w/'chromium',s]
for name in expected:roots.extend([s/'third_party/android_build_tools'/name,s/'third_party/android_build_tools'/name/'cipd'])
packages={'chromium/third_party/android_build_tools/'+n for n in expected}
for root in roots:
 item={'root':str(root),'gclient_files':[],'cipd_exists':(root/'.cipd').is_dir(),'matching_packages':[]}
 if root.is_dir():
  for p in root.iterdir():
   if p.name in {'.gclient','.gclient_entries','.gclient_entries.old','.gclient_previous_sync_commits'} and p.is_file():
    entry={'name':p.name,'sha256':sha(p),'size':p.stat().st_size}
    if p.name in {'.gclient_entries','.gclient_entries.old'}:
     tree=ast.parse(small(p,4*1024*1024).decode('utf-8'));matches=[]
     for node in tree.body:
      if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='entries' for x in node.targets):
       entries=ast.literal_eval(node.value)
       for key,value in entries.items():
        for package in packages:
         if isinstance(key,str) and key.endswith(':'+package) and isinstance(value,str):
          version=re.search(re.escape(package)+r'@([A-Za-z0-9_-]{40,128})$',value)
          matches.append({'package_name':package,'entry_key':key,'version':version[1] if version else 'UNRECOGNIZED_VALUE_NOT_PRINTED'})
     entry['selected_package_entries']=matches
    item['gclient_files'].append(entry)
 pkgs=root/'.cipd/pkgs'
 if pkgs.is_dir():
  children=list(pkgs.iterdir())
  if len(children)>20000:raise ValueError('too many package records; narrow review required')
  for child in children:
   desc=child/'description.json'
   if not desc.is_file():continue
   data=json.loads(small(desc))
   if data.get('package_name') not in packages:continue
   row={'description_path':str(desc),'description_sha256':sha(desc),'package_name':data.get('package_name'),'subdir':data.get('subdir'),'current':None}
   current=child/'_current';txt=child/'_current.txt'
   if current.is_symlink():row['current']=os.readlink(current)
   elif txt.is_file():row['current']=small(txt,512).decode('utf-8').strip()
   instance=row['current']
   if instance and re.fullmatch(r'[A-Za-z0-9_-]{40,128}',instance):
    manifest=child/instance/'.cipdpkg/manifest.json'
    if manifest.is_file():
     md=json.loads(small(manifest,4*1024*1024))
     row['manifest']={'path':str(manifest),'sha256':sha(manifest),'format_version':md.get('format_version'),'package_name':md.get('package_name'),'install_mode':md.get('install_mode'),'actual_install_mode':md.get('actual_install_mode'),'version_file':md.get('version_file'),'jar_files':[f for f in md.get('files',[]) if f.get('name') in {v[0] for v in expected.values()}]}
   item['matching_packages'].append(row)
 report['roots'].append(item)
print(json.dumps(report,indent=2))
PY
```

Do not share raw acquisition logs. If an already-known bounded acquisition log
exists, extract only these three exact package names/instances and command
status, with timestamps and file hash; no general recursive grep of the workspace.
The batch hashes gclient records and extracts ONLY exact package keys/versions
from a literal entries assignment. Treat unsupported AST/schema as unresolved;
never execute .gclient or .gclient_entries as Python. Entries are configured
checkout records, not a replacement for current payload verification.
A missing function/unknown client storage layout remains unresolved, not an excuse
to keep guessing paths. The saved actual tool source is the next decisive evidence.

## Controller compatibility and future isolated-output sequence

Keep the actual applying controller checkout7b60873 for the existing helper's
`--verify` and applied.json. Do not checkout the new documentation commit there
and silently accept a controller mismatch: that helper binds exact controller
proof/diff hashes. Never edit applied.json. The source record's updated_provenance,
58 after hashes and complete Default output snapshot are still the apply baseline.

New review revisions since7b60873 must be proved ancestor descendants with ONLY
Markdown under docs plus PROJECT_STATUS.md/ARCHITECTURE.md/DECISIONS.md changes;
product, selection, graph scanner, preparation helper and tests must be byte-
identical to7b60873. Fetching review history in the separate controller is allowed
only to inspect commits; leave HEAD7b60873 while re-verifying the original receipt.
Store a NEW external compatibility receipt containing both SHAs, exact changed
paths/diff digest and invariant-file hashes. Do not rewrite old controller fields.
If any non-document code delta exists, STOP; this docs-only proof no longer applies.

Future order after fresh source-only verify (NO reapply), jar/instance provenance
review and new approval:

1. Recheck Windows physical drive and WSL free disk/inodes, RAM/swap and idle
   runner. Identify actual VHD backing volume before applying C's226.6GiB bound;
   do not assume815GiB is available physical growth. Preserve space for Windows,
   saved Default/APKs/backups and swap/pagefile needs. No numeric safe threshold
   or peak storage estimate has yet been measured. Do not count swap as fast RAM.
2. Record tool/processor hashes above, candidate58-after/updated_provenance,
   source diff and Default inventory. Resolve missing CIPD binding as described;
   do not mask it with observed-hash allowlisting. Old Default args stay unchanged.
3. Only with approval, use the isolated-output plan's future setup example to
   create a fresh NullAwayContent output. Exactly3 argument overrides: ErrorProne
   true, static_analysis="on", warnings-as-errors true. All other args unchanged;
   no copying generated products/history, no APK/signing use of this output.
4. Separate approval/gate for verification GN: saved GN/depot, only NEW output;
   record graph, config, tools/source/default invariance. Stop on source writes,
   Default changes, missing tools requiring downloads or unreviewed commands.
5. Before analysis, inspect actual compile/analysis rules, default arm64, JNI/
   generated Java/header/jar/processor dependency closures and all .sources/shards.
   Use actual graph targets only, no guessed names. Exact NullAway processor flags,
   synchronous mode, warnings-as-errors and coverage are required, not flag toggle
   alone. Measure graph size and planned dependency actions; obtain reviewed
   capacity/working-set estimates before executing producers. No estimate yet.
6. Keep separate source/provenance/config/graph/analysis receipt. Only successful
   actual real-source analysis can satisfy separate NullAway review. Existing
   Default/helper NOT_PROVEN record remains factual and unchanged. Product Java/
   native/APK integration later uses Default, never verification jars or outputs.

This task only prepares these gates. GN graph completion in the earlier TQNw0X
receipt concerns saved Default, not a future verification graph. No new output,
analysis target/capacity measurement, successful NullAway or APK claim is made.

### Future read-only controller proof and existing apply verification

REVIEW_SHA must be the final reviewed docs-only commit reported with this PR.
Fetch is controller history only, not dependency synchronization; no checkout.
Run only while saved source/output are idle. No apply or output generation occurs.

```sh
(
  set -eu
  CONTENT_CONTROL=/home/takuma/versanium/run9-control-093f787-3k3yO1
  test -z "$(git -C "$CONTENT_CONTROL" status --porcelain)"
  test "$(git -C "$CONTENT_CONTROL" rev-parse HEAD)" = 7b608732d56f3885d5c950715d10709405695e70
  git -C "$CONTENT_CONTROL" fetch --no-tags https://github.com/Nvoid911-Lab/Versanium.git next-test/156-zoom-transfer-pip
  export CONTENT_CONTROL CONTENT_REVIEW_SHA=REVIEW_SHA
  python3 - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
c=Path(os.environ['CONTENT_CONTROL']);new=os.environ['CONTENT_REVIEW_SHA'];old='7b608732d56f3885d5c950715d10709405695e70'
def git(*args):return subprocess.check_output(['git','-C',str(c),*args])
subprocess.run(['git','-C',str(c),'merge-base','--is-ancestor',old,new],check=True)
paths=git('diff','--no-renames','--name-only',old,new).decode().splitlines()
assert all(p in {'PROJECT_STATUS.md','ARCHITECTURE.md','DECISIONS.md'} or (p.startswith('docs/') and p.endswith('.md')) for p in paths),paths
invariants=['tools/versanium/prepare_content_diagnostic.py','tools/versanium/content_diagnostic_graph.py','docs/versanium/content-fullscreen-diagnostic-selection.json','tools/apply_content_fullscreen_origin.py']
sha=lambda b:hashlib.sha256(b).hexdigest();hashes={}
for p in invariants:
 before=git('show',old+':'+p);after=git('show',new+':'+p)
 assert before==after==(c/p).read_bytes(),p
 hashes[p]=sha(before)
print(json.dumps({'applying_controller':old,'review_controller':new,'changed_paths':paths,'diff_sha256':sha(git('diff','--binary',old,new)),'invariants':hashes},indent=2))
PY
  PYTHONDONTWRITEBYTECODE=1 python3 "$CONTENT_CONTROL/tools/versanium/prepare_content_diagnostic.py" \
    --workspace /home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951 \
    --control "$CONTENT_CONTROL" \
    --native-source-record /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/source-applied.json \
    --build-evidence /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/graph-reaudit-ZFshuZ \
    --signed-apk /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/signed-test/Versanium-156.0.8078.47_Test_ConfigAOriginForwardNative.apk \
    --evidence /home/takuma/versanium/content-origin-evidence-TQNw0X/applied.json \
    --verify
)
```

Keep controller7b60873: the new preparation is documentation, not a new applying
controller. Do not replace `--verify` by `--apply`, do not change receipt paths to
make another baseline pass. If Default or candidate drifted, stop and retain
proof; no rollback or record editing. Save stdout to a NEW external file if needed.

## Research links and local checks

- [Fixed156 DEPS](https://github.com/chromium/chromium/blob/1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775/DEPS)
- [Layout research mirror gclient.py](https://github.com/angelobreuer/depot_tools/blob/5786e1ee10664e011c9b65e438e584468524441f/gclient.py)
- [Layout research mirror gclient_scm.py](https://github.com/angelobreuer/depot_tools/blob/5786e1ee10664e011c9b65e438e584468524441f/gclient_scm.py)
- [LUCI deployment format](https://github.com/luci/luci-go/blob/494fe33d1585f712aedcd0e09b82e646d9c1d8ca/cipd/client/cipd/deployer/deployer.go)
- [LUCI manifest format](https://github.com/luci/luci-go/blob/494fe33d1585f712aedcd0e09b82e646d9c1d8ca/cipd/client/cipd/pkg/manifest.go)

Documented Bash/embedded Python syntax, actionlint and git diff --check PASS.
Product/helper/selection invariant diff from7b60873 is empty. No new runtime test
or host collection was executed; prior95 tests are historical, not a newly run
NullAway check. Official depot_tools HTTP403 and unknown host client revision
limit the layout conclusion until the batch verifies actual saved tools. Only
small public source files were read for research; no dependency package/archive
was obtained. No claim that embedded jar versions or local deployment metadata
were actually received yet; only the three reported jar hashes are confirmed.
