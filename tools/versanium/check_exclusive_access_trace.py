"""Fixed156 source audit only: not a runtime stack, native compile or host check."""
from pathlib import Path
import argparse
import urllib.request
from check_external_fullscreen_trace import PIN, check
FILES = {'chrome/android/java/src/org/chromium/chrome/browser/ui/ExclusiveAccessManager.java': ('6dbe3eb0375b56d5cf3914c022d5424cbd0657712ba39ada4e7c4b3c5ed4d51e', ['.exitFullscreenModeForTab(mExclusiveAccessManagerAndroidNativePointer, webContents);', 'mFullscreenManager.setFullscreenManagerDelegate(']), 'chrome/android/java/src/org/chromium/chrome/browser/ui/ExclusiveAccessContext.java': ('031998b9e84ca80a67741194b2f6ead447677a3115425c4ce293a6ee0ea75415', ['mFullscreenManager.onExitFullscreen(mActiveTab);']), 'chrome/browser/ui/android/exclusive_access/exclusive_access_manager_android.cc': ('a9ea784edfbed8af5dfaed15168571a492d25f3ab21a677152d3eb754dcc8706', ['eam_.fullscreen_controller()->ExitFullscreenModeForTab(wc);']), 'chrome/browser/ui/android/exclusive_access/exclusive_access_manager_android.h': ('334fd5f3e7a3903a7d3ce78e81cf745b2b06591187892608be43fbe6592acc42', ['ExitFullscreenModeForTab(']), 'chrome/browser/ui/android/exclusive_access/exclusive_access_context_android.cc': ('61abd2cccc3bdfd7c49ef24221e39c066f0b8fcc03d72fa8f48830ebdc136f35', ['Java_ExclusiveAccessContext_exitFullscreenModeForTab(env, java_context_);']), 'chrome/browser/ui/exclusive_access/fullscreen_controller.cc': ('5b0036a49883b06a2cdd3b7515744f1307e214cc8a35baebc829acd291bfd1a9', ['SetTabWithExclusiveAccess(nullptr);', 'web_contents->ExitFullscreen(will_cause_resize);', 'NotifyTabExclusiveAccessLost();', 'exclusive_access_manager()->context()->ExitFullscreen();']), 'chrome/browser/ui/android/exclusive_access/BUILD.gn': ('ae23b678569062fb6770ac04cd37a4d664286a4eb0e65ab0a1726ea16b0f1c7a', ['source_set("exclusive_access")', '"exclusive_access_manager_android.cc",', '"//chrome/android:jni_headers",']), 'chrome/browser/ui/exclusive_access/BUILD.gn': ('75f090c1e5d401a102d3357a4f1cbe9ed130f899177a698369ada2928dd547f6', ['source_set("exclusive_access")', '"fullscreen_controller.cc",']), 'content/browser/renderer_host/render_widget_host_view_android.cc': ('042663d78a4d8799386d5a86f9e911ecef9f4a584c56a7ca3b87406ae8fc16d6', ['// Picture-in-Picture requires fullscreen, and stays in fullscreen.', 'pending_screen_state_.is_fullscreen = is_fullscreen;'])}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-tree',type=Path,help='optional pristine fixed-source snapshot')
    a=p.parse_args()
    for name,(digest,edges) in FILES.items():
        if a.source_tree:
            data=(a.source_tree/name).read_bytes()
        else:
            with urllib.request.urlopen(f'https://raw.githubusercontent.com/chromium/chromium/{PIN}/{name}',timeout=60) as r:
                data=r.read()
        check(data,digest,edges)
        try:check(data+b'\n',digest,edges)
        except ValueError:pass
        else:raise AssertionError('drift accepted')
        print('fixed source/edge + drift rejection PASS:',name)
    print('9 files PASS; initial requester, native compilation and device fix NOT established')
if __name__=='__main__':main()
