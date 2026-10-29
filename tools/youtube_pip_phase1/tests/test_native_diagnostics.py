"""Fixed-source composition and safety invariants; NOT native compilation/device proof."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import test_bundle as bundle

BUNDLE = bundle.BUNDLE

BLOCK = re.compile(r'^// VSPIP_DIAGNOSTIC_BEGIN\n.*?^// VSPIP_DIAGNOSTIC_END\n', re.M | re.S)
NATIVE = BUNDLE/'tests/fixtures/native'
PINS = json.loads((NATIVE/'pins.json').read_text())

def native_files():
    return {e['path']: gzip.decompress((NATIVE/n).read_bytes()).decode()
            for n,e in PINS['files'].items()}

class NativeDiagnosticTest(unittest.TestCase):
    def compose(self, root):
        fixture = bundle.BundleTest()
        fixture.fixture(root)
        fixture.installer().apply(root)
        return {p:(root/p).read_text(encoding='utf-8') for p in native_files()}

    def test_exact_behavioral_source_restored_without_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            actual = self.compose(Path(d))
            for path, original in native_files().items():
                with self.subTest(path=path):
                    self.assertEqual(BLOCK.sub('', actual[path]), original)
                    self.assertEqual(actual[path].count('VSPIP_DIAGNOSTIC_BEGIN'),
                                     len(BLOCK.findall(actual[path])))
        patch=(BUNDLE/'native-diagnostics.patch').read_text()
        self.assertEqual(len(native_files()),9)
        self.assertFalse(any(s.startswith('-') and not s.startswith('---')
                             for s in patch.splitlines()))

    def test_sender_receiver_identifiers_and_transition_only_volume(self):
        with tempfile.TemporaryDirectory() as d:
            files=self.compose(Path(d))
            media=files['third_party/blink/renderer/core/html/media/html_media_element.cc']
            video=files['third_party/blink/renderer/core/html/media/html_video_element.cc']
            observer=files['content/browser/media/media_web_contents_observer.cc']
            self.assertIn('web_media_player_->GetPlayerId()',media)
            self.assertIn('GetDocument().Token().ToString()',media)
            self.assertIn('frame->GetLocalFrameToken().ToString()',media)
            self.assertIn('id.player_id',observer)
            self.assertIn('frame->GetFrameToken().ToString()',observer)
            self.assertIn('versanium_diagnostic_status_ != diagnostic_status ||',video)
            self.assertIn('versanium_diagnostic_player_ != diagnostic_player',video)
            start=video.index('"PIP_PERMISSION_PRODUCER"')
            self.assertIn('FastHasAttribute(html_names::kDisablepictureinpictureAttr)',video[start:start+220])
            self.assertLess(start,video.index('observer->OnMediaEffectivelyFullscreenChanged(status)'))
            start=observer.index('void MediaWebContentsObserver::OnMediaEffectivelyFullscreenChanged(')
            end=observer.index('void MediaWebContentsObserver::OnMediaPlaying()',start)
            method=observer[start:end]
            self.assertLess(method.index('picture_in_picture_allowed_in_fullscreen_ = false'),
                            method.index('"PIP_PERMISSION_RECEIVED"'))
            self.assertIn('if (versanium_permission_changed)',method)

    def test_no_unsafe_getters_new_jni_private_payload_or_behavior_calls(self):
        with tempfile.TemporaryDirectory() as d:
            files=self.compose(Path(d))
            additions='\n'.join(block for text in files.values() for block in BLOCK.findall(text))
            for forbidden in ('IsPictureInPictureAllowedForFullscreenVideo(',
                              'GetDocumentToken(', 'GetMediaPlayerRemote(', 'RequestPause(',
                              'ExecuteJavaScript', 'SetAttribute(', 'RemoveAttribute(',
                              '.spec()', 'currentSrc(', 'printf(', 'std::cout', 'JNI_'):
                self.assertNotIn(forbidden,additions)
            self.assertIn('frame ? frame->GetFrameToken()',additions)
            self.assertIn('web_media_player_ ? web_media_player_->GetPlayerId() : -1',additions)
            self.assertIn('has_navigation_document ? GetDocument().Token().ToString() : "unknown"',additions)
            self.assertIn('if (!contents)',additions)
            self.assertIn('diagnostic_contents ? diagnostic_contents->GetPrimaryMainFrame() : nullptr',additions)
            self.assertNotRegex(additions,r'(?:contents|frame|player)\s*<<\s*(?:contents|frame|this)\b')
        policy=next((BUNDLE/'java').rglob('*Policy.java')).read_text()
        self.assertIn('String fullscreenPipAllowed = fullscreenVideo\n',policy)
        self.assertIn('? Boolean.toString(wc.isPictureInPictureAllowedForFullscreenVideo()) : "unknown"',policy)
        self.assertLess(policy.index('if (wc == null || wc.isDestroyed())'),policy.index('wc.getMainFrame()'))

    def test_first_pause_ingress_and_session_cause_result_order(self):
        with tempfile.TemporaryDirectory() as d:
            files=self.compose(Path(d))
            media=files['third_party/blink/renderer/core/html/media/html_media_element.cc']
            start=media.index('void HTMLMediaElement::PauseInternal(')
            method=media[start:media.index('void HTMLMediaElement::',start+10)]
            self.assertLess(method.index('"MEDIA_PAUSE_REQUEST"'),method.index('InvokeResourceSelectionAlgorithm()'))
            self.assertIn('if (!paused_)',method)
            self.assertIn('static_cast<int>(pause_reason)',method)
            controller=files['content/browser/media/session/media_session_controller.cc']
            self.assertLess(controller.index('source=MediaSessionController::OnSuspend'),
                            controller.index('->RequestPause(triggered_by_user)'))
            session=files['content/browser/media/session/media_session_impl.cc']
            self.assertIn('content_already_paused=',session)
            wmp=files['third_party/blink/renderer/platform/media/web_media_player_impl.cc']
            self.assertLess(wmp.index('source=WebMediaPlayerImpl::PauseVideoIfNeeded'),
                            wmp.index('client_->PausePlayback(pause_reason)'))

    def test_native_anchor_drift_has_no_partial_java_or_native_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture=bundle.BundleTest();fixture.fixture(root)
            path=root/'third_party/blink/renderer/core/html/media/html_media_element.cc'
            path.write_text(path.read_text().replace('void HTMLMediaElement::PauseInternal(',
                                                    'void HTMLMediaElement::UnexpectedPauseInternal('))
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(subprocess.CalledProcessError):fixture.installer().apply(root)
            self.assertEqual(before,{p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()})

if __name__=='__main__':
    unittest.main()
