#!/usr/bin/env python3
"""Camada de TENSÃO / SUSPENSE (sintetizada, original), somada ao leito de efeitos + música na montagem.
Cada episódio descreve as deixas em v2/epXX/tensao_cfg.py (lista CUES); o assemble.py só usa out/tensao.wav se ele existir,
então episódios antigos não mudam.
Tipos de deixa (tempos em segundos da narração):
  ('drone', t0, t1, g)          grave contínuo com batimento lento (inquietação)
  ('pulso', t0, t1, bpm, g)     ostinato grave de semínimas/colcheias com semitom (urgência)
  ('relogio', t0, t1, bpm, g)   tique-taque (contagem, tempo passando)
  ('coracao', t0, t1, bpm, g)   batimento cardíaco (perigo físico)
  ('cluster', t0, t1, g)        agudos dissonantes trêmulos (suspense)
  ('subida', t0, t1, g)         riser: ruído + varredura que corta seco em t1 (antes de uma revelação)
  ('reverso', t, d, g)          sopro reverso que termina em t
  ('braam', t, g)               impacto grave de metais sintéticos (número forte / revelação)
  ('queda', t, g)               "sub drop" curto (corte para o silêncio)
Uso: EP=09 python3 v2/lib/tensao.py"""
import os, sys, math, importlib.util
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
rng = np.random.default_rng(7)
def _sos(k, f, o=2): return butter(o, f, k, fs=SR, output='sos')
def lp(x, f, o=2): return sosfilt(_sos('lowpass', f, o), x)
def hp(x, f, o=2): return sosfilt(_sos('highpass', f, o), x)
def bp(x, a, b, o=2): return sosfilt(_sos('bandpass', [a, b], o), x)
def tt(d): return np.arange(int(d * SR)) / SR
def fade(x, a, b):
    n = len(x); ia, ib = min(n, int(a * SR)), min(n, int(b * SR)); w = np.ones(n)
    if ia: w[:ia] = np.sin(np.linspace(0, np.pi / 2, ia)) ** 2
    if ib: w[n - ib:] = np.cos(np.linspace(0, np.pi / 2, ib)) ** 2
    return x * w
def saw(f, x, ph=0.0): return 2 * ((f * x + ph) % 1.0) - 1

def drone(d, root=36.7):
    x = tt(d); l = np.zeros_like(x); r = np.zeros_like(x)
    for k, (f, g) in enumerate([(root, 1.0), (root * 1.007, 0.8), (root * 2.003, 0.35), (root * 3.01, 0.12), (root * 1.4983, 0.18)]):
        ph = rng.uniform(0, 6.28); l += g * np.sin(2 * np.pi * f * x + ph); r += g * np.sin(2 * np.pi * f * 1.0015 * x + ph + 0.4)
    air = lp(np.cumsum(rng.standard_normal(len(x))), 1) ; air = hp(air, 30); air = lp(air, 220); air /= np.abs(air).max() + 1e-9
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * x)
    return fade(l * lfo + 0.5 * air, 1.6, 1.8), fade(r * lfo + 0.5 * air[::-1], 1.6, 1.8)

def pulso(d, bpm, root=73.4):
    x = tt(d); o = np.zeros_like(x); step = 60 / bpm / 2; pat = [1, 1, 1.0595, 1, 1, 1, 0.9439, 1]
    n = 0; s = 0.0
    while s < d:
        f = root * pat[n % len(pat)]; seg = tt(min(step * 0.9, d - s)); i = int(s * SR)
        e = np.exp(-seg * 9) * np.minimum(seg / 0.004, 1); acc = 1.0 if n % 4 == 0 else 0.7
        o[i:i + len(seg)] += acc * e * (saw(f, seg) + 0.6 * saw(f * 1.005, seg) + 0.5 * np.sin(2 * np.pi * f / 2 * seg))
        n += 1; s += step
    o = lp(o, 420, 4); o *= np.minimum(1, np.linspace(0.35, 1.2, len(o)))  # cresce ao longo da deixa
    return fade(o, 0.4, 0.5), fade(o, 0.4, 0.5)

def relogio(d, bpm):
    x = np.zeros(int(d * SR)); step = 60 / bpm; s = 0.0; k = 0
    while s < d - 0.05:
        seg = tt(0.045); f = 2600 if k % 2 == 0 else 1900
        c = (np.sin(2 * np.pi * f * seg) + 0.5 * bp(rng.standard_normal(len(seg)), 2000, 7000)) * np.exp(-seg * 140)
        i = int(s * SR); x[i:i + len(c)] += c[:len(x) - i]; s += step; k += 1
    return x * 0.9, np.roll(x, int(0.004 * SR)) * 0.9

def coracao(d, bpm):
    x = np.zeros(int(d * SR)); step = 60 / bpm; s = 0.0
    def thump(g):
        seg = tt(0.22); f = 62 * np.exp(-seg * 6); ph = 2 * np.pi * np.cumsum(f) / SR
        return g * np.sin(ph) * np.exp(-seg * 18) * np.minimum(seg / 0.006, 1)
    while s < d - 0.4:
        for off, g in ((0.0, 1.0), (0.26, 0.7)):
            c = thump(g); i = int((s + off) * SR); x[i:i + len(c)] += c[:max(0, len(x) - i)]
        s += step
    x = lp(x, 160); return x, x

def cluster(d):
    x = tt(d); l = np.zeros_like(x); r = np.zeros_like(x)
    for f in (1661, 1760, 1865, 2489):
        trem = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(5.5, 7.5) * x + rng.uniform(0, 6))
        l += trem * np.sin(2 * np.pi * f * x + rng.uniform(0, 6)); r += trem * np.sin(2 * np.pi * f * 1.002 * x + rng.uniform(0, 6))
    g = np.minimum(1, x / max(d * 0.7, 0.1)); return fade(l * g, 0.8, 0.6) * 0.18, fade(r * g, 0.8, 0.6) * 0.18

def subida(d):
    x = tt(d); p = x / d; n = rng.standard_normal(len(x))
    nz = np.zeros_like(x); edges = np.linspace(0, len(x), 9).astype(int)
    for a, b in zip(edges[:-1], edges[1:]):  # passa-faixa que sobe por blocos (com cruzamento suave via janela)
        c = 400 * 2 ** (4.0 * (a + b) / 2 / len(x)); nz[a:b] = bp(n[max(0, a - 2000):b], c * 0.7, min(c * 1.6, 20000))[-(b - a):]
    f = 110 * 2 ** (3.2 * p ** 1.6); sw = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    o = (0.55 * nz + 0.45 * sw) * p ** 2.2
    o[-int(0.008 * SR):] *= np.linspace(1, 0, int(0.008 * SR))
    return o, np.roll(o, int(0.006 * SR))

def reverso(d):
    n = rng.standard_normal(int(d * SR)); e = np.exp(-tt(d) * 5.0 / d); o = lp(hp(n * e, 300), 5000)[::-1]
    return o * 0.8, np.roll(o, int(0.007 * SR)) * 0.8

def braam(d=3.0, root=36.7):
    x = tt(d); env = np.minimum(x / 0.025, 1) * np.exp(-x * 1.15)
    o = np.zeros_like(x)
    for f, g in ((root, 1.0), (root * 1.5, 0.7), (root * 2, 0.8), (root * 3, 0.35), (root * 2 * 1.0595, 0.25)):
        o += g * (saw(f, x) + saw(f * 1.004, x, 0.3))
    cut = 180 + 1400 * np.exp(-x * 2.2)  # filtro que fecha
    out = np.zeros_like(o); blk = 2400
    for i in range(0, len(o), blk):
        out[i:i + blk] = lp(o[max(0, i - 4800):i + blk], float(cut[i]), 2)[-len(o[i:i + blk]):]
    sub = np.sin(2 * np.pi * root * x) * np.exp(-x * 1.4) * 1.2
    hit = lp(rng.standard_normal(len(x)), 900) * np.exp(-x * 14) * 0.8
    o = (out * 0.45 + sub + hit) * env
    return o, np.roll(o, int(0.009 * SR))

def queda(d=1.2):
    x = tt(d); f = 90 * np.exp(-x * 2.5) + 28; o = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.8) * np.minimum(x / 0.01, 1)
    return o, o

def ir(seconds=2.4, seed=3):
    r = np.random.default_rng(seed); n = int(seconds * SR); e = np.exp(-np.arange(n) / SR * 3.2)
    return lp(r.standard_normal(n) * e, 4500) * 0.035, lp(r.standard_normal(n) * e, 4500) * 0.035

def render(cues, end):
    N = int(end * SR) + 1; L = np.zeros(N); R = np.zeros(N); WL = np.zeros(N); WR = np.zeros(N)
    def put(sig, at, g, wet):
        l, r = sig; i = int(at * SR)
        for buf, s, wb in ((L, l, WL), (R, r, WR)):
            a, b = max(0, i), min(N, i + len(s))
            if b <= a: continue
            buf[a:b] += g * s[a - i:b - i]; wb[a:b] += wet * g * s[a - i:b - i]
    for c in cues:
        k = c[0]
        if k == 'drone':   put(drone(c[2] - c[1]), c[1], c[3], 0.3)
        elif k == 'pulso': put(pulso(c[2] - c[1], c[3]), c[1], c[4], 0.2)
        elif k == 'relogio': put(relogio(c[2] - c[1], c[3]), c[1], c[4], 0.25)
        elif k == 'coracao': put(coracao(c[2] - c[1], c[3]), c[1], c[4], 0.1)
        elif k == 'cluster': put(cluster(c[2] - c[1]), c[1], c[3], 0.6)
        elif k == 'subida': put(subida(c[2] - c[1]), c[1], c[3], 0.4)
        elif k == 'reverso': put(reverso(c[2]), c[1] - c[2], c[3], 0.5)
        elif k == 'braam': put(braam(), c[1], c[2], 0.7)
        elif k == 'queda': put(queda(), c[1], c[2], 0.4)
        else: raise ValueError(k)
    il, ir_ = ir()
    L += fftconvolve(WL, il)[:N]; R += fftconvolve(WR, ir_)[:N]
    st = np.stack([L, R], 1); st = hp(st.T, 25).T
    pk = np.abs(st).max() + 1e-9; st *= 10 ** (-3 / 20) / pk  # pico a −3 dBFS; o nível final é dado pelo peso no assemble
    return st

if __name__ == '__main__':
    EP = os.environ['EP']; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); BASE = os.path.join(HERE, f'ep{EP}')
    spec = importlib.util.spec_from_file_location('tcfg', os.path.join(BASE, 'tensao_cfg.py')); cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
    st = render(cfg.CUES, cfg.END); os.makedirs(os.path.join(BASE, 'out'), exist_ok=True)
    dst = os.path.join(BASE, 'out', 'tensao.wav'); wavfile.write(dst, SR, (st * 32767).astype(np.int16))
    print(dst, f'{len(st) / SR:.2f}s', len(cfg.CUES), 'deixas')
