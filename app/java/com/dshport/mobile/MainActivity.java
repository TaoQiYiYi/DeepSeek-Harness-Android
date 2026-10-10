package com.dshport.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;

import android.graphics.Color;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {
    private static final String BASE_URL = "http://127.0.0.1:3080/";
    private static final int REQ_FILE = 41;
    private static final int REQ_STORAGE = 42;

    private WebView web;
    private LinearLayout overlay;
    private ProgressBar spinner;
    private TextView status;
    private Button retry;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private String lastLoaded = "";
    private boolean embedded;
    private ValueCallback<Uri[]> fileCallback;

    private final Runnable poll = new Runnable() {
        @Override public void run() {
            step();
            handler.postDelayed(this, 500);
        }
    };

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        embedded = Runtime.runtimeBundled(this);
        Runtime.log(this, "app start, embedded=" + embedded + ", sdk=" + Build.VERSION.SDK_INT);
        buildUi();

        if (Build.VERSION.SDK_INT >= 33) {
            try {
                requestPermissions(new String[]{ "android.permission.POST_NOTIFICATIONS" }, 7);
            } catch (Throwable ignored) { }
        }

        handler.postDelayed(new Runnable() {
            public void run() { ensureStorageAccess(); }
        }, 1500);

        if (embedded) {
            Runtime.writeStatus(this, "BOOTING");
            startEngine();
            handler.post(poll);
        } else {
            overlay.setGravity(Gravity.TOP | Gravity.CENTER_HORIZONTAL);
            overlay.setBackgroundColor(0x66000000);
            spinner.setVisibility(View.GONE);
            showBanner("直连模式：正在连接 " + BASE_URL + "（引擎需在外部运行）");
            web.loadUrl(BASE_URL);
        }
    }

    /** 是否已能真正读写共享存储（功能探测，比权限查询可靠）。 */
    private boolean sharedStorageReady() {
        try {
            File root = Environment.getExternalStorageDirectory();
            if (root == null) return false;
            File probe = new File(root, ".dsh_access_probe");
            FileOutputStream o = new FileOutputStream(probe);
            o.write(1);
            o.close();
            return probe.delete();
        } catch (Throwable t) {
            return false;
        }
    }

    private void ensureStorageAccess() {
        if (sharedStorageReady()) {
            Runtime.log(this, "storage: shared storage writable");
            return;
        }
        Runtime.log(this, "storage: no shared-storage access yet");
        new AlertDialog.Builder(this)
                .setTitle(R.string.storage_title)
                .setMessage(R.string.storage_message)
                .setPositiveButton(R.string.storage_grant, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface d, int w) { requestStorageAccess(); }
                })
                .setNegativeButton(R.string.storage_later, null)
                .show();
    }

    private void requestStorageAccess() {
        try {
            requestPermissions(new String[] {
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                    "android.permission.READ_EXTERNAL_STORAGE"
            }, REQ_STORAGE);
        } catch (Throwable t) {
            Runtime.log(this, "request storage perms failed: " + t);
            openAllFilesSettings();
        }
    }

    private void openAllFilesSettings() {
        if (Build.VERSION.SDK_INT < 30) return;
        try {
            startActivity(new Intent("android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION",
                    Uri.parse("package:" + getPackageName())));
        } catch (Throwable t) {
            try {
                startActivity(new Intent("android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"));
            } catch (Throwable t2) {
                Runtime.log(this, "cannot open all-files settings: " + t2);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] granted) {
        super.onRequestPermissionsResult(code, perms, granted);
        if (code != REQ_STORAGE) return;
        if (sharedStorageReady()) {
            Runtime.log(this, "storage: granted — shared storage writable");
            Toast.makeText(this, R.string.storage_ok, Toast.LENGTH_SHORT).show();
        } else {
            Runtime.log(this, "storage: still not writable, opening all-files settings");
            openAllFilesSettings();
        }
    }

    /* ================= 应用内「获取更新」 ================= */
    private static final String UPDATE_REPO = "TaoQiYiYi/DeepSeek-Harness-Android";
    private volatile boolean updateBusy;
    private String pendingApkUrl;

    private void handleShellCommand(String json) {
        try {
            JSONObject o = new JSONObject(json);
            String cmd = o.optString("cmd", "");
            if ("chrome".equals(cmd)) applyChrome(o.optString("bg", null));
            else if ("check".equals(cmd)) startUpdateCheck();
            else if ("install".equals(cmd)) startUpdateInstall(o.optString("url", null));
            else if ("log".equals(cmd)) sendLogToPage();
            else if ("copylog".equals(cmd)) copyLogToClipboard();
        } catch (Throwable t) {
            Runtime.log(this, "shell command failed: " + t);
        }
    }

    private void sendLogToPage() {
        new Thread(new Runnable() {
            public void run() {
                String net = "[网络自检·引擎] " + nodeNetworkTest() + "\n";
                final String log = net + Runtime.tailLog(MainActivity.this, 40000);
                callJs("window.__dshmLog && window.__dshmLog(" + JSONObject.quote(log) + ")");
            }
        }, "log-net").start();
    }

    /** 用运行时自带的 Node 直接请求官方 API，验证引擎侧网络（DNS/TLS/连通性）。 */
    private String nodeNetworkTest() {
        try {
            File rt = Runtime.root(this);
            File node = new File(rt, "bin/node");
            if (!node.exists()) return "(运行时未解压，跳过)";
            String script = "const t=Date.now();fetch('https://api.deepseek.com/',{signal:AbortSignal.timeout(15000)})"
                    + ".then(r=>{console.log('\u6210\u529f HTTP '+r.status+' \u7528\u65f6'+(Date.now()-t)+'ms');process.exit(0)},"
                    + "e=>{console.log('\u5931\u8d25 '+(e&&e.message||e)+(e&&e.cause?(' | '+(e.cause.code||e.cause.message||'')):''));process.exit(0)})";
            ProcessBuilder pb = new ProcessBuilder(node.getAbsolutePath(), "-e", script);
            pb.environment().put("HOME", Runtime.homeDir(this).getAbsolutePath());
            pb.environment().put("PATH", rt.getAbsolutePath() + "/bin:/system/bin:/system/xbin");
            pb.environment().put("LD_LIBRARY_PATH", rt.getAbsolutePath() + "/lib");
            pb.environment().put("OPENSSL_CONF", new File(rt, "etc/tls/openssl.cnf").getAbsolutePath());
            pb.redirectErrorStream(true);
            Process p = pb.start();
            java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(p.getInputStream(), "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = r.readLine()) != null) {
                if (sb.length() > 0) sb.append(' ');
                sb.append(line);
            }
            p.waitFor();
            return sb.length() == 0 ? "(无输出)" : sb.toString();
        } catch (Throwable t) {
            return "\u5f02\u5e38: " + t;
        }
    }

    private void copyLogToClipboard() {
        try {
            final String log = Runtime.tailLog(this, 40000);
            ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
            if (cm != null) {
                cm.setPrimaryClip(ClipData.newPlainText("dsh-log", log));
                runOnUiThread(new Runnable() {
                    public void run() { Toast.makeText(MainActivity.this, "日志已复制到剪贴板", Toast.LENGTH_SHORT).show(); }
                });
            }
        } catch (Throwable t) {
            Runtime.log(this, "copy log failed: " + t);
        }
    }

    /** 主题同步：把界面底色应用到状态栏 / 导航栏，并按亮度切换图标色。 */
    private void applyChrome(String hex) {
        if (hex == null || hex.isEmpty()) return;
        try {
            int c = Color.parseColor(hex);
            int color = 0xFF000000 | (c & 0xFFFFFF);
            getWindow().setStatusBarColor(color);
            getWindow().setNavigationBarColor(color);
            double lum = (0.299 * Color.red(color) + 0.587 * Color.green(color) + 0.114 * Color.blue(color)) / 255.0;
            View dv = getWindow().getDecorView();
            int flags = dv.getSystemUiVisibility();
            int light = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            if (lum > 0.6) flags |= light;
            else flags &= ~light;
            dv.setSystemUiVisibility(flags);
        } catch (Throwable t) {
            Runtime.log(this, "chrome color failed: " + t);
        }
    }

    private void startUpdateCheck() {
        if (updateBusy) return;
        updateBusy = true;
        new Thread(new Runnable() {
            public void run() {
                String payload;
                try {
                    JSONObject rel = githubLatestRelease();
                    String tag = rel.optString("tag_name", "");
                    String latest = (tag.startsWith("v") || tag.startsWith("V")) ? tag.substring(1) : tag;
                    String current = Runtime.APP_VERSION;
                    JSONArray assets = rel.optJSONArray("assets");
                    String apkUrl = null, apkName = null;
                    long apkSize = 0;
                    if (assets != null) {
                        for (int i = 0; i < assets.length(); i++) {
                            JSONObject a = assets.optJSONObject(i);
                            if (a == null) continue;
                            String nm = a.optString("name", "");
                            if (!nm.toLowerCase().endsWith(".apk")) continue;
                            boolean full = nm.toLowerCase().contains("full");
                            if (apkUrl == null || full) {
                                apkUrl = a.optString("browser_download_url", "");
                                apkName = nm;
                                apkSize = a.optLong("size", 0);
                            }
                            if (full) break;
                        }
                    }
                    pendingApkUrl = apkUrl;
                    JSONObject out = new JSONObject();
                    out.put("ok", true);
                    out.put("current", current);
                    out.put("latest", latest);
                    out.put("hasUpdate", compareVersions(latest, current) > 0);
                    out.put("apkUrl", apkUrl == null ? "" : apkUrl);
                    out.put("apkName", apkName == null ? "" : apkName);
                    out.put("apkSize", apkSize);
                    out.put("htmlUrl", rel.optString("html_url", ""));
                    out.put("notes", rel.optString("body", ""));
                    payload = out.toString();
                } catch (Throwable t) {
                    Runtime.log(MainActivity.this, "update check failed: " + t);
                    payload = "{\"ok\":false,\"error\":" + JSONObject.quote(String.valueOf(t.getMessage() == null ? t : t.getMessage())) + "}";
                }
                updateBusy = false;
                callJs("window.__dshUpdateResult && window.__dshUpdateResult(" + payload + ")");
            }
        }, "dsh-update-check").start();
    }

    private JSONObject githubLatestRelease() throws Exception {
        URL url = new URL("https://api.github.com/repos/" + UPDATE_REPO + "/releases/latest");
        HttpURLConnection c = (HttpURLConnection) url.openConnection();
        c.setRequestProperty("Accept", "application/vnd.github+json");
        c.setRequestProperty("User-Agent", "DSHPort-Android");
        c.setConnectTimeout(15000);
        c.setReadTimeout(20000);
        int code = c.getResponseCode();
        if (code == 404) throw new IOException("仓库还没有发布 Release（或仓库不可见）");
        if (code == 403) throw new IOException("GitHub 访问受限（HTTP 403），稍后再试");
        if (code != 200) throw new IOException("GitHub 返回 HTTP " + code);
        return new JSONObject(readStream(c.getInputStream()));
    }

    private void startUpdateInstall(final String apkUrl) {
        final String url = (apkUrl == null || apkUrl.isEmpty()) ? pendingApkUrl : apkUrl;
        if (url == null || url.isEmpty()) {
            callJs("window.__dshUpdateState && window.__dshUpdateState('fail','没有可用的下载地址')");
            return;
        }
        if (updateBusy) return;
        updateBusy = true;
        new Thread(new Runnable() {
            public void run() {
                try {
                    File dir = new File(getFilesDir(), "share");
                    if (!dir.mkdirs() && !dir.isDirectory()) throw new IOException("无法创建下载目录");
                    File out = new File(dir, "dshport-update.apk");
                    HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                    c.setInstanceFollowRedirects(true);
                    c.setRequestProperty("User-Agent", "DSHPort-Android");
                    c.setConnectTimeout(15000);
                    c.setReadTimeout(30000);
                    int code = c.getResponseCode();
                    if (code != 200) throw new IOException("下载失败 HTTP " + code);
                    long total = c.getContentLength();
                    InputStream in = c.getInputStream();
                    FileOutputStream fo = new FileOutputStream(out);
                    byte[] buf = new byte[65536];
                    long done = 0;
                    int lastPct = -1;
                    int n;
                    while ((n = in.read(buf)) > 0) {
                        fo.write(buf, 0, n);
                        done += n;
                        if (total > 0) {
                            int pct = (int) (done * 100 / total);
                            if (pct != lastPct) {
                                lastPct = pct;
                                callJs("window.__dshUpdateProgress && window.__dshUpdateProgress(" + pct + ")");
                            }
                        }
                    }
                    fo.close();
                    in.close();
                    Runtime.log(MainActivity.this, "update downloaded: " + out.length() + " bytes");
                    callJs("window.__dshUpdateProgress && window.__dshUpdateProgress(100)");
                    installApk(out);
                } catch (Throwable t) {
                    Runtime.log(MainActivity.this, "update download failed: " + t);
                    callJs("window.__dshUpdateState && window.__dshUpdateState('fail'," +
                            JSONObject.quote(String.valueOf(t.getMessage() == null ? t : t.getMessage())) + ")");
                }
                updateBusy = false;
            }
        }, "dsh-update-download").start();
    }

    private void installApk(File apk) {
        try {
            Uri uri = Uri.parse("content://" + ShareProvider.AUTHORITY + "/" + Uri.encode(apk.getName()));
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(uri, "application/vnd.android.package-archive");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
            callJs("window.__dshUpdateState && window.__dshUpdateState('done','下载完成，请在系统安装器中确认安装')");
        } catch (Throwable t) {
            Runtime.log(this, "install intent failed: " + t);
            callJs("window.__dshUpdateState && window.__dshUpdateState('fail'," +
                    JSONObject.quote("无法调起系统安装器：" + t) + ")");
        }
    }

    private void callJs(final String code) {
        runOnUiThread(new Runnable() {
            public void run() {
                try { web.evaluateJavascript(code, null); } catch (Throwable ignored) { }
            }
        });
    }

    private static String readStream(InputStream in) throws IOException {
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
        in.close();
        return new String(bo.toByteArray(), "UTF-8");
    }

    private static int compareVersions(String a, String b) {
        int[] x = verParts(a), y = verParts(b);
        int len = Math.max(x.length, y.length);
        for (int i = 0; i < len; i++) {
            int xi = i < x.length ? x[i] : 0;
            int yi = i < y.length ? y[i] : 0;
            if (xi != yi) return xi > yi ? 1 : -1;
        }
        return 0;
    }

    private static int[] verParts(String v) {
        String s = v == null ? "" : v.trim();
        if (s.startsWith("v") || s.startsWith("V")) s = s.substring(1);
        String[] seg = s.split("[^0-9]+");
        int cnt = 0;
        for (String t : seg) if (t.length() > 0) cnt++;
        int[] out = new int[cnt];
        int k = 0;
        for (String t : seg) {
            if (t.length() == 0) continue;
            try { out[k++] = Integer.parseInt(t); } catch (Throwable e) { out[k++] = 0; }
        }
        return out;
    }

    private int buildCode() {
        try {
            return getPackageManager().getPackageInfo(getPackageName(), 0).versionCode;
        } catch (Throwable t) {
            return -1;
        }
    }

    private void startEngine() {
        Intent svc = new Intent(this, ServerService.class);
        try {
            startForegroundService(svc);
        } catch (Throwable t) {
            Runtime.log(this, "startForegroundService failed: " + t);
            startService(svc);
        }
    }

    private void restartEngine() {
        Intent stop = new Intent(this, ServerService.class).setAction(ServerService.ACTION_STOP);
        startService(stop);
        spinner.setVisibility(View.VISIBLE);
        retry.setVisibility(View.GONE);
        status.setVisibility(View.VISIBLE);
        status.setText(R.string.status_booting);
        startEngine();
    }

    private void step() {
        String s = Runtime.readStatus(this);
        if (s.startsWith("EXTRACT") || s.isEmpty()) {
            int pct = 0;
            String[] parts = s.split(" ");
            if (parts.length > 1) {
                try { pct = Integer.parseInt(parts[1]); } catch (Throwable ignored) { }
            }
            spinner.setVisibility(View.VISIBLE);
            retry.setVisibility(View.GONE);
            status.setVisibility(View.VISIBLE);
            status.setText(getString(R.string.status_extracting, pct));
        } else if (s.equals("BOOTING")) {
            spinner.setVisibility(View.VISIBLE);
            retry.setVisibility(View.GONE);
            status.setVisibility(View.VISIBLE);
            status.setText(R.string.status_booting);
        } else if (s.startsWith("READY")) {
            String url = s.length() > 6 ? s.substring(6).trim() : BASE_URL;
            spinner.setVisibility(View.GONE);
            retry.setVisibility(View.GONE);
            overlay.setVisibility(View.GONE);
            if (!url.equals(lastLoaded)) {
                lastLoaded = url;
                Runtime.log(this, "loading " + url.replaceAll("token=[^&]+", "token=***"));
                web.loadUrl(url);
            }
        } else if (s.startsWith("ERROR")) {
            String msg = s.length() > 6 ? s.substring(6).trim() : "未知错误";
            spinner.setVisibility(View.GONE);
            overlay.setVisibility(View.VISIBLE);
            status.setVisibility(View.VISIBLE);
            status.setText(getString(R.string.status_error) + "\n" + msg);
            retry.setVisibility(View.VISIBLE);
        }
    }

    private void showBanner(String text) {
        spinner.setVisibility(View.GONE);
        retry.setVisibility(View.GONE);
        status.setVisibility(View.VISIBLE);
        status.setText(text);
    }

    private void buildUi() {
        FrameLayout root = new FrameLayout(this);

        web = new WebView(this);
        WebSettings st = web.getSettings();
        st.setJavaScriptEnabled(true);
        st.setDomStorageEnabled(true);
        st.setUseWideViewPort(true);
        st.setLoadWithOverviewMode(true);
        st.setMediaPlaybackRequiresUserGesture(false);
        st.setAllowFileAccess(false);
        st.setAllowContentAccess(true);
        web.setBackgroundColor(0xFF0B0D12);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView v, String url, android.graphics.Bitmap favicon) {
                injectMobileJs();
            }
            @Override
            public void onReceivedError(WebView v, WebResourceRequest req, WebResourceError err) {
                if (req != null && req.isForMainFrame()) {
                    Runtime.log(MainActivity.this, "load error: " + err.getDescription());
                }
            }
            @Override
            public void onPageFinished(WebView v, String url) {
                injectMobileJs();
                injectCriticalCss();
                Runtime.log(MainActivity.this, "page finished: " + url.replaceAll("token=[^&]+", "token=***"));
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                String msg = m == null ? null : m.message();
                if (msg != null && msg.startsWith("__DSHM__")) {
                    handleShellCommand(msg.substring(8));
                    return true;
                }
                Runtime.log(MainActivity.this, "js: " + msg);
                return true;
            }
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams params) {
                fileCallback = cb;
                try {
                    Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("*/*");
                    startActivityForResult(Intent.createChooser(i, "选择文件"), REQ_FILE);
                    return true;
                } catch (Throwable t) {
                    fileCallback = null;
                    return false;
                }
            }
        });
        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        overlay = new LinearLayout(this);
        overlay.setOrientation(LinearLayout.VERTICAL);
        overlay.setGravity(Gravity.CENTER);
        overlay.setPadding(48, 48, 48, 48);
        overlay.setBackgroundColor(0xF00B0D12);
        spinner = new ProgressBar(this);
        overlay.addView(spinner);
        status = new TextView(this);
        status.setTextColor(0xFFE8EAF0);
        status.setGravity(Gravity.CENTER);
        status.setPadding(0, 24, 0, 24);
        overlay.addView(status);
        retry = new Button(this);
        retry.setText(R.string.retry);
        retry.setVisibility(View.GONE);
        retry.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) { restartEngine(); }
        });
        overlay.addView(retry);
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
        root.addView(overlay, lp);

        // ⋯ 菜单按钮已按用户要求彻底移除（不设任何隐藏入口）

        setContentView(root);
    }

    /** 由 App 直接注入的关键布局 CSS —— 不依赖 mobile.js 是否运行成功。 */
    private void injectCriticalCss() {
        try {
            String css = Runtime.readAll(getAssets().open("mobile-critical.css"));
            String js = "(function(){try{if(document.getElementById('dshm-crit'))return;"
                    + "var s=document.createElement('style');s.id='dshm-crit';"
                    + "s.textContent=" + JSONObject.quote(css) + ";"
                    + "(document.head||document.documentElement).appendChild(s);}catch(e){}})();";
            web.evaluateJavascript(js, null);
        } catch (Throwable t) {
            Runtime.log(this, "critical css inject failed: " + t);
        }
    }

    private void injectMobileJs() {
        try {
            web.evaluateJavascript("window.__dshAppVersion='" + Runtime.APP_VERSION + "';"
                    + "window.__dshAppBuild=" + buildCode() + ";"
                    + "window.__dshCoreVersion='" + Runtime.coreVersion(this) + "';", null);
            final String js = Runtime.readAll(getAssets().open("mobile.js"));
            web.evaluateJavascript(js, null);
        } catch (Throwable t) {
            Runtime.log(this, "mobile js inject failed: " + t);
        }
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    private void showMenu() {
        String[] items = new String[] { "重启引擎 / 重新载入", "查看运行日志", "关于" };
        new AlertDialog.Builder(this)
                .setTitle("DSH")
                .setItems(items, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface d, int which) {
                        if (which == 0) {
                            if (embedded) restartEngine();
                            else web.loadUrl(BASE_URL);
                        } else if (which == 1) {
                            showLog();
                        } else {
                            String info = "本应用 = 官方 DeepSeek Harness 移动端移植壳\n"
                                    + "版本 " + Runtime.APP_VERSION + "\n"
                                    + "运行时: " + (embedded ? "内嵌" : "未内嵌（直连模式）") + "\n"
                                    + "服务地址: " + BASE_URL;
                            new AlertDialog.Builder(MainActivity.this).setMessage(info)
                                    .setPositiveButton("好", null).show();
                        }
                    }
                })
                .show();
    }

    private void showLog() {
        String log = Runtime.tailLog(this, 60000);
        TextView tv = new TextView(this);
        tv.setText(log);
        tv.setTextSize(10);
        tv.setTextIsSelectable(true);
        ScrollView sv = new ScrollView(this);
        sv.addView(tv);
        new AlertDialog.Builder(this)
                .setTitle("运行日志")
                .setView(sv)
                .setPositiveButton("复制", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface d, int w) {
                        ClipboardManager cm = (ClipboardManager) MainActivity.this.getSystemService(CLIPBOARD_SERVICE);
                        if (cm != null) {
                            cm.setPrimaryClip(ClipData.newPlainText("dsh-log", log));
                            Toast.makeText(MainActivity.this, "已复制", Toast.LENGTH_SHORT).show();
                        }
                    }
                })
                .setNegativeButton("关闭", null)
                .show();
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_FILE) {
            Uri[] out = null;
            if (res == RESULT_OK && data != null && data.getData() != null) {
                out = new Uri[]{ data.getData() };
            }
            if (fileCallback != null) {
                fileCallback.onReceiveValue(out);
                fileCallback = null;
            }
            return;
        }
        super.onActivityResult(req, res, data);
    }

    @Override
    public void onBackPressed() {
        // 逐级返回：先让页面关掉面板/弹窗，再回退网页历史，最后才退出应用。
        if (web == null || status == null) {
            backFallback(false);
            return;
        }
        try {
            web.evaluateJavascript(
                    "(function(){try{return window.__dshmBack?window.__dshmBack():false}catch(e){return false}})()",
                    new ValueCallback<String>() {
                        @Override public void onReceiveValue(String value) {
                            backFallback(value != null && value.contains("true"));
                        }
                    });
        } catch (Throwable t) {
            backFallback(false);
        }
    }

    private void backFallback(boolean pageHandled) {
        if (pageHandled) return;
        try {
            if (web != null && web.canGoBack()) {
                web.goBack();
                return;
            }
        } catch (Throwable ignored) { }
        try {
            super.onBackPressed();
        } catch (Throwable ignored) { }
    }

    @Override
    protected void onDestroy() {
        handler.removeCallbacks(poll);
        super.onDestroy();
    }
}
