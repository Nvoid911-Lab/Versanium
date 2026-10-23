// Copyright 2026 Titanium contributors. SPDX-License-Identifier: BSD-3-Clause
package org.chromium.content_public.browser;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Collections;

/** UI-owned snapshots, coalesced serial background writes and bounded retries. */
public final class EnvironmentZoomPersistence implements EnvironmentZoomPolicy.Storage {
    public interface Writer { boolean write(Map<String, String> values); }
    public interface Dispatch {
        void later(Runnable task, int milliseconds);
        void cancel(Runnable task);
        void background(Runnable task);
        void main(Runnable task);
        void failure();
    }
    private final Writer writer;
    private final Dispatch dispatch;
    private final Runnable launchTask = this::launch;
    private Map<String, String> memory;
    private Map<String, String> pending;
    private boolean running;
    private int failures;
    public EnvironmentZoomPersistence(Map<String, String> initial, Writer writer, Dispatch dispatch) {
        memory = new LinkedHashMap<>(initial);
        this.writer = writer;
        this.dispatch = dispatch;
    }
    @Override public Map<String, String> read() { return new LinkedHashMap<>(memory); }
    @Override public void write(Map<String, String> values) {
        memory = Collections.unmodifiableMap(new LinkedHashMap<>(values));
        pending = memory; // One immutable snapshot, shared safely by the worker and UI reads.
        failures = 0;
        if (!running) schedule(200);
    }
    @Override public void replace(Map<String, String> values, java.util.function.Consumer<Boolean> done) {
        if (hasPendingWrite()) { done.accept(false);return; } // Never race a queued ordinary save.
        Map<String, String> batch = Collections.unmodifiableMap(new LinkedHashMap<>(values));
        running = true;
        dispatch.background(() -> {
            boolean success;
            try { success = writer.write(batch); }
            catch (RuntimeException error) { success = false; }
            final boolean result = success;
            dispatch.main(() -> {
                running = false;
                if (result) memory = batch;
                done.accept(result); // Import UI owns failure feedback; no uncommitted retry snapshot.
            });
        });
    }
    public void flush() {
        dispatch.cancel(launchTask);
        failures = 0;
        launch(); // Submit, never wait or write on the UI thread.
    }
    private void schedule(int delay) {
        dispatch.cancel(launchTask);
        dispatch.later(launchTask, delay);
    }
    private void launch() {
        if (running || pending == null) return;
        Map<String, String> batch = pending;
        pending = null;
        running = true;
        dispatch.background(() -> {
            boolean success;
            try { success = writer.write(batch); }
            catch (RuntimeException error) { success = false; }
            final boolean result = success;
            dispatch.main(() -> complete(batch, result));
        });
    }
    private void complete(Map<String, String> batch, boolean success) {
        running = false;
        if (success) {
            failures = 0;
            if (pending != null) schedule(200);
        } else {
            if (pending == null) pending = batch; // Never replace a newer UI snapshot with old data.
            failures++;
            if (failures == 1) dispatch.failure();
            if (failures < 3) schedule(1000 * failures);
        }
    }
    public boolean hasPendingWrite() { return running || pending != null; }
    public boolean hasFailure() { return failures != 0; }
}
