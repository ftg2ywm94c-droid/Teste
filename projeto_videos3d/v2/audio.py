#!/usr/bin/env python3
"""Design sonoro do vídeo 01, 100% sintetizado (sem samples de terceiros) e dirigido pela mesma cinemática da animação
(v2/lib/story.py + v2/shots.py): motor e rodagem pela velocidade e distância à câmera, freada enquanto o freio atua,
passos no contato do pé, pulo/aterrissagem, quique da bola no meio-fio, sons de interface quando os rótulos aparecem,
transições nos cortes, efeito de câmera lenta (grave e abafado) e tempo congelado. Música discreta opcional.
Saída: v2/out/sfx.wav e v2/out/music.wav (48 kHz estéreo) + v2/out/sfx_events.json. A voz NÃO é tocada aqui."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, 'lib'), HERE]
import story as S
import shots as SH

SR = 48000; T_END = SH.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(11)
def sos(kind, f): return butter(2, f, kind, fs=SR, output='sos')
def bp(x, lo, hi): return sosfilt(sos('bandpass', [lo, hi]), x)
def lp(x, f): return sosfilt(sos('lowpass', f), x)
def hp(x, f): return sosfilt(sos('highpass', f), x)
def env(d, a=0.003, k=6.0):
    x = np.arange(int(d * SR)) / SR; return np.minimum(x / a, 1) * np.exp(-k * x / d)

# ------------------------------------------------------------------ estado da cena por instante (espelha v2/render.py)
def shot_at(T):
    for s in SH.SHOTS:
        if s.t0 <= T < s.t1: return s
    return SH.SHOTS[-1]

def state(T):
    s = shot_at(T); cars = []; kid = None; k = 1.0
    def st(tau, v0):
        xf, v = S.car_front(tau, v0); return xf, v, S.REACT < tau < S.stop_tau(v0)
    if hasattr(s, 'car'):
        xf, v = s.car(T); cars.append((xf - S.FRONT, S.LANE_R, v, False))
    elif s.name in ('F', 'G'):
        tau60 = (T - s.T60) if s.name == 'F' else s.tau60(T); tau50 = (T - s.T50) if s.name == 'F' else 99.0
        if s.name == 'G': k = (s.tau60(T + 0.01) - s.tau60(T - 0.01)) / 0.02
        a, v, b = st(tau60, S.V60); cars.append((a - S.FRONT, S.LANE_R, v, b))
        a, v, b = st(tau50, S.V50); cars.append((a - S.FRONT, S.LANE_L, v, b))
    else:
        tau = s.tau(T); k = (s.tau(T + 0.01) - s.tau(T - 0.01)) / 0.02
        a, v, b = st(tau, S.V60); cars.append((a - S.FRONT, S.LANE_R, v, b)); kid = tau
    c = s.cam(T)
    return s, cars, kid, k, np.array(c['pos']), np.array(c['look'])

# amostragem de controle a 1 kHz e interpolação para áudio
CR = 1000; tc = np.arange(int(T_END * CR) + 1) / CR
ctrl = [state(min(T, T_END - 1e-4)) for T in tc]
shot_name = [c[0].name for c in ctrl]
kscale = np.array([max(min(c[3], 1.0), 0.0) for c in ctrl])
def up(a): return np.interp(t, tc, a)

# ------------------------------------------------------------------ motor/pneus/freada por carro
def car_track(idx):
    v = np.zeros(len(tc)); g = np.zeros(len(tc)); pan = np.zeros(len(tc)); br = np.zeros(len(tc)); pres = np.zeros(len(tc))
    for i, (s, cars, kid, k, cp, cl) in enumerate(ctrl):
        if idx >= len(cars): continue
        x, y, vv, b = cars[idx]; p = np.array([x, y, 0.6]); d = np.linalg.norm(p - cp)
        fwd = cl - cp; fwd /= np.linalg.norm(fwd); right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right) + 1e-9
        v[i] = vv; g[i] = 1 / (1 + (d / 7.0) ** 1.4); pan[i] = np.clip(np.dot(p - cp, right) / (d + 1e-6), -1, 1); br[i] = b; pres[i] = 1
    return v, g, pan, br, pres

def engine(v, k, seed):
    r = np.random.default_rng(seed)
    gear = np.where(v < 7, v / 7, np.where(v < 12, (v - 7) / 5 + 0.35, (v - 12) / 6 + 0.45))
    f0 = (26 + 62 * gear) * (0.45 + 0.55 * k)                                  # câmera lenta derruba o tom
    ph = 2 * np.pi * np.cumsum(f0) / SR
    x = sum(np.sin(ph * h + r.uniform(0, 6)) / h ** 1.1 for h in (1, 2, 3, 4, 6, 8)) * (0.6 + 0.4 * np.sin(ph * 0.5))
    x = lp(x, 1400) * 0.30 + bp(r.standard_normal(N), 60, 400) * 0.06
    road = bp(r.standard_normal(N), 250, 2600) * 0.11 * (v / 16) ** 1.5
    return x, road

sfx_L = np.zeros(N); sfx_R = np.zeros(N); events = dict(steps=[], pops=[], cuts=[], brake=[], stops=[])
def add_st(sig, gain=1.0, pan=0.0):
    global sfx_L, sfx_R
    sfx_L += sig * gain * np.sqrt((1 - pan) / 2) * 1.41; sfx_R += sig * gain * np.sqrt((1 + pan) / 2) * 1.41
def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(i, 0); b = min(N, i + len(sig)); seg = np.zeros(N); seg[a:b] = sig[a - i:b - i]
    add_st(seg, gain, pan)

K = up(kscale)
freeze = up(np.array([1.0 if n == 'E' else 0.0 for n in shot_name]))
for idx, seed in ((0, 1), (1, 2)):
    v, g, pan, br, pres = car_track(idx)
    if pres.max() == 0: continue
    V, G, P, BR = up(v), up(g), up(pan), up(br)
    eng, road = engine(V, K, seed)
    muff = lp(eng + road, 500); slow = np.clip(1 - K, 0, 1)
    sig = ((eng + road) * (1 - slow) + muff * slow * 1.3) * G * (1 - freeze * 0.85)
    # freada: chiado tonal + ruído de atrito, proporcional à velocidade
    vib = 1 + 0.015 * np.sin(2 * np.pi * 23 * t)
    sq = np.sin(2 * np.pi * np.cumsum((1050 + 140 * np.sin(2 * np.pi * 0.7 * t)) * vib * (0.5 + 0.5 * K)) / SR) * 0.35
    sq += bp(rng.standard_normal(N), 1800, 6000) * 0.8
    sq = np.where(K < 0.5, lp(sq, 1200) * 1.4, sq)
    screech = sq * BR * np.clip(V / 6, 0, 1) ** 0.7 * G * 0.22 * (1 - freeze)
    add_st(sig, 1.0, 0.0); sfx_L += screech * np.sqrt((1 - P) / 2) * 1.41; sfx_R += screech * np.sqrt((1 + P) / 2) * 1.41
    # parada: baque da suspensão
    for i in range(1, len(tc)):
        if v[i - 1] > 0 and v[i] == 0 and br[i - 1] and shot_name[i] == shot_name[i - 1]:
            e = env(0.35, k=5); s_ = np.sin(2 * np.pi * 48 * np.arange(len(e)) / SR) * e + bp(rng.standard_normal(len(e)), 80, 900) * e * 0.4
            place(s_, tc[i], 0.5 * g[i], pan[i]); events['stops'].append(round(tc[i], 3))
        if br[i] and not br[i - 1]: events['brake'].append(round(tc[i], 3))

# ------------------------------------------------------------------ menino: passos, pulo, aterrissagem; bola
def step_sound(slowk):
    e = env(0.08 / max(slowk, 0.35), k=7); n = len(e)
    s_ = bp(rng.standard_normal(n), 250 * max(slowk, 0.4), 2400 * max(slowk, 0.4)) * e * 0.6 + np.sin(2 * np.pi * 90 * max(slowk, 0.5) * np.arange(n) / SR) * e * 0.5
    return s_
prev_d = None; prev_tau = None
from functools import lru_cache
@lru_cache(None)
def kid_dist(tau):
    n = 300; t0 = S.KID_PATH[0][0]; s = 0.0; px, py = S.kid_xy(t0)
    for i in range(1, n + 1):
        tt = t0 + (tau - t0) * i / n; x, y = S.kid_xy(tt); s += math.hypot(x - px, y - py); px, py = x, y
    return s
ball_prev = None
for i, (s, cars, kid, k, cp, cl) in enumerate(ctrl):
    if kid is None or s.name not in ('C', 'D1', 'D2', 'H'): prev_d = None; ball_prev = None; continue
    tau = round(kid, 3); kx, ky = S.kid_xy(tau)
    dk = np.linalg.norm(np.array([kx, ky, 0.3]) - cp); gk = 1 / (1 + (dk / 4.5) ** 1.5)
    d = kid_dist(tau) if tau < 1.55 else None
    if d is not None and prev_d is not None and math.floor(d / 0.525) > math.floor(prev_d / 0.525) and -2.6 < tau < 1.2:
        place(step_sound(k), tc[i], 0.55 * gk); events['steps'].append(round(tc[i], 3))
    prev_d = d
    if prev_tau is not None:
        if prev_tau < 1.56 <= tau: place(bp(rng.standard_normal(int(0.12 * SR)), 300, 3000) * env(0.12, k=4) * 0.5, tc[i], gk)          # impulso
        if prev_tau < 2.0 <= tau:                                                                                                         # aterrissagem
            e = env(0.25, k=5); place((np.sin(2 * np.pi * 70 * np.arange(len(e)) / SR) + bp(rng.standard_normal(len(e)), 150, 1600) * 0.5) * e, tc[i], 0.7 * gk)
    by = S.ball_xy(tau)[1]; db = np.linalg.norm(np.array([0.6, by, 0.1]) - cp); gb = 1 / (1 + (db / 4.5) ** 1.5)
    if ball_prev is not None:
        for edge in (-3.58,):
            if ball_prev < edge <= by:
                for j, (dt, a) in enumerate(((0, 1.0), (0.16, 0.45), (0.27, 0.2))):
                    e = env(0.12, k=6); place((np.sin(2 * np.pi * 210 * np.arange(len(e)) / SR) * 0.7 + bp(rng.standard_normal(len(e)), 300, 2500) * 0.4) * e, tc[i] + dt, 0.6 * a * gb)
        if ball_prev <= -8.49 < by: place(bp(rng.standard_normal(int(0.1 * SR)), 200, 1800) * env(0.1) * 0.6, tc[i], gb)
    ball_prev = by; prev_tau = tau

# ------------------------------------------------------------------ interface, transições, câmera lenta, congelamento
def pop_sound():
    e = env(0.09, a=0.001, k=8); x = np.arange(len(e)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * x / 0.09) * x) * 0.5 + np.sin(2 * np.pi * 3000 * x) * 0.15) * e
caps = json.load(open(os.path.join(HERE, 'out', 'legenda.json')))
POPS = [23.55, 26.3, SH.BY_NAME['F'].T50 + S.stop_tau(S.V50), SH.BY_NAME['F'].T60 + S.stop_tau(S.V60), 32.0, 57.85] + [h[0] + 0.05 for h in caps['hud']]
for p in POPS: place(pop_sound(), p, 0.22); events['pops'].append(round(p, 3))
def whoosh(d=0.6, up_=True):
    n = int(d * SR); x = np.arange(n) / n; e = np.sin(np.pi * x) ** 2
    f = np.linspace(400, 2600, n) if up_ else np.linspace(2600, 300, n)
    nz = rng.standard_normal(n); out = np.zeros(n)
    for a in range(0, n, 2048):                          # filtro varrido em blocos
        b = min(n, a + 2048); fc = f[a]; out[a:b] = bp(nz[max(0, a - 512):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    return out * e
for s in SH.SHOTS[1:]:
    w = whoosh(0.55, s.name not in ('D1', 'E')); place(w, s.t0 - 0.30, 0.10 if s.name in ('B', 'C', 'D2') else 0.18); events['cuts'].append(s.t0)
# entrada da câmera lenta: impacto grave
e = env(1.6, a=0.01, k=3); x = np.arange(len(e)) / SR
place(np.sin(2 * np.pi * (55 - 15 * x) * x) * e * 0.9 + lp(rng.standard_normal(len(e)), 300) * e * 0.4, SH.BY_NAME['D1'].t0 - 0.02, 0.45)
# tempo congelado (CTA): subida reversa + drone grave
E_ = SH.BY_NAME['E']; n = int(0.7 * SR); x = np.arange(n) / n
place(bp(rng.standard_normal(n), 500, 5000) * x ** 3, E_.t0 - 0.7, 0.25)
d = int((E_.t1 - E_.t0) * SR); x = np.arange(d) / SR
drone = (np.sin(2 * np.pi * 41 * x) + 0.5 * np.sin(2 * np.pi * 61.5 * x) + 0.25 * np.sin(2 * np.pi * 82 * x)) * np.minimum(x / 0.3, 1) * np.minimum((d / SR - x) / 0.4, 1)
place(drone * (0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * x)), E_.t0, 0.10)
# tique-taque discreto durante a contagem dos 25 m (D2), acelerando com o tempo da história
for T_ in np.arange(SH.BY_NAME['D2'].t0 + 0.1, 24.9, 0.36): place(pop_sound() * 0.5, T_, 0.08)

# ------------------------------------------------------------------ ambiente (vento, pássaros, tráfego distante)
amb = lp(np.cumsum(rng.standard_normal(N)) * 0.002, 900); amb = hp(amb, 40)
amb = amb / (np.abs(amb).max() + 1e-9) * 0.05 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t))
birds = np.zeros(N)
for bt in np.sort(rng.uniform(0, T_END, 26)):
    for j in range(rng.integers(2, 5)):
        dd = rng.uniform(0.05, 0.09); x = np.arange(int(dd * SR)) / SR; f0 = rng.uniform(3000, 4800)
        i = int((bt + j * 0.12) * SR)
        if i + len(x) < N: birds[i:i + len(x)] += np.sin(2 * np.pi * (f0 * x + rng.uniform(-1, 1) * 9000 * x * x)) * np.hanning(len(x)) * 0.02
sim = up(np.array([1.0 if n in ('F', 'G') else 0.0 for n in shot_name]))
ambience = (amb + birds) * (1 - 0.6 * sim) * (1 - 0.8 * freeze) * (0.5 + 0.5 * np.clip(K, 0, 1))
add_st(ambience, 1.0, 0.0)

# ------------------------------------------------------------------ música (discreta, original): pad + pulso
mus = np.zeros(N)
BPM = 96; beat = 60 / BPM
CH = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]      # Lá m – Fá – Dó – Sol
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
bar = 4 * beat; nb = int(T_END / bar) + 1
for b in range(nb):
    t0 = b * bar; chord = CH[b % 4]
    if E_.t0 - 0.2 < t0 < E_.t1: continue
    d = int(bar * SR); x = np.arange(d) / SR
    padv = sum(np.sin(2 * np.pi * mtof(m - 12) * x + j) * 0.5 + np.sin(2 * np.pi * mtof(m) * x * 1.003) * 0.25 for j, m in enumerate(chord))
    padv *= np.minimum(x / 0.4, 1) * np.minimum((bar - x) / 0.4, 1)
    i = int(t0 * SR); j = min(N, i + d); mus[i:j] += lp(padv, 1800)[:j - i] * 0.05
    for q in range(8):                       # arpejo suave em colcheias
        m = chord[q % 3] + (12 if q % 4 == 3 else 0); dd = int(0.35 * SR); xx = np.arange(dd) / SR
        nt = (np.sin(2 * np.pi * mtof(m) * xx) + 0.3 * np.sin(4 * np.pi * mtof(m) * xx)) * np.exp(-9 * xx) * np.minimum(xx / 0.004, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += nt[:b_ - a_] * 0.035
mus *= (1 - freeze) * (0.55 + 0.45 * (1 - np.clip(1 - K, 0, 1)))
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.2, 1)

# ------------------------------------------------------------------ saída
fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.3, 1)
st = np.stack([sfx_L, sfx_R], 1) * fade[:, None]
pk = np.abs(st).max(); st = st / pk * 0.7
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
wavfile.write(os.path.join(HERE, 'out', 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(HERE, 'out', 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(HERE, 'out', 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | passos', len(events['steps']), '| freadas', events['brake'], '| paradas', events['stops'], '| pops', len(events['pops']))
