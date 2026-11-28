#!/usr/bin/env python3
"""Design sonoro do vídeo 03, 100% sintetizado e dirigido pelos dados da animação (v2/ep03/plan.py):
polo (vento gelado), salto e queda, túnel (zumbido elétrico + anéis passando na mesma cadência da imagem),
núcleo (ronco grave), espaço (drone), Téo subindo e caindo de volta, batida na parede, sons de interface nos rótulos,
transições nos cortes e música discreta. A voz NÃO é tocada aqui.
Saída: v2/ep03/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P
import scene_consts as SCC

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(33)
def sos(kind, f, o=2): return butter(o, f, kind, fs=SR, output='sos')
def bp(x, lo, hi): return sosfilt(sos('bandpass', [lo, hi]), x)
def lp(x, f): return sosfilt(sos('lowpass', f), x)
def env(d, a=0.003, k=6.0):
    x = np.arange(int(d * SR)) / SR; return np.minimum(x / a, 1) * np.exp(-k * x / d)
def noise(n=N): return rng.standard_normal(n)

L = np.zeros(N); R = np.zeros(N); events = dict(pops=[], cuts=[], impacts=[], rings=0)
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
names = [shot_at(min(T, T_END - 1e-4)).name for T in tc]
def up(a): return np.interp(t, tc, np.asarray(a, float))
def smooth(x, s=0.04):
    k = int(s * SR); w = np.hanning(2 * k + 1); w /= w.sum(); return np.convolve(x, w, 'same')
def mask(*ns): return smooth(up([1.0 if n in ns else 0.0 for n in names]))
polo = mask('A', 'H'); space = mask('B', 'D', 'G', 'I', 'J', 'K'); tun = mask('E', 'F', 'L')
# C começa na superfície e mergulha no poço: vento -> túnel
Cm = up([1.0 if n == 'C' else 0.0 for n in names]); cdepth = up([min(1.0, max(0.0, -P.C.teo_z(T) / 30.0)) if n == 'C' else 0.0 for T, n in zip(tc, names)])
polo = polo + smooth(Cm) * (1 - cdepth); tun = tun + smooth(Cm) * cdepth

def whoosh(d=0.6, f0=400, f1=2600):
    n = int(d * SR); xx = np.arange(n) / n; e_ = np.sin(np.pi * xx) ** 2; f = np.linspace(f0, f1, n)
    nz = noise(n); out = np.zeros(n)
    for a in range(0, n, 2048):
        b = min(n, a + 2048); fc = f[a]; out[a:b] = bp(nz[max(0, a - 512):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    return out * e_

# ------------------------------------------------------------------ polo: vento gelado com rajadas e neve fina
gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t) * np.sin(2 * np.pi * 0.41 * t + 1)
icew = (lp(noise(), 500) * 0.6 + bp(noise(), 600, 2400) * 0.25 * gust + bp(noise(), 4000, 9000) * 0.03) * gust
add_st(icew * polo, 0.55)
# ------------------------------------------------------------------ espaço: drone grave
drone = (np.sin(2 * np.pi * 41.2 * t) + 0.6 * np.sin(2 * np.pi * 61.7 * t + 1) + 0.3 * np.sin(2 * np.pi * 82.4 * t + 2)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t))
add_st((drone * 0.10 + lp(noise(), 400) * 0.08) * space, 1.0)
# ------------------------------------------------------------------ túnel: zumbido + anéis passando (mesma cadência da imagem)
hum = (np.sin(2 * np.pi * 60 * t) * 0.5 + np.sin(2 * np.pi * 120 * t) * 0.3 + np.sin(2 * np.pi * 180 * t) * 0.1) * 0.08
add_st(hum * tun, 1.0)
# posição dos anéis relativa à câmera: s(T) integra a velocidade de cada plano de túnel (como no render)
ring_t = []
for s in P.SHOTS:
    if s.kind == 'tunel':
        sd, prev = 0.0, None; Ts = np.arange(s.t0, s.t1, 1 / 600)
        for T in Ts:
            dt = 0 if prev is None else T - prev; prev = T; sd_new = sd + dt * s.speed(T)
            if int(sd_new / SCC.SEG) != int(sd / SCC.SEG): ring_t.append(T)
            sd = sd_new
    if s.name == 'C':            # anéis passando pela câmera que cai junto com o Téo
        prev = None
        for T in np.arange(P.T_PULO, s.t1, 1 / 600):
            z = P.C.cam(T)['pos'][2]
            if prev is not None and int((z + 4) / SCC.SEG) != int((prev + 4) / SCC.SEG): ring_t.append(T)
            prev = z
for rt in ring_t:
    n = int(0.12 * SR); xx = np.arange(n) / SR; e_ = np.sin(np.pi * xx / 0.12) ** 2
    zz = (np.sin(2 * np.pi * 240 * xx) * 0.5 + bp(noise(n), 1500, 5000) * 0.3) * e_
    place(zz, rt - 0.06, 0.05, rng.uniform(-0.4, 0.4))
events['rings'] = len(ring_t)
# núcleo (E): ronco grave e chiado de calor
Em = mask('E'); rumble = (lp(noise(), 120) * 1.2 + np.sin(2 * np.pi * 33 * t) * 0.4) * Em
add_st(rumble, 0.35); add_st(bp(noise(), 3000, 8000) * Em * 0.04, 1.0)
place(whoosh(1.2, 300, 3500), 28.0 - 0.4, 0.3)
# ------------------------------------------------------------------ salto (C): passos, impulso e mergulho
place(bp(noise(int(0.08 * SR)), 300, 2000) * env(0.08), P.T_PULO - 0.05, 0.25)
place(whoosh(1.0, 1800, 300), P.T_PULO + 0.1, 0.35)
# ------------------------------------------------------------------ Téo sobe e cai de volta (H, Polo Sul)
Hs = P.BY_NAME['H']
place(whoosh(1.6, 300, 1600), 41.6, 0.3)
n = int(0.5 * SR); xx = np.arange(n) / SR; place(np.sin(2 * np.pi * (900 + 300 * xx) * xx) * env(0.5, k=4) * 0.6, P.T_AP - 0.1, 0.12)    # "v = 0": nota suspensa
place(whoosh(1.4, 1600, 250), 45.5, 0.32)
# ------------------------------------------------------------------ oscilação (I): passagens rápidas pelo centro
Ii = P.BY_NAME['I']
centers = [T for T in np.arange(Ii.t0, Ii.t1, 1 / 300) if abs(P.F.fall(Ii.tphys(T))[0]) < 0.01 * P.F.R]
last = -9
for c in centers:
    if c - last > 0.2: place(whoosh(0.35, 500, 2200), c - 0.17, 0.16); last = c
# ------------------------------------------------------------------ rotação (K) e batida na parede (L)
Km = mask('K'); add_st(bp(noise(), 120, 600) * Km * 0.18, 1.0)
Ls = P.BY_NAME['L']
e_ = env(0.6, a=0.002, k=5); xx = np.arange(len(e_)) / SR
bonk = (np.sin(2 * np.pi * (180 - 60 * xx) * xx) + 0.6 * np.sin(2 * np.pi * 523 * xx) * np.exp(-12 * xx) + lp(noise(len(e_)), 900) * 0.8) * e_
place(bonk, Ls.T_HIT, 0.6, 0.5); events['impacts'].append(round(Ls.T_HIT, 3))
scrape = bp(noise(int(1.6 * SR)), 1500, 6000) * np.linspace(1, 0, int(1.6 * SR)) ** 2
place(scrape, Ls.T_HIT + 0.05, 0.08, 0.6)
# ------------------------------------------------------------------ interface (rótulos), "38 min" e transições
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); xx = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * xx / 0.09) * xx) * 0.5 + np.sin(2 * np.pi * 3000 * xx) * 0.15) * e_
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90} | {P.D.graph['t_on'], 22.6})
for p_ in pops: place(pop_sound(), p_, 0.22); events['pops'].append(p_)
for f_ in (1046.5, 1318.5, 1568.0):        # acorde brilhante na resposta "38 min"
    n = int(1.4 * SR); xx = np.arange(n) / SR; place(np.sin(2 * np.pi * f_ * xx) * np.exp(-3 * xx) * np.minimum(xx / 0.005, 1), 37.05, 0.07)
for s in P.SHOTS[1:]:
    place(whoosh(0.55), s.t0 - 0.30, 0.12); events['cuts'].append(s.t0)

# ------------------------------------------------------------------ música: pad + pulso (Mi m – Dó – Sol – Ré), 92 BPM
mus = np.zeros(N); BPM = 92; beat = 60 / BPM; bar = 4 * beat
CH = [(52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(T_END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]; d = int(bar * SR); xx = np.arange(d) / SR
    padv = sum(np.sin(2 * np.pi * mtof(m - 12) * xx + j) * 0.5 + np.sin(2 * np.pi * mtof(m) * xx * 1.003) * 0.25 for j, m in enumerate(chord))
    padv *= np.minimum(xx / 0.5, 1) * np.minimum((bar - xx) / 0.5, 1)
    i = int(t0 * SR); j = min(N, i + d); mus[i:j] += lp(padv, 1600)[:j - i] * 0.05
    for q in range(8):
        m = chord[q % 3] + 12 + (12 if q % 4 == 3 else 0); dd = int(0.4 * SR); x2 = np.arange(dd) / SR
        nt = (np.sin(2 * np.pi * mtof(m) * x2) + 0.3 * np.sin(4 * np.pi * mtof(m) * x2)) * np.exp(-8 * x2) * np.minimum(x2 / 0.004, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += nt[:b_ - a_] * 0.03
    for k in range(4):
        dd = int(0.25 * SR); x2 = np.arange(dd) / SR
        kk = np.sin(2 * np.pi * (55 * x2 + 60 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-14 * x2)
        a_ = int((t0 + k * beat) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += kk[:b_ - a_] * 0.05
cta = mask('F'); mus *= (1 - 0.85 * smooth(cta, 0.2))
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)

fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.7
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', events['impacts'], '| anéis', events['rings'], '| pops', len(events['pops']), '| cortes', len(events['cuts']))
