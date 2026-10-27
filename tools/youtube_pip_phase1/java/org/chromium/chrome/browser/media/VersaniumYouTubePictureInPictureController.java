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
import org.chromium.chrome.browser.tab.TabObserver;
import org.chromium.chrome.browser.tab.TabHidingType;
import org.chromium.content_public.browser.MediaSession;
import org.chromium.content_public.browser.NavigationHandle;
import org.chromium.content_public.browser.WebContents;
import org.chromium.content_public.browser.WebContentsObserver;
import org.chromium.media_session.mojom.MediaSession.SuspendType;
import org.chromium.ui.base.WindowAndroid;
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
    private final Runnable mLeaveUpstream;
    private State mState = State.INACTIVE;
    private long mGeneration;
    private long mEpoch;
    private long mEnteredAt;
    private @Nullable Owner mOwner;
    private @Nullable Owner mCandidate;
    private @Nullable Tab mObservedTab;
    private @Nullable WebContentsObserver mExitObserver;
    private boolean mExitUiDone;
    private boolean mExitDecisionDone;
    private boolean mUpstreamEntered;
    private boolean mBlockCurrentMedia;
    private boolean mDestroyed;
    private final TabObserver mObserver = new TabObserver() {
        @Override
        public void onDidFinishNavigationInPrimaryMainFrame(Tab tab, NavigationHandle navigation) {
            if (!navigation.hasCommitted()) return;
            Owner owner = mOwner != null ? mOwner : mCandidate;
            if (owner == null || tab != owner.tab) return;
            if (!navigation.isSameDocument()
                    || !owner.videoId.equals(VersaniumYouTubePictureInPicturePolicy.videoId(
                            navigation.getUrl().getSpec()))) {
                ++mEpoch;
                invalidate();
            }
        }

        @Override
        public void onUrlUpdated(Tab tab) {
            Owner owner = mOwner != null ? mOwner : mCandidate;
            if (owner != null && tab == owner.tab
                    && !owner.videoId.equals(VersaniumYouTubePictureInPicturePolicy.videoId(
                            tab.getUrl().getSpec()))) {
                ++mEpoch;
                invalidate();
            }
        }

        @Override
        public void onContentChanged(Tab tab) {
            Owner owner = mOwner != null ? mOwner : mCandidate;
            if (owner != null && tab == owner.tab && tab.getWebContents() != owner.webContents) {
                ++mEpoch;
                invalidate();
            }
        }

        @Override
        public void onActivityAttachmentChanged(Tab tab, @Nullable WindowAndroid window) {
            Owner owner = mOwner != null ? mOwner : mCandidate;
            if (owner != null && tab == owner.tab && window != owner.window) invalidate();
        }

        @Override
        public void onHidden(Tab tab, int reason) {
            if (reason != TabHidingType.ACTIVITY_HIDDEN) invalidate();
        }

        @Override
        public void onClosingStateChanged(Tab tab, boolean closing) {
            if (closing) invalidate();
        }

        @Override
        public void onCrash(Tab tab) { invalidate(); }

        @Override
        public void onDestroyed(Tab tab) { invalidate(); }
    };

    VersaniumYouTubePictureInPictureController(
            Activity activity, ActivityTabProvider tabs, FullscreenManager fullscreen,
            Runnable leaveUpstream) {
        ThreadUtils.assertOnUiThread();
        mActivity = activity;
        mTabs = tabs;
        mFullscreen = fullscreen;
        mLeaveUpstream = leaveUpstream;
    }

    long beginEntry(@Nullable Tab tab, boolean upstream) {
        ThreadUtils.assertOnUiThread();
        Owner owner = VersaniumYouTubePictureInPicturePolicy.capture(mActivity, tab, upstream, mEpoch);
        if (owner == null || mDestroyed || mState == State.EXITING) return 0;
        if (mOwner != null) {
            return mOwner.tab == owner.tab && mOwner.live(mActivity, mEpoch) ? mGeneration : 0;
        }
        mOwner = owner;
        mCandidate = null;
        observe(owner.tab);
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
                && owner.activity == mActivity;
    }

    private void clear() {
        if (mExitObserver != null) {
            mExitObserver.observe(null);
            mExitObserver = null;
        }
        observe(null);
        WeakReference<VersaniumYouTubePictureInPictureController> ref = sLocators.get(mActivity);
        if (ref != null && ref.get() == this) sLocators.remove(mActivity);
        mOwner = null;
        mCandidate = null;
        mUpstreamEntered = false;
        mGeneration = ++sGeneration;
        mState = State.INACTIVE;
    }

    private void observe(@Nullable Tab tab) {
        if (mObservedTab == tab) return;
        if (mObservedTab != null) mObservedTab.removeObserver(mObserver);
        mObservedTab = tab;
        if (tab != null) tab.addObserver(mObserver);
    }

    private void invalidate() {
        mCandidate = null;
        Owner owner = mOwner;
        if (owner != null) beginExit(mGeneration, false, true);
        else observe(null);
    }

    /** Protection ends before any external cleanup calls. */
    private void beginExit(long generation, boolean classify, boolean immediateUi) {
        Owner owner = mOwner;
        if (owner == null || !matches(generation, owner) || mState == State.EXITING) return;
        mState = State.EXITING;
        mCandidate = null;
        mExitUiDone = false;
        mExitDecisionDone = !classify;
        if (!classify) suspendOwner(owner);
        if (classify) {
            PostTask.postDelayedTask(TaskTraits.UI_DEFAULT, () -> {
                if (!matches(generation, owner) || mState != State.EXITING
                        || mExitDecisionDone || mActivity.isDestroyed()) return;
                if (org.chromium.base.ApplicationStatus.getStateForActivity(mActivity)
                        != org.chromium.base.ActivityState.RESUMED) suspendOwner(owner);
                mExitDecisionDone = true;
                finishIfReady();
            }, VersaniumYouTubePictureInPicturePolicy.EXIT_CLASSIFICATION_MS);
        }
        if (owner.live(mActivity, mEpoch)) {
            mExitObserver = new WebContentsObserver(owner.webContents) {
                @Override
                public void didToggleFullscreenModeForTab(boolean entered, boolean willResize) {
                    if (!entered && matches(generation, owner) && mState == State.EXITING) {
                        finishUi(generation, owner);
                    }
                }
            };
            owner.webContents.exitFullscreen();
        }
        if (immediateUi || !owner.live(mActivity, mEpoch)) finishUi(generation, owner);
        else {
            PostTask.postDelayedTask(TaskTraits.UI_DEFAULT, () -> {
                if (matches(generation, owner) && !mActivity.isDestroyed()) finishUi(generation, owner);
            }, VersaniumYouTubePictureInPicturePolicy.DOM_EXIT_TIMEOUT_MS);
        }
    }

    private void finishUi(long generation, Owner owner) {
        if (!matches(generation, owner) || mState != State.EXITING || mExitUiDone) return;
        mExitUiDone = true;
        if (mExitObserver != null) {
            mExitObserver.observe(null);
            mExitObserver = null;
        }
        // The handler's identity guard rejects an unrelated/new tab fullscreen.
        mFullscreen.onExitFullscreen(owner.tab);
        mLeaveUpstream.run();
        finishIfReady();
    }

    private void finishIfReady() {
        if (mState == State.EXITING && mExitUiDone && mExitDecisionDone) clear();
    }

    private void suspendOwner(Owner owner) {
        if (!owner.live(mActivity, mEpoch)) return;
        MediaSession session = MediaSession.fromWebContents(owner.webContents);
        if (session != null) session.suspend(SuspendType.SYSTEM);
    }

    void onResume() {
        if (mState == State.EXITING) {
            mExitDecisionDone = true;
            finishIfReady();
        }
    }

    void onStop() {
        Owner owner = mOwner;
        if (owner == null) return;
        if (mState != State.EXITING) beginExit(mGeneration, false, true);
        else {
            suspendOwner(owner);
            mExitDecisionDone = true;
            finishIfReady();
        }
    }

    void onDestroy() {
        Owner owner = mOwner;
        if (owner != null) {
            if (!owner.webContents.isDestroyed() && owner.documentEpoch == mEpoch
                    && owner.tab.getWebContents() == owner.webContents) {
                MediaSession session = MediaSession.fromWebContents(owner.webContents);
                if (session != null) session.suspend(SuspendType.SYSTEM);
                owner.webContents.exitFullscreen();
            }
            mFullscreen.onExitFullscreen(owner.tab);
            mLeaveUpstream.run();
        }
        clear();
        mDestroyed = true;
    }

    void updateCandidate(@Nullable Tab tab, boolean upstream) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed) return;
        if (mState != State.INACTIVE) {
            if (mOwner != null && mTabs.get() != mOwner.tab) invalidate();
            return;
        }
        mCandidate = VersaniumYouTubePictureInPicturePolicy.capture(mActivity, tab, upstream, mEpoch);
        observe(mCandidate == null ? null : mCandidate.tab);
        if (mCandidate != null) sLocators.put(mActivity, new WeakReference<>(this));
    }

    /** False suppresses only a duplicate callback for our owned session. */
    boolean onFrameworkEntered(boolean upstream) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed) return true;
        Owner owner = mOwner;
        if (owner == null && mState == State.INACTIVE) {
            Owner candidate = mCandidate;
            if (candidate == null || !candidate.live(mActivity, mEpoch)
                    || candidate.tab != mTabs.get()) {
                candidate = VersaniumYouTubePictureInPicturePolicy.capture(
                        mActivity, mTabs.get(), upstream, mEpoch);
            }
            if (candidate != null && mActivity.isInPictureInPictureMode()) {
                mOwner = candidate;
                mCandidate = null;
                mGeneration = ++sGeneration;
                mState = State.ENTERING;
                mEnteredAt = SystemClock.elapsedRealtime();
                mBlockCurrentMedia = true;
                observe(candidate.tab);
                sLocators.put(mActivity, new WeakReference<>(this));
                owner = candidate;
            }
        }
        if (owner == null) {
            mBlockCurrentMedia = false;
            return true;
        }
        if (mState == State.EXITING || !owner.live(mActivity, mEpoch)
                || owner.tab != mTabs.get() || !mActivity.isInPictureInPictureMode()) return false;
        mState = State.ACTIVE;
        if (mUpstreamEntered) return false;
        mUpstreamEntered = true;
        return true;
    }

    void onEntryComplete() {
        Owner owner = mOwner;
        if (owner != null && (!owner.live(mActivity, mEpoch) || owner.tab != mTabs.get())) invalidate();
    }

    void beginFrameworkExit() {
        if (mOwner != null) beginExit(mGeneration, true, false);
        else {
            mCandidate = null;
            observe(null);
        }
    }

    void onNewIntent() {
        invalidate();
    }
}
