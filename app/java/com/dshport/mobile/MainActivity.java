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

public class MainActivity extends Activity {
    private static final String BASE_URL = "http://127.0.0.1:3080/";
    private static final int REQ_FILE = 41;

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
                Runtime.log(MainActivity.this, "page finished: " + url.replaceAll("token=[^&]+", "token=***"));
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                Runtime.log(MainActivity.this, "js: " + m.message());
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

    private void injectMobileJs() {
        try {
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
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        handler.removeCallbacks(poll);
        super.onDestroy();
    }
}
