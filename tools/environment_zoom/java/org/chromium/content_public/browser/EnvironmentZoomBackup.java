// Copyright 2026 Versanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.content_public.browser;

import android.util.JsonReader;
import android.util.JsonToken;
import android.util.JsonWriter;
import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.LinkedHashMap;
import java.util.HashSet;
import java.util.Map;
import java.nio.charset.StandardCharsets;

/** Strict portable backup; native absolute exponents are never converted to rounded percent.
 * The archive domain is every finite double, matching Policy storage/migration, NOT the
 * 50..300 percent slider domain. No arithmetic is needed to validate or round-trip a value.
 * Renderer support for extreme legacy values is a separate concern; do not silently clamp.
 */
public final class EnvironmentZoomBackup {
    public static final int MAX_BYTES = 1024 * 1024;
    public static final int MAX_SITES = 10000;
    public final Map<String, String> values;
    public final String displayMode;
    private EnvironmentZoomBackup(Map<String, String> values, String mode) {
        this.values = java.util.Collections.unmodifiableMap(values);
        displayMode = mode;
    }
    public static String encode(EnvironmentZoomPolicy policy, String mode) throws IOException {
        requireMode(mode);
        StringWriter buffer = new StringWriter();
        JsonWriter out = new JsonWriter(buffer);
        out.beginObject().name("format").value("versanium-environment-zoom")
                .name("version").value(1).name("unit").value("log-base-1.2-exponent")
                .name("displayModeForCurrentScreen").value(mode);
        for (EnvironmentZoomPolicy.Environment env : EnvironmentZoomPolicy.Environment.values()) {
            out.name(env.name()).beginObject().name("default").value(policy.defaultFactor(env))
                    .name("sites").beginObject();
            for (Map.Entry<String, Double> entry : policy.sites(env).entrySet()) {
                out.name(entry.getKey()).value(entry.getValue());
            }
            out.endObject().endObject();
        }
        out.endObject();out.close();
        String result = buffer.toString();
        decode(result); // Export only files that our bounded importer accepts.
        return result;
    }
    public static EnvironmentZoomBackup decode(String json) throws IOException {
        if (json.getBytes(StandardCharsets.UTF_8).length > MAX_BYTES) throw new IOException("Too large");
        Map<String, String> result = new LinkedHashMap<>();
        HashSet<String> fields = new HashSet<>();
        String mode = null;
        JsonReader reader = new JsonReader(new StringReader(json));
        reader.setLenient(false);
        reader.beginObject();
        int total = 0;
        while (reader.hasNext()) {
            String key = reader.nextName();
            if (!fields.add(key)) throw new IOException("Duplicate field");
            switch (key) {
                case "format":
                    if (!"versanium-environment-zoom".equals(reader.nextString())) throw new IOException("Format");
                    break;
                case "version":
                    if (reader.peek() != JsonToken.NUMBER || !"1".equals(reader.nextString())) throw new IOException("Version");
                    break;
                case "unit":
                    if (!"log-base-1.2-exponent".equals(reader.nextString())) throw new IOException("Unit");
                    break;
                case "displayModeForCurrentScreen":mode = reader.nextString();requireMode(mode);break;
                case "MOBILE":case "DEX":
                    HashSet<String> nested = new HashSet<>();
                    reader.beginObject();
                    while (reader.hasNext()) {
                        String part = reader.nextName();
                        if (!nested.add(part)) throw new IOException("Duplicate environment field");
                        if ("default".equals(part)) result.put("default." + key, number(reader));
                        else if ("sites".equals(part)) {
                            reader.beginObject();
                            HashSet<String> hosts = new HashSet<>();
                            while (reader.hasNext()) {
                                String host = reader.nextName();
                                if (host.isEmpty() || host.length() > 2048 || !hosts.add(host)
                                        || host.codePoints().anyMatch(c -> c < 32 || c == 127 || (c >= 0xd800 && c <= 0xdfff))
                                        || ++total > MAX_SITES) throw new IOException("Invalid host/count");
                                result.put("site." + key + "." + host, number(reader));
                            }
                            reader.endObject();
                        } else throw new IOException("Unknown environment field");
                    }
                    reader.endObject();
                    if (nested.size() != 2) throw new IOException("Missing environment field");
                    break;
                default:throw new IOException("Unknown field");
            }
        }
        reader.endObject();
        if (reader.peek() != JsonToken.END_DOCUMENT || fields.size() != 6) throw new IOException("Incomplete/trailing document");
        reader.close();
        result.put("version", "1"); // Preserve the existing storage migration marker.
        return new EnvironmentZoomBackup(result, mode);
    }
    private static String number(JsonReader reader) throws IOException {
        if (reader.peek() != JsonToken.NUMBER) throw new IOException("Expected numeric exponent");
        double value = reader.nextDouble();
        if (!Double.isFinite(value)) throw new IOException("Non-finite zoom exponent");
        return Double.toString(value);
    }
    /** An archive can preserve every finite old value, but never feed pow overflow/underflow
     * to a renderer through an imported file. Check Android's documented font envelope too.
     * This is numerical safety, not a promise that every ratio is supported by Blink UI.
     * Reject the whole restore explicitly; keep the archive and existing settings unchanged.
     */
    public void validateForRestore() throws IOException {
        for (Map.Entry<String,String> entry : values.entrySet()) {
            if (!entry.getKey().startsWith("default.") && !entry.getKey().startsWith("site.")) continue;
            double ratio = Math.pow(1.2, Double.parseDouble(entry.getValue()));
            if (!Double.isFinite(ratio * 2.0) || ratio * 0.85 < Double.MIN_NORMAL) {
                throw new IOException("Legacy exponent cannot be safely applied; archive preserved");
            }
        }
    }
    /** Exact exponent, including values the slider cannot represent; no percent overflow. */
    public static String describeDefault(String exponent) {
        return "1.2^" + exponent;
    }
    private static void requireMode(String mode) throws IOException {
        if (!"auto".equals(mode) && !"mobile".equals(mode) && !"dex".equals(mode)) throw new IOException("Display mode");
    }
}
