"""Planos do vídeo 01 (distância de parada). T = tempo da narração (s); tau = tempo da história (ver lib/story.py).
Cada plano: intervalo [t0, t1) em T, mapa T->tau, câmera, atores visíveis e rótulos. Os tempos vêm de analysis/narracao/01_words.json."""
import math
from story import (car_front, V60, V50, REACT, DECEL, X_HAZARD, LANE_R, LANE_L, FRONT, kid_xy, kid_hop, ball_xy, sstep,
                   stop_dist, stop_tau, speed_at_x)

FPS = 30
END = 68.0   # narração termina em 67,16 s; 0,84 s de respiro final

# ---------------------------------------------------------------- interpolação suave (PCHIP: monótona, sem overshoot)
def pchip(knots):
    xs = [k[0] for k in knots]; ys = [k[1] for k in knots]; n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]; d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    if n == 2: m = [d[0], d[0]]
    else:
        m[0], m[-1] = d[0], d[-1]
        for i in range(1, n - 1):
            if d[i - 1] * d[i] <= 0: m[i] = 0.0
            else:
                w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    def f(x):
        if x <= xs[0]: return ys[0] + m[0] * (x - xs[0]) if n > 1 else ys[0]
        if x >= xs[-1]: return ys[-1] + m[-1] * (x - xs[-1])
        i = max(j for j in range(n - 1) if xs[j] <= x)
        t = (x - xs[i]) / h[i]; t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f

def ease(knots):
    """Interpola vetores (tuplas) com suavização smoothstep entre chaves: (T, valor). Velocidade zero nas chaves internas
    só quando os vizinhos invertem; usamos PCHIP por componente."""
    dim = len(knots[0][1]); fs = [pchip([(t, v[k]) for t, v in knots]) for k in range(dim)]
    return lambda T: tuple(f(T) for f in fs)

def lerp(a, b, t): return tuple(x + (y - x) * t for x, y in zip(a, b))

# ---------------------------------------------------------------- carro de cada "dia"
def cruise(x_at, T_at, v):
    return lambda T: (x_at + v * (T - T_at), v)

STORY_T0 = 17.30   # T em que tau = 0 no plano C

class Shot:
    def __init__(self, name, t0, t1, desc):
        self.name, self.t0, self.t1, self.desc = name, t0, t1, desc
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def car_center(xf): return xf - FRONT

SHOTS = []

# A — gancho: travelling lateral baixo, da roda até o Téo; passa a placa de 50
A = Shot('A', 0.0, 6.30, 'gancho: travelling lateral da roda ao motorista, placa 50 passando')
A.car = cruise(-175.0, 0.0, V60)
A.cam = lambda T: (lambda e, xc: dict(
    pos=(xc + 2.6 - 3.6 * e, LANE_R - 3.0 - 1.6 * e, 0.55 + 0.85 * e),
    look=(xc + 1.1 - 1.2 * e, LANE_R + 0.1 + 0.25 * e, 0.5 + 0.75 * e), lens=24 + 8 * e))(sstep(0.3, 5.8, T), car_center(A.car(T)[0]))
A.face = lambda T: {'neutral': 1.0}
SHOTS.append(A)

# B — "todo dia... via de cinquenta": grua aérea acompanhando, passa a 2ª placa
B = Shot('B', 6.30, 10.70, 'plano geral aéreo, grua descendo e acompanhando; placa de 50 em x=-75')
B.car = cruise(-120.0, 6.30, V60)
B.cam = lambda T: (lambda e, xc: dict(pos=(xc - 16 + 6 * e, LANE_R - 9 + 2.5 * e, 15 - 7 * e), look=(xc + 10 - 2 * e, LANE_R + 0.5, 0.0), lens=24 + 4 * e))(
    sstep(6.3, 10.7, T), car_center(B.car(T)[0]))
B.face = lambda T: {'neutral': 1.0}
SHOTS.append(B)

# C — bola e menino: câmera de perseguição atrás do carro, teleobjetiva comprimindo os 35 m
C = Shot('C', 10.70, 17.30, 'perseguição atrás/acima do carro; bola sai do quintal, menino corre atrás')
C.tau = lambda T: T - STORY_T0
C.cam = lambda T: (lambda e, xf: dict(pos=(xf - 9.5 + 2.0 * e, LANE_R - 1.2 + 0.2 * e, 3.4 - 0.4 * e), look=(xf + 30 + 3 * e, LANE_R - 1.2 * e, 0.3 + 0.3 * e),
                                       lens=30 + 42 * e))(sstep(10.7, 17.3, T), car_front(C.tau(T), V60)[0])
C.face = lambda T: {'neutral': 1.0}
SHOTS.append(C)

# D1 — reação do Téo (câmera lenta): de frente para o para-brisa
D1 = Shot('D1', 17.30, 21.33, 'câmera lenta: frente do carro, rosto do Téo pelo para-brisa')
D1.tau = pchip([(17.30, 0.0), (21.33, 0.62)])
D1.cam = lambda T: (lambda e, xc: dict(pos=(xc + 7.5 - 1.8 * e, LANE_R + 1.6 - 0.6 * e, 1.45 - 0.05 * e), look=(xc - 0.25, LANE_R + 0.38, 1.10), lens=55 + 30 * e))(
    sstep(17.3, 21.33, T), car_center(car_front(D1.tau(T), V60)[0]))
D1.face = lambda T: {'neutral': 1 - sstep(18.9, 19.5, T), 'alarm': sstep(18.9, 19.5, T)}
SHOTS.append(D1)

# D2 — 25 m de reação: vista alta atrás, faixa amarela crescendo; "sobraram só dez"
D2 = Shot('D2', 21.33, 27.80, 'grua alta atrás do carro: faixa de reação (25 m) e sobra de 10 m')
D2.tau = pchip([(21.33, 0.62), (24.90, 1.50), (27.80, 1.535)])
D2.cam = ease([(21.33, (-28.0, LANE_R - 3.0, 3.2, -12.0, LANE_R, 0.8)), (24.9, (-44.0, LANE_R - 4.0, 13.0, -8.0, LANE_R + 0.3, 0.0)),
               (27.8, (-40.0, LANE_R - 4.5, 15.5, -5.0, LANE_R + 0.3, 0.0))])
D2.cam = (lambda f: lambda T: (lambda v: dict(pos=v[:3], look=v[3:], lens=30 - 2 * sstep(21.33, 27.8, T)))(f(T)))(D2.cam)
D2.face = lambda T: {'alarm': 1.0}
D2.strips = ['react_story', 'gap10']
SHOTS.append(D2)

# E — CTA: tempo congelado, órbita controlada em volta do carro e do menino
E = Shot('E', 27.80, 31.80, 'tempo congelado no início da freada; órbita lenta')
E.tau = lambda T: 1.535
E.cam = lambda T: (lambda a, e: dict(pos=(-5.5 + 13.5 * math.cos(a), -1.8 + 13.5 * math.sin(a), 4.8 + 1.5 * e), look=(-5.0, -2.0, 0.4), lens=24))(
    math.radians(-140 + 70 * sstep(27.8, 31.8, T)), sstep(27.8, 31.8, T))
E.face = lambda T: {'alarm': 1.0}
E.strips = ['react_story', 'gap10']
SHOTS.append(E)

# F — simulação: duas faixas, 50 (azul) e 60 (vermelho); marcas de 35 m e 45 m
F = Shot('F', 31.80, 43.35, 'simulação lado a lado: frenagem ∝ v²; para em 35 m e 45 m')
F.T50, F.T60 = 35.60, 38.60   # instante em que cada carro cruza a linha do perigo
F.cam = ease([(31.8, (-37.0, -9.0, 1.4, -35.0, 0.0, 0.6)), (35.0, (-60.0, -6.0, 14.0, -18.0, 0.0, 0.0)),
              (39.5, (-50.0, -5.0, 22.0, -8.0, 0.0, 0.0)), (43.35, (-42.0, -4.0, 24.0, -3.0, 0.0, 0.0))])
F.cam = (lambda f: lambda T: (lambda v: dict(pos=v[:3], look=v[3:], lens=24 + 6 * sstep(31.8, 43.35, T)))(f(T)))(F.cam)
F.face = lambda T: {'focus': 1.0}
F.strips = ['sim50', 'sim60']
SHOTS.append(F)

# G — "no ponto exato...": carro a 50 já parado; o de 60 passa a 43 km/h ao lado (câmera baixa, lenta no final)
G = Shot('G', 43.35, 50.30, 'carro de 50 parado; carro de 60 passa ao lado a 43 km/h')
G.tau60 = pchip([(43.35, 0.40), (46.95, 2.14), (50.30, 2.215)])
G.cam = ease([(43.35, (3.5, -6.2, 0.9, -12.0, -0.3, 0.9)), (46.95, (3.0, -6.6, 1.1, -1.0, 0.0, 0.8)), (50.30, (2.2, -7.0, 1.6, 0.0, 0.0, 0.8))])
G.cam = (lambda f: lambda T: (lambda v: dict(pos=v[:3], look=v[3:], lens=26 + 6 * sstep(46.0, 50.3, T)))(f(T)))(G.cam)
G.face = lambda T: {'focus': 1.0}
G.strips = ['sim50', 'mark50']
SHOTS.append(G)

# H — desfecho: o menino pula de volta; o carro passa e para 10 m depois
H = Shot('H', 50.30, 59.45, 'menino pula para a calçada; carro passa e para 10 m depois')
H.tau = pchip([(50.30, 1.40), (54.90, 2.02), (57.75, 3.88), (59.45, 3.95)])
H.cam = ease([(50.30, (-4.5, 5.6, 1.15, 0.0, -2.4, 0.75)), (54.9, (-3.8, 5.8, 1.25, 0.2, -3.4, 0.65)),
              (56.4, (-1.5, 6.4, 1.6, 3.5, -2.6, 0.7)), (59.45, (0.5, 8.0, 2.6, 4.2, -2.4, 0.5))])
H.cam = (lambda f: lambda T: (lambda v: dict(pos=v[:3], look=v[3:], lens=46 - 18 * sstep(54.6, 57.0, T)))(f(T)))(H.cam)
H.face = lambda T: {'alarm': 1 - sstep(57.8, 58.6, T), 'relief': sstep(57.8, 58.6, T)}
H.strips = ['gap10_after']
SHOTS.append(H)

# I — epílogo: o Téo a 50, passando a placa; grua sobe para o plano geral
I = Shot('I', 59.45, END, 'epílogo a 50 km/h: travelling lateral que sobe para plano geral')
I.car = cruise(-100.0, 59.45, V50)
I.cam = lambda T: (lambda e, xc: dict(pos=(xc + 3.5 - 7 * e, LANE_R - 4.2 - 7 * e, 1.3 + 13 * e), look=(xc + 0.5 + 6 * e, LANE_R + 0.3, 0.9 - 0.7 * e), lens=28 - 4 * e))(
    sstep(59.6, 67.6, T), car_center(I.car(T)[0]))
I.face = lambda T: {'relief': 1.0}
SHOTS.append(I)

BY_NAME = {s.name: s for s in SHOTS}
assert abs(SHOTS[-1].t1 - END) < 1e-9 and all(abs(a.t1 - b.t0) < 1e-9 for a, b in zip(SHOTS, SHOTS[1:]))
