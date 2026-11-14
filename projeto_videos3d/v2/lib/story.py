"""Cinemática da história (sem dependência do Blender). Unidades SI; eixo X = sentido do carro, Y = esquerda do motorista, Z = cima.
Premissas (Queensland Gov.): reação 1,5 s, desaceleração 7 m/s² em pista seca.
tau = tempo da história em s; tau = 0 é o instante em que o menino entra na faixa do carro (perigo visível)."""
import math
REACT, DECEL = 1.5, 7.0
V60, V50 = 60 / 3.6, 50 / 3.6
X_KID = 0.0                 # ponto da rua onde o menino entra
X_HAZARD = -35.0            # frente do carro no instante do perigo (35 m antes)
LANE_R, LANE_L = -1.75, 1.75
CAR_LEN, CAR_W, WHEEL_R = 4.2, 1.8, 0.33
FRONT = CAR_LEN / 2         # origem do carro no centro; frente = x + 2,1

def car_front(tau, v0, t_react=REACT, x0=X_HAZARD, brake=True):
    """Posição da frente do carro e velocidade. Antes de tau=0 o carro anda a v0 constante."""
    if tau <= t_react or not brake:
        return x0 + v0 * tau, v0
    u = tau - t_react; ustop = v0 / DECEL
    if u >= ustop:
        return x0 + v0 * t_react + v0 * v0 / (2 * DECEL), 0.0
    return x0 + v0 * t_react + v0 * u - DECEL * u * u / 2, v0 - DECEL * u

def stop_tau(v0): return REACT + v0 / DECEL
def stop_dist(v0): return v0 * REACT + v0 * v0 / (2 * DECEL)

def speed_at_x(v0, x_from_hazard):
    """Velocidade (m/s) ao passar a x m do ponto do perigo."""
    r = v0 * REACT
    if x_from_hazard <= r: return v0
    v2 = v0 * v0 - 2 * DECEL * (x_from_hazard - r)
    return math.sqrt(v2) if v2 > 0 else 0.0

def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0); return t * t * (3 - 2 * t)

# --- menino ---------------------------------------------------------------
# trajetória em (x, y) + fase: corre do portão até a faixa, para ao ver o carro, ouve a freada e pula de volta.
KID_PATH = [(-2.6, -2.2, -9.0), (0.0, -0.15, -2.35), (1.2, 0.05, -2.05), (1.55, 0.05, -2.05), (2.0, -0.05, -4.15), (9.0, -0.05, -4.3)]
def kid_xy(tau):
    P = KID_PATH
    if tau <= P[0][0]: return P[0][1], P[0][2]
    for (t0, x0, y0), (t1, x1, y1) in zip(P, P[1:]):
        if tau <= t1:
            k = (tau - t0) / (t1 - t0)
            if t0 == 0.0: k = math.sin(k * math.pi / 2)            # desacelera ao ver o carro
            if t0 == 1.55: k = sstep(0, 1, k)                       # pulo
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    return P[-1][1], P[-1][2]
def kid_hop(tau):
    """Altura do pulo de volta (parábola) entre tau 1,55 e 2,0."""
    if 1.55 < tau < 2.0:
        u = (tau - 1.55) / 0.45; return 0.32 * 4 * u * (1 - u)
    return 0.0

# --- bola -----------------------------------------------------------------
BALL_R = 0.11
def ball_xy(tau):
    """Sai do jardim em tau=-5,9, cruza a rua e para no meio-fio oposto. Rola sem deslizar."""
    t0 = -5.9; y0, y1 = -8.5, 3.3
    if tau < t0: return 0.6, y0, 0.0
    u = tau - t0; v0 = 3.4; dec = 0.55
    s = min(v0 * u - dec * u * u / 2, y1 - y0) if u < v0 / dec else y1 - y0
    # pequenos quiques ao descer o meio-fio (y=-3,5)
    z = 0.0
    y = y0 + s
    return 0.6 + 0.02 * s, y, z

def collision_report(samples=4000, t0=-6, t1=6):
    """Distância mínima entre a lateral do carro (faixa direita) e o menino/bola ao longo do tempo."""
    worst_kid, worst_ball = 9e9, 9e9
    for i in range(samples):
        tau = t0 + (t1 - t0) * i / samples
        xf, _ = car_front(tau, V60); xr = xf - CAR_LEN
        ymin, ymax = LANE_R - CAR_W / 2, LANE_R + CAR_W / 2
        def gap(px, py, r):
            dx = max(xr - px, 0, px - xf); dy = max(ymin - py, 0, py - ymax)
            return math.hypot(dx, dy) - r
        kx, ky = kid_xy(tau); worst_kid = min(worst_kid, gap(kx, ky, 0.22))
        bx, by, _ = ball_xy(tau); worst_ball = min(worst_ball, gap(bx, by, BALL_R))
    return worst_kid, worst_ball

if __name__ == '__main__':
    print('parada 50:', round(stop_dist(V50), 2), 'm  60:', round(stop_dist(V60), 2), 'm')
    print('vel. do carro a 60 no ponto onde o de 50 para:', round(speed_at_x(V60, stop_dist(V50)) * 3.6, 1), 'km/h')
    xf, v = car_front(stop_tau(V60), V60); print('carro 60 para em x =', round(xf, 2), '(menino em 0)')
    for tau in (1.5, 1.75, 2.0, 2.19):
        print('tau', tau, 'frente', [round(a, 2) for a in car_front(tau, V60)], 'menino', [round(a, 2) for a in kid_xy(tau)])
    print('folga mínima menino/bola (m):', [round(a, 2) for a in collision_report()])
