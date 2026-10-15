#!/usr/bin/env python3
"""rc3-1 fix: 健壮性——对话页保持「侧栏必收起」不变量；退出前先收起侧栏"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

# 1) syncChatPage：已处于对话页时也校正侧栏（防止异常态残留）
a = """      } else if (open && cur) {
        ensureChatBack();
      } else if (!open && cur) {"""
assert s.count(a) == 1, 'anchor1'
s = s.replace(a, """      } else if (open && cur) {
        collapseSidebarIfOpen();
        ensureChatBack();
      } else if (!open && cur) {""", 1)

# 2) exitChatToHome：先收起侧栏再点新建会话，且优先用图标栏按钮
a = """  function exitChatToHome() {
    try {
      var t = document.querySelector('[class*="hHd-Xa_newSession"]') || document.querySelector('button[aria-label="新建会话"]');
      if (t) { t.click(); return true; }
    } catch (e) {}
    return false;
  }"""
assert s.count(a) == 1, 'anchor2'
s = s.replace(a, """  function exitChatToHome() {
    try {
      var frame = document.querySelector('.pI_x6G_frame');
      if (frame && !frame.hasAttribute('data-sidebar-collapsed')) collapseSidebarIfOpen();
      var t = document.querySelector('button[aria-label="新建会话"]') || document.querySelector('[class*="hHd-Xa_newSession"]');
      if (t) { t.click(); return true; }
    } catch (e) {}
    return false;
  }""", 1)

open(F, 'w', encoding='utf-8').write(s)
print('健壮性修复 OK:', len(s), 'bytes')
