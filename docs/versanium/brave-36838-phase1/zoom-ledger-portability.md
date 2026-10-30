# Zoom protection ledger portability — 2026-10-28 JST

State after ledger validation: **READY_FOR_36838_BUILD_PREP_ENVIRONMENT_SETUP**.
This fixes only the repository-side ledger blocker. **Fresh build environment/JDK
blocker remains unresolved. No GN / compile / APK / device verification.**
This supersedes prior raw-checkout Zoom gate claims in historical Phase 1 reports;
the overall BUILD_PREP is not complete and no build is authorized.

## Read-only cause confirmation

Start/reviewed commit: `ec620a1d69244f2e9eb405d3d21ecd9a3d0a8752`.
Branch: `next-test/156-zoom-transfer-pip`; PR5 Open/Draft/unmerged, body unchanged.
Comparison was captured before repository edits for all24 old ledger entries.
[Full machine-readable evidence](zoom-ledger-migration-evidence.json) includes exact
hashes, check-attr output, git ls-files --eol, root attributes, protected Git tree
and complete Phase 1 Git tree.

All24 old ledger hashes equal the CRLF representation. All24 Git blobs equal the
LF representation and differ from the old ledger. On this Windows checkout, all24
raw hashes equal the old ledger; this differs from the reported Linux checkout's
24 raw mismatches. Read-only in-memory normalization proves that line endings
fully account for all24 differences; no product files were rewritten. Old evidence
is consistent with CRLF working-tree collection, not Git blob collection. The old
external ad hoc scripts also explicitly hashed Path.read_bytes().

The root .gitattributes contains only a whitespace rule for the Zoom patch:
`tools/environment_zoom/chromium.patch whitespace=-blank-at-eol`.
For all24 paths, `git check-attr text eol working-tree-encoding -- <path>` returns
unspecified for each attribute; git ls-files --eol reports i/lf w/crlf.
Effective core.autocrlf=true originates from the bundled Git system gitconfig;
core.eol and core.attributesfile have no explicit values. No attributes/config
are changed by this task. LF/CRLF columns below are diagnostic comparisons only,
never accepted alternative hashes in the new gate.

| path | old ledger SHA256 | Git blob SHA256 | worktree raw SHA256 | LF SHA256 | CRLF SHA256 | attributes | conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tools/apply_environment_zoom.py` | `a20a2570644c9bf4920dd9eb0eca0a4480ad431b892c7d1457f3c08ffaa246ed` | `94ab563bf3d7427aa09a3f0867718c40fd5be2ec1bc980a6a21782884ca23702` | `a20a2570644c9bf4920dd9eb0eca0a4480ad431b892c7d1457f3c08ffaa246ed` | `94ab563bf3d7427aa09a3f0867718c40fd5be2ec1bc980a6a21782884ca23702` | `a20a2570644c9bf4920dd9eb0eca0a4480ad431b892c7d1457f3c08ffaa246ed` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/check_environment_zoom_revision.py` | `27dd051618857fb6f2fed87197f2088384b7f024ae8228e0bb96bb0cbe3cf6e5` | `4bd78829e604a73d9aaa80bdf05de6e85ada762ef8d60e99d3169fac77f26f3a` | `27dd051618857fb6f2fed87197f2088384b7f024ae8228e0bb96bb0cbe3cf6e5` | `4bd78829e604a73d9aaa80bdf05de6e85ada762ef8d60e99d3169fac77f26f3a` | `27dd051618857fb6f2fed87197f2088384b7f024ae8228e0bb96bb0cbe3cf6e5` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/chromium.patch` | `413d1d9d6bb1dcc6823853a1c6eb513cb463389d7093effe73004ccb99416357` | `4e000a4e12a7a5c07e1078c49f94a7759b897891db0d11b7ae3570fce3caa839` | `413d1d9d6bb1dcc6823853a1c6eb513cb463389d7093effe73004ccb99416357` | `4e000a4e12a7a5c07e1078c49f94a7759b897891db0d11b7ae3570fce3caa839` | `413d1d9d6bb1dcc6823853a1c6eb513cb463389d7093effe73004ccb99416357` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/components/browser_ui/accessibility/EnvironmentZoomSettings.java` | `5c5a1f6a2295a9593dffcf7d535e0b340fdea20aa237993fb7dbb11fb19a870d` | `4ed4b716da8dc6e46042eb113590993c131f7458795c2392a67079031de0b343` | `5c5a1f6a2295a9593dffcf7d535e0b340fdea20aa237993fb7dbb11fb19a870d` | `4ed4b716da8dc6e46042eb113590993c131f7458795c2392a67079031de0b343` | `5c5a1f6a2295a9593dffcf7d535e0b340fdea20aa237993fb7dbb11fb19a870d` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/components/browser_ui/accessibility/EnvironmentZoomTransfer.java` | `78e43ed5d5acf4d2d3760a984aec66d8a4b620e32901afca09b42a9fedc74b9c` | `2ded03bb7cb2faed74e592df1840e80b522542f5ad61cf3cc1ed245cf8fe6224` | `78e43ed5d5acf4d2d3760a984aec66d8a4b620e32901afca09b42a9fedc74b9c` | `2ded03bb7cb2faed74e592df1840e80b522542f5ad61cf3cc1ed245cf8fe6224` | `78e43ed5d5acf4d2d3760a984aec66d8a4b620e32901afca09b42a9fedc74b9c` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoom.java` | `03a90e4025e47840656ba3f5ecbb6ce3427b8b2f83d8d0a00456994fb405431d` | `ba8ea5c809ec73525caaae2e9e3c00db198471d2102382b349ad95402f6afaf0` | `03a90e4025e47840656ba3f5ecbb6ce3427b8b2f83d8d0a00456994fb405431d` | `ba8ea5c809ec73525caaae2e9e3c00db198471d2102382b349ad95402f6afaf0` | `03a90e4025e47840656ba3f5ecbb6ce3427b8b2f83d8d0a00456994fb405431d` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomBackup.java` | `43a839821c8cb958b68eef6a556008eee6d3d6772a9f369c7cdcd37408de8e0e` | `4f2695a9a4dfdbf19eeea12103b71231dc325ff797c62ce57fef633a373132d2` | `43a839821c8cb958b68eef6a556008eee6d3d6772a9f369c7cdcd37408de8e0e` | `4f2695a9a4dfdbf19eeea12103b71231dc325ff797c62ce57fef633a373132d2` | `43a839821c8cb958b68eef6a556008eee6d3d6772a9f369c7cdcd37408de8e0e` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomPersistence.java` | `56ad51ab5d568c9d971f6c40479d725eca90bcaa7725a16c371759ae5c8e1153` | `2434ef8f3bdaf39fd6f5693fc77fa06c1f0d141581e187223602f9f160b61d98` | `56ad51ab5d568c9d971f6c40479d725eca90bcaa7725a16c371759ae5c8e1153` | `2434ef8f3bdaf39fd6f5693fc77fa06c1f0d141581e187223602f9f160b61d98` | `56ad51ab5d568c9d971f6c40479d725eca90bcaa7725a16c371759ae5c8e1153` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomPolicy.java` | `1c5bfb31fe70c6301a5b8cb3648fde2e466fc25610516d0bcccf94539a976b04` | `5e7ea3f850171728a383717457cba0a64f1f4cd0f74c2cf6df11576ee7deb471` | `1c5bfb31fe70c6301a5b8cb3648fde2e466fc25610516d0bcccf94539a976b04` | `5e7ea3f850171728a383717457cba0a64f1f4cd0f74c2cf6df11576ee7deb471` | `1c5bfb31fe70c6301a5b8cb3648fde2e466fc25610516d0bcccf94539a976b04` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/res/values-ja/titanium_zoom_strings.xml` | `361032366c51eb796dd15bd27bdf90aa9bc4d70bf8ed65668fb6a6835fcf7c14` | `764c0e474713d1e62d876c20dc4a4ac40138076bc7a980ad2a28278602d23738` | `361032366c51eb796dd15bd27bdf90aa9bc4d70bf8ed65668fb6a6835fcf7c14` | `764c0e474713d1e62d876c20dc4a4ac40138076bc7a980ad2a28278602d23738` | `361032366c51eb796dd15bd27bdf90aa9bc4d70bf8ed65668fb6a6835fcf7c14` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/res/values/titanium_zoom_strings.xml` | `3985ee43d899255841dffc50f4eea400a68d25d2ff143aca9ba02626739ee61c` | `3544d5f499a0b105078e225f3b3dc1dcba4b75ec75cc316969e5af074e124270` | `3985ee43d899255841dffc50f4eea400a68d25d2ff143aca9ba02626739ee61c` | `3544d5f499a0b105078e225f3b3dc1dcba4b75ec75cc316969e5af074e124270` | `3985ee43d899255841dffc50f4eea400a68d25d2ff143aca9ba02626739ee61c` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/EnvironmentZoomBackupTest.java` | `c9212c917cbdc60eeb9c43e7203b4ece59791a5eb6e0412a6ad5009afae29ae9` | `c7a36345633d3f7f63c853358d92279265bdfbb05b118a58afb43a8e9f224425` | `c9212c917cbdc60eeb9c43e7203b4ece59791a5eb6e0412a6ad5009afae29ae9` | `c7a36345633d3f7f63c853358d92279265bdfbb05b118a58afb43a8e9f224425` | `c9212c917cbdc60eeb9c43e7203b4ece59791a5eb6e0412a6ad5009afae29ae9` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/EnvironmentZoomBridgeTest.java` | `97a0b36ce191547dc9b7874affd95aec86449121363555c4cae6edb0c72fb4a3` | `f045a434850629e720c5b6b5850cc4e4fa62df18aecab2037b13de38b93d628d` | `97a0b36ce191547dc9b7874affd95aec86449121363555c4cae6edb0c72fb4a3` | `f045a434850629e720c5b6b5850cc4e4fa62df18aecab2037b13de38b93d628d` | `97a0b36ce191547dc9b7874affd95aec86449121363555c4cae6edb0c72fb4a3` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/EnvironmentZoomPersistenceTest.java` | `ed988f61401da0a8c1fd38983bb6120929c919da4e3b2c6d4734182be187297f` | `ed11f01f3c394a0ff8425d50c192b9bdcf583315926b01abe18cb3c00a5dd379` | `ed988f61401da0a8c1fd38983bb6120929c919da4e3b2c6d4734182be187297f` | `ed11f01f3c394a0ff8425d50c192b9bdcf583315926b01abe18cb3c00a5dd379` | `ed988f61401da0a8c1fd38983bb6120929c919da4e3b2c6d4734182be187297f` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/EnvironmentZoomPolicyTest.java` | `0fafb8d1ad017bdb5a1fbef0df065b1c5797f71cc55c4d8027d317038f230d5d` | `67704503d9d522dbdc04543c7d7a572488371d42ec779c50f1d230dcbc355143` | `0fafb8d1ad017bdb5a1fbef0df065b1c5797f71cc55c4d8027d317038f230d5d` | `67704503d9d522dbdc04543c7d7a572488371d42ec779c50f1d230dcbc355143` | `0fafb8d1ad017bdb5a1fbef0df065b1c5797f71cc55c4d8027d317038f230d5d` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/ParseJavaSources.java` | `c80f07e6a41e2bfd1dc30d81558a059a8e7de18dd481216e3b6c5a9ef1350fe8` | `1c8084440c1661481479c6d6313690adc11b5b6ff802023b2f6a756623c8a159` | `c80f07e6a41e2bfd1dc30d81558a059a8e7de18dd481216e3b6c5a9ef1350fe8` | `1c8084440c1661481479c6d6313690adc11b5b6ff802023b2f6a756623c8a159` | `c80f07e6a41e2bfd1dc30d81558a059a8e7de18dd481216e3b6c5a9ef1350fe8` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_android_api.py` | `ff446018912c5d6d7b61cd06c380ed20a63b4047a3e75d0a57d690ef08b4f5db` | `ee4c7771c3e439eab02de3aaef565bb79d3275420374777b82952fff089bc380` | `ff446018912c5d6d7b61cd06c380ed20a63b4047a3e75d0a57d690ef08b4f5db` | `ee4c7771c3e439eab02de3aaef565bb79d3275420374777b82952fff089bc380` | `ff446018912c5d6d7b61cd06c380ed20a63b4047a3e75d0a57d690ef08b4f5db` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_build_pin.py` | `356f8e6b2ee5508ed60d40e3bc6f95f3eb53d9c413ecea217051be8401ae61df` | `b7291d070c47f9b830083becd05a0ff836e29f25b03c1a5f6b1255832c7ef65d` | `356f8e6b2ee5508ed60d40e3bc6f95f3eb53d9c413ecea217051be8401ae61df` | `b7291d070c47f9b830083becd05a0ff836e29f25b03c1a5f6b1255832c7ef65d` | `356f8e6b2ee5508ed60d40e3bc6f95f3eb53d9c413ecea217051be8401ae61df` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_jni_abi.py` | `6482bfc9a24c500913335e2f441563826d7b627656fb7a245284b78d3fe7f5ba` | `d7429859e3c1800881ef1cc46ccef932fbc3b15f3ced290877b90d5ac42f0843` | `6482bfc9a24c500913335e2f441563826d7b627656fb7a245284b78d3fe7f5ba` | `d7429859e3c1800881ef1cc46ccef932fbc3b15f3ced290877b90d5ac42f0843` | `6482bfc9a24c500913335e2f441563826d7b627656fb7a245284b78d3fe7f5ba` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_patch.py` | `07b66c7e541aa31c47382b7b02c9ddf2b2131ab0929dcd15db8bc3ac63f9e5dd` | `09a670d4f4bd6c5cd1ac314a996d2f8286e2d848010bf980b982f9217de584cf` | `07b66c7e541aa31c47382b7b02c9ddf2b2131ab0929dcd15db8bc3ac63f9e5dd` | `09a670d4f4bd6c5cd1ac314a996d2f8286e2d848010bf980b982f9217de584cf` | `07b66c7e541aa31c47382b7b02c9ddf2b2131ab0929dcd15db8bc3ac63f9e5dd` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_settings_resources.py` | `f0570f5aa0d3bef1911e93e13471ab9c84a6bd4821913095f3985a6bf88d671c` | `bb29037b8a4eea87e5ceb7c2765dcf1cbd2538b08e358c76c92ca8f03602288c` | `f0570f5aa0d3bef1911e93e13471ab9c84a6bd4821913095f3985a6bf88d671c` | `bb29037b8a4eea87e5ceb7c2765dcf1cbd2538b08e358c76c92ca8f03602288c` | `f0570f5aa0d3bef1911e93e13471ab9c84a6bd4821913095f3985a6bf88d671c` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/check_video_fullscreen.py` | `7861e99546a8041d6e94dd1990fef9799bbd9422c68e9b5fe196285fd7769e7e` | `6f24c892c10122f889c516add0bc200091fbaefc54d509552a27f2ad6735659b` | `7861e99546a8041d6e94dd1990fef9799bbd9422c68e9b5fe196285fd7769e7e` | `6f24c892c10122f889c516add0bc200091fbaefc54d509552a27f2ad6735659b` | `7861e99546a8041d6e94dd1990fef9799bbd9422c68e9b5fe196285fd7769e7e` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/fixtures/legacy-zoom-v1.properties` | `b474a3c75417fdd95c687b29788bc0eda0cd86fbcfe6a168613ded1d674900e7` | `36cb6e7afb81f339c64dce9334d81fb2f3f4ebb67ebd05c21a8db4a5e2b48ea2` | `b474a3c75417fdd95c687b29788bc0eda0cd86fbcfe6a168613ded1d674900e7` | `36cb6e7afb81f339c64dce9334d81fb2f3f4ebb67ebd05c21a8db4a5e2b48ea2` | `b474a3c75417fdd95c687b29788bc0eda0cd86fbcfe6a168613ded1d674900e7` | text/eol/encoding unspecified | old = CRLF; blob = LF |
| `tools/environment_zoom/tests/run_local_tests.py` | `e067f39c3353ebe2d4e75cb24d38a400fea4517968c8ddc8985cb4128f4815ff` | `2f016e8585613c61af4ec0c2ae9a5fecf05004a143e05911d18b4aaadee4829c` | `e067f39c3353ebe2d4e75cb24d38a400fea4517968c8ddc8985cb4128f4815ff` | `2f016e8585613c61af4ec0c2ae9a5fecf05004a143e05911d18b4aaadee4829c` | `e067f39c3353ebe2d4e75cb24d38a400fea4517968c8ddc8985cb4128f4815ff` | text/eol/encoding unspecified | old = CRLF; blob = LF |

## Canonical contract and migration

The only canonical bytes are **Git blob content bytes at an explicitly resolved
commit**, SHA256 hashed without decoding, clean/smudge filters or EOL conversion.
Git object IDs are not substituted for the SHA256 of blob content.
The reviewed baseline is pinned by full40-character commit SHA in
[zoom-protection-ledger.json](zoom-protection-ledger.json).

Version2 schema fields: schema_version=2, hash_algorithm=sha256,
content_source=git-blob, ref=reviewed commit, files=the exact reviewed24 paths/hashes.
The existing flat zoom-before.json is preserved byte-for-byte as legacy raw-byte
evidence; candidate/terminal validation snapshots remain historical and unchanged.
The new versioned ledger is authoritative for future Zoom protection gates.
Old-to-new hash mapping is retained in the comparison table and evidence JSON.
Do not run historical worktree-hash scripts as portable BUILD_PREP gates.

Previously no repository-owned Zoom protection generator/validator existed:
zoom-before.json and report snapshots were collected/checked by workspace-only
ad hoc Python scripts (final_validation.py / verify_terminal.py and follow-ups).
Those scripts are not reused. A standalone repository tool now supplies both
generation and validation; no Zoom product or Phase 1 implementation/test changes.

## Validator / generator

From repository root, with existing Python3 (no JDK or build setup):

```sh
python3 -B tools/zoom_protection.py validate --ref HEAD
python3 -B tools/zoom_protection.py validate --ref <explicit-target-commit>
python3 -B tools/zoom_protection.py generate --ref <reviewed-commit>
python3 -B -m unittest discover -s tools/tests -p test_zoom_protection.py -v
```

Generate prints a candidate ledger; it never rewrites a ledger or auto-accepts a
new baseline. A baseline change needs its own review. Validate accepts --repo and
--ledger overrides but requires --ref. It first verifies the ledger against its
pinned reviewed commit, then checks the explicit target ref against the ledger.

The scope is independently fixed in the validator: two Zoom entry scripts plus
every tree entry beneath tools/environment_zoom. The reviewed24 paths must match
exactly. Missing/extra ledger or tree paths, duplicate JSON keys, missing objects,
unknown refs, non-regular100644 modes (including symlink/gitlink), schema/source/
algorithm errors and any SHA256 mismatch fail closed. No text-normalization
allowlist, fallback to working tree, warning-only mismatch or disabled exact gate.

Blob gate and worktree gate are separate: matching HEAD blobs with modified local
files produce blob_gate=PASS, worktree_gate=FAIL, dirty=true plus status records.
CLI exit2 signals dirty state; exit1 signals blob/schema/Git failure; exit0 requires
matching blobs and clean worktree. Untracked files are reported too. The blob API
can independently validate a known commit even while the checkout is dirty;
a dirty worktree must still be resolved before proceeding.

## Tests and invariants

**18 ledger-specific unittest methods PASS.** They cover actual disposable LF/CRLF clones
(verify each of24 raw files has the expected line endings), one-byte committed
content change, worktree-only modification plus CLI exit2, missing path/blob,
wrong hash/target ref/reviewed ref, core.autocrlf true/input/false and attributes
eol=lf/crlf changes, duplicate/missing/extra entries, unexpected protected tree
path, symlink/submodule/executable modes and invalid schema/digest. Synthetic
repositories only; no protected Zoom tests/product code are executed or edited.

The ledger24 path set is identical to the historical set. Protection of the
actual Zoom pre/post Git content and unchanged Phase1 tree is checked separately;
the migration evidence carries initial tree IDs and full canonical SHA256 hashes.
Retired34 paths remain absent. No old generators are restored.

No Zoom Java/patch/resources/tests/export/import/phone/DeX/persistence/backup/
numeric policy changes. No Phase1 Controller/Policy/patch/tests, PiP behavior,
#33522/#39765/manual toolbar/script injector/C++/JNI/pin changes.
No GN, Chromium compile, javac setup, Android downloads, depot_tools, fresh Chromium
checkout, build.sh, full patch.sh, APK, Actions, saved Run9, merge/tag/release/
Production operation, force push or PR body edit.
