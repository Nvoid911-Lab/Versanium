import java.util.*;
import org.chromium.content_public.browser.EnvironmentZoomPersistence;
public final class EnvironmentZoomPersistenceTest {
 static int checks;
 static void check(boolean value){if(!value)throw new AssertionError();checks++;}
 static final class Dispatch implements EnvironmentZoomPersistence.Dispatch {
  Map<Runnable,Integer> delayed=new LinkedHashMap<>();Queue<Runnable> worker=new ArrayDeque<>(),main=new ArrayDeque<>();int errors;
  public void later(Runnable task,int delay){delayed.put(task,delay);}
  public void cancel(Runnable task){delayed.remove(task);}
  public void background(Runnable task){worker.add(task);}
  public void main(Runnable task){main.add(task);}
  public void failure(){errors++;}
  void launch(){List<Runnable> tasks=new ArrayList<>(delayed.keySet());delayed.clear();tasks.forEach(Runnable::run);}
  void complete(){worker.remove().run();main.remove().run();}
 }
 public static void main(String[] args){
  Dispatch d=new Dispatch();List<Map<String,String>> disk=new ArrayList<>();boolean[] fail={false};
  EnvironmentZoomPersistence p=new EnvironmentZoomPersistence(Map.of(),value->{
   if(fail[0])return false;disk.add(new LinkedHashMap<>(value));return true;
  },d);
  for(int i=0;i<1000;i++)p.write(Map.of("zoom",Integer.toString(i),"version","1"));
  check(d.delayed.size()==1 && disk.isEmpty());check(p.read().get("zoom").equals("999"));
  d.launch();check(d.worker.size()==1 && disk.isEmpty());
  p.write(Map.of("zoom","newer"));check(d.worker.size()==1);d.complete();check(disk.get(0).get("zoom").equals("999"));
  d.launch();d.complete();check(disk.get(1).get("zoom").equals("newer") && !p.hasPendingWrite());
  fail[0]=true;p.write(Map.of("zoom","failed"));p.flush();check(disk.size()==2);d.complete();
  check(p.hasFailure() && p.hasPendingWrite() && d.errors==1);
  p.write(Map.of("zoom","latest"));d.launch();d.complete();d.launch();d.complete();d.launch();d.complete();
  check(d.delayed.isEmpty() && p.hasPendingWrite());check(d.errors==2);
  fail[0]=false;p.flush();d.complete();check(disk.get(2).get("zoom").equals("latest"));
  check(!p.hasPendingWrite() && !p.hasFailure());
  Dispatch exceptionDispatch=new Dispatch();EnvironmentZoomPersistence exception=new EnvironmentZoomPersistence(Map.of(),values->{throw new IllegalStateException();},exceptionDispatch);
  exception.write(Map.of("keep","pending"));exception.flush();exceptionDispatch.complete();
  check(exception.hasFailure() && exception.read().get("keep").equals("pending"));
  boolean[] replaced={false};
  p.replace(Map.of("zoom","imported"),ok->replaced[0]=ok);
  check(!replaced[0]&&p.read().get("zoom").equals("latest"));
  d.complete();check(replaced[0]&&p.read().get("zoom").equals("imported"));
  fail[0]=true;replaced[0]=true;p.replace(Map.of("zoom","rejected"),ok->replaced[0]=ok);
  d.complete();check(!replaced[0]&&p.read().get("zoom").equals("imported"));
  p.write(Map.of("zoom","pending"));replaced[0]=true;
  p.replace(Map.of("zoom","must.not.race"),ok->replaced[0]=ok);
  check(!replaced[0]&&p.read().get("zoom").equals("pending"));
  System.out.println("EnvironmentZoomPersistence: "+checks+" checks PASS (1000 changes coalesced; serial writes, failures and retry)");
 }
}
