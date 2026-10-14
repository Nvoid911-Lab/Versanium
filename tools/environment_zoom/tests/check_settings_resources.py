"""Check actual settings XML/layout contracts; this does NOT run an Android UI.

Supply the applied Chromium tree, pristine pinned source metadata/theme, and an
AndroidX Preference AAR. The AAR version is printed explicitly: a different
version cannot establish behavior of Chromium's pinned snapshot.
"""
import argparse
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ANDROID = '{http://schemas.android.com/apk/res/android}'
BASE = 'components/browser_ui/accessibility/android/java/'


def require_seekbar_views(preference, aar):
    # A local layout is mandatory; do not depend on the host's preference theme.
    layout = preference.get(ANDROID + 'layout')
    if not layout or not layout.startswith('@layout/'):
        raise ValueError('SeekBarPreference has no explicit layout; generic Preference layout lacks seekbar_value')
    root = ET.fromstring(aar.read('res/layout/' + layout[8:] + '.xml'))
    views = {element.get(ANDROID + 'id', '').split('/')[-1]: element.tag
             for element in root.iter()}
    if views.get('seekbar') != 'SeekBar' or views.get('seekbar_value') != 'TextView':
        raise ValueError('SeekBarPreference binding requires SeekBar/seekbar and TextView/seekbar_value')
    return layout


def run(applied, source, artifact, version):
    root = ET.parse(applied / (BASE + 'res/xml/accessibility_preferences.xml')).getroot()
    preferences = {p.get(ANDROID + 'key'): p for p in root}
    original = ET.parse(source / (BASE + 'res/xml/accessibility_preferences.xml')).getroot()
    for p in original:
        key = p.get(ANDROID + 'key')
        assert key in preferences and preferences[key].tag == p.tag, key
    info = (source / 'third_party/androidx/committed/libs/androidx_preference_preference/androidx_preference_preference.info').read_text()
    theme = ET.parse(source / 'components/browser_ui/settings/android/java/res/values/styles.xml').getroot()
    preference_theme = next(s for s in theme if s.get('name') == 'PreferenceTheme')
    assert not any(i.get('name') == 'seekBarPreferenceStyle' for i in preference_theme)
    with zipfile.ZipFile(artifact) as aar:
        for environment in ('mobile', 'dex'):
            pref = preferences['titanium_zoom_' + environment]
            assert pref.tag == 'androidx.preference.SeekBarPreference'
            assert pref.get(ANDROID + 'persistent') == 'false'
            layout = require_seekbar_views(pref, aar)
            assert '"res/layout/' + layout[8:] + '.xml"' in info
            # Regression: both pre-fix nodes must fail the same view contract.
            unfixed = ET.fromstring(ET.tostring(pref))
            del unfixed.attrib[ANDROID + 'layout']
            try:
                require_seekbar_views(unfixed, aar)
            except ValueError:
                pass
            else:
                raise AssertionError('Pre-fix preference was accepted')
            sites = preferences['titanium_zoom_' + environment + '_sites']
            assert sites.tag == 'Preference' and sites.get(ANDROID + 'persistent') == 'false'
        mode = preferences['titanium_zoom_display']
        assert mode.tag == 'androidx.preference.ListPreference'
        assert mode.get(ANDROID + 'persistent') == 'false'
    print('Settings resource contract PASS: two layouts, view types/IDs, negative pre-fix cases, existing keys, persistence flags')
    print('AAR supplied version:', version, 'SHA256:', hashlib.sha256(artifact.read_bytes()).hexdigest())
    print('Source/resource inspection only; fragment creation, Android theme resolution and actual device exception remain UNVERIFIED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--applied-tree', type=Path, required=True)
    parser.add_argument('--source-tree', type=Path, required=True)
    parser.add_argument('--preference-aar', type=Path, required=True)
    parser.add_argument('--aar-version', required=True)
    args = parser.parse_args()
    run(args.applied_tree, args.source_tree, args.preference_aar, args.aar_version)
