#!/usr/bin/env python3
"""Design sonoro do vídeo 07, 100% sintetizado e dirigido pelo plano (v2/ep07/plan.py): cidade abandonada (vento, gemidos graves
dos zumbis ao longe), mata (insetos, gotas), formiga (passinhos), esporos (brilhos), laboratório (zumbido), escudo (tom), vírus (pulsação),
cão (rosnado), morcego (bater de asas), gráfico (bipes nos ataques). A voz NÃO é tocada aqui.
Saída: v2/ep07/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(44)
def sos(kind, f, o=2): return butter(o, f, kind, fs=SR, output='sos')
def bp(x, lo, hi): return sosfilt(sos('bandpass', [lo, hi]), x)
def lp(x, f): return sosfilt(sos('lowpass', f), x)
def hp(x, f): return sosfilt(sos('highpass', f), x)
def env(d, a=0.003, k=6.0):
    x = np.arange(int(d * SR)) / SR; return np.minimum(x / a, 1) * np.exp(-k * x / d)
def noise(n=N): return rng.standard_normal(n)

L = np.zeros(N); R = np.zeros(N); events = dict(pops=[], cuts=[], impacts=[])
def add_st(sig, gain=1.0, pan=0.0):
    global L, R
    L += sig * gain * np.sqrt((1 - pan) / 2) * 1.41; R += sig * gain * np.sqrt((1 + pan) / 2) * 1.41
def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(i, 0); b = min(N, i + len(sig)); seg = np.zeros(N); seg[a:b] = sig[a - i:b - i]; add_st(seg, gain, pan)

CR = 1000; tc = np.arange(int(T_END * CR) + 1) / CR
def shot_at(T):
    for s in P.SHOTS:
        if s.t0 <= T < s.t1: return s
    return P.SHOTS[-1]
kinds = [shot_at(min(T, T_END - 1e-4)).kind for T in tc]; names = [shot_at(min(T, T_END - 1e-4)).name for T in tc]
def up(a): return np.interp(t, tc, np.asarray(a, float))
def smooth(x, s=0.04):
    k = int(s * SR); w = np.hanning(2 * k + 1); w /= w.sum(); return np.convolve(x, w, 'same')
def kmask(*ks): return smooth(up([1.0 if k in ks else 0.0 for k in kinds]))
def nmask(*ns): return smooth(up([1.0 if n in ns else 0.0 for n in names]))
def whoosh(d=0.6, f0=400, f1=2600):
    n = int(d * SR); xx = np.arange(n) / n; e_ = np.sin(np.pi * xx) ** 2; f = np.linspace(f0, f1, n)
    nz = noise(n); out = np.zeros(n)
    for a in range(0, n, 2048):
        b = min(n, a + 2048); fc = f[a]; out[a:b] = bp(nz[max(0, a - 512):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    return out * e_
def tone(f, d, k=4.0, a=0.004):
    xx = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * xx) * np.exp(-k * xx) * np.minimum(xx / a, 1)


# ------------------------------------------------------------------ vento (forte e uivante), chuva, trovões, árvore e destroços
wind_lvl = smooth(up([getattr(shot_at(min(T, T_END - 1e-4)), 'wind', 0.0) for T in tc]), 0.15)
rain_lvl = smooth(up([getattr(shot_at(min(T, T_END - 1e-4)), 'rain', 0.0) for T in tc]), 0.15)
gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.61 * t + 1.0)
howl = np.zeros(N)
for f0, g in ((380, 1.0), (520, 0.6), (760, 0.35)):
    howl += bp(noise(), f0 * 0.9, f0 * 1.15) * g * (0.5 + 0.5 * np.sin(2 * np.pi * (0.17 + f0 / 5000) * t + f0))
add_st((lp(noise(), 700) * 0.6 + howl * 0.5) * wind_lvl * gust, 0.55, -0.15)
add_st((lp(noise(), 700) * 0.6 + howl * 0.4) * wind_lvl * gust[::-1], 0.45, 0.15)
add_st(hp(noise(), 3000) * rain_lvl * 0.10 + bp(noise(), 800, 2500) * rain_lvl * 0.05, 1.0)
def thunder(d=2.6):
    n = int(d * SR); xx = np.arange(n) / SR
    return (lp(noise(n), 160) * 1.4 + bp(noise(n), 160, 900) * np.exp(-6 * xx) * 0.8) * np.minimum(xx / 0.02, 1) * np.exp(-1.4 * xx)
for s_ in P.SHOTS:
    for tf in getattr(s_, 'flash', ()): place(thunder(), tf + 0.25, 0.9); events['impacts'].append(tf)
place(thunder(3.0), 0.05, 0.6)
# árvore: estalo + queda
crack = bp(noise(int(0.25 * SR)), 1500, 6000) * env(0.25, 0.001, 9); place(crack, P.T_ARVORE, 0.5)
place(lp(noise(int(0.9 * SR)), 250) * env(0.9, 0.05, 4), P.T_ARVORE + 0.7, 0.9); events['impacts'].append(P.T_ARVORE + 0.7)
# apagão: zumbido elétrico que corta
n = int(0.5 * SR); xx = np.arange(n) / SR; place(np.sin(2 * np.pi * 120 * xx) * (1 - xx / 0.5) * 0.6 + bp(noise(n), 2000, 5000) * env(0.5, 0.001, 12) * 0.5, P.T_APAGA - 0.1, 0.25)
# destroços: batidas e tilintar de vidro
for s_ in P.SHOTS:
    if hasattr(s_, 'debris'):
        for k in range(int((s_.t1 - s_.t0) * 4)):
            at = s_.t0 + rng.uniform(0, s_.t1 - s_.t0)
            place(bp(noise(int(0.12 * SR)), 300, 2500) * env(0.12, 0.002, 10), at, 0.18, rng.uniform(-0.8, 0.8))
            if rng.random() < 0.4: place(sum(tone(rng.uniform(3000, 6000), 0.25, 14) for _ in range(3)) * 0.3, at + 0.05, 0.06, rng.uniform(-0.8, 0.8))
# espaço e relevo: grave contínuo; furacão no relevo perde força
add_st(lp(noise(), 120) * kmask('globo') * 0.25 + np.sin(2 * np.pi * 45 * t) * kmask('globo') * 0.1, 1.0)
F4 = P.BY_NAME['F4']; wk = np.clip((t - F4.weaken[0]) / (F4.weaken[1] - F4.weaken[0]), 0, 1)
rel = kmask('relevo'); add_st((lp(noise(), 500) * 0.5 + howl * 0.3) * rel * (1 - 0.8 * wk) * 0.45, 1.0)
# painéis: bipes de leitura
place(tone(880, 0.12, 12), 21.8, 0.12); place(tone(1320, 0.18, 10), 24.6, 0.14); place(tone(330, 0.5, 4), 54.6, 0.2)
# ------------------------------------------------------------------ interface (rótulos e painéis) e transições
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); xx = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * xx / 0.09) * xx) * 0.5 + np.sin(2 * np.pi * 3000 * xx) * 0.15) * e_
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90} | {round(s.panel[1], 3) for s in P.SHOTS if s.panel and s.panel[1] > s.t0 + 0.05})
for p_ in pops: place(pop_sound(), p_, 0.22); events['pops'].append(p_)
for s in P.SHOTS[1:]:
    place(whoosh(0.45), s.t0 - 0.24, 0.10); events['cuts'].append(s.t0)

# ------------------------------------------------------------------ música: Ré m – Si♭ – Fá – Dó, 100 BPM, tensa
mus = np.zeros(N); BPM = 100; beat = 60 / BPM; bar = 4 * beat
CH = [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(T_END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]; d = int(bar * SR); xx = np.arange(d) / SR
    padv = sum(np.sin(2 * np.pi * mtof(m - 12) * xx + j) * 0.5 + np.sin(2 * np.pi * mtof(m) * xx * 1.003) * 0.25 for j, m in enumerate(chord))
    padv *= np.minimum(xx / 0.5, 1) * np.minimum((bar - xx) / 0.5, 1)
    i = int(t0 * SR); j = min(N, i + d); mus[i:j] += lp(padv, 1500)[:j - i] * 0.05
    for q in range(8):
        m = chord[q % 3] + 12 + (12 if q % 4 == 3 else 0); dd = int(0.35 * SR); x2 = np.arange(dd) / SR
        nt = (np.sin(2 * np.pi * mtof(m) * x2) + 0.3 * np.sin(4 * np.pi * mtof(m) * x2)) * np.exp(-9 * x2) * np.minimum(x2 / 0.004, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += nt[:b_ - a_] * 0.028
    for k in range(4):
        dd = int(0.25 * SR); x2 = np.arange(dd) / SR
        kk = np.sin(2 * np.pi * (55 * x2 + 60 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-14 * x2)
        a_ = int((t0 + k * beat) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += kk[:b_ - a_] * 0.05
mus *= 1 - 0.6 * nmask('H1')                                       # CTA
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)
fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.7
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', events['impacts'], '| pops', len(events['pops']), '| cortes', len(events['cuts']))
