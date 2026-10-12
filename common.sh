export SCRIPT_DIR=$(realpath $(dirname $0))

replace() {
    export org=$2 new=$3
    find $1 -type f -exec sed -i 's@'$org'@'$new'@g' {} \;
}

set_keys() {
    mkdir -p $SCRIPT_DIR/keys
    echo $LOCAL_TEST_JKS | base64 -d > $SCRIPT_DIR/keys/local.properties
    echo $STORE_TEST_JKS | base64 -d > $SCRIPT_DIR/keys/test.jks
    unset LOCAL_TEST_JKS
    unset STORE_TEST_JKS
}

sign_apk() {
    local apksigner
    apksigner=$(find "$ANDROID_HOME/build-tools" -name apksigner | sort -V | tail -n 1)
    if [ ! -x "$apksigner" ]; then echo "ERROR: apksigner was not found." >&2; exit 1; fi
    source "$SCRIPT_DIR/keys/local.properties" || exit 1
    if [ -z "$storePassword" ] || [ -z "$keyPassword" ] || [ -z "$keyAlias" ]; then
        echo "ERROR: APK signing properties are missing required values." >&2
        exit 1
    fi
    "$apksigner" sign --verbose --ks "$SCRIPT_DIR/keys/test.jks" --ks-pass "pass:$storePassword" --key-pass "pass:$keyPassword" --ks-key-alias "$keyAlias" --out "$2" "$1" || exit 1
    "$apksigner" verify "$2" || exit 1
}

sign_aab() {
    source "$SCRIPT_DIR/keys/local.properties" || exit 1
    jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore "$SCRIPT_DIR/keys/test.jks" -storepass "$storePassword" -keypass "$keyPassword" -signedjar "$2" "$1" "$keyAlias" || exit 1
}

version_lt() {
  [ "$1" != "$2" ] && [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n1)" = "$1" ]
}
