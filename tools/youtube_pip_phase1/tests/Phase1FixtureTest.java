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
        final VersaniumYouTubePictureInPictureController controller;
        Host() {
            PostTask.reset();
            tab.window = new WindowAndroid(activity);
            wc.window = tab.window;
            tabs.tab = tab;
            controller = new VersaniumYouTubePictureInPictureController(
                    activity, tabs, fullscreen, () -> ++leaves, this::confirm);
        }
        void confirm() { if (controller.onFrameworkEntered(true)) ++confirmedEntries; }
        long enter() { return controller.beginEntry(tab, true); }
        void active() { enter(); activity.pip = true; check(controller.onFrameworkEntered(true), "first enter"); }
        boolean hidden() { return VersaniumYouTubePictureInPictureController.preserveOnHidden(
                activity, tab, tab, 1); }
    }
    public static void main(String[] args) {
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
            check(h.controller.requiresUpstreamDismiss(reason), "terminal upstream retained");
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
        System.out.println("PASS: " + checks + " actual-source fixture assertions");
    }
}
