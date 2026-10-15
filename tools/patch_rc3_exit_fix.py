#!/usr/bin/env python3
"""rc3-1 fix2: 退出优先用侧栏「新会话」主按钮（实测有效），图标栏按钮作后备"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()
a = """      var t = document.querySelector('button[aria-label="新建会话"]') || document.querySelector('[class*="hHd-Xa_newSession"]');"""
assert s.count(a) == 1, 'anchor'
s = s.replace(a, """      var t = document.querySelector('[class*="hHd-Xa_newSession"]') || document.querySelector('button[aria-label="新建会话"]');""", 1)
open(F, 'w', encoding='utf-8').write(s)
print('退出优先级修复 OK')
