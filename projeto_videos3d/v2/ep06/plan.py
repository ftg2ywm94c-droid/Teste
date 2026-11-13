"""Planos do vídeo 06 (e se começasse um apocalipse zumbi no Brasil?). T = tempo da narração (s), amarrado a analysis/narracao/06_words.json.
Ritmo dos vídeos 04/05: cortes nas batidas das frases + câmera sempre em movimento; nenhum trecho > 3 s sem novidade.
Tipos de cenário: cidade (rua abandonada ao entardecer), rua (dia), mata (escala de formiga, cm), globo, lab, virus."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 74.25           # narração termina em 74,08 s

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []; self.panel = None
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def add(a, b, k=1.0): return tuple(x + k * y for x, y in zip(a, b))
def _front(c, d, up):
    p, l = c['pos'], c['look']; v = [b - a for a, b in zip(p, l)]; n = math.sqrt(sum(x * x for x in v))
    return (p[0] + v[0] / n * d, p[1] + v[1] / n * d, p[2] + v[2] / n * d + up)
def anchor(shot, d, up, T=None):
    p = _front(shot.cam(shot.t0 if T is None else T), d, up); return lambda T_: p
def follow(shot, d, up): return lambda T: _front(shot.cam(T), d, up)
def eased(knots):
    f = ease(knots); a, b = knots[0][0], knots[-1][0]
    return lambda T: f(min(max(T, a), b))
def cam(pos_knots, look_knots, lens=35, lens_knots=None):
    P, L = eased(pos_knots), eased(look_knots)
    LN = eased([(t, (v,)) for t, v in lens_knots]) if lens_knots else None
    return lambda T: dict(pos=P(T), look=L(T), lens=LN(T)[0] if LN else lens)

YEL, RED, WHITE, BLUE, GREEN, CYAN = (1.0, 0.80, 0.08), (1.0, 0.22, 0.14), (0.97, 0.97, 0.97), (0.45, 0.72, 1.0), (0.35, 0.95, 0.45), (0.35, 0.95, 1.0)
SHOTS = []
def S(*a):
    s = Shot(*a); SHOTS.append(s); return s

TEO = (20.5, 4.7, 0.15); HEAD = (20.5, 4.7, 1.72)
T_FOGO = 99.0                 # a rua deste vídeo não apaga o fogo
# mata (cm): folha principal sai do caule em z = 9, para +X, inclinada 12° para cima
LEAF_Z = 9.0; LEAF_TILT = math.radians(12)
def leaf_pt(x, below=0.0): return (x, 0.0, LEAF_Z + x * math.tan(LEAF_TILT) - below)
BITE = leaf_pt(2.6, 0.13)      # formiga presa embaixo da folha
T_SOBE = 18.04; T_MORDE = 19.40; T_MORRE = 20.46; T_CRESCE = 23.34; T_ESPORO = 24.36

# ================================================================= GANCHO
A1 = S('A1', 0.00, 1.44, 'cidade', 'cidade brasileira abandonada ao entardecer')
A1.cam = cam([(0.0, (17.0, -1.2, 0.5)), (1.44, (19.5, -0.9, 0.65))], [(0.0, (40.0, 0.5, 1.6)), (1.44, (40.0, 0.4, 1.7))], 28)
A2 = S('A2', 1.44, 2.62, 'cidade', 'zumbis estilizados vindo pela rua')
A2.cam = cam([(1.44, (24.0, -3.4, 1.2)), (2.62, (25.2, -3.0, 1.3))], [(1.44, (34.0, 0.0, 1.3)), (2.62, (34.0, 0.0, 1.35))], 40)
A2.labels = [('zumbi', 'apocalipse zumbi', RED, 0.5, 1.75, 99, lambda T: (33.0, -0.5, 2.9))]
A3 = S('A3', 2.62, 4.18, 'cidade', 'no Brasil? Téo vê')
A3.cam = cam([(2.62, (18.6, 1.6, 1.5)), (4.18, (19.4, 2.4, 1.6))], [(2.62, (20.5, 4.7, 1.45)), (4.18, (20.5, 4.7, 1.55))], 35)
A3.teo = 'alarm'
A3.labels = [('br', 'no Brasil?', YEL, 0.16, 2.70, 99, lambda T: (20.5, 4.4, 2.22))]
A4 = S('A4', 4.18, 6.16, 'cidade', 'antes de correr, uma notícia')
A4.cam = cam([(4.18, (14.0, -2.0, 1.6)), (6.16, (16.0, -1.0, 2.2))], [(4.18, (21.0, 4.7, 1.2)), (6.16, (21.0, 4.7, 1.2))], 28)
A4.teo = 'alarm'
A4.labels = [('noticia', 'uma notícia', WHITE, 0.4, 5.20, 99, lambda T: (20.5, 4.0, 2.7))]
A5 = S('A5', 6.16, 8.40, 'mata', 'o fungo zumbi existe')
A5.cam = cam([(6.16, (1.0, -5.5, 7.6)), (8.4, (3.4, -4.2, 7.9))], [(6.16, (2.6, 0, 8.9)), (8.4, (2.6, 0, 9.0))], 50)
A5.ant = 'dead'; A5.stroma = 0.0
A5.labels = [('existe', 'o fungo zumbi existe', YEL, 0.16, 6.72, 99, follow(A5, 3.0, 0.75))]
def _ll(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return (r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la))
ZM = (-21.0, -42.6)
A6 = S('A6', 8.40, 10.16, 'globo', 'e foi achado aqui')
A6.cam = cam([(8.4, add(_ll(-10, -20, 40.0), (0, 0, 0))), (10.16, _ll(-17, -36, 24.0))], [(8.4, (0, 0, 0)), (10.16, _ll(*ZM, 5.0))], 35)
A6.pin_on = 8.98
A6.labels = [('aqui', 'aqui', RED, 1.0, 8.98, 99, lambda T: add(_ll(*ZM, 11.4), (0, 0, 1.4)))]
B1 = S('B1', 10.16, 12.38, 'globo', 'Mata Atlântica de Minas Gerais')
B1.cam = cam([(10.16, _ll(-17, -36, 24.0)), (12.38, _ll(-19, -40, 17.0))], [(10.16, _ll(*ZM, 5.0)), (12.38, _ll(*ZM, 7.5))], 35)
B1.pin_on = 0.0
B1.labels = [('mata', 'Mata Atlântica · MG', GREEN, 0.5, 10.62, 99, lambda T: add(_ll(*ZM, 11.2), (0, 0, 1.0)))]

# ================================================================= CONTEXTO (mata)
B2 = S('B2', 12.38, 15.00, 'mata', 'quatro espécies de fungo, cada uma numa formiga')
B2.cam = cam([(12.38, (2.4, -11.0, 7.0)), (15.0, (2.8, -8.5, 7.4))], [(12.38, (2.8, 0, 9.4)), (15.0, (2.9, 0, 9.4))], 35)
B2.four = True
B2.labels = [('4esp', '4 espécies', YEL, 0.3, 13.50, 99, follow(B2, 5.0, 1.0))]
B3 = S('B3', 15.00, 16.98, 'mata', 'que controlam formigas')
B3.cam = cam([(15.0, (1.4, -3.4, 2.2)), (16.98, (1.0, -3.0, 3.4))], [(15.0, (0.0, 0, 2.0)), (16.98, (0.0, 0, 3.2))], 40)
B3.ant = 'climb'
B3.labels = [('controla', 'controla a formiga', RED, 0.11, 15.28, 99, follow(B3, 2.2, 0.55))]
B4 = S('B4', 16.98, 19.40, 'mata', 'a formiga infectada sobe numa planta')
B4.cam = cam([(16.98, (2.2, -4.0, 4.5)), (19.4, (2.2, -4.4, 8.4))], [(16.98, (0.0, 0, 4.6)), (19.4, (0.8, 0, 8.6))], 38)
B4.ant = 'climb'
B4.labels = [('sobe', 'sobe', WHITE, 0.18, 18.04, 99, follow(B4, 3.0, 0.7))]
B5 = S('B5', 19.40, 21.82, 'mata', 'morde uma folha e morre ali')
B5.cam = cam([(19.4, (2.2, -3.4, 8.45)), (21.82, (2.6, -3.0, 8.55))], [(19.4, BITE), (21.82, BITE)], 60)
B5.ant = 'bite'
B5.labels = [('morde', 'mordida da morte', RED, 0.07, 19.60, 99, follow(B5, 1.6, -0.35))]
B6 = S('B6', 21.82, 25.52, 'mata', 'do corpo dela, o fungo cresce e solta esporos')
B6.cam = cam([(21.82, (3.8, -2.6, 8.3)), (25.52, (3.6, -3.4, 8.4))], [(21.82, add(BITE, (0, 0, -0.3))), (25.52, add(BITE, (0, 0, -0.5)))], 40)
B6.ant = 'dead'; B6.stroma = T_CRESCE; B6.spore_t = T_ESPORO
B6.labels = [('esporos', 'esporos', WHITE, 0.11, T_ESPORO, 99, follow(B6, 2.2, -0.5))]

# ================================================================= DESENVOLVIMENTO
C1 = S('C1', 25.52, 27.94, 'rua', 'mas em gente ele não pega')
C1.cam = cam([(25.52, (18.8, 1.2, 1.5)), (27.94, (19.9, 2.6, 1.6))], [(25.52, (20.5, 4.7, 1.35)), (27.94, (20.5, 4.7, 1.5))], 35)
C1.teo = 'relief'
C1.labels = [('gente', 'em gente: não pega', GREEN, 0.14, 26.58, 99, lambda T: (20.5, 4.4, 2.22))]
C2 = S('C2', 27.94, 31.30, 'lab', 'quase todo fungo cresce mal acima de 30 °C')
C2.cam = cam([(27.94, (2.6, -9.0, 4.4)), (31.3, (1.8, -8.0, 3.8))], [(27.94, (0, 0, 3.4)), (31.3, (0, 0, 3.2))], 40)
C2.temp = lambda T: 20 + 10 * sstep(28.6, 30.3, T)
C2.panel = ('curve', 28.10, 99, (28.3, 30.3))
C3 = S('C3', 31.30, 33.96, 'lab', 'e o nosso corpo fica em 37')
C3.cam = cam([(31.3, (1.6, -6.0, 4.4)), (33.96, (1.0, -4.6, 5.4))], [(31.3, (0, 0, 4.4)), (33.96, (0, 0, 5.2))], 40)
C3.temp = lambda T: 30 + 7 * sstep(31.5, 32.5, T)
C3.labels = [('37', '37 °C', RED, 0.4, 32.48, 99, lambda T: (1.0, 0.0, 5.0))]
C4 = S('C4', 33.96, 36.38, 'rua', 'o calor do corpo é um escudo')
C4.cam = cam([(33.96, (17.8, 0.6, 1.6)), (36.38, (19.0, 1.4, 1.7))], [(33.96, (20.5, 4.7, 1.2)), (36.38, (20.5, 4.7, 1.25))], 32)
C4.teo = 'relief'; C4.shield = 34.1
C4.labels = [('escudo', 'escudo: 37 °C', CYAN, 0.16, 35.20, 99, lambda T: (20.5, 4.0, 2.45))]
D1 = S('D1', 36.38, 40.30, 'virus', 'e o vírus? a raiva é o mais perto disso')
D1.cam = cam([(36.38, (3.0, -16.0, 2.0)), (40.3, (1.0, -6.5, 0.6))], [(36.38, (0, 0, 0)), (40.3, (0, 0, 0))], 32)
D1.labels = [('virus', 'vírus da raiva', RED, 0.4, 38.16, 99, follow(D1, 4.0, 1.1)),
             ('bala', 'forma de bala (real)', WHITE, 0.2, 39.0, 99, follow(D1, 4.0, -0.9))]
D2 = S('D2', 40.30, 43.92, 'cidade', 'passa pela mordida e pode deixar o animal agressivo')
D2.cam = cam([(40.3, (16.6, 1.6, 0.6)), (43.92, (17.6, 2.4, 0.75))], [(40.3, (18.5, 4.6, 0.55)), (43.92, (18.5, 4.6, 0.6))], 32)
D2.dog = ('growl', (18.5, 4.6, 0.15)); D2.bat = True
D2.labels = [('mordida', 'mordida', WHITE, 0.14, 40.76, 99, lambda T: (18.5, 4.4, 1.25)),
             ('agress', 'agressivo', RED, 0.14, 42.54, 99, lambda T: (18.5, 4.4, 1.06))]
D3 = S('D3', 43.92, 47.82, 'cidade', 'leva semanas para agir, não segundos')
D3.cam = cam([(43.92, (14.5, -3.0, 2.0)), (47.82, (16.5, -1.5, 1.6))], [(43.92, (20.0, 4.7, 1.2)), (47.82, (19.5, 4.7, 1.0))], 28)
D3.dog = ('idle', (18.5, 4.6, 0.15)); D3.panel = ('cal', 44.20, 99, (44.4, 45.7))
D3.labels = [('naoseg', 'não segundos', RED, 0.4, 45.84, 99, lambda T: (19.5, 4.0, 2.8))]

# ================================================================= CTA
E1 = S('E1', 47.82, 50.44, 'rua', 'CTA: Téo acena')
E1.cam = cam([(47.82, (17.5, 0.8, 1.4)), (50.44, (22.8, 1.2, 1.5))], [(47.82, (20.5, 4.7, 1.25)), (50.44, (20.5, 4.7, 1.3))], 30)
E1.teo = 'wave'
E1.labels = [('prox', 'próximo: e se…?', YEL, 0.3, 48.16, 99, lambda T: (20.5, 4.4, 2.35))]

# ================================================================= REVELAÇÃO (modelo matemático)
F1 = S('F1', 50.44, 53.12, 'cidade', 'e se mesmo assim acontecesse?')
F1.cam = cam([(50.44, (22.0, -5.0, 1.0)), (53.12, (23.5, -4.0, 1.1))], [(50.44, (34.0, 0.0, 1.4)), (53.12, (33.0, 0.0, 1.4))], 32)
F1.labels = [('assim', 'e se acontecesse?', YEL, 0.45, 51.32, 99, lambda T: (32.0, 0.0, 3.0))]
F2 = S('F2', 53.12, 56.08, 'cidade', 'matemáticos já simularam um surto')
F2.cam = cam([(53.12, (10.0, -8.0, 4.0)), (56.08, (12.0, -9.0, 5.0))], [(53.12, (30.0, 2.0, 1.0)), (56.08, (30.0, 2.0, 1.0))], 26)
F2.panel = ('sir', 53.20, 99, 'esperar', (53.4, 56.0))
F3 = S('F3', 56.08, 59.80, 'cidade', 'esperar é o pior plano')
F3.cam = cam([(56.08, (12.0, -9.0, 5.0)), (59.8, (14.0, -10.0, 6.0))], [(56.08, (30.0, 2.0, 1.0)), (59.8, (30.0, 2.0, 1.0))], 26)
F3.panel = ('sir', 0.0, 99, 'esperar', (53.4, 56.0)); F3.sir_tag = ('esperar: humanos somem', RED, 57.08)
F4 = S('F4', 59.80, 63.82, 'cidade', 'só agir rápido, várias vezes, segura o surto')
F4.cam = cam([(59.8, (14.0, -10.0, 6.0)), (63.82, (16.0, -11.0, 7.0))], [(59.8, (30.0, 2.0, 1.0)), (63.82, (30.0, 2.0, 1.0))], 26)
F4.panel = ('sir', 0.0, 99, 'agir', (59.9, 62.3)); F4.sir_tag = ('agir rápido, várias vezes', GREEN, 59.96)

# ================================================================= FINAL
G1 = S('G1', 63.82, 68.30, 'mata', 'o fungo zumbi existe, mas só para formigas')
G1.cam = cam([(63.82, (3.4, -3.0, 8.4)), (68.3, (5.0, -12.0, 7.0))], [(63.82, add(BITE, (0, 0, -0.4))), (68.3, (2.4, 0, 8.6))], 40)
G1.ant = 'dead'; G1.stroma = 0.0
G1.labels = [('soform', 'só para formigas', YEL, 0.3, 66.90, 99, follow(G1, 5.0, 1.1))]
G2 = S('G2', 68.30, 71.56, 'rua', 'para nós, o perigo real é a raiva')
G2.cam = cam([(68.3, (17.6, 1.0, 1.2)), (71.56, (18.6, 1.6, 1.3))], [(68.3, (19.8, 4.7, 0.9)), (71.56, (19.8, 4.7, 0.95))], 30)
G2.teo = 'idle'; G2.dog = ('idle', (19.2, 4.4, 0.15), True)
G2.labels = [('raiva', 'raiva', RED, 0.2, 70.84, 99, lambda T: (19.6, 4.2, 2.1))]
G3 = S('G3', 71.56, 74.25, 'rua', 'que ainda passa por morcegos e cães sem vacina')
G3.cam = cam([(71.56, (16.0, -0.5, 1.0)), (74.25, (15.0, -3.0, 3.4))], [(71.56, (19.2, 4.4, 0.7)), (74.25, (19.5, 4.6, 1.2))], 30)
G3.teo = 'idle'; G3.dog = ('idle', (19.2, 4.4, 0.15), True); G3.bat = True
G3.labels = [('morcego', 'morcegos', WHITE, 0.25, 72.42, 99, lambda T: (17.6, 4.0, 2.6)),
             ('vacina', 'vacine seu pet', GREEN, 0.3, 73.50, 99, lambda T: (19.2, 4.2, 1.6))]

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
