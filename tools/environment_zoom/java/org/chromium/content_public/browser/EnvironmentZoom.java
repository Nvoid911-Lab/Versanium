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
import org.chromium.base.StrictModeContext;
import org.chromium.base.ThreadUtils;
import org.chromium.base.Log;
import org.chromium.content.browser.HostZoomMapImpl;
import org.chromium.ui.base.WindowAndroid;
import org.chromium.ui.display.DisplayAndroid;

import java.util.ArrayList;
import java.lang.ref.WeakReference;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** UI-thread-only bridge; no application-wide host/default zoom switching. */
public final class EnvironmentZoom {
    private static final Map<BrowserContextHandle, EnvironmentZoomPolicy> STORES = new WeakHashMap<>();
    private static final Map<WebContents, Runnable> ENVIRONMENT_LISTENERS = new WeakHashMap<>();
    private static final Map<WebContents, Binding> CONTENTS = new WeakHashMap<>();
    private static final Map<BrowserContextHandle, Boolean> LEGACY_DEFAULTS = new WeakHashMap<>();
    private static final Map<String, WeakReference<EnvironmentZoomPolicy>> REGULAR = new LinkedHashMap<>();
    private static final Map<String, EnvironmentZoomPersistence> RETAINED_WRITES = new LinkedHashMap<>();
    private static final Map<BrowserContextHandle, String> PROFILE_KEYS = new WeakHashMap<>();
    private static final Map<WebContents, Boolean> RETIRED = new WeakHashMap<>();
    private static final Map<Activity, Boolean> ACTIVITIES = new WeakHashMap<>();
    private static final Handler HANDLER = new Handler(Looper.getMainLooper());
    private static boolean listening;
    private static boolean refreshScheduled;
    private static boolean refreshing;
    private static final Map<BrowserContextHandle, EnvironmentZoomPersistence> WRITES = new WeakHashMap<>();
    private static final ExecutorService WRITER = Executors.newSingleThreadExecutor(task -> {
        Thread thread = new Thread(task, "TitaniumZoomWriter");
        thread.setDaemon(true);
        return thread;
    });
    private static final class Binding {
        final BrowserContextHandle context;
        final EnvironmentZoomPolicy policy;
        EnvironmentZoomPolicy.Environment lastEnvironment;
        float lastFont = 1.0f;
        Binding(BrowserContextHandle context, EnvironmentZoomPolicy policy) {
            this.context = context;
            this.policy = policy;
        }
    }
    private EnvironmentZoom() {}

    public static void registerLegacyDefaultPresence(BrowserContextHandle context, boolean present) {
        LEGACY_DEFAULTS.put(context, present);
    }
    public static boolean isPrivateContext(BrowserContextHandle context) {
        ThreadUtils.assertOnUiThread();
        return context.getNativeBrowserContextPointer() == 0 || HostZoomMapImpl.isEnvironmentPrivate(context);
    }
    public static void setEnvironmentListener(WebContents contents, Runnable listener) {
        ENVIRONMENT_LISTENERS.put(contents,listener);
    }
    public static boolean isMobileDisplay(WebContents contents) {
        Binding binding = binding(contents);
        return binding != null && binding.lastEnvironment == EnvironmentZoomPolicy.Environment.MOBILE;
    }
    public static EnvironmentZoomPolicy store(BrowserContextHandle context) {
        ThreadUtils.assertOnUiThread();
        if (context.getNativeBrowserContextPointer() == 0) throw new IllegalStateException("Zoom profile is unavailable");
        EnvironmentZoomPolicy cached = STORES.get(context);
        if (cached != null) return cached;
        // Native profile path scopes the file, including future multiple regular profiles.
        String key = HostZoomMapImpl.getEnvironmentProfileKey(context);
        if (key.isEmpty()) throw new IllegalStateException("Zoom profile is unavailable");
        SharedPreferences prefs;
        Map<String, String> initial = new LinkedHashMap<>();
        try (StrictModeContext ignored = StrictModeContext.allowDiskReads()) {
            prefs = ContextUtils.getApplicationContext().getSharedPreferences(
                    "titanium_environment_zoom_" + key, Context.MODE_PRIVATE);
            for (Map.Entry<String, ?> e : prefs.getAll().entrySet()) {
                if (e.getValue() instanceof String) initial.put(e.getKey(), (String) e.getValue());
            }
        }
        boolean privateProfile = HostZoomMapImpl.isEnvironmentPrivate(context);
        EnvironmentZoomPolicy.Storage storage;
        if (privateProfile) {
            WeakReference<EnvironmentZoomPolicy> regular = REGULAR.get(key);
            EnvironmentZoomPolicy active = regular == null ? null : regular.get();
            if (active != null) {
                initial.clear();
                initial.putAll(active.snapshot()); // Include regular changes still awaiting worker persistence.
            } else if (RETAINED_WRITES.containsKey(key)) {
                initial.clear();
                initial.putAll(RETAINED_WRITES.get(key).read());
            }
            storage = new EnvironmentZoomPolicy.Storage() {
                private Map<String, String> memory = initial;
                @Override public Map<String, String> read() { return new LinkedHashMap<>(memory); }
                @Override public void write(Map<String, String> values) { memory = new LinkedHashMap<>(values); }
            };
        } else {
            EnvironmentZoomPersistence persistence = RETAINED_WRITES.remove(key);
            if (persistence == null) persistence = new EnvironmentZoomPersistence(initial, values -> {
                SharedPreferences.Editor editor = prefs.edit().clear();
                for (Map.Entry<String, String> e : values.entrySet()) editor.putString(e.getKey(), e.getValue());
                return editor.commit(); // Worker only; preserve marker and both maps in one transaction.
            }, new EnvironmentZoomPersistence.Dispatch() {
                @Override public void later(Runnable task, int delay) { HANDLER.postDelayed(task, delay); }
                @Override public void cancel(Runnable task) { HANDLER.removeCallbacks(task); }
                @Override public void background(Runnable task) { WRITER.execute(task); }
                @Override public void main(Runnable task) { HANDLER.post(task); }
                @Override public void failure() {
                    Log.e("TitaniumZoom", "Zoom settings could not be saved; pending snapshot retained for retry");
                    for (WebContents contents : new ArrayList<>(CONTENTS.keySet())) {
                        Activity owner = activity(contents);
                        if (owner != null && !owner.isFinishing() && !owner.isDestroyed()) {
                            android.widget.Toast.makeText(owner,
                                    "Zoom settings could not be saved. Please retry after checking storage.",
                                    android.widget.Toast.LENGTH_LONG).show();
                            break;
                        }
                    }
                }
            });
            WRITES.put(context, persistence);
            storage = persistence;
        }
        EnvironmentZoomPolicy result = new EnvironmentZoomPolicy(storage,
                HostZoomMap.getDefaultZoomLevel(context), HostZoomMap.getAllHostZoomLevels(context),
                LEGACY_DEFAULTS.getOrDefault(context, false));
        STORES.put(context, result);
        PROFILE_KEYS.put(context, key);
        if (!privateProfile) REGULAR.put(key, new WeakReference<>(result));
        return result;
    }

    public static void attach(WebContents contents, BrowserContextHandle context) {
        ThreadUtils.assertOnUiThread();
        if (contents.isDestroyed() || RETIRED.containsKey(contents)) return;
        if (context.getNativeBrowserContextPointer() == 0) {
            RETIRED.put(contents, true);
            return;
        }
        Binding binding = CONTENTS.get(contents);
        if (binding == null || binding.context != context) {
            binding = new Binding(context, store(context));
            CONTENTS.put(contents, binding);
        }
        updateEnvironment(contents, binding);
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
        ThreadUtils.assertOnUiThread();
        EnvironmentZoomPersistence persistence = WRITES.remove(context);
        if (persistence != null) persistence.flush();
        String key = PROFILE_KEYS.remove(context);
        if (key != null && persistence != null && persistence.hasPendingWrite()) {
            RETAINED_WRITES.put(key, persistence); // Keep failed/pending regular data through profile teardown.
        }
        EnvironmentZoomPolicy removed = STORES.remove(context);
        WeakReference<EnvironmentZoomPolicy> regular = REGULAR.get(key);
        if (regular != null && regular.get() == removed) REGULAR.remove(key);
        LEGACY_DEFAULTS.remove(context);
        for (WebContents contents : new ArrayList<>(CONTENTS.keySet())) {
            if (CONTENTS.get(contents).context == context) {
                RETIRED.put(contents, true);
                CONTENTS.remove(contents);
            }
        }
    }
    private static Activity activity(WebContents contents) {
        if (contents.isDestroyed()) return null;
        WindowAndroid window = contents.getTopLevelNativeWindow();
        return window == null ? null : window.getActivity().get();
    }
    public static EnvironmentZoomPolicy.Environment environment(Context context) {
        return environment(context, null);
    }
    private static EnvironmentZoomPolicy.Environment environment(Context context, EnvironmentZoomPolicy policy) {
        int displayId = displayId(context);
        // Override is display-scoped. It changes classification, never the zoom values themselves.
        String mode = ContextUtils.getAppSharedPreferences().getString(
                "titanium.zoom.display." + displayId, "auto");
        if (policy != null) mode = policy.displayMode(displayId, mode);
        boolean dex = "dex".equals(mode) || ("auto".equals(mode)
                && displayId != Display.DEFAULT_DISPLAY);
        return dex ? EnvironmentZoomPolicy.Environment.DEX : EnvironmentZoomPolicy.Environment.MOBILE;
    }
    public static int displayId(Context context) {
        return DisplayAndroid.getNonMultiDisplay(context).getDisplayId();
    }
    public static String displayMode(Context context, EnvironmentZoomPolicy policy) {
        return policy.displayMode(displayId(context),displayMode(context));
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
    private static Binding binding(WebContents contents) {
        ThreadUtils.assertOnUiThread();
        if (contents.isDestroyed()) return null;
        Binding binding = CONTENTS.get(contents);
        if (binding != null) updateEnvironment(contents, binding);
        return binding;
    }
    private static void updateEnvironment(WebContents contents, Binding binding) {
        Activity owner = activity(contents);
        if (owner == null || owner.isDestroyed()) return;
        binding.lastEnvironment = environment(owner, binding.policy);
        binding.lastFont = HostZoomMap.shouldAdjustForOSLevel()
                ? owner.getResources().getConfiguration().fontScale : 1.0f;
    }
    public static double defaultFor(WebContents contents) {
        Binding binding = binding(contents);
        return binding == null || binding.lastEnvironment == null ? Double.NaN
                : binding.policy.defaultFactor(binding.lastEnvironment);
    }
    public static double resolve(WebContents contents, String host) {
        Binding binding = binding(contents);
        return binding == null || binding.lastEnvironment == null ? Double.NaN
                : binding.policy.resolve(binding.lastEnvironment, host);
    }
    // Read only. No initialization, persistence, refresh or profile JNI from native zoom lookup.
    public static double rendered(WebContents contents, String host) {
        Binding binding = binding(contents);
        if (binding == null || binding.lastEnvironment == null) return Double.NaN;
        return binding.policy.resolve(binding.lastEnvironment, host)
                + Math.log(binding.lastFont) / Math.log(1.2);
    }
    public static boolean save(WebContents contents, String host, double factor) {
        Binding binding = binding(contents);
        if (binding == null) return RETIRED.containsKey(contents);
        // A temporarily detached managed tab must not fall through to legacy global persistence.
        if (binding.lastEnvironment == null || !Double.isFinite(factor)) return true;
        double absolute = EnvironmentZoomPolicy.factor(Math.max(50, Math.min(300,
                EnvironmentZoomPolicy.percent(factor))));
        binding.policy.setSite(binding.lastEnvironment, host, absolute);
        scheduleRefresh(); // Never synchronously re-enter native zoom update from a native setter.
        return true;
    }
    public static boolean reset(WebContents contents) {
        Binding binding = binding(contents);
        if (binding == null) return RETIRED.containsKey(contents);
        if (binding.lastEnvironment == null) return true;
        binding.policy.resetSite(binding.lastEnvironment, HostZoomMapImpl.getEnvironmentHost(contents));
        scheduleRefresh();
        return true;
    }
    private static void scheduleRefresh() {
        if (refreshScheduled) return;
        refreshScheduled = true;
        HANDLER.post(() -> {
            refreshScheduled = false;
            refreshAll();
        });
    }
    public static boolean hasPendingWrites() {
        ThreadUtils.assertOnUiThread();
        for (EnvironmentZoomPersistence persistence : WRITES.values()) {
            if (persistence.hasPendingWrite()) return true;
        }
        for (EnvironmentZoomPersistence persistence : RETAINED_WRITES.values()) {
            if (persistence.hasPendingWrite()) return true;
        }
        return false;
    }
    public static void flushPendingWrites() {
        ThreadUtils.assertOnUiThread();
        for (EnvironmentZoomPersistence persistence : new ArrayList<>(WRITES.values())) persistence.flush();
        for (EnvironmentZoomPersistence persistence : new ArrayList<>(RETAINED_WRITES.values())) persistence.flush();
    }
    public static void refreshAll() {
        ThreadUtils.assertOnUiThread();
        if (refreshing) { scheduleRefresh(); return; }
        refreshing = true;
        try {
            for (WebContents contents : new ArrayList<>(CONTENTS.keySet())) {
                if (contents.isDestroyed()) CONTENTS.remove(contents);
                else refresh(contents);
            }
        } finally { refreshing = false; }
    }
    private static void refresh(WebContents contents) {
        if (!contents.isDestroyed() && activity(contents) != null) {
            HostZoomMapImpl.refreshEnvironmentZoom(contents);
            Runnable listener = ENVIRONMENT_LISTENERS.get(contents);
            if (listener != null) listener.run(); // Outside native zoom lookup; no JNI->Java->JS recursion.
        }
    }
}
