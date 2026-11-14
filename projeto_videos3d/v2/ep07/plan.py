"""Planos do vídeo 07 (e se um furacão chegasse na Avenida Paulista?). T = tempo da narração (s), amarrado a analysis/narracao/07_words.json.
Ritmo: cortes nas batidas das frases + câmera sempre em movimento; nenhum trecho > 3 s sem novidade.
Tipos de cenário: paulista (avenida sob tempestade), globo (Terra com furacão), relevo (corte mar → serra → planalto), rua (bairro do Téo com vento)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 63.75           # narração termina em 63,71 s

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
def _ll(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return (r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la))

YEL, RED, WHITE, BLUE, GREEN, CYAN = (1.0, 0.80, 0.08), (1.0, 0.22, 0.14), (0.97, 0.97, 0.97), (0.45, 0.72, 1.0), (0.35, 0.95, 0.45), (0.35, 0.95, 1.0)
SHOTS = []
def S(*a):
    s = Shot(*a); SHOTS.append(s); return s

TEO = (13.0, -14.6, 0.2); TREE = (28.0, -14.4, 0.2)
HUR_SP = (-26.6, -43.6)                  # furacão hipotético ao largo de SP (ilustração)
CAT = (-28.6, -48.4)                     # Catarina, 2004, litoral sul de SC
T_ARVORE = 15.25; T_APAGA = 18.70

# ================================================================= CHOQUE
A1 = S('A1', 0.00, 2.96, 'paulista', 'vento de 250 km/h')
A1.cam = cam([(0.0, (-12.0, -6.0, 1.1)), (2.96, (4.0, -5.5, 1.6))], [(0.0, (70.0, 1.0, 8.0)), (2.96, (70.0, 0.5, 9.0))], 24)
A1.wind = 1.0; A1.rain = 1.0; A1.debris = 1.2; A1.shake = 0.6
A1.panel = ('speed', 0.30, 99, (0.72, 2.74), 'up')
A2 = S('A2', 2.96, 4.68, 'paulista', 'na Avenida Paulista')
A2.cam = cam([(2.96, (-70.0, -6.0, 95.0)), (4.68, (-55.0, -5.0, 88.0))], [(2.96, (120.0, 0.0, 0.0)), (4.68, (125.0, 0.0, 0.0))], 30)
A2.wind = 1.0; A2.rain = 0.8
A2.labels = [('paulista', 'Avenida Paulista', YEL, 2.0, 3.20, 99, follow(A2, 45.0, 8.0))]
A3 = S('A3', 4.68, 7.60, 'globo', 'é o que um furacão dos mais fortes traria')
A3.cam = cam([(4.68, _ll(-22, -38, 22.0)), (7.60, _ll(-27, -44, 14.5))], [(4.68, _ll(*HUR_SP, 8.0)), (7.60, _ll(*HUR_SP, 9.6))], 35)
A3.hur = HUR_SP; A3.hur_size = 0.13
A3.labels = [('cat5', 'categoria 5: 250+ km/h', RED, 0.14, 6.22, 99, follow(A3, 3.0, 0.75))]
A4 = S('A4', 7.60, 11.40, 'paulista', 'só que São Paulo tem uma defesa')
A4.cam = cam([(7.60, (11.4, -10.2, 1.2)), (11.40, (11.9, -10.8, 1.3))], [(7.60, (13.0, -14.6, 1.7)), (11.40, (13.0, -14.6, 1.8))], 32)
A4.teo = 'look_up'; A4.wind = 0.5; A4.rain = 1.0
A4.labels = [('defesa', 'a defesa de SP?', YEL, 0.16, 8.84, 99, lambda T: (13.0, -14.0, 2.3))]

# ================================================================= ESCALADA
B1 = S('B1', 11.40, 15.10, 'paulista', 'em 2023, um vento de pouco mais de cem por hora')
B1.cam = cam([(11.40, (18.0, -7.5, 2.2)), (15.10, (28.0, -6.0, 2.6))], [(11.40, (80.0, 2.0, 10.0)), (15.10, (85.0, 3.0, 9.0))], 26)
B1.wind = 0.5; B1.rain = 0.7
B1.labels = [('ano', '2023', WHITE, 0.9, 11.62, 99, follow(B1, 16.0, 3.4)),
             ('v104', 'rajada de 104 km/h', YEL, 0.7, 14.34, 99, follow(B1, 16.0, 1.9))]
B2 = S('B2', 15.10, 17.10, 'paulista', 'derrubou centenas de árvores')
B2.cam = cam([(15.10, (20.5, -6.2, 1.3)), (17.10, (21.5, -5.8, 1.5))], [(15.10, (28.0, -11.5, 3.5)), (17.10, (28.0, -9.5, 1.5))], 30)
B2.wind = 0.6; B2.rain = 0.8; B2.tree = T_ARVORE; B2.shake = 0.3
B2.labels = [('arvores', 'centenas de árvores', WHITE, 0.42, 15.70, 99, follow(B2, 9.0, 2.0))]
B3 = S('B3', 17.10, 19.70, 'paulista', 'e deixou milhões de casas sem luz')
B3.cam = cam([(17.10, (-24.0, -3.0, 8.0)), (19.70, (-18.0, -3.5, 9.0))], [(17.10, (80.0, 14.0, 26.0)), (19.70, (80.0, 14.0, 25.0))], 30)
B3.wind = 0.4; B3.rain = 0.8; B3.blackout = T_APAGA; B3.tree_down = True
B3.labels = [('semluz', 'sem luz', RED, 1.4, 18.94, 99, follow(B3, 30.0, 4.0))]
C1 = S('C1', 19.70, 22.60, 'paulista', 'um furacão desses venta mais que o dobro')
C1.cam = cam([(19.70, (-6.0, 4.0, 3.0)), (22.60, (0.0, 3.0, 3.6))], [(19.70, (80.0, -4.0, 12.0)), (22.60, (80.0, -4.0, 12.0))], 28)
C1.wind = 0.8; C1.rain = 0.8; C1.lights_off = True
C1.panel = ('compare', 19.75, 99, (20.10, 21.80))
C2 = S('C2', 22.60, 25.90, 'paulista', 'e o dobro de vento empurra quatro vezes mais')
C2.cam = cam([(22.60, (30.0, 9.0, 2.0)), (25.90, (34.0, 8.0, 2.4))], [(22.60, (90.0, -6.0, 10.0)), (25.90, (90.0, -6.0, 9.0))], 28)
C2.wind = 1.0; C2.rain = 0.9; C2.lights_off = True; C2.debris = 23.0
C2.panel = ('forca', 22.62, 99, (22.94, 24.40))
D1 = S('D1', 25.90, 29.45, 'paulista', 'entre os prédios da Paulista, o vento ainda acelera')
D1.cam = cam([(25.90, (-40.0, 0.0, 22.0)), (29.45, (-16.0, 0.0, 17.0))], [(25.90, (140.0, 0.0, 6.0)), (29.45, (140.0, 0.0, 6.0))], 26)
D1.wind = 0.8; D1.rain = 0.6; D1.arrows = 26.10; D1.lights_off = True
D1.labels = [('corredor', 'efeito corredor', YEL, 1.4, 26.70, 99, follow(D1, 30.0, 6.5))]
D2 = S('D2', 29.45, 31.30, 'paulista', 'placas, vidros')
D2.cam = cam([(29.45, (12.0, -3.0, 2.4)), (31.30, (14.0, -2.5, 2.6))], [(29.45, (40.0, 1.0, 3.6)), (31.30, (40.0, 1.0, 3.8))], 28)
D2.wind = 1.0; D2.rain = 1.0; D2.debris = 29.20; D2.shake = 0.8; D2.lights_off = True
D2.labels = [('placas', 'placas', WHITE, 0.42, 29.60, 99, follow(D2, 9.0, 1.6)), ('vidros', 'vidros', CYAN, 0.42, 30.50, 99, follow(D2, 9.0, 0.95))]
D3 = S('D3', 31.30, 32.95, 'paulista', 'e galhos viram projéteis')
D3.cam = cam([(31.30, (30.0, 6.0, 1.6)), (32.95, (31.0, 5.0, 2.0))], [(31.30, (10.0, -2.0, 3.5)), (32.95, (10.0, -2.0, 3.5))], 24)
D3.wind = 1.0; D3.rain = 1.0; D3.debris = 29.80; D3.shake = 1.0; D3.lights_off = True; D3.deb_dir = -1
D3.labels = [('projeteis', 'projéteis', RED, 0.45, 31.80, 99, follow(D3, 8.0, 1.5))]
E1 = S('E1', 32.95, 34.60, 'globo', 'e o Brasil já teve um')
E1.cam = cam([(32.95, _ll(-15, -30, 30.0)), (34.60, _ll(-24, -44, 18.0))], [(32.95, (0, 0, 0)), (34.60, _ll(*CAT, 7.0))], 35)
E1.hur = CAT; E1.hur_size = 0.05
E2 = S('E2', 34.60, 37.60, 'globo', 'em 2004, o furacão Catarina')
E2.cam = cam([(34.60, _ll(-24, -44, 18.0)), (37.60, _ll(-27.5, -47.6, 12.6))], [(34.60, _ll(*CAT, 7.0)), (37.60, _ll(*CAT, 9.4))], 35)
E2.hur = CAT; E2.hur_size = 0.05; E2.landfall = True; E2.no_pin = True
E2.labels = [('catarina', 'furacão Catarina · 2004', YEL, 0.17, 36.40, 99, follow(E2, 2.6, 0.45))]
E3 = S('E3', 37.60, 39.80, 'rua', 'danificou milhares de casas no Sul')
E3.cam = cam([(37.60, (4.0, -3.0, 2.0)), (39.80, (7.0, -2.0, 2.4))], [(37.60, (24.0, 6.0, 4.0)), (39.80, (24.0, 6.0, 4.5))], 28)
E3.wind = 0.9; E3.rain = 0.8; E3.debris = 37.40; E3.shake = 0.4; E3.storm = True
E3.labels = [('casas', 'milhares de casas danificadas', WHITE, 0.36, 37.90, 99, follow(E3, 9.0, 1.7))]

# ================================================================= VIRADA: a defesa
F1 = S('F1', 39.80, 41.70, 'relevo', 'agora, a defesa')
F1.cam = cam([(39.80, (-88.0, -60.0, 46.0)), (41.70, (-80.0, -54.0, 41.0))], [(39.80, (22.0, 0.0, 4.0)), (41.70, (22.0, 0.0, 4.0))], 30)
F1.hur_x = (-45.0, -44.0)
F1.labels = [('defesa2', 'a defesa', YEL, 5.0, 40.64, 99, lambda T: (14.0, -4.0, 17.0))]
F2 = S('F2', 41.70, 44.10, 'relevo', 'furacão precisa de mar quente')
F2.cam = cam([(41.70, (-78.0, -40.0, 38.0)), (44.10, (-72.0, -36.0, 33.0))], [(41.70, (-42.0, 0.0, 3.0)), (44.10, (-40.0, 0.0, 3.0))], 30)
F2.hur_x = (-46.0, -42.0)
F2.labels = [('marq', 'mar quente (26 °C ou mais)', RED, 2.6, 42.94, 99, lambda T: (-44.0, 0.0, 15.0))]
F3 = S('F3', 44.10, 48.55, 'relevo', 'São Paulo fica a uns 60 km da costa, em cima da serra')
F3.cam = cam([(44.10, (-22.0, -50.0, 34.0)), (48.55, (22.0, -52.0, 30.0))], [(44.10, (28.0, 0.0, 5.0)), (48.55, (50.0, 0.0, 7.0))], 30)
F3.hur_x = (-42.0, -38.0); F3.dim = (45.26, 46.30)
F3.labels = [('sp', 'São Paulo', YEL, 4.0, 44.30, 99, lambda T: (60.0, 0.0, 15.0)),
             ('km60', '~60 km da costa', WHITE, 3.0, 45.60, 99, lambda T: (30.0, -16.0, 15.5)),
             ('serra', 'serra (~800 m)', GREEN, 3.0, 47.60, 99, lambda T: (12.0, -16.0, 9.0))]
F4 = S('F4', 48.55, 52.30, 'relevo', 'longe do mar, ele perde combustível e enfraquece')
F4.cam = cam([(48.55, (-62.0, -55.0, 46.0)), (52.30, (-8.0, -58.0, 42.0))], [(48.55, (-18.0, 0.0, 8.0)), (52.30, (32.0, 0.0, 8.0))], 30)
F4.hur_x = (-30.0, 34.0); F4.dim = (0.0, 0.0); F4.weaken = (49.0, 52.0)
F4.labels = [('enfraquece', 'enfraquece', RED, 2.4, 51.16, 99, lambda T: (34.0, -6.0, 24.0))]

# ================================================================= FINAL
G1 = S('G1', 52.30, 56.45, 'paulista', 'os 250 por hora não chegam inteiros na Paulista')
G1.cam = cam([(52.30, (-20.0, 3.0, 3.0)), (56.45, (-8.0, 2.0, 3.6))], [(52.30, (80.0, -3.0, 14.0)), (56.45, (80.0, -3.0, 14.0))], 26)
G1.wind = 0.35; G1.rain = 0.6
G1.panel = ('speed', 52.40, 99, (52.40, 52.41), 'strike', 54.58)
G2 = S('G2', 56.45, 61.25, 'paulista', 'o perigo real é a tempestade comum')
G2.cam = cam([(56.45, (18.0, -4.0, 1.8)), (61.25, (24.0, -5.5, 2.4))], [(56.45, (30.0, -11.0, 1.0)), (61.25, (30.0, -11.0, 1.2))], 30)
G2.wind = 0.6; G2.rain = 1.0; G2.tree_down = True; G2.flash = (57.90, 59.60)
G2.labels = [('tempestade', 'tempestade comum', YEL, 0.235, 57.82, 99, follow(G2, 5.0, 1.36)),
             ('capaz', 'já mostrou do que é capaz', WHITE, 0.18, 59.40, 99, follow(G2, 5.0, 0.81))]
H1 = S('H1', 61.25, END, 'paulista', 'segue o perfil para o próximo e se')
H1.cam = cam([(61.25, (-10.0, 0.0, 20.0)), (END, (-50.0, -6.0, 80.0))], [(61.25, (60.0, 0.0, 15.0)), (END, (100.0, 0.0, 15.0))], 30)
H1.wind = 0.4; H1.rain = 0.7
H1.labels = [('prox', 'próximo: e se...?', YEL, 1.4, 61.70, 99, follow(H1, 30.0, 4.0))]

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6

# ---- thumbnail (só existe com THUMB=1; não entra em SHOTS nem no vídeo)
if os.environ.get('THUMB'):
    TH = Shot('THUMB', 1.0, 2.0, 'paulista', 'thumbnail: tempestade na Paulista, raio e destroços')
    _tc = [float(v) for v in os.environ.get('THUMB_CAM', '-6.0,-5.0,1.3,70.0,1.0,12.0,22').split(',')]
    TH.cam = cam([(1.0, tuple(_tc[0:3])), (2.0, tuple(_tc[0:3]))], [(1.0, tuple(_tc[3:6])), (2.0, tuple(_tc[3:6]))], _tc[6])
    TH.wind = 1.0; TH.rain = 1.0; TH.debris = float(os.environ.get('THUMB_DEB', '1.0')); TH.flash = (float(os.environ.get('THUMB_FLASH', '1.5')),)
    BY_NAME['THUMB'] = TH
