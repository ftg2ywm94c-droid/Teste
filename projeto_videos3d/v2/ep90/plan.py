"""Planos do piloto de qualidade (15 s, roteiros/piloto_qualidade.md) na skill Xavier: teste_xavier/src/videos/piloto (PilotoShort).
3D em 1080x1920 NATIVO. Narração: Spuds Oxley (eleven_v3), narracao/piloto/piloto_narracao.mp3 (cópia idêntica em narracao/90_narracao.mp3)."""
import math
FPS = 30; END = 15.6          # TOTAL = 468 quadros na story.ts (a voz acaba em 15,22 s)
NATIVE = True
SFX_BUS = (2.0, 2)
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(poste=3.9, mao=7.35, rua2=9.95, chave=12.45, pisca=4.94, apaga=6.12, liga=8.14, alguem=11.2)
F = lambda t: math.floor(t * FPS + 0.5)          # igual ao Math.round da story.ts
_cuts = [0, F(W['poste']), F(W['mao']), F(W['rua2']), F(W['chave']), 468]
_names = ['P1_anda', 'P2_poste', 'P3_mao', 'P4_pov', 'P5_chave']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
