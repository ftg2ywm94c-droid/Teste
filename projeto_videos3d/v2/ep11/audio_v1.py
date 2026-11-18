#!/usr/bin/env python3
"""Som do vídeo 11 (versão na skill Xavier): sons reais CC0 (assets/sfx_cc0, OpenGameArt) + efeitos sintetizados
(vibração do celular, encaixe magnético, bipes da maquininha, chiado de rádio, aviso de mensagem, carga) + trilha
(pad em ré menor que abre para ré maior no "dia três"). Tempos = palavras da narração (analysis/narracao/11_words.json).
Saída: v2/ep11/out/sfx.wav e music.wav (48 kHz estéreo). A camada de tensão é v2/ep11/out/tensao.wav (tensao.py)."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; END = 72.52; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

def load(name, t0=0.0, d=None):
    c = ['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', os.path.join(S, name)] + (['-t', str(d)] if d else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
def loop(name, d):
    x = load(name); reps = int(np.ceil(d * SR / len(x))) + 1; return np.tile(x, (reps, 1))[:int(d * SR)]
def fade(x, a=0.05, b=0.3):
    x = x.copy(); na, nb = min(len(x), int(a * SR)), min(len(x), int(b * SR))
    x[:na] *= np.linspace(0, 1, na)[:, None]; x[len(x) - nb:] *= np.linspace(1, 0, nb)[:, None]; return x
sos = lambda k, f, o=2: butter(o, f, k, fs=SR, output='sos')
bp = lambda x, lo, hi: sosfilt(sos('bandpass', [lo, hi]), x, axis=0)
lp = lambda x, f: sosfilt(sos('lowpass', f), x, axis=0)
def env(d, a=0.003, k=6.0):
    t = np.arange(int(d * SR)) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-k * t)
def st(m, pan=0.0): return np.stack([m * np.sqrt((1 - pan) / 2), m * np.sqrt((1 + pan) / 2)], 1)
def tone(f, d, k=5.0, a=0.003): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, a, k)

sfx = np.zeros((N, 2)); mus = np.zeros((N, 2)); EV = []
def put(x, at, g=1.0, bus=None, tag=''):
    b = sfx if bus is None else bus; i = int(at * SR); n = min(len(x), N - i)
    if n > 0: b[i:i + n] += x[:n] * g
    if tag: EV.append((round(at, 2), tag))

# ---- sintetizados ----
def vibra(d=0.9):        # celular vibrando: 2 pulsos de zumbido 160 Hz com chacoalhar
    t = np.arange(int(d * SR)) / SR; gate = ((t % 0.45) < 0.28).astype(float)
    m = (np.sin(2 * np.pi * 160 * t) + 0.4 * np.sign(np.sin(2 * np.pi * 320 * t))) * gate
    return st(lp(m, 900) * 0.5)
def snap():              # encaixe magnético: clique seco + baque grave + tilintar metálico curto
    c = rng.standard_normal(int(0.02 * SR)) * env(0.02, 0.0005, 260)
    th = tone(70, 0.25, 18) * 0.9
    ring = sum(tone(f, 0.35, 16) * g for f, g in [(2350, 0.18), (3720, 0.1), (5100, 0.06)])
    m = np.zeros(int(0.4 * SR)); m[:len(c)] += c * 1.4; m[:len(th)] += th; m[:len(ring)] += ring
    return st(m)
def bipe(f=2200, d=0.09): return st(tone(f, d, 8) * 0.5)
def erro():              # bipe de erro duplo grave
    m = np.zeros(int(0.5 * SR)); a = np.sign(tone(330, 0.16, 3)) * env(0.16, 0.002, 4) * 0.35
    m[:len(a)] += a; m[int(0.22 * SR):int(0.22 * SR) + len(a)] += a; return st(lp(m, 2500))
def chiado(d):           # rádio sintonizando: ruído em banda com varredura
    x = bp(rng.standard_normal(int(d * SR)), 600, 3200) * 0.25
    t = np.arange(len(x)) / SR; sw = np.sin(2 * np.pi * (300 + 900 * t / d) * t) * 0.12 * (t > d * 0.6)
    return fade(st(x + sw), 0.05, 0.25)
def mensagem(): return st(np.concatenate([tone(1320, 0.09, 14), tone(1760, 0.18, 10)]) * 0.45)
def carga():             # carga começando: arpejo ascendente suave
    m = np.zeros(int(0.9 * SR))
    for i, f in enumerate((523, 659, 784, 1047)): x = tone(f, 0.5, 6) * 0.3; m[int(i * 0.09 * SR):int(i * 0.09 * SR) + len(x)] += x
    return st(m)
def lanterna(): return load('clique_3.flac')
def relogio(d, bpm=120):
    m = np.zeros(int(d * SR)); step = 60 / bpm
    for k in range(int(d / step)):
        x = tone(1900 if k % 2 else 1500, 0.03, 60) * 0.5; i = int(k * step * SR); m[i:i + len(x)] += x[:len(m) - i]
    return st(m)

# ---- linha do tempo ----
put(fade(loop('geladeira_loop.flac', 3.94), 0.4, 0.4), 0.0, 0.35, tag='casa: zumbido da geladeira')
put(fade(loop('zumbido_eletrico.flac', 2.0), 0.05, 0.8), 3.95, 0.12, tag='Amapá: zumbido que morre')
put(fade(load('gotas.flac', 0, 6.0), 0.3, 1.0), 4.2, 0.35, tag='Amapá: silêncio com gotas')
put(fade(loop('chuva_loop.flac', 7.1), 0.15, 0.25), 10.18, 0.9, tag='SP: chuva')
put(load('chuva_trovao.flac', 0, 5.0), 11.96, 0.7, tag='SP: trovão (temporal)')
put(load('chuva_trovao.flac', 5.0, 4.0), 15.6, 0.5, tag='SP: trovão 2')
put(fade(loop('geladeira_loop.flac', 1.33), 0.1, 0.02), 17.23, 0.6, tag='hora zero: geladeira ligada')
put(load('disjuntor_desliga.flac'), 18.51, 1.2, tag='apaga: disjuntor')
put(load('maquina_desligando.flac'), 18.46, 0.8, tag='apaga: geladeira desligando')
put(relogio(22.6 - 19.9, 120), 19.9, 0.3, tag='geladeira: relógio de 4 h')
put(bipe(880, 0.12), 25.66, 0.6, tag='risco: aviso')
put(load('maquina_desligando.flac'), 30.2, 0.45, tag='bomba parando')
put(load('clique_5.flac'), 30.24, 0.8, tag='bomba: clique')
put(fade(load('porao_gotejando.flac', 0, 2.2), 0.05, 0.6), 31.5, 0.6, tag='torneira pingando até secar')
put(fade(loop('gerador_loop.flac', 2.2), 0.3, 0.5), 37.9, 0.55, tag='antena: gerador')
put(load('maquina_desligando.flac'), 39.75, 0.5, tag='gerador falha')
put(fade(loop('zumbido_eletrico.flac', 1.2), 0.02, 0.4), 39.8, 0.15)
put(load('clique_1.flac'), 41.1, 0.8, tag='sinal some')
for k in range(2): put(bipe(2200), 42.05 + k * 0.16, 0.8)
EV.append((42.05, 'maquininha: bipes'))
put(erro(), 44.12, 0.9, tag='Pix não passa: erro')
put(vibra(), 45.0, 0.9, tag='celular vibrando')
put(lanterna(), 48.12, 1.0, tag='lanterna: clique')
put(chiado(1.7), 49.04, 0.7, tag='rádio sintonizando')
put(mensagem(), 50.94, 0.8, tag='mensagem enviada')
put(snap(), 59.12, 1.0, tag='power bank: encaixe magnético')
put(carga(), 60.78, 0.7, tag='carga começando')
put(load('disjuntor_liga.flac'), 63.7, 1.1, tag='a luz volta: disjuntor')
put(fade(loop('geladeira_loop.flac', 4.5), 0.5, 1.0), 64.0, 0.35, tag='geladeira volta')
put(fade(loop('zumbido_eletrico.flac', 0.8), 0.02, 0.5), 63.86, 0.12)

# ---- trilha: pad em ré menor (tensão) que abre para ré maior no dia três ----
def pad(freqs, d, g=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1400) * g / len(freqs); a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
SEC = [(0.0, 17.2, (73.4, 110, 174.6, 220)), (17.2, 26.9, (73.4, 116.5, 174.6, 233.1)), (26.9, 44.9, (65.4, 98, 155.6, 196)),
       (44.9, 52.2, (87.3, 130.8, 174.6, 220)), (52.2, 62.7, (98, 146.8, 196, 246.9)), (62.7, END, (73.4, 110, 185, 220, 293.7))]
for a, b, fr in SEC: put(pad(fr, b - a + 1.0), a, 1.0, bus=mus)
# pulso leve de "relógio" na trilha nos dias 1 e 2
put(relogio(44.9 - 26.9, 96) * 0.25, 26.9, 1.0, bus=mus)

pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.5 / pk
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
import json; json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
