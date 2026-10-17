# 実アイコン投入・残作業報告（2026-10-18 JST）

## リポジトリ・API

- Primary: https://github.com/Nvoid911/android-titanium-browser
- Secondary: https://github.com/Nvoid911-Lab/android-titanium-browser
- 両 main は `6755ccfd5d5c8a5e8fa3620be6da9ccd4a399aa7` を維持。migration/versanium のみ通常pushし、履歴書換え・force push・main mergeはしていない。
- 両 `GET /repos/{owner}/android-titanium-browser` はHTTP 200、`permissions.admin/push` はtrue。以前の接続拒否は解消したが、操作ごとのGitHub App権限は別である。
- `PATCH /repos/Nvoid911/android-titanium-browser`（name=Versanium、指定description）はHTTP **403**、GitHub応答メッセージ **Resource not accessible by integration**。GitHub CLIのエラーとして確認。ネットワーク遮断ではなく連携認証の権限制限。以後metadata変更は停止し、別経路・認証変更による回避はしていない。
- rename未実施のためremote URLは旧URLのまま正しく維持。jqssun upstream URLも変更なし。
- DescriptionとTopicsは未変更。Primary descriptionは `Secure open-source Android browser with support for extensions`、Secondaryはnull、両topicsは空。
- 適用予定description: An Android browser focused on providing a comfortable and consistent browsing experience across smartphones and desktop-style environments.
- 追加予定topics: android, browser, chromium, titanium, samsung-dex, desktop-mode, android-browser, chromium-browser。既存topicを削除する実装はない。
- `GET /repos/{owner}/android-titanium-browser/actions/permissions` も両方HTTP403、Resource not accessible by integration。Actions設定は変更していない。
- Social Previewのホスト設定は未実施。完成PNG/SVGを保存済み。GitHub Settings → Social preview から `res/versanium/social-preview.png` をアップロード可能。

## 実画像と生成物

添付の実ファイルはPNGではなく1280×1280 JPEG。`master-original.jpg` は添付とバイト同一。`master.png` はデコード画素を変更しないPNG化。AI生成・再描画・別ロゴ置換はしていない。

透明foregroundのみ輝度をalphaに変換し、JPEGの黒背景ノイズ（輝度16/255以下）を除去。原本・canonical PNGは加工しない。白い惑星、外周、軌道、星、中央形状を保持。Adaptiveの全図柄は66dp円内に収める。背景は黒、monochrome/themedは同じ白alpha bitmapを参照する。既存 `res_titanium_base` の17リソースを置換し、GNリソース名を増やさない。旧 `res/drawable/themed_app_icon.xml` を再コピーする経路は使わない。

全24画像/XML成果物とSHA256は `res/versanium/assets.json`、今回の全変更ファイルは `remaining-work-files.txt` に記録した。5密度（mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi）それぞれにlegacy launcher、adaptive foreground、black background。その他:

- `res/versanium/master-original.jpg`, `master.png`, `logo.png`
- `res/versanium/android/mipmap-nodpi/layered_app_icon_foreground.xml`
- `res/versanium/android/drawable/themed_app_icon.xml`
- `res/versanium/social-preview.png` (1280×640), `social-preview.svg`（同じmaster PNGを埋込み）
- `fastlane/metadata/android/en-US/images/icon.png` (512×512)
- `fastlane/metadata/android/en-US/images/featureGraphic.png` (1024×500)

## 検証

確認済み:

- migration tests 11件PASS（JPEG原本保持とPNG変換の回帰検証を追加）。fixtureテストは実画像の検証とは区別。
- `tools/versanium/tests/check_real_assets.py`: 実画像24ハッシュ、原本とのデコード画素一致、全PNG/XML、密度寸法、黒背景、白monochrome、66dp円のsafe zone、fastlane寸法、SVGの埋込みPNG一致PASS。
- 既存zoom: policy481 assertions、bridge31 assertions、persistence13 checks PASS。bridgeのAndroid/JNI/rendererはmockであり実機検証ではない。
- source pin: Chromium155.0.8059.79 (`a49e2e3d4addfd84e765b52afe230bedb81096db`)、Vanadium `8a06a43a04074ab26fa4dc8f8aba915285d56839`、revision gate5ケースPASS。
- actionlint（Buildおよび署名診断Workflow）、全Workflow YAML/inline shell（migration test）、bash -n、git diff --check PASS。
- 実画像AndroidリソースのAAPT2 compile PASS (`8.7.3-12006047`)。resource compileでありAPK link/統合コンパイルではない。
- LICENSEはmainとSHA256一致。今回の差分ではWorkflow・署名・Android identity・zoom/F11のソース変更なし。

ソース照合・限定検証:

- 固定Chromiumの実launcher XMLと、固定Vanadium branding patchから生成した17個の既存リソース置換先で適用を確認する限定チェックを実施。全翻訳ファイルや全Chromium treeを統合した検証とは区別する。
- Titaniumはupstream、attribution/license、Titanium Extension for Android、内部titaniumディレクトリ/namespace/互換キー/patch対象として維持。一括置換していない。前回の分類表は `titanium-occurrences.tsv`、今回の追加分は `remaining-titanium-occurrences.tsv`。

未確認:

- 完全な統合ビルド成功、APK署名・更新インストール、Galaxy S23/Android16/One UI8.5のスマホ/DeX表示・Settings/About/通知/拡張等。ローカル空き約30GBで、Chromiumフル取得/ビルドは行っていない。

## Test Build

Primary dispatch: HTTP422 **Actions has been disabled for this repository**。設定を変更して回避していない。

Secondaryでは明示的なworkflow_dispatchが受理され、Blacksmith runnerが起動。`Versanium Build`、runner `blacksmith-8vcpu-ubuntu-2404`、`f11_test_build=true`。原本ハッシュ/ソース固定のpreflight、Set ENVは成功し、Build進行中として確認した。

- 実行: https://github.com/Nvoid911-Lab/android-titanium-browser/actions/runs/39064803299
- ビルド対象SHA: `f84c68c09f33472e6cb601d311272b3783e68031`（後続は検証・報告ファイルのみ）
- Artifact期待値: **Versanium-Test**
- APK期待値: **Versanium-155.0.8059.79_Test.apk**
- 本報告記録時点ではビルド完了・Artifact生成未確認。無料枠残量は取得できず、完走は保証できない。追加の重複ビルドは起動していない。
- 正式Release、production tag、正式APK公開、mainへのmergeは未実施。release承認flagはfalseを維持。

package/applicationId changed: **NO**

signing configuration changed: **NO**

既存の共存ID、Provider/権限分離、LOCAL_TEST_JKS/STORE_TEST_JKS参照を保持。Secrets値の取得・表示・変更や署名鍵生成はしていない。

次はActions完了結果を確認し、成功時のTest Artifactのみで実機評価する。metadata変更にはGitHub連携のrepository administration操作権限が必要。実機承認までmain merge・正式公開は保留。
