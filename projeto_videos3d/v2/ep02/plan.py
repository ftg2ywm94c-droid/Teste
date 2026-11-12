"""Planos do vídeo 02 (E se a Terra parasse de girar?). T = tempo da narração (s), amarrado a analysis/narracao/02_words.json.
Cada plano: intervalo [t0, t1), tipo de cenário, câmera e estados (giro da Terra, vento, mar, rótulos)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..')]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 76.5            # narração termina em 75,73 s
LAT_B, LON_B = -15.8, -47.9   # Brasília (marcador "você")

def integ(w, t0, T, n=400):
    """∫ w(t) dt de t0 até T (regra do trapézio)."""
    if T <= t0: return 0.0
    h = (T - t0) / n; s = 0.5 * (w(t0) + w(T))
    for i in range(1, n): s += w(t0 + i * h)
    return s * h

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []      # (id, texto, cor, tamanho, t_on, t_off, pos(T)->xyz)
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def ll(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return (r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la))
def rotz(p, a): return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a), p[2])
def add(a, b, k=1.0): return tuple(x + k * y for x, y in zip(a, b))
def shake(T, t0, t1, amp, f=17.0):
    k = sstep(t0, t0 + 0.06, T) * (1 - sstep(t0 + 0.1, t1, T))
    return (amp * k * math.sin(T * f * 6.28), amp * k * math.sin(T * f * 5.1 + 1.3), amp * 0.6 * k * math.sin(T * f * 7.3 + 2.1))

YEL, RED, WHITE, BLUE = (1.0, 0.80, 0.08), (1.0, 0.25, 0.15), (0.97, 0.97, 0.97), (0.45, 0.75, 1.0)
SHOTS = []
R = 10.0

# ---------------------------------------------------------------- A — gancho: câmera presa ao Brasil; as estrelas correm; tudo para
A = Shot('A', 0.0, 6.90, 'globe', 'gancho: girando com a Terra; para em "parasse?"')
A_w = lambda t: 0.30 * (1 - sstep(5.05, 5.75, t))
A.spin = lambda T: integ(A_w, 0.0, T)
A.sun = (math.cos(-0.35), math.sin(-0.35), 0.18)
def _A_cam(T):
    th = A.spin(T); e = sstep(0.0, 6.9, T)
    pos_e = ll(LAT_B + 26 - 6 * e, LON_B + 8, 46 - 10 * e)
    look_e = ll(LAT_B + 16, LON_B + 3, 9.0)
    s = shake(T, 5.05, 6.3, 0.18)
    return dict(pos=add(rotz(pos_e, th), s), look=add(rotz(look_e, th), s, 0.5), lens=40 + 6 * e)
A.cam = _A_cam
A.marker = True
A.labels = [('voce', 'você', YEL, 0.85, 1.05, 99, lambda T: rotz(ll(LAT_B + 3.2, LON_B, 11.6), A.spin(T))),
            ('vel', '+1.000 km/h', WHITE, 0.95, 2.45, 99, lambda T: rotz(ll(LAT_B - 4.5, LON_B + 2, 11.9), A.spin(T)))]
SHOTS.append(A)

# ---------------------------------------------------------------- B — a Terra gira uma vez por dia; o Equador a 1.670 km/h
B_ = Shot('B', 6.90, 14.20, 'globe', 'contexto: giro, linha do Equador, 1.670 km/h')
B_.spin = lambda T: 1.2 + 0.16 * (T - 6.9)
B_.sun = (0.55, -0.80, 0.22)
B_cam = ease([(6.9, (6.0, -37.0, 15.0)), (10.5, (14.0, -30.0, 7.0)), (14.2, (17.0, -25.0, 3.6))])
B_look = ease([(6.9, (0.0, 0.0, 1.5)), (10.5, (1.0, -2.0, 0.6)), (14.2, (2.5, -3.5, 0.2))])
B_.cam = lambda T: dict(pos=B_cam(T), look=B_look(T), lens=40)
B_.equator = lambda T: sstep(9.25, 9.85, T)
B_.arrow = lambda T: sstep(10.9, 11.5, T)
B_.labels = [('dia', '1 volta por dia', WHITE, 0.85, 7.35, 10.6, lambda T: (1.0, -6.0, 11.4)),
             ('v1670', '1.670 km/h', RED, 1.0, 11.0, 99, lambda T: (8.6, -9.4, 2.4))]
SHOTS.append(B_)

# ---------------------------------------------------------------- C — orla: você, o ar e o mar vão junto
C = Shot('C', 14.20, 19.90, 'orla', 'você, o ar e o mar vão junto; ninguém sente')
TEO_SPOT = (3.2, -0.2)         # Téo na areia, olhando o mar; coqueiro logo a leste
PALM_HUG = (4.65, 0.55)
C_cam = ease([(14.2, (8.6, -9.4, 2.3)), (19.9, (8.4, -8.0, 2.2))])
C_look = ease([(14.2, (-2.5, 6.0, 1.4)), (19.9, (-2.0, 6.0, 1.3))])
C.cam = lambda T: dict(pos=C_cam(T), look=C_look(T), lens=24)
C.wind = lambda T: 0.0
C.labels = [('voce', 'você', YEL, 0.6, 14.42, 99, lambda T: (3.2, -0.2, 2.55)),
            ('ar', 'ar', WHITE, 1.5, 15.30, 99, lambda T: (-6.0, 16.0, 10.2)),
            ('mar', 'mar', BLUE, 0.75, 15.90, 99, lambda T: (-2.6, 0.2, 1.75))]
C.arrows = [('voce', (3.25, -0.2, 2.08), 0.9, 14.42), ('ar', (-6.6, 16.0, 8.6), 2.8, 15.30), ('mar', (-3.3, 0.2, 1.0), 1.4, 15.90)]
SHOTS.append(C)

# ---------------------------------------------------------------- D — o planeta trava: o chão para, o ar e o mar seguem para leste
D = Shot('D', 19.90, 28.20, 'orla', 'trava: tranco, Téo se agarra ao coqueiro, vento e mar correm para o leste')
T_TRAVA, T_CHAO, T_VENTO = 21.16, 23.10, 24.05
D.wind = lambda T: 0.25 * sstep(T_TRAVA, T_TRAVA + 0.4, T) * (1 - sstep(T_TRAVA + 0.5, T_CHAO, T)) + sstep(T_CHAO + 0.1, T_VENTO + 0.9, T)
D_cam = ease([(19.9, (6.6, -5.6, 1.6)), (21.0, (6.5, -5.3, 1.6)), (23.0, (6.6, -5.0, 1.6)), (25.4, (9.0, -9.6, 2.4)), (28.2, (10.0, -11.5, 3.0))])
D_look = ease([(19.9, (3.6, 0.4, 1.35)), (21.0, (3.7, 0.4, 1.35)), (23.0, (4.0, 0.5, 1.3)), (25.4, (0.5, 5.0, 1.9)), (28.2, (-1.0, 6.0, 2.3))])
def _D_cam(T):
    s = shake(T, T_TRAVA, T_TRAVA + 0.9, 0.09); s2 = shake(T, T_CHAO, T_CHAO + 1.2, 0.06, 11)
    w = D.wind(T); s3 = (0.012 * w * math.sin(T * 41), 0.01 * w * math.sin(T * 37 + 1), 0.008 * w * math.sin(T * 29))
    p = add(add(add(D_cam(T), s), s2), s3)
    return dict(pos=p, look=add(D_look(T), s, 0.6), lens=30 - 6 * sstep(23.4, 25.4, T))
D.cam = _D_cam
D.labels = [('chao', 'chão: 0 km/h', WHITE, 0.2, 23.15, 99, lambda T: (5.9, -1.0, 0.35)),
            ('vento', 'ar e mar: 1.670 km/h', RED, 1.25, 25.0, 99, lambda T: (-6.0, 12.0, 6.6))]
D.arrows = [('vento', (-6.6, 12.0, 5.3), 3.6, 25.0)]
SHOTS.append(D)

# ---------------------------------------------------------------- E — ônibus freando de repente
E = Shot('E', 28.20, 33.30, 'bus', 'analogia: ônibus freia, passageiros vão para a frente')
BUS_X, BUS_V, BUS_DEC, T_BRAKE = 36.8, 11.0, 6.5, 29.16
def bus_y(T):
    if T < T_BRAKE: return BUS_V * (T - T_BRAKE)
    t = min(T - T_BRAKE, BUS_V / BUS_DEC); return BUS_V * t - 0.5 * BUS_DEC * t * t
def bus_v(T):
    if T < T_BRAKE: return BUS_V
    return max(BUS_V - BUS_DEC * (T - T_BRAKE), 0.0)
E.bus_y, E.bus_v, E.T_BRAKE = bus_y, bus_v, T_BRAKE
def _E_cam(T):
    yb = bus_y(T); k = sstep(29.0, 31.6, T)
    d = sstep(30.6, 34.5, T)   # v0.3: recuo lento para não congelar com o ônibus parado
    pos = (31.3 + 0.8 * k - 0.6 * d, yb - 1.4 - 2.0 * k - 1.2 * d, 2.25 + 0.2 * k + 0.25 * d)
    look = (36.4, yb + 0.7 - 0.4 * k, 2.15)
    return dict(pos=pos, look=look, lens=26 - 2 * k - 1.5 * d)
E.cam = _E_cam
E.wind = lambda T: 0.0
E.labels = [('bus', '1.600 km/h → 0', RED, 0.32, 30.85, 99, lambda T: (35.0, bus_y(T) + 0.5, 3.75))]
SHOTS.append(E)

# ---------------------------------------------------------------- F — CTA: Equador ou polos?
F = Shot('F', 33.30, 39.40, 'globe', 'pergunta: Equador ou polos?')
F.spin = lambda T: 0.9
F.sun = (0.75, -0.55, 0.40)
F.cam = lambda T: (lambda a, r: dict(pos=(r * math.cos(math.radians(a)) * math.cos(math.radians(30)), r * math.sin(math.radians(a)) * math.cos(math.radians(30)),
                                           r * math.sin(math.radians(30))), look=(0, 0, 1.8), lens=40))(-60 + 14 * sstep(33.3, 39.4, T), 38.0)
F.equator = lambda T: sstep(35.1, 35.6, T)
F.polar = lambda T: sstep(36.1, 36.6, T)
F.labels = [('eq', 'Equador?', RED, 1.5, 35.15, 99, lambda T: (8.2, -9.4, -1.2)),
            ('polo', 'Polos?', BLUE, 1.5, 36.15, 99, lambda T: (0.6, -1.0, 13.2))]
SHOTS.append(F)

# ---------------------------------------------------------------- G — resposta: perto dos polos o chão quase não se move
G = Shot('G', 39.40, 43.10, 'globe', 'polos: velocidade ~0; faixas de velocidade')
G.spin = lambda T: 0.9
G.sun = F.sun
def _G_cam(T):
    e = sstep(39.4, 43.1, T); a = -46 + 6 * e; el = 30 + 32 * e; r = 38 - 9 * e
    return dict(pos=(r * math.cos(math.radians(a)) * math.cos(math.radians(el)), r * math.sin(math.radians(a)) * math.cos(math.radians(el)), r * math.sin(math.radians(el))),
                look=(0, 0, 1.8 + 4.0 * e), lens=40)
G.cam = _G_cam
G.equator = lambda T: 1.0
G.polar = lambda T: 1.0
G.bands = lambda T: sstep(39.5, 40.3, T)
G.labels = [('polo0', '≈ 0 km/h', BLUE, 1.3, 40.05, 99, lambda T: (0.8, -1.2, 12.8)),
            ('eq1670', '1.670 km/h', RED, 1.2, 40.7, 99, lambda T: (8.6, -7.6, 0.5))]
SHOTS.append(G)

# ---------------------------------------------------------------- H — vento 4x a maior rajada; o mar invade
H = Shot('H', 43.10, 51.70, 'orla', 'tempestade: barras 408 x 1.670 km/h; o mar avança sobre a orla')
H.wind = lambda T: 1.0
T_MAR = 48.60
H.surge = lambda T: sstep(T_MAR, 51.7, T)
H_cam = ease([(43.1, (-6.0, -42.0, 11.0)), (47.5, (-8.0, -38.0, 12.0)), (51.7, (-12.0, -32.0, 14.0))])
H_look = ease([(43.1, (14.0, 8.0, 1.5)), (47.5, (16.0, 6.0, 2.0)), (51.7, (20.0, 4.0, 1.0))])
H.cam = lambda T: dict(pos=add(H_cam(T), (0.03 * math.sin(T * 31), 0.02 * math.sin(T * 27), 0.03 * math.sin(T * 23))), look=H_look(T), lens=28)
H.bars = dict(origin=(1.0, -27.5, 12.6), t_big=44.15, t_small=46.75, t_x4=47.45)
SHOTS.append(H)

# ---------------------------------------------------------------- I — parada lenta: um dia duraria um ano
I = Shot('I', 51.70, 60.50, 'orbit', 'parada lenta: Terra sem giro em volta do Sol; 6 meses de dia, 6 de noite')
ORB_R, I_ER, SUN_R = 11.0, 2.0, 3.4
PSI0 = math.radians(-90)
I.psi = lambda T: PSI0 + math.pi * sstep(54.35, 59.6, T)
I_wspin = lambda t: 1.6 * (1 - sstep(51.8, 54.3, t))
TH_END = PSI0 + math.pi - math.radians(LON_B)
I.spin = lambda T: TH_END - integ(I_wspin, T, 54.4) if T < 54.4 else TH_END
def _I_cam(T):
    ps = I.psi(T); E_ = (ORB_R * math.cos(ps), ORB_R * math.sin(ps), 0.0)
    rin = (-math.cos(ps), -math.sin(ps), 0.0); tg = (-math.sin(ps), math.cos(ps), 0.0)
    k = sstep(51.7, 55.2, T)
    d = 30 - 23.0 * k; h = 14 - 13.0 * k; up = tuple((1 - k) * a + k * b for a, b in zip((0, 0, 1), rin))
    pos = add(add(E_, tg, d), (0, 0, h)); look = add(E_, rin, 5.0 - 3.0 * k)
    return dict(pos=pos, look=look, lens=22, up=up)
I.cam = _I_cam
I.earth_pos = lambda T: (ORB_R * math.cos(I.psi(T)), ORB_R * math.sin(I.psi(T)), 0.0)
def _I_lbl(off):
    def f(T):
        ps = I.psi(T); E_ = I.earth_pos(T); rin = (-math.cos(ps), -math.sin(ps), 0.0)
        return add(E_, rin, off)
    return f
I.labels = [('ano', '1 dia = 1 ano', WHITE, 0.62, 54.40, 56.3, _I_lbl(3.0)),
            ('sol', '6 meses de sol', YEL, 0.62, 56.45, 58.85, _I_lbl(3.0)),
            ('noite', '6 meses de noite', BLUE, 0.62, 58.95, 99, _I_lbl(3.0))]
SHOTS.append(I)

# ---------------------------------------------------------------- J — os mares escorrem para os polos: um continente gigante
J = Shot('J', 60.50, 68.90, 'globe', 'migração dos oceanos para os polos (modelo Fraczek/Esri, relevo NOAA ETOPO5)')
J.spin = lambda T: math.radians(20)
J.sun = (math.cos(math.radians(-10)), math.sin(math.radians(-10)), 0.45)
J.ocean = lambda T: sstep(61.75, 66.2, T)
def _J_cam(T):
    e = sstep(60.5, 68.9, T); a = -2 + 8 * e; el = 6 + 30 * e; r = 37 + 4 * e
    return dict(pos=(r * math.cos(math.radians(a)) * math.cos(math.radians(el)), r * math.sin(math.radians(a)) * math.cos(math.radians(el)), r * math.sin(math.radians(el))),
                look=(0, 0, 0.5 + 1.0 * e), lens=40)
J.cam = _J_cam
J.labels = [('oceanoN', 'oceano', BLUE, 1.3, 64.35, 99, lambda T: (4.0, 1.5, 11.6)),
            ('cont', 'continente gigante', YEL, 1.1, 65.7, 99, lambda T: (11.6, 2.0, -0.6))]
SHOTS.append(J)

# ---------------------------------------------------------------- K — a boa notícia: desacelera menos de 2 ms por século
K = Shot('K', 68.90, END, 'globe', 'final: Terra girando normalmente, Lua ao fundo')
K.spin = lambda T: 0.4 + 0.10 * (T - 68.9)
K.sun = (math.cos(math.radians(15)), math.sin(math.radians(15)), 0.15)
K_cam = ease([(68.9, (24.0, -14.0, 6.0)), (72.5, (30.0, -22.0, 5.0)), (76.5, (36.0, -32.0, 4.0))])
K_look = ease([(68.9, (0.0, 0.0, 0.5)), (76.5, (-4.0, 6.0, 1.0))])
K.cam = lambda T: dict(pos=K_cam(T), look=K_look(T), lens=38)
K.moon = (-60.0, 85.0, 14.0)
SHOTS.append(K)

BY_NAME = {s.name: s for s in SHOTS}
assert abs(SHOTS[-1].t1 - END) < 1e-9 and all(abs(a.t1 - b.t0) < 1e-9 for a, b in zip(SHOTS, SHOTS[1:]))
