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
    public static void main(String[] args){
        BrowserContextHandle normal=new BrowserContextHandle();
        Activity phone=new Activity(0),dex=new Activity(2);
        WebContents m=tab(phone,normal),d=tab(dex,normal);
        pct(m.rendered,100);pct(d.rendered,67);
        EnvironmentZoom.save(m,m.host,EnvironmentZoomPolicy.factor(100));
        EnvironmentZoom.save(d,d.host,EnvironmentZoomPolicy.factor(80));
        pct(m.rendered,100);pct(d.rendered,80);
        EnvironmentZoom.store(normal).setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(80));
        EnvironmentZoom.refreshAll();
        EnvironmentZoom.store(normal).setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(67));
        EnvironmentZoom.refreshAll();pct(d.rendered,80);
        // Move only this Activity, including back to a display that was already connected.
        phone.moveTo(2);pct(m.rendered,80);pct(d.rendered,80);
        phone.moveTo(0);pct(m.rendered,100);pct(d.rendered,80);
        EnvironmentZoom.reset(d);pct(d.rendered,67);pct(m.rendered,100);
        // Destroy/recreate the activity; binding reuses persisted profile maps, not a last-display global.
        m.destroyed=true;WebContents replacement=tab(new Activity(0),normal);pct(replacement.rendered,100);
        d.host="other.test";EnvironmentZoom.refreshAll();pct(d.rendered,67);
        BrowserContextHandle privateProfile=new BrowserContextHandle();privateProfile.privateProfile=true;
        WebContents secret=tab(new Activity(2),privateProfile);
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
        EnvironmentZoom.forgetContext(normal);
        BrowserContextHandle restarted=new BrowserContextHandle();
        WebContents afterRestart=tab(new Activity(0),restarted);pct(afterRestart.rendered,100);
        check(EnvironmentZoom.store(restarted).hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"pending.test"));
        System.out.println("EnvironmentZoomBridge: "+checks+" assertions passed with MOCK Android/JNI renderer");
    }
}
