"""Camada de motion graphics do vídeo 10, desenhada direto em 1080x1920 (nativo; o 3D por baixo é que é ampliado de 720x1280).
Lê o plan.py (lista `mg` de cada plano) e as âncoras 3D projetadas em events/<plano>.json (gravadas pelo render.py).
Uso:
  python3 v2/ep10/mograph.py all [PLANOS...]      -> v2/ep10/mg/<plano>/NNNN.png (RGBA, transparente onde não há gráfico)
  python3 v2/ep10/mograph.py still PLANO F base.png saida.png   -> compõe um quadro de teste sobre um still 3D"""
import os, sys, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf')
W, H = 1080, 1920
# zonas seguras do 9:16 (TikTok, Reels, Shorts): abas em cima, botões na direita do meio para baixo, legenda e descrição embaixo
SAFE = dict(top=230, bottom=1180, left=60, right_mid=930)
_fc = {}
def font(sz):
    sz = max(8, int(round(sz)))
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

# ------------------------------------------------------------------ curvas de tempo
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_back(u, s=1.9):
    u = clamp(u) - 1; return 1 + (s + 1) * u ** 3 + s * u ** 2
def out_cubic(u): u = clamp(u); return 1 - (1 - u) ** 3
def inout(u): u = clamp(u); return u * u * (3 - 2 * u)
def life(T, t_on, t_off, fade=0.14):
    """alfa de entrada/saída."""
    if T < t_on: return 0.0
    return clamp((T - t_on) / 0.06) * (1 - clamp((T - t_off) / fade))

# ------------------------------------------------------------------ desenho de texto como sprite
_sprite = {}
def text_sprite(text, size, color, stroke=None, glow=True):
    k = (text, int(size), color, stroke)
    if k in _sprite: return _sprite[k]
    f = font(size); sw = stroke if stroke is not None else max(3, int(size * 0.06))
    bb = f.getbbox(text, stroke_width=sw); w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((20 - bb[0], 20 - bb[1]), text, font=f, fill=color + (255,), stroke_width=sw, stroke_fill=(12, 12, 16, 255))
    if glow:
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((20 - bb[0], 26 - bb[1]), text, font=f, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(8)); sh.alpha_composite(im); im = sh
    _sprite[k] = im; return im

def paste(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.003 or scale <= 0.01: return
    if abs(scale - 1) > 1e-3: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def anim_scale(T, t_on, kind):
    u = (T - t_on)
    if kind == 'slam': return 1 + 0.9 * (1 - out_cubic(u / 0.16))          # chega grande e "bate"
    if kind == 'slide': return 1.0
    return out_back(u / 0.22)                                                # pop

def rrect(size, color, radius=24, outline=None, ow=0):
    im = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=color, outline=outline, width=ow); return im

def label_box(text, size, color, bg=(14, 16, 22, 225), fg=None):
    f = font(size); bb = f.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = int(size * 0.5); box = rrect((tw + 2 * pad, th + int(1.3 * pad)), bg, radius=int(size * 0.45))
    ImageDraw.Draw(box).text((pad - bb[0], int(0.65 * pad) - bb[1]), text, font=f, fill=(fg or color) + (255,))
    # filete colorido embaixo
    ImageDraw.Draw(box).rectangle((pad, box.height - 7, box.width - pad, box.height - 3), fill=color + (255,))
    return box

# ------------------------------------------------------------------ elementos
def anchor_xy(ev, name):
    a = (ev.get('anc') or {}).get(name)
    if not a: return None
    return a[0] * W, a[1] * H

def el_title(cv, T, ev, e):
    _, text, t_on, t_off, (x, y), size, color, kind = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    sp = text_sprite(text, size, color); s = anim_scale(T, t_on, kind)
    dx = -260 * (1 - out_cubic((T - t_on) / 0.2)) if kind == 'slide' else 0
    paste(cv, sp, x + dx, y, s, al)

def el_counter(cv, T, ev, e):
    _, fmt, v0, v1, ta, tb, (x, y), size, color, t_on, t_off = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    v = v0 + (v1 - v0) * inout((T - ta) / max(tb - ta, 1e-3))
    txt = fmt.format(v)
    sp = text_sprite(txt, size, color); paste(cv, sp, x, y, out_back((T - t_on) / 0.2), al)

def el_atag(cv, T, ev, e):
    _, text, anc, t_on, t_off, size, color = e
    al = life(T, t_on, t_off); xy = anchor_xy(ev, anc)
    if al <= 0 or not xy: return
    box = label_box(text, size, color); x, y = xy
    y = clamp(y - box.height / 2 - 18, SAFE['top'], SAFE['bottom'])
    x = clamp(x, box.width / 2 + SAFE['left'], (SAFE['right_mid'] if y > 600 else W - SAFE['left']) - box.width / 2)
    paste(cv, box, x, y, out_back((T - t_on) / 0.2), al)
    d = ImageDraw.Draw(cv); s = out_back((T - t_on) / 0.2)
    if s > 0.5 and al > 0.5:
        ty = y + box.height / 2 * s; d.polygon([(xy[0] - 14, ty - 2), (xy[0] + 14, ty - 2), (xy[0], ty + 18)], fill=color + (int(255 * al),))

def el_badge(cv, T, ev, e):
    _, text, t_on, t_off, (x, y), size, color, t_cut = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    f = font(size); bb = f.getbbox(text); pad = int(size * 0.45)
    box = rrect((bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + int(1.4 * pad)), color + (255,), radius=int(size * 0.35))
    ImageDraw.Draw(box).text((pad - bb[0], int(0.7 * pad) - bb[1]), text, font=f, fill=(14, 14, 18, 255))
    s = out_back((T - t_on) / 0.22)
    if t_cut is None or T < t_cut:
        paste(cv, box, x, y, s, al)
        if t_cut is not None and T > t_cut - 0.12:                                 # linha de corte se desenhando
            u = clamp((T - (t_cut - 0.12)) / 0.12); d = ImageDraw.Draw(cv)
            x0, y0 = x - box.width / 2 - 30, y + box.height / 2 + 10; x1, y1 = x + box.width / 2 + 30, y - box.height / 2 - 10
            d.line([(x0, y0), (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)], fill=(255, 255, 255, 255), width=10)
    else:                                                                          # cortado: as duas metades se separam e caem
        u = T - t_cut; half = box.width // 2
        L_ = box.crop((0, 0, half, box.height)); R_ = box.crop((half, 0, box.width, box.height))
        g = 900 * u * u
        paste(cv, L_, x - half / 2 - 60 * u, y + g * 0.6, 1.0, al * (1 - clamp(u / 0.9)), rot=18 * u)
        paste(cv, R_, x + half / 2 + 80 * u, y + g, 1.0, al * (1 - clamp(u / 0.9)), rot=-26 * u)

def el_ring(cv, T, ev, e):
    _, anc, r, t_on, t_off, color = e
    al = life(T, t_on, t_off); xy = anchor_xy(ev, anc)
    if al <= 0 or not xy: return
    u = out_cubic((T - t_on) / 0.35); x, y = xy; rr = r * (1.0 + 0.03 * math.sin(T * 6))
    d = ImageDraw.Draw(cv); d.arc((x - rr, y - rr, x + rr, y + rr), -90, -90 + 360 * u, fill=color + (int(255 * al),), width=12)

def el_slider(cv, T, ev, e):
    _, label, v0, v1, ta, tb, (x, y), t_on, t_off = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    pw, ph = 860, 190; panel = rrect((pw, ph), (14, 16, 22, 215), 30)
    d = ImageDraw.Draw(panel); d.text((40, 26), label, font=font(48), fill=(255, 255, 255, 255))
    v = v0 + (v1 - v0) * out_cubic((T - ta) / max(tb - ta, 1e-3))
    d.rounded_rectangle((40, 110, pw - 40, 150), 20, fill=(60, 64, 74, 255))
    d.rounded_rectangle((40, 110, 40 + (pw - 80) * v, 150), 20, fill=P.YEL + (255,))
    if T > ta:
        q = text_sprite('?', 120, P.YEL); panel.alpha_composite(q.resize((q.width // 2, q.height // 2)), (pw - 120, 0))
        ax = pw - 300; d.rectangle((ax - 9, 34, ax + 9, 70), fill=P.RED + (255,)); d.polygon([(ax - 26, 66), (ax + 26, 66), (ax, 98)], fill=P.RED + (255,))
    paste(cv, panel, x, y, out_back((T - t_on) / 0.22), al)

def el_price(cv, T, ev, e):
    _, anc, v0, v1, ta, tb, t_on, t_off = e
    al = life(T, t_on, t_off); xy = anchor_xy(ev, anc)
    if al <= 0 or not xy: return
    v = v0 + (v1 - v0) * inout((T - ta) / (tb - ta)); v = math.floor(v * 100 + 0.5) / 100
    col = P.GREEN if T > ta else (255, 236, 160)
    txt = ('R$ %.2f' % v).replace('.', ',')
    sz = 120; sp = text_sprite(txt, sz, col, stroke=4, glow=False)
    panel = rrect((sp.width + 60, sp.height + 30), (6, 12, 10, 235), 22, outline=(60, 90, 70, 255), ow=4); panel.alpha_composite(sp, (30, 15))
    d = ImageDraw.Draw(panel); d.text((34, 6), 'GASOLINA / LITRO', font=font(26), fill=(150, 200, 160, 255))
    x, y = xy; y = clamp(y, 700, 1100)
    paste(cv, panel, x, y, out_back((T - t_on) / 0.22), al)

def el_rewind(cv, T, ev, e):
    _, t_on, t_off, (x, y) = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    im = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((10, 10, 290, 290), fill=(14, 16, 22, 220), outline=P.YEL + (255,), width=10)
    for dx in (0, 85):
        d.polygon([(190 - dx, 90), (190 - dx, 210), (105 - dx, 150)], fill=P.YEL + (255,))
    paste(cv, im, x, y, out_back((T - t_on) / 0.22) * (1 + 0.05 * math.sin((T - t_on) * 12)), al, rot=0)

def el_share(cv, T, ev, e):
    _, t_on, t_off = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    pw, ph = 940, 330; panel = rrect((pw, ph), (14, 16, 22, 225), 30); d = ImageDraw.Draw(panel)
    d.text((40, 24), 'O MESMO IMPOSTO, NA RENDA DE CADA UM', font=font(38), fill=(255, 255, 255, 255))
    u = out_cubic((T - t_on - 0.15) / 0.5)
    for i, (lab, frac) in enumerate((('R$ 1 mil', 1.0), ('R$ 100 mil', 0.01))):
        y0 = 110 + i * 100; d.text((40, y0 + 4), lab, font=font(36), fill=(220, 224, 232, 255))
        bx0, bx1 = 300, pw - 40; d.rounded_rectangle((bx0, y0, bx1, y0 + 56), 14, fill=(60, 64, 74, 255))
        wfill = max(8, (bx1 - bx0) * 0.55 * frac * u) if frac < 1 else (bx1 - bx0) * 0.55 * u
        d.rounded_rectangle((bx0, y0, bx0 + wfill, y0 + 56), 14, fill=P.RED + (255,))
    d.text((pw - 200, ph - 50), 'ilustração', font=font(26), fill=(160, 166, 178, 255))
    paste(cv, panel, 540, 360, out_back((T - t_on) / 0.22), al)

def el_quem(cv, T, ev, e):
    _, tq, ts, td = e
    if T >= tq:
        sp = text_sprite('QUANTO?', 150, P.WHITE); al = 1 - 0.55 * clamp((T - ts) / 0.2)
        paste(cv, sp, 540, 470, anim_scale(T, tq, 'pop'), al)
        if T >= ts:
            u = out_cubic((T - ts) / 0.18); d = ImageDraw.Draw(cv); x0, x1 = 540 - sp.width / 2 + 20, 540 + sp.width / 2 - 20
            d.line([(x0, 480), (x0 + (x1 - x0) * u, 470)], fill=P.RED + (255,), width=18)
    if T >= td:
        sp = text_sprite('DE QUEM?', 190, P.YEL); paste(cv, sp, 540, 720, anim_scale(T, td, 'slam'), 1.0)

def el_chips(cv, T, ev, e):
    _, names, t0, dt, y = e
    sizes = [label_box(n, 54, P.YEL, bg=(14, 16, 22, 230)) for n in names]
    gap = 26; rows = [sizes[:3], sizes[3:]]; k = 0
    for r, row in enumerate(rows):
        tw = sum(b.width for b in row) + gap * (len(row) - 1); x = 540 - tw / 2
        for b in row:
            t_on = t0 + dt * k; k += 1
            if T >= t_on: paste(cv, b, x + b.width / 2, y + r * 120, out_back((T - t_on) / 0.2), life(T, t_on, 99))
            x += b.width + gap

def el_darrow(cv, T, ev, e):
    _, t_on, t_off, (x, y), color = e
    al = life(T, t_on, t_off)
    if al <= 0: return
    im = Image.new('RGBA', (220, 340), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((80, 10, 140, 200), fill=color + (255,), outline=(12, 12, 16, 255), width=6); d.polygon([(20, 190), (200, 190), (110, 330)], fill=color + (255,), outline=(12, 12, 16, 255))
    paste(cv, im, x, y + 40 * out_cubic((T - t_on) / 0.3), out_back((T - t_on) / 0.2), al)

ELS = dict(darrow=el_darrow, title=el_title, counter=el_counter, atag=el_atag, badge=el_badge, ring=el_ring, slider=el_slider, price=el_price,
           rewind=el_rewind, share=el_share, quem=el_quem, chips=el_chips)

# ------------------------------------------------------------------ transições (faixa diagonal amarela nas viradas de bloco)
WIPES = {'B1', 'C1', 'E1', 'F1', 'G2'}
def wipe(cv, T, shot):
    if shot.name not in WIPES: return
    u = (T - shot.t0 + 0.04) / 0.2
    if not (0 <= u <= 1): return
    d = ImageDraw.Draw(cv); x = -900 + 3000 * out_cubic(u); bw = 380
    d.polygon([(x, 0), (x + bw, 0), (x + bw - 700, H), (x - 700, H)], fill=P.YEL + (255,))
    d.polygon([(x + bw + 40, 0), (x + bw + 110, 0), (x + bw - 590, H), (x + bw - 660, H)], fill=(255, 255, 255, 220))

def render_frame(shot, ev):
    T = ev['T']; cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for e in shot.mg: ELS[e[0]](cv, T, ev, e)
    wipe(cv, T, shot)
    return cv

def load_events(shot):
    p = os.path.join(HERE, 'events', f'{shot.name}.json')
    if os.path.exists(p): return {e['f']: e for e in json.load(open(p))['frames']}
    return {}

def run_all(names=None):
    for s in P.SHOTS:
        if names and s.name not in names: continue
        evs = load_events(s); out = os.path.join(HERE, 'mg', s.name); os.makedirs(out, exist_ok=True)
        for f in s.frames:
            ev = evs.get(f, dict(f=f, T=f / P.FPS)); render_frame(s, ev).save(os.path.join(out, f'{f:04d}.png'), compress_level=3)
        print(s.name, 'ok', len(s.frames), flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'all': run_all(sys.argv[2:])
    elif sys.argv[1] == 'still':
        s = P.BY_NAME[sys.argv[2]]; f = int(sys.argv[3]); ev = load_events(s).get(f, dict(f=f, T=f / P.FPS))
        base = Image.open(sys.argv[4]).convert('RGBA').resize((W, H), Image.LANCZOS); base.alpha_composite(render_frame(s, ev)); base.convert('RGB').save(sys.argv[5])
