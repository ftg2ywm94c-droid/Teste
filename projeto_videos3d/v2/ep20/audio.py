#!/usr/bin/env python3
"""Som do vídeo 20 (A Visita · Ep. 1). Sem ruído sintético contínuo (lição do vídeo 19: o "chiado").
- chuva e trovões REAIS (CC0: assets/sfx_cc0/chuva_loop.flac, chuva_trovao.flac): abafados dentro de casa, cheios lá fora; trovão em cada relâmpago;
- efeitos gerados na ElevenLabs (assets/sfx_ia, ver CREDITOS.md): despertador, celular vibrando, batidas na porta, maçaneta;
- swishes CC0 nos cortes, impactos nos títulos, pad grave (música) e whoosh do loop.
Saída: v2/ep20/out/sfx.wav, music.wav, sfx_events.json."""
import os, sys, json, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; END = 76.01; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); IA = os.path.join(ROOT, 'assets', 'sfx_ia'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE); import plan as P
rng = np.random.default_rng(20)
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
def seg(x, a, d, tail=0.25): y = x[int(a * SR):int((a + d + tail) * SR)].copy(); return fade(y, 0.003, tail)

# ---- chuva: começa em "chover" (16,8 s); dentro de casa passa-baixa 700 Hz e mais baixa; lá fora cheia ----
OUTS = ('S08', 'S12', 'S13', 'S15', 'S16', 'S17')
g = np.full(N, 0.0)
for s in P.SHOTS:
    if s.t1 <= P.W['chuva']: continue
    g[int(max(s.t0, P.W['chuva']) * SR):int(s.t1 * SR)] = 1.0 if s.name.startswith(OUTS) else 0.35
k = int(0.08 * SR); g = np.convolve(g, np.ones(k) / k, 'same')
rain = loop(cc0('chuva_loop.flac'), END)
ramp = np.clip((np.arange(N) / SR - P.W['chuva']) / 1.5, 0, 1)
inside = (g < 0.6)[:, None]
sfx += np.where(inside, lp(rain, 700) * 1.6, rain) * (g * ramp)[:, None] * 0.32
EV.append((P.W['chuva'], 'chuva real CC0 (abafada dentro, cheia lá fora)'))
# trovões reais em cada relâmpago (o trecho mais forte do arquivo de trovão), abafados dentro
th = cc0('chuva_trovao.flac'); e = np.abs(th).mean(1); kk = int(0.5 * SR); pk_i = int(np.argmax(np.convolve(e, np.ones(kk), 'same')))
boom = fade(th[max(0, pk_i - int(0.6 * SR)):pk_i + int(3.5 * SR)], 0.2, 1.2); boom = norm(boom)
for b in [17.6, 29.0, 41.6, 47.2, 56.4, 74.2]:
    ins = g[min(N - 1, int((b + 0.3) * SR))] < 0.6
    put(lp(boom, 900) if ins else boom, b + 0.25, 0.42 if ins else 0.55, tag='trovão (relâmpago)')
# ---- despertador: toca do quadro 0 até "celular acende", só no quarto ----
al = norm(ia('despertador.mp3')); put(loop(al, P.W['cel'] + 0.3), 0.0, 0.5, tag='despertador 03:00')
# ---- celular: acende (toque curto de notificação = vibração) e vibra de novo ----
vb = norm(ia('celular_vibra.mp3'))
for t, gg, tg in [(8.1, 0.45, 'celular acende (vibra)'), (9.9, 0.4, 'mensagem 1'), (15.25, 0.4, 'mensagem 2'), (53.3, 0.55, 'o celular vibra de novo'), (59.7, 0.3, 'digitando')]:
    put(vb, t, gg, tag=tg)
# ---- batidas: 3 batidas (uma batida real recortada, repetida com intervalo de 0,45 s) ----
kn = norm(ia('batidas_porta.mp3')); one = seg(kn, 1.08, 0.08, 0.3)
for i, t in enumerate([19.25, 19.7, 20.15]): put(one, t, 0.95 - 0.08 * i)
EV.append((19.25, 'TOC TOC TOC: três batidas'))
for i, t in enumerate([56.5, 56.95, 57.4]): put(lp(one, 1800), t, 0.5)   # batem de novo, mais fraco, no "mas se ela tá na porta"
EV.append((56.5, 'batidas de novo (fracas)'))
# ---- a maçaneta girando ----
put(norm(ia('macaneta.mp3')), 50.6, 0.7, tag='maçaneta girando')
# ---- cortes e títulos ----
for i, s in enumerate(P.SHOTS[1:]): put(cc0(f'swish_{(1, 4, 7, 10, 13)[i % 5]}.flac'), s.t0 - 0.06, 0.16)
for t, nm in [(13.5, 'impacto_hit_01.flac'), (28.9, 'impacto_hit_03.flac'), (48.8, 'impacto_hit_03.flac'), (60.7, 'impacto_metal_hit_02.flac'), (63.3, 'impacto_hit_04.flac'), (65.9, 'impacto_hit_04.flac')]:
    put(cc0(nm), t, 0.32, tag='título: impacto')
put(cc0('whoosh_ar.flac', 0, 0.8), 74.5, 0.4, tag='E se...: whoosh do loop')
# ---- pad grave (música) ----
def pad(freqs, d, gg=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * gg / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, fr in [(0.0, 16.8, (73.4, 110, 146.8, 174.6)), (16.8, 28.9, (69.3, 103.8, 138.6, 164.8)), (28.9, 49.8, (65.4, 98, 130.8, 155.6)),
                 (49.8, 61.7, (61.7, 92.5, 123.5, 146.8)), (61.7, END, (73.4, 110, 146.8, 185))]:
    put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)
pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
