// Copyright 2026 Versanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.components.browser_ui.accessibility;

import android.app.AlertDialog;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.preference.Preference;
import androidx.preference.PreferenceFragmentCompat;
import androidx.preference.SeekBarPreference;
import androidx.preference.ListPreference;
import org.chromium.content_public.browser.BrowserContextHandle;
import org.chromium.content_public.browser.EnvironmentZoom;
import org.chromium.content_public.browser.EnvironmentZoomPolicy;
import org.chromium.content_public.browser.EnvironmentZoomBackup;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** SAF only: no storage permission, display IDs, browsing/session data or private state exported. */
final class EnvironmentZoomTransfer {
    private static final ExecutorService IO = Executors.newSingleThreadExecutor();
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    static void add(PreferenceFragmentCompat fragment, BrowserContextHandle browser,
            EnvironmentZoomPolicy policy) {
        Context app = fragment.requireContext().getApplicationContext();
        Preference export = new Preference(fragment.requireContext());
        export.setTitle(R.string.titanium_zoom_export);
        Preference restore = new Preference(fragment.requireContext());
        restore.setTitle(R.string.titanium_zoom_import);
        export.setPersistent(false);restore.setPersistent(false);
        fragment.getPreferenceScreen().addPreference(export);
        fragment.getPreferenceScreen().addPreference(restore);
        boolean regular = !EnvironmentZoom.isPrivateContext(browser);
        export.setEnabled(regular);restore.setEnabled(regular);
        ActivityResultLauncher<String> create = fragment.registerForActivityResult(
                new ActivityResultContracts.CreateDocument("application/json"), uri -> {
                    if (uri == null || !fragment.isAdded() || EnvironmentZoom.isPrivateContext(browser)) return;
                    final String json;
                    try { json = EnvironmentZoomBackup.encode(policy,
                            EnvironmentZoom.displayMode(fragment.requireContext(),policy)); }
                    catch (IOException | IllegalArgumentException error) { message(app,false);return; }
                    IO.execute(() -> {
                        boolean success = false;
                        try (OutputStream out = app.getContentResolver().openOutputStream(uri,"wt")) {
                            if (out == null) throw new IOException("No output stream");
                            out.write(json.getBytes(StandardCharsets.UTF_8));out.flush();
                            success = true;
                        } catch (IOException | IllegalArgumentException | SecurityException error) { success = false; }
                        final boolean result = success;
                        MAIN.post(() -> message(app,result));
                    });
                });
        ActivityResultLauncher<String[]> open = fragment.registerForActivityResult(
                new ActivityResultContracts.OpenDocument(), uri -> {
                    if (uri == null || !fragment.isAdded() || EnvironmentZoom.isPrivateContext(browser)) return;
                    IO.execute(() -> {
                        EnvironmentZoomBackup backup;
                        try (InputStream in = app.getContentResolver().openInputStream(uri)) {
                            if (in == null) throw new IOException("No input stream");
                            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                            byte[] chunk = new byte[8192];int count;
                            while ((count=in.read(chunk)) != -1) {
                                if (count == 0) throw new IOException("Invalid stream progress");
                                if (bytes.size()+count > EnvironmentZoomBackup.MAX_BYTES) throw new IOException("Too large");
                                bytes.write(chunk,0,count);
                            }
                            String json = StandardCharsets.UTF_8.newDecoder()
                                    .onMalformedInput(CodingErrorAction.REPORT)
                                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                                    .decode(ByteBuffer.wrap(bytes.toByteArray())).toString();
                            backup = EnvironmentZoomBackup.decode(json);
                        } catch (IOException | IllegalStateException | IllegalArgumentException | SecurityException error) {
                            MAIN.post(() -> message(app,false));return;
                        }
                        MAIN.post(() -> confirm(fragment,browser,policy,backup,app));
                    });
                });
        export.setOnPreferenceClickListener(p -> { create.launch("Versanium-zoom.json");return true; });
        restore.setOnPreferenceClickListener(p -> {
            if (!policy.isReplacing()) open.launch(new String[]{"application/json","text/plain"});
            return true;
        });
    }
    private static void confirm(PreferenceFragmentCompat fragment, BrowserContextHandle browser,
            EnvironmentZoomPolicy policy, EnvironmentZoomBackup backup, Context app) {
        if (!fragment.isAdded() || EnvironmentZoom.isPrivateContext(browser)) return;
        int sites = (int)backup.values.keySet().stream().filter(k -> k.startsWith("site.")).count();
        String summary = fragment.getString(R.string.titanium_zoom_import_confirm,
                EnvironmentZoomPolicy.percent(Double.parseDouble(backup.values.get("default.MOBILE"))),
                EnvironmentZoomPolicy.percent(Double.parseDouble(backup.values.get("default.DEX"))),
                sites,backup.displayMode);
        new AlertDialog.Builder(fragment.requireContext()).setTitle(R.string.titanium_zoom_import)
                .setMessage(summary).setNegativeButton(android.R.string.cancel,null)
                .setPositiveButton(android.R.string.ok,(dialog,button) -> {
                    if (!fragment.isAdded() || EnvironmentZoom.isPrivateContext(browser)) return;
                    policy.importSnapshot(backup.values,backup.displayMode,
                            EnvironmentZoom.displayId(fragment.requireContext()), success -> {
                        if (success) {
                            EnvironmentZoom.refreshAll();
                            if (fragment.isAdded()) {
                                for (EnvironmentZoomPolicy.Environment env : EnvironmentZoomPolicy.Environment.values()) {
                                    SeekBarPreference pref = fragment.findPreference("titanium_zoom_" +
                                            (env==EnvironmentZoomPolicy.Environment.MOBILE?"mobile":"dex"));
                                    if (pref != null) pref.setValue(EnvironmentZoomPolicy.percent(policy.defaultFactor(env)));
                                }
                                ListPreference mode = fragment.findPreference("titanium_zoom_display");
                                if (mode != null) mode.setValue(EnvironmentZoom.displayMode(fragment.requireContext(),policy));
                            }
                        }
                        message(app,success);
                    });
                }).show();
    }
    private static void message(Context context, boolean success) {
        Toast.makeText(context, success ? R.string.titanium_zoom_transfer_ok
                : R.string.titanium_zoom_transfer_failed,Toast.LENGTH_LONG).show();
    }
}
