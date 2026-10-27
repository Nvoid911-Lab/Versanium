"""Install the independent Brave #36838 Phase 1 bundle in a fresh Chromium tree.

Never invokes GN, compilation, the retired generators, or saved-workspace helpers.
"""
from pathlib import Path
import argparse
import shutil
import subprocess

BUNDLE = Path(__file__).resolve().parent


def apply(root):
    root = root.resolve()
    patch = BUNDLE / 'chromium.patch'
    copies = {
        root / 'chrome/android/java/src' / p.relative_to(BUNDLE / 'java'): p
        for p in (BUNDLE / 'java').rglob('*.java')
    }
    if len(copies) != 2 or any(p.exists() for p in copies):
        raise RuntimeError('Expected two absent Phase 1 overlay destinations')
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=root, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=root, check=True)
    for target, source in copies.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    apply(parser.parse_args().root)
