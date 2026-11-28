"""Monta a faixa de vozes do vídeo 20 (narracao/20_narracao.mp3) com as falas geradas (sem mudar velocidade nem cortar pausas).
- cada fala é nivelada pelo RMS das partes com voz (as falas soam com o mesmo volume);
- a avó atrás da porta: A1 abafada (passa-baixa 2,6 kHz, "do outro lado da porta"); A2 sussurrada mais perto (passa-baixa 4,5 kHz);
- os intervalos sem voz são os momentos das mensagens na tela.
Saída: ../20_narracao.mp3 e 20_linhas.json (início/fim de cada fala)."""
import os, json, subprocess, numpy as np
from scipy.signal import butter, sosfilt
H = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ORDEM = [('N1', 0.00), ('N2', 16.80), ('A1', 22.30), ('N3', 25.60), ('A2', 49.80), ('N4', 52.80), ('N5', 56.20), ('N6', 61.60)]
TAIL = 0.65
def load(i):
    c = ['ffmpeg', '-v', 'error', '-i', os.path.join(H, i + '.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32).astype(np.float64)
def lp(x, f): return sosfilt(butter(4, f, 'low', fs=SR, output='sos'), x)
def vrms(x):
    h = int(0.02 * SR); e = np.array([np.sqrt((x[k:k + h] ** 2).mean()) for k in range(0, len(x) - h, h)]); return np.sqrt((e[e > e.max() * 0.1] ** 2).mean())
xs = {i: load(i) for i, _ in ORDEM}
end = max(t + len(xs[i]) / SR for i, t in ORDEM) + TAIL; out = np.zeros(int(end * SR)); lines = []
for i, t in ORDEM:
    x = xs[i] * (0.1 / vrms(xs[i]))
    if i == 'A1': x = lp(x, 2600) * 1.15
    if i == 'A2': x = lp(x, 4500)
    a = int(t * SR); out[a:a + len(x)] += x; lines.append(dict(id=i, t0=round(t, 3), t1=round(t + len(x) / SR, 3)))
for a, b in zip(lines, lines[1:]): assert b['t0'] >= a['t1'] - 0.7, (a, b)   # as falas não se sobrepõem (só o silêncio final do take)
out *= 0.89 / np.abs(out).max()
wav = os.path.join(H, '20_narracao.wav'); from scipy.io import wavfile; wavfile.write(wav, SR, (out * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-b:a', '192k', os.path.join(H, '..', '20_narracao.mp3')], check=True)
json.dump(dict(end=round(end, 3), lines=lines), open(os.path.join(H, '20_linhas.json'), 'w'), indent=1)
print('fim', round(end, 2), 's'); [print(l) for l in lines]
