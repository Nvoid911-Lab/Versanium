"""Install the independent Brave #36838 Phase 1 bundle in a fresh Chromium tree.

Never invokes GN, compilation, the retired generators, or saved-workspace helpers.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parent


def apply(root):
    root = root.resolve()
    patch = (BUNDLE / 'chromium.patch').read_bytes().replace(b'\r\n', b'\n')
    # One preflight for Java hooks and native logging; do not partially install.
    patch += (BUNDLE / 'native-diagnostics.patch').read_bytes().replace(b'\r\n', b'\n')
    copies = {
        root / 'chrome/android/java/src' / p.relative_to(BUNDLE / 'java'): p
        for p in (BUNDLE / 'java').rglob('*.java')
    }
    if len(copies) != 2 or any(p.exists() for p in copies):
        raise RuntimeError('Expected two absent Phase 1 overlay destinations')
    subprocess.run(['git', 'apply', '--check', '-'], input=patch, cwd=root, check=True)
    subprocess.run(['git', 'apply', '-'], input=patch, cwd=root, check=True)
    for target, source in copies.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(BUNDLE.parent))
    from check_environment_zoom_revision import validate
    validate(args.root, BUNDLE.parents[1])
    apply(args.root)
