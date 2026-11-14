#!/usr/bin/env python3
"""Montagem final: quadros 720x1280 -> 1080x1920 (lanczos, declarado como ampliação) + legenda ASS + narração original + efeitos/música
com ducking pela voz, normalização -14 LUFS / -1,5 dBTP. Depois roda o QC.
Uso: python3 v2/assemble.py [--allow-missing]"""
import os, sys, glob, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE); sys.path[:0] = [os.path.join(HERE, 'lib'), HERE]
EP = os.environ.get('EP')          # ex.: EP=02 usa v2/ep02 (planos, quadros, saída) e narracao/02_narracao.mp3
if EP:
    BASE = os.path.join(HERE, f'ep{EP}'); sys.path.insert(0, BASE); import plan as SH
    DEF_NAME = {'02': '02_terra_parasse_de_girar_1080x1920.mp4', '03': '03_buraco_atravessa_a_terra_1080x1920.mp4', '04': '04_oxigenio_sumisse_20s_1080x1920.mp4', '05': '05_todo_oxigenio_sumisse_1080x1920.mp4', '06': '06_apocalipse_zumbi_brasil_1080x1920.mp4', '07': '07_furacao_avenida_paulista_1080x1920.mp4'}.get(EP, f'{EP}_1080x1920.mp4')
else:
    BASE = HERE; import shots as SH
    DEF_NAME = '01_distancia_de_parada_1080x1920.mp4'
FR = os.path.abspath(os.environ.get('FRAMES_DIR', os.path.join(BASE, 'frames'))); OUT = os.environ.get('OUT_DIR', os.path.join(BASE, 'out')); os.makedirs(OUT, exist_ok=True)
NARR = os.path.join(PROJ, 'narracao', f'{EP or "01"}_narracao.mp3')
total = round(SH.END * SH.FPS)
paths, missing = [], []
for s in SH.SHOTS:
    for f in s.frames:
        p = os.path.join(FR, s.name, f'{f:04d}.png')
        if not os.path.exists(p) or os.path.getsize(p) == 0: missing.append(f)
        paths.append(p)
assert len(paths) == total, (len(paths), total)
if missing and '--allow-missing' not in sys.argv: sys.exit(f'faltam {len(missing)} quadros (ex.: {missing[:10]})')
with open(os.path.join(OUT, 'frames.txt'), 'w') as f:
    last = None
    for p in paths:
        if os.path.exists(p) and os.path.getsize(p) > 0: last = p
        f.write(f"file '{last}'\nduration {1 / SH.FPS:.6f}\n")
def run(c): print('$', ' '.join(c[:6]), '...'); subprocess.run(c, check=True)
# áudio: voz original intacta (só reamostrada) + leito de efeitos/música abaixado pela voz
fc = ('[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[v][key];'
      '[1:a][2:a]amix=inputs=2:weights=1 0.55:normalize=0[bed];'
      '[bed][key]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=300:makeup=1[duck];'
      '[v]volume=1.0[vv];[vv][duck]amix=inputs=2:weights=1 0.62:normalize=0:duration=longest,'
      'apad=whole_dur=' + f'{SH.END:.3f}' + ',atrim=0:' + f'{SH.END:.3f}' + ',loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[mix]')
run(['ffmpeg', '-y', '-v', 'error', '-i', NARR, '-i', os.path.join(OUT, 'sfx.wav'), '-i', os.path.join(OUT, 'music.wav'),
     '-filter_complex', fc, '-map', '[mix]', '-ar', '48000', '-c:a', 'pcm_s16le', os.path.join(OUT, 'mix.wav')])
vf = ('scale=1080:1920:flags=lanczos,unsharp=5:5:0.45:5:5:0.0,eq=contrast=1.03:saturation=1.05,'
      f"ass={os.path.join(OUT, 'legenda.ass')}:fontsdir={os.path.join(PROJ, 'fonts')},format=yuv420p")
final = os.path.join(OUT, os.environ.get('OUT_NAME', DEF_NAME))
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(OUT, 'frames.txt'), '-i', os.path.join(OUT, 'mix.wav'),
     '-vf', vf, '-r', '30', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{SH.END:.3f}', '-movflags', '+faststart', final + '.tmp.mp4'])
os.replace(final + '.tmp.mp4', final); print('ok', final, 'faltando:', len(missing))
# versão leve (~6 Mbps) para baixar no celular: o app só mostra o botão de baixar em arquivos menores
if os.path.getsize(final) > 80e6 and os.environ.get('LEVE', '1') == '1':
    leve = final.replace('.mp4', '_leve.mp4'); x = ['-c:v', 'libx264', '-preset', 'slow', '-b:v', '6200k', '-maxrate', '9000k', '-bufsize', '12000k']
    pl = os.path.join(OUT, 'ffpass')
    run(['ffmpeg', '-y', '-v', 'error', '-i', final] + x + ['-pass', '1', '-passlogfile', pl, '-an', '-f', 'mp4', '/dev/null'])
    run(['ffmpeg', '-y', '-v', 'error', '-i', final] + x + ['-pass', '2', '-passlogfile', pl, '-profile:v', 'high', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', '-c:a', 'copy', leve])
    for f in os.listdir(OUT):
        if f.startswith('ffpass'): os.remove(os.path.join(OUT, f))
    print('leve', leve, round(os.path.getsize(leve) / 1e6), 'MB')
