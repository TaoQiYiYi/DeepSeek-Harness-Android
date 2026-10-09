#!/bin/sh
# Build the DSH Android port APK inside the Minis Alpine sandbox.
set -e

P=/var/minis/workspace/dshport
B=/opt/build/dshport
AJAR=/opt/android/android30.jar
AAPT2=/opt/tx/aapt2
D8JAR=/opt/tx/d8x/data/data/com.termux/files/usr/share/java/d8.jar
APKSIGNER=/opt/tx/apkx/data/data/com.termux/files/usr/share/java/apksigner.jar
KS=/opt/build/dsh.keystore
KSPASS=dshport
TARGET_SDK=${TARGET_SDK:-28}
VERSION_NAME=${VERSION_NAME:-0.1.0}
VERSION_CODE=${VERSION_CODE:-10}
OUTNAME=${OUTNAME:-DSHPort}

mkdir -p /opt/build "$P/out"
rm -rf "$B"
mkdir -p "$B/classes" "$B/dex" "$B/apk" "$B/gen"

echo "== 1/6 aapt2 compile =="
"$AAPT2" compile --dir "$P/app/res" -o "$B/res.zip"

echo "== 2/6 aapt2 link (targetSdk=$TARGET_SDK) =="
"$AAPT2" link -o "$B/base.apk" -I "$AJAR" \
  --manifest "$P/app/AndroidManifest.xml" \
  --java "$B/gen" \
  --min-sdk-version 26 --target-sdk-version "$TARGET_SDK" \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" \
  "$B/res.zip"

echo "== 3/6 javac =="
rg --files "$P/app/java" "$B/gen" -g '*.java' > "$B/sources.txt"
wc -l < "$B/sources.txt"
if ! javac -source 8 -target 8 -encoding UTF-8 -nowarn -bootclasspath "$AJAR" \
      -d "$B/classes" @"$B/sources.txt" 2> "$B/javac.err"; then
  echo "-- bootclasspath 模式失败，改用 classpath 模式 --"
  cat "$B/javac.err"
  javac -source 8 -target 8 -encoding UTF-8 -nowarn -classpath "$AJAR" \
    -d "$B/classes" @"$B/sources.txt"
fi

echo "== 4/6 d8 =="
(cd "$B/classes" && jar cf "$B/classes.jar" .)
java -cp "$D8JAR" com.android.tools.r8.D8 --lib "$AJAR" --min-api 26 \
  --output "$B/dex" "$B/classes.jar"
ls -la "$B/dex"

echo "== 5/6 package =="
cd "$B/apk"
cp "$B/base.apk" app-unsigned.apk
cp "$B/dex/classes.dex" .
zip -q -X app-unsigned.apk classes.dex
if [ -f "$P/app/assets/runtime.zip" ]; then
  echo "adding runtime.zip (stored, no recompression)…"
  mkdir -p assets
  cp "$P/app/assets/runtime.zip" assets/runtime.zip
  zip -q -X -0 app-unsigned.apk assets/runtime.zip
  if [ -f "$P/app/assets/runtime.size" ]; then
    cp "$P/app/assets/runtime.size" assets/runtime.size
    zip -q -X app-unsigned.apk assets/runtime.size
  fi
fi
if [ -f "$P/app/assets/mobile.js" ]; then
  mkdir -p assets
  cp "$P/app/assets/mobile.js" assets/mobile.js
  zip -q -X app-unsigned.apk assets/mobile.js
fi
ls -la app-unsigned.apk

echo "== 6/6 sign =="
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore "$KS" -alias dsh -keyalg RSA -keysize 2048 -validity 3650 \
    -storepass "$KSPASS" -keypass "$KSPASS" -dname "CN=DSH Port,O=Personal"
fi
java -jar "$APKSIGNER" sign --ks "$KS" --ks-pass "pass:$KSPASS" --key-pass "pass:$KSPASS" \
  --out "$B/$OUTNAME-$VERSION_NAME.apk" app-unsigned.apk
java -jar "$APKSIGNER" verify --print-certs "$B/$OUTNAME-$VERSION_NAME.apk" | head -6
cp "$B/$OUTNAME-$VERSION_NAME.apk" "$P/out/"
ls -la "$P/out/"
echo "DONE: $P/out/$OUTNAME-$VERSION_NAME.apk"
