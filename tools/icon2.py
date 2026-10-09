#!/usr/bin/env python3
"""Generate launcher icons for the DSH app from the official black-whale SVG."""
import io
import os

import cairosvg
from PIL import Image, ImageDraw

SVG = '/opt/dshstage/node_modules/@deepseek-ai/dsh-web-frontend/dist/favicon.svg'
OUT = '/var/minis/workspace/dshport/app/res'

png = cairosvg.svg2png(url=SVG, output_width=1024, output_height=1024)
whale = Image.open(io.BytesIO(png)).convert('RGBA')
bbox = whale.getbbox()
whale = whale.crop(bbox)
print('whale rendered:', whale.size)


def fit(img, size):
    w, h = img.size
    s = min(size / w, size / h)
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    img2 = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    canvas.paste(img2, ((size - nw) // 2, (size - nh) // 2), img2)
    return canvas


def legacy(px, rounded=True):
    c = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    if rounded:
        d.rounded_rectangle([0, 0, px - 1, px - 1], radius=max(2, int(px * 0.1875)),
                            fill=(255, 255, 255, 255))
    else:
        d.ellipse([0, 0, px - 1, px - 1], fill=(255, 255, 255, 255))
    w = fit(whale, int(px * 0.53))
    c.paste(w, ((px - w.size[0]) // 2, (px - w.size[1]) // 2), w)
    return c


legacy_dens = {
    'mipmap-mdpi': 48, 'mipmap-hdpi': 72, 'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144, 'mipmap-xxxhdpi': 192,
}
for folder, px in legacy_dens.items():
    p = os.path.join(OUT, folder)
    os.makedirs(p, exist_ok=True)
    legacy(px).save(os.path.join(p, 'ic_launcher.png'))
    legacy(px, rounded=False).save(os.path.join(p, 'ic_launcher_round.png'))

fg_dens = {
    'mipmap-mdpi': 108, 'mipmap-hdpi': 162, 'mipmap-xhdpi': 216,
    'mipmap-xxhdpi': 324, 'mipmap-xxxhdpi': 432,
}
for folder, px in fg_dens.items():
    p = os.path.join(OUT, folder)
    fit(whale, int(px * 0.46)).save(os.path.join(p, 'ic_launcher_fg.png'))

os.makedirs('/var/minis/workspace/dshport/out', exist_ok=True)
legacy(512).save('/var/minis/workspace/dshport/out/icon_preview.png')
print('icons written to', OUT)
