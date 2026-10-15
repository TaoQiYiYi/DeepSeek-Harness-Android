#!/usr/bin/env python3
"""build36: render-guard rescue dialog + safemode (temporarily set aside plugins)."""
F = '/var/minis/workspace/dshport/app/java/com/dshport/mobile/MainActivity.java'
s = open(F, encoding='utf-8').read()

# 1) onPageFinished 里加渲染守护
a = "            public void onPageFinished(WebView v, String url) {\n                injectMobileJs();\n                injectCriticalCss();"
assert s.count(a) == 1, 'anchor1'
s = s.replace(a, a + "\n                armRenderGuard();", 1)

# 2) startEngine 前还原安全模式
a = "    private void startEngine() {"
assert s.count(a) == 1, 'anchor2'
s = s.replace(a, "    private void startEngine() {\n        restoreSafemodePlugins();", 1)

# 3) 方法块插到 injectMobileJs 之前
a = "    private void injectMobileJs() {"
assert s.count(a) == 1, 'anchor3'
methods = '''    private boolean rescueShown = false;

    /** 安全模式：把上次会话临时移开的插件目录还原（每次启动引擎前调用）。 */
    private void restoreSafemodePlugins() {
        try {
            File safe = dshProfileFile("node_modules.dshm-safe");
            File nm = dshProfileFile("node_modules");
            if (safe != null && safe.exists() && nm != null && !nm.exists()) {
                if (safe.renameTo(nm)) Runtime.log(this, "safemode: plugins restored");
                else Runtime.log(this, "safemode: restore failed");
            }
        } catch (Throwable t) {}
    }

    private File dshProfileFile(String name) {
        try {
            File a = new File(getFilesDir(), "dsh/profiles/web/" + name);
            if (a.exists() || (a.getParentFile() != null && a.getParentFile().exists())) return a;
            File b = new File(Runtime.homeDir(this), "profiles/web/" + name);
            if (b.exists() || (b.getParentFile() != null && b.getParentFile().exists())) return b;
        } catch (Throwable t) {}
        return null;
    }

    /** 渲染守护：页面完成后若内容疑似空白（第三方插件把启动打挂的典型症状），给出救援选项。 */
    private void armRenderGuard() {
        try {
            web.postDelayed(new Runnable() {
                public void run() {
                    try {
                        web.evaluateJavascript(
                            "(function(){try{var t=(document.body&&document.body.innerText)||'';var r=document.getElementById('root');return {len:String(t).trim().length,root:r?r.childElementCount:-1};}catch(e){return null;}})()",
                            new ValueCallback<String>() {
                                public void onReceiveValue(String v) {
                                    try {
                                        if (v == null || v.equals("null") || v.length() < 5) return;
                                        org.json.JSONObject o = new org.json.JSONObject(v);
                                        int len = o.optInt("len", -1);
                                        int root = o.optInt("root", -1);
                                        if (len >= 0 && len < 10 && root <= 0) offerRescueDialog();
                                    } catch (Throwable t) {}
                                }
                            });
                    } catch (Throwable t) {}
                }
            }, 6500);
        } catch (Throwable t) {}
    }

    private void offerRescueDialog() {
        if (rescueShown) return;
        rescueShown = true;
        try {
            Runtime.log(this, "render guard: page appears blank, offering rescue");
            new AlertDialog.Builder(this)
                .setTitle("页面渲染异常")
                .setMessage("检测到界面没有正常显示（常见于第三方插件与页面不兼容）。\\n\\n可先尝试重载；若仍不可用，选择「禁用插件重载」会暂时移开第三方插件（下次打开应用自动恢复）。")
                .setPositiveButton("重载", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface d, int w) {
                        try { web.reload(); } catch (Throwable t) {}
                    }
                })
                .setNeutralButton("禁用插件重载", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface d, int w) { safemodeReload(); }
                })
                .setNegativeButton("忽略", (DialogInterface.OnClickListener) null)
                .show();
        } catch (Throwable t) {}
    }

    private void safemodeReload() {
        try {
            File nm = dshProfileFile("node_modules");
            File safe = dshProfileFile("node_modules.dshm-safe");
            if (nm != null && nm.exists() && safe != null && !safe.exists()) {
                if (nm.renameTo(safe)) Runtime.log(this, "safemode: plugins moved aside");
                else Runtime.log(this, "safemode: rename failed");
            }
            restartEngine();
            web.postDelayed(new Runnable() {
                public void run() {
                    try { web.reload(); } catch (Throwable t) {}
                }
            }, 2500);
        } catch (Throwable t) {
            Runtime.log(this, "safemode reload failed: " + t);
        }
    }

'''
s = s.replace(a, methods + a, 1)

open(F, 'w', encoding='utf-8').write(s)
print('MainActivity 救援补丁 OK:', len(s), 'bytes')
