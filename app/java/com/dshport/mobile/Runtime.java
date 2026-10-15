package com.dshport.mobile;

import android.content.Context;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Paths, logging, status file and first-run runtime extraction. */
final class Runtime {
    static final String APP_VERSION = "0.2.2-rc3";
    static final String RUNTIME_VERSION = "0.2.2-rc1-r8";

    private Runtime() {}

    static File root(Context c) { return new File(c.getFilesDir(), "runtime"); }
    static File nodeBin(Context c) { return new File(root(c), "bin/node"); }
    static File dshEntry(Context c) {
        return new File(root(c), "node_modules/@deepseek-ai/dsh/lib/bin.js");
    }
    static File homeDir(Context c) { return new File(c.getFilesDir(), "home"); }
    static File dshHome(Context c) { return new File(c.getFilesDir(), "dsh"); }
    static File tmpDir(Context c) { return new File(c.getFilesDir(), "tmp"); }
    static File logFile(Context c) { return new File(c.getFilesDir(), "logs/server.log"); }
    static File statusFile(Context c) { return new File(c.getFilesDir(), "status"); }

    /** Whether this APK bundles a runtime at all (assets/runtime.zip). */
    static boolean runtimeBundled(Context c) {
        try { InputStream in = c.getAssets().open("runtime.zip"); in.close(); return true; }
        catch (IOException e) { return false; }
    }

    static boolean runtimeReady(Context c) {
        File ok = new File(root(c), ".ok");
        if (!ok.exists()) return false;
        try {
            String s = readAll(new FileInputStream(ok)).trim();
            return s.startsWith(RUNTIME_VERSION) && nodeBin(c).exists() && dshEntry(c).exists();
        } catch (Throwable t) {
            return false;
        }
    }

    static synchronized void log(Context c, String line) {
        try {
            File f = logFile(c);
            File p = f.getParentFile();
            if (p != null) p.mkdirs();
            if (f.length() > 1024 * 1024) { boolean ignored = f.delete(); }
            FileWriter w = new FileWriter(f, true);
            w.write(new SimpleDateFormat("HH:mm:ss", Locale.US).format(new Date()) + "  " + line + "\n");
            w.close();
        } catch (Throwable ignored) { }
    }

    static String readStatus(Context c) {
        try { return readAll(new FileInputStream(statusFile(c))).trim(); }
        catch (Throwable t) { return ""; }
    }

    static void writeStatus(Context c, String s) {
        try {
            File f = statusFile(c);
            File p = f.getParentFile();
            if (p != null) p.mkdirs();
            FileOutputStream o = new FileOutputStream(f);
            o.write(s.getBytes("UTF-8"));
            o.close();
        } catch (Throwable ignored) { }
    }

    static String tailLog(Context c, int maxChars) {
        try {
            String all = readAll(new FileInputStream(logFile(c)));
            if (all.length() <= maxChars) return all;
            return all.substring(all.length() - maxChars);
        } catch (Throwable t) { return "(无日志)"; }
    }

    static String debugState(Context c) {
        StringBuilder sb = new StringBuilder();
        sb.append("ready=").append(runtimeReady(c));
        File ok = new File(root(c), ".ok");
        sb.append(" okExists=").append(ok.exists());
        if (ok.exists()) {
            try { sb.append(" ok='").append(readAll(new FileInputStream(ok)).trim()).append('\''); }
            catch (Throwable t) { sb.append(" okReadError"); }
        }
        sb.append(" node=").append(nodeBin(c).exists());
        sb.append(" dsh=").append(dshEntry(c).exists());
        File[] kids = c.getFilesDir().listFiles();
        sb.append(" filesDirItems=").append(kids == null ? -1 : kids.length);
        File[] dshKids = dshHome(c).listFiles();
        sb.append(" dshHomeItems=").append(dshKids == null ? -1 : dshKids.length);
        return sb.toString();
    }

    static String ensureSentinel(Context c) {
        File f = new File(c.getFilesDir(), ".install_marker");
        if (!f.exists()) {
            try {
                FileWriter w = new FileWriter(f);
                w.write("first-seen " + System.currentTimeMillis());
                w.close();
            } catch (Throwable ignored) { }
        }
        try { return readAll(new FileInputStream(f)).trim(); }
        catch (Throwable t) { return "(unreadable)"; }
    }

    /** 已解压运行时的 DSH 核心版本；未解压时返回空串。 */
    static String coreVersion(Context c) {
        try {
            File pkg = new File(root(c), "node_modules/@deepseek-ai/dsh/package.json");
            String s = readAll(new FileInputStream(pkg));
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("\"version\"\\s*:\\s*\"([^\"]+)\"").matcher(s);
            if (m.find()) return m.group(1);
        } catch (Throwable ignored) { }
        return "";
    }

    static String readAll(InputStream in) throws IOException {
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
        in.close();
        return new String(bo.toByteArray(), "UTF-8");
    }

    interface Progress { void onProgress(int pct); }

    /** Extract assets/runtime.zip into filesDir/runtime. Blocking; call off main thread. */
    static void extract(Context c, Progress p) throws IOException {
        File rt = root(c);
        deleteRec(rt);
        if (!rt.mkdirs() && !rt.isDirectory()) throw new IOException("无法创建运行时目录");

        long total = 256L * 1024 * 1024;
        try {
            String s = readAll(c.getAssets().open("runtime.size")).trim();
            total = Long.parseLong(s);
        } catch (Throwable ignored) { }

        ZipInputStream zin = new ZipInputStream(new BufferedInputStream(c.getAssets().open("runtime.zip"), 1 << 16));
        byte[] buf = new byte[1 << 16];
        long done = 0;
        int lastPct = -1;
        ZipEntry e;
        StringBuilder links = new StringBuilder();
        while ((e = zin.getNextEntry()) != null) {
            String name = e.getName();
            if (name.startsWith("/") || name.contains("..")) continue;
            if ("_links.tsv".equals(name)) {
                ByteArrayOutputStream lb = new ByteArrayOutputStream();
                int n0;
                while ((n0 = zin.read(buf)) > 0) lb.write(buf, 0, n0);
                links.append(new String(lb.toByteArray(), "UTF-8"));
                continue;
            }
            File out = new File(rt, name);
            if (e.isDirectory()) { out.mkdirs(); continue; }
            File parent = out.getParentFile();
            if (parent != null) parent.mkdirs();
            FileOutputStream o = new FileOutputStream(out);
            int n;
            while ((n = zin.read(buf)) > 0) { o.write(buf, 0, n); done += n; }
            o.close();
            if (name.startsWith("bin/") || name.endsWith("/bin/node")) {
                out.setExecutable(true, false);
                out.setReadable(true, false);
            }
            if (p != null) {
                int pct = (int) Math.min(99, done * 100 / Math.max(1, total));
                if (pct != lastPct) { lastPct = pct; p.onProgress(pct); }
            }
        }
        zin.close();

        int made = 0;
        for (String ln : links.toString().split("\n")) {
            if (ln.trim().length() == 0) continue;
            String[] parts = ln.split("\t");
            if (parts.length != 2) continue;
            try {
                File lp = new File(rt, parts[0]);
                File parent = lp.getParentFile();
                if (parent != null) parent.mkdirs();
                if (lp.exists() || java.nio.file.Files.isSymbolicLink(lp.toPath())) {
                    boolean ignored = lp.delete();
                }
                java.nio.file.Files.createSymbolicLink(lp.toPath(),
                        java.nio.file.Paths.get(parts[1]));
                made++;
            } catch (Throwable ignored) { }
        }
        log(c, "runtime extracted, symlinks created: " + made);

        File ok = new File(rt, ".ok");
        FileWriter w = new FileWriter(ok);
        w.write(RUNTIME_VERSION + " " + System.currentTimeMillis());
        w.close();
    }

    static void deleteRec(File f) {
        if (f == null || !f.exists()) return;
        if (f.isDirectory()) {
            File[] kids = f.listFiles();
            if (kids != null) for (File k : kids) deleteRec(k);
        }
        boolean ignored = f.delete();
    }
}
