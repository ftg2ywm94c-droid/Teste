"""Planos do vídeo 18 (Jogador 2 · Ep. 1) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/jogador2 (story.ts tem os mesmos cortes)."""
FPS = 30; END = 64.60
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(e0=6.82, mora=9.28, juntou=12.96, internet=16.2, agora=20.28, so=22.58, ai=24.68, luzinha=26.74, sem=29.54, tv=31.46, na=33.38,
         voce=37.68, os=39.6, sofa=43.4, alguma=45.4, decide=47.54, opcaoA=48.94, opcaoB=52.56, comenta=57.28, manda=61.6)
F = lambda t: round(t * FPS)
_keys = list(W)
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [round(END * FPS)]
_names = ['S01_tv_99', 'S02_luz_caiu', 'S03_sitio', 'S04_console', 'S05_antena', 'S06_escuro', 'S07_milharal', 'S08_percebe',
          'S09_luzinha', 'S10_sem_energia', 'S11_tv_liga', 'S12_jogador2', 'S13_um_controle', 'S14_cachorros', 'S15_sofa',
          'S16_vibrar', 'S17_decide', 'S18_opcao_a', 'S19_opcao_b', 'S20_escolha', 'S21_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
