"""Planos do vídeo 04 (e se o oxigênio sumisse por 20 segundos). T = tempo da narração (s), amarrado a analysis/narracao/04_words.json.
Ritmo: cortes nas batidas das frases + câmera sempre em movimento; nenhum trecho > 3 s sem novidade na tela (corte, rótulo, movimento forte).
Tipos de cenário: rua, mol, ceu, pulmao, cabine, cristal, terra."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 74.40           # narração termina em 74,24 s

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []      # (id, texto, cor, tamanho, t_on, t_off, pos(T)->xyz)
        self.panel = None     # painel preso à câmera: ('pie', ...), ('gauge', ...), ('alt', ...)
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def add(a, b, k=1.0): return tuple(x + k * y for x, y in zip(a, b))
def _front(c, d, up):
    p, l = c['pos'], c['look']; v = [b - a for a, b in zip(p, l)]; n = math.sqrt(sum(x * x for x in v))
    return (p[0] + v[0] / n * d, p[1] + v[1] / n * d, p[2] + v[2] / n * d + up)
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

# ---------------------------------------------------------------- referências da rua
TEO = (20.5, 4.7, 0.15)                    # Téo na calçada (topo da calçada z = 0,15)
HEAD = (20.5, 4.7, 1.72)
CANDLE = (17.3, 5.35, 1.10); GAS = (24.95, 5.5, 1.18)
BLD = (21.5, 10.0)                          # frente do prédio (y), centro em x
T_SOME = 4.25                               # o O₂ some (logo depois de "segundos")
T_SOME_B = 15.62                            # "some" (moléculas vermelhas somem no plano B3)
T_FOGO = 25.55                              # "apaga"
T_VOLTA = 65.70                             # "volta"

# ================================================================= GANCHO
A1 = S('A1', 0.00, 1.30, 'rua', 'gancho: rua de manhã, Téo andando; carro passa')
A1.cam = cam([(0.0, (15.0, -1.2, 1.35)), (1.3, (16.6, -0.6, 1.4))], [(0.0, (22.0, 4.7, 1.1)), (1.3, (21.2, 4.7, 1.15))], 30)
A1.teo = 'walk'; A1.car = lambda T: (-2.0 + 11.0 * T, 1.75, 0.0, 0.0)
A2 = S('A2', 1.30, 2.60, 'rua', 'gancho: close no rosto do Téo; ele respira fundo')
A2.cam = cam([(1.3, (20.9, 2.9, 1.62)), (2.6, (20.75, 3.55, 1.68))], [(1.3, HEAD), (2.6, HEAD)], 50)
A2.teo = 'inhale'
A3 = S('A3', 2.60, 5.30, 'mol', 'o ar de perto; as moléculas vermelhas (O₂) somem')
A3.cam = cam([(2.6, (-6.0, -16.0, 2.0)), (5.3, (-1.0, -9.5, 0.5))], [(2.6, (2.0, 0.0, 0.0)), (5.3, (1.5, 0.0, -0.3))], 30)
A3.vanish = T_SOME
A3.labels = [('vinte', '20 s', YEL, 1.4, 3.55, 99, lambda T: add(A3.cam(T)['pos'], (3.2, 9.0, 3.4)))]
A5 = S('A5', 5.30, 7.00, 'rua', 'os prédios não caem: a câmera sobe pela fachada')
A5.cam = cam([(5.3, (21.5, -2.0, 1.3)), (7.0, (22.6, -3.6, 1.8))], [(5.3, (21.5, 10.0, 4.0)), (7.0, (21.5, 10.0, 19.0))], 20)
A5.labels = [('depe', 'de pé', GREEN, 1.6, 6.10, 99, lambda T: (21.5, 8.0, 15.5))]
A6 = S('A6', 7.00, 9.40, 'rua', 'o problema é você: Téo leva a mão ao pescoço')
A6.cam = cam([(7.0, (18.8, 1.2, 1.5)), (9.4, (19.9, 2.6, 1.6))], [(7.0, (20.5, 4.7, 1.35)), (9.4, (20.5, 4.7, 1.55))], 35)
A6.teo = 'throat'

# ================================================================= CONTEXTO (moléculas)
B1 = S('B1', 9.40, 12.20, 'mol', 'o ar: quase 80 % nitrogênio (azul)')
B1.cam = cam([(9.4, (16.0, -10.0, 6.0)), (12.2, (11.0, -14.0, 3.0))], [(9.4, (0, 0, 0)), (12.2, (0, 0, 0))], 28)
B1.panel = ('pie', 10.25, 99, 'N2')
B2 = S('B2', 12.20, 14.40, 'mol', 'só 21 % é oxigênio (vermelho)')
B2.cam = cam([(12.2, (-4.0, -7.0, -1.0)), (14.4, (-1.5, -5.0, 0.8))], [(12.2, (1.0, 2.0, 0.0)), (14.4, (2.0, 2.0, 0.5))], 32)
B2.panel = ('pie', 12.55, 99, 'O2'); B2.o2glow = (12.6, 13.1)
B3 = S('B3', 14.40, 16.60, 'mol', 'e é só ele que some')
B3.cam = cam([(14.4, (5.0, -9.0, 2.5)), (16.6, (2.5, -12.0, 1.0))], [(14.4, (0, 0, 0)), (16.6, (0, 0, 0))], 30)
B3.vanish = T_SOME_B; B3.panel = ('pie', 14.45, 99, 'gone')

# ================================================================= PRESSÃO E OUVIDOS
C1 = S('C1', 16.60, 19.80, 'rua', 'a pressão cai um quinto: medidor de 101 para 80 kPa')
C1.cam = cam([(16.6, (17.0, -9.0, 6.5)), (19.8, (18.5, -4.5, 2.4))], [(16.6, (20.5, 6.0, 3.0)), (19.8, (20.5, 4.7, 1.4))], 26)
C1.teo = 'idle'; C1.panel = ('gauge', 16.95, 99, (18.10, 19.25))
C2 = S('C2', 19.80, 21.30, 'rua', 'ouvidos estalam: Téo leva as mãos às orelhas')
C2.cam = cam([(19.8, (21.6, 3.6, 1.78)), (21.3, (21.2, 3.4, 1.72))], [(19.8, HEAD), (21.3, HEAD)], 55)
C2.teo = 'ears'
C2.labels = [('ploc', 'ploc!', YEL, 0.05, 20.62, 99, lambda T: (20.78, 4.45, 1.98))]
C3 = S('C3', 21.30, 24.70, 'ceu', 'como subir 2 mil metros num piscar de olhos: a câmera sobe atravessando as nuvens')
C3.cam = cam([(21.3, (0.0, -60.0, -1350.0)), (22.0, (0.0, -60.0, -1330.0)), (23.8, (0.0, -60.0, 600.0)), (24.7, (0.0, -60.0, 650.0))],
             [(21.3, (0.0, 400.0, -1150.0)), (24.7, (0.0, 400.0, 760.0))], 22)
C3.panel = ('alt', 21.45, 99, (22.0, 23.8)); C3.no_jet = True

# ================================================================= FOGO
D1 = S('D1', 24.70, 26.40, 'rua', 'todo fogo apaga: a boca de gás acesa se apaga')
D1.cam = cam([(24.7, (23.4, 3.55, 1.95)), (26.4, (24.1, 3.95, 1.72))], [(24.7, (24.95, 5.5, 1.22)), (26.4, (24.95, 5.5, 1.2))], 35)
D1.teo = 'idle'; D1.fire_out = T_FOGO
D1.labels = [('fogo', 'fogo precisa de O₂', YEL, 0.06, 24.95, 99, lambda T: (24.85, 5.4, 1.62))]
D2 = S('D2', 26.40, 27.00, 'rua', 'vela: só a fumacinha')
D2.cam = cam([(26.4, (17.0, 4.55, 1.2)), (27.0, (17.15, 4.68, 1.22))], [(26.4, (17.3, 5.35, 1.16)), (27.0, (17.3, 5.35, 1.18))], 60)
D2.fire_out = 0.0; D2.wisp = CANDLE
D3 = S('D3', 27.00, 27.65, 'rua', 'fogão: boca de gás apagada')
D3.cam = cam([(27.0, (24.5, 4.6, 1.75)), (27.65, (24.75, 4.75, 1.65))], [(27.0, (24.95, 5.5, 1.2)), (27.65, (24.95, 5.5, 1.2))], 45)
D3.fire_out = 0.0
D4 = S('D4', 27.65, 28.80, 'rua', 'motor de carro: o escapamento para de soltar fumaça, o carro perde força')
D4.cam = cam([(27.65, (22.0, -3.8, 0.7)), (28.8, (25.6, -3.6, 0.8))], [(27.65, (26.0, -1.75, 0.5)), (28.8, (29.0, -1.75, 0.6))], 30)
D4.car = lambda T: (26.0 + 5.0 * (T - 27.65) - 1.2 * max(T - 27.95, 0) ** 2, -1.75, 0.0, 0.0); D4.engine_off = 27.95

# ================================================================= AVIÃO
E1 = S('E1', 28.80, 32.30, 'ceu', 'até as turbinas apagam; o avião segue planando')
E1.jet = lambda T: ((T - 28.8) * 220.0, 0.0, -(max(T - 29.5, 0)) * 6.0)
E1.cam = lambda T: dict(pos=add(E1.jet(T), (30.0 - 26.0 * sstep(28.8, 32.3, T), -46.0 - 4.0 * sstep(28.8, 32.3, T), -9.0 + 5.0 * sstep(28.8, 32.3, T))),
                        look=add(E1.jet(T), (-2.0, 0, 2.0)), lens=30)
E1.engines = lambda T: 1.0 - sstep(29.30, 29.9, T)
E1.labels = [('turbina', 'turbinas apagadas', RED, 1.6, 29.95, 99, lambda T: add(E1.jet(T), (-3.0, 0.0, 8.5))),
             ('planando', 'planando', CYAN, 1.6, 31.0, 99, lambda T: add(E1.jet(T), (-3.0, 0.0, 12.0)))]

# ================================================================= RESPIRAÇÃO
F1 = S('F1', 32.30, 34.40, 'rua', 'prender a respiração não adianta: Téo tapa o nariz e a boca')
F1.cam = cam([(32.3, (19.6, 2.6, 1.6)), (34.4, (20.2, 3.3, 1.66))], [(32.3, HEAD), (34.4, HEAD)], 42)
F1.teo = 'hold'
F1.labels = [('naoad', 'não adianta', RED, 0.05, 33.55, 99, lambda T: (20.5, 4.4, 2.06))]
F2 = S('F2', 34.40, 36.80, 'pulmao', 'o oxigênio dos pulmões também some')
F2.cam = cam([(34.4, (0.0, -11.5, 1.0)), (36.8, (0.6, -7.5, 0.4))], [(34.4, (0.0, 0.0, 0.4)), (36.8, (0.3, -0.5, 0.2))], 35)
F2.vanish = 35.95
F3 = S('F3', 36.80, 40.30, 'pulmao', 'o sangue perde oxigênio para o pulmão vazio')
F3.cam = cam([(36.8, (99.0, -12.0, 4.5)), (40.3, (101.0, -8.5, 2.0))], [(36.8, (100.0, -1.0, 0.0)), (40.3, (101.0, -1.2, 0.2))], 32)
F3.leak = (37.2, 40.3)
F3.labels = [('sai', 'O₂ sai do sangue', RED, 0.3, 38.25, 99, lambda T: _front(F3.cam(T), 5.0, 1.9))]

# ================================================================= ALTITUDE E CABINE
G1 = S('G1', 40.30, 43.80, 'ceu', 'avião despressurizado a quase 14 mil metros')
G1.jet = lambda T: ((T - 40.3) * 240.0, 0.0, 400.0)
G1.cam = lambda T: dict(pos=add(G1.jet(T), (-55.0 + 30 * sstep(40.3, 43.8, T), -38.0 + 8 * sstep(40.3, 43.8, T), -10.0 + 6 * sstep(40.3, 43.8, T))),
                        look=add(G1.jet(T), (0, 0, 0)), lens=28)
G1.engines = lambda T: 1.0; G1.high = True
G1.labels = [('alt', '13.700 m', YEL, 1.8, 42.25, 99, lambda T: add(G1.jet(T), (0.0, 0.0, 9.0)))]
G2 = S('G2', 43.80, 47.90, 'cabine', 'as máscaras caem: sobram de 9 a 15 segundos')
G2.cam = cam([(43.8, (6.5, 0.15, 1.75)), (47.9, (0.9, 0.05, 1.55))], [(43.8, (-1.0, -0.4, 1.25)), (47.9, (-1.0, -0.6, 1.15))], 24)
G2.drop = 43.95
G2.labels = [('tuc', '9–15 s', RED, 0.32, 44.40, 99, lambda T: (-1.2, -0.2, 2.12)),
             ('consc', 'de consciência', WHITE, 0.13, 46.30, 99, lambda T: (-1.2, -0.2, 1.9))]

# ================================================================= CTA
H1 = S('H1', 47.90, 50.70, 'rua', 'CTA: Téo acena para a câmera')
H1.cam = cam([(47.9, (17.5, 0.8, 1.4)), (50.7, (22.8, 1.2, 1.5))], [(47.9, (20.5, 4.7, 1.25)), (50.7, (20.5, 4.7, 1.3))], 30)
H1.teo = 'wave'
H1.labels = [('prox', 'próximo: e se…?', YEL, 0.3, 48.40, 99, lambda T: (20.5, 4.4, 2.35))]

# ================================================================= REVELAÇÃO
I1 = S('I1', 50.70, 54.10, 'rua', 'e os prédios desmoronando dos vídeos virais?')
I1.cam = cam([(50.7, (14.0, -3.0, 0.8)), (54.1, (17.5, -4.5, 1.2))], [(50.7, (21.5, 10.0, 10.0)), (54.1, (21.5, 10.0, 12.0))], 18)
I1.labels = [('viral', '“prédios desabam”', WHITE, 1.3, 51.55, 99, lambda T: (21.5, 7.0, 14.0))]
I2 = S('I2', 54.10, 55.20, 'rua', 'mito')
I2.cam = cam([(54.1, (21.5, -1.0, 6.0)), (55.2, (21.5, 1.5, 7.0))], [(54.1, (21.5, 10.0, 9.5)), (55.2, (21.5, 10.0, 9.5))], 30)
I2.labels = [('mito', 'MITO', RED, 2.2, 54.28, 99, lambda T: (21.5, 7.5, 9.5))]
J1 = S('J1', 55.20, 59.70, 'cristal', 'o oxigênio do concreto, da água e das rochas está preso em moléculas')
J1.cam = cam([(55.2, (-6.0, -14.0, 3.0)), (57.6, (7.0, -30.0, 6.0)), (59.7, (-1.0, -6.5, 1.8))],
             [(55.2, (-3.4, 0.0, 0.0)), (57.6, (7.0, 0.0, 0.0)), (59.7, (0.0, 0.0, 1.0))], 30)
J1.labels = [('conc', 'concreto', WHITE, 1.1, 56.06, 99, lambda T: (-3.4, -2.0, 6.2)),
             ('agua', 'água', BLUE, 1.1, 56.88, 99, lambda T: (20.0, -2.0, 5.0)),
             ('rocha', 'rocha', WHITE, 1.1, 57.38, 99, lambda T: (6.8, -2.0, 6.2)),
             ('preso', 'ligado: não sai', RED, 0.16, 58.30, 99, lambda T: _front(J1.cam(T), 2.2, 0.75))]
J2 = S('J2', 59.70, 64.10, 'terra', 'quase metade da crosta é oxigênio, e ele fica onde está')
J2.cam = cam([(59.7, (18.0, 44.0, 16.0)), (64.1, (27.0, 30.0, 9.0))], [(59.7, (0, 0, 2.0)), (64.1, (0, 0, 1.5))], 40)
J2.panel = ('pie46', 60.55, 99, None)

# ================================================================= FINAL
K1 = S('K1', 64.10, 66.50, 'rua', 'segundo vinte: o ar volta (moléculas vermelhas reaparecem); Téo caído na calçada')
K1.cam = cam([(64.1, (16.5, -0.5, 3.2)), (66.5, (18.0, 1.2, 2.4))], [(64.1, (20.5, 4.7, 0.5)), (66.5, (20.5, 4.7, 0.6))], 30)
K1.teo = 'lying'; K1.o2back = T_VOLTA
K1.labels = [('vinte2', '20 s', YEL, 0.5, 64.60, 99, lambda T: (20.0, 4.6, 2.4))]
K2 = S('K2', 66.50, 68.40, 'rua', 'os ouvidos estalam de novo')
K2.cam = cam([(66.5, (20.45, 3.55, 1.65)), (68.4, (20.6, 3.8, 1.38))], [(66.5, (20.85, 4.7, 0.3)), (68.4, (20.85, 4.7, 0.3))], 38)
K2.teo = 'lying'; K2.o2back = 0.0
K2.labels = [('ploc2', 'ploc!', YEL, 0.035, 67.28, 99, lambda T: (20.8, 4.85, 0.95))]
K3 = S('K3', 68.40, 70.50, 'rua', 'quem desmaiou acorda: Téo senta')
K3.cam = cam([(68.4, (17.6, 2.6, 0.9)), (70.5, (18.4, 3.0, 1.1))], [(68.4, (20.0, 4.7, 0.45)), (70.5, (20.1, 4.7, 0.75))], 32)
K3.teo = 'situp'; K3.o2back = 0.0
L1 = S('L1', 70.50, 72.30, 'rua', 'o planeta sai inteiro: a câmera sobe sobre a rua')
L1.cam = cam([(70.5, (12.0, -6.0, 3.0)), (72.3, (2.0, -16.0, 22.0))], [(70.5, (21.0, 6.0, 4.0)), (72.3, (24.0, 6.0, 4.0))], 24)
L1.teo = 'sitting'; L1.o2back = 0.0
L2 = S('L2', 72.30, 74.40, 'rua', 'o perigo foi quem estava dirigindo: carro parado no poste, pisca-alerta')
L2.cam = cam([(72.3, (33.5, -8.5, 1.4)), (74.4, (35.6, -7.4, 1.3))], [(72.3, (38.6, -3.1, 0.9)), (74.4, (38.9, -3.2, 0.9))], 32)
L2.car = lambda T: (38.0, -2.9, 0.0, math.radians(28)); L2.crashed = True; L2.o2back = 0.0

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
