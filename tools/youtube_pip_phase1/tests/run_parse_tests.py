"""Parse actual composed Chromium source plus overlays; no dependency resolution."""
from pathlib import Path
import argparse
import subprocess
import tempfile
from test_bundle import BundleTest, BUNDLE

def run(jdk):
    with tempfile.TemporaryDirectory(prefix='versanium-pip-parse-') as d:
        root=Path(d);test=BundleTest();test.fixture(root);test.installer().apply(root)
        classes=root/'parser';classes.mkdir()
        subprocess.run([str(jdk/'bin/javac.exe'),'-d',str(classes),
                        str(BUNDLE/'tests/ParseJavaSources.java')],check=True)
        java=sorted((root/'chrome').rglob('*.java'))
        subprocess.run([str(jdk/'bin/java.exe'),'-cp',str(classes),'ParseJavaSources',
                        *map(str,java)],check=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--jdk',required=True,type=Path)
    run(p.parse_args().jdk)
