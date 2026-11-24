#!/usr/bin/env python3
"""Títulos do vídeo 18 (Jogador 2 · Ep. 1) em 1080x1920 (camada RGBA sobre o 3D): gancho "FALTAVA 1% / E A LUZ CAIU.", selo
"JOGADOR 2 · EP. 1" com "no final, você decide", aviso "NO FINAL: A OU B", cartões A e B, a escolha, o pedido de envio e o fecho.
Sem pergunta fixa no topo. Sem logo nem marca de jogo ou console.
Uso: python3 v2/ep18/mograph.py -> v2/ep18/mg/<plano>/NNNN.png."""
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
    s = 'JOGADOR 2 · EP. 1'; fo = f(44); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 34
    d.rounded_rectangle((x0, y, x0 + w + 68, y + 76), 38, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((x0 + 34, y + 8), s, font=fo, fill=INK + (int(255 * k),))
def backing(d, y0, y1, k, a=170):
    d.rounded_rectangle((70, y0, W - 70, y1), 40, fill=(10, 12, 24, int(a * k)))

def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    if t < 3.0:                           # gancho: a ameaça no quadro 0 (99 % e a luz cai)
        k = env(t, -1, 3.0, 0.1, 0.2); backing(d, 150, 450, k, 190)
        text(d, W / 2, 180, 'FALTAVA 1%', WHT, 110, k); text(d, W / 2, 310, 'E A LUZ CAIU.', YEL, 104, k); n += 1
    if 3.0 <= t < 8.6:
        k = env(t, 3.0, 8.6, 0.2, 0.3); backing(d, 200, 420, k, 160)
        badge(d, 230, k)
        if t >= 3.4: text(d, W / 2, 330, 'no final, você decide', YEL, 50, env(t, 3.4, 8.6))
        n += 1
    if 26.0 <= t < 36.0:                  # aviso de que há escolha (metade do público sai perto da metade do vídeo)
        k = env(t, 26.0, 36.0, 0.3, 0.3); s2 = 'NO FINAL: A OU B'; fo = f(50); w = d.textlength(s2, font=fo)
        d.rounded_rectangle(((W - w) / 2 - 28, 112, (W + w) / 2 + 28, 188), 30, fill=(16, 16, 16, int(170 * k)))
        text(d, W / 2, 120, s2, YEL, 50, k, stroke=0); n += 1
    if 48.94 <= t < 52.5: card(d, 60, 300, 1020, 540, RED, env(t, 48.94, 52.5), 'A', 'PEGAR O QUE VIBRA\nNO SOFÁ', 52); n += 1
    if 52.56 <= t < 57.2: card(d, 60, 300, 1020, 540, GRN, env(t, 52.56, 57.2), 'B', 'LIGAR O GERADOR\nNO GALPÃO', 52); n += 1
    if 57.28 <= t < 63.9:      # a escolha: os dois cartões lado a lado + chamada para comentar + envio
        k = env(t, 57.28, 63.9)
        card(d, 50, 300, 525, 480, RED, k, 'A', 'PEGAR', 50); card(d, 555, 300, 1030, 480, GRN, k, 'B', 'GERADOR', 44)
        text(d, W / 2, 520, 'COMENTA A OU B', YEL, 84, k)
        if t >= 59.0: text(d, W / 2, 640, 'a mais comentada vira a PARTE 2', WHT, 50, env(t, 59.0, 63.9))
        if t >= 61.6: text(d, W / 2, 730, 'manda pra quem tá esperando esse jogo', WHT, 42, env(t, 61.6, 63.9))
        n += 1
    if t >= 64.0:              # fecho
        k = env(t, 64.0, 99, 0.12); text(d, W / 2, 330, 'VOCÊ DECIDE', YEL, 130, k)
        text(d, W / 2, 500, 'PARTE 2 EM BREVE', WHT, 64, k); n += 1
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
