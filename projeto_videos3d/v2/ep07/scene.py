"""Cenários do vídeo 07 (e se um furacão chegasse na Avenida Paulista?). Reaproveita utilitários dos vídeos 02–06 e acrescenta:
- paulista: avenida larga estilizada (6 faixas + canteiro), prédios altos com janelas procedurais (luz controlável),
  duas torres de antena treliçadas, árvores e postes; céu de tempestade, chuva presa à câmera, rajadas de vento,
  setas de vento (efeito corredor), destroços (placas, vidros, galhos) e uma árvore que tomba.
- globo: Terra com um furacão estilizado (espiral de nuvens com olho) em lat/lon.
- relevo: corte do terreno do mar até o planalto (escala vertical exagerada), com São Paulo no alto da serra
  e um furacão que encolhe ao entrar na terra.
Personagens e cenário são estilizados; nada copia obras existentes."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Euler, Matrix
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('scene06', os.path.join(HERE, '..', 'ep06', 'scene.py'))
S6 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S6)
for _k in dir(S6):
    if not _k.startswith('__'): globals()[_k] = getattr(S6, _k)
S2 = S6.S2

# ------------------------------------------------------------------ materiais
def facade_mat(name, base, lit_frac=0.45, seed=0.0):
    """Fachada com janelas procedurais (3,2 x 3,5 m). Valor 'Luz' (0–1) acende/apaga as janelas acesas."""
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); x, y, z = nb.sep(tc.outputs['Object'])
    u = nb.math('ADD', x, y)
    fu = nb.math('FRACT', nb.math('DIVIDE', u, 3.2)); fz = nb.math('FRACT', nb.math('DIVIDE', z, 3.5))
    win = nb.math('MULTIPLY', nb.math('MULTIPLY', nb.math('GREATER_THAN', fu, 0.14), nb.math('LESS_THAN', fu, 0.86)),
                  nb.math('MULTIPLY', nb.math('GREATER_THAN', fz, 0.28), nb.math('LESS_THAN', fz, 0.86)))
    cell = nb.comb(nb.math('FLOOR', nb.math('DIVIDE', u, 3.2)), nb.math('FLOOR', nb.math('DIVIDE', z, 3.5)), seed)
    wn = nb.n('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'; nb.link(cell, wn.inputs['Vector'])
    lit = nb.math('LESS_THAN', wn.outputs['Value'], lit_frac)
    nb.link(nb.mixc(win, base, (0.035, 0.045, 0.06)), bs.inputs['Base Color'])
    nb.link(nb.mixf(win, 0.8, 0.35), bs.inputs['Roughness'])
    bs.inputs['Emission Color'].default_value = (1.0, 0.78, 0.48, 1)
    luz = nb.value('Luz', 1.0)
    nb.link(nb.math('MULTIPLY', nb.math('MULTIPLY', win, lit), nb.math('MULTIPLY', luz, 1.4)), bs.inputs['Emission Strength'])
    nb.link(bs.outputs[0], out.inputs[0]); return m

def set_lights(v, f):
    """Liga/desliga as janelas de todos os prédios (valor 'Luz' em cada material de fachada)."""
    for m in bpy.data.materials:
        if m.name.startswith('Fachada') and m.node_tree and 'Luz' in m.node_tree.nodes:
            o = m.node_tree.nodes['Luz'].outputs[0]; o.default_value = v; o.keyframe_insert('default_value', frame=f)

def storm_world(top=(0.06, 0.065, 0.075), bottom=(0.24, 0.25, 0.28)):
    gradient_world(top, bottom, 'Tempestade')

# ------------------------------------------------------------------ Avenida Paulista estilizada
ROAD_W, WALK_W = 12.0, 6.0           # meia-largura da pista e largura da calçada (m)
AX0, AX1 = -90.0, 320.0
FACADE = [(0.55, 0.56, 0.58), (0.42, 0.45, 0.5), (0.62, 0.6, 0.55), (0.3, 0.34, 0.4), (0.7, 0.7, 0.72), (0.48, 0.42, 0.38)]

def lattice_tower(C, base, h, w0=5.0, w1=0.8):
    """Torre de antena treliçada (estilizada, sem copiar uma torre real)."""
    mat = B.mat_basic('TorreMetal', (0.75, 0.25, 0.2), 0.45, 0.6); white = B.mat_basic('TorreBranca', (0.9, 0.9, 0.9), 0.45, 0.5)
    bx, by, bz = base; corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]; n = 9
    def pt(c, t): w = (w0 + (w1 - w0) * t) / 2; return Vector((bx + c[0] * w, by + c[1] * w, bz + h * t))
    def bar(a, b, r, m):
        d = b - a; o = B.cyl('torre_barra', r, d.length, ((a + b) / 2)[:], m, C, seg=6, smooth=False)
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y'); return o
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n; m = mat if i % 2 == 0 else white
        for k in range(4):
            c0, c1 = corners[k], corners[(k + 1) % 4]
            bar(pt(c0, t0), pt(c0, t1), 0.12 * (1 - 0.5 * t0), m)
            bar(pt(c0, t1), pt(c1, t1), 0.07, m); bar(pt(c0, t0), pt(c1, t1), 0.05, m)
    bar(pt((0, 0), 1.0), pt((0, 0), 1.0) + Vector((0, 0, h * 0.18)), 0.15, white)
    red = B.mat_basic('LuzTorre', (1, 0.05, 0.02), 0.3, emit=(1, 0.05, 0.02), emit_s=12)
    for t in (0.5, 1.0): B.sphere('luz_torre', 0.35, pt((0, 0), t)[:] if t < 1 else (bx, by, bz + h * 1.18), red, C, seg=12)

def build_paulista(seed=7, towers=True):
    storm_world(); r = random.Random(seed)
    C = B.new_coll('Paulista')
    asphalt = B.mat_pbr('AsfaltoMolhado', 'asphalt_02', 4.0, tint=(0.55, 0.56, 0.6), var=0.2, rough_mul=0.35)
    walk = B.mat_pbr('CalcadaSP', 'concrete_pavement', 1.6, tint=(0.75, 0.74, 0.72), rough_mul=0.5)
    xc, L = (AX0 + AX1) / 2, AX1 - AX0
    B.box('pista', (L, 2 * ROAD_W, 0.2), (xc, 0, -0.1), asphalt, C)
    for s in (1, -1):
        B.box('calcada', (L, WALK_W, 0.3), (xc, s * (ROAD_W + WALK_W / 2), 0.05), walk, C)
        B.box('meio_fio', (L, 0.25, 0.32), (xc, s * (ROAD_W + 0.12), 0.06), B.mat_basic('MeioFio', (0.7, 0.7, 0.68), 0.6), C)
    # canteiro central com plantas
    B.box('canteiro', (L, 1.8, 0.45), (xc, 0, 0.12), B.mat_basic('Canteiro', (0.5, 0.5, 0.48), 0.7), C)
    for x in range(int(AX0) + 6, int(AX1), 14): B.instance('shrub_02', (x, 0, 0.35), r.uniform(0, 6.3), r.uniform(0.7, 1.0), C)
    paint = B.mat_basic('Faixa', (0.85, 0.85, 0.82), 0.5)
    for yl in (-8.0, -4.0, 4.0, 8.0):
        for x in range(int(AX0), int(AX1), 9): B.box('faixa', (4.0, 0.15, 0.01), (x, yl, 0.005), paint, C)
    # prédios
    mats = [facade_mat(f'Fachada{i}', tuple(v * 0.7 for v in c), 0.07 + 0.04 * (i % 3), seed=i * 1.7) for i, c in enumerate(FACADE)]
    roofm = B.mat_basic('Cobertura', (0.25, 0.26, 0.28), 0.8)
    blds = []
    for s in (1, -1):
        x = AX0; k = 0
        while x < AX1:
            w = r.uniform(16, 30); d = r.uniform(20, 32); mid = 1 - min(abs(x - 110) / 220, 1)
            h = r.uniform(30, 55) + mid * r.uniform(20, 80); y0 = s * (ROAD_W + WALK_W + 1.0)
            m = mats[(k + (s > 0)) % len(mats)]
            o = B.box('predio', (w, d, h), (x + w / 2, y0 + s * d / 2, h / 2), m, C); blds.append(o)
            B.box('cobertura', (w * 0.6, d * 0.6, 3.0), (x + w / 2, y0 + s * d / 2, h + 1.5), roofm, C)
            if k % 3 == 1: B.box('marquise', (w * 0.9, 2.0, 0.25), (x + w / 2, y0 - s * 1.0, 4.2), B.mat_basic('Marquise', (0.2, 0.2, 0.22), 0.4, 0.5), C)
            if towers and ((s > 0 and k == 8) or (s < 0 and k == 12)): lattice_tower(C, (x + w / 2, y0 + s * d / 2, h + 3.0), 70.0)
            x += w + r.uniform(1.5, 5.0); k += 1
    # árvores e postes nas calçadas
    trees = []
    for s in (1, -1):
        for i, x in enumerate(range(int(AX0) + 4, int(AX1), 12)):
            t = B.instance('tree_small_02', (x + r.uniform(-1, 1), s * (ROAD_W + 2.4), 0.2), r.uniform(0, 6.3), r.uniform(0.9, 1.25), C)
            trees.append(t)
        for x in range(int(AX0) + 10, int(AX1), 24): B.instance('street_lamp_01', (x, s * (ROAD_W + 0.9), 0.2), 0.0 if s < 0 else math.pi, 1.0, C)
    # carros parados
    cars = []
    for i, (x, y, col) in enumerate([(34, -7, (0.7, 0.05, 0.04)), (22, -2, (0.85, 0.85, 0.86)), (36, 6, (0.1, 0.2, 0.5)), (55, -10, (0.15, 0.15, 0.16)), (70, 2, (0.9, 0.75, 0.1))]):
        c = B.build_car(f'CarroSP{i}', col, driver=False); c['root'].location = (x, y, 0.0); c['root'].rotation_euler = (0, 0, 0 if y < 0 else math.pi); cars.append(c)
    # luz: céu fechado (sol fraco e frio) e relâmpago
    sun = bpy.data.lights.new('Sol', 'SUN'); sun.energy = 1.8; sun.color = (0.78, 0.84, 0.95); sun.angle = math.radians(12)
    so = B.link(bpy.data.objects.new('Sol', sun)); so.rotation_euler = (math.radians(35), 0, math.radians(30))
    fl = bpy.data.lights.new('Relampago', 'AREA'); fl.energy = 0.0; fl.size = 200; fl.color = (0.8, 0.85, 1.0)
    flo = B.link(bpy.data.objects.new('Relampago', fl)); flo.location = (120, 40, 260); flo.rotation_euler = (math.radians(15), 0, 0)
    return dict(buildings=blds, trees=trees, cars=cars, flash=fl, coll=C)

# ------------------------------------------------------------------ chuva, vento e destroços
def build_rain(cam, n=420, seed=5):
    """Gotas como traços finos presos à câmera (sempre no quadro)."""
    m = B.mat_basic('Chuva', (0.8, 0.85, 0.95), 0.1, emit=(0.75, 0.8, 0.9), emit_s=0.35, alpha=0.2); r = random.Random(seed)
    base = B.box('gota_base', (0.004, 0.004, 0.45), (0, 0, 0), m, B.new_coll('Chuva')); base.hide_render = True
    drops = []
    for i in range(n):
        o = B.link(bpy.data.objects.new(f'gota{i}', base.data), base.users_collection[0]); o.parent = cam; o.visible_shadow = False
        zc = -r.uniform(1.2, 16.0); s = -zc * 0.6
        drops.append((o, r.uniform(-s, s), zc, r.uniform(0, 1), r.uniform(0.85, 1.2)))
    return drops

def rain_pose(drops, T, f, slant=0.35, speed=9.0):
    for o, x0, zc, ph, sp in drops:
        hh = -zc * 1.2; y = hh - ((T * speed * sp + ph * 2 * hh) % (2 * hh))
        o.location = (x0 + slant * y * 0.2, y, zc); o.rotation_euler = (0, 0, -slant); o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)

def build_gusts(C, n=60, seed=8, x0=-20, x1=120):
    """Rajadas: faixas brancas finas e translúcidas que correm no sentido +X."""
    m = B.mat_basic('Rajada', (0.9, 0.92, 0.95), 0.2, emit=(0.9, 0.92, 0.95), emit_s=0.9, alpha=0.28); r = random.Random(seed)
    out = []
    for i in range(n):
        o = B.box('rajada', (r.uniform(4, 9), 0.035, 0.035), (0, 0, 0), m, C); o.visible_shadow = False
        out.append((o, r.uniform(x0, x1), r.uniform(-ROAD_W * 1.2, ROAD_W * 1.2), r.uniform(0.6, 12.0), r.uniform(0, 1), r.uniform(0.8, 1.3)))
    return out

def gust_pose(gusts, T, f, speed, span=(-20, 120), vis=1.0):
    a, b = span; Lx = b - a
    for o, x0, y, z, ph, sp in gusts:
        x = a + ((x0 - a) + T * speed * sp) % Lx
        o.location = (x, y + 0.6 * math.sin(T * 2 + ph * 6), z + 0.3 * math.sin(T * 3 + ph * 9)); o.scale = (max(vis, 1e-4),) * 3
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)

def arrow_mesh(name, L, w, mat, C):
    bm = bmesh.new(); hw = w / 2; hl = L * 0.35
    pts = [(0, -hw * 0.45), (L - hl, -hw * 0.45), (L - hl, -hw), (L, 0), (L - hl, hw), (L - hl, hw * 0.45), (0, hw * 0.45)]
    vs = [bm.verts.new((x, 0, y)) for x, y in pts]; bm.faces.new(vs)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = B.link(bpy.data.objects.new(name, me), C); o.data.materials.append(mat)
    sol = o.modifiers.new('esp', 'SOLIDIFY'); sol.thickness = 0.08; return o

def build_arrows(C, n=14):
    m = B.mat_basic('SetaVento', (1.0, 0.82, 0.1), 0.4, emit=(1.0, 0.82, 0.1), emit_s=2.2)
    return [arrow_mesh(f'seta{i}', 6.0, 2.4, m, C) for i in range(n)]

def arrows_pose(arrows, T, f, x0=-30, x1=140, vis=1.0):
    """Setas que entram no corredor e aceleram (velocidade cresce com x: efeito corredor ilustrativo)."""
    n = len(arrows)
    for i, o in enumerate(arrows):
        lane = (i % 3 - 1) * 4.5; z = 6.0 + (i % 2) * 7.0
        u = ((T * 0.42 + i / n) % 1.0); x = x0 + (x1 - x0) * u ** 1.8      # x cresce cada vez mais rápido
        sc = (0.7 + 0.8 * u) * max(vis, 1e-4)
        o.location = (x, lane, z); o.scale = (sc * (0.8 + 0.9 * u), 1, sc); o.rotation_euler = (math.radians(90), 0, 0)
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)

def build_debris(C, seed=4, kinds=('placa', 'vidro', 'galho')):
    r = random.Random(seed); out = []
    pm = [B.mat_basic(f'Placa{i}', c, 0.5) for i, c in enumerate([(0.9, 0.15, 0.1), (0.95, 0.85, 0.2), (0.1, 0.35, 0.8), (0.95, 0.95, 0.95)])]
    glass = B.mat_basic('Caco', (0.7, 0.85, 0.9), 0.05, emit=(0.6, 0.75, 0.8), emit_s=0.3, alpha=0.55)
    wood = B.mat_basic('Galho', (0.3, 0.2, 0.12), 0.8); leaf = B.mat_basic('FolhaGalho', (0.18, 0.35, 0.1), 0.7)
    for i in range(36):
        k = kinds[i % len(kinds)]
        if k == 'placa': o = B.box('placa', (r.uniform(0.8, 1.6), r.uniform(0.5, 1.0), 0.04), (0, 0, 0), pm[i % 4], C)
        elif k == 'vidro': o = B.box('vidro_v', (r.uniform(0.3, 0.7), r.uniform(0.3, 0.6), 0.02), (0, 0, 0), glass, C)
        else:
            o = B.cyl('galho', 0.04, r.uniform(1.0, 1.8), (0, 0, 0), wood, C, seg=6, rot=(0, math.radians(90), 0))
            for j in range(3):
                lf = B.sphere('folhas', 0.28, (r.uniform(-0.6, 0.6), 0, r.uniform(-0.1, 0.1)), leaf, C, scale=(1.3, 0.5, 0.8), seg=8); lf.parent = o
        out.append(dict(o=o, kind=k, x0=r.uniform(-25, 15), y=r.uniform(-10, 10), z0=r.uniform(1.0, 9.0), ph=r.uniform(0, 1), sp=r.uniform(0.8, 1.3),
                        spin=Vector((r.uniform(-9, 9), r.uniform(-9, 9), r.uniform(-9, 9)))))
    return out

def debris_pose(deb, T, t_on, f, speed=24.0, span=70.0):
    for d in deb:
        u = T - t_on - d['ph'] * 0.8; o = d['o']
        if u < 0: o.scale = (1e-4,) * 3; o.location = (d['x0'], d['y'], d['z0'])
        else:
            uu = u % (span / (speed * d['sp']))
            o.location = (d['x0'] + uu * speed * d['sp'], d['y'] + 1.5 * math.sin(uu * 3 + d['ph'] * 6), d['z0'] + 2.0 * math.sin(uu * 2.2 + d['ph'] * 5))
            o.rotation_euler = (d['spin'] * uu)[:]; o.scale = (1.0,) * 3
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f); o.keyframe_insert('scale', frame=f)

def falling_tree(C, base, rot_z=0.0, scale=1.2):
    """Árvore com pivô na base: gira em torno de X local para tombar."""
    piv = B.link(bpy.data.objects.new('pivo_arvore', None), C); piv.location = base; piv.rotation_euler = (0, 0, rot_z)
    t = B.instance('tree_small_02', (0, 0, 0), 0.0, scale, C); t.parent = piv; return piv

# ------------------------------------------------------------------ furacão estilizado (espiral de nuvens)
def hurricane_mat(name='Furacao'):
    m, nb = new_mat(name); m.blend_method = 'BLEND'; out = nb.n('ShaderNodeOutputMaterial')
    tc = nb.n('ShaderNodeTexCoord'); x, y, z = nb.sep(tc.outputs['Object'])
    rr = nb.vmath('LENGTH', nb.comb(x, y, 0.0)); ang = nb.math('ARCTAN2', y, x)
    rot = nb.value('Giro', 0.0); forca = nb.value('Forca', 1.0)
    arms = nb.math('ADD', nb.math('MULTIPLY', nb.math('ADD', ang, rot), 2.0), nb.math('MULTIPLY', nb.math('LOGARITHM', nb.math('ADD', rr, 0.02), 2.718), -5.5))
    spiral = nb.math('ADD', 0.5, nb.math('MULTIPLY', nb.math('SINE', arms), 0.5))
    ns = nb.n('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 6.0; ns.inputs['Detail'].default_value = 8; ns.inputs['Roughness'].default_value = 0.6
    nb.link(nb.comb(nb.math('ADD', x, nb.math('MULTIPLY', rot, 0.1)), y, 0.0), ns.inputs['Vector'])
    dens = nb.math('MULTIPLY', nb.sstep(0.06, 0.13, rr), nb.math('SUBTRACT', 1.0, nb.sstep(0.45, 1.0, rr)))
    dens = nb.math('MULTIPLY', dens, nb.mixf(nb.sstep(0.12, 0.3, rr), 1.0, nb.math('POWER', spiral, 1.8)))
    dens = nb.math('MULTIPLY', dens, nb.sstep(0.28, 0.6, ns.outputs['Fac']))
    dens = nb.math('MINIMUM', 0.95, nb.math('MULTIPLY', dens, nb.math('MULTIPLY', forca, 1.3)))
    bs = nb.n('ShaderNodeBsdfDiffuse'); bs.inputs[0].default_value = (0.97, 0.97, 0.98, 1)
    em = nb.n('ShaderNodeEmission'); em.inputs[0].default_value = (0.9, 0.92, 0.96, 1); em.inputs[1].default_value = 0.25
    add = nb.n('ShaderNodeAddShader'); nb.link(bs.outputs[0], add.inputs[0]); nb.link(em.outputs[0], add.inputs[1])
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader')
    nb.link(dens, mx.inputs[0]); nb.link(tr.outputs[0], mx.inputs[1]); nb.link(add.outputs[0], mx.inputs[2]); nb.link(mx.outputs[0], out.inputs[0])
    return m

def build_hurricane(C, radius, layers=3, thick=0.0, name='Furacao'):
    m = hurricane_mat(name); root = B.link(bpy.data.objects.new(name, None), C)
    for i in range(layers):
        bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=1.0)
        o = B.mesh_obj(f'{name}_disco{i}', bm, m, C); o.parent = root
        o.location = (0, 0, thick * i / max(layers - 1, 1)); o.scale = (1 - 0.12 * i,) * 3; o.rotation_euler = (0, 0, i * 0.7); o.visible_shadow = False
    root.scale = (radius,) * 3
    return root, m

def set_mat_value(m, name, v, f):
    o = m.node_tree.nodes[name].outputs[0]; o.default_value = v; o.keyframe_insert('default_value', frame=f)

# ------------------------------------------------------------------ globo com furacão
SP = (-23.56, -46.66); CATARINA = (-28.6, -48.6)
def build_globo7(lat, lon, size=0.075):
    S2.setup_space_world(0.8); e = S2.build_earth(10.0)
    sd = Vector((0.2, -0.85, 0.45)).normalized(); S2.sun_lamp(sd, 4.5); S2.set_sunpos(tuple(sd * 1e5))
    C = e['coll']; piv = B.link(bpy.data.objects.new('furacao_pivo', None), C); piv.parent = e['spin']
    d = S2.latlon(lat, lon, 1.012); piv.location = d; piv.rotation_mode = 'QUATERNION'; piv.rotation_quaternion = d.to_track_quat('Z', 'Y')
    h, m = build_hurricane(C, size, layers=3, thick=0.004); h.parent = piv
    pin = S2.marker(e, SP[0], SP[1], (1.0, 0.82, 0.1), 'sao_paulo', 0.35)
    return dict(earth=e, hurricane=h, hmat=m, hpiv=piv, pin=pin)

# ------------------------------------------------------------------ corte do relevo (km na horizontal; escala vertical 1 un = 100 m)
def terrain_z(x):
    """Altura (unidades de 100 m) ao longo do perfil: planície até 8 km, serra até ~16 km, planalto ~800 m."""
    if x < 0: return -3.0
    if x < 8: return 0.15 + 0.02 * x
    if x < 16: u = (x - 8) / 8; return 0.3 + 7.7 * (3 * u * u - 2 * u * u * u)
    return 8.0 + 0.4 * math.sin(x * 0.35) + 0.25 * math.sin(x * 0.9)

def build_relevo():
    gradient_world((0.10, 0.16, 0.30), (0.55, 0.62, 0.72), 'CeuRelevo')
    C = B.new_coll('Relevo')
    bm = bmesh.new(); xs = [0.0 + 0.5 * i for i in range(181)]; D = 60.0
    top = [bm.verts.new((x, -D, terrain_z(x))) for x in xs]; topb = [bm.verts.new((x, D, terrain_z(x))) for x in xs]
    bot = [bm.verts.new((x, -D, -6.0)) for x in xs]; botb = [bm.verts.new((x, D, -6.0)) for x in xs]
    for i in range(len(xs) - 1):
        bm.faces.new((top[i], top[i + 1], topb[i + 1], topb[i]))
        bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    me = bpy.data.meshes.new('terreno'); bm.to_mesh(me); bm.free()
    land = B.link(bpy.data.objects.new('terreno', me), C)
    gm = B.mat_pbr('Mata', 'leafy_grass', 2.0, tint=(0.55, 0.75, 0.45)); rm = B.mat_basic('CorteTerra', (0.42, 0.3, 0.2), 0.9)
    land.data.materials.append(gm); land.data.materials.append(rm)
    for p in land.data.polygons: p.material_index = 0 if p.normal.z > 0.2 else 1
    sea = B.box('mar', (160, 2 * D, 0.1), (-80, 0, 0.0), S2.mat_water('MarQuente'), C)
    B.box('fundo_mar', (160, 2 * D, 0.1), (-80, 0, -6.0), B.mat_basic('FundoMar', (0.05, 0.15, 0.2), 0.8), C)
    sec = B.box('corte_mar', (160, 0.2, 6.0), (-80, -D, -3.0), B.mat_basic('AguaCorte', (0.05, 0.3, 0.45), 0.2, alpha=0.75), C)
    # cidade no planalto (x ≈ 60 km)
    city = B.mat_basic('CidadeSP', (0.75, 0.75, 0.78), 0.5); r = random.Random(3)
    for i in range(160):
        x = r.uniform(52, 68); y = r.uniform(-14, 14); h = r.uniform(0.4, 2.2)
        B.box('predinho', (r.uniform(0.3, 0.8), r.uniform(0.3, 0.8), h), (x, y, terrain_z(x) + h / 2), city, C)
    sun = bpy.data.lights.new('SolRelevo', 'SUN'); sun.energy = 3.0; sun.color = (1.0, 0.95, 0.88)
    so = B.link(bpy.data.objects.new('SolRelevo', sun)); so.rotation_euler = (math.radians(40), math.radians(-20), math.radians(10))
    h, m = build_hurricane(C, 18.0, layers=4, thick=0.5, name='FuracaoRelevo')
    # cota "60 km"
    line = B.mat_basic('Cota', (1, 1, 1), 0.4, emit=(1, 1, 1), emit_s=1.2)
    dim = B.box('cota', (60.0, 0.35, 0.35), (30.0, -16.0, 12.0), line, C); dim.scale = (1e-4, 1, 1)
    ticks = [B.box('cota_ponta', (0.35, 0.35, 2.4), (x, -16.0, 12.0), line, C) for x in (0.0, 60.0)]
    return dict(hurricane=h, hmat=m, dim=dim, ticks=ticks)
