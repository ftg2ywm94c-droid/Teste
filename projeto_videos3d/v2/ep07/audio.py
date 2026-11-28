#!/usr/bin/env python3
"""Design sonoro do vídeo 07 (furacão na Avenida Paulista), 100% sintetizado e dirigido pelo plano (v2/ep07/plan.py).
Camadas: vento com rajadas e uivo entre prédios (ressonâncias que sobem com a força), chuva (chiado + gotas individuais),
trovões (estalo + ribombar com eco), árvore (rangido, estalo, queda, folhas), apagão (zumbido elétrico, faísca, queda de tensão),
destroços (placas metálicas, vidro quebrando, galhos) com "passagens" perto da câmera, mar e furacão no relevo, espaço,
painéis (sobe-e-impacto) e reverberação de cidade. A voz NÃO é tocada aqui (o ducking é feito na montagem).
Saída: v2/ep07/out/sfx.wav e music.wav (48 kHz estéreo) + sfx_events.json."""
import os, sys, json, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P

SR = 48000; T_END = P.END; N = int(T_END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(77)
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
WIND = ctrl([getattr(x, 'wind', 0.0) for x in SH], 0.25)
RAIN = ctrl([getattr(x, 'rain', 0.0) for x in SH], 0.2)

# ------------------------------------------------------------------ vento: rajadas (passeio aleatório suave) + uivo ressonante entre prédios
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
base_l = lp(brown(), 900) * 0.8 + lp(noise(), 350) * 0.25; base_r = lp(brown(), 900) * 0.8 + lp(noise(), 350) * 0.25
h1 = resonant_howl(320 + 380 * gust_c, 14); h2 = resonant_howl(540 + 520 * gust_c[::-1], 20); h3 = resonant_howl(880 + 600 * gust_c, 26)
howl_l = h1 * 0.5 + h3 * 0.25; howl_r = h2 * 0.5 + h3 * 0.2
street = kmask('paulista', 'rua')
wl = (base_l * 0.55 + howl_l * 0.35 * GUST) * WIND * GUST * street; wr = (base_r * 0.55 + howl_r * 0.35 * GUST) * WIND * GUST * street
bed(wl * 0.6, wr * 0.6, 0.15)
# assobio agudo nas rajadas fortes (cantos de prédio)
whis = resonant_howl(1400 + 900 * gust_c, 40); bed(whis * np.clip(GUST - 0.9, 0, 1) * WIND * street * 0.12, whis[::-1] * np.clip(GUST - 0.9, 0, 1) * WIND * street * 0.1)

# ------------------------------------------------------------------ chuva: chiado + gotas individuais + escoamento
hiss_l = bp(noise(), 2500, 11000) * 0.5 + bp(noise(), 600, 2500) * 0.18; hiss_r = bp(noise(), 2500, 11000) * 0.5 + bp(noise(), 600, 2500) * 0.18
bed(hiss_l * RAIN * 0.10, hiss_r * RAIN * 0.10, 0.1)
drops = np.zeros(N); drops_r = np.zeros(N)
nd = int(T_END * 900); rain_c = np.interp(tc, t[::480], RAIN[::480])
for k in range(nd):
    at = rng.uniform(0, T_END); lvl = float(np.interp(at, tc, rain_c))
    if rng.random() > lvl: continue
    f = rng.uniform(1800, 7000); n = int(rng.uniform(0.004, 0.012) * SR); x = np.arange(n) / SR
    d = np.sin(2 * np.pi * f * x * (1 - 0.3 * x / x[-1])) * np.exp(-x / (x[-1] / 4)) * rng.uniform(0.2, 1.0)
    i = int(at * SR); j = min(N, i + n)
    (drops if rng.random() < 0.5 else drops_r)[i:j] += d[:j - i]
bed(drops * 0.05, drops_r * 0.05, 0.05)
bed(lp(noise(), 250) * RAIN * 0.06 * street, lp(noise(), 250) * RAIN * 0.06 * street)          # água escorrendo

# ------------------------------------------------------------------ trovões
def thunder(d=4.0, near=1.0):
    n = int(d * SR); x = np.arange(n) / SR; out = np.zeros(n)
    for k in range(int(6 * near)):                                                 # estalos iniciais
        a = int(rng.uniform(0, 0.12) * SR); m = int(0.03 * SR); out[a:a + m] += hp(noise(m), 1200) * np.exp(-np.arange(m) / (m / 5)) * near
    rum = lp(brown(n), 140) * 2.0 + bp(noise(n), 60, 400) * 0.6
    sw = np.zeros(n)
    for k in range(5):
        c = rng.uniform(0.15, d * 0.7); w = rng.uniform(0.2, 0.8); sw += np.exp(-((x - c) / w) ** 2) * rng.uniform(0.5, 1.0)
    out += rum * (0.3 + sw) * np.exp(-x / (d * 0.45)) * np.minimum(x / 0.04, 1)
    return out / (np.abs(out).max() + 1e-9)
place(thunder(4.5, 0.6), 0.02, 0.55, -0.3, delay_ms=8)
for s_ in P.SHOTS:
    for tf in getattr(s_, 'flash', ()):
        place(thunder(4.0, 1.0), tf + 0.18, 0.75, rng.uniform(-0.4, 0.4), delay_ms=6); events['impacts'].append(tf)
place(thunder(3.5, 0.4), 13.2, 0.3, 0.5)                                            # trovão distante no temporal de 2023

# ------------------------------------------------------------------ árvore: rangido, estalo, queda, folhas e baque
TA = P.T_ARVORE
n = int(0.8 * SR); x = np.arange(n) / SR; fm = 140 + 60 * np.sin(2 * np.pi * 3 * x) + 200 * x
creak = np.sign(np.sin(2 * np.pi * np.cumsum(fm) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * x)); creak = bp(creak, 250, 1600) * np.minimum(x / 0.3, 1)
place(creak, TA - 0.55, 0.22, -0.2)
snap = mix(hp(noise(int(0.06 * SR)), 800) * env(0.06, 0.0005, 7), tone(780, 0.12, 30) * 0.6, tone(1350, 0.08, 40) * 0.4)
place(snap, TA, 0.8, -0.2); events['impacts'].append(TA)
n = int(1.1 * SR); x = np.arange(n) / SR
leaves = bp(noise(n), 2500, 9000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * x))) * np.sin(np.pi * x / 1.1) ** 2
place(leaves, TA + 0.15, 0.35, -0.1)
crash = mix(lp(noise(int(1.0 * SR)), 300) * env(1.0, 0.004, 5) * 1.4, bp(noise(int(0.4 * SR)), 300, 2000) * env(0.4, 0.002, 6) * 0.6)
place(crash, TA + 0.72, 1.0, -0.1); place(tone(55, 0.6, 7) * 0.9, TA + 0.72, 0.6); events['impacts'].append(TA + 0.72)

# ------------------------------------------------------------------ apagão: zumbido, faísca, queda de tensão, silêncio
TB = P.T_APAGA; n = int(1.2 * SR); x = np.arange(n) / SR
hum = sum(np.sin(2 * np.pi * 60 * h * x) / h for h in (1, 2, 3, 5)) * np.minimum(x / 0.5, 1)
place(hum[:int((TB - 17.6) * SR)] if TB > 17.6 else hum, 17.6, 0.06, wet=False)
for k in range(9):
    place(hp(noise(int(0.02 * SR)), 2500) * env(0.02, 0.0003, 6), TB - 0.12 + rng.uniform(0, 0.25), 0.35, rng.uniform(-0.6, 0.6))
glide = np.sin(2 * np.pi * np.cumsum(np.geomspace(320, 35, int(0.9 * SR))) / SR) * np.exp(-np.arange(int(0.9 * SR)) / SR * 2.5)
place(glide, TB, 0.32); place(lp(noise(int(0.15 * SR)), 200) * env(0.15, 0.001, 6), TB + 0.02, 0.5); events['impacts'].append(TB)

# ------------------------------------------------------------------ destroços: placas (metal), vidro, galhos, passagens
def metal_clang(f0=None):
    f0 = f0 or rng.uniform(260, 520); d = rng.uniform(0.35, 0.7)
    return mix(*[tone(f0 * r, d, k) * g for r, k, g in ((1.0, 5, 1.0), (2.76, 8, 0.6), (5.40, 12, 0.4), (8.93, 18, 0.25))], hp(noise(int(d * SR)), 2000) * env(d, 0.0005, 30) * 0.4)
def glass_shatter():
    d = 0.45; n = int(d * SR); out = np.zeros(n)
    for k in range(40):
        a = int(min(rng.exponential(0.06), d - 0.06) * SR); s_ = tone(rng.uniform(3500, 11000), 0.06, 40) * rng.uniform(0.3, 1)
        out[a:a + len(s_)] += s_[:n - a]
    return mix(out, hp(noise(n), 4000) * env(d, 0.0005, 14) * 0.5)
def wood_knock(): return mix(bp(noise(int(0.08 * SR)), 300, 1400) * env(0.08, 0.0008, 8), tone(rng.uniform(180, 320), 0.15, 25) * 0.5)
def passby(d=0.5):
    n = int(d * SR); x = np.arange(n) / n; f = 500 + 2500 * np.exp(-((x - 0.5) / 0.18) ** 2); out = np.zeros(n); z = noise(n)
    for a in range(0, n, 1200):
        b = min(n, a + 1200); out[a:b] = bp(z[max(0, a - 600):b], f[a] * 0.6, min(f[a] * 1.5, 20000))[-(b - a):]
    return out * np.sin(np.pi * x) ** 2
for s_ in P.SHOTS:
    if not hasattr(s_, 'debris'): continue
    dur = s_.t1 - s_.t0; t_on = max(s_.debris, s_.t0)
    for k in range(int(dur * 3.2)):
        at = rng.uniform(t_on, s_.t1); kind = rng.choice(['placa', 'vidro', 'galho'], p=[0.45, 0.25, 0.3]); pan = rng.uniform(-0.85, 0.85)
        sig = metal_clang() if kind == 'placa' else glass_shatter() if kind == 'vidro' else wood_knock()
        place(sig, at, 0.22 if kind != 'vidro' else 0.16, pan, delay_ms=rng.uniform(0, 0.6))
    for k in range(int(dur * 1.5)):
        place(passby(rng.uniform(0.35, 0.7)), rng.uniform(t_on, s_.t1), 0.22, rng.uniform(-0.7, 0.7))
# palavras-gatilho do roteiro: placas, vidros, galhos
place(metal_clang(330), 29.55, 0.45, -0.3); place(glass_shatter(), 30.50, 0.4, 0.3); place(wood_knock(), 31.05, 0.5, 0.0); place(passby(0.6), 31.6, 0.4, 0.2)
events['impacts'] += [29.55, 30.50, 31.05]

# ------------------------------------------------------------------ espaço (furacão visto de cima), relevo (mar, furacão enfraquecendo)
glob = kmask('globo'); swirl = resonant_howl(180 + 60 * np.sin(2 * np.pi * 0.3 * tc), 6)
bed((lp(brown(), 90) * 0.5 + swirl * 0.15) * glob * 0.5, (lp(brown(), 90) * 0.5 + swirl[::-1] * 0.15) * glob * 0.5, 0.2)
rel = kmask('relevo'); F4 = P.BY_NAME['F4']; wk = np.clip((t - F4.weaken[0]) / (F4.weaken[1] - F4.weaken[0]), 0, 1)
swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t) ** 2
sea = lp(noise(), 600) * swell * 0.5 + bp(noise(), 800, 3000) * swell ** 3 * 0.15
bed(sea * rel * 0.35, sea[::-1] * rel * 0.35, 0.1)
hur = (lp(brown(), 600) * 0.6 + h1 * 0.4) * (1 - 0.85 * wk)
bed(hur * rel * 0.4, hur[::-1] * rel * 0.4, 0.15)

# ------------------------------------------------------------------ painéis e contador
def riser(d, f0, f1):
    n = int(d * SR); x = np.arange(n) / SR; f = np.geomspace(f0, f1, n)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + bp(noise(n), 1000, 6000) * 0.3) * (x / d) ** 1.5
def hit(boom=60):
    return mix(tone(boom, 0.9, 5) * 1.0, lp(noise(int(0.4 * SR)), 900) * env(0.4, 0.001, 8) * 0.6, tone(2400, 0.05, 30) * 0.3)
place(hit(48), 0.0, 0.9, wet=True); events['impacts'].append(0.0)                    # impacto do gancho
A1 = P.BY_NAME['A1']; t1, t2 = A1.panel[3]; place(riser(t2 - t1, 180, 900), t1, 0.28); place(hit(55), t2, 0.6)
C1 = P.BY_NAME['C1']; c1, c2 = C1.panel[3]; place(riser((c2 - c1) / 2, 300, 700), c1, 0.18); place(riser((c2 - c1) / 2, 300, 1300), (c1 + c2) / 2, 0.22); place(hit(70), 21.80, 0.45)
C2 = P.BY_NAME['C2']; f1_, f2_ = C2.panel[3]; place(tone(660, 0.2, 10), f1_, 0.2)
for i in range(4): place(tone(520 + 140 * i, 0.12, 14), f2_ - 0.6 + 0.2 * i, 0.18)
place(hit(45), f2_ + 0.2, 0.7); events['impacts'].append(f2_ + 0.2)
G1 = P.BY_NAME['G1']; ts = G1.panel[5]
n = int(0.45 * SR); x = np.arange(n) / SR; scratch = bp(noise(n), 500, 4000) * np.sin(np.pi * x / 0.45) * (1 + np.sin(2 * np.pi * 18 * x))
place(scratch, ts, 0.35); place(np.sin(2 * np.pi * np.cumsum(np.geomspace(500, 60, int(0.6 * SR))) / SR) * env(0.6, 0.002, 3), ts + 0.05, 0.4)
# setas do efeito corredor: sopro que acelera
D1 = P.BY_NAME['D1']; place(passby(1.2), D1.arrows, 0.3); place(riser(2.0, 200, 1100) * 0.6, D1.arrows + 0.4, 0.2)

# ------------------------------------------------------------------ interface (rótulos) e transições
def pop_sound():
    e_ = env(0.09, a=0.001, k=8); x = np.arange(len(e_)) / SR
    return (np.sin(2 * np.pi * (1500 + 900 * x / 0.09) * x) * 0.5 + np.sin(2 * np.pi * 3000 * x) * 0.15) * e_
pops = sorted({round(l[4], 3) for s in P.SHOTS for l in s.labels if l[4] < 90})
for p_ in pops: place(pop_sound(), p_, 0.18, wet=False); events['pops'].append(p_)
for s in P.SHOTS[1:]:
    place(passby(0.5), s.t0 - 0.25, 0.10); events['cuts'].append(s.t0)

# ------------------------------------------------------------------ reverberação de cidade (resposta ao impulso sintética)
ir_n = int(1.6 * SR); xi = np.arange(ir_n) / SR
def ir(seed):
    r_ = np.random.default_rng(seed); h = r_.standard_normal(ir_n) * np.exp(-xi / 0.35); h[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    return lp(h, 4500) / np.sqrt(np.sum(h ** 2))
L += fftconvolve(FX_L, ir(1))[:N] * 0.35 * kmask('paulista', 'rua', s=0.02) + fftconvolve(FX_L, ir(1))[:N] * 0.12 * (1 - kmask('paulista', 'rua', s=0.02))
R += fftconvolve(FX_R, ir(2))[:N] * 0.35 * kmask('paulista', 'rua', s=0.02) + fftconvolve(FX_R, ir(2))[:N] * 0.12 * (1 - kmask('paulista', 'rua', s=0.02))

# ------------------------------------------------------------------ música: Ré m – Si♭ – Fá – Dó, 100 BPM, tensa; pulso grave
mus = np.zeros(N); BPM = 100; beat = 60 / BPM; bar = 4 * beat
CH = [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(T_END / bar) + 1):
    t0 = b * bar; chord = CH[b % 4]; d = int(bar * SR); x = np.arange(d) / SR
    padv = sum(np.sin(2 * np.pi * mtof(m - 12) * x + j) * 0.5 + np.sin(2 * np.pi * mtof(m) * x * 1.003) * 0.25 for j, m in enumerate(chord))
    padv *= np.minimum(x / 0.5, 1) * np.minimum((bar - x) / 0.5, 1)
    i = int(t0 * SR); j = min(N, i + d)
    if i < N: mus[i:j] += lp(padv, 1500)[:j - i] * 0.05
    for q in range(8):
        m = chord[q % 3] + 12 + (12 if q % 4 == 3 else 0); dd = int(0.35 * SR); x2 = np.arange(dd) / SR
        nt = (np.sin(2 * np.pi * mtof(m) * x2) + 0.3 * np.sin(4 * np.pi * mtof(m) * x2)) * np.exp(-9 * x2) * np.minimum(x2 / 0.004, 1)
        a_ = int((t0 + q * beat / 2) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += nt[:b_ - a_] * 0.024
    for k in range(4):
        dd = int(0.3 * SR); x2 = np.arange(dd) / SR
        kk = np.sin(2 * np.pi * (48 * x2 + 70 * (1 - np.exp(-30 * x2)) / 30)) * np.exp(-11 * x2)
        a_ = int((t0 + k * beat) * SR); b_ = min(N, a_ + dd)
        if a_ < N: mus[a_:b_] += kk[:b_ - a_] * 0.06
mus *= 1 - 0.6 * kmask('globo') * 0 - 0.5 * ctrl([1.0 if x.name == 'H1' else 0.0 for x in SH])
mus *= np.minimum(t / 1.0, 1) * np.minimum((T_END - t) / 1.5, 1)

fade = np.minimum(t / 0.01, 1) * np.minimum((T_END - t) / 0.4, 1)
st = np.stack([L, R], 1) * fade[:, None]; st = st / (np.abs(st).max() + 1e-9) * 0.8
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
wavfile.write(os.path.join(out, 'sfx.wav'), SR, st.astype(np.float32))
mm = np.stack([mus, mus * 0.97], 1); mm = mm / (np.abs(mm).max() + 1e-9) * 0.5
wavfile.write(os.path.join(out, 'music.wav'), SR, mm.astype(np.float32))
json.dump(events, open(os.path.join(out, 'sfx_events.json'), 'w'), indent=1)
print('ok', T_END, 's | impactos', len(events['impacts']), '| pops', len(events['pops']), '| cortes', len(events['cuts']))
