"""Planos do vídeo 10 (e se o Brasil cobrasse menos impostos?). T = tempo da narração (s), amarrado a analysis/narracao/10_words.json
(narração já com o corte do "EUA" mal pronunciado).
Estilo: 3D (palco escuro, câmera com movimentos precisos de "motion control") + camada de motion graphics (v2/ep10/mograph.py).
Cada plano tem `set` (o que o 3D monta) e `mg` (elementos gráficos: tempo, posição em 1080x1920 ou âncora 3D)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 64.42           # narração termina em 64,42 s

class Shot:
    def __init__(self, name, t0, t1, set_, desc):
        self.name, self.t0, self.t1, self.set, self.desc = name, t0, t1, set_, desc
        self.kind = 'estudio'; self.labels = []; self.panel = None; self.mg = []
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def eased(knots):
    f = ease(knots); a, b = knots[0][0], knots[-1][0]
    return lambda T: f(min(max(T, a), b))
def cam(pos_knots, look_knots, lens=35):
    P, L = eased(pos_knots), eased(look_knots)
    if isinstance(lens, (int, float)): return lambda T: dict(pos=P(T), look=L(T), lens=lens)
    Lf = eased([(t, (v, 0, 0)) for t, v in lens])
    return lambda T: dict(pos=P(T), look=L(T), lens=Lf(T)[0])

YEL, RED, WHITE, TEAL, GREEN, GREY = (255, 204, 20), (240, 58, 42), (250, 250, 250), (40, 190, 200), (80, 220, 110), (160, 166, 178)
SHOTS = []
def S(*a):
    s = Shot(*a); SHOTS.append(s); return s

# posições fixas
TEO_A = (-0.85, -0.1, 0.0); COFRE = (0.95, 0.55, 0.0); CAL = (0.05, 2.3, 0.0)
POOR, RICH = (-1.95, -0.25, 0.0), (1.95, -0.25, 0.0)

# ================================================================= GANCHO
A1 = S('A1', 0.00, 4.90, 'cofre', 'todo ano você trabalha uns cinco meses só para pagar imposto')
A1.cam = cam([(0.0, (-0.55, -1.7, 1.05)), (1.6, (-0.2, -3.0, 1.25)), (4.90, (0.35, -5.4, 1.85))],
             [(0.0, (-0.65, 0.0, 1.0)), (1.6, (0.0, 0.6, 1.25)), (4.90, (0.1, 1.2, 1.55))], [(0.0, 30), (4.9, 28)])
A1.teo = 'give'; A1.coins = ('in', 0.55, 4.7); A1.pages = (1.70, 2.22, 2.74, 3.30, 3.86); A1.push = (1.62, 3.74)
A1.mg = [('title', '5', 1.62, 99, (540, 330), 260, YEL, 'slam'), ('title', 'MESES', 2.12, 99, (540, 520), 120, WHITE, 'slam'),
         ('counter', '{:.0f} dias de trabalho por ano', 0, 149, 2.75, 4.2, (540, 640), 44, WHITE, 2.7, 99)]
A2 = S('A2', 4.90, 6.85, 'cofre', 'e se o Brasil cobrasse menos?')
A2.cam = cam([(4.90, (2.2, -2.1, 0.45)), (6.85, (-1.0, -2.9, 0.75))], [(4.90, (0.4, 0.5, 1.3)), (6.85, (0.0, 0.5, 1.35))], 24)
A2.teo = 'look'; A2.coins = ('out', 5.44, 6.8); A2.pages_done = True
A2.mg = [('slider', 'IMPOSTO', 1.0, 0.45, 5.44, 6.25, (540, 420), 5.0, 99)]
A3 = S('A3', 6.85, 9.75, 'cadeado', 'tem um detalhe que muda tudo')
A3.cam = cam([(6.85, (0.0, -3.4, 1.2)), (9.75, (0.0, -2.6, 1.05))], [(6.85, (0.0, 0.0, 0.95)), (9.75, (0.0, 0.0, 0.95))], [(6.85, 26), (7.35, 26), (7.55, 46), (9.75, 52)])
A3.shake = 8.16; A3.whip = True
A3.mg = [('ring', 'lock', 260, 7.42, 99, YEL)]
# ================================================================= DEGRAU 1: TAMANHO
B1 = S('B1', 9.75, 15.75, 'pib', 'o Brasil arrecada quase um terço de tudo que produz: a maior carga da América Latina')
B1.cam = cam([(9.75, (0.0, -2.2, 3.4)), (12.9, (0.2, -2.9, 2.4)), (13.6, (3.0, -4.6, 1.3)), (15.75, (3.5, -4.2, 1.2))],
             [(9.75, (0.0, 0.0, 0.1)), (12.9, (0.0, 0.0, 0.25)), (13.6, (3.4, 0.0, 1.25)), (15.75, (3.4, 0.0, 1.2))], 30)
B1.slice = 11.30; B1.bars = (13.70, 14.60); B1.push = (11.46,)
B1.mg = [('title', '1/3', 11.46, 13.4, (540, 330), 230, YEL, 'slam'), ('title', 'DE TUDO QUE O PAÍS PRODUZ', 11.9, 13.4, (540, 500), 52, WHITE, 'pop'),
         ('title', '32% do PIB', 12.5, 13.4, (540, 590), 46, YEL, 'pop'),
         ('atag', 'BRASIL  32%', 'bar_br', 13.75, 99, 50, YEL), ('atag', 'MÉDIA DA AMÉRICA LATINA  21%', 'bar_al', 14.65, 99, 38, WHITE),
         ('title', 'A MAIOR CARGA DA REGIÃO', 14.0, 99, (540, 250), 58, YEL, 'pop')]
B2 = S('B2', 15.75, 20.40, 'preco', 'e mais de quarenta por cento vem escondido no preço do que você compra')
B2.cam = cam([(15.75, (1.3, -3.2, 1.7)), (17.7, (0.55, -2.0, 1.35)), (20.40, (0.2, -1.55, 1.3))],
             [(15.75, (0.0, 0.2, 1.05)), (17.7, (0.0, -0.3, 1.25)), (20.40, (0.0, -0.3, 1.25))], 32)
B2.split = 17.86; B2.push = (16.60,)
B2.mg = [('counter', '{:.0f}%', 0, 43, 16.6, 17.3, (540, 330), 230, YEL, 16.6, 99),
         ('title', 'DA ARRECADAÇÃO VEM DE IMPOSTO NO CONSUMO', 17.0, 99, (540, 500), 38, WHITE, 'pop'),
         ('atag', 'PRODUTO', 'tag_a', 18.1, 99, 40, WHITE), ('atag', 'IMPOSTO', 'tag_b', 18.3, 99, 40, RED)]
# ================================================================= DEGRAU 2: CORTAR FUNCIONA, MAS ALGUÉM PAGA
C1 = S('C1', 20.40, 24.40, 'bomba', 'em 2022, o país cortou o ICMS da gasolina')
C1.cam = cam([(20.40, (2.4, -2.5, 1.7)), (24.40, (-1.5, -2.9, 1.25))], [(20.40, (0.0, 0.2, 1.15)), (24.40, (0.2, 0.2, 1.2))], 30)
C1.snips = (22.56, 23.95); C1.scissors = (21.9, 99)
C1.mg = [('title', '2022', 20.8, 99, (540, 320), 200, YEL, 'slam'), ('badge', 'ICMS', 23.66, 99, (540, 520), 64, RED, 23.95)]
C2 = S('C2', 24.40, 28.40, 'bomba', 'e o preço caiu quase nove por cento em uma semana')
C2.cam = cam([(24.40, (0.6, -2.1, 1.45)), (28.40, (0.12, -1.35, 1.3))], [(24.40, (0.0, -0.2, 1.3)), (28.40, (0.0, -0.3, 1.28))], 32)
C2.push = (26.76,)
C2.mg = [('price', 'visor', 7.13, 6.49, 26.0, 27.0, 24.45, 99), ('badge', '−8,9% EM 1 SEMANA', 26.76, 99, (540, 330), 58, GREEN, None),
         ('title', 'preço médio da gasolina (ANP, julho/2022)', 24.6, 99, (540, 430), 32, GREY, 'pop')]
D1 = S('D1', 28.40, 34.40, 'rombo', 'só que a conta não some: os estados dizem que perderam mais de cem bilhões')
D1.cam = cam([(28.40, (2.6, -2.9, 0.55)), (34.40, (1.9, -2.0, 0.75))], [(28.40, (0.5, 0.3, 0.75)), (34.40, (0.7, 0.3, 0.6))], 26)
D1.drain = 30.0; D1.push = (30.06, 33.20)
D1.mg = [('atag', 'COFRE DOS ESTADOS', 'cofre_top', 31.2, 99, 42, WHITE),
         ('counter', '−R$ {:.0f} BI', 0, 100, 32.5, 33.5, (540, 340), 130, RED, 32.5, 99)]
E1 = S('E1', 34.40, 38.50, 'kansas', 'o Kansas cortou impostos prometendo crescimento')
E1.cam = cam([(34.40, (-2.8, -3.2, 1.0)), (38.50, (-0.6, -4.4, 1.6))], [(34.40, (-0.6, 0.0, 0.8)), (38.50, (0.4, 0.0, 1.0))], 28)
E1.snips = (35.6,); E1.scissors = (35.2, 36.6); E1.arrow_up = 37.3
E1.mg = [('badge', 'KANSAS (EUA)', 34.94, 99, (540, 300), 66, YEL, None), ('title', '2012', 35.5, 99, (540, 420), 90, WHITE, 'slam'),
         ('atag', 'CRESCIMENTO?', 'arrow_tip', 37.4, 99, 40, GREEN)]
E2 = S('E2', 38.50, 43.70, 'kansas', 'a arrecadação despencou, o crescimento não veio, e voltaram atrás')
E2.cam = cam([(38.50, (0.8, -4.0, 1.9)), (43.70, (1.6, -3.4, 1.3))], [(38.50, (0.3, 0.0, 0.7)), (43.70, (0.4, 0.0, 0.8))], 28)
E2.drop = 39.46; E2.droop = 41.18; E2.rewind = 42.2; E2.push = (39.46,)
E2.mg = [('atag', 'ARRECADAÇÃO', 'bars_top', 38.76, 42.05, 44, WHITE), ('darrow', 39.6, 42.1, (880, 600), RED),
         ('rewind', 42.2, 99, (540, 300)), ('title', '2017: VOLTARAM ATRÁS', 42.5, 99, (540, 480), 52, YEL, 'pop')]
# ================================================================= VIRADA: DE QUEM
F1 = S('F1', 43.70, 48.70, 'balanca', 'agora o detalhe: um pacote de café paga o mesmo imposto')
F1.cam = cam([(43.70, (0.0, -5.6, 2.6)), (48.70, (0.0, -6.6, 1.9))], [(43.70, (0.0, 0.3, 1.25)), (48.70, (0.0, 0.3, 1.2))], 20)
F1.packets = 45.44; F1.push = (43.86, 47.30); F1.tilt = None
F1.mg = [('atag', 'MESMO IMPOSTO', 'pan_l', 47.35, 99, 38, RED), ('atag', 'MESMO IMPOSTO', 'pan_r', 47.45, 99, 38, RED), ('title', '=', 47.5, 99, (540, 760), 140, WHITE, 'slam')]
F2 = S('F2', 48.70, 53.40, 'balanca', 'para quem ganha mil ou cem mil; para quem ganha pouco, pesa muito mais')
F2.cam = cam([(48.70, (0.0, -6.6, 1.9)), (53.40, (-0.9, -5.6, 1.45))], [(48.70, (0.0, 0.3, 1.2)), (53.40, (-0.4, 0.3, 1.0))], 20)
F2.packets = 0.0; F2.tilt = 52.02; F2.push = (52.02,)
F2.mg = [('atag', 'GANHA R$ 1 MIL', 'head_l', 48.78, 99, 36, WHITE), ('atag', 'GANHA R$ 100 MIL', 'head_r', 49.56, 99, 36, WHITE),
         ('share', 52.1, 99)]
G1 = S('G1', 53.40, 56.66, 'balanca', 'a pergunta não é só quanto cobrar; é de quem')
G1.cam = cam([(53.40, (-2.6, -4.4, 1.0)), (56.66, (2.4, -4.6, 1.1))], [(53.40, (0.0, 0.3, 1.3)), (56.66, (0.0, 0.3, 1.3))], 26)
G1.tilt = 0.0; G1.packets = 0.0; G1.dim = 0.55
G1.mg = [('quem', 54.8, 55.6, 56.08)]
# ================================================================= FINAL EM LOOP
G2 = S('G2', 56.66, 61.55, 'cafe', 'no próximo café, lembra: até o fim de maio, ele não é seu')
G2.cam = cam([(56.66, (0.5, -1.6, 1.45)), (59.3, (0.6, -2.6, 1.5)), (61.55, (0.2, -3.6, 1.7))],
             [(56.66, (-0.1, 0.0, 1.25)), (59.3, (0.1, 0.8, 1.35)), (61.55, (0.2, 1.0, 1.45))], 30)
G2.teo = 'cup'; G2.cal_on = 59.42; G2.burst = 60.5; G2.push = (59.42,)
G2.mg = [('ring', 'cal', 240, 59.6, 99, RED)]
H1 = S('H1', 61.55, END, 'tesoura', 'comenta qual imposto você cortaria primeiro')
H1.cam = cam([(61.55, (0.3, -3.1, 1.3)), (END, (0.0, -3.6, 1.35))], [(61.55, (0.0, 0.0, 1.1)), (END, (0.0, 0.0, 1.15))], 30)
H1.teo = 'scissors'; H1.snips = (63.36,)
H1.mg = [('chips', ['ICMS', 'IR', 'IPI', 'ISS', 'IOF'], 62.0, 0.22, 390), ('title', 'QUAL VOCÊ CORTARIA?', 61.95, 99, (540, 260), 62, YEL, 'pop')]

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
