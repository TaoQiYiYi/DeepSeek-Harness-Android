package com.dshport.mobile;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

/** Minimal read-only provider exposing files/share/ for ACTION_VIEW intents. */
public class ShareProvider extends ContentProvider {
    public static final String AUTHORITY = "com.dshport.mobile.share";

    @Override
    public boolean onCreate() { return true; }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (!"r".equals(mode)) throw new FileNotFoundException("read-only provider");
        String name = uri.getLastPathSegment();
        if (name == null || name.isEmpty() || name.contains("/") || name.contains("\\") || name.contains("..")) {
            throw new FileNotFoundException("invalid name");
        }
        File dir = new File(getContext().getFilesDir(), "share");
        File f = new File(dir, name);
        try {
            String dirPath = dir.getCanonicalPath() + File.separator;
            if (!f.getCanonicalPath().startsWith(dirPath)) throw new FileNotFoundException("path escape");
        } catch (IOException e) {
            throw new FileNotFoundException("bad path");
        }
        if (!f.exists()) throw new FileNotFoundException("missing " + name);
        return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public String getType(Uri uri) {
        String name = uri == null ? null : uri.getLastPathSegment();
        if (name != null && name.toLowerCase().endsWith(".apk")) return "application/vnd.android.package-archive";
        return "text/plain";
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) { return null; }

    @Override
    public Uri insert(Uri uri, ContentValues values) { return null; }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) { return 0; }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) { return 0; }
}
