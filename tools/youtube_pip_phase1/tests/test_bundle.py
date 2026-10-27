"""Build-free boundary checks; these do not establish Chromium Java correctness."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest

BUNDLE=Path(__file__).resolve().parents[1]

class BundleTest(unittest.TestCase):
    def fixture(self, root):
        fixture=BUNDLE/'tests/fixtures'
        pins=json.loads((fixture/'pins.json').read_text())
        for name,entry in pins['files'].items():
            data=gzip.decompress((fixture/name).read_bytes())
            self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'])
            p=root/entry['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        data=gzip.decompress((fixture/'vanadium-selected.patch.gz').read_bytes())
        self.assertEqual(hashlib.sha256(data).hexdigest(),pins['selected_vanadium_sha256'])
        subprocess.run(['git','apply','--whitespace=nowarn','-'],input=data,cwd=root,check=True)
        activity='chrome/android/java/src/org/chromium/chrome/browser/app/ChromeActivity.java'
        zoom=(BUNDLE.parent/'environment_zoom/chromium.patch').read_bytes().replace(b'\r\n',b'\n')
        subprocess.run(['git','apply','--include='+activity,'-'],input=zoom,cwd=root,check=True)
        return root/activity

    def installer(self):
        spec=importlib.util.spec_from_file_location('phase1_apply',BUNDLE/'apply.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module

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

    def test_fixed156_vanadium_zoom_patch_composition(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);activity=self.fixture(root)
            before=activity.read_text(encoding='utf-8')
            self.installer().apply(root)
            after=activity.read_text(encoding='utf-8')
            for call in ('EnvironmentZoom.refreshAll();','EnvironmentZoom.flushPendingWrites();'):
                def context(text):
                    lines=text.splitlines();i=next(i for i,x in enumerate(lines) if call in x)
                    return lines[i-1:i+3]
                self.assertEqual(context(before),context(after))
                self.assertEqual(after.count(call),1)
            gni=(root/'chrome/android/chrome_java_sources.gni').read_text(encoding='utf-8')
            for name in ('Controller','Policy'):
                self.assertEqual(gni.count('VersaniumYouTubePictureInPicture'+name+'.java'),1)
            self.assertIn('ManualCallbackDelayer.java',gni)
            with self.assertRaises(RuntimeError):self.installer().apply(root)

    def test_anchor_drift_has_no_partial_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);activity=self.fixture(root)
            gni=root/'chrome/android/chrome_java_sources.gni'
            gni.write_bytes(gni.read_bytes().replace(b'FullscreenVideoPictureInPictureController.java',
                                                     b'ChangedFullscreenVideoPictureInPictureController.java'))
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(subprocess.CalledProcessError):self.installer().apply(root)
            self.assertEqual(before,{p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_hook_order_and_forbidden_surfaces(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root);self.installer().apply(root)
            base=root/'chrome/android/java/src/org/chromium/chrome/browser'
            video=(base/'media/FullscreenVideoPictureInPictureController.java').read_text(encoding='utf-8')
            start=video.index('final boolean hadPipSession')
            section=video[start:video.index('// If we just entered PiP',start)]
            self.assertLess(section.index('updateAutoPictureInPictureStatusIfNeeded()'),
                            section.index('mVersaniumPip.handleDismiss'))
            self.assertIn('hadPipSession && mVersaniumPip.requiresUpstreamDismiss(reason)',section)
            entry=video[video.index('final long generation'):video.index('public void onStashReported')]
            self.assertLess(entry.index('beginEntry('),entry.index('enterPictureInPictureMode('))
            self.assertEqual(entry.count('rollback(generation)'),2)
            self.assertIn('mVersaniumPip.guardDelayed(this::unpauseVideoDuringUnstashIfNeeded)',video)
            activity=(base/'app/ChromeActivity.java').read_text(encoding='utf-8')
            start=activity.index('public void onPictureInPictureModeChanged')
            end=activity.index('mLastPictureInPictureModeForTesting = false',start)
            callback=activity[start:end]
            self.assertLess(callback.index('wasInPictureInPictureForMinimizedCustomTabs()) return'),
                            callback.index('onVersaniumFrameworkEntered'))
            self.assertLess(callback.index('shouldEnterPip()) return'),
                            callback.index('onVersaniumFrameworkEntered'))
            self.assertLess(callback.index('onVersaniumFrameworkExiting'),
                            callback.index('mActorPipController.onFrameworkExitedPictureInPicture'))
            html=(base/'fullscreen/FullscreenHtmlApiHandlerBase.java').read_text(encoding='utf-8')
            self.assertIn('else if (newState == ActivityState.DESTROYED)',html)
            self.assertIn('ApplicationStatus.unregisterActivityStateListener(this)',html)
            targets=[line for line in (BUNDLE/'chromium.patch').read_text().splitlines() if line.startswith('+++ ')]
            self.assertEqual(len(targets),4)
            self.assertFalse(any('components/' in t or 'content/' in t for t in targets))

if __name__=='__main__':
    unittest.main()
