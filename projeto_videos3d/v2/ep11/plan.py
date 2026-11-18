"""Planos do vídeo 11 na skill Xavier (Remotion + three.js). O 3D é renderizado em 1080x1920 NATIVO em
teste_xavier/src/videos/luz (story.ts tem os mesmos cortes). Este arquivo só lista os planos para a montagem e o QC."""
FPS = 30; END = 72.52
NATIVE = True
SFX_BUS = (2.0, 2)   # efeitos num canal próprio: +6 dB e ducking leve (razão 2) — pedido do usuário: efeitos mais presentes
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(naoE=3.94, em2024=10.2, hora=17.24, apaga=18.56, geladeira=19.78, dia1=26.86, dia2=34.86, maquininha=41.82, ai=44.96, porIsso=52.22, dia3=62.72, diferente=67.3)
F = lambda t: round(t * FPS)
_cuts = [0, F(W['naoE']) - 1, F(W['em2024']) - 1, F(W['hora']) - 1, F(W['apaga']) - 1, F(W['geladeira']) - 2, F(W['dia1']) - 1, F(W['dia2']) - 1,
         F(W['maquininha']) - 2, F(W['ai']) - 1, F(W['porIsso']) - 1, F(W['dia3']) - 1, F(W['diferente']) + 3, round(END * FPS)]
_names = ['S01_gancho', 'S02_amapa', 'S03_temporal', 'S04_hora_zero', 'S05_apaga', 'S06_geladeira', 'S07_predio', 'S08_antena',
          'S09_maquininha', 'S10_celular', 'S11_powerbank', 'S12_luz_volta', 'S13_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
