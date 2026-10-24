"""Scoped EAM native diagnosis only; fixed156 anchors, no eligibility reruns."""
from pathlib import Path

ROOT = 'chrome/browser/ui/'
CONTEXT = ROOT+'exclusive_access/exclusive_access_context.h'
ANDROID = ROOT+'android/exclusive_access/exclusive_access_context_android'
MANAGER = ROOT+'android/exclusive_access/exclusive_access_manager_android.cc'
FULLSCREEN = ROOT+'exclusive_access/fullscreen_controller.cc'
JAVA = 'chrome/android/java/src/org/chromium/chrome/browser/ui/ExclusiveAccessContext.java'
SCOPE = ROOT+'exclusive_access/versanium_fullscreen_diagnostic_scope.h'
SCOPE_TEXT = '''// Diagnostic-only synchronous depth; no owner pointers or asynchronous attribution.
#ifndef CHROME_BROWSER_UI_EXCLUSIVE_ACCESS_VERSANIUM_FULLSCREEN_DIAGNOSTIC_SCOPE_H_
#define CHROME_BROWSER_UI_EXCLUSIVE_ACCESS_VERSANIUM_FULLSCREEN_DIAGNOSTIC_SCOPE_H_
namespace versanium_fullscreen_diagnostic {
inline thread_local int depth = 0;
class Scope {
 public:
  Scope() { ++depth; }
  ~Scope() { --depth; }
  Scope(const Scope&) = delete;
  Scope& operator=(const Scope&) = delete;
};
}  // namespace versanium_fullscreen_diagnostic
#endif
'''

def transform(name, text):
    if ('versanium_fullscreen_diagnostic' in text or 'reportNativeFullscreenDiagnostic' in text
            or 'ReportNativeFullscreenDiagnostic' in text):
        raise RuntimeError('Native diagnostic already applied: '+name)
    def one(before,after):
        nonlocal text
        if text.count(before)!=1:raise RuntimeError('Native diagnostic anchor mismatch: '+name+' '+before[:70])
        text=text.replace(before,after,1)
    if name==CONTEXT:
        one('  virtual ~ExclusiveAccessContext() = default;', '''  virtual ~ExclusiveAccessContext() = default;

  // Diagnostic hook: fixed stage numbers, no permission/eligibility queries.
  // Desktop contexts keep the default no-op; Android applies all privacy gates.
  virtual void ReportNativeFullscreenDiagnostic(content::WebContents*,
                                               int, int) {}
''')
    elif name==ANDROID+'.h':
        one('  void ExitFullscreen() override;', '''  void ExitFullscreen() override;
  void ReportNativeFullscreenDiagnostic(content::WebContents* contents,
                                       int stage, int depth) override;''')
    elif name==ANDROID+'.cc':
        one('#include "base/notreached.h"', '#include "base/notreached.h"\n#include "base/command_line.h"\n#include "content/public/browser/browser_thread.h"\n#include "content/public/browser/browser_context.h"\n#include "url/gurl.h"')
        one('void ExclusiveAccessContextAndroid::ExitFullscreen() {', '''void ExclusiveAccessContextAndroid::ReportNativeFullscreenDiagnostic(
    content::WebContents* contents, int stage, int depth) {
  // No raw owner retained; synchronous JNI only on the existing UI thread.
  if (!content::BrowserThread::CurrentlyOn(content::BrowserThread::UI) ||
      !contents || java_context_.is_null()) return;
  if (!base::CommandLine::ForCurrentProcess()->HasSwitch(
          "versanium-youtube-diagnostics")) return;
  auto* browser_context = contents->GetBrowserContext();
  if (!browser_context || browser_context->ShutdownStarted() ||
      browser_context->IsOffTheRecord()) return;
  const GURL& url = contents->GetLastCommittedURL();
  if (!url.SchemeIs("https") ||
      !(url.host() == "youtube.com" || url.host() == "www.youtube.com" ||
        url.host() == "m.youtube.com")) return;
  JNIEnv* env = jni_zero::AttachCurrentThread();
  Java_ExclusiveAccessContext_reportNativeFullscreenDiagnostic(
      env, java_context_, contents->GetJavaWebContents(), stage, depth);
}

void ExclusiveAccessContextAndroid::ExitFullscreen() {''')
    elif name in (MANAGER,FULLSCREEN):
        anchor='#include "content/public/browser/web_contents.h"'
        one(anchor,anchor+'\n#include "'+SCOPE+'"')
        if name==MANAGER:
            one('  eam_.fullscreen_controller()->ExitFullscreenModeForTab(wc);', '''  versanium_fullscreen_diagnostic::Scope diagnostic_scope;
  eac_->ReportNativeFullscreenDiagnostic(
      wc, 1, versanium_fullscreen_diagnostic::depth);
  eam_.fullscreen_controller()->ExitFullscreenModeForTab(wc);''')
        else:
            start='void FullscreenController::ExitFullscreenModeForTab(WebContents* web_contents) {'
            end='\nvoid FullscreenController::'
            pos=text.index(start);stop=text.index(end,pos+len(start))
            body=text[pos:stop]
            def body_one(a,b):
                nonlocal body
                if body.count(a)!=1:raise RuntimeError('Fullscreen branch anchor drift')
                body=body.replace(a,b,1)
            call=lambda stage:'diagnose('+str(stage)+');'
            body_one(start,start+'''
  versanium_fullscreen_diagnostic::Scope diagnostic_scope;
  auto diagnostic_weak = weak_ptr_factory_.GetWeakPtr();
  auto diagnostic_contents_weak = web_contents ? web_contents->GetWeakPtr()
                                             : base::WeakPtr<content::WebContents>();
  auto diagnose = [diagnostic_weak, diagnostic_contents_weak](int stage) {
    if (!diagnostic_weak || !diagnostic_contents_weak) return;
    diagnostic_weak->exclusive_access_manager()->context()->ReportNativeFullscreenDiagnostic(
        diagnostic_contents_weak.get(), stage, versanium_fullscreen_diagnostic::depth);
  };
  diagnose(2);''')
            body_one('if (MaybeToggleFullscreenWithinTab(web_contents, false)) {','if (MaybeToggleFullscreenWithinTab(web_contents, false)) {\n    '+call(3))
            body_one('web_contents != exclusive_access_tab()) {','web_contents != exclusive_access_tab()) {\n    '+call(4))
            body_one('if (!exclusive_access_context->IsFullscreen()) {','if (!exclusive_access_context->IsFullscreen()) {\n    '+call(5))
            body_one('if (IsFullscreenCausedByTab()) {','if (IsFullscreenCausedByTab()) {\n    '+call(6))
            body_one('  NotifyTabExclusiveAccessLost();','  '+call(7)+'\n  NotifyTabExclusiveAccessLost();')
            text=text[:pos]+body+text[stop:]
            one('''    WebContents* web_contents = exclusive_access_tab();
    SetTabWithExclusiveAccess(nullptr);''','''    WebContents* web_contents = exclusive_access_tab();
    exclusive_access_manager()->context()->ReportNativeFullscreenDiagnostic(
        web_contents, 8, versanium_fullscreen_diagnostic::depth);
    SetTabWithExclusiveAccess(nullptr);''')
            one('''  auto weak_ptr = weak_ptr_factory_.GetWeakPtr();
#if BUILDFLAG(IS_MAC) || BUILDFLAG(IS_ANDROID)''','''  auto weak_ptr = weak_ptr_factory_.GetWeakPtr();
  auto* diagnostic_contents = exclusive_access_tab();
  base::WeakPtr<content::WebContents> diagnostic_contents_weak =
      diagnostic_contents ? diagnostic_contents->GetWeakPtr()
                          : base::WeakPtr<content::WebContents>();
#if BUILDFLAG(IS_MAC) || BUILDFLAG(IS_ANDROID)''')
            one('  exclusive_access_manager()->context()->ExitFullscreen();','''  if (diagnostic_contents_weak) {
    exclusive_access_manager()->context()->ReportNativeFullscreenDiagnostic(
        diagnostic_contents_weak.get(), 9, versanium_fullscreen_diagnostic::depth);
  }
  exclusive_access_manager()->context()->ExitFullscreen();''')
    elif name==JAVA:
        one('''    @CalledByNative
    public void exitFullscreenModeForTab() {''','''    // Called synchronously with the actual native request WebContents, not a guessed tab.
    @CalledByNative
    void reportNativeFullscreenDiagnostic(
            @Nullable WebContents contents, int stage, int depth) {
        Tab tab = mActiveTab;
        if (mNativeExclusiveAccessContextAndroid == 0 || contents == null
                || contents.isDestroyed() || tab == null || tab.isDestroyed()
                || tab.isOffTheRecord() || tab.getWebContents() != contents
                || depth < 0 || depth > 64) return;
        String label;
        switch (stage) {
            case 1: label = "eam_jni_entry"; break;
            case 2: label = "controller_entry"; break;
            case 3: label = "within_tab_return"; break;
            case 4: label = "window_or_tab_return"; break;
            case 5: label = "context_not_fullscreen_return"; break;
            case 6: label = "tab_caused_exit"; break;
            case 7: label = "browser_state_loss"; break;
            case 8: label = "notify_access_lost"; break;
            case 9: label = "context_exit_call"; break;
            default: return;
        }
        org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController
                .reportFullscreenDelegateOrigin(tab, "origin6_native_" + label + "_d" + depth);
    }

    @CalledByNative
    public void exitFullscreenModeForTab() {''')
        one('''        if (mActiveTab != null) {
            mFullscreenManager.onExitFullscreen(mActiveTab);''','''        if (mActiveTab != null) {
            org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController
                    .reportFullscreenDelegateOrigin(mActiveTab, "origin6_native_context_to_base");
            mFullscreenManager.onExitFullscreen(mActiveTab);''')
    elif name==ROOT+'exclusive_access/BUILD.gn':
        one('    "fullscreen_controller.h",','    "fullscreen_controller.h",\n    "versanium_fullscreen_diagnostic_scope.h",')
    else:raise RuntimeError('Unexpected native diagnostic path: '+name)
    return text

FILES=(CONTEXT,ANDROID+'.h',ANDROID+'.cc',MANAGER,FULLSCREEN,JAVA,ROOT+'exclusive_access/BUILD.gn')
def apply(root):
    root=Path(root)
    if (root/SCOPE).exists():raise RuntimeError('Native diagnostic scope header already exists')
    changed={n:transform(n,(root/n).read_text()) for n in FILES}
    for n,text in changed.items():(root/n).write_text(text)
    (root/SCOPE).write_text(SCOPE_TEXT)
