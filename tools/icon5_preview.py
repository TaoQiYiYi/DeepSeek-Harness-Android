#!/usr/bin/env python3
"""Preview: official DeepSeek icon vs our adaptive icon at several sizes.

Simulates what a launcher shows: take the 108dp canvas, crop the central 72dp
(the guaranteed-visible area) and apply a squircle mask.
"""
import io

import cairosvg
from PIL import Image, ImageChops, ImageDraw

SVG_DARK = '/opt/dshstage/node_modules/@deepseek-ai/dsh-web-frontend/dist/favicon-dark.svg'
BG = (11, 13, 18, 255)
PANEL = 500


def gt(ch, t):
    return ch.point(lambda v: 255 if v > t else 0)


png = cairosvg.svg2png(url=SVG_DARK, output_width=1024, output_height=1024)
whale = Image.open(io.BytesIO(png)).convert('RGBA')
whale = whale.crop(whale.getbbox())
print('whale aspect %.3f' % (whale.size[0] / whale.size[1]))


def fit(img, size):
    w, h = img.size
    s = min(size / w, size / h)
    nw, nh = max(1, int(w * s)), max(1, int(h * s))
    i2 = img.resize((nw, nh), Image.LANCZOS)
    c = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c.paste(i2, ((size - nw) // 2, (size - nh) // 2), i2)
    return c


def sim(frac, px=432):
    fg = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    w = fit(whale, max(1, int(px * frac)))
    fg.paste(w, ((px - w.size[0]) // 2, (px - w.size[1]) // 2), w)
    c = Image.new('RGBA', (px, px), BG)
    c.alpha_composite(fg)
    m = px // 6
    crop = c.crop((m, m, px - m, px - m))
    mask = Image.new('L', crop.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, crop.size[0] - 1, crop.size[1] - 1],
                        radius=int(crop.size[0] * 0.23), fill=255)
    out = Image.new('RGBA', crop.size, (0, 0, 0, 0))
    out.paste(crop, (0, 0), mask)
    return out.resize((PANEL, PANEL), Image.LANCZOS)


def official():
    im = Image.open('/tmp/b_official_ds.png').convert('RGB')
    W, H = im.size
    r, g, b = im.split()
    white = ImageChops.multiply(ImageChops.multiply(gt(r, 195), gt(g, 195)), gt(b, 195))
    wp = white.load()
    rows = [sum(1 for x in range(W) if wp[x, y] > 0) for y in range(H)]
    bottom = 0
    for y in range(H):
        if rows[y] > W * 0.6:
            bottom = y
    ymid = bottom // 2
    xs = [x for x in range(W) if wp[x, ymid] > 0]
    tile = (min(xs), 0, max(xs), bottom)
    blue = ImageChops.multiply(ImageChops.subtract(b, r).point(lambda v: 255 if v > 30 else 0),
                               gt(b, 130))
    bp = blue.load()
    bxs, bys = [], []
    for y in range(0, bottom):
        for x in range(tile[0], tile[2]):
            if bp[x, y] > 0:
                bxs.append(x)
                bys.append(y)
    wbox = (min(bxs), min(bys), max(bxs), max(bys))
    tw = tile[2] - tile[0] + 1
    th = bottom + 1
    ww = wbox[2] - wbox[0] + 1
    wh = wbox[3] - wbox[1] + 1
    print('official: tile=%s whale=%s  whale/tile  w=%.3f h=%.3f' % (tile, wbox, ww / tw, wh / th))
    tile_im = im.crop((tile[0], 0, tile[2] + 1, bottom + 1)).convert('RGBA')
    return tile_im.resize((PANEL, PANEL), Image.LANCZOS), ww / tw


off, off_ratio = official()
panels = [('official  w=%.2f' % off_ratio, off)]
for frac in (0.38, 0.42, 0.46):
    panels.append(('%.2f -> visible %.2f' % (frac, frac * 1.5), sim(frac)))

sheet = Image.new('RGB', (PANEL * len(panels) + 10 * (len(panels) + 1), PANEL + 46), (28, 28, 34))
d = ImageDraw.Draw(sheet)
x = 10
for label, img in panels:
    sheet.paste(img.convert('RGB'), (x, 40))
    d.text((x + 6, 14), label, fill=(255, 255, 255))
    x += PANEL + 10
sheet.save('/var/minis/workspace/dshport/out/icon_compare.png')
print('saved out/icon_compare.png')
print('suggested FG_FRAC = %.3f  (so on-device width = %.2f of tile)'
      % (off_ratio * 72.0 / 108.0, off_ratio))
