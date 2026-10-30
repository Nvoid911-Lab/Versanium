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
  check(EnvironmentZoomBackup.decode(json.replace("\"default\":0.0","\"default\":999")).values.get("default.MOBILE").equals("999.0"));
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
  Properties persisted=new Properties();
  try(Reader reader=new FileReader(args[0],java.nio.charset.StandardCharsets.UTF_8)){persisted.load(reader);}
  Store fixtureStore=new Store();
  for(String key:persisted.stringPropertyNames())fixtureStore.disk.put(key,persisted.getProperty(key));
  EnvironmentZoomPolicy fixture=new EnvironmentZoomPolicy(fixtureStore,0,Map.of("must.not.migrate",1.0));
  EnvironmentZoomBackup fixtureCopy=EnvironmentZoomBackup.decode(EnvironmentZoomBackup.encode(fixture,"auto"));
  fixtureCopy.validateForRestore();
  Store fixtureDestination=new Store();EnvironmentZoomPolicy fixtureRestored=new EnvironmentZoomPolicy(fixtureDestination,0,Map.of());
  fixtureRestored.importSnapshot(fixtureCopy.values,"auto",0,success->check(success));
  EnvironmentZoomPolicy fixtureReopened=new EnvironmentZoomPolicy(fixtureDestination,0,Map.of());
  for(String key:persisted.stringPropertyNames()) {
   if(key.equals("version"))check(fixtureReopened.snapshot().get(key).equals("1"));
   else check(Double.doubleToRawLongBits(Double.parseDouble(persisted.getProperty(key)))==Double.doubleToRawLongBits(Double.parseDouble(fixtureReopened.snapshot().get(key))));
  }
  check(!fixtureReopened.hasSite(EnvironmentZoomPolicy.Environment.MOBILE,"must.not.migrate"));
  // Real pre-migration input path and existing v1 storage keys, not a slider test double.
  // No device/profile data was collected: these are deterministic legacy zoom examples.
  Map<String,Double> legacy=new LinkedHashMap<>();
  legacy.put("small.test",Math.log(.25)/Math.log(1.2));
  legacy.put("large.test",Math.log(4.0)/Math.log(1.2));
  legacy.put("fractional.test",Math.log(.333333333333)/Math.log(1.2));
  Store legacyStore=new Store();
  double legacyDefault=Math.log(4.5)/Math.log(1.2);
  EnvironmentZoomPolicy migrated=new EnvironmentZoomPolicy(legacyStore,legacyDefault,legacy,true);
  EnvironmentZoomBackup legacyBackup=EnvironmentZoomBackup.decode(EnvironmentZoomBackup.encode(migrated,"auto"));
  legacyBackup.validateForRestore();check(true);
  Store importedStore=new Store();EnvironmentZoomPolicy imported=new EnvironmentZoomPolicy(importedStore,0,Map.of());
  imported.importSnapshot(legacyBackup.values,"auto",0,success->check(success));
  EnvironmentZoomPolicy legacyRestart=new EnvironmentZoomPolicy(importedStore,0,Map.of("must.not.remigrate",2.0));
  for(var env:EnvironmentZoomPolicy.Environment.values()) {
   check(Double.doubleToRawLongBits(legacyRestart.defaultFactor(env))==Double.doubleToRawLongBits(legacyDefault));
   for(var entry:legacy.entrySet()) check(Double.doubleToRawLongBits(legacyRestart.resolve(env,entry.getKey()))==Double.doubleToRawLongBits(entry.getValue()));
   check(!legacyRestart.hasSite(env,"must.not.remigrate"));
  }
  for(double value:new double[]{-Double.MAX_VALUE,Double.MAX_VALUE,Double.MIN_VALUE,-999,999,-0.0}) {
   migrated.setDefault(EnvironmentZoomPolicy.Environment.MOBILE,value);
   migrated.setSite(EnvironmentZoomPolicy.Environment.DEX,"finite.test",value);
   EnvironmentZoomBackup copy=EnvironmentZoomBackup.decode(EnvironmentZoomBackup.encode(migrated,"dex"));
   check(Double.doubleToRawLongBits(Double.parseDouble(copy.values.get("default.MOBILE")))==Double.doubleToRawLongBits(value));
   check(Double.doubleToRawLongBits(Double.parseDouble(copy.values.get("site.DEX.finite.test")))==Double.doubleToRawLongBits(value));
  }
  try {EnvironmentZoomBackup.decode(EnvironmentZoomBackup.encode(migrated,"auto")).validateForRestore();check(true);}
  catch(IOException error){throw new AssertionError("Negative zero must restore",error);}
  for(double unsafe:new double[]{-Double.MAX_VALUE,Double.MAX_VALUE,-9999,9999}) {
   migrated.setDefault(EnvironmentZoomPolicy.Environment.MOBILE,unsafe);
   EnvironmentZoomBackup archive=EnvironmentZoomBackup.decode(EnvironmentZoomBackup.encode(migrated,"auto"));
   try {archive.validateForRestore();throw new AssertionError("Unsafe restore accepted");}
   catch(IOException expected){checks++;}
   check(Double.parseDouble(archive.values.get("default.MOBILE"))==unsafe);
  }
  check(EnvironmentZoomBackup.describeDefault(Double.toString(Double.MAX_VALUE)).equals("1.2^"+Double.MAX_VALUE));
  System.out.println("EnvironmentZoomBackup: "+checks+" checks PASS (real Android JSON classes; no SAF UI)");
 }
}
