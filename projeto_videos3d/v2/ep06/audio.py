#!/usr/bin/env python3
"""Design sonoro do vídeo 06, 100% sintetizado e dirigido pelo plano (v2/ep06/plan.py): cidade abandonada (vento, gemidos graves
dos zumbis ao longe), mata (insetos, gotas), formiga (passinhos), esporos (brilhos), laboratório (zumbido), escudo (tom), vírus (pulsação),
cão (rosnado), morcego (bater de asas), gráfico (bipes nos ataques). A voz NÃO é tocada aqui.
Saída: v2/ep06/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
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



# ------------------------------------------------------------------ cidade e rua
cid = kmask('cidade'); rua = kmask('rua')
add_st(lp(noise(), 500) * cid * 0.35, 1.0)
for k in range(14):
    at = rng.uniform(0, T_END); n = int(1.2 * SR); xx = np.arange(n) / SR
    moan = (np.sin(2 * np.pi * (110 + 15 * np.sin(2 * np.pi * 0.8 * xx)) * xx) * 0.6 + lp(noise(n), 300) * 0.4) * np.sin(np.pi * xx / 1.2) ** 2
    seg = np.zeros(N); i = int(at * SR); j = min(N, i + n); seg[i:j] = moan[:j - i]; add_st(lp(seg, 600) * cid, 0.06, rng.uniform(-0.7, 0.7))
amb = lp(noise(), 350) * 0.5 + bp(noise(), 300, 1200) * 0.12; add_st(amb * rua, 0.3)
for k in range(int(T_END * 1.3)):
    at = rng.uniform(0, T_END); n = int(0.18 * SR); xx = np.arange(n) / SR; f0 = rng.uniform(2800, 4200)
    chirp = np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * 14 * xx)) * xx) * np.sin(np.pi * xx / 0.18) ** 2
    seg = np.zeros(N); i = int(at * SR); j = min(N, i + n); seg[i:j] = chirp[:j - i]; add_st(seg * rua, 0.02, rng.uniform(-0.7, 0.7))
# ------------------------------------------------------------------ mata: insetos e gotas; esporos
mata = kmask('mata'); add_st(bp(noise(), 4000, 9000) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) * mata * 0.03 + lp(noise(), 300) * mata * 0.08, 1.0)
for k in range(20):
    at = rng.uniform(6, 26); place(tone(rng.uniform(900, 1500), 0.1, 20) * 0.4, at, 0.04 * float(shot_at(at).kind == 'mata'), rng.uniform(-0.6, 0.6))
place(tone(220, 0.6, 5) * 0.6, P.T_MORRE, 0.1); events['impacts'].append(P.T_MORRE)
for k in range(30): place(tone(rng.uniform(2400, 3800), 0.08, 25) * 0.5, P.T_ESPORO + rng.uniform(0, 1.0), 0.05, rng.uniform(-0.8, 0.8))
place(whoosh(1.0, 300, 1800), P.T_CRESCE - 0.1, 0.18)
# ------------------------------------------------------------------ laboratório, escudo, vírus
add_st((np.sin(2 * np.pi * 120 * t) * 0.3 + lp(noise(), 200) * 0.3) * kmask('lab') * 0.25, 1.0)
C4 = P.BY_NAME['C4']; place(tone(440, 1.4, 1.5) + tone(660, 1.4, 1.5) * 0.5, C4.shield, 0.12); events['impacts'].append(C4.shield)
vir = kmask('virus'); add_st(np.sin(2 * np.pi * 50 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.2 * t)) * vir * 0.2 + bp(noise(), 2000, 6000) * vir * 0.02, 1.0)
# ------------------------------------------------------------------ cão (rosnado) e morcego
D2 = P.BY_NAME['D2']; n = int((D2.t1 - D2.t0) * SR); xx = np.arange(n) / SR
growl = lp(noise(n), 350) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * xx)) * np.minimum(xx / 0.3, 1); place(growl, D2.t0, 0.4)
for s_ in P.SHOTS:
    if getattr(s_, 'bat', False):
        for k in range(int((s_.t1 - s_.t0) * 6)): place(bp(noise(int(0.04 * SR)), 300, 1500) * env(0.04), s_.t0 + k / 6, 0.05, 0.3)
# ------------------------------------------------------------------ gráfico: bipes nos ataques
F4 = P.BY_NAME['F4']; t1, t2 = F4.panel[4]
for i in range(1, 11): place(tone(1200, 0.08, 20), t1 + (t2 - t1) * i / 10, 0.1)
# ------------------------------------------------------------------ interface (rótulos e painéis) e transições
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); xx = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * xx / 0.09) * xx) * 0.5 + np.sin(2 * np.pi * 3000 * xx) * 0.15) * e_
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90} | {round(s.panel[1], 3) for s in P.SHOTS if s.panel and s.panel[1] > s.t0 + 0.05})
for p_ in pops: place(pop_sound(), p_, 0.22); events['pops'].append(p_)
for s in P.SHOTS[1:]:
    place(whoosh(0.45), s.t0 - 0.24, 0.10); events['cuts'].append(s.t0)

# ------------------------------------------------------------------ música: Lá m – Fá – Dó – Sol, 96 BPM, mais tensa no meio
mus = np.zeros(N); BPM = 96; beat = 60 / BPM; bar = 4 * beat
CH = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
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
mus *= 1 - 0.8 * nmask('E1')                                       # CTA
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)
fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.7
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', events['impacts'], '| pops', len(events['pops']), '| cortes', len(events['cuts']))
