#!/usr/bin/env python3
"""Trilha 100% sintetizada (sem samples de terceiros), dirigida pelos eventos reais da animação
(renders/preview/S*_events.json): passos no instante do contato do pé, motor pela velocidade do carro,
freada enquanto o freio está ativo. Uso: python3 scripts/mix_audio.py"""
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR = 48000; STRIDE = 0.85; rng = np.random.default_rng(3)
fr = []; 
for s in ('S1', 'S2', 'S3'): fr += json.load(open(f'renders/preview/{s}_events.json'))['frames']
N = len(fr); T = N / 30; n = int(T * SR); t = np.arange(n) / SR
def filt(x, lo=None, hi=None):
    if lo and hi: b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band')
    elif hi: b, a = butter(2, hi / (SR / 2), 'low')
    else: b, a = butter(2, lo / (SR / 2), 'high')
    return lfilter(b, a, x)
def up(key): return np.interp(t, np.arange(N) / 30, [f[key] for f in fr])
def place(buf, sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig)); 
    if 0 <= i < n: buf[i:j] += sig[:j - i] * g
def env(d, a=0.004, k=6): x = np.arange(int(d * SR)) / SR; return np.minimum(x / a, 1) * np.exp(-k * x / d)
amb = filt(rng.standard_normal(n), 150, 1800) * 0.012
for bt in np.sort(rng.uniform(0, T, 9)):                                   # passarinhos
    for k in range(rng.integers(2, 5)):
        d = 0.07; x = np.arange(int(d * SR)) / SR; f0 = rng.uniform(3200, 4600)
        place(amb, np.sin(2 * np.pi * (f0 * x + 2500 * x * x)) * np.hanning(len(x)), bt + k * 0.11, 0.018)
steps = np.zeros(n); events = []
for i in range(1, N):                                                      # contato de cada pé (meio ciclo)
    a, b = fr[i - 1]['s'] / STRIDE * 2, fr[i]['s'] / STRIDE * 2
    if np.floor(b) > np.floor(a) and b - a < 1:
        tt = (i - 1 + (np.floor(b) - a) / (b - a)) / 30; events.append(round(tt, 3))
        e = env(0.09, k=7); s = filt(rng.standard_normal(len(e)), 300, 2600) * e * 0.5 + np.sin(2 * np.pi * 95 * np.arange(len(e)) / SR) * e * 0.6
        place(steps, s, tt, 0.20 * rng.uniform(0.8, 1.1))
for i in range(1, N):                                                      # aterrissagem do pulinho
    if fr[i - 1].get('hop') and not fr[i].get('hop'):
        e = env(0.14, k=6); place(steps, np.sin(2 * np.pi * 70 * np.arange(len(e)) / SR) * e + filt(rng.standard_normal(len(e)), 200, 1500) * e * .4, i / 30, 0.3)
    if fr[i].get('hop') and not fr[i - 1].get('hop'):
        d = 0.22; x = np.arange(int(d * SR)) / SR; place(steps, np.sin(2 * np.pi * (320 * x + 1500 * x * x)) * np.hanning(len(x)), i / 30, 0.14)
v = up('car_v'); cx = up('car_x'); cam = np.array([np.interp(t, np.arange(N) / 30, [f['cam'][k] for f in fr]) for k in range(3)])
dist = np.sqrt((cx - cam[0]) ** 2 + (0.95 - cam[2]) ** 2 + 1); gain = 1 / (1 + (dist / 5) ** 1.6)
f0 = 42 + 7.5 * v; ph = 2 * np.pi * np.cumsum(f0) / SR
eng = sum(np.sin(ph * k) / k ** 1.2 for k in (1, 2, 3, 4, 6)) * (0.55 + 0.45 * np.sin(ph * 0.5))
eng = filt(eng, hi=900) * 0.16 + filt(rng.standard_normal(n), 300, 2500) * 0.05 * (v / 10)
car = eng * gain
br = up('brake'); 
vib = 1 + 0.012 * np.sin(2 * np.pi * 31 * t); sq = np.sin(2 * np.pi * np.cumsum(1250 * vib + 60 * v) / SR) * 0.6 + filt(rng.standard_normal(n), 1800, 5200) * 0.9
car += sq * np.clip(br, 0, 1) ** 2 * np.clip(v / 6, 0, 1) ** 0.6 * 0.20 * np.clip(gain * 2.2, 0, 1)
stop_i = next((i for i in range(1, N) if fr[i]['car_v'] == 0 and fr[i - 1]['car_v'] > 0), None)
if stop_i:
    e = env(0.25, k=5); place(car, np.sin(2 * np.pi * 55 * np.arange(len(e)) / SR) * e, stop_i / 30, 0.35)
mus = np.zeros(n)                                                          # ostinato simples (original)
def note(f, d=0.5):
    x = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(4 * np.pi * f * x) + 0.12 * np.sin(8 * np.pi * f * x)) * np.minimum(x / 0.003, 1) * np.exp(-7 * x)
C = dict(c=261.63, d=293.66, e=329.63, g=392.0, a=440.0, C=523.25, G2=196.0, C2=130.81, F2=174.61)
pat = 'c e g e a g e d'.split(); beat = 0.3
tb = (stop_i / 30 - 1.4) if stop_i else T
for k in range(int(tb / beat)):
    place(mus, note(C[pat[k % 8]]), k * beat, 0.05)
    if k % 4 == 0: place(mus, note(C['C2' if (k // 4) % 2 == 0 else 'F2'], 0.9), k * beat, 0.07)
if stop_i:
    for j, nn in enumerate(('c', 'e', 'g', 'C')): place(mus, note(C[nn], 1.2), stop_i / 30 + 1.25 + j * 0.09, 0.07)
mix = amb + steps + car + mus
pan = np.clip(0.5 + 0.03 * (cx - cam[0]), 0.2, 0.8)
L = amb + steps + mus + car * np.sqrt(1 - pan) * 1.4; R = amb + steps + mus + car * np.sqrt(pan) * 1.4
st = np.stack([L, R], 1); st *= np.minimum(t / 0.05, 1)[:, None] * np.minimum((T - t) / 0.25, 1)[:, None]
st = np.tanh(st / np.abs(st).max() * 1.6) * 0.80
wavfile.write('audio/sfx/mix.wav', SR, (st * 32767).astype(np.int16))
json.dump(dict(duration=T, footstep_times=events, car_stop=stop_i / 30 if stop_i else None, narration='AUSENTE (sem TTS pt-BR no ambiente)'), open('audio/sfx/mix_events.json', 'w'), indent=1)
print('ok', T, len(events), 'passos')
