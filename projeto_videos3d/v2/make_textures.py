#!/usr/bin/env python3
"""Gera texturas desenhadas (rosto dos personagens, placa de velocidade). Uso: python3 v2/make_textures.py"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures'); os.makedirs(D, exist_ok=True)
F = os.path.join(os.path.dirname(D), '..', 'fonts', 'Poppins-Bold.ttf')
S = 1024
def face(name, eye_h, pupil, brow_dy, brow_tilt, mouth):
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = S // 2, int(S * 0.55)
    for sx in (-1, 1):
        ex = cx + sx * 135
        d.ellipse([ex - 62, cy - eye_h, ex + 62, cy + eye_h], fill=(255, 255, 255, 255), outline=(20, 20, 24, 255), width=10)
        pr = pupil; d.ellipse([ex - pr, cy - pr + 6, ex + pr, cy + pr + 6], fill=(22, 22, 28, 255))
        d.ellipse([ex - pr // 2 + 10, cy - pr + 14, ex - pr // 2 + 30, cy - pr + 34], fill=(255, 255, 255, 255))
        by = cy - eye_h - 40 - brow_dy
        d.line([ex - 60, by + sx * brow_tilt, ex + 60, by - sx * brow_tilt], fill=(30, 22, 18, 255), width=22)
        d.ellipse([ex - 70 + sx * 40, cy + 85, ex + 10 + sx * 40, cy + 125], fill=(255, 120, 120, 90))
    my = cy + 165
    if mouth == 'smile': d.arc([cx - 110, my - 90, cx + 110, my + 50], 20, 160, fill=(40, 20, 20, 255), width=20)
    elif mouth == 'o':
        d.ellipse([cx - 60, my - 55, cx + 60, my + 75], fill=(70, 20, 25, 255), outline=(30, 12, 12, 255), width=10)
        d.ellipse([cx - 34, my + 25, cx + 34, my + 68], fill=(205, 85, 95, 255))
    elif mouth == 'flat': d.line([cx - 70, my, cx + 70, my - 6], fill=(40, 20, 20, 255), width=18)
    elif mouth == 'grin':
        d.chord([cx - 120, my - 70, cx + 120, my + 90], 0, 180, fill=(70, 20, 25, 255), outline=(30, 12, 12, 255), width=10)
        d.rectangle([cx - 90, my + 8, cx + 90, my + 30], fill=(250, 250, 250, 255))
    im.save(f'{D}/face_{name}.png')
face('neutral', 70, 34, 0, 0, 'smile')
face('alarm', 92, 26, 38, -12, 'o')
face('focus', 58, 34, -8, 14, 'flat')
face('relief', 66, 34, 6, -4, 'grin')
# placa de limite de velocidade (padrão R-19 brasileiro: aro vermelho, fundo branco, número preto)
for n in (50, 60):
    im = Image.new('RGB', (S, S), (245, 245, 245)); d = ImageDraw.Draw(im)
    d.ellipse([20, 20, S - 20, S - 20], fill=(200, 20, 30)); d.ellipse([150, 150, S - 150, S - 150], fill=(250, 250, 250))
    f = ImageFont.truetype(F, 420); t = str(n); w = d.textlength(t, font=f)
    d.text(((S - w) / 2, S / 2 - 290), t, font=f, fill=(15, 15, 15))
    d.text((S / 2 - d.textlength('km/h', font=ImageFont.truetype(F, 110)) / 2, S / 2 + 150), 'km/h', font=ImageFont.truetype(F, 110), fill=(15, 15, 15))
    im.save(f'{D}/sign_{n}.png')
print('ok', sorted(os.listdir(D)))
