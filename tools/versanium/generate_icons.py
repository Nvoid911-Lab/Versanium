"""Deterministic format conversion of the supplied master; never generate/redesign a logo.
Usage: python tools/versanium/generate_icons.py /path/to/original.png
"""
from pathlib import Path
import argparse,base64,hashlib,io,json,math,shutil
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageOps

REPO=Path(__file__).resolve().parents[2]
BASE=Path('res/versanium')
DENSITIES={'mdpi':1,'hdpi':1.5,'xhdpi':2,'xxhdpi':3,'xxxhdpi':4}
XML='''<?xml version="1.0" encoding="utf-8"?>
<!-- Resource wiring derived from Chromium. Copyright 2022 The Chromium Authors.
Use of this source code is governed by a BSD-style license in LICENSE. -->
<bitmap xmlns:android="http://schemas.android.com/apk/res/android"
    android:src="@mipmap/layered_app_icon" android:gravity="fill" android:filter="true" />
'''

def generate(master,repo=REPO,font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')):
    raw=master.read_bytes()
    source=Image.open(io.BytesIO(raw))
    if source.format!='PNG' or source.width!=source.height or source.width<512:
        raise ValueError('Provide the original square PNG, at least 512px; no replacement/generated logo is accepted')
    image=source.convert('RGBA')
    # White artwork on black: luminance becomes alpha. On black this retains the design.
    alpha=ImageChops.multiply(ImageOps.grayscale(image),image.getchannel('A'))
    box=alpha.getbbox()
    if not box:raise ValueError('No artwork found in the supplied master')
    ink=Image.new('RGBA',image.size,'white');ink.putalpha(alpha);ink=ink.crop(box)
    a=ink.getchannel('A');px=a.load();cx,cy=(ink.width-1)/2,(ink.height-1)/2
    radius=max(math.hypot(x-cx,y-cy) for y in range(ink.height) for x in range(ink.width) if px[x,y])
    # Entire artwork fits inside the adaptive icon's 66dp circular safe zone.
    factor=32/max(radius,1)
    paths=[]
    def save(relative,data):
        p=repo/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);paths.append(str(relative))
    def png(relative,img):
        b=io.BytesIO();img.save(b,format='PNG');save(relative,b.getvalue())
    save(BASE/'master.png',raw)  # Byte-for-byte source preservation.
    for density,scale in DENSITIES.items():
        folder=BASE/'android'/('mipmap-'+density)
        png(folder/'app_icon.png',image.resize((round(48*scale),)*2,Image.Resampling.LANCZOS))
        foreground=Image.new('RGBA',(round(108*scale),)*2)
        glyph=ink.resize((max(1,round(ink.width*factor*scale)),max(1,round(ink.height*factor*scale))),Image.Resampling.LANCZOS)
        foreground.alpha_composite(glyph,((foreground.width-glyph.width)//2,(foreground.height-glyph.height)//2))
        png(folder/'layered_app_icon.png',foreground)
        png(folder/'layered_app_icon_background.png',Image.new('RGBA',foreground.size,'black'))
    save(BASE/'android/mipmap-nodpi/layered_app_icon_foreground.xml',XML.encode())
    save(BASE/'android/drawable/themed_app_icon.xml',XML.encode())
    logo=image.resize((512,512),Image.Resampling.LANCZOS)
    png(BASE/'logo.png',logo)
    png(Path('fastlane/metadata/android/en-US/images/icon.png'),logo)
    for relative,size in [(BASE/'social-preview.png',(1280,640)),(Path('fastlane/metadata/android/en-US/images/featureGraphic.png'),(1024,500))]:
        canvas=Image.new('RGB',size,'black');art_size=round(size[1]*.82)
        canvas.paste(image.resize((art_size,art_size),Image.Resampling.LANCZOS),(32,(size[1]-art_size)//2))
        draw=ImageDraw.Draw(canvas);x=art_size+64;y=size[1]//2-55
        draw.text((x,y),'Versanium',font=ImageFont.truetype(str(font_path),round(size[0]*.05)),fill='white')
        draw.text((x,y+90),'Android browsing across\nmobile and desktop environments',font=ImageFont.truetype(str(font_path),round(size[0]*.016)),fill='white')
        png(relative,canvas)
    data=base64.b64encode(raw).decode()
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640"><rect width="1280" height="640" fill="black"/><image x="32" y="58" width="525" height="525" href="data:image/png;base64,{data}"/><text x="589" y="315" fill="white" font-family="sans-serif" font-size="64">Versanium</text><text x="589" y="390" fill="white" font-family="sans-serif" font-size="20">Android browsing across</text><text x="589" y="418" fill="white" font-family="sans-serif" font-size="20">mobile and desktop environments</text></svg>'''
    save(BASE/'social-preview.svg',svg.encode())
    manifest={'master_sha256':hashlib.sha256(raw).hexdigest(),'files':{p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in paths}}
    target=repo/BASE/'assets.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared assets from unchanged supplied master:',len(paths))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('master',type=Path);a=p.parse_args();generate(a.master)
