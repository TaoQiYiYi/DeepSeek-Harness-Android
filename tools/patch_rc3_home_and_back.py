#!/usr/bin/env python3
"""rc3-3: ①主页独立成页(隐藏图标栏+注入菜单键) ②对话页「⋯」钉到右侧 ③__dshmBack 关闭按钮匹配修复"""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

# ---------- A) CSS：主页模式 + ⋯ 靠右 ----------
a = """    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_sectionHeader"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',
    '}',"""
assert s.count(a) == 1, 'anchor A'
s = s.replace(a, """    '  /* —— rc3：主页独立成页 —— */',
    '  html body[data-dshm-home="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-home="1"] .pI_x6G_sidebarCol { display: none !important; }',
    '  html body[data-dshm-home="1"] [class*="wSkVaW_header"] { position: relative !important; }',
    '  #dshm-home-menu { position: absolute !important; left: 7px !important; top: 50% !important; transform: translateY(-50%) !important; width: 36px !important; height: 36px !important; min-width: 36px !important; min-height: 36px !important; padding: 0 !important; margin: 0 !important; border: none !important; border-radius: 50% !important; background: transparent !important; color: inherit !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 6 !important; }',
    '  #dshm-home-menu:active { background: rgba(128, 128, 128, 0.22) !important; }',
    '  /* —— rc3：对话页「⋯」贴右侧栏切换按钮 —— */',
    '  html body[data-dshm-chat="1"] [aria-label="更多操作"] { position: absolute !important; right: 48px !important; top: 12px !important; }',
    '}',""", 1)

# ---------- B) JS：主页模块 ----------
a = "  /* ---------------- 侧栏遮罩点击收起（原有行为） ---------------- */"
assert s.count(a) == 1, 'anchor B'
s = s.replace(a, """  /* ---------------- rc3：主页独立成页 ---------------- */
  function removeHomeMenu() {
    try { var b = document.getElementById('dshm-home-menu'); if (b && b.parentNode) b.parentNode.removeChild(b); } catch (e) {}
  }

  function ensureHomeMenu() {
    try {
      var hdr = document.querySelector('[class*="wSkVaW_header"]');
      if (!hdr) return;
      var b = document.getElementById('dshm-home-menu');
      if (b && b.parentNode !== hdr) { removeHomeMenu(); b = null; }
      if (b) return;
      b = document.createElement('button');
      b.id = 'dshm-home-menu';
      b.type = 'button';
      b.setAttribute('aria-label', '会话列表');
      b.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6.5h16M4 12h16M4 17.5h16" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"/></svg>';
      b.addEventListener('click', function (ev) {
        ev.preventDefault(); ev.stopPropagation();
        try {
          var hb = document.querySelector('button[aria-label="打开侧边栏"]');
          if (hb) hb.click();
        } catch (e) {}
      }, true);
      hdr.insertBefore(b, hdr.firstChild);
    } catch (e) {}
  }

  function syncHomePage() {
    try {
      if (window.innerWidth > 720) {
        if (document.body.getAttribute('data-dshm-home') === '1') document.body.removeAttribute('data-dshm-home');
        removeHomeMenu();
        return;
      }
      var chat = document.body.getAttribute('data-dshm-chat') === '1';
      var sess = document.body.getAttribute('data-dshm-sessions') === '1';
      var want = !chat && !sess;
      var cur = document.body.getAttribute('data-dshm-home') === '1';
      if (want && !cur) document.body.setAttribute('data-dshm-home', '1');
      else if (!want && cur) document.body.removeAttribute('data-dshm-home');
      if (want) ensureHomeMenu(); else removeHomeMenu();
    } catch (e) {}
  }

""" + a, 1)

# ---------- C) __dshmBack：匹配 textContent 的「关闭/close」+ 常见取消文案 + 遮罩兜底 ----------
a = """          if (t === '✕' || t === '×' || al.indexOf('关闭') >= 0 || al.toLowerCase().indexOf('close') >= 0) {
            btns[i].click();
            return true;
          }
        }
        return false;
      }"""
assert s.count(a) == 1, 'anchor C'
s = s.replace(a, """          var tl = t.toLowerCase();
          var all = al.toLowerCase();
          if (t === '✕' || t === '×' || t.indexOf('关闭') >= 0 || tl.indexOf('close') >= 0 ||
              al.indexOf('关闭') >= 0 || all.indexOf('close') >= 0 || all.indexOf('dismiss') >= 0 ||
              t === '稍后配置' || t === '稍后' || t === '跳过' || t === '取消' || t === '忽略' || t === '知道了') {
            btns[i].click();
            return true;
          }
        }
        try { ov.dispatchEvent(new MouseEvent('click', { bubbles: true })); return true; } catch (e) {}
        return false;
      }""", 1)

# ---------- D) tick()：加入主页同步 ----------
a = "    try { syncSessionsPage(); } catch (e) {}\n    try { bindSessionPageActions(); } catch (e) {}"
assert s.count(a) == 1, 'anchor D'
s = s.replace(a, "    try { syncSessionsPage(); } catch (e) {}\n    try { syncHomePage(); } catch (e) {}\n    try { bindSessionPageActions(); } catch (e) {}", 1)

open(F, 'w', encoding='utf-8').write(s)
print('rc3-3 补丁 OK:', len(s), 'bytes')
