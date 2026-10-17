// Copyright 2026 Titanium contributors. SPDX-License-Identifier: BSD-3-Clause
import org.chromium.content_public.browser.EnvironmentZoomPolicy;
import org.chromium.content_public.browser.EnvironmentZoomPolicy.Environment;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class EnvironmentZoomPolicyTest {
    private static int checks;
    static final class Disk implements EnvironmentZoomPolicy.Storage {
        final Path path;
        int writes;
        Disk(Path path) { this.path = path; }
        public Map<String,String> read() {
            Properties p = new Properties();
            if (Files.exists(path)) try (InputStream in = Files.newInputStream(path)) { p.load(in); }
            catch (IOException e) { throw new UncheckedIOException(e); }
            Map<String,String> result = new LinkedHashMap<>();
            for (String k : p.stringPropertyNames()) result.put(k,p.getProperty(k));
            return result;
        }
        public void write(Map<String,String> values) {
            Properties p = new Properties();p.putAll(values);
            try (OutputStream out = Files.newOutputStream(path)) { p.store(out,"test fixture"); }
            catch (IOException e) { throw new UncheckedIOException(e); }
            writes++;
        }
    }
    static final class Memory implements EnvironmentZoomPolicy.Storage {
        Map<String,String> values;
        Memory(Map<String,String> seed) { values = new LinkedHashMap<>(seed); }
        public Map<String,String> read() { return new LinkedHashMap<>(values); }
        public void write(Map<String,String> updated) { values = new LinkedHashMap<>(updated); }
    }
    static void equal(double a,double b) { if (Math.abs(a-b)>1e-12) throw new AssertionError(a+" != "+b); checks++; }
    static void check(boolean ok) { if(!ok)throw new AssertionError();checks++; }
    static double f(int pct) { return EnvironmentZoomPolicy.factor(pct); }
    public static void main(String[] args) throws Exception {
        Path dir=Files.createTempDirectory("titanium-zoom-test");
        try {
            Disk disk=new Disk(dir.resolve("regular.properties"));
            EnvironmentZoomPolicy p=new EnvironmentZoomPolicy(disk,0,Map.of());
            equal(p.defaultFactor(Environment.MOBILE),f(100));equal(p.defaultFactor(Environment.DEX),f(67));
            equal(Math.pow(1.2,f(67)),.67);check(EnvironmentZoomPolicy.percent(f(67))==67);
            p.setSite(Environment.MOBILE,"youtube.com",f(100));p.setSite(Environment.DEX,"youtube.com",f(80));
            equal(p.resolve(Environment.MOBILE,"youtube.com"),f(100));equal(p.resolve(Environment.DEX,"youtube.com"),f(80));
            p.setDefault(Environment.DEX,f(80));check(p.hasSite(Environment.DEX,"youtube.com"));
            p.setDefault(Environment.DEX,f(67));equal(p.resolve(Environment.DEX,"youtube.com"),f(80));
            p.setDefault(Environment.MOBILE,f(125));equal(p.resolve(Environment.MOBILE,"youtube.com"),f(100));
            // UI 100 == default still means explicit until Reset.
            p.setDefault(Environment.MOBILE,f(100));p.setSite(Environment.MOBILE,"same.test",f(100));
            p.setDefault(Environment.MOBILE,f(150));equal(p.resolve(Environment.MOBILE,"same.test"),f(100));
            p.resetSite(Environment.DEX,"youtube.com");equal(p.resolve(Environment.DEX,"youtube.com"),f(67));
            equal(p.resolve(Environment.MOBILE,"youtube.com"),f(100));
            int writes=disk.writes;
            EnvironmentZoomPolicy restarted=new EnvironmentZoomPolicy(disk,f(300),Map.of("bad-migration.test",f(250)));
            check(disk.writes==writes);equal(restarted.resolve(Environment.MOBILE,"youtube.com"),f(100));
            equal(restarted.defaultFactor(Environment.DEX),f(67));check(!restarted.hasSite(Environment.DEX,"bad-migration.test"));
            // Two simultaneously visible pages resolve against one store without changing defaults.
            for(int i=0;i<100;i++) {
                equal(restarted.resolve(Environment.MOBILE,"youtube.com"),f(100));
                equal(restarted.resolve(Environment.DEX,"youtube.com"),f(67));
            }
            byte[] before=Files.readAllBytes(disk.path);
            EnvironmentZoomPolicy privateSession=new EnvironmentZoomPolicy(new Memory(restarted.snapshot()),0,Map.of());
            privateSession.setSite(Environment.MOBILE,"private.test",f(90));
            privateSession.setDefault(Environment.DEX,f(120));privateSession.resetSite(Environment.MOBILE,"youtube.com");
            check(Arrays.equals(before,Files.readAllBytes(disk.path)));check(!restarted.hasSite(Environment.MOBILE,"private.test"));
            equal(restarted.resolve(Environment.MOBILE,"youtube.com"),f(100));equal(restarted.defaultFactor(Environment.DEX),f(67));
            EnvironmentZoomPolicy newPrivate=new EnvironmentZoomPolicy(new Memory(restarted.snapshot()),0,Map.of());
            check(!newPrivate.hasSite(Environment.MOBILE,"private.test"));
            Map<String,Double> old=new LinkedHashMap<>();old.put("example.com",-1.22);old.put("www.example.com",f(80));
            Disk importedDisk=new Disk(dir.resolve("imported.properties"));
            EnvironmentZoomPolicy imported=new EnvironmentZoomPolicy(importedDisk,f(125),old);
            equal(imported.defaultFactor(Environment.MOBILE),f(125));equal(imported.defaultFactor(Environment.DEX),f(125));
            equal(imported.resolve(Environment.MOBILE,"example.com"),-1.22);equal(imported.resolve(Environment.DEX,"www.example.com"),f(80));
            imported.setSite(Environment.MOBILE,"example.com",f(90));equal(imported.resolve(Environment.DEX,"example.com"),-1.22);
            imported.resetSite(Environment.MOBILE,"www.example.com");equal(imported.resolve(Environment.DEX,"www.example.com"),f(80));
            check(old.size()==2 && old.get("example.com")==-1.22);
            EnvironmentZoomPolicy dataWithDefault100=new EnvironmentZoomPolicy(new Memory(Map.of()),0,old);
            equal(dataWithDefault100.defaultFactor(Environment.DEX),f(100));
            EnvironmentZoomPolicy explicitlySaved100 = new EnvironmentZoomPolicy(new Memory(Map.of()),0,Map.of(),true);
            equal(explicitlySaved100.defaultFactor(Environment.DEX),f(100));
            for(int pct=50;pct<=300;pct++)check(EnvironmentZoomPolicy.percent(f(pct))==pct);
            System.out.println("EnvironmentZoomPolicy: "+checks+" assertions passed (real file roundtrip and migration; no Android renderer)");
        } finally {
            try(var paths=Files.walk(dir)){ paths.sorted(Comparator.reverseOrder()).forEach(p->{try{Files.delete(p);}catch(IOException e){throw new UncheckedIOException(e);}}); }
        }
    }
}
