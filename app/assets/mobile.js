(function () {
  if (window.__dshmInit) return;
  window.__dshmInit = true;

  var CSS = [
    '@media (max-width: 720px) {',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) { grid-template-columns: 0 minmax(0, 1fr) minmax(0px, 0px) !important; }',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) .pI_x6G_centerCol { grid-column: 2 !important; }',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) .pI_x6G_rightbarCol { grid-column: 3 !important; }',
    '  .pI_x6G_frame:not([data-sidebar-collapsed]) .pI_x6G_sidebarCol { position: absolute !important; left: 0; top: 0; bottom: 0; width: min(84vw, 320px) !important; z-index: 70; box-shadow: 6px 0 28px rgba(0, 0, 0, 0.25); }',
    '  .pI_x6G_handle { display: none !important; }',
    '  .VOzbGW_panel { width: 100% !important; max-width: none !important; height: 100% !important; max-height: none !important; flex-direction: column !important; border-radius: 0 !important; }',
    '  .VOzbGW_nav { width: 100% !important; flex-direction: row !important; align-items: center !important; flex: 0 0 auto !important; }',
    '  .VOzbGW_navList { flex-direction: row !important; width: auto !important; flex: 1 1 auto !important; overflow-x: auto !important; overflow-y: hidden !important; }',
    '  .VOzbGW_navCell { width: auto !important; flex: 0 0 auto !important; white-space: nowrap !important; }',
    '  .VOzbGW_content { width: 100% !important; flex: 1 1 auto !important; min-height: 0 !important; }',
    '  .VOzbGW_options { width: 100% !important; min-height: 0 !important; }',
    '  .VOzbGW_navTitle { white-space: nowrap !important; width: auto !important; flex: 0 0 auto !important; }',
    '  .VOzbGW_navList::-webkit-scrollbar { display: none !important; height: 0 !important; }',
    '  .VOzbGW_content { box-sizing: border-box !important; }',
    '  .VOzbGW_options { box-sizing: border-box !important; }',
    '  ._8HJdBW_cubeRow { flex-wrap: nowrap !important; }',
    '  ._8HJdBW_themeCube { flex: 1 1 0 !important; min-width: 0 !important; }',
    '  .oY77xG_row { padding: 12px 0 !important; }',
    '}'
  ].join('\n');

  function collapseToggle() {
    var sc = document.querySelector('.pI_x6G_sidebarCol');
    if (!sc) return null;
    return sc.querySelector('button[aria-label*="收起"]') ||
           sc.querySelector('button[aria-label*="ollapse"]') ||
           sc.querySelector('.hHd-Xa_iconButton.hHd-Xa_toggle');
  }

  function apply() {
    try {
      if (!document.getElementById('dshm-css')) {
        var st = document.createElement('style');
        st.id = 'dshm-css';
        st.textContent = CSS;
        (document.head || document.documentElement).appendChild(st);
      }
      if (!window.__dshmBackdrop) {
        window.__dshmBackdrop = true;
        document.addEventListener('pointerdown', function (ev) {
          try {
            if (window.innerWidth > 720) return;
            var frame = document.querySelector('.pI_x6G_frame');
            if (!frame || frame.hasAttribute('data-sidebar-collapsed')) return;
            var sc = document.querySelector('.pI_x6G_sidebarCol');
            if (sc && sc.contains(ev.target)) return;
            var tgl = collapseToggle();
            if (tgl) tgl.click();
          } catch (e) {}
        }, true);
      }
    } catch (e) {}
  }

  if (document.head || document.documentElement) apply();
  document.addEventListener('DOMContentLoaded', apply);
})();
