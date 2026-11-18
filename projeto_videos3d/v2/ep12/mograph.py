#!/usr/bin/env python3
"""Títulos do vídeo 12 em 1080x1920 (camada RGBA sobre o 3D): "23:00", "+10 MIN", contagem de 10 segundos, cartões das
opções A e B, a escolha final e "resposta no comentário fixado". Faixa dos títulos: y 300-700 (a legenda fica em ~1260-1360,
as notas no topo em ~140-200). Uso: python3 v2/ep12/mograph.py -> v2/ep12/mg/<plano>/NNNN.png."""
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

# ---- clima nítido em 2D (chuva, respingos, rajadas, folhas) por cima do 3D nos planos de tempestade ----
import math, random
WX = {'S06_vento_chega': (0.0, 1.0, 0.0), 'S08_arvores': (1.0, 1.0, 1.0), 'S12_arvore': (1.0, 0.9, 1.0), 'S13_inclina': (1.0, 1.0, 0.0),
      'S15_opcao_a': (1.0, 1.0, 1.0), 'S17_escolha': (0.9, 0.8, 1.0)}   # plano: (chuva, vento, respingos no chão)
def wind_lvl(t): return 0.0 if t < 23.64 else min(1.0, 0.15 + 0.85 * ((t - 23.64) / 7.0)) if t < 30.7 else 1.0
R0 = random.Random(12); DROPS = [(R0.random() * 1300 - 100, R0.random() * 2200, 0.6 + 0.8 * R0.random(), R0.random() < 0.35) for _ in range(340)]
LEAVES = [(R0.random() * 1920, R0.random(), 0.6 + 0.8 * R0.random(), R0.random() * 6.28, R0.choice([(79, 154, 67), (98, 174, 76), (138, 106, 58), (62, 126, 56)])) for _ in range(40)]
def weather(t, name):
    if name not in WX: return None
    rain, wnd, spl = WX[name]; w = wnd * wind_lvl(t)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    slant = 0.18 + 0.22 * w
    if rain:
        for x0, y0, sp, near in DROPS:
            v = (2400 if near else 1500) * sp; L = (150 if near else 80) * sp
            y = (y0 + v * t) % 2200 - 140; x = (x0 + slant * v * t) % 1300 - 110
            a = int((200 if near else 120) * rain)
            d.line([(x, y), (x - slant * L, y - L)], fill=(225, 235, 255, a), width=4 if near else 2)
    if spl:   # respingos: anéis curtos que nascem e somem no chão (metade de baixo)
        f = int(t * 30)
        for k in range(26):
            r = random.Random(f // 3 * 97 + k); x = r.random() * W; y = 1450 + r.random() * 430; u = (f % 3) / 3
            rx, ry = 10 + 22 * u, 3 + 6 * u; a = int(170 * (1 - u) * spl)
            d.ellipse((x - rx, y - ry, x + rx, y + ry), outline=(225, 235, 255, a), width=3)
            for s_ in (-1, 1): d.line([(x, y), (x + s_ * 14 * (0.5 + u), y - 16 * (1 - u))], fill=(225, 235, 255, a), width=2)
    if w > 0.05:
        for k in range(5):   # rajadas: arcos longos e finos varrendo da esquerda para a direita
            r = random.Random(k * 31); ph = (t * (0.7 + 0.3 * r.random()) + r.random()) % 1; y = 250 + r.random() * 1400
            x = -700 + ph * 2400; L = 500 + 300 * r.random(); a = int(150 * w * math.sin(math.pi * ph))
            pts = [(x + i * L / 12, y + 40 * math.sin(i / 12 * math.pi + k) - i * 3) for i in range(13)]
            d.line(pts, fill=(235, 242, 255, a), width=3 + k % 3, joint='curve')
        n = int(len(LEAVES) * w)
        for y0, ph0, sp, rot0, col in LEAVES[:n]:   # folhas cruzando a tela, girando
            ph = (ph0 + t * 0.55 * sp) % 1; x = -80 + ph * 1240; y = y0 + 120 * math.sin(ph * 9 + rot0) + ph * 160
            a = rot0 + t * 9 * sp; rx, ry = 22 * sp, 9 * sp
            poly = [(x + rx * math.cos(a + q_) * (1 if i % 2 == 0 else 0.4), y + rx * math.sin(a + q_) * (1 if i % 2 == 0 else 0.4)) for i, q_ in enumerate([0, math.pi / 2, math.pi, 3 * math.pi / 2])]
            d.polygon(poly, fill=col + (235,), outline=(36, 23, 38, 220))
    return im

COUNT0, COUNT1 = 48.78, 60.06           # "você tem 10 segundos" ... "E aí" (o 1 fica parado na escolha)
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    if 1.0 <= t < 3.72: text(d, W / 2, 330, '23:00', WHT, 190, env(t, 1.0, 3.72)); n += 1
    if 22.1 <= t < 25.0: text(d, W / 2, 330, '+10 MIN', YEL, 170, env(t, 22.1, 25.0)); n += 1
    if COUNT0 <= t < COUNT1:   # contagem 10 -> 1 no canto direito
        k = env(t, COUNT0, COUNT1 + 5, 0.15, 0.2); v = max(1, 10 - int((t - COUNT0) / ((COUNT1 - COUNT0) / 9.5)))
        cx, cy, r = 905, 410, 105
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(16, 20, 40, int(220 * k)), outline=RED + (int(255 * k),), width=10)
        frac = ((t - COUNT0) % ((COUNT1 - COUNT0) / 9.5)) / ((COUNT1 - COUNT0) / 9.5)
        d.arc((cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18), -90, -90 + 360 * (1 - frac), fill=YEL + (int(255 * k),), width=10)
        text(d, cx, cy - 78, str(v), WHT, 130, k); n += 1
    if 50.34 <= t < 54.3: card(d, 60, 300, 790, 520, RED, env(t, 50.34, 54.3), 'A', 'SAIR\nPRA RUA', 60); n += 1
    if 54.34 <= t < 60.0: card(d, 60, 300, 790, 520, GRN, env(t, 54.34, 60.0), 'B', 'BANHEIRO\nSEM JANELA', 54); n += 1
    if 60.06 <= t < 66.7:      # a escolha: os dois cartões lado a lado + chamada para comentar
        k = env(t, 60.06, 66.7)
        card(d, 50, 300, 525, 480, RED, k, 'A', 'RUA', 52); card(d, 555, 300, 1030, 480, GRN, k, 'B', 'BANHEIRO', 44)
        if t >= 62.1: text(d, W / 2, 520, 'COMENTA A OU B', YEL, 84, env(t, 62.1, 66.7))
        if t >= 64.0: text(d, W / 2, 640, 'resposta no comentário fixado', WHT, 50, env(t, 64.0, 66.7))
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
            im, n = frame(fr / P.FPS); wx = weather(fr / P.FPS, s.name)
            if wx is not None: wx.alpha_composite(im); im = wx; n += 1
            if not n: os.link(blank, dst); continue
            im.save(dst, compress_level=1); c += 1
        print(s.name, 'ok', c, 'quadros com título')
if __name__ == '__main__': main()
