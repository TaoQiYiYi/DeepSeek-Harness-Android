package com.dshport.mobile;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.IBinder;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Foreground service that boots and supervises the official dsh web server. */
public class ServerService extends Service {
    static final int PORT = 3080;
    static final String CHANNEL = "dsh";
    static final String ACTION_STOP = "com.dshport.mobile.STOP";

    private Process proc;
    private Thread worker;
    private volatile boolean stopping = false;
    private Thread shareWatcher;
    private volatile boolean watcherRun = false;

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL,
                    getString(R.string.notif_channel), NotificationManager.IMPORTANCE_LOW);
            nm.createNotificationChannel(ch);
        }
        startForeground(1, notif("引擎启动中…"));
        startShareWatcher();
    }

    private Notification notif(String text) {
        Intent i = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 0, i,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        return new Notification.Builder(this, CHANNEL)
                .setSmallIcon(android.R.drawable.stat_notify_sync)
                .setContentTitle(getString(R.string.notif_title))
                .setContentText(text)
                .setContentIntent(pi)
                .setOngoing(true)
                .build();
    }

    private void updateNotif(String text) {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) nm.notify(1, notif(text));
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopEverything();
            stopSelf();
            return START_NOT_STICKY;
        }
        if (worker == null || !worker.isAlive()) {
            stopping = false;
            worker = new Thread(new Runnable() {
                public void run() { runEngine(); }
            }, "dsh-engine");
            worker.start();
        }
        return START_STICKY;
    }

    private int pickPort() {
        ArrayList<Integer> candidates = new ArrayList<>();
        int sticky = readStickyPort();
        if (sticky > 0) candidates.add(sticky);
        for (int p = PORT; p < PORT + 10; p++) {
            if (!candidates.contains(p)) candidates.add(p);
        }
        for (int p : candidates) {
            ServerSocket s = null;
            try {
                s = new ServerSocket(p, 1, InetAddress.getByAddress(new byte[] { 127, 0, 0, 1 }));
                writeStickyPort(p);
                return p;
            } catch (Throwable ignored) {
            } finally {
                if (s != null) try { s.close(); } catch (Throwable ignored) { }
            }
        }
        return PORT;
    }

    private int readStickyPort() {
        try {
            return Integer.parseInt(Runtime.readAll(new FileInputStream(new File(getFilesDir(), "port.txt"))).trim());
        } catch (Throwable t) {
            return -1;
        }
    }

    private void writeStickyPort(int p) {
        try {
            FileWriter w = new FileWriter(new File(getFilesDir(), "port.txt"));
            w.write(String.valueOf(p));
            w.close();
        } catch (Throwable ignored) { }
    }

    private void runEngine() {
        Context ctx = this;
        try {
            Runtime.log(ctx, "startup: " + Runtime.debugState(ctx) + " marker=" + Runtime.ensureSentinel(ctx));
            if (!Runtime.runtimeReady(ctx)) {
                Runtime.writeStatus(ctx, "EXTRACT 0");
                Runtime.log(ctx, "extracting bundled runtime…");
                long t0 = System.currentTimeMillis();
                Runtime.extract(ctx, new Runtime.Progress() {
                    public void onProgress(int pct) { Runtime.writeStatus(ctx, "EXTRACT " + pct); }
                });
                Runtime.log(ctx, "extract done in " + (System.currentTimeMillis() - t0) / 1000 + "s");
            }
            Runtime.writeStatus(ctx, "BOOTING");
            updateNotif("引擎启动中…");

            File rt = Runtime.root(ctx);
            File home = Runtime.homeDir(ctx);
            File dshHome = Runtime.dshHome(ctx);
            if (!home.mkdirs() && !home.isDirectory()) Runtime.log(ctx, "warn: home mkdir failed");
            if (!dshHome.mkdirs() && !dshHome.isDirectory()) Runtime.log(ctx, "warn: dsh home mkdir failed");
            if (!Runtime.tmpDir(ctx).mkdirs() && !Runtime.tmpDir(ctx).isDirectory()) Runtime.log(ctx, "warn: tmp mkdir failed");

            List<String> cmd = new ArrayList<>();
            cmd.add(Runtime.nodeBin(ctx).getAbsolutePath());
            cmd.add("--expose-internals");
            cmd.add(Runtime.dshEntry(ctx).getAbsolutePath());
            cmd.add("web");
            cmd.add("--no-open");
            cmd.add("--host");
            cmd.add("127.0.0.1");
            int port = pickPort();
            Runtime.log(ctx, "using port " + port);
            cmd.add("--port");
            cmd.add(String.valueOf(port));

            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.directory(home);
            Map<String, String> env = pb.environment();
            env.put("HOME", home.getAbsolutePath());
            env.put("DSH_HOME", dshHome.getAbsolutePath());
            env.put("TMPDIR", Runtime.tmpDir(ctx).getAbsolutePath());
            env.put("PATH", rt.getAbsolutePath() + "/bin:/system/bin:/system/xbin");
            env.put("LD_LIBRARY_PATH", rt.getAbsolutePath() + "/lib");
            env.put("LANG", "C.UTF-8");
            env.put("DSH_SHARE_DIR", new File(getFilesDir(), "share").getAbsolutePath());
            pb.redirectErrorStream(true);

            Runtime.log(ctx, "spawn: " + cmd);
            proc = pb.start();
            BufferedReader r = new BufferedReader(new InputStreamReader(proc.getInputStream(), "UTF-8"));
            String line;
            while ((line = r.readLine()) != null) {
                Runtime.log(ctx, "[engine] " + line);
                int idx = line.indexOf("http://127.0.0.1:");
                if (idx >= 0 && line.indexOf("token=") > idx) {
                    String url = line.substring(idx).trim();
                    int sp = url.indexOf(' ');
                    if (sp > 0) url = url.substring(0, sp);
                    Runtime.writeStatus(ctx, "READY " + url);
                    updateNotif("运行中 · 端口 " + port);
                }
            }
            int code = proc.waitFor();
            Runtime.log(ctx, "engine exited, code=" + code);
            Runtime.writeStatus(ctx, stopping ? "STOPPED" : "ERROR 引擎进程退出（code " + code + "），请查看日志");
        } catch (Throwable t) {
            Runtime.log(ctx, "engine failed: " + t);
            Runtime.writeStatus(ctx, "ERROR " + t);
        }
    }

    private void startShareWatcher() {
        watcherRun = true;
        shareWatcher = new Thread(new Runnable() {
            public void run() {
                File dir = new File(getFilesDir(), "share");
                File req = new File(dir, ".request");
                while (watcherRun) {
                    try {
                        if (req.exists()) {
                            String name = Runtime.readAll(new FileInputStream(req)).trim();
                            boolean ignored = req.delete();
                            if (!name.isEmpty()) openSharedFile(name);
                        }
                        Thread.sleep(800);
                    } catch (Throwable t) {
                        Runtime.log(ServerService.this, "share watcher: " + t);
                        try { Thread.sleep(2000); } catch (Throwable ignored2) { }
                    }
                }
            }
        }, "share-watcher");
        shareWatcher.start();
    }

    private void openSharedFile(String name) {
        try {
            File dir = new File(getFilesDir(), "share");
            File f = new File(dir, name);
            if (!f.getCanonicalPath().startsWith(dir.getCanonicalPath() + File.separator)) {
                Runtime.log(this, "openSharedFile: rejected name " + name);
                return;
            }
            if (!f.exists()) {
                Runtime.log(this, "openSharedFile: missing " + name);
                return;
            }
            Uri uri = Uri.parse("content://" + ShareProvider.AUTHORITY + "/" + Uri.encode(name));
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(uri, mimeOf(name));
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
            Runtime.log(this, "openSharedFile: intent fired for " + name);
        } catch (android.content.ActivityNotFoundException anf) {
            Runtime.log(this, "openSharedFile: no app can view " + name);
            NotificationManager nm2 = getSystemService(NotificationManager.class);
            if (nm2 != null) nm2.notify(2, notif("未找到可打开该文件的应用，副本已保留在应用内"));
        } catch (Throwable t) {
            Runtime.log(this, "openSharedFile failed: " + t);
        }
    }

    private String mimeOf(String name) {
        String n = name.toLowerCase();
        if (n.endsWith(".json")) return "application/json";
        return "text/plain";
    }

    private void stopEverything() {
        stopping = true;
        try { if (proc != null) proc.destroy(); } catch (Throwable ignored) { }
        Runtime.writeStatus(this, "STOPPED");
    }

    @Override
    public void onDestroy() {
        watcherRun = false;
        stopEverything();
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) { return null; }
}
