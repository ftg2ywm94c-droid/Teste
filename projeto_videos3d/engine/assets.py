"""Biblioteca de assets procedurais: personagem rigado, carro, cenário de bairro."""
import numpy as np
from .rt import Prim, Frame, V, F, norm, rot_x, rot_y, rot_z, flat

def sstep(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def vnoise(x, z):
    x = np.asarray(x, np.float64); z = np.asarray(z, np.float64)
    xi, zi = np.floor(x), np.floor(z); fx, fz = x - xi, z - zi
    h = lambda i, j: np.modf(np.sin(i * 127.1 + j * 311.7) * 43758.5453)[0] % 1.0
    ux, uz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    return ((h(xi, zi) * (1 - ux) + h(xi + 1, zi) * ux) * (1 - uz) + (h(xi, zi + 1) * (1 - ux) + h(xi + 1, zi + 1) * ux) * uz).astype(F)
def mix(a, b, t): return a + (b - a) * np.asarray(t, F)[..., None]

# ------------------------------------------------------------------ PERSONAGEM
SKIN = V(1.0, 0.86, 0.66); CAP = V(0.95, 0.42, 0.10); SHIRT = V(0.10, 0.62, 0.60); PANTS = V(0.16, 0.20, 0.42)
INK = V(0.06, 0.05, 0.08); BLUSH = V(1.0, 0.55, 0.50)
DEF_EXPR = dict(eye_open=1.0, wide=0.0, brow=0.0, smile=0.6, mouth_open=0.0, gaze=0.0)

def head_shader(ex):
    def sh(pl, nl, pw):
        x, y, z = pl[:, 0], pl[:, 1], pl[:, 2]; c = np.broadcast_to(SKIN, pl.shape).copy(); front = z > 0.15
        capd = y * 0.94 - z * 0.34
        c = np.where((capd > 0.36)[:, None], np.where((capd < 0.44)[:, None], CAP * 0.6, CAP), c)
        face = front & (capd <= 0.36)
        c = np.where((face & ((np.abs(x) - 0.50) ** 2 + (y + 0.20) ** 2 < 0.012))[:, None], mix(SKIN, BLUSH, 0.7), c)
        rx = 0.085 * (1 + 0.35 * ex['wide']); ry = max(0.018, 0.150 * ex['eye_open'] * (1 + 0.35 * ex['wide']))
        exx = np.abs(x - ex['gaze'] * 0.05) - 0.27; eyy = y - 0.02
        eye = (exx / rx) ** 2 + (eyy / ry) ** 2 < 1
        hl = ((exx + 0.03) / (rx * .35)) ** 2 + ((eyy - ry * .45) / (rx * .35)) ** 2 < 1
        c = np.where((face & eye)[:, None], np.where((hl & (ry > .06))[:, None], V(1, 1, 1), INK), c)
        if abs(ex['brow']) > 0.05:  # sobrancelha: segmento inclinado
            by = 0.02 + ry + 0.07 + 0.06 * max(ex['brow'], 0) + exx * (-0.9 * ex['brow'] if ex['brow'] < 0 else 0.25)
            c = np.where((face & (np.abs(y - by) < 0.022) & (np.abs(exx) < 0.11))[:, None], INK, c)
        mo = ex['mouth_open']
        if mo > 0.25:
            mouth = (x / (0.10 + 0.03 * mo)) ** 2 + ((y + 0.36) / (0.04 + 0.11 * mo)) ** 2 < 1
            c = np.where((face & mouth)[:, None], np.where(((y + 0.36) < -0.03)[:, None], V(0.85, 0.3, 0.3), V(0.25, 0.05, 0.08)), c)
        else:
            my = -0.33 - ex['smile'] * 0.10 + ex['smile'] * 2.2 * x * x
            c = np.where((face & (np.abs(y - my) < 0.024) & (np.abs(x) < 0.19))[:, None], INK, c)
        return c
    return sh

def shirt_shader(pl, nl, pw):
    c = np.broadcast_to(SHIRT, pl.shape).copy()
    c = np.where(((np.abs(pl[:, 0]) < 0.06) & (pl[:, 2] > 0))[:, None], SHIRT * 1.45, c)       # zíper
    c = np.where((pl[:, 1] < -0.62)[:, None], SHIRT * 0.62, c)                                    # barra
    return c

class Path:
    """Curva (polilinha densa) parametrizada por comprimento de arco."""
    def __init__(s, pts):
        s.p = np.asarray(pts, np.float64); d = np.linalg.norm(np.diff(s.p, axis=0), axis=1)
        s.s = np.r_[0, np.cumsum(d)]; s.len = s.s[-1]
    def at(s, q):
        if q <= 0: t = norm(s.p[1] - s.p[0]); return s.p[0] + t * q, t
        if q >= s.len: t = norm(s.p[-1] - s.p[-2]); return s.p[-1] + t * (q - s.len), t
        i = min(np.searchsorted(s.s, q) - 1, len(s.p) - 2); u = (q - s.s[i]) / (s.s[i + 1] - s.s[i])
        j0, j1 = max(i - 1, 0), min(i + 2, len(s.p) - 1)
        t = norm(mix(norm(s.p[i + 1] - s.p[j0]), norm(s.p[j1] - s.p[i]), u))
        return s.p[i] + (s.p[i + 1] - s.p[i]) * u, t
def bezier(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2, p3 = map(lambda q: np.asarray(q, np.float64), (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3

STRIDE = 0.85; HIP = 0.53; LEG = 0.29
def foot_state(path, s, off, side):
    """Pé plantado em coordenada de MUNDO durante o apoio (sem foot sliding)."""
    u = s / STRIDE - off; n = np.floor(u); fr = u - n; a = (n + off + 0.25) * STRIDE
    if fr < 0.5: q, lift, pitch = a, 0.0, 0.0
    else:
        e = (fr - .5) / .5; es = e * e * (3 - 2 * e); q = a + STRIDE * es
        lift = 0.13 * np.sin(np.pi * es) ** 1.2; pitch = 0.55 * np.sin(np.pi * e) * (1 - 1.6 * e)
    p, t = path.at(q); sd = np.array([t[1], -t[0]])
    xz = p + sd * side * 0.105
    return V(xz[0], lift, xz[1]), V(t[0], 0, t[1]), pitch, fr

def character(path, s, walk=1.0, hop=0.0, lean=0.0, head_yaw=0.0, head_pitch=0.0, arm_raise=0.0, squash=0.0, expr=None, group=100):
    ex = dict(DEF_EXPR); ex.update(expr or {})
    kw = dict(group=group, outline=1); P = []
    p, t = path.at(s); fwd = V(t[0], 0, t[1]); up = V(0, 1, 0); side = np.cross(up, fwd)
    yaw = np.arctan2(fwd[0], fwd[2]); ph = 2 * np.pi * s / STRIDE
    hipy = HIP + 0.028 * np.sin(ph) ** 2 * walk + hop - 0.05 * squash
    root = Frame(rot_y(yaw) @ rot_x(lean), (p[0], hipy, p[1]))
    sway = 0.022 * np.sin(ph) * walk
    for sd, off in ((1, 0.0), (-1, 0.5)):
        ft, ff, pitch, fr = foot_state(path, s, off, sd); ft = ft + up * hop
        H = root.pt((sd * 0.10 + sway, 0, 0)); ank = ft + up * 0.07 - ff * 0.03
        d = ank - H; L = min(np.linalg.norm(d), 2 * LEG * 0.999); dn = d / np.linalg.norm(d)
        bend = norm(fwd - dn * (fwd @ dn)); ca = L / (2 * LEG)
        knee = H + dn * LEG * ca + bend * LEG * np.sqrt(max(0, 1 - ca * ca)); ank = H + dn * L
        P += [Prim('cap', flat(PANTS), a=H, b=knee, r=0.058, **kw), Prim('cap', flat(PANTS * 0.92), a=knee, b=ank, r=0.052, **kw)]
        fyaw = np.arctan2(ff[0], ff[2]); sf = Frame(rot_y(fyaw) @ rot_x(pitch), ank - up * 0.02)
        P.append(sf.prim('sph', flat((0.93, 0.93, 0.95)), pos=(0, 0, 0.055), scale=(0.075, 0.055, 0.135), **kw))
    tor = root.child(rot_x(0.05 * walk) @ rot_y(0.10 * np.sin(ph) * walk), (sway, 0.28, 0))
    P.append(tor.prim('sph', shirt_shader, scale=(0.235, 0.31 * (1 - .12 * squash), 0.195), **kw))
    P.append(tor.prim('sph', flat((0.98, 0.72, 0.12)), pos=(0, 0.04, -0.19), scale=(0.17, 0.20, 0.10), **kw))  # mochila
    for sd in (1, -1):
        a = -0.75 * np.cos(ph) * sd * walk; sh = (sd * 0.215, 0.15, 0)
        ud = norm(V(sd * 0.22, -np.cos(a), np.sin(a))); fd = norm(V(sd * 0.10, -np.cos(a + 0.55 * walk + 0.15), np.sin(a + 0.55 * walk + 0.15)))
        ud = norm(mix(ud, norm(V(sd * 0.75, 0.62, 0.15)), arm_raise)); fd = norm(mix(fd, norm(V(sd * 0.25, 1.0, 0.25)), arm_raise))
        el = V(*sh) + ud * 0.21; hd = el + fd * 0.20
        P += [tor.cap(flat(SHIRT * 0.9), sh, el, 0.05, **kw), tor.cap(flat(SHIRT * 0.9), el, hd, 0.046, **kw),
              tor.prim('sph', flat(SKIN), pos=hd + fd * 0.03, scale=(0.066,) * 3, **kw)]
    hd = tor.child(rot_y(head_yaw) @ rot_x(head_pitch - 0.04 * walk * np.cos(2 * ph)), (0, 0.63 - 0.03 * squash, 0.02))
    P.append(hd.prim('sph', head_shader(ex), scale=(0.40,) * 3, **kw))
    P.append(hd.prim('sph', flat(CAP * 0.8), pos=(0, 0.215, 0.36), scale=(0.25, 0.03, 0.19), R=rot_x(0.22), **kw))  # aba
    P.append(hd.prim('sph', flat(CAP * 0.6), pos=(0, 0.415, -0.13), scale=(0.05,) * 3, **kw))
    return P, dict(head=hd.t.copy(), root=V(p[0], 0, p[1]), fwd=fwd)

# ------------------------------------------------------------------ CARRO
def wheel_shader(pl, nl, pw):
    r = np.hypot(pl[:, 0], pl[:, 2]); ang = np.arctan2(pl[:, 2], pl[:, 0])
    c = np.broadcast_to(V(0.07, 0.07, 0.08), pl.shape).copy(); capf = np.abs(pl[:, 1]) > 0.99
    hub = capf & (r < 0.62); spoke = hub & ((np.abs(np.sin(ang * 2.5)) < 0.35) | (r < 0.22))
    c = np.where(hub[:, None], V(0.45, 0.47, 0.5), c); c = np.where(spoke[:, None], V(0.88, 0.9, 0.92), c)
    return c
def car(x, z, dist, pitch=0.0, drop=0.0, body=(0.93, 0.25, 0.42), group=200):
    """Carro olhando para +x. Rodas giram conforme a distância percorrida."""
    kw = dict(group=group, outline=2); B = V(*body); P = []
    base = Frame(rot_y(np.pi / 2), (x, 0, z))                      # local: z frente, x lateral
    bd = base.child(rot_x(pitch), (0, 0.50 - drop, 0))
    def body_sh(pl, nl, pw):
        c = np.broadcast_to(B, pl.shape).copy()
        c = np.where((pl[:, 1] < -0.45)[:, None], B * 0.45, c)
        c = np.where(((np.abs(pl[:, 1] - 0.15) < 0.06))[:, None], V(1, 1, 1) * 0.95, c)
        return c
    def cabin_sh(pl, nl, pw):
        c = np.broadcast_to(B, pl.shape).copy()
        glass = (pl[:, 1] > 0.12) & (pl[:, 1] < 0.78) & ~((np.abs(pl[:, 2] + 0.05) < 0.07) & (np.abs(pl[:, 0]) > 0.6))
        return np.where(glass[:, None], V(0.10, 0.16, 0.26), c)
    P.append(bd.prim('box', body_sh, pos=(0, 0.02, 0), scale=(0.78, 0.26, 1.72), gloss=0.5, **kw))
    P.append(bd.prim('sph', flat(B), pos=(0, 0.10, 1.30), scale=(0.77, 0.26, 0.62), gloss=0.5, **kw))       # capô
    P.append(bd.prim('sph', flat(B), pos=(0, 0.10, -1.35), scale=(0.77, 0.27, 0.55), gloss=0.5, **kw))      # traseira
    P.append(bd.prim('sph', cabin_sh, pos=(0, 0.30, -0.20), scale=(0.72, 0.56, 1.05), gloss=0.9, **kw))    # cabine
    P.append(bd.prim('box', flat((0.16, 0.16, 0.18)), pos=(0, -0.19, 1.80), scale=(0.74, 0.09, 0.10), **kw))
    P.append(bd.prim('box', flat((0.16, 0.16, 0.18)), pos=(0, -0.19, -1.80), scale=(0.74, 0.09, 0.10), **kw))
    for sd in (1, -1):
        P.append(bd.prim('sph', flat((1.0, 0.96, 0.75)), pos=(sd * 0.52, 0.08, 1.80), scale=(0.15, 0.11, 0.10), emis=0.6, **kw))
        P.append(bd.prim('sph', flat((0.95, 0.10, 0.08)), pos=(sd * 0.55, 0.10, -1.82), scale=(0.13, 0.08, 0.08), emis=0.3, **kw))
        for wz in (1.12, -1.12):
            wf = base.child(rot_x(dist / 0.34) @ rot_z(np.pi / 2), (sd * 0.74, 0.34, wz))
            P.append(wf.prim('cyl', wheel_shader, scale=(0.34, 0.13, 0.34), **kw))
    return P

# ------------------------------------------------------------------ CENÁRIO
ROAD_HALF = 3.0
def ground_shader(pl, nl, pw):
    x, z = pw[:, 0], pw[:, 2]; az = np.abs(z); n1 = vnoise(x * 0.35, z * 0.35); n2 = vnoise(x * 3.1, z * 3.1)
    g = mix(V(0.22, 0.56, 0.16), V(0.40, 0.72, 0.20), sstep(0.35, 0.65, n1)) * (0.88 + 0.2 * n2)[:, None] * (0.94 + 0.06 * np.sign(np.sin(z * 2.2)))[:, None]
    walk = mix(V(0.66, 0.63, 0.58), V(0.58, 0.56, 0.52), n2 * 0.6)
    joint = (np.abs((x / 1.1) % 1 - .5) > 0.475) | (np.abs(az - 4.0) < 0.02)
    walk = np.where(joint[:, None], walk * 0.78, walk)
    road = V(0.24, 0.25, 0.29) * (0.90 + 0.2 * n2)[:, None]
    road = np.where(((az < 0.07) & ((x % 3.0) < 1.6) & (np.abs(x) > 2.2))[:, None], V(0.98, 0.80, 0.18), road)
    road = np.where(((np.abs(az - 2.72) < 0.06))[:, None], V(0.92, 0.92, 0.92), road)
    cw = (np.abs(x) < 1.3) & (az < 2.6) & (((z + 2.6) % 0.8) < 0.42)
    road = np.where(cw[:, None], V(0.95, 0.95, 0.95), road)
    c = np.where((az < ROAD_HALF)[:, None], road, np.where((az < 5.0)[:, None], walk, g))
    return np.where(((az >= ROAD_HALF) & (az < 3.18))[:, None], V(0.74, 0.73, 0.70), c)

def house(x, z, face, wall, roof, g):
    """face: -1 = frente virada para -z (rua), +1 = frente para +z."""
    W = V(*wall); P = []
    def sh(pl, nl, pw):
        c = np.broadcast_to(W, pl.shape).copy(); fr = pl[:, 2] * face > 0.99; u, v = pl[:, 0], pl[:, 1]
        c = np.where((v < -0.86)[:, None], W * 0.7, c)
        door = fr & (np.abs(u) < 0.16) & (v < 0.05); c = np.where(door[:, None], V(0.45, 0.25, 0.14), c)
        win = fr & (np.abs(np.abs(u) - 0.58) < 0.2) & (np.abs(v - 0.1) < 0.3)
        wf = win & ((np.abs(np.abs(u) - 0.58) > 0.16) | (np.abs(v - 0.1) > 0.26) | (np.abs(np.abs(u) - 0.58) < 0.02))
        c = np.where(win[:, None], V(0.55, 0.80, 0.95), c); c = np.where(wf[:, None], V(1, 1, 1), c)
        return c
    P.append(Prim('box', sh, c=(x, 1.5, z), M=np.diag(V(2.7, 1.5, 2.2)), group=g))
    M = np.diag(V(1, 0.62, 1)) @ rot_x(np.pi / 4) @ np.diag(V(2.95, 1.62, 1.62))
    P.append(Prim('box', flat(roof), c=(x, 3.0, z), M=M, group=g))
    P.append(Prim('box', flat(V(*wall) * 0.8), c=(x + 1.4, 3.9, z + 0.6), M=np.diag(V(0.28, 0.6, 0.28)), group=g))
    return P
def tree(x, z, s, g, hue=0.0):
    leaf = V(0.20 + hue, 0.58, 0.20)
    def sh(pl, nl, pw): return leaf * (0.82 + 0.36 * vnoise(pw[:, 0] * 2.5 + pw[:, 1] * 1.7, pw[:, 2] * 2.5))[:, None]
    P = [Prim('cyl', flat((0.42, 0.27, 0.16)), c=(x, 0.9 * s, z), M=np.diag(V(0.16 * s, 0.9 * s, 0.16 * s)), group=g)]
    for dx, dy, dz, r in ((0, 2.3, 0, 1.05), (0.65, 1.9, 0.2, 0.75), (-0.6, 1.95, -0.25, 0.8), (0.1, 3.0, 0.1, 0.7)):
        P.append(Prim('sph', sh, c=(x + dx * s, dy * s, z + dz * s), M=np.diag(V(r * s, r * s * 0.92, r * s)), group=g))
    return P
def lamp(x, z, sgn, g):
    P = [Prim('cyl', flat((0.20, 0.22, 0.26)), c=(x, 1.7, z), M=np.diag(V(0.05, 1.7, 0.05)), group=g),
         Prim('cap', flat((0.20, 0.22, 0.26)), a=(x, 3.4, z), b=(x, 3.5, z - sgn * 0.7), r=0.045, group=g),
         Prim('sph', flat((1.0, 0.95, 0.8)), c=(x, 3.42, z - sgn * 0.75), M=np.diag(V(0.16, 0.1, 0.16)), group=g, emis=0.2)]
    return P
def mailbox(x, z, g, col=(0.85, 0.15, 0.15)):
    return [Prim('cyl', flat((0.9, 0.9, 0.9)), c=(x, 0.4, z), M=np.diag(V(0.035, 0.4, 0.035)), group=g),
            Prim('box', flat(col), c=(x, 0.9, z), M=np.diag(V(0.14, 0.12, 0.22)), group=g)]
def sign(x, z, g):
    def sh(pl, nl, pw):
        c = np.broadcast_to(V(1.0, 0.82, 0.1), pl.shape).copy()
        return np.where(((np.abs(pl[:, 0]) > 0.82) | (np.abs(pl[:, 1]) > 0.82))[:, None], V(0.08, 0.08, 0.08), c)
    return [Prim('cyl', flat((0.75, 0.76, 0.78)), c=(x, 1.0, z), M=np.diag(V(0.035, 1.0, 0.035)), group=g),
            Prim('box', sh, c=(x, 2.05, z), M=rot_y(np.pi / 2) @ rot_z(np.pi / 4) @ np.diag(V(0.33, 0.33, 0.02)), group=g, emis=0.01)]

def cloud_sh(pl, nl, pw): return mix(V(0.78, 0.86, 1.0), V(1.12, 1.12, 1.12), sstep(-0.6, 0.5, nl[:, 1]))
def environment():
    P = [Prim('plane', ground_shader, shadow=False)]; g = 1; rng = np.random.default_rng(7)
    walls = [(0.98, 0.93, 0.80), (0.80, 0.90, 0.98), (0.99, 0.84, 0.80), (0.86, 0.95, 0.84), (0.96, 0.90, 0.98)]
    roofs = [(0.75, 0.25, 0.20), (0.25, 0.35, 0.55), (0.45, 0.30, 0.22), (0.30, 0.50, 0.42)]
    for k, x in enumerate(range(-76, 40, 11)):
        for face, zz in ((-1, 10.6), (1, -11.2)):
            j = k * 2 + (face > 0); xx = x + (5.5 if face > 0 else 0)
            P += house(xx, zz, face, walls[j % 5], roofs[(j * 3) % 4], g); g += 1
            P += tree(xx + 5.3 + rng.uniform(-.6, .6), zz - face * rng.uniform(2.0, 4.0), rng.uniform(0.85, 1.25), g, rng.uniform(-.05, .08)); g += 1
            P += mailbox(xx - 1.2, -face * 5.5 if False else zz + face * 4.9, g, [(0.85, 0.15, 0.15), (0.15, 0.4, 0.85), (0.95, 0.75, 0.1)][j % 3]); g += 1
            for b in range(2):  # arbustos
                bx = xx + (-2.2 + 4.4 * b); col = V(0.22, 0.52, 0.20) * rng.uniform(0.9, 1.2)
                P.append(Prim('sph', flat(col), c=(bx, 0.35, zz + face * 2.6), M=np.diag(V(0.7, 0.5, 0.5)), group=g))
            g += 1
    for x in range(-70, 40, 14):
        P += lamp(x + 6.0, 5.25, 1, g); g += 1; P += lamp(x + 9.5, -5.25, -1, g); g += 1
    P += sign(-2.1, 3.55, g); g += 1; P += sign(-2.1, -3.55, g); g += 1
    for x, z, r, c in ((-60, 95, 60, (0.42, 0.70, 0.36)), (30, 110, 75, (0.36, 0.64, 0.38)), (-140, 60, 70, (0.40, 0.68, 0.40)),
                       (-30, -100, 65, (0.40, 0.69, 0.36)), (70, -90, 60, (0.36, 0.64, 0.38)), (-150, -40, 60, (0.42, 0.70, 0.38))):
        P.append(Prim('sph', flat(c), c=(x, -r * 0.72, z), M=np.diag(V(r, r, r)), shadow=False, group=0))
    for cx, cy, cz in ((-80, 34, 60), (-30, 42, 120), (40, 30, 90), (-120, 38, -30), (-60, 30, -90), (20, 36, -110), (-170, 45, 40), (90, 40, 10)):
        for dx, dy, r in ((0, 0, 7), (7, -1, 5.5), (-7, -1.2, 5), (3, 2.5, 5)):
            P.append(Prim('sph', cloud_sh, c=(cx + dx, cy + dy, cz), M=np.diag(V(r * 1.3, r * 0.7, r)), shadow=False, nofog=True, emis=0.01))
    return P
