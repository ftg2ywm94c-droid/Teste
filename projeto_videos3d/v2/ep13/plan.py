"""Planos do vídeo 13 (série "Você decide": O último ônibus, Ep. 1) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/onibus (story.ts tem os mesmos cortes)."""
FPS = 30; END = 70.6
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
LIMITER = 0.8        # limitador a 192 kHz (pico real abaixo de -1 dBTP depois do AAC)
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(so=3.5, senta=5.84, ate=10.42, naoE=12.58, banco=14.12, ele1=17.6, voce2=20.28, numero=22.8, naoDesce=25.84, olha=28.36,
         ele2=30.14, chega=33.32, onibus=37.42, porta=40.86, celular3=45.94, voceTem=49.8, opcaoA=52.04, opcaoB=55.62, comenta=61.0, se=66.76)
F = lambda t: round(t * FPS)
_keys = ['so', 'senta', 'ate', 'naoE', 'banco', 'ele1', 'voce2', 'numero', 'naoDesce', 'olha', 'ele2', 'chega', 'onibus', 'porta', 'celular3',
         'voceTem', 'opcaoA', 'opcaoB', 'comenta', 'se']
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [round(END * FPS)]
_names = ['S01_gancho', 'S02_corredor', 'S03_cochilo', 'S04_toca', 'S05_acorda', 'S06_sozinho', 'S07_toca_de_novo', 'S08_aproxima',
          'S09_desconhecido', 'S10_nao_desce', 'S11_motorista', 'S12_retrovisor', 'S13_ele_sabe', 'S14_freia', 'S15_porta', 'S16_fica_sentado',
          'S17_cinco_seg', 'S18_opcao_a', 'S19_opcao_b', 'S20_escolha', 'S21_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
