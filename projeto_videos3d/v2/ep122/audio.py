"""Som do vídeo 122 (The Key Ep. 2, 65 s). Cada efeito sai de um tempo da cena (teste_xavier/src/videos/chave2/story.ts):
o arranco da chave, o tranco no pulso, a corrida (os seus passos e os dele, mais pesados), o chaveiro tremendo e raspando na fechadura,
o clique, a porta batendo, as 4 pancadas, o silêncio (o ambiente some), a vibração do celular, o interruptor do quarto e o rangido em cima.
Saída: v2/ep122/out/sfx.wav, music.wav, sfx_events.json."""
import os, sys, json, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 48000; END = 65.0; N = int(END * SR)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(ROOT, 'assets', 'sfx_cc0'); IA = os.path.join(ROOT, 'assets', 'sfx_ia'); OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE); import plan as P
rng = np.random.default_rng(122)
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
K = P.W; tg = np.arange(N) / SR
hpf = lambda x, f: sosfilt(sos('highpass', f), x, axis=0)
sw = lambda k: norm(cc0(f'swish_{k}.flac')); woo = norm(cc0('whoosh_ar.flac'))
# ---- ambiente: rua (grilos + zumbido do poste) até a porta bater; dentro de casa um quarto quase mudo; some no "silence" ----
gr = loop(cc0('grilos_loop.flac'), END); hum = loop(cc0('zumbido_eletrico.flac'), END)
outK = np.clip(1 - (tg - 23.1) / 0.08, 0, 1) + np.clip((tg - 63.9) / 0.1, 0, 1)          # lá fora (e de novo no loop)
sfx += gr * np.clip(outK, 0, 1)[:, None] * 0.14 + hum * np.clip(outK, 0, 1)[:, None] * 0.05
room = lp(loop(cc0('geladeira_loop.flac'), END), 220)
inK = np.clip((tg - 23.1) / 0.1, 0, 1) * np.clip(1 - (tg - 63.9) / 0.1, 0, 1) * (1 - 0.85 * np.clip((tg - 30.3) / 0.6, 0, 1) * np.clip(1 - (tg - 33.5) / 0.4, 0, 1))
sfx += room * inK[:, None] * 0.05
EV.append((23.1, 'ambiente: rua lá fora até a porta bater; dentro, um quarto quase mudo; o silêncio de 30,3 a 33,5 s'))
# ---- o arranco: whoosh + chaveiro; o tranco no pulso ----
put(sw(7), K['e_key'] - 0.12, 0.35, tag='arranco da chave (swish)'); put(norm(ia('chaveiro.mp3'))[int(0.18 * SR):], K['e_key'], 0.3, tag='chaveiro na sua mão')
put(norm(cc0('impacto_hit_01.flac')), K['e_grabs'] + 0.25, 0.3, tag='ele agarra o pulso'); put(norm(cc0('impacto_hit_04.flac')), K['e_hard'], 0.42, tag='"hard": tranco')
put(sw(10), K['e_twist'], 0.38, tag='você se solta')
# ---- a corrida: os seus passos (contatos do ciclo, phase = z/1,5) e os dele, mais pesados e graves ----
ps = norm(ia('passos_calcada.mp3')); ONS = [0.06, 0.67, 1.49, 2.26, 2.98, 3.77, 4.58]
def step(t, g, low=None):
    a = ONS[int(rng.integers(len(ONS)))]; one = fade(ps[int((a - 0.02) * SR):int((a + 0.26) * SR)], 0.003, 0.1)
    put(lp(one, low) if low else one, t - 0.02, g)
def zy(t): return 15.45 + 3.9 * (t - 6.8)
t = 6.85; n = 0
while t < 13.7: step(t, 0.62 * rng.uniform(0.85, 1)); t += 0.75 / 2; n += 1          # 3,9 m/s, passada de 1,5 m: um pé a cada 0,38 s
t = 7.7; m = 0
while t < 22.8:
    d = 0.55 if t < 13.0 else 0.62
    near = 1.0 if t < 13.0 else (0.45 if t < 17.3 else (0.9 if t < 18.9 else 0.55))      # longe quando a câmera está na fechadura
    step(t, 0.55 * near, 1600); t += d / 2; m += 1
EV.append((6.85, f'{n} passos seus correndo e {m} dele (mais graves) até a porta'))
put(woo, 8.55, 0.25, tag='corte para a câmera correndo')
# ---- a fechadura: chaveiro tremendo, a chave raspando, o flip e o clique ----
ch = norm(ia('chaveiro.mp3'))
put(ch, 13.1, 0.45); put(ch[int(0.4 * SR):], 15.3, 0.45, tag='chaveiro tremendo na mão')
mac = norm(ia('macaneta.mp3')); put(hpf(mac, 900)[:int(1.6 * SR)], K['e_wont'], 0.45, tag='a chave raspando (não entra)')
put(norm(cc0('clique_7.flac')), K['e_flip'] + 0.05, 0.14, tag='flip')
put(norm(cc0('clique_1.flac')), K['e_click'], 0.75, tag='Click (a chave entra)'); put(norm(ia('fechadura_troca.mp3'))[int(1.72 * SR):int(2.3 * SR)], K['e_click'] + 0.1, 0.4)
# ---- dentro: a porta abre, você entra, a porta BATE ----
put(mac[int(0.15 * SR):int(1.1 * SR)], 21.7, 0.16, tag='porta abre')
slam = norm(ia('porta_bate_forte.mp3')); put(slam, K['e_slam'] - 0.08, 0.6, tag='SLAM (porta bate)')
# ---- as 4 pancadas dele do lado de fora (BANG, hits, once, twice) ----
mu = norm(ia('murro_porta.mp3'))
for tb, g in [(K['e_bang'], 1.0), (K['e_hits'] + 0.1, 0.8), (K['e_once'], 0.9), (K['e_twice'], 1.0)]: put(mu, tb, g)
EV.append((K['e_bang'], 'pancadas na porta (murro_porta, ElevenLabs) em BANG, hits, once, twice'))
# ---- o celular vibra; a mensagem chega ----
put(fade(norm(ia('celular_vibra.mp3'))[:int(0.75 * SR)], 0.005, 0.12), 32.75, 0.4, tag='celular vibra no fim do silêncio, antes de "Your phone" (não cobre a fala)')
put(norm(cc0('bolha_1.flac')), K['e_nice'] - 0.15, 0.3, tag='mensagem chega')
# ---- em cima: o interruptor do quarto (a luz apaga) e o rangido do assoalho ----
put(norm(cc0('clique_5.flac')), K['e_off'] - 0.02, 0.45, tag='a luz do quarto apaga (interruptor)')
cr = norm(ia('rangido_assoalho.mp3')); put(lp(cr, 3500), K['e_someone'] - 0.6, 0.55, tag='rangido do assoalho em cima')
put(lp(cr, 2500)[int(0.6 * SR):], K['e_already'] + 0.4, 0.4)
# ---- cortes e cartões ----
for tk in (50.4, 54.22, 57.3): put(sw(4), tk - 0.05, 0.16)
EV.append((50.4, 'swishes nos cartões A, B e "comment"'))
put(sw(10), 63.85, 0.2, tag='What if... -> loop')
# ---- pad grave (música): tenso, sobe na corrida, some no silêncio ----
def pad(freqs, d, gg=0.06):
    t = np.arange(int(d * SR)) / SR; m = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): m += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    m = lp(m, 1200) * gg / len(freqs); a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return np.stack([m * a, np.roll(m, 240) * a], 1)
for a, b, frq, g in [(0.0, 5.4, (73.4, 110, 146.8, 174.6), 0.06), (5.4, 13.0, (77.8, 116.5, 155.6, 185.0), 0.08), (13.0, 23.1, (82.4, 123.5, 164.8, 196.0), 0.08),
                     (23.1, 30.2, (65.4, 98, 130.8, 155.6), 0.06), (33.6, 42.2, (61.7, 92.5, 123.5, 146.8), 0.05), (42.2, 49.3, (58.3, 87.3, 116.5, 138.6), 0.06),
                     (49.3, END, (73.4, 110, 146.8, 174.6), 0.06)]:
    put(pad(frq, b - a + 0.6, g), a, 1.0, bus=mus)
# ---- a narração por cima: os efeitos abaixam ~8 dB enquanto ele fala (ataque 30 ms, volta em 250 ms) e voltam cheios nas pausas ----
vo = load(os.path.join(ROOT, 'narracao', '122_narracao.mp3'))[:N, 0]; vo = np.pad(vo, (0, N - len(vo)))
hop = 480; env = np.array([np.sqrt(np.mean(vo[i:i + hop] ** 2)) for i in range(0, N, hop)]); env = env / max(env.max(), 1e-9)
on = np.clip((20 * np.log10(env + 1e-6) + 40) / 15, 0, 1)                      # 0 abaixo de -40 dB, 1 acima de -25 dB (relativo ao pico)
sm = np.zeros_like(on); a_up, a_dn = np.exp(-hop / (0.03 * SR)), np.exp(-hop / (0.25 * SR))
for i in range(len(on)): sm[i] = on[i] + (sm[i - 1] - on[i]) * (a_up if on[i] > sm[i - 1] else a_dn) if i else on[i]
DUCK = 10 ** (-8 / 20); duck = np.repeat(1 - (1 - DUCK) * sm, hop)[:N]
sfx *= duck[:, None]; mus *= (1 - 0.6 * (1 - duck))[:, None]
EV.append((0.0, 'efeitos -8 dB enquanto a narração fala (envelope da voz), cheios nas pausas'))
pk = max(np.abs(sfx).max(), 1e-9); sfx *= min(1.0, 0.89 / pk)
pk = max(np.abs(mus).max(), 1e-9); mus *= 0.38 / pk   # trilha um pouco mais baixa que no 21 (não cobrir a narração)
wavfile.write(os.path.join(OUT, 'sfx.wav'), SR, (sfx * 32767).astype(np.int16))
wavfile.write(os.path.join(OUT, 'music.wav'), SR, (mus * 32767).astype(np.int16))
json.dump(sorted(EV), open(os.path.join(OUT, 'sfx_events.json'), 'w'), ensure_ascii=False, indent=0)
print('ok', len(EV), 'eventos')
