#!/usr/bin/env python3
"""Som do vídeo 13 (O último ônibus, Ep. 1) — regra do ESTILO §9: efeitos com presença, canal próprio.
Sons reais CC0 (assets/sfx_cc0) + sintetizados: motor diesel e ruído de pista (mais alto dentro), zumbido das lâmpadas,
toque genérico do celular e vibração, notificações, freio com chiado de ar, porta pneumática, poste piscando, contagem.
Saída: v2/ep13/out/sfx.wav, music.wav, sfx_events.json."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 70.6; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(13)

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


# ---- vídeo 13 ----
import sys; sys.path.insert(0, HERE); import plan as P
OUTSIDE = ('S01', 'S14', 'S18', 'S20', 'S21')
def mask(inside_g, outside_g):
    g = np.zeros(N)
    for s in P.SHOTS:
        a, b = int(s.t0 * SR), int(s.t1 * SR); g[a:b] = outside_g if s.name.startswith(OUTSIDE) else inside_g
    k = int(0.05 * SR); return np.convolve(g, np.ones(k) / k, 'same')
# movimento do ônibus (0 parado .. 1 a 8 m/s), igual ao story.ts: freia de 37,42 a 40,24; parado; sai em 67,4
T = np.arange(N) / SR
speed = np.ones(N)
speed = np.where((T >= 37.42) & (T < 40.24), (40.24 - T) / (40.24 - 37.42), speed)
speed = np.where((T >= 40.24) & (T < 55.62), 0.0, speed)
speed = np.where((T >= 55.62) & (T < 61.0), 1.0, speed)                  # opção B: o ônibus andando
speed = np.where((T >= 61.0) & (T < 67.36), 0.0, speed)                  # a escolha: parado no ponto
speed = np.where(T >= 67.36, np.clip((T - 67.36) * 1.6 / 8.0, 0, 1), speed)  # vai embora
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
bed = (eng * (0.55 * gin + 0.5 * gout) + road * (0.7 * gin + 0.35 * gout))
sfx += st(bed) * 0.15
EV.append((0.0, 'motor diesel + ruído de pista (mais alto dentro; segue a velocidade do ônibus)'))
# chacoalhar de dentro: estalinhos metálicos aleatórios quando anda
rat = np.zeros(N)
for p0 in rng.integers(0, N - 2000, 900):
    if speed[p0] > 0.3: L = int(rng.integers(200, 900)); rat[p0:p0 + L] += bp(rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 5)), 1500, 6000) * 0.5
sfx += st(rat * gin * speed) * 0.2
# lâmpadas do teto: zumbido de 120 Hz (some quando piscam no "fica sentado")
hum = (np.sin(2 * np.pi * 120 * T) * 0.6 + np.sin(2 * np.pi * 240 * T) * 0.25 + np.sin(2 * np.pi * 360 * T) * 0.1) * 0.06
fl = np.ones(N)
for a, b in [(48.35, 48.45), (48.6, 48.67), (48.82, 48.87)]: fl[int(a * SR):int(b * SR)] = 0
sfx += st(hum * gin * fl)
EV.append((2.4, 'lâmpadas fluorescentes zumbindo (dentro)'))
for a in (48.35, 48.6, 48.82): put(fade(loop('zumbido_eletrico.flac', 0.1), 0.004, 0.03), a, 0.5)
EV.append((48.35, 'as luzes piscam: estalos elétricos'))
# noite lá fora: grilos (fora e pela porta aberta)
cr = loop('grilos_loop.flac', END); door_open = np.where((T >= 41.0) & (T < 66.9), 1.0, 0.0)
crm = np.clip(gout + 0.6 * door_open * gin, 0, 1); crm = np.convolve(crm, np.ones(4800) / 4800, 'same')
sfx += cr * crm[:, None] * 0.35
EV.append((0.0, 'grilos lá fora (e pela porta aberta)'))

CORTES = [s.t0 for s in P.SHOTS[1:]]
for i, c in enumerate(CORTES): put(load(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), c - 0.06, 0.3)
EV.append((0.0, 'swish em cada corte'))
for t, nm, f0, g in [(0.4, 'impacto_hit_01.flac', 56, 0.22), (52.04, 'impacto_hit_03.flac', 62, 0.32), (55.62, 'impacto_hit_03.flac', 66, 0.24),
                     (61.0, 'impacto_metal_hit_02.flac', 55, 0.42), (66.76, 'impacto_hit_04.flac', 52, 0.3)]:
    put(riser(), t - 0.45, 0.4); put(hit(nm, 0.8, f0), t, g, tag='título: whoosh + impacto')

# ---- o celular desconhecido ----
def toque(d):
    """toque genérico de celular: arpejo curto tipo marimba repetido"""
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
def ring_far(x):   # o celular lá na frente, ouvido do fundo
    return lp(x, 2200) * 0.6
r1 = toque(17.9 - 10.92); put(ring_far(r1[:int((12.58 - 10.92) * SR)]), 10.92, 0.4, tag='o celular toca (toque genérico)')
put(r1[int((12.58 - 10.92) * SR):], 12.58, 0.2)
put(vib(17.9 - 10.92), 10.92, 0.3)
r2 = toque(22.75 - 18.9); put(r2, 18.9, 0.24, tag='toca de novo'); put(vib(22.75 - 18.9), 18.9, 0.3)
put(load('clique_3.flac'), 17.9, 0.5, tag='para: silêncio')
def plim(): return st(np.concatenate([tone(1568, 0.08, 18), tone(2093, 0.22, 9)]) * 0.5)
put(plim(), 24.7, 0.3, tag='mensagem: plim'); put(plim(), 25.86, 0.5, tag='NÃO DESCE: plim')
put(vib(0.6), 33.64, 0.45); put(plim(), 33.7, 0.35, tag='outra mensagem')
put(vib(1.1), 46.46, 0.6, tag='vibra uma última vez'); put(plim(), 46.6, 0.55)
# passos no corredor
def passo(): m = boom(0.22, 95, 0.35); m[:int(0.06 * SR)] += st(lp(rng.standard_normal(int(0.06 * SR)) * env(0.06, 0.002, 50), 1200) * 0.9); return m
for k in range(8): put(passo(), 20.35 + k * 0.3, 0.55)
EV.append((20.35, 'passos no corredor'))
# o retrovisor
put(load('whoosh_ar.flac', 0, 0.5), 32.0, 0.35, tag='desvia o olhar: whoosh curto')
# ---- a freada e a porta ----
def chiado_freio(d=2.6):
    t = np.arange(int(d * SR)) / SR; f = 2650 + 120 * np.sin(2 * np.pi * 7 * t) + 300 * (t / d)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t) ** 2)
    return st(m * 0.18 + bp(rng.standard_normal(len(t)), 2000, 5000) * 0.05 * np.minimum(1, t / 0.4))
def ar(d=0.9, g=1.0):   # chiado de ar comprimido (freio / porta)
    t = np.arange(int(d * SR)) / SR; x = sosfilt(sos('highpass', 1800), rng.standard_normal(len(t))) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)
    return st(x * 0.5 * g)
put(chiado_freio(), 37.7, 0.5, tag='freio chiando'); put(ar(1.0), 40.25, 0.35, tag='parou: chiado de ar'); put(boom(0.6, 60, 0.6), 40.24, 0.35)
put(ar(0.7, 0.9), 41.05, 0.8, tag='porta pneumática abre'); put(load('clique_5.flac'), 41.7, 0.9); put(boom(0.4, 80, 0.5), 41.72, 0.5)
# o poste piscando: estalos e zumbido sincronizados (de 40,2 até a saída)
def pole_off(t):
    n = int(t * 7.5); h = lambda i: (np.sin(i * 127.1 + 31.7) * 43758.5453) % 1
    return h(n) < 0.32 or (h(n + 500) < 0.2 and (t * 30) % 3 < 1)
pz = np.zeros(N); prev = False
for i in range(int(39.84 * 30), int(67.0 * 30)):
    t = i / 30; off = pole_off(t); a = int(t * SR); b = int((t + 1 / 30) * SR)
    pz[a:b] = 0 if off else 1
    if off != prev and a + 600 < N:   # estalo elétrico a cada vez que o poste apaga/acende
        c = bp(rng.standard_normal(600) * np.exp(-np.arange(600) / 120), 1500, 7000) * 0.6; sfx[a:a + 600] += st(c) * (0.06 + 0.22 * gout[a] + 0.1 * door_open[a])
    prev = off
buzz = loop('zumbido_eletrico.flac', END)[:, 0] * pz * 0.25
sfx += st(buzz * np.clip(gout + 0.4 * door_open * gin, 0, 1))
EV.append((40.24, 'poste piscando: zumbido elétrico'))
# contagem (5 -> 1)
STEP = (61.0 - 50.38) / 5
def tique(): m = tone(850, 0.06, 40) * 0.3; m[:int(0.04 * SR)] += tone(1700, 0.04, 70) * 0.6; return st(m)
for k in range(5): put(tique(), 50.38 + k * STEP, 0.45); put(boom(0.4, 80, 0.4), 50.38 + k * STEP, 0.12)
EV.append((50.38, 'contagem: tique + grave a cada número'))
put(passo(), 53.4, 0.6, tag='A: pé no degrau'); put(passo(), 53.75, 0.5)
put(ar(0.8, 0.8), 57.2, 0.4, tag='B: a porta fecha, o ônibus segue'); put(boom(0.5, 70, 0.5), 57.9, 0.5)
put(bipe(1760, 0.08), 61.38, 0.5, tag='COMENTA: pop')
put(ar(0.8, 0.8), 66.9, 0.7, tag='fim: a porta fecha e o ônibus vai embora')
put(load('whoosh_ar.flac', 0, 0.8), 69.9, 0.45, tag='Você decide: whoosh final')

# ---- trilha: pad grave em dó sustenido menor, mais tensa a partir das mensagens ----
def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 10.4, (69.3, 103.8, 138.6, 164.8)), (10.4, 25.8, (65.4, 98, 130.8, 155.6)), (25.8, 40.9, (69.3, 103.8, 138.6, 146.8)),
                 (40.9, 61.0, (61.7, 92.5, 123.5, 146.8)), (61.0, END, (69.3, 103.8, 138.6, 164.8))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)

pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
