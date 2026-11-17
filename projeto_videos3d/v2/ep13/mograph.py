#!/usr/bin/env python3
"""Títulos do vídeo 13 em 1080x1920 (camada RGBA sobre o 3D): selo "VOCÊ DECIDE · EP. 1", "00:10", contagem de 5 segundos,
cartões das opções A e B, a escolha final ("a mais comentada vira o EP. 2") e o fecho "VOCÊ DECIDE". Faixa dos títulos:
y 220-700 (a legenda fica em ~1260-1360, as notas no topo em ~140-200). Uso: python3 v2/ep13/mograph.py -> v2/ep13/mg/<plano>/NNNN.png."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import plan as P
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf'); W, H = 1080, 1920
YEL, WHT, RED, GRN, INK = (255, 210, 20), (255, 255, 255), (255, 90, 80), (70, 225, 140), (16, 16, 16)
def f(px): return ImageFont.truetype(FONT, px)
def env(t, t0, t1, a=0.18, b=0.2):
    k = max(0.0, min(1.0, (t - t0) / a, (t1 - t) / b)); return 1 - (1 - k) ** 3
def text(d, cx, y, s, col, px, k, stroke=None):
    s2 = max(1, int(px * (0.85 + 0.15 * k))); fo = f(s2); w = d.textlength(s, font=fo)
    d.text((cx - w / 2, y + (px - s2) / 2), s, font=fo, fill=col + (int(255 * k),), stroke_width=stroke if stroke is not None else max(4, s2 // 18), stroke_fill=INK + (int(230 * k),))
def card(d, x0, y0, x1, y1, col, k, letter, label, lpx=46):
    d.rounded_rectangle((x0, y0, x1, y1), 40, fill=(16, 20, 40, int(215 * k)), outline=col + (int(255 * k),), width=7)
    r = (y1 - y0) // 2 - 22; cy = (y0 + y1) // 2; cx = x0 + 30 + r
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (int(255 * k),), outline=INK + (int(255 * k),), width=6)
    text(d, cx, cy - int(r * 0.95), letter, INK, int(r * 1.5), k, stroke=0)
    lines = label.split('\n'); lh = int(lpx * 1.12); y = cy - lh * len(lines) // 2
    for ln in lines: text(d, (cx + r + x1) // 2, y, ln, WHT, lpx, k); y += lh

def badge(d, y, k):
    s = 'VOCÊ DECIDE · EP. 1'; fo = f(44); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 34
    d.rounded_rectangle((x0, y, x0 + w + 68, y + 76), 38, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((x0 + 34, y + 8), s, font=fo, fill=INK + (int(255 * k),))

COUNT0, COUNT1 = 50.38, 61.0           # "cinco segundos" ... "Comenta" (o 1 fica parado no fim)
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    if t < 5.7: badge(d, 230, env(t, 0.0, 5.7, 0.25, 0.3)); n += 1
    if 0.4 <= t < 3.4: text(d, W / 2, 340, '00:10', WHT, 190, env(t, 0.4, 3.4)); n += 1
    if COUNT0 <= t < COUNT1:   # contagem 5 -> 1 no canto direito
        st = (COUNT1 - COUNT0) / 5.0; k = env(t, COUNT0, COUNT1 + 5, 0.15, 0.2); v = max(1, 5 - int((t - COUNT0) / st))
        cx, cy, r = 905, 410, 105
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(16, 20, 40, int(220 * k)), outline=RED + (int(255 * k),), width=10)
        frac = ((t - COUNT0) % st) / st
        d.arc((cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18), -90, -90 + 360 * (1 - frac), fill=YEL + (int(255 * k),), width=10)
        text(d, cx, cy - 78, str(v), WHT, 130, k); n += 1
    if 52.04 <= t < 55.6: card(d, 60, 300, 790, 520, RED, env(t, 52.04, 55.6), 'A', 'DESCER NO\nSEU PONTO', 54); n += 1
    if 55.62 <= t < 60.95: card(d, 60, 300, 790, 520, GRN, env(t, 55.62, 60.95), 'B', 'FICAR NO\nÔNIBUS', 58); n += 1
    if 61.0 <= t < 66.7:       # a escolha: os dois cartões lado a lado + chamada para comentar
        k = env(t, 61.0, 66.7)
        card(d, 50, 300, 525, 480, RED, k, 'A', 'DESCER', 50); card(d, 555, 300, 1030, 480, GRN, k, 'B', 'FICAR', 52)
        text(d, W / 2, 520, 'COMENTA A OU B', YEL, 84, env(t, 61.0, 66.7))
        if t >= 63.1: text(d, W / 2, 640, 'a mais comentada vira o EP. 2', WHT, 52, env(t, 63.1, 66.7))
        n += 1
    if t >= 66.76:             # fecho
        k = env(t, 66.76, 99); text(d, W / 2, 330, 'VOCÊ DECIDE', YEL, 130, k)
        if t >= 67.3: text(d, W / 2, 500, 'EP. 2 EM BREVE', WHT, 64, env(t, 67.3, 99)); n += 1
        n += 1
    return im, n
def main():
    mg = os.path.join(HERE, 'mg'); os.makedirs(mg, exist_ok=True)
    blank = os.path.join(mg, '_blank.png'); Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(blank)
    for s in P.SHOTS:
        dd = os.path.join(mg, s.name); os.makedirs(dd, exist_ok=True); c = 0
        for fr in s.frames:
            dst = os.path.join(dd, f'{fr:04d}.png')
            if os.path.lexists(dst): os.remove(dst)
            im, n = frame(fr / P.FPS)
            if not n: os.link(blank, dst); continue
            im.save(dst, compress_level=1); c += 1
        print(s.name, 'ok', c, 'quadros com título')
if __name__ == '__main__': main()
