# YouTube PiP・背景再生の修正準備

作業ブランチ: `feature/youtube-pip`。調査の開始基準は実機確認済み
`469469769d5b02ad9a974b6c96ac91199c77ab23`。
本家新版の更新とは別ブランチで調査を開始した。

ホーム移動のAndroid PiPと、別タブへ移動したWebContentsの再生継続を区別する。
既存報告の観測は原因確定のログではない。
Brave比較は `46cfe58223924f363192475396dcb196ec29423d` の公開ソースに固定。

新版は作業Aの `2111f749c735680c91d05eb51dcaf0e749988f38` を採用して比較する。
調査したController、背景停止処理、Java/GN/JNI関連の限定取得範囲は旧版と同一。
版番号が上がったことをPiPの解決根拠にしない。

## 確認できた事実と未確定の原因

- Issue #335の公開ページを再取得し、YouTube PiPの報告であることを確認。Issueへの書き込みなし。
- ホーム移動: ChromeActivityのonUserLeaveHint、Androidのauto-enter、FullscreenVideoPictureInPictureController
  の経路。active effectively-fullscreen video、動画のPiP許可、端末機能、Activityの終了/再生成、
  recent tasks等を検査する。F11でツールバーを隠すことは動画プレーヤーの全画面条件とは別。
- タブ切替: WebContents/rendererの非表示とページのvisibilitychange、MediaSession等の別経路。
  Androidのホーム移動と同一原因とは断定しない。サイトJSがpauseしたことも未確認。
- Titaniumのpatch.shはIsBackgroundMediaSuspendEnabledのAndroid分岐を無効にし、
  AutoPictureInPictureAndroid等のfeature overrideを既に持つ。新版にも該当アンカーが存在する。
  既存処理は保持。背景captureのfeatureは再生継続を保証しない。
- ControllerのonStop/dismissにはMediaSession.suspendが残る。動画側の許可、PiP entry、
  手動停止や復帰までフラグだけで解決することはできない。
- スマホ/DeX、Twitch、Chrome/Brave、Premiumなし、uBlock無効の観測は既存報告の通り。
  比較環境の差を絞る材料であり、停止原因のログではない。
- 調べた新版ソースでは上記Controllerと背景停止関数は旧版と同一。関連修復を確認できなかった。
  取得範囲外のBlink/サイト挙動まで同一であることや、新版で再現することは未確認。

## Braveの固定ソースと依存・ライセンス

参照先はすべて `brave/brave-core` の `46cfe58223924f363192475396dcb196ec29423d`。
今回もこのSHAのraw URLからhelper、Controller、BUILD.gn、LICENSEを取得して照合した。
利用者がインストールしたBrave APKとこのSHAが同じという証拠はない。

- `browser/android/youtube_script_injector/youtube_script_injector_tab_helper.cc`:
  YouTubeドメイン/主文書を限定し、背景再生ではユーザー設定とfeatureに従い
  visibilitychangeの登録抑制/visibilityState変更。PiPではWEB_PLAYER_CONTEXT_CONFIGSの
  MWEB_WATCH内にある既知のblocking flagsを変更。別の処理が実際の動画全画面到達を確認する。
- `android/java/org/chromium/chrome/browser/media/BraveFullscreenVideoPictureInPictureController.java`:
  BraveActivity、JNI helper、YouTube PiP session、画面ロック等の依存がある。
  単独ファイルの移植ではentry/失敗時復帰/タブ遷移まで成立しない。
- helperはrenderer側Mojo script injector、navigation entry state、prefs/features、
  BraveActivity/Controller、GN depsも必要。背景再生とPiPは異なる設定・機能。
- 重要な移植上の制約: Chromium RenderFrameHost.ExecuteJavaScriptはchrome:// / devtools://用。
  Brave helperはAllowInjectingJavaScript()を呼ぶ。ChromiumのAPI説明はこれを**グローバル**な
  許可としてWebView等の特定構成に限定している。Titaniumへ単にコピーする案は採用しない。
  テスト用ExecuteJavaScriptForTestsや偽のuser activationも本番の代替にしない。
- Brave独自ファイルはMPL-2.0。コピー/改変する場合は著作権・ライセンス告知を保持し、
  MPL §3.1のCovered Sourceの提供、§3.2の入手方法通知等が必要。ChromiumのBSD告知も保持。
  今回はBraveのコードやスクリプトをリポジトリへ流用していない。診断は独自コード。

## 比較した修正候補

| 候補 | 影響・規模 | 必要な確認・判断 |
|---|---|---|
| 動画全画面/許可の診断（今回実装） | 小。OFF既定、通常YouTubeタブだけのboolログ。再生制御は変更しない | スマホ/DeX、インライン/動画全画面/F11を分けてPiPの拒否条件を見る |
| YouTubeの既知PiP blocking configだけ変更 | 中。明示的なユーザー選択、主文書・HTTPS・既知ホスト/設定形式の検査が必要 | 実際の設定名・消費タイミング、動画全画面とPiP entryを確認。インラインから全画面を勝手に要求しない |
| YouTubeの背景再生対策 | 中～大。主文書・対象ホスト・ユーザー設定で限定。ページの可視性を変えると節電、広告、更新抑制、視聴状態へ影響 | ホーム/タブ切替を別々に検証。手動pauseを尊重。visibility偽装を全サイトへ広げない |
| Brave型の非同期fullscreen→PiPセッション | 大。renderer/native/Java/JNI、タイムアウト・document lifetime・復帰管理 | entry失敗、全画面解除、画面移動、再生成、タブ復元、シークレット、DeXを十分に検証するまで保留 |

既知config名は `html5_picture_in_picture_blocking_ontimeupdate`、`..._onresize`、
`..._document_fullscreen`、`..._standard_api`。これらが端末のYouTubeで存在し、有効かは未確認。
将来の対策は未知の名前、欠落したytcfg/DOM、型不一致なら変更しない。
許可された主文書への注入方式（例えば対象ホスト限定・ユーザー選択の拡張機能）を確立し、
YouTube/他サイト/サブフレームを区別する必要がある。全サイトの可視性、autoplayやuser activationの
制限解除は実装しない。原因が不明なため、今回再生動作の修正は実装していない。

## 実装した診断候補

`tools/youtube_pip/diagnostics.patch` と専用applyスクリプトを、このブランチだけのpatch.shで適用。
新版のソース固定ゲートとgit apply --checkを通す。更新ブランチには存在しない。
新しいJNI/Javaファイル/GN sourceは不要。既存Controllerのソース登録とbase、Tab、GURLの
直接依存を固定GN/Java sourceリストで照合。Native flagsは既存SINGLE_VALUE_TYPEを使用する。

`chrome://flags/#titanium-youtube-pip-diagnostics` の **Titanium YouTube PiP diagnostics** は既定OFF。
有効化・再起動後、HTTPSのyoutube.com / www.youtube.com / m.youtube.comにある通常タブのみ記録。
他ホスト、サブドメイン偽装、HTTP、シークレット/OTR、破棄済みWebContentsは対象外。
判定は現在の主文書のcommitted URLで行うが、URLを記録しない。

記録は `attempt_allowed/blocked`、`auto_allowed/blocked`、Android APIのtrue/false/exception分類、
framework entered/exited、onStopの既存suspend、resume、既存dismiss理由の整数分類と、
full / videoAllows / devicePip / inPip / changing / finishingの真偽値だけ。
同じ連続レコードは抑制。タイトル、URL、Cookie、認証情報、例外全文、YouTube config、動画IDは記録しない。
ログへの値は定数、既存enum、boolだけ。保存プロフィールを変更せず、値のキャッシュはController寿命内だけ。

この診断は動画側PiP許可と端末機能を記録するが、Androidのアプリ別PiP許可やrecent tasksの全条件、
サイトJSのpause理由を網羅しない。auto-enter時はattempt経路を通らない場合もあるので、auto/frameworkの
記録も追加した。タブ切替後の新しい主文書がYouTubeでなければ記録しない。空ログを原因不在と扱わない。
PiP失敗時の復帰、手動停止、MediaSessionの既存処理、Twitch、DeX、画面移動の動作は変更しない。

## 検証結果

確認済み:

- 新版の対象3ファイルへ選択Vanadiumパッチを実適用し、診断patchをcheck/apply。
- Java23構文解析。型チェックとは区別。
- 実際の診断メソッドを抽出し、明示的なAndroid/Chromiumテストダブルで26件PASS。
  OFF時の早期return、シークレット、破棄、HTTPS/厳密ホスト、dedup、許可するログ形式を検証。
- 診断メソッド単位の限定Javaコンパイル: 実Android API26クラス＋固定Chromiumソース由来の
  **宣言のみ**の依存を使用。テストダブルのコンパイルだけを型チェックと呼んでいない。
  Android API jarは公開SHA1照合済み、約101MBの限定取得。SDK/NDK一式の取得はしない。
- shell構文とgit diff --check。Aの検証結果とソース固定を維持。

ソース照合のみ: Controllerの残り、flagsのNative登録、GN依存、ホーム/タブ/MediaSession、Brave。
未確認: Controller全体のJava/NullAway、Native flags本体/GN gen、完全な統合コンパイル、
実際の診断フラグの表示・ログとAndroid lifecycle、PiP/背景再生の実機動作。

## 次の最小限の実機比較（ビルド予算確保後）

1. A更新だけのAPKとB診断候補入りAPKを分ける。Bでも最初はフラグOFFでA相当の挙動を比較する。
2. BでフラグをEnabledにし、案内に従い再起動。AndroidのF11 TestのPiP許可を端末設定で確認。
3. 同じ公開動画・ログイン条件で、スマホ/DeX × インライン/動画全画面/F11のみについて、
   **ホーム移動**と**別タブ切替**を別々に試す。URLや動画名を記録する必要はない。
4. Twitchを対照にし、手動pause、PiPから復帰、画面移動、シークレットの通常挙動も確認。
5. 必要なら、Termux側（whoamiがu0_a…、rishのshell内ではない）で次を実行してから1回だけ再現する。

```sh
umask 077
mkdir -p "$HOME/titanium-pip-logs"
pip_log_file="$HOME/titanium-pip-logs/pip-$(date +%Y%m%d-%H%M%S).log"
rish -c 'p=$(pidof -s io.github.nvoid911.titanium.f11test); [ -n "$p" ] || exit 1; exec logcat -b main --pid="$p" -v brief -T 1 cr_TitaniumPiP:I TitaniumPiP:I "*:S"' 2>&1 | tee "$pip_log_file"
```

再現後TermuxでCtrl+C。保存先はTermux私有領域の `$HOME/titanium-pip-logs/`。
これはBの**診断フラグON時**の専用タグだけであり、現行4694697のAPKにはこのタグはない。
共有するのはそのbool/分類行と「スマホ/DeX・表示状態・ホーム/別タブ・結果」のみ。
万一別情報が混じったら値を伏せる。全logcat/dumpsys/config全文は共有しない。
比較後はフラグをDisabled/Defaultに戻して再起動する。

ビルド前の残課題: 予算・容量を確保して統合コンパイル、Native flag/診断経路の実機確認。
挙動修正APKはまだ準備完了ではない。Aは更新のみ、Bは独立した**診断候補**として評価可能なソース状態。
boolログでPiP側を絞ってもタブ切替のサイトJS原因は別途確認が必要。
Actions、build.sh、Chromiumフルビルドは今回実行していない。
