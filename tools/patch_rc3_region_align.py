#!/usr/bin/env python3
"""rc3-5: 会话页「工作区」区块与顶部按钮对齐（消除右侧 31px 缺口）
根因：bhn1Oq_root 的 padding-right:12 + 列表层负 margin 出血未抵消 → 列表行右缘比按钮短 31px
配方（424 实测）：bhn1Oq_root pr:0 + 列表层 mr:0 + groupSection width:+18px → 行右缘 413 vs 按钮 414 ✓
"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

a = "    '  html body[data-dshm-sessions=\"1\"] [class*=\"bhn1Oq_sectionHeader\"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',"
assert s.count(a) == 1, 'anchor'
s = s.replace(a, a + """
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"] { padding-right: 0 !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_listArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_treeBody"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_list"] { margin-right: 0 !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_groupSection"] { width: calc(100% + 18px) !important; }',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_sessionRow"],',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_projectRow"] { margin-right: 0 !important; }',""", 1)

open(F, 'w', encoding='utf-8').write(s)
print('rc3-5 工作区对齐补丁 OK:', len(s), 'bytes')
