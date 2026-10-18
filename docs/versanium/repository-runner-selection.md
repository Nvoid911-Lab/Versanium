# Repository別runner選択（2026-10-18）

Primaryを唯一のSource of Truthとし、同一のbuild.ymlをSecondaryへ通常同期する。

| Repository | Runner |
|---|---|
| Nvoid911/Versanium | sengi-standard-8-ubuntu-2404 |
| Nvoid911-Lab/Versanium | blacksmith-8vcpu-ubuntu-2404 |

Sengi labelは既存履歴 `069b1e58ed7d9f97e30bfcc6c2e4b4aafb8f212b`（Use Sengi 8 vCPU runner by default）のbuild.ymlで確認した。Blacksmith labelは作業前のmigration/versaniumで確認した。現在のrunner登録状態・容量・権限は実行確認していない。

Workflowの `runs-on` は `fromJSON` によるrepository→label対応表を `github.repository` で参照する。自由入力のrunner inputは廃止した。将来のrunner切替は、この対応表をPrimaryでレビュー・変更してSecondaryへ同期する。各repositoryで毎回修正する必要はない。

build jobの `if` で上記2repositoryのみ許可する。job条件はrunner割当より先に評価されるため、想定外repositoryではjobをスキップしrunnerを確保しない。これは「失敗jobを実行する」のではなく「Buildを実行させない」fail-closedである。対応表にないrepositoryのruns-on評価にも、実runnerではない拒否用ラベル `versanium-repository-not-allowed` を設定する。Blacksmith等への既定fallbackは設けない。

## 保持事項

- workflow_dispatchのみ。runner input以外のTest inputは変更なし。
- Test package `io.github.nvoid911.versanium.test` と従来F11 package `io.github.nvoid911.titanium.f11test` の分離、表示名、実アイコン、正式版identity経路は変更なし。
- `VERSANIUM_RELEASE_APPROVED: 'false'` を維持。正式版のstage/publish/attestは非Test・明示承認true・Primary repository一致の3条件を維持し、Secondaryは許可しない。
- Build step、署名設定、LOCAL_TEST_JKS/STORE_TEST_JKS等のSecrets参照は作業前と一致。

## 検証

- migration tests 13件PASS。実YAMLから対応表とjob条件を読み、Primary→Sengi、Secondary→Blacksmith、想定外3repository→job許可なし／拒否labelをローカル検証した。Actions式全体の実行エンジンによる評価ではない。
- Release guardの正確な3条件と承認false、Test package分離、Secrets参照を回帰テストで検証。
- actionlint v1.7.7 PASS。
- YAML validation / 全Workflow inline shellのbash構文検証 PASS（migration tests）。
- bash -n build.sh patch.sh common.sh .github/scripts/check-signing-properties.sh PASS。
- git diff --check PASS。
- 作業前後のYAMLを比較し、全Build steps・global permissions・envが同一であることを確認。identity・署名・アイコンの実装差分なし。

GitHub Actionsは一切実行していない。dispatch、run開始、rerun、job rerun、runnerを消費する操作、build.sh実行は行っていない。実際のSengi/Blacksmith割当・起動はユーザーの制限解除後の手動実行で確認する。

変更ファイルは `.github/workflows/build.yml`、`tools/versanium/tests/test_migration.py`、本書のみ。migration/versaniumだけに通常pushし、Primary/Secondaryを同一SHAに保つ。main merge、Release、tag、force push、履歴書換えは行わない。
