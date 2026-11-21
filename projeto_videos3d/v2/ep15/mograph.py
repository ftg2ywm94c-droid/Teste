#!/usr/bin/env python3
"""Títulos do vídeo 15 em 1080x1920 (camada RGBA sobre o 3D): gancho "A PORTA FECHOU. / E ELE NÃO PAROU.", selo "VOCÊ DECIDE · PARTE 2"
com "vocês escolheram B", pergunta fixa no topo "PRA ONDE ELE TÁ INDO?", "ÚLTIMA PARADA.", contagem de 5 segundos, cartões A e B,
a escolha ("a mais comentada vira a PARTE 3"), o pedido de envio e o fecho. Faixa dos títulos: y 220-700 (a legenda fica em ~1260-1360).
Uso: python3 v2/ep15/mograph.py -> v2/ep15/mg/<plano>/NNNN.png."""
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
    s = 'VOCÊ DECIDE · PARTE 2'; fo = f(44); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 34
    d.rounded_rectangle((x0, y, x0 + w + 68, y + 76), 38, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((x0 + 34, y + 8), s, font=fo, fill=INK + (int(255 * k),))

COUNT0, COUNT1 = 57.12, 65.8           # "cinco segundos" ... "Comenta" (o 1 fica parado no fim)
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    if t < 3.05:                          # gancho: a premissa no quadro 0
        k = env(t, -1, 3.05, 0.1, 0.2); text(d, W / 2, 330, 'A PORTA FECHOU.', WHT, 104, k)
        if t >= 0.0: text(d, W / 2, 470, 'E ELE NÃO PAROU.', YEL, 104, env(t, 0.9, 3.05, 0.12, 0.2) if t >= 0.9 else 0.0)
        n += 1
    if 3.05 <= t < 8.0: badge(d, 230, env(t, 3.05, 8.0, 0.2, 0.3)); text(d, W / 2, 330, 'vocês escolheram B', WHT, 52, env(t, 3.2, 8.0)); n += 1
    if 3.05 <= t < 65.75:                 # pergunta fixa no topo (lição do Things Explained)
        k = env(t, 3.05, 65.75, 0.3, 0.2); s2 = 'PRA ONDE ELE TÁ INDO?'; fo = f(50); w = d.textlength(s2, font=fo)
        d.rounded_rectangle(((W - w) / 2 - 28, 112, (W + w) / 2 + 28, 188), 30, fill=(16, 16, 16, int(170 * k)))
        text(d, W / 2, 120, s2, YEL, 50, k, stroke=0); n += 1
    if 51.0 <= t < 52.4: text(d, W / 2, 380, 'ÚLTIMA PARADA.', WHT, 116, env(t, 51.0, 52.4, 0.12, 0.2)); n += 1
    if COUNT0 <= t < COUNT1:   # contagem 5 -> 1 no canto direito
        st = (COUNT1 - COUNT0) / 5.0; k = env(t, COUNT0, COUNT1 + 5, 0.15, 0.2); v = max(1, 5 - int((t - COUNT0) / st))
        cx, cy, r = 905, 650, 105
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(16, 20, 40, int(220 * k)), outline=RED + (int(255 * k),), width=10)
        frac = ((t - COUNT0) % st) / st
        d.arc((cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18), -90, -90 + 360 * (1 - frac), fill=YEL + (int(255 * k),), width=10)
        text(d, cx, cy - 78, str(v), WHT, 130, k); n += 1
    if 58.96 <= t < 61.5: card(d, 60, 300, 790, 520, RED, env(t, 58.96, 61.5), 'A', 'ATENDER A\nLIGAÇÃO', 56); n += 1
    if 61.52 <= t < 65.75: card(d, 60, 300, 790, 520, GRN, env(t, 61.52, 65.75), 'B', 'DESCER E\nCORRER', 58); n += 1
    if 65.8 <= t < 72.8:       # a escolha: os dois cartões lado a lado + chamada para comentar + envio
        k = env(t, 65.8, 72.8)
        card(d, 50, 300, 525, 480, RED, k, 'A', 'ATENDER', 48); card(d, 555, 300, 1030, 480, GRN, k, 'B', 'CORRER', 50)
        text(d, W / 2, 520, 'COMENTA A OU B', YEL, 84, k)
        if t >= 67.62: text(d, W / 2, 640, 'a mais comentada vira a PARTE 3', WHT, 50, env(t, 67.62, 72.8))
        if t >= 70.18: text(d, W / 2, 730, 'manda pra quem escolheria diferente', WHT, 44, env(t, 70.18, 72.8))
        n += 1
    if t >= 72.94:             # fecho
        k = env(t, 72.94, 99); text(d, W / 2, 330, 'VOCÊ DECIDE', YEL, 130, k)
        if t >= 73.4: text(d, W / 2, 500, 'PARTE 3 EM BREVE', WHT, 64, env(t, 73.4, 99)); n += 1
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
