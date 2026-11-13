"""Cenários do vídeo 06 (e se começasse um apocalipse zumbi no Brasil?). Reaproveita a rua do vídeo 04/05 e a Terra do vídeo 02, e acrescenta:
- cidade: a rua ao entardecer, abandonada (mato, carro parado, lixo) com "zumbis" estilizados ao longe (sem violência gráfica).
- mata: escala de formiga (1 unidade = 1 cm): caule, folhas, formiga-carpinteira, fungo crescendo da nuca e esporos.
- globo: Terra com alfinete na Zona da Mata de Minas Gerais.
- lab: fundo escuro com termômetro 3D.
- virus: vírions da raiva (forma de bala, como os reais) flutuando.
- bichos: cão e morcego estilizados (usados na rua)."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Euler, Matrix
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('scene05', os.path.join(HERE, '..', 'ep05', 'scene.py'))
S5 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S5)
for _k in dir(S5):
    if not _k.startswith('__'): globals()[_k] = getattr(S5, _k)
_spec2 = importlib.util.spec_from_file_location('scene02', os.path.join(HERE, '..', 'ep02', 'scene.py'))
S2 = importlib.util.module_from_spec(_spec2); _spec2.loader.exec_module(S2)

# ------------------------------------------------------------------ cidade abandonada ao entardecer
ZOMBIE = dict(B.TEO, skin=(0.52, 0.60, 0.48), shirt=(0.28, 0.24, 0.22), pants=(0.20, 0.20, 0.24), shoes=(0.25, 0.22, 0.2), cap=None, hair=(0.12, 0.1, 0.08))
def dusk(strength=0.16):
    w = bpy.context.scene.world; w.node_tree.nodes['Background'].inputs[1].default_value = strength
    sun = bpy.data.objects['Sol']; sun.data.energy = 1.6; sun.data.color = (1.0, 0.5, 0.25)
    sun.rotation_euler = Euler((math.radians(80), math.radians(0), math.radians(-60)))

def build_cidade(abandoned=True, n_zombies=6, seed=3):
    R = build_rua()
    if not abandoned: return R
    dusk()
    C = B.new_coll('Abandono'); r = random.Random(seed)
    # mato nas frestas da calçada e da rua
    for i in range(70):
        x = r.uniform(-10, 50); y = r.choice([r.uniform(2.6, 8.5), r.uniform(-6.5, -2.8), r.uniform(-1.5, 1.5)])
        B.instance(r.choice(['shrub_01', 'shrub_02', 'shrub_04']), (x, y, 0.15 if abs(y) > 2.5 else 0.0), r.uniform(0, 6.3), r.uniform(0.25, 0.7), C)
    grass = B.mat_basic('MatoSeco', (0.30, 0.36, 0.12), 0.9)
    for i in range(160):
        x = r.uniform(-10, 50); y = r.uniform(-7, 8.5)
        o = B.cyl('capim', 0.015, r.uniform(0.2, 0.5), (x, y, 0.15 if abs(y) > 2.5 else 0.05), grass, C, seg=5)
        o.rotation_euler = (r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), 0)
    lixo = B.mat_basic('Lixo', (0.35, 0.33, 0.3), 0.8)
    for i in range(25):
        B.box('lixo', (r.uniform(0.1, 0.4), r.uniform(0.1, 0.3), 0.04), (r.uniform(5, 40), r.uniform(-2.4, 7), 0.17), lixo, C, rot=(0, 0, r.uniform(0, 3)))
    car = R['car']; car['root'].location = (12.0, -1.9, 0.0); car['root'].rotation_euler = (0, 0, math.radians(14)); car['driver']['root'].hide_render = True
    for o in car['driver']['root'].children_recursive: o.hide_render = True
    for p in car['puffs']: p.hide_render = True
    # zumbis estilizados ao longe
    Z = []
    for i in range(n_zombies):
        z = B.build_character(f'Zumbi{i}', dict(ZOMBIE, shirt=(r.uniform(0.2, 0.35), r.uniform(0.18, 0.28), r.uniform(0.18, 0.26))), B.new_coll(f'ZumbiCol{i}'))
        x0 = 30.0 + i * 3.2 + r.uniform(-1, 1); y0 = r.uniform(-2.5, 2.5)
        z['root'].location = (x0, y0, 0.0); Z.append(dict(ch=z, x0=x0, y0=y0, ph=r.uniform(0, 6.3), sp=r.uniform(0.35, 0.6)))
    R['zombies'] = Z
    return R

def zombie_pose(zd, f, T):
    z = zd['ch']; ph = T * 2 * math.pi * 0.55 + zd['ph']; s = math.sin(ph)
    z['root'].location = (zd['x0'] - zd['sp'] * T, zd['y0'] + 0.15 * math.sin(T * 0.4 + zd['ph']), 0.0)
    z['root'].rotation_euler = (0, 0, math.radians(-90 + 8 * math.sin(T * 0.7 + zd['ph'])))
    B.pose(z, frame=f, spine=(12, 0, 6 * s), head=(18, 8 * math.sin(ph * 0.5), -10 * s),
           **{'thigh.L': (-14 * s, 0, 0), 'thigh.R': (14 * s, 0, 0), 'shin.L': (max(0, 22 * math.sin(ph + 1.6)), 0, 0), 'shin.R': (max(0, -22 * math.sin(ph + 1.6)), 0, 0),
              'upper_arm.L': (-80 + 6 * s, 0, -6), 'upper_arm.R': (-76 - 6 * s, 0, 6), 'forearm.L': (-10, 0, 0), 'forearm.R': (-14, 0, 0)})
    B.set_face(z, {'neutral': 1.0}, f)
    for o in (z['root'],): o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)

# ------------------------------------------------------------------ mata em escala de formiga (cm)
ANT_COL = (0.17, 0.08, 0.035)
def leaf_mesh(name, L, W, mat, C, curl=0.25, seed=0):
    bm = bmesh.new(); r = random.Random(seed); nu, nv = 24, 8; vs = {}
    for i in range(nu + 1):
        u = i / nu; w = W * math.sin(math.pi * u) ** 0.8 * (1 - 0.15 * u)
        for j in range(nv + 1):
            v = (j / nv) * 2 - 1
            x = u * L; y = v * w / 2; z = -curl * (v * v) * W * 0.4 + 0.15 * L * math.sin(math.pi * u * 0.6) * 0.2
            vs[i, j] = bm.verts.new((x, y, z))
    for i in range(nu):
        for j in range(nv): bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
    o = B.mesh_obj(name, bm, mat, C, True)
    sol = o.modifiers.new('esp', 'SOLIDIFY'); sol.thickness = 0.03
    return o

def leaf_material(name='Folha', col=(0.10, 0.32, 0.06)):
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); wv = nb.n('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3.0; wv.inputs['Distortion'].default_value = 1.5
    nb.link(tc.outputs['Object'], wv.inputs['Vector']); ramp = nb.n('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*col, 1); ramp.color_ramp.elements[1].color = (col[0] * 1.6, col[1] * 1.5, col[2] * 1.4, 1)
    nb.link(wv.outputs['Fac'], ramp.inputs[0]); nb.link(ramp.outputs[0], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.45; bs.inputs['Subsurface Weight'].default_value = 0.15
    nb.link(bs.outputs[0], out.inputs[0]); return m

def build_ant(name, C, col=ANT_COL, scale=1.0):
    """Formiga-carpinteira estilizada (~1,2 cm): cabeça, tórax, gáster, 6 pernas em 2 segmentos, antenas, mandíbulas. Frente = +X."""
    m = B.mat_basic(name + '_Corpo', col, 0.3, coat=0.8)
    root = B.link(bpy.data.objects.new(name, None), C); root.scale = (scale,) * 3
    head = B.sphere(name + '_cab', 0.13, (0.36, 0, 0.06), m, C, scale=(1.0, 1.1, 0.95), seg=24); head.parent = root
    th = B.sphere(name + '_torax', 0.11, (0.15, 0, 0.05), m, C, scale=(1.6, 0.8, 0.8), seg=24); th.parent = root
    pet = B.sphere(name + '_peciolo', 0.045, (-0.04, 0, 0.05), m, C, seg=16); pet.parent = root
    gas = B.sphere(name + '_gaster', 0.17, (-0.24, 0, 0.07), m, C, scale=(1.35, 1.0, 0.9), seg=24); gas.parent = root
    legs = []
    for k, x in enumerate((0.21, 0.15, 0.09)):
        for sd in (1, -1):
            hip = B.link(bpy.data.objects.new(f'{name}_quadril{k}{sd}', None), C); hip.parent = root; hip.location = (x, 0.05 * sd, 0.03)
            up = B.cyl(f'{name}_coxa{k}{sd}', 0.012, 0.2, (0, 0.1 * sd, 0.04), m, C, seg=8); up.rotation_euler = (math.radians(-65 * sd), 0, 0); up.parent = hip
            kn = B.link(bpy.data.objects.new(f'{name}_joelho{k}{sd}', None), C); kn.parent = hip; kn.location = (0, 0.18 * sd, 0.085)
            lo = B.cyl(f'{name}_tibia{k}{sd}', 0.009, 0.22, (0, 0.05 * sd, -0.09), m, C, seg=8); lo.rotation_euler = (math.radians(30 * sd), 0, 0); lo.parent = kn
            hip.rotation_euler = (0, 0, math.radians((k - 1) * -35 * sd)); legs.append((hip, k, sd))
    ants = []
    for sd in (1, -1):
        a = B.cyl(f'{name}_antena{sd}', 0.007, 0.22, (0.5, 0.06 * sd, 0.15), m, C, seg=6); a.rotation_euler = (math.radians(-25 * sd), math.radians(60), 0); a.parent = root; ants.append(a)
        md = B.box(f'{name}_mandibula{sd}', (0.07, 0.015, 0.015), (0.49, 0.035 * sd, 0.03), m, C); md.rotation_euler = (0, 0, math.radians(-25 * sd)); md.parent = root
    return dict(root=root, head=head, legs=legs, antennae=ants, mat=m)

def ant_walk(ant, f, T, speed=1.0, amp=22):
    for hip, k, sd in ant['legs']:
        ph = T * 2 * math.pi * 3.0 * speed + (k % 2) * math.pi + (0 if sd > 0 else math.pi)
        hip.rotation_euler = (math.radians(6 * math.sin(ph + 1.5) * (1 if amp else 0)), 0, math.radians((k - 1) * -35 * sd + amp * math.sin(ph)))
        hip.keyframe_insert('rotation_euler', frame=f)

def build_stroma(name, C, length=0.9):
    """Haste do fungo (estroma) que nasce da nuca da formiga; cresce pela escala Z (0 a 1). Ponta com 'cápsula' de esporos."""
    m = B.mat_basic(name + '_Mat', (0.78, 0.62, 0.40), 0.6)
    root = B.link(bpy.data.objects.new(name, None), C)
    cu = bpy.data.curves.new(name + '_cv', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.022; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for i, p in enumerate(((0, 0, 0), (0.05, 0.02, length * 0.5), (-0.06, 0.0, length))):
        bp = sp.bezier_points[i]; bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.bezier_points[2].radius = 0.5
    o = B.link(bpy.data.objects.new(name + '_haste', cu), C); o.parent = root; cu.materials.append(m)
    tip = B.sphere(name + '_ponta', 0.06, (-0.06, 0, length), B.mat_basic(name + '_Ponta', (0.62, 0.44, 0.26), 0.7), C, scale=(1, 1, 1.5), seg=16); tip.parent = root
    root.scale = (1, 1, 1e-3); return root

def build_mata(n_leaves=14, seed=5):
    gradient_world((0.16, 0.30, 0.12), (0.04, 0.09, 0.04), 'Mata')
    C = B.new_coll('Mata'); r = random.Random(seed)
    stem_m = B.mat_basic('Caule', (0.22, 0.30, 0.10), 0.6)
    stem = B.cyl('caule', 0.12, 16.0, (0, 0, 8.0), stem_m, C, seg=24)
    lm = leaf_material(); leaves = []
    # folha principal (onde a formiga morde): sai do caule a 9 cm, para +X, levemente inclinada
    main = leaf_mesh('folha_principal', 7.0, 3.2, lm, C, seed=1); main.location = (0.1, 0, 9.0); main.rotation_euler = (0, math.radians(-12), 0); leaves.append(main)
    for i in range(n_leaves):
        z = r.uniform(1.5, 15); a = r.uniform(0, 6.3); L = r.uniform(4, 8)
        lf = leaf_mesh(f'folha{i}', L, L * 0.45, lm, C, seed=i + 3); lf.location = (0.1 * math.cos(a), 0.1 * math.sin(a), z)
        lf.rotation_euler = (r.uniform(-0.3, 0.3), math.radians(r.uniform(-30, 10)), a)
        if abs(z - 9.0) < 1.5 and abs(math.cos(a) - 1) < 0.6: continue
        if math.sin(a) < 0.2: continue                       # nada entre a câmera (lado -Y) e a formiga
        leaves.append(lf)
    # fundo: folhas grandes desfocadas
    bg = leaf_material('FolhaFundo', (0.06, 0.20, 0.05))
    for i in range(10):
        lf = leaf_mesh(f'fundo{i}', 30, 14, bg, C, seed=40 + i); lf.location = (r.uniform(-30, 30), r.uniform(25, 45), r.uniform(-5, 20))
        lf.rotation_euler = (math.radians(80), r.uniform(-0.6, 0.6), r.uniform(-0.4, 0.4))
    key = bpy.data.lights.new('LuzMata', 'AREA'); key.energy = 900; key.size = 20; key.color = (1.0, 0.95, 0.8)
    ko = B.link(bpy.data.objects.new('LuzMata', key)); ko.location = (6, -14, 22); ko.rotation_euler = (math.radians(40), 0, math.radians(20))
    fill = bpy.data.lights.new('LuzMata2', 'AREA'); fill.energy = 250; fill.size = 20; fill.color = (0.7, 0.9, 1.0)
    fo = B.link(bpy.data.objects.new('LuzMata2', fill)); fo.location = (-12, -6, 4); fo.rotation_euler = (math.radians(80), 0, math.radians(-60))
    lo = bpy.data.lights.new('LuzBaixo', 'AREA'); lo.energy = 120; lo.size = 4; lo.color = (1.0, 0.95, 0.85)
    loo = B.link(bpy.data.objects.new('LuzBaixo', lo)); loo.location = (2.6, -2.5, 6.4); loo.rotation_euler = (math.radians(-130), 0, 0)
    return dict(stem=stem, leaves=leaves, main=main)

def spores(C, n, center, seed=9):
    m = B.mat_basic('Esporo', (0.95, 0.92, 0.8), 0.6, emit=(0.95, 0.92, 0.8), emit_s=1.2); r = random.Random(seed); out = []
    base = B.sphere('esporo_base', 0.012, (0, 0, 0), m, C, seg=8)
    for i in range(n):
        o = B.link(bpy.data.objects.new(f'esporo{i}', base.data), C); o.location = center; o.scale = (1e-4,) * 3; o.visible_shadow = False
        v = Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1.4, 0.2))).normalized() * r.uniform(0.4, 1.4)
        out.append((o, v, r.uniform(0, 1.0)))
    bpy.data.objects.remove(base)
    return out

# ------------------------------------------------------------------ globo
def build_globo():
    S2.setup_space_world(0.8); e = S2.build_earth(10.0)
    sd = Vector((0.3, -0.8, 0.4)).normalized(); S2.sun_lamp(sd, 4.5); S2.set_sunpos(tuple(sd * 1e5))
    pin = S2.marker(e, -21.0, -42.6, (1.0, 0.25, 0.12), 'zona_da_mata', 0.45)
    return dict(earth=e, pin=pin, latlon=S2.latlon)

# ------------------------------------------------------------------ laboratório: termômetro
def build_lab():
    gradient_world((0.06, 0.07, 0.10), (0.01, 0.01, 0.02), 'Lab')
    C = B.new_coll('Lab')
    glass = B.mat_thin_glass('VidroTermo', (0.85, 0.9, 0.95)); red = B.mat_basic('Mercurio', (0.85, 0.05, 0.03), 0.3, emit=(0.85, 0.05, 0.03), emit_s=0.8)
    B.cyl('tubo', 0.22, 6.0, (0, 0, 3.4), glass, C, seg=32); B.sphere('bulbo', 0.42, (0, 0, 0.2), glass, C, seg=32)
    B.sphere('bulbo_in', 0.34, (0, 0, 0.2), red, C, seg=32)
    col = B.cyl('coluna', 0.12, 1.0, (0, 0, 0), red, C, seg=24)
    for v in col.data.vertices: v.co.z += 0.5
    col.data.update(); col.location = (0, 0, 0.45)
    tm = B.mat_basic('Escala', (0.9, 0.9, 0.92), 0.4)
    for k in range(0, 41, 5):
        B.box('marca', (0.25 if k % 10 == 0 else 0.15, 0.02, 0.02), (0.36, 0, 0.6 + k / 40 * 5.4), tm, C)
    key = bpy.data.lights.new('LuzLab', 'AREA'); key.energy = 600; key.size = 6
    ko = B.link(bpy.data.objects.new('LuzLab', key)); ko.location = (3, -6, 6); ko.rotation_euler = (math.radians(50), 0, math.radians(25))
    return dict(column=col, temp_z=lambda c: 0.6 + c / 40 * 5.4 - 0.45)

# ------------------------------------------------------------------ vírus da raiva (forma de bala)
def virion_mesh(C, L=1.8, r=0.4):
    m = B.mat_basic('Virion', (0.55, 0.12, 0.16), 0.4, coat=0.5, emit=(0.6, 0.1, 0.15), emit_s=0.3)
    sp = B.mat_basic('Espicula', (0.85, 0.7, 0.75), 0.4)
    body = B.cyl('virion_corpo', r, L, (0, 0, 0), m, C, seg=32)
    cap = B.sphere('virion_ponta', r, (0, 0, L / 2), m, C, seg=32)
    parts = [body, cap]; rr = random.Random(2)
    for i in range(70):
        z = rr.uniform(-L / 2, L / 2 + r * 0.8); a = rr.uniform(0, 6.3)
        rad = r if z <= L / 2 else math.sqrt(max(r * r - (z - L / 2) ** 2, 0.01))
        s = B.cyl('espicula', 0.025, 0.18, (rad * math.cos(a) * 1.15, rad * math.sin(a) * 1.15, z), sp, C, seg=6)
        n = Vector((math.cos(a), math.sin(a), 0 if z <= L / 2 else (z - L / 2) / r)).normalized()
        s.rotation_mode = 'QUATERNION'; s.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(n); parts.append(s)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = body; bpy.ops.object.join(); body.name = 'virion'
    return body

def build_virus(n=26, seed=4):
    gradient_world((0.16, 0.03, 0.05), (0.03, 0.0, 0.01), 'Virus')
    C = B.new_coll('Virus'); base = virion_mesh(C); r = random.Random(seed); out = []
    for i in range(n):
        o = B.link(bpy.data.objects.new(f'virion{i}', base.data), C)
        o.location = (r.uniform(-9, 9), r.uniform(-4, 14), r.uniform(-6, 6)); o.rotation_euler = (r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3))
        o.keyframe_insert('location', frame=0); o.keyframe_insert('rotation_euler', frame=0)
        for fc in o.animation_data.action.fcurves:
            mm = fc.modifiers.new('NOISE'); mm.scale = 50 + r.uniform(0, 30); mm.strength = 0.8 if fc.data_path == 'location' else 1.5; mm.phase = r.uniform(0, 100)
        out.append(o)
    base.location = (0, 0, 0); base.scale = (1.4,) * 3; base.rotation_euler = (math.radians(70), math.radians(10), math.radians(30))
    key = bpy.data.lights.new('LuzVirus', 'AREA'); key.energy = 1500; key.size = 10
    ko = B.link(bpy.data.objects.new('LuzVirus', key)); ko.location = (4, -12, 8); ko.rotation_euler = (math.radians(50), 0, math.radians(15))
    return dict(hero=base, virions=out)

# ------------------------------------------------------------------ cão e morcego
def build_dog(name, C, coat=(0.62, 0.42, 0.22), tag=False):
    """Cão estilizado (~0,55 m de altura). Frente = -Y (como o Téo)."""
    m = B.mat_basic(name + '_Pelo', coat, 0.8); dark = B.mat_basic(name + '_Focinho', (0.08, 0.06, 0.05), 0.5)
    root = B.link(bpy.data.objects.new(name, None), C)
    body = B.sphere(name + '_corpo', 0.22, (0, 0, 0.45), m, C, scale=(0.75, 1.7, 0.8)); body.parent = root
    head = B.link(bpy.data.objects.new(name + '_cabeca', None), C); head.parent = root; head.location = (0, -0.38, 0.62)
    hs = B.sphere(name + '_cranio', 0.13, (0, -0.02, 0.04), m, C, scale=(0.9, 1.0, 0.9)); hs.parent = head
    sn = B.sphere(name + '_focinho', 0.07, (0, -0.14, 0.0), m, C, scale=(0.8, 1.3, 0.75)); sn.parent = head
    nose = B.sphere(name + '_nariz', 0.025, (0, -0.23, 0.02), dark, C); nose.parent = head
    for sd in (1, -1):
        ear = B.sphere(name + f'_orelha{sd}', 0.06, (0.09 * sd, 0.02, 0.13), m, C, scale=(0.5, 0.3, 1.2)); ear.parent = head
        eye = B.sphere(name + f'_olho{sd}', 0.016, (0.05 * sd, -0.12, 0.07), dark, C); eye.parent = head
    legs = []
    for x, y in ((0.1, -0.24), (-0.1, -0.24), (0.1, 0.24), (-0.1, 0.24)):
        piv = B.link(bpy.data.objects.new(name + '_perna', None), C); piv.parent = root; piv.location = (x, y, 0.42)
        lg = B.capsule(name + '_pata', 0.04, 0.36, m, C); lg.parent = piv; legs.append(piv)
    tail = B.link(bpy.data.objects.new(name + '_rabo', None), C); tail.parent = root; tail.location = (0, 0.36, 0.55)
    tl = B.capsule(name + '_rabo_m', 0.03, 0.26, m, C); tl.parent = tail; tl.rotation_euler = (math.radians(140), 0, 0)
    col = B.cyl(name + '_coleira', 0.085, 0.03, (0, 0.06, -0.05), B.mat_basic('Coleira', (0.1, 0.35, 0.85), 0.4), C, seg=24, rot=(math.radians(70), 0, 0)); col.parent = head
    if tag:
        t = B.cyl(name + '_plaquinha', 0.03, 0.006, (0, -0.06, -0.12), B.mat_basic('Plaquinha', (0.95, 0.8, 0.2), 0.2, 1.0), C, seg=24, rot=(math.radians(90), 0, 0)); t.parent = head
    return dict(root=root, head=head, legs=legs, tail=tail)

def dog_anim(d, f, T, mode='idle'):
    if mode == 'growl':
        k = 0.5 + 0.5 * math.sin(T * 9); d['head'].rotation_euler = (math.radians(12 + 6 * k), 0, math.radians(4 * math.sin(T * 5))); d['head'].location.z = 0.58
        d['tail'].rotation_euler = (math.radians(-30), 0, 0)
    else:
        d['head'].rotation_euler = (math.radians(-6 + 4 * math.sin(T * 1.3)), 0, math.radians(12 * math.sin(T * 0.7))); d['head'].location.z = 0.62
        d['tail'].rotation_euler = (math.radians(20), math.radians(25 * math.sin(T * 12)), 0)
    d['head'].keyframe_insert('rotation_euler', frame=f); d['head'].keyframe_insert('location', frame=f); d['tail'].keyframe_insert('rotation_euler', frame=f)

def build_bat(name, C):
    m = B.mat_basic(name + '_Pele', (0.12, 0.09, 0.08), 0.7); wing_m = B.mat_basic(name + '_Asa', (0.18, 0.12, 0.11), 0.8)
    root = B.link(bpy.data.objects.new(name, None), C)
    body = B.sphere(name + '_corpo', 0.05, (0, 0, 0), m, C, scale=(0.8, 1.6, 0.8)); body.parent = root
    hd = B.sphere(name + '_cab', 0.035, (0, -0.08, 0.01), m, C); hd.parent = root
    for sd in (1, -1):
        e = B.sphere(name + f'_orelha{sd}', 0.015, (0.02 * sd, -0.08, 0.045), m, C, scale=(0.6, 0.4, 1.5)); e.parent = root
    wings = []
    for sd in (1, -1):
        piv = B.link(bpy.data.objects.new(name + f'_asa{sd}', None), C); piv.parent = root; piv.location = (0.03 * sd, 0, 0.01)
        bm = bmesh.new(); pts = [(0, -0.05, 0), (0.12 * sd, -0.07, 0.01), (0.26 * sd, -0.02, 0), (0.22 * sd, 0.05, 0), (0.12 * sd, 0.03, 0), (0.05 * sd, 0.08, 0), (0, 0.06, 0)]
        vs = [bm.verts.new(p) for p in pts]; bm.faces.new(vs if sd > 0 else vs[::-1])
        w = B.mesh_obj(name + f'_membrana{sd}', bm, wing_m, C); w.parent = piv; wings.append((piv, sd))
    root.scale = (3.0,) * 3
    return dict(root=root, wings=wings)

def bat_anim(b, f, T):
    for piv, sd in b['wings']:
        piv.rotation_euler = (0, math.radians(55 * math.sin(T * 2 * math.pi * 6) * sd), 0); piv.keyframe_insert('rotation_euler', frame=f)
