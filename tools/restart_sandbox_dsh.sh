#!/bin/sh
cd /opt/dshstage || exit 1
[ -f /opt/tx/flock-orig.js ] || cp node_modules/@deepseek-ai/node-addon-system/lib/flock.js /opt/tx/flock-orig.js
cp /opt/tx/flock-patched.js node_modules/@deepseek-ai/node-addon-system/lib/flock.js
pkill -f 'deepseek-ai/dsh/lib/bin.js' 2>/dev/null
pkill -f 'node_modules/.bin/dsh' 2>/dev/null
sleep 1
nohup env DSH_JS_INTERNALS_FALLBACK=1 node --expose-internals ./node_modules/@deepseek-ai/dsh/lib/bin.js web --no-open --port 3089 > /tmp/dsh3.log 2>&1 &
sleep 22
echo '--- 启动日志 ---'
head -80 /tmp/dsh3.log
echo '--- HTTP ---'
curl -s -o /dev/null -w 'HTTP %{http_code}\n' --max-time 6 http://127.0.0.1:3080/
