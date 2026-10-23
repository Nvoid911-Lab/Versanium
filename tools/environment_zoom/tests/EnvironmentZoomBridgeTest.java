// Tests the production bridge with the explicit API doubles in run_local_tests.py.
import android.app.Activity;
import android.content.Preferences;
import org.chromium.content_public.browser.*;
import org.chromium.ui.base.WindowAndroid;
import java.util.Map;

public final class EnvironmentZoomBridgeTest {
    static int checks;
    static void pct(double factor,int percent) {
        if(Math.abs(Math.pow(1.2,factor)-percent/100.0)>1e-10) throw new AssertionError(factor+" != "+percent);
        checks++;
    }
    static void check(boolean value){if(!value)throw new AssertionError();checks++;}
    static WebContents tab(Activity activity,BrowserContextHandle profile){
        WebContents c=new WebContents();c.window=new WindowAndroid(activity);EnvironmentZoom.attach(c,profile);return c;
    }
    static void settle() throws Exception {
        EnvironmentZoom.flushPendingWrites();
        long limit=System.nanoTime()+5_000_000_000L;
        do {
            android.os.Handler.drain();
            if(!EnvironmentZoom.hasPendingWrites())return;
            Thread.sleep(5);
        }while(System.nanoTime()<limit);
        throw new AssertionError("Persistence did not complete");
    }
    public static void main(String[] args) throws Exception {
        BrowserContextHandle normal=new BrowserContextHandle();
        Activity phone=new Activity(0),dex=new Activity(2);
        WebContents m=tab(phone,normal),d=tab(dex,normal);
        pct(m.rendered,100);pct(d.rendered,67);
        EnvironmentZoom.save(m,m.host,EnvironmentZoomPolicy.factor(100));
        EnvironmentZoom.save(d,d.host,EnvironmentZoomPolicy.factor(80));
        android.os.Handler.drain();
        pct(m.rendered,100);pct(d.rendered,80);
        EnvironmentZoom.store(normal).setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(80));
        EnvironmentZoom.refreshAll();
        EnvironmentZoom.store(normal).setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(67));
        EnvironmentZoom.refreshAll();pct(d.rendered,80);
        // Move only this Activity, including back to a display that was already connected.
        phone.moveTo(2);android.os.Handler.drain();pct(m.rendered,80);pct(d.rendered,80);
        phone.moveTo(0);android.os.Handler.drain();pct(m.rendered,100);pct(d.rendered,80);
        EnvironmentZoom.reset(d);android.os.Handler.drain();pct(d.rendered,67);pct(m.rendered,100);
        m.window=null;
        pct(EnvironmentZoom.rendered(m,m.host),100);
        check(EnvironmentZoom.save(m,m.host,EnvironmentZoomPolicy.factor(90)));
        pct(EnvironmentZoom.resolve(m,m.host),90);
        m.window=new WindowAndroid(phone);
        EnvironmentZoom.save(m,m.host,EnvironmentZoomPolicy.factor(100));
        android.os.Handler.drain();
        // Destroy/recreate the activity; binding reuses persisted profile maps, not a last-display global.
        m.destroyed=true;
        check(Double.isNaN(EnvironmentZoom.resolve(m,m.host)));
        WebContents replacement=tab(new Activity(0),normal);pct(replacement.rendered,100);
        d.host="other.test";EnvironmentZoom.refreshAll();pct(d.rendered,67);
        EnvironmentZoom.store(normal).setSite(EnvironmentZoomPolicy.Environment.MOBILE,"pending-private-inherit.test",EnvironmentZoomPolicy.factor(85));
        BrowserContextHandle privateProfile=new BrowserContextHandle();privateProfile.privateProfile=true;
        WebContents secret=tab(new Activity(2),privateProfile);
        check(EnvironmentZoom.store(privateProfile).hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"pending-private-inherit.test"));
        settle();
        Preferences file=Preferences.get("titanium_environment_zoom_Default");
        Map<String,?> disk=file.getAll();int writes=file.writes;
        EnvironmentZoom.save(secret,"private.test",EnvironmentZoomPolicy.factor(90));
        secret.host="private.test";EnvironmentZoom.refreshAll();pct(secret.rendered,90);
        check(file.writes==writes && file.getAll().equals(disk));
        check(!EnvironmentZoom.store(normal).hasSite(EnvironmentZoomPolicy.Environment.DEX,"private.test"));
        EnvironmentZoom.forgetContext(privateProfile);
        check(Double.isNaN(EnvironmentZoom.resolve(secret,"private.test")));
        BrowserContextHandle nextPrivate=new BrowserContextHandle();nextPrivate.privateProfile=true;
        check(!EnvironmentZoom.store(nextPrivate).hasSite(EnvironmentZoomPolicy.Environment.DEX,"private.test"));
        // Native callbacks can ask for a pending RFH host independently of the Java visible URL.
        EnvironmentZoom.save(replacement,"pending.test",EnvironmentZoomPolicy.factor(75));
        pct(EnvironmentZoom.rendered(replacement,"pending.test"),75);pct(replacement.rendered,100);
        EnvironmentZoom.setDisplayMode(dex,"mobile");pct(d.rendered,100);
        EnvironmentZoom.setDisplayMode(dex,"auto");pct(d.rendered,67);
        settle();
        EnvironmentZoom.forgetContext(normal);
        BrowserContextHandle restarted=new BrowserContextHandle();
        WebContents afterRestart=tab(new Activity(0),restarted);pct(afterRestart.rendered,100);
        check(EnvironmentZoom.store(restarted).hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"pending.test"));
        settle();
        check(EnvironmentZoom.save(secret,"retired.test",EnvironmentZoomPolicy.factor(90)));
        check(!EnvironmentZoom.store(restarted).hasSite(EnvironmentZoomPolicy.Environment.DEX,"retired.test"));
        WebContents importedDisplay=tab(dex,restarted);
        EnvironmentZoom.store(restarted).setDisplayMode(dex.displayId,"mobile");
        EnvironmentZoom.refreshAll();
        check(EnvironmentZoom.displayMode(dex,EnvironmentZoom.store(restarted)).equals("mobile"));
        check(!EnvironmentZoom.isMobileDisplay(importedDisplay)); // Zoom override must not make DeX a phone.
        settle();
        Map<String,String> imported=new java.util.LinkedHashMap<>(EnvironmentZoom.store(restarted).snapshot());
        imported.put("default.MOBILE",Double.toString(EnvironmentZoomPolicy.factor(110)));
        final boolean[] importedDone={false};
        EnvironmentZoom.importSnapshot(restarted,imported,"dex",42,ok->importedDone[0]=ok);
        check(EnvironmentZoom.store(restarted).isReplacing());
        EnvironmentZoom.forgetContext(restarted);
        BrowserContextHandle recreatedDuringImport=new BrowserContextHandle();
        EnvironmentZoomPolicy during=EnvironmentZoom.store(recreatedDuringImport);
        check(during.isReplacing());
        during.setSite(EnvironmentZoomPolicy.Environment.MOBILE,"must.not.write.during.import",0);
        check(!during.hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"must.not.write.during.import"));
        settle();check(importedDone[0]&&!during.isReplacing());
        pct(during.defaultFactor(EnvironmentZoomPolicy.Environment.MOBILE),110);
        check(during.displayMode(42,"auto").equals("dex"));
        System.out.println("EnvironmentZoomBridge: "+checks+" assertions passed with MOCK Android/JNI renderer");
    }
}
