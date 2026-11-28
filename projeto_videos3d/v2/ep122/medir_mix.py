"""Mede, palavra por palavra, quanto a narração fica acima dos efeitos + trilha (pior caso: sem o compressor da montagem).
Uso: python3 v2/ep122/medir_mix.py [ganho_dos_efeitos]  (o ganho padrão é o SFX_BUS do plan.py)."""
import os, sys, json, subprocess, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(os.path.dirname(H)); sys.path.insert(0, H); import plan
SR = 16000
ld = lambda f: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).astype(np.float64)
g = float(sys.argv[1]) if len(sys.argv) > 1 else plan.SFX_BUS[0]
vo = ld(os.path.join(P, 'narracao', '122_narracao.mp3')); sx = ld(os.path.join(H, 'out', 'sfx.wav')); mu = ld(os.path.join(H, 'out', 'music.wav')); te = ld(os.path.join(H, 'out', 'tensao.wav'))
n = min(map(len, (vo, sx, mu, te))); vo, sx, mu, te = vo[:n], sx[:n], mu[:n], te[:n]
bed = sx * g + (mu * 0.55 + te * getattr(plan, 'W_TENSAO', 0.75)) * 0.62
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
ws = json.load(open(os.path.join(P, 'analysis', 'narracao', '122_words.json')))['words']
rows = [(w['w'], w['s'], db(vo[int(w['s'] * SR):int(w['e'] * SR)]) - db(bed[int(w['s'] * SR):int(w['e'] * SR)])) for w in ws]
rows.sort(key=lambda r: r[2])
print(f'ganho dos efeitos {g}: voz acima do resto, por palavra — pior {rows[0][2]:.1f} dB ("{rows[0][0]}" {rows[0][1]:.2f}s), mediana {rows[len(rows)//2][2]:.1f} dB')
print('5 piores:', [(r[0], round(r[1], 2), round(r[2], 1)) for r in rows[:5]])
for w, t, d in rows[:5]:
    a, b = int(t * SR), int(t * SR) + int(0.3 * SR)
    print(f'  "{w}" {t:.2f}s  voz {db(vo[a:b]):.1f}  efeitos {db(sx[a:b] * g):.1f}  trilha {db(mu[a:b] * 0.55 * 0.62):.1f}  tensão {db(te[a:b] * getattr(plan, 'W_TENSAO', 0.75) * 0.62):.1f} dB')
