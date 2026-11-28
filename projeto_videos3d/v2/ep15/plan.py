"""Planos do vídeo 15 (série "Você decide": O último ônibus, Parte 2) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/onibus2 (story.ts tem os mesmos cortes)."""
FPS = 30; END = 75.96
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
LIMITER = 0.8        # limitador a 192 kHz (pico real abaixo de -1 dBTP depois do AAC)
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(e1=3.08, no=5.96, ele1=10.02, as_=14.52, o1=20.26, boa=23.02, voce1=26.82, ele2=30.58, e2=36.06, o2=38.08, dezenas=40.72,
         e3=45.04, a1=46.96, pela=48.38, e4=52.44, voceTem=56.72, opcaoA=58.96, opcaoB=61.52, comenta=65.8, e5=72.82)
F = lambda t: round(t * FPS)
_keys = list(W)
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [2279]
_names = ['S01_porta_fecha', 'S02_vai_embora', 'S03_letreiro', 'S04_rua_escura', 'S05_luzes', 'S06_vibra', 'S07_boa_escolha', 'S08_retrovisor',
          'S09_banco_fundo', 'S10_alguem', 'S11_garagem', 'S12_dezenas', 'S13_sem_motorista', 'S14_porta_abre', 'S15_ultima_parada',
          'S16_toca', 'S17_cinco_seg', 'S18_opcao_a', 'S19_opcao_b', 'S20_escolha', 'S21_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
