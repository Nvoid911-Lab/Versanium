"""Source-level coexistence check. Supply pinned Chromium manifest after Vanadium hunks.
This compares manifest-derived identifiers; it does not merge/compile an APK.
"""
from pathlib import Path
import argparse,re,sys,tempfile
sys.dont_write_bytecode=True
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'tools'))
import configure_f11_identity as identity

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest',type=Path,required=True)
options=parser.parse_args()
manifest=options.manifest.read_text()
authorities=[v.strip() for group in re.findall(r'android:authorities="([^"]+)"',manifest) for v in group.split(';')]
permissions=re.findall(r'<permission(?:-group|-tree)?\b[^>]*android:name="([^"]+)"',manifest)
affinities=[v for v in re.findall(r'android:taskAffinity="([^"]*)"',manifest) if v]
assert authorities and permissions and affinities
for label,values in [('authorities',authorities),('custom permissions',permissions),('nonempty task affinities',affinities)]:
    assert all(re.match(r'^\{\{ manifest_package \}\}(?:\.|$)',v) for v in values),(label,values)
    old={v.replace('{{ manifest_package }}',identity.PACKAGE) for v in values}
    new={v.replace('{{ manifest_package }}',identity.VERSANIUM_TEST_PACKAGE) for v in values}
    assert old.isdisjoint(new),(label,old&new)
    print(f'{label}: {len(values)} package-derived identifiers; old/new sets disjoint')
assert 'android:sharedUserId' not in manifest
assert 'package="{{ manifest_package }}"' in manifest
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    args=root/'out/Default/args.gn';args.parent.mkdir(parents=True);args.write_bytes((REPO/'args.gn').read_bytes())
    strings=root/'chrome/android/java/res_titanium_base/values/channel_constants.xml';strings.parent.mkdir(parents=True)
    strings.write_text('<resources><string name="app_name">Versanium</string></resources>')
    destination=root/'chrome/android/java/AndroidManifest.xml';destination.write_text(manifest)
    identity.configure(root,versanium_test=True)
    assert 'chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args.read_text()
    assert destination.read_text()==manifest
    identity.configure(root)
    assert 'chrome_public_manifest_package = "io.github.nvoid911.titanium.f11test"' in args.read_text()
print('Pinned patched manifest + generated GN identity selection PASS; empty task affinities disable affinity, absent affinities inherit the distinct app package')
