#!/usr/bin/env python3
"""Design sonoro do vídeo 08 (fogo nunca descoberto), sintetizado e dirigido pelo plano (v2/ep08/plan.py).
Saída: v2/ep08/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(88)
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

# ------------------------------------------------------------------ ambiente: savana de dia (vento leve, pássaros, insetos), noite (grilos), estúdio, espaço
day = kmask('dia'); night = kmask('noite'); studio = kmask('estudio'); glob = kmask('globo')
wl_ = lp(brown(), 700) * 0.6 + bp(noise(), 300, 1200) * 0.08; wr_ = lp(brown(), 700) * 0.6 + bp(noise(), 300, 1200) * 0.08
GUST = np.interp(t, tc, np.clip(0.6 + 0.3 * np.sin(2 * np.pi * 0.11 * tc) + 0.15 * np.sin(2 * np.pi * 0.37 * tc + 1), 0.2, 1.1))
bed(wl_ * GUST * (0.35 * day + 0.25 * night), wr_ * GUST * (0.35 * day + 0.25 * night), 0.1)
grass = bp(noise(), 3000, 9000) * GUST ** 2; bed(grass * 0.03 * day, grass[::-1] * 0.03 * day)
# pássaros: chilreios curtos e distantes
for k in range(int(P.END * 0.9)):
    at = rng.uniform(0, P.END)
    if np.interp(at, t[::480], day[::480]) < 0.5: continue
    f0 = rng.uniform(2600, 4800); n = int(rng.uniform(0.06, 0.14) * SR); x = np.arange(n) / SR
    ch = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.25 * np.sin(2 * np.pi * rng.uniform(25, 45) * x))) / SR) * np.sin(np.pi * x / x[-1]) ** 2
    for r_ in range(int(rng.integers(1, 4))): place(ch, at + r_ * rng.uniform(0.12, 0.2), 0.035, rng.uniform(-0.8, 0.8))
# cigarra de dia (zumbido modulado) e grilos à noite (pulsos a ~4,5 Hz)
cic = bp(noise(), 4200, 6200) * (0.5 + 0.5 * np.sin(2 * np.pi * 47 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
bed(cic * 0.012 * day, cic[::-1] * 0.012 * day)
cr = np.zeros(N); cr2 = np.zeros(N)
for f_, rate, ph, arr in ((4300, 4.4, 0.0, cr), (4650, 3.9, 0.3, cr2), (3950, 5.1, 0.7, cr)):
    gate = (np.sin(2 * np.pi * rate * t + ph) > 0.55).astype(float) * (np.sin(2 * np.pi * 0.23 * t + ph) > -0.3)
    arr += np.sin(2 * np.pi * f_ * t) * lp(gate, 200) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t))
bed(cr * 0.02 * night, cr2 * 0.02 * night, 0.1)
room = lp(noise(), 180) * 0.08; bed(room * studio, room[::-1] * studio)
space = lp(brown(), 80) * 0.4 + bp(noise(), 120, 600) * 0.05; bed(space * glob * 0.35, space[::-1] * glob * 0.35, 0.2)

# ------------------------------------------------------------------ fogueira: estalos + chiado + ronco grave (quando acesa)
FIRE = np.zeros(len(tc))
for i, T in enumerate(tc):
    s = SH[i]
    if s.kind == 'estudio' and (getattr(s, 'food', False) or hasattr(s, 'food_feed')): FIRE[i] = 0.45
    elif s.kind == 'noite' and (getattr(s, 'group', False) or getattr(s, 'fire', None) is not None):
        fw = getattr(s, 'fire', (s.t0 - 1, 99)); FIRE[i] = 1.0 if fw[0] <= T < fw[1] else 0.0
FIRE_A = ctrl(FIRE, 0.05)
roar = lp(brown(), 220) * 0.6 + bp(noise(), 200, 900) * 0.15 * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3.1 * t)))
bed(roar * FIRE_A * 0.35, roar[::-1] * FIRE_A * 0.35, 0.1)
fc_ = np.interp(np.arange(0, P.END, 1 / 1000), tc, FIRE)
for k in range(int(P.END * 14)):
    at = rng.uniform(0, P.END); lvl = float(np.interp(at, tc, FIRE))
    if rng.random() > lvl: continue
    n = int(rng.uniform(0.004, 0.02) * SR); c = hp(noise(n), rng.uniform(1500, 4000)) * np.exp(-np.arange(n) / (n / 4))
    if rng.random() < 0.15: c = mix(c, tone(rng.uniform(600, 1400), 0.05, 40) * 0.5)
    place(c, at, rng.uniform(0.08, 0.3), rng.uniform(-0.5, 0.5))
# fogo apagando em "descoberto": chiado que cai + sopro grave
B2 = P.BY_NAME['B2']; te = B2.fire[1]; n = int(1.2 * SR); x = np.arange(n) / SR
hiss = bp(noise(n), 2500, 9000) * np.exp(-x / 0.35) * np.minimum(x / 0.01, 1)
place(hiss, te, 0.5, wet=True); place(lp(noise(int(0.5 * SR)), 250) * env(0.5, 0.003, 5), te, 0.5); events['impacts'].append(te)
# fogo acendendo em D2: "fwoosh"
D2 = P.BY_NAME['D2']; n = int(0.9 * SR); x = np.arange(n) / SR
fw_ = lp(noise(n), 1200) * np.sin(np.pi * np.minimum(x / 0.9, 1)) ** 1.5 * np.minimum(x / 0.25, 1); place(fw_, D2.fire[0] - 0.15, 0.6); events['impacts'].append(D2.fire[0])

# ------------------------------------------------------------------ mastigação (cru, duro): mordidas crocantes no ritmo da animação
def chomp():
    n = int(rng.uniform(0.07, 0.12) * SR); x = np.arange(n) / SR
    crunch = bp(noise(n), 900, 5000) * (0.4 + 0.6 * (rng.random(n) > 0.6)) * np.exp(-x / 0.04)
    return mix(crunch, lp(noise(n), 300) * np.exp(-x / 0.03) * 0.8)
for s in P.SHOTS:
    if getattr(s, 'teo', None) != 'chew': continue
    g_ = 0.22 if s.name in ('A1', 'G2') else 0.08 if s.name == 'C3' else 0.12
    T = s.t0 + 0.05
    while T < s.t1 - 0.05:
        place(chomp(), T, g_ * rng.uniform(0.7, 1.0), rng.uniform(-0.15, 0.15)); T += 1 / 2.5 + rng.uniform(-0.02, 0.02)

# ------------------------------------------------------------------ comentário: "notificação" (dois toques) e cartão saindo
def ding(f=1320):
    return mix(tone(f, 0.5, 7) * 0.7, tone(f * 2.01, 0.3, 12) * 0.2, np.concatenate([np.zeros(int(0.09 * SR)), tone(f * 1.5, 0.6, 6) * 0.6]))
B1 = P.BY_NAME['B1']; place(ding(), B1.panel[1], 0.4, wet=True); place(pop_sound(), B1.panel[3], 0.2); events['pops'] += [B1.panel[1], B1.panel[3]]
G1 = P.BY_NAME['G1']; place(ding(990), G1.panel[1], 0.3)
for j in range(7): place(np.sin(2 * np.pi * np.cumsum(np.geomspace(1400 - 90 * j, 300, int(0.12 * SR))) / SR) * env(0.12, 0.002, 4), G1.panel[3] + 0.12 * j, 0.12)
place(lp(noise(int(1.5 * SR)), 400) * env(1.5, 0.3, 3), G1.panel[3] + 0.9, 0.25)          # vazio
# CTA: teclado digitando + cursor
H1 = P.BY_NAME['H1']; place(ding(1480), H1.panel[1], 0.3)
for k in range(9): place(mix(hp(noise(int(0.02 * SR)), 2000) * env(0.02, 0.0005, 6), tone(rng.uniform(140, 220), 0.04, 30) * 0.3), H1.t0 + 0.25 + k * rng.uniform(0.09, 0.14), 0.18, rng.uniform(-0.2, 0.2))
place(hit(60), H1.panel[3], 0.4)

# ------------------------------------------------------------------ painéis: relógio (tique-taque que acelera), barras (sobe), cérebro (pulso)
def tick(f=2200): return mix(tone(f, 0.03, 60), hp(noise(int(0.01 * SR)), 3000) * env(0.01, 0.0003, 5) * 0.4)
for nm in ('A1', 'C3', 'C4'):
    s = P.BY_NAME[nm]; t1, t2 = s.panel[3]; T = t1; k = 0
    while T < t2: place(tick(2200 if k % 2 else 1800), T, 0.16); k += 1; T += max(0.06, 0.22 - 0.03 * k)
    place(hit(62 if nm != 'C4' else 90), t2, 0.35 if nm != 'C4' else 0.25)
C2 = P.BY_NAME['C2']; a_, b_ = C2.panel[3]; place(riser(0.6, 300, 700), a_ - 0.5, 0.15); place(riser(0.6, 300, 1100), b_ - 0.5, 0.2); place(tone(880, 0.25, 9), b_ + 0.1, 0.15)
E2 = P.BY_NAME['E2']; a_, b_ = E2.panel[3]; place(riser(b_ - a_, 200, 900), a_, 0.25); place(hit(55), b_, 0.45)
n = int((E2.t1 - E2.t0) * SR); x = np.arange(n) / SR; hum_ = sum(np.sin(2 * np.pi * 60 * h * x) / h for h in (1, 2, 3, 4)) * np.minimum(x / 1.0, 1) * np.minimum((x[-1] - x) / 0.5, 1)
place(lp(hum_, 600), E2.t0, 0.05, wet=False)
F2 = P.BY_NAME['F2']
for k in range(5): place(mix(tone(55, 0.25, 12), tone(80, 0.18, 14) * 0.5), F2.t0 + 0.3 + k * 0.62, 0.35)
place(mix(tone(1046, 0.8, 4), tone(1568, 0.8, 5) * 0.5), F2.panel[3], 0.18)
F3 = P.BY_NAME['F3']; a_, b_ = F3.food_feed
for k in range(int((F3.t1 - a_) * 9)): place(tone(rng.uniform(1800, 4200), 0.12, 20), a_ + k / 9 + rng.uniform(0, 0.05), 0.05, rng.uniform(-0.5, 0.5))
place(riser(F3.brain_glow - a_, 300, 1200), a_, 0.2); place(mix(tone(523, 1.4, 2.5), tone(659, 1.4, 2.5) * 0.6, tone(784, 1.4, 2.5) * 0.5), F3.brain_glow, 0.25)
# E1: objetos (metal, cerâmica, vidro) aparecem com som próprio e somem com "sopro"
E1 = P.BY_NAME['E1']
for (ta, nm), sig in zip(E1.objs, (mix(*[tone(310 * r, 0.6, k) * g for r, k, g in ((1.0, 5, 1.0), (2.76, 8, 0.6), (5.4, 12, 0.4))]),
                                    mix(tone(420, 0.25, 18), bp(noise(int(0.08 * SR)), 400, 2000) * env(0.08, 0.001, 6) * 0.5),
                                    mix(tone(2800, 0.5, 8), tone(4200, 0.4, 10) * 0.5))):
    place(sig, ta, 0.3); events['impacts'].append(ta)
place(np.sin(2 * np.pi * np.cumsum(np.geomspace(900, 120, int(0.5 * SR))) / SR) * env(0.5, 0.005, 4), E1.objs_off, 0.25)
# Téo: susto (C1), alívio (C4), pensamento (F1)
place(hit(70), P.BY_NAME['C1'].t_pose, 0.35); place(tone(660, 0.4, 5) * 0.4, P.BY_NAME['C4'].t_pose, 0.2)
place(riser(1.2, 200, 800), P.BY_NAME['F1'].push[0] - 1.0, 0.18); place(hit(50), P.BY_NAME['F1'].push[0], 0.5)
place(hit(44), 0.0, 0.7); events['impacts'].append(0.0)

# ------------------------------------------------------------------ rótulos e chicotes de câmera (whoosh em cada corte)
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90}) + [b for s in P.SHOTS for b in getattr(s, 'bubbles', ())]
for p_ in pops: place(pop_sound(), p_, 0.16, wet=False); events['pops'].append(p_)
for s in P.SHOTS[1:]:
    place(passby(0.45), s.t0 - 0.2, 0.16, rng.uniform(-0.4, 0.4)); events['cuts'].append(s.t0)
for s in P.SHOTS:
    for tp in getattr(s, 'push', ()): place(riser(0.2, 400, 1600) * 0.5, tp - 0.05, 0.08)

# ------------------------------------------------------------------ reverberação leve (ar livre / estúdio)
ir_n = int(1.2 * SR); xi = np.arange(ir_n) / SR
def ir(seed, dec):
    r_ = np.random.default_rng(seed); h = r_.standard_normal(ir_n) * np.exp(-xi / dec); h[:int(0.015 * SR)] *= np.linspace(0, 1, int(0.015 * SR))
    return lp(h, 5000) / np.sqrt(np.sum(h ** 2))
L += fftconvolve(FX_L, ir(1, 0.18))[:N] * 0.18; R += fftconvolve(FX_R, ir(2, 0.18))[:N] * 0.18

# ------------------------------------------------------------------ música: Lá menor modal, 92 BPM, curiosa (kalimba + pad + tambor grave), sobe na virada
mus = np.zeros(N); BPM = 92; beat = 60 / BPM; bar = 4 * beat
CH = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 55, 59)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(P.END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]; d = int(bar * SR); x = np.arange(d) / SR
    padv = sum(np.sin(2 * np.pi * mtof(m - 12) * x + j) * 0.5 + np.sin(2 * np.pi * mtof(m) * x * 1.004) * 0.22 for j, m in enumerate(chord))
    padv *= np.minimum(x / 0.6, 1) * np.minimum((bar - x) / 0.6, 1)
    i = int(t0 * SR); j = min(N, i + d)
    if i < N: mus[i:j] += lp(padv, 1300)[:j - i] * 0.045
    for q in range(8):
        if (q + b) % 3 == 2: continue
        m = chord[(q * 2) % 3] + 12 + (12 if q == 5 else 0); dd = int(0.5 * SR); x2 = np.arange(dd) / SR
        kal = (np.sin(2 * np.pi * mtof(m) * x2) + 0.25 * np.sin(2 * np.pi * mtof(m) * 4.02 * x2) * np.exp(-30 * x2)) * np.exp(-7 * x2) * np.minimum(x2 / 0.002, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += kal[:b_ - a_] * 0.028
    for k in (0, 2.5):
        dd = int(0.4 * SR); x2 = np.arange(dd) / SR
        dr = np.sin(2 * np.pi * (60 * x2 + 50 * (1 - np.exp(-25 * x2)) / 25)) * np.exp(-8 * x2)
        a_ = int((t0 + k * beat) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += dr[:b_ - a_] * 0.05
lift = 1 + 0.35 * ctrl([1.0 if 44.4 <= T < 55.7 else 0.0 for T in tc], 0.5)
duck = 1 - 0.55 * ctrl([1.0 if (55.66 <= T < 60.26) else 0.0 for T in tc], 0.3)          # "nem existisse": quase silêncio
mus *= lift * duck * np.minimum(t / 0.8, 1) * np.minimum((P.END - t) / 1.2, 1)

fade = np.minimum(t / 0.01, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.8
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', len(events['impacts']), '| pops', len(events['pops']), '| cortes', len(events['cuts']))
