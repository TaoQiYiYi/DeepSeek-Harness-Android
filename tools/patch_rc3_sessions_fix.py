#!/usr/bin/env python3
"""rc3-2 fix: 提升会话选择页 CSS 优先级（旧抽屉规则 .frame:not(...) .sidebarCol = 3 类级，需 4 级）"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()
a = "html body[data-dshm-sessions=\"1\"] .pI_x6G_sidebarCol { width: 100%"
assert s.count(a) == 1, 'anchor'
s = s.replace(a, "html body[data-dshm-sessions=\"1\"] .pI_x6G_frame .pI_x6G_sidebarCol { width: 100%", 1)
open(F, 'w', encoding='utf-8').write(s)
print('优先级修复 OK')
