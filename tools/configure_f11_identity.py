"""Configure only the generated F11 build tree, before GN generation."""

from pathlib import Path
import re


PACKAGE = "io.github.nvoid911.titanium.f11test"
APP_NAME = "Versanium"


def configure(root):
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
    if "android:sharedUserId" in manifest:
        raise ValueError("Unexpected shared UID in Chrome manifest")
    if '@string/app_name' not in manifest:
        raise ValueError("Expected Chrome manifest to use the app_name resource")

    args, count = re.subn(
        r'^chrome_public_manifest_package\s*=\s*"[^"]+"\s*$',
        f'chrome_public_manifest_package = "{PACKAGE}"', args, flags=re.MULTILINE,
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
    print(f"F11 test identity: {PACKAGE} / {APP_NAME}")


if __name__ == "__main__":
    configure(Path.cwd())
