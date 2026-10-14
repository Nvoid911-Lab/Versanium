// Copyright 2026 Titanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.content_public.browser;

import java.util.LinkedHashMap;
import java.util.Map;

/** Android-independent persistence and precedence policy. Values are absolute zoom exponents. */
public final class EnvironmentZoomPolicy {
    public enum Environment { MOBILE, DEX }
    public interface Storage {
        Map<String, String> read();
        void write(Map<String, String> values);
    }
    private final Storage storage;
    private final Map<String, String> values;

    public EnvironmentZoomPolicy(Storage storage, double legacyDefault,
            Map<String, Double> legacySites) {
        this(storage, legacyDefault, legacySites, false);
    }
    public EnvironmentZoomPolicy(Storage storage, double legacyDefault,
            Map<String, Double> legacySites, boolean hasLegacyDefaultPreference) {
        this.storage = storage;
        values = new LinkedHashMap<>(storage.read());
        if (!"1".equals(values.get("version"))) {
            // A nonempty old profile keeps its default in BOTH environments. Never modify it.
            boolean existing = hasLegacyDefaultPreference || legacyDefault != 0.0 || !legacySites.isEmpty();
            values.put("default.MOBILE", Double.toString(legacyDefault));
            values.put("default.DEX", Double.toString(existing ? legacyDefault : factor(67)));
            for (Environment env : Environment.values()) {
                for (Map.Entry<String, Double> site : legacySites.entrySet()) {
                    values.put(siteKey(env, site.getKey()), Double.toString(site.getValue()));
                }
            }
            values.put("version", "1");
            storage.write(new LinkedHashMap<>(values));
        }
    }
    public static double factor(int percent) {
        if (percent < 50 || percent > 300) throw new IllegalArgumentException("Zoom out of range");
        return Math.log(percent / 100.0) / Math.log(1.2);
    }
    public static int percent(double factor) {
        return (int) Math.round(100.0 * Math.pow(1.2, factor));
    }
    private static String siteKey(Environment env, String host) {
        return "site." + env.name() + "." + host;
    }
    public double defaultFactor(Environment env) {
        return Double.parseDouble(values.get("default." + env.name()));
    }
    public double resolve(Environment env, String host) {
        String saved = values.get(siteKey(env, host));
        return saved == null ? defaultFactor(env) : Double.parseDouble(saved);
    }
    public boolean hasSite(Environment env, String host) {
        return values.containsKey(siteKey(env, host));
    }
    public void setDefault(Environment env, double factor) {
        requireFinite(factor);
        values.put("default." + env.name(), Double.toString(factor));
        persist(); // Deliberately do not prune site entries equal to the default.
    }
    public void setSite(Environment env, String host, double factor) {
        requireFinite(factor);
        if (host.isEmpty()) return;
        values.put(siteKey(env, host), Double.toString(factor));
        persist(); // Explicitly saving the default is still an explicit site choice.
    }
    public void resetSite(Environment env, String host) {
        values.remove(siteKey(env, host));
        persist();
    }
    public Map<String, Double> sites(Environment env) {
        Map<String, Double> sites = new LinkedHashMap<>();
        String prefix = "site." + env.name() + ".";
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (entry.getKey().startsWith(prefix)) {
                sites.put(entry.getKey().substring(prefix.length()), Double.valueOf(entry.getValue()));
            }
        }
        return sites;
    }
    public Map<String, String> snapshot() { return new LinkedHashMap<>(values); }
    private void persist() { storage.write(snapshot()); }
    private static void requireFinite(double value) {
        if (!Double.isFinite(value)) throw new IllegalArgumentException("Non-finite zoom");
    }
}
