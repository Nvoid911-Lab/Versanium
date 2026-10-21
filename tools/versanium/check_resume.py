"""Read-only, narrowly pinned recovery validation for IdeaPad Run #5."""
from pathlib import Path
import argparse
import re
import subprocess
import sys

BASE = '6e7517e6de89e5a1230cebf906470795112466a3'
PACKAGE = 'io.github.nvoid911.versanium.test'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def expected_args(base_args):
    result = base_args.replace('target_cpu = "arm"', 'target_cpu = "arm64"')
    result, count = re.subn(r'^chrome_public_manifest_package\s*=\s*"[^"]+"\s*$',
                           f'chrome_public_manifest_package = "{PACKAGE}"',
                           result, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError('Expected exactly one package setting')
    return result


def validate(workspace, control):
    workspace, control = workspace.resolve(), control.resolve()
    if control != workspace / 'versanium-recovery-control':
        raise RuntimeError('Unexpected control checkout location')
    if git(workspace, 'rev-parse', 'HEAD') != BASE:
        raise RuntimeError('Recovery is restricted to the original Run #5 repository HEAD')
    # Current controller may change recovery code/docs/workflows, never build inputs.
    changed = git(control, 'diff', '--name-only', BASE, 'HEAD').splitlines()
    allowed = {'PROJECT_STATUS.md', 'ARCHITECTURE.md', 'DECISIONS.md', 'RULES.md'}
    for path in changed:
        if path not in allowed and not path.startswith(('.github/workflows/', 'docs/',
                'tools/versanium/tests/', 'tools/versanium/check_resume.py',
                'tools/versanium/resume_ideapad.sh')):
            raise RuntimeError(f'Build input changed since Run #5: {path}')
    source = workspace / 'chromium/src'
    output = source / 'out/Default'
    args = (output / 'args.gn').read_text()
    baseline = subprocess.check_output(['git', '-C', str(control), 'show', BASE + ':args.gn'], text=True)
    if args != expected_args(baseline):
        raise RuntimeError('Existing GN args differ from the original arm64 Test configuration')
    if not re.search(r'^target_cpu\s*=\s*"arm64"$', args, re.MULTILINE):
        raise RuntimeError('Expected arm64 Test build')
    for name in ['build.ninja', '.ninja_log', '.siso_deps']:
        if not (output / name).is_file():
            raise RuntimeError(f'Missing incremental build state: {name}')
    if not (workspace / 'depot_tools/autoninja').is_file():
        raise RuntimeError('Missing preserved depot_tools')
    sys.path.insert(0, str(control / 'tools'))
    from check_environment_zoom_revision import validate as validate_inputs
    validate_inputs(source, workspace)
    if not git(source, 'rev-parse', 'HEAD').startswith('8b1224debc'):
        raise RuntimeError('Patched Chromium HEAD differs from the reported Run #5 state')
    print('Original Run #5 workspace and arm64 Test configuration verified')
    print('Patched source has expected local changes; no reset, sync, hooks or patch reapplication')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--control', type=Path, required=True)
    a = p.parse_args()
    validate(a.workspace, a.control)
