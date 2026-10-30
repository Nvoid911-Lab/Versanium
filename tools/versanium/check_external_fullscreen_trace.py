"""Fixed-source edge audit, NOT a compiler or proof of the device's caller."""
import hashlib
import urllib.request

PIN = '1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775'
JAVA = 'chrome/android/java/src/org/chromium/chrome/browser/'
FILES = {
    JAVA + 'TabbedModeTabDelegateFactory.java': (
        'e3bd1fa27f3acb357c72f055046928024b3cad1bf13e6f56a96df4f508bb4db7',
        ['return new ActivityTabWebContentsDelegateAndroid(']),
    JAVA + 'tab/TabWebContentsDelegateAndroidImpl.java': (
        'c2c49994544fe08b30a751b8930567d68a84560703d91c87e4a401d61f142c92',
        ['public void exitFullscreenModeForTab() {\n        mDelegate.exitFullscreenModeForTab();']),
    JAVA + 'app/tab_activity_glue/ActivityTabWebContentsDelegateAndroid.java': (
        '76e8e619408d0ec0af592870a12b257a95b7121452019303757a25b3ff9078cc',
        ['mExclusiveAccessManager.exitFullscreenModeForTab(mTab.getWebContents());',
         'mFullscreenManager.onExitFullscreen(mTab);']),
    'components/embedder_support/android/delegate/web_contents_delegate_android.cc': (
        'dece00a67b4585483a6a354cde49b5a34816a03b2aa594ee89249b3d165d4b10',
        ['Java_WebContentsDelegateAndroid_exitFullscreenModeForTab(env, obj);']),
    'content/browser/web_contents/web_contents_impl.cc': (
        'e551b400ae68665f06ce6f00807728763192866024be92e1507370d0db0a4199',
        ['delegate_->ExitFullscreenModeForTab(this);', 'ExitFullscreenMode(will_cause_resize);']),
    'content/browser/renderer_host/render_frame_host_impl.cc': (
        '79ad8104360b34a5a1ca953e3cc3a6c73b1463db3de11ce787264170bd3a1d9e',
        ['delegate_->ExitFullscreenMode(/*will_cause_resize=*/true);']),
}

def check(data, digest, edges):
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('fixed-source bytes mismatch')
    for edge in edges:
        if edge.encode() not in data:
            raise ValueError('missing call edge: ' + edge)

if __name__ == '__main__':
    for path, (digest, edges) in FILES.items():
        with urllib.request.urlopen(
                f'https://raw.githubusercontent.com/chromium/chromium/{PIN}/{path}',
                timeout=60) as response:
            data = response.read()
        check(data, digest, edges)
        try:
            check(data + b'\n', digest, edges)
        except ValueError:
            pass
        else:
            raise AssertionError('drift accepted')
        print('fixed source + call edge PASS:', path)
    print('6 fixed files PASS; runtime caller and compilation NOT verified')
