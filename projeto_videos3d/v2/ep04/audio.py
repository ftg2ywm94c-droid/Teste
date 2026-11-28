#!/usr/bin/env python3
"""Design sonoro do vídeo 04, 100% sintetizado e dirigido pelo plano (v2/ep04/plan.py):
rua (pássaros, trânsito ao longe), moléculas (brilho no ar e estalos quando somem), ouvidos estalando (som abafado + clique),
fogo apagando, motor do carro parando, turbinas do jato morrendo, coração e fluxo de sangue, alarme e máscaras na cabine,
batida do "MITO", tons de cristal nos átomos, o ar voltando (inspiração), pisca-alerta no fim. A voz NÃO é tocada aqui.
Saída: v2/ep04/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
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

# ------------------------------------------------------------------ rua: ambiente (trânsito ao longe + pássaros)
rua = kmask('rua')
amb = lp(noise(), 350) * 0.5 + bp(noise(), 300, 1200) * 0.12
add_st(amb * rua, 0.35)
for k in range(int(T_END * 1.3)):
    at = rng.uniform(0, T_END); n = int(0.18 * SR); xx = np.arange(n) / SR; f0 = rng.uniform(2800, 4200)
    chirp = np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * 14 * xx)) * xx) * np.sin(np.pi * xx / 0.18) ** 2
    seg = np.zeros(N); i = int(at * SR); j = min(N, i + n); seg[i:j] = chirp[:j - i]; add_st(seg * rua, 0.02, rng.uniform(-0.7, 0.7))
# carro: motor em A1 (passando) e D4 (morre em engine_off)
A1 = P.BY_NAME['A1']; D4 = P.BY_NAME['D4']
eng = (np.sin(2 * np.pi * 38 * t) + 0.5 * np.sin(2 * np.pi * 76 * t) + lp(noise(), 200) * 0.6)
add_st(eng * nmask('A1') * 0.25, 1.0, 0.3)
d4 = nmask('D4') * (1 - smooth(up([1.0 if T > D4.engine_off else 0.0 for T in tc]), 0.08))
add_st(eng * d4 * 0.35, 1.0)
place(bp(noise(int(0.35 * SR)), 80, 400) * env(0.35, k=5), D4.engine_off, 0.3)        # engasgo do motor
# ------------------------------------------------------------------ moléculas: brilho no ar; estalos quando o O₂ some
mol = kmask('mol'); shimmer = bp(noise(), 5000, 11000) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t))
add_st(shimmer * mol * 0.03 + lp(noise(), 250) * mol * 0.06, 1.0)
for tv in (P.T_SOME, P.T_SOME_B):
    for k in range(26):
        at = tv + rng.uniform(0, 0.4); place(tone(rng.uniform(900, 1700), 0.06, 30) * 0.6, at, 0.07, rng.uniform(-0.8, 0.8))
    place(whoosh(0.5, 2500, 300), tv - 0.05, 0.18); events['impacts'].append(tv)
# ------------------------------------------------------------------ pressão caindo e ouvidos
C1 = P.BY_NAME['C1']; t1, t2 = C1.panel[3]
n = int((t2 - t1) * SR); xx = np.arange(n) / n; place(lp(noise(n), 120) * np.sin(np.pi * xx) * 1.2 + np.sin(2 * np.pi * (60 - 25 * xx) * xx * (t2 - t1)) * np.sin(np.pi * xx), t1, 0.25)
def ploc():
    e_ = env(0.12, a=0.001, k=9); xx = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (420 - 1500 * xx) * xx) + lp(noise(len(e_)), 1200) * 0.5) * e_
for at in (20.62, 67.28): place(ploc(), at, 0.55); events['impacts'].append(at)
muff = nmask('C2'); add_st(lp(noise(), 160) * muff * 0.25, 1.0)
# subida rápida (C3): vento e nuvens
place(whoosh(2.2, 200, 3000), 21.8, 0.45)
# ------------------------------------------------------------------ fogo: crepitar e "fuff" ao apagar
fire = nmask('D1') * (1 - smooth(up([1.0 if T > P.T_FOGO else 0.0 for T in tc]), 0.05))
crack = np.zeros(N)
for k in range(60):
    i = int(rng.uniform(24.7, P.T_FOGO) * SR); m = int(0.01 * SR); crack[i:i + m] += noise(m) * np.exp(-np.arange(m) / (0.002 * SR))
add_st((bp(noise(), 200, 1500) * 0.15 + hp(crack, 1500) * 0.6) * fire, 0.4)
place(lp(noise(int(0.4 * SR)), 500) * env(0.4, a=0.005, k=7), P.T_FOGO, 0.45)
# vela: chiado do pavio (D2); gás sem chama (D3): chiado fino
add_st(bp(noise(), 3000, 7000) * nmask('D3') * 0.04, 1.0)
# ------------------------------------------------------------------ jato: turbinas morrem; só o vento
E1 = P.BY_NAME['E1']
jet = bp(noise(), 300, 4000) * 0.6 + np.sin(2 * np.pi * 1200 * t) * 0.03
roar = up([E1.engines(T) if n == 'E1' else (1.0 if n == 'G1' else 0.0) for T, n in zip(tc, names)])
add_st(jet * smooth(roar, 0.1) * 0.35, 1.0)
wind = lp(noise(), 900) * (nmask('E1', 'G1') * 0.5 + nmask('C3') * 0.3)
add_st(wind, 0.35)
n = int(1.2 * SR); xx = np.arange(n) / SR; place(np.sin(2 * np.pi * (520 - 260 * xx / 1.2) * xx) * np.exp(-1.5 * xx) * 0.5, 29.3, 0.18)   # rotação caindo
# ------------------------------------------------------------------ corpo: coração e sangue
pul = kmask('pulmao')
hb = np.zeros(N)
for k in range(int(T_END / 0.85)):
    at = k * 0.85
    for d_, g in ((0.0, 1.0), (0.2, 0.7)):
        i = int((at + d_) * SR); m = int(0.12 * SR)
        if i + m < N: hb[i:i + m] += np.sin(2 * np.pi * 55 * np.arange(m) / SR) * np.exp(-np.arange(m) / (0.03 * SR)) * g
add_st(hb * pul * 0.5 + lp(noise(), 300) * nmask('F3') * 0.15, 1.0)
for k in range(24):
    at = 37.3 + 2.8 * k / 24; place(tone(rng.uniform(1400, 2200), 0.08, 25) * 0.5, at, 0.05, rng.uniform(-0.6, 0.6))   # O₂ saindo
# ------------------------------------------------------------------ cabine: alarme + máscaras
G2 = P.BY_NAME['G2']
for k in range(3): place(tone(880, 0.35, 3) + tone(660, 0.35, 3) * 0.6, G2.drop - 0.12 + 0.55 * k, 0.12)
for k in range(30): place(bp(noise(int(0.05 * SR)), 1500, 5000) * env(0.05), G2.drop + 0.025 * k + rng.uniform(0, 0.08), 0.04, rng.uniform(-0.8, 0.8))
add_st(lp(noise(), 300) * kmask('cabine') * 0.25, 1.0)
# ------------------------------------------------------------------ revelação: batida do "MITO", cristais, Terra
e_ = env(0.8, a=0.002, k=5); xx = np.arange(len(e_)) / SR
place((np.sin(2 * np.pi * (90 - 30 * xx) * xx) + lp(noise(len(e_)), 600) * 0.7) * e_, 54.28, 0.55); events['impacts'].append(54.28)
cr = kmask('cristal'); add_st(bp(noise(), 6000, 12000) * cr * 0.02, 1.0)
drone = (np.sin(2 * np.pi * 41.2 * t) + 0.6 * np.sin(2 * np.pi * 61.7 * t + 1)) * 0.1
add_st(drone * kmask('terra', 'cristal'), 1.0)
# ------------------------------------------------------------------ o ar volta: inspiração longa
place(whoosh(1.1, 300, 2500) * np.linspace(0.3, 1, int(1.1 * SR)), P.T_VOLTA - 0.6, 0.35)
# pisca-alerta (L2)
L2 = P.BY_NAME['L2']
for k in range(int((L2.t1 - L2.t0) * 1.6) + 1):
    at = L2.t0 + k / 1.6; place(bp(noise(int(0.03 * SR)), 1800, 4000) * env(0.03), at, 0.08, 0.3); place(bp(noise(int(0.03 * SR)), 1200, 3000) * env(0.03), at + 0.31, 0.06, 0.3)
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
mus *= (1 - 0.85 * nmask('H1'))                                   # CTA: música quase some
mus *= 1 - 0.6 * smooth(up([1.0 if 54.2 < T < 55.3 else 0.0 for T in tc]), 0.05)   # respiro no "Mito"
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)

fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.7
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', events['impacts'], '| pops', len(events['pops']), '| cortes', len(events['cuts']))
