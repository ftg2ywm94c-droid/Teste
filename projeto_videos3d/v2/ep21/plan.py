"""Planos do vídeo 21 (A Chave · Ep. 1, roteiros/21_a_chave_ep1.md) na skill Xavier: teste_xavier/src/videos/chave (ChaveShort).
3D em 1080x1920 NATIVO. Os planos 1–5 são os quadros do piloto (v2/ep90/frames, links), iguais. Narração: narracao/21_narracao.mp3
(piloto intacto + 4 falas novas do Spuds Oxley, eleven_v3; montagem em narracao/21_vozes/montar.py)."""
import math
FPS = 30; END = 65.0          # TOTAL = 1950 quadros na story.ts
NATIVE = True
SFX_BUS = (2.0, 2)
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(poste=3.9, mao=7.35, rua2=9.95, chave=12.45, pisca=4.94, apaga=6.12, liga=8.14, alguem=11.2,
         k_perdeu=16.08, k_praca=18.64, k_procurou=19.9, k_banco=20.98, k_grama=21.96, k_meiofio=22.86, k_homem=26.2, k_olhando=27.8,
         k_sol=29.92, k_desistiu=31.8, k_chaveiro=33.48, k_fechadura=34.82, k_entao=36.22, k_seguro=37.3, k_levanta=40.6, k_aponta=42.56,
         k_casa=43.82, k_quarto=46.7, k_acende=47.2, k_sozinho=50.44, k_decide=51.68, k_se=63.58)
F = lambda t: math.floor(t * FPS + 0.5)          # igual ao Math.round da story.ts
_cuts = [0] + [F(t) for t in (W['poste'], W['mao'], W['rua2'], W['chave'], 15.6, 19.9, 24.0, 29.2, 36.1, 39.6, 45.8, 51.6, 63.6)] + [1950]
_names = ['P1_anda', 'P2_poste', 'P3_mao', 'P4_pov', 'P5_chave', 'C06_sobe', 'C07_procura', 'C08_homem', 'C09_por_do_sol', 'C10_volta',
          'C11_aponta', 'C12_janela', 'C13_escolha', 'C14_loop']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
