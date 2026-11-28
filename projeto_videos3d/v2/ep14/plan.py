"""Planos do vídeo 14 (Vendaval · Ep. 2, continuação do vídeo 12) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/vendaval2 (story.ts tem os mesmos cortes)."""
FPS = 30; END = 67.4
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
LIMITER = 0.8        # limitador a 192 kHz (pico real abaixo de -1 dBTP depois do AAC)
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(porta=2.86, celular=4.34, la=8.14, ai=10.44, casa=12.3, vidro=14.02, arvore=18.78, voce=21.96, mas=24.4, e1=27.34, voceAbre=29.6,
         a2=32.22, noChao=34.92, ai2=40.78, e2=43.76, opcaoA=48.3, opcaoB=53.22, comenta=58.3, se=63.66)
F = lambda t: round(t * FPS)
_keys = list(W)
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [round(END * FPS)]
_names = ['S01_recap', 'S02_trinco', 'S03_lanterna', 'S04_vento', 'S05_queda', 'S06_treme', 'S07_destrocos', 'S08_caiu', 'S09_inteiro',
          'S10_goteira', 'S11_fumaca', 'S12_fresta', 'S13_sala', 'S14_fio', 'S15_vibra', 'S16_vizinha', 'S17_opcao_a', 'S18_opcao_b',
          'S19_escolha', 'S20_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
