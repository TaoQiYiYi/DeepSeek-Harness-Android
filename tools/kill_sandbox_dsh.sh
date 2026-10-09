#!/bin/sh
# 停掉沙箱内遗留的 dsh 测试服务器（避免占用 127.0.0.1:3080）
pkill -f 'deepseek-ai/dsh/lib/bin.js' 2>/dev/null
pkill -f 'node_modules/.bin/dsh' 2>/dev/null
sleep 1
echo '--- 端口检查 ---'
curl -s -o /dev/null --max-time 4 -w 'HTTP %{http_code}\n' http://127.0.0.1:3080/ || echo '端口 3080 已空闲（连接被拒绝）'
