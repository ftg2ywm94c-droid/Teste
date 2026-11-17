#!/usr/bin/env python3
"""Áudio + legenda do teste (trecho 16,90–22,90 s do vídeo 11): narração original, camada de tensão do 11, sons reais CC0
(geladeira, disjuntor, máquina desligando) e tique-taque sintetizado no plano do relógio. Saída: out/apagao/som.wav e legenda.ass"""
import os, sys, re, subprocess, numpy as np
from scipy.io import wavfile
P = '/home/user/Teste/projeto_videos3d'; sys.path.insert(0, P + '/v2/lib'); import tensao as TZ
T0, D = 16.9, 6.0; SR = 48000; OUT = '/home/user/Teste/teste_xavier/out/apagao'
T_OFF, T_FR = 18.56 - T0, 19.78 - T0
def load(p, t0=0.0, d=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', p] + (['-t', str(d)] if d else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
N = int(D * SR); bed = np.zeros((N, 2))
def put(x, at, g):
    i = int(at * SR); n = min(len(x), N - i)
    if n > 0: bed[i:i + n] += x[:n] * g
ten = load(P + '/v2/ep11/out/tensao.wav', T0, D); put(ten, 0, 0.75)
S = P + '/assets/sfx_cc0/'
fr = load(S + 'geladeira_loop.flac', 0, T_OFF + 0.02); fr[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))[:, None]; put(fr, 0, 0.9)
put(load(S + 'disjuntor_desliga.flac'), T_OFF - 0.05, 1.2)
put(load(S + 'maquina_desligando.flac'), T_OFF - 0.1, 0.8)
l, r = TZ.relogio(D - T_FR - 0.1, 120); put(np.stack([l, r], 1), T_FR + 0.1, 0.35)
wavfile.write(OUT + '/bed.wav', SR, bed.astype(np.float32))
narr = P + '/narracao/11_narracao.mp3'
fc = (f'[0:a]atrim={T0}:{T0 + D},asetpts=PTS-STARTPTS,aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[v][key];'
      '[bed][key]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=300:makeup=1[duck];'
      '[v][duck]amix=inputs=2:weights=1 0.62:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[mix]')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', narr, '-i', OUT + '/bed.wav', '-filter_complex', fc.replace('[bed]', '[1:a]'),
                '-map', '[mix]', '-c:a', 'pcm_s16le', OUT + '/som.wav'], check=True)
# legenda: desloca a do vídeo 11 inteiro para o trecho
def ts(s): s = max(0, s); return f'{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}'
def tsec(x): h, m, s = x.split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
L = []
for ln in open(P + '/v2/ep11/out/legenda.ass'):
    if ln.startswith('Dialogue:'):
        p = ln.split(',', 9); a, b = tsec(p[1]) - T0, tsec(p[2]) - T0
        if b <= 0 or a >= D: continue
        p[1], p[2] = ts(a), ts(min(b, D)); ln = ','.join(p)
    L.append(ln)
open(OUT + '/legenda.ass', 'w').writelines(L); print('ok')
