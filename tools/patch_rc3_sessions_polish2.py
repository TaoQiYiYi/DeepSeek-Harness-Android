#!/usr/bin/env python3
"""rc3-2 polish2: 撑宽抽屉整个容器链（hHd-Xa_root 限宽 280 是瓶颈）"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()
a = "    '  html body[data-dshm-sessions=\"1\"] [class*=\"hHd-Xa_newSession\"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',"
assert s.count(a) == 1, 'anchor'
s = s.replace(a, a + """
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_root"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_logoRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_regionArea"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_panelList"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_panelRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_footArea"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_footerActions"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_settingsArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_sectionHeader"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',""", 1)
open(F, 'w', encoding='utf-8').write(s)
print('容器链撑宽 OK')
