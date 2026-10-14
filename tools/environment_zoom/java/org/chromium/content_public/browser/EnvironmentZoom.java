// Copyright 2026 Titanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.content_public.browser;

import android.app.Activity;
import android.content.ComponentCallbacks;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.hardware.display.DisplayManager;
import android.os.Handler;
import android.os.Looper;
import android.view.Display;

import org.chromium.base.ContextUtils;
import org.chromium.content.browser.HostZoomMapImpl;
import org.chromium.ui.base.WindowAndroid;
import org.chromium.ui.display.DisplayAndroid;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** UI-thread-only bridge; no application-wide host/default zoom switching. */
public final class EnvironmentZoom {
    private static final Map<BrowserContextHandle, EnvironmentZoomPolicy> STORES = new WeakHashMap<>();
    private static final Map<WebContents, BrowserContextHandle> CONTENTS = new WeakHashMap<>();
    private static final Map<BrowserContextHandle, Boolean> LEGACY_DEFAULTS = new WeakHashMap<>();
    private static final Map<Activity, Boolean> ACTIVITIES = new WeakHashMap<>();
    private static final Handler HANDLER = new Handler(Looper.getMainLooper());
    private static boolean listening;
    private EnvironmentZoom() {}

    public static void registerLegacyDefaultPresence(BrowserContextHandle context, boolean present) {
        LEGACY_DEFAULTS.put(context, present);
    }
    public static EnvironmentZoomPolicy store(BrowserContextHandle context) {
        EnvironmentZoomPolicy cached = STORES.get(context);
        if (cached != null) return cached;
        // Native profile path scopes the file, including future multiple regular profiles.
        String key = HostZoomMapImpl.getEnvironmentProfileKey(context);
        SharedPreferences prefs = ContextUtils.getApplicationContext().getSharedPreferences(
                "titanium_environment_zoom_" + key, Context.MODE_PRIVATE);
        boolean privateProfile = HostZoomMapImpl.isEnvironmentPrivate(context);
        EnvironmentZoomPolicy.Storage storage = new EnvironmentZoomPolicy.Storage() {
            private Map<String, String> memory = readPrefs();
            private Map<String, String> readPrefs() {
                Map<String, String> result = new LinkedHashMap<>();
                for (Map.Entry<String, ?> e : prefs.getAll().entrySet()) {
                    if (e.getValue() instanceof String) result.put(e.getKey(), (String) e.getValue());
                }
                return result;
            }
            @Override public Map<String, String> read() { return new LinkedHashMap<>(memory); }
            @Override public void write(Map<String, String> values) {
                if (!privateProfile) {
                    SharedPreferences.Editor editor = prefs.edit().clear();
                    for (Map.Entry<String, String> e : values.entrySet()) editor.putString(e.getKey(), e.getValue());
                    // One transaction contains migration marker AND both complete maps.
                    // Refuse a readiness claim when durable persistence fails.
                    if (!editor.commit()) throw new IllegalStateException("Zoom persistence failed");
                }
                memory = new LinkedHashMap<>(values);
            }
        };
        EnvironmentZoomPolicy result = new EnvironmentZoomPolicy(storage,
                HostZoomMap.getDefaultZoomLevel(context), HostZoomMap.getAllHostZoomLevels(context),
                LEGACY_DEFAULTS.getOrDefault(context, false));
        STORES.put(context, result);
        return result;
    }

    public static void attach(WebContents contents, BrowserContextHandle context) {
        store(context); // Migrate before a renderer can query the new zoom path.
        CONTENTS.put(contents, context);
        Activity activity = activity(contents);
        if (activity != null && !ACTIVITIES.containsKey(activity)) {
            ACTIVITIES.put(activity, true);
            activity.registerComponentCallbacks(new ComponentCallbacks() {
                @Override public void onConfigurationChanged(Configuration c) { scheduleRefresh(); }
                @Override public void onLowMemory() {}
            });
        }
        if (!listening) {
            listening = true;
            DisplayManager manager = (DisplayManager) ContextUtils.getApplicationContext()
                    .getSystemService(Context.DISPLAY_SERVICE);
            if (manager != null) manager.registerDisplayListener(new DisplayManager.DisplayListener() {
                @Override public void onDisplayAdded(int id) { scheduleRefresh(); }
                @Override public void onDisplayRemoved(int id) { scheduleRefresh(); }
                @Override public void onDisplayChanged(int id) { scheduleRefresh(); }
            }, HANDLER);
        }
        refresh(contents);
    }
    public static void forgetContext(BrowserContextHandle context) {
        STORES.remove(context);
        LEGACY_DEFAULTS.remove(context);
        CONTENTS.values().removeIf(value -> value == context);
    }
    private static Activity activity(WebContents contents) {
        WindowAndroid window = contents.getTopLevelNativeWindow();
        return window == null ? null : window.getActivity().get();
    }
    public static EnvironmentZoomPolicy.Environment environment(Context context) {
        int displayId = DisplayAndroid.getNonMultiDisplay(context).getDisplayId();
        // Override is display-scoped. It changes classification, never the zoom values themselves.
        String mode = ContextUtils.getAppSharedPreferences().getString(
                "titanium.zoom.display." + displayId, "auto");
        boolean dex = "dex".equals(mode) || ("auto".equals(mode)
                && displayId != Display.DEFAULT_DISPLAY);
        return dex ? EnvironmentZoomPolicy.Environment.DEX : EnvironmentZoomPolicy.Environment.MOBILE;
    }
    public static String displayMode(Context context) {
        int displayId = DisplayAndroid.getNonMultiDisplay(context).getDisplayId();
        return ContextUtils.getAppSharedPreferences().getString(
                "titanium.zoom.display." + displayId, "auto");
    }
    public static void setDisplayMode(Context context, String mode) {
        int displayId = DisplayAndroid.getNonMultiDisplay(context).getDisplayId();
        ContextUtils.getAppSharedPreferences().edit().putString(
                "titanium.zoom.display." + displayId, mode).apply();
        refreshAll();
    }
    public static double defaultFor(WebContents contents) {
        BrowserContextHandle context = CONTENTS.get(contents);
        Activity activity = activity(contents);
        return context == null || activity == null ? Double.NaN
                : store(context).defaultFactor(environment(activity));
    }
    public static double resolve(WebContents contents, String host) {
        BrowserContextHandle context = CONTENTS.get(contents);
        Activity activity = activity(contents);
        return context == null || activity == null ? Double.NaN
                : store(context).resolve(environment(activity), host);
    }
    // Used at native RFH zoom lookup, including navigation, restore, BFCache and renderer swaps.
    public static double rendered(WebContents contents, String host) {
        double level = resolve(contents, host);
        Activity activity = activity(contents);
        if (!Double.isFinite(level) || activity == null) return Double.NaN;
        float font = HostZoomMap.shouldAdjustForOSLevel()
                ? activity.getResources().getConfiguration().fontScale : 1.0f;
        // Do not use HostZoomMap's process-global external-monitor scale.
        return level + Math.log(font) / Math.log(1.2);
    }
    public static boolean save(WebContents contents, String host, double factor) {
        BrowserContextHandle context = CONTENTS.get(contents);
        Activity activity = activity(contents);
        if (context == null || activity == null) return false;
        // Presets rounded in upstream must also represent their displayed integer percentage.
        double absolute = EnvironmentZoomPolicy.factor(Math.max(50, Math.min(300,
                EnvironmentZoomPolicy.percent(factor))));
        store(context).setSite(environment(activity), host, absolute);
        refreshAll();
        return true;
    }
    public static boolean reset(WebContents contents) {
        BrowserContextHandle context = CONTENTS.get(contents);
        Activity activity = activity(contents);
        if (context == null || activity == null) return false;
        store(context).resetSite(environment(activity), HostZoomMapImpl.getEnvironmentHost(contents));
        refreshAll();
        return true;
    }
    private static void scheduleRefresh() { HANDLER.post(EnvironmentZoom::refreshAll); }
    public static void refreshAll() {
        for (WebContents contents : new ArrayList<>(CONTENTS.keySet())) refresh(contents);
    }
    private static void refresh(WebContents contents) {
        if (!contents.isDestroyed() && activity(contents) != null) HostZoomMapImpl.refreshEnvironmentZoom(contents);
    }
}
