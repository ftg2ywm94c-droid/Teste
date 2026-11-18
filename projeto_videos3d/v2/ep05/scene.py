"""Cenários do vídeo 05 (e se TODO o oxigênio sumisse por 20 segundos). Reaproveita tudo do vídeo 04 (rua, moléculas, cristal, Terra)
e acrescenta:
- agua: moléculas de água (O vermelho, H branco); o O some e os H se juntam em pares (H₂) que se espalham como gás.
- mar: oceano (modificador Ocean) sob o céu; a superfície baixa e vira névoa.
- desmanche do prédio (rua): blocos de concreto que caem e viram pó; depois ficam como entulho.
- cristal: o mesmo do vídeo 04, com os átomos separados por elemento para sumir/espalhar."""
import bpy, math, os, random, importlib.util
from mathutils import Vector, Euler
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('scene04', os.path.join(HERE, '..', 'ep04', 'scene.py'))
S4 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S4)
for _k in dir(S4):
    if not _k.startswith('__'): globals()[_k] = getattr(S4, _k)

# ------------------------------------------------------------------ prédio que se desfaz
BLD_BOX = (12.0, 31.0, 10.0, 22.0)            # x0, x1, y0, y1 do prédio do vídeo 04
def building_objects():
    names = ('predio_nucleo', 'laje', 'pilar', 'peitoril', 'caixilho', 'casa_maquinas', 'entrada')
    return [o for o in bpy.data.objects if o.type == 'MESH' and o.name.split('.')[0] in names]

def chunk_list(seed=21, size=1.25, H=22.6):
    """Blocos na casca do prédio (frente, laterais e topo). Cada bloco: posição inicial, atraso, deriva e posição final no entulho."""
    x0, x1, y0, y1 = BLD_BOX; r = random.Random(seed); out = []
    def add(p):
        h = p[2] / H
        land = (p[0] + r.uniform(-3.5, 3.5) * (0.3 + h), p[1] - r.uniform(0.0, 4.0) * h, 0.0)
        out.append(dict(p0=Vector(p), delay=0.55 * (1 - h) + r.uniform(0, 0.35), land=Vector(land), spin=Vector((r.uniform(-4, 4), r.uniform(-4, 4), r.uniform(-4, 4))),
                        s_end=r.uniform(0.35, 0.75)))
    nz = int(H / size)
    for k in range(nz):
        z = 0.6 + k * size
        for i in range(int((x1 - x0) / size) + 1):
            add((x0 + i * size, y0 - 0.1, z))
        for j in range(1, int((y1 - y0) / size)):
            add((x0 - 0.1, y0 + j * size, z)); add((x1 + 0.1, y0 + j * size, z))
    for i in range(1, int((x1 - x0) / size)):
        for j in range(1, int((y1 - y0) / size), 2): add((x0 + i * size, y0 + j * size, H))
    return out

def chunk_state(c, T, t0, fall=1.6):
    """Posição, rotação e escala do bloco no tempo T (o desmanche começa em t0)."""
    u = (T - t0 - c['delay']) / fall
    if u <= 0: return c['p0'], (0, 0, 0), 1.0
    u = min(u, 1.0); e = u * u
    p = c['p0'].lerp(c['land'], e); top = c['land'].z + 0.35 * c['s_end']
    # pilha de entulho: os blocos de baixo ficam mais altos (o entulho tem volume)
    p = Vector((p.x, p.y, max(p.z, top + 1.2 * (1 - (c['p0'].z / 22.6)) * u)))
    s = 1.0 - (1.0 - c['s_end']) * min(u * 1.4, 1.0)
    return p, (c['spin'] * e)[:], s

def build_chunks(C, size=1.25):
    me = bpy.data.meshes.new('bloco'); import bmesh
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=size * 0.92); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    me.materials.append(concrete()); chunks = chunk_list(size=size)
    for i, c in enumerate(chunks):
        o = B.link(bpy.data.objects.new(f'bloco{i}', me), C); o.location = c['p0']; c['obj'] = o
    return chunks

def dust_puffs(C, n=40, seed=8):
    """Nuvem de pó: esferas cinza translúcidas que crescem no pé do prédio."""
    m = B.mat_basic('Po', (0.62, 0.6, 0.57), 0.95, alpha=0.18); r = random.Random(seed); out = []
    x0, x1, y0, y1 = BLD_BOX
    for i in range(n):
        p = (r.uniform(x0 - 2, x1 + 2), r.uniform(y0 - 6, y0 + 2), r.uniform(0.5, 6.0))
        o = B.sphere(f'po{i}', 1.0, p, m, C, seg=16); o.visible_shadow = False; o.scale = (1e-4,) * 3
        out.append((o, r.uniform(0.0, 1.2), r.uniform(1.8, 3.6)))
    return out

# ------------------------------------------------------------------ água: moléculas de H₂O
def build_agua(n=150, box=(-12, 12, -12, 12, -8, 8), seed=6):
    gradient_world((0.02, 0.07, 0.16), (0.0, 0.015, 0.05), 'AguaMol')
    C = B.new_coll('Agua'); r = random.Random(seed)
    mO = atom_mat('O', 0.25); mH = atom_mat('H', 0.08); mb = B.mat_basic('LigacaoAgua', (0.85, 0.85, 0.88), 0.3)
    me_O = bpy.data.meshes.new('O_mesh'); me_H = bpy.data.meshes.new('H_mesh')
    so = B.sphere('tmpO', 0.42, (0, 0, 0), mO, C, seg=24); sh = B.sphere('tmpH', 0.26, (0, 0, 0), mH, C, seg=16)
    for o in (so, sh):
        for p in o.data.polygons: p.use_smooth = True
    mols = []; ang = math.radians(104.5) / 2
    for i in range(n):
        c = Vector((r.uniform(box[0], box[1]), r.uniform(box[2], box[3]), r.uniform(box[4], box[5])))
        rot = Euler((r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3))).to_matrix()
        d1 = rot @ Vector((math.sin(ang), 0, math.cos(ang))) * 0.75; d2 = rot @ Vector((-math.sin(ang), 0, math.cos(ang))) * 0.75
        O = B.link(bpy.data.objects.new(f'aO{i}', so.data), C); O.location = c
        H1 = B.link(bpy.data.objects.new(f'aH{i}a', sh.data), C); H1.location = c + d1
        H2 = B.link(bpy.data.objects.new(f'aH{i}b', sh.data), C); H2.location = c + d2
        b1 = bond(c, c + d1, C, 0.07, mb); b2 = bond(c, c + d2, C, 0.07, mb)
        v = Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-0.6, 1))).normalized() * r.uniform(3.0, 6.0)
        mols.append(dict(c=c, d1=d1, d2=d2, O=O, H=(H1, H2), bonds=(b1, b2), v=v, ph=r.uniform(0, 6.3), dt=r.uniform(0, 0.3)))
    bpy.data.objects.remove(so); bpy.data.objects.remove(sh)
    key = bpy.data.lights.new('LuzAgua', 'AREA'); key.energy = 2600; key.size = 12
    ko = B.link(bpy.data.objects.new('LuzAgua', key)); ko.location = (4, -16, 10); ko.rotation_euler = (math.radians(55), 0, math.radians(15))
    return mols

def agua_state(m, T, t_gone, scatter=False):
    """Estado de uma molécula: deriva térmica; depois de t_gone o O some e os 2 H viram H₂ que se afasta (gás)."""
    j = Vector((0.25 * math.sin(T * 1.3 + m['ph']), 0.25 * math.cos(T * 1.1 + m['ph']), 0.2 * math.sin(T * 0.9 + 2 * m['ph'])))
    c = m['c'] + j; tg = t_gone + m['dt']
    if T < tg and not scatter: return dict(O=c, H1=c + m['d1'], H2=c + m['d2'], kO=1.0)
    u = 3.0 if scatter else T - tg
    pair = min(u / 0.25, 1.0)                                  # os dois H se aproximam (ligação H–H de 0,74 Å ≈ 0,5 aqui)
    mid = c + (m['d1'] + m['d2']) / 2 + m['v'] * max(u - 0.15, 0) * (0.6 + 0.4 * min(u, 1.5))
    ax = (m['d1'] - m['d2']).normalized() * 0.26
    h1 = (c + m['d1']).lerp(mid + ax, pair); h2 = (c + m['d2']).lerp(mid - ax, pair)
    kO = max(1.0 - u / 0.12, 0.0)
    return dict(O=c, H1=h1, H2=h2, kO=kO)

# ------------------------------------------------------------------ mar
def build_mar():
    B.setup_world(1.0)
    sun = bpy.data.objects['Sol']; sun.rotation_euler = Euler((math.radians(62), 0, math.radians(200)))
    C = B.new_coll('Mar')
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0)); sea = bpy.context.object; sea.name = 'oceano'
    B.link(sea, C) if sea.name not in C.objects else None
    m = sea.modifiers.new('ondas', 'OCEAN'); m.resolution = 12; m.size = 1.0; m.spatial_size = 120; m.wave_scale = 1.4; m.choppiness = 1.2
    m.wind_velocity = 14; m.repeat_x = 3; m.repeat_y = 3; m.use_normals = True
    water = B.mat_basic('AguaMar', (0.015, 0.09, 0.14), 0.04, coat=0.6); sea.data.materials.append(water)
    for p in sea.data.polygons: p.use_smooth = True
    sea.location = (0, 0, 0)
    # névoa: esferas brancas translúcidas que sobem
    mv = B.mat_basic('Vapor', (0.95, 0.96, 0.98), 0.95, alpha=0.14); r = random.Random(12); vap = []
    for i in range(110):
        p = Vector((r.uniform(-70, 70), r.uniform(20, 180), 0.0))
        o = B.sphere(f'vapor{i}', 1.0, p[:], mv, C, seg=16); o.visible_shadow = False; o.scale = (1e-4,) * 3
        vap.append((o, p, r.uniform(0.0, 0.8), r.uniform(9.0, 20.0), r.uniform(8.0, 22.0)))
    return dict(sea=sea, ocean=m, vapor=vap)

# ------------------------------------------------------------------ cristal com átomos por elemento
def build_cristal5():
    groups = build_cristal(); r = random.Random(9)
    atoms = dict(O=[], Si=[], Ca=[], H=[], bond=[])
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        nm = o.name.split('.')[0]
        if nm in ('O', 'Si', 'Ca', 'H'): atoms[nm].append(o)
        elif nm == 'ligacao': atoms['bond'].append(o)
    drift = {o.name: Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 0.4))).normalized() * r.uniform(1.5, 3.5)
             for o in atoms['Si'] + atoms['Ca'] + atoms['H']}
    return dict(groups=groups, atoms=atoms, drift=drift, p0={o.name: o.location.copy() for k in atoms for o in atoms[k]})

# ------------------------------------------------------------------ átomos de O soltos (a volta)
def loose_O(C, n, center, spread, seed=14, r_=0.12):
    m = atom_mat('O', 0.25); r = random.Random(seed); out = []
    base = B.sphere('Osolto_base', r_, (0, 0, 0), m, C, seg=20)
    for p in base.data.polygons: p.use_smooth = True
    for i in range(n):
        o = B.link(bpy.data.objects.new(f'Osolto{i}', base.data), C)
        p = Vector((center[0] + r.uniform(-spread[0], spread[0]), center[1] + r.uniform(-spread[1], spread[1]), center[2] + r.uniform(-spread[2], spread[2])))
        o.location = p; o.scale = (1e-4,) * 3; o.visible_shadow = False
        out.append((o, p, r.uniform(0, 0.6), r.uniform(0, 6.3)))
    bpy.data.objects.remove(base)
    return out
