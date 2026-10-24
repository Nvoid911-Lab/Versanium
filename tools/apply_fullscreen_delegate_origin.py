"""Add fixed-label Java forwarding diagnostics on top of AOrigin; no exit changes."""
from pathlib import Path

PREFIX = 'chrome/android/java/src/org/chromium/chrome/browser/'
WRAPPER = PREFIX + 'tab/TabWebContentsDelegateAndroidImpl.java'
ACTIVITY = PREFIX + 'app/tab_activity_glue/ActivityTabWebContentsDelegateAndroid.java'
CONTROLLER = PREFIX + 'media/FullscreenVideoPictureInPictureController.java'
CALL = ('org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController.'
        'reportFullscreenDelegateOrigin(mTab, "origin6_{}");')
# Labels are fixed at insertion time; no runtime page-derived text is accepted.
BRIDGE = '''    /** Fixed internal labels; no Activity inference or retained Tab/native pointer. */
    public static void reportFullscreenDelegateOrigin(@Nullable Tab originTab, String origin) {
        if (originTab == null || originTab.isDestroyed() || originTab.isOffTheRecord()) return;
        for (FullscreenVideoPictureInPictureController controller : sControllers.values()) {
            if (originTab == controller.mActivityTabProvider.get()) {
                controller.reportTitaniumYoutubePip(origin);
            }
        }
    }

'''

def transform(path, source):
    if path == WRAPPER:
        pairs = [('''    public void exitFullscreenModeForTab() {
        mDelegate.exitFullscreenModeForTab();''',
                  '''    public void exitFullscreenModeForTab() {
        ''' + CALL.format('webcontents_delegate_forward') + '''
        mDelegate.exitFullscreenModeForTab();''')]
    elif path == ACTIVITY:
        pairs = [
            ('                mExclusiveAccessManager.exitFullscreenModeForTab(mTab.getWebContents());',
             '                ' + CALL.format('activity_delegate_exclusive_forward') + '\n'
             '                mExclusiveAccessManager.exitFullscreenModeForTab(mTab.getWebContents());'),
            ('                mFullscreenManager.onExitFullscreen(mTab);',
             '                ' + CALL.format('activity_delegate_fullscreen_forward') + '\n'
             '                mFullscreenManager.onExitFullscreen(mTab);')]
    elif path == CONTROLLER:
        anchor = '    public static void reportFullscreenExitOrigin(Activity activity, @Nullable Tab originTab, String origin) {'
        pairs = [(anchor, BRIDGE + anchor)]
    else:
        raise RuntimeError('unexpected delegate diagnostic path')
    if 'reportFullscreenDelegateOrigin' in source:
        raise RuntimeError('delegate diagnostic already present')
    for before, after in pairs:
        if source.count(before) != 1:
            raise RuntimeError('delegate diagnostic anchor mismatch: ' + path)
        source = source.replace(before, after, 1)
    return source

def apply(root):
    root = Path(root)
    # Validate every input before writing any selected file in the fresh pipeline.
    changed = {p: transform(p, (root/p).read_text())
               for p in (WRAPPER, ACTIVITY, CONTROLLER)}
    for p, text in changed.items():
        (root/p).write_text(text)
