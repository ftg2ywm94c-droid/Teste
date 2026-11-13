"""Cenários do vídeo 04 (e se o oxigênio sumisse por 20 segundos). Reaproveita a rua e o Téo do vídeo 01 e a Terra em corte do vídeo 03.
- rua: rua do vídeo 01 + prédio de concreto, mesa de café com vela, carrinho de lanche com chama de gás, carro com motorista.
- mol: o ar visto de perto — moléculas de N₂ (azuis) e O₂ (vermelhas) num fundo azul-escuro.
- ceu: céu (Poly Haven) com mar de nuvens e um jato estilizado.
- pulmao: pulmões estilizados (vista geral) e, ao lado, um alvéolo com capilar (vista de perto).
- cabine: interior de avião com máscaras de oxigênio.
- cristal: átomos do concreto/rocha (O ligado a Si e Ca) e moléculas de água.
- terra: Terra em corte do vídeo 03."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Matrix, Euler
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.append(os.path.join(HERE, '..', 'ep03'))
_spec = importlib.util.spec_from_file_location('scene03', os.path.join(HERE, '..', 'ep03', 'scene.py'))
S3 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S3)
NB, new_mat, set_value = S3.NB, S3.new_mat, S3.set_value
rnd = random.Random(4)

def mesh_from(name, verts, faces, mat, C, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = B.link(bpy.data.objects.new(name, me), C)
    if mat: o.data.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def emit_mat(name, color, s):
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); e = nb.n('ShaderNodeEmission')
    e.inputs[0].default_value = (*color, 1); e.inputs[1].default_value = s; nb.link(e.outputs[0], out.inputs[0]); return m

def plain_world(color, strength=1.0, name='Fundo'):
    sc = bpy.context.scene; w = bpy.data.worlds.new(name); sc.world = w; w.use_nodes = True
    N = w.node_tree.nodes; N['Background'].inputs[0].default_value = (*color, 1); N['Background'].inputs[1].default_value = strength

def gradient_world(top, bottom, name='Gradiente'):
    """Fundo em degradê vertical (visto pela câmera) e luz ambiente suave."""
    sc = bpy.context.scene; w = bpy.data.worlds.new(name); sc.world = w; w.use_nodes = True
    nb = NB(w.node_tree); nb.N.clear(); out = nb.n('ShaderNodeOutputWorld'); bg = nb.n('ShaderNodeBackground')
    tc = nb.n('ShaderNodeTexCoord'); z = nb.sep(tc.outputs['Generated'])[2]
    col = nb.mixc(nb.sstep(0.35, 0.75, z), bottom, top); nb.link(col, bg.inputs[0]); bg.inputs[1].default_value = 1.0
    nb.link(bg.outputs[0], out.inputs[0])

# ------------------------------------------------------------------ chama
def flame_material(name='Chama', blue_base=False):
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); e = nb.n('ShaderNodeEmission')
    tc = nb.n('ShaderNodeTexCoord'); z = nb.sep(tc.outputs['Generated'])[2]
    base = (0.25, 0.45, 1.0) if blue_base else (1.0, 0.45, 0.06)
    col = nb.mixc(nb.sstep(0.05, 0.45, z), base, (1.0, 0.62, 0.12)); col = nb.mixc(nb.sstep(0.55, 0.95, z), col, (1.0, 0.92, 0.55))
    nb.link(col, e.inputs[0]); e.inputs[1].default_value = 9.0
    lw = nb.n('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.45
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader')
    nb.link(nb.math('POWER', lw.outputs['Facing'], 1.6), mx.inputs[0]); nb.link(e.outputs[0], mx.inputs[1]); nb.link(tr.outputs[0], mx.inputs[2])
    nb.link(mx.outputs[0], out.inputs[0])
    return m

def flame(name, loc, h, r, C, blue_base=False, light=1.0):
    """Gota de fogo (esfera esticada e afinada no topo) + luz pontual quente. A origem fica na base da chama."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=1.0)
    for v in bm.verts:
        t = (v.co.z + 1) / 2; k = (1 - t) ** 0.55 * (1 + 0.6 * t) if t > 0.0 else 1.0
        v.co = Vector((v.co.x * r * k, v.co.y * r * k, t * h))
    root = B.link(bpy.data.objects.new(name + '_raiz', None), C); root.location = loc
    o = B.mesh_obj(name, bm, flame_material('Chama' + ('Gas' if blue_base else ''), blue_base), C, smooth=True)
    o.parent = root; o.visible_shadow = False
    lt = bpy.data.lights.new(name + '_luz', 'POINT'); lt.energy = 25.0 * light; lt.color = (1.0, 0.6, 0.25); lt.shadow_soft_size = r * 2
    lo = B.link(bpy.data.objects.new(name + '_luz', lt), C); lo.parent = root; lo.location = (0, 0, h * 0.4)
    return dict(root=root, obj=o, light=lo, energy=lt.energy)

def flicker(o, amount=0.08, speed=6.0, seed=0):
    """Tremulação barata: modificador de ruído nas curvas de escala (sem chave por quadro)."""
    o.keyframe_insert('scale', frame=0)
    for fc in o.animation_data.action.fcurves:
        if fc.data_path == 'scale':
            m = fc.modifiers.new('NOISE'); m.scale = speed; m.strength = amount * 2; m.phase = seed * 7 + fc.array_index * 3; m.blend_type = 'ADD'

# ------------------------------------------------------------------ rua
def concrete():
    return B.mat_pbr('Concreto', 'grey_plaster_02', 3.0, tint=(0.70, 0.72, 0.76), var=0.10)

def build_building(C, x0=12.0, x1=31.0, y0=10.0, y1=22.0, floors=7, fh=3.2):
    """Prédio de concreto aparente: lajes salientes, faixas de vidro, pilares; cobertura com casa de máquinas."""
    cm = concrete(); glass = B.mat_basic('VidroPredio', (0.10, 0.14, 0.18), 0.06, coat=0.5); frame = B.mat_basic('Caixilho', (0.18, 0.18, 0.2), 0.5)
    w, d = x1 - x0, y1 - y0; xc, yc = (x0 + x1) / 2, (y0 + y1) / 2; H = floors * fh
    B.box('predio_nucleo', (w - 0.6, d - 0.6, H), (xc, yc, H / 2 + 0.15), glass, C)
    for i in range(floors + 1):
        B.box('laje', (w + 0.5, d + 0.5, 0.42), (xc, yc, 0.15 + i * fh), cm, C, bevel=0.03)
    nx = 7
    for j in range(nx + 1):
        x = x0 + w * j / nx
        B.box('pilar', (0.45, 0.45, H), (x, y0 - 0.05, H / 2 + 0.15), cm, C)
        B.box('pilar', (0.45, 0.45, H), (x, y1 + 0.05, H / 2 + 0.15), cm, C)
    for i in range(floors):
        z = 0.15 + i * fh + fh * 0.5
        B.box('peitoril', (w, 0.25, 0.9), (xc, y0 - 0.1, 0.15 + i * fh + 0.66), cm, C)
        B.box('caixilho', (w - 0.4, 0.06, 0.06), (xc, y0 - 0.28, z + 0.7), frame, C)
    B.box('casa_maquinas', (5, 4, 2.6), (xc + 3, yc, H + 1.45), cm, C, bevel=0.05)
    B.box('entrada', (4.0, 1.6, 0.25), (xc, y0 - 1.2, 3.3), cm, C)
    return H + 0.15

def clear_area(x0, x1, y0, y1):
    """Apaga casas/telhados/janelas/cercas da rua do vídeo 01 cujo centro cai na área (lugar do prédio)."""
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or not o.name.split('.')[0] in ('casa', 'base', 'telhado', 'janela', 'vidro', 'porta'): continue
        x, y = o.location.x, o.location.y
        if o.name.startswith('telhado'): pass
        if x0 <= x <= x1 and y0 <= y <= y1: bpy.data.objects.remove(o)

def build_cafe(C, loc):
    x, y = loc; wood = B.mat_basic('Madeira', (0.42, 0.26, 0.14), 0.55); metal = B.mat_basic('MetalPreto', (0.05, 0.05, 0.06), 0.4, 0.8)
    B.cyl('mesa_tampo', 0.42, 0.04, (x, y, 0.92), wood, C, seg=40); B.cyl('mesa_pe', 0.035, 0.75, (x, y, 0.52), metal, C)
    B.cyl('mesa_base', 0.22, 0.03, (x, y, 0.165), metal, C, seg=32)
    for a in (40, 220):
        cx, cy = x + 0.62 * math.cos(math.radians(a)), y + 0.62 * math.sin(math.radians(a))
        B.cyl('cadeira_assento', 0.22, 0.04, (cx, cy, 0.62), wood, C, seg=32); B.cyl('cadeira_pe', 0.025, 0.47, (cx, cy, 0.38), metal, C)
    B.cyl('copo', 0.045, 0.1, (x - 0.15, y + 0.12, 0.99), B.mat_basic('Xicara', (0.95, 0.95, 0.93), 0.3), C)
    B.cyl('vela', 0.04, 0.14, (x + 0.1, y - 0.05, 1.01), B.mat_basic('Cera', (0.96, 0.93, 0.86), 0.45), C)
    B.cyl('pavio', 0.004, 0.02, (x + 0.1, y - 0.05, 1.09), B.mat_basic('Pavio', (0.05, 0.04, 0.03), 0.9), C)
    B.cyl('pote_vela', 0.075, 0.1, (x + 0.1, y - 0.05, 0.99), B.mat_thin_glass('PoteVidro', (0.8, 0.85, 0.85)), C)
    return flame('chama_vela', (x + 0.1, y - 0.05, 1.095), 0.07, 0.014, C, light=0.35)

def build_cart(C, loc):
    """Carrinho de lanche com chapa e boca de gás (anel de chamas azuladas)."""
    x, y = loc; body = B.mat_basic('Carrinho', (0.85, 0.18, 0.12), 0.4, coat=0.6); steel = B.mat_basic('Inox', (0.8, 0.8, 0.82), 0.25, 1.0)
    B.box('carrinho', (1.8, 0.9, 0.9), (x, y, 0.65), body, C, bevel=0.05)
    B.box('bancada', (1.9, 1.0, 0.04), (x, y, 1.12), steel, C)
    for sx in (-0.7, 0.7): B.cyl('roda', 0.18, 0.06, (x + sx, y - 0.46, 0.33), B.mat_basic('Borracha', (0.04, 0.04, 0.04), 0.8), C, rot=(math.radians(90), 0, 0))
    for sx in (-0.85, 0.85): B.cyl('haste', 0.02, 1.2, (x + sx, y + 0.4, 1.72), steel, C)
    aw = B.box('toldo', (2.0, 1.3, 0.05), (x, y + 0.05, 2.33), B.mat_basic('Toldo', (0.98, 0.85, 0.2), 0.6), C, rot=(math.radians(-10), 0, 0))
    B.cyl('queimador', 0.1, 0.03, (x + 0.35, y, 1.15), B.mat_basic('Queimador', (0.06, 0.06, 0.07), 0.5, 0.7), C, seg=32)
    [B.box('trempe', (0.34, 0.025, 0.025), (x + 0.35, y, 1.25), B.mat_basic('Ferro', (0.08, 0.08, 0.08), 0.6, 0.6), C, rot=(0, 0, math.radians(a))) for a in (0, 60, 120)]
    fl = []
    for i in range(10):
        a = 2 * math.pi * i / 10; fl.append(flame(f'chama_gas{i}', (x + 0.35 + 0.09 * math.cos(a), y + 0.09 * math.sin(a), 1.16), 0.10, 0.024, C, blue_base=True, light=0.12))
    return fl

def build_driver_car(C):
    car = B.build_car('CarroRua', (0.12, 0.35, 0.78), driver=False)
    P = dict(B.TEO_DRIVER, shirt=(0.75, 0.2, 0.28), cap=None, hair=(0.18, 0.12, 0.08))
    drv = B.build_character('Motorista', P, car['coll'], seated=True); drv['root'].parent = car['body']
    drv['root'].location = (-0.22, 0.38, 0.64 - drv['hip_z']); drv['root'].rotation_euler = (0, 0, math.radians(90))
    car['driver'] = drv
    # fumaça do escapamento: bolinhas cinza translúcidas atrás do carro
    sm = B.mat_basic('Fumaca', (0.55, 0.55, 0.56), 0.9, alpha=0.35); puffs = []
    for i in range(6):
        p = B.sphere(f'fumaca{i}', 0.09 + 0.03 * i, (-2.35 - 0.22 * i, -0.55, 0.3 + 0.03 * i), sm, car['coll'], seg=16)
        p.parent = car['body']; p.visible_shadow = False; puffs.append(p)
    car['puffs'] = puffs
    return car

def build_rua():
    B.setup_world(); C0 = B.build_street(signs=((-75.0, 50),))
    clear_area(10.0, 33.0, 8.0, 30.0)
    C = B.new_coll('Ep04Rua')
    top = build_building(C)
    candle = build_cafe(C, (17.2, 5.4)); gas = build_cart(C, (24.6, 5.5))
    car = build_driver_car(C)
    pole = B.cyl('poste_batida', 0.09, 4.5, (40.0, -4.0, 2.4), B.mat_basic('MetalPoste', (0.45, 0.47, 0.5), 0.4, 0.8), C)
    return dict(candle=candle, gas=gas, car=car, building_top=top)

# ------------------------------------------------------------------ moléculas do ar
N2_COL, O2_COL = (0.06, 0.28, 0.85), (0.85, 0.04, 0.02)
def molecule_proto(name, col, r=0.32, gap=0.42, glow=0.08):
    C = B.new_coll('proto_' + name); m = B.mat_basic('Atomo' + name, col, 0.25, coat=0.7, emit=col, emit_s=glow)
    a = B.sphere(name + '_a', r, (-gap / 2, 0, 0), m, C, seg=24); b = B.sphere(name + '_b', r, (gap / 2, 0, 0), m, C, seg=24)
    for o in (a, b):
        for p in o.data.polygons: p.use_smooth = True
    bpy.context.view_layer.layer_collection.children['proto_' + name].exclude = True
    return C

def build_molecules(n=520, box=(-14, 14, -14, 14, -9, 9), seed=3, frac_o2=0.21):
    """Campo de moléculas com deriva aleatória (ruído nas curvas). Proporção real: 78 % N₂, 21 % O₂ (argônio omitido)."""
    gradient_world((0.02, 0.05, 0.14), (0.0, 0.01, 0.04), 'ArMol')
    pN, pO = molecule_proto('N2', N2_COL), molecule_proto('O2', O2_COL, glow=0.25)
    C = B.new_coll('Moleculas'); r = random.Random(seed); mols = []
    for i in range(n):
        is_o = r.random() < frac_o2
        o = bpy.data.objects.new(f'mol{i}', None); o.instance_type = 'COLLECTION'; o.instance_collection = pO if is_o else pN
        o.location = (r.uniform(box[0], box[1]), r.uniform(box[2], box[3]), r.uniform(box[4], box[5]))
        o.rotation_euler = (r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3)); B.link(o, C)
        o.keyframe_insert('location', frame=0); o.keyframe_insert('rotation_euler', frame=0)
        for fc in o.animation_data.action.fcurves:
            m = fc.modifiers.new('NOISE'); m.scale = 40 + r.uniform(0, 30); m.strength = 0.9 if fc.data_path == 'location' else 2.0
            m.phase = r.uniform(0, 100)
        mols.append((o, is_o))
    key = bpy.data.lights.new('LuzMol', 'SUN'); key.energy = 2.5; key.angle = math.radians(20)
    ko = B.link(bpy.data.objects.new('LuzMol', key)); ko.rotation_euler = (math.radians(40), math.radians(20), math.radians(30))
    return mols

# ------------------------------------------------------------------ céu e avião
def cloud_deck(z=-600.0, size=40000.0, scale=0.0009, thr=(0.42, 0.62), name='MarNuvens', sea=True):
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); n1 = nb.n('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = scale; n1.inputs['Detail'].default_value = 8
    n1.inputs['Roughness'].default_value = 0.62; nb.link(tc.outputs['Object'], n1.inputs['Vector'])
    dens = nb.sstep(thr[0], thr[1], n1.outputs['Fac'])
    bs.inputs['Base Color'].default_value = (0.95, 0.96, 0.98, 1); bs.inputs['Roughness'].default_value = 1.0
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader'); nb.link(dens, mx.inputs[0]); nb.link(tr.outputs[0], mx.inputs[1]); nb.link(bs.outputs[0], mx.inputs[2])
    nb.link(mx.outputs[0], out.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z)); p = bpy.context.object; p.name = 'nuvens'; p.data.materials.append(m)
    p.visible_shadow = False
    if not sea: return p
    sea = B.mat_basic('MarLonge', (0.10, 0.22, 0.34), 0.3)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z - 900)); s = bpy.context.object; s.name = 'mar'; s.data.materials.append(sea)
    return p

def build_jet(C):
    """Jato bimotor estilizado (~38 m). Frente em +X. Devolve dict(root, glows[])."""
    root = B.link(bpy.data.objects.new('Jato', None), C)
    white = B.mat_basic('Fuselagem', (0.93, 0.94, 0.96), 0.3, 0.1, coat=0.6); blue = B.mat_basic('Faixa', (0.05, 0.25, 0.65), 0.35, coat=0.6)
    grey = B.mat_basic('AsaCinza', (0.75, 0.77, 0.8), 0.35, 0.3); dark = B.mat_basic('Para-brisa', (0.03, 0.04, 0.06), 0.1, coat=1.0)
    L, R = 38.0, 2.0
    fus = B.capsule('fuselagem', R, L - 2 * R, white, C); fus.rotation_euler = (0, math.radians(90), 0); fus.parent = root
    stripe = B.cyl('faixa', R * 1.004, L * 0.62, (1.0, 0, -0.35), blue, C, seg=48, rot=(0, math.radians(90), 0)); stripe.scale = (0.25, 1, 1); stripe.parent = root
    B.cyl('janelas', R * 1.006, L * 0.6, (0.5, 0, 0.45), dark, C, seg=48, rot=(0, math.radians(90), 0)).scale = (0.07, 1, 1)
    bpy.data.objects['janelas'].parent = root
    ws = B.sphere('parabrisa', R * 0.82, (L / 2 - 3.6, 0, 0.55), dark, C, scale=(0.9, 0.95, 0.45)); ws.parent = root
    def wing(name, span, root_c, tip_c, sweep, z, y_side, dihedral, x0, thick=0.35):
        bm = bmesh.new()
        pts = [(x0, 0), (x0 - root_c, 0), (x0 - sweep - tip_c, span), (x0 - sweep, span)]
        top = [bm.verts.new((x, y * y_side, z + abs(y) * math.tan(math.radians(dihedral)) + thick / 2)) for x, y in pts]
        bot = [bm.verts.new((x, y * y_side, z + abs(y) * math.tan(math.radians(dihedral)) - thick / 2)) for x, y in pts]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(4):
            j = (i + 1) % 4; bm.faces.new([top[i], bot[i], bot[j], top[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = B.mesh_obj(name, bm, grey, C); o.parent = root; return o
    for s in (-1, 1):
        wing(f'asa{s}', 16.0, 7.5, 2.2, 7.5, -0.9, s, 5, 4.0)
        wing(f'estab{s}', 6.0, 3.4, 1.4, 3.4, 0.4, s, 4, -14.0, 0.22)
    bm = bmesh.new()
    pts = [(-12.5, 0), (-17.5, 0), (-19.5, 7.0), (-17.0, 7.0)]
    vs = [[bm.verts.new((x, sy * 0.15, 1.2 + z)) for x, z in pts] for sy in (-1, 1)]
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[1])
    for i in range(4):
        j = (i + 1) % 4; bm.faces.new([vs[0][i], vs[0][j], vs[1][j], vs[1][i]])
    fin = B.mesh_obj('deriva', bm, blue, C); fin.parent = root
    glows = []
    for s in (-1, 1):
        nac = B.cyl(f'motor{s}', 1.15, 4.6, (1.2, s * 6.2, -2.3), white, C, seg=40, rot=(0, math.radians(90), 0)); nac.parent = root
        B.cyl(f'pilone{s}', 0.25, 1.4, (1.6, s * 6.2, -1.3), grey, C, seg=12).parent = root
        g = B.cyl(f'escape{s}', 0.75, 0.05, (-1.15, s * 6.2, -2.3), emit_mat(f'Escape{s}', (1.0, 0.55, 0.2), 6.0), C, seg=32, rot=(0, math.radians(90), 0))
        g.parent = root; g.visible_shadow = False; glows.append(g)
    return dict(root=root, glows=glows)

def build_ceu():
    B.setup_world(1.0); w = bpy.context.scene.world
    sun = bpy.data.objects['Sol']; sun.rotation_euler = Euler((math.radians(55), 0, math.radians(30)))
    cloud_deck(); cloud_deck(-250.0, scale=0.0016, thr=(0.55, 0.7), name='NuvensAltas', sea=False)
    C = B.new_coll('Ceu'); jet = build_jet(C)
    return dict(jet=jet)

# ------------------------------------------------------------------ pulmões e alvéolo
def tissue(name, col, rough=0.55, emit=0.0):
    return B.mat_basic(name, col, rough, coat=0.4, emit=col if emit else None, emit_s=emit)

def lobe(name, loc, scale, mat, C, seed=0):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=28, radius=1.0)
    r = random.Random(seed)
    for v in bm.verts:
        n = 1 + 0.04 * math.sin(5 * v.co.x + seed) * math.cos(4 * v.co.z + 2 * seed)
        if v.co.x * (1 if loc[0] > 0 else -1) < -0.2: n *= 0.85     # face interna achatada (onde fica o coração)
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])) * n
    o = B.mesh_obj(name, bm, mat, C, smooth=True); o.location = loc; return o

def build_pulmao():
    gradient_world((0.03, 0.02, 0.05), (0.0, 0.0, 0.01), 'Corpo')
    C = B.new_coll('Pulmoes'); lung = tissue('Pulmao', (0.92, 0.45, 0.48), 0.6); air = tissue('Traqueia', (0.85, 0.75, 0.72), 0.5)
    heart = tissue('Coracao', (0.6, 0.06, 0.08), 0.45)
    L = lobe('pulmao_esq', (-1.15, 0, 0), (0.95, 0.75, 1.55), lung, C, 1); R = lobe('pulmao_dir', (1.2, 0, 0.05), (1.05, 0.78, 1.6), lung, C, 2)
    B.cyl('traqueia', 0.22, 2.2, (0, 0.05, 2.35), air, C, seg=24)
    for s in (-1, 1):
        b = B.cyl(f'bronquio{s}', 0.15, 1.2, (s * 0.42, 0.05, 1.05), air, C, seg=20, rot=(0, math.radians(-s * 40), 0))
    B.sphere('coracao', 0.62, (0.25, -0.45, -0.55), heart, C, scale=(1.0, 0.9, 1.15))
    rim = bpy.data.lights.new('Contorno', 'AREA'); rim.energy = 900; rim.size = 6; rim.color = (0.7, 0.8, 1.0)
    ro = B.link(bpy.data.objects.new('Contorno', rim)); ro.location = (0, 6, 3); ro.rotation_euler = (math.radians(-65), 0, 0)
    key = bpy.data.lights.new('Chave', 'AREA'); key.energy = 700; key.size = 5; key.color = (1.0, 0.92, 0.85)
    ko = B.link(bpy.data.objects.new('Chave', key)); ko.location = (3, -7, 2); ko.rotation_euler = (math.radians(70), 0, math.radians(20))
    # partículas de O₂ dentro dos pulmões
    om = emit_mat('O2Brilho', O2_COL, 5.0); r = random.Random(9); dots = []
    for i in range(140):
        cx = r.choice((-1.15, 1.2)); p = Vector((r.gauss(0, 0.5), r.gauss(0, 0.35), r.gauss(0, 0.8)))
        s = B.sphere(f'o2p{i}', 0.045, (cx + p.x, p.y - 0.85, p.z), om, C, seg=10); s.visible_shadow = False; dots.append(s)
    # alvéolo (vista de perto) em x = 100
    AC = B.new_coll('Alveolo'); X = 100.0
    alv = tissue('Alveolo', (0.95, 0.62, 0.62), 0.5)
    sac = B.sphere('alveolo', 2.2, (X, 0, 0), alv, AC, seg=48); sac.data.materials[0] = alv
    mt = sac.data.materials[0]
    cap = tissue('Capilar', (0.75, 0.08, 0.1), 0.45)
    path = []
    for i in range(41):
        a = -math.pi * 0.85 + 1.7 * math.pi * i / 40; path.append((X + 2.45 * math.cos(a), -0.9 + 0.3 * math.sin(3 * a), 2.45 * math.sin(a)))
    cu = bpy.data.curves.new('capilar', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.32; cu.bevel_resolution = 6
    sp = cu.splines.new('POLY'); sp.points.add(len(path) - 1)
    for i, p in enumerate(path): sp.points[i].co = (*p, 1)
    co = B.link(bpy.data.objects.new('capilar', cu), AC); co.data.materials.append(B.mat_basic('CapilarParede', (0.9, 0.35, 0.38), 0.3, alpha=0.3)); co.visible_shadow = False
    for nm, loc, en in (('ChaveAlv', (X + 4, -8, 5), 1200), ('ContraAlv', (X - 5, 6, 2), 700)):
        l_ = bpy.data.lights.new(nm, 'AREA'); l_.energy = en; l_.size = 5; lo_ = B.link(bpy.data.objects.new(nm, l_)); lo_.location = loc
        d_ = Vector((X, 0, 0)) - Vector(loc); lo_.rotation_euler = d_.to_track_quat('-Z', 'Y').to_euler()
    rbc_m = tissue('Hemacia', (0.7, 0.03, 0.05), 0.35); cells = []
    for i in range(18):
        c = B.sphere(f'hemacia{i}', 0.22, (X, 0, 0), rbc_m, AC, scale=(1, 1, 0.42), seg=20); c.visible_shadow = False; cells.append(c)
    o2s = []
    for i in range(36):
        s = B.sphere(f'o2s{i}', 0.07, (X, 0, 0), om, AC, seg=10); s.visible_shadow = False; o2s.append(s)
    return dict(lungs=(L, R), dots=dots, X=X, path=path, cells=cells, o2s=o2s)

# ------------------------------------------------------------------ cabine do avião
def build_cabine():
    plain_world((0.55, 0.62, 0.72), 0.6, 'CeuJanela')
    C = B.new_coll('Cabine'); wall = B.mat_basic('ParedeCabine', (0.9, 0.9, 0.88), 0.5); floor_m = B.mat_basic('Carpete', (0.22, 0.24, 0.3), 0.9)
    seat = B.mat_basic('Poltrona', (0.08, 0.22, 0.5), 0.7); bin_m = B.mat_basic('Bagageiro', (0.94, 0.94, 0.93), 0.35)
    L = 18.0
    B.box('piso', (L, 3.6, 0.1), (0, 0, -0.05), floor_m, C)
    for s in (-1, 1):
        B.box(f'parede{s}', (L, 0.1, 2.4), (0, s * 1.85, 1.2), wall, C)
        B.box(f'bagageiro{s}', (L, 0.75, 0.55), (0, s * 1.45, 2.05), bin_m, C, bevel=0.06)
        for i in range(12):
            x = -L / 2 + 1.0 + i * 1.45
            B.box('janela', (0.32, 0.12, 0.45), (x, s * 1.81, 1.25), emit_mat('JanelaLuz', (0.75, 0.85, 1.0), 2.0), C, bevel=0.1)
    B.box('teto', (L, 3.8, 0.1), (0, 0, 2.45), wall, C)
    B.box('luz_teto', (L, 0.35, 0.03), (0, 0, 2.39), emit_mat('LuzTeto', (1.0, 0.95, 0.88), 3.0), C)
    rows = []
    for i in range(10):
        x = -L / 2 + 1.6 + i * 1.6
        for s in (-1, 1):
            for k in range(3):
                y = s * (0.62 + 0.5 * k)
                B.box('assento', (0.48, 0.46, 0.12), (x, y, 0.48), seat, C, bevel=0.04)
                B.box('encosto', (0.12, 0.46, 0.75), (x - 0.24, y, 0.85), seat, C, bevel=0.04)
        rows.append(x)
    # máscaras: copo amarelo + tubo, presas ao teto sobre cada fileira (lado direito)
    mk = B.mat_basic('Mascara', (0.98, 0.78, 0.08), 0.45); tube_m = B.mat_basic('TuboMascara', (0.92, 0.92, 0.9), 0.5)
    masks = []
    for i, x in enumerate(rows):
        for s in (-1, 1):
            for k in range(3):
                y = s * (0.62 + 0.5 * k)
                root = B.link(bpy.data.objects.new(f'mascara_{i}_{s}_{k}', None), C); root.location = (x + 0.15, y, 1.75)
                cup = B.cyl('copo_mascara', 0.07, 0.09, (0, 0, 0), mk, C, seg=20); cup.parent = root
                t = B.cyl('tubo_mascara', 0.008, 1.0, (0, 0, 0.5), tube_m, C, seg=8); t.parent = root
                masks.append((root, t))
    seated = B.build_character('Teo', B.TEO, B.new_coll('TeoCol'), seated=True)
    seated['root'].location = (rows[4] - 0.05, -0.62, 0.48 - seated['hip_z'] + 0.05); seated['root'].rotation_euler = (0, 0, math.radians(90))
    kl = bpy.data.lights.new('LuzCabine', 'AREA'); kl.energy = 400; kl.size = 4; kl.color = (1.0, 0.95, 0.9)
    ko = B.link(bpy.data.objects.new('LuzCabine', kl)); ko.location = (0, 0, 2.3)
    return dict(masks=masks, rows=rows, teo=seated)

# ------------------------------------------------------------------ átomos (concreto / rocha / água)
ATOM = dict(O=((0.85, 0.04, 0.02), 0.42), Si=((0.62, 0.52, 0.30), 0.5), Ca=((0.20, 0.62, 0.30), 0.55), H=((0.92, 0.92, 0.95), 0.25))
def atom_mat(el, glow=0.12):
    col = ATOM[el][0]; return B.mat_basic('Atomo_' + el, col, 0.25, coat=0.8, emit=col, emit_s=glow)

def bond(a, b, C, r=0.09, mat=None):
    a, b = Vector(a), Vector(b); d = b - a; o = B.cyl('ligacao', r, d.length, ((a + b) / 2)[:], mat or B.mat_basic('Ligacao', (0.85, 0.85, 0.88), 0.3), C, seg=12)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); return o

def build_cristal():
    gradient_world((0.05, 0.05, 0.08), (0.01, 0.01, 0.02), 'Atomos')
    C = B.new_coll('Cristal'); mats = {k: atom_mat(k, 0.25 if k == 'O' else 0.05) for k in ATOM}
    groups = dict(concreto=[], rocha=[], agua=[])
    # rede de silicato/cálcio (concreto e rocha): Si no centro de tetraedros de O; Ca entre eles
    def tetra(c, C2, key):
        c = Vector(c); tips = [Vector(v).normalized() * 1.6 for v in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))]
        objs = [B.sphere('Si', ATOM['Si'][1], c[:], mats['Si'], C2, seg=24)]
        for t in tips:
            objs.append(B.sphere('O', ATOM['O'][1], (c + t)[:], mats['O'], C2, seg=24)); objs.append(bond(c, c + t, C2))
        groups[key] += objs
    for i in range(-2, 3):
        for j in range(-1, 2):
            for k in range(-1, 2):
                tetra((i * 3.4, j * 3.4, k * 3.4), C, 'concreto' if i <= 0 else 'rocha')
                if (i + j + k) % 2 == 0: groups['concreto' if i <= 0 else 'rocha'].append(B.sphere('Ca', ATOM['Ca'][1], (i * 3.4 + 1.7, j * 3.4 + 1.7, k * 3.4 + 1.7), mats['Ca'], C, seg=24))
    # moléculas de água à direita
    W = Vector((20.0, 0, 0))
    for n in range(14):
        c = W + Vector((rnd.uniform(-3, 3), rnd.uniform(-3, 3), rnd.uniform(-3, 3))); ang = math.radians(104.5) / 2
        rot = Euler((rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3))).to_matrix()
        h1 = c + rot @ Vector((math.sin(ang), 0, math.cos(ang))) * 0.75; h2 = c + rot @ Vector((-math.sin(ang), 0, math.cos(ang))) * 0.75
        groups['agua'] += [B.sphere('O', ATOM['O'][1], c[:], mats['O'], C, seg=24), B.sphere('H', ATOM['H'][1], h1[:], mats['H'], C, seg=16),
                           B.sphere('H', ATOM['H'][1], h2[:], mats['H'], C, seg=16), bond(c, h1, C, 0.07), bond(c, h2, C, 0.07)]
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.data.polygons:
            for p in o.data.polygons: p.use_smooth = True
    key = bpy.data.lights.new('LuzAtomo', 'AREA'); key.energy = 3000; key.size = 10
    ko = B.link(bpy.data.objects.new('LuzAtomo', key)); ko.location = (4, -14, 10); ko.rotation_euler = (math.radians(50), 0, math.radians(15))
    return groups

# ------------------------------------------------------------------ Terra (vídeo 03)
def build_terra(R=10.0):
    S3.setup_space_world(stars=0.8)
    earth = S3.build_cut_earth(R, 'wedge')
    sd = Vector((0.6, -0.5, 0.45)).normalized(); S3.sun_lamp(sd, 4.2); S3.set_sunpos(tuple(sd * 1e5))
    return earth
