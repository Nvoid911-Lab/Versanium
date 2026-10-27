/* Copyright (c) 2026 The Brave Authors. All rights reserved.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at https://mozilla.org/MPL/2.0/. */
// SPDX-License-Identifier: MPL-2.0
// Adapted from Brave #36838.
// Source revision: 4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2

package org.chromium.chrome.browser.media;

import android.app.Activity;
import android.net.Uri;
import android.os.SystemClock;

import org.chromium.build.annotations.NullMarked;
import org.chromium.build.annotations.Nullable;
import org.chromium.chrome.browser.ChromeTabbedActivity;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.content_public.browser.WebContents;
import org.chromium.ui.base.WindowAndroid;

/** Phase 1 policy for the existing fullscreen-video entry point only. */
@NullMarked
public final class VersaniumYouTubePictureInPicturePolicy {
    // Single integration gate. Intermediate commits must remain disabled.
    static final boolean ENABLED = false;
    static final long ENTRY_TIMEOUT_MS = 2000;
    static final long EXIT_CLASSIFICATION_MS = 1000;
    static final long DOM_EXIT_TIMEOUT_MS = 500;

    enum State { INACTIVE, ENTERING, ACTIVE, EXITING }

    /** An identity token, never a tab ID lookup or a current-tab media fallback. */
    static final class Owner {
        final Activity activity;
        final WindowAndroid window;
        final Tab tab;
        final int tabId;
        final WebContents webContents;
        final long documentEpoch;
        final String videoId;

        Owner(Activity activity, WindowAndroid window, Tab tab, WebContents wc, long epoch) {
            this.activity = activity;
            this.window = window;
            this.tab = tab;
            tabId = tab.getId();
            webContents = wc;
            documentEpoch = epoch;
            videoId = videoId(tab.getUrl().getSpec());
        }

        boolean live(Activity host, long epoch) {
            return activity == host
                    && !host.isFinishing() && !host.isDestroyed()
                    && !host.isChangingConfigurations()
                    && documentEpoch == epoch && !tab.isDestroyed()
                    && tab.getId() == tabId && tab.getWebContents() == webContents
                    && !webContents.isDestroyed() && tab.getWindowAndroid() == window
                    && window.getActivity().get() == activity
                    && !videoId.isEmpty() && videoId.equals(videoId(tab.getUrl().getSpec()));
        }
    }

    static String videoId(String spec) {
        Uri uri = Uri.parse(spec);
        if (!"https".equals(uri.getScheme()) || !"m.youtube.com".equals(uri.getHost())
                || !"/watch".equals(uri.getPath()) || uri.getUserInfo() != null
                || (uri.getPort() != -1 && uri.getPort() != 443)) return "";
        String id = uri.getQueryParameter("v");
        return id == null ? "" : id;
    }

    static @Nullable Owner capture(Activity activity, @Nullable Tab tab, boolean upstream, long epoch) {
        if (!ENABLED || !(activity instanceof ChromeTabbedActivity) || !upstream
                || activity.isFinishing() || activity.isDestroyed()
                || activity.isChangingConfigurations() || tab == null || tab.isDestroyed()
                || videoId(tab.getUrl().getSpec()).isEmpty()) return null;
        WebContents wc = tab.getWebContents();
        WindowAndroid window = tab.getWindowAndroid();
        if (wc == null || wc.isDestroyed() || window == null
                || window.getActivity().get() != activity) return null;
        return new Owner(activity, window, tab, wc, epoch);
    }

    static boolean protectedState(State state, long enteredAt, boolean frameworkPip) {
        return (state == State.ENTERING
                        && SystemClock.elapsedRealtime() - enteredAt < ENTRY_TIMEOUT_MS)
                || (state == State.ACTIVE && frameworkPip);
    }

    static boolean transientReason(int reason) {
        return reason == FullscreenVideoPictureInPictureController.MetricsEndReason.START
                || reason == FullscreenVideoPictureInPictureController.MetricsEndReason.RESUME
                || reason == FullscreenVideoPictureInPictureController.MetricsEndReason.LEFT_FULLSCREEN
                || reason == FullscreenVideoPictureInPictureController.MetricsEndReason.WEB_CONTENTS_LEFT_FULLSCREEN;
    }

    private VersaniumYouTubePictureInPicturePolicy() {}
}
