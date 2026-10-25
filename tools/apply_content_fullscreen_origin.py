"""Content ingress / persistent-false diagnostics only, via existing observer boundary."""
from pathlib import Path

WC='content/browser/web_contents/web_contents_impl'
OBS='content/public/browser/web_contents_observer.h'
PROXY='content/browser/android/web_contents_observer_proxy'
JPROXY='content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsObserverProxy.java'
JOBS='content/public/android/java/src/org/chromium/content_public/browser/WebContentsObserver.java'
RFH='content/browser/renderer_host/render_frame_host_impl.cc'
MEDIA='content/browser/media/media_web_contents_observer.cc'
PIP='chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'
FILES=(WC+'.h',WC+'.cc',OBS,PROXY+'.h',PROXY+'.cc',JPROXY,JOBS,RFH,MEDIA,PIP)
LABELS={1:'renderer_api_enter',2:'renderer_api_return',3:'dispatch_enter',4:'dispatch_return',
        5:'browser_exit_enter',6:'browser_exit_return',7:'navigation_exit',
        8:'security_downstream_exit',9:'security_opener_exit',10:'renderer_gone_exit',
        11:'persistent_false_no_player',12:'persistent_false_send_begin',13:'persistent_false_send_returned',
        14:'persistent_false_unchanged'}

def transform(name,text):
    if 'VersaniumContentFullscreenDiagnostic' in text or 'versaniumContentFullscreenDiagnostic' in text or 'content_diag_' in text:
        raise RuntimeError('Content diagnosis already applied: '+name)
    def one(old,new):
        nonlocal text
        if text.count(old)!=1:raise RuntimeError('Content diagnosis anchor changed: '+name+' '+old[:80])
        text=text.replace(old,new,1)
    if name==OBS:
        one('  // Invoked when the renderer process has toggled the tab into/out of', '''  // Fixed diagnostic enums only. Implementations must not mutate state or pump tasks.
  virtual void VersaniumContentFullscreenDiagnostic(int) {}

  // Invoked when the renderer process has toggled the tab into/out of''')
    elif name==WC+'.h':
        one('  void ExitFullscreen(bool will_cause_resize) override;', '''  void ReportVersaniumContentFullscreenDiagnostic(int stage);
  void ExitFullscreen(bool will_cause_resize) override;''')
    elif name==WC+'.cc':
        one('void WebContentsImpl::ExitFullscreenMode(bool will_cause_resize) {', '''void WebContentsImpl::ReportVersaniumContentFullscreenDiagnostic(int stage) {
#if BUILDFLAG(IS_ANDROID)
  // Scope only: never query fullscreen permission/eligibility here.
  if (!BrowserThread::CurrentlyOn(BrowserThread::UI) || IsBeingDestroyed() ||
      stage < 1 || stage > 14) return;
  if (!base::CommandLine::ForCurrentProcess()->HasSwitch(
          "versanium-youtube-diagnostics")) return;
  auto* context = GetBrowserContext();
  if (!context || context->ShutdownStarted() || context->IsOffTheRecord()) return;
  const auto* frame = GetPrimaryMainFrame();
  if (!frame || !frame->IsActive()) return;
  const GURL& url = GetLastCommittedURL();
  if (!url.SchemeIs("https") ||
      !(url.host() == "youtube.com" || url.host() == "www.youtube.com" ||
        url.host() == "m.youtube.com")) return;
  observers_.NotifyObservers(
      &WebContentsObserver::VersaniumContentFullscreenDiagnostic, stage);
#endif
}

void WebContentsImpl::ExitFullscreenMode(bool will_cause_resize) {
  auto content_diag_weak = weak_factory_.GetWeakPtr();
  ReportVersaniumContentFullscreenDiagnostic(3);
  if (!content_diag_weak) return;''')
        # Insert return marker at actual function end, after all original statements.
        start=text.index('void WebContentsImpl::ExitFullscreenMode(bool will_cause_resize) {')
        end=text.index('\n}\n',start)
        text=text[:end]+'''
  if (content_diag_weak) {
    content_diag_weak->ReportVersaniumContentFullscreenDiagnostic(4);
  }'''+text[end:]
        one('''void WebContentsImpl::ExitFullscreen(bool will_cause_resize) {''','''void WebContentsImpl::ExitFullscreen(bool will_cause_resize) {
  auto content_diag_weak = weak_factory_.GetWeakPtr();
  ReportVersaniumContentFullscreenDiagnostic(5);
  if (!content_diag_weak) return;''')
        one('''  ExitFullscreenMode(will_cause_resize);
}''','''  ExitFullscreenMode(will_cause_resize);
  if (content_diag_weak) {
    content_diag_weak->ReportVersaniumContentFullscreenDiagnostic(6);
  }
}''')
        one('''        fullscreen_contents->ExitFullscreen(true);''','''        fullscreen_contents->ReportVersaniumContentFullscreenDiagnostic(8);
        if (!fullscreen_contents) continue;
        fullscreen_contents->ExitFullscreen(true);''')
        one('''      opener->ExitFullscreen(true);''','''      opener->ReportVersaniumContentFullscreenDiagnostic(9);
      if (!opener) continue;
      opener->ExitFullscreen(true);''')
        one('''    base::WeakPtr<WebContentsImpl> weak_this = weak_factory_.GetWeakPtr();
    ExitFullscreen(false);''','''    base::WeakPtr<WebContentsImpl> weak_this = weak_factory_.GetWeakPtr();
    ReportVersaniumContentFullscreenDiagnostic(7);
    if (!weak_this) return;
    ExitFullscreen(false);''')
        one('''  if (IsFullscreen()) {
    ExitFullscreenMode(false);''','''  if (IsFullscreen()) {
    auto content_diag_weak = weak_factory_.GetWeakPtr();
    ReportVersaniumContentFullscreenDiagnostic(10);
    if (!content_diag_weak) return;
    ExitFullscreenMode(false);''')
        one('''  if (has_persistent_video_ == has_persistent_video) {
    return;''','''  if (has_persistent_video_ == has_persistent_video) {
    if (!has_persistent_video) ReportVersaniumContentFullscreenDiagnostic(14);
    return;''')
    elif name==RFH:
        one('#include "content/browser/renderer_host/render_frame_host_impl.h"', '#include "content/browser/renderer_host/render_frame_host_impl.h"\n#include "content/browser/web_contents/web_contents_impl.h"')
        start=text.index('void RenderFrameHostImpl::ExitFullscreen() {');end=text.index('\n}\n',start)
        body=text[start:end]
        old='  base::WeakPtr<RenderFrameHostImpl> weak_ptr = GetWeakPtr();'
        if body.count(old)!=1:raise RuntimeError('Renderer exit lifetime anchor changed')
        body=body.replace(old,old+'''
#if BUILDFLAG(IS_ANDROID)
  base::WeakPtr<WebContents> content_diag_contents;
  if (IsActive() && IsInPrimaryMainFrame()) {
    if (auto* contents = WebContentsImpl::FromRenderFrameHostImpl(this)) {
      content_diag_contents = contents->GetWeakPtr();
      contents->ReportVersaniumContentFullscreenDiagnostic(1);
    }
  }
  if (!weak_ptr) return;
#endif''')
        body+='''
#if BUILDFLAG(IS_ANDROID)
  if (weak_ptr && content_diag_contents && weak_ptr->IsActive() &&
      weak_ptr.get() == static_cast<WebContentsImpl*>(content_diag_contents.get())->GetPrimaryMainFrame()) {
    static_cast<WebContentsImpl*>(content_diag_contents.get())
        ->ReportVersaniumContentFullscreenDiagnostic(2);
  }
#endif'''
        text=text[:start]+body+text[end:]
    elif name==PROXY+'.h':
        one(' private:\n', ' private:\n  void VersaniumContentFullscreenDiagnostic(int stage) override;\n')
    elif name==PROXY+'.cc':
        one('void WebContentsObserverProxy::MediaStoppedPlaying(','''void WebContentsObserverProxy::VersaniumContentFullscreenDiagnostic(int stage) {
  // New callback uses nullable lookup; existing checked getters/CHECKs stay intact.
  if (!web_contents()) return;
  JNIEnv* env = AttachCurrentThread();
  auto obj = Java_WebContentsObserverProxy_getForVersaniumDiagnostic(env, web_contents());
  if (obj.is_null()) return;
  Java_WebContentsObserverProxy_versaniumContentFullscreenDiagnostic(env, obj, stage);
}

void WebContentsObserverProxy::MediaStoppedPlaying(''')
    elif name==JOBS:
        one('''    /**
     * Called when media stopped playing.''','''    /** Fixed internal diagnostic enum; no state mutation or page execution. */
    public void versaniumContentFullscreenDiagnostic(int stage) {}

    /**
     * Called when media stopped playing.''')
    elif name==JPROXY:
        one('''    @CalledByNative
    private static WebContentsObserverProxy getFromWebContents(''','''    @CalledByNative
    static @Nullable WebContentsObserverProxy getForVersaniumDiagnostic(
            @JniType("content::WebContents*") @Nullable WebContents webContents) {
        if (webContents == null) return null;
        @Nullable WebContentsObserverProxy proxy =
                ((WebContentsImpl) webContents).getWebContentsObserverProxy();
        return proxy != null && proxy.mNativeWebContentsObserverProxy != 0 ? proxy : null;
    }

    @CalledByNative
    private static WebContentsObserverProxy getFromWebContents(''')
        one('''    public void mediaStoppedPlaying(int id) {''','''    public void versaniumContentFullscreenDiagnostic(int stage) {
        if (mNativeWebContentsObserverProxy == 0) return;
        handleObserverCall();
        Iterator<WebContentsObserver> observersIterator = mObservers.iterator();
        for (; observersIterator.hasNext(); ) {
            observersIterator.next().versaniumContentFullscreenDiagnostic(stage);
        }
        finishObserverCall();
    }

    @Override
    @CalledByNative
    public void mediaStoppedPlaying(int id) {''')
    elif name==MEDIA:
        one('''  if (!fullscreen_player_)
    return;

  // The message''','''  if (!fullscreen_player_) {
    if (!value) web_contents_impl()->ReportVersaniumContentFullscreenDiagnostic(11);
    return;
  }
  base::WeakPtr<WebContents> content_diag_contents;
  if (!value) {
    content_diag_contents = web_contents_impl()->GetWeakPtr();
    web_contents_impl()->ReportVersaniumContentFullscreenDiagnostic(12);
    if (!content_diag_contents) return;
  }

  // The message''')
        one('''  GetMediaPlayerRemote(*fullscreen_player_)->SetPersistentState(value);''','''  GetMediaPlayerRemote(*fullscreen_player_)->SetPersistentState(value);
  if (!value && content_diag_contents) {
    static_cast<WebContentsImpl*>(content_diag_contents.get())
        ->ReportVersaniumContentFullscreenDiagnostic(13);
  }''')
    elif name==PIP:
        one('''                    if (!webContents.isDestroyed()) {
                        webContents.setHasPersistentVideo(false);
                    }''','''                    if (!webContents.isDestroyed()) {
                        if (webContents == getWebContents()) reportTitaniumYoutubePip("content_diag_cleanup_false_request");
                        webContents.setHasPersistentVideo(false);
                        if (!webContents.isDestroyed() && webContents == getWebContents()) reportTitaniumYoutubePip("content_diag_cleanup_false_returned");
                    }''')
        anchor='''        @Override
        public void mediaStartedPlaying(int id, boolean hasAudio, boolean hasVideo) {'''
        cases='\n'.join('                case '+str(n)+': label = "content_diag_'+s+'"; break;' for n,s in LABELS.items())
        one(anchor,'''        @Override
        public void versaniumContentFullscreenDiagnostic(int stage) {
            WebContents actual = super.getWebContents();
            if (actual == null || actual.isDestroyed() || actual != FullscreenVideoPictureInPictureController.this.getWebContents()) return;
            String label;
            switch (stage) {
'''+cases+'''
                default: return;
            }
            reportTitaniumYoutubePip(label);
        }

'''+anchor)
    else:raise RuntimeError('Unexpected content diagnostic path: '+name)
    return text

def apply(root):
    root=Path(root);changed={n:transform(n,(root/n).read_text()) for n in FILES}
    for n,s in changed.items():(root/n).write_text(s)
