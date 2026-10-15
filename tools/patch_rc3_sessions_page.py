#!/usr/bin/env python3
"""rc3-2: 会话选择页独立成页（session list as standalone page）
- 侧栏展开（原 86vw 抽屉）→ body[data-dshm-sessions=1]：占满全屏，成为「会话选择页」
- 点「新会话」按钮/列表项 → 自动收起回到首页草稿
- 对话页优先：对话页打开时列表页标志强制清除（避免列表盖住对话）
"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

# ---------- A) CSS：对话页规则后追加会话选择页规则 ----------
a = "    '  #dshm-chat-back:active { background: rgba(128, 128, 128, 0.22) !important; }',\n    '}',"
assert s.count(a) == 1, 'anchor A'
s = s.replace(a, """    '  #dshm-chat-back:active { background: rgba(128, 128, 128, 0.22) !important; }',
    '  /* —— rc3：会话选择页独立成页 —— */',
    '  html body[data-dshm-sessions="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-sessions="1"] .pI_x6G_sidebarCol { width: 100% !important; max-width: none !important; box-shadow: none !important; }',
    '}',""", 1)

# ---------- B) JS：会话选择页模块 ----------
a = "  /* ---------------- 侧栏遮罩点击收起（原有行为） ---------------- */"
assert s.count(a) == 1, 'anchor B'
s = s.replace(a, """  /* ---------------- rc3：会话选择页独立成页 ---------------- */
  function syncSessionsPage() {
    try {
      if (window.innerWidth > 720) {
        if (document.body.getAttribute('data-dshm-sessions') === '1') document.body.removeAttribute('data-dshm-sessions');
        return;
      }
      if (document.body.getAttribute('data-dshm-chat') === '1') {
        if (document.body.getAttribute('data-dshm-sessions') === '1') document.body.removeAttribute('data-dshm-sessions');
        return;
      }
      var frame = document.querySelector('.pI_x6G_frame');
      var open = !!frame && !frame.hasAttribute('data-sidebar-collapsed');
      var cur = document.body.getAttribute('data-dshm-sessions') === '1';
      if (open && !cur) document.body.setAttribute('data-dshm-sessions', '1');
      else if (!open && cur) document.body.removeAttribute('data-dshm-sessions');
    } catch (e) {}
  }

  function bindSessionPageActions() {
    if (window.__dshmSessBound) return;
    window.__dshmSessBound = true;
    document.addEventListener('click', function (ev) {
      try {
        if (window.innerWidth > 720) return;
        if (document.body.getAttribute('data-dshm-sessions') !== '1') return;
        var t = ev.target;
        if (!t || !t.closest) return;
        var draft = !!t.closest('[class*="hHd-Xa_newSession"]') ||
          !!(t.closest('[class*="YDXeBa_sessionRow"]') && ((t.closest('[class*="YDXeBa_sessionRow"]').textContent || '').indexOf('新会话') === 0));
        if (draft) setTimeout(function () { try { collapseSidebarIfOpen(); } catch (e) {} }, 80);
      } catch (e) {}
    }, true);
  }

""" + a, 1)

# ---------- C) tick()：加入会话选择页同步 ----------
a = "    try { syncChatPage(); } catch (e) {}\n  }"
assert s.count(a) == 1, 'anchor C'
s = s.replace(a, "    try { syncChatPage(); } catch (e) {}\n    try { syncSessionsPage(); } catch (e) {}\n    try { bindSessionPageActions(); } catch (e) {}\n  }", 1)

open(F, 'w', encoding='utf-8').write(s)
print('rc3-2 会话选择页独立成页 补丁 OK:', len(s), 'bytes')
