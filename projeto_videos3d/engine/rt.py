"""Renderizador 3D por software (ray casting analítico, NumPy).
Geometria real em espaço 3D: esferas/elipsoides, caixas orientadas, cilindros,
cápsulas e plano de chão; câmera em perspectiva, z-buffer por raio, sombras
projetadas pelo sol (shadow rays), iluminação toon, névoa e contorno."""
import numpy as np
F = np.float32; INF = F(1e30); EPS = F(1e-3)
def V(*a): return np.array(a, F)
def norm(v): return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def rot_y(a): c, s = np.cos(a), np.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]], F)
def rot_x(a): c, s = np.cos(a), np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]], F)
def rot_z(a): c, s = np.cos(a), np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]], F)
def flat(col): 
    col = V(*col)
    return lambda pl, nl, pw: np.broadcast_to(col, pl.shape)
UB = {'sph': 1.0, 'box': 3 ** .5, 'cyl': 2 ** .5}

class Prim:
    def __init__(s, kind, shader, c=None, M=None, a=None, b=None, r=None, group=0, shadow=True,
                 outline=0, gloss=0.0, emis=0.0, nofog=False):
        s.kind, s.shader, s.group, s.shadow, s.outline, s.gloss, s.emis, s.nofog = kind, shader, group, shadow, outline, gloss, emis, nofog
        if kind == 'cap':
            s.a, s.b, s.r = V(*a), V(*b), F(r); s.c = (s.a + s.b) / 2; s.R = float(np.linalg.norm(s.b - s.a) / 2 + r)
        elif kind == 'plane':
            s.c = V(0, 0, 0); s.R = 1e9
        else:
            s.c = V(*c); s.M = np.asarray(M, F); s.Minv = np.linalg.inv(s.M).astype(F)
            s.R = float(UB[kind] * np.linalg.svd(s.M, compute_uv=False)[0])

class Frame:
    """Transformação hierárquica (rig): R (3x3) + t."""
    def __init__(s, R=None, t=(0, 0, 0)): s.R = np.eye(3, dtype=F) if R is None else np.asarray(R, F); s.t = V(*t)
    def child(s, R=None, t=(0, 0, 0)): return Frame(s.R @ (np.eye(3, dtype=F) if R is None else R), s.pt(t))
    def pt(s, p): return s.R @ V(*p) + s.t
    def prim(s, kind, shader, pos=(0, 0, 0), scale=(1, 1, 1), R=None, **kw):
        M = s.R @ (np.eye(3, dtype=F) if R is None else R) @ np.diag(V(*scale))
        return Prim(kind, shader, c=s.pt(pos), M=M, **kw)
    def cap(s, shader, a, b, r, **kw): return Prim('cap', shader, a=s.pt(a), b=s.pt(b), r=r, **kw)

def _local(p, o, d):
    ol = (o - p.c) @ p.Minv.T
    return np.broadcast_to(ol, d.shape).astype(F), d @ p.Minv.T

def intersect(p, o, d):
    """o: (3,) ou (N,3); d: (N,3) normalizado. Retorna t (N,)."""
    n = len(d); t = np.full(n, INF, F)
    with np.errstate(all='ignore'):
        if p.kind == 'plane':
            oy = o[..., 1]; dy = d[:, 1]; tt = -oy / dy
            return np.where((dy < -1e-6) & (tt > EPS), tt, INF).astype(F)
        if p.kind == 'cap':
            ba = p.b - p.a; oa = np.broadcast_to(o - p.a, d.shape)
            baba = ba @ ba; bard = d @ ba; baoa = oa @ ba; rdoa = (d * oa).sum(1); oaoa = (oa * oa).sum(1)
            A = baba - bard * bard; B = baba * rdoa - baoa * bard; C = baba * oaoa - baoa * baoa - p.r * p.r * baba
            h = B * B - A * C; ok = h >= 0
            tt = (-B - np.sqrt(np.where(ok, h, 0))) / np.where(np.abs(A) < 1e-9, 1e-9, A)
            y = baoa + tt * bard
            body = ok & (y > 0) & (y < baba) & (tt > EPS)
            t = np.where(body, tt, t)
            for cen in (p.a, p.b):
                oc = np.broadcast_to(o - cen, d.shape); b2 = (d * oc).sum(1); c2 = (oc * oc).sum(1) - p.r * p.r
                h2 = b2 * b2 - c2; ts = -b2 - np.sqrt(np.where(h2 > 0, h2, 0))
                t = np.where((h2 > 0) & (ts > EPS) & (ts < t), ts, t)
            return t.astype(F)
        ol, dl = _local(p, o, d)
        if p.kind == 'sph':
            a = (dl * dl).sum(1); b = (ol * dl).sum(1); c = (ol * ol).sum(1) - 1
            disc = b * b - a * c; tt = (-b - np.sqrt(np.where(disc > 0, disc, 0))) / a
            return np.where((disc > 0) & (tt > EPS), tt, INF).astype(F)
        if p.kind == 'box':
            inv = 1 / np.where(np.abs(dl) < 1e-9, 1e-9, dl)
            t1 = (-1 - ol) * inv; t2 = (1 - ol) * inv
            tn = np.minimum(t1, t2).max(1); tf = np.maximum(t1, t2).min(1)
            return np.where((tn < tf) & (tn > EPS), tn, INF).astype(F)
        if p.kind == 'cyl':
            a = dl[:, 0] ** 2 + dl[:, 2] ** 2; b = ol[:, 0] * dl[:, 0] + ol[:, 2] * dl[:, 2]; c = ol[:, 0] ** 2 + ol[:, 2] ** 2 - 1
            disc = b * b - a * c; ts = (-b - np.sqrt(np.where(disc > 0, disc, 0))) / np.where(a < 1e-12, 1e-12, a)
            y = ol[:, 1] + ts * dl[:, 1]
            t = np.where((disc > 0) & (np.abs(y) <= 1) & (ts > EPS), ts, t)
            for sg in (1, -1):
                tc = (sg - ol[:, 1]) / np.where(np.abs(dl[:, 1]) < 1e-9, 1e-9, dl[:, 1])
                x = ol[:, 0] + tc * dl[:, 0]; z = ol[:, 2] + tc * dl[:, 2]
                t = np.where((x * x + z * z <= 1) & (tc > EPS) & (tc < t), tc, t)
            return t.astype(F)

def surface(p, pw):
    """posição local e normal de mundo no ponto pw."""
    if p.kind == 'plane':
        n = np.zeros_like(pw); n[:, 1] = 1; return pw, n
    if p.kind == 'cap':
        ba = p.b - p.a; pa = pw - p.a; h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
        return np.c_[h, h, h], norm(pa - h[:, None] * ba)
    pl = (pw - p.c) @ p.Minv.T
    if p.kind == 'sph': nl = pl
    elif p.kind == 'box':
        ax = np.abs(pl).argmax(1); nl = np.zeros_like(pl); r = np.arange(len(pl)); nl[r, ax] = np.sign(pl[r, ax])
    else:
        cap = np.abs(pl[:, 1]) > 0.999; nl = pl.copy(); nl[:, 1] = 0
        nl[cap] = 0; nl[cap, 1] = np.sign(pl[cap, 1])
    return pl, norm(nl @ p.Minv)

class Camera:
    def __init__(s, pos, target, vfov=50.0, roll=0.0):
        s.pos = V(*pos); s.fwd = norm(V(*target) - s.pos); s.right = norm(np.cross(s.fwd, V(0, 1, 0)))
        s.up = np.cross(s.right, s.fwd)
        if roll: s.right, s.up = s.right * np.cos(roll) + s.up * np.sin(roll), s.up * np.cos(roll) - s.right * np.sin(roll)
        s.tan = np.tan(np.radians(vfov) / 2)
    def rays(s, W, H):
        u = ((np.arange(W, dtype=F) + .5) / W * 2 - 1) * s.tan * W / H; v = (1 - (np.arange(H, dtype=F) + .5) / H * 2) * s.tan
        return norm(s.fwd + u[None, :, None] * s.right + v[:, None, None] * s.up).astype(F)
    def rect(s, c, R, W, H):
        rel = c - s.pos; z = rel @ s.fwd
        if z + R < 0.05: return None
        if z - R < 0.1: return 0, H, 0, W
        k = H / 2 / s.tan; x = rel @ s.right / z * k + W / 2; y = H / 2 - rel @ s.up / z * k
        r = R / (z - R) * k * 1.1 + 2
        x0, x1, y0, y1 = int(max(0, x - r)), int(min(W, x + r + 1)), int(max(0, y - r)), int(min(H, y + r + 1))
        return (y0, y1, x0, x1) if x1 > x0 and y1 > y0 else None

SUN_DIR = norm(V(0.30, 0.78, -0.55)); SUN = V(1.0, 0.95, 0.84) * 1.05
SKY_A = V(0.50, 0.63, 0.86) * 0.62; GND_A = V(0.36, 0.40, 0.22) * 0.30
ZEN = V(0.08, 0.30, 0.88); HOR = V(0.60, 0.80, 0.98)

def render(prims, cam, W, H, sun_dir=SUN_DIR):
    D = cam.rays(W, H); tb = np.full((H, W), INF, F); ib = np.full((H, W), -1, np.int32); rects = {}
    for i, p in enumerate(prims):
        rc = cam.rect(p.c, p.R, W, H)
        if rc is None: continue
        y0, y1, x0, x1 = rc; d = D[y0:y1, x0:x1].reshape(-1, 3)
        t = intersect(p, cam.pos, d).reshape(y1 - y0, x1 - x0)
        m = t < tb[y0:y1, x0:x1]
        if m.any(): tb[y0:y1, x0:x1][m] = t[m]; ib[y0:y1, x0:x1][m] = i; rects[i] = rc
    N = np.zeros((H, W, 3), F); A = np.zeros((H, W, 3), F); P = np.zeros((H, W, 3), F)
    gl = np.zeros((H, W), F); em = np.zeros((H, W), F); nf = np.zeros((H, W), bool); ol = np.zeros((H, W), np.int16)
    for i, (y0, y1, x0, x1) in rects.items():
        p = prims[i]; m = ib[y0:y1, x0:x1] == i
        if not m.any(): continue
        pw = cam.pos + tb[y0:y1, x0:x1][m][:, None] * D[y0:y1, x0:x1][m]
        pl, n = surface(p, pw)
        P[y0:y1, x0:x1][m] = pw; N[y0:y1, x0:x1][m] = n; A[y0:y1, x0:x1][m] = p.shader(pl, n, pw)
        gl[y0:y1, x0:x1][m] = p.gloss; em[y0:y1, x0:x1][m] = p.emis; nf[y0:y1, x0:x1][m] = p.nofog; ol[y0:y1, x0:x1][m] = p.outline
    hit = ib >= 0; ndl = np.clip(N @ sun_dir, 0, 1)
    # ---- sombras: shadow rays hierárquicos (grupo -> primitiva) no espaço da luz
    lit = np.zeros((H, W), F); act = np.flatnonzero((hit & (ndl > 0) & (em < 0.9)).ravel())
    Pa = P.reshape(-1, 3)[act] + N.reshape(-1, 3)[act] * F(4e-3)
    U = norm(np.cross(sun_dir, V(0, 1, 0))); Vv = np.cross(sun_dir, U)
    pu, pv, pL = Pa @ U, Pa @ Vv, Pa @ sun_dir; sh = np.zeros(len(act), bool)
    groups = {}
    for p in prims:
        if p.shadow and p.kind != 'plane': groups.setdefault(p.group, []).append(p)
    Ld = None
    for g, mem in groups.items():
        cs = np.array([q.c for q in mem]); gc = cs.mean(0); gR = max(np.linalg.norm(q.c - gc) + q.R for q in mem)
        gm = np.flatnonzero((~sh) & ((pu - gc @ U) ** 2 + (pv - gc @ Vv) ** 2 < gR * gR) & (pL < gc @ sun_dir + gR))
        if not len(gm): continue
        for q in mem:
            sub = gm[((pu[gm] - q.c @ U) ** 2 + (pv[gm] - q.c @ Vv) ** 2 < q.R * q.R) & (pL[gm] < q.c @ sun_dir + q.R) & (~sh[gm])]
            if not len(sub): continue
            t = intersect(q, Pa[sub], np.broadcast_to(sun_dir, (len(sub), 3)))
            sh[sub[t < 1e20]] = True
    lit.ravel()[act[~sh]] = 1
    import cv2
    lit = cv2.GaussianBlur(lit, (0, 0), max(0.8, H / 1100))
    # ---- iluminação toon
    band = np.clip(ndl / 0.30, 0, 1); band = band * band * (3 - 2 * band)
    dif = (0.72 * band + 0.28 * ndl) * lit
    amb = SKY_A * (0.62 + 0.38 * N[..., 1:2]) + GND_A * (0.5 - 0.5 * N[..., 1:2])
    col = A * (amb + SUN * dif[..., None])
    Rf = D - 2 * (D * N).sum(-1, keepdims=True) * N
    spec = np.clip(Rf @ sun_dir, 0, 1) ** 48 * gl * lit
    fres = (1 - np.clip(-(D * N).sum(-1), 0, 1)) ** 3 * gl * 0.35
    col = col + spec[..., None] * 1.2 + fres[..., None] * HOR
    col = np.where(em[..., None] > 0, A * (1 + em[..., None]) * 0.9 + col * 0.1, col)
    # ---- céu e névoa
    dy = np.clip(D[..., 1], 0, 1)[..., None]; sky = HOR + (ZEN - HOR) * dy ** 0.55
    sky = sky + V(1, .9, .7) * (np.clip(D @ sun_dir, 0, 1) ** 220)[..., None] * 0.5
    fog = (1 - np.exp(-np.minimum(tb, 400) * 0.0032))[..., None] * (~nf)[..., None]
    col = col * (1 - fog) + HOR * 0.97 * fog
    col = np.where(hit[..., None], col, sky)
    # ---- contorno (id + profundidade) para grupos marcados
    e = np.zeros((H, W), bool)
    for ax in (0, 1):
        a_, b_ = np.take(ib, range(0, ib.shape[ax] - 1), ax), np.take(ib, range(1, ib.shape[ax]), ax)
        oa, ob = np.take(ol, range(0, ib.shape[ax] - 1), ax), np.take(ol, range(1, ib.shape[ax]), ax)
        ta, tb2 = np.take(tb, range(0, ib.shape[ax] - 1), ax), np.take(tb, range(1, ib.shape[ax]), ax)
        dd = ((oa > 0) | (ob > 0)) & (a_ != b_) & ((oa != ob) | (np.abs(ta - tb2) > 0.045 * np.minimum(ta, tb2) ** 0.5))
        if ax == 0: e[:-1] |= dd
        else: e[:, :-1] |= dd
    k = max(2, int(round(H / 520)))
    e = cv2.dilate(e.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    col = np.where(e[..., None] > 0, V(0.05, 0.05, 0.08), col)
    return col

def tonemap(col, W, H):
    """SS -> resolução final (área), curva suave, saturação, vinheta, gama."""
    import cv2
    c = cv2.resize(col, (W, H), interpolation=cv2.INTER_AREA)
    c = c / (1 + 0.18 * c) * 1.12
    l = c @ V(0.3, 0.59, 0.11); c = l[..., None] + (c - l[..., None]) * 1.28
    yy, xx = np.mgrid[0:H, 0:W]; r2 = ((xx / W - .5) ** 2 + ((yy / H - .5) * .9) ** 2)
    c = c * (1 - 0.32 * r2)[..., None]
    return (np.clip(c, 0, 1) ** (1 / 2.2) * 255 + .5).astype(np.uint8)
