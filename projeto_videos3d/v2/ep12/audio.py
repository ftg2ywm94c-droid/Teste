#!/usr/bin/env python3
"""Som do vídeo 12 (vendaval à noite, suspense em 2ª pessoa) — regra do ESTILO §9: efeitos com presença, canal próprio.
Sons reais CC0 (assets/sfx_cc0) + sintetizados: vento com rajadas, assobio na fresta, estalo e rangido da árvore, alarme
do celular (genérico), contagem. Ambientes externos ficam abafados (passa-baixa) nos planos dentro de casa/banheiro.
Saída: v2/ep12/out/sfx.wav, music.wav, sfx_events.json."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 71.16; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

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
    b = sfx if bus is None else bus; i = int(at * SR); n = min(len(x), N - i)
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


# ---- vídeo 12 ----
import sys; sys.path.insert(0, HERE); import plan as P
def shot_at(t):
    for s in P.SHOTS:
        if s.t0 <= t < s.t1: return s.name
    return P.SHOTS[-1].name
INSIDE = ('S02', 'S03', 'S04', 'S07', 'S10', 'S11', 'S14', 'S16')   # dentro de casa (S16 = banheiro, ainda mais abafado)
def wind_level(t):
    if t >= 66.74: return max(0.0, 1 - (t - 66.74) / 1.0)
    if t < 23.64: return 0.0
    if t < 30.72: return 0.15 + 0.55 * min(1, (t - 23.64) / 7.08) ** 2 * (3 - 2 * min(1, (t - 23.64) / 7.08))
    return 0.7 + 0.3 * min(1, (t - 30.72) / 1.5)
def bed_mask(kind):
    """ganho por amostra para ambientes externos: 1 fora, 0.45 dentro (abafado), 0.25 no banheiro"""
    t = np.arange(N) / SR; g = np.ones(N)
    for s in P.SHOTS:
        a, b = int(s.t0 * SR), int(s.t1 * SR)
        g[a:b] = 0.25 if s.name.startswith('S16') else (0.45 if s.name.startswith(INSIDE) else 1.0)
    k = int(0.06 * SR); g = np.convolve(g, np.ones(k) / k, 'same'); return g
def muffle_split(x):
    """mistura de versão aberta e abafada conforme o plano"""
    g = bed_mask('x'); lo = lp(x, 420); return x * g[:, None] + lo * (1 - g[:, None]) * 0.9
def wind(d):            # vento: ruído em duas bandas com rajadas lentas e uivo
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t + 1) * np.sin(2 * np.pi * 0.071 * t + 2) + 0.25 * np.sin(2 * np.pi * 0.43 * t)
    low = lp(x, 180) * 2.2; mid = bp(x, 350, 1400) * 0.7
    howl = np.sin(2 * np.pi * np.cumsum(520 + 260 * np.sin(2 * np.pi * 0.11 * t) + 120 * gust) / SR) * 0.04 * gust
    m = (low + mid * np.clip(gust, 0, 1.4)) * (0.6 + 0.4 * gust) + howl
    return np.stack([m, np.roll(m, 900)], 1) * 0.5
def assobio(d):         # assobio fino na fresta: ruído em banda estreita com afinação oscilando
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n)
    for k in range(0, n, 2400):
        f0 = 1500 + 350 * np.sin(2 * np.pi * 0.7 * t[k]) + 150 * np.sin(2 * np.pi * 2.3 * t[k]); seg = x[k:k + 2400]
        out[k:k + len(seg)] = bp(seg, f0 * 0.97, f0 * 1.03)
    tone_ = np.sin(2 * np.pi * np.cumsum(1500 + 350 * np.sin(2 * np.pi * 0.7 * t)) / SR) * 0.15
    return fade(st((out * 3 + tone_) * 0.6), 0.3, 0.4)
def rangido(d=1.1, f0=70):  # madeira rangendo: dente de serra com afinação tremida, filtrado
    n = int(d * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.25 * np.sin(2 * np.pi * 3.1 * t) + 0.1 * rng.standard_normal(n).cumsum() / np.sqrt(n))
    ph = np.cumsum(f) / SR; m = bp(((ph % 1) * 2 - 1), 120, 900) * env(d, 0.15, 1.8)
    return st(m * 0.9)
def estalo():           # estalo grave: rachado seco + grave ressonante + rangido
    c = rng.standard_normal(int(0.05 * SR)) * env(0.05, 0.0005, 70)
    m = np.zeros(int(1.6 * SR)); m[:len(c)] += bp(c, 300, 5000) * 2.0
    x = st(m) + boom(1.6, 48, 1.0) * 0.9; r = rangido(1.2, 62); x[:len(r)] += r * 0.8; return x
def alarme(d):          # alarme de emergência genérico do celular: dois tons alternados, envelope em blocos
    n = int(d * SR); t = np.arange(n) / SR; f = np.where((t % 0.5) < 0.25, 870, 1050)
    m = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.22 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    gate = ((t % 1.6) < 1.25).astype(float); return fade(st(lp(m * gate, 4000)), 0.01, 0.2)
def passos(t0, n, dt=0.27):
    for k in range(n):
        m = boom(0.25, 90, 0.4); m[:int(0.08 * SR)] += st(lp(rng.standard_normal(int(0.08 * SR)) * env(0.08, 0.002, 40), 900) * 1.2); put(m, t0 + k * dt, 0.6)
def tique():
    m = tone(850, 0.06, 40) * 0.3; m[:int(0.04 * SR)] += tone(1700, 0.04, 70) * 0.6; return st(m)

# leito: vento + chuva com nível do vento e abafamento por plano
lev = np.array([wind_level(i / SR) for i in range(0, N, 480)]); lev = np.interp(np.arange(N), np.arange(0, N, 480), lev)
wb = wind(END) * lev[:, None] ** 1.3
rain = np.zeros((N, 2)); a0 = int(28.4 * SR); rl = loop('chuva_loop.flac', END - 28.4); rain[a0:a0 + len(rl)] = rl[:N - a0]
rain *= np.clip((np.arange(N) / SR - 28.4) / 2.0, 0, 1)[:, None] * np.clip((67.6 - np.arange(N) / SR) / 0.9, 0, 1)[:, None]
# gotas nítidas: milhares de estalinhos curtos e agudos (2-9 kHz) espalhados no estéreo, por cima do loop de chuva
def patter(d, rate=420):
    n = int(d * SR); out = np.zeros((n, 2)); k = int(rate * d); pos = rng.integers(0, n - 400, k)
    for i, p0 in enumerate(pos):
        L = rng.integers(60, 260); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * (0.3 + 0.7 * rng.random())
        pan = rng.random(); out[p0:p0 + L, 0] += c * np.sqrt(1 - pan); out[p0:p0 + L, 1] += c * np.sqrt(pan)
    return sosfilt(sos('highpass', 2000), out, axis=0) * 0.5
pt = np.zeros((N, 2)); pp = patter(END - 28.4); pt[a0:a0 + len(pp)] = pp[:N - a0]
pt *= np.clip((np.arange(N) / SR - 28.4) / 2.0, 0, 1)[:, None] * np.clip((67.6 - np.arange(N) / SR) / 0.9, 0, 1)[:, None]
sfx += muffle_split(wb * 1.25 + rain * 1.1 + pt * 1.3)
EV += [(23.64, 'vento (sintetizado, rajadas) — abafado dentro de casa'), (28.4, 'chuva + gotas nítidas (sintetizadas)')]

CORTES = [s.t0 for s in P.SHOTS[1:]]
for i, c in enumerate(CORTES): put(load(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), c - 0.06, 0.45)
EV.append((0.0, 'swish em cada corte'))
for t, nm, f0 in [(1.0, 'impacto_hit_01.flac', 58), (22.1, 'impacto_hit_04.flac', 52), (50.34, 'impacto_hit_03.flac', 62), (54.34, 'impacto_hit_03.flac', 66), (60.06, 'impacto_metal_hit_02.flac', 55)]:
    put(riser(), t - 0.45, 0.4); put(hit(nm, 0.8, f0), t, 0.22 if t < 2 else 0.42, tag='título: whoosh + impacto')

# 0-23: noite calma, alarme, a rua parada
put(fade(loop('grilos_loop.flac', 20.5), 0.8, 0.08), 0.0, 0.5, tag='noite: grilos (param no "calma demais")')
put(relogio(3.7, 60) * 0.5, 0.0, 0.5, tag='relógio da sala')
put(fade(loop('geladeira_loop.flac', 31.5), 0.5, 0.05), 4.0, 0.18, tag='casa: zumbido baixo da geladeira')
put(alarme(4.8), 4.5, 0.7, tag='celular: alarme de emergência (genérico)'); put(vibra(4.6), 4.5, 0.5)
put(load('clique_7.flac'), 7.86, 0.6, tag='silencioso: clique')
put(bipe(1320, 0.1), 11.64, 0.5, tag='ALERTA SEVERO: bipe'); put(bipe(990, 0.16), 13.16, 0.5, tag='VENDAVAL: bipe')
put(fade(load('gotas.flac', 0, 3.0), 0.5, 1.0), 17.3, 0.12)
# 23-36: o vento chega, assobio, árvores, telha, a luz pisca e apaga
put(load('whoosh_ar.flac', 0, 2.5), 23.7, 0.8, tag='o vento chega: rajada')
put(assobio(2.6), 25.9, 0.75, tag='assobio fino na fresta')
for tk in (29.6, 30.3, 31.0): put(rangido(0.9, 80 + 10 * (tk % 1)), tk, 0.55)
EV.append((29.6, 'galhos rangendo'))
put(fade(load('chuva_trovao.flac', 0, 4.0), 0.02, 1.0), 29.2, 0.85, tag='trovão'); put(boom(2.0, 40), 29.2, 0.6)
put(load('whoosh_ar.flac', 0, 0.8), 31.8, 0.7, tag='telha voando'); put(load('impacto_rock_hit_01.flac'), 32.95, 0.8); put(load('impacto_hit_03.flac'), 33.05, 0.6, tag='telha cai lá fora')
for a in (34.52, 34.82, 35.14, 35.52): put(fade(loop('zumbido_eletrico.flac', 0.12), 0.005, 0.03), a, 0.5)
EV.append((34.52, 'a luz pisca: zumbido'))
put(load('disjuntor_desliga.flac'), 35.75, 0.5, tag='apaga'); put(sweep(300, 30, 1.0, 0.45), 35.8, 0.25); put(boom(1.8, 44), 36.3, 0.55)
put(load('maquina_desligando.flac'), 35.78, 0.4, tag='geladeira desliga')
# 36-46: escuro, estalo, a árvore inclina
put(load('chuva_trovao.flac', 5.0, 3.0), 37.95, 0.7, tag='trovão')
put(estalo(), 38.54, 1.2, tag='estalo grave')
for tk, f0 in ((40.0, 66), (41.4, 58), (42.6, 70), (43.3, 55), (44.0, 60)): put(rangido(1.0, f0), tk, 0.75)
EV.append((40.0, 'a árvore range'))
put(fade(load('chuva_trovao.flac', 2.0, 3.0), 0.02, 1.0), 40.35, 0.7); put(boom(1.6, 42), 40.35, 0.5)
put(estalo(), 44.44, 1.1, tag='na sua direção: estalo'); put(fade(load('chuva_trovao.flac', 1.0, 3.0), 0.02, 1.0), 44.25, 0.6)
# 46-60: bateria, contagem, opções
put(bipe(440, 0.12), 46.96, 0.8); put(bipe(440, 0.12), 47.2, 0.8, tag='bateria fraca: bipe duplo')
STEP = (60.06 - 48.78) / 9.5
for k in range(10): put(tique(), 48.78 + k * STEP, 0.45); put(boom(0.4, 80, 0.4), 48.78 + k * STEP, 0.12)
EV.append((48.78, 'contagem: tique + grave a cada número'))
put(load('whoosh_ar.flac', 0, 1.2), 51.5, 0.9, tag='A: porta abre, o vento entra'); passos(51.75, 9)
put(fade(load('chuva_trovao.flac', 0, 3.0), 0.02, 1.0), 52.1, 0.7)
put(load('impacto_hit_04.flac'), 56.4, 1.0, tag='B: porta do banheiro bate'); put(boom(0.9, 70), 56.4, 0.7)
put(load('clique_5.flac'), 56.62, 1.1, tag='trinco')
# 60-71: escolha, resposta, calma de novo
put(fade(load('chuva_trovao.flac', 5.0, 3.0), 0.02, 1.0), 61.0, 0.5)
put(bipe(1760, 0.08), 62.18, 0.5, tag='COMENTA: pop'); put(sino(), 64.04, 0.45, tag='resposta no comentário: sino')
put(fade(loop('grilos_loop.flac', 4.4), 1.0, 0.6), 66.8, 0.5, tag='calma: grilos voltam')
put(load('whoosh_ar.flac', 0, 0.8), 70.3, 0.5, tag='E se...: whoosh final')

# ---- trilha: pad grave em ré menor, com pulso; some na escolha e volta suave no fim ----
def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 23.9, (73.4, 110, 146.8, 174.6)), (23.9, 46.0, (69.3, 103.8, 138.6, 164.8)), (46.0, 60.1, (65.4, 98, 130.8, 155.6)),
                 (60.1, 66.8, (73.4, 110, 146.8)), (66.8, END, (73.4, 110, 146.8, 185))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)

pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
