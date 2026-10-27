/* Copyright (c) 2026 The Brave Authors. All rights reserved.
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at https://mozilla.org/MPL/2.0/. */
// SPDX-License-Identifier: MPL-2.0
// Adapted from Brave #36838.
// Source revision: 4ea2dc54aaf5a404064cd9ff4473ee088a95fdb2

package org.chromium.chrome.browser.media;

import android.app.Activity;
import android.os.SystemClock;

import org.chromium.base.ThreadUtils;
import org.chromium.base.task.PostTask;
import org.chromium.base.task.TaskTraits;
import org.chromium.build.annotations.NullMarked;
import org.chromium.build.annotations.Nullable;
import org.chromium.chrome.browser.ActivityTabProvider;
import org.chromium.chrome.browser.fullscreen.FullscreenManager;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.chrome.browser.media.VersaniumYouTubePictureInPicturePolicy.Owner;
import org.chromium.chrome.browser.media.VersaniumYouTubePictureInPicturePolicy.State;

import java.lang.ref.WeakReference;
import java.util.WeakHashMap;

/** Chrome-only owner transaction. Strongly retained by the host's video controller. */
@NullMarked
public final class VersaniumYouTubePictureInPictureController {
    private static final WeakHashMap<Activity,
            WeakReference<VersaniumYouTubePictureInPictureController>> sLocators = new WeakHashMap<>();
    private static long sGeneration;
    private final Activity mActivity;
    private final ActivityTabProvider mTabs;
    private final FullscreenManager mFullscreen;
    private State mState = State.INACTIVE;
    private long mGeneration;
    private long mEpoch;
    private long mEnteredAt;
    private @Nullable Owner mOwner;
    private boolean mDestroyed;

    VersaniumYouTubePictureInPictureController(
            Activity activity, ActivityTabProvider tabs, FullscreenManager fullscreen) {
        ThreadUtils.assertOnUiThread();
        mActivity = activity;
        mTabs = tabs;
        mFullscreen = fullscreen;
    }

    long beginEntry(@Nullable Tab tab, boolean upstream) {
        ThreadUtils.assertOnUiThread();
        Owner owner = VersaniumYouTubePictureInPicturePolicy.capture(mActivity, tab, upstream, mEpoch);
        if (owner == null || mDestroyed || mState == State.EXITING) return 0;
        if (mOwner != null) {
            return mOwner.tab == owner.tab && mOwner.live(mActivity, mEpoch) ? mGeneration : 0;
        }
        mOwner = owner;
        mGeneration = ++sGeneration;
        mState = State.ENTERING;
        mEnteredAt = SystemClock.elapsedRealtime();
        sLocators.put(mActivity, new WeakReference<>(this));
        long generation = mGeneration;
        PostTask.postDelayedTask(TaskTraits.UI_DEFAULT, () -> {
            if (!matches(generation, owner) || mState != State.ENTERING) return;
            if (mActivity.isInPictureInPictureMode() && owner.live(mActivity, mEpoch)) {
                mState = State.ACTIVE;
            } else {
                rollback(generation);
            }
        }, VersaniumYouTubePictureInPicturePolicy.ENTRY_TIMEOUT_MS);
        return generation;
    }

    void rollback(long generation) {
        if (generation == 0 || generation != mGeneration || mState != State.ENTERING) return;
        clear();
    }

    private boolean matches(long generation, Owner owner) {
        return !mDestroyed && generation == mGeneration && mOwner == owner
                && owner.activity == mActivity && !mActivity.isDestroyed();
    }

    private void clear() {
        WeakReference<VersaniumYouTubePictureInPictureController> ref = sLocators.get(mActivity);
        if (ref != null && ref.get() == this) sLocators.remove(mActivity);
        mOwner = null;
        mState = State.INACTIVE;
    }
}
