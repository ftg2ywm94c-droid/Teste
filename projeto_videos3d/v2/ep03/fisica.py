"""Física do vídeo 03: queda num túnel pela Terra com a densidade real (modelo PREM, Dziewonski e Anderson, 1981).
Python puro (roda dentro do Blender). Unidades SI. Conferido contra Klotz (Am. J. Phys. 83, 231, 2015): 38 min 11 s."""
import math

R = 6371e3; G = 6.674e-11; OMEGA = 7.2921e-5   # raio médio, constante gravitacional, rotação sideral (rad/s)
CMB = 3480e3                                     # raio da fronteira manto-núcleo (2.891 km de profundidade)
ICB = 1221.5e3                                   # raio do núcleo interno

def rho(r):
    x = r / R; k = r / 1e3
    if k < 1221.5: return (13.0885 - 8.8381 * x * x) * 1e3
    if k < 3480: return (12.5815 - 1.2638 * x - 3.6426 * x * x - 5.5281 * x ** 3) * 1e3
    if k < 5701: return (7.9565 - 6.4761 * x + 5.5283 * x * x - 3.0807 * x ** 3) * 1e3
    if k < 5771: return (5.3197 - 1.4836 * x) * 1e3
    if k < 5971: return (11.2494 - 8.0298 * x) * 1e3
    if k < 6151: return (7.1089 - 3.8045 * x) * 1e3
    if k < 6346.6: return (2.6910 + 0.6924 * x) * 1e3
    if k < 6356: return 2.9e3
    if k < 6368: return 2.6e3
    return 1.02e3

# tabela g(r) por integração da massa
N = 4000
_r = [R * i / N for i in range(N + 1)]
_g = [0.0]; _m = 0.0
for i in range(1, N + 1):
    a, b = _r[i - 1], _r[i]; rm = 0.5 * (a + b)
    _m += 4 * math.pi * rm * rm * rho(rm) * (b - a)
    _g.append(G * _m / (b * b))
M_TERRA = _m

def g(r):
    r = abs(r)
    if r >= R: return G * M_TERRA / (r * r)
    x = r / R * N; i = min(int(x), N - 1); f = x - i
    return _g[i] * (1 - f) + _g[i + 1] * f

# queda ao longo do eixo (1D): z de +R a -R e volta. Integração RK4, passo 0,5 s.
def _fall_table(dt=0.5):
    z, v, t = R, 0.0, 0.0; T, Z, V = [0.0], [R], [0.0]
    def acc(z): return -math.copysign(g(z), z)
    while True:
        k1v = acc(z); k1z = v
        k2v = acc(z + 0.5 * dt * k1z); k2z = v + 0.5 * dt * k1v
        k3v = acc(z + 0.5 * dt * k2z); k3z = v + 0.5 * dt * k2v
        k4v = acc(z + dt * k3z); k4z = v + dt * k3v
        z += dt / 6 * (k1z + 2 * k2z + 2 * k3z + k4z); v += dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v); t += dt
        T.append(t); Z.append(z); V.append(v)
        if v >= 0 and t > 10: break          # parou do outro lado (z ≈ -R)
    return T, Z, V
_T, _Z, _V = _fall_table()
T_HALF = _T[-1]                              # ida (polo a polo), s
V_MAX = max(abs(x) for x in _V)

def fall(t):
    """Estado (z, v) no tempo t (s) da oscilação sem atrito, começando parado em z=+R."""
    t = t % (2 * T_HALF); sgn = 1.0
    if t > T_HALF: t -= T_HALF; sgn = -1.0
    i = min(int(t / 0.5), len(_T) - 2); f = (t - _T[i]) / 0.5
    return sgn * (_Z[i] * (1 - f) + _Z[i + 1] * f), sgn * (_V[i] * (1 - f) + _V[i + 1] * f)

def depth_time(d):
    """Tempo (s) para chegar à profundidade d (m) partindo da superfície."""
    for i in range(1, len(_Z)):
        if R - _Z[i] >= d: return _T[i]
    return T_HALF

def equatorial_drop(t_end=1200.0, dt=0.25):
    """Queda num túnel equatorial que gira com a Terra: integra no referencial inercial (plano do Equador),
    partindo da superfície com a velocidade de rotação ωR. Devolve lista de (t, x, y, ang_tunel)."""
    x, y, vx, vy, t = R, 0.0, 0.0, OMEGA * R, 0.0; out = [(0.0, x, y, 0.0)]
    def a(x, y):
        r = math.hypot(x, y); gg = g(r); return -gg * x / r, -gg * y / r
    while t < t_end:
        ax1, ay1 = a(x, y)
        ax2, ay2 = a(x + 0.5 * dt * vx, y + 0.5 * dt * vy)
        vx2, vy2 = vx + 0.5 * dt * ax1, vy + 0.5 * dt * ay1
        ax3, ay3 = a(x + 0.5 * dt * vx2, y + 0.5 * dt * vy2)
        vx3, vy3 = vx + 0.5 * dt * ax2, vy + 0.5 * dt * ay2
        ax4, ay4 = a(x + dt * vx3, y + dt * vy3)
        vx4, vy4 = vx + dt * ax3, vy + dt * ay3
        x += dt / 6 * (vx + 2 * vx2 + 2 * vx3 + vx4); y += dt / 6 * (vy + 2 * vy2 + 2 * vy3 + vy4)
        vx += dt / 6 * (ax1 + 2 * ax2 + 2 * ax3 + ax4); vy += dt / 6 * (ay1 + 2 * ay2 + 2 * ay3 + ay4); t += dt
        out.append((t, x, y, OMEGA * t))
    return out

if __name__ == '__main__':
    print(f'massa {M_TERRA:.4e} kg; g sup {g(R):.2f}; g na fronteira do núcleo {g(CMB):.2f} m/s²')
    print(f'ida: {T_HALF / 60:.2f} min ({int(T_HALF // 60)} min {T_HALF % 60:.0f} s); v máx {V_MAX:.0f} m/s = {V_MAX * 3.6:.0f} km/h')
    print(f'até a fronteira do núcleo (2.891 km): {depth_time(R - CMB) / 60:.1f} min')
    eq = equatorial_drop(600)
    for t, x, y, th in eq[::240]:
        r = math.hypot(x, y); ang = math.atan2(y, x) - th          # desvio angular em relação ao túnel (rad)
        print(f't={t:5.0f}s prof={(R - r) / 1e3:7.1f} km desvio lateral={r * math.sin(ang) / 1e3:8.2f} km')
