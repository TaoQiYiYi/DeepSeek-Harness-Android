(function () {
  if (window.__dshmInit) return;
  window.__dshmInit = true;

  var APP_VER = window.__dshAppVersion || '';

  /* 第三方移动端适配插件接管时，本适配全面让位（仅保留 App 功能层）。
     目前识别：dsh-web-mobile（若将来支持更多插件，在此列表补充即可）。 */
  function pluginOwnsMobile() {
    if (window.__dshmPluginMobile) return true;
    try {
      if (document.querySelector('style[data-plugin-css*="dsh-web-mobile"]')) { window.__dshmPluginMobile = true; return true; }
      var b = window.__DSH_BOOT__;
      if (b && JSON.stringify(b).indexOf('dsh-web-mobile') !== -1) { window.__dshmPluginMobile = true; return true; }
    } catch (e) {}
    return false;
  }

  /* ---------------- CSS ---------------- */
  var CSS = [
    '@media (max-width: 720px) {',
    '  .pI_x6G_sidebarCol { grid-column: 1 !important; }',
    '  .pI_x6G_centerCol { grid-column: 2 !important; }',
    '  .pI_x6G_rightbarCol { grid-column: 3 !important; }',
    '  /* 左栏展开 = 浮层，主内容占满 */',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) .pI_x6G_sidebarCol { position: absolute !important; left: 0 !important; top: 0; bottom: 0; height: auto !important; width: min(86vw, 320px) !important; z-index: 71; box-shadow: 6px 0 28px rgba(0, 0, 0, 0.28); }',
    '  /* 只开右栏（左栏折叠时）：保留 56px 图标栏 */',
    '  .pI_x6G_frame[data-sidebar-collapsed]:not([data-rightbar-collapsed]) { grid-template-columns: 56px minmax(0, 1fr) 0 !important; }',
    '  /* 右栏展开 = 浮层 */',
    '  .pI_x6G_frame:not([data-rightbar-collapsed]) .pI_x6G_rightbarCol { position: absolute !important; right: 0 !important; left: auto !important; top: 0; bottom: 0; height: auto !important; width: min(92vw, 380px) !important; z-index: 71; box-shadow: -6px 0 28px rgba(0, 0, 0, 0.28); }',
    '  .pI_x6G_handle { display: none !important; }',
    '  .VOzbGW_overlay { padding: 0 !important; }',
    '  .VOzbGW_panel { display: flex !important; flex-direction: column !important; width: 100% !important; max-width: none !important; height: 100% !important; max-height: none !important; border-radius: 0 !important; }',
    '  .VOzbGW_nav { width: 100% !important; height: auto !important; flex: 0 0 auto !important; flex-direction: row !important; align-items: center !important; }',
    '  .VOzbGW_navList { flex-direction: row !important; width: auto !important; flex: 1 1 auto !important; overflow-x: auto !important; overflow-y: hidden !important; }',
    '  .VOzbGW_navCell { width: auto !important; flex: 0 0 auto !important; white-space: nowrap !important; }',
    '  .VOzbGW_navTitle { white-space: nowrap !important; width: auto !important; flex: 0 0 auto !important; }',
    '  .VOzbGW_navList::-webkit-scrollbar { display: none !important; height: 0 !important; }',
    '  .VOzbGW_content { width: 100% !important; min-width: 0 !important; min-height: 0 !important; flex: 1 1 auto !important; box-sizing: border-box !important; }',
    '  .VOzbGW_options { width: 100% !important; min-width: 0 !important; min-height: 0 !important; box-sizing: border-box !important; }',
    '  ._8HJdBW_cubeRow { flex-wrap: nowrap !important; }',
    '  ._8HJdBW_themeCube { flex: 1 1 0 !important; min-width: 0 !important; }',
    '  .oY77xG_row { padding: 12px 0 !important; }',
    '  .bVCLcG_row:has(.vnGTiq_field) { flex-wrap: wrap !important; }',
    '  .bVCLcG_row:has(.vnGTiq_field) .bVCLcG_rowText { flex: 1 1 100% !important; padding-right: 0 !important; }',
    '  .bVCLcG_row:has(.vnGTiq_field) .vnGTiq_field { flex: 1 1 100% !important; width: 100% !important; }',
    '  [class*="_3e4SsG_menu"] { min-width: 210px !important; width: max-content !important; max-width: 84vw !important; }',
    '  [class*="uV2eYG_overlayAnchor"] { width: auto !important; }',
    '  img { max-width: 100% !important; max-height: 46vh !important; object-fit: contain !important; }',
    '  video { max-width: 100% !important; }',
    '  pre { max-width: 100% !important; overflow-x: auto !important; }',
    '  .pI_x6G_composerSeat button { min-width: 38px !important; min-height: 38px !important; }',
    '  #dshm-update-bar { display: flex !important; }',
    '  /* —— rc3：对话页独立成页 —— */',
    '  html body[data-dshm-chat="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-chat="1"] .pI_x6G_sidebarCol { display: none !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_header"] { position: relative !important; padding-left: 50px !important; }',
    '  html body[data-dshm-chat="1"] [class*="_tabHostHeader_"] { position: relative !important; padding-left: 46px !important; }',
    '  #dshm-chat-back { position: absolute !important; left: 7px !important; top: 50% !important; transform: translateY(-50%) !important; width: 36px !important; height: 36px !important; min-width: 36px !important; min-height: 36px !important; padding: 0 !important; margin: 0 !important; border: none !important; border-radius: 50% !important; background: transparent !important; color: inherit !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 6 !important; }',
    '  #dshm-chat-back:active { background: rgba(128, 128, 128, 0.22) !important; }',
    '  /* —— rc3：会话选择页独立成页 —— */',
    '  html body[data-dshm-sessions="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-sessions="1"] .pI_x6G_frame .pI_x6G_sidebarCol { width: 100% !important; max-width: none !important; box-shadow: none !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_listArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_treeBody"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_list"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_groupSection"],',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_sessionRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_newSession"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_root"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_logoRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_regionArea"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_panelList"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_panelRow"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_footArea"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_footerActions"],',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_settingsArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_sectionHeader"] { width: 100% !important; max-width: none !important; box-sizing: border-box !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_root"] { padding-right: 0 !important; }',
    '  html body[data-dshm-sessions="1"] [class*="hHd-Xa_regionArea"] { margin-left: 0 !important; margin-right: 0 !important; padding-left: 0 !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_listArea"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_treeBody"],',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_list"] { margin-left: 0 !important; margin-right: 0 !important; padding-left: 0 !important; padding-right: 0 !important; }',
    '  html body[data-dshm-sessions="1"] [class*="bhn1Oq_groupSection"] { width: 100% !important; }',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_sessionRow"],',
    '  html body[data-dshm-sessions="1"] [class*="YDXeBa_projectRow"] { margin-right: 0 !important; }',
    '  /* —— rc3：主页独立成页 —— */',
    '  html body[data-dshm-home="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-home="1"] .pI_x6G_sidebarCol { display: none !important; }',
    '  html body[data-dshm-home="1"] [class*="wSkVaW_header"] { position: relative !important; }',
    '  /* —— rc3：插件/自动化页面独立成页 —— */',
    '  html body[data-dshm-page="1"] .pI_x6G_frame { grid-template-columns: 0 minmax(0, 1fr) 0 !important; }',
    '  html body[data-dshm-page="1"] .pI_x6G_sidebarCol { display: none !important; }',
    '  #dshm-home-menu { position: absolute !important; left: 7px !important; top: 50% !important; transform: translateY(-50%) !important; width: 36px !important; height: 36px !important; min-width: 36px !important; min-height: 36px !important; padding: 0 !important; margin: 0 !important; border: none !important; border-radius: 50% !important; background: transparent !important; color: inherit !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 6 !important; }',
    '  #dshm-home-menu:active { background: rgba(128, 128, 128, 0.22) !important; }',
    '  /* —— rc3：对话页「⋯」贴右侧栏切换按钮 —— */',
    '  html body[data-dshm-chat="1"] [aria-label="更多操作"] { position: fixed !important; right: 48px !important; top: 12px !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_headerUtilities"],',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_headerCorner"] { width: 0 !important; min-width: 0 !important; margin: 0 !important; padding: 0 !important; flex: 0 0 0 !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_headerActions"] { display: none !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_crumb"] { max-width: 100% !important; }',
    '  html body[data-dshm-chat="1"] [class*="wSkVaW_header"] { grid-template-columns: 0 minmax(0, 1fr) !important; }',
    '}',
    '* { -webkit-tap-highlight-color: transparent !important; }',
    'html, body { overscroll-behavior: none; }',
    '::-webkit-scrollbar { width: 0 !important; height: 0 !important; }',
    '#dshm-update-bar { display: none; align-items: center; gap: 12px; flex: 0 0 auto; padding: 10px 16px 14px; border-top: 1px solid rgba(128, 128, 128, 0.28); }',
    '#dshm-update-bar .dshm-ub-title { font-size: 14px; font-weight: 600; }',
    '#dshm-update-bar .dshm-ub-sub { font-size: 11px; opacity: 0.6; margin-top: 2px; }',
    '#dshm-update-bar button { padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(128, 128, 128, 0.35); background: transparent; color: inherit; font-size: 13px; }',
    '#dshm-update-bar button:first-of-type { margin-left: auto; }',
    '#dshm-update-bar button + button { margin-left: 8px; }',
    '#dshm-dlg .dshm-body.dshm-log { max-height: 52vh; overflow-y: auto; font-size: 10px; text-align: left; white-space: pre-wrap; word-break: break-all; font-family: monospace; }',
    '#dshm-dlg-wrap { position: fixed; inset: 0; z-index: 9999; display: none; align-items: center; justify-content: center; padding: 24px; background: rgba(0, 0, 0, 0.42); }',
    '#dshm-dlg { width: 100%; max-width: 340px; border-radius: 16px; padding: 20px; box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32); }',
    '#dshm-dlg h3 { margin: 0 0 10px; font-size: 16px; }',
    '#dshm-dlg .dshm-body { font-size: 13px; line-height: 1.55; white-space: pre-wrap; word-break: break-word; opacity: 0.86; }',
    '#dshm-dlg .dshm-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 18px; }',
    '#dshm-dlg button { padding: 9px 16px; border-radius: 999px; border: 1px solid rgba(128, 128, 128, 0.35); background: transparent; color: inherit; font-size: 13px; }',
    '#dshm-dlg button.dshm-primary { border-color: transparent; background: #4d6bfe; color: #fff; }',
    '#dshm-dlg .dshm-bar { height: 6px; border-radius: 3px; background: rgba(128, 128, 128, 0.28); overflow: hidden; margin-top: 14px; }',
    '#dshm-dlg .dshm-bar > i { display: block; height: 100%; width: 0; background: #4d6bfe; }'
  ].join('\n');

  function injectCss() {
    if (pluginOwnsMobile()) { removeMyCss(); return; }
    if (!document || document.getElementById('dshm-css')) return;
    var root = document.head || document.documentElement;
    if (!root) return;
    var st = document.createElement('style');
    st.id = 'dshm-css';
    st.textContent = CSS;
    root.appendChild(st);
  }

  function removeMyCss() {
    try { var a = document.getElementById('dshm-css'); if (a && a.parentNode) a.parentNode.removeChild(a); } catch (e) {}
    try { var b = document.getElementById('dshm-crit'); if (b && b.parentNode) b.parentNode.removeChild(b); } catch (e) {}
  }

  /* ---------------- 主题同步：把界面底色推给宿主设置系统栏颜色 ---------------- */
  var lastBg = '';
  function reportChrome() {
    try {
      var el = document.querySelector('.VOzbGW_panel') || document.body;
      if (!el) return;
      var bg = getComputedStyle(el).backgroundColor;
      var m = bg && bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (!m) return;
      var hex = '#';
      for (var i = 1; i <= 3; i++) hex += ('0' + parseInt(m[i], 10).toString(16)).slice(-2);
      if (hex === lastBg) return;
      lastBg = hex;
      send({ cmd: 'chrome', bg: hex });
    } catch (e) {}
  }

  /* ---------------- 与宿主通信（自定义 scheme，由 MainActivity 拦截） ---------------- */
  function send(obj) {
    try { console.log('__DSHM__' + JSON.stringify(obj)); } catch (e) {}
  }

  /* ---------------- 设置面板里的「获取更新」 ---------------- */
  function themeOf(el) {
    var cs = getComputedStyle(el);
    return { bg: cs.backgroundColor, fg: cs.color };
  }

  function buildUpdateBar() {
    var panel = document.querySelector('.VOzbGW_panel');
    if (!panel || document.getElementById('dshm-update-bar')) return;
    var bar = document.createElement('div');
    bar.id = 'dshm-update-bar';
    var sub = '当前版本 v' + (APP_VER || '—');
    if (window.__dshAppBuild) sub += ' · build ' + window.__dshAppBuild;
    if (window.__dshCoreVersion) sub += ' · 核心 ' + window.__dshCoreVersion;
    bar.innerHTML = '<div><div class="dshm-ub-title">获取更新</div><div class="dshm-ub-sub">' +
      sub + '</div></div><button type="button" class="dshm-ub-check">检查更新</button>' +
      '<button type="button" class="dshm-ub-log">日志</button>';
    var t = themeOf(panel);
    bar.style.background = t.bg;
    bar.style.color = t.fg;
    var btns = bar.querySelectorAll('button');
    for (var bi = 0; bi < btns.length; bi++) btns[bi].style.color = t.fg;
    btns[0].addEventListener('click', function (ev) { ev.stopPropagation(); doCheck(); }, true);
    btns[1].addEventListener('click', function (ev) { ev.stopPropagation(); doLog(); }, true);
    panel.appendChild(bar);
  }

  function syncUpdateBar() {
    try {
      var panel = document.querySelector('.VOzbGW_panel');
      if (panel && !document.getElementById('dshm-update-bar')) buildUpdateBar();
      var overlay = document.querySelector('.VOzbGW_overlay');
      if (!overlay && document.getElementById('dshm-update-bar')) {
        var b = document.getElementById('dshm-update-bar');
        b.parentNode.removeChild(b);
      }
    } catch (e) {}
  }

  /* ---------------- 对话框 ---------------- */
  function dlgWrap() {
    var w = document.getElementById('dshm-dlg-wrap');
    if (w) return w;
    w = document.createElement('div');
    w.id = 'dshm-dlg-wrap';
    w.innerHTML = '<div id="dshm-dlg"><h3></h3><div class="dshm-body"></div>' +
      '<div class="dshm-bar" style="display:none"><i></i></div>' +
      '<div class="dshm-actions"><button class="dshm-cancel" type="button">关闭</button>' +
      '<button class="dshm-ok dshm-primary" type="button" style="display:none">下载并安装</button></div></div>';
    document.body.appendChild(w);
    w.addEventListener('click', function (ev) { if (ev.target === w) hideDlg(); }, true);
    w.querySelector('.dshm-cancel').addEventListener('click', hideDlg, true);
    return w;
  }

  function showDlg(title, body, okText, onOk, busy) {
    var w = dlgWrap();
    var panel = document.querySelector('.VOzbGW_panel') || document.body;
    var t = themeOf(panel);
    var card = w.querySelector('#dshm-dlg');
    card.style.background = t.bg;
    card.style.color = t.fg;
    w.querySelector('h3').textContent = title;
    w.querySelector('.dshm-body').textContent = body;
    var bar = w.querySelector('.dshm-bar');
    bar.style.display = busy ? 'block' : 'none';
    bar.querySelector('i').style.width = '0%';
    var ok = w.querySelector('.dshm-ok');
    if (okText) {
      ok.style.display = '';
      ok.textContent = okText;
      ok.onclick = function () { hideDlg(); if (onOk) onOk(); };
    } else {
      ok.style.display = 'none';
    }
    w.style.display = 'flex';
  }

  function hideDlg() {
    var w = document.getElementById('dshm-dlg-wrap');
    if (w) w.style.display = 'none';
  }

  function setProgress(pct) {
    var w = document.getElementById('dshm-dlg-wrap');
    if (!w) return;
    w.querySelector('.dshm-bar').style.display = 'block';
    w.querySelector('.dshm-bar > i').style.width = pct + '%';
  }

  function doLog() {
    showDlg('运行日志', '正在读取…', null, null, false);
    send({ cmd: 'log' });
  }

  window.__dshmLog = function (text) {
    try {
      var w = dlgWrap();
      w.querySelector('h3').textContent = '运行日志';
      var body = w.querySelector('.dshm-body');
      body.classList.add('dshm-log');
      body.textContent = text || '(空)';
      body.scrollTop = body.scrollHeight;
      var ok = w.querySelector('.dshm-ok');
      ok.style.display = '';
      ok.textContent = '复制日志';
      ok.onclick = function () { send({ cmd: 'copylog' }); };
      w.style.display = 'flex';
    } catch (e) {}
  };

  function doCheck() {
    showDlg('检查更新', '正在检查最新版本…', null, null, true);
    send({ cmd: 'check' });
  }

  /* 宿主回调 */
  window.__dshUpdateResult = function (info) {
    try {
      if (!info || info.ok !== true) {
        showDlg('检查更新', '检查失败：' + ((info && info.error) || '未知错误') + '\n\n请检查网络后重试。', null, null, false);
        return;
      }
      if (!info.hasUpdate) {
        showDlg('检查更新', '已是最新版本 v' + info.current + '。', null, null, false);
        return;
      }
      var body = '发现新版本 v' + info.latest + '（当前 v' + info.current + '）';
      if (info.apkSize) body += '\n安装包 ' + (Math.round(info.apkSize / 1048576 * 10) / 10) + ' MB';
      if (info.notes) body += '\n\n' + String(info.notes).slice(0, 400);
      else body += '\n\n下载后由系统安装器完成安装。';
      var url = info.apkUrl;
      if (!url) {
        showDlg('检查更新', '新版本没有可下载的 APK 附件。', null, null, false);
        return;
      }
      showDlg('发现新版本', body, '下载并安装', function () {
        showDlg('下载更新', '正在下载安装包…', null, null, true);
        send({ cmd: 'install', url: url });
      }, false);
    } catch (e) {}
  };

  window.__dshUpdateProgress = function (pct) {
    setProgress(Math.max(0, Math.min(100, pct | 0)));
  };

  window.__dshUpdateState = function (kind, msg) {
    if (kind === 'done') showDlg('下载完成', msg || '已开始安装，请在系统安装器中完成。', null, null, false);
    else showDlg('更新失败', msg || '未知错误', null, null, false);
  };

  /* ---------------- rc3：对话页独立成页 ---------------- */
  function chatViewOpen() {
    try {
      if (window.innerWidth > 720) return false;
      if (document.querySelector('[class*="wSkVaW_header"] [class*="wSkVaW_tab"]')) return true;
      if (document.querySelector('[class*="EvIC1a_"]')) return true;
      var card = null;
      var cands = document.querySelectorAll('button, [role="button"], a');
      for (var i = 0; i < cands.length; i++) {
        var t = cands[i].textContent || '';
        var r = cands[i].getBoundingClientRect();
        if (t.indexOf('工作区文件') !== -1 && r.width > 120 && r.height > 40) { card = cands[i]; break; }
      }
      return !!card;
    } catch (e) { return false; }
  }

  /* 通用「页面」根检测：插件（X_2TxG_page）、自动化（t-XoWW_page）等以 *_page 结尾的整屏容器 */
  function pageRootEl() {
    try {
      var els = document.querySelectorAll('[class*="_page"]');
      for (var i = 0; i < els.length; i++) {
        var toks = String(els[i].className || '').split(/\s+/);
        var ok = false;
        for (var j = 0; j < toks.length; j++) { if (/_page$/.test(toks[j])) { ok = true; break; } }
        if (!ok) continue;
        var r = els[i].getBoundingClientRect();
        if (r.width > 200 && r.height > 120) return els[i];
      }
    } catch (e) {}
    return null;
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
      var frame = document.querySelector('.pI_x6G_frame');
      if (frame && !frame.hasAttribute('data-sidebar-collapsed')) collapseSidebarIfOpen();
      var t = document.querySelector('[class*="hHd-Xa_newSession"]') || document.querySelector('button[aria-label="新建会话"]');
      if (t) { t.click(); return true; }
    } catch (e) {}
    return false;
  }

  function ensureChatBack() {
    try {
      var hdr = null;
      var hcands = document.querySelectorAll('[class*="_tabHostHeader_"], [class*="wSkVaW_header"]');
      for (var hi = 0; hi < hcands.length; hi++) {
        var hc = hcands[hi];
        var hr = hc.getBoundingClientRect();
        if (hr.width > 200 && hr.height >= 30 && hr.y < 80 && hr.x > -5 && hr.x < 40 && getComputedStyle(hc).display !== 'none') {
          hdr = hc;
          if (String(hc.className).indexOf('tabHostHeader') !== -1) break;
        }
      }
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
        if (window.__dshmBack) { window.__dshmBack(); return; }
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
      var exitWin = !!(window.__dshmExitChatUntil && Date.now() < window.__dshmExitChatUntil);
      if (open && !cur) {
        var frX = document.querySelector('.pI_x6G_frame');
        if (!frX || frX.hasAttribute('data-sidebar-collapsed')) {
          document.body.setAttribute('data-dshm-chat', '1');
          collapseSidebarIfOpen();
          ensureChatBack();
        }
      } else if (open && cur) {
        if (exitWin) {
          var fr2 = document.querySelector('.pI_x6G_frame');
          if (fr2 && !fr2.hasAttribute('data-sidebar-collapsed')) {
            document.body.removeAttribute('data-dshm-chat');
            window.__dshmExitChatUntil = 0;
          }
        } else {
          collapseSidebarIfOpen();
          ensureChatBack();
        }
      } else if (!open && cur) {
        document.body.removeAttribute('data-dshm-chat');
      }
    } catch (e) {}
  }

  /* ---------------- rc3：会话选择页独立成页 ---------------- */
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
        var rowEl = t.closest('[class*="YDXeBa_sessionRow"]');
        var guarded = !!(t.closest('button[aria-haspopup]') || t.closest('button[aria-label*="更多"]') || t.closest('[role="menu"]'));
        var isSessionNav = !!t.closest('[class*="hHd-Xa_newSession"]') || (!!rowEl && !guarded);
        var navBtn = t.closest('button');
        var navLabel = navBtn ? (navBtn.textContent || '').trim() : '';
        var isPageNav = (navLabel === '插件' || navLabel === '自动化任务');
        if (isSessionNav || isPageNav) { try { collapseSidebarIfOpen(); } catch (e) {} window.__dshmCollapseUntil = Date.now() + 2000; }
      } catch (e) {}
    }, true);
  }

  /* ---------------- rc3：主页独立成页 ---------------- */
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
        if (document.body.getAttribute('data-dshm-page') === '1') document.body.removeAttribute('data-dshm-page');
        removeHomeMenu();
        return;
      }
      var chat = document.body.getAttribute('data-dshm-chat') === '1';
      var sess = document.body.getAttribute('data-dshm-sessions') === '1';
      var pageEl = pageRootEl();
      var pageMode = !!pageEl;
      var pageCur = document.body.getAttribute('data-dshm-page') === '1';
      if (pageMode && !chat && !sess) {
        var frP = document.querySelector('.pI_x6G_frame');
        var drawerOpen = !!frP && !frP.hasAttribute('data-sidebar-collapsed');
        if (drawerOpen) { if (pageCur) document.body.removeAttribute('data-dshm-page'); }
        else if (!pageCur) document.body.setAttribute('data-dshm-page', '1');
      } else if (pageCur) document.body.removeAttribute('data-dshm-page');
      var want = !chat && !sess && !pageMode;
      var cur = document.body.getAttribute('data-dshm-home') === '1';
      if (want && !cur) document.body.setAttribute('data-dshm-home', '1');
      else if (!want && cur) document.body.removeAttribute('data-dshm-home');
      if (want) ensureHomeMenu(); else removeHomeMenu();
    } catch (e) {}
  }

  /* ---------------- 侧栏遮罩点击收起（原有行为） ---------------- */
  /** 返回键处理：关掉打开的弹窗/面板；返回 true 表示已处理（不退出应用）。 */
  window.__dshmBack = function () {
    try {
      var w = document.getElementById('dshm-dlg-wrap');
      if (w && w.style.display === 'flex') { hideDlg(); return true; }
      var ov = document.querySelector('.VOzbGW_overlay');
      if (ov) {
        var btns = ov.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
          var t = (btns[i].textContent || '').trim();
          var al = (btns[i].getAttribute('aria-label') || '');
          var tl = t.toLowerCase();
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
      }
      if (document.body.getAttribute('data-dshm-chat') === '1') {
        var cf = document.querySelector('.pI_x6G_frame');
        if (cf && !cf.hasAttribute('data-rightbar-collapsed')) {
          var rb = document.querySelector('button[aria-label*="右侧"]');
          if (rb) { rb.click(); return true; }
        }
        var cob = document.querySelector('button[aria-label="打开侧边栏"]');
        if (cob) { window.__dshmExitChatUntil = Date.now() + 3000; try { cob.click(); } catch (e) {} return true; }
        exitChatToHome();
        return true;
      }
      var pageEl = pageRootEl();
      if (pageEl && document.body.getAttribute('data-dshm-sessions') !== '1') {
        var ob = document.querySelector('button[aria-label="打开侧边栏"]');
        if (ob) { window.__dshmCollapseUntil = 0; ob.click(); return true; }
      }
      if (window.__dshmPluginMobile) return false;
      if (document.body.getAttribute('data-dshm-sessions') === '1') {
        var tg2 = collapseToggle();
        if (tg2) { tg2.click(); return true; }
        return true;
      }
      var frame = document.querySelector('.pI_x6G_frame');
      if (frame && !frame.hasAttribute('data-rightbar-collapsed')) {
        var rb = document.querySelector('button[aria-label*="右侧"]');
        if (rb) { rb.click(); return true; }
      }
      if (frame && !frame.hasAttribute('data-sidebar-collapsed')) {
        var tgl = collapseToggle();
        if (tgl) { tgl.click(); return true; }
      }
      return false;
    } catch (e) { return false; }
  };

  function collapseToggle() {
    var sc = document.querySelector('.pI_x6G_sidebarCol');
    if (!sc) return null;
    return sc.querySelector('button[aria-label*="收起"]') ||
      sc.querySelector('button[aria-label*="ollapse"]') ||
      sc.querySelector('.hHd-Xa_iconButton.hHd-Xa_toggle');
  }

  function bindBackdrop() {
    if (window.__dshmBackdrop) return;
    window.__dshmBackdrop = true;
    document.addEventListener('pointerdown', function (ev) {
      try {
        if (window.__dshmPluginMobile || window.innerWidth > 720) return;
        var bar = document.getElementById('dshm-update-bar');
        if (bar && bar.contains(ev.target)) return;
        var tg = ev.target;
        if (tg && tg.closest && tg.closest('button[aria-label*="添加文件"], button[aria-label*="调用指令"]')) return;
        var frame = document.querySelector('.pI_x6G_frame');
        if (!frame || frame.hasAttribute('data-sidebar-collapsed')) return;
        var sc = document.querySelector('.pI_x6G_sidebarCol');
        if (sc && sc.contains(ev.target)) return;
        var tgl = collapseToggle();
        if (tgl) tgl.click();
      } catch (e) {}
    }, true);
  }

  /** 「+」菜单防「打开即闪退」：无论何种原因被立刻关掉，都在短时间内自动重开（限次）。 */
  function plusMenuKeeper() {
    if (window.__dshmMenuKeeper) return;
    window.__dshmMenuKeeper = true;
    var wasOpen = false, openAt = 0, reopenCount = 0, lastPlusTap = 0, lastReopen = 0;
    function menuOf() { return document.querySelector('[class*="_3e4SsG_menu"]'); }
    function plusOf() { return document.querySelector('button[aria-label*="添加文件"], button[aria-label*="调用指令"]'); }
    ['pointerdown', 'touchstart', 'click'].forEach(function (tp) {
      document.addEventListener(tp, function (ev) {
        try {
          if (window.innerWidth > 720) return;
          var t = ev.target;
          if (!t || !t.closest) return;
          if (t.closest('button[aria-label*="添加文件"], button[aria-label*="调用指令"]')) {
            lastPlusTap = Date.now();
            reopenCount = 0;
            lastReopen = 0;
          } else if (!t.closest('[class*="_3e4SsG_menu"]')) {
            reopenCount = 99;
          }
        } catch (e) {}
      }, true);
    });
    function maybeReopen() {
      if (window.__dshmPluginMobile) return;
      var now = Date.now();
      if (now - lastPlusTap > 1500) return;
      if (now - lastReopen < 900) return;
      if (reopenCount >= 3) return;
      if (menuOf()) return;
      var plus = plusOf();
      if (!plus) return;
      lastReopen = now;
      reopenCount++;
      try { plus.click(); } catch (e) {}
    }
    try {
      new MutationObserver(function () {
        var open = !!menuOf();
        var now = Date.now();
        if (open && !wasOpen) { wasOpen = true; openAt = now; }
        else if (!open && wasOpen) { wasOpen = false; maybeReopen(); }
      }).observe(document.documentElement, { childList: true, subtree: true });
    } catch (e) {}
    setInterval(function () {
      try {
        var open = !!menuOf();
        var now = Date.now();
        if (open) { wasOpen = true; if (!openAt) openAt = now; return; }
        if (wasOpen) { wasOpen = false; maybeReopen(); return; }
        if (now - lastPlusTap < 1400 && now - openAt < 1500) maybeReopen();
      } catch (e) {}
    }, 120);
  }


  function plusMenuGuard() {
    if (window.__dshmMenuGuard) return;
    window.__dshmMenuGuard = true;
    var lastOpen = 0;
    function menuOf() { return document.querySelector('[class*="_3e4SsG_menu"]'); }
    try {
      new MutationObserver(function () {
        if (menuOf()) lastOpen = Date.now();
      }).observe(document.documentElement, { childList: true, subtree: true });
    } catch (e) {}
    var types = ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click', 'touchstart', 'touchend', 'touchcancel'];
    types.forEach(function (tp) {
      document.addEventListener(tp, function (ev) {
        try {
          if (window.__dshmPluginMobile || window.innerWidth > 720) return;
          if (!menuOf()) return;
          if (Date.now() - lastOpen > 450) return;
          var t = ev.target;
          if (!t || !t.closest) return;
          if (!t.closest('button[aria-label*="添加文件"], button[aria-label*="调用指令"]')) return;
          ev.stopPropagation();
          ev.preventDefault();
        } catch (e) {}
      }, true);
    });
  }

  function tick() {
    if (pluginOwnsMobile()) {
      try { removeMyCss(); } catch (e) {}
      try { reportChrome(); } catch (e) {}
      try { syncUpdateBar(); } catch (e) {}
      return;
    }
    try { injectCss(); } catch (e) {}
    try { reportChrome(); } catch (e) {}
    try { syncUpdateBar(); } catch (e) {}
    try { bindBackdrop(); } catch (e) {}
    try { plusMenuKeeper(); } catch (e) {}
    try { syncChatPage(); } catch (e) {}
    try { syncSessionsPage(); } catch (e) {}
    try { syncHomePage(); } catch (e) {}
    try { bindSessionPageActions(); } catch (e) {}
    try { if (window.__dshmCollapseUntil && Date.now() < window.__dshmCollapseUntil && document.body.getAttribute('data-dshm-chat') !== '1') collapseSidebarIfOpen(); } catch (e) {}
  }

  try { setInterval(tick, 1500); } catch (e) {}
  try { tick(); } catch (e) {}
  try { document.addEventListener('DOMContentLoaded', tick); } catch (e) {}
  try {
    new MutationObserver(tick).observe(document.documentElement || document, {
      childList: true, subtree: true, attributes: true,
      attributeFilter: ['class', 'data-sidebar-collapsed', 'style']
    });
  } catch (e) {}
})();
