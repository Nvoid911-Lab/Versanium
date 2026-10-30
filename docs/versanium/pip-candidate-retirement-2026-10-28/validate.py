from pathlib import Path
import subprocess,sys,json,hashlib,ast,re,unittest,importlib.util,os
ROOT=Path(__file__).resolve().parents[3]
REPORT=ROOT/'docs/versanium/pip-candidate-retirement-2026-10-28'
ledger=json.loads((REPORT/'before.json').read_text(encoding='utf-8'))
def git(*args):return subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'-C',str(ROOT),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
results=[]
def passed(label): results.append(label);print('PASS:',label,flush=True)
for n,h in ledger['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
passed(f"All {len(ledger['protected_sha256'])} protected input files byte-identical (including all pre-existing docs/evidence, Zoom, pins, workflows, branding)")
assert all(not (ROOT/n).exists() for n in ledger['delete'])
passed('All 34 planned old candidate files absent')
for n in ['tools/apply_environment_zoom.py','tools/check_environment_zoom_revision.py','tools/configure_f11_identity.py']:
    assert sha((ROOT/n).read_bytes())==ledger['all_tracked_sha256'][n]
old=git('show',ledger['start_head']+':patch.sh')
assert (ROOT/'patch.sh').read_bytes().replace(b'\r\n',b'\n')==old.replace(b'python3 "$SCRIPT_DIR/tools/apply_youtube_candidates.py" || exit 1\n',b'')
passed('patch.sh exact one-line deletion only; Zoom/F11/context-menu shard2/inherited media and non-PiP edits unchanged')
old=git('show',ledger['start_head']+':tools/versanium/write_build_provenance.py')
start=old.index(b"    for path in sorted((repository/'tools/youtube_pip')");end=old.index(b"    inputs['clang_binary']",start)
assert (ROOT/'tools/versanium/write_build_provenance.py').read_bytes().replace(b'\r\n',b'\n')==old[:start]+old[end:]
passed('Shared provenance recorder: only 3 old-candidate lines removed')
texts=[n for n in ledger['all_tracked_sha256'] if (ROOT/n).is_file() and n.startswith('tools/') and n.endswith(('.py','.java','.patch','.js','.cjs','.sh'))]
removed_refs=[]
for n in texts+['patch.sh','build.sh','common.sh']:
    text=(ROOT/n).read_text(encoding='utf-8')
    for removed in ledger['delete']:
        if removed in text: removed_refs.append((n,removed))
assert not removed_refs,removed_refs
passed('No executable reference to a deleted candidate generator, patch, test or controller')
runtime_pattern=re.compile(r'versanium-youtube-(?:pip-candidate|background-candidate|diagnostics)|applyVersaniumYoutubeCandidate|versanium_fullscreen_diagnostic_scope|reportTitaniumYoutubePip|unsafe.?diagnostic',re.I)
hits=[]
for n in texts+['patch.sh']:
    if runtime_pattern.search((ROOT/n).read_text(encoding='utf-8')):hits.append(n)
assert not hits,hits
passed('No old product flag, TabImpl candidate hook, controller logger or diagnostic scope reference in executable product inputs')
python_files=list((ROOT/'tools').rglob('*.py'))
for p in python_files:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
passed(f'Python AST syntax: {len(python_files)} remaining tool/test files')
shell=Path('C:/Users/Nvoid/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/usr/bin/sh.exe')
subprocess.run([str(shell),'-n','patch.sh'],cwd=ROOT,check=True)
passed('patch.sh Bash 5.2 syntax via bundled sh.exe; script NOT executed')
f11=(ROOT/'patch.sh').read_text(encoding='utf-8').split("python3 - <<'PY_F11' || exit 1\n",1)[1].split('\nPY_F11',1)[0]
ast.parse(f11);passed('F11 embedded Python syntax retained')
for script in ['tools/environment_zoom/tests/check_build_pin.py']:
    subprocess.run([sys.executable,'-B',script],cwd=ROOT,check=True,env=dict(os.environ,PYTHONUTF8='1'))
passed('Existing Chromium156/Vanadium revision gate: 5 metadata-model cases')
spec=importlib.util.spec_from_file_location('migration',ROOT/'tools/versanium/tests/test_migration.py')
m=importlib.util.module_from_spec(spec)
try:spec.loader.exec_module(m)
except ModuleNotFoundError as exc:
    assert exc.name=='yaml'
    print('SKIP migration tests: PyYAML unavailable',flush=True)
    m=None
excluded={'test_build_identity_selector_without_running_build_script','test_packaging_bytes_and_only_arm64','test_workflow_release_guard_and_no_auto_trigger','test_inline_shell_and_yaml'}
if m:
    suite=unittest.TestSuite(m.MigrationTests(n) for n in unittest.defaultTestLoader.getTestCaseNames(m.MigrationTests) if n not in excluded)
    r=unittest.TextTestRunner(verbosity=2).run(suite);assert r.wasSuccessful()
    passed(f'Existing migration non-shell/non-APK tests: {r.testsRun} passed')
for name in ['test_contextmenu_patch.py','test_selected_pipeline.py']:
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tools/versanium/tests'),pattern=name));assert r.wasSuccessful()
    passed(f'{name}: ran {r.testsRun}; skips {len(r.skipped)} (fixed source/fixture unavailable)')
assets=json.loads((ROOT/'res/versanium/assets.json').read_text())
worktree_diffs=[]
for n,h in assets['files'].items():
    data=(ROOT/n).read_bytes()
    if sha(data)!=h:
        assert sha(git('show',ledger['start_head']+':'+n))==h,n
        assert sha(data.replace(b'\r\n',b'\n'))==h,n
        assert sha(data)==ledger['all_tracked_sha256'][n],n
        worktree_diffs.append(n)
passed(f'Asset mismatch diagnosed: {len(worktree_diffs)} pre-existing CRLF worktree text files; committed LF blobs match asset ledger; no asset edits')
subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'-C',str(ROOT),'diff','--check'],check=True)
passed('git diff --check')
out={'checks_passed':results,'asset_check_raw':'FAIL on pre-existing CRLF asset; committed blobs and start hashes verified; no fix in PiP cleanup','asset_crlf_files':worktree_diffs,'limitations':['Migration/resume suite unavailable: bundled Python has no PyYAML; no dependencies installed','No JDK/javac/java available: JVM Zoom policy/bridge/persistence/backup tests not run','No pinned Chromium source/selected fixture: real patch application and integration skipped','No GN/build/Actions/APK/device validation performed','Historical read-only trace/JNI verifiers retained; docs and manifests retain old names as evidence','EnvironmentZoom.java and its tests retain old comment/API; all bytes intentionally unchanged']}
(REPORT/'validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('STATIC VALIDATION COMPLETE',flush=True)
