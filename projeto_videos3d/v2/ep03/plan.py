"""Planos do vídeo 03 (buraco que atravessa a Terra). T = tempo da narração (s), amarrado a analysis/narracao/03_words.json.
Tipos de cenário: 'polo' (neve + boca do túnel), 'tunel' (dentro do poço), 'corte' (Terra em corte no espaço)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease
import fisica as F

FPS = 30
END = 66.0            # narração termina em 65,12 s
R = 10.0              # raio da Terra nas cenas de corte (unidades de cena)
KM = R / 6371.0       # 1 km em unidades de cena

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []      # (id, texto, cor, tamanho, t_on, t_off, pos(T)->xyz)
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def add(a, b, k=1.0): return tuple(x + k * y for x, y in zip(a, b))
def sph(lon, el, r):
    lo, e = math.radians(lon), math.radians(el)
    return (r * math.cos(e) * math.cos(lo), r * math.cos(e) * math.sin(lo), r * math.sin(e))
def clamp_pchip(knots):
    f = pchip(knots); a, b = knots[0][0], knots[-1][0]
    return lambda x: f(min(max(x, a), b))
def eased(knots):
    f = ease(knots); a, b = knots[0][0], knots[-1][0]
    return lambda T: f(min(max(T, a), b))

YEL, RED, WHITE, BLUE, CYAN, ORANGE = (1.0, 0.80, 0.08), (1.0, 0.25, 0.15), (0.97, 0.97, 0.97), (0.45, 0.75, 1.0), (0.35, 0.95, 1.0), (1.0, 0.55, 0.12)
SHOTS = []
VIEW = 45.0           # longitude de onde se olha o corte (meio da cunha aberta)
MARK_OFF = 0.35       # Téo desenhado um pouco à frente do eixo (para não sumir dentro das faces do corte)
def on_axis(z_units): return add((0.0, 0.0, z_units), sph(VIEW, 0, MARK_OFF))
def z_of_depth(d_km): return R - d_km * KM

# ---------------------------------------------------------------- A — gancho: Téo na boca do túnel, Polo Norte
A = Shot('A', 0.00, 6.40, 'polo', 'gancho: Téo na beira do buraco; a câmera sobe e olha para dentro do poço')
A.pole_name = 'POLO NORTE'
A_cam = eased([(0.0, (5.8, -9.6, 1.25)), (3.4, (4.6, -8.2, 1.7)), (6.4, (1.2, -4.6, 7.4))])
A_look = eased([(0.0, (0.2, -2.6, 1.05)), (3.4, (0.0, -2.2, 0.9)), (6.4, (0.0, 0.4, -9.0))])
A.cam = lambda T: dict(pos=A_cam(T), look=A_look(T), lens=30 - 4 * sstep(3.4, 6.4, T))
A.labels = []
SHOTS.append(A)

# ---------------------------------------------------------------- B — o túnel reto, de polo a polo, sem ar
B_ = Shot('B', 6.40, 10.50, 'corte', 'contexto: Terra em corte; o túnel cresce do Polo Norte ao Polo Sul')
B_.cut = 'wedge'
B_.sun = sph(28, 32, 1)
B_.spin = lambda T: 0.0
B_.tube = lambda T: sstep(7.05, 8.95, T)
B_cam = eased([(6.4, sph(VIEW + 12, 18, 62)), (10.5, sph(VIEW + 2, 12, 38))])
B_.cam = lambda T: dict(pos=B_cam(T), look=(0, 0, 0.0), lens=40)
B_.labels = [('pn', 'Polo Norte', BLUE, 1.0, 8.30, 99, lambda T: (0.0, 0.0, 12.3)),
             ('ps', 'Polo Sul', BLUE, 1.0, 8.70, 99, lambda T: (0.0, 0.0, -12.3)),
             ('vac', 'sem ar (vácuo)', CYAN, 0.85, 9.40, 99, lambda T: add(sph(VIEW, 0, 4.2), (0, 0, 3.4)))]
SHOTS.append(B_)

# ---------------------------------------------------------------- C — você pula... e flutua, sem peso
C = Shot('C', 10.50, 16.30, 'polo', 'Téo pula no poço; a câmera cai junto; flutua sem peso')
C.pole_name = 'POLO NORTE'
T_PULO = 11.15
TEO_RIM = (0.0, -3.45)
def teo_fall_z(T):
    t = max(0.0, T - (T_PULO + 0.25)); return -0.5 * 9.8 * t * t
C.teo_z = teo_fall_z
def _C_cam(T):
    zt = teo_fall_z(T); k = sstep(T_PULO + 0.1, T_PULO + 1.4, T)
    z0 = -6.5; zc = min(z0, zt - 3.0 * k - (1 - k) * 6.5) if T > T_PULO else z0
    pos = (0.9 - 0.5 * k, 0.9 - 0.3 * k, zc)
    look_z = (1.4 if T < T_PULO + 0.3 else 1.4 + (zt + 0.9 - 1.4) * k)
    look = (0.0, -2.4 * (1 - k), look_z)
    return dict(pos=pos, look=look, lens=22, up=(0, 1, 0) if False else (0, 0, 1))
C.cam = _C_cam
def _teo_xy(T):
    u = sstep(T_PULO, T_PULO + 0.9, T); return (TEO_RIM[0], TEO_RIM[1] * (1 - u) - 0.2 * u)
C.teo_xy = _teo_xy
C.labels = [('peso', 'sem peso', CYAN, 0.30, 13.70, 99, lambda T: (0.9, -0.1, teo_fall_z(T) + 1.7))]
SHOTS.append(C)

# ---------------------------------------------------------------- D — a gravidade AUMENTA até o núcleo de ferro
D = Shot('D', 16.30, 28.00, 'corte', 'Téo desce pelo eixo; gráfico da gravidade (PREM): sobe até 10,7 m/s² no núcleo e depois cai')
D.cut = 'wedge'; D.sun = B_.sun; D.spin = lambda T: 0.0; D.tube = lambda T: 1.0
D.depth = clamp_pchip([(16.3, 0.0), (18.05, 0.0), (21.0, 1150.0), (24.25, 2891.0), (26.2, 4700.0), (27.7, 6371.0), (28.0, 6371.0)])
D.marker = lambda T: on_axis(z_of_depth(D.depth(T)) + 0.25 * (1 - sstep(17.4, 18.2, T)))
D_cam = eased([(16.3, sph(VIEW + 2, 30, 30)), (21.0, sph(VIEW, 16, 25)), (25.0, sph(VIEW - 2, 8, 24)), (28.0, sph(VIEW - 3, 4, 23))])
D_look = eased([(16.3, (0.0, 0.0, 6.2)), (21.0, (0.0, 0.0, 4.0)), (25.0, (0.0, 0.0, 1.5)), (28.0, (0.0, 0.0, 0.0))])
D.cam = lambda T: dict(pos=D_cam(T), look=add(D_look(T), (0, 0, -4.0)), lens=40)
D.graph = dict(t_on=16.9, t_off=27.95)
D.labels = [('nucleo', 'núcleo de ferro', ORANGE, 0.62, 22.05, 99, lambda T: add(sph(VIEW - 30, 0, 3.6), (0, 0, 3.0))),
            ('cmb', '2.891 km', WHITE, 0.55, 23.80, 99, lambda T: add(on_axis(z_of_depth(2891)), sph(VIEW + 90, 0, 1.6)))]
SHOTS.append(D)

# ---------------------------------------------------------------- E — no centro: mais de 35 mil km/h
E = Shot('E', 28.00, 32.90, 'tunel', 'dentro do túnel no núcleo: paredes em brasa, anéis passando muito rápido')
E.prof = lambda T: 0.78 + 0.22 * sstep(28.0, 28.8, T)
E.speed = lambda T: 150.0
E.cam = lambda T: dict(pos=(0.45 + 0.03 * math.sin(T * 23), 0.65 + 0.03 * math.sin(T * 19), -205.0 - 2.3), look=(0.0, 0.0, -205.0 + 0.4), lens=22)
E.teo_z = lambda T: -205.0
E.labels = [('v', '35.700 km/h', YEL, 0.36, 30.15, 99, lambda T: (0.95, -0.35, -205.0 + 1.75))]
SHOTS.append(E)

# ---------------------------------------------------------------- F — CTA: quanto tempo dura a queda?
F_ = Shot('F', 32.90, 36.90, 'tunel', 'pergunta: Téo flutuando olha para a câmera e encolhe os ombros')
F_.prof = lambda T: 0.30
F_.speed = lambda T: 60.0 - 25.0 * sstep(32.9, 34.0, T)
F_.cam = lambda T: (lambda k: dict(pos=(0.1 + 0.5 * k, -2.9 + 0.5 * k, -205.0 + 0.9 - 0.2 * k), look=(0.0, 0.0, -205.0 + 1.1), lens=26))(sstep(32.9, 36.9, T))
F_.teo_z = lambda T: -205.0
F_.labels = [('q', 'quanto tempo?', WHITE, 0.30, 34.85, 99, lambda T: (0.0, 0.0, -205.0 + 2.55))]
SHOTS.append(F_)

# ---------------------------------------------------------------- G — 38 minutos: atravessa o planeta
G = Shot('G', 36.90, 40.50, 'corte', 'resposta: 38 min; Téo atravessa de polo a polo (tempo acelerado)')
G.cut = 'wedge'; G.sun = B_.sun; G.spin = lambda T: 0.0; G.tube = lambda T: 1.0
G.tphys = lambda T: F.T_HALF * sstep(37.25, 40.45, T) ** 1.0
G.marker = lambda T: on_axis(F.fall(G.tphys(T) if T < 40.45 else F.T_HALF - 1e-3)[0] / F.R * R)
G_cam = eased([(36.9, sph(VIEW + 4, 10, 40)), (40.5, sph(VIEW - 4, 6, 37))])
G.cam = lambda T: dict(pos=G_cam(T), look=(0.0, 0.0, -0.8), lens=40)
G.labels = [('t38', '38 min', YEL, 1.9, 37.05, 99, lambda T: (0.0, 0.0, 13.2))]
SHOTS.append(G)

# ---------------------------------------------------------------- H — chega parado na borda... e cai de volta (Polo Sul)
H = Shot('H', 40.50, 47.40, 'polo', 'Polo Sul: Téo sobe freando, para no nível da borda, não alcança e cai de volta (câmera lenta)')
H.pole_name = 'POLO SUL'
T_AP = 44.55; Z0_H = -7.0
G_VIS = 2 * (-Z0_H) / (T_AP - 41.0) ** 2
H.teo_z = lambda T: -0.5 * G_VIS * (T - T_AP) ** 2
H_cam = eased([(40.5, (5.2, -6.6, 2.2)), (44.5, (4.0, -5.4, 1.5)), (47.4, (3.2, -4.6, 2.6))])
H_look = eased([(40.5, (0.0, 0.0, -0.4)), (44.5, (0.0, 0.0, 0.6)), (47.4, (0.0, 0.0, -1.2))])
H.cam = lambda T: dict(pos=H_cam(T), look=H_look(T), lens=30)
H.labels = [('v0', 'v = 0', YEL, 0.36, 44.20, 45.9, lambda T: (1.35, -0.6, 2.25))]
SHOTS.append(H)

# ---------------------------------------------------------------- I — vai e volta para sempre
I = Shot('I', 47.40, 50.10, 'corte', 'oscilação: polo a polo e de volta (tempo acelerado)')
I.cut = 'wedge'; I.sun = B_.sun; I.spin = lambda T: 0.0; I.tube = lambda T: 1.0
I.tphys = lambda T: F.T_HALF + 3.6 * F.T_HALF * sstep(47.45, 50.1, T)       # continua de onde parou (no Polo Sul)
I.marker = lambda T: on_axis(F.fall(I.tphys(T))[0] / F.R * R)
I_cam = eased([(47.4, sph(VIEW - 4, 6, 37)), (50.1, sph(VIEW - 14, 10, 41))])
I.cam = lambda T: dict(pos=I_cam(T), look=(0.0, 0.0, -0.4), lens=40)
I.labels = [('iv', 'ida e volta: 76 min', YEL, 1.0, 48.05, 99, lambda T: (0.0, 0.0, 13.0))]
SHOTS.append(I)

# ---------------------------------------------------------------- J — vida real: 5.000 °C; buraco mais fundo: 12 km
J = Shot('J', 50.10, 58.80, 'corte', 'realidade: o túnel some; núcleo a mais de 5.000 °C; zoom no poço de Kola (12 km)')
J.cut = 'wedge'; J.sun = B_.sun; J.spin = lambda T: 0.0
J.tube = lambda T: 1.0 - sstep(50.9, 51.9, T)
J.heat = lambda T: 1.0 + 1.6 * sstep(52.7, 54.2, T) - 1.0 * sstep(55.2, 56.0, T)
J.kola = 69.0
KOLA = (math.cos(math.radians(69.0)) * R, 0.0, math.sin(math.radians(69.0)) * R)
J.clouds = lambda T: 1.0 - sstep(55.0, 55.8, T)
def _J_cam(T):
    """Aproximação contínua até a crosta perto de Kola: alvo vai do centro a Kola; distância cai em escala log (30 -> 1,5)."""
    kl = sstep(54.6, 56.6, T); kd = sstep(54.7, 57.3, T)
    tgt = tuple(a * (1 - kl) + b * kl for a, b in zip((0.0, 0.0, 0.0), add(KOLA, (0.0, 0.0, -0.18))))
    d0, d1 = sph(VIEW - 6, 6, 1.0), (0.10, 0.99, 0.05)
    dv = tuple(a * (1 - kd) + b * kd for a, b in zip(d0, d1)); n = math.sqrt(sum(x * x for x in dv)); dv = tuple(x / n for x in dv)
    dist = math.exp(math.log(30.0) * (1 - kd) + math.log(1.5) * kd)
    return dict(pos=add(tgt, dv, dist), look=tgt, lens=40 + 10 * kd)
J.cam = _J_cam
J.labels = [('calor', '> 5.000 °C', ORANGE, 1.0, 53.85, 55.3, lambda T: add(sph(VIEW, 0, 2.2), (0, 0, 1.6))),
            ('kola', 'buraco mais fundo: 12 km', RED, 0.030, 57.20, 99, lambda T: add(KOLA, (0.03, 0.05, -0.10))),
            ('raio', 'até o centro: 6.371 km ↓', WHITE, 0.028, 57.75, 99, lambda T: add(KOLA, (0.03, 0.05, -0.34)))]
SHOTS.append(J)

# ---------------------------------------------------------------- K — por que de polo a polo? (rotação)
K = Shot('K', 58.80, 62.50, 'corte', 'Terra girando em corte (octante): o túnel no eixo não sai do lugar; o túnel no Equador gira junto')
K.cut = 'octant'; K.sun = sph(20, 40, 1)
K.spin = lambda T: -0.55 + 0.32 * (T - 58.8)
K.tube = lambda T: 1.0
K.eq_tube = lambda T: sstep(61.0, 61.6, T)
EQ_TUBE_R = 0.012
K_cam = eased([(58.8, sph(VIEW + 5, 38, 38)), (62.5, sph(VIEW - 8, 46, 31))])
K.cam = lambda T: dict(pos=K_cam(T), look=(0.0, 0.0, 0.8), lens=40)
K.labels = [('eixo', 'no eixo: não sai do lugar', CYAN, 0.95, 59.55, 61.0, lambda T: (0.0, 0.0, 12.6)),
            ('gira', 'fora do eixo: gira junto', YEL, 0.95, 61.35, 99, lambda T: (0.0, 0.0, 12.6))]
SHOTS.append(K)

# ---------------------------------------------------------------- L — num túnel fora do eixo, você é empurrado contra a parede
L = Shot('L', 62.50, END, 'tunel', 'dentro de um túnel no Equador: o giro da Terra empurra Téo para o lado até bater na parede (tempo acelerado)')
L_T0 = 62.70
EQ = F.equatorial_drop(60.0, dt=0.05)
def _dev(tp):
    i = min(int(tp / 0.05), len(EQ) - 1); t, x, y, th = EQ[i]
    return math.hypot(x, y) * math.sin(math.atan2(y, x) - th)            # desvio lateral real (m), para leste
L.WALL = 3.0 - 0.38                                                      # centro do Téo encostado na parede
L.t_hit = next(t for t, x, y, th in EQ if math.hypot(x, y) * math.sin(math.atan2(y, x) - th) >= L.WALL)
L.TS = L.t_hit / (64.30 - L_T0)                                          # escala de tempo: bate em T = 64,30 s
L.T_HIT = L_T0 + L.t_hit / L.TS
L.tphys = lambda T: max(0.0, (T - L_T0) * L.TS)
L.lat = lambda T: min(_dev(L.tphys(T)), L.WALL)
L.prof = lambda T: 0.12
L.speed = lambda T: 20.0 + 130.0 * sstep(62.6, 63.6, T)
L.teo_z = lambda T: -205.0
L.cam = lambda T: dict(pos=(-0.6, -0.5, -205.0 - 4.2), look=(0.9, 0.0, -205.0 + 0.5), lens=15)
L.labels = [('parede', 'parede!', RED, 0.55, 64.32, 99, lambda T: (0.6, -0.6, -205.0 + 1.2))]
SHOTS.append(L)

BY_NAME = {s.name: s for s in SHOTS}
assert abs(SHOTS[-1].t1 - END) < 1e-9 and all(abs(a.t1 - b.t0) < 1e-9 for a, b in zip(SHOTS, SHOTS[1:]))

if __name__ == '__main__':
    for s in SHOTS: print(s.name, s.t0, s.t1, s.kind, len(s.frames), s.desc)
    print('L: bate na parede (desvio real 2,62 m) em t_fís =', round(L.t_hit, 1), 's; escala', round(L.TS, 2), 'x; T =', round(L.T_HIT, 2))
