"""Planos do vídeo 20 (A Visita · Ep. 1) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/visita (story.ts tem os mesmos cortes, F(t) sem -1).
Áudio: narrador Spuds Oxley + avó (Edna), ElevenLabs eleven_v3, em narracao/20_narracao.mp3 (76,01 s)."""
FPS = 30; END = 76.01
NATIVE = True
SFX_BUS = (2.0, 2)
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(relogio=1.9, senta=4.4, cel=7.4, msg1=9.8, foto=13.5, msg2=15.2, chuva=16.8, bate=18.8, corredor=22.3, olho=25.6, ela=28.9,
         casaco=30.8, janela=33.3, celia=35.1, marido=41.5, rua=44.4, macaneta=49.8, vibra=52.8, msg3=54.9, porta2=56.2, digitando=59.6,
         decide=61.7, opcaoA=63.3, opcaoB=65.9, comenta=69.0, se=74.5)
F = lambda t: round(t * FPS)
_cuts = [0] + [F(W[k]) for k in W] + [2280]
_names = ['S01_quarto', 'S02_despertador', 'S03_acorda', 'S04_celular', 'S05_msg1', 'S06_foto', 'S07_msg2', 'S08_chuva', 'S09_bate',
          'S10_corredor', 'S11_olho', 'S12_avo', 'S13_casaco', 'S14_janela', 'S15_celia', 'S16_marido', 'S17_rua', 'S18_macaneta',
          'S19_vibra', 'S20_msg3', 'S21_fresta', 'S22_digitando', 'S23_decide', 'S24_opcao_a', 'S25_opcao_b', 'S26_escolha', 'S27_loop']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
