"""Apply only the separate PiP branch's opt-in, privacy-scoped diagnostic patch."""
from pathlib import Path
import os
import subprocess


def apply(root, repository):
    patch = repository / 'tools/youtube_pip/diagnostics.patch'
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=root, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=root, check=True)


if __name__ == '__main__':
    from check_environment_zoom_revision import validate
    root = Path.cwd()
    repository = Path(os.environ['SCRIPT_DIR'])
    validate(root, repository)
    apply(root, repository)
