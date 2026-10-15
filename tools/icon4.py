#!/usr/bin/env python3
"""Launcher icons for the DSH port — v0.2.2.

Fix vs icon3.py: the adaptive foreground / monochrome layers must be a FULL
108dp canvas with the whale centred and padded. icon3.py saved a tight crop
of the whale as the layer instead, and launchers stretch that layer to the
whole 108dp canvas — so the whale rendered ~1.5x too large and was clipped
by the launcher mask. (It also explains why shrinking 0.46 -> 0.42 changed
nothing: the crop was normalised away on device.)

Layout rules used here:
  adaptive foreground/mono : 108dp canvas, whale width = FG_FRAC of it
                             (0.44 => ~66% of the 72dp visible area,
                              matching the official DeepSeek icon)
  legacy ic_launcher       : full-bleed rounded square, whale = LEGACY_FRAC
"""
import io
import os

import cairosvg
from PIL import Image, ImageDraw

SVG_DARK = '/opt/dshstage/node_modules/@deepseek-ai/dsh-web-frontend/dist/favicon-dark.svg'
OUT = '/var/minis/workspace/dshport/app/res'
BG = (11, 13, 18, 255)  # #0B0D12 — same as the app dark theme

FG_FRAC = 0.42       # whale width as a fraction of the 108dp canvas
LEGACY_FRAC = 0.58   # whale width as a fraction of a legacy full-bleed icon

png = cairosvg.svg2png(url=SVG_DARK, output_width=1024, output_height=1024)
whale = Image.open(io.BytesIO(png)).convert('RGBA')
whale = whale.crop(whale.getbbox())
print('whale source:', whale.size, 'aspect %.3f' % (whale.size[0] / whale.size[1]))


def fit(img, size):
    w, h = img.size
    s = min(size / w, size / h)
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    img2 = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    canvas.paste(img2, ((size - nw) // 2, (size - nh) // 2), img2)
    return canvas


def layer(px, frac):
    """Full px*px transparent canvas with the whale centred at `frac`."""
    c = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    w = fit(whale, max(1, int(px * frac)))
    c.paste(w, ((px - w.size[0]) // 2, (px - w.size[1]) // 2), w)
    return c


def legacy(px, rounded=True):
    c = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    if rounded:
        d.rounded_rectangle([0, 0, px - 1, px - 1], radius=max(2, int(px * 0.1875)), fill=BG)
    else:
        d.ellipse([0, 0, px - 1, px - 1], fill=BG)
    w = fit(whale, max(1, int(px * LEGACY_FRAC)))
    c.paste(w, ((px - w.size[0]) // 2, (px - w.size[1]) // 2), w)
    return c


legacy_dens = {
    'mipmap-mdpi': 48, 'mipmap-hdpi': 72, 'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144, 'mipmap-xxxhdpi': 192,
}
fg_dens = {
    'mipmap-mdpi': 108, 'mipmap-hdpi': 162, 'mipmap-xhdpi': 216,
    'mipmap-xxhdpi': 324, 'mipmap-xxxhdpi': 432,
}

for folder, px in legacy_dens.items():
    p = os.path.join(OUT, folder)
    os.makedirs(p, exist_ok=True)
    legacy(px).save(os.path.join(p, 'ic_launcher.png'))
    legacy(px, rounded=False).save(os.path.join(p, 'ic_launcher_round.png'))

for folder, px in fg_dens.items():
    p = os.path.join(OUT, folder)
    os.makedirs(p, exist_ok=True)
    L = layer(px, FG_FRAC)
    L.save(os.path.join(p, 'ic_launcher_fg.png'))
    L.save(os.path.join(p, 'ic_launcher_mono.png'))

print('fg: whale %.0f%% of canvas -> %.0f%% of the visible 72dp area'
      % (FG_FRAC * 100, FG_FRAC * 108.0 / 72.0 * 100))

os.makedirs('/var/minis/workspace/dshport/out', exist_ok=True)
legacy(512).save('/var/minis/workspace/dshport/out/icon_preview.png')
print('icons written to', OUT)
