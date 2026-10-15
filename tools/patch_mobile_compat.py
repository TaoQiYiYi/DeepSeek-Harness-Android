#!/usr/bin/env python3
"""build36: stand down mobile adaptation when dsh-web-mobile (or similar) takes over."""
F = '/var/minis/workspace/dshport/app/assets/mobile.js'
s = open(F, encoding='utf-8').read()

# 1) 检测器
a = "  var APP_VER = window.__dshAppVersion || '';"
assert s.count(a) == 1, 'anchor1'
s = s.replace(a, a + """

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
  }""", 1)

# 2) injectCss 让位 + removeMyCss
a = "  function injectCss() {\n    if (!document || document.getElementById('dshm-css')) return;"
assert s.count(a) == 1, 'anchor2'
s = s.replace(a, "  function injectCss() {\n    if (pluginOwnsMobile()) { removeMyCss(); return; }\n    if (!document || document.getElementById('dshm-css')) return;", 1)

a = "    root.appendChild(st);\n  }"
assert s.count(a) == 1, 'anchor3'
s = s.replace(a, """    root.appendChild(st);
  }

  function removeMyCss() {
    try { var s = document.getElementById('dshm-css'); if (s && s.parentNode) s.parentNode.removeChild(s); } catch (e) {}
  }""", 1)

# 3) tick() 让位（保留系统栏/更新条）
a = "  function tick() {\n    try { injectCss(); } catch (e) {}"
assert s.count(a) == 1, 'anchor4'
s = s.replace(a, """  function tick() {
    if (pluginOwnsMobile()) {
      try { removeMyCss(); } catch (e) {}
      try { reportChrome(); } catch (e) {}
      try { syncUpdateBar(); } catch (e) {}
      return;
    }
    try { injectCss(); } catch (e) {}""", 1)

# 4) 遮罩行为让位
a = "    window.__dshmBackdrop = true;\n    document.addEventListener('pointerdown', function (ev) {\n      try {\n        if (window.innerWidth > 720) return;"
assert s.count(a) == 1, 'anchor5'
s = s.replace(a, "    window.__dshmBackdrop = true;\n    document.addEventListener('pointerdown', function (ev) {\n      try {\n        if (window.__dshmPluginMobile || window.innerWidth > 720) return;", 1)

# 5) 加号菜单守护让位
a = "    function maybeReopen() {\n      var now = Date.now();"
assert s.count(a) == 1, 'anchor6'
s = s.replace(a, "    function maybeReopen() {\n      if (window.__dshmPluginMobile) return;\n      var now = Date.now();", 1)

a = "        try {\n          if (window.innerWidth > 720) return;\n          if (!menuOf()) return;"
assert s.count(a) == 1, 'anchor7'
s = s.replace(a, "        try {\n          if (window.__dshmPluginMobile || window.innerWidth > 720) return;\n          if (!menuOf()) return;", 1)

# 6) 返回键：插件接管时不碰侧栏/抽屉
a = "      var frame = document.querySelector('.pI_x6G_frame');\n      if (frame && !frame.hasAttribute('data-rightbar-collapsed')) {"
assert s.count(a) == 1, 'anchor8'
s = s.replace(a, "      if (window.__dshmPluginMobile) return false;\n      var frame = document.querySelector('.pI_x6G_frame');\n      if (frame && !frame.hasAttribute('data-rightbar-collapsed')) {", 1)

open(F, 'w', encoding='utf-8').write(s)
print('mobile.js 让位补丁 OK:', len(s), 'bytes')
