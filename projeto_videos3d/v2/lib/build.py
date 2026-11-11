"""Construção da cena no Blender 4.2 (rua, casas, carro, personagens). Importado pelos scripts de plano.
Tudo procedural + assets CC0 do Poly Haven (assets/polyhaven). Eixo X = sentido do carro, Z = cima."""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
PH = os.path.join(PROJ, 'assets', 'polyhaven')
TEX = os.path.join(PROJ, 'v2', 'textures')
FONT = os.path.join(PROJ, 'fonts', 'Poppins-Bold.ttf')
rnd = random.Random(7)

# ------------------------------------------------------------------ utilidades
def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj); return obj

def new_coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in (parent or bpy.context.scene.collection).children: (parent or bpy.context.scene.collection).children.link(c)
    return c

def mesh_obj(name, bm, mat=None, coll=None, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if mat: me.materials.append(mat)
    return link(o, coll)

def box(name, size, loc=(0, 0, 0), mat=None, coll=None, bevel=0.0, seg=2, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = mesh_obj(name, bm, mat, coll); o.location = loc; o.rotation_euler = rot
    if bevel > 0:
        m = o.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = seg; m.limit_method = 'ANGLE'
        for p in o.data.polygons: p.use_smooth = True
        o.data.shade_smooth() if hasattr(o.data, 'shade_smooth') else None
    return o

def cyl(name, r, h, loc=(0, 0, 0), mat=None, coll=None, seg=24, rot=(0, 0, 0), smooth=True):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    o = mesh_obj(name, bm, mat, coll, smooth); o.location = loc; o.rotation_euler = rot; return o

def sphere(name, r, loc=(0, 0, 0), mat=None, coll=None, scale=(1, 1, 1), seg=32):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    o = mesh_obj(name, bm, mat, coll, True); o.location = loc; o.scale = scale; return o

def capsule(name, r, length, mat=None, coll=None, r2=None):
    """Cápsula ao longo de -Z a partir da origem (membro pendurado)."""
    r2 = r2 or r; bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=r2, radius2=r, depth=length)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -length / 2))
    for z, rr in ((0, r), (-length, r2)):
        s = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=rr)
        bmesh.ops.translate(bm, verts=s['verts'], vec=(0, 0, z))
    return mesh_obj(name, bm, mat, coll, True)

# ------------------------------------------------------------------ materiais
def _nodes(mat):
    mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs[0], out.inputs[0]); return nt, bsdf

def mat_basic(name, color, rough=0.5, metal=0.0, coat=0.0, emit=None, emit_s=0.0, transmission=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, b = _nodes(m)
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal; b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.04
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = emit_s
    if transmission: b.inputs['Transmission Weight'].default_value = transmission; b.inputs['IOR'].default_value = 1.45
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m

def mat_pbr(name, asset, size_m, tint=(1, 1, 1), var=0.18, rough_mul=1.0, bump=1.0):
    """PBR com projeção box em coordenadas de objeto (escala real, sem esticar) + variação de cor por ruído."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, b = _nodes(m); N, L = nt.nodes, nt.links
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / size_m,) * 3
    L.new(tc.outputs['Object'], mp.inputs[0])
    d = os.path.join(PH, asset)
    def img(suffix, cs):
        f = [x for x in os.listdir(d) if suffix in x][0]
        t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(d, f), check_existing=True)
        t.image.colorspace_settings.name = cs; t.projection = 'BOX'; t.projection_blend = 0.25; L.new(mp.outputs[0], t.inputs[0]); return t
    dif, nor, rou = img('_diff_', 'sRGB'), img('_nor_gl_', 'Non-Color'), img('_rough_', 'Non-Color')
    noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 0.35 / size_m * 3; L.new(tc.outputs['Object'], noise.inputs[0])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = var
    L.new(dif.outputs[0], mix.inputs[6]); L.new(noise.outputs['Color'], mix.inputs[7])
    tintn = N.new('ShaderNodeMix'); tintn.data_type = 'RGBA'; tintn.blend_type = 'MULTIPLY'; tintn.inputs['Factor'].default_value = 1.0
    tintn.inputs[7].default_value = (*tint, 1); L.new(mix.outputs[2], tintn.inputs[6]); L.new(tintn.outputs[2], b.inputs['Base Color'])
    mr = N.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = rough_mul
    L.new(rou.outputs[0], mr.inputs[0]); L.new(mr.outputs[0], b.inputs['Roughness'])
    nm = N.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = bump; L.new(nor.outputs[0], nm.inputs['Color']); L.new(nm.outputs[0], b.inputs['Normal'])
    return m

def mat_thin_glass(name, tint=(0.55, 0.62, 0.68)):
    """Vidro fino (sem refração): transparente + reflexo especular por Fresnel. Deixa o sol entrar no carro sem cáusticas."""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial'); mix = N.new('ShaderNodeMixShader'); tr = N.new('ShaderNodeBsdfTransparent')
    gl = N.new('ShaderNodeBsdfGlossy'); fr = N.new('ShaderNodeLayerWeight'); fr.inputs['Blend'].default_value = 0.25
    tr.inputs['Color'].default_value = (*tint, 1); gl.inputs['Roughness'].default_value = 0.02
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'; add.inputs[1].default_value = 0.16; add.use_clamp = True
    L.new(fr.outputs['Fresnel'], add.inputs[0]); L.new(add.outputs[0], mix.inputs[0]); L.new(tr.outputs[0], mix.inputs[1]); L.new(gl.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs[0]); return m

def mat_image(name, path, rough=0.4, emit=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, b = _nodes(m); N, L = nt.nodes, nt.links
    t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True); t.extension = 'CLIP'
    L.new(t.outputs[0], b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough
    if emit: L.new(t.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    return m

def mat_skin_face(name, skin, faces):
    """Pele + rosto desenhado projetado na frente da cabeça (-Y local). faces: lista de nomes; fatores em nós 'F_<nome>'."""
    m = bpy.data.materials.new(name); nt, b = _nodes(m); N, L = nt.nodes, nt.links
    b.inputs['Roughness'].default_value = 0.55; b.inputs['Subsurface Weight'].default_value = 0.08
    b.inputs['Subsurface Radius'].default_value = (0.4, 0.2, 0.1)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    # coordenadas geradas vão de 0..1 na caixa do objeto: x→u, z→v; frente = y baixo
    comb = N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0], comb.inputs[0]); L.new(sep.outputs[2], comb.inputs[1])
    front = N.new('ShaderNodeMath'); front.operation = 'LESS_THAN'; front.inputs[1].default_value = 0.45; L.new(sep.outputs[1], front.inputs[0])
    color = (*skin, 1); prev = None; alpha_sum = None
    base = N.new('ShaderNodeRGB'); base.outputs[0].default_value = color; cur = base.outputs[0]
    for f in faces:
        t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(os.path.join(TEX, f'face_{f}.png'), check_existing=True); t.extension = 'CLIP'
        L.new(comb.outputs[0], t.inputs[0])
        fac = N.new('ShaderNodeValue'); fac.name = f'F_{f}'; fac.outputs[0].default_value = 1.0 if f == faces[0] else 0.0
        a = N.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; L.new(t.outputs['Alpha'], a.inputs[0]); L.new(fac.outputs[0], a.inputs[1])
        a2 = N.new('ShaderNodeMath'); a2.operation = 'MULTIPLY'; L.new(a.outputs[0], a2.inputs[0]); L.new(front.outputs[0], a2.inputs[1])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(a2.outputs[0], mx.inputs['Factor']); L.new(cur, mx.inputs[6]); L.new(t.outputs[0], mx.inputs[7])
        cur = mx.outputs[2]
    L.new(cur, b.inputs['Base Color'])
    return m

# ------------------------------------------------------------------ mundo / render
def setup_world(strength=1.0):
    sc = bpy.context.scene; w = bpy.data.worlds.new('Ceu'); sc.world = w; w.use_nodes = True; N, L = w.node_tree.nodes, w.node_tree.links
    N.clear(); out = N.new('ShaderNodeOutputWorld'); bg = N.new('ShaderNodeBackground'); env = N.new('ShaderNodeTexEnvironment')
    hd = [x for x in os.listdir(os.path.join(PH, 'kloofendal_48d_partly_cloudy_puresky')) if x.endswith('.hdr')][0]
    env.image = bpy.data.images.load(os.path.join(PH, 'kloofendal_48d_partly_cloudy_puresky', hd))
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value[2] = math.radians(200)
    L.new(tc.outputs['Generated'], mp.inputs[0]); L.new(mp.outputs[0], env.inputs[0])
    L.new(env.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = strength; L.new(bg.outputs[0], out.inputs[0])
    sun = bpy.data.lights.new('Sol', 'SUN'); sun.energy = 4.2; sun.angle = math.radians(2.2); sun.color = (1.0, 0.95, 0.87)
    so = link(bpy.data.objects.new('Sol', sun)); so.rotation_euler = Euler((math.radians(48), math.radians(8), math.radians(-35)))

def setup_render(w, h, spp, preview=False):
    sc = bpy.context.scene; r = sc.render; c = sc.cycles
    r.engine = 'CYCLES'; c.device = 'CPU'; r.resolution_x, r.resolution_y = w, h; r.resolution_percentage = 100
    r.fps = 30; c.samples = spp; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03
    c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'
    c.max_bounces = 4; c.diffuse_bounces = 2; c.glossy_bounces = 2; c.transmission_bounces = 4; c.transparent_max_bounces = 6
    c.caustics_reflective = False; c.caustics_refractive = False; c.blur_glossy = 1.0
    c.light_sampling_threshold = 0.01; r.use_persistent_data = True
    r.use_motion_blur = not preview; r.motion_blur_shutter = 0.45
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = 0.15
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGB'; r.image_settings.color_depth = '8'
    r.use_overwrite = False; r.use_placeholder = True
    r.film_transparent = False
    sc.view_layers[0].use_pass_mist = True; sc.world.mist_settings.start = 60; sc.world.mist_settings.depth = 260; sc.world.mist_settings.falloff = 'QUADRATIC'
    # composição: névoa atmosférica leve pela passada de mist
    sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers'); comp = nt.nodes.new('CompositorNodeComposite')
    mix = nt.nodes.new('CompositorNodeMixRGB'); mix.blend_type = 'MIX'; mix.inputs[2].default_value = (0.70, 0.80, 0.92, 1)
    mul = nt.nodes.new('CompositorNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.22
    nt.links.new(rl.outputs['Mist'], mul.inputs[0]); nt.links.new(mul.outputs[0], mix.inputs[0]); nt.links.new(rl.outputs['Image'], mix.inputs[1])
    nt.links.new(mix.outputs[0], comp.inputs[0])

# ------------------------------------------------------------------ assets glTF (Poly Haven)
_GLTF = {}
def gltf_collection(name):
    """Importa um modelo glTF uma vez para uma coleção escondida e devolve a coleção (para instanciar)."""
    if name in _GLTF: return _GLTF[name]
    lib = new_coll('_lib'); c = new_coll('lib_' + name, lib)
    before = set(bpy.data.objects)
    f = [x for x in os.listdir(os.path.join(PH, name)) if x.endswith('.gltf')][0]
    bpy.ops.import_scene.gltf(filepath=os.path.join(PH, name, f))
    for o in set(bpy.data.objects) - before:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
    lib.hide_render = True; lib.hide_viewport = True
    bpy.context.view_layer.layer_collection.children['_lib'].exclude = True
    _GLTF[name] = c; return c

def instance(name, loc, rot_z=0.0, scale=1.0, coll=None):
    c = gltf_collection(name); o = bpy.data.objects.new(f'{name}_inst', None); o.instance_type = 'COLLECTION'; o.instance_collection = c
    o.location = loc; o.rotation_euler = (0, 0, rot_z); o.scale = (scale,) * 3; return link(o, coll)

# ------------------------------------------------------------------ rua e bairro
X0, X1 = -260.0, 140.0
def build_street(signs=((-150.0, 50), (-20.0, 50))):
    C = new_coll('Rua'); L = X1 - X0; xc = (X0 + X1) / 2
    asphalt = mat_pbr('Asfalto', 'asphalt_02', 4.0, tint=(0.82, 0.82, 0.84), var=0.22)
    walk = mat_pbr('Calcada', 'concrete_pavement', 1.6, tint=(0.95, 0.93, 0.9))
    grass = mat_pbr('Grama', 'leafy_grass', 2.5, tint=(0.55, 0.95, 0.35), var=0.3)
    curbm = mat_basic('MeioFio', (0.62, 0.62, 0.6), 0.75)
    box('asfalto', (L, 7.0, 0.1), (xc, 0, -0.05), asphalt, C)
    paint_w = mat_basic('TintaBranca', (0.85, 0.85, 0.82), 0.6); paint_y = mat_basic('TintaAmarela', (0.95, 0.68, 0.08), 0.6)
    for s in (-1, 1):
        box(f'faixa_borda{s}', (L, 0.12, 0.004), (xc, s * 3.2, 0.002), paint_w, C)
        box(f'meiofio{s}', (L, 0.16, 0.16), (xc, s * 3.58, 0.08), curbm, C, bevel=0.025)
        box(f'calcada{s}', (L, 2.5, 0.15), (xc, s * 4.91, 0.075), walk, C)
        box(f'grama{s}', (L, 80, 0.12), (xc, s * 46.16, 0.06), grass, C)
    x = X0
    while x < X1:                                   # linha central amarela tracejada (4 m / 4 m)
        for dy in (-0.09, 0.09): box('faixa_c', (4.0, 0.1, 0.004), (x + 2, dy, 0.002), paint_y, C)
        x += 8.0
    hills = mat_basic('Colinas', (0.30, 0.42, 0.24), 0.9)
    for i in range(14):                             # colinas distantes para profundidade
        sx = X0 + i * 32 + rnd.uniform(-8, 8)
        for s in (-1, 1): sphere('colina', 1.0, (sx, s * rnd.uniform(120, 170), -8), hills, C, scale=(rnd.uniform(40, 70), rnd.uniform(30, 45), rnd.uniform(16, 26)), seg=24)
    for sx, n in signs: speed_sign(sx, n, C)
    build_houses(C); build_props(C)
    return C

def speed_sign(x, n, C, side=-1):
    pole = mat_basic('Metal', (0.6, 0.62, 0.64), 0.35, 0.9)
    cyl('placa_poste', 0.035, 2.6, (x, side * 4.0, 1.45), pole, C)
    face = cyl('placa', 0.38, 0.03, (x - 0.03, side * 4.0, 2.55), mat_image(f'Placa{n}', os.path.join(TEX, f'sign_{n}.png'), 0.35), C, seg=48,
               rot=(0, math.radians(90), 0))
    # UV planar para a face: projeta a imagem pelo eixo do cilindro
    me = face.data; uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (0.5 + v.y / 0.78, 0.5 + v.x / 0.78)
    back = cyl('placa_tras', 0.385, 0.02, (x + 0.0, side * 4.0, 2.55), pole, C, seg=48, rot=(0, math.radians(90), 0))

HOUSE_COLORS = [(0.95, 0.88, 0.72), (0.78, 0.88, 0.95), (0.96, 0.80, 0.74), (0.86, 0.93, 0.80), (0.98, 0.95, 0.90), (0.92, 0.84, 0.94)]
def build_houses(C):
    roof_a = mat_pbr('TelhaA', 'clay_roof_tiles_02', 2.0, tint=(1.0, 0.85, 0.8)); roof_b = mat_pbr('TelhaB', 'grey_roof_tiles', 2.0)
    glass = mat_basic('VidroJanela', (0.12, 0.16, 0.2), 0.05, 0.0, coat=0.0); frame = mat_basic('Moldura', (0.95, 0.95, 0.93), 0.4)
    door_m = mat_basic('Porta', (0.38, 0.22, 0.12), 0.5); fence_m = mat_basic('Cerca', (0.96, 0.96, 0.94), 0.5)
    for s in (-1, 1):
        x = X0 + 6; k = 0
        while x < X1 - 10:
            w = rnd.uniform(9, 12); d = rnd.uniform(8, 10); hgt = rnd.choice([3.0, 3.0, 5.8]); y = s * (16 + d / 2 + rnd.uniform(-1, 1.5))
            col = HOUSE_COLORS[(k + (s > 0) * 3) % len(HOUSE_COLORS)]
            wall = mat_pbr(f'Parede{k % 6}{s}', 'painted_plaster_wall', 3.0, tint=col, var=0.12)
            box('casa', (w, d, hgt), (x + w / 2, y, hgt / 2 + 0.1), wall, C)
            box('base', (w + 0.1, d + 0.1, 0.35), (x + w / 2, y, 0.17), mat_basic('Rodape', (0.5, 0.48, 0.46), 0.8), C)
            roof(x + w / 2, y, w + 0.8, d + 0.9, hgt + 0.1, rnd.uniform(1.6, 2.4), roof_a if k % 3 else roof_b, C)
            fy = y - s * (d / 2 + 0.02)
            for wi in range(int(w // 3)):
                wx = x + 1.6 + wi * 3.0
                if abs(wx - (x + w / 2)) < 1.0: continue
                for fl in ([1.6] if hgt < 4 else [1.6, 4.3]):
                    box('janela', (1.3, 0.06, 1.2), (wx, fy, fl), frame, C); box('vidro', (1.1, 0.08, 1.0), (wx, fy, fl), glass, C)
            box('porta', (1.0, 0.08, 2.1), (x + w / 2, fy, 1.15), door_m, C)
            # cerca baixa na divisa com a calçada, com portão aberto
            gx = x + w / 2 + 2.5
            for a, b in ((x, gx - 0.75), (gx + 0.75, x + w)):
                if s < 0 and b > -4.5 and a < 2.5:      # entrada de garagem do quintal do menino (caminho dele e da bola)
                    for a2, b2 in ((a, -4.5), (2.5, b)):
                        if b2 - a2 > 0.2: picket_fence(a2, b2, s * 6.25, fence_m, C)
                    continue
                if b - a > 0.2: picket_fence(a, b, s * 6.25, fence_m, C)
            x += w + rnd.uniform(4, 8); k += 1

def picket_fence(a, b, y, mat, C):
    """Cerca de ripas: postes a cada 1,8 m, duas travessas e ripas de 9 cm a cada 16 cm, num único mesh."""
    bm = bmesh.new()
    def add(cx, cy, cz, sx, sy, sz):
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']: v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, cz + v.co.z * sz))
    n = max(int((b - a) / 0.16), 1)
    for i in range(n + 1):
        x = a + (b - a) * i / n; add(x, y, 0.58, 0.085, 0.022, 0.86)
    for z in (0.38, 0.8): add((a + b) / 2, y + 0.025, z, b - a, 0.03, 0.07)
    x = a
    while x <= b + 0.01: add(x, y + 0.03, 0.55, 0.09, 0.09, 0.95); x += 1.8
    o = mesh_obj('cerca', bm, mat, C)
    m = o.modifiers.new('b', 'BEVEL'); m.width = 0.008; m.segments = 1

def roof(xc, yc, w, d, z0, h, mat, C):
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (-w / 2, 0, h), (w / 2, 0, h)]]
    for f in ([0, 1, 5, 4], [2, 3, 4, 5], [0, 4, 3], [1, 2, 5], [0, 3, 2, 1]): bm.faces.new([v[i] for i in f])
    o = mesh_obj('telhado', bm, mat, C); o.location = (xc, yc, z0)
    m = o.modifiers.new('sol', 'SOLIDIFY'); m.thickness = 0.12

def build_props(C):
    """Árvores, arbustos, postes, hidrante, lixeiras (instâncias Poly Haven)."""
    for s in (-1, 1):
        x = X0 + 12
        while x < X1 - 5:
            if abs(x - 0.0) > 6:
                instance(rnd.choice(['island_tree_01', 'tree_small_02']), (x, s * rnd.uniform(9, 12), 0.12), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.15), C)
            x += rnd.uniform(14, 24)
        x = X0 + 3
        while x < X1:
            if not (s < 0 and -6 < x < 4):
                instance(rnd.choice(['shrub_01', 'shrub_02', 'shrub_04']), (x, s * rnd.uniform(6.8, 7.6), 0.12), rnd.uniform(0, 6.28), rnd.uniform(0.9, 1.4), C)
            x += rnd.uniform(5, 9)
        x = X0 + 15
        while x < X1:
            instance('street_lamp_01', (x, s * 3.95, 0.15), math.radians(90 if s < 0 else -90), 1.0, C); x += 32
    box('garagem', (6.5, 9.5, 0.03), (-1.0, -10.9, 0.135), mat_pbr('Garagem', 'concrete_pavement', 1.2, tint=(0.85, 0.85, 0.85)), C)
    instance('metal_trash_can', (7.5, -5.6, 0.15), 0.0, 1.0, C)
    instance('metal_trash_can', (-48.0, 5.6, 0.15), 0.0, 1.0, C)

# ------------------------------------------------------------------ carro
def build_car(name, paint_rgb, driver=True):
    """Hatch compacto procedural: carroceria em perfil extrudado com chanfros + subdivisão, cabine de vidro com colunas,
    caixas de roda recortadas, pneus com sulco, rodas de 5 raios, faróis, lanternas (emissão controlável), retrovisores, maçanetas.
    Origem = centro do carro no chão. Frente em +X. Devolve (root, rodas[], lanterna_material)."""
    C = new_coll(name); root = link(bpy.data.objects.new(name, None), C)
    body_root = link(bpy.data.objects.new(name + '_suspensao', None), C); body_root.parent = root
    paint = mat_basic(name + '_Pintura', paint_rgb, 0.32, 0.45, coat=1.0)
    trim = mat_basic('PlasticoPreto', (0.025, 0.025, 0.028), 0.55); chrome = mat_basic('Cromo', (0.9, 0.9, 0.92), 0.12, 1.0)
    glass = mat_thin_glass('VidroCarro')
    rubber = mat_basic('Borracha', (0.035, 0.035, 0.035), 0.8); rim = mat_basic('Aro', (0.72, 0.73, 0.75), 0.25, 1.0)
    head = mat_basic('Farol', (0.95, 0.95, 0.9), 0.05, 0.0, emit=(1, 0.95, 0.85), emit_s=1.5)
    tail = mat_basic(name + '_Lanterna', (0.5, 0.02, 0.02), 0.2, emit=(1, 0.05, 0.03), emit_s=0.6)
    interior = mat_basic('Interior', (0.12, 0.12, 0.13), 0.7)
    # carroceria inferior: perfil lateral (x,z) extrudado em y
    prof = [(-2.08, 0.30), (2.08, 0.30), (2.12, 0.52), (2.04, 0.76), (1.75, 0.86), (0.95, 0.98), (-1.70, 1.02), (-2.06, 0.94), (-2.12, 0.60)]
    W = 1.76
    bm = bmesh.new(); vs = []
    for sgn in (-1, 1): vs.append([bm.verts.new((x, sgn * W / 2, z)) for x, z in prof])
    n = len(prof); bm.faces.new(vs[0][::-1]); bm.faces.new(vs[1])
    for i in range(n):
        j = (i + 1) % n; bm.faces.new([vs[0][i], vs[0][j], vs[1][j], vs[1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = mesh_obj(name + '_carroceria', bm, paint, C); body.parent = body_root
    bv = body.modifiers.new('bev', 'BEVEL'); bv.width = 0.09; bv.segments = 4; bv.limit_method = 'ANGLE'
    for wx in (1.32, -1.30):                         # caixas de roda
        cut = cyl('corte', 0.42, 2.2, (wx, 0, 0.33), None, C, seg=40, rot=(math.radians(90), 0, 0)); cut.hide_render = True; cut.hide_viewport = True
        b = body.modifiers.new('arco', 'BOOLEAN'); b.object = cut; b.operation = 'DIFFERENCE'; b.solver = 'EXACT'
        cut.parent = body_root
    body.modifiers.new('sub', 'SUBSURF').levels = 1; body.data.shade_smooth()
    wn = body.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = True
    # cabine: perfil trapezoidal, vidro nas laterais/para-brisa, teto na cor do carro
    cab = [(0.98, 0.98), (0.05, 1.50), (-1.20, 1.52), (-1.78, 1.02)]
    bm = bmesh.new(); vs = []
    for sgn in (-1, 1): vs.append([bm.verts.new((x, sgn * 0.70, z)) for x, z in cab])
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[1])
    for i in range(4):
        j = (i + 1) % 4; bm.faces.new([vs[0][i], vs[0][j], vs[1][j], vs[1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cabin = mesh_obj(name + '_cabine', bm, glass, C); cabin.parent = body_root
    bv = cabin.modifiers.new('bev', 'BEVEL'); bv.width = 0.05; bv.segments = 3
    roof = box(name + '_teto', (1.40, 1.42, 0.06), (-0.57, 0, 1.51), paint, C, bevel=0.025); roof.parent = body_root
    for x0, z0, x1, z1 in ((0.98, 0.98, 0.05, 1.50), (-1.78, 1.02, -1.20, 1.52)):          # colunas A e C
        for sgn in (-1, 1):
            L = math.hypot(x1 - x0, z1 - z0); ang = math.atan2(z1 - z0, x1 - x0)
            p = box('coluna', (L, 0.07, 0.07), ((x0 + x1) / 2, sgn * 0.69, (z0 + z1) / 2), paint, C, rot=(0, -ang, 0), bevel=0.015); p.parent = body_root
    for sgn in (-1, 1):
        p = box('colunaB', (0.09, 0.05, 0.50), (-0.45, sgn * 0.70, 1.26), trim, C); p.parent = body_root
        m = box('retrovisor', (0.14, 0.2, 0.11), (0.82, sgn * 0.98, 1.05), paint, C, bevel=0.03); m.parent = body_root
        for hx in (0.15, -0.95):
            h = box('macaneta', (0.16, 0.02, 0.03), (hx, sgn * 0.885, 0.86), chrome, C, bevel=0.008); h.parent = body_root
        for lx in (0.62, -0.42):
            ln = box('friso_porta', (0.008, 0.012, 0.52), (lx, sgn * 0.886, 0.70), trim, C); ln.parent = body_root
        f = box('farol', (0.08, 0.36, 0.13), (2.05, sgn * 0.58, 0.70), head, C, bevel=0.03, rot=(0, math.radians(-25), 0)); f.parent = body_root
        t = box('lanterna', (0.06, 0.32, 0.16), (-2.10, sgn * 0.6, 0.80), tail, C, bevel=0.02); t.parent = body_root
    g = box('grade', (0.06, 0.8, 0.14), (2.10, 0, 0.50), trim, C, bevel=0.02); g.parent = body_root
    for x in (2.13, -2.15):
        b = box('parachoque', (0.12, 1.72, 0.16), (x, 0, 0.36), trim, C, bevel=0.05); b.parent = body_root
    box('soleira', (1.62, 1.80, 0.13), (0.01, 0, 0.37), trim, C, bevel=0.03).parent = body_root
    pl = box('placa', (0.02, 0.4, 0.13), (-2.16, 0, 0.56), mat_basic('PlacaCarro', (0.92, 0.92, 0.9), 0.4), C); pl.parent = body_root
    # interior visível pelo vidro: painel, bancos, volante
    box('painel', (0.4, 1.5, 0.25), (0.78, 0, 0.93), interior, C).parent = body_root
    for sy in (0.38, -0.38):
        box('banco', (0.5, 0.5, 0.12), (-0.25, sy, 0.50), interior, C, bevel=0.04).parent = body_root
        box('encosto', (0.12, 0.5, 0.62), (-0.55, sy, 0.95), interior, C, bevel=0.04, rot=(0, math.radians(-12), 0)).parent = body_root
    box('banco_tras', (0.5, 1.4, 0.5), (-1.25, 0, 0.75), interior, C, bevel=0.05).parent = body_root
    wheel_s = link(bpy.data.objects.new('volante_eixo', None), C); wheel_s.parent = body_root; wheel_s.location = (0.48, 0.38, 1.0); wheel_s.rotation_euler = (0, math.radians(-62), 0)
    vt = bpy.data.meshes.new('volante'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=24, radius1=0.19, radius2=0.19, depth=0.03); bm.to_mesh(vt)
    vo = link(bpy.data.objects.new('volante', vt), C); vo.data.materials.append(interior); vo.parent = wheel_s
    sol = vo.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.03
    # rodas
    wheels = []
    for wx in (1.32, -1.30):
        for sgn in (-1, 1):
            hub = link(bpy.data.objects.new('roda_eixo', None), C); hub.parent = root; hub.location = (wx, sgn * 0.76, 0.33)
            spin = link(bpy.data.objects.new('roda_giro', None), C); spin.parent = hub; spin.rotation_mode = 'XYZ'
            tire = bpy.data.meshes.new('pneu'); bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.33, radius2=0.33, depth=0.22)
            bm.to_mesh(tire); to = link(bpy.data.objects.new('pneu', tire), C); to.data.materials.append(rubber); to.parent = spin
            to.rotation_euler = (math.radians(90), 0, 0)
            bvm = to.modifiers.new('b', 'BEVEL'); bvm.width = 0.06; bvm.segments = 4; to.data.shade_smooth()
            # sulcos (blocos ao redor da banda)
            for k in range(36):
                a = 2 * math.pi * k / 36
                bl = box('sulco', (0.035, 0.18, 0.012), (0.333 * math.cos(a), 0, 0.333 * math.sin(a)), rubber, C, rot=(0, -a + math.pi / 2, 0)); bl.parent = spin
            rd = cyl('aro', 0.2, 0.23, (0, 0, 0), rim, C, seg=40, rot=(math.radians(90), 0, 0)); rd.parent = spin
            for k in range(5):
                a = 2 * math.pi * k / 5
                sp = box('raio', (0.2, 0.05, 0.04), (0.09 * math.cos(a), sgn * 0.12, 0.09 * math.sin(a)), rim, C, rot=(0, -a, 0)); sp.parent = spin
            hubc = cyl('cubo', 0.045, 0.25, (0, 0, 0), chrome, C, seg=16, rot=(math.radians(90), 0, 0)); hubc.parent = spin
            disc = cyl('disco', 0.17, 0.02, (0, -sgn * 0.02, 0), mat_basic('Disco', (0.35, 0.33, 0.32), 0.35, 1.0), C, seg=32, rot=(math.radians(90), 0, 0)); disc.parent = hub
            wheels.append(spin)
    drv = None
    if driver:
        drv = build_character(name + '_Teo', TEO_DRIVER, C, seated=True); drv['root'].parent = body_root
        drv['root'].location = (-0.18, 0.38, 0.58 - drv['hip_z']); drv['root'].rotation_euler = (0, 0, math.radians(90))
    return dict(root=root, body=body_root, wheels=wheels, tail=tail, paint=paint, coll=C, driver=drv)

# ------------------------------------------------------------------ personagens
TEO = dict(h=1.0, skin=(0.98, 0.92, 0.86), shirt=(0.08, 0.55, 0.58), pants=(0.14, 0.18, 0.35), shoes=(0.95, 0.95, 0.95),
           cap=(0.98, 0.55, 0.08), head_r=0.17, kid=False)
TEO_DRIVER = dict(TEO, h=0.80, head_r=0.15)
KID = dict(h=0.62, skin=(0.98, 0.92, 0.86), shirt=(0.98, 0.78, 0.12), pants=(0.15, 0.32, 0.72), shoes=(0.9, 0.15, 0.15),
           cap=None, hair=(0.25, 0.15, 0.08), head_r=0.16, kid=True)

def build_character(name, P, C, seated=False):
    """Personagem volumétrico: cabeça esférica com rosto desenhado (troca de expressão por material), tronco arredondado,
    braços/pernas em cápsulas com mangas e calça, mãos, tênis. Peças rígidas presas aos ossos de um armature.
    Local: frente = -Y, cima = +Z. Devolve dict(root, arm, face_mat, bones)."""
    s = P['h']; hip_z = 0.86 * s + (0.05 if P['kid'] else 0.0)
    arm_d = bpy.data.armatures.new(name + '_arm'); arm = link(bpy.data.objects.new(name + '_rig', arm_d), C)
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT'); E = arm_d.edit_bones
    def bone(n, h, t, parent=None):
        b = E.new(n); b.head = h; b.tail = t
        if parent: b.parent = E[parent]; b.use_connect = False
        return b
    leg = 0.80 * s if not P['kid'] else 0.46; thigh = leg * 0.5; shin = leg * 0.5
    hip_z = leg + 0.08
    torso = 0.50 * s if not P['kid'] else 0.34
    bone('root', (0, 0, 0), (0, 0.2, 0))
    bone('hips', (0, 0, hip_z), (0, 0, hip_z + 0.1), 'root')
    bone('spine', (0, 0, hip_z + 0.1), (0, 0, hip_z + torso), 'hips')
    bone('head', (0, 0, hip_z + torso), (0, 0, hip_z + torso + 0.2), 'spine')
    sh_w = 0.20 * s if not P['kid'] else 0.15; hip_w = 0.10 * s if not P['kid'] else 0.075
    ua = 0.30 * s if not P['kid'] else 0.19; fa = 0.28 * s if not P['kid'] else 0.18
    for sd, sx in (('L', 1), ('R', -1)):
        sz = hip_z + torso - 0.06
        bone(f'upper_arm.{sd}', (sx * sh_w, 0, sz), (sx * sh_w, 0, sz - ua), 'spine')
        bone(f'forearm.{sd}', (sx * sh_w, 0, sz - ua), (sx * sh_w, 0, sz - ua - fa), f'upper_arm.{sd}')
        bone(f'thigh.{sd}', (sx * hip_w, 0, hip_z), (sx * hip_w, 0, hip_z - thigh), 'hips')
        bone(f'shin.{sd}', (sx * hip_w, 0, hip_z - thigh), (sx * hip_w, 0, hip_z - thigh - shin), f'thigh.{sd}')
    bpy.ops.object.mode_set(mode='OBJECT')
    root = link(bpy.data.objects.new(name, None), C); arm.parent = root
    skin = mat_basic(name + '_Pele', P['skin'], 0.55); shirt = mat_basic(name + '_Camisa', P['shirt'], 0.8)
    pants = mat_basic(name + '_Calca', P['pants'], 0.85); shoes = mat_basic(name + '_Tenis', P['shoes'], 0.5)
    sole = mat_basic('Sola', (0.95, 0.95, 0.95), 0.6)
    face = mat_skin_face(name + '_Rosto', P['skin'], ['neutral', 'alarm', 'focus', 'relief'])
    bpy.context.view_layer.update()
    def attach(o, b, world_loc, rot=(0, 0, 0)):
        o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = b
        bpy.context.view_layer.update()
        o.matrix_world = Matrix.Translation(world_loc) @ Euler(rot).to_matrix().to_4x4()
    # tronco (camisa) e quadril (calça)
    tor = box(name + '_tronco', (2 * sh_w + 0.02, 0.24 * s if not P['kid'] else 0.18, torso * 0.92), (0, 0, 0), shirt, C, bevel=0.07 * s if not P['kid'] else 0.06, seg=4)
    attach(tor, 'spine', Vector((0, 0, hip_z + torso / 2 + 0.03)))
    hp = box(name + '_quadril', (2 * hip_w + 0.12, 0.2 * s if not P['kid'] else 0.16, 0.16), (0, 0, 0), pants, C, bevel=0.05, seg=3)
    attach(hp, 'hips', Vector((0, 0, hip_z + 0.02)))
    hr = P['head_r'] * (1.0 if not P['kid'] else 1.0)
    neck = cyl(name + '_pescoco', 0.045, 0.08, (0, 0, 0), skin, C, seg=16); attach(neck, 'head', Vector((0, 0, hip_z + torso + 0.03)))
    hd = sphere(name + '_cabeca', hr, (0, 0, 0), face, C, seg=48); attach(hd, 'head', Vector((0, 0, hip_z + torso + hr + 0.02)))
    if P.get('cap'):
        capm = mat_basic(name + '_Bone', P['cap'], 0.6)
        cp = sphere(name + '_bone', hr * 1.04, (0, 0, 0), capm, C, scale=(1, 1, 0.55)); attach(cp, 'head', Vector((0, 0.015, hip_z + torso + hr + 0.02 + hr * 0.62)))
        ab = box(name + '_aba', (hr * 1.5, hr * 1.1, 0.02), (0, 0, 0), capm, C, bevel=0.01); attach(ab, 'head', Vector((0, -hr * 1.0, hip_z + torso + hr + 0.02 + hr * 0.42)), (math.radians(-10), 0, 0))
    if P.get('hair'):
        hm = mat_basic(name + '_Cabelo', P['hair'], 0.7)
        hh = sphere(name + '_cabelo', hr * 1.05, (0, 0, 0), hm, C, scale=(1, 1.02, 0.72)); attach(hh, 'head', Vector((0, 0.04, hip_z + torso + hr + 0.02 + hr * 0.5)))
    for sd, sx in (('L', 1), ('R', -1)):
        sz = hip_z + torso - 0.06
        r_arm = 0.045 * s if not P['kid'] else 0.04
        u = capsule(name + '_braco' + sd, r_arm * 1.25, ua, shirt, C); attach(u, f'upper_arm.{sd}', Vector((sx * sh_w, 0, sz)))
        f = capsule(name + '_antebraco' + sd, r_arm, fa, skin, C, r2=r_arm * 0.9); attach(f, f'forearm.{sd}', Vector((sx * sh_w, 0, sz - ua)))
        hnd = sphere(name + '_mao' + sd, r_arm * 1.35, (0, 0, 0), skin, C, scale=(0.85, 1.0, 1.15)); attach(hnd, f'forearm.{sd}', Vector((sx * sh_w, 0, sz - ua - fa - 0.02)))
        r_leg = 0.06 * s if not P['kid'] else 0.05
        t = capsule(name + '_coxa' + sd, r_leg * 1.2, thigh, pants, C, r2=r_leg); attach(t, f'thigh.{sd}', Vector((sx * hip_w, 0, hip_z)))
        sh = capsule(name + '_canela' + sd, r_leg, shin, pants if not P['kid'] else skin, C, r2=r_leg * 0.85)
        attach(sh, f'shin.{sd}', Vector((sx * hip_w, 0, hip_z - thigh)))
        ft = box(name + '_tenis' + sd, (r_leg * 2.2, r_leg * 4.2, r_leg * 1.6), (0, 0, 0), shoes, C, bevel=r_leg * 0.6, seg=3)
        attach(ft, f'shin.{sd}', Vector((sx * hip_w, -r_leg * 1.1, hip_z - thigh - shin + r_leg * 0.25)))
        so = box(name + '_sola' + sd, (r_leg * 2.3, r_leg * 4.3, r_leg * 0.45), (0, 0, 0), sole, C, bevel=r_leg * 0.15)
        attach(so, f'shin.{sd}', Vector((sx * hip_w, -r_leg * 1.1, hip_z - thigh - shin - r_leg * 0.45)))
    for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'
    arm.hide_render = False
    ch = dict(root=root, arm=arm, face=face, P=P, leg=leg, thigh=thigh, shin=shin, hip_z=hip_z)
    if seated: pose(ch, sit=1.0)
    return ch

def set_face(ch, weights, frame=None):
    nt = ch['face'].node_tree
    for k in ('neutral', 'alarm', 'focus', 'relief'):
        n = nt.nodes[f'F_{k}']; n.outputs[0].default_value = weights.get(k, 0.0)
        if frame is not None: n.outputs[0].keyframe_insert('default_value', frame=frame)

def pose(ch, frame=None, sit=0.0, **rot):
    """rot: nome_osso=(rx,ry,rz) em graus. sit=1 aplica pose sentada (motorista)."""
    pb = ch['arm'].pose.bones
    base = {}
    if sit:
        base = {'thigh.L': (-85, 0, 0), 'thigh.R': (-85, 0, 0), 'shin.L': (80, 0, 0), 'shin.R': (80, 0, 0),
                'upper_arm.L': (-55, 0, -8), 'upper_arm.R': (-55, 0, 8), 'forearm.L': (-35, 0, 0), 'forearm.R': (-35, 0, 0), 'spine': (8, 0, 0)}
    base.update(rot)
    for b in pb:
        r = base.get(b.name, (0, 0, 0)); b.rotation_euler = tuple(math.radians(a) for a in r)
        if frame is not None: b.keyframe_insert('rotation_euler', frame=frame)
    if frame is not None and 'root_loc' in rot: pass

# ------------------------------------------------------------------ rótulos 3D
def label(text, loc, size=0.9, color=(1, 1, 1), bg=(0.05, 0.05, 0.06), coll=None, name='rotulo'):
    """Etiqueta: texto Poppins emissivo sobre placa escura arredondada. Devolve o objeto raiz (vazio)."""
    C = coll or new_coll('Rotulos'); root = link(bpy.data.objects.new(name, None), C); root.location = loc
    cu = bpy.data.curves.new(name + '_txt', 'FONT'); cu.body = text; cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = 0.01
    t = link(bpy.data.objects.new(name + '_txt', cu), C); t.parent = root; t.location = (0, 0, 0.02)
    t.data.materials.append(mat_basic('RotuloTxt_' + '%.2f%.2f%.2f' % color, color, 0.5, emit=color, emit_s=1.2))
    w = size * (0.62 * len(text) + 0.6); h = size * 1.35
    p = box(name + '_placa', (w, h, 0.02), (0, 0, 0), mat_basic('RotuloFundo', bg, 0.6, alpha=1.0), C, bevel=size * 0.3, seg=4); p.parent = root
    return root
