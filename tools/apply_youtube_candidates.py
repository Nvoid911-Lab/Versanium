"""Generate exact-anchor, top-document-only opt-in candidate hooks after zoom; fail closed."""
from pathlib import Path
import json,os,subprocess

def apply(root,repository):
    diagnostics=repository/'tools/youtube_pip/diagnostics.patch'
    execution=repository/'tools/youtube_pip/execution_scope.patch'
    subprocess.run(['git','apply','--check',str(execution)],cwd=root,check=True)
    subprocess.run(['git','apply','--check',str(diagnostics)],cwd=root,check=True)
    tab=root/'chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java'
    source=tab.read_text()
    marker='    void didFinishPageLoad(GURL url) {\n'
    show='    public void show(@TabSelectionType int type) {\n'
    hide='    public final void hide(@TabHidingType int type) {\n'
    for anchor in (marker,show,hide):
        if source.count(anchor)!=1:raise RuntimeError('YouTube TabImpl hook changed')
    script=(repository/'tools/youtube_pip/candidate.js').read_text()
    if not script.startswith('/*versanium-youtube-candidate-v1*/'):
        raise RuntimeError('Marked YouTube payload required for fail-closed native execution')
    method='''    private void applyVersaniumYoutubeCandidate(String stage) {
        if (isDestroyed() || mNativeTabAndroid == 0 || mProfile.getNativeBrowserContextPointer() == 0
                || getWebContents() == null || getWebContents().isDestroyed() || isOffTheRecord()
                || !org.chromium.base.CommandLine.isInitialized()) return;
        var command = org.chromium.base.CommandLine.getInstance();
        boolean pip = command.hasSwitch("versanium-youtube-pip-candidate");
        boolean background = command.hasSwitch("versanium-youtube-background-candidate");
        boolean diagnostics = command.hasSwitch("versanium-youtube-diagnostics");
        if (!pip && !background && !diagnostics) return;
        var contents = getWebContents();
        var address = contents.getLastCommittedUrl();
        if (!"https".equals(address.getScheme()) || !("youtube.com".equals(address.getHost())
                || "www.youtube.com".equals(address.getHost())
                || "m.youtube.com".equals(address.getHost()))) return;
        boolean mobile = EnvironmentZoom.isMobileDisplay(contents);
        String options = "{\\"mobile\\":" + mobile + ",\\"pip\\":" + pip
                + ",\\"background\\":" + background + ",\\\"diagnostics\\\":" + diagnostics + "}";
        String script = SCRIPT_LITERAL.replace("__VERSANIUM_OPTIONS__", options);
        if (diagnostics) Log.i("VersaniumYT", "stage=%s injection_requested mobile=%b", stage,mobile);
        contents.evaluateJavaScript(script, result -> {
            if (diagnostics && result != null && result.length() < 512) {
                try {
                    org.json.JSONObject record = new org.json.JSONObject(result);
                    Log.i("VersaniumYT", "stage=%s mobile=%b pip=%b background=%b backgroundApplied=%b adjusted=%b pause=%b visibility=%b paused=%b pauseMethod=%b pauseUserActivation=%b",
                            stage,
                            record.optBoolean("mobile"),record.optBoolean("pip"),record.optBoolean("background"),record.optBoolean("backgroundApplied"),
                            record.optBoolean("pipAdjusted"),record.optBoolean("pauseObserved"),
                            record.optBoolean("visibilityObserved"),record.optBoolean("paused"),
                            record.optBoolean("pauseMethodObserved"),record.optBoolean("pauseWithActivation"));
                } catch (org.json.JSONException error) {
                    Log.i("VersaniumYT", "diagnostic_invalid");
                }
            }
        });
        java.lang.ref.WeakReference<TabImpl> owner = new java.lang.ref.WeakReference<>(this);
        EnvironmentZoom.setEnvironmentListener(contents, () -> {
            TabImpl active = owner.get();
            if (active != null) active.applyVersaniumYoutubeCandidate("environment");
        });
    }
'''.replace('SCRIPT_LITERAL',json.dumps(script,ensure_ascii=True))
    source=source.replace(marker,method+'\n'+marker+'        applyVersaniumYoutubeCandidate("load");\n')
    source=source.replace(show,show+'        applyVersaniumYoutubeCandidate("show");\n')
    source=source.replace(hide,hide+'        applyVersaniumYoutubeCandidate("hide");\n')
    subprocess.run(['git','apply',str(execution)],cwd=root,check=True)
    subprocess.run(['git','apply',str(diagnostics)],cwd=root,check=True)
    tab.write_text(source)
    flags=root/'chrome/browser/about_flags.cc'
    text=flags.read_text();anchor='    {"versanium-youtube-diagnostics",'
    if text.count(anchor)!=1:raise RuntimeError('YouTube flags anchor changed')
    entries=''
    for name,label,description in [
        ('versanium-youtube-pip-candidate','Versanium YouTube PiP candidate','Normal top-level YouTube mobile tabs only: clear the HTML video PiP suppression attribute. Fullscreen and Android PiP permission remain required. Experimental; restart to disable.'),
        ('versanium-youtube-background-candidate','Versanium YouTube background candidate','Normal top-level YouTube mobile tabs only: hide document visibility changes from the site. Does not resume paused video or bypass autoplay. Experimental; restart to disable.')]:
        entries+='    {'+json.dumps(name)+', '+json.dumps(label)+', '+json.dumps(description)+', kOsAndroid, SINGLE_VALUE_TYPE('+json.dumps(name)+')},\n'
    flags.write_text(text.replace(anchor,entries+anchor))
    metadata=root/'chrome/browser/flag-metadata.json'
    import re
    metadata_text=metadata.read_text()
    metadata_text,count=re.subn(r'  \{\n    "name": "versanium-youtube-diagnostics",.*?\n  \},\n','',metadata_text,flags=re.S)
    if count!=1:raise RuntimeError('YouTube metadata anchor changed')
    for name in ('versanium-youtube-background-candidate','versanium-youtube-diagnostics','versanium-youtube-pip-candidate'):
        record={'name':name,'owners':['298596960+Nvoid911@users.noreply.github.com'],'expiry_milestone':157}
        entry='  '+json.dumps(record,indent=2).replace('\n','\n  ')+',\n'
        matches=list(re.finditer(r'  \{\n    "name": "([^"\n]+)"',metadata_text))
        following=next((m for m in matches if m.group(1)>name),None)
        position=following.start() if following else metadata_text.rfind(']')
        metadata_text=metadata_text[:position]+entry+metadata_text[position:]
    metadata.write_text(metadata_text)

if __name__=='__main__':
    from check_environment_zoom_revision import validate
    repository=Path(os.environ['SCRIPT_DIR']);root=Path.cwd();validate(root,repository);apply(root,repository)
