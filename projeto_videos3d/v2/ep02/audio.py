#!/usr/bin/env python3
"""Design sonoro do vídeo 02, 100% sintetizado e dirigido pelos mesmos dados da animação (v2/ep02/plan.py):
espaço (drone, estrelas correndo, travada do giro), orla (ondas, gaivotas, brisa -> vendaval proporcional ao vento,
mar que avança), tranco do chão, ônibus (motor pela velocidade, freada, ar comprimido), sons de interface quando os
rótulos aparecem, transições nos cortes e música discreta. A voz NÃO é tocada aqui.
Saída: v2/ep02/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(22)
def sos(kind, f, o=2): return butter(o, f, kind, fs=SR, output='sos')
def bp(x, lo, hi): return sosfilt(sos('bandpass', [lo, hi]), x)
def lp(x, f): return sosfilt(sos('lowpass', f), x)
def hp(x, f): return sosfilt(sos('highpass', f), x)
def env(d, a=0.003, k=6.0):
    x = np.arange(int(d * SR)) / SR; return np.minimum(x / a, 1) * np.exp(-k * x / d)
def noise(n=N): return rng.standard_normal(n)

L = np.zeros(N); R = np.zeros(N); events = dict(pops=[], cuts=[], impacts=[], brake=None)
def add_st(sig, gain=1.0, pan=0.0):
    global L, R
    L += sig * gain * np.sqrt((1 - pan) / 2) * 1.41; R += sig * gain * np.sqrt((1 + pan) / 2) * 1.41
def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    a = max(i, 0); b = min(N, i + len(sig)); seg = np.zeros(N); seg[a:b] = sig[a - i:b - i]; add_st(seg, gain, pan)

# ------------------------------------------------------------------ controle por instante (1 kHz)
CR = 1000; tc = np.arange(int(T_END * CR) + 1) / CR
def shot_at(T):
    for s in P.SHOTS:
        if s.t0 <= T < s.t1: return s
    return P.SHOTS[-1]
names = [shot_at(min(T, T_END - 1e-4)).name for T in tc]
def up(a): return np.interp(t, tc, np.asarray(a, float))
def mask(*ns): return up([1.0 if n in ns else 0.0 for n in names])
space = mask('A', 'B', 'F', 'G', 'I', 'J', 'K'); orla = mask('C', 'D', 'H'); busm = mask('E')
wind = up([shot_at(T).wind(T) if hasattr(shot_at(T), 'wind') else 0.0 for T in tc])
surge = up([shot_at(T).surge(T) if hasattr(shot_at(T), 'surge') else 0.0 for T in tc])
def smooth(x, s=0.04):            # suaviza degraus nos cortes
    k = int(s * SR); w = np.hanning(2 * k + 1); w /= w.sum(); return np.convolve(x, w, 'same')
space, orla, busm = smooth(space), smooth(orla), smooth(busm)

# ------------------------------------------------------------------ espaço: drone grave + "estrelas correndo" no gancho
x = t
drone = (np.sin(2 * np.pi * 36.7 * x) + 0.6 * np.sin(2 * np.pi * 55 * x + 1) + 0.3 * np.sin(2 * np.pi * 73.4 * x + 2)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * x))
air = lp(noise(), 400) * 0.25
spinA = up([P.A_w(T) / 0.30 if n == 'A' else 0.0 for T, n in zip(tc, names)])
rush = bp(noise(), 300, 2500) * spinA * 0.35            # sopro proporcional ao giro no gancho
add_st((drone * 0.10 + air * 0.4) * space + rush, 1.0)
# travada do giro (A, "parasse?"): rangido metálico grave + impacto
e = env(2.2, a=0.02, k=2.5); xx = np.arange(len(e)) / SR
groan = np.sin(2 * np.pi * (70 - 25 * xx) * xx) * e + bp(noise(len(e)), 90, 700) * e * 0.5
place(groan, 5.05, 0.55); events['impacts'].append(5.05)

# ------------------------------------------------------------------ orla: ondas, gaivotas, brisa -> vendaval
sw = 0.5 + 0.5 * np.sin(2 * np.pi * t / 6.5) ** 2
waves = lp(noise(), 900) * (0.25 + 0.75 * sw) * 0.35 + bp(noise(), 1500, 6000) * sw ** 3 * 0.08
gulls = np.zeros(N)
for bt in np.sort(rng.uniform(14.2, 52, 9)):
    for j in range(rng.integers(2, 4)):
        d = rng.uniform(0.18, 0.3); xx = np.arange(int(d * SR)) / SR; f0 = rng.uniform(1300, 1800)
        i = int((bt + j * 0.32) * SR)
        if i + len(xx) < N: gulls[i:i + len(xx)] += np.sin(2 * np.pi * (f0 * xx - 1400 * xx * xx)) * np.hanning(len(xx)) * 0.03
breeze = bp(noise(), 200, 1200) * 0.06
gust = 0.75 + 0.25 * np.sin(2 * np.pi * 0.7 * t) * np.sin(2 * np.pi * 0.23 * t + 1)
roar = (lp(noise(), 350) * 0.9 + bp(noise(), 400, 2200) * 0.45 + bp(noise(), 2500, 7000) * 0.12) * gust
flap = bp(noise(), 900, 4000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t))) * 0.08
calm = (waves + gulls * (1 - wind) + breeze) * (1 - 0.7 * wind)
storm = (roar * 0.55 + flap + lp(noise(), 600) * 0.3) * wind ** 1.3
rushw = (lp(noise(), 500) * 0.9 + bp(noise(), 300, 3000) * 0.4) * surge ** 0.6 * (1 - surge * 0.3)
add_st((calm + storm + rushw * 1.2) * orla, 1.0)
# tranco ("trava") e o chão parando: terremoto curto + baque
for at, g, d in ((P.T_TRAVA, 0.55, 1.2), (P.T_CHAO, 0.75, 1.8)):
    e = env(d, a=0.01, k=3); xx = np.arange(len(e)) / SR
    q = (np.sin(2 * np.pi * (42 - 10 * xx) * xx) + lp(noise(len(e)), 180) * 1.2) * e
    place(q, at, g); events['impacts'].append(at)
# boné voando: whoosh curto
def whoosh(d=0.6, f0=400, f1=2600):
    n = int(d * SR); xx = np.arange(n) / n; e_ = np.sin(np.pi * xx) ** 2; f = np.linspace(f0, f1, n)
    nz = noise(n); out = np.zeros(n)
    for a in range(0, n, 2048):
        b = min(n, a + 2048); fc = f[a]; out[a:b] = bp(nz[max(0, a - 512):b], fc * 0.6, min(fc * 1.6, 20000))[-(b - a):]
    return out * e_
place(whoosh(0.5, 2500, 700), P.T_CHAO + 0.15, 0.25, 0.4)

# ------------------------------------------------------------------ ônibus: motor pela velocidade, freada, ar comprimido
Eb = P.BY_NAME['E']
vb = up([Eb.bus_v(T) if n == 'E' else 0.0 for T, n in zip(tc, names)])
f0 = 32 + 2.6 * vb; ph = 2 * np.pi * np.cumsum(f0) / SR
eng = sum(np.sin(ph * h + h) / h for h in (1, 2, 3, 4, 6)) * 0.25 + bp(noise(), 60, 300) * 0.08
roadb = bp(noise(), 200, 2000) * 0.10 * (vb / 11) ** 1.4
city = bp(noise(), 150, 1200) * 0.05
braking = up([1.0 if n == 'E' and Eb.T_BRAKE <= T < Eb.T_BRAKE + P.BUS_V / P.BUS_DEC else 0.0 for T, n in zip(tc, names)])
sq = (np.sin(2 * np.pi * np.cumsum(820 + 60 * np.sin(2 * np.pi * 5 * t)) / SR) * 0.3 + bp(noise(), 1500, 5000) * 0.7) * braking * np.clip(vb / 4, 0, 1)
add_st((eng + roadb + city) * busm + sq * 0.22, 1.0)
t_stop = Eb.T_BRAKE + P.BUS_V / P.BUS_DEC
psh = bp(noise(int(0.8 * SR)), 2000, 9000) * env(0.8, a=0.02, k=3)
place(psh, t_stop + 0.25, 0.25); events['brake'] = dict(start=Eb.T_BRAKE, stop=round(t_stop, 3))
e = env(0.4, k=5); place(np.sin(2 * np.pi * 45 * np.arange(len(e)) / SR) * e, t_stop, 0.35)

# ------------------------------------------------------------------ mar escorrendo para os polos (J): ronco grave varrido
Jm = P.BY_NAME['J']; oc = up([Jm.ocean(T) if n == 'J' else 0.0 for T, n in zip(tc, names)])
doc = np.gradient(oc) * SR; doc = doc / (doc.max() + 1e-9)
drain = (lp(noise(), 250) * 0.8 + bp(noise(), 200, 900) * 0.3) * doc
add_st(drain, 0.6)
# órbita (I): sopro lento enquanto a Terra percorre meia volta
Im = P.BY_NAME['I']; ps = up([Im.psi(T) if n == 'I' else 0.0 for T, n in zip(tc, names)])
dps = np.abs(np.gradient(ps)) * SR; dps = dps / (dps.max() + 1e-9)
add_st(bp(noise(), 150, 900) * dps * 0.25, 1.0)

# ------------------------------------------------------------------ interface (rótulos) e transições
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); xx = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * xx / 0.09) * xx) * 0.5 + np.sin(2 * np.pi * 3000 * xx) * 0.15) * e_
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90} | {round(a_[3], 3) for s in P.SHOTS for a_ in getattr(s, 'arrows', [])})
if hasattr(P.BY_NAME['H'], 'bars'): pops += [P.BY_NAME['H'].bars[k] for k in ('t_big', 't_small', 't_x4')]
for p_ in sorted(set(pops)): place(pop_sound(), p_, 0.22); events['pops'].append(p_)
# barra crescendo (H): tom subindo enquanto cresce
for k_, dur in (('t_big', 0.7), ('t_small', 0.7)):
    n = int(dur * SR); xx = np.arange(n) / SR; tone = np.sin(2 * np.pi * (400 * xx + 500 * xx * xx / dur)) * np.minimum(xx / 0.02, 1) * np.exp(-2 * xx)
    place(tone, P.BY_NAME['H'].bars[k_], 0.06)
# anéis e faixas no globo: brilho subindo
for at in (9.25, 35.1, 36.1, 39.5):
    n = int(0.6 * SR); xx = np.arange(n) / n; place(bp(noise(n), 2000, 8000) * xx ** 2 * (1 - xx) * 4, at, 0.06)
for s in P.SHOTS[1:]:
    place(whoosh(0.55), s.t0 - 0.30, 0.12); events['cuts'].append(s.t0)

# ------------------------------------------------------------------ música: pad cinematográfico + pulso (Ré m – Si♭ – Fá – Dó)
mus = np.zeros(N); BPM = 88; beat = 60 / BPM; bar = 4 * beat
CH = [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]
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
    kick_t = [t0 + k * beat for k in range(4)]
    for kt in kick_t:
        dd = int(0.25 * SR); x2 = np.arange(dd) / SR
        kk = np.sin(2 * np.pi * (55 * x2 + 60 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-14 * x2)
        a_ = int(kt * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += kk[:b_ - a_] * 0.05
# CTA (F): pausa na música (só o drone); tempestade: música recua; final: abre
cta = mask('F'); mus *= (1 - 0.85 * smooth(cta, 0.2)) * (1 - 0.5 * wind) * (1 - 0.4 * surge)
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)

fade = np.minimum(t / 0.02, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.7
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', events['impacts'], '| freio', events['brake'], '| pops', len(events['pops']), '| cortes', len(events['cuts']))
