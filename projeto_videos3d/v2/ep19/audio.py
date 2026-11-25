#!/usr/bin/env python3
"""Som do vídeo 19 (A Noite Livre · Ep. 1) — regra do ESTILO §9: efeitos com presença, canal próprio.
Sons CC0 (assets/sfx_cc0) + sintetizados: zumbido da TV e do console instalando, a luz caindo (power down), grilos e vento no
sítio, cachorros latindo (param junto com a imagem), a TV ligando sozinha com chiado, som de conexão genérico (nenhum som de
fabricante), a almofada vibrando. Abafado dentro da sala.
Saída: v2/ep18/out/sfx.wav, music.wav, sfx_events.json."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 64.58; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(19)

def load(name, t0=0.0, d=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', os.path.join(S, name)] + (['-t', str(d)] if d else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
def loop(name, d):
    x = load(name); reps = int(np.ceil(d * SR / len(x))) + 1; return np.tile(x, (reps, 1))[:int(d * SR)]
def fade(x, a=0.05, b=0.3):
    x = x.copy(); na, nb = min(len(x), int(a * SR)), min(len(x), int(b * SR))
    x[:na] *= np.linspace(0, 1, na)[:, None]; x[len(x) - nb:] *= np.linspace(1, 0, nb)[:, None]; return x
sos = lambda k, f, o=2: butter(o, f, k, fs=SR, output='sos')
bp = lambda x, lo, hi: sosfilt(sos('bandpass', [lo, hi]), x, axis=0)
lp = lambda x, f: sosfilt(sos('lowpass', f), x, axis=0)
def env(d, a=0.003, k=6.0):
    t = np.arange(int(d * SR)) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-k * t)
def st(m, pan=0.0): return np.stack([m * np.sqrt((1 - pan) / 2), m * np.sqrt((1 + pan) / 2)], 1)
def tone(f, d, k=5.0, a=0.003): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, a, k)

sfx = np.zeros((N, 2)); mus = np.zeros((N, 2)); EV = []
def put(x, at, g=1.0, bus=None, tag=''):
    b = sfx if bus is None else bus; i = int(at * SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), N - i)
    if n > 0: b[i:i + n] += x[:n] * g
    if tag: EV.append((round(at, 2), tag))

# ---- sintetizados ----
def vibra(d=0.9):        # celular vibrando: 2 pulsos de zumbido 160 Hz com chacoalhar
    t = np.arange(int(d * SR)) / SR; gate = ((t % 0.45) < 0.28).astype(float)
    m = (np.sin(2 * np.pi * 160 * t) + 0.4 * np.sign(np.sin(2 * np.pi * 320 * t))) * gate
    return st(lp(m, 900) * 0.5)
def snap():              # encaixe magnético: clique seco + baque grave + tilintar metálico curto
    c = rng.standard_normal(int(0.02 * SR)) * env(0.02, 0.0005, 260)
    th = tone(70, 0.25, 18) * 0.9
    ring = sum(tone(f, 0.35, 16) * g for f, g in [(2350, 0.18), (3720, 0.1), (5100, 0.06)])
    m = np.zeros(int(0.4 * SR)); m[:len(c)] += c * 1.4; m[:len(th)] += th; m[:len(ring)] += ring
    return st(m)
def bipe(f=2200, d=0.09): return st(tone(f, d, 8) * 0.5)
def erro():              # bipe de erro duplo grave
    m = np.zeros(int(0.5 * SR)); a = np.sign(tone(330, 0.16, 3)) * env(0.16, 0.002, 4) * 0.35
    m[:len(a)] += a; m[int(0.22 * SR):int(0.22 * SR) + len(a)] += a; return st(lp(m, 2500))
def chiado(d):           # rádio sintonizando: ruído em banda com varredura
    x = bp(rng.standard_normal(int(d * SR)), 600, 3200) * 0.25
    t = np.arange(len(x)) / SR; sw = np.sin(2 * np.pi * (300 + 900 * t / d) * t) * 0.12 * (t > d * 0.6)
    return fade(st(x + sw), 0.05, 0.25)
def mensagem(): return st(np.concatenate([tone(1320, 0.09, 14), tone(1760, 0.18, 10)]) * 0.45)
def carga():             # carga começando: arpejo ascendente suave
    m = np.zeros(int(0.9 * SR))
    for i, f in enumerate((523, 659, 784, 1047)): x = tone(f, 0.5, 6) * 0.3; m[int(i * 0.09 * SR):int(i * 0.09 * SR) + len(x)] += x
    return st(m)
def lanterna(): return load('clique_3.flac')
def relogio(d, bpm=120):
    m = np.zeros(int(d * SR)); step = 60 / bpm
    for k in range(int(d / step)):
        x = tone(1900 if k % 2 else 1500, 0.03, 60) * 0.5; i = int(k * step * SR); m[i:i + len(x)] += x[:len(m) - i]
    return st(m)

# ---- sintetizados v2: impactos de título, power down/up, sinal perdido, sino do CTA ----
def boom(d=1.4, f0=58, g=1.0):      # grave de impacto (sub com queda de afinação)
    t = np.arange(int(d * SR)) / SR; f = f0 * (1 + 0.6 * np.exp(-t * 9))
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 3.2) * g)
def riser(d=0.45):                  # whoosh de entrada (ruído filtrado que sobe)
    x = bp(rng.standard_normal(int(d * SR)), 300, 6000); t = np.linspace(0, 1, len(x))
    return fade(st(x * t ** 2.2 * 0.5), 0.01, 0.03)
def hit(name='impacto_hit_01.flac', g=1.0, f0=58):
    h = load(name); b = boom(1.2, f0); m = np.zeros((max(len(h), len(b)), 2)); m[:len(h)] += h * g; m[:len(b)] += b * 0.8; return m
def sweep(f0, f1, d, g=0.4):        # power down (f0>f1) / power up (f0<f1): dente de serra filtrado
    t = np.arange(int(d * SR)) / SR; f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    m = lp(((ph / np.pi) % 2 - 1) * 0.5 + np.sin(ph) * 0.5, 1800) * g
    return fade(st(m), 0.02, 0.15)
def sinal_perdido(): return st(np.concatenate([tone(f, 0.14, 9) * 0.4 for f in (988, 784, 523)]))
def sino(): return st(sum(tone(f, 1.6, 2.6) * g for f, g in [(1318.5, 0.35), (2637, 0.12), (3956, 0.05)]))
def ondas_cliques(t0, n=9, dt=0.11):  # luzes acendendo em onda pela rua: cliques espalhados no estéreo
    for k in range(n):
        c = load(('clique_1.flac', 'clique_3.flac', 'clique_5.flac', 'clique_7.flac')[k % 4]); pan = -0.8 + 1.6 * k / (n - 1)
        put(np.stack([c[:, 0] * np.sqrt((1 - pan) / 2), c[:, 1] * np.sqrt((1 + pan) / 2)], 1), t0 + k * dt, 1.0)

# ---- sintetizados v2: impactos de título, power down/up, sinal perdido, sino do CTA ----
def boom(d=1.4, f0=58, g=1.0):      # grave de impacto (sub com queda de afinação)
    t = np.arange(int(d * SR)) / SR; f = f0 * (1 + 0.6 * np.exp(-t * 9))
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 3.2) * g)
def riser(d=0.45):                  # whoosh de entrada (ruído filtrado que sobe)
    x = bp(rng.standard_normal(int(d * SR)), 300, 6000); t = np.linspace(0, 1, len(x))
    return fade(st(x * t ** 2.2 * 0.5), 0.01, 0.03)
def hit(name='impacto_hit_01.flac', g=1.0, f0=58):
    h = load(name); b = boom(1.2, f0); m = np.zeros((max(len(h), len(b)), 2)); m[:len(h)] += h * g; m[:len(b)] += b * 0.8; return m
def sweep(f0, f1, d, g=0.4):        # power down (f0>f1) / power up (f0<f1): dente de serra filtrado
    t = np.arange(int(d * SR)) / SR; f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    m = lp(((ph / np.pi) % 2 - 1) * 0.5 + np.sin(ph) * 0.5, 1800) * g
    return fade(st(m), 0.02, 0.15)
def sinal_perdido(): return st(np.concatenate([tone(f, 0.14, 9) * 0.4 for f in (988, 784, 523)]))
def sino(): return st(sum(tone(f, 1.6, 2.6) * g for f, g in [(1318.5, 0.35), (2637, 0.12), (3956, 0.05)]))
def ondas_cliques(t0, n=9, dt=0.11):  # luzes acendendo em onda pela rua: cliques espalhados no estéreo
    for k in range(n):
        c = load(('clique_1.flac', 'clique_3.flac', 'clique_5.flac', 'clique_7.flac')[k % 4]); pan = -0.8 + 1.6 * k / (n - 1)
        put(np.stack([c[:, 0] * np.sqrt((1 - pan) / 2), c[:, 1] * np.sqrt((1 + pan) / 2)], 1), t0 + k * dt, 1.0)



import sys; sys.path.insert(0, HERE); import plan as P
# planos de fora (rua): som cheio; dentro da sala: abafado
EXT = ('S09', 'S11', 'S12', 'S17', 'S18', 'S19')
def ext_mask():
    g = np.full(N, 0.3)
    for s in P.SHOTS:
        if s.name.startswith(EXT): g[int(s.t0 * SR):int(s.t1 * SR)] = 1.0
    k = int(0.06 * SR); return np.convolve(g, np.ones(k) / k, 'same')
def muffle(x, g): lo = lp(x, 420); return x * g[:, None] + lo * (1 - g[:, None]) * 0.9
def grilos(d):
    n = int(d * SR); out = np.zeros((n, 2)); t = np.arange(n) / SR
    for k in range(4):
        f = 4300 + 180 * k; rate = 2.6 + 0.5 * k; ph = rng.uniform(0, 6)
        gate = ((np.sin(2 * np.pi * rate * t + ph) > 0.55) * (np.sin(2 * np.pi * 38 * t) > 0)).astype(float)
        m = np.sin(2 * np.pi * f * t) * gate * 0.035; pan = -0.7 + 0.45 * k
        out[:, 0] += m * np.sqrt((1 - pan) / 2); out[:, 1] += m * np.sqrt((1 + pan) / 2)
    return out
def cidade(d):          # cidade ao longe: rumor grave contínuo
    x = rng.standard_normal(int(d * SR)); m = lp(x, 160) * 1.4 + bp(x, 200, 700) * 0.15
    return np.stack([m, np.roll(m, 700)], 1) * 0.35
def latido(f0=560):
    d = 0.22; t = np.arange(int(d * SR)) / SR; f = f0 * (1.25 - 0.45 * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR; m = (np.sign(np.sin(ph)) * 0.5 + np.sin(ph)) * env(d, 0.004, 9)
    m = bp(m + rng.standard_normal(len(t)) * 0.35 * env(d, 0.002, 14), 300, 2600); return st(m * 0.9)
PARA = 46.78; BARK0 = 24.59
def bark_at(t): return t < PARA and (int(t * 4.6) % 3 != 2)   # igual ao story.ts (barkAt)
def hum(d, f=60, g=0.03):
    t = np.arange(int(d * SR)) / SR; m = np.sin(2 * np.pi * f * t) * 0.6 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    return fade(st(bp(rng.standard_normal(len(t)), 600, 3000) * 0.15 + m * g), 0.3, 0.3)
def clac():             # tranca girando: dois cliques metálicos + baque
    m = np.zeros(int(0.35 * SR))
    for i0, f in ((0.0, 2600), (0.09, 3400)):
        c = bp(rng.standard_normal(int(0.03 * SR)), f - 800, f + 1200) * env(0.03, 0.0004, 160); i = int(i0 * SR); m[i:i + len(c)] += c * 1.3
    th = tone(110, 0.2, 22) * 0.5; m[int(0.09 * SR):int(0.09 * SR) + len(th)] += th; return st(m)
def cortina(d=1.2):     # argolas correndo no varão + pano
    x = bp(rng.standard_normal(int(d * SR)), 1500, 7000) * 0.12; t = np.arange(len(x)) / SR
    x *= (0.4 + 0.6 * (np.sin(2 * np.pi * 9 * t) > 0)); return fade(st(x), 0.05, 0.3)
def vento_rabo(d):      # abanar de rabo: sopro suave ritmado (3,2/s, igual à imagem)
    x = bp(rng.standard_normal(int(d * SR)), 250, 1200); t = np.arange(len(x)) / SR
    return st(x * (0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t)) ** 2 * 0.12)

g = ext_mask()
amb = grilos(END) + cidade(END)
sfx += muffle(amb, g) * 0.25
EV += [(0.0, 'noite: grilos + cidade ao longe (abafado dentro da sala)')]
# a TV ligada na sala (zumbido baixo), só nos planos de dentro
for s in P.SHOTS:
    if not s.name.startswith(EXT): put(hum(s.t1 - s.t0, 60, 0.02), s.t0, 0.6)
EV.append((0.0, 'TV ligada: zumbido baixo nos planos da sala'))
put(cortina(1.4), 16.9, 0.9, tag='a cortina fechando')
put(clac(), 19.02, 1.2, tag='CLAC: tranca')
# o Thor latindo: começa a ser ouvido no portão aberto; cheio na rua, abafado dentro; para em "para de latir"
prev = False
for i in range(int(BARK0 * 30), int(PARA * 30)):
    t = i / 30; on = bark_at(t)
    if on and not prev:
        gi = g[min(N - 1, int(t * SR))]; put(lp(latido(560), 3200 if gi > 0.6 else 650), t, 0.32 * (0.3 + 0.7 * gi))
    prev = on
EV.append((BARK0, 'Thor latindo (igual à imagem) até "para de latir" (46,78 s)'))
put(boom(0.9, 50, 0.6), PARA + 0.02, 0.3, tag='para de latir: silêncio seco')
put(vento_rabo(50.53 - 47.76), 47.76, 0.8, tag='rabo abanando')
# impactos de título
CORTES = [s.t0 for s in P.SHOTS[1:]]
for i, c in enumerate(CORTES): put(load(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), c - 0.06, 0.2)
for t, nm, f0, g2 in [(27.3, 'impacto_hit_01.flac', 58, 0.26), (44.62, 'impacto_hit_03.flac', 52, 0.3), (52.1, 'impacto_hit_03.flac', 62, 0.26),
                      (54.6, 'impacto_hit_03.flac', 66, 0.22), (58.2, 'impacto_metal_hit_02.flac', 55, 0.28)]:
    put(riser(), t - 0.45, 0.35); put(hit(nm, 0.8, f0), t, g2, tag='título: whoosh + impacto')
put(bipe(1760, 0.08), 60.04, 1.3, tag='a mais comentada: pop')
put(load('whoosh_ar.flac', 0, 0.8), 62.55, 0.4, tag='E se...: whoosh do loop')

def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 16.2, (73.4, 110, 146.8, 174.6)), (16.2, 27.3, (69.3, 103.8, 138.6, 164.8)), (27.3, 45.4, (65.4, 98, 130.8, 155.6)),
                 (45.4, 58.2, (61.7, 92.5, 123.5, 146.8)), (58.2, END, (73.4, 110, 146.8, 185))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)
pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
