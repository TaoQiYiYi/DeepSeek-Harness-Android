#!/usr/bin/env python3
"""rc3-2 fix: 新会话行点击后收起抽屉改为「立即 + tick 持续校正 2s」，避免与 App 选中处理竞态"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

a = "        if (draft) setTimeout(function () { try { collapseSidebarIfOpen(); } catch (e) {} }, 80);"
assert s.count(a) == 1, 'anchor1'
s = s.replace(a, "        if (draft) { try { collapseSidebarIfOpen(); } catch (e) {} window.__dshmCollapseUntil = Date.now() + 2000; }", 1)

a = "    try { bindSessionPageActions(); } catch (e) {}\n  }"
assert s.count(a) == 1, 'anchor2'
s = s.replace(a, """    try { bindSessionPageActions(); } catch (e) {}
    try { if (window.__dshmCollapseUntil && Date.now() < window.__dshmCollapseUntil && document.body.getAttribute('data-dshm-chat') !== '1') collapseSidebarIfOpen(); } catch (e) {}
  }""", 1)

open(F, 'w', encoding='utf-8').write(s)
print('收抽屉竞态修复 OK:', len(s), 'bytes')
