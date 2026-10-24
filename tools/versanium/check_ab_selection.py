"""Generate A/B selected-source manifests in external scratch; never touch saved Run9."""
from pathlib import Path
import argparse,subprocess,tempfile,hashlib,json,tarfile,io
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[2]
base='60b00375def663584dfd5c6fd249d25498eeafb2'
target='257b37413ef119e249d9d903b8712af5ba919b7b'
a.output.mkdir(parents=True,exist_ok=False)
with tempfile.TemporaryDirectory() as d:
 roots={}
 for mode,revision in [('installed',base),('A',target),('B',target)]:
  control=Path(d)/mode;control.mkdir()
  archive=subprocess.check_output(['git','-C',str(repo),'archive',revision])
  with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(control,filter='data')
  # Submodule patches are unchanged, but not included by git archive.
  import shutil
  shutil.copytree(repo/'vanadium/patches',control/'vanadium/patches',dirs_exist_ok=True)
  # Use corrected coverage tooling for every product selection, not historical
  # fixture omissions in their archived test scripts. Product patches stay pinned.
  for name in ['tools/youtube_pip/tests/check_source_integration.py','tools/versanium/flag_metadata_pipeline.py','tools/versanium/selected_patch_pipeline.py']:
   shutil.copyfile(repo/name,control/name)
  if mode=='A':
   (control/'tools/environment_zoom/chromium.patch').write_bytes(subprocess.check_output(['git','-C',str(repo),'show',base+':tools/environment_zoom/chromium.patch']))
  root=a.output/mode
  subprocess.run(['python3',str(control/'tools/youtube_pip/tests/check_source_integration.py'),'--source-tree',str(a.source),'--output-dir',str(root)],check=True)
  if mode=='installed':
   import sys
   sys.path.insert(0,str(repo/'tools/versanium'))
   from flag_metadata_pipeline import reproduce
   metadata=reproduce((a.source/'chrome/browser/flag-metadata.json').read_bytes())[1]
   assert hashlib.sha256(metadata).hexdigest()=='dc5a9275719afa3bfdd89a1a1f199f524a701d3bdb4c512f4ab8bb0841abb88b'
   (root/'chrome/browser/flag-metadata.json').write_bytes(metadata)
  roots[mode]=root
 def hashes(root):return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in root.rglob('*') if f.is_file()}
 sets={k:hashes(v) for k,v in roots.items()}
 result={'base_product':base,'selection_source':target,'kind':'selected-source comparison NOT complete Run9 provenance','files':sets,'deltas':{}}
 for before,after in [('installed','A'),('A','B')]:
  changed=[n for n in sets[after] if sets[before].get(n)!=sets[after][n]]
  expected={'installed->A':{'chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'},'A->B':{'content/browser/host_zoom_map_impl.cc','content/browser/web_contents/web_contents_impl.cc'}}
  assert set(changed)==expected[before+'->'+after],changed
  result['deltas'][before+'->'+after]=changed
  diff=b''
  for name in changed:
   r=subprocess.run(['git','diff','--no-index','--',str(roots[before]/name),str(roots[after]/name)],capture_output=True)
   if r.returncode not in (0,1):raise RuntimeError(r.stderr)
   diff+=r.stdout
  (a.output/(before+'-to-'+after+'.review.diff')).write_bytes(diff.replace(b'\n \n',b'\n\n'))
 (a.output/'selection-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result['deltas'],indent=2))
