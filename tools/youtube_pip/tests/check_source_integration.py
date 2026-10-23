"""Selective real-source integration. No build.sh, Chromium download, GN or runner use.
Supply pristine files from the exact pinned Chromium commit. Only output-dir is mutated.
"""
from pathlib import Path
import argparse,importlib.util,subprocess,fnmatch,shutil,sys,re,json
sys.dont_write_bytecode=True
repo=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-tree',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
spec=importlib.util.spec_from_file_location('zoom_patch_test',repo/'tools/environment_zoom/tests/check_patch.py');zoom=importlib.util.module_from_spec(spec);spec.loader.exec_module(zoom)
zoom.run(a.source_tree,repo/'vanadium/patches',a.output_dir)
paths=[line[6:] for line in (repo/'tools/youtube_pip/diagnostics.patch').read_text().splitlines() if line.startswith('--- a/')]
paths+=['chrome/android/java/src/org/chromium/chrome/browser/ChromeTabbedActivity.java','content/public/renderer/render_frame_media_playback_options.cc','chrome/android/java/AndroidManifest.xml']
for relative in paths:
 target=a.output_dir/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.source_tree/relative,target)
for patch in sorted((repo/'vanadium/patches').glob('*.patch')):
 if any(fnmatch.fnmatch(patch.name,pattern) for pattern in zoom.removed):continue
 text=patch.read_text().replace('VANADIUM','TITANIUM').replace('Vanadium','Titanium').replace('vanadium','titanium')
 subprocess.run(['git','apply',*['--include='+path for path in paths],'-'],input=text,text=True,cwd=a.output_dir,check=True)
f11=(repo/'patch.sh').read_text().split("python3 - <<'PY_F11' || exit 1\n",1)[1].split('\nPY_F11',1)[0]
subprocess.run(['python3','-c',f11],cwd=a.output_dir,check=True)
media=a.output_dir/'content/public/renderer/render_frame_media_playback_options.cc'
text=media.read_text();assert text.count('#if BUILDFLAG(IS_ANDROID)')==2
media.write_text(text.replace('#if BUILDFLAG(IS_ANDROID)','#if 0')) # Existing unchanged Titanium policy.
sys.path.insert(0,str(repo/'tools'))
from apply_youtube_candidates import apply
apply(a.output_dir,repo)
flags=(a.output_dir/'chrome/browser/flag-metadata.json').read_text()
names=re.findall(r'"name": "([^"\n]+)"',flags)
assert len(names)==len(set(names))
for name in ('versanium-youtube-diagnostics','versanium-youtube-pip-candidate','versanium-youtube-background-candidate'):
 assert names.count(name)==1
 record=re.search(r'\{[^{}]*"name": "'+name+r'"[^{}]*\}',flags).group()
 assert json.loads(record)['expiry_milestone']==157
assert 'void applyVersaniumYoutubeCandidate(String stage)' in (a.output_dir/'chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java').read_text()
print('Pinned 156 + selected Vanadium + zoom/SAF + F11 + inherited media policy + PiP hooks/flags PASS')
print('No full patch.sh execution, GN, AndroidX/UI inflation or Chromium native compilation')
