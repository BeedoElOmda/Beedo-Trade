package io.github.beedoelomda.beedotrade;

import android.app.Activity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.work.Constraints;
import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.NetworkType;
import androidx.work.OneTimeWorkRequest;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.util.Calendar;
import java.util.TimeZone;
import java.util.concurrent.TimeUnit;

/**
 * The daily alert check after the EGX close (scheduled for 15:00 Cairo time), which Android runs even when the app
 * is closed. The check itself is the desktop engine's, in Python (beedotrade/alerts.py). Copied into the Briefcase
 * Android project by .github/workflows/build-android.yml.
 */
public class AlertWorker extends Worker {
    private static final String TAG = "BeedoAlerts";
    private static final String CHANNEL = "alerts";

    public AlertWorker(@NonNull Context context, @NonNull WorkerParameters params) {
        super(context, params);
    }

    @NonNull
    @Override
    public Result doWork() {
        Context ctx = getApplicationContext();
        try {
            if (!Python.isStarted()) {  // the app is closed: start Python just for the check
                AndroidPlatform platform = new AndroidPlatform(ctx);
                platform.redirectStdioToLogcat();
                Python.start(platform);
            }
            Python.getInstance().getModule("beedotrade.alerts").callAttr("run", ctx);
            return Result.success();
        } catch (Exception e) {
            Log.e(TAG, "Alert check failed", e);
            return Result.retry();
        }
    }

    /** One check a day at 15:00 Cairo time, when the phone is online. Called each time the app starts; keeps an existing schedule. */
    public static void schedule(Context ctx) {
        Calendar now = Calendar.getInstance(TimeZone.getTimeZone("Africa/Cairo"));
        Calendar next = (Calendar) now.clone();
        next.set(Calendar.HOUR_OF_DAY, 15);
        next.set(Calendar.MINUTE, 0);
        next.set(Calendar.SECOND, 0);
        if (!next.after(now)) next.add(Calendar.DAY_OF_MONTH, 1);
        PeriodicWorkRequest req = new PeriodicWorkRequest.Builder(AlertWorker.class, 1, TimeUnit.DAYS)
                .setInitialDelay(next.getTimeInMillis() - now.getTimeInMillis(), TimeUnit.MILLISECONDS)
                .setConstraints(new Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
                .build();
        WorkManager.getInstance(ctx).enqueueUniquePeriodicWork("beedo-alerts", ExistingPeriodicWorkPolicy.KEEP, req);
    }

    /** Runs the check once, now (used by the emulator test). */
    public static void runNow(Context ctx) {
        WorkManager.getInstance(ctx).enqueue(new OneTimeWorkRequest.Builder(AlertWorker.class).build());
    }

    /** Shows one notification; tapping it opens the app. */
    public static void show(Context ctx, int id, String title, String text) {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Alerts", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Price, score and signal alerts for your stocks");
            ctx.getSystemService(NotificationManager.class).createNotificationChannel(ch);
        }
        Intent open = ctx.getPackageManager().getLaunchIntentForPackage(ctx.getPackageName());
        PendingIntent tap = open == null ? null
                : PendingIntent.getActivity(ctx, 0, open, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_popup_reminder)  // a plain system icon: app icons can't be notification icons
                .setContentTitle(title)
                .setContentText(text)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                .setAutoCancel(true)
                .setContentIntent(tap);
        try {
            NotificationManagerCompat.from(ctx).notify(id, b.build());
        } catch (SecurityException e) {
            Log.w(TAG, "Notifications are switched off for Mo'ashir Trade");
        }
    }

    /** Android 13 and later: ask once for permission to show notifications. */
    public static void askPermission(Activity a) {
        if (Build.VERSION.SDK_INT >= 33
                && a.checkSelfPermission("android.permission.POST_NOTIFICATIONS") != PackageManager.PERMISSION_GRANTED) {
            a.requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, 7);
        }
    }
}
