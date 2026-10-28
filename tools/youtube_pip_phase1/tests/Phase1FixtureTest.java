// Copyright 2026 Versanium contributors. BSD-style test fixture.
package org.chromium.chrome.browser.media;

import android.app.Activity;
import org.chromium.base.task.PostTask;
import org.chromium.chrome.browser.ChromeTabbedActivity;
import org.chromium.chrome.browser.ActivityTabProvider;
import org.chromium.chrome.browser.fullscreen.FullscreenManager;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.content_public.browser.WebContents;
import org.chromium.ui.base.WindowAndroid;
import static org.chromium.chrome.browser.media.FullscreenVideoPictureInPictureController.MetricsEndReason.*;

/** Runs production source with explicit API doubles; no Android correctness claim. */
public final class Phase1FixtureTest {
    private static int checks;
    private static void check(boolean value, String label) {
        ++checks;
        if (!value) throw new AssertionError(label);
    }
    private static final class Host {
        final ChromeTabbedActivity activity = new ChromeTabbedActivity();
        final ActivityTabProvider tabs = new ActivityTabProvider();
        final FullscreenManager fullscreen = new FullscreenManager();
        final Tab tab = new Tab();
        final WebContents wc = tab.wc;
        int leaves;
        int confirmedEntries;
        final FullscreenVideoPictureInPictureController video = new FullscreenVideoPictureInPictureController();
        final VersaniumYouTubePictureInPictureController controller;
        Host() {
            PostTask.reset();
            tab.window = new WindowAndroid(activity);
            wc.window = tab.window;
            tabs.tab = tab;
            controller = new VersaniumYouTubePictureInPictureController(
                    activity, tabs, fullscreen, () -> { ++leaves; video.leave(); }, this::confirm,
                    (reason, source, contents) -> video.dismiss(activity, reason, source, contents));
            video.mVersaniumPip = controller;
        }
        void confirm() { if (controller.onFrameworkEntered(true)) ++confirmedEntries; }
        long enter() { return controller.beginEntry(tab, true); }
        void active() { enter(); activity.pip = true; check(controller.onFrameworkEntered(true), "first enter");
            video.callbacks.add(() -> {}); }
        boolean hidden() { return VersaniumYouTubePictureInPictureController.preserveOnHidden(
                activity, tab, tab, 1); }
    }
    private static void terminalOrder(int reason, boolean dedicatedFirst, boolean destroyed, boolean reentrant) {
        Host h = new Host(); h.active();
        org.chromium.chrome.browser.tab.TabObserver dedicated = h.tab.observers.get(0);
        Runnable terminal = () -> {
            if (reason == CLOSE) dedicated.onClosingStateChanged(h.tab, true);
            else if (reason == CRASH) dedicated.onCrash(h.tab);
            else dedicated.onActivityAttachmentChanged(h.tab, null);
        };
        if (destroyed) h.wc.destroyed = true;
        // Leave callback reentry occurs after callbacks have been detached, before UI cleanup.
        if (reentrant) {
            h.video.callbacks.add(() -> h.video.dismiss(h.activity, LEFT_FULLSCREEN, h.tab, h.wc));
            h.video.callbacks.add(() -> h.video.dismiss(h.activity, reason, h.tab, h.wc));
        }
        if (dedicatedFirst) { terminal.run(); h.video.dismiss(h.activity, reason, h.tab, h.wc); }
        else { h.video.dismiss(h.activity, reason, h.tab, h.wc); terminal.run(); }
        check(h.video.dismisses == 1 && h.activity.moves == 1, "terminal executes once " + reason);
        check(h.leaves == 1 && h.fullscreen.exits == 1, "controller cleanup once " + reason);
        h.video.dismiss(h.activity, reason, h.tab, h.wc); terminal.run();
        PostTask.advance(3000);
        check(h.video.dismisses == 1 && h.activity.moves == 1 && h.leaves == 1,
                "duplicates and delayed work cannot repeat " + reason);
        check(h.controller.claimTerminalDismiss(reason, h.tab, h.wc)
                == VersaniumYouTubePictureInPictureController.TERMINAL_DUPLICATE, "consume once");
        if (destroyed) check(h.wc.domExits == 0 && h.wc.session.suspends == 0, "dead WC skipped");
        System.out.println("PASS observer order: " + reason + " dedicatedFirst=" + dedicatedFirst
                + " destroyed=" + destroyed + " reentrant=" + reentrant);
    }
    private static void candidateTerminal(int reason, boolean upstreamFirst) {
        Host h = new Host(); h.controller.updateCandidate(h.tab, true);
        org.chromium.chrome.browser.tab.TabObserver observer = h.tab.observers.get(0);
        final int[] delayed = {0};
        Runnable queued = h.controller.guardDelayed(() -> ++delayed[0]);
        Runnable signal = () -> {
            if (reason == CLOSE) observer.onClosingStateChanged(h.tab, true);
            else if (reason == CRASH) observer.onCrash(h.tab);
            else observer.onActivityAttachmentChanged(h.tab, null);
        };
        h.video.update = () -> h.controller.updateCandidate(h.tab, true);
        if (upstreamFirst) h.video.dismiss(h.activity, reason, h.tab, h.wc);
        signal.run(); signal.run(); queued.run();
        if (!upstreamFirst) h.video.dismiss(h.activity, reason, h.tab, h.wc);
        check(h.tab.observers.size() == 1 && !h.tab.observers.contains(observer),
                "candidate terminal replaces authority with recovery observer " + reason);
        check(delayed[0] == 0, "candidate timer revoked " + reason);
        check(h.controller.claimTerminalDismiss(reason, h.tab, h.wc)
                == VersaniumYouTubePictureInPictureController.TERMINAL_UNRELATED, "candidate no token");
        h.controller.updateCandidate(h.tab, true); // Auto update must not resurrect this snapshot.
        h.activity.pip = true;
        check(!h.hidden(), "terminal prevents provisional adoption " + reason);
        h.controller.onFrameworkEntered(false);
        check(!h.controller.ownsMediaRouting() && !h.hidden(), "late framework cannot adopt " + reason);
        PostTask.advance(3000);
        check(h.leaves == 0 && h.wc.domExits == 0 && h.fullscreen.exits == 0
                && h.wc.session.suspends == 0 && h.confirmedEntries == 0
                && h.activity.moves == 0 && h.video.dismisses == 0, "candidate no owner side effects");
        // Same Tab/WC, new candidate generation: old observer must be inert.
        Host newer = new Host(); newer.controller.updateCandidate(newer.tab, true);
        org.chromium.chrome.browser.tab.TabObserver old = newer.tab.observers.get(0);
        newer.controller.updateCandidate(newer.tab, true);
        old.onClosingStateChanged(newer.tab, true); old.onCrash(newer.tab);
        old.onActivityAttachmentChanged(newer.tab, null);
        newer.controller.claimTerminalDismiss(reason, new Tab(), new WebContents());
        newer.activity.pip = true;
        check(newer.hidden(), "stale generation and mismatched source retain candidate");
        // A different document can qualify again after candidate retirement.
        h.activity.pip = false; h.tab.wc = new WebContents(); h.tab.wc.window = h.tab.window;
        h.controller.updateCandidate(h.tab, true); signal.run();
        h.activity.pip = true;
        check(h.hidden(), "old observer cannot clear replacement WC candidate");
        System.out.println("PASS candidate terminal: " + reason + " upstreamFirst=" + upstreamFirst);
    }
    private static void sameContentsRecovery(int mode) {
        Host h = new Host();
        h.controller.updateCandidate(h.tab, true);
        org.chromium.chrome.browser.tab.TabObserver old = h.tab.observers.get(0);
        Runnable delayedTerminal = h.controller.guardDelayed(
                () -> h.video.dismiss(h.activity, CRASH, h.tab, h.wc));
        old.onCrash(h.tab);
        org.chromium.chrome.browser.tab.TabObserver recovery = h.tab.observers.get(0);
        old.onCrash(h.tab); // Duplicate must not replace recovery observation.
        check(h.tab.observers.size() == 1 && h.tab.observers.get(0) == recovery, "duplicate tombstone");
        h.controller.updateCandidate(h.tab, true);
        h.activity.pip = true;
        h.controller.onFrameworkEntered(false);
        check(!h.hidden() && !h.controller.ownsMediaRouting(), "same document late/provisional rejected");
        h.tab.commit(true, h.tab.url + "#fragment");
        h.controller.updateCandidate(h.tab, true);
        check(!h.hidden(), "fragment does not expire tombstone");
        PostTask.advance(100000);
        h.controller.updateCandidate(h.tab, true);
        check(!h.hidden(), "time alone does not expire tombstone");
        if (mode == 0) h.tab.commit(false, h.tab.url); // same URL reload
        else if (mode == 1) h.tab.commit(false, "https://m.youtube.com/watch?v=cross");
        else if (mode == 2) h.tab.commit(true, "https://m.youtube.com/watch?v=DIFFERENT");
        else {
            h.tab.url = "https://m.youtube.com/watch?v=DIFFERENT";
            recovery.onUrlUpdated(h.tab);
        }
        check(h.tab.wc == h.wc && h.tab.observers.isEmpty(), "fresh evidence releases tombstone observer");
        h.controller.updateCandidate(h.tab, true);
        old.onCrash(h.tab); old.onClosingStateChanged(h.tab, true);
        old.onActivityAttachmentChanged(h.tab, null); delayedTerminal.run();
        recovery.onDestroyed(h.tab);
        recovery.onDidFinishNavigationInPrimaryMainFrame(h.tab,
                new org.chromium.content_public.browser.NavigationHandle(false, h.tab.url));
        check(h.hidden(), "same identities recover and stale observers cannot revoke " + mode);
        check(h.leaves == 0 && h.video.dismisses == 0 && h.wc.domExits == 0,
                "recovery has no owner cleanup");
        h.controller.onDestroy();
        check(h.tab.observers.isEmpty(), "recovery lifecycle detaches");
        System.out.println("PASS same-WebContents recovery: " + mode);
    }

    private static void recoveryLifecycle(int mode) {
        Host h = new Host(); h.controller.updateCandidate(h.tab, true);
        h.tab.observers.get(0).onCrash(h.tab);
        org.chromium.chrome.browser.tab.TabObserver recovery = h.tab.observers.get(0);
        recovery.onDidFinishNavigationInPrimaryMainFrame(new Tab(),
                new org.chromium.content_public.browser.NavigationHandle(false, h.tab.url));
        org.chromium.content_public.browser.NavigationHandle pending =
                new org.chromium.content_public.browser.NavigationHandle(false, h.tab.url);
        pending.committed = false;
        recovery.onDidFinishNavigationInPrimaryMainFrame(h.tab, pending);
        h.controller.updateCandidate(h.tab, true); h.activity.pip = true;
        check(!h.hidden(), "wrong tab and uncommitted navigation cannot expire rejection");
        h.activity.pip = false;
        if (mode == 0) h.controller.onDestroy();
        else if (mode == 1) recovery.onDestroyed(h.tab);
        else if (mode == 2) check(h.enter() > 0, "explicit entry retains existing eligibility");
        else if (mode == 3) {
            h.tab.wc = new WebContents(); h.tab.wc.window = h.tab.window;
            recovery.onContentChanged(h.tab);
        } else h.tab.url = "https://m.youtube.com/watch?v=freshWithoutCallback";
        if (mode != 2 && mode != 4) check(h.tab.observers.isEmpty(), "terminal observation released " + mode);
        if (mode >= 3) {
            h.controller.updateCandidate(h.tab, true);
            check(!h.tab.observers.contains(recovery), "fresh capture removes recovery observer");
            h.activity.pip = true;
            check(h.hidden(), "identity/video fresh capture accepted " + mode);
        }
        h.controller.onDestroy();
        check(h.tab.observers.isEmpty(), "all recovery lifecycle observers released");
    }

    private static void passivePageDiagnostics(boolean desktop) {
        Host h = new Host(); h.wc.navigation.desktop = desktop;
        h.controller.diagnosticObserve(h.tab);
        check(h.wc.observers.size() == 1 && h.wc.session.observers.size() == 1,
                "passive page and session observers attached");
        org.chromium.content_public.browser.WebContentsObserver outgoing = h.wc.observers.get(0);
        org.chromium.content_public.browser.MediaSessionObserver media = h.wc.session.observers.get(0);
        outgoing.mediaStartedPlaying(1, true, true);
        media.mediaSessionStateChanged(true, false);
        Tab incoming = new Tab(); incoming.id = 2;
        incoming.window = h.tab.window; incoming.wc.window = h.tab.window;
        incoming.wc.navigation.desktop = desktop;
        h.tabs.tab = incoming;
        h.controller.diagnosticTabEvent("TAB_UNSELECTED", h.tab, "fixture=true");
        h.controller.diagnosticObserve(incoming);
        int afterSwitch = org.chromium.base.Log.lines.size();
        h.wc.visibility = 1; outgoing.onVisibilityChanged(1);
        outgoing.mediaStoppedPlaying(1); media.mediaSessionStateChanged(true, true);
        check(org.chromium.base.Log.lines.subList(afterSwitch, org.chromium.base.Log.lines.size())
                .stream().anyMatch(line -> line.contains("event=MEDIA_SESSION ")
                        && line.contains("desktop_site=" + desktop)
                        && line.contains("retainedOutgoing=true") && line.contains("sessionSuspended=true")),
                "outgoing media state after switch remains observable " + desktop);
        check(org.chromium.base.Log.lines.subList(afterSwitch, org.chromium.base.Log.lines.size())
                .stream().anyMatch(line -> line.contains("event=WC_VISIBILITY ")
                        && line.contains("desktop_site=" + desktop)), "visibility and page mode correlated");
        check(!h.controller.ownsMediaRouting() && h.leaves == 0 && h.wc.domExits == 0
                && h.wc.session.suspends == 0 && h.wc.session.resumes == 0,
                "passive diagnostic cannot adopt, resume or clean owner");
        Tab third = new Tab(); third.id = 3; third.window = h.tab.window; third.wc.window = h.tab.window;
        h.controller.diagnosticObserve(third);
        check(h.wc.observers.isEmpty() && h.wc.session.observers.isEmpty(), "two-page bound evicts oldest");
        int beforeStale = org.chromium.base.Log.lines.size();
        outgoing.mediaStoppedPlaying(1); media.mediaSessionStateChanged(true, true);
        check(org.chromium.base.Log.lines.size() == beforeStale, "stale detached diagnostic callbacks inert");
        third.wc.observers.get(0).webContentsDestroyed();
        check(third.wc.observers.isEmpty() && third.wc.session.observers.isEmpty(),
                "WebContents destruction releases diagnostic observers");
        h.controller.onDestroy();
        check(incoming.wc.observers.isEmpty() && incoming.wc.session.observers.isEmpty()
                && third.wc.observers.isEmpty() && third.wc.session.observers.isEmpty(),
                "host destroy releases both diagnostic pages");
    }

    public static void main(String[] args) {
        passivePageDiagnostics(false); passivePageDiagnostics(true);
        for (int mode = 0; mode < 5; ++mode) recoveryLifecycle(mode);
        for (int mode = 0; mode < 4; ++mode) sameContentsRecovery(mode);
        for (int reason : new int[]{CLOSE, CRASH, REPARENT}) {
            candidateTerminal(reason, false); candidateTerminal(reason, true);
        }
        for (int reason : new int[]{CLOSE, CRASH, REPARENT}) {
            for (boolean first : new boolean[]{true, false}) {
                for (boolean reentrant : new boolean[]{false, true}) {
                    terminalOrder(reason, first, false, reentrant);
                    terminalOrder(reason, first, true, reentrant);
                }
            }
        }
        for (int identity = 0; identity < 3; ++identity) {
            Host fresh = new Host(); fresh.controller.updateCandidate(fresh.tab, true);
            org.chromium.chrome.browser.tab.TabObserver oldObserver = fresh.tab.observers.get(0);
            if (identity == 0) fresh.tab.commit(false, fresh.tab.url);
            else if (identity == 1) {
                fresh.tab.window = new WindowAndroid(fresh.activity);
                fresh.wc.window = fresh.tab.window;
            } else {
                fresh.tabs.tab = new Tab();
                fresh.tabs.tab.window = new WindowAndroid(fresh.activity);
                fresh.tabs.tab.wc.window = fresh.tabs.tab.window;
            }
            Tab source = fresh.tabs.tab;
            fresh.controller.updateCandidate(source, true);
            oldObserver.onClosingStateChanged(fresh.tab, true);
            oldObserver.onCrash(fresh.tab); oldObserver.onActivityAttachmentChanged(fresh.tab, null);
            fresh.controller.claimTerminalDismiss(CLOSE, source, new WebContents());
            fresh.activity.pip = true;
            check(VersaniumYouTubePictureInPictureController.preserveOnHidden(
                    fresh.activity, source, source, 1), "replacement epoch/window/tab survives stale terminal " + identity);
        }
        Host retired = new Host(); retired.active();
        org.chromium.chrome.browser.tab.TabObserver retiredObserver = retired.tab.observers.get(0);
        retiredObserver.onClosingStateChanged(retired.tab, true);
        retired.controller.updateCandidate(retired.tab, true);
        retiredObserver.onCrash(retired.tab);
        check(retired.controller.claimTerminalDismiss(CLOSE, retired.tab, retired.wc)
                == VersaniumYouTubePictureInPictureController.TERMINAL_DUPLICATE,
                "retired owner token remains duplicate without clearing candidate");
        retired.activity.pip = true;
        check(retired.hidden(), "retired token and stale observer cannot discard new candidate");
        Host order = new Host(); order.active();
        order.video.update = () -> order.controller.updateCandidate(null, false);
        order.tabs.tab = new Tab();
        order.video.dismiss(order.activity, CLOSE, order.tab, order.wc);
        check(order.activity.moves == 1 && order.leaves == 1, "claim precedes auto update cleanup");
        Host newTab = new Host(); newTab.active();
        newTab.tabs.tab = new Tab();
        newTab.video.dismiss(newTab.activity, NEW_TAB, null, null);
        check(newTab.activity.moves == 0 && newTab.leaves == 1, "NEW_TAB foreground retained");
        check(newTab.controller.claimTerminalDismiss(NEW_TAB, newTab.tab, newTab.wc)
                == VersaniumYouTubePictureInPictureController.TERMINAL_UNRELATED, "NEW_TAB no token");
        Host stale = new Host(); stale.active();
        Runnable oldTerminal = stale.controller.guardDelayed(
                () -> stale.video.dismiss(stale.activity, CLOSE, stale.tab, stale.wc));
        stale.tab.observers.get(0).onClosingStateChanged(stale.tab, true);
        int previousMoves = stale.activity.moves;
        stale.controller.onNewIntent(); stale.active(); oldTerminal.run();
        check(stale.activity.moves == previousMoves, "stale generation terminal rejected after new entry");
        check(stale.controller.claimTerminalDismiss(CLOSE, new Tab(), new WebContents())
                == VersaniumYouTubePictureInPictureController.TERMINAL_UNRELATED, "wrong owner no token");
        String[] rejected = {"http://m.youtube.com/watch?v=a", "https://www.youtube.com/watch?v=a",
            "https://m.youtube.com.evil/watch?v=a", "https://m.youtube.com/shorts?v=a",
            "https://m.youtube.com/watch", "https://m.youtube.com/watch?v=",
            "https://user@m.youtube.com/watch?v=a", "https://m.youtube.com:444/watch?v=a"};
        for (String url : rejected) {
            Host h = new Host(); h.tab.url = url;
            check(h.enter() == 0, "URL reject " + url); h.controller.onDestroy();
        }
        Host h = new Host();
        check(h.controller.beginEntry(h.tab, false) == 0, "upstream ineligible");
        check(VersaniumYouTubePictureInPicturePolicy.capture(
                new Activity(), h.tab, true, 0) == null, "non-tabbed rejected");
        h.activity.finishing = true; check(h.enter() == 0, "finishing");
        h.activity.finishing = false; h.activity.changing = true; check(h.enter() == 0, "config");
        h.activity.changing = false;
        long g = h.enter(); check(g > 0, "entry"); check(h.enter() == g, "duplicate explicit");
        check(h.hidden(), "valid entering preserves");
        h.controller.rollback(g); check(!h.hidden(), "rollback");
        check(h.wc.domExits == 0 && h.wc.session.suspends == 0, "rollback no teardown");
        check(!h.controller.ownsMediaRouting(), "rollback routing restored");
        h = new Host(); g = h.enter(); h.activity.pip = true;
        check(h.controller.onFrameworkEntered(true), "callback first");
        h.controller.rollback(g); check(h.hidden(), "late rollback cannot clear ACTIVE");
        check(!h.controller.onFrameworkEntered(true), "duplicate true");
        h = new Host(); h.enter(); PostTask.advance(2000); check(!h.hidden(), "orphan rollback");
        check(h.tab.observers.isEmpty(), "orphan observers removed");
        h = new Host(); h.enter(); h.activity.pip = true; PostTask.advance(2000);
        check(h.hidden(), "orphan framework confirmation");
        check(h.confirmedEntries == 1, "orphan confirms upstream entry once");
        check(!h.controller.onFrameworkEntered(true), "late actual callback dedupes timeout confirmation");
        h = new Host(); h.controller.updateCandidate(h.tab, true);
        check(!h.hidden(), "candidate alone does not protect");
        h.activity.pip = true; check(h.hidden(), "candidate framework provisional");
        check(h.controller.onFrameworkEntered(false), "provisional has not claimed upstream");
        check(!h.controller.onFrameworkEntered(false), "provisional duplicate");
        h = new Host(); h.controller.updateCandidate(h.tab, true);
        h.controller.updateCandidate(null, false); h.activity.pip = true;
        check(!h.hidden(), "disabled candidate");
        h = new Host(); h.active();
        check(!VersaniumYouTubePictureInPictureController.preserveOnStopped(
                h.activity, new Activity(), h.tab), "wrong callback activity");
        check(!VersaniumYouTubePictureInPictureController.preserveOnHidden(
                h.activity, new Tab(), h.tab, 1), "wrong tab");
        h.tab.window = new WindowAndroid(h.activity); check(!h.hidden(), "wrong window");
        h = new Host(); h.active(); h.tab.wc = new WebContents(); check(!h.hidden(), "wrong WC");
        h = new Host(); h.active(); h.tab.id = 2; check(!h.hidden(), "wrong tab ID");
        h = new Host(); h.active(); h.tab.commit(false, h.tab.url);
        check(!h.hidden(), "cross document epoch invalidation");
        check(h.wc.session.suspends == 0, "new document not suspended");
        h = new Host(); h.active(); h.tab.commit(true, "https://m.youtube.com/watch?v=two");
        check(!h.hidden(), "same document video change invalidation");
        h = new Host(); h.active(); h.tab.commit(true, "https://m.youtube.com/watch?v=one#fragment");
        check(h.hidden(), "same video fragment retains");
        for (int reason : new int[]{START, RESUME, LEFT_FULLSCREEN, WEB_CONTENTS_LEFT_FULLSCREEN}) {
            h = new Host(); h.active();
            check(h.controller.handleDismiss(reason, h.tab, h.wc), "owner transient " + reason);
            check(h.wc.session.suspends == 0, "transient no suspend");
        }
        for (int reason : new int[]{CLOSE, CRASH, REPARENT}) {
            h = new Host(); h.active();
            check(!h.controller.handleDismiss(reason, h.tab, h.wc), "terminal passthrough " + reason);
            check(h.controller.claimTerminalDismiss(reason, h.tab, h.wc)
                    == VersaniumYouTubePictureInPictureController.TERMINAL_UNRELATED,
                    "unreserved direct cleanup cannot grant terminal");
            check(!h.hidden(), "terminal protection removed");
        }
        h = new Host(); h.active();
        check(!h.controller.handleDismiss(LEFT_FULLSCREEN, new Tab(), new WebContents()), "wrong source not suppressed");
        h = new Host(); h.active(); Tab incoming = new Tab(); h.tabs.tab = incoming;
        check(h.controller.handleDismiss(NEW_TAB, null, null), "new tab dedicated path");
        check(h.wc.session.suspends == 1 && incoming.wc.session.suspends == 0, "only old owner stopped");
        check(h.controller.ownerMediaSession() == null && h.controller.ownsMediaRouting(), "no media fallback tombstone");
        h = new Host(); h.active(); h.tab.hide(0); check(!h.hidden(), "switch hidden cleanup");
        check(h.fullscreen.last == h.tab, "owner UI argument");
        h = new Host(); h.active(); h.activity.pip = false; h.controller.beginFrameworkExit();
        check(!h.hidden(), "false protection off immediately");
        h.controller.onResume(); PostTask.advance(1000);
        check(h.wc.session.suspends == 0 && h.leaves == 1, "expand preserve playback cleanup once");
        h = new Host(); h.active(); h.activity.pip = false; h.controller.beginFrameworkExit();
        h.activity.state = 5; h.controller.onStop(); PostTask.advance(1500);
        check(h.wc.session.suspends == 1 && h.leaves == 1, "close stop once");
        h = new Host(); h.active(); h.activity.pip = false; h.activity.state = 5;
        h.controller.beginFrameworkExit(); PostTask.advance(1000);
        check(h.wc.session.suspends == 1 && h.leaves == 1, "close fallback");
        h = new Host(); h.active(); h.wc.synchronousExit = true; h.activity.pip = false;
        h.controller.beginFrameworkExit(); h.controller.onResume(); PostTask.advance(2000);
        check(h.leaves == 1 && h.wc.domExits == 1 && h.wc.observers.isEmpty(), "DOM/fallback single claim");
        h = new Host(); h.active(); final int[] calls = {0};
        Runnable old = h.controller.guardDelayed(() -> ++calls[0]);
        h.controller.onNewIntent(); h.activity.pip = false; h.enter(); old.run();
        check(calls[0] == 0, "old generation callback");
        h = new Host(); final int[] currentCalls = {0};
        Runnable unowned = h.controller.guardDelayed(() -> ++currentCalls[0]);
        h.tabs.tab = new Tab(); unowned.run(); check(currentCalls[0] == 0, "unowned old tab deferred callback");
        h = new Host(); h.active(); h.activity.changing = true; h.controller.onDestroy();
        check(h.wc.session.suspends == 1 && h.tab.observers.isEmpty(), "config destroy cleanup");
        check(h.wc.session.resumes == 0, "never entry resume");
        h = new Host(); h.active(); h.activity.pip = false; h.controller.beginFrameworkExit();
        h.controller.onDestroy(); check(h.leaves == 1, "destroy during EXITING leaves once");
        h = new Host(); h.active(); Tab other = new Tab(); h.fullscreen.enter(other);
        h.controller.onNewIntent(); check(h.fullscreen.exits == 0, "new tab UI not cleared");
        h = new Host(); h.active(); h.tab.commit(false, h.tab.url);
        h.fullscreen.enter(h.tab); PostTask.advance(3000);
        check(h.fullscreen.exits == 1, "old fallback cannot clear later document UI");
        h = new Host(); h.active();
        java.util.List<Runnable> callbacks = new java.util.ArrayList<>();
        final Host captured = h;
        callbacks.add(() -> check(callbacks.isEmpty(), "detached before reentrant callback"));
        check(captured.controller.drainLeaveCallbacks(callbacks), "owned callback drain");
        check(callbacks.isEmpty(), "callbacks drained");
        h = new Host(); h.controller.updateCandidate(h.tab, true);
        h.tab.commit(false, h.tab.url); h.activity.pip = true;
        check(!h.hidden(), "auto candidate navigation invalidated");
        h = new Host(); h.active();
        check(!VersaniumYouTubePictureInPictureController.preserveOnHidden(
                h.activity, h.tab, h.tab, 99), "unknown hidden fails closed");
        h = new Host(); h.active(); h.activity.state = 5; h.controller.onStop();
        check(h.wc.session.suspends == 1, "screen lock follows ordinary stop");
        h = new Host(); h.active(); h.activity.pip = false; h.controller.beginFrameworkExit();
        h.activity.state = 3; PostTask.advance(1000);
        check(h.wc.session.suspends == 0, "already resumed fallback expands");
        h = new Host(); h.active(); h.wc.destroyed = true; h.controller.onDestroy();
        check(h.wc.domExits == 0 && h.wc.session.suspends == 0, "destroyed WC APIs skipped");
        check(h.fullscreen.observers.isEmpty(), "host listener released");
        check(org.chromium.base.Log.lines.stream().allMatch(line -> line.startsWith("VersaniumPiP VSPIP event=")),
                "diagnostic tag and format");
        for (String event : new String[]{"POLICY", "INIT", "OWNER_ADOPT", "STATE", "GENERATION",
                "ENTRY_REQUESTED", "ENTRY_SUPPRESSED", "ENTRY_ABORTED", "FRAMEWORK_ENTERED",
                "CLEANUP", "EXIT", "TERMINAL_ARM", "TERMINAL_CLAIM", "CANDIDATE_TERMINAL"}) {
            check(org.chromium.base.Log.lines.stream().anyMatch(line -> line.contains("event=" + event + " ")),
                    "diagnostic observation " + event);
        }
        for (String reason : new String[]{"non_https", "wrong_host", "wrong_path", "missing_video_id",
                "unsupported_activity", "upstream_ineligible", "activity_finishing", "configuration_change",
                "eligible"}) {
            check(org.chromium.base.Log.lines.stream().anyMatch(line -> line.contains("reason=" + reason)),
                    "diagnostic policy reason " + reason);
        }
        check(org.chromium.base.Log.lines.stream().noneMatch(line -> line.contains("watch?v=")
                || line.contains("videoId=one")), "diagnostics omit full URL and video IDs");
        System.out.println("PASS: " + checks + " actual-source fixture assertions");
    }
}
