#!/usr/bin/env python3
"""Som do vídeo 14 (Vendaval · Ep. 2) — regra do ESTILO §9: efeitos com presença, canal próprio.
Sons reais CC0 (assets/sfx_cc0) + sintetizados: tempestade, a árvore rangendo e caindo, vidro, telhas, silêncio, goteira e
faíscas sincronizadas com a imagem, vibração do celular, discagem do 193. Abafado dentro do banheiro.
Saída: v2/ep14/out/sfx.wav, music.wav, sfx_events.json."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 67.4; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(14)

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


# ---- vídeo 12 ----
import sys; sys.path.insert(0, HERE); import plan as P
def shot_at(t):
    for s in P.SHOTS:
        if s.t0 <= t < s.t1: return s.name
    return P.SHOTS[-1].name
BATH = ('S01', 'S02', 'S03', 'S06', 'S09', 'S10', 'S11', 'S12', 'S15', 'S18'); ROOM = ('S13', 'S14', 'S17')
def wind_level(t):   # igual ao story.ts
    if t < 12.3: return 1.0
    if t < 17.9: u = (t - 12.3) / 5.6; return 1.0 - 0.72 * u * u * (3 - 2 * u)
    return 0.28
def bed_mask(kind):
    """ganho por amostra para ambientes externos: 1 fora, 0.45 dentro (abafado), 0.25 no banheiro"""
    t = np.arange(N) / SR; g = np.ones(N)
    for s in P.SHOTS:
        a, b = int(s.t0 * SR), int(s.t1 * SR)
        g[a:b] = 0.3 if s.name.startswith(BATH) else (0.65 if s.name.startswith(ROOM) else 1.0)
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

# leito: vento + chuva + gotas nítidas, conforme o vento e abafado por plano
lev = np.array([wind_level(i / SR) for i in range(0, N, 480)]); lev = np.interp(np.arange(N), np.arange(0, N, 480), lev)
wb = wind(END) * lev[:, None] ** 1.3
rain = loop('chuva_loop.flac', END) * (0.45 + 0.55 * lev)[:, None]
def patter(d, rate=420):
    n = int(d * SR); out = np.zeros((n, 2)); k = int(rate * d); pos = rng.integers(0, n - 400, k)
    for p0 in pos:
        L = rng.integers(60, 260); c = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * (0.3 + 0.7 * rng.random())
        pan = rng.random(); out[p0:p0 + L, 0] += c * np.sqrt(1 - pan); out[p0:p0 + L, 1] += c * np.sqrt(pan)
    return sosfilt(sos('highpass', 2000), out, axis=0) * 0.5
pt = patter(END) * (0.4 + 0.6 * lev)[:, None]
sfx += muffle_split(wb * 1.25 + rain * 1.1 + pt * 1.3) * 0.32
EV += [(0.0, 'tempestade: vento + chuva + gotas (abafado no banheiro)')]
CORTES = [s.t0 for s in P.SHOTS[1:]]
for i, c in enumerate(CORTES): put(load(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), c - 0.06, 0.3)
for t, nm, f0, g in [(0.25, 'impacto_hit_01.flac', 58, 0.22), (48.3, 'impacto_hit_03.flac', 62, 0.3), (53.22, 'impacto_hit_03.flac', 66, 0.24),
                     (58.3, 'impacto_metal_hit_02.flac', 55, 0.3), (63.66, 'impacto_hit_04.flac', 52, 0.25)]:
    put(riser(), t - 0.45, 0.4); put(hit(nm, 0.8, f0), t, g, tag='título: whoosh + impacto')
# banheiro: trinco, bateria, lanterna
put(load('clique_5.flac'), 3.1, 2.0, tag='trinco'); put(load('clique_1.flac'), 3.32, 1.5)
put(bipe(440, 0.12), 5.1, 1.0); put(bipe(440, 0.12), 5.34, 1.0, tag='bateria 8 %: bipe duplo'); put(load('clique_3.flac'), 6.7, 0.6, tag='lanterna: clique')
put(load('whoosh_ar.flac', 0, 2.2), 8.2, 0.7, tag='o vento uiva: rajada'); put(assobio(2.0), 9.0, 0.5)
put(fade(load('chuva_trovao.flac', 0, 3.0), 0.02, 1.0), 9.0, 0.6, tag='trovão')
# a queda da árvore (física no story.ts: começa ~0,9 s antes do estrondo)
TF = 11.48 - 0.95
for k, (tk, f0) in enumerate(((TF - 0.4, 64), (TF, 56), (TF + 0.35, 50))): put(rangido(0.9, f0), tk, 0.5)
put(estalo(), TF, 0.45, tag='a árvore racha e começa a cair')
put(load('whoosh_ar.flac', 0, 1.0), TF + 0.2, 0.6)
put(boom(2.4, 36, 1.0), 11.48, 0.3, tag='ESTRONDO: a árvore bate na casa'); put(load('impacto_rock_hit_01.flac'), 11.48, 0.35); put(load('impacto_hit_04.flac'), 11.5, 0.3)
put(fade(load('chuva_trovao.flac', 2.0, 3.0), 0.02, 1.0), 11.53, 0.6)
put(boom(1.6, 30, 0.8), 12.3, 0.45, tag='a casa treme: ronco grave')
dust = bp(rng.standard_normal(int(1.6 * SR)), 2000, 8000) * np.exp(-np.arange(int(1.6 * SR)) / SR * 1.5) * 0.12; put(st(dust), 12.4, 0.5, tag='poeira caindo')
def vidro(d=0.9):   # vidro quebrando: estalo + muitos tilintares agudos espalhados
    m = np.zeros((int(d * SR), 2)); c = rng.standard_normal(int(0.04 * SR)) * env(0.04, 0.0005, 80); m[:len(c)] += st(bp(c, 1500, 9000)) * 1.5
    for i in range(40):
        a = int(rng.random() * (d - 0.2) * SR); f = 3000 + 5000 * rng.random(); x = tone(f, 0.15, 30) * (0.1 + 0.2 * rng.random()); pan = rng.random() * 2 - 1
        m[a:a + len(x)] += st(x, pan)[:len(m) - a]
    return m
put(vidro(), 14.05, 0.8, tag='vidro quebrando'); put(vidro(0.6), 14.5, 0.5)
for i, tk in enumerate((15.2, 15.45, 15.62, 15.9, 16.1, 16.35)): put(load('impacto_rock_hit_01.flac'), tk, 1.3 - 0.12 * i)
EV.append((15.2, 'telhas caindo na calçada'))
# goteira (gotas batem na poça como na imagem: período 0,95 s, duas gotas defasadas)
def plink():
    x = tone(1350 + 300 * rng.random(), 0.12, 30) * 0.4; x[:int(0.06 * SR)] += tone(700, 0.06, 50) * 0.2; return st(x)
for k in range(2):
    t = 24.4 + ((0.295 - k * 0.475) % 0.95)
    while t < 29.6: put(plink(), t, 2.2 if t < 27.34 else 1.0); t += 0.95
EV.append((24.4, 'goteira: gotas na poça (sincronizadas)'))
crk = bp(rng.standard_normal(int(2.3 * SR)), 1500, 6000) * (rng.random(int(2.3 * SR)) < 0.004) * 4; put(st(crk), 27.4, 0.25, tag='cheiro de queimado: estalinhos')
put(rangido(1.4, 140), 29.9, 0.55, tag='a porta abre uma fresta: rangido')
# faíscas do fio (mesma função do story.ts), mais fortes de perto
def spark_at(t):
    h = lambda i: (np.sin(i * 127.1 + 31.7) * 43758.5453) % 1; n = int(t * 15)
    return h(n) < 0.42 or (h(n + 77) < 0.25 and (t * 30) % 2 < 1)
for a_, b_, g in [(30.4, 32.22, 0.12), (32.22, 34.92, 0.25), (34.92, 40.78, 0.55), (48.3, 53.22, 0.35)]:
    prev = False
    for i in range(int(a_ * 30), int(b_ * 30)):
        on = spark_at(i / 30)
        if on and not prev:
            c = bp(rng.standard_normal(int(0.08 * SR)) * env(0.08, 0.0005, 35), 1200, 9000) * 1.2
            put(st(c, rng.random() * 0.4 - 0.2), i / 30, g); put(fade(loop('zumbido_eletrico.flac', 0.07), 0.003, 0.02), i / 30, g * 0.8)
        prev = on
EV.append((30.4, 'faíscas do fio (sincronizadas com a imagem)'))
put(vibra(1.8), 41.66, 0.2, tag='o celular vibra')
put(bipe(440, 0.12), 42.66, 0.5, tag='6 %: bipe')
# opção A: passos sobre vidro e galhos
for k in range(9):
    m = boom(0.22, 95, 0.3); m[:int(0.06 * SR)] += st(bp(rng.standard_normal(int(0.06 * SR)), 2500, 8000) * 0.5); put(m, 49.4 + k * 0.42, 1.4)
EV.append((49.4, 'A: passos no vidro e nos galhos'))
# opção B: discando 1-9-3 (DTMF) e chamando
DT = {'1': (697, 1209), '9': (852, 1477), '3': (697, 1477)}
for i, d in enumerate('193'): x = tone(DT[d][0], 0.14, 2) * 0.25 + tone(DT[d][1], 0.14, 2) * 0.25; put(st(x), 55.0 + i * 0.22, 1.2)
for k in range(2): put(st(tone(425, 1.0, 0.3) * 0.25), 56.0 + k * 1.6, 1.0)
EV.append((55.0, 'B: discando 193 e chamando'))
put(fade(load('chuva_trovao.flac', 5.0, 3.0), 0.02, 1.0), 59.6, 0.4)
put(bipe(1760, 0.08), 60.88, 1.4, tag='COMENTA: pop')
put(load('whoosh_ar.flac', 0, 0.8), 66.4, 0.45, tag='E se...: whoosh final')

def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 11.5, (73.4, 110, 146.8, 174.6)), (12.0, 29.6, (69.3, 103.8, 138.6, 164.8)), (29.6, 48.3, (65.4, 98, 130.8, 155.6)),
                 (48.3, 58.3, (61.7, 92.5, 123.5, 146.8)), (58.3, END, (73.4, 110, 146.8, 185))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)
pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
