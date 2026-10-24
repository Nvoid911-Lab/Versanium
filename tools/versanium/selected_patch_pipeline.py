"""Replay reviewed single-line patch.sh commands for the selected manifest files.
Only scratch trees may be passed. No full patch/build script is executed.
"""
from pathlib import Path
import subprocess

FILES = ('content/browser/web_contents/web_contents_impl.cc',
         'chrome/android/java/AndroidManifest.xml',
         'chrome/android/java/src/org/chromium/chrome/browser/ChromeTabbedActivity.java')

def commands(text):
    result=[]
    for line in text.splitlines():
        if not line.startswith('sed -i ') or not any(name in line for name in FILES):continue
        # Fixed156 takes the else branch of the version_lt152 NTP block.
        if 'import org.chromium.chrome.browser.url_constants.UrlConstantResolverFactory;' in line:continue
        if 'if (isTabNtp \\&\\& !currentTab.isNativePage())' in line:continue
        result.append(line)
    if len(result)!=6:raise RuntimeError('Selected patch.sh command coverage changed: '+str(len(result)))
    return result

def apply(root,repository):
    selected=commands((repository/'patch.sh').read_text())
    for line in selected:
        subprocess.run(['bash','-eu','-c',line],cwd=root,check=True)
    return selected
