"""Reject unknown Chromium/Vanadium inputs before applying the zoom integration patch."""
from pathlib import Path
import re
import subprocess

VANADIUM = '2ae4335402eabcc6e025f3400185fe25094d8521'
VERSION = '156.0.8078.47'
CHROMIUM = '1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def validate_repository(repository):
    if git(repository / 'vanadium', 'rev-parse', 'HEAD^{commit}') != VANADIUM:
        raise RuntimeError('Environment zoom requires the reviewed Vanadium commit')
    versions = re.findall(r'[0-9]+(?:\.[0-9]+){3}', (repository / 'vanadium/args.gn').read_text())
    if not versions or versions[0] != VERSION:
        raise RuntimeError('Vanadium version does not match the reviewed Chromium version')


def validate(chromium_root, repository):
    validate_repository(repository)
    fetched = git(chromium_root, 'rev-parse', f'chromium_{VERSION}^{{commit}}')
    if fetched != CHROMIUM:
        raise RuntimeError('Fetched Chromium tag does not match the reviewed commit')
    subprocess.run(['git', '-C', str(chromium_root), 'merge-base', '--is-ancestor',
                    CHROMIUM, 'HEAD'], check=True)
    print(f'Zoom inputs verified: Chromium {VERSION} / {CHROMIUM}; Vanadium {VANADIUM}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--chromium-root', type=Path)
    args = parser.parse_args()
    if args.chromium_root:
        validate(args.chromium_root, args.repository)
    else:
        validate_repository(args.repository)
        print('Reviewed Vanadium revision and Chromium version verified')
