"""Recovery guard checks without downloading or building Chromium."""
from pathlib import Path
import importlib.util
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('resume', ROOT / 'tools/versanium/check_resume.py')
resume = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.control = self.workspace / 'versanium-recovery-control'
        self.control.mkdir()
        self.output = self.workspace / 'chromium/src/out/Default'
        self.output.mkdir(parents=True)
        self.args = (ROOT / 'args.gn').read_text()
        for name in ['build.ninja', '.ninja_log', '.siso_deps']:
            (self.output / name).write_text('preserved')
        (self.output / 'args.gn').write_text(resume.expected_args(self.args))
        tool = self.workspace / 'depot_tools/autoninja'
        tool.parent.mkdir()
        tool.touch()
        self.changed = '.github/workflows/resume-ideapad.yml'
        self.head = resume.BASE
        self.addCleanup(patch.stopall)
        patch.object(resume, 'git', side_effect=self.git).start()
        patch.object(resume.subprocess, 'check_output', return_value=self.args).start()
        self.input_check = types.SimpleNamespace(validate=lambda *a: None)
        patch.dict(sys.modules, {'check_environment_zoom_revision': self.input_check}).start()

    def git(self, root, *args):
        if args[0] == 'diff':
            return self.changed
        return '8b1224debc00000000000000000000000000000000' if root.name == 'src' else self.head

    def test_accepts_original_configuration_without_changing_outputs(self):
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        resume.validate(self.workspace, self.control)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})

    def test_rejects_changed_build_input(self):
        self.changed = 'patch.sh'
        with self.assertRaisesRegex(RuntimeError, 'Build input changed'):
            resume.validate(self.workspace, self.control)

    def test_rejects_other_run_and_release_identity(self):
        self.head = 'other'
        with self.assertRaisesRegex(RuntimeError, 'original Run'):
            resume.validate(self.workspace, self.control)
        self.head = resume.BASE
        (self.output / 'args.gn').write_text(self.args)
        with self.assertRaisesRegex(RuntimeError, 'GN args'):
            resume.validate(self.workspace, self.control)

    def test_missing_state_never_falls_back_to_full_build(self):
        (self.output / '.siso_deps').unlink()
        with self.assertRaisesRegex(RuntimeError, 'Missing incremental'):
            resume.validate(self.workspace, self.control)

    def test_rejects_wrong_control_location(self):
        with self.assertRaisesRegex(RuntimeError, 'control checkout'):
            resume.validate(self.workspace, self.workspace)

    def test_existing_workspace_blocks_checkout(self):
        w = yaml.load((ROOT / '.github/workflows/build.yml').read_text(), Loader=yaml.BaseLoader)
        step = next(s for s in w['jobs']['build']['steps'] if s.get('name', '').startswith('Protect existing'))
        self.assertIn('Protect existing', step['name'])
        result = subprocess.run(['bash', '-c', step['run']],
                                env={'GITHUB_WORKSPACE': str(self.workspace)}, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.output / '.siso_deps').exists())

    def test_recovery_selection_and_isolated_checkout(self):
        w = yaml.load((ROOT / '.github/workflows/build.yml').read_text(), Loader=yaml.BaseLoader)
        job = w['jobs']['build']
        self.assertIn('1200', job['timeout-minutes'])
        steps = job['steps']
        checkout = next(s for s in steps if s.get('uses', '').startswith('actions/checkout@'))
        self.assertIn('versanium-recovery-control', checkout['with']['path'])
        self.assertEqual(w['env']['VERSANIUM_RELEASE_APPROVED'], 'false')
        self.assertEqual(w['on']['workflow_dispatch']['inputs']['resume_ideapad']['default'], 'false')
        guard = steps[0]['run'].split('if [ "$RESUME" = true ]; then')[0]
        for provider, test, repo, accepted in [
            ('ideapad', 'true', 'Nvoid911-Lab/Versanium', True),
            ('blacksmith', 'true', 'Nvoid911-Lab/Versanium', False),
            ('ideapad', 'false', 'Nvoid911-Lab/Versanium', False),
            ('ideapad', 'true', 'Nvoid911/Versanium', False),
        ]:
            result = subprocess.run(['bash', '-c', guard], capture_output=True,
                env={'RESUME': 'true', 'PROVIDER': provider, 'TEST_BUILD': test, 'GITHUB_REPOSITORY': repo})
            self.assertEqual(result.returncode == 0, accepted)

    def test_both_targets_limit_jobs_and_stop_on_failure(self):
        # Exercise the actual shell invocation lines with a fake compiler driver.
        script = (ROOT / 'tools/versanium/resume_ideapad.sh').read_text()
        commands = '\n'.join(line for line in script.splitlines() if line.startswith('autoninja '))
        self.assertTrue(commands)
        stub = 'autoninja() { printf "%s\\n" "$*"; return "${FAIL:-0}"; };\n'
        completed = subprocess.run(['bash', '-e', '-c', stub + commands],
            capture_output=True, text=True, env={})
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.splitlines(), [
            '-C out/Default -j 6 chrome_java',
            '-C out/Default -j 6 chrome_public_apk'])
        failed = subprocess.run(['bash', '-e', '-c', stub + commands],
            capture_output=True, text=True, env={'FAIL': '9'})
        self.assertEqual(failed.returncode, 9)
        self.assertEqual(len(failed.stdout.splitlines()), 1)


if __name__ == '__main__':
    unittest.main()
