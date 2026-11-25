#!/usr/bin/env python3
"""Títulos do vídeo 21 (A Chave · Ep. 1) em 1080x1920 (camada RGBA sobre o 3D), no nosso estilo (Poppins + amarelo):
- selo "A CHAVE · EP. 1 / no final, você decide" nos primeiros 2,5 s e no plano do loop (a emenda fica igual);
- cartões A/B, "COMENTA A OU B" e "a mais comentada vira a PARTE 2" na escolha.
O resto do vídeo fica sem títulos: a legenda de uma palavra e a câmera contam a história.
Uso: python3 v2/ep21/mograph.py -> v2/ep21/mg/<plano>/NNNN.png."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import plan as P
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf'); W, H = 1080, 1920
YEL, WHT, RED, GRN, INK = (255, 210, 20), (255, 255, 255), (235, 60, 60), (70, 225, 140), (16, 14, 22)
def f(px): return ImageFont.truetype(FONT, px)
def env(t, t0, t1, a=0.18, b=0.2):
    k = max(0.0, min(1.0, (t - t0) / a, (t1 - t) / b)); return 1 - (1 - k) ** 3
def text(d, cx, y, s, col, px, k, stroke=None, anchor='mt'):
    s2 = max(1, int(px * (0.85 + 0.15 * k))); fo = f(s2)
    d.text((cx, y + (px - s2) / 2), s, font=fo, fill=col + (int(255 * k),), anchor=anchor,
           stroke_width=stroke if stroke is not None else max(4, s2 // 14), stroke_fill=INK + (int(230 * k),))
def card(d, x0, y0, x1, y1, col, k, letter, label, lpx=46):
    d.rounded_rectangle((x0, y0, x1, y1), 40, fill=(16, 20, 40, int(215 * k)), outline=col + (int(255 * k),), width=7)
    r = (y1 - y0) // 2 - 22; cy = (y0 + y1) // 2; cx = x0 + 30 + r
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (int(255 * k),), outline=INK + (int(255 * k),), width=6)
    text(d, cx, cy, letter, INK, int(r * 1.5), k, stroke=0, anchor='mm')
    lines = label.split('\n'); lh = int(lpx * 1.12); y = cy - lh * len(lines) // 2
    for ln in lines: text(d, (cx + r + x1) // 2, y, ln, WHT, lpx, k); y += lh
def badge(d, k):
    s = 'A CHAVE · EP. 1'; fo = f(46); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 36
    d.rounded_rectangle((x0, 390, x0 + w + 72, 470), 40, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((W / 2, 430), s, font=fo, fill=INK + (int(255 * k),), anchor='mm')
    text(d, W / 2, 492, 'no final, você decide', YEL, 50, k)
A, B, COM, SE = 53.16, 56.1, 58.04, P.W['k_se']
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if t < 2.5: badge(d, min(1.0, (2.5 - t) / 0.25))
    if t >= SE + 0.02: badge(d, min(1.0, (t - SE - 0.02) / 0.25))       # no último quadro igual ao quadro 0 (k = 1)
    if A <= t < B: card(d, 60, 380, 1020, 620, RED, env(t, A, B), 'A', 'PEGA A CHAVE\nDA MÃO DELE', 52)
    if B <= t < COM: card(d, 60, 380, 1020, 620, GRN, env(t, B, COM), 'B', 'CORRE\nPRA CASA', 56)
    if COM <= t < SE:
        k = env(t, COM, SE)
        card(d, 50, 380, 525, 560, RED, k, 'A', 'PEGAR', 50); card(d, 555, 380, 1030, 560, GRN, k, 'B', 'CORRER', 50)
        text(d, W / 2, 600, 'COMENTA A OU B', YEL, 84, k)
        if t >= 60.66:
            k2 = env(t, 60.66, SE); w2 = d.textlength('a mais comentada vira a PARTE 2', font=f(50))
            d.rounded_rectangle((W / 2 - w2 / 2 - 30, 708, W / 2 + w2 / 2 + 30, 792), 36, fill=(10, 12, 24, int(200 * k2)))
            text(d, W / 2, 720, 'a mais comentada vira a PARTE 2', WHT, 50, k2)
    return im
def main():
    only = set(sys.argv[1:]); mg = os.path.join(HERE, 'mg'); os.makedirs(mg, exist_ok=True); empty = None
    for s in P.SHOTS:
        if only and s.name not in only: continue
        dd = os.path.join(mg, s.name); os.makedirs(dd, exist_ok=True)
        for fr in s.frames:
            dst = os.path.join(dd, f'{fr:04d}.png')
            if os.path.lexists(dst): os.remove(dst)
            im = frame(fr / P.FPS)
            if im.getbbox() is None:                       # quadro vazio: um arquivo só, ligado por link (economiza disco)
                if empty is None: empty = os.path.join(mg, 'vazio.png'); im.save(empty)
                os.link(empty, dst)
            else: im.save(dst, compress_level=1)
        print(s.name, 'ok', len(s.frames), 'quadros')
if __name__ == '__main__': main()
