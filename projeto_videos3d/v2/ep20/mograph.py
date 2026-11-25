#!/usr/bin/env python3
"""Títulos do vídeo 20 (A Visita · Ep. 1) em 1080x1920 (camada RGBA sobre o 3D), com as técnicas das referências
(analysis/refs/MANUAL_REFERENCIAS.md) no nosso estilo (Poppins + amarelo):
- HUD fixo: relógio 03:00 → 03:06 e a bateria do celular caindo;
- palavra-chave no topo de cada plano (amarelo; vermelho no medo);
- tela do celular em tela cheia (app de mensagens GENÉRICO, sem logo nem cores de marca) com as mensagens do "Vó ❤";
- anel do olho mágico nos planos da varanda; "BIP BIP" e "TOC TOC TOC" carimbados; círculo no marido;
- cartões A/B, "COMENTA A OU B" e fecho em loop (o último plano repete o quadro 0).
Uso: python3 v2/ep20/mograph.py -> v2/ep20/mg/<plano>/NNNN.png."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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


# ---- HUD fixo: relógio e bateria ----
CLOCK = [(0.0, '03:00'), (16.8, '03:01'), (25.6, '03:02'), (35.1, '03:03'), (44.4, '03:04'), (52.8, '03:05'), (61.7, '03:06')]
def hud(d, t, k=1.0):
    loop = t >= P.W['se']
    clock = '03:00' if loop else [c for a, c in CLOCK if t >= a][-1]
    bat = 23 if loop else max(6, int(round(23 - 17 * t / P.W['se'])))
    d.rounded_rectangle((48, 150, 300, 312), 26, fill=(10, 12, 24, int(175 * k)))
    d.text((72, 214), clock, font=f(74), fill=WHT + (255,), anchor='lm')
    col = RED if bat <= 10 else YEL
    d.rounded_rectangle((74, 264, 132, 290), 5, outline=col + (255,), width=4); d.rectangle((132, 271, 138, 283), fill=col + (255,))
    d.rectangle((79, 269, 79 + int(48 * bat / 100), 285), fill=col + (255,)); d.text((150, 277), f'{bat}%', font=f(30), fill=col + (255,), anchor='lm')

KEYS = {  # plano: (texto, cor do sublinhado, início opcional)
    'S02_despertador': ('TOCA SOZINHO', YEL), 'S03_acorda': ('SEM ALARME', YEL), 'S04_celular': ('O CELULAR ACENDE', YEL),
    'S06_foto': ('MORREU HÁ 2 ANOS', RED), 'S08_chuva': ('COMEÇA A CHOVER', YEL), 'S09_bate': ('ALGUÉM NA PORTA', RED),
    'S10_corredor': ('É A VOZ DELA', RED), 'S11_olho': ('O OLHO MÁGICO', YEL), 'S12_avo': ('É ELA', RED), 'S13_casaco': ('O CASACO DO ENTERRO', RED),
    'S14_janela': ('A JANELA', YEL), 'S15_celia': ('A DONA CÉLIA', YEL), 'S16_marido': ('MORREU HÁ 8 ANOS', RED), 'S17_rua': ('CADA CASA, UMA VISITA', RED),
    'S18_macaneta': ('A MAÇANETA', RED), 'S19_vibra': ('VIBROU DE NOVO', YEL), 'S21_fresta': ('ELA ESTÁ NA PORTA', RED), 'S23_decide': ('VOCÊ DECIDE', YEL),
}
def keyword(d, s, col, k):
    fo = f(60); w = d.textlength(s, font=fo)
    text(d, W / 2, 392, s, WHT, 60, k); d.rectangle((W / 2 - w / 2, 470, W / 2 + w / 2, 480), fill=col + (int(255 * k),))

def stamp(im, s, x, y, ang, k, col=RED, px=96, w=560):
    lay = Image.new('RGBA', (w, 220), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((12, 12, w - 12, 208), 26, outline=col + (int(255 * k),), width=12, fill=(255, 255, 255, int(28 * k)))
    dd.text((w / 2, 110), s, font=f(px), fill=col + (int(255 * k),), anchor='mm', stroke_width=5, stroke_fill=INK + (int(255 * k),))
    sc = 1.25 - 0.25 * k; lay = lay.resize((int(w * sc), int(220 * sc)), Image.BICUBIC).rotate(ang, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
def pop(t, t0, d=0.12): return max(0.0, min(1.0, (t - t0) / d))

def shot_of(t):
    fr = int(round(t * P.FPS))
    return next((s for s in P.SHOTS if s.a <= fr < s.b), P.SHOTS[-1])

def badge(d, k):
    s = 'A VISITA · EP. 1'; fo = f(46); w = d.textlength(s, font=fo); x0 = (W - w) / 2 - 36
    d.rounded_rectangle((x0, 390, x0 + w + 72, 470), 40, fill=YEL + (int(240 * k),), outline=INK + (int(255 * k),), width=5)
    d.text((W / 2, 430), s, font=fo, fill=INK + (int(255 * k),), anchor='mm')
    text(d, W / 2, 492, 'no final, você decide', YEL, 50, k)

# ---- a tela do celular (app de mensagens genérico) ----
MSGS = [(10.2, 'não abre a porta'), (15.4, 'ela não entra sem\nser convidada'), (55.0, 'essa aí na porta\nnão sou eu')]
def phone(im, t, k=1.0):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = 210, 330, 870, 1420
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 10, y0 + 24, x1 + 10, y1 + 24), 80, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    d.rounded_rectangle((x0, y0, x1, y1), 80, fill=(22, 24, 32, 255), outline=INK + (255,), width=10)
    sx0, sy0, sx1, sy1 = x0 + 26, y0 + 30, x1 - 26, y1 - 30
    d.rounded_rectangle((sx0, sy0, sx1, sy1), 58, fill=(236, 230, 222, 255))
    d.rounded_rectangle((sx0, sy0, sx1, sy0 + 160), 58, fill=(58, 64, 82, 255)); d.rectangle((sx0, sy0 + 100, sx1, sy0 + 160), fill=(58, 64, 82, 255))
    d.rounded_rectangle((W / 2 - 70, sy0 + 16, W / 2 + 70, sy0 + 40), 12, fill=(10, 10, 14, 255))
    d.ellipse((sx0 + 34, sy0 + 62, sx0 + 120, sy0 + 148), fill=(196, 192, 204, 255), outline=WHT + (255,), width=4)
    d.text((sx0 + 77, sy0 + 105), 'V', font=f(44), fill=(70, 66, 80, 255), anchor='mm')
    d.text((sx0 + 142, sy0 + 88), 'Vó ❤', font=f(44), fill=WHT + (255,), anchor='lm') if False else d.text((sx0 + 142, sy0 + 88), 'Vó', font=f(46), fill=WHT + (255,), anchor='lm')
    hx, hy = sx0 + 142 + d.textlength('Vó ', font=f(46)) + 16, sy0 + 90   # coração desenhado (a fonte não tem o símbolo)
    d.ellipse((hx - 16, hy - 14, hx, hy + 2), fill=(235, 70, 90, 255)); d.ellipse((hx, hy - 14, hx + 16, hy + 2), fill=(235, 70, 90, 255))
    d.polygon([(hx - 16, hy - 4), (hx + 16, hy - 4), (hx, hy + 18)], fill=(235, 70, 90, 255))
    typing = t >= P.W['digitando']
    d.text((sx0 + 142, sy0 + 132), 'digitando…' if typing else 'online', font=f(28), fill=(150, 230, 170, 255), anchor='lm')
    y = sy0 + 200
    d.text((W / 2, y), 'HOJE', font=f(24), fill=(140, 136, 130, 255), anchor='mm'); y += 50
    for t0, s in MSGS:
        if t < t0: continue
        kk = pop(t, t0, 0.18); lines = s.split('\n'); fo = f(44); tw = max(d.textlength(l, font=fo) for l in lines)
        bh = 64 + 56 * len(lines); bw = tw + 70; bx = sx0 + 34; sc = 0.85 + 0.15 * kk
        col = (255, 228, 226) if t0 > 50 else (255, 255, 255)
        d.rounded_rectangle((bx, y, bx + bw * sc, y + bh * sc), 30, fill=col + (int(255 * kk),), outline=(200, 194, 186, int(255 * kk)), width=3)
        if kk > 0.6:
            for j, l in enumerate(lines): d.text((bx + 34, y + 24 + 56 * j), l, font=fo, fill=(30, 28, 36, 255), anchor='lt')
            d.text((bx + bw * sc - 18, y + bh * sc - 12), '03:0' + ('0' if t0 < 50 else '5'), font=f(22), fill=(140, 136, 130, 255), anchor='rb')
        y += bh + 30
    if typing:
        bx = sx0 + 34; d.rounded_rectangle((bx, y, bx + 170, y + 86), 30, fill=(255, 255, 255, 255), outline=(200, 194, 186, 255), width=3)
        for j in range(3):
            a = 0.35 + 0.65 * max(0.0, __import__('math').sin((t * 3.0 - j * 0.33) * 6.283))
            d.ellipse((bx + 38 + j * 40 - 12, y + 31, bx + 38 + j * 40 + 12, y + 55), fill=(110, 106, 120, int(255 * a)))
    d.rounded_rectangle((sx0 + 24, sy1 - 110, sx1 - 24, sy1 - 30), 40, fill=(255, 255, 255, 255), outline=(200, 194, 186, 255), width=3)
    d.text((sx0 + 60, sy1 - 70), 'Mensagem', font=f(32), fill=(160, 156, 150, 255), anchor='lm')
PHONE_SHOTS = ('S05_msg1', 'S07_msg2', 'S20_msg3', 'S22_digitando')

def peephole(im):   # anel preto do olho mágico, com borda suave
    m = Image.new('L', (W, H), 255); ImageDraw.Draw(m).ellipse((540 - 500, 980 - 500, 540 + 500, 980 + 500), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(28)); blk = Image.new('RGBA', (W, H), (4, 4, 8, 255)); blk.putalpha(m); im.alpha_composite(blk)

def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); n = 0
    s = shot_of(t)
    if s.name in ('S12_avo', 'S13_casaco'): peephole(im); d = ImageDraw.Draw(im)
    if s.name in PHONE_SHOTS: phone(im, t); d = ImageDraw.Draw(im)
    hud(d, t); n += 1
    if s.name in ('S01_quarto', 'S27_loop'): badge(d, 1.0)
    elif s.name in KEYS:
        kv = KEYS[s.name]; t0 = kv[2] if len(kv) > 2 else s.t0
        if t >= t0: keyword(d, kv[0], kv[1], env(t, t0, s.t1, 0.15, 0.1))
    if s.name in ('S01_quarto', 'S02_despertador', 'S03_acorda') and t < P.W['cel'] + 0.4 and int(t * 2.2) % 2 == 0:
        stamp(im, 'BIP BIP', 760 if s.name != 'S02_despertador' else 540, 1180 if s.name != 'S02_despertador' else 1250, -7, 1.0, RED, 92)
    if s.name == 'S09_bate':
        words = [w for w, tk in zip(['TOC', 'TOC', 'TOC'], [19.25, 19.7, 20.15]) if t >= tk]
        if words: stamp(im, ' '.join(words) + '!', 540, 1180, 6, pop(t, [19.25, 19.7, 20.15][len(words) - 1]), YEL, 96, 760)
    if s.name == 'S16_marido':
        k = env(t, 42.2, s.t1, 0.25, 0.1)
        if k > 0: d.ellipse(CIRCLE, outline=YEL + (int(255 * k),), width=10)
    if P.W['opcaoA'] <= t < P.W['opcaoB']: card(d, 60, 380, 1020, 620, RED, env(t, P.W['opcaoA'], P.W['opcaoB']), 'A', 'ABRE A PORTA\nPRA VÓ', 52)
    if P.W['opcaoB'] <= t < P.W['comenta']: card(d, 60, 380, 1020, 620, GRN, env(t, P.W['opcaoB'], P.W['comenta']), 'B', 'RESPONDE A\nMENSAGEM', 52)
    if P.W['comenta'] <= t < P.W['se']:
        k = env(t, P.W['comenta'], P.W['se'])
        card(d, 50, 380, 525, 560, RED, k, 'A', 'ABRIR', 50); card(d, 555, 380, 1030, 560, GRN, k, 'B', 'RESPONDER', 44)
        text(d, W / 2, 600, 'COMENTA A OU B', YEL, 84, k)
        if t >= 71.4:
            k2 = env(t, 71.4, P.W['se']); w2 = d.textlength('a mais comentada vira a PARTE 2', font=f(50))
            d.rounded_rectangle((W / 2 - w2 / 2 - 30, 708, W / 2 + w2 / 2 + 30, 792), 36, fill=(10, 12, 24, int(200 * k2)))
            text(d, W / 2, 720, 'a mais comentada vira a PARTE 2', WHT, 50, k2)
    return im, n
CIRCLE = (560, 560, 860, 960)   # ajustado depois dos quadros de conferência

def main():
    only = set(sys.argv[1:])
    mg = os.path.join(HERE, 'mg'); os.makedirs(mg, exist_ok=True)
    for s in P.SHOTS:
        if only and s.name not in only: continue
        dd = os.path.join(mg, s.name); os.makedirs(dd, exist_ok=True)
        for fr in s.frames:
            dst = os.path.join(dd, f'{fr:04d}.png')
            if os.path.lexists(dst): os.remove(dst)
            im, n = frame(fr / P.FPS); im.save(dst, compress_level=1)
        print(s.name, 'ok', len(s.frames), 'quadros')
if __name__ == '__main__': main()
