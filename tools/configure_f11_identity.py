"""Configure only the generated F11 build tree, before GN generation."""

from pathlib import Path
import re
import argparse


PACKAGE = "io.github.nvoid911.titanium.f11test"
VERSANIUM_TEST_PACKAGE = "io.github.nvoid911.versanium.test"
APP_NAME = "Versanium"


def configure(root, versanium_test=False):
    package = VERSANIUM_TEST_PACKAGE if versanium_test else PACKAGE
    args_path = root / "out/Default/args.gn"
    strings_path = root / "chrome/android/java/res_titanium_base/values/channel_constants.xml"
    manifest_path = root / "chrome/android/java/AndroidManifest.xml"
    args = args_path.read_text()
    strings = strings_path.read_text()
    manifest = manifest_path.read_text()

    # Chromium uses manifest_package for provider authorities, signature
    # permissions and task affinity. Fail rather than silently accept a new
    # hard-coded authority or shared UID that could prevent coexistence.
    authorities = re.findall(r'android:authorities="([^"]+)"', manifest)
    if not authorities or any(
        not value.strip().startswith("{{ manifest_package }}")
        for group in authorities for value in group.split(";")
    ):
        raise ValueError("Expected all Chrome provider authorities to use manifest_package")
    declared_permissions = re.findall(r'<permission(?:-group|-tree)?\b[^>]*android:name="([^"]+)"', manifest)
    affinities = re.findall(r'android:taskAffinity="([^"]*)"', manifest)
    for value in [*declared_permissions, *(v for v in affinities if v)]:
        if not re.match(r'^\{\{ manifest_package \}\}(?:\.|$)', value):
            raise ValueError("Expected custom permissions and nonempty task affinities to use manifest_package")
    if "android:sharedUserId" in manifest:
        raise ValueError("Unexpected shared UID in Chrome manifest")
    if '@string/app_name' not in manifest:
        raise ValueError("Expected Chrome manifest to use the app_name resource")

    args, count = re.subn(
        r'^chrome_public_manifest_package\s*=\s*"[^"]+"\s*$',
        f'chrome_public_manifest_package = "{package}"', args, flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Expected exactly one chrome_public_manifest_package setting")
    strings, count = re.subn(
        r'(<string\s+name="app_name"[^>]*>)[^<]*(</string>)',
        rf'\g<1>{APP_NAME}\g<2>', strings,
    )
    if count != 1:
        raise ValueError("Expected exactly one app_name resource")

    # Validate every input before writing either output. Base args.gn and the
    # checked-in resources remain untouched; only the Chromium tree changes.
    args_path.write_text(args)
    strings_path.write_text(strings)
    print(f"Generated test identity: {package} / {APP_NAME}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versanium-test", action="store_true", help="Isolate only the Versanium Test delivery")
    options = parser.parse_args()
    configure(Path.cwd(), versanium_test=options.versanium_test)
