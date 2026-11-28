#!/usr/bin/env python3
"""Design sonoro do vídeo 09 (vida real com as regras do GTA), sintetizado e dirigido pelo plano (v2/ep09/plan.py).
Saída: v2/ep09/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(99)
def sos(kind, f, o=2): return butter(o, f, kind, fs=SR, output='sos')
def bp(x, lo, hi, o=2): return sosfilt(sos('bandpass', [lo, hi], o), x)
def lp(x, f, o=2): return sosfilt(sos('lowpass', f, o), x)
def hp(x, f, o=2): return sosfilt(sos('highpass', f, o), x)
def noise(n=N): return rng.standard_normal(n)
def brown(n=N):
    x = np.cumsum(rng.standard_normal(n)); x -= lp(x, 8); return x / (np.abs(x).max() + 1e-9)
def env(d, a=0.003, k=6.0):
    x = np.arange(int(d * SR)) / SR; return np.minimum(x / max(a, 1e-4), 1) * np.exp(-k * x / d)
def tone(f, d, k=4.0, a=0.004):
    x = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * x) * np.exp(-k * x) * np.minimum(x / a, 1)

def mix(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
L = np.zeros(N); R = np.zeros(N); FX_L = np.zeros(N); FX_R = np.zeros(N)
events = dict(pops=[], cuts=[], impacts=[])
def place(sig, at, gain=1.0, pan=0.0, wet=True, delay_ms=0.0):
    """Soma um som curto em 'at' (s). pan −1..1; atraso inter-aural opcional para largura."""
    i = int(at * SR); n = len(sig)
    if i >= N or i + n <= 0: return
    a = max(i, 0); b = min(N, i + n); s = sig[a - i:b - i] * gain
    gl, gr = math.sqrt((1 - pan) / 2) * 1.41, math.sqrt((1 + pan) / 2) * 1.41
    d = int(delay_ms * SR / 1000)
    L[a:b] += s * gl; R[min(N, a + d):min(N, b + d)] += (s * gr)[:max(0, min(N, b + d) - min(N, a + d))]
    if wet: FX_L[a:b] += s * gl; FX_R[a:b] += s * gr
def bed(sl, sr_, wet=0.0):
    global L, R
    L += sl; R += sr_
    if wet: FX_L[:] += sl * wet; FX_R[:] += sr_ * wet

# ------------------------------------------------------------------ máscaras por plano (calculadas a 1 kHz e interpoladas)
CR = 1000; tc = np.arange(int(T_END * CR) + 1) / CR
def shot_at(T):
    for s in P.SHOTS:
        if s.t0 <= T < s.t1: return s
    return P.SHOTS[-1]
SH = [shot_at(min(T, T_END - 1e-4)) for T in tc]
def ctrl(vals, s=0.08):
    v = np.asarray(vals, float); k = max(1, int(s * CR)); w = np.hanning(2 * k + 1); w /= w.sum()
    return np.interp(t, tc, np.convolve(np.pad(v, k, mode='edge'), w, 'valid'))
def kmask(*ks, s=0.06): return ctrl([1.0 if x.kind in ks else 0.0 for x in SH], s)
walk = np.cumsum(rng.standard_normal(len(tc))) * 0.02; walk = walk - np.convolve(walk, np.ones(4000) / 4000, 'same')
gust_c = np.clip(0.65 + walk * 2.2 + 0.25 * np.sin(2 * np.pi * 0.19 * tc), 0.25, 1.4)
GUST = np.interp(t, tc, gust_c)
def resonant_howl(fc_ctrl, q=18.0, seed=0):
    """Ruído passado por um banco de passa-faixas estreitos cujo centro acompanha fc_ctrl (curva a 1 kHz)."""
    out = np.zeros(N); x = noise(); blk = 4800
    for a in range(0, N, blk):
        b = min(N, a + blk); fc = float(np.interp(a / SR, tc, fc_ctrl)); bw = fc / q
        seg = sosfilt(sos('bandpass', [max(fc - bw, 30), fc + bw]), x[max(0, a - 2400):b])[-(b - a):]
        out[a:b] = seg
    return out / (np.abs(out).max() + 1e-9)
def passby(d=0.5):
    n = int(d * SR); x = np.arange(n) / n; f = 500 + 2500 * np.exp(-((x - 0.5) / 0.18) ** 2); out = np.zeros(n); z = noise(n)
    for a in range(0, n, 1200):
        b = min(n, a + 1200); out[a:b] = bp(z[max(0, a - 600):b], f[a] * 0.6, min(f[a] * 1.5, 20000))[-(b - a):]
    return out * np.sin(np.pi * x) ** 2
def riser(d, f0, f1):
    n = int(d * SR); x = np.arange(n) / SR; f = np.geomspace(f0, f1, n)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + bp(noise(n), 1000, 6000) * 0.3) * (x / d) ** 1.5
def hit(boom=60):
    return mix(tone(boom, 0.9, 5) * 1.0, lp(noise(int(0.4 * SR)), 900) * env(0.4, 0.001, 8) * 0.6, tone(2400, 0.05, 30) * 0.3)
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); x = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * x / 0.09) * x) * 0.5 + np.sin(2 * np.pi * 3000 * x) * 0.15) * e_

# ------------------------------------------------------------------ ambiente: rua de dia (trânsito ao longe, vento, pássaros), estúdio (sala), trailer (só nossa trilha)
street = kmask('rua'); studio = kmask('estudio')
traffic = lp(brown(), 300) * 0.5 + bp(noise(), 200, 900) * 0.06
bed(traffic * 0.3 * street, traffic[::-1] * 0.3 * street, 0.05)
for k in range(int(P.END * 0.5)):
    at = rng.uniform(0, P.END)
    if np.interp(at, t[::480], street[::480]) < 0.5: continue
    f0 = rng.uniform(2600, 4600); n = int(rng.uniform(0.06, 0.12) * SR); x = np.arange(n) / SR
    ch = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.2 * np.sin(2 * np.pi * 35 * x))) / SR) * np.sin(np.pi * x / x[-1]) ** 2
    place(ch, at, 0.025, rng.uniform(-0.8, 0.8))
room = lp(noise(), 180) * 0.08; bed(room * studio, room[::-1] * studio)

def chime(fs=(784, 988, 1175, 1568), step=0.07, g=0.5):
    return mix(*[np.concatenate([np.zeros(int(i * step * SR)), tone(f, 0.45, 7) * g]) for i, f in enumerate(fs)])
def buzzer(d=0.35):
    x = np.arange(int(d * SR)) / SR; return np.sign(np.sin(2 * np.pi * 110 * x)) * 0.4 * np.minimum((d - x) / 0.05, 1) * np.minimum(x / 0.01, 1)
def tape_stop(d=0.6):
    n = int(d * SR); x = np.arange(n) / n; f = 600 * (1 - x) ** 2 + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - x) * 0.6 + lp(noise(n), 800) * (1 - x) * 0.3
def thud(): return mix(tone(55, 0.5, 7), lp(noise(int(0.25 * SR)), 500) * env(0.25, 0.001, 7) * 0.8)
def engine(d, f0, f1):
    n = int(d * SR); f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sign(np.sin(ph)) * 0.3 + np.sin(2 * ph) * 0.3) * np.minimum(np.arange(n) / (0.3 * SR), 1)
def crash():
    n = int(0.9 * SR); x = np.arange(n) / SR
    return mix(tone(48, 0.9, 5), bp(noise(n), 800, 7000) * np.exp(-x / 0.18) * 0.7, hp(noise(n), 4000) * (rng.random(n) > 0.85) * np.exp(-x / 0.3) * 0.4)

# ------------------------------------------------------------------ eventos dirigidos pelo plano
A1 = P.BY_NAME['A1']
place(thud(), A1.t0 + 0.02, 0.5); events['impacts'].append(A1.t0)
place(chime(), A1.t_up, 0.3); events['pops'].append(A1.t_up)
for k in range(int((A1.t_real - A1.t_walk) * 2.2)): place(lp(noise(int(0.05 * SR)), 1500) * env(0.05, 0.001, 6), A1.t_walk + k / 2.2, 0.12)
place(tape_stop(), A1.t_real - 0.05, 0.45); place(thud(), A1.t_real + 0.2, 0.35); place(buzzer(0.3), A1.t_real + 0.12, 0.18); events['impacts'].append(A1.t_real)
B1 = P.BY_NAME['B1']; place(chime((523, 659, 784)), B1.hud[0] + 0.05, 0.22)
for nm in ('C1', 'C2'):
    s = P.BY_NAME[nm]; tg, th, kmh = s.drive
    place(engine(th - s.t0, 70, 140 if kmh < 50 else 210) * np.linspace(0.3, 1, int((th - s.t0) * SR)), s.t0, 0.12)
    place(riser(min(0.8, th - s.t0), 300, 1400), th - 0.8, 0.15)
    place(crash(), th, 0.55); events['impacts'].append(th)
    tr_ = s.panel[4]
    for i in range(s.panel[5]): place(pop_sound(), tr_ + 0.06 * i, 0.12)
    place(hit(60), tr_ + 0.06 * s.panel[5], 0.3)
D1 = P.BY_NAME['D1']
n = int((D1.t1 - D1.t0) * SR); x = np.arange(n) / SR
place(bp(noise(n), 300, 2500) * (0.4 + 0.6 * np.sin(np.pi * x / x[-1])), D1.t0, 0.12)                # vento no alto do prédio
place(hit(55), D1.panel[3], 0.35)
D2 = P.BY_NAME['D2']
for k in range(int((D2.t_eat + 1.0 - D2.t_eat) * 3)):
    m_ = int(0.09 * SR); place(mix(bp(noise(m_), 500, 3000) * np.exp(-np.arange(m_) / SR / 0.03), lp(noise(m_), 250) * 0.6), D2.t_eat + k / 3, 0.15)
place(buzzer(0.35), D2.t_eat + 0.8, 0.25); events['impacts'].append(D2.t_eat + 0.8)
D3 = P.BY_NAME['D3']; t1_, t2_ = D3.panel[3]
for i in range(8):
    tt = (t1_ - 1.6 + 0.2 * i) if i < 6 else (t2_ - 0.3 + 0.25 * (i - 6)); place(tone(1200 + 60 * i, 0.08, 25), tt, 0.12)
place(hit(70), t2_, 0.25)
E1 = P.BY_NAME['E1']
for tt in E1.panel[3]: place(pop_sound(), tt, 0.15)
place(riser(E1.t_light - 37.5, 120, 600), 37.5, 0.18)
place(mix(tone(90, 0.6, 6), hp(noise(int(0.08 * SR)), 1500) * env(0.08, 0.001, 5) * 0.6), E1.t_light, 0.6); events['impacts'].append(E1.t_light)   # holofote: "clunk"
E2 = P.BY_NAME['E2']; place(hit(50), E2.t0 + 0.05, 0.3)
for s_ in E2.labels: place(mix(pop_sound(), np.sin(2 * np.pi * 300 * np.arange(int(0.12 * SR)) / SR) * env(0.12, 0.001, 6) * 0.3), s_[4], 0.18)
place(chime((659, 784)), E2.compare, 0.2)
# trailer: só a nossa trilha e um "whoosh" de entrada (o áudio do trailer não entra)
for s in P.SHOTS:
    if s.kind == 'trailer': place(riser(0.35, 500, 2600) * 0.6, s.t0 - 0.3, 0.15); place(hit(65), s.t0, 0.25); events['cuts'].append(s.t0)
TR4 = P.BY_NAME['TR4']; m_ = int(0.8 * SR); xx = np.arange(m_) / SR
place(mix(hp(noise(m_), 3000) * np.exp(-xx / 0.2) * (rng.random(m_) > 0.7), tone(2600, 0.3, 12) * 0.3), TR4.t0 + 0.75, 0.3)   # vidro (nosso som)
F1 = P.BY_NAME['F1']; t_on, t_br = F1.button
place(mix(tone(880, 0.15, 12), tone(1320, 0.15, 12) * 0.5), t_on + 0.05, 0.2)
m_ = int(0.7 * SR); xx = np.arange(m_) / SR
place(mix(hp(noise(m_), 2500) * np.exp(-xx / 0.15), tone(180, 0.4, 8) * 0.6), t_br, 0.4); events['impacts'].append(t_br)
place(np.sin(2 * np.pi * np.cumsum(np.geomspace(700, 90, int(0.7 * SR))) / SR) * env(0.7, 0.01, 3), t_br + 0.2, 0.2)
H1 = P.BY_NAME['H1']
place(mix(tone(1480, 0.5, 7) * 0.7, np.concatenate([np.zeros(int(0.09 * SR)), tone(2220, 0.6, 6) * 0.6])), H1.panel[1], 0.3)
for k in range(9): place(mix(hp(noise(int(0.02 * SR)), 2000) * env(0.02, 0.0005, 6), tone(rng.uniform(140, 220), 0.04, 30) * 0.3), H1.t0 + 0.3 + k * rng.uniform(0.09, 0.14), 0.16, rng.uniform(-0.2, 0.2))
place(hit(60), H1.panel[3], 0.35)

# ------------------------------------------------------------------ rótulos e cortes
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90 and s.name != 'E2'})
for p_ in pops: place(pop_sound(), p_, 0.16, wet=False); events['pops'].append(p_)
for s in P.SHOTS[1:]:
    if s.kind != 'trailer': place(passby(0.45), s.t0 - 0.2, 0.14, rng.uniform(-0.4, 0.4)); events['cuts'].append(s.t0)
for s in P.SHOTS:
    for tp in getattr(s, 'push', ()): place(riser(0.2, 400, 1600) * 0.5, tp - 0.05, 0.08)

# ------------------------------------------------------------------ reverberação leve
ir_n = int(1.2 * SR); xi = np.arange(ir_n) / SR
def ir(seed, dec):
    r_ = np.random.default_rng(seed); h = r_.standard_normal(ir_n) * np.exp(-xi / dec); h[:int(0.015 * SR)] *= np.linspace(0, 1, int(0.015 * SR))
    return lp(h, 5000) / np.sqrt(np.sum(h ** 2))
L += fftconvolve(FX_L, ir(1, 0.18))[:N] * 0.18; R += fftconvolve(FX_R, ir(2, 0.18))[:N] * 0.18

# ------------------------------------------------------------------ música própria: Mi menor, 100 BPM, baixo sintetizado + batida + arpejo (tom de "jogo"), cai na virada
mus = np.zeros(N); BPM = 100; beat = 60 / BPM; bar = 4 * beat
CH = [(52, 55, 59), (48, 52, 55), (50, 54, 57), (47, 50, 54)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(P.END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]
    for q in range(8):                                   # baixo em colcheias
        dd = int(beat / 2 * SR); x2 = np.arange(dd) / SR; f = mtof(chord[0] - 12)
        bs = (2 * ((f * x2) % 1) - 1) * np.exp(-6 * x2) * np.minimum(x2 / 0.003, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += lp(bs, 700)[:b_ - a_] * 0.06
    for q in range(4):                                   # bumbo e caixa
        a_ = int((t0 + q * beat) * SR); dd = int(0.3 * SR); x2 = np.arange(dd) / SR
        k_ = np.sin(2 * np.pi * (50 * x2 + 80 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-9 * x2) if q % 2 == 0 else bp(rng.standard_normal(dd), 1500, 6000) * np.exp(-18 * x2) * 0.5
        b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += k_[:b_ - a_] * 0.07
        a2 = int((t0 + q * beat + beat / 2) * SR); hh = hp(rng.standard_normal(int(0.04 * SR)), 7000) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.01)
        if a2 < N: mus[a2:min(N, a2 + len(hh))] += hh[:min(N, a2 + len(hh)) - a2] * 0.03
    for q in range(16):                                  # arpejo
        if (q + b) % 4 == 3: continue
        m = chord[q % 3] + 24; dd = int(0.2 * SR); x2 = np.arange(dd) / SR
        ar = np.sign(np.sin(2 * np.pi * mtof(m) * x2)) * np.exp(-14 * x2) * np.minimum(x2 / 0.002, 1)
        a_ = int((t0 + q * beat / 4) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += lp(ar, 3000)[:b_ - a_] * 0.012
duck = 1 - 0.6 * ctrl([1.0 if (36.4 <= T < 43.3) else 0.0 for T in tc], 0.4)          # virada: quase só o holofote
lift = 1 + 0.25 * ctrl([1.0 if 43.3 <= T < 51.8 else 0.0 for T in tc], 0.5)
duck2 = 1 - 0.5 * ctrl([1.0 if (56.1 <= T < 58.9) else 0.0 for T in tc], 0.2)          # botão quebra: silêncio
mus *= duck * lift * duck2 * np.minimum(t / 0.5, 1) * np.minimum((P.END - t) / 1.0, 1)

fade = np.minimum(t / 0.01, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.8
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', len(events['impacts']), '| pops', len(events['pops']), '| cortes', len(events['cuts']))
