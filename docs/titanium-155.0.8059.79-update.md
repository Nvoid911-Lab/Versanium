# v155.0.8059.79 更新レビュー

作業ブランチ: `update/titanium-155.0.8059.79`。
基準: 実機確認済みの `469469769d5b02ad9a974b6c96ac91199c77ab23`。
originの `feature/dex-mobile-zoom` がこのSHAを指すことをfetchで確認した。

## 採用した入力

| 入力 | 固定値・確認方法 |
|---|---|
| 本家リリース | `v155.0.8059.79` → `3f02ed2a05886655b875b21e7c273d8a54fe75ed`。本家へのgit ls-remote、タグfetch、実コミットを確認 |
| 共通祖先 | `c433018f78b54dea5573f2789ed086022c7ec6f1`。git merge-base |
| Vanadium | `8a06a43a04074ab26fa4dc8f8aba915285d56839`。本家タグのgitlinkと実際のsubmodule HEADを照合 |
| Chromium | `155.0.8059.79` / `a49e2e3d4addfd84e765b52afe230bedb81096db`。Vanadium args.gn、Chromiumタグのgit ls-remote。限定ソースはこのSHAのraw URLから取得 |

共通祖先から本家タグまでの変更はVanadiumのgitlinkだけ。本家コミットを第2親に
持つマージで履歴を保持した。競合なし。Vanadiumの更新は155.0.8059.79向けパッチ移植、
版番号、config app 215→216を含む。文字列リブランドおよびローカルパスワード関連の
パッチ更新も含まれる。旧版パッチへ戻す競合解消や最新版main/tagへの追従は行っていない。
Chromium全体の変更を監査したわけではなく、個別CVEの修復を独自に確認したとは主張しない。

`check_environment_zoom_revision.py` のVanadium、版番号、Chromium SHAを新版に更新。
F11手動ビルドは正確なSHAを別refへfetchしてdetached checkoutする既存処理を維持。
新版refの一致と、そのSHAがパッチ適用後HEADの祖先であることを検査する条件も維持。
祖先チェックを削除して通す変更はない。実際のフルビルドツリーでの祖先チェックは未実行。

## 独自機能と保存データ

F11、共存ID `io.github.nvoid911.titanium.f11test`、Provider/独自権限の分離、署名コード、
手動専用Workflow、runner、Secretsは変更なし。PiP動作変更はこのブランチに含めない。

環境別ズームの全Javaコード、XML差分、保存キー・プロフィールパス識別、保存形式、
移行マーカー、workerによる非同期保存、破棄・再入対策は基準と同一。
専用 `preference_widget_seekbar_material` の明示も維持。更新時にデータを消す処理や
再移行を追加していない。既存ファイル保存／移行テストも実行した。

基準APKではユーザーがF11、ユーザー補助画面、両スライダー、モバイル100%/DeX67%、
環境別サイト保存、デフォルト変更・再起動後の保持を実機確認済み。
**その結果を新版APKの実機確認に読み替えない。**

## ローカル検証

空き約30GB。Chromiumの限定ソース134ファイル（数MB）を取得し、旧版との比較では
取得範囲の変更はDEPSのみ。これにはズーム対象、関連Java/API/GN、PiP Controller、
背景停止処理とJNI生成器を含む。Chromium全ソースの不変を意味しない。
Vanadiumはsubmoduleを初期化し、Git履歴約383MBを取得した。

確認済み:

- 新版の選択Vanadiumパッチを実適用→ズームoverlay実適用、reverse check、アンカー不一致拒否。
- JNI生成器の実行と、実生成ヘッダーを使う6つのC++型アサーション。g++の
  clang lifetimebound属性に関する警告あり。Android向け本体.ccコンパイルではない。
- Android実APIとChromiumソース由来の宣言のみの依存を用いた3つのズームJavaクラスの限定コンパイル。
- Policy 481 assertions、Bridge 31 assertions、Persistence 13 checks。
  BridgeのAndroid/JNIはテストダブル。画面・rendererの動作確認ではない。
- リソース契約検証: 既存項目・型、両専用レイアウト、SeekBar/TextViewと必須ID、修正前相当の負例。
  レイアウト内容はAndroidX 1.2.1の照合用AAR。固定snapshotそのものの実行ではない。
- AAPT2による適用後XML・文字列リソースのcompile。resource linkは未実行。
- 固定参照ゲート5件、Vanadium実HEAD/版番号検査、shell構文、actionlint、git diff --check。

ソース照合のみ:

- Profile→EnvironmentZoomのGN依存、sources/resources、HostZoomMap JNI生成対象、
  新しいJava呼出先の宣言と可視性。今回取得したこれらのソースは旧版と同一。
- SeekBar専用レイアウトを保持。両環境の保存形式はGit差分でも同一。

未確認:

- 設定Fragmentの実生成・bind・テーマ解決、AndroidX固定snapshotでの画面表示。
- GN gen、NullAwayを含むChromium全Java、対象ネイティブ.cc本体、完全な統合コンパイル。
- 新版APKの実機動作、シークレット・同時表示・画面移動の回帰、署名済みAPKのID照合。

フル取得/ビルドは公式目安空き100GB以上に届かず、Blacksmith残約81分も以前の
約194分のビルドに足りない。gclient/depot_tools/Android SDK/NDK等を取得していない。
将来の統合確認は十分な容量・予算を用意してから通常の手動Workflowを使う。
今回はActions、build.sh、Chromiumフルビルドを実行していない。

次のAPK比較は更新ブランチだけのAPKを先に評価する。設定画面、67%表示・適用、
保存済みサイトの保持、両環境・再起動を確認し、PiP候補入りAPKとは分けて評価する。
