"""Cenários do vídeo 03 (buraco que atravessa a Terra). Reaproveita a Terra do vídeo 02 (texturas Solar System Scope CC BY 4.0).
- Terra em corte: cunha (longitudes 0–90°, polo a polo) ou octante (a mesma cunha só no hemisfério norte, que expõe o Equador).
  Faces do corte com as camadas do modelo PREM (crosta, manto, núcleo externo líquido, núcleo interno).
- Túnel por dentro: poço cilíndrico com placas de metal e anéis de luz; a cor das paredes muda com a profundidade (K_prof).
- Polo: neve (Poly Haven CC0), boca do túnel com borda de segurança, placa com o nome do polo."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Matrix, Euler
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('scene02', os.path.join(HERE, '..', 'ep02', 'scene.py'))
S2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S2)
NB, new_mat, setup_space_world, set_value, set_sunpos, sun_lamp = S2.NB, S2.new_mat, S2.setup_space_world, S2.set_value, S2.set_sunpos, S2.sun_lamp
build_moon = S2.build_moon

# raios das camadas (fração do raio da Terra, PREM)
R_ICB, R_CMB, R_660, R_MOHO = 1221.5 / 6371, 3480 / 6371, 5701 / 6371, 6336 / 6371   # crosta média ~35 km

# ------------------------------------------------------------------ Terra em corte
def layers_material():
    m, nb = new_mat('Camadas'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); P = tc.outputs['Object']; r = nb.vmath('LENGTH', P)
    tn = nb.n('ShaderNodeTexNoise'); tn.inputs['Scale'].default_value = 7.0; tn.inputs['Detail'].default_value = 6; tn.inputs['Distortion'].default_value = 0.6
    nb.link(P, tn.inputs['Vector']); nz = tn.outputs['Fac']
    w = 0.004
    inner, outer, lowm, upm, crust = (1.0, 0.80, 0.30), (0.95, 0.38, 0.03), (0.50, 0.07, 0.02), (0.70, 0.20, 0.04), (0.30, 0.25, 0.21)
    col = nb.mixc(nb.sstep(R_ICB - w, R_ICB + w, r), inner, outer)
    col = nb.mixc(nb.sstep(R_CMB - w, R_CMB + w, r), col, lowm)
    col = nb.mixc(nb.sstep(R_660 - w, R_660 + w, r), col, upm)
    col = nb.mixc(nb.sstep(R_MOHO - 0.0015, R_MOHO + 0.0015, r), col, crust)
    col = nb.mixc(nb.math('MULTIPLY', nz, 0.35), col, (0.05, 0.02, 0.01))      # variação (convecção)
    # linhas finas nas fronteiras
    edge = 0.0
    for rb in (R_ICB, R_CMB, R_660):
        d = nb.math('ABSOLUTE', nb.math('SUBTRACT', r, rb)); e = nb.sstep(0.0025, 0.0, d)
        edge = e if isinstance(edge, float) else nb.math('MAXIMUM', edge, e)
    col = nb.mixc(nb.math('MULTIPLY', edge, 0.55), col, (0.02, 0.01, 0.0))
    nb.link(col, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.7
    # brilho de calor: núcleo interno > externo > manto inferior; K_calor intensifica (plano do "cinco mil graus")
    K = nb.value('K_calor', 1.0)
    heat = nb.mixf(nb.sstep(R_ICB - w, R_ICB + w, r), 1.5, 0.75)
    heat = nb.mixf(nb.sstep(R_CMB - w, R_CMB + w, r), heat, 0.12)
    heat = nb.mixf(nb.sstep(R_660 - w, R_660 + w, r), heat, 0.05)
    heat = nb.mixf(nb.sstep(R_MOHO - 0.002, R_MOHO + 0.002, r), heat, 0.0)
    hk = nb.math('MULTIPLY', heat, nb.math('ADD', 1.0, nb.math('MULTIPLY', nb.math('SUBTRACT', K, 1.0), nb.sstep(R_CMB + 0.02, 0.0, r))))
    nb.link(col, bs.inputs['Emission Color']); nb.link(nb.math('MULTIPLY', hk, nb.math('ADD', 0.75, nb.math('MULTIPLY', nz, 0.5))), bs.inputs['Emission Strength'])
    nb.link(bs.outputs[0], out.inputs[0]); return m

def _cut_sphere(name, r, mat, C, cut, seg=160):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    # alinha um meridiano com a longitude 0
    a0 = min((math.atan2(v.co.y, v.co.x) % (2 * math.pi / seg)) for v in bm.verts if abs(v.co.z) < r * 0.99)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-a0, 3, 'Z'))
    kill = []
    for f in bm.faces:
        c = f.calc_center_median(); lon = math.degrees(math.atan2(c.y, c.x))
        if 0.0 < lon < 90.0 and (cut == 'wedge' or c.z > 0): kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    o = B.mesh_obj(name, bm, mat, C, smooth=True); return o

def _disc(name, verts_fn, n, mat, C):
    """Leque de triângulos: centro + borda dada por verts_fn(i) (i=0..n)."""
    bm = bmesh.new(); c = bm.verts.new((0, 0, 0)); ring = [bm.verts.new(verts_fn(i)) for i in range(n + 1)]
    for i in range(n): bm.faces.new((c, ring[i], ring[i + 1]))
    return B.mesh_obj(name, bm, mat, C)

def build_cut_earth(R=10.0, cut='wedge'):
    C = B.new_coll('Terra')
    root = B.link(bpy.data.objects.new('Terra', None), C); root.rotation_mode = 'XYZ'
    spin = B.link(bpy.data.objects.new('TerraGiro', None), C); spin.parent = root; spin.rotation_mode = 'XYZ'
    e = _cut_sphere('TerraSup', 1.0, S2.earth_material(), C, cut); e.parent = spin
    cl = _cut_sphere('NuvensSup', 1.007, S2.cloud_material(), C, cut, seg=128); cl.parent = spin
    at = _cut_sphere('AtmosferaSup', 1.035, S2.atmosphere_material(), C, cut, seg=96); at.parent = spin
    at.visible_shadow = False; at.visible_diffuse = False; at.visible_glossy = False
    lm = layers_material(); n = 96; z0 = -math.pi / 2 if cut == 'wedge' else 0.0
    fa = _disc('CorteA', lambda i: (math.cos(z0 + (math.pi / 2 - z0) * i / n), 0.0, math.sin(z0 + (math.pi / 2 - z0) * i / n)), n, lm, C)
    fb = _disc('CorteB', lambda i: (0.0, math.cos(z0 + (math.pi / 2 - z0) * i / n), math.sin(z0 + (math.pi / 2 - z0) * i / n)), n, lm, C)
    faces = [fa, fb]
    if cut == 'octant':
        fe = _disc('CorteEq', lambda i: (math.cos(math.pi / 2 * i / n), math.sin(math.pi / 2 * i / n), 0.0), n, lm, C); faces.append(fe)
    for f in faces: f.parent = spin
    root.scale = (R,) * 3
    return dict(root=root, spin=spin, coll=C, R=R, faces=faces)

def tube(earth, name, a, b, radius, color, emit_s=3.0, parent='spin'):
    """Tubo (túnel) entre os pontos a e b em unidades da Terra. Origem em a; escala Z (0–1) faz o túnel 'crescer' de a até b."""
    C = earth['coll']; m = B.mat_basic('Tunel_' + name, color, 0.3, emit=color, emit_s=emit_s)
    a, b = Vector(a), Vector(b); L = (b - a).length
    o = B.cyl(name, radius, L, (0, 0, 0), m, C, seg=24)
    for v in o.data.vertices: v.co.z -= L / 2                             # de 0 a -L (ao longo de -Z local, de a para b)
    o.data.update()
    o.parent = earth[parent]; o.location = a; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = (a - b).to_track_quat('Z', 'Y')
    o.visible_shadow = False
    return o

def kola_tick(earth, lat=69.0):
    """Faixa vermelha de 12 km desenhada na face do corte (plano y=0), da superfície para dentro, na latitude de Kola."""
    C = earth['coll']; m = B.mat_basic('Kola', (1.0, 0.12, 0.08), 0.4, emit=(1.0, 0.12, 0.08), emit_s=4.0)
    d = 12.0 / 6371.0; w = 0.0035; la = math.radians(lat)
    u = Vector((math.cos(la), 0.0, math.sin(la))); t = Vector((-math.sin(la), 0.0, math.cos(la))); off = Vector((0, 0.0005, 0))
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in (u + t * w / 2 + off, u - t * w / 2 + off, u * (1 - d) - t * w / 2 + off, u * (1 - d) + t * w / 2 + off)]
    bm.faces.new(vs); o = B.mesh_obj('kola', bm, m, C); o.parent = earth['spin']
    return o

# ------------------------------------------------------------------ túnel por dentro
from scene_consts import SEG, TUN_R

def wall_material():
    """Placas de metal (Poly Haven) que esquentam com a profundidade: K_prof 0 = crosta, 1 = núcleo (brilho laranja-branco)."""
    m = B.mat_pbr('ParedeTunel', 'metal_plate', 2.0, tint=(0.75, 0.78, 0.82), var=0.12)
    nt = m.node_tree; N, L = nt.nodes, nt.links; bs = N['Principled BSDF']
    v = N.new('ShaderNodeValue'); v.name = 'K_prof'; v.outputs[0].default_value = 0.0
    tc = N.new('ShaderNodeTexCoord'); wv = N.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value = 0.6; wv.inputs['Detail'].default_value = 4
    L.new(tc.outputs['Object'], wv.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.0, 0.0, 0.0, 1)
    e1 = cr.elements.new(0.35); e1.color = (0.45, 0.03, 0.005, 1)
    e2 = cr.elements.new(0.7); e2.color = (0.85, 0.16, 0.01, 1)
    cr.elements[-1].position = 1.0; cr.elements[-1].color = (1.0, 0.30, 0.02, 1)
    L.new(v.outputs[0], ramp.inputs[0]); L.new(ramp.outputs[0], bs.inputs['Emission Color'])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; L.new(v.outputs[0], mul.inputs[0]); L.new(wv.outputs['Fac'], mul.inputs[1])
    mul2 = N.new('ShaderNodeMath'); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = 1.7; L.new(mul.outputs[0], mul2.inputs[0])
    L.new(mul2.outputs[0], bs.inputs['Emission Strength'])
    lk = bs.inputs['Base Color'].links[0]; dk = N.new('ShaderNodeMix'); dk.data_type = 'RGBA'; dk.blend_type = 'MULTIPLY'
    inv = N.new('ShaderNodeMath'); inv.operation = 'MULTIPLY_ADD'; inv.inputs[1].default_value = -0.85; inv.inputs[2].default_value = 1.0
    L.new(v.outputs[0], inv.inputs[0]); dk.inputs[0].default_value = 1.0
    cm = N.new('ShaderNodeCombineColor'); L.new(inv.outputs[0], cm.inputs[0]); L.new(inv.outputs[0], cm.inputs[1]); L.new(inv.outputs[0], cm.inputs[2])
    L.new(lk.from_socket, dk.inputs[6]); L.new(cm.outputs[0], dk.inputs[7]); L.new(dk.outputs[2], bs.inputs['Base Color'])
    return m

def ring_material():
    m = B.mat_basic('AnelLuz', (0.85, 0.95, 1.0), 0.3, emit=(0.80, 0.93, 1.0), emit_s=9.0)
    return m

def build_tunnel(C, z_top=0.0, length=420.0, open_top=True):
    """Poço vertical de z_top até z_top-length. Paredes viradas para dentro, anéis de luz a cada SEG m,
    quatro trilhos longitudinais e marcas de profundidade. Devolve o objeto raiz (mover em Z desloca tudo)."""
    root = B.link(bpy.data.objects.new('Tunel', None), C)
    wm = wall_material(); rm = ring_material(); dark = B.mat_basic('TrilhoTunel', (0.08, 0.08, 0.09), 0.4, metal=0.8)
    bm = bmesh.new(); n = 48; nz = int(length / 2.0)
    for k in range(nz + 1):
        z = z_top - length * k / nz
        for i in range(n):
            a = 2 * math.pi * i / n; bm.verts.new((TUN_R * math.cos(a), TUN_R * math.sin(a), z))
    bm.verts.ensure_lookup_table()
    for k in range(nz):
        for i in range(n):
            a, b_ = k * n + i, k * n + (i + 1) % n
            bm.faces.new((bm.verts[a], bm.verts[a + n], bm.verts[b_ + n], bm.verts[b_]))   # normais para dentro
    w = B.mesh_obj('TunelParede', bm, wm, C, smooth=True); w.parent = root
    z = z_top - 4.0; i = 0
    while z > z_top - length:
        bmr = bmesh.new(); bmesh.ops.create_cone(bmr, cap_ends=False, segments=64, radius1=TUN_R - 0.04, radius2=TUN_R - 0.04, depth=0.22)
        o = B.mesh_obj(f'anel{i}', bmr, rm, C); o.location = (0, 0, z); o.parent = root; o.visible_shadow = False
        z -= SEG; i += 1
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        t = B.box(f'trilho{k}', (0.14, 0.14, length), (0.92 * TUN_R * math.cos(a), 0.92 * TUN_R * math.sin(a), z_top - length / 2), dark, C, bevel=0.03)
        t.rotation_euler = (0, 0, a); t.parent = root
    return root

# ------------------------------------------------------------------ polo
def mat_hazard():
    m, nb = new_mat('BordaSeguranca'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); x, y, z = nb.sep(tc.outputs['Object'])
    a = nb.math('ARCTAN2', y, x); s = nb.math('SINE', nb.math('ADD', nb.math('MULTIPLY', a, 24.0), nb.math('MULTIPLY', z, 6.0)))
    k = nb.sstep(-0.05, 0.05, s)
    nb.link(nb.mixc(k, (0.02, 0.02, 0.02), (1.0, 0.72, 0.02)), bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.45
    nb.link(bs.outputs[0], out.inputs[0]); return m

def build_pole(name_txt='POLO NORTE'):
    C = B.new_coll('Polo')
    snow = B.mat_pbr('Neve', 'snow_02', 3.0, tint=(0.97, 0.99, 1.04), var=0.0, bump=0.5)
    # chão com ondulações suaves e um furo de 3,5 m de raio no centro
    bm = bmesh.new(); size, n = 900.0, 260
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=size / 2)
    rnd = random.Random(3); ph = [rnd.uniform(0, 6.28) for _ in range(8)]
    for v in bm.verts:
        x, y = v.co.x, v.co.y; d = math.hypot(x, y)
        h = 0.0
        for i, (fx, fy, amp) in enumerate(((0.011, 0.007, 0.9), (0.023, -0.017, 0.35), (-0.005, 0.013, 1.6), (0.047, 0.031, 0.12))):
            h += amp * math.sin(fx * x + fy * y + ph[i])
        h *= min(1.0, max(0.0, (d - 8.0) / 25.0)) ** 1.5        # plano perto do buraco
        h += max(0.0, d - 260.0) * 0.18                            # sobe ao longe (cristas de gelo no horizonte)
        v.co.z = h
    kill = [f for f in bm.faces if f.calc_center_median().xy.length < 3.6]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    nt = snow.node_tree; bsn = nt.nodes['Principled BSDF']; lk = bsn.inputs['Base Color'].links[0]
    mw = nt.nodes.new('ShaderNodeMix'); mw.data_type = 'RGBA'; mw.inputs[0].default_value = 0.55; mw.inputs[7].default_value = (0.93, 0.96, 1.0, 1)
    nt.links.new(lk.from_socket, mw.inputs[6]); nt.links.new(mw.outputs[2], bsn.inputs['Base Color'])
    g = B.mesh_obj('ChaoNeve', bm, snow, C, smooth=True)
    # anel de concreto entre o furo da malha e a borda do túnel
    con = B.mat_pbr('ConcretoPolo', 'concrete_pavement', 2.0, tint=(0.85, 0.87, 0.9))
    bmc = bmesh.new(); bmesh.ops.create_circle(bmc, segments=96, radius=5.2)
    ring_out = list(bmc.verts); bmesh.ops.create_circle(bmc, segments=96, radius=TUN_R)
    bmc.verts.ensure_lookup_table(); ins = bmc.verts[96:]
    for i in range(96): bmc.faces.new((ring_out[i], ring_out[(i + 1) % 96], ins[(i + 1) % 96], ins[i]))
    for v in bmc.verts: v.co.z = 0.02
    B.mesh_obj('LajeBoca', bmc, con, C)
    # borda de segurança (listras) e guarda-corpo baixo
    hz = mat_hazard()
    bmh = bmesh.new(); bmesh.ops.create_cone(bmh, cap_ends=False, segments=96, radius1=TUN_R + 0.02, radius2=TUN_R + 0.02, depth=0.35)
    for v in bmh.verts: v.co.z += 0.17
    B.mesh_obj('BordaListrada', bmh, hz, C, smooth=True)
    # placa
    post_m = B.mat_basic('PostePlaca', (0.75, 0.75, 0.78), 0.35, metal=0.9)
    B.cyl('poste_placa', 0.06, 2.6, (-5.2, 1.2, 1.3), post_m, C, seg=16)
    board_m = B.mat_basic('Placa', (0.85, 0.12, 0.10), 0.5)
    bd = B.box('placa', (2.6, 0.08, 0.9), (-5.2, 1.2, 2.35), board_m, C, bevel=0.06)
    cu = bpy.data.curves.new('placa_txt', 'FONT'); cu.body = name_txt; cu.font = bpy.data.fonts.load(B.FONT, check_existing=True)
    cu.size = 0.42; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = 0.01
    t = B.link(bpy.data.objects.new('placa_txt', cu), C); t.location = (-5.2, 1.15, 2.35); t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(B.mat_basic('PlacaTxt', (1, 1, 1), 0.5, emit=(1, 1, 1), emit_s=0.6))
    # poço por baixo (o mesmo túnel), com a boca no nível do chão
    tun = build_tunnel(C, z_top=0.0, length=300.0)
    return C, tun

def cold_world():
    """Céu do Poly Haven com tom mais frio e Sol baixo (polo)."""
    B.setup_world(1.0); w = bpy.context.scene.world; N, L = w.node_tree.nodes, w.node_tree.links
    bg = N['Background']; env = [n for n in N if n.bl_idname == 'ShaderNodeTexEnvironment'][0]
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    mx.inputs[7].default_value = (0.86, 0.93, 1.06, 1); L.new(env.outputs[0], mx.inputs[6]); L.new(mx.outputs[2], bg.inputs[0])
    sun = bpy.data.objects['Sol']; sun.rotation_euler = Euler((math.radians(76), 0, math.radians(-40))); sun.data.energy = 3.6
    sun.data.color = (1.0, 0.93, 0.82)
