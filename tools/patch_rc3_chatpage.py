#!/usr/bin/env python3
"""rc3-1: 对话页独立成页（chat as standalone page）
- 进入对话（header 出现 对话/轨迹 tab）→ body[data-dshm-chat=1]：侧栏隐藏、对话占满全屏
- 注入左上角返回键 → 退出到首页草稿态
- 抽屉里点会话 → 自动收抽屉（进入对话页时统一收起）
- 系统返回键 __dshmBack：对话页中先关右栏浮层，再退出对话页
"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

# ---------- A) CSS：媒体块末尾追加对话页规则 ----------
a = "    '  #dshm-update-bar { display: flex !important; }',\n    '}',"
assert s.count(a) == 1, 'anchor A'
s = s.replace(a, """    '  #dshm-update-bar { display: flex !important; }',
    '  /* —— rc3：对话页独立成页 —— */',
    '  html body[data-dshm-chat="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-chat="1"] .pI_x6G_sidebarCol { display: none !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_header"] { position: relative !important; padding-left: 50px !important; }',
    '  #dshm-chat-back { position: absolute !important; left: 7px !important; top: 50% !important; transform: translateY(-50%) !important; width: 36px !important; height: 36px !important; min-width: 36px !important; min-height: 36px !important; padding: 0 !important; margin: 0 !important; border: none !important; border-radius: 50% !important; background: transparent !important; color: inherit !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 6 !important; }',
    '  #dshm-chat-back:active { background: rgba(128, 128, 128, 0.22) !important; }',
    '}',""", 1)

# ---------- B) JS：对话页模块（插在「侧栏遮罩点击收起」注释前） ----------
a = "  /* ---------------- 侧栏遮罩点击收起（原有行为） ---------------- */"
assert s.count(a) == 1, 'anchor B'
s = s.replace(a, """  /* ---------------- rc3：对话页独立成页 ---------------- */
  function chatViewOpen() {
    try { return !!document.querySelector('[class*="wSkVaW_header"] [class*="wSkVaW_tab"]'); } catch (e) { return false; }
  }

  function collapseSidebarIfOpen() {
    try {
      var frame = document.querySelector('.pI_x6G_frame');
      if (frame && !frame.hasAttribute('data-sidebar-collapsed')) {
        var tgl = collapseToggle();
        if (tgl) tgl.click();
      }
    } catch (e) {}
  }

  function exitChatToHome() {
    try {
      var t = document.querySelector('[class*="hHd-Xa_newSession"]') || document.querySelector('button[aria-label="新建会话"]');
      if (t) { t.click(); return true; }
    } catch (e) {}
    return false;
  }

  function ensureChatBack() {
    try {
      var hdr = document.querySelector('[class*="wSkVaW_header"]');
      if (!hdr) return;
      var b = document.getElementById('dshm-chat-back');
      if (b && b.parentNode !== hdr) { try { b.parentNode.removeChild(b); } catch (e) {} b = null; }
      if (b) return;
      b = document.createElement('button');
      b.id = 'dshm-chat-back';
      b.type = 'button';
      b.setAttribute('aria-label', '返回');
      b.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M15.2 19.2 8 12l7.2-7.2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      b.addEventListener('click', function (ev) {
        ev.preventDefault(); ev.stopPropagation();
        exitChatToHome();
      }, true);
      hdr.insertBefore(b, hdr.firstChild);
    } catch (e) {}
  }

  function syncChatPage() {
    try {
      if (window.innerWidth > 720) {
        if (document.body.getAttribute('data-dshm-chat') === '1') document.body.removeAttribute('data-dshm-chat');
        return;
      }
      var open = chatViewOpen();
      var cur = document.body.getAttribute('data-dshm-chat') === '1';
      if (open && !cur) {
        document.body.setAttribute('data-dshm-chat', '1');
        collapseSidebarIfOpen();
        ensureChatBack();
      } else if (open && cur) {
        ensureChatBack();
      } else if (!open && cur) {
        document.body.removeAttribute('data-dshm-chat');
      }
    } catch (e) {}
  }

""" + a, 1)

# ---------- C) __dshmBack：对话页中先关右栏浮层，再退出对话页 ----------
a = "      if (window.__dshmPluginMobile) return false;"
assert s.count(a) == 1, 'anchor C'
s = s.replace(a, """      if (document.body.getAttribute('data-dshm-chat') === '1') {
        var cf = document.querySelector('.pI_x6G_frame');
        if (cf && !cf.hasAttribute('data-rightbar-collapsed')) {
          var rb = document.querySelector('button[aria-label*="右侧"]');
          if (rb) { rb.click(); return true; }
        }
        exitChatToHome();
        return true;
      }
      if (window.__dshmPluginMobile) return false;""", 1)

# ---------- D) tick()：加入 syncChatPage ----------
a = "    try { plusMenuKeeper(); } catch (e) {}\n  }"
assert s.count(a) == 1, 'anchor D'
s = s.replace(a, "    try { plusMenuKeeper(); } catch (e) {}\n    try { syncChatPage(); } catch (e) {}\n  }", 1)

open(F, 'w', encoding='utf-8').write(s)
print('rc3-1 对话页独立成页 补丁 OK:', len(s), 'bytes')
