# ビルド前の統合レビュー

レビュー元は `6901f21452d9bb286eb39dc20f0ddac24ed9e820`。
Actions、build.sh、Chromiumフルビルドは実行していない。build.shは修正と `bash -n` のみ。
PiP、署名、Secrets、runner、main、feature/f11-toolbarは変更していない。

## 発見・修正した問題

1. **JNI生成条件の訂正**：private @CalledByNativeは単独生成器の既定条件では拒否されたが、
   固定版jni_zero.gniのgenerate_jni wrapperはallow_private_called_by_natives=trueを設定している。
   実GN相当のフラグで元6901f21の生成も成功したため、元SHAのビルド不具合とは断定しない。
   callbackは既存公開callbackに揃えてpublic staticにし、厳格な単独生成条件でも互換にした。
   修正後は実GN相当のフラグでも生成・型検証に成功。必要なGN条件と単独コマンドの既定条件を区別する。
2. **UIスレッドの同期commitと例外**：スライダー操作が辞書全体を同期commitし、失敗時にJava例外を
   ネイティブcallbackまで送る設計だった。UIはメモリへ反映し、200msのdebounceで最新のimmutable snapshotを
   一つのworkerへ送る方式に変更。commitはworkerだけで実行。設定のSeekBarも連続通知を無効にする。
   連続1000更新を1回へまとめる試験を実施。辞書snapshotのUI上のコピーはサイト件数に比例するので、
   大きな辞書と実機スライダーの性能は別途確認が必要。
3. **失敗時の扱い**：commit false／RuntimeExceptionはworkerで捕捉。最新snapshotを保持し、最大3回の
   自動試行（追加試行は1秒・2秒後）。新しい変更、Activity stop、プロフィール破棄のflushで再試行可能。
   失敗時はURL・ホスト・値・例外内容を含まないログと通知を出す。通常プロフィール破棄後の未保存snapshotも
   プロセス内で保持し、再生成時に引き継ぐ。シークレットはこのworker／保持領域を使用しない。
   flushは投入だけでUIを待たせない。成功前の強制終了・電源断・継続的な保存失敗による未保存データの消失は
   防げず、保存完了とメモリ反映を同一視してはいけない。
4. **破棄／再入**：native照会時にstoreを初期化する可能性を除去。照会は準備済みBindingの読み取りだけ。
   native setterの中から同期refreshせず、次のUI処理にまとめて投稿する。
   Profile破棄開始時、native pointerの無効化・破棄observerより前にBindingを外す。
   破棄済みWebContentsは参照せず、native getter／refreshにもnull・IsBeingDestroyedガードを追加。
   破棄中のmanaged WebContentsのsaveはlegacyのグローバル保存へ落とさない。
5. **Activity不在**：一時的にdetachしたmanaged tabには最後に確認した環境／fontScaleを保持する。
   一度も環境を確定できなかった場合、照会はNaNで既存描画にfallbackし、saveはlegacyへ書き込まず保留する。
   Activity再接続時に実際の表示先を再評価する。
6. **未保存の通常設定とシークレット**：通常workerがまだ書いていない値も、シークレット作成時には
   通常のメモリsnapshotからコピーする。private変更を通常／ディスクへ戻す経路はない。
7. **ソース固定の不足**：Update skipだけではローカルのサブモジュール状態やタグの変更を検出できなかった。
   WorkflowでF11入力時にVanadium HEADと版を事前確認。F11ではChromiumをタグ名でなく固定SHAでfetchし、
   detached checkoutする。git amが検証用upstream refを進めないようにする。
   gclientの大きな取得前とズーム適用直前に、SHA・VERSION・祖先関係を検証する。

## 固定版とソース照合

Vanadium：`c1892f4db7a828b9fcbca9ab6a6898b0a7396fae`。
Chromium：`155.0.8059.39`、`3ff7ac5a9224be9156d7f8703a06e22890aafd34`。
後者はGitHub Chromiumのタグへのread-only `git ls-remote` と一致した。
VanadiumパッチはTitaniumと同じ除外・名称置換を行い、対象ファイルへ適用して検証した。
実際の将来のActionsは実行していない。想定外の入力なら停止する設計であり、実ビルド成功の主張ではない。
通常ビルドのUpdateは維持するが、この機能ブランチで固定版から先へ進めた場合はreviewed-input gateが拒否する。

| 呼び出し | 固定版の宣言・可視性の照合 |
|---|---|
| BrowserContextHandle.getNativeBrowserContextPointer | public interfaceのlong、引数なし。Profile実装はmNativeProfileを返す。0を初期化前に拒否する。 |
| Profile.shutdownStarted / 破棄開始 | public boolean、引数なし。notifyWillBeDestroyedでmDestroyNotified設定後、ProfileManager observerの前に外す。 |
| WebContents.isDestroyed | public boolean。native handle 0／IsBeingDestroyedを確認する。 |
| WebContents.getTopLevelNativeWindow | nullable WindowAndroid、引数なし。実装はcheckNotDestroyed後にnative getter。 |
| WindowAndroid.getActivity | public WeakReference<Activity>。baseはnullを返すが、ChromeActivityが使うActivityWindowAndroidのoverrideはActivityを返す。 |
| DisplayAndroid.getNonMultiDisplay / getDisplayId | public static DisplayAndroid(Context) / public int()。ActivityのContextを使用。 |
| HostZoomMap.getDefaultZoomLevel / getAllHostZoomLevels | public static double(BrowserContextHandle) / Map<String,Double>(BrowserContextHandle)。移行時だけ使う。 |
| HostZoomMap.shouldAdjustForOSLevel | public static boolean()。描画読み取りに使用し、プロフィールの保存を呼ばない。 |
| UserPrefs.get / PrefService.isDefaultValuePreference | public static PrefService(BrowserContextHandle) / public boolean(String)。getのnullを防御し、Android用pref名を確認した。 |
| ContextUtils / ThreadUtils / StrictModeContext / Log | 実ソースの公開static宣言を抽出して限定コンパイルに使用。引数・戻り値とimportを照合。 |
| AndroidのActivity・Handler・DisplayManager・SharedPreferences・Toast | 実Android APIのclassfileで新規中核コードを限定コンパイル。新しいSDK 37全体のコンパイルではない。 |
| PageZoomSliderPreference / PageZoomPreference | 既存AccessibilitySettingsと同じpublic constructor・delegate setter。新規setContrastOnlyは同じpackageにpublic追加。 |
| AndroidX Preference / Fragment | 固定依存のsnapshotはPreference 1.3.0-SNAPSHOT、Fragment 1.10.0-SNAPSHOT。正確なAAR取得が403で遮断され、**このsnapshotのメソッド型・設定画面の型チェックは未確認**。 |

## GN／リソース／JNI

- 新規EnvironmentZoom / Policy / Persistenceはcontent_full_javaのsources。
  Android UI、ContextUtils、ThreadUtils、Log、StrictModeContext、WindowAndroid、DisplayAndroidの所有targetは
  既存のbase_java／ui_no_recycler_view_java直接依存に含まれる。JDKのMap／Executor等にGN依存追加は不要。
- Profileを所有するchrome/browser/profiles/android:javaには、変更前からcontent_full_java／content_javaの
  直接依存がある。EnvironmentZoomはProfileやChromeのclassをimportしない。
  今回のGN変更はsources／resources追加のみで依存edgeは追加しないため、新たなGN循環は導入していない。
  完全なgn gen / gn checkを行ったという意味ではない。
- Accessibility lib_javaは既にcontent_full_java、prefs、user_prefs、Fragment、Preferenceへ直接依存する。
  EnvironmentZoomSettingsを同targetのsourcesへ追加。
- 日英のtitanium_zoom_strings.xmlはjava_resources sourcesへ追加。各R.stringはXMLと対応し、
  resetは直接resource dependencyのbrowser_ui_strings.grdにIDS_RESETが存在することを確認した。
  page_zoom_sectionは既存page_zoom_preference.xmlに存在する。AAPT/resource linkingは未実行。
- HostZoomMapImpl.javaは元からcontent_jni_headersのgenerate_jni sources。追加callbackやNativeMethodsも
  同じ生成対象で、新規Java4ファイル自体はJNI生成対象ではない。
- 実gniの命名に合わせ、HostZoomMapImpl_shared_jni.h／HostZoomMapImpl_jni.hを生成した。GN wrapperと同じprivate許可フラグも確認・指定した。
  新規getterはstd::string、private判定はbool、refreshはvoid。
  callbackはJavaの(WebContents,String)→double、(WebContents,String,double)→boolean。
  実生成のdescriptorはそれぞれ `(Lorg/chromium/content_public/browser/WebContents;Ljava/lang/String;)D` と
  `(Lorg/chromium/content_public/browser/WebContents;Ljava/lang/String;D)Z`。
- JavaRef<JWebContents>／JavaRef<JBrowserContextHandle>から既存JavaRef<jobject>への変換を実jni_zero headerで
  C++23 static_assertした。bool・double・std::stringの戻り型も確認した。
- NativeのGetJavaWebContents、FromJavaWebContents、IsBeingDestroyed、UpdateZoom、GetPath、HexEncode、
  GetParentOrOuterDocumentは公開宣言と照合。std::isfiniteにcmath、quiet_NaNにlimits、HexEncodeに
  string_number_conversions、文字列JNI変換にjni_stringを使用。
  Android専用JNI部分はIS_ANDROID内、非AndroidのGetEnvironmentZoomLevelはNaNを返す。
  Androidツールチェーンで.cc全体をコンパイルしたわけではない。

## 呼び出し・保存経路

native zoom lookup → Java.rendered → cached Binding／Policy.resolve。
途中のisDestroyed／getTopLevelNativeWindowはWebContentsAndroidの読み取りgetterへ戻るが、
IsBeingDestroyedとWindowAndroidのGetJavaObjectを返すだけでZoom／保存／refreshを呼ばない。
環境再評価のDisplayAndroid getterもzoom setterには接続していない。
初期移行・デフォルトJNI・プロフィールパスJNIはlookup経路から除いた。

native／Javaの操作 → 現在のBindingの環境のsite辞書だけ更新 → debounced worker保存 → posted refresh。
refreshAllはそれぞれのWebContentsの画面と同じprofile storeから読み取り、保存しない。
全WebContentsを再評価する点は残るが、別画面の辞書・デフォルトを変更する経路はない。
再入ガードを追加し、過去の破棄済みWebContentsはweak mapから除去する。
実Androidの構成変更・複数Activity・レンダラーの動作を検証済みとはしない。

## 実施済み／未確認

**実施済み**：実jni_zeroによる生成、実生成headerを含む6箇所のC++ JNI型アサーションのコンパイル、
中核Java 3クラスの実Android API＋固定Chromium宣言を使った限定コンパイル、
Policy481・bridge31（Android/JNIはdouble）・persistence13・revision metadata model5の検証、
Vanadium後の実パッチ適用と拒否、XML、シェル、actionlint、差分検証。

**ソース照合のみ**：Profile/Tab/Activityの全体、GN targetのsources/deps/resource edges、
native .cc bodyとライフサイクル呼び出し経路。Java限定コンパイルでChromium側の実装classとNullAwayはコンパイルしていない。
宣言投影にUnsupportedOperationExceptionのbodyを置いたものは型の照合専用で実行していない。
実Android APIはRobolectric android-all 4.4の39.7MiB artifact（HTTPS＋公開checksum確認）からplatform classを抽出したもの。
SDK 37での型・ツールチェーンの完全な確認ではない。

**未確認**：固定AndroidX AARでのEnvironmentZoomSettings型チェック、SDK37、NullAway、AAPT、gn gen/check、
Chromium Android clangでのhost_zoom_map_impl.cc／web_contents_impl.cc全体のコンパイル、APK・実機動作。
限定C++チェックはhost GCC14＋OpenJDK JNI header。Clang向け属性の警告があり、Android ABIリンク／動作確認は含まない。

固定AndroidXのREADME.chromiumにあるandroidx.devのsnapshot URLはproxyから403。
正確なAARを別バージョンへ置き換えて成功扱いにはしていない。追加取得許可が必要な宛先はandroidx.dev。
GN binaryと完全な生成済みsource/depsもない。公式の対象版Android build instructionsは空き100GB以上、RAM8GB以上
（16GB超推奨）を要件とする。本環境の/tmpは17GB程度であり、大規模取得は実行しなかった。
既存の準備済みツリーがあるなら、固定inputs確認→同じVanadium/Titaniumパッチ→gn gen/check→
JNI/Java/AAPTの対象target→対象C++ objectだけの順に確認し、APK target／フルビルドを起動しない。
実target名はそのツリーのgn desc／ninja -t targetsで確認する。JVMテストの成功だけで統合完了とは判断できない。


## 限定検証の再実行

以下は依存を自動取得せず、指定したローカル素材だけを使う。source-treeは固定版へVanadiumと本ブランチの
ズームパッチを適用済みのツリー。jni_zeroと必要なAPIファイル／headersも同じChromium版を用意する。

```sh
python3 tools/environment_zoom/tests/run_local_tests.py --ecj /path/to/ecj-3.40.0.jar
python3 tools/environment_zoom/tests/check_build_pin.py
python3 tools/environment_zoom/tests/check_android_api.py \
  --source-tree /path/to/patched-chromium \
  --android-jar /path/to/checksummed-android-api.jar \
  --ecj /path/to/ecj-3.40.0.jar --output-dir /tmp/zoom-api-review
python3 tools/environment_zoom/tests/check_jni_abi.py \
  --source-tree /path/to/patched-chromium \
  --jni-include /path/to/jdk-or-ndk-jni-headers --output-dir /tmp/zoom-jni-review
```

check_android_apiは実行不能な宣言投影を作るため、これをアプリのクラスパス／本番ツリーに混ぜてはいけない。
check_jni_abiの成功は関数のbody・リンク・Androidランタイムの検証ではない。
