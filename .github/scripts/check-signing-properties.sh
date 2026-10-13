#!/usr/bin/env bash
# common.sh sources local.properties as Bash, not Java properties.
# Use assignments named storePassword, keyPassword and keyAlias. Quote values
# containing spaces or shell metacharacters. Never print the decoded file.
set +x
set -euo pipefail
umask 077

temp_dir=$(mktemp -d)
trap 'rm -rf -- "$temp_dir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
properties="$temp_dir/local.properties"
missing=7
failed=0

if [[ -z ${LOCAL_TEST_JKS:-} ]]; then
    printf '%s\n' 'LOCAL_TEST_JKS: 不足'
    failed=1
else
    printf '%s\n' 'LOCAL_TEST_JKS: 設定済み'
    if ! printf '%s' "$LOCAL_TEST_JKS" | base64 --decode > "$properties" 2>/dev/null; then
        printf '%s\n' 'Base64復号: 失敗'
        failed=1
    else
        printf '%s\n' 'Base64復号: 成功'
        if ! bash --noprofile --norc -n "$properties" >/dev/null 2>&1; then
            printf '%s\n' 'Bash設定形式: 不一致' '設定ファイル読み込み: 失敗'
            failed=1
        else
            # A separate shell mirrors common.sh's source operation. Suppress
            # ALL output, including source diagnostics and tracing enabled by
            # the file itself. Return only a status bitmask, never values.
            status=0
            env -u LOCAL_TEST_JKS -u storePassword -u keyPassword -u keyAlias \
                bash --noprofile --norc -c '
                    set +x
                    set +e
                    set +u
                    source "$1"
                    loaded=$?
                    set +x
                    set +e
                    set +u
                    result=16
                    [[ -n ${storePassword:-} ]] || result=$((result | 1))
                    [[ -n ${keyPassword:-} ]] || result=$((result | 2))
                    [[ -n ${keyAlias:-} ]] || result=$((result | 4))
                    [[ $loaded -eq 0 ]] || result=$((result | 8))
                    exit "$result"
                ' signing-properties "$properties" >/dev/null 2>&1 || status=$?
            if (( status >= 16 && status <= 31 )); then
                missing=$((status & 7))
                if (( status & 8 )); then
                    printf '%s\n' 'Bash設定形式: 不一致' '設定ファイル読み込み: 失敗'
                    failed=1
                else
                    printf '%s\n' 'Bash設定形式: 一致' '設定ファイル読み込み: 成功'
                fi
            else
                printf '%s\n' 'Bash設定形式: 不一致' '設定ファイル読み込み: 失敗'
                failed=1
            fi
        fi
    fi
fi

for entry in storePassword:1 keyPassword:2 keyAlias:4; do
    name=${entry%:*}
    bit=${entry#*:}
    if (( missing & bit )); then
        printf '%s: 不足\n' "$name"
    else
        printf '%s: 設定済み\n' "$name"
    fi
done

if (( failed || missing )); then
    printf '%s\n' '署名設定の確認: 失敗。LOCAL_TEST_JKSにはBash変数代入形式を使用してください。'
    exit 1
fi
printf '%s\n' '署名設定の確認: 成功'
