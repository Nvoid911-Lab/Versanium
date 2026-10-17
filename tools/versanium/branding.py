"""Change generated, user-facing product strings, never repository-wide identifiers."""
from pathlib import Path
import re

APP_NAME = 'Versanium'
CHANNEL = 'chrome/android/java/res_titanium_base/values/channel_constants.xml'
PRODUCT = 'chrome/app/theme/chromium/BRANDING'
# Restricted to text nodes of resource elements, not keys, attributes, paths or comments.
ELEMENT = re.compile(r'<(?P<tag>message|translation|string)\b[^>]*>.*?</(?P=tag)>', re.S)
KEEP = re.compile(r'Copyright|license|licence|attribution|https://github\.com/(?:jqssun/android-titanium|GrapheneOS/Vanadium|chromium/)', re.I)
TEXT_TOKEN = re.compile(r'https?://[^\s<>]+|Titanium Extension(?: for Android)?|Titanium Browser for Android|(?<![A-Za-z0-9_])Titanium(?![A-Za-z0-9_])')


def brand_resources(text):
    def element(match):
        source = match.group()
        if KEEP.search(source):
            return source  # Explicit upstream reference, credits, or legal text: B category.
        parts = re.split(r'(<[^>]*>)', source)
        for i in range(0, len(parts), 2):
            parts[i] = TEXT_TOKEN.sub(lambda token: APP_NAME if token.group() == 'Titanium' else token.group(), parts[i])
        return ''.join(parts)
    return ELEMENT.sub(element, text)


def resource_paths(repository):
    paths = set()
    for patch in (repository / 'vanadium/patches').glob('000[12]-*.patch'):
        paths.update(re.findall(r'^diff --git a/(\S+\.(?:grd|grdp|xtb)) b/', patch.read_text(), re.M))
    if not paths:
        raise RuntimeError('Reviewed Vanadium resource paths unavailable')
    return sorted(paths)


def text_edits(root, repository, paths=None):
    result = {}
    for relative in [CHANNEL, *(resource_paths(repository) if paths is None else paths)]:
        file = root / relative
        if not file.is_file():
            raise RuntimeError(f'Missing generated branding resource: {relative}')
        original = file.read_text()
        updated = brand_resources(original)
        if updated != original:
            result[file] = updated
    channel = result.get(root / CHANNEL, (root / CHANNEL).read_text())
    if not re.search(r'<string\s+name="app_name"[^>]*>Versanium</string>', channel):
        raise RuntimeError('Expected exactly the current app name in channel_constants')
    product = root / PRODUCT
    original = product.read_text()
    updated = original
    for key in ('PRODUCT_FULLNAME', 'PRODUCT_SHORTNAME'):
        updated, count = re.subn(r'^' + key + r'=[^\n]*$', key + '=' + APP_NAME, updated, flags=re.M)
        if count != 1:
            raise RuntimeError(f'Unexpected product branding key: {key}')
    result[product] = updated
    return result
