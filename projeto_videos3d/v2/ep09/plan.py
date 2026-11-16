"""Planos do vídeo 09 (e se a vida real seguisse as regras do GTA?). T = tempo da narração (s), amarrado a analysis/narracao/09_words.json.
Estilo 2. Tipos: rua (rua de dia do vídeo 04), estudio (laboratório de batida), trailer (trecho curto do trailer oficial, sem áudio,
com moldura "NO JOGO" e crédito; quadros gerados por v2/ep09/trailer.py, não pelo Blender)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 61.90           # narração termina em 61,88 s

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []; self.panel = None
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def eased(knots):
    f = ease(knots); a, b = knots[0][0], knots[-1][0]
    return lambda T: f(min(max(T, a), b))
def cam(pos_knots, look_knots, lens=35):
    P, L = eased(pos_knots), eased(look_knots)
    return lambda T: dict(pos=P(T), look=L(T), lens=lens)

YEL, RED, WHITE, BLUE, GREEN, ORANGE = (1.0, 0.80, 0.08), (1.0, 0.22, 0.14), (0.97, 0.97, 0.97), (0.45, 0.72, 1.0), (0.35, 0.95, 0.45), (1.0, 0.55, 0.12)
SHOTS = []
def S(*a):
    s = Shot(*a); SHOTS.append(s); return s

TEO = (21.0, 4.7, 0.0)           # Téo na calçada, de frente para a rua (-Y)
ROAD = (21.0, 0.2, 0.0)          # Téo deitado na pista
BLD_Y0 = 10.0                    # fachada do prédio de 7 andares (x 12–31)
CAFE = (17.2, 5.4)

# ================================================================= GANCHO
TR1 = S('TR1', 0.00, 1.46, 'trailer', 'no GTA (trailer: perseguição de carro)'); TR1.src = 46.40
A1 = S('A1', 1.46, 7.60, 'rua', 'você é atropelado, levanta e sai andando; na vida real, nem levantaria')
A1.cam = cam([(1.46, (23.9, -2.3, 0.95)), (7.60, (23.2, -1.8, 0.9))], [(1.46, (21.4, 0.9, 0.5)), (7.60, (21.2, 0.9, 0.55))], 32)
A1.teo = 'game_getup'; A1.t_up = 2.56; A1.t_walk = 3.26; A1.t_real = 4.48; A1.hud = (1.50, 99, 'game_getup')
A1.car = (17.2, 1.75, 0.0); A1.push = (4.48,)
A1.labels = [('real', 'NA VIDA REAL', RED, 0.2, 4.50, 99, lambda T: (21.6, 0.9, 1.05))]
TR2 = S('TR2', 7.60, 9.90, 'trailer', 'o GTA 6 chega agora (trailer: data de lançamento)'); TR2.src = 81.00
B1 = S('B1', 9.90, 14.50, 'rua', 'então vamos testar: e se a vida real seguisse as regras do jogo?')
B1.cam = cam([(9.90, (23.6, -1.2, 1.5)), (14.50, (22.2, 0.6, 1.35))], [(9.90, (21.0, 4.7, 1.1)), (14.50, (21.0, 4.7, 1.15))], 32)
B1.teo = 'think'; B1.t_pose = 10.1; B1.hud = (9.95, 99, 'full'); B1.push = (13.16,)
B1.labels = [('teste', 'TESTE: VIDA REAL', YEL, 0.24, 11.0, 99, lambda T: (21.0, 4.5, 2.25))]
# ================================================================= TESTE 1: ATROPELAMENTO
C1 = S('C1', 14.50, 20.30, 'estudio', 'a quarenta por hora, um em cada dez pedestres morre')
C1.cam = cam([(14.50, (2.8, -7.2, 1.6)), (20.30, (1.8, -5.6, 1.3))], [(14.50, (-1.0, 0.0, 0.8)), (20.30, (-0.5, 0.0, 0.8))], 30)
C1.dummy = True; C1.drive = (16.0, 19.46, 40); C1.flash = 19.46
C1.panel = ('risco', 16.60, 99, 40, 17.82, 1)
C2 = S('C2', 20.30, 22.40, 'estudio', 'a setenta, metade')
C2.cam = cam([(20.30, (-3.2, -4.6, 0.9)), (22.40, (-2.4, -4.0, 0.85))], [(20.30, (0.0, 0.0, 0.8)), (22.40, (0.0, 0.0, 0.8))], 28)
C2.dummy = True; C2.drive = (20.35, 22.05, 70); C2.flash = 22.05
C2.panel = ('risco', 20.32, 99, 70, 21.48, 5)
TR3 = S('TR3', 22.40, 24.00, 'trailer', 'agora a queda (trailer: salto de moto)'); TR3.src = 48.05
# ================================================================= TESTE 2: QUEDA
D1 = S('D1', 24.00, 27.60, 'rua', 'cair de uns quatro andares mata cerca de metade das pessoas')
D1.cam = cam([(24.00, (19.4, -2.4, 1.4)), (27.60, (19.8, -3.6, 2.2))], [(24.00, (21.0, BLD_Y0, 3.5)), (25.2, (21.0, BLD_Y0, 12.4)), (27.60, (21.0, BLD_Y0, 11.6))], 22)
D1.dummy_roof = True; D1.floors = (24.3, 24.52)
D1.panel = ('queda', 25.30, 99, 26.18)
# ================================================================= TESTE 3: CURA
D2 = S('D2', 27.60, 31.50, 'rua', 'e se você sobreviver, nenhum cachorro-quente resolve')
D2.cam = cam([(27.60, (19.2, 2.6, 1.25)), (31.50, (18.6, 3.4, 1.15))], [(27.60, (17.2, 5.4, 1.0)), (31.50, (17.2, 5.4, 1.0))], 30)
D2.teo = 'eat'; D2.cafe = True; D2.hud = (27.65, 99, 'eat'); D2.t_eat = 29.64; D2.push = (30.44,)
D3 = S('D3', 31.50, 36.40, 'rua', 'um osso quebrado leva, em média, de seis a oito semanas para colar')
D3.cam = cam([(31.50, (16.1, 3.5, 1.05)), (36.40, (16.6, 3.0, 1.1))], [(31.50, (17.2, 5.4, 0.85)), (36.40, (17.2, 5.4, 0.9))], 35)
D3.teo = 'sad'; D3.cafe = True; D3.t_pose = 31.6
D3.panel = ('semanas', 31.60, 99, (33.88, 34.60))
# ================================================================= VIRADA
E1 = S('E1', 36.40, 43.30, 'estudio', 'uma artista e dois especialistas em trauma criaram o corpo feito para aguentar um acidente')
E1.cam = cam([(36.40, (0.0, -7.5, 1.6)), (43.30, (0.0, -5.2, 1.3))], [(36.40, (0.0, 0.0, 1.2)), (43.30, (0.0, 0.0, 1.0))], 32)
E1.armored = 'silhouette'; E1.t_light = 41.9
E1.panel = ('equipe', 36.60, 42.6, (36.90, 37.68, 38.30))
E2 = S('E2', 43.30, 51.80, 'estudio', 'Graham: crânio gigante, sem pescoço, bolsas de ar; é assim que a gente precisaria ser')
E2.cam = cam([(43.30, (1.0, -3.6, 1.35)), (48.6, (0.6, -3.0, 1.3)), (51.80, (0.9, -5.6, 1.3))], [(43.30, (0.0, 0.0, 1.15)), (48.6, (0.0, 0.0, 1.2)), (51.80, (0.5, 0.0, 1.0))], 32)
E2.armored = 'lit'; E2.compare = 49.2; E2.push = (45.08,)
E2.labels = [('cranio', 'crânio gigante', YEL, 0.15, 45.08, 99, lambda T: (0.0, -0.2, 2.05)),
             ('pescoco', 'sem pescoço', YEL, 0.15, 46.12, 99, lambda T: (0.38, -0.35, 1.6)),
             ('bolsas', 'bolsas de ar no peito', YEL, 0.15, 47.18, 99, lambda T: (0.0, -0.4, 0.78))]
TR4 = S('TR4', 51.80, 54.40, 'trailer', 'quando o jogo mandar você levantar (trailer: queda de prédio)'); TR4.src = 67.90
# ================================================================= FINAL EM LOOP
F1 = S('F1', 54.40, 58.90, 'rua', 'aqui fora não tem botão de tentar de novo')
F1.cam = cam([(54.40, (22.6, 0.4, 1.3)), (58.90, (22.0, 1.4, 1.25))], [(54.40, (21.0, 4.7, 1.25)), (58.90, (21.0, 4.7, 1.2))], 30)
F1.teo = 'stand'; F1.button = (54.50, 56.08)
H1 = S('H1', 58.90, END, 'rua', 'comenta qual missão você quer ver testada na vida real')
H1.cam = cam([(58.90, (22.0, 1.4, 1.25)), (END, (23.2, -1.8, 1.7))], [(58.90, (21.0, 4.7, 1.2)), (END, (21.0, 4.7, 1.3))], 32)
H1.teo = 'wave'; H1.t_pose = 59.0; H1.dim = 0.35
H1.panel = ('cta', 58.95, 99, 60.50)

NOTES = {}   # notas na tela ficam no captions_cfg.py

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
