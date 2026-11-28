"""Planos do vídeo 16 (Vendaval · Ep. 3, continuação do vídeo 14) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/vendaval3 (story.ts tem os mesmos cortes)."""
FPS = 30; END = 76.93
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(n193=4.36, atendem=7.38, endereco=10.06, fio=12.1, vizinha=13.76, outro=15.68, nao=18.14, tres=22.76, ligacao=24.08, agora=27.2,
         la=30.42, ela=32.42, e1=34.88, ai=38.02, e2=41.4, abre=43.52, entre=47.88, e3=51.32, opcaoA=56.38, opcaoB=60.92, comenta=66.58, manda=71.58)
F = lambda t: round(t * FPS)
_keys = list(W)
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [round(END * FPS)]
_names = ['S01_disca_193', 'S02_chama', 'S03_atendem', 'S04_endereco', 'S05_fio', 'S06_vizinha_janela', 'S07_voz_calma', 'S08_nao_chega_perto',
          'S09_tres_porcento', 'S10_apaga', 'S11_escuridao', 'S12_sirene_longe', 'S13_chegando', 'S14_para_silencio', 'S15_batem', 'S16_vizinha_porta',
          'S17_abre', 'S18_sala_escura', 'S19_fio_meio', 'S20_opcao_a', 'S21_opcao_b', 'S22_escolha', 'S23_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
