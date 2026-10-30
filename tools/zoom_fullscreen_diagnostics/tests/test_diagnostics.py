"""Actual composed source, installer and normalized-evidence tests; not Chromium compilation."""
import copy
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import unittest

B=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
installer=load('zoomfs_apply',B/'apply.py')
correlation=load('zoomfs_correlation',B/'correlation.py')
M=json.loads((B/'tests/fixtures/manifest.json').read_text())
BLOCK=re.compile(r'^// VSZOOMFS_DIAGNOSTIC_BEGIN\n.*?^// VSZOOMFS_DIAGNOSTIC_END\n',re.M|re.S)
def baseline():
    return {p:gzip.decompress((B/'tests/fixtures'/e['fixture']).read_bytes()) for p,e in M['files'].items()}
def fixture(root):
    for p,data in baseline().items():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
def composed(root):
    fixture(root);installer.apply(root,True)
    return {p:(root/p).read_text(encoding='utf-8') for p in M['files']}
def method(text,signature):
    start=text.index(signature);opening=text.index('{',start);depth=1;i=opening+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]

class Overlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        cls.sources=composed(cls.root)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_exact_native_behavior_and_existing_pip_bytes(self):
        for p,b in baseline().items():
            self.assertEqual(hashlib.sha256(b).hexdigest(),M['files'][p]['before_sha256'])
            if p.endswith('.cc'):
                self.assertEqual(BLOCK.sub('',self.sources[p]),b.decode(),p)
                pip=re.compile(r'// VSPIP_DIAGNOSTIC_BEGIN.*?// VSPIP_DIAGNOSTIC_END',re.S)
                self.assertEqual(pip.findall(self.sources[p]),pip.findall(b.decode()))
    def test_java_calculation_exact_inverse(self):
        p=next(p for p in self.sources if p.endswith('.java'));inverse=M['java_inverse']
        restored=self.sources[p].replace(inverse['helper'],'').replace(inverse['new'],inverse['old'])
        restored=restored.replace('import org.chromium.content_public.browser.RenderFrameHost;\n','').replace('import org.chromium.content_public.browser.GlobalRenderFrameHostId;\n','')
        self.assertEqual(restored,baseline()[p].decode())
        self.assertEqual(self.sources[p].count('binding.policy.resolve(binding.lastEnvironment, host)'),baseline()[p].decode().count('binding.policy.resolve(binding.lastEnvironment, host)'))
    def test_full_selector_contains_early_return_before_correction(self):
        source=self.sources['content/browser/web_contents/web_contents_impl.cc']
        f=method(source,'double WebContentsImpl::GetPendingZoomLevel(')
        branch=f.split('if (!pending_entry) {',1)[1].split('url = pending_entry->GetURL();',1)[0]
        self.assertIn('pending=0 reason=no_pending',branch)
        self.assertIn('return HostZoomMap::GetZoomLevel(this, rfh->GetGlobalId());',branch)
        self.assertLess(f.index('reason=no_pending'),f.index('FULLSCREEN_CORRECTION_SELECTED'))
        self.assertNotIn('return 0.0',branch)
    def test_actual_send_and_adoption_order(self):
        rh=self.sources['content/browser/renderer_host/render_widget_host_impl.cc']
        self.assertLess(rh.index('blink_widget_->UpdateVisualProperties(*visual_properties);'),rh.index('"VISUAL_PROPERTIES_SEND"'))
        ww=self.sources['third_party/blink/renderer/core/frame/web_frame_widget_impl.cc']
        self.assertLess(ww.index('"VISUAL_PROPERTIES_RECEIVED"'),ww.index('  SetZoomInternal(visual_properties.zoom_level,'))
        self.assertLess(ww.index('local_frame->SetLayoutZoomFactor(layout_zoom_factor);'),ww.index('"RENDERER_ZOOM_ADOPTED"'))
        self.assertIn('grant_stored_before=',ww);self.assertIn('grant_received=',ww)
    def test_gated_bounded_and_no_unsafe_pip_getter(self):
        for p,s in self.sources.items():
            if p.endswith('.cc') and 'void VSZoomLog' in s:
                helper=s.split('void VSZoomLog',1)[1].split('// VSZOOMFS_DIAGNOSTIC_END',1)[0]
                self.assertLess(helper.index('if (!VSZoomEnabled()) return;'),helper.index('static thread_local'))
                self.assertIn('std::array<Entry, 32>',helper);self.assertIn('changes > 64',helper)
            for block in BLOCK.findall(s):
                for forbidden in ('IsPictureInPictureAllowedForFullscreenVideo(', 'SetTemporaryZoomLevel(',
                                  'SetEnvironmentZoomLevel(', 'UpdateZoom();','UpdateAllLifecyclePhases',
                                  'GetDocumentToken(', 'GetZoomLevel(this'):
                    self.assertNotIn(forbidden,block)
    def test_pipeline_order_registration_and_gate_forwarding(self):
        script=(B.parents[1]/'patch.sh').read_text(encoding='utf-8')
        self.assertLess(script.index('tools/versanium/apply.py'),script.index('tools/zoom_fullscreen_diagnostics/apply.py'))
        self.assertEqual(len(M['files']),8)
        self.assertFalse(any(p.endswith(('.gn','.gni')) for p in M['files']))
        cli=self.sources['chrome/browser/chrome_content_browser_client.cc']
        self.assertIn('command_line->AppendSwitch("versanium-zoom-fullscreen-diagnostics")',cli)
        java=self.sources[next(p for p in self.sources if p.endswith('.java'))]
        self.assertLess(java.index('if (vsZoomDiagnosticsEnabled()) vsZoomState'),java.index('private static final class VSZoomStore'))
    def test_apply_idempotent_and_read_only(self):
        before={p:(self.root/p).read_bytes() for p in M['files']}
        self.assertEqual(installer.apply(self.root,True),'already_applied')
        self.assertEqual(before,{p:(self.root/p).read_bytes() for p in M['files']})
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);fixture(r);self.assertEqual(installer.apply(r),'verified_not_applied')
            self.assertEqual(installer.verify(r),'before')
    def test_drift_and_partial_refused_before_writes(self):
        for partial in (False,True):
            with tempfile.TemporaryDirectory() as d:
                r=Path(d);fixture(r);p=next(iter(M['files']))
                (r/p).write_text(self.sources[p] if partial else 'drift',encoding='utf-8',newline='\n')
                before={p:(r/p).read_bytes() for p in M['files']}
                with self.assertRaises(RuntimeError):installer.apply(r,True)
                self.assertEqual(before,{p:(r/p).read_bytes() for p in M['files']})

def records(zoom=0,selected=False):
    keys=dict(trial='phone50_repeat1',wc='7:8',frame='frame-token',document='doc-token',widget='7:9',grant=4)
    sequence=[]
    if selected:sequence.append(dict(keys,event='FULLSCREEN_CORRECTION_SELECTED',selected_exp=0))
    for event in ('VISUAL_PROPERTIES_SEND','VISUAL_PROPERTIES_RECEIVED','RENDERER_ZOOM_ADOPTED'):
        sequence.append(dict(keys,event=event,zoom_exp=zoom))
    box=dict(w=1080,h=600,unit='root_paint_px',space='paint-root')
    sequence.append(dict(keys,event='FULLSCREEN_LAYOUT',valid=True,video=box,viewport=box.copy()))
    return sequence

class Evidence(unittest.TestCase):
    def test_50_100_200_not_a_product_fix(self):
        for pct in (50,100,200):
            zoom=math.log(pct/100)/math.log(1.2);rs=records(zoom)
            self.assertTrue(correlation.validate_chain(rs)['transport_and_adoption'])
            self.assertFalse(correlation.validate_chain(rs)['correction_applied'])
            self.assertEqual(rs[0]['zoom_exp'],zoom)
            self.assertEqual(correlation.geometry_ratio(dict(w=pct*10,h=pct*6,unit='css_px',space='document'),dict(w=1000,h=600,unit='css_px',space='document')),(pct/100,pct/100))
    def test_zero_is_not_correction(self):
        self.assertFalse(correlation.validate_chain(records())['correction_applied'])
        self.assertTrue(correlation.validate_chain(records(selected=True))['correction_applied'])
        rs=records(selected=True);rs[-1]['valid']=False
        self.assertFalse(correlation.validate_chain(rs)['correction_applied'])
    def test_identity_fail_closed(self):
        for k in correlation.IDENTITY:
            for value in (None,'unknown','other'):
                rs=records();rs[1][k]=value
                with self.assertRaises(ValueError):correlation.validate_chain(rs)
    def test_missing_mismatch_order_and_ambiguity(self):
        for i in range(3):
            rs=records();rs.pop(i)
            with self.assertRaises(ValueError):correlation.validate_chain(rs)
        rs=records();rs[1]['zoom_exp']=5
        with self.assertRaises(ValueError):correlation.validate_chain(rs)
        rs=records();rs[0],rs[1]=rs[1],rs[0]
        with self.assertRaises(ValueError):correlation.validate_chain(rs)
        rs=records(selected=True);rs.insert(1,dict(rs[0],event='FULLSCREEN_CORRECTION_SKIP'))
        with self.assertRaises(ValueError):correlation.validate_chain(rs)
        rs=records(5,selected=True)
        with self.assertRaises(ValueError):correlation.validate_chain(rs)
        rs=records(selected=True);rs[0].pop('selected_exp')
        with self.assertRaises(ValueError):correlation.validate_chain(rs)
    def test_coordinates_and_invalid_geometry_rejected(self):
        base=dict(w=100,h=100,unit='css_px',space='document')
        for changes in (dict(unit='dip'),dict(unit='device_px'),dict(space='other'),dict(space=None),dict(w=0),dict(h=float('nan'))):
            with self.assertRaises(ValueError):correlation.geometry_ratio(base,dict(base,**changes))

if __name__=='__main__':unittest.main()
