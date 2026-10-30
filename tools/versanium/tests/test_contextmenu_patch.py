"""Real fixed-source context-menu transform; no Chromium build or analysis."""
from pathlib import Path
import hashlib
import itertools
import re
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
REL='chrome/android/java/src/org/chromium/chrome/browser/contextmenu/ChromeContextMenuPopulator.java'
FIXED_SHA='f180a74b1d0e13e7c8f4e9c59d11b9b68944ab0ae0c3d0d3c5fc5a8810ec227f'
POST_SHA='89380eab2e93a7c1f47782fa966f993642c2407a13b842518f7204e230e720c5'
OLD=b'|| (TabUtils.isUsingDesktopUserAgent(mItemDelegate.getWebContents())\n                        && mParams.getSourceType() == MenuSourceType.LONG_PRESS));'
NEW=b'|| mParams.getSourceType() == MenuSourceType.LONG_PRESS);'


def validate(data):
    text=data.decode('utf-8')
    signature='    boolean shouldShowEmptySpaceContextMenu() {\n'
    if text.count(signature)!=1:raise AssertionError('Expected one context-menu method')
    method=text.split(signature,1)[1].split('\n    }',1)[0]
    actual=method.split('        return ',1)[1]
    expected='(mParams.getSourceType() == MenuSourceType.MOUSE\n                || mParams.getSourceType() == MenuSourceType.LONG_PRESS);'
    if actual!=expected:raise AssertionError('Changed context-menu semantics/constant expression')
    if 'true || TabUtils.isUsingDesktopUserAgent' in text:raise AssertionError('Constant expression returned')


def apply_contextmenu(root, repository):
    # Fixed156 skips the old (<156.0.8060.0) developer-menu command.
    commands=[l for l in (repository/'patch.sh').read_text().splitlines()
              if l.startswith('sed -i ') and 'TabUtils' in l and REL in l]
    if len(commands)!=1:raise AssertionError('Context-menu command coverage changed')
    target=root/REL;before=target.read_bytes()
    if before.count(OLD)!=1:raise AssertionError('Fixed context-menu source anchor changed')
    subprocess.run(['bash','-c',commands[0]],cwd=root,check=True)
    generated=target.read_bytes()
    if generated!=before.replace(OLD,NEW,1):raise AssertionError('Unrelated context-menu bytes changed')
    validate(generated)
    return generated


class ContextMenuTests(unittest.TestCase):
    def source(self):
        candidates=[Path('/tmp/versanium156/source')/REL,Path('/tmp/versanium-contextmenu-fixed156.java')]
        p=next((p for p in candidates if p.is_file()),None)
        if p is None:self.skipTest('Pinned Chromium source not locally available')
        data=p.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),FIXED_SHA)
        return data
    def test_fresh_generator_exact_bytes_and_idempotence(self):
        data=self.source()
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);p=r/REL;p.parent.mkdir(parents=True);p.write_bytes(data)
            generated=apply_contextmenu(r,ROOT)
            self.assertEqual(hashlib.sha256(generated).hexdigest(),POST_SHA)
            # The sed itself is idempotent; fresh-source harness refuses old input reuse.
            command=next(l for l in (ROOT/'patch.sh').read_text().splitlines() if l.startswith('sed -i ') and 'TabUtils' in l and REL in l)
            subprocess.run(['bash','-c',command],cwd=r,check=True)
            self.assertEqual(p.read_bytes(),generated)
    def test_reject_constant_and_upstream_semantics_regression(self):
        data=self.source()
        for mutated in (data,data.replace(OLD,b'|| ((true || TabUtils.isUsingDesktopUserAgent(mItemDelegate.getWebContents()))\n                        && mParams.getSourceType() == MenuSourceType.LONG_PRESS));'),data.replace(OLD,b'|| (false && mParams.getSourceType() == MenuSourceType.LONG_PRESS));')):
            with self.subTest():
                with self.assertRaises(AssertionError):validate(mutated)
    def test_reject_missing_long_press_condition(self):
        data=self.source().replace(OLD,NEW,1)
        with self.assertRaises(AssertionError):validate(data.replace(b'|| mParams.getSourceType() == MenuSourceType.LONG_PRESS',b''))
    def test_short_circuit_semantics(self):
        # desktopUA is already unevaluated under true||, for every combination.
        for mouse,long_press,desktop in itertools.product((False,True),repeat=3):
            calls=[]
            def ua():calls.append('UA');return desktop
            old=mouse or ((True or ua()) and long_press)
            new=mouse or long_press
            self.assertEqual(old,new);self.assertEqual(calls,[])

if __name__=='__main__':unittest.main(verbosity=2)
