# CIPD collector large-receipt correction — 2026-10-26 JST

Previous docs/controller9db02a6 collection stopped BEFORE CIPD/jar collection at
`/home/takuma/versanium/cipd-review-evidence-sucsAo`: small(applied.json) applied
a 1MiB package-metadata cap to the normal full Default inventory receipt. No jar,
package instance or new acquisition finding is inferred from that failed run.
Keep that evidence and collector unchanged. This replacement is a new external
collector; product/helper/selection and applying controller7b60873 are unchanged.

## Separate read policies and validation

Applied receipt: regular non-symlink file, 0<size<=256MiB. Read via json.load,
not small/read_bytes+json.loads, after recording size and SHA256. Estimated memory
budget =32*file bytes+64MiB; require <=half actual MemAvailable (swap NOT counted).
This is a conservative heuristic, not a hard allocator/RSS guarantee. Missing
MemAvailable, cap violation, MemoryError, malformed/deep JSON or unsupported
schema stops with evidence; never silently raises the cap or strips inventory.
Hash/size/mtime/inode are rechecked after parsing. Duplicate keys are rejected.

Check format/configuration/completed source-only phase, no GN/compile, paths,
original applying controller, repository/Chromium/depot pins, exact selection
hash,10 before/after pairs and the entire inventory's entry types/required outputs.
Receipt stores10 changed pairs;58-input coverage is still enforced by the
original --verify/selection, not falsely inferred from a58-entry receipt map.
Only required fields and read statistics remain for later collection; original
file/inventory is neither rewritten nor removed. This is schema/integrity reading,
NOT replacement for original58-source/provenance/Default verification.

Small policies unchanged: description/package JSON1MiB, explicit manifest and
DEPS/gclient source/entries caps4MiB, embedded jar metadata64KiB, current ID512B.
Audited all small() callers: applied.json was the only inventory-bearing receipt
passed to it. Hash-only gclient records/binaries/jars use streaming SHA256, not
small(). Source files/entries/manifest format caps may still stop on unusually
large metadata; that is explicit review, not a reason to remove all limits.
Native source/graph/after-apk inventories are NOT parsed by this collector; old
helpers use their own readers and are unchanged. No claim that all other actual
host evidence sizes have been measured.

## Complete replacement command — fresh external evidence only

This creates only a NEW external evidence directory/collector/report. It does
NOT checkout/change applying controller, edit saved files, run clients/bootstrap,
create a build output, fetch dependencies or compile. Keep builders idle. On
failure, report/log/status/collector remain; no automatic retry/reset/cleanup.
Save the printed directory. Share selected report fields and error, not general
logs/configuration. Unknown metadata/layout remains unresolved as in the prior
[provenance report](nullaway-cipd-host-followup.md).

```sh
(
  set -eu
  CIPD_EVIDENCE=$(mktemp -d /home/takuma/versanium/cipd-review-evidence-v2-XXXXXX)
  printf 'Evidence: %s\n' "$CIPD_EVIDENCE"
  cat > "$CIPD_EVIDENCE/collect-cipd-v2.py" <<'PY'
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
def available_memory():
 for line in Path('/proc/meminfo').read_text(encoding='ascii').splitlines():
  fields=line.split()
  if fields and fields[0]=='MemAvailable:' and fields[2:]==['kB']:
   return int(fields[1])*1024
 raise ValueError('MemAvailable unavailable; stop for memory review')
def no_duplicate_keys(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError('duplicate JSON key')
  result[key]=value
 return result
def read_applied(p,workspace,available_bytes=None):
 # Large inventory-bearing receipts have their own bounded policy, not small().
 st=p.stat();size=st.st_size
 if not p.is_file() or p.is_symlink() or not 0<size<=256*1024*1024:
  raise ValueError('applied record unsupported type/size; max 256MiB')
 available=available_memory() if available_bytes is None else available_bytes
 estimated=32*size+64*1024*1024
 if type(available) is not int or available<=0 or estimated>available//2:
  raise ValueError('applied JSON estimated memory exceeds half MemAvailable; stop')
 before=sha(p)
 with p.open('r',encoding='utf-8') as f:
  r=json.load(f,object_pairs_hook=no_duplicate_keys)
 def need(ok,message):
  if not ok:raise ValueError('invalid applied record: '+message)
 def digest_string(v,n=64):return isinstance(v,str) and re.fullmatch('[0-9a-f]{'+str(n)+'}',v) is not None
 need(type(r) is dict,'root object')
 need(type(r.get('format')) is int and r['format']==1,'format')
 need(r.get('configuration')=='NativeContentOrigin','configuration')
 need(r.get('applied') is True and r.get('phase')=='SOURCE_APPLIED_GRAPH_UNCHANGED','completed source-only phase')
 need(r.get('gn_executed') is False and r.get('compile_executed') is False,'no GN/compile')
 need(r.get('paths')==[str(workspace),str(workspace/'chromium/src'),str(workspace/'chromium/src/out/Default')],'saved paths')
 proof=r.get('controller_proof');prov=r.get('updated_provenance')
 need(type(proof) is dict and proof.get('preparation_controller')=='7b608732d56f3885d5c950715d10709405695e70','applying controller')
 need(type(prov) is dict and digest_string(prov.get('depot_tools_commit'),40),'depot commit')
 need(prov.get('repository_commit')=='7d9102f4f0e35dec9f69425de44cd889836a88ac','repository pin')
 need(prov.get('chromium_input')=='1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775','Chromium pin')
 need(r.get('selection_hash')=='393b14b36f80070856c492a043423f68f7e2fff47a5634a7f148f124f9aa341a','fixed selection hash')
 maps=[]
 for key in ['before_sha256','after_sha256']:
  values=r.get(key)
  need(type(values) is dict and len(values)==10,key+' shape')
  need(all(isinstance(n,str) and n and not Path(n).is_absolute() and '..' not in Path(n).parts and digest_string(h) for n,h in values.items()),key+' paths/hashes')
  maps.append(values)
 need(maps[0].keys()==maps[1].keys() and sum(maps[0][n]!=maps[1][n] for n in maps[0])==10,'10 changed-file hash pairs (58-input selection checked by original helper)')
 outputs=r.get('outputs');need(type(outputs) is dict and bool(outputs),'output inventory')
 for name,v in outputs.items():
  need(isinstance(name,str) and name and not Path(name).is_absolute() and '..' not in Path(name).parts,'inventory path')
  need(type(v) is dict,'inventory entry')
  if 'link' in v:need(set(v)=={'link'} and isinstance(v['link'],str),'inventory link')
  else:
   need(set(v)=={'sha256','mode','size','mtime_ns'} and digest_string(v['sha256']),'inventory file fields')
   need(all(type(v[k]) is int and v[k]>=0 for k in ['mode','size','mtime_ns']),'inventory numeric fields')
 for name in ['args.gn','build.ninja','.ninja_log','.siso_deps']:
  need(name in outputs and 'sha256' in outputs[name],'required output '+name)
 after=p.stat()
 need((st.st_size,st.st_mtime_ns,st.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino) and sha(p)==before,'record changed while reading')
 # Keep only needed fields in memory during jar/package collection; disk inventory untouched.
 return {'controller_proof':proof,'updated_provenance':prov,'receipt_sha256':before,
         'read_stats':{'bytes':size,'estimated_memory_bytes':estimated,'mem_available_bytes':available,'output_entries':len(outputs)}}

record=read_applied(a,w);prov=record['updated_provenance']
report={'applied_read_stats':record['read_stats'],'applied_sha256':record['receipt_sha256'],'applying_controller':record['controller_proof']['preparation_controller'],
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
  if PYTHONDONTWRITEBYTECODE=1 python3 "$CIPD_EVIDENCE/collect-cipd-v2.py" > "$CIPD_EVIDENCE/report.json" 2> "$CIPD_EVIDENCE/stderr.log"; then
    printf '0\n' > "$CIPD_EVIDENCE/status"
    printf 'Collection complete: %s/report.json\n' "$CIPD_EVIDENCE"
  else
    CIPD_STATUS=$?
    printf '%s\n' "$CIPD_STATUS" > "$CIPD_EVIDENCE/status"
    cat "$CIPD_EVIDENCE/stderr.log"
    printf 'Stopped; all evidence retained: %s\n' "$CIPD_EVIDENCE"
    exit "$CIPD_STATUS"
  fi
)
```

Read report.applied_read_stats for actual bytes, estimated memory, available
memory and inventory count. An empty/partial report after failure is NOT PASS.
New receipt reader passing is NOT evidence that CIPD identity/NullAway passed.

## Regression validation (local fixtures only)

Five tests execute the actual documented reader functions extracted via AST:
>1MiB normal12004-entry inventory and unchanged original bytes; malformed/root/
duplicate JSON; required key/type/config/phase rejection;256MiB size and memory
budget rejection; retained1MiB metadata cap. PASS. These fixtures are not a real
host applied.json replay or CIPD collection. Reproducible regression source:

```python
import ast,hashlib,json,re,tempfile,unittest,copy
from pathlib import Path
# Run from repository root; extract the exact collector embedded above.
text=Path('docs/versanium/cipd-collector-large-record-review.md').read_text()
source=re.search(r"cat > .*? <<'PY'\n(.*?)\nPY\n",text,re.S)[1];tree=ast.parse(source)
names={'sha','small','available_memory','no_duplicate_keys','read_applied'}
ns=dict(Path=Path,hashlib=hashlib,json=json,re=re)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<actual documented functions>','exec'),ns)
class Receipts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)/'applied.json';self.w=Path('/saved/workspace')
  sel=json.loads(Path('docs/versanium/content-fullscreen-diagnostic-selection.json').read_text())
  entry={'sha256':'a'*64,'mode':33188,'size':1,'mtime_ns':1}
  self.r={'format':1,'configuration':'NativeContentOrigin','applied':True,'phase':'SOURCE_APPLIED_GRAPH_UNCHANGED','gn_executed':False,'compile_executed':False,'paths':[str(self.w),str(self.w/'chromium/src'),str(self.w/'chromium/src/out/Default')],'controller_proof':{'preparation_controller':'7b608732d56f3885d5c950715d10709405695e70'},'updated_provenance':{'depot_tools_commit':'b'*40,'repository_commit':'7d9102f4f0e35dec9f69425de44cd889836a88ac','chromium_input':'1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775'},'selection_hash':'393b14b36f80070856c492a043423f68f7e2fff47a5634a7f148f124f9aa341a','before_sha256':sel['before'],'after_sha256':sel['after'],'outputs':{k:dict(entry) for k in ['args.gn','build.ninja','.ninja_log','.siso_deps']+[f'obj/item{i}.o' for i in range(12000)]}}
 def run_record(self,r):
  self.p.write_text(json.dumps(r));return ns['read_applied'](self.p,self.w,available_bytes=1024**3)
 def test_large_valid_and_unchanged(self):
  self.p.write_text(json.dumps(self.r));before=self.p.read_bytes();self.assertGreater(len(before),1024**2)
  result=ns['read_applied'](self.p,self.w,available_bytes=1024**3)
  self.assertEqual(result['read_stats']['output_entries'],12004);self.assertEqual(self.p.read_bytes(),before);self.assertNotIn('outputs',result)
 def test_required_fields_types_config(self):
  for key in ['updated_provenance','controller_proof','configuration','outputs','before_sha256','paths']:
   wrong=copy.deepcopy(self.r);del wrong[key]
   with self.subTest(missing=key),self.assertRaises(ValueError):self.run_record(wrong)
  for key,value in [('applied',1),('format',True),('configuration','AOriginForwardNative'),('outputs',[]),('controller_proof',{}),('updated_provenance',{}),('gn_executed',True)]:
   wrong=copy.deepcopy(self.r);wrong[key]=value
   with self.subTest(wrong=key),self.assertRaises(ValueError):self.run_record(wrong)
 def test_invalid_json_duplicate(self):
  for text in ['{not JSON','[]','{"format":1,"format":1}']:
   self.p.write_text(text)
   with self.assertRaises(ValueError):ns['read_applied'](self.p,self.w,available_bytes=1024**3)
 def test_memory_and_size_caps(self):
  self.p.write_text(json.dumps(self.r))
  with self.assertRaisesRegex(ValueError,'memory'):ns['read_applied'](self.p,self.w,available_bytes=1024)
  with self.p.open('wb') as f:f.truncate(256*1024**2+1)
  with self.assertRaisesRegex(ValueError,'size'):ns['read_applied'](self.p,self.w,available_bytes=1024**3)
 def test_small_metadata_cap_retained(self):
  self.p.write_bytes(b'x'*(1024**2+1))
  with self.assertRaisesRegex(ValueError,'metadata too large'):ns['small'](self.p)
unittest.main()

```

Controller compatibility remains docs-only: fetch/review new SHA WITHOUT changing
HEAD7b60873, use prior follow-up's ancestor/Markdown-only/invariant proof and
original helper --verify on TQNw0X/applied.json. Never reapply or edit old receipt.
Default/args, candidate58,3 future argument overrides and future isolated analysis
sequence unchanged. No verification output/GN/analysis work has been done.
