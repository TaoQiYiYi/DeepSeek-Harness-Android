#!/usr/bin/env python3
"""rc3-2 polish: 会话选择页内容撑满页宽"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()
a = "    '  html body[data-dshm-sessions=\"1\"] .pI_x6G_frame .pI_x6G_sidebarCol { width: 100% !important; max-width: none !important; box-shadow: none !important; }',"
assert s.count(a) == 1, 'anchor'
s = s.replace(a, a + """
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_listArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_treeBody"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_list"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_groupSection"],',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_sessionRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_newSession"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',""", 1)
open(F, 'w', encoding='utf-8').write(s)
print('列表页润色 OK')
