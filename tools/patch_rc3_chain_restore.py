#!/usr/bin/env python3
"""rc3-4: 修复 rc3-3 补丁误删的容器链收尾行（会话页内容被钉回 280 的根因）"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

a = """    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"],',
    '  /* —— rc3：主页独立成页 —— */',"""
assert s.count(a) == 1, 'anchor'
s = s.replace(a, """    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_sectionHeader"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',
    '  /* —— rc3：主页独立成页 —— */',""", 1)

open(F, 'w', encoding='utf-8').write(s)
print('容器链收尾行已恢复 OK:', len(s), 'bytes')
