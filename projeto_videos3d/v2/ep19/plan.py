"""Planos do vídeo 19 (A Noite Livre · Ep. 1) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/noitelivre (story.ts tem os mesmos cortes, F(t) sem -1).
Áudio: narração (ElevenLabs, Ana Dias) + falas dos personagens em narracao/19_narracao.mp3 (64,58 s)."""
FPS = 30; END = 64.58
NATIVE = True
SFX_BUS = (2.0, 2)
LIMITER = 0.8
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(tv1=3.55, ancora=8.36, rostos=12.25, cortina=16.24, tranca=18.76, cade=21.12, quintal=22.39, portao=24.59, ultimo=25.85,
         rua=28.5, esquina=32.2, porta=35.93, thor=37.32, dois=38.86, correr=40.53, vira=43.62, quieto=45.37, mascaras=48.55,
         decide=50.53, opcaoA=52.1, opcaoB=54.6, comenta=58.2, se=62.55)
F = lambda t: round(t * FPS)
_cuts = [0] + [F(W[k]) for k in W] + [1937]
_names = ['S01_sofa', 'S02_tv', 'S03_ancora', 'S04_rostos', 'S05_cortina', 'S06_tranca', 'S07_caminha', 'S08_quintal', 'S09_portao',
          'S10_foi_voce', 'S11_thor_rua', 'S12_mascaras', 'S13_porta', 'S14_bia', 'S15_tv_2min', 'S16_pai', 'S17_vira',
          'S18_thor_quieto', 'S19_abana', 'S20_decide', 'S21_opcao_a', 'S22_opcao_b', 'S23_escolha', 'S24_loop']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
BY_NAME = {s.name: s for s in SHOTS}
