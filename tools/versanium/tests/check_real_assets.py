"""Validate the committed real attachment and Android exports, not a synthetic fixture.
Does not inflate Android UI, link an APK, or run a renderer.
"""
from pathlib import Path
import base64,math,sys,xml.etree.ElementTree as ET
from PIL import Image
sys.dont_write_bytecode=True
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'tools/versanium'))
from apply import check_assets
from generate_icons import DENSITIES

values=check_assets(REPO)
base=REPO/'res/versanium'
with Image.open(base/'master-original.jpg') as original, Image.open(base/'master.png') as converted:
    assert original.format=='JPEG' and converted.format=='PNG'
    assert original.size==converted.size==(1280,1280)
    assert original.convert('RGBA').tobytes()==converted.convert('RGBA').tobytes()
for relative in values['files']:
    path=REPO/relative
    if path.suffix=='.png':
        with Image.open(path) as image:image.verify()
    elif path.suffix=='.xml':ET.parse(path)
for density,scale in DENSITIES.items():
    folder=base/'android'/('mipmap-'+density)
    with Image.open(folder/'app_icon.png') as image:assert image.size==(round(48*scale),)*2
    with Image.open(folder/'layered_app_icon_background.png') as image:
        assert image.size==(round(108*scale),)*2
        assert image.convert('RGBA').getextrema()==((0,0),(0,0),(0,0),(255,255))
    with Image.open(folder/'layered_app_icon.png') as image:
        assert image.size==(round(108*scale),)*2
        alpha=image.getchannel('A');center=(image.width-1)/2
        radius=max(math.hypot(x-center,y-center) for y in range(image.height) for x in range(image.width) if alpha.getpixel((x,y))>16)
        assert radius/scale<=33,(density,radius/scale)
        for pixel in (image.getpixel((x,y)) for y in range(image.height) for x in range(image.width)):
            if pixel[3]>16:assert min(pixel[:3])>=250  # White monochrome artwork.
for path in (base/'android').rglob('*.xml'):
    node=ET.parse(path).getroot()
    assert node.tag=='bitmap'
    assert node.get('{http://schemas.android.com/apk/res/android}src')=='@mipmap/layered_app_icon'
for name,size in [('icon.png',(512,512)),('featureGraphic.png',(1024,500))]:
    with Image.open(REPO/'fastlane/metadata/android/en-US/images'/name) as image:assert image.size==size
svg=ET.parse(base/'social-preview.svg').getroot()
embedded=svg.find('{http://www.w3.org/2000/svg}image').get('href')
assert embedded.startswith('data:image/png;base64,')
assert base64.b64decode(embedded.split(',',1)[1])==(base/'master.png').read_bytes()
print('Real attachment decoded-pixel identity, 24 hashes, 5 densities, adaptive circular safe zone, monochrome references, fastlane dimensions and SVG embedded master PASS')
