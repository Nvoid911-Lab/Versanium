import org.chromium.content_public.browser.*;
import java.util.*;
import java.io.*;
public final class EnvironmentZoomBackupTest {
 static int checks;
 static void check(boolean yes){if(!yes)throw new AssertionError();checks++;}
 static final class Store implements EnvironmentZoomPolicy.Storage {
  Map<String,String> disk=new LinkedHashMap<>();boolean fail;
  public Map<String,String> read(){return new LinkedHashMap<>(disk);}
  public void write(Map<String,String> values){disk=new LinkedHashMap<>(values);}
  public void replace(Map<String,String> values,java.util.function.Consumer<Boolean> done){if(!fail)write(values);done.accept(!fail);}
 }
 static void reject(String json)throws Exception{
  try{EnvironmentZoomBackup.decode(json);throw new AssertionError("Accepted invalid document");}
  catch(IOException|IllegalStateException|NumberFormatException expected){checks++;}
 }
 public static void main(String[] args)throws Exception{
  Store original=new Store();EnvironmentZoomPolicy policy=new EnvironmentZoomPolicy(original,0,Map.of());
  double exact=Math.log(.673456789)/Math.log(1.2);
  policy.setDefault(EnvironmentZoomPolicy.Environment.DEX,exact);
  policy.setSite(EnvironmentZoomPolicy.Environment.MOBILE,"same.test",0);
  policy.setSite(EnvironmentZoomPolicy.Environment.DEX,"same.test",EnvironmentZoomPolicy.factor(80));
  policy.setDisplayMode(987,"dex");
  String json=EnvironmentZoomBackup.encode(policy,"mobile");
  check(!json.contains("987")&&!json.contains("display."));
  EnvironmentZoomBackup backup=EnvironmentZoomBackup.decode(json);
  check(Double.parseDouble(backup.values.get("default.DEX"))==exact);
  Store target=new Store();EnvironmentZoomPolicy restored=new EnvironmentZoomPolicy(target,0,Map.of());
  restored.setSite(EnvironmentZoomPolicy.Environment.MOBILE,"removed.test",0);
  restored.setDisplayMode(17,"dex");
  final boolean[] done={false};
  Object observerOwner=new Object();List<Boolean> states=new ArrayList<>();
  restored.observeTransfer(observerOwner,()->states.add(restored.isReplacing()));
  restored.importSnapshot(backup.values,backup.displayMode,42,success->done[0]=success);
  check(states.equals(List.of(false,true,false)));
  check(done[0]&&!restored.hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"removed.test"));
  check(restored.resolve(EnvironmentZoomPolicy.Environment.MOBILE,"same.test")==0);
  check(restored.resolve(EnvironmentZoomPolicy.Environment.DEX,"same.test")==EnvironmentZoomPolicy.factor(80));
  check(restored.displayMode(42,"auto").equals("mobile")&&restored.displayMode(17,"auto").equals("dex"));
  restored.setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(80));
  restored.setDefault(EnvironmentZoomPolicy.Environment.DEX,EnvironmentZoomPolicy.factor(150));
  check(restored.resolve(EnvironmentZoomPolicy.Environment.DEX,"same.test")==EnvironmentZoomPolicy.factor(80));
  EnvironmentZoomPolicy restarted=new EnvironmentZoomPolicy(target,0,Map.of("do.not.migrate",1.0));
  check(restarted.hasSite(EnvironmentZoomPolicy.Environment.DEX,"same.test")&&!restarted.hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"do.not.migrate"));
  Map<String,String> before=restored.snapshot();target.fail=true;done[0]=true;
  restored.importSnapshot(backup.values,backup.displayMode,66,success->done[0]=success);
  check(!done[0]&&before.equals(restored.snapshot()));
  reject(json.replace("\"version\":1","\"version\":2"));
  reject(json.replace("\"version\":1","\"version\":1,\"version\":1"));
  reject(json.replace("\"default\":0.0","\"default\":null"));
  reject(json.replace("\"default\":0.0","\"default\":\"NaN\""));
  reject(json.replace("\"default\":0.0","\"default\":1e999"));
  reject(json.replace("\"default\":0.0","\"default\":999"));
  reject(json.replace("\"unit\":\"log-base-1.2-exponent\"","\"unit\":\"percent\""));
  reject(json+" {}");reject(json.substring(0,json.length()-1));
  reject(json.replace("\"MOBILE\"","\"OTHER\""));
  reject(" ".repeat(EnvironmentZoomBackup.MAX_BYTES+1));
  reject(json.replace("\"same.test\":0.0","\"same.test\":0.0,\"same.test\":0.0"));
  reject(json.replace("same.test","bad\\ud800"));
  StringBuilder excessive=new StringBuilder();
  for(int i=0;i<EnvironmentZoomBackup.MAX_SITES+1;i++){
    if(i>0)excessive.append(',');excessive.append("\"host").append(i).append("\":0.0");
  }
  reject(json.replace("\"same.test\":0.0",excessive.toString()));
  check(before.equals(restored.snapshot())); // Decode failure/cancel never applies anything.
  System.out.println("EnvironmentZoomBackup: "+checks+" checks PASS (real Android JSON classes; no SAF UI)");
 }
}
