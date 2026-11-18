"""Planos do vídeo 05 (e se TODO o oxigênio sumisse por 20 segundos). T = tempo da narração (s), amarrado a analysis/narracao/05_words.json.
Ritmo do vídeo 04: cortes nas batidas das frases + câmera sempre em movimento; nenhum trecho > 3 s sem novidade na tela.
Tipos de cenário: rua, mol, terra, cristal, agua, mar."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 73.40           # narração termina em 73,22 s

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []      # (id, texto, cor, tamanho, t_on, t_off, pos(T)->xyz)
        self.panel = None     # painel preso à câmera: ('pie46', ...), ('body', ...), ('timer', ...)
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def add(a, b, k=1.0): return tuple(x + k * y for x, y in zip(a, b))
def _front(c, d, up):
    p, l = c['pos'], c['look']; v = [b - a for a, b in zip(p, l)]; n = math.sqrt(sum(x * x for x in v))
    return (p[0] + v[0] / n * d, p[1] + v[1] / n * d, p[2] + v[2] / n * d + up)
def anchor(shot, d, up, T=None):
    """Rótulo parado no mundo, à distância d na frente da câmera (no início do plano, ou no instante T)."""
    p = _front(shot.cam(shot.t0 if T is None else T), d, up); return lambda T_: p
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

# ---------------------------------------------------------------- referências
TEO = (20.5, 4.7, 0.15); HEAD = (20.5, 4.7, 1.72)
T_FOGO = 25.30                # depois disto, sem chamas na rua (sem oxigênio)
T_SOME_AR = 2.45              # "sumia" (lembrança do vídeo 04)
T_AGUA = 27.62                # "oxigênio" — a água perde o O
T_MAR = 32.90                 # "viram gás"
T_ROCHA = 38.35               # "Sem ele"
T_PREDIO = 39.45              # "prédios se desfazem"
T_CROSTA = 41.30              # "crosta"
T_CORPO = 44.62               # "perde dois terços"
T_SOME_B = T_CORPO            # (nome usado no painel de pizza)
T_VOLTA = 55.14               # "volta"

# ================================================================= GANCHO
A1 = S('A1', 0.00, 1.05, 'rua', 'no último vídeo: Téo andando na rua')
A1.cam = cam([(0.0, (15.0, -1.2, 1.35)), (1.05, (16.4, -0.7, 1.4))], [(0.0, (22.0, 4.7, 1.1)), (1.05, (21.3, 4.7, 1.15))], 30)
A1.teo = 'walk'
A1.labels = [('v04', 'vídeo 04', WHITE, 0.16, 0.25, 99, lambda T: (20.9, 4.6, 2.25))]
A2 = S('A2', 1.05, 3.55, 'mol', 'só o O₂ do ar sumia (lembrança)')
A2.cam = cam([(1.05, (-6.0, -16.0, 2.0)), (3.55, (-1.5, -10.5, 0.8))], [(1.05, (2.0, 0.0, 0.0)), (3.55, (1.5, 0.0, -0.3))], 30)
A2.vanish = T_SOME_AR
A2.labels = [('soar', 'só o O₂ do ar', WHITE, 0.32, 1.55, 99, anchor(A2, 3.2, 0.75, T=3.55))]
A3 = S('A3', 3.55, 6.30, 'terra', 'e se sumisse TODO o oxigênio do planeta?')
A3.cam = cam([(3.55, (34.0, 44.0, 16.0)), (6.3, (22.0, 32.0, 9.0))], [(3.55, (0, 0, 1.5)), (6.3, (0, 0, 1.0))], 40)
A3.labels = [('todo', 'TODO o oxigênio', RED, 2.4, 4.34, 99, lambda T: (0.0, 0.0, 13.0))]
A4 = S('A4', 6.30, 8.60, 'rua', 'por 20 segundos')
A4.cam = cam([(6.3, (14.0, -3.0, 0.8)), (8.6, (17.0, -4.6, 1.3))], [(6.3, (21.5, 10.0, 10.0)), (8.6, (21.5, 10.0, 12.0))], 18)
A4.labels = [('vinte', '20 s', YEL, 2.0, 6.62, 99, lambda T: (21.5, 7.0, 14.0))]
A5 = S('A5', 8.60, 11.40, 'rua', 'respirar é o menor problema')
A5.cam = cam([(8.6, (18.8, 1.2, 1.5)), (11.4, (19.9, 2.6, 1.6))], [(8.6, (20.5, 4.7, 1.35)), (11.4, (20.5, 4.7, 1.5))], 35)
A5.teo = 'idle'
A5.labels = [('menor', 'o menor problema', YEL, 0.14, 9.86, 99, lambda T: (20.5, 4.4, 2.22))]

# ================================================================= CONTEXTO
B1 = S('B1', 11.40, 14.90, 'rua', 'isso é impossível: experimento mental')
B1.cam = cam([(11.4, (18.5, -4.5, 2.4)), (14.9, (16.5, -10.5, 7.0))], [(11.4, (20.5, 4.7, 1.6)), (14.9, (21.0, 7.0, 4.5))], 26)
B1.teo = 'idle'
B1.labels = [('imposs', 'impossível', RED, 1.3, 11.82, 99, lambda T: (20.5, 3.0, 4.9)),
             ('mental', 'experimento mental', WHITE, 0.75, 12.86, 99, lambda T: (20.5, 3.0, 3.5))]
B2 = S('B2', 14.90, 16.70, 'cristal', 'o oxigênio está em quase tudo')
B2.cam = cam([(14.9, (-10.0, -20.0, 8.0)), (16.7, (4.0, -22.0, 5.0))], [(14.9, (0, 0, 0)), (16.7, (0, 0, 0))], 30)
B2.oglow = (15.2, 15.8)
B2.labels = [('tudo', 'oxigênio: quase tudo', YEL, 1.1, 15.18, 99, lambda T: (0.0, -4.0, 7.6))]
B3 = S('B3', 16.70, 17.80, 'agua', 'na água')
B3.cam = cam([(16.7, (0.0, -22.0, 3.0)), (17.8, (1.5, -18.0, 1.5))], [(16.7, (0, 0, 0)), (17.8, (0, 0, 0))], 30)
B3.labels = [('agua', 'água', BLUE, 1.2, 16.94, 99, lambda T: (0.0, -9.0, 5.2))]
B4 = S('B4', 17.80, 18.85, 'cristal', 'nas rochas')
B4.cam = cam([(17.8, (13.0, -12.0, 4.0)), (18.85, (10.0, -9.5, 2.6))], [(17.8, (5.0, 0, 0)), (18.85, (5.0, 0, 0))], 32)
B4.labels = [('rocha', 'rochas', WHITE, 0.6, 17.96, 99, anchor(B4, 5.0, 1.5, T=18.85))]
B5 = S('B5', 18.85, 20.30, 'rua', 'no concreto')
B5.cam = cam([(18.85, (16.0, 3.0, 6.0)), (20.3, (17.5, 3.6, 8.0))], [(18.85, (19.5, 10.0, 7.0)), (20.3, (20.5, 10.0, 9.0))], 30)
B5.labels = [('concr', 'concreto', WHITE, 0.55, 19.02, 99, lambda T: (19.2, 8.0, 8.4))]
B6 = S('B6', 20.30, 25.30, 'rua', 'e em você: quase dois terços do seu corpo')
B6.cam = cam([(20.3, (19.2, 2.0, 1.5)), (25.3, (19.9, 3.1, 1.62))], [(20.3, (20.5, 4.7, 1.25)), (25.3, (20.5, 4.7, 1.4))], 30)
B6.teo = 'idle'; B6.panel = ('body', 21.64, 99, 'hi')
B6.labels = [('voce', 'você', YEL, 0.14, 20.56, 99, lambda T: (20.5, 4.4, 2.08))]

# ================================================================= DESENVOLVIMENTO
C1 = S('C1', 25.30, 28.50, 'agua', 'no primeiro instante a água perde o oxigênio')
C1.cam = cam([(25.3, (6.0, -26.0, 6.0)), (28.5, (1.0, -13.0, 1.0))], [(25.3, (0, 0, 0)), (28.5, (0, 0, 0))], 30)
C1.vanish = T_AGUA
C1.labels = [('inst', '1º instante', YEL, 0.7, 25.48, 99, lambda T: _front(C1.cam(T), 7.0, 1.9))]
C2 = S('C2', 28.50, 32.10, 'agua', 'sobra hidrogênio: um gás')
C2.cam = cam([(28.5, (-14.0, -16.0, 4.0)), (32.1, (-11.0, -22.0, 2.0))], [(28.5, (0, 0, 0)), (32.1, (0, 0, 0))], 28)
C2.vanish = T_AGUA
C2.labels = [('h2', 'H₂: gás', WHITE, 1.2, 29.78, 99, lambda T: (-4.0, -5.0, 5.0))]
C3 = S('C3', 32.10, 34.60, 'mar', 'rios e oceanos viram gás')
C3.cam = cam([(32.1, (0.0, -30.0, 9.0)), (34.6, (0.0, -24.0, 13.0))], [(32.1, (0.0, 60.0, 0.0)), (34.6, (0.0, 60.0, 4.0))], 24)
C3.labels = [('gas', 'vira gás', WHITE, 4.5, 33.30, 99, lambda T: (0.0, 20.0, 15.0))]
D1 = S('D1', 34.60, 38.30, 'cristal', 'rochas e concreto: quase metade oxigênio')
D1.cam = cam([(34.6, (0.0, -24.0, 6.0)), (38.3, (-6.0, -18.0, 3.0))], [(34.6, (0, 0, 1.0)), (38.3, (0, 0, 1.0))], 28)
D1.panel = ('pie46', 36.12, 99, None); D1.oglow = (36.5, 37.3)
D2 = S('D2', 38.30, 39.40, 'cristal', 'sem ele, a rede se desfaz')
D2.cam = cam([(38.3, (-4.0, -16.0, 4.0)), (39.4, (-2.5, -13.0, 3.0))], [(38.3, (0, 0, 0)), (39.4, (0, 0, 0))], 30)
D2.vanish = T_ROCHA
D3 = S('D3', 39.40, 41.00, 'rua', 'os prédios se desfazem')
D3.cam = cam([(39.4, (6.0, -16.0, 3.0)), (41.0, (8.0, -19.0, 4.0))], [(39.4, (21.5, 14.0, 9.0)), (41.0, (21.5, 14.0, 5.0))], 22)
D3.crumble = T_PREDIO; D3.teo = 'idle'
D4 = S('D4', 41.00, 43.85, 'terra', 'a crosta do planeta perde a firmeza')
D4.cam = cam([(41.0, (26.0, 32.0, 10.0)), (43.85, (20.0, 27.0, 7.0))], [(41.0, (0, 0, 1.0)), (43.85, (0, 0, 1.0))], 40)
D4.shake = T_CROSTA
D4.labels = [('crosta', 'crosta sem firmeza', WHITE, 1.9, 41.26, 99, lambda T: (0.0, 0.0, 12.6))]
E1 = S('E1', 43.85, 48.10, 'rua', 'o corpo perde dois terços da massa')
E1.cam = cam([(43.85, (19.0, 1.8, 1.5)), (48.1, (19.6, 2.6, 1.55))], [(43.85, (20.5, 4.7, 1.15)), (48.1, (20.5, 4.7, 1.1))], 30)
E1.teo = 'idle'; E1.crumbled = True; E1.fade = (T_CORPO, 46.9); E1.panel = ('body', 43.95, 99, 'gone')
E1.labels = [('massa', '−65% da massa', RED, 0.16, 45.04, 99, lambda T: (20.5, 4.4, 2.25))]
E2 = S('E2', 48.10, 51.00, 'rua', 'ninguém sobrevive ao primeiro segundo')
E2.cam = cam([(48.1, (16.0, -1.0, 2.2)), (51.0, (17.5, 0.5, 1.9))], [(48.1, (20.5, 4.7, 1.0)), (51.0, (20.5, 4.7, 0.8))], 28)
E2.crumbled = True; E2.no_teo = True
E2.labels = [('seg', '1º segundo', YEL, 0.35, 49.28, 99, lambda T: (20.5, 4.6, 1.8))]

# ================================================================= CTA
F1 = S('F1', 51.00, 54.10, 'terra', 'CTA: próximo "e se"')
F1.cam = cam([(51.0, (30.0, 40.0, 14.0)), (54.1, (25.0, 35.0, 10.0))], [(51.0, (0, 0, 2.0)), (54.1, (0, 0, 1.5))], 40)
F1.labels = [('prox', 'próximo: e se…?', YEL, 2.2, 51.48, 99, lambda T: (0.0, 0.0, 13.0))]

# ================================================================= REVELAÇÃO
G1 = S('G1', 54.10, 57.60, 'rua', 'no segundo 20 o oxigênio volta')
G1.cam = cam([(54.1, (10.0, -12.0, 4.0)), (57.6, (12.0, -10.0, 5.0))], [(54.1, (21.0, 12.0, 2.5)), (57.6, (21.0, 12.0, 3.0))], 24)
G1.crumbled = True; G1.no_teo = True; G1.loose = (T_VOLTA, (21.0, 7.0, 4.0), (12.0, 7.0, 3.6), 320, 0.14)
G1.labels = [('vinte2', '20 s', YEL, 1.4, 56.40, 99, lambda T: (21.0, 4.0, 8.4))]
G2 = S('G2', 57.60, 60.40, 'rua', 'volta como átomos soltos')
G2.cam = cam([(57.6, (18.0, 1.0, 1.6)), (60.4, (19.5, 2.2, 1.45))], [(57.6, (21.0, 8.0, 1.2)), (60.4, (21.5, 8.0, 1.3))], 30)
G2.crumbled = True; G2.no_teo = True; G2.loose = (0.0, (21.0, 6.5, 1.6), (4.5, 3.0, 1.4), 160, 0.05)
G2.labels = [('soltos', 'átomos soltos', RED, 0.3, 58.48, 99, lambda T: (20.3, 5.2, 2.55))]
G3 = S('G3', 60.40, 61.40, 'agua', 'a água não se remonta')
G3.cam = cam([(60.4, (0.0, -18.0, 2.0)), (61.4, (1.0, -15.5, 1.0))], [(60.4, (0, 0, 0)), (61.4, (0, 0, 0))], 30)
G3.scatter = 0.9; G3.loose = (0.0, (0.0, 0.0, 0.0), (10.0, 10.0, 6.0), 120, 0.42)
G3.labels = [('agua2', 'água', BLUE, 1.0, 60.64, 99, lambda T: (0.0, -6.0, 4.2))]
G4 = S('G4', 61.40, 62.10, 'cristal', 'as rochas não se remontam')
G4.cam = cam([(61.4, (-5.0, -17.0, 4.0)), (62.1, (-3.5, -15.0, 3.0))], [(61.4, (0, 0, 0)), (62.1, (0, 0, 0))], 30)
G4.scatter = 1.0; G4.loose = (0.0, (0.0, 0.0, 0.0), (8.0, 6.0, 6.0), 90, 0.42)
G4.labels = [('rochas2', 'rochas', WHITE, 1.0, 61.50, 99, lambda T: (0.0, -6.0, 4.4))]
G5 = S('G5', 62.10, 65.10, 'rua', 'nem as pessoas')
G5.cam = cam([(62.1, (18.5, 1.5, 1.6)), (65.1, (19.4, 2.3, 1.5))], [(62.1, (20.5, 4.7, 1.0)), (65.1, (20.5, 4.7, 1.0))], 30)
G5.crumbled = True; G5.no_teo = True; G5.loose = (0.0, (20.5, 4.9, 1.3), (2.2, 1.6, 1.1), 110, 0.035)
G5.labels = [('pessoas', 'pessoas', WHITE, 0.18, 62.18, 99, lambda T: (20.5, 4.6, 1.92)),
             ('remonta', 'não se remontam', RED, 0.18, 63.16, 99, lambda T: (20.5, 4.6, 1.62))]

# ================================================================= FINAL
H1 = S('H1', 65.10, 68.20, 'rua', 'por isso os vinte segundos não importam')
H1.cam = cam([(65.1, (20.0, -6.0, 3.0)), (68.2, (20.0, -14.0, 15.0))], [(65.1, (21.0, 10.0, 3.0)), (68.2, (21.0, 10.0, 1.0))], 24)
H1.crumbled = True; H1.no_teo = True; H1.loose = (0.0, (21.0, 7.0, 3.0), (12.0, 7.0, 3.0), 300, 0.14)
H1.labels = [('vinte3', '20 s', YEL, 1.5, 65.74, 99, lambda T: (21.0, 4.0, 8.6)),
             ('naoimp', 'não importam', WHITE, 0.9, 66.42, 99, lambda T: (21.0, 4.0, 6.8))]
H2 = S('H2', 68.20, 71.00, 'rua', '20 segundos ou um piscar de olhos')
H2.cam = cam([(68.2, (31.0, -6.0, 2.5)), (71.0, (28.0, -8.5, 3.5))], [(68.2, (21.0, 8.0, 2.5)), (71.0, (21.0, 8.0, 3.0))], 26)
H2.crumbled = True; H2.no_teo = True; H2.loose = (0.0, (21.0, 7.0, 3.0), (12.0, 7.0, 3.0), 300, 0.12)
H2.labels = [('vinte4', '20 s', YEL, 1.1, 68.30, 99, lambda T: (23.0, 4.0, 6.4)),
             ('piscar', '= um piscar de olhos', WHITE, 0.6, 69.34, 99, lambda T: (23.0, 4.0, 5.0))]
H3 = S('H3', 71.00, 73.40, 'rua', 'tudo acaba no primeiro instante')
H3.cam = cam([(71.0, (20.0, -10.0, 8.0)), (73.4, (20.0, -34.0, 34.0))], [(71.0, (21.0, 10.0, 0.0)), (73.4, (21.0, 10.0, 0.0))], 26)
H3.crumbled = True; H3.no_teo = True; H3.loose = (0.0, (21.0, 7.0, 3.0), (14.0, 8.0, 3.0), 320, 0.16)
H3.labels = [('fim', 'tudo acaba no 1º instante', YEL, 0.6, 71.12, 99, lambda T: _front(H3.cam(T), 11.0, 1.6))]

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
