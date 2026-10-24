"""Add fixed-label origin records to existing fullscreen requests, not new decisions."""
from pathlib import Path

BASE_PATH='chrome/android/java/src/org/chromium/chrome/browser/fullscreen/FullscreenHtmlApiHandlerBase.java'

def transform(source):
    def replace(old,new):
        nonlocal source
        if source.count(old)!=1:raise RuntimeError('Fullscreen origin anchor changed: '+old[:100])
        source=source.replace(old,new,1)
    def event(label,tab='(mTabInFullscreen != null ? mTabInFullscreen : mTab)'):
        return ('org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController.'
                'reportFullscreenExitOrigin(mActivity, '+tab+', "origin6_'+label+'");')
    # All inserted calls sit in already selected branches; no flags/state getter
    # or permission/eligibility function is queried again for diagnosis.
    replace('        public void onMultiWindowModeChanged(boolean isInMultiWindowMode) {',
            '        public void onMultiWindowModeChanged(boolean isInMultiWindowMode) {\n            '+event('multiwindow_callback'))
    replace('''                    && !ChromeFeatureList.sEnableExclusiveAccessManager.isEnabled()) {
                // Fix for''',
            '''                    && !ChromeFeatureList.sEnableExclusiveAccessManager.isEnabled()) {
                '''+event('multiwindow_feature_branch')+'''
                // Fix for''')
    replace('''                    mFullscreenManagerDelegate.onExitFullscreen(mTab);
                }
            }
            mIsInMultiWindowMode''',
            '''                    '''+event('multiwindow_guard_passed')+'''
                    mFullscreenManagerDelegate.onExitFullscreen(mTab);
                }
            }
            mIsInMultiWindowMode''')
    replace('''                    protected void onObservingDifferentTab(@Nullable Tab tab) {
                        mTab = tab;''',
            '''                    protected void onObservingDifferentTab(@Nullable Tab tab) {
                        '''+event('tab_provider_change')+'''
                        mTab = tab;''')
    replace('''                        // Clean up any fullscreen state that might impact other tabs.
                        mFullscreenManagerDelegate.onExitFullscreen(null);''',
            '''                        // Clean up any fullscreen state that might impact other tabs.
                        '''+event('tab_hidden','tab')+'''
                        mFullscreenManagerDelegate.onExitFullscreen(null);''')
    replace('''                        if (tab == mTabInFullscreen) {
                            mFullscreenManagerDelegate.onExitFullscreen(tab);''',
            '''                        if (tab == mTabInFullscreen) {
                            '''+event('tab_destroyed','tab')+'''
                            mFullscreenManagerDelegate.onExitFullscreen(tab);''')
    replace('''                        if (!navigation.isSameDocument() && tab == modelSelector.getCurrentTab()) {
                            mFullscreenManagerDelegate.onExitFullscreen(null);''',
            '''                        if (!navigation.isSameDocument() && tab == modelSelector.getCurrentTab()) {
                            '''+event('primary_navigation','tab')+'''
                            mFullscreenManagerDelegate.onExitFullscreen(null);''')
    replace('''        if (tab != mTab && tab != mTabInFullscreen) return;
        setEnterFullscreenRunnable(tab, null);''',
            '''        if (tab != mTab && tab != mTabInFullscreen) return;
        '''+event('accepted_on_exit','tab')+'''
        setEnterFullscreenRunnable(tab, null);''')
    replace('''            for (FullscreenManager.Observer observer : mObservers) {
                observer.onExitFullscreen(tab);''',
            '''            for (FullscreenManager.Observer observer : mObservers) {
                '''+event('notify_exit_observer','tab')+'''
                observer.onExitFullscreen(tab);''')
    replace('''    public void exitPersistentFullscreenMode() {
        // Return''',
            '''    public void exitPersistentFullscreenMode() {
        '''+event('exit_persistent_entry')+'''
        // Return''')
    replace('''            mFullscreenManagerDelegate.onExitFullscreen(null);
        } else if (newState == ActivityState.DESTROYED) {''',
            '''            '''+event('activity_stopped_request')+'''
            mFullscreenManagerDelegate.onExitFullscreen(null);
        } else if (newState == ActivityState.DESTROYED) {''')
    return source

def apply(root):
    path=Path(root)/BASE_PATH
    original=path.read_text()
    path.write_text(transform(original))
