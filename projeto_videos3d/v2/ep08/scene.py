"""Cenários do vídeo 08 (e se o fogo nunca tivesse sido descoberto?).
- savana: chão de capim seco, acácias (Poly Haven island_tree_01), pedras, céu HDRI de dia ou lua à noite
- fogueira: pedras, lenha, chamas (de ep04), brasas subindo, luz que tremula
- ancestrais: personagens com o mesmo boneco do Téo, cores de pele e roupas diferentes, sem boné
- estudio: fundo em degradê para objetos (raiz crua e assada, aço, cerâmica, vidro, cérebro)
- globo noturno: Terra com as luzes das cidades (de ep02)"""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Euler, Matrix
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, ep):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, '..', ep, 'scene.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S4 = _load('scene04', 'ep04'); S2 = _load('scene02', 'ep02')
NB, new_mat, emit_mat, gradient_world, flame, flicker = S2.NB, S2.new_mat, S4.emit_mat, S4.gradient_world, S4.flame, S4.flicker

# ------------------------------------------------------------------ materiais
def grass_mat():
    m, nb = new_mat('CapimSeco'); out = nb.n('ShaderNodeOutputMaterial'); b = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); n1 = nb.n('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.08; n1.inputs['Detail'].default_value = 6
    nb.link(tc.outputs['Object'], n1.inputs[0])
    n2 = nb.n('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 2.5; nb.link(tc.outputs['Object'], n2.inputs[0])
    c = nb.mixc(nb.sstep(0.35, 0.65, n1.outputs[0]), (0.42, 0.33, 0.14), (0.55, 0.47, 0.22))
    c = nb.mixc(nb.math('MULTIPLY', n2.outputs[0], 0.5), c, (0.30, 0.24, 0.12))
    nb.link(c, b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.95
    bump = nb.n('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4; nb.link(n2.outputs[0], bump.inputs['Height']); nb.link(bump.outputs[0], b.inputs['Normal'])
    nb.link(b.outputs[0], out.inputs[0]); return m

def blade_mat():
    m, nb = new_mat('Folhinha'); out = nb.n('ShaderNodeOutputMaterial'); b = nb.n('ShaderNodeBsdfPrincipled')
    hi = nb.n('ShaderNodeHairInfo'); c = nb.mixc(hi.outputs['Intercept'], (0.30, 0.24, 0.10), (0.78, 0.68, 0.36))
    rnd = nb.mixc(nb.math('MULTIPLY', hi.outputs['Random'], 0.6), c, (0.45, 0.42, 0.18))
    nb.link(rnd, b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.7
    nb.link(b.outputs[0], out.inputs[0]); return m

def rock_mesh(name, r, loc, C, seed, mat):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r); rr = random.Random(seed)
    for v in bm.verts: v.co *= 1 + rr.uniform(-0.18, 0.18)
    for v in bm.verts: v.co.z *= 0.6
    o = B.mesh_obj(name, bm, mat, C, True); o.location = loc; o.rotation_euler = (0, 0, rr.uniform(0, 6.3)); return o

# ------------------------------------------------------------------ savana
def build_savana(night=False, seed=4, grass=True):
    C = B.new_coll('Savana'); r = random.Random(seed)
    if night:
        S2.setup_space_world(0.25)                                          # céu escuro com estrelas
        w = bpy.context.scene.world
        for n in w.node_tree.nodes:
            if n.bl_idname == 'ShaderNodeBackground': n.inputs[1].default_value = 0.6
        moon = bpy.data.lights.new('Lua', 'SUN'); moon.energy = 0.45; moon.color = (0.55, 0.65, 1.0); moon.angle = math.radians(1)
        mo = B.link(bpy.data.objects.new('Lua', moon)); mo.rotation_euler = Euler((math.radians(55), 0, math.radians(140)))
    else:
        B.setup_world(1.0)
        sun = bpy.data.objects['Sol']; sun.data.energy = 4.0; sun.data.color = (1.0, 0.92, 0.80)
        sun.rotation_euler = Euler((math.radians(52), math.radians(6), math.radians(-30)))
    gm = grass_mat(); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=120, y_segments=120, size=200)
    for v in bm.verts:
        d = Vector((v.co.x, v.co.y)).length
        v.co.z = (0.25 * math.sin(v.co.x * 0.11) * math.cos(v.co.y * 0.09) + 0.0006 * max(d - 25, 0) ** 2 * 0.2) if d > 10 else 0.0
    ground = B.mesh_obj('chao', bm, gm, C, True)
    if grass:
        pb = bmesh.new(); bmesh.ops.create_grid(pb, x_segments=40, y_segments=20, size=1.0)
        for v in pb.verts: v.co.x *= 14; v.co.y *= 6
        patch = B.mesh_obj('capinzal', pb, gm, C, True); patch.location = (0, 9.5, 0.005)   # só atrás do Téo e da fogueira
        ps_mod = patch.modifiers.new('capim', 'PARTICLE_SYSTEM'); ps = ps_mod.particle_system.settings; ground = patch
        ps.type = 'HAIR'; ps.count = 16000; ps.hair_length = 0.22; ps.use_advanced_hair = True; ps.render_type = 'PATH'
        ps.child_type = 'INTERPOLATED'; ps.rendered_child_count = 6; ps.clump_factor = 0.4; ps.roughness_2 = 0.08
        ps.root_radius = 0.6; ps.tip_radius = 0.0; ps.radius_scale = 0.012; ps.use_hair_bspline = True
        ps.factor_random = 0.5; ground.data.materials.append(blade_mat()); ps.material = 2
        ground.particle_systems[0].seed = seed
    rm = B.mat_basic('Pedra', (0.36, 0.33, 0.30), 0.85)
    for i in range(26):
        a = r.uniform(0, 6.3); d = r.uniform(6, 60); rock_mesh(f'pedra{i}', r.uniform(0.2, 0.9), (d * math.cos(a), d * math.sin(a), 0.0), C, i, rm)
    for i, (x, y, s) in enumerate([(-14, 22, 1.4), (18, 30, 1.7), (-34, 48, 2.0), (40, 62, 2.2), (-6, 70, 1.9), (55, 20, 1.6), (-50, 15, 1.8)]):
        B.instance('island_tree_01', (x, y, 0.0), r.uniform(0, 6.3), s, C)
    return dict(ground=ground, coll=C)

# ------------------------------------------------------------------ fogueira
def build_fogueira(loc=(0, 0, 0), C=None, scale=1.0):
    C = C or B.new_coll('Fogueira'); root = B.link(bpy.data.objects.new('fogueira', None), C); root.location = loc; root.scale = (scale,) * 3
    rm = B.mat_basic('PedraFogo', (0.30, 0.28, 0.26), 0.8); wood = B.mat_basic('Lenha', (0.22, 0.13, 0.07), 0.8)
    char_ = B.mat_basic('Carvao', (0.03, 0.03, 0.03), 0.9, emit=(1.0, 0.25, 0.04), emit_s=0.0)
    for i in range(10):
        a = i / 10 * 2 * math.pi; o = rock_mesh(f'pfog{i}', 0.16, (0.62 * math.cos(a), 0.62 * math.sin(a), 0.05), C, 40 + i, rm); o.parent = root
    for i in range(5):
        a = i / 5 * 2 * math.pi + 0.3
        o = B.cyl(f'lenha{i}', 0.055, 0.85, (0.18 * math.cos(a), 0.18 * math.sin(a), 0.2), wood, C, seg=10)
        o.rotation_euler = Euler((math.radians(62), 0, a + math.pi / 2)); o.parent = root
    ember_bed = B.cyl('brasas', 0.38, 0.06, (0, 0, 0.03), char_, C, seg=20); ember_bed.parent = root
    fl = []
    for i, (dx, dy, h, rr) in enumerate([(0, 0, 0.78, 0.15), (0.13, 0.07, 0.55, 0.11), (-0.14, -0.04, 0.6, 0.11), (0.03, -0.15, 0.48, 0.09), (-0.06, 0.15, 0.5, 0.1), (0.16, -0.1, 0.38, 0.08), (-0.17, 0.1, 0.36, 0.08)]):
        f = flame(f'chama{i}', (dx, dy, 0.08), h, rr, C, light=0.0); f['root'].parent = root; flicker(f['obj'], 0.18, 9.0, i); fl.append(f)
    for m_ in bpy.data.materials:
        if m_.name.startswith('Chama'):
            for n_ in m_.node_tree.nodes:
                if n_.bl_idname == 'ShaderNodeEmission': n_.inputs[1].default_value = 3.2
    lt = bpy.data.lights.new('LuzFogo', 'POINT'); lt.energy = 600.0 * scale ** 2; lt.color = (1.0, 0.52, 0.18); lt.shadow_soft_size = 0.35
    lo = B.link(bpy.data.objects.new('LuzFogo', lt), C); lo.parent = root; lo.location = (0, 0, 0.7)
    sm = emit_mat('Fagulha', (1.0, 0.55, 0.15), 30.0); sparks = []
    for i in range(36):
        s = B.sphere(f'fagulha{i}', 0.012, (0, 0, 0), sm, C, seg=6); s.parent = root; s.visible_shadow = False; sparks.append(s)
    return dict(root=root, flames=fl, light=lo, sparks=sparks, bed=ember_bed, char=char_, energy=lt.energy)

def fire_pose(F, T, f, on=1.0, seed=1):
    """on: 0 apagada … 1 acesa. Luz tremula por soma de senos; fagulhas sobem em ciclos."""
    fl = 0.82 + 0.1 * math.sin(T * 13.1) + 0.06 * math.sin(T * 23.7 + 1) + 0.04 * math.sin(T * 41.0)
    F['light'].data.energy = F['energy'] * on * fl; F['light'].data.keyframe_insert('energy', frame=f)
    for x in F['flames']:
        x['root'].scale = (max(on, 1e-4),) * 3; x['root'].keyframe_insert('scale', frame=f)
    n = F['char'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']; n.default_value = 3.0 * on + 0.6 * (on > 0.01); n.keyframe_insert('default_value', frame=f)
    r = random.Random(seed)
    for i, s in enumerate(F['sparks']):
        per = r.uniform(1.2, 2.2); ph = r.uniform(0, per); u = ((T + ph) % per) / per; a = r.uniform(0, 6.3); rad = r.uniform(0.02, 0.25)
        s.location = (rad * math.cos(a) + 0.15 * math.sin(u * 7 + i), rad * math.sin(a), 0.3 + u * r.uniform(1.6, 2.6))
        k = on * (1 - u) * (u > 0.03); s.scale = (max(k, 1e-4),) * 3; s.keyframe_insert('location', frame=f); s.keyframe_insert('scale', frame=f)

# ------------------------------------------------------------------ ancestrais
SKINS = [(0.48, 0.32, 0.22), (0.62, 0.43, 0.30), (0.36, 0.24, 0.16), (0.72, 0.52, 0.38)]
def ancestor(i, C):
    P = dict(B.TEO, skin=SKINS[i % 4], shirt=[(0.52, 0.36, 0.20), (0.44, 0.30, 0.18), (0.60, 0.44, 0.26), (0.40, 0.33, 0.24)][i % 4],
             pants=[(0.36, 0.25, 0.14), (0.30, 0.22, 0.13), (0.42, 0.30, 0.18), (0.33, 0.27, 0.18)][i % 4], shoes=(0.30, 0.22, 0.15),
             cap=None, hair=[(0.08, 0.06, 0.05), (0.15, 0.09, 0.05), (0.05, 0.04, 0.04), (0.22, 0.14, 0.08)][i % 4], h=[1.0, 0.95, 1.05, 0.9][i % 4])
    return B.build_character(f'Anc{i}', P, C)

# ------------------------------------------------------------------ estúdio e objetos
def build_estudio(top=(0.10, 0.08, 0.07), bottom=(0.015, 0.012, 0.01), floor=True):
    gradient_world(top, bottom, 'Estudio'); C = B.new_coll('Estudio')
    if floor:
        fm = B.mat_basic('ChaoEstudio', (0.06, 0.05, 0.045), 0.55)
        f = B.cyl('piso', 7.0, 0.1, (0, 0, -0.05), fm, C, seg=64)
    key = bpy.data.lights.new('Chave', 'AREA'); key.energy = 520; key.size = 4; key.color = (1.0, 0.86, 0.72)
    ko = B.link(bpy.data.objects.new('Chave', key)); ko.location = (-3.5, -5, 5); ko.rotation_euler = (math.radians(50), 0, math.radians(-35))
    rim = bpy.data.lights.new('Recorte', 'AREA'); rim.energy = 380; rim.size = 3; rim.color = (0.6, 0.75, 1.0)
    ro = B.link(bpy.data.objects.new('Recorte', rim)); ro.location = (4, 5, 4); ro.rotation_euler = (math.radians(-55), 0, math.radians(-140))
    return dict(coll=C, key=ko, rim=ro)

def tuber(name, loc, C, cooked=False, seed=2):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=1.0); rr = random.Random(seed)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.55 * (1 + 0.1 * math.sin(v.co.z * 5 + seed)), v.co.y * 0.5, v.co.z * 1.0)) * (1 + rr.uniform(-0.03, 0.03))
    if cooked:
        m, nb = new_mat('RaizAssada'); out = nb.n('ShaderNodeOutputMaterial'); b = nb.n('ShaderNodeBsdfPrincipled')
        tc = nb.n('ShaderNodeTexCoord'); vo = nb.n('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 4.0; nb.link(tc.outputs['Object'], vo.inputs[0])
        c = nb.mixc(nb.sstep(0.15, 0.4, vo.outputs['Distance']), (0.06, 0.03, 0.015), (0.62, 0.32, 0.10)); nb.link(c, b.inputs['Base Color'])
        b.inputs['Roughness'].default_value = 0.55; b.inputs['Emission Color'].default_value = (1.0, 0.4, 0.1, 1); b.inputs['Emission Strength'].default_value = 0.0
        nb.link(b.outputs[0], out.inputs[0]); mat = m
    else:
        mat = B.mat_basic('RaizCrua', (0.50, 0.33, 0.20), 0.75)
    o = B.mesh_obj(name, bm, mat, C, True); o.location = loc; o.rotation_euler = (0, math.radians(75), 0); return o

def lathe(name, prof, mat, C, seg=48):
    """Sólido de revolução a partir de (raio, z)."""
    verts, faces = [], []
    for i in range(seg):
        a = i / seg * 2 * math.pi
        for r, z in prof: verts.append((r * math.cos(a), r * math.sin(a), z))
    n = len(prof)
    for i in range(seg):
        j = (i + 1) % seg
        for k in range(n - 1): faces.append((i * n + k, j * n + k, j * n + k + 1, i * n + k + 1))
    return S4.mesh_from(name, verts, faces, mat, C, smooth=True)

def build_objetos(C):
    steel = B.mat_basic('Aco', (0.62, 0.64, 0.68), 0.28, metal=1.0)
    beam = B.link(bpy.data.objects.new('aco', None), C)
    for nm, sz, z in (('aba1', (1.6, 0.6, 0.07), 0.48), ('alma', (1.6, 0.07, 0.9), 0.0), ('aba2', (1.6, 0.6, 0.07), -0.48)):
        o = B.box('viga_' + nm, sz, (0, 0, z), steel, C, bevel=0.01); o.parent = beam
    beam.rotation_euler = (0, 0, math.radians(30))
    clay = B.mat_basic('Ceramica', (0.66, 0.30, 0.16), 0.7)
    pot = lathe('ceramica', [(0.0, 0.0), (0.35, 0.0), (0.55, 0.25), (0.62, 0.55), (0.5, 0.9), (0.36, 1.05), (0.4, 1.15), (0.36, 1.17), (0.31, 1.07)], clay, C)
    glass = B.mat_basic('VidroGarrafa', (0.55, 0.85, 0.70), 0.03, transmission=1.0)
    bottle = lathe('vidro', [(0.0, 0.0), (0.32, 0.0), (0.34, 0.05), (0.34, 0.85), (0.28, 1.05), (0.13, 1.25), (0.12, 1.55), (0.15, 1.6), (0.12, 1.62), (0.10, 1.55), (0.10, 1.25)], glass, C)
    return dict(aco=beam, ceramica=pot, vidro=bottle)

def build_cerebro(C, loc=(0, 0, 1.4), r=0.9):
    m, nb = new_mat('Cerebro'); out = nb.n('ShaderNodeOutputMaterial'); b = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); wv = nb.n('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value = 3.2; wv.inputs['Detail'].default_value = 4; wv.inputs['Distortion'].default_value = 3.0
    nb.link(tc.outputs['Object'], wv.inputs[0]); ridge = nb.math('ABSOLUTE', nb.math('SUBTRACT', wv.outputs[0], 0.5))
    ridge = nb.sstep(0.0, 0.08, ridge)
    nb.link(nb.mixc(ridge, (0.62, 0.22, 0.30), (0.95, 0.52, 0.56)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.45; b.inputs['Subsurface Weight'].default_value = 0.25
    b.inputs['Emission Color'].default_value = (1.0, 0.45, 0.35, 1); b.inputs['Emission Strength'].default_value = 0.0
    bump = nb.n('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.9; nb.link(ridge, bump.inputs['Height']); nb.link(bump.outputs[0], b.inputs['Normal'])
    nb.link(b.outputs[0], out.inputs[0])
    root = B.link(bpy.data.objects.new('cerebro', None), C); root.location = loc
    for sx in (-1, 1):
        h = B.sphere(f'hemisferio{sx}', r, (sx * r * 0.27, 0, 0), m, C, scale=(0.5, 1.12, 0.74), seg=48); h.parent = root
    cb = B.sphere('cerebelo', r * 0.38, (0, r * 0.62, -r * 0.48), m, C, scale=(1.3, 0.8, 0.7), seg=32); cb.parent = root
    return dict(root=root, mat=m)

# ------------------------------------------------------------------ globo noturno (luzes das cidades)
def build_globo_noite():
    S2.setup_space_world(0.8); e = S2.build_earth(10.0)
    sd = Vector((-0.75, 0.6, 0.25)).normalized(); S2.sun_lamp(sd, 4.5); S2.set_sunpos(tuple(sd * 1e5))   # sol atrás: lado visível na noite
    return dict(earth=e, latlon=S2.latlon)
