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
    def test_jpeg_original_preserved_and_png_converted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);original=root/'original.jpg'
            Image.open(self.input).convert('RGB').save(original,format='JPEG')
            output=root/'output';output.mkdir();generate_icons.generate(original,output)
            self.assertEqual(original.read_bytes(),(output/'res/versanium/master-original.jpg').read_bytes())
            with Image.open(output/'res/versanium/master.png') as converted:self.assertEqual(converted.format,'PNG')
            self.assertEqual(len(assets.check_assets(output)['files']),24)

    def test_missing_master_fails_before_build(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):assets.check_assets(Path(d))
    def test_branding_text_nodes_only_and_japanese(self):
        s='<!-- Copyright Titanium Authors --><message name="IDS_TITANIUM" desc="Titanium implementation">Titaniumを開く<ph name="titanium">Titanium</ph></message>'
        out=branding.brand_resources(s)
        self.assertIn('Versaniumを開く',out);self.assertIn('>Versanium</ph>',out)
        self.assertIn('name="IDS_TITANIUM" desc="Titanium implementation"',out)
        self.assertIn('Copyright Titanium Authors',out)
        mixed=branding.brand_resources('<message name="HELP">Titanium uses Titanium Extension for Android. See https://support.example/Titanium/help</message>')
        self.assertIn('Versanium uses Titanium Extension for Android',mixed)
        self.assertIn('https://support.example/Titanium/help',mixed)
    def test_upstream_component_and_legal_references_remain(self):
        for s in ['<message name="EXT">Titanium Extension for Android</message>', '<message name="COPYRIGHT">Copyright Titanium Authors</message>', '<message name="LINK">https://github.com/jqssun/android-titanium-browser Titanium</message>']:
            self.assertEqual(branding.brand_resources(s),s)
        self.assertEqual(branding.brand_resources('package app.titanium.config; TitaniumConfParser'), 'package app.titanium.config; TitaniumConfParser')
    def test_adaptive_monochrome_references(self):
        for p in (self.repo/'res/versanium/android').rglob('*.xml'):
            root=ET.parse(p).getroot();self.assertEqual(root.tag,'bitmap')
            self.assertEqual(root.get('{http://schemas.android.com/apk/res/android}src'),'@mipmap/layered_app_icon')
    def test_test_identity_isolation_and_legacy_default(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);args=root/'out/Default/args.gn';args.parent.mkdir(parents=True)
            args.write_text((REPO/'args.gn').read_text())
            strings=root/branding.CHANNEL;strings.parent.mkdir(parents=True);strings.write_text('<resources><string name="app_name" translatable="false">Titanium</string></resources>')
            manifest=root/'chrome/android/java/AndroidManifest.xml';manifest.parent.mkdir(parents=True,exist_ok=True)
            original='<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="@string/app_name"><provider android:authorities="{{ manifest_package }}.provider"/></application></manifest>'
            manifest.write_text(original);identity.configure(root)
            self.assertEqual(identity.PACKAGE,'io.github.nvoid911.titanium.f11test')
            self.assertIn('>Versanium</string>',strings.read_text());self.assertEqual(manifest.read_text(),original)
            self.assertIn('chrome_public_manifest_package = "io.github.nvoid911.titanium.f11test"',args.read_text())
            identity.configure(root,versanium_test=True)
            self.assertIn('chrome_public_manifest_package = "io.github.nvoid911.versanium.test"',args.read_text())
            self.assertEqual(manifest.read_text(),original)
            self.assertIn('>Versanium</string>',strings.read_text())
            for bad in ('<permission android:name="io.github.nvoid911.titanium.f11test.PRIVATE"/>', '<activity android:taskAffinity="shared.task"/>'):
                manifest.write_text(original.replace('</application>',bad+'</application>'))
                before=args.read_bytes()
                with self.assertRaises(ValueError):identity.configure(root,versanium_test=True)
                self.assertEqual(before,args.read_bytes())
    def test_build_identity_selector_without_running_build_script(self):
        import re
        script=(REPO/'build.sh').read_text()
        block=re.search(r'    identity_options=\(\).*?python3[^\n]+(?= \|\| \{)',script,re.S).group()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);args=root/'out/Default/args.gn';args.parent.mkdir(parents=True)
            strings=root/branding.CHANNEL;strings.parent.mkdir(parents=True)
            manifest=root/'chrome/android/java/AndroidManifest.xml'
            manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="@string/app_name"><provider android:authorities="{{ manifest_package }}.provider"/></application></manifest>')
            for selected,package in [('1',identity.VERSANIUM_TEST_PACKAGE),('0',identity.PACKAGE),(None,identity.PACKAGE)]:
                args.write_text((REPO/'args.gn').read_text())
                strings.write_text('<resources><string name="app_name">Versanium</string></resources>')
                env=dict(os.environ,SCRIPT_DIR=str(REPO));env.pop('VERSANIUM_TEST_BUILD',None)
                if selected is not None:env['VERSANIUM_TEST_BUILD']=selected
                subprocess.run(['bash','-e','-c',block],cwd=root,env=env,check=True,capture_output=True,text=True)
                self.assertIn('chrome_public_manifest_package = "'+package+'"',args.read_text())

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
        inputs=w['on']['workflow_dispatch']['inputs']
        self.assertEqual(inputs['f11_test_build']['default'],'true')
        self.assertEqual(inputs['runner_provider']['type'],'choice')
        self.assertEqual(inputs['runner_provider']['default'],'blacksmith')
        self.assertEqual(inputs['runner_provider']['options'],['blacksmith','sengi','ideapad'])
        self.assertNotIn('runner',inputs)
        steps=w['jobs']['build']['steps']
        build=next(s for s in steps if s.get('name')=='Build')
        self.assertEqual(build['env']['F11_TEST_BUILD'],'1')  # Existing F11 compilation/signing mode is retained.
        self.assertEqual(build['env']['VERSANIUM_TEST_BUILD'],"${{ inputs.f11_test_build && '1' || '0' }}")
        self.assertEqual(build['env']['LOCAL_TEST_JKS'],'${{ secrets.LOCAL_TEST_JKS }}')
        self.assertEqual(build['env']['STORE_TEST_JKS'],'${{ secrets.STORE_TEST_JKS }}')
        expected_guard="${{ !inputs.f11_test_build && env.VERSANIUM_RELEASE_APPROVED == 'true' && github.repository == 'Nvoid911-Lab/Versanium' }}"
        for step in steps:
            if step.get('name','').startswith(('Publish','Attest','Stage approved')):
                self.assertEqual(step['if'],expected_guard)
                guard=step['if'];self.assertIn('!inputs.f11_test_build',guard);self.assertIn("env.VERSANIUM_RELEASE_APPROVED == 'true'",guard);self.assertIn("github.repository == 'Nvoid911-Lab/Versanium'",guard)
        upload=next(s for s in steps if s.get('uses','').startswith('actions/upload-artifact@'))
        self.assertEqual(upload['with']['name'],'Versanium-Test');self.assertTrue(upload['with']['path'].endswith('_Test.apk'))
        preflight=next(s['run'] for s in steps if s.get('name','').startswith('Enforce'))
        env={'PATH':os.environ['PATH'],'TEST_BUILD':'false','VERSANIUM_RELEASE_APPROVED':'false'}
        blocked=subprocess.run(['bash','-c','python3() { return 0; };\n'+preflight],env=env,capture_output=True,text=True)
        self.assertNotEqual(blocked.returncode,0);self.assertIn('Only a test artifact',blocked.stderr)
        env['TEST_BUILD']='true';allowed=subprocess.run(['bash','-c','python3() { return 0; };\n'+preflight],env=env,capture_output=True,text=True)
        self.assertEqual(allowed.returncode,0)  # CLI checks mocked here; real asset check is tested separately.
    def test_runner_provider_map_and_repository_allocation_guard(self):
        import re
        w=yaml.load((REPO/'.github/workflows/build.yml').read_text(),Loader=yaml.BaseLoader)
        job=w['jobs']['build']
        match=re.fullmatch(r"\$\{\{ fromJSON\('([^']+)'\)\[inputs\.runner_provider\] \|\| 'versanium-runner-not-allowed' \}\}",job['runs-on'])
        self.assertIsNotNone(match)
        mapping=json.loads(match.group(1))
        self.assertEqual(mapping,{'blacksmith':'blacksmith-8vcpu-ubuntu-2404','sengi':'sengi-standard-8-ubuntu-2404','ideapad':'versanium-ideapad'})
        guard=job['if'];self.assertTrue(guard.startswith('${{ ') and guard.endswith(' }}'))
        atoms=guard[4:-3].split(' || ')
        allowed=[]
        for atom in atoms:
            part=re.fullmatch(r"github.repository == '([^']+)'",atom)
            self.assertIsNotNone(part);allowed.append(part.group(1))
        self.assertEqual(set(allowed),{'Nvoid911-Lab/Versanium','Nvoid911/Versanium'})
        self.assertEqual(mapping['blacksmith'],'blacksmith-8vcpu-ubuntu-2404')
        self.assertEqual(mapping['sengi'],'sengi-standard-8-ubuntu-2404')
        self.assertEqual(mapping['ideapad'],'versanium-ideapad')
        self.assertIn('[inputs.runner_provider]',job['runs-on'])
        self.assertNotIn('[inputs.runner]',job['runs-on'])

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
