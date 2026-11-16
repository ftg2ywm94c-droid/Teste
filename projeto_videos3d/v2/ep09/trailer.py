"""Gera os quadros dos planos de trailer (TR*) do vídeo 09 a partir do trailer oficial enviado pelo usuário.
Trechos curtos (≤ 2,6 s), sem áudio, numa moldura própria: fundo desfocado, faixa central, etiqueta "NO JOGO" e crédito.
Uso: python3 v2/ep09/trailer.py   → v2/ep09/frames/TRn/NNNN.png (720x1280, numeração global de quadros)."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import plan as P
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'assets', 'trailer', '09_trailer_gta6.mp4')
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf')
W, H, BH = 720, 1280, 506            # faixa central: recorte 1536x1080 do trailer → 720x506

def run(shot):
    n = len(shot.frames); f0 = shot.frames[0]; out = os.path.join(HERE, 'frames', shot.name); os.makedirs(out, exist_ok=True)
    y0 = (H - BH) // 2 - 40
    tag = "drawtext=fontfile='%s':text='NO JOGO':fontsize=40:fontcolor=black:box=1:boxcolor=0xFFCC14:boxborderw=14:x=(w-text_w)/2:y=%d" % (FONT, y0 - 78)
    cred = "drawtext=fontfile='%s':text='trailer oficial — Rockstar Games':fontsize=19:fontcolor=white@0.85:box=1:boxcolor=black@0.55:boxborderw=6:x=w-text_w-18:y=%d" % (FONT, y0 + BH - 36)
    fc = (f"[0:v]fps=30,split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=24:2,eq=brightness=-0.18:saturation=0.8[bg];"
          f"[b]crop=1536:1080,scale={W}:{BH}[fg];[bg][fg]overlay=0:{y0},{tag},{cred}")
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{shot.src:.3f}', '-i', SRC, '-an', '-filter_complex', fc, '-frames:v', str(n),
           '-start_number', str(f0), os.path.join(out, '%04d.png')]
    subprocess.run(cmd, check=True)
    got = len([x for x in os.listdir(out) if x.endswith('.png')]); print(shot.name, 'quadros', got, 'de', n, flush=True)
    assert got == n

if __name__ == '__main__':
    for s in P.SHOTS:
        if s.kind == 'trailer': run(s)
