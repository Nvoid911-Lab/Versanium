"""Apply the reviewed zoom patch to the generated Chromium tree, never the repository itself."""
from pathlib import Path
import os
import shutil
import subprocess


def apply(root, bundle):
    patch = bundle / 'chromium.patch'
    # Check all upstream anchors before touching any tracked Chromium file.
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=root, check=True)
    files = {}
    for source in (bundle / 'java').rglob('*.java'):
        relative = source.relative_to(bundle / 'java')
        if relative.parts[:4] == ('org', 'chromium', 'content_public', 'browser'):
            target = root / 'content/public/android/java/src' / relative
        else:
            target = root / 'components/browser_ui/accessibility/android/java/src' / relative
        files[target] = source
    for source in (bundle / 'res').rglob('*.xml'):
        files[root / 'components/browser_ui/accessibility/android/java/res'
              / source.relative_to(bundle / 'res')] = source
    for target in files:
        if target.exists():
            raise RuntimeError(f'Refusing to replace an existing overlay: {target.relative_to(root)}')
    subprocess.run(['git', 'apply', str(patch)], cwd=root, check=True)
    for target, source in files.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    print('Environment zoom patch applied; Chromium compilation still required')


if __name__ == '__main__':
    apply(Path.cwd(), Path(os.environ['SCRIPT_DIR']) / 'tools/environment_zoom')
