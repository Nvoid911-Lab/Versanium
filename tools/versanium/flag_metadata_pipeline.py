"""Reproduce Run9 flag-metadata stages without normalizing or reformatting JSON."""
import json
import re

EXPIRY_FLAGS = (
    "align-wakeups",
    "android-bottom-bar",
    "cct-open-in-browser-button-if-allowed-by-embedder",
    "darken-websites-checkbox-in-themes-setting",
    "enable-accessibility-sequential-focus",
    "enforce-incognito-isolation",
    "inline-pdf-v2",
    "jump-start-omnibox",
    "lock-controls-on-tablets-v2",
    "offline-auto-fetch",
    "use-fullscreen-insets-api",
)

CANDIDATE_FLAGS = (
    "versanium-youtube-background-candidate",
    "versanium-youtube-diagnostics",
    "versanium-youtube-pip-candidate",
)


def apply_expiry_overrides(data):
    """Mirror patch.sh's ordered sed ranges while retaining every other byte."""
    for name in EXPIRY_FLAGS:
        start_marker = ('"name": "' + name + '"').encode("ascii")
        start = data.find(start_marker)
        if start < 0 or data.find(start_marker, start + 1) >= 0:
            raise RuntimeError("Expected one expiry flag record: " + name)
        end = data.find(b"}", start)
        if end < 0:
            raise RuntimeError("Unterminated expiry flag record: " + name)
        record = data[start:end]
        pattern = rb'"expiry_milestone": [0-9]+'
        if len(re.findall(pattern, record)) != 1:
            raise RuntimeError("Expected one numeric expiry in: " + name)
        updated = re.sub(pattern, b'"expiry_milestone": -1', record, count=1)
        data = data[:start] + updated + data[end:]
    return data


def apply_candidate_entries(data):
    """Mirror apply_youtube_candidates.py insertion order and formatting exactly."""
    text = data.decode("utf-8")
    text, count = re.subn(
        r'  \{\n    "name": "versanium-youtube-diagnostics",.*?\n  \},\n',
        "",
        text,
        flags=re.S,
    )
    if count not in (0, 1):
        raise RuntimeError("Unexpected pre-existing diagnostics records")
    for name in CANDIDATE_FLAGS:
        record = {
            "name": name,
            "owners": ["298596960+Nvoid911@users.noreply.github.com"],
            "expiry_milestone": 157,
        }
        entry = "  " + json.dumps(record, indent=2).replace("\n", "\n  ") + ",\n"
        matches = list(re.finditer(r'  \{\n    "name": "([^"\n]+)"', text))
        following = next((match for match in matches if match.group(1) > name), None)
        position = following.start() if following else text.rfind("]")
        if position < 0:
            raise RuntimeError("Malformed flag metadata array")
        text = text[:position] + entry + text[position:]
    return text.encode("utf-8")


def reproduce(head_data):
    expiry = apply_expiry_overrides(head_data)
    return expiry, apply_candidate_entries(expiry)


def patch_sh_flags(patch_text):
    match = re.search(r'for flag in ((?:"[^"]+" ?)+); do\n\s+sed -i .*flag-metadata\.json', patch_text)
    if not match:
        raise RuntimeError("patch.sh expiry loop changed")
    return tuple(re.findall(r'"([^"]+)"', match.group(1)))
