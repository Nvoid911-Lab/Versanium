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
import org.chromium.chrome.browser.fullscreen.FullscreenOptions;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.chrome.browser.tab.TabObserver;
import org.chromium.chrome.browser.tab.TabHidingType;
import org.chromium.content_public.browser.MediaSession;
import org.chromium.content_public.browser.MediaSessionObserver;
import org.chromium.content_public.browser.NavigationHandle;
import org.chromium.content_public.browser.WebContents;
import org.chromium.content_public.browser.WebContentsObserver;
import org.chromium.media_session.mojom.MediaSession.SuspendType;
import org.chromium.ui.base.WindowAndroid;
import org.chromium.chrome.browser.media.VersaniumYouTubePictureInPicturePolicy.Owner;
import org.chromium.chrome.browser.media.VersaniumYouTubePictureInPicturePolicy.State;

import java.lang.ref.WeakReference;
import java.util.WeakHashMap;
import java.util.ArrayList;
import java.util.List;

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
    private final Runnable mConfirmEntry;
    interface TerminalDismissCallback {
        void dismiss(int reason, Tab tab, WebContents webContents);
    }
    private final TerminalDismissCallback mTerminalDismiss;
    private @Nullable Tab mUiTab;
    private long mUiEpoch;
    private boolean mUpstreamCleanupDone;
    private final FullscreenManager.Observer mUiObserver = new FullscreenManager.Observer() {
        @Override
        public void onEnterFullscreen(Tab tab, FullscreenOptions options) {
            diagnostic("FULLSCREEN_ENTER", "tab=" + tab.getId());
            mUiTab = tab;
            mUiEpoch = mEpoch;
        }

        @Override
        public void onExitFullscreen(Tab tab) {
            diagnostic("FULLSCREEN_EXIT", "tab=" + tab.getId());
            if (mUiTab == tab) mUiTab = null;
        }
    };
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
    // Survives clear() only for the just-retired generation; never a current-tab lookup.
    private @Nullable Owner mTerminalOwner;
    private long mTerminalGeneration;
    private long mRetiredGeneration;
    private boolean mTerminalConsumed;
    static final int TERMINAL_UNRELATED = 0;
    static final int TERMINAL_CLAIMED = 1;
    static final int TERMINAL_DUPLICATE = 2;
    private @Nullable Owner mRejectedCandidate;
    private @Nullable TabObserver mRecoveryObserver;
    private @Nullable TabObserver mObserver;

    public static void diagnosticActivity(Activity activity, String event) {
        diagnosticActivity(activity, event, null);
    }

    public static void diagnosticActivity(Activity activity, String event, @Nullable Tab tab) {
        VersaniumYouTubePictureInPicturePolicy.diagnostic(event,
                VersaniumYouTubePictureInPicturePolicy.diagnosticPageFields(tab)
                + " finishing=" + activity.isFinishing() + " destroyed=" + activity.isDestroyed()
                + " configurationChanging=" + activity.isChangingConfigurations()
                + " frameworkPip=" + activity.isInPictureInPictureMode());
    }

    void diagnostic(String event, String fields) {
        Owner owner = mOwner;
        VersaniumYouTubePictureInPicturePolicy.diagnostic(event,
                "state=" + mState + " generation=" + mGeneration + " epoch=" + mEpoch
                + " hasOwner=" + (owner != null) + " hasCandidate=" + (mCandidate != null)
                + " ownerTab=" + (owner == null ? -1 : owner.tabId)
                + " hasOwnerWebContents=" + (owner != null)
                + " foregroundOwner=" + (owner != null && owner.tab == mTabs.get()) + " "
                + VersaniumYouTubePictureInPicturePolicy.diagnosticPageFields(
                        owner != null ? owner.tab : mTabs.get()) + " " + fields);
        if (mDiagnosticPage != null) mDiagnosticPage.emit("PAGE_SNAPSHOT", "trigger=" + event);
        if (mPreviousDiagnosticPage != null) {
            mPreviousDiagnosticPage.emit("PAGE_SNAPSHOT", "trigger=" + event);
        }
    }

    private void transition(State next, String reason) {
        VersaniumYouTubePictureInPicturePolicy.diagnostic("STATE",
                "from=" + mState + " to=" + next + " reason=" + reason
                + " generation=" + mGeneration + " "
                + VersaniumYouTubePictureInPicturePolicy.diagnosticPageFields(
                        mOwner != null ? mOwner.tab : mTabs.get()));
        mState = next;
    }

    boolean diagnosticUpstream(boolean allowed, String reason) {
        diagnostic("UPSTREAM_POLICY", "eligible=" + allowed + " reason=" + reason);
        if (!allowed) VersaniumYouTubePictureInPicturePolicy.diagnosticPolicy(
                mActivity, mTabs.get(), false, false, reason);
        return allowed;
    }

    // At most two passive page probes, independent from PiP ownership/generation.
    // Retaining the outgoing page catches asynchronous pause/visibility AFTER tab switch.
    private @Nullable DiagnosticPage mDiagnosticPage;
    private @Nullable DiagnosticPage mPreviousDiagnosticPage;

    private final class DiagnosticPage {
        final Tab tab;
        final WebContents wc;
        final int tabId;
        private boolean closed;
        private boolean lastDesktopSite;
        private String playingSignal = "unknown";
        private String sessionControllable = "unknown";
        private String sessionSuspended = "unknown";
        private @Nullable WebContentsObserver contentsObserver;
        private @Nullable MediaSessionObserver sessionObserver;

        DiagnosticPage(Tab source, WebContents contents) {
            tab = source;
            tabId = source.getId();
            wc = contents;
            lastDesktopSite = wc.getNavigationController().getUseDesktopUserAgent();
            contentsObserver = new WebContentsObserver(wc) {
                @Override
                public void onVisibilityChanged(int visibility) {
                    emit("WC_VISIBILITY", "visibility=" + visibility);
                }

                @Override
                public void mediaStartedPlaying(int id, boolean hasAudio, boolean hasVideo) {
                    playingSignal = "started";
                    emit("MEDIA_STARTED", "player=" + id + " hasAudio=" + hasAudio + " hasVideo=" + hasVideo);
                }

                @Override
                public void mediaStoppedPlaying(int id) {
                    playingSignal = "stopped";
                    emit("MEDIA_STOPPED", "player=" + id + " aggregatePlaying=unknown");
                }

                @Override
                public void didToggleFullscreenModeForTab(boolean entered, boolean willResize) {
                    if (org.chromium.base.CommandLine.isInitialized()
                            && org.chromium.base.CommandLine.getInstance().hasSwitch(
                                    "versanium-zoom-fullscreen-diagnostics")
                            && !closed && !mDestroyed && !tab.isDestroyed()
                            && !wc.isDestroyed() && tab.getWebContents() == wc) {
                        org.chromium.content_public.browser.EnvironmentZoom.vsZoomFullscreen(wc, tabId, entered);
                    }
                    emit("PAGE_FULLSCREEN", "entered=" + entered);
                }

                @Override
                public void webContentsDestroyed() {
                    VersaniumYouTubePictureInPicturePolicy.diagnostic("PAGE_DESTROYED",
                            "sourceTab=" + tabId + " desktop_site=" + lastDesktopSite + " pageReadable=false");
                    close();
                }
            };
            MediaSession session = MediaSession.fromWebContents(wc);
            if (session != null) {
                sessionObserver = new MediaSessionObserver(session) {
                    @Override
                    public void mediaSessionStateChanged(boolean controllable, boolean suspended) {
                        sessionControllable = Boolean.toString(controllable);
                        sessionSuspended = Boolean.toString(suspended);
                        emit("MEDIA_SESSION", "source=existing_java_callback");
                    }

                    @Override
                    public void mediaSessionDestroyed() {
                        emit("MEDIA_SESSION_DESTROYED", "sessionActive=unavailable");
                        stopObserving();
                    }
                };
            }
            emit("PAGE_MODE", "source=existing_navigation_controller");
        }

        boolean matches(Tab source, WebContents contents) {
            return !closed && tab == source && wc == contents;
        }

        void emit(String event, String detail) {
            if (closed || mDestroyed) return;
            if (tab.isDestroyed() || wc.isDestroyed() || tab.getWebContents() != wc) {
                close();
                return;
            }
            lastDesktopSite = wc.getNavigationController().getUseDesktopUserAgent();
            VersaniumYouTubePictureInPicturePolicy.diagnostic(event,
                    "sourceTab=" + tabId + " selected=" + (mTabs.get() == tab)
                    + " owner=" + (mOwner != null && mOwner.tab == tab)
                    + " retainedOutgoing=" + (mTabs.get() != tab)
                    + " " + VersaniumYouTubePictureInPicturePolicy.diagnosticPageFields(tab)
                    + " mediaPlayingSignal=" + playingSignal
                    + " sessionControllable=" + sessionControllable
                    + " sessionSuspended=" + sessionSuspended
                    + " sessionActive=unavailable " + detail);
        }

        void close() {
            if (closed) return;
            closed = true;
            if (contentsObserver != null) contentsObserver.observe(null);
            if (sessionObserver != null) sessionObserver.stopObserving();
            contentsObserver = null;
            sessionObserver = null;
            if (mDiagnosticPage == this) mDiagnosticPage = null;
            if (mPreviousDiagnosticPage == this) mPreviousDiagnosticPage = null;
        }
    }

    void diagnosticObserve(@Nullable Tab tab) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed
                || tab == null || tab.isDestroyed()) return;
        WebContents wc = tab.getWebContents();
        if (wc == null || wc.isDestroyed()) return;
        android.net.Uri uri = android.net.Uri.parse(tab.getUrl().getSpec());
        String host = uri.getHost();
        // Broader diagnostic observation is NOT product eligibility.
        if (!("m.youtube.com".equals(host) || "www.youtube.com".equals(host)
                || "youtube.com".equals(host)) || !"/watch".equals(uri.getPath())) return;
        if (mDiagnosticPage != null && mDiagnosticPage.matches(tab, wc)) return;
        if (mPreviousDiagnosticPage != null && mPreviousDiagnosticPage.matches(tab, wc)) {
            DiagnosticPage selected = mPreviousDiagnosticPage;
            mPreviousDiagnosticPage = mDiagnosticPage;
            mDiagnosticPage = selected;
            selected.emit("PAGE_MODE", "source=reselected");
            return;
        }
        if (mPreviousDiagnosticPage != null) mPreviousDiagnosticPage.close();
        mPreviousDiagnosticPage = mDiagnosticPage;
        mDiagnosticPage = new DiagnosticPage(tab, wc);
    }

    void diagnosticTabEvent(String event, @Nullable Tab tab, String fields) {
        VersaniumYouTubePictureInPicturePolicy.diagnostic(event,
                "sourceTab=" + (tab == null ? -1 : tab.getId()) + " "
                + VersaniumYouTubePictureInPicturePolicy.diagnosticPageFields(tab) + " " + fields);
        if (mDiagnosticPage != null) mDiagnosticPage.emit("PAGE_SNAPSHOT", "trigger=" + event);
        if (mPreviousDiagnosticPage != null) {
            mPreviousDiagnosticPage.emit("PAGE_SNAPSHOT", "trigger=" + event);
        }
    }

    private TabObserver createObserver(Owner observed, long generation) {
        return new TabObserver() {
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
                if (owner != null && tab == owner.tab && window != owner.window) {
                    invalidateTerminal(observed, generation, FullscreenVideoPictureInPictureController.MetricsEndReason.REPARENT, tab);
                }
            }

            @Override
            public void onHidden(Tab tab, int reason) {
                if (reason != TabHidingType.ACTIVITY_HIDDEN) invalidate();
            }

            @Override
            public void onClosingStateChanged(Tab tab, boolean closing) {
                if (closing) invalidateTerminal(observed, generation, FullscreenVideoPictureInPictureController.MetricsEndReason.CLOSE, tab);
            }

            @Override
            public void onCrash(Tab tab) {
                invalidateTerminal(observed, generation, FullscreenVideoPictureInPictureController.MetricsEndReason.CRASH, tab);
            }

            @Override
            public void onDestroyed(Tab tab) { diagnostic("TAB_DESTROYED", "tab=" + tab.getId()); invalidate(); }
        };
    }

    VersaniumYouTubePictureInPictureController(
            Activity activity, ActivityTabProvider tabs, FullscreenManager fullscreen,
            Runnable leaveUpstream, Runnable confirmEntry, TerminalDismissCallback terminalDismiss) {
        ThreadUtils.assertOnUiThread();
        mActivity = activity;
        mTabs = tabs;
        mFullscreen = fullscreen;
        mLeaveUpstream = leaveUpstream;
        mConfirmEntry = confirmEntry;
        mTerminalDismiss = terminalDismiss;
        diagnostic("INIT", "enabled=" + VersaniumYouTubePictureInPicturePolicy.ENABLED);
        if (VersaniumYouTubePictureInPicturePolicy.ENABLED) mFullscreen.addObserver(mUiObserver);
    }

    long beginEntry(@Nullable Tab tab, boolean upstream) {
        diagnostic("ENTRY_REQUESTED", "path=beginEntry");
        ThreadUtils.assertOnUiThread();
        Owner owner = VersaniumYouTubePictureInPicturePolicy.capture(mActivity, tab, upstream, mEpoch);
        if (owner == null || mDestroyed || mState == State.EXITING) {
            diagnostic("ENTRY_SUPPRESSED", "reason=no_eligible_owner_or_exiting");
            return 0;
        }
        if (mOwner != null) {
            if (mOwner.tab == owner.tab && mOwner.live(mActivity, mEpoch)) return mGeneration;
            diagnostic("OWNER_REPLACEMENT", "action=invalidate_existing");
            invalidate();
            return 0;
        }
        clearRejectedCandidate();
        resetTerminal();
        diagnostic("OWNER_ADOPT", "path=explicit");
        mOwner = owner;
        seedUiOwner(owner);
        mBlockCurrentMedia = true;
        mCandidate = null;
        mGeneration = ++sGeneration;
        diagnostic("GENERATION", "action=advance");
        observe(owner.tab);
        transition(State.ENTERING, "owner_adopted");
        mEnteredAt = SystemClock.elapsedRealtime();
        sLocators.put(mActivity, new WeakReference<>(this));
        long generation = mGeneration;
        PostTask.postDelayedTask(TaskTraits.UI_DEFAULT, () -> {
            if (!matches(generation, owner) || mState != State.ENTERING) return;
            if (mActivity.isInPictureInPictureMode() && owner.live(mActivity, mEpoch)) {
                mConfirmEntry.run();
            } else {
                rollback(generation);
            }
        }, VersaniumYouTubePictureInPicturePolicy.ENTRY_TIMEOUT_MS);
        return generation;
    }

    void rollback(long generation) {
        diagnostic("ROLLBACK_REQUESTED", "path=rollback");
        if (generation == 0 || generation != mGeneration || mState != State.ENTERING) return;
        diagnostic("ENTRY_ABORTED", "reason=rollback");
        mBlockCurrentMedia = false;
        clear();
    }

    private boolean matches(long generation, Owner owner) {
        return !mDestroyed && generation == mGeneration && mOwner == owner
                && owner.activity == mActivity;
    }

    private void clear() {
        diagnostic("CLEANUP", "path=clear");
        if (mExitObserver != null) {
            mExitObserver.observe(null);
            mExitObserver = null;
        }
        observe(null);
        WeakReference<VersaniumYouTubePictureInPictureController> ref = sLocators.get(mActivity);
        if (ref != null && ref.get() == this) sLocators.remove(mActivity);
        mRetiredGeneration = mGeneration;
        mOwner = null;
        mCandidate = null;
        mUpstreamEntered = false;
        mUpstreamCleanupDone = false;
        mGeneration = ++sGeneration;
        diagnostic("GENERATION", "action=advance");
        transition(State.INACTIVE, "clear");
    }

    private void observe(@Nullable Tab tab) {
        if (mObservedTab != null && mObserver != null) mObservedTab.removeObserver(mObserver);
        mObservedTab = tab;
        mObserver = null;
        Owner observed = mOwner != null ? mOwner : mCandidate;
        if (tab != null && observed != null) {
            TabObserver observer = createObserver(observed, mGeneration);
            mObserver = observer;
            tab.addObserver(observer);
        }
    }

    private void invalidate() {
        mCandidate = null;
        Owner owner = mOwner;
        if (owner != null) beginExit(mGeneration, false, true);
        else observe(null);
    }

    /** Protection ends before any external cleanup calls. */
    private void beginExit(long generation, boolean classify, boolean immediateUi) {
        diagnostic("EXIT", "path=beginExit");
        Owner owner = mOwner;
        if (owner == null || !matches(generation, owner) || mState == State.EXITING) return;
        transition(State.EXITING, "exit_or_destroy");
        mCandidate = null;
        mExitUiDone = false;
        mExitDecisionDone = !classify;
        // Detach persistent-video callbacks before external DOM/UI calls can reenter VIDEO.
        leaveUpstreamOnce();
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
        clearOwnerUi(owner);
        finishIfReady();
    }

    private void finishIfReady() {
        if (mState == State.EXITING && mExitUiDone && mExitDecisionDone) clear();
    }

    private void suspendOwner(Owner owner) {
        if (!owner.attached(mActivity, mEpoch)) return;
        diagnostic("OWNER_SUSPEND", "path=existing_cleanup");
        MediaSession session = MediaSession.fromWebContents(owner.webContents);
        if (session != null) session.suspend(SuspendType.SYSTEM);
    }

    void onResume() {
        diagnostic("RESUME", "path=onResume");
        if (mState == State.EXITING) {
            mExitDecisionDone = true;
            finishIfReady();
        }
    }

    void onStop() {
        diagnostic("STOP", "path=onStop");
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
        diagnostic("DESTROY", "path=onDestroy");
        Owner owner = mOwner;
        if (owner != null) {
            transition(State.EXITING, "exit_or_destroy");
            leaveUpstreamOnce();
            if (!owner.webContents.isDestroyed() && owner.documentEpoch == mEpoch
                    && owner.tab.getWebContents() == owner.webContents) {
                MediaSession session = MediaSession.fromWebContents(owner.webContents);
                if (session != null) session.suspend(SuspendType.SYSTEM);
                owner.webContents.exitFullscreen();
            }
            clearOwnerUi(owner);
        }
        clear();
        if (VersaniumYouTubePictureInPicturePolicy.ENABLED) mFullscreen.removeObserver(mUiObserver);
        resetTerminal();
        clearRejectedCandidate();
        mDestroyed = true;
        if (mDiagnosticPage != null) mDiagnosticPage.close();
        if (mPreviousDiagnosticPage != null) mPreviousDiagnosticPage.close();
        mDiagnosticPage = null;
        mPreviousDiagnosticPage = null;
    }

    void updateCandidate(@Nullable Tab tab, boolean upstream) {
        diagnostic("CANDIDATE_UPDATE", "path=updateCandidate upstreamEligible=" + upstream);
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed) return;
        if (mState != State.INACTIVE) {
            if (mOwner != null && mTabs.get() != mOwner.tab) invalidate();
            return;
        }
        Owner candidate = VersaniumYouTubePictureInPicturePolicy.capture(mActivity, tab, upstream, mEpoch);
        if (candidate != null && rejectedCandidate(candidate)) candidate = null;
        if (mCandidate == null && candidate == null) return;
        mCandidate = candidate;
        mGeneration = ++sGeneration;
        diagnostic("GENERATION", "action=advance");
        observe(mCandidate == null ? null : mCandidate.tab);
        if (mCandidate != null) sLocators.put(mActivity, new WeakReference<>(this));
    }

    /** False suppresses only a duplicate callback for our owned session. */
    boolean onFrameworkEntered(boolean upstream) {
        diagnostic("FRAMEWORK_ENTERED", "path=onFrameworkEntered");
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed) return true;
        Owner owner = mOwner;
        if (owner == null && mState == State.INACTIVE) {
            Owner candidate = mCandidate;
            if (candidate != null && (!candidate.live(mActivity, mEpoch)
                    || candidate.tab != mTabs.get())) candidate = null;
            if (candidate != null && mActivity.isInPictureInPictureMode()) {
                resetTerminal();
                diagnostic("OWNER_ADOPT", "path=framework_or_provisional");
                mOwner = candidate;
                seedUiOwner(candidate);
                mCandidate = null;
                mGeneration = ++sGeneration;
                diagnostic("GENERATION", "action=advance");
                transition(State.ENTERING, "owner_adopted");
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
        if (mState == State.EXITING) return false;
        if (!owner.live(mActivity, mEpoch) || owner.tab != mTabs.get()
                || !mActivity.isInPictureInPictureMode()) {
            invalidate();
            return false;
        }
        transition(State.ACTIVE, "framework_entered");
        if (mUpstreamEntered) return false;
        mUpstreamEntered = true;
        return true;
    }

    void onEntryComplete() {
        Owner owner = mOwner;
        if (owner != null && (!owner.live(mActivity, mEpoch) || owner.tab != mTabs.get())) invalidate();
    }

    void beginFrameworkExit() {
        diagnostic("FRAMEWORK_EXIT", "path=beginFrameworkExit");
        if (mOwner != null) beginExit(mGeneration, true, false);
        else {
            mCandidate = null;
            observe(null);
        }
    }

    void onNewIntent() {
        diagnostic("NEW_INTENT", "path=onNewIntent");
        resetTerminal();
        invalidate();
    }

    /** The two fullscreen signals must carry the originating tab/WC. */
    boolean handleDismiss(int reason, @Nullable Tab sourceTab, @Nullable WebContents sourceWc) {
        diagnostic("DISMISS", "reason=" + reason + " newTab=" + (reason == FullscreenVideoPictureInPictureController.MetricsEndReason.NEW_TAB)
                + " incomingTab=" + (mTabs.get() == null ? -1 : mTabs.get().getId()));
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED) return false;
        if (reason == FullscreenVideoPictureInPictureController.MetricsEndReason.NEW_TAB) {
            resetTerminal();
        }
        Owner owner = mOwner;
        if (owner == null) {
            if (reason == FullscreenVideoPictureInPictureController.MetricsEndReason.NEW_TAB) {
                mCandidate = null;
                observe(null);
            }
            return false;
        }
        boolean lifecycle = reason == FullscreenVideoPictureInPictureController.MetricsEndReason.START
                || reason == FullscreenVideoPictureInPictureController.MetricsEndReason.RESUME;
        boolean sourceMatches = lifecycle
                || (sourceTab == owner.tab && sourceWc == owner.webContents);
        if (sourceMatches && mTabs.get() == owner.tab && owner.live(mActivity, mEpoch)
                && VersaniumYouTubePictureInPicturePolicy.transientReason(reason)
                && VersaniumYouTubePictureInPicturePolicy.protectedState(
                        mState, mEnteredAt, mActivity.isInPictureInPictureMode())
                && (lifecycle || mActivity.isInPictureInPictureMode())) return true;
        if (reason == FullscreenVideoPictureInPictureController.MetricsEndReason.NEW_TAB) {
            beginExit(mGeneration, false, true);
            return true; // The incoming foreground tab must never be moved to the back.
        }
        // A non-owner fullscreen event is not ours to suppress or use for owner cleanup.
        if (!lifecycle && !sourceMatches) return false;
        if (reason == FullscreenVideoPictureInPictureController.MetricsEndReason.RESUME
                && !mActivity.isInPictureInPictureMode()) beginExit(mGeneration, true, false);
        else beginExit(mGeneration, false, true);
        return false;
    }

    boolean ownsMediaRouting() { return mBlockCurrentMedia; }

    @Nullable MediaSession ownerMediaSession() {
        Owner owner = mOwner;
        return owner != null && owner.live(mActivity, mEpoch)
                ? MediaSession.fromWebContents(owner.webContents) : null;
    }

    /** Invalidates queued upstream work even after cleanup, before another entry occurs. */
    Runnable guardDelayed(Runnable action) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED) return action;
        long generation = mGeneration;
        Owner owner = mOwner;
        Tab tab = mTabs.get();
        WebContents wc = tab == null ? null : tab.getWebContents();
        return () -> {
            if (mDestroyed || generation != mGeneration || mActivity.isDestroyed()
                    || mActivity.isFinishing() || mActivity.isChangingConfigurations()) return;
            if (mTabs.get() != tab || (tab != null && tab.getWebContents() != wc)) return;
            if (owner != null && (!matches(generation, owner)
                    || !owner.live(mActivity, mEpoch))) return;
            action.run();
        };
    }

    @Nullable Tab entryTab(@Nullable Tab upstreamTab) {
        Owner owner = mOwner;
        if (owner != null) return owner.live(mActivity, mEpoch) ? owner.tab : null;
        return mBlockCurrentMedia ? null : upstreamTab;
    }

    private boolean preserve(@Nullable Tab tab, @Nullable Tab fullscreenTab) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed
                || tab == null || tab != fullscreenTab || tab != mTabs.get()) return false;
        Owner owner = mOwner;
        if (owner == null && mState == State.INACTIVE && mActivity.isInPictureInPictureMode()) {
            Owner candidate = mCandidate;
            if (candidate != null && candidate.tab == tab && candidate.live(mActivity, mEpoch)) {
                resetTerminal();
                diagnostic("OWNER_ADOPT", "path=framework_or_provisional");
                mOwner = candidate;
                seedUiOwner(candidate);
                mCandidate = null;
                mGeneration = ++sGeneration;
                diagnostic("GENERATION", "action=advance");
                transition(State.ENTERING, "owner_adopted");
                mEnteredAt = SystemClock.elapsedRealtime();
                mBlockCurrentMedia = true;
                owner = candidate;
                observe(candidate.tab);
                // Framework already reports PiP. This provisional adoption must not claim
                // that the upstream persistent-video callback has run.
                long generation = mGeneration;
                Owner adopted = candidate;
                PostTask.postDelayedTask(TaskTraits.UI_DEFAULT, () -> {
                    if (!matches(generation, adopted) || mState != State.ENTERING) return;
                    if (mActivity.isInPictureInPictureMode() && adopted.live(mActivity, mEpoch)) {
                        mConfirmEntry.run();
                    } else rollback(generation);
                }, VersaniumYouTubePictureInPicturePolicy.ENTRY_TIMEOUT_MS);
            }
        }
        return owner != null && owner.tab == tab && owner.live(mActivity, mEpoch)
                && VersaniumYouTubePictureInPicturePolicy.protectedState(
                        mState, mEnteredAt, mActivity.isInPictureInPictureMode());
    }

    private static @Nullable VersaniumYouTubePictureInPictureController locate(Activity activity) {
        ThreadUtils.assertOnUiThread();
        WeakReference<VersaniumYouTubePictureInPictureController> ref = sLocators.get(activity);
        return ref == null ? null : ref.get();
    }

    public static boolean preserveOnHidden(Activity activity, @Nullable Tab tab,
            @Nullable Tab fullscreenTab, int reason) {
        VersaniumYouTubePictureInPictureController controller = locate(activity);
        if (controller == null) return false;
        if (reason != TabHidingType.ACTIVITY_HIDDEN) {
            Owner owner = controller.mOwner;
            if (owner != null && owner.tab == tab) controller.invalidate();
            return false;
        }
        return controller.preserve(tab, fullscreenTab);
    }

    public static boolean preserveOnStopped(Activity handler, Activity callback,
            @Nullable Tab fullscreenTab) {
        if (handler != callback) return false;
        VersaniumYouTubePictureInPictureController controller = locate(handler);
        return controller != null && controller.preserve(fullscreenTab, fullscreenTab);
    }

    private void resetTerminal() {
        diagnostic("TERMINAL_RESET", "path=resetTerminal");
        mTerminalOwner = null;
        mTerminalGeneration = 0;
        mTerminalConsumed = false;
    }

    private void armTerminal(int reason, @Nullable Tab tab, @Nullable WebContents wc) {
        Owner owner = mOwner;
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed || owner == null
                || owner.tab != tab || owner.webContents != wc
                || !VersaniumYouTubePictureInPicturePolicy.passthroughReason(reason)) return;
        if (mTerminalOwner == owner && mTerminalGeneration == mGeneration) return;
        diagnostic("TERMINAL_ARM", "reason=" + reason);
        mTerminalOwner = owner;
        mTerminalGeneration = mGeneration;
        mTerminalConsumed = false;
    }

    private void clearRejectedCandidate() {
        Owner rejected = mRejectedCandidate;
        if (rejected != null && mRecoveryObserver != null) {
            rejected.tab.removeObserver(mRecoveryObserver);
        }
        mRecoveryObserver = null;
        mRejectedCandidate = null;
    }

    // Retain only document recovery observation, never candidate/owner authority.
    private void observeRejectedCandidate(Owner rejected) {
        long generation = mGeneration;
        TabObserver observer = new TabObserver() {
            private boolean current(Tab tab) {
                return !mDestroyed && mRejectedCandidate == rejected
                        && mGeneration == generation && tab == rejected.tab;
            }

            private void recovered(Tab tab) {
                if (!current(tab)) return;
                ++mEpoch;
                clearRejectedCandidate();
            }

            @Override
            public void onDidFinishNavigationInPrimaryMainFrame(Tab tab, NavigationHandle navigation) {
                if (!current(tab) || !navigation.hasCommitted()) return;
                if (!navigation.isSameDocument()
                        || !rejected.videoId.equals(VersaniumYouTubePictureInPicturePolicy.videoId(
                                navigation.getUrl().getSpec()))) recovered(tab);
            }

            @Override
            public void onUrlUpdated(Tab tab) {
                if (current(tab) && !rejected.videoId.equals(
                        VersaniumYouTubePictureInPicturePolicy.videoId(tab.getUrl().getSpec()))) {
                    recovered(tab);
                }
            }

            @Override
            public void onContentChanged(Tab tab) {
                if (current(tab) && tab.getWebContents() != rejected.webContents) recovered(tab);
            }

            @Override
            public void onDestroyed(Tab tab) {
                if (current(tab)) clearRejectedCandidate();
            }
        };
        mRecoveryObserver = observer;
        rejected.tab.addObserver(observer);
    }

    // No clock expiry: only validated document/session evidence lifts rejection.
    private boolean rejectedCandidate(Owner candidate) {
        Owner rejected = mRejectedCandidate;
        if (rejected == null) return false;
        boolean same = rejected.activity == candidate.activity
                && rejected.tab == candidate.tab && rejected.tabId == candidate.tabId
                && rejected.webContents == candidate.webContents && rejected.window == candidate.window
                && rejected.documentEpoch == candidate.documentEpoch
                && rejected.videoId.equals(candidate.videoId);
        if (!same) clearRejectedCandidate();
        return same;
    }

    private void discardTerminalCandidate(Owner candidate, long generation) {
        if (mOwner != null || mCandidate != candidate || mGeneration != generation
                || candidate.activity != mActivity || candidate.documentEpoch != mEpoch) return;
        // Revoke snapshots and queued work before detaching observers; no owner cleanup.
        clearRejectedCandidate();
        diagnostic("CANDIDATE_TERMINAL", "ownerCleanup=false");
        mRejectedCandidate = candidate;
        mCandidate = null;
        mGeneration = ++sGeneration;
        diagnostic("GENERATION", "action=advance");
        observe(null);
        observeRejectedCandidate(candidate);
        WeakReference<VersaniumYouTubePictureInPictureController> ref = sLocators.get(mActivity);
        if (ref != null && ref.get() == this) sLocators.remove(mActivity);
    }

    private void invalidateTerminal(Owner observed, long generation, int reason, Tab tab) {
        if (!VersaniumYouTubePictureInPicturePolicy.passthroughReason(reason)
                || mDestroyed || observed.tab != tab || observed.activity != mActivity
                || observed.documentEpoch != mEpoch || generation != mGeneration) return;
        Owner owner = mOwner;
        if (owner == null) {
            discardTerminalCandidate(observed, generation);
            return;
        }
        if (owner != observed) return;
        // Reserve responsibility before leave callbacks / DOM / UI can synchronously reenter.
        armTerminal(reason, tab, owner.webContents);
        invalidate();
        // Cleanup may unregister the upstream observer during this very dispatch.
        // Route through the same one-shot VIDEO hook even if it will no longer be notified.
        if (mTerminalOwner == owner && mTerminalGeneration == generation) {
            mTerminalDismiss.dismiss(reason, tab, owner.webContents);
        }
    }

    boolean ownsTerminalSource(@Nullable Tab tab, @Nullable WebContents wc) {
        Owner owner = mOwner != null ? mOwner : mTerminalOwner;
        return VersaniumYouTubePictureInPicturePolicy.ENABLED && !mDestroyed && owner != null
                && owner.tab == tab && owner.webContents == wc;
    }

    /** Claim before VIDEO updates candidates or calls external cleanup. No WC API is needed. */
    int claimTerminalDismiss(int reason, @Nullable Tab tab, @Nullable WebContents wc) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || mDestroyed
                || !VersaniumYouTubePictureInPicturePolicy.passthroughReason(reason)) {
            return TERMINAL_UNRELATED;
        }
        Owner candidate = mCandidate;
        if (mOwner == null && candidate != null && candidate.tab == tab
                && candidate.webContents == wc
                && !(mTerminalOwner != null && mTerminalOwner.tab == tab
                        && mTerminalOwner.webContents == wc)) {
            discardTerminalCandidate(candidate, mGeneration);
        }
        armTerminal(reason, tab, wc);
        Owner terminal = mTerminalOwner;
        if (terminal == null || terminal.tab != tab || terminal.webContents != wc
                || terminal.activity != mActivity
                || !(mTerminalGeneration == mGeneration && mOwner == terminal
                        || mOwner == null && mTerminalGeneration == mRetiredGeneration)) {
            return TERMINAL_UNRELATED;
        }
        if (mTerminalConsumed) return TERMINAL_DUPLICATE;
        diagnostic("TERMINAL_CLAIM", "reason=" + reason);
        mTerminalConsumed = true;
        return TERMINAL_CLAIMED;
    }

    boolean drainLeaveCallbacks(List<Runnable> callbacks) {
        if (!VersaniumYouTubePictureInPicturePolicy.ENABLED || !mBlockCurrentMedia) return false;
        List<Runnable> captured = new ArrayList<>(callbacks);
        callbacks.clear();
        for (Runnable callback : captured) callback.run();
        return true;
    }

    private void seedUiOwner(Owner owner) {
        if (mUiTab == null && mFullscreen.getPersistentFullscreenMode()) {
            mUiTab = owner.tab;
            mUiEpoch = owner.documentEpoch;
        }
    }

    private void clearOwnerUi(Owner owner) {
        if (mUiTab != owner.tab || mUiEpoch != owner.documentEpoch) return;
        mUiTab = null;
        mFullscreen.onExitFullscreen(owner.tab);
    }

    private void leaveUpstreamOnce() {
        if (mUpstreamCleanupDone) return;
        mUpstreamCleanupDone = true;
        mLeaveUpstream.run();
    }
}
