#!/usr/bin/env python3
"""Design sonoro do vídeo 10 (Brasil com menos impostos), sintetizado e dirigido pelo plano (v2/ep10/plan.py).
Saída: v2/ep10/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
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


# ------------------------------------------------------------------ ambiente: palco (sala grande e escura) o vídeo inteiro
room = lp(noise(), 180) * 0.08; bed(room, room[::-1], 0.0)
def clink(k=0):
    f0 = 2800 + 900 * ((k * 7) % 5) / 5; return mix(tone(f0, 0.18, 22) * 0.5, tone(f0 * 1.52, 0.12, 30) * 0.3, hp(noise(int(0.02 * SR)), 5000) * env(0.02, 0.0005, 5) * 0.4)
def swish(d=0.25, f0=800, f1=4000):
    n = int(d * SR); x = np.arange(n) / n; out = np.zeros(n); z = noise(n)
    for a in range(0, n, 1200):
        b = min(n, a + 1200); fc = f0 + (f1 - f0) * x[a]; out[a:b] = bp(z[max(0, a - 600):b], fc * 0.6, min(fc * 1.5, 20000))[-(b - a):]
    return out * np.sin(np.pi * x) ** 1.5
def tear(d=0.35):
    n = int(d * SR); return hp(noise(n), 1800) * (rng.random(n) > 0.55) * np.exp(-np.arange(n) / SR / 0.12)
def snip():
    return mix(hp(noise(int(0.05 * SR)), 3000) * env(0.05, 0.0005, 7) * 0.8, tone(3400, 0.06, 40) * 0.4, tone(5200, 0.04, 50) * 0.2)
def tick(): return tone(1800, 0.03, 60) * 0.6
def rewind(d=0.7):
    n = int(d * SR); x = np.arange(n) / n; f = np.geomspace(300, 2400, n)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bp(noise(n), 1500, 6000) * 0.3) * np.sin(np.pi * x)
def creak(d=0.5):
    n = int(d * SR); x = np.arange(n) / SR; f = 180 + 60 * np.sin(2 * np.pi * 3 * x)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * bp(noise(n), 300, 1800) * 0.5 * np.sin(np.pi * x / d)
B_ = P.BY_NAME
def popk(at, g=0.14): place(pop_sound(), at, g, wet=False); events['pops'].append(round(at, 3))
def hitk(at, g=0.3, boom=60): place(hit(boom), at, g); events['impacts'].append(round(at, 3))
# A1: moedas entrando no cofre, folhas arrancadas, números batendo
s = B_['A1']; mode, ta, tb = s.coins
for i in range(22):
    ts_ = ta + (tb - 0.6 - ta) * i / 21; place(swish(0.3, 1200, 3500) * 0.3, ts_, 0.05, -0.3); place(clink(i), ts_ + 0.55, 0.16, 0.3)
for tp in s.pages: place(tear(), tp, 0.22, rng.uniform(-0.3, 0.3)); place(swish(0.3, 600, 2500), tp + 0.05, 0.1)
hitk(1.62, 0.35); hitk(2.12, 0.25, 70)
for k in range(30): place(tick(), 2.75 + k * (4.2 - 2.75) / 30, 0.06)
# A2: moedas voltando (de trás pra frente) e barra do imposto descendo
s = B_['A2']
place(rewind(0.6), s.coins[1] - 0.1, 0.18)
for i in range(22): place(clink(i), s.coins[1] + (s.coins[2] - 0.6 - s.coins[1]) * i / 21, 0.1, -0.2)
n_ = int(0.8 * SR); place(np.sin(2 * np.pi * np.cumsum(np.linspace(900, 300, n_)) / SR) * env(0.8, 0.01, 2) * 0.5, 5.44, 0.14); popk(5.0)
# A3: zoom seco e cadeado tremendo
s = B_['A3']; place(riser(0.3, 300, 2400), 7.12, 0.16); hitk(7.42, 0.25, 55)
for k in range(6): place(mix(tone(900 + 150 * k, 0.05, 40), hp(noise(int(0.03 * SR)), 3000) * env(0.03, 0.0005, 5) * 0.5), s.shake + 0.045 * k, 0.14)
place(mix(tone(1200, 0.08, 30), tone(600, 0.15, 15)), s.shake + 0.08, 0.25)
# B1: fatia saindo, colunas subindo
s = B_['B1']; place(swish(0.3, 500, 3000), s.slice - 0.05, 0.18); hitk(11.46, 0.35)
popk(11.9); popk(12.5)
for tb_ in s.bars: place(riser(0.45, 150, 900), tb_, 0.16); hitk(tb_ + 0.45, 0.2, 75)
popk(14.0)
# B2: contador, etiqueta rasgando
for k in range(22): place(tick(), 16.6 + k * 0.7 / 22, 0.07)
hitk(16.6, 0.3); popk(17.0); place(tear(0.4), B_['B2'].split, 0.3); popk(18.1); popk(18.3)
# C1/C2: 2022, tesoura, preço rolando
hitk(20.8, 0.35); popk(23.66)
for sn in B_['C1'].snips: place(snip(), sn, 0.35)
place(swish(0.25), 23.95, 0.15)
for k in range(30): place(tick(), 26.0 + k / 30, 0.05)
place(mix(tone(1568, 0.4, 7), np.concatenate([np.zeros(int(0.08 * SR)), tone(2093, 0.5, 6)])), 26.76, 0.22); popk(24.6)
# D1: moedas escorrendo pelo rombo, contador negativo
s = B_['D1']
for i in range(60): place(clink(i), s.drain + i * 0.07 + 0.45, 0.07 + 0.05 * (i % 3 == 0), rng.uniform(0.0, 0.6))
popk(31.2); n_ = int(1.0 * SR); place(np.sin(2 * np.pi * np.cumsum(np.geomspace(800, 120, n_)) / SR) * env(1.0, 0.01, 1.5) * 0.5, 32.5, 0.16); hitk(33.5, 0.4, 45)
# E1/E2: Kansas
popk(34.94); hitk(35.5, 0.3); place(snip(), 35.6, 0.35); place(riser(0.4, 200, 1200), 37.3, 0.14); popk(37.4)
s = B_['E2']; popk(38.76)
for i in range(6): place(thud(), s.drop + 0.07 * i + 0.25, 0.18)
place(tape_stop(0.6), s.droop, 0.3); place(rewind(0.7), s.rewind - 0.05, 0.25); popk(42.5)
# F1/F2/G1: balança
popk(45.44); popk(45.5); popk(47.35); popk(47.45); hitk(47.5, 0.25, 70)
popk(48.78); popk(49.56); place(creak(0.6), 52.0, 0.25); hitk(52.2, 0.4, 45); popk(52.1)
popk(54.8, 0.18); place(swish(0.2, 2000, 6000), 55.6, 0.2); hitk(56.08, 0.45, 50)
# G2/H1: final em loop
s = B_['G2']; popk(s.cal_on)
for i in range(16): place(clink(i), s.burst + 0.03 * i, 0.1, 0.4)
place(swish(0.4, 600, 4000), s.burst, 0.15)
for k in range(5): popk(62.0 + 0.22 * k, 0.12)
place(snip(), 63.36, 0.4)
# transições e push-ins
for nm in ('B1', 'C1', 'E1', 'F1', 'G2'): place(swish(0.25, 700, 5000), B_[nm].t0 - 0.06, 0.2); events['cuts'].append(B_[nm].t0)
for s in P.SHOTS[1:]: place(passby(0.4), s.t0 - 0.18, 0.1, rng.uniform(-0.4, 0.4))
for s in P.SHOTS:
    for tp in getattr(s, 'push', ()): place(riser(0.2, 400, 1600) * 0.5, tp - 0.05, 0.07)
# ------------------------------------------------------------------ reverberação leve
ir_n = int(1.2 * SR); xi = np.arange(ir_n) / SR
def ir(seed, dec):
    r_ = np.random.default_rng(seed); h = r_.standard_normal(ir_n) * np.exp(-xi / dec); h[:int(0.015 * SR)] *= np.linspace(0, 1, int(0.015 * SR))
    return lp(h, 5000) / np.sqrt(np.sum(h ** 2))
L += fftconvolve(FX_L, ir(1, 0.18))[:N] * 0.18; R += fftconvolve(FX_R, ir(2, 0.18))[:N] * 0.18


# ------------------------------------------------------------------ música própria: Dó menor, 110 BPM, pulso de "contagem" (sintetizador), some na pergunta "de quem?"
mus = np.zeros(N); BPM = 110; beat = 60 / BPM; bar = 4 * beat
CH = [(48, 51, 55), (44, 48, 51), (46, 50, 53), (43, 47, 50)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(P.END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]
    for q in range(8):
        dd = int(beat / 2 * SR); x2 = np.arange(dd) / SR; f = mtof(chord[0] - 12)
        bs = (2 * ((f * x2) % 1) - 1) * np.exp(-7 * x2) * np.minimum(x2 / 0.003, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += lp(bs, 600)[:b_ - a_] * 0.06
    for q in range(4):
        a_ = int((t0 + q * beat) * SR); dd = int(0.3 * SR); x2 = np.arange(dd) / SR
        k_ = np.sin(2 * np.pi * (48 * x2 + 90 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-9 * x2) if q % 2 == 0 else bp(rng.standard_normal(dd), 1800, 7000) * np.exp(-20 * x2) * 0.45
        b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += k_[:b_ - a_] * 0.07
        for h in (0.25, 0.75):
            a2 = int((t0 + q * beat + beat * h) * SR); hh = hp(rng.standard_normal(int(0.03 * SR)), 8000) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.008)
            if a2 < N: mus[a2:min(N, a2 + len(hh))] += hh[:min(N, a2 + len(hh)) - a2] * 0.025
    for q in range(16):
        m = chord[(q * 2) % 3] + 24; dd = int(0.16 * SR); x2 = np.arange(dd) / SR
        pl = (np.sin(2 * np.pi * mtof(m) * x2) + 0.4 * np.sin(4 * np.pi * mtof(m) * x2)) * np.exp(-16 * x2) * np.minimum(x2 / 0.002, 1)
        a_ = int((t0 + q * beat / 4) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += pl[:b_ - a_] * 0.014
duck = 1 - 0.75 * ctrl([1.0 if (53.4 <= T < 56.1) else 0.0 for T in tc], 0.3)            # "quanto? de quem?": quase silêncio
lift = 1 + 0.2 * ctrl([1.0 if 43.7 <= T < 53.4 else 0.0 for T in tc], 0.5)
mus *= duck * lift * np.minimum(t / 0.4, 1) * np.minimum((P.END - t) / 1.0, 1)

fade = np.minimum(t / 0.01, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.8
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', len(events['impacts']), '| pops', len(events['pops']), '| cortes', len(events['cuts']))
