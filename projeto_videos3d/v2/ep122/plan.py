"""Planos do vídeo 122 (The Key · Ep. 2, inglês, canal You Decide 3D; roteiros/122_the_key_ep2.md) na skill Xavier:
teste_xavier/src/videos/chave2 (Chave2Short). 3D em 1080x1920 NATIVO. Narração: narracao/122_narracao.mp3 (Spuds Oxley, eleven_v3, en;
montagem em narracao/122_vozes/montar.py)."""
import math
FPS = 30; END = 65.0          # TOTAL = 1950 quadros na story.ts
NATIVE = True
SFX_BUS = (2.0, 2)
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(e_rip=0.3, e_key=0.76, e_grabs=2.62, e_hard=4.3, e_twist=5.7, e_run=7.38, e_behind=8.82, e_fast=10.8, e_shaking=14.06,
         e_wont=15.56, e_wrong=17.5, e_flip=19.18, e_click=20.38, e_inside=22.0, e_slam=23.16, e_bang=24.68, e_hits=26.12, e_once=27.56,
         e_twice=28.82, e_then=30.32, e_silence=32.18, e_phone=33.96, e_unknown=35.92, e_nice=37.94, e_keys=40.5, e_upstairs=42.66,
         e_off=44.78, e_someone=46.62, e_already=47.84, e_decide=49.4, e_A=50.4, e_B=54.22, e_comment=57.3, e_most=60.6, e_whatif=64.02, k_se=63.9)
F = lambda t: math.floor(t * FPS + 0.5)          # igual ao Math.round da story.ts
_cuts = [0] + [F(t) for t in (2.3, 5.4, 8.6, 13.0, 17.3, 18.9, 21.6, 24.5, 30.2, 33.6, 42.2, 49.3, 63.9)] + [1950]
_names = ['G01_arranca', 'G02_pulso', 'G03_corre', 'G04_perseguicao', 'G05_fechadura', 'G06_atras', 'G07_click', 'I08_bate_porta',
          'I09_bang', 'I10_silencio', 'I11_celular', 'I12_escada', 'I13_escolha', 'G14_loop']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
