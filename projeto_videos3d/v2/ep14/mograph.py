#!/usr/bin/env python3
"""Títulos do vídeo 14 (Vendaval · Ep. 2) em 1080x1920 (camada RGBA sobre o 3D): selo "VENDAVAL · EP. 2", "vocês escolheram B",
cartões das opções A e B, a escolha final ("a mais comentada vira o EP. 3") e o fecho; mais a camada 2D nítida de chuva e vento
nos planos de fora (a mesma do vídeo 12). Uso: python3 v2/ep14/mograph.py -> v2/ep14/mg/<plano>/NNNN.png."""
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
WX = {'S04_vento': (1.0, 1.0, 1.0), 'S05_queda': (1.0, 1.0, 1.0), 'S07_destrocos': (1.0, 1.0, 1.0), 'S08_caiu': (0.6, 1.0, 0.6),
      'S16_vizinha': (0.55, 1.0, 0.5), 'S19_escolha': (0.5, 1.0, 0.5), 'S20_cta': (0.45, 1.0, 0.4)}   # plano: (chuva, vento, respingos no chão)
def wind_lvl(t):   # igual ao story.ts: forte até o estrondo, baixa até o "silêncio" e fica fraco
    if t < 12.3: return 1.0
    if t < 17.9: u = (t - 12.3) / 5.6; return 1.0 - 0.72 * u * u * (3 - 2 * u)
    return 0.28
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

def badge(d, y, k, s='VENDAVAL · EP. 2'):
    fo = f(44); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 34
    d.rounded_rectangle((x0, y, x0 + w + 68, y + 76), 38, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((x0 + 34, y + 8), s, font=fo, fill=INK + (int(255 * k),))
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    if t < 4.3: badge(d, 230, env(t, 0.0, 4.3, 0.25, 0.3)); n += 1
    if 0.2 <= t < 2.8:
        k = env(t, 0.2, 2.8); text(d, W / 2, 340, 'vocês escolheram', WHT, 58, k); card(d, 175, 440, 905, 620, GRN, k, 'B', 'BANHEIRO', 60); n += 1
    if 48.3 <= t < 53.2: card(d, 60, 300, 790, 520, RED, env(t, 48.3, 53.2), 'A', 'ATRAVESSAR\nE AJUDAR', 52); n += 1
    if 53.22 <= t < 58.25: card(d, 60, 300, 790, 520, GRN, env(t, 53.22, 58.25), 'B', 'FICAR E\nLIGAR 193', 56); n += 1
    if 58.3 <= t < 63.6:
        k = env(t, 58.3, 63.6)
        card(d, 50, 300, 525, 480, RED, k, 'A', 'AJUDAR', 50); card(d, 555, 300, 1030, 480, GRN, k, 'B', 'LIGAR 193', 42)
        text(d, W / 2, 520, 'COMENTA A OU B', YEL, 84, k)
        if t >= 60.7: text(d, W / 2, 640, 'a mais comentada vira o EP. 3', WHT, 52, env(t, 60.7, 63.6))
        n += 1
    if t >= 63.66:
        k = env(t, 63.66, 99); text(d, W / 2, 330, 'VENDAVAL', YEL, 140, k)
        if t >= 64.2: text(d, W / 2, 510, 'EP. 3 EM BREVE', WHT, 64, env(t, 64.2, 99))
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
