#!/usr/bin/env python3
"""Títulos do vídeo 19 (A Noite Livre · Ep. 1) em 1080x1920 (camada RGBA sobre o 3D), com as técnicas das referências
(analysis/refs/MANUAL_REFERENCIAS.md) no nosso estilo (Poppins + amarelo):
- HUD fixo: "● NOITE LIVRE", relógio 21:57 → 21:58 (TV: faltam dois minutos) → 21:59 (o Thor para de latir) e "FALTAM X MIN";
- palavra-chave no topo de cada plano, com sublinhado (amarelo; vermelho no perigo);
- onomatopeias carimbadas na palavra exata ("CLAC" na tranca, "AU! AU!" no Thor latindo);
- círculo na máscara do meio quando o Thor abana o rabo;
- cartões A/B, "COMENTA A OU B" e "a mais comentada vira a PARTE 2";
- fecho em loop: o último plano repete o quadro 0 (selo da série + HUD em 21:57).
Uso: python3 v2/ep19/mograph.py -> v2/ep19/mg/<plano>/NNNN.png."""
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

# ---- HUD fixo (canto superior esquerdo, abaixo da faixa das abas do app) ----
def hud(d, t, k=1.0):
    loop = t >= P.W['se']
    clock, falta = ('21:57', 'FALTAM 3 MIN') if (loop or t < P.W['dois']) else (('21:58', 'FALTAM 2 MIN') if t < 46.78 else ('21:59', 'FALTA 1 MIN'))
    d.rounded_rectangle((48, 150, 330, 330), 26, fill=(10, 12, 24, int(175 * k)))
    d.ellipse((74, 178, 92, 196), fill=RED + (int(255 * k),)); d.text((104, 187), 'NOITE LIVRE', font=f(30), fill=WHT + (int(255 * k),), anchor='lm')
    d.text((72, 250), clock, font=f(74), fill=WHT + (int(255 * k),), anchor='lm')
    d.text((74, 306), falta, font=f(32), fill=(RED if not clock.endswith('57') else YEL) + (int(255 * k),), anchor='lm')

# ---- palavra-chave do plano (topo, centro) ----
KEYS = {  # plano: (texto, cor do sublinhado, início opcional)
    'S02_tv': ('DAS 22H ÀS 6H', YEL), 'S04_rostos': ('SEM POLÍCIA', RED), 'S05_cortina': ('A CORTINA', YEL), 'S06_tranca': ('TUDO TRANCADO', YEL),
    'S07_caminha': ('CADÊ O THOR?', RED), 'S08_quintal': ('NO QUINTAL', YEL), 'S09_portao': ('O PORTÃO ABERTO', RED), 'S10_foi_voce': ('FOI VOCÊ', RED, 27.4),
    'S11_thor_rua': ('NO MEIO DA RUA', YEL), 'S12_mascaras': ('3 MÁSCARAS', RED), 'S13_porta': ('NINGUÉM ABRE', YEL), 'S14_bia': ('É O THOR!', RED),
    'S16_pai': ('30 SEGUNDOS', YEL), 'S17_vira': ('ELE VIU', RED, 44.62), 'S18_thor_quieto': ('PAROU DE LATIR', RED, 46.78), 'S19_abana': ('ABANOU O RABO', RED),
    'S20_decide': ('VOCÊ DECIDE', YEL),
}
def keyword(d, s, col, k):
    fo = f(60); w = d.textlength(s, font=fo)
    text(d, W / 2, 392, s, WHT, 60, k); d.rectangle((W / 2 - w / 2, 470, W / 2 + w / 2, 480), fill=col + (int(255 * k),))

# ---- onomatopeia carimbada (gira levemente, entra com um "soco" de escala) ----
def stamp(im, s, x, y, ang, k, col=RED, px=96):
    lay = Image.new('RGBA', (560, 220), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((12, 12, 548, 208), 26, outline=col + (int(255 * k),), width=12, fill=(255, 255, 255, int(28 * k)))
    dd.text((280, 110), s, font=f(px), fill=col + (int(255 * k),), anchor='mm', stroke_width=5, stroke_fill=INK + (int(255 * k),))
    sc = 1.25 - 0.25 * k; lay = lay.resize((int(560 * sc), int(220 * sc)), Image.BICUBIC).rotate(ang, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
def pop(t, t0, d=0.12): return max(0.0, min(1.0, (t - t0) / d))

def shot_of(t):
    fr = int(round(t * P.FPS))
    return next((s for s in P.SHOTS if s.a <= fr < s.b), P.SHOTS[-1])

def badge(d, k):   # selo da série (quadro 0 e fecho em loop)
    s = 'A NOITE LIVRE · EP. 1'; fo = f(46); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 36
    d.rounded_rectangle((x0, 390, x0 + w + 72, 470), 40, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((W / 2, 430), s, font=fo, fill=INK + (int(255 * k),), anchor='mm')
    text(d, W / 2, 492, 'no final, você decide', YEL, 50, k)

def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    s = shot_of(t)
    hud(d, t); n += 1
    if s.name == 'S01_sofa' or s.name == 'S24_loop':
        badge(d, 1.0)                                    # igual no quadro 0 e no fim: o Short emenda sem costura
    elif s.name in KEYS:
        kv = KEYS[s.name]; t0 = kv[2] if len(kv) > 2 else s.t0
        if t >= t0: keyword(d, kv[0], kv[1], env(t, t0, s.t1, 0.15, 0.1))
    if s.name == 'S06_tranca' and t >= 19.02: stamp(im, 'CLAC!', 760, 900, -8, pop(t, 19.02), YEL)
    if s.name in ('S11_thor_rua', 'S12_mascaras'):
        bk = int(t * 4.6) % 3 != 2
        if bk: stamp(im, 'AU! AU!', 720 if s.name == 'S11_thor_rua' else 300, 820 if s.name == 'S11_thor_rua' else 1120, 9, 1.0)
    if s.name == 'S19_abana':
        k = env(t, 49.0, s.t1, 0.25, 0.1)
        if k > 0: d.ellipse((120, 640, 330, 1080), outline=YEL + (int(255 * k),), width=10)
    if P.W['opcaoA'] <= t < P.W['opcaoB']: card(d, 60, 380, 1020, 620, RED, env(t, P.W['opcaoA'], P.W['opcaoB']), 'A', 'CORRE E PEGA\nO THOR', 52)
    if P.W['opcaoB'] <= t < P.W['comenta']: card(d, 60, 380, 1020, 620, GRN, env(t, P.W['opcaoB'], P.W['comenta']), 'B', 'FICA E CHAMA\nPELA JANELA', 52)
    if P.W['comenta'] <= t < P.W['se']:
        k = env(t, P.W['comenta'], P.W['se'])
        card(d, 50, 380, 525, 560, RED, k, 'A', 'PEGAR', 50); card(d, 555, 380, 1030, 560, GRN, k, 'B', 'JANELA', 50)
        text(d, W / 2, 600, 'COMENTA A OU B', YEL, 84, k)
        if t >= 60.04: text(d, W / 2, 720, 'a mais comentada vira a PARTE 2', WHT, 50, env(t, 60.04, P.W['se']))
    return im, n

def main():
    mg = os.path.join(HERE, 'mg'); os.makedirs(mg, exist_ok=True)
    for s in P.SHOTS:
        dd = os.path.join(mg, s.name); os.makedirs(dd, exist_ok=True)
        for fr in s.frames:
            dst = os.path.join(dd, f'{fr:04d}.png')
            if os.path.lexists(dst): os.remove(dst)
            im, n = frame(fr / P.FPS); im.save(dst, compress_level=1)
        print(s.name, 'ok', len(s.frames), 'quadros')
if __name__ == '__main__': main()
