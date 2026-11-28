#!/usr/bin/env python3
"""Som do piloto de qualidade (15,6 s). Cada efeito sai de um tempo da própria cena (teste_xavier/src/videos/piloto/story.ts e cast.ts),
não de chute:
- passos (ElevenLabs, assets/sfx_ia/passos_calcada.mp3): um por contato do pé no ciclo de caminhada (phase = 0,9·t; contato em 0 e 0,5
  -> a cada 0,556 s) enquanto você anda (t < 4,5 s);
- zumbido do poste (CC0 zumbido_eletrico.flac): ligado e desligado quadro a quadro pelo MESMO padrão de poleAt; estalo em cada troca;
- clique da lanterna (CC0 clique_1.flac) no "liga" (8,14 s);
- chaveiro (ElevenLabs, chaveiro.mp3) quando a lanterna revela a figura e no close da chave;
- grilos CC0 bem baixos (rua de madrugada), swishes nos cortes, pad grave. Sem ruído sintético contínuo.
Saída: v2/ep90/out/sfx.wav, music.wav, sfx_events.json."""
import os, sys, json, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; END = 15.6; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); IA = os.path.join(ROOT, 'assets', 'sfx_ia'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE); import plan as P
rng = np.random.default_rng(90)
def load(path, t0=0.0, d=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', path] + (['-t', str(d)] if d else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
cc0 = lambda n, *a: load(os.path.join(S, n), *a); ia = lambda n, *a: load(os.path.join(IA, n), *a)
def loop(x, d): reps = int(np.ceil(d * SR / len(x))) + 1; return np.tile(x, (reps, 1))[:int(d * SR)]
def fade(x, a=0.05, b=0.3):
    x = x.copy(); na, nb = min(len(x), int(a * SR)), min(len(x), int(b * SR)); x[:na] *= np.linspace(0, 1, na)[:, None]; x[len(x) - nb:] *= np.linspace(1, 0, nb)[:, None]; return x
sos = lambda k, f, o=2: butter(o, f, k, fs=SR, output='sos')
lp = lambda x, f: sosfilt(sos('lowpass', f), x, axis=0)
norm = lambda x, pk=1.0: x * (pk / max(np.abs(x).max(), 1e-9))
sfx = np.zeros((N, 2)); mus = np.zeros((N, 2)); EV = []
def put(x, at, g=1.0, bus=None, tag=''):
    b = sfx if bus is None else bus; i = int(at * SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), N - i)
    if n > 0: b[i:i + n] += x[:n] * g
    if tag: EV.append((round(at, 2), tag))
W = P.W
# ---- o poste: mesmo padrão quadro a quadro de poleAt (story.ts) ----
PAT = [1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0]
def pole_at(t):
    if t < W['pisca']: return 1
    if t >= W['apaga']: return 0
    k = int(np.floor((t - W['pisca']) * 30)); return PAT[k] if k < len(PAT) else 0
fr = np.arange(int(END * 30)) / 30; on = np.array([pole_at(t) for t in fr], float)
gate = np.repeat(on, SR // 30)[:N]; gate = np.pad(gate, (0, N - len(gate)))
k = int(0.004 * SR); gate = np.convolve(gate, np.ones(k) / k, 'same')       # sem estalo digital na troca (4 ms)
near = np.where((np.arange(N) / SR >= P.BY_NAME['P2_poste'].t0) & (np.arange(N) / SR < P.BY_NAME['P3_mao'].t0), 1.0, 0.35)  # perto da lâmpada no plano 2
k = int(0.1 * SR); near = np.convolve(near, np.ones(k) / k, 'same')
hum = loop(cc0('zumbido_eletrico.flac'), END)
sfx += hum * (gate * near)[:, None] * 0.22
EV.append((0.0, 'zumbido do poste (CC0), no padrão de poleAt'))
clk = norm(cc0('clique_3.flac')); flips = [fr[i] for i in range(1, len(on)) if on[i] != on[i - 1]]
for t in flips: put(clk, t, 0.18 if on[int(round(t * 30))] else 0.25)
EV.append((W['pisca'], f'estalos do poste: {len(flips)} trocas'))
put(lp(norm(cc0('disjuntor_desliga.flac')), 2500), W['apaga'], 0.35, tag='poste apaga (estalo final)')
# ---- passos: contatos do ciclo (phase = 0,9 t; contato em 0 e 0,5) enquanto anda ----
ps = norm(ia('passos_calcada.mp3')); ONS = [0.06, 0.67, 1.49, 2.26, 2.98, 3.77, 4.58]   # ataques medidos no arquivo
steps = [kk / 1.8 for kk in range(20) if kk / 1.8 < 4.5]
for i, t in enumerate(steps):
    a = ONS[i % len(ONS)]; one = fade(ps[int((a - 0.02) * SR):int((a + 0.32) * SR)], 0.004, 0.12)
    put(one, t - 0.02, 0.55 * rng.uniform(0.85, 1.0))
EV.append((0.0, f'{len(steps)} passos nos contatos do pé'))
# ---- lanterna ----
put(norm(cc0('clique_1.flac')), W['liga'] - 0.02, 0.5, tag='clique da lanterna')
# ---- o chaveiro: baixo quando a lanterna revela, cheio no close ----
ch = norm(ia('chaveiro.mp3'))
put(lp(ch, 5000), W['alguem'] + 0.15, 0.25, tag='chaveiro ao longe')
put(ch, W['chave'] + 0.1, 0.55, tag='chaveiro no close')
# ---- ambiente: grilos bem baixos ----
sfx += loop(cc0('grilos_loop.flac'), END) * 0.12
# ---- cortes ----
for i, s in enumerate(P.SHOTS[1:]): put(cc0(f'swish_{(1, 4, 7, 10)[i % 4]}.flac'), s.t0 - 0.06, 0.14)
put(cc0('impacto_hit_03.flac'), W['chave'], 0.28, tag='impacto: segurando a sua chave')
# ---- pad grave (música) ----
def pad(freqs, d, gg=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * gg / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, frq in [(0.0, 7.35, (73.4, 110, 146.8, 174.6)), (7.35, 12.45, (69.3, 103.8, 138.6, 164.8)), (12.45, END, (65.4, 98, 130.8, 155.6))]:
    put(pad(frq, b - a + 0.8), a, 1.0, bus=mus)
pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos; trocas do poste', [round(x, 2) for x in flips])
