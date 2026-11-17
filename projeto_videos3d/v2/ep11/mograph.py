#!/usr/bin/env python3
"""Títulos do vídeo 11 em 1080x1920 (camada RGBA sobreposta ao 3D): ano/lugar, HORA 0, DIA 1-3, ≈4 H e o cartão final
"link na bio" + "#publi". Faixa dos títulos: y 300-560 (acima da legenda em ~1260-1360 e abaixo das notas no topo).
Uso: python3 v2/ep11/mograph.py  ->  v2/ep11/mg/<plano>/NNNN.png (quadros vazios são links para um PNG transparente)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import plan as P
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf'); W, H = 1080, 1920
YEL, WHT, RED, GRN = (255, 210, 20), (255, 255, 255), (255, 90, 80), (70, 225, 140)
def f(px): return ImageFont.truetype(FONT, px)
# (t0, t1, linhas [(texto, cor, px)], y do topo, estilo)
TIT = [
    (5.14, 10.0, [('2020', YEL, 190), ('AMAPÁ · QUASE 4 DIAS NO ESCURO', WHT, 50)], 300, 'big'),
    (10.25, 17.0, [('2024', YEL, 190), ('SÃO PAULO · 2,1 MILHÕES SEM LUZ', WHT, 50)], 300, 'big'),
    (17.24, 19.7, [('HORA 0', WHT, 170)], 330, 'big'),
    (22.1, 26.7, [('≈ 4 H', YEL, 170), ('GELADEIRA FECHADA', WHT, 50)], 300, 'big'),
    (26.86, 30.0, [('DIA 1', YEL, 190)], 320, 'big'),
    (34.86, 38.0, [('DIA 2', YEL, 190)], 320, 'big'),
    (62.72, 66.0, [('DIA 3', GRN, 190)], 320, 'big'),
    (67.4, 72.52, [('O POWER BANK DO VÍDEO', WHT, 56), ('LINK NA BIO', YEL, 120)], 330, 'card'),
]
def draw_title(lines, y0, k, style):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = y0
    if style == 'card':
        hh = sum(int(px * 1.15) for _, _, px in lines) + 60
        d.rounded_rectangle((90, y - 30, W - 90, y - 30 + hh), 44, fill=(16, 20, 40, int(200 * k)), outline=YEL + (int(255 * k),), width=6)
    for txt, col, px in lines:
        s = max(1, int(px * (0.85 + 0.15 * k))); fo = f(s); w = d.textlength(txt, font=fo)
        d.text(((W - w) / 2, y + (px - s) / 2), txt, font=fo, fill=col + (int(255 * k),), stroke_width=max(4, s // 18), stroke_fill=(16, 16, 16, int(230 * k)))
        y += int(px * 1.15)
    return im
def main():
    mg = os.path.join(HERE, 'mg'); os.makedirs(mg, exist_ok=True)
    blank = os.path.join(mg, '_blank.png'); Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(blank)
    for s in P.SHOTS:
        dd = os.path.join(mg, s.name); os.makedirs(dd, exist_ok=True); n = 0
        for fr in s.frames:
            t = fr / P.FPS; dst = os.path.join(dd, f'{fr:04d}.png')
            if os.path.lexists(dst): os.remove(dst)
            act = [x for x in TIT if x[0] <= t < x[1]]
            if not act: os.link(blank, dst); continue
            t0, t1, lines, y0, st = act[0]
            k = min(1.0, (t - t0) / 0.18, (t1 - t) / 0.2)
            k = max(0.0, k); k = 1 - (1 - k) ** 3
            draw_title(lines, y0, k, st).save(dst, compress_level=1); n += 1
        print(s.name, 'ok', n, 'quadros com título')
if __name__ == '__main__': main()
