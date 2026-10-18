# Versanium repository / runner policy（2026-10-18）

## Repository roles

`Nvoid911-Lab/Versanium` を今後の **Primary / Source of Truth** とする。

`Nvoid911/Versanium` は **Backup / Secondary** として保持し、Lab側の移行・ビルド・実機検証・Release経路が十分に確認できた後にArchiveする方針とする。

通常の同期方向は以下とする。

```text
Nvoid911-Lab/Versanium
        ↓
Nvoid911/Versanium
```

PrimaryとSecondaryで独立した開発履歴を進めない。force pushやhistory rewriteは行わない。

## GitHub Actions runner selection

Versanium Buildは `workflow_dispatch` の `runner_provider` choice inputから、次のreview済みrunnerのみ選択できる。

| Choice | Runner label |
|---|---|
| `blacksmith` | `blacksmith-8vcpu-ubuntu-2404` |
| `sengi` | `sengi-standard-8-ubuntu-2404` |

自由入力のrunner labelは許可しない。`runs-on` はchoice→labelの固定mapから選択し、未定義値は実在しない `versanium-runner-not-allowed` へfail-closedする。

Build job自体は次の2repositoryのみ許可する。

- `Nvoid911-Lab/Versanium`（Primary）
- `Nvoid911/Versanium`（Backup / Secondary）

これにより、PrimaryでBlacksmith/Sengiを利用状況・無料枠・必要に応じた課金方針に応じて選択できる。Backup側でもTest build経路は保持できるが、正式なSource of TruthはLabのみとする。

## Production Release restriction

Production ReleaseはPrimaryである次のrepositoryだけに限定する。

```text
Nvoid911-Lab/Versanium
```

正式版のstage / publish / attestは、以下の全条件を満たす場合のみ許可する。

- Test buildではない
- `VERSANIUM_RELEASE_APPROVED == 'true'`
- `github.repository == 'Nvoid911-Lab/Versanium'`

現在は引き続き `VERSANIUM_RELEASE_APPROVED: 'false'` とし、実機Testと明示承認前のProduction Releaseを禁止する。

## Test / signing policy

以下は変更しない。

- Versanium Test package: `io.github.nvoid911.versanium.test`
- Legacy Titanium F11 Test package: `io.github.nvoid911.titanium.f11test`
- `LOCAL_TEST_JKS`
- `STORE_TEST_JKS`
- 既存のF11 test compilation/signing pathを利用したVersanium Test build
- Test artifact name: `Versanium-Test`

Production package identity / signing identity / update compatibilityは、正式Release前に別途監査する。

## CircleCI policy

CircleCIは検証用途を終了し、今後のVersanium buildでは使用しない。

Primary/開発branchから `.circleci/config.yml` を削除し、GitHub Actions + Blacksmith/Sengiをbuild経路とする。CircleCI側のGitHub連携・project接続も解除する。

過去のCircleCI検証branchやcommitがhistory上に残ることは許容するが、active configuration / triggerとしては使用しない。

## Build前に必ず並行して確認する項目

今後のVersanium Test buildを開始する前に、runner選択だけでなく次の3系統を同時に確認する。

1. **Titanium upstream version / source alignment**
   - `jqssun/android-titanium-browser` の最新version・commitを確認する。
   - Versaniumの現在pinとの差分を確認する。
   - 必要なら `migration/versanium` にupstream変更を取り込んでからbuildする。

2. **Build optimization**
   - Chromium/Vanadium buildの所要時間・runner resource・不要な再処理を確認する。
   - Blacksmith/Sengiの無料枠と必要に応じた課金を踏まえ、無駄なbuildを避ける。
   - build前static validationを優先し、runner消費はユーザーの明示実行まで開始しない。

3. **YouTube PiP investigation**
   - Titanium/Chromiumで確認されているYouTube PiP問題の調査・修正検討を並行して維持する。
   - PiP修正候補をbuildへ入れる場合は、upstreamとの差分・Versanium固有変更・回帰リスクを先に確認する。

これらは別々の作業ではあるが、次回Test build candidateを決める際には必ず同じpre-build判断に含める。

## Execution rule

ChatGPTが要件・upstream・build・PiP・runner方針を整理し、repository変更とstatic validationを行う。

GitHub Actionsのrunnerを実際に消費する操作は、ユーザーが明示的にbuild実行を指示するまで開始しない。

Test build成功後はGalaxy S23 / Samsung DeXで実機検証を行い、その結果を確認するまでは `migration/versanium → main` の機能移行、Production Release、tag作成を進めない。
