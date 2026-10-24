// Copyright 2026 Titanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.components.browser_ui.accessibility;

import android.app.AlertDialog;
import android.content.Context;

import androidx.preference.ListPreference;
import androidx.preference.Preference;
import androidx.preference.PreferenceFragmentCompat;
import androidx.preference.SeekBarPreference;

import org.chromium.content_public.browser.BrowserContextHandle;
import org.chromium.components.prefs.PrefService;
import org.chromium.components.user_prefs.UserPrefs;
import org.chromium.content_public.browser.EnvironmentZoom;
import org.chromium.content_public.browser.EnvironmentZoomPolicy;
import org.chromium.content_public.browser.EnvironmentZoomBackup;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/** Two defaults and two explicit site-reset lists replace the old global zoom controls. */
final class EnvironmentZoomSettings {
    private EnvironmentZoomSettings() {}
    static void add(PreferenceFragmentCompat fragment, BrowserContextHandle context) {
        if (context.getNativeBrowserContextPointer() == 0) return;
        PrefService prefs = UserPrefs.get(context);
        EnvironmentZoom.registerLegacyDefaultPresence(context, prefs == null
                || !prefs.isDefaultValuePreference("partition.default_zoom_level.android"));
        EnvironmentZoomPolicy policy = EnvironmentZoom.store(context);
        Context activity = fragment.requireContext();
        for (EnvironmentZoomPolicy.Environment env : EnvironmentZoomPolicy.Environment.values()) {
            String name = env == EnvironmentZoomPolicy.Environment.MOBILE ? "mobile" : "dex";
            SeekBarPreference pref = fragment.findPreference("titanium_zoom_" + name);
            if (pref == null) throw new IllegalStateException("Missing zoom preference");
            pref.setMin(50);
            pref.setMax(300);
            pref.setSeekBarIncrement(1);
            pref.setShowSeekBarValue(true);
            // Preference commits the default at the end of tracking, not for every thumb movement.
            pref.setUpdatesContinuously(false);
            showDefault(pref,policy.defaultFactor(env),activity);
            pref.setOnPreferenceChangeListener((p, value) -> {
                if (policy.isReplacing()) return false;
                policy.setDefault(env, EnvironmentZoomPolicy.factor((Integer) value));
                showDefault(pref,policy.defaultFactor(env),activity);
                EnvironmentZoom.refreshAll();
                return true;
            });
            Preference sites = fragment.findPreference("titanium_zoom_" + name + "_sites");
            if (sites == null) throw new IllegalStateException("Missing site zoom preference");
            sites.setSummary(activity.getString(R.string.titanium_zoom_sites_summary));
            sites.setOnPreferenceClickListener(p -> {
                showSites(activity, policy, env);
                return true;
            });
        }
        ListPreference mode = fragment.findPreference("titanium_zoom_display");
        if (mode == null) throw new IllegalStateException("Missing display preference");
        mode.setEntries(new CharSequence[] {activity.getString(R.string.titanium_zoom_auto),
                activity.getString(R.string.titanium_zoom_mobile), activity.getString(R.string.titanium_zoom_dex)});
        mode.setEntryValues(new CharSequence[] {"auto", "mobile", "dex"});
        mode.setValue(EnvironmentZoom.displayMode(activity, policy));
        mode.setSummaryProvider(ListPreference.SimpleSummaryProvider.getInstance());
        mode.setOnPreferenceChangeListener((p, value) -> {
            if (policy.isReplacing()) return false;
            policy.setDisplayMode(EnvironmentZoom.displayId(activity), (String) value);
            EnvironmentZoom.refreshAll();
            return true;
        });
        EnvironmentZoomTransfer.add(fragment,context,policy);
        final boolean allowTransfer = !EnvironmentZoom.isPrivateContext(context);
        java.lang.ref.WeakReference<PreferenceFragmentCompat> weak = new java.lang.ref.WeakReference<>(fragment);
        policy.observeTransfer(fragment, () -> {
            PreferenceFragmentCompat active = weak.get();
            if (active == null || !active.isAdded() || active.getPreferenceScreen() == null) return;
            android.app.Activity owner = active.getActivity();
            if (owner == null || owner.isFinishing() || owner.isDestroyed()) return;
            for (String key : new String[]{"titanium_zoom_mobile","titanium_zoom_dex",
                    "titanium_zoom_mobile_sites","titanium_zoom_dex_sites","titanium_zoom_display",
                    "titanium_zoom_export","titanium_zoom_import"}) {
                Preference control = active.findPreference(key);
                if (control != null) control.setEnabled(!policy.isReplacing()
                        && (allowTransfer || (!key.endsWith("_export") && !key.endsWith("_import"))));
            }
            for (EnvironmentZoomPolicy.Environment env : EnvironmentZoomPolicy.Environment.values()) {
                SeekBarPreference slider = active.findPreference("titanium_zoom_" +
                        (env == EnvironmentZoomPolicy.Environment.MOBILE ? "mobile" : "dex"));
                if (slider != null) showDefault(slider,policy.defaultFactor(env),active.requireContext());
            }
            ListPreference display = active.findPreference("titanium_zoom_display");
            if (display != null) display.setValue(EnvironmentZoom.displayMode(active.requireContext(),policy));
        });
    }
    private static void showDefault(SeekBarPreference slider, double factor, Context context) {
        double percent = 100.0 * Math.pow(1.2,factor);
        boolean outside = percent < 50.0 - 1e-9 || percent > 300.0 + 1e-9;
        // Only the thumb is bounded. This never calls policy.setDefault or changes storage.
        slider.setValue(percent <= 50 ? 50 : percent >= 300 ? 300 : (int)Math.round(percent));
        slider.setSummary(outside ? context.getString(R.string.titanium_zoom_legacy_default_summary,
                EnvironmentZoomBackup.describeDefault(Double.toString(factor)))
                : context.getString(R.string.titanium_zoom_default_summary));
    }
    private static void showSites(Context activity, EnvironmentZoomPolicy policy,
            EnvironmentZoomPolicy.Environment env) {
        Map<String, Double> saved = policy.sites(env);
        List<String> hosts = new ArrayList<>(saved.keySet());
        Collections.sort(hosts);
        if (hosts.isEmpty()) {
            new AlertDialog.Builder(activity).setMessage(R.string.titanium_zoom_no_sites)
                    .setPositiveButton(android.R.string.ok, null).show();
            return;
        }
        String[] labels = new String[hosts.size()];
        for (int i = 0; i < hosts.size(); i++) {
            labels[i] = hosts.get(i) + " — " + EnvironmentZoomBackup.describeDefault(Double.toString(saved.get(hosts.get(i))));
        }
        new AlertDialog.Builder(activity).setTitle(R.string.titanium_zoom_sites_summary)
                .setItems(labels, (dialog, index) -> {
                    new AlertDialog.Builder(activity).setTitle(labels[index])
                            .setMessage(R.string.titanium_zoom_reset_confirm)
                            .setNegativeButton(android.R.string.cancel, null)
                            .setPositiveButton(R.string.reset, (confirmation, button) -> {
                                policy.resetSite(env, hosts.get(index));
                                EnvironmentZoom.refreshAll();
                            }).show();
                }).setNegativeButton(android.R.string.cancel, null).show();
    }
}
