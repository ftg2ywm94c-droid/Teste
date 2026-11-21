#!/usr/bin/env python3
"""Som do vídeo 15 (O último ônibus, Parte 2) — regra do ESTILO §9: efeitos com presença, canal próprio.
Sons reais CC0 (assets/sfx_cc0) + sintetizados: motor diesel e ruído de pista (mais alto dentro), zumbido das lâmpadas,
toque genérico do celular e vibração, notificações, freio com chiado de ar, porta pneumática, poste piscando, contagem.
Saída: v2/ep15/out/sfx.wav, music.wav, sfx_events.json."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 75.96; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(15)

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


# ---- vídeo 15 ----
import sys; sys.path.insert(0, HERE); import plan as P
OUTSIDE = ('S02', 'S03', 'S04', 'S11', 'S12', 'S13', 'S19', 'S20', 'S21')
GARAGE_T = 38.08
def mask(inside_g, outside_g):
    g = np.zeros(N)
    for s in P.SHOTS:
        a, b = int(s.t0 * SR), int(s.t1 * SR); g[a:b] = outside_g if s.name.startswith(OUTSIDE) else inside_g
    k = int(0.05 * SR); return np.convolve(g, np.ones(k) / k, 'same')
# movimento do ônibus (0 parado .. 1 a 8 m/s), igual ao story.ts: parado até 2,2 s, acelera, anda; na garagem freia até parar em 45,58
T = np.arange(N) / SR
speed = np.clip((T - 2.2) * 1.8 / 8.0, 0, 1)
sg = (T - GARAGE_T) / 7.5
speed = np.where(T >= GARAGE_T, np.clip(1.6 * (1 - sg), 0, 1), speed)
def motor():
    """diesel: fundamental 32-55 Hz com harmônicos em dente de serra, rugido filtrado, e ruído de pista proporcional à velocidade"""
    rpm = 0.35 + 0.65 * speed; f = 30 + 26 * rpm + 1.5 * np.sin(2 * np.pi * 0.6 * T)
    ph = np.cumsum(f) / SR; saw = (ph % 1) * 2 - 1
    eng = lp(saw, 260) * 0.9 + lp(np.sign(np.sin(2 * np.pi * ph * 2)), 180) * 0.25
    eng *= 0.8 + 0.2 * np.sin(2 * np.pi * ph * 0.5)
    road = bp(rng.standard_normal(N), 70, 700) * 1.6 * speed ** 1.2 + bp(rng.standard_normal(N), 900, 3000) * 0.15 * speed
    return eng * (0.6 + 0.4 * rpm), road
eng, road = motor()
gin, gout = mask(1.0, 0.35), mask(0.0, 1.0)
# o motor desliga quando ele para na garagem (só o tique do motor esfriando depois)
engine_on = np.where(T < 46.2, 1.0, np.clip(1 - (T - 46.2) / 0.6, 0, 1))
bed = (eng * engine_on * (0.55 * gin + 0.5 * gout) + road * (0.7 * gin + 0.35 * gout))
sfx += st(bed) * 0.15
EV.append((0.0, 'motor diesel + ruído de pista (segue a velocidade; desliga na garagem)'))
put(boom(0.7, 45, 0.6), 46.2, 0.35, tag='motor desliga')
rat = np.zeros(N)
for p0 in rng.integers(0, N - 2000, 900):
    if speed[p0] > 0.3: Lr = int(rng.integers(200, 900)); rat[p0:p0 + Lr] += bp(rng.standard_normal(Lr) * np.exp(-np.arange(Lr) / (Lr / 5)), 1500, 6000) * 0.5
sfx += st(rat * gin * speed) * 0.2
# lâmpadas do teto: zumbido que perde força a cada lâmpada que apaga (da frente pro fundo), com clique e estalo
OFFS = [16.29 + (6 - k) * 0.52 for k in range(6, 0, -1)]
lamps = np.full(N, 7.0)
for a in OFFS: lamps -= (T >= a)
hum = (np.sin(2 * np.pi * 120 * T) * 0.6 + np.sin(2 * np.pi * 240 * T) * 0.25 + np.sin(2 * np.pi * 360 * T) * 0.1) * 0.06 * (lamps / 7)
sfx += st(hum * gin)
for i, a in enumerate(OFFS):
    put(load(('clique_1.flac', 'clique_3.flac', 'clique_5.flac', 'clique_7.flac')[i % 4]), a, 0.9); put(boom(0.25, 90, 0.4), a, 0.25)
EV.append((OFFS[0], 'as luzes apagam uma por uma: clique + baque a cada lâmpada'))
# a lâmpada do fundo piscando (planos 9 e 10): estalos elétricos
def back_flick(t):
    n = int(t * 9); h = (np.sin((n + 77) * 127.1 + 31.7) * 43758.5453) % 1
    return h < 0.18 or (36.3 < t < 36.48)
prev = False
for i in range(int(30.58 * 30), int(38.08 * 30)):
    t = i / 30; off = back_flick(t); a = int(t * SR)
    if off != prev and a + 600 < N: c = bp(rng.standard_normal(600) * np.exp(-np.arange(600) / 120), 1500, 7000) * 0.6; sfx[a:a + 600] += st(c) * 0.25
    prev = off
put(fade(loop('zumbido_eletrico.flac', 7.4), 0.3, 0.3), 30.6, 0.18, tag='a lâmpada do fundo zumbindo e piscando')
# rua: grilos (planos de fora na rua), some na rua escura e na garagem
cr = loop('grilos_loop.flac', END); street = np.where(T < 14.5, 1.0, 0.0) * np.clip(gout + 0.5 * gin, 0, 1)
street = np.convolve(street, np.ones(9600) / 9600, 'same'); sfx += cr * street[:, None] * 0.3
EV.append((0.0, 'grilos na rua'))
# garagem: zumbido grave das lâmpadas de sódio e ar parado (eco curto)
gar = np.where(T >= GARAGE_T, 1.0, 0.0) * np.where(T >= 75.5, 0.0, 1.0); gar = np.convolve(gar, np.ones(4800) / 4800, 'same')
sod = (np.sin(2 * np.pi * 100 * T) * 0.5 + np.sin(2 * np.pi * 200 * T) * 0.2) * 0.05 + bp(rng.standard_normal(N), 200, 900) * 0.04
sfx += st(sod * gar * (0.5 + 0.5 * gout))
EV.append((GARAGE_T, 'garagem: zumbido das lâmpadas de sódio'))
put(sweep(180, 40, 1.4, 0.5), 75.45, 0.6, tag='as lâmpadas da garagem apagam'); put(boom(1.2, 50, 0.8), 75.5, 0.5)

CORTES = [s.t0 for s in P.SHOTS[1:]]
for i, c in enumerate(CORTES): put(load(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), c - 0.06, 0.28)
EV.append((0.0, 'swish em cada corte'))
# quadro 0: impacto junto com o texto do gancho
put(hit('impacto_hit_01.flac', 0.9, 54), 0.0, 0.3, tag='quadro 0: impacto (gancho)')
for t, nm, f0, g in [(51.08, 'impacto_hit_03.flac', 58, 0.32), (58.96, 'impacto_hit_03.flac', 62, 0.3), (61.52, 'impacto_hit_03.flac', 66, 0.24),
                     (65.8, 'impacto_metal_hit_02.flac', 55, 0.42), (72.94, 'impacto_hit_04.flac', 52, 0.3)]:
    put(riser(), t - 0.45, 0.4); put(hit(nm, 0.8, f0), t, g, tag='título: whoosh + impacto')

# ---- portas e freio ----
def chiado_freio(d=2.6):
    t = np.arange(int(d * SR)) / SR; f = 2650 + 120 * np.sin(2 * np.pi * 7 * t) + 300 * (t / d)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t) ** 2)
    return st(m * 0.18 + bp(rng.standard_normal(len(t)), 2000, 5000) * 0.05 * np.minimum(1, t / 0.4))
def ar(d=0.9, g=1.0):
    t = np.arange(int(d * SR)) / SR; x = sosfilt(sos('highpass', 1800), rng.standard_normal(len(t))) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)
    return st(x * 0.5 * g)
put(ar(0.8, 1.0), 0.55, 0.8, tag='porta pneumática fecha'); put(load('clique_5.flac'), 1.28, 1.0); put(boom(0.5, 70, 0.8), 1.3, 0.6)
# o poste do seu ponto piscando (planos 1 e 2): estalos
def pole_off(t):
    n = int(t * 7.5); h = lambda i: (np.sin(i * 127.1 + 31.7) * 43758.5453) % 1
    return h(n) < 0.32 or (h(n + 500) < 0.2 and (t * 30) % 3 < 1)
prev = False
for i in range(0, int(5.96 * 30)):
    t = i / 30; off = pole_off(t); a = int(t * SR)
    if off != prev and a + 600 < N: c = bp(rng.standard_normal(600) * np.exp(-np.arange(600) / 120), 1500, 7000) * 0.6; sfx[a:a + 600] += st(c) * (0.06 + 0.2 * gout[a])
    prev = off
# o letreiro troca: zap elétrico
for a in (7.86, 8.06, 8.18, 8.28): put(fade(loop('zumbido_eletrico.flac', 0.08), 0.004, 0.02), a, 0.55)
put(bipe(660, 0.12), 8.36, 0.35, tag='letreiro vira FORA DE SERVIÇO: zap + bipe')
put(chiado_freio(2.4), 43.4, 0.4, tag='freia na garagem'); put(ar(1.0), 45.6, 0.4, tag='parou: chiado de ar')
put(ar(0.7, 0.9), 47.4, 0.8, tag='a porta abre'); put(load('clique_5.flac'), 48.1, 0.9); put(boom(0.4, 80, 0.5), 48.12, 0.5)

# ---- o celular ----
def toque(d):
    notes = [(0.0, 1175), (0.16, 1568), (0.32, 1760), (0.48, 1568), (0.8, 1175), (0.96, 1568), (1.12, 2093)]
    m = np.zeros(int(d * SR)); per = 1.9
    for k in range(int(d / per) + 1):
        for dt, fq in notes:
            i = int((k * per + dt) * SR)
            if i >= len(m): break
            x = tone(fq, 0.28, 14) * 0.5; x[:int(0.12 * SR)] += tone(fq * 4, 0.12, 30) * 0.12; x = x[:len(m) - i]; m[i:i + len(x)] += x
    return st(m)
def vib(d):
    t = np.arange(int(d * SR)) / SR; gate = ((t % 1.0) < 0.55).astype(float)
    return st(lp((np.sin(2 * np.pi * 150 * t) + 0.5 * np.sign(np.sin(2 * np.pi * 300 * t))) * gate, 900) * 0.4)
def plim(): return st(np.concatenate([tone(1568, 0.08, 18), tone(2093, 0.22, 9)]) * 0.5)
put(vib(1.6), 20.75, 0.6, tag='o celular vibra no banco'); put(plim(), 20.85, 0.35)
put(plim(), 23.0, 0.5, tag='BOA ESCOLHA: plim')
put(load('whoosh_ar.flac', 0, 0.5), 27.1, 0.3, tag='você olha o retrovisor: whoosh curto')
put(load('whoosh_ar.flac', 0, 0.6), 50.25, 0.3, tag='ele vira pra você')
put(toque(65.8 - 53.64), 53.64, 0.24, tag='o celular toca (toque genérico)'); put(vib(65.8 - 53.64), 53.64, 0.3)
STEP = (65.8 - 57.12) / 5
def tique(): m = tone(850, 0.06, 40) * 0.3; m[:int(0.04 * SR)] += tone(1700, 0.04, 70) * 0.6; return st(m)
for k in range(5): put(tique(), 57.12 + k * STEP, 0.45); put(boom(0.4, 80, 0.4), 57.12 + k * STEP, 0.12)
EV.append((57.12, 'contagem: tique + grave a cada número'))
def passo(): m = boom(0.22, 95, 0.35); m[:int(0.06 * SR)] += st(lp(rng.standard_normal(int(0.06 * SR)) * env(0.06, 0.002, 50), 1200) * 0.9); return m
for k in range(5): put(passo(), 62.7 + k * 0.26, 0.55)
EV.append((62.7, 'B: passos correndo no concreto'))
put(bipe(1760, 0.08), 66.16, 0.5, tag='COMENTA: pop')
put(load('whoosh_ar.flac', 0, 0.8), 74.8, 0.45, tag='Você decide: whoosh final')

# ---- trilha: pad grave em dó sustenido menor ----
def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 14.5, (69.3, 103.8, 138.6, 164.8)), (14.5, 30.5, (65.4, 98, 130.8, 155.6)), (30.5, 38.1, (69.3, 103.8, 138.6, 146.8)),
                 (38.1, 65.8, (61.7, 92.5, 123.5, 146.8)), (65.8, END, (69.3, 103.8, 138.6, 164.8))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)

pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
