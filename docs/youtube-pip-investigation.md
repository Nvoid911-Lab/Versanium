# YouTubeのPiPとバックグラウンド再生調査

これは旧版の調査記録です。新版比較と独立した診断候補は [修正準備](youtube-pip-preparation.md) を参照。

PiP・再生動作の変更は実装していない。以下はソース調査と公開run情報で、実機で原因を確定した結果ではない。

## 成功APKの来歴

[Build #1](https://github.com/Nvoid911-Lab/android-titanium-browser/actions/runs/38403963131) は公開ページ上で
Success、4時間18分17秒、`titanium-f11-arm64-test`（139 MB）を確認できる。
WorkflowのTitaniumコミットは `a5909598c55da64751d70a8d2facf4a555eab554`。
artifact digestは `sha256:3f5b237b017972e0cab5630170cfda262c339a7b762d166db6749b465c24ebd9`。
これはユーザーの成功APKと対応する有力なrunだが、手元のインストールAPKとdigestを照合したわけではない。

このコミットのVanadium参照は `c1892f4db7a828b9fcbca9ab6a6898b0a7396fae`。
そのargs.gnの版は `155.0.8059.39`。build.shはVanadiumの版番号に対応するChromiumタグをfetchする。
ただし当時のWorkflowはUpdateで最新Vanadiumタグに進めていた。APIアクセスは403、公開runページは
「Sign in to view logs」で、実際のcheckoutとVERSIONログ／artifact内容は取得できなかった。
したがって成功APKの**実際のChromium・Vanadium版／commitは不明**。静的参照を実使用版と断定しない。
TitaniumもWorkflow起点のコミットまでは確認済みだが、実行中のUpdateが作るコミットはログ未確認。
APK内バージョンだけではVanadiumとChromiumの実コミットまでは確定しない。

[Issue #335](https://github.com/jqssun/android-titanium-browser/issues/335) は公開ページ上でOpen、コメント0。
本文の旧版は154.0.8037.92であり、今回の成功APKの版番号を証明する情報ではない。
ユーザーの観測（本体でYouTube停止、DeX/Twitchで動作、Chromeで再現、Braveで動作、Premiumなし、
uBlock無効でも再現）は重要な比較条件だが、停止理由を示すログではない。

## 対象ソースで確認できた事実

調査の固定対象はChromium 155.0.8059.39と上記Vanadium参照、TitaniumのF11ブランチ。

| 処理 | 根拠と意味 |
|---|---|
| バックグラウンド停止 | `content/public/renderer/render_frame_media_playback_options.cc` の `IsBackgroundMediaSuspendEnabled`。通常Androidは停止を許可し、large form factorの例外がある。Titaniumのpatch.shはこのファイルの `#if BUILDFLAG(IS_ANDROID)` を `#if 0` に置換する。対象版にそのアンカーは存在し、適用後は関数がfalseを返す。既にブラウザー側のこの停止ポリシーを全サイトで外している。 |
| Auto PiPフラグ | `chrome/browser/chrome_browser_field_trials.cc` のdesktop Android分岐をアンカーに `media::kAutoPictureInPictureAndroid` を含む無条件のfeature overrideを挿入し、元の分岐を `#if 0` にする既存パッチ。フラグだけで動画の許可やAndroid Activity条件を満たせるわけではない。 |
| Background capturingフラグ | `media::kAndroidEnableBackgroundMediaCapturing` はcapture用のfeatureで、YouTube動画の再生継続を直接保証しない。 |
| ホーム移動 | ChromeActivity.onUserLeaveHint → FullscreenVideoPictureInPictureController.attemptPictureInPicture。canDoPictureInPictureはactive effectively-fullscreen video、動画のPiP許可、端末のPiP機能、Activityの終了／再構成、最近のtask条件を確認する。ブラウザーのF11によるtoolbar非表示は、動画がeffectively fullscreenになることと別。 |
| PiPの停止／解除 | Controller.onStop、onResumeとdismiss処理にはMediaSessionのsuspendやPiP終了の経路が残る。全画面・タブ変更にも反応する。rendererの背景停止を無効にするだけではここを消せない。 |
| タブ切替 | 非表示のWebContentsになることと、Android Activityがホームへ移動することは別。ページのvisibilitychange、ブラウザーのmedia/session処理、YouTubeのJSが停止させる可能性がある。PiPが起動しないことだけではタブ停止を説明できない。 |

Vanadiumの対象パッチ群に、この版の上記PiP Controllerや背景停止関数を変更するパッチは見つからなかった。
Titaniumは再生ポリシーを変更する一方、YouTube専用の非表示検知／PiP用設定変更を持っていない。
対象外のsubproject・拡張・実行時feature設定まで含めて、成功APKに原因がないと証明したわけではない。

## 根拠のある候補と未確認事項

1. **YouTubeの非表示検知による停止**：Braveに明示的なYouTube対策があるため有力。
   ただしユーザーの動画でJSのpause呼び出しを捕捉したわけではなく未確定。
   DeXとモバイルでは表示先だけでなくWebサイトのmobile/desktop版も変わり得る。
2. **動画側のPiP許可・effectively fullscreen条件**：Android Controllerが実際に検査している。
   `disablePictureInPicture`、player設定、動画全画面かが候補。Premium／地域／動画種別は比較条件であり、
   Premiumなしという事実だけで原因を断定しない。
3. **Activity／MediaSessionの停止**：PiPに入る前の非表示、tab switch、Controllerのdismiss/onStopと
   suspension原因を比較する必要がある。Twitch成功は端末全体のPiP禁止の可能性を下げるが、全経路を否定しない。
4. **Samsung／Android 16の経路差**：同一端末のDeXで動作することと整合するが、Braveが動作するため
   OSのみの問題とは言えない。ホーム移動／タブ切替を別々に測るべき。

## Braveの関連実装と適用案

調査時のbrave-core masterを `46cfe58223924f363192475396dcb196ec29423d` に固定して参照した。

- [YouTubeScriptInjectorTabHelper](https://github.com/brave/brave-core/blob/46cfe58223924f363192475396dcb196ec29423d/browser/android/youtube_script_injector/youtube_script_injector_tab_helper.cc):
  YouTubeドメイン／main documentに限定し、background video playbackのfeature＋ユーザー設定で
  visibilitychangeのlistener登録を抑制し、document.visibilityStateをvisibleにする処理がある。
  別のPiP処理ではYouTubeの実験設定のPiP blocking flagsを書き換える。
  さらに動画全画面を非同期で要求し、実際のfullscreen到達を確認した後にPiPへ連携する。
- [BraveFullscreenVideoPictureInPictureController](https://github.com/brave/brave-core/blob/46cfe58223924f363192475396dcb196ec29423d/android/java/org/chromium/chrome/browser/media/BraveFullscreenVideoPictureInPictureController.java):
  screen lock時の停止／再開、YouTube用PiPセッションのentry/dismiss、新規タブの取り扱いがある。
- [Chromium Controllerへの接続パッチ](https://github.com/brave/brave-core/blob/46cfe58223924f363192475396dcb196ec29423d/patches/chrome-android-java-src-org-chromium-chrome-browser-media-FullscreenVideoPictureInPictureController.java.patch):
  upstreamへのhookに加え、BraveActivity、JNI helper、script injector等の依存が必要。
  単独のフラグや一つのJavaファイルをコピーすれば動く構成ではない。

これらはユーザーのインストール済みBraveの実版／有効設定を確認した情報ではない。
現在の公開実装を、現象と整合する実装例として扱う。

修正候補は、まず停止原因の記録と最小比較。その後、**YouTubeだけ・ユーザーが選択した場合だけ**の
background playbackとPiP設定を別々に実装する。PiP entry条件・失敗時の復帰・シークレット・画面移動を検証する。
YouTubeのvisibilityを固定すると、サイトの非表示時の節電・更新抑制・視聴状態等も変わる。
全サイトへのvisibility偽装は行わず、autoplay／user activation制約も一律解除しない。
YouTube実験設定の名前／DOMは変更され得るため、既知条件を満たさなければ何もしない設計と回帰テストが必要。

Braveの当該独自ファイルはMPL-2.0。コピー／改変して配布する場合はファイルの著作権・ライセンス告知を保持し、
Covered Softwareのソース提供と入手方法の通知などLICENSEの§3.1・§3.2を満たす必要がある。
Chromium由来部分のBSD告知も保持する。Titaniumの既存LICENSEだけでBrave由来部分を再ライセンスしない。
今回はソースの流用もPiPコード変更もしていない。

## 最小限の実機比較

同じ公開動画・同じログイン条件で、スマホと有線DeXを比較する。URLや動画ID・アカウント情報をログへ残す必要はない。

1. 動画のインライン表示と、動画プレーヤーの全画面を分ける。F11だけの全画面とも区別する。
2. 各状態で「ホーム移動」と「別タブ切替」を別々に試し、再生停止時刻／PiP発生／通知の再生状態だけ記録する。
3. サイトのモバイル版／PC版を比較する。この切替は調査条件でありズームの環境判定には使わない。
4. Android設定でF11 TestのPiP権限を確認する。Twitchを同じ手順の対照にする。
5. 必要時だけ、制御した再現時間帯にControllerの可否をboolと分類値で記録する小さな診断案を検討する。
   fullscreen / video allows PiP / Activity finishing / changingConfigurations / PiP API result /
   MediaSession suspended reason / document visibility / video paused、表示ID程度で足りる。
   タイトル、URL、cookies、headers、YouTubeのconfig全文、認証情報は記録しない。
   広範なlogcat/dumpsysやリモートデバッグ出力をそのまま公開しない。

## ビルド判断

今回はズームだけの差分を評価し、PiP修正を同じAPKへ混ぜないことを推奨する。
PiPは未確定の候補が複数あり、Brave型の変更はDOM・ネイティブActivity・MediaSessionを跨ぐ。
同時に変更すると画面移動・ライフサイクルの不具合をズームと切り分けにくい。
残491分／前回259分という残量は、同規模のビルドを2回行える保証ではない。
まず統合型チェック、差分レビューと既存APKでの上記比較を済ませ、明確な修正対象が固まった後にPiPの別変更を判断する。
今回Actionsは起動していない。
