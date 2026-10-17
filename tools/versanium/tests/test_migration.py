"""Local migration checks; synthetic image/template fixtures are NOT the supplied logo or an APK build."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,tempfile,unittest
sys.dont_write_bytecode=True
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
import yaml

REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'tools/versanium'))
import branding,generate_icons,package_apk
spec=importlib.util.spec_from_file_location('assets_apply',REPO/'tools/versanium/apply.py');assets=importlib.util.module_from_spec(spec);spec.loader.exec_module(assets)
spec=importlib.util.spec_from_file_location('identity',REPO/'tools/configure_f11_identity.py');identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)

class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        fixture=Image.new('RGB',(512,512),'black');d=ImageDraw.Draw(fixture);d.rectangle((100,110,190,360),fill='white');d.rectangle((190,290,350,360),fill='white')
        cls.input=cls.root/'synthetic-test-fixture.png';fixture.save(cls.input)
        cls.repo=cls.root/'repo';cls.repo.mkdir();generate_icons.generate(cls.input,cls.repo)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_master_bytes_and_density_dimensions(self):
        self.assertEqual(self.input.read_bytes(),(self.repo/'res/versanium/master.png').read_bytes())
        for density,scale in generate_icons.DENSITIES.items():
            folder=self.repo/'res/versanium/android'/('mipmap-'+density)
            with Image.open(folder/'app_icon.png') as image:self.assertEqual(image.size,(round(48*scale),)*2)
            with Image.open(folder/'layered_app_icon.png') as image:self.assertEqual(image.size,(round(108*scale),)*2)
            with Image.open(folder/'layered_app_icon_background.png') as image:self.assertEqual(image.getpixel((0,0)),(0,0,0,255))
    def test_asset_completeness_and_tamper_detection(self):
        values=assets.check_assets(self.repo);self.assertEqual(len(values['files']),23)
        p=self.repo/'res/versanium/logo.png';old=p.read_bytes();p.write_bytes(b'changed')
        try:
            with self.assertRaises(RuntimeError):assets.check_assets(self.repo)
        finally:p.write_bytes(old)
        manifest=self.repo/'res/versanium/assets.json';old=manifest.read_text();bad=json.loads(old);bad['files']={};manifest.write_text(json.dumps(bad))
        try:
            with self.assertRaises(RuntimeError):assets.check_assets(self.repo)
        finally:manifest.write_text(old)
    def test_missing_master_fails_before_build(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):assets.check_assets(Path(d))
    def test_branding_text_nodes_only_and_japanese(self):
        s='<!-- Copyright Titanium Authors --><message name="IDS_TITANIUM" desc="Titanium implementation">Titaniumを開く<ph name="titanium">Titanium</ph></message>'
        out=branding.brand_resources(s)
        self.assertIn('Versaniumを開く',out);self.assertIn('>Versanium</ph>',out)
        self.assertIn('name="IDS_TITANIUM" desc="Titanium implementation"',out)
        self.assertIn('Copyright Titanium Authors',out)
    def test_upstream_component_and_legal_references_remain(self):
        for s in ['<message name="EXT">Titanium Extension for Android</message>', '<message name="COPYRIGHT">Copyright Titanium Authors</message>', '<message name="LINK">https://github.com/jqssun/android-titanium-browser Titanium</message>']:
            self.assertEqual(branding.brand_resources(s),s)
        self.assertEqual(branding.brand_resources('package app.titanium.config; TitaniumConfParser'), 'package app.titanium.config; TitaniumConfParser')
    def test_adaptive_monochrome_references(self):
        for p in (self.repo/'res/versanium/android').rglob('*.xml'):
            root=ET.parse(p).getroot();self.assertEqual(root.tag,'bitmap')
            self.assertEqual(root.get('{http://schemas.android.com/apk/res/android}src'),'@mipmap/layered_app_icon')
    def test_identity_changes_only_visible_label(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);args=root/'out/Default/args.gn';args.parent.mkdir(parents=True)
            args.write_text((REPO/'args.gn').read_text())
            strings=root/branding.CHANNEL;strings.parent.mkdir(parents=True);strings.write_text('<resources><string name="app_name" translatable="false">Titanium</string></resources>')
            manifest=root/'chrome/android/java/AndroidManifest.xml';manifest.parent.mkdir(parents=True,exist_ok=True)
            original='<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="@string/app_name"><provider android:authorities="{{ manifest_package }}.provider"/></application></manifest>'
            manifest.write_text(original);identity.configure(root)
            self.assertEqual(identity.PACKAGE,'io.github.nvoid911.titanium.f11test')
            self.assertIn('>Versanium</string>',strings.read_text());self.assertEqual(manifest.read_text(),original)
    def test_packaging_bytes_and_only_arm64(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'release';source.mkdir();payload=b'NOT-AN-APK: filename/copy fixture only'
            (source/'155.0.8059.79-arm64-v8a.apk').write_bytes(payload)
            (source/'155.0.8059.79-armeabi-v7a.apk').write_bytes(b'not for release')
            test=package_apk.package(source,root/'test','155.0.8059.79',True)
            prod=package_apk.package(source,root/'production-name-fixture','155.0.8059.79',False)
            self.assertEqual(test.name,'Versanium-155.0.8059.79_Test.apk');self.assertEqual(prod.name,'Versanium-155.0.8059.79_arm64-v8a.apk')
            self.assertEqual(test.read_bytes(),payload);self.assertEqual(prod.read_bytes(),payload)
            with self.assertRaises(ValueError):package_apk.package(source,root/'bad','155.0.8059.39',True)
            with self.assertRaises(ValueError):package_apk.package(source,root/'bad','155.0.8059.79\nINJECT',True)
    def test_workflow_release_guard_and_no_auto_trigger(self):
        w=yaml.load((REPO/'.github/workflows/build.yml').read_text(),Loader=yaml.BaseLoader)
        self.assertEqual(set(w['on']),{'workflow_dispatch'});self.assertEqual(w['name'],'Versanium Build')
        self.assertEqual(w['env']['VERSANIUM_RELEASE_APPROVED'],'false')
        self.assertEqual(w['on']['workflow_dispatch']['inputs']['f11_test_build']['default'],'true')
        self.assertEqual(w['on']['workflow_dispatch']['inputs']['runner']['default'],'blacksmith-8vcpu-ubuntu-2404')
        steps=w['jobs']['build']['steps']
        for step in steps:
            if step.get('name','').startswith(('Publish','Attest','Stage approved')):
                guard=step['if'];self.assertIn('!inputs.f11_test_build',guard);self.assertIn("env.VERSANIUM_RELEASE_APPROVED == 'true'",guard);self.assertIn("github.repository == 'Nvoid911/Versanium'",guard)
        upload=next(s for s in steps if s.get('uses','').startswith('actions/upload-artifact@'))
        self.assertEqual(upload['with']['name'],'Versanium-Test');self.assertTrue(upload['with']['path'].endswith('_Test.apk'))
        preflight=next(s['run'] for s in steps if s.get('name','').startswith('Enforce'))
        env={'PATH':os.environ['PATH'],'TEST_BUILD':'false','VERSANIUM_RELEASE_APPROVED':'false'}
        blocked=subprocess.run(['bash','-c','python3() { return 0; };\n'+preflight],env=env,capture_output=True,text=True)
        self.assertNotEqual(blocked.returncode,0);self.assertIn('Only a test artifact',blocked.stderr)
        env['TEST_BUILD']='true';allowed=subprocess.run(['bash','-c','python3() { return 0; };\n'+preflight],env=env,capture_output=True,text=True)
        self.assertEqual(allowed.returncode,0)  # CLI checks mocked here; real asset check is tested separately.
    def test_inline_shell_and_yaml(self):
        for p in (REPO/'.github/workflows').glob('*.yml'):
            w=yaml.load(p.read_text(),Loader=yaml.BaseLoader)
            for job in w.get('jobs',{}).values():
                for step in job.get('steps',[]):
                    if 'run' in step:
                        import re
                        code=re.sub(r'\$\{\{.*?\}\}','fixture',step['run'])
                        subprocess.run(['bash','-n'],input=code,text=True,check=True)

if __name__=='__main__':unittest.main(verbosity=2)
