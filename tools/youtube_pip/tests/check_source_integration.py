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
paths += [line[6:] for line in (repo/'tools/youtube_pip/execution_scope.patch').read_text().splitlines() if line.startswith('--- a/')]
paths+=['url/gurl.h','chrome/android/java/src/org/chromium/chrome/browser/ChromeTabbedActivity.java','content/public/renderer/render_frame_media_playback_options.cc','chrome/android/java/AndroidManifest.xml']
paths+=['chrome/android/java/src/org/chromium/chrome/browser/fullscreen/FullscreenHtmlApiHandlerBase.java']
paths+=['chrome/android/java/src/org/chromium/chrome/browser/tab/TabWebContentsDelegateAndroidImpl.java',
        'chrome/android/java/src/org/chromium/chrome/browser/app/tab_activity_glue/ActivityTabWebContentsDelegateAndroid.java']
sys.path.insert(0,str(repo/'tools'))
from apply_fullscreen_native_origin import FILES as native_diagnostic_inputs
paths+=list(native_diagnostic_inputs)
from apply_content_fullscreen_origin import FILES as content_diagnostic_inputs
paths+=list(content_diagnostic_inputs)
paths=list(dict.fromkeys(paths))
for relative in paths:
 target=a.output_dir/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.source_tree/relative,target)
for patch in sorted((repo/'vanadium/patches').glob('*.patch')):
 if any(fnmatch.fnmatch(patch.name,pattern) for pattern in zoom.removed):continue
 text=patch.read_text().replace('VANADIUM','TITANIUM').replace('Vanadium','Titanium').replace('vanadium','titanium')
 subprocess.run(['git','apply',*['--include='+path for path in paths],'-'],input=text,text=True,cwd=a.output_dir,check=True)
sys.path.insert(0,str(repo/'tools'))
from versanium.selected_patch_pipeline import apply as apply_common_selected
apply_common_selected(a.output_dir,repo)
f11=(repo/'patch.sh').read_text().split("python3 - <<'PY_F11' || exit 1\n",1)[1].split('\nPY_F11',1)[0]
subprocess.run(['python3','-c',f11],cwd=a.output_dir,check=True)
media=a.output_dir/'content/public/renderer/render_frame_media_playback_options.cc'
text=media.read_text();assert text.count('#if BUILDFLAG(IS_ANDROID)')==2
media.write_text(text.replace('#if BUILDFLAG(IS_ANDROID)','#if 0')) # Existing unchanged Titanium policy.
sys.path.insert(0,str(repo/'tools'))
from versanium.flag_metadata_pipeline import apply_expiry_overrides,patch_sh_flags,EXPIRY_FLAGS
assert patch_sh_flags((repo/'patch.sh').read_text())==EXPIRY_FLAGS
metadata=a.output_dir/'chrome/browser/flag-metadata.json'
metadata.write_bytes(apply_expiry_overrides(metadata.read_bytes()))
from apply_youtube_candidates import apply
apply(a.output_dir,repo)
flags=metadata.read_text()
names=re.findall(r'"name": "([^"\n]+)"',flags)
assert len(names)==len(set(names))
for name in ('versanium-youtube-diagnostics','versanium-youtube-pip-candidate','versanium-youtube-background-candidate'):
 assert names.count(name)==1
 record=re.search(r'\{[^{}]*"name": "'+name+r'"[^{}]*\}',flags).group()
 assert json.loads(record)['expiry_milestone']==157
assert 'void applyVersaniumYoutubeCandidate(String stage)' in (a.output_dir/'chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java').read_text()
native=(a.output_dir/'content/browser/renderer_host/render_frame_host_impl.cc').read_text()
assert 'CanExecuteJavaScript() ||' not in native
assert 'void RenderFrameHostImpl::ExecuteVersaniumYoutubeCandidate(' in native
assert 'kVersaniumYoutubeCandidate' in native
# Generic permission and complete generic execution bodies remain byte-for-byte pinned.
original=(a.source_tree/'content/browser/renderer_host/render_frame_host_impl.cc').read_text()
for name,end in [('ExecuteJavaScript','ExecuteJavaScriptInIsolatedWorld')]:
 start='void RenderFrameHostImpl::'+name+'('
 baseline=original.split(start,1)[1].split('\n}\n',1)[0]
 actual=native.split(start,1)[1].split('\n}\n',1)[0]
 assert actual==baseline
assert native.split('bool RenderFrameHostImpl::CanExecuteJavaScript() {',1)[1].split('\n}',1)[0] == original.split('bool RenderFrameHostImpl::CanExecuteJavaScript() {',1)[1].split('\n}',1)[0]
header=(a.output_dir/'content/browser/renderer_host/versanium_youtube_candidate.h').read_text()
assert (repo/'tools/youtube_pip/candidate.js').read_text() in header
assert 'versanium-youtube-candidate-v1' not in (repo/'tools/youtube_pip/execution_scope.patch').read_text()
entry=(a.output_dir/'content/browser/web_contents/web_contents_android.cc').read_text()
baseline=(a.source_tree/'content/browser/web_contents/web_contents_android.cc').read_text()
assert entry.split('void WebContentsAndroid::EvaluateJavaScript(',1)[1].split('\n}\n',1)[0] == baseline.split('void WebContentsAndroid::EvaluateJavaScript(',1)[1].split('\n}\n',1)[0]
assert 'candidate_context->IsOffTheRecord()' in native
assert 'candidate_context->ShutdownStarted()' in native
assert 'frame->GetParentOrOuterDocumentOrEmbedder()' in native
# Fixed-payload API has no Java/native script argument; generic callers keep old CHECKs.
assert 'ApplyVersaniumYoutubeCandidate(\n    JNIEnv* env, bool mobile, const JavaRef<jobject>& callback)' in entry
fixed=native.split('void RenderFrameHostImpl::ExecuteVersaniumYoutubeCandidate(',1)[1].split('\n}\n',1)[0]
assert 'if (!IsVersaniumYoutubeScopeAllowed(this))' in fixed
assert 'std::u16string script = kVersaniumYoutubeCandidate;' in fixed
assert 'JavaScriptExecuteRequest(script, wants_result' in fixed
assert 'ExecuteJavaScript(' not in fixed and 'ForTests' not in fixed
java=(a.output_dir/'content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsImpl.java').read_text()
assert 'long nativeWebContentsAndroid, boolean mobile, @Nullable JavaScriptCallback callback);' in java
assert 'renderer_host/versanium_youtube_candidate.h' in (a.output_dir/'content/browser/BUILD.gn').read_text()
assert 'contents.applyVersaniumYoutubeCandidate(mobile, null)' in (repo/'tools/apply_youtube_candidates.py').read_text()
assert 'contents.evaluateJavaScript(' not in (repo/'tools/apply_youtube_candidates.py').read_text()
assert 'AllowInjectingJavaScript();' not in (repo/'tools/youtube_pip/execution_scope.patch').read_text()
print('Pinned 156 + selected Vanadium + zoom/SAF + F11 + inherited media policy + PiP hooks/flags PASS')
print('No full patch.sh execution, GN, AndroidX/UI inflation or Chromium native compilation')
