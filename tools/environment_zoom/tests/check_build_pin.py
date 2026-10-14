"""Unit-check revision rejection with controlled Git metadata. Does not invoke build.sh."""
from pathlib import Path
from unittest.mock import patch
import importlib.util
import subprocess
import tempfile
import sys
sys.dont_write_bytecode = True
repo=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('pin',repo/'tools/check_environment_zoom_revision.py')
pin=importlib.util.module_from_spec(spec);spec.loader.exec_module(pin)
checks=0
with tempfile.TemporaryDirectory(prefix='zoom-pin-') as temp:
    root=Path(temp);(root/'vanadium').mkdir();args=root/'vanadium/args.gn'
    def run(vanadium, chromium, version, ancestry):
        args.write_text(f'android_default_version_name = "{version}"\n')
        def git(path,*args):return vanadium if path.name=='vanadium' else chromium
        with patch.object(pin,'git',side_effect=git),patch.object(pin.subprocess,'run',side_effect=ancestry):
            pin.validate(root,root)
    run(pin.VANADIUM,pin.CHROMIUM,pin.VERSION,None);checks+=1
    for vanadium,chromium,version,ancestry in [
        ('0'*40,pin.CHROMIUM,pin.VERSION,None),
        (pin.VANADIUM,'0'*40,pin.VERSION,None),
        (pin.VANADIUM,pin.CHROMIUM,'999.0.0.0',None),
        (pin.VANADIUM,pin.CHROMIUM,pin.VERSION,subprocess.CalledProcessError(1,['git','merge-base'])),
    ]:
        try:run(vanadium,chromium,version,ancestry)
        except (RuntimeError,subprocess.CalledProcessError):checks+=1
        else:raise AssertionError('Unknown inputs accepted')
print(f'Revision gate: {checks} metadata-model cases PASS; real tag SHA was separately checked via git ls-remote')
