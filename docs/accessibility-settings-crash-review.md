# ユーザー補助画面の表示失敗の調査・修正

対象は `feature/dex-mobile-zoom` の `a6191b9e4f262b74bb9d68581d472694ace41c5e`。
このAPKのビルドと更新は利用者が成功を確認している。今回こちらではActions、
`build.sh`、Chromiumフルビルドを実行していない。

## 発見と修正

新しい2つの `androidx.preference.SeekBarPreference` が、レイアウトもスタイルも
XMLで指定せず、ホストテーマの `seekBarPreferenceStyle` に依存していた。
固定Chromiumの `components/browser_ui/settings/android/java/res/values/styles.xml`
にある `PreferenceTheme` には、この属性が定義されていない。
`chrome/android/java/res/values/styles.xml` の `Base.Theme.Chromium.Settings` は
この独自の `PreferenceTheme` を指定する。AndroidX標準の
`PreferenceThemeOverlay` が常に適用されると仮定できない。

照合したAndroidX公開ソースでは、SeekBarPreferenceのXML用コンストラクターは
`seekBarPreferenceStyle` を選び、フォールバックの `defStyleRes` は0。
通常のPreferenceレイアウトには `seekbar` / `seekbar_value` がなく、
`onBindViewHolder()` が `seekbar_value` をTextViewとして取得した直後に
`setVisibility()` を呼ぶため、専用レイアウトが選ばれなければnull参照になる。
これは生成済みPreferenceをRecyclerViewへ表示するときの問題であり、
設定保存PolicyのテストやJavaコンパイルだけでは見つからない。

修正は `tools/environment_zoom/chromium.patch` の2つのスライダーへ
`android:layout="@layout/preference_widget_seekbar_material"` を追加するだけ。
専用レイアウトの選択をテーマ任せにせず、必要なビューを備えた既存AndroidX
リソースを使用する。新しいJavaクラス・独自レイアウト・広いtry/catchは追加しない。

**実機の例外は未確定。** クラッシュログは未取得で、Chromiumが固定する
AndroidX Preference **1.3.0-SNAPSHOT / build 16323643** のAAR取得は
このクラウド環境の接続先制限で403になった。照合用にGoogle Mavenから取得した
**1.2.1** のAAR・sources.jar（公開SHA1照合済み）とAndroidX公開mainソースは
上記のコンストラクター・bind処理を持つが、固定snapshotの実装確認の代用とは
扱わない。snapshotのコミットを変更したり、依存を1.2.1へ変更したりしていない。
発見したテーマ依存を除去する修正であり、今回の端末の確定原因／修復済みとの
主張は、ログ照合と実機確認まで保留する。

## 固定ソースの画面生成経路

Chromium `155.0.8059.39` / `3ff7ac5a9224be9156d7f8703a06e22890aafd34`、
Vanadium `c1892f4db7a828b9fcbca9ab6a6898b0a7396fae` を維持して調べた。
今回のAPKの実行時バージョン情報を端末から読み取ったわけではない。

1. `chrome/android/java/res/xml/main_preferences.xml` の `accessibility` が
   `org.chromium.components.browser_ui.accessibility.AccessibilitySettings` を指定。
2. `SettingsActivity.onPreferenceStartFragment()` → `startSettings()` によって
   対象のSettingsActivity/Fragmentへ遷移する。
3. Activityは `super.onCreate()` の前に `FragmentDependencyProvider` を登録。
   `onFragmentAttached()` で `ChromeAccessibilitySettingsDelegate(mActivity, mProfile)`
   を渡す。通常経路では `onCreatePreferences()` より前にdelegateが設定される。
4. AndroidX PreferenceFragmentCompatがPreference用テーマを選んでから
   `AccessibilitySettings.onCreatePreferences()` を呼び、SettingsUtils経由でXMLを展開。
5. `EnvironmentZoomSettings.add()` がUserPrefs/EnvironmentZoom.store、2つのデフォルト、
   サイト設定へのリンク、画面分類のListPreferenceを初期化する。
6. 既存の強制ズーム、読み上げ関連、キャプション、Caret browsing等が初期化され、
   RecyclerViewが各Preferenceのレイアウトを生成・bindする。

レビュー用ツリーに、ズーム変更の対象ファイルへの選択済みVanadiumパッチを
実際に適用してからズームoverlayを適用した。追加で、SettingsActivity、
FragmentDependencyProvider、MainSettings、SettingsContainmentHelper、delegate、
SettingsUtils、設定テーマ、PageZoomSliderPreferenceとレイアウトの10ファイルを
固定ソースから取得し、交差するVanadiumパッチ0141 / 0142 / 0151 / 0270を
実際に適用した。リブランド・除外条件は既存patch検証と同じ。
設定トップの `main_preferences.xml` も選択Vanadiumパッチを適用してから、
`accessibility` が同じFragmentを指すことを確認した。
Chromium全体を取得・全パッチ適用したツリーではない。

重点確認の結果（以下はソース照合であり、Android動作確認ではない）:

- `add()` のfindPreferenceとXMLのキー／クラスは一致する。スライダー値の
  変更コールバックはInteger、ListPreferenceはStringを扱う通常のAPI契約。
  ListPreferenceのentries/entryValuesを設定してからvalue、summary providerを設定。
- 元のXML項目は削除していない。旧グローバル設定に代わる2つのデフォルトを表示し、
  `zoom_info` は非表示にするが、参照されるPreference自体は残る。
- nativeプロフィールのポインターが0なら `add()` は戻る。通常のdelegateは保持した
  Profileを返す。nullプロフィールや破棄途中が今回の原因という証拠はない。
  設定画面のActivity/ネイティブプロフィール寿命を実行して確認したわけではない。
- 画面分類は設定FragmentのContextをDisplayAndroidへ渡す。PC版サイト／UA／幅の
  判定は追加していない。今回の修正では画面分類処理を変更していない。
- Smart Zoom有効時だけ作られるcontrast用PageZoomSliderPreferenceのレイアウトには
  `page_zoom_section` があり、その非表示処理が参照するIDは存在する。
- サイト一覧のandroid.app.AlertDialogはリンクを押した後に生成される。
  設定画面を開く時点では生成されない。ダイアログの実機テーマ表示は未確認。
- 保存処理、データ移行、サイト別マップ、F11、共存ID、署名、Secrets、runner、
  ソース固定、PiPコードに変更はない。

## 実施した検証と限界

- 選択Vanadiumパッチ→ズームoverlayの実適用、XML解析、reverse apply確認: PASS。
  アンカー不一致で全体を拒否する既存の負例もPASS（意図したgit applyエラー）。
- AAPT2 `8.7.3-12006047`（Google Maven公開SHA1照合済み）で、適用後の
  ユーザー補助XMLとoverlay文字列リソースを **compile**: PASS。
  リソース **link**、固定snapshotとの解決、APK生成は未実行。
- `check_settings_resources.py`: PASS。適用後の2つのXMLノードからレイアウトを
  たどり、照合用AndroidX **1.2.1** AARの実XMLでSeekBar/TextViewと必須IDを確認。
  固定snapshotのAARメタデータにも同じレイアウトが存在することを確認。
  修正前に相当する指定なしノード2件は検証で拒否。既存項目、クラス、persistent=false
  も確認する。この検証はリソース契約の照合であり、Androidテーマ解決の実行ではない。
- 既存Policy: 481 assertions PASS（ファイル保存・移行を実行）。
  Bridge: 31 assertions PASS（Android/JNIはテストダブル）。
  Persistence: 13 checks PASS（保存の集約・失敗・再試行）。
  これらを設定画面の生成／表示確認とは扱わない。
- 固定入力ゲート5件、`git diff --check`: PASS。

クラウドにAndroid端末／エミュレーターがなく、固定AndroidX snapshotも取得できず、
**実際の設定画面の生成・bind・表示テスト、完全な統合コンパイルは未実行**。
APK上で、スマホとDeXのユーザー補助画面を開く／閉じる、2つのスライダー、
画面分類の選択ダイアログ、サイト一覧と解除、Smart Zoom有効時のcontrastを確認する。
再起動後の既存値と、もう一方の画面環境の値が保持されることも実機確認が必要。

再利用できるソース／リソース照合手順:

```sh
python tools/environment_zoom/tests/check_patch.py \
  --source-tree /path/to/pinned-chromium \
  --vanadium-patches /path/to/pinned-vanadium/patches \
  --output-dir /tmp/new-zoom-review-tree
python tools/environment_zoom/tests/check_settings_resources.py \
  --applied-tree /tmp/new-zoom-review-tree \
  --source-tree /path/to/pinned-chromium \
  --preference-aar /path/to/preference.aar \
  --aar-version '実際に渡したAARのバージョン'
```

## 再ビルド前の最小限の端末ログ

再ビルド前に、現在のa6191b9 APKで以下を行うと、SeekBarPreferenceのbind中の例外か、
別の初期化・ネイティブ例外かを区別できる。TermuxからShizukuの **rish** が既に
使える場合の手順。Termux単体の通常権限では他アプリのlogcatを読めない。
Shizukuを起動し、Termux/rishの利用を許可しておく。rishが未設定ならShizukuの
「ターミナルアプリで使用」の案内でセットアップする。端末外へログを送るコマンドはない。

1. F11テストAPKを開き、まず設定のトップ画面まで進む。
2. Termuxで以下を開始する。ブラウザーが生きている間のPIDを取得し、そのPIDの
   **crashバッファだけ** を監視する。PID取得に失敗した場合は監視を開始しない。

   ```sh
   rish -c 'p=$(pidof -s io.github.nvoid911.titanium.f11test); [ -n "$p" ] || exit 1; exec logcat -b crash --pid="$p" -v brief -T 1'
   ```

3. ブラウザーへ戻り「ユーザー補助機能」を一度押し、Termuxに戻ってCtrl+C。
4. 共有するのは対象の `FATAL EXCEPTION`、例外クラス、`Caused by`、スタックの
   Settings/EnvironmentZoomSettings/SeekBarPreference付近のフレームだけでよい。
   例外メッセージにURL・検索語・トークン等があればその部分を伏せる。
   main/systemバッファ、全アプリのログ、bugreport全体は共有しない。

このコマンドは設定操作中にPIDが変わる前のクラッシュを狙う。端末がTermuxへ
移動する際にブラウザーを終了した場合は、PIDが変わって採取できないのでやり直す。
ログが出ない場合は「crashバッファに対象PIDの記録なし」と報告し、追加採取の
範囲を判断する。空ログをもってクラッシュしなかったとは判断しない。

期待する根拠はNullPointerExceptionと `androidx.preference.SeekBarPreference.onBindViewHolder`
周辺のフレーム。別の例外なら、そのログを先に照合してから次のビルドを判断する。
今回の変更だけで実機の修復が確定したとはせず、Blacksmithの残量を消費する前に
この限定ログを確認することを推奨する。
