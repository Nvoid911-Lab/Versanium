# Versanium Test のpackage分離（2026-10-18）

従来のVersanium Test APKはTitanium F11 Testと同じpackageだったため、別アプリとして共存できなかった。今回の変更は migration/versanium のTest配送だけを分離する。

| 対象 | package |
|---|---|
| 既存Titanium F11 Test／従来F11既定値 | `io.github.nvoid911.titanium.f11test`（変更なし） |
| Versanium Test | `io.github.nvoid911.versanium.test`（今回分離） |

表示名は **Versanium**。実Versaniumアイコン・Adaptive・themed/monochromeは変更なし。新規アプリなのでTitanium F11 Testのデータ・デフォルトブラウザ設定を引き継がない設計であり、既存アプリの更新にはならない。既に生成済みの旧APKのpackageは変わらないため、旧APKをこの分離版としてインストールしないこと。

## 選択経路と正式版

Workflowの既存 `f11_test_build=true` の場合だけ `VERSANIUM_TEST_BUILD=1` をBuild環境へ渡す。build.shの既存F11生成経路では、その値が1のときだけ `--versanium-test` をidentity設定ツールへ渡す。新flagが0または未指定なら従来のTitanium F11 packageを選ぶ。`F11_TEST_BUILD` は既存のコンパイル・署名経路を選択するため維持する。

正式配送側（入力false）の既存identity経路と、base `args.gn` の `chrome_public_manifest_package = "io.github.jqssun.helium"` は変更しない。正式版identityを今回決定・再設計していない。正式Release承認flagはfalseのまま。

## 静的検証

- migration tests **12件PASS**。専用ID・従来ID、設定失敗前の書込み防止、不正な固定permission/task affinityの拒否、Workflow Test条件を検証。
- build.sh全体は実行せず、identity選択部分だけを抽出して一時fixture上で実行し、flag=1/0/未指定の3経路を検証した。
- Chromium固定SHA `a49e2e3d4addfd84e765b52afe230bedb81096db` (155.0.8059.79) の実manifestを取得。Vanadium固定 `8a06a43a04074ab26fa4dc8f8aba915285d56839` の対象patch 0118/0156/0230/0280/0283のmanifest hunksを適用し、既存Vanadium→Titanium置換とpatch.shのmanifest直接編集も反映した限定treeで検証。
- 実GN `chrome_public_apk_tmpl.gni` は `chrome_public_manifest_package` → `_manifest_package` → Jinja `manifest_package` およびAPK targetの `manifest_package` へ渡していることをソース照合。
- 実manifestの **11 authority、5独自permission、1空でないtask affinity** はすべて `manifest_package` 由来。旧ID・新IDを当てはめた各集合は重複なし。空task affinityはaffinity無効、未指定は別々のアプリpackageを継承。sharedUserIdなし。
- ProviderのJavaクラス名・内部Java namespaceは変更不要であり変更なし。利用するAndroid標準permissionや外部コンポーネントへの参照は独自permission宣言とは区別する。
- 検証コマンド: `python tools/versanium/tests/check_identity_manifest.py --manifest /path/to/applied/chrome/android/java/AndroidManifest.xml`
- actionlint v1.7.7（公式配布物のSHA256照合済み）PASS。全WorkflowのYAML/inline shell検証はmigration testsでPASS。`bash -n build.sh patch.sh common.sh .github/scripts/check-signing-properties.sh`、`git diff --check` PASS。
- 実アイコン検証 `check_real_assets.py`（24hash・画素・density・safe zone・themed参照等）PASS。source pin検証（5 metadata cases）PASS。アイコン・署名・base args・ズーム/F11実装本体に今回の差分なし。

これはソースを使った静的検証と限定的なローカルテストであり、GN実行・最終manifest merge・APK生成・インストールテストではない。ライブラリを含めた最終merged manifestは次回のユーザー手動ビルド後に確認する。実機では新旧同時インストール、旧アプリのデータとデフォルトブラウザ設定の保持、新アプリ表示名・アイコン・起動・設定・DeXを確認する。

## 保持と運用

Signing configuration changed: **NO**。`common.sh`、LOCAL_TEST_JKS/STORE_TEST_JKS参照、署名診断、既存キーは変更せず、Secrets値の取得もしていない。

今回 **GitHub Actionsを実行していない**。dispatch/rerun/job rerun/runner消費操作、build.sh実行、Chromiumフルビルド、Release/tag作成、main mergeは実施していない。制限解除後の手動実行はユーザーが行う。Primary/Secondaryは同じコミットを通常pushで同期する。

変更ファイル:

- `.github/workflows/build.yml`
- `build.sh`
- `tools/configure_f11_identity.py`
- `tools/versanium/tests/test_migration.py`
- `tools/versanium/tests/check_identity_manifest.py`
- `docs/versanium/test-package-isolation.md`

過去のremaining-work-report.md等は当時の状態を記録した履歴資料であり、Test identityについては本報告が更新情報となる。
