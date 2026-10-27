"""Build-free boundary checks; these do not establish Chromium Java correctness."""
from pathlib import Path
import unittest

BUNDLE=Path(__file__).resolve().parents[1]

class BundleTest(unittest.TestCase):
    def test_scope_and_provenance(self):
        java=list((BUNDLE/'java').rglob('*.java'))
        self.assertEqual(len(java),2)
        for p in java:
            text=p.read_text()
            self.assertIn('Copyright (c) 2026 The Brave Authors',text)
            self.assertIn('SPDX-License-Identifier: MPL-2.0',text)
            self.assertIn('4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2',text)
            self.assertNotIn('mediaSession.resume(',text)
            self.assertNotIn('evaluateJavaScript',text)
    def test_registered_sources(self):
        text=(BUNDLE/'chromium.patch').read_text()
        for p in (BUNDLE/'java').rglob('*.java'):
            self.assertIn(p.name,text)

if __name__=='__main__':
    unittest.main()
