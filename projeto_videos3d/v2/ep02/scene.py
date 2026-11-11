"""Cenários do vídeo 02 (E se a Terra parasse de girar?). Usa os utilitários de v2/lib/build.py.
- Espaço: Terra (texturas Solar System Scope CC BY 4.0, baseadas em NASA), nuvens, atmosfera, luzes noturnas,
  migração dos oceanos (relevo NOAA ETOPO5) controlada por um valor no material, Sol, Lua, céu estrelado.
- Orla equatorial: mar a oeste (x<0), praia, calçadão, avenida e prédios a leste (x>0). Leste = +X.
- Coqueiros procedurais articulados (dobram com o vento), ônibus urbano procedural, detritos do vento."""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Euler
import build as B

PROJ = B.PROJ; EA = os.path.join(PROJ, 'assets', 'earth')
rnd = random.Random(11)

# ------------------------------------------------------------------ mini-DSL de nós
class NB:
    def __init__(self, nt): self.nt = nt; self.N = nt.nodes; self.L = nt.links
    def n(self, kind, **kw):
        x = self.N.new(kind)
        for k, v in kw.items(): setattr(x, k, v)
        return x
    def link(self, a, b): self.L.new(a, b); return b
    def math(self, op, a, b=None, clamp=False):
        m = self.n('ShaderNodeMath', operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): m.inputs[i].default_value = v
            else: self.L.new(v, m.inputs[i])
        return m.outputs[0]
    def vmath(self, op, a, b=None):
        m = self.n('ShaderNodeVectorMath', operation=op)
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (tuple, list)): m.inputs[i].default_value = v
            else: self.L.new(v, m.inputs[i])
        return m.outputs['Value'] if op in ('DOT_PRODUCT', 'LENGTH', 'DISTANCE') else m.outputs['Vector']
    def mixc(self, fac, a, b):
        m = self.n('ShaderNodeMix', data_type='RGBA')
        for sock, v in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(v, (int, float)): sock.default_value = v
            elif isinstance(v, tuple): sock.default_value = (*v, 1) if len(v) == 3 else v
            else: self.L.new(v, sock)
        return m.outputs[2]
    def mixf(self, fac, a, b):
        m = self.n('ShaderNodeMix', data_type='FLOAT')
        for sock, v in ((m.inputs[0], fac), (m.inputs[2], a), (m.inputs[3], b)):
            if isinstance(v, (int, float)): sock.default_value = v
            else: self.L.new(v, sock)
        return m.outputs[0]
    def value(self, name, v=0.0):
        x = self.n('ShaderNodeValue'); x.name = name; x.label = name; x.outputs[0].default_value = v; return x.outputs[0]
    def img(self, path, vec, cs='sRGB', interp='Linear'):
        t = self.n('ShaderNodeTexImage', interpolation=interp, extension='REPEAT'); t.image = bpy.data.images.load(path, check_existing=True)
        t.image.colorspace_settings.name = cs; self.L.new(vec, t.inputs[0]); return t
    def sep(self, v):
        s = self.n('ShaderNodeSeparateXYZ'); self.L.new(v, s.inputs[0]); return s.outputs
    def comb(self, x, y, z):
        c = self.n('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            if isinstance(v, (int, float)): c.inputs[i].default_value = v
            else: self.L.new(v, c.inputs[i])
        return c.outputs[0]
    def sstep(self, a, b, x):
        m = self.n('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP', clamp=True)
        m.inputs['From Min'].default_value = a; m.inputs['From Max'].default_value = b; self.L.new(x, m.inputs['Value']); return m.outputs[0]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.node_tree.nodes.clear(); return m, NB(m.node_tree)

# ------------------------------------------------------------------ espaço
A_GEOIDE, C_GEOIDE = 21400.0, 11694.0   # m: achatamento do geoide e constante de conservação de volume (ver roteiro/README)

def setup_space_world(stars=0.8):
    sc = bpy.context.scene; w = bpy.data.worlds.new('Espaco'); sc.world = w; w.use_nodes = True
    nb = NB(w.node_tree); nb.N.clear(); out = nb.n('ShaderNodeOutputWorld'); bg = nb.n('ShaderNodeBackground')
    tc = nb.n('ShaderNodeTexCoord'); env = nb.n('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(EA, '8k_stars_milky_way.jpg'))
    nb.link(tc.outputs['Generated'], env.inputs[0])
    lp = nb.n('ShaderNodeLightPath'); s = nb.math('MULTIPLY', lp.outputs['Is Camera Ray'], stars)
    nb.link(env.outputs[0], bg.inputs[0]); nb.link(s, bg.inputs[1]); nb.link(bg.outputs[0], out.inputs[0])

def earth_material():
    m, nb = new_mat('Terra'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); P = nb.vmath('NORMALIZE', tc.outputs['Object'])
    x, y, z = nb.sep(P)
    lon = nb.math('ARCTAN2', y, x); lat = nb.math('ARCSINE', z)
    u = nb.math('ADD', nb.math('DIVIDE', lon, 2 * math.pi), 0.5); v = nb.math('ADD', nb.math('DIVIDE', lat, math.pi), 0.5)
    uv = nb.comb(u, v, 0.0)
    day = nb.img(os.path.join(EA, '8k_earth_daymap.jpg'), uv).outputs[0]
    night = nb.img(os.path.join(EA, '8k_earth_nightmap.jpg'), uv).outputs[0]
    el = nb.img(os.path.join(EA, 'etopo5_u16.png'), uv, 'Non-Color').outputs[0]
    elev = nb.math('SUBTRACT', nb.math('MULTIPLY', el, 65535.0), 32768.0)
    K = nb.value('K_oceano', 0.0)
    cos2 = nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY', z, z))
    s = nb.math('MULTIPLY', K, nb.math('SUBTRACT', C_GEOIDE, nb.math('MULTIPLY', cos2, A_GEOIDE)))
    depth = nb.math('SUBTRACT', s, elev)                      # >0: coberto por água no estado K
    wet = nb.sstep(-15.0, 15.0, depth)                        # máscara de água (borda suave de ~30 m de relevo)
    was = nb.sstep(-15.0, 15.0, nb.math('MULTIPLY', elev, -1.0))
    newly_dry = nb.math('MULTIPLY', was, nb.math('SUBTRACT', 1.0, wet))
    newly_wet = nb.math('MULTIPLY', wet, nb.math('SUBTRACT', 1.0, was))
    # fundo do mar exposto: cor por profundidade original (cinza escuro no abismo, bege na plataforma)
    tn = nb.n('ShaderNodeTexNoise'); tn.inputs['Scale'].default_value = 40.0; tn.inputs['Detail'].default_value = 8; nb.link(P, tn.inputs['Vector'])
    sea_floor = nb.mixc(nb.sstep(-3500.0, -150.0, elev), (0.30, 0.25, 0.20), (0.50, 0.40, 0.27))
    sea_floor = nb.mixc(nb.sstep(-6500.0, -3500.0, elev), (0.12, 0.11, 0.10), sea_floor)
    sea_floor = nb.mixc(nb.math('MULTIPLY', tn.outputs[0], 0.45), sea_floor, (0.20, 0.16, 0.12))
    deep = nb.mixc(nb.sstep(0.0, 4000.0, depth), (0.035, 0.12, 0.22), (0.010, 0.035, 0.085))
    col = nb.mixc(newly_dry, day, sea_floor); col = nb.mixc(newly_wet, col, deep)
    # faixas de velocidade de rotação (vermelho no Equador -> azul nos polos)
    band = nb.mixc(nb.sstep(0.25, 0.97, nb.math('SQRT', cos2)), (0.05, 0.30, 1.0), (1.0, 0.10, 0.03))
    KB = nb.value('K_faixas', 0.0); col = nb.mixc(nb.math('MULTIPLY', KB, 0.62), col, band)
    nb.link(col, bs.inputs['Base Color'])
    nb.link(nb.mixf(wet, 0.82, 0.32), bs.inputs['Roughness'])
    bs.inputs['Specular IOR Level'].default_value = 0.35
    # luzes da noite: lado oposto ao Sol (posição 'SolPos' em coordenadas de mundo), só em terra seca
    geo = nb.n('ShaderNodeNewGeometry'); sp = nb.n('ShaderNodeCombineXYZ'); sp.name = 'SolPos'
    L = nb.vmath('NORMALIZE', nb.vmath('SUBTRACT', sp.outputs[0], geo.outputs['Position']))
    ndl = nb.vmath('DOT_PRODUCT', geo.outputs['Normal'], L)
    dark = nb.sstep(0.06, -0.18, ndl)
    lights = nb.math('MULTIPLY', nb.math('MULTIPLY', dark, nb.math('SUBTRACT', 1.0, wet)), nb.value('K_luzes', 1.0))
    nb.link(night, bs.inputs['Emission Color']); nb.link(nb.math('MULTIPLY', lights, 2.2), bs.inputs['Emission Strength'])
    nb.link(bs.outputs[0], out.inputs[0])
    return m

def cloud_material():
    m, nb = new_mat('Nuvens'); m.blend_method = 'BLEND'
    out = nb.n('ShaderNodeOutputMaterial'); tc = nb.n('ShaderNodeTexCoord'); P = nb.vmath('NORMALIZE', tc.outputs['Object'])
    x, y, z = nb.sep(P); uv = nb.comb(nb.math('ADD', nb.math('DIVIDE', nb.math('ARCTAN2', y, x), 2 * math.pi), 0.5),
                                      nb.math('ADD', nb.math('DIVIDE', nb.math('ARCSINE', z), math.pi), 0.5), 0.0)
    c = nb.img(os.path.join(EA, '8k_earth_clouds.jpg'), uv, 'Non-Color').outputs[0]
    a = nb.math('MULTIPLY', nb.math('POWER', c, 1.3), nb.value('K_nuvem', 0.9))
    bs = nb.n('ShaderNodeBsdfDiffuse'); bs.inputs[0].default_value = (0.95, 0.95, 0.95, 1)
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader')
    nb.link(a, mx.inputs[0]); nb.link(tr.outputs[0], mx.inputs[1]); nb.link(bs.outputs[0], mx.inputs[2]); nb.link(mx.outputs[0], out.inputs[0])
    return m

def atmosphere_material():
    m, nb = new_mat('Atmosfera'); out = nb.n('ShaderNodeOutputMaterial')
    lw = nb.n('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    rim = nb.math('POWER', lw.outputs['Facing'], 3.0)
    geo = nb.n('ShaderNodeNewGeometry'); sp = nb.n('ShaderNodeCombineXYZ'); sp.name = 'SolPos'
    L = nb.vmath('NORMALIZE', nb.vmath('SUBTRACT', sp.outputs[0], geo.outputs['Position']))
    lit = nb.sstep(-0.35, 0.25, nb.vmath('DOT_PRODUCT', geo.outputs['Normal'], L))
    em = nb.n('ShaderNodeEmission'); em.inputs[0].default_value = (0.30, 0.58, 1.0, 1)
    nb.link(nb.math('MULTIPLY', nb.math('MULTIPLY', rim, lit), 2.6), em.inputs[1])
    tr = nb.n('ShaderNodeBsdfTransparent'); add = nb.n('ShaderNodeAddShader')
    nb.link(tr.outputs[0], add.inputs[0]); nb.link(em.outputs[0], add.inputs[1]); nb.link(add.outputs[0], out.inputs[0])
    return m

def set_sunpos(pos, frame=None):
    for mn in ('Terra', 'Atmosfera'):
        n = bpy.data.materials[mn].node_tree.nodes['SolPos']
        for i in range(3):
            n.inputs[i].default_value = pos[i]
            if frame is not None: n.inputs[i].keyframe_insert('default_value', frame=frame)

def set_value(mat, name, v, frame=None):
    n = bpy.data.materials[mat].node_tree.nodes[name]; n.outputs[0].default_value = v
    if frame is not None: n.outputs[0].keyframe_insert('default_value', frame=frame)

def build_earth(R=10.0):
    C = B.new_coll('Terra')
    root = B.link(bpy.data.objects.new('Terra', None), C); root.rotation_mode = 'XYZ'
    spin = B.link(bpy.data.objects.new('TerraGiro', None), C); spin.parent = root; spin.rotation_mode = 'XYZ'
    e = B.sphere('TerraSup', 1.0, (0, 0, 0), earth_material(), C, seg=160); e.parent = spin
    cl = B.sphere('NuvensSup', 1.007, (0, 0, 0), cloud_material(), C, seg=128); cl.parent = spin
    cl.visible_shadow = True
    at = B.sphere('AtmosferaSup', 1.035, (0, 0, 0), atmosphere_material(), C, seg=96); at.parent = root
    at.visible_shadow = False; at.visible_diffuse = False; at.visible_glossy = False
    root.scale = (R,) * 3
    return dict(root=root, spin=spin, coll=C, R=R)

def latlon(lat, lon, r=1.0):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la)))

def marker(earth, lat, lon, color=(1.0, 0.78, 0.05), name='marcador', size=1.0):
    """Alfinete preso à superfície (filho do giro da Terra). Tamanho em unidades da Terra (R=1)."""
    C = earth['coll']; m = B.mat_basic('Marcador_' + name, color, 0.4, emit=color, emit_s=1.5)
    piv = B.link(bpy.data.objects.new(name, None), C); piv.parent = earth['spin']
    d = latlon(lat, lon); piv.location = d; piv.rotation_mode = 'QUATERNION'; piv.rotation_quaternion = d.to_track_quat('Z', 'Y')
    s = size * 0.018
    head = B.sphere(name + '_cab', s * 1.4, (0, 0, s * 4.2), m, C, seg=24); head.parent = piv
    st = B.cyl(name + '_haste', s * 0.35, s * 4.0, (0, 0, s * 2.0), m, C, seg=12); st.parent = piv
    ring = B.cyl(name + '_base', s * 2.2, s * 0.2, (0, 0, s * 0.1), B.mat_basic('MarcadorBase_' + name, color, 0.5, emit=color, emit_s=0.6), C, seg=32); ring.parent = piv
    return piv

def lat_ring(earth, lat, color, name, width=0.006, emit=2.0):
    C = earth['coll']; m = B.mat_basic('Anel_' + name, color, 0.5, emit=color, emit_s=emit)
    r = math.cos(math.radians(lat)) * 1.004; z = math.sin(math.radians(lat)) * 1.004
    bm = bmesh.new(); bmesh.ops.create_circle(bm, segments=256, radius=r)
    o = B.mesh_obj('anel_' + name, bm, m, C); o.location = (0, 0, z); o.parent = earth['spin']
    sk = o.modifiers.new('sk', 'SKIN') if False else None
    # tubo fino via bevel de curva
    bpy.data.objects.remove(o)
    cu = bpy.data.curves.new('anel_' + name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = width; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = 256; sp.points.add(n - 1)
    for i in range(n):
        a = 2 * math.pi * i / n; sp.points[i].co = (r * math.cos(a), r * math.sin(a), z, 1)
    sp.use_cyclic_u = True
    o = B.link(bpy.data.objects.new('anel_' + name, cu), C); o.data.materials.append(m); o.parent = earth['spin']
    return o

def build_sun(loc, r):
    C = B.new_coll('Sol'); m, nb = new_mat('SolSup'); out = nb.n('ShaderNodeOutputMaterial'); em = nb.n('ShaderNodeEmission')
    tc = nb.n('ShaderNodeTexCoord'); P = nb.vmath('NORMALIZE', tc.outputs['Object']); x, y, z = nb.sep(P)
    uv = nb.comb(nb.math('ADD', nb.math('DIVIDE', nb.math('ARCTAN2', y, x), 2 * math.pi), 0.5), nb.math('ADD', nb.math('DIVIDE', nb.math('ARCSINE', z), math.pi), 0.5), 0.0)
    t = nb.img(os.path.join(EA, '2k_sun.jpg'), uv).outputs[0]
    nb.link(nb.mixc(0.35, t, (1.0, 0.75, 0.35)), em.inputs[0]); em.inputs[1].default_value = 9.0; nb.link(em.outputs[0], out.inputs[0])
    s = B.sphere('Sol', r, loc, m, C, seg=64); s.visible_shadow = False
    # halo
    hm, hb = new_mat('Halo'); ho = hb.n('ShaderNodeOutputMaterial'); lw = hb.n('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.3
    e2 = hb.n('ShaderNodeEmission'); e2.inputs[0].default_value = (1.0, 0.62, 0.25, 1)
    hb.link(hb.math('MULTIPLY', hb.math('POWER', lw.outputs['Facing'], 4.0), 3.0), e2.inputs[1])
    tr = hb.n('ShaderNodeBsdfTransparent'); ad = hb.n('ShaderNodeAddShader'); hb.link(tr.outputs[0], ad.inputs[0]); hb.link(e2.outputs[0], ad.inputs[1]); hb.link(ad.outputs[0], ho.inputs[0])
    h = B.sphere('Halo', r * 1.6, loc, hm, C, seg=48); h.visible_shadow = False; h.visible_diffuse = False
    pl = bpy.data.lights.new('LuzSol', 'POINT'); pl.energy = 4.0e5; pl.shadow_soft_size = r; pl.color = (1.0, 0.95, 0.88)
    po = B.link(bpy.data.objects.new('LuzSol', pl), C); po.location = loc
    return s

def build_moon(loc, r):
    path = os.path.join(EA, '2k_moon.jpg')
    m, nb = new_mat('LuaSup'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled'); bs.inputs['Roughness'].default_value = 0.95
    tc = nb.n('ShaderNodeTexCoord'); P = nb.vmath('NORMALIZE', tc.outputs['Object']); x, y, z = nb.sep(P)
    uv = nb.comb(nb.math('ADD', nb.math('DIVIDE', nb.math('ARCTAN2', y, x), 2 * math.pi), 0.5), nb.math('ADD', nb.math('DIVIDE', nb.math('ARCSINE', z), math.pi), 0.5), 0.0)
    if os.path.exists(path): nb.link(nb.img(path, uv).outputs[0], bs.inputs['Base Color'])
    else: bs.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)
    nb.link(bs.outputs[0], out.inputs[0])
    return B.sphere('Lua', r, loc, m, B.new_coll('Lua'), seg=64)

def sun_lamp(direction, energy=4.5):
    """Luz do Sol direcional. direction: vetor de onde a luz VEM (da Terra para o Sol)."""
    l = bpy.data.lights.new('SolDir', 'SUN'); l.energy = energy; l.angle = math.radians(0.6); l.color = (1.0, 0.96, 0.90)
    o = B.link(bpy.data.objects.new('SolDir', l)); d = Vector(direction).normalized()
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y'); return o

# ------------------------------------------------------------------ orla equatorial
Y0, Y1 = -160.0, 160.0
X_SHORE, X_WALK0, X_WALK1, X_ROAD0, X_ROAD1, X_SIDE1 = 0.0, 24.0, 31.0, 31.4, 38.6, 41.6

def sand_z(x): return 0.018 * x            # praia inclinada: 0 na linha d'água, 0,43 m no calçadão

def mat_calcadao():
    """Calçadão de pedra portuguesa em ondas (preto e branco), procedural."""
    m, nb = new_mat('Calcadao'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); x, y, z = nb.sep(tc.outputs['Object'])
    wave = nb.math('SINE', nb.math('MULTIPLY', y, 0.9))
    xx = nb.math('ADD', x, nb.math('MULTIPLY', wave, 0.8))
    band = nb.math('GREATER_THAN', nb.math('SINE', nb.math('MULTIPLY', xx, 2.4)), 0.0)
    vor = nb.n('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 24.0; nb.link(tc.outputs['Object'], vor.inputs['Vector'])
    vor.feature = 'DISTANCE_TO_EDGE'; grout = nb.sstep(0.0, 0.035, vor.outputs['Distance'])
    noise = nb.n('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 3.0; nb.link(tc.outputs['Object'], noise.inputs['Vector'])
    base = nb.mixc(band, (0.80, 0.78, 0.74), (0.06, 0.06, 0.065))
    base = nb.mixc(nb.math('MULTIPLY', noise.outputs[0], 0.25), base, (0.5, 0.45, 0.4))
    col = nb.mixc(grout, (0.30, 0.28, 0.25), base)
    nb.link(col, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 0.62
    bump = nb.n('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; nb.link(grout, bump.inputs['Height']); nb.link(bump.outputs[0], bs.inputs['Normal'])
    nb.link(bs.outputs[0], out.inputs[0]); return m

def mat_water(name='Mar'):
    """Mar: azul-esverdeado brilhante com ondas (ruído deslocado no tempo pelo valor 'W_fase') e espuma na beira."""
    m, nb = new_mat(name); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); ph = nb.value('W_fase', 0.0)
    P = nb.vmath('ADD', tc.outputs['Object'], nb.comb(nb.math('MULTIPLY', ph, -1.0), 0.0, 0.0))
    n1 = nb.n('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.35; n1.inputs['Detail'].default_value = 6
    nb.link(nb.vmath('MULTIPLY', P, (1.0, 2.2, 1.0)), n1.inputs['Vector'])
    wv = nb.n('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'; wv.inputs['Scale'].default_value = 0.06
    wv.inputs['Distortion'].default_value = 6.0; wv.inputs['Detail'].default_value = 3; nb.link(P, wv.inputs['Vector'])
    h = nb.math('ADD', nb.math('MULTIPLY', n1.outputs[0], 1.0), nb.math('MULTIPLY', wv.outputs['Fac'], 0.12))
    bump = nb.n('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.5; bump.inputs['Distance'].default_value = 0.3
    nb.link(h, bump.inputs['Height']); nb.link(bump.outputs[0], bs.inputs['Normal'])
    # espuma: perto da borda (atributo 'espuma' no objeto: valor por objeto) + cristas
    foam_v = nb.value('W_espuma', 0.0)
    crest = nb.sstep(0.70, 0.86, h)
    lw = nb.n('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.2
    deep = nb.mixc(lw.outputs['Facing'], (0.015, 0.11, 0.13), (0.05, 0.25, 0.30))
    foam = nb.math('MINIMUM', 1.0, nb.math('ADD', nb.math('MULTIPLY', crest, 0.25), foam_v))
    nb.link(nb.mixc(foam, deep, (0.85, 0.88, 0.88)), bs.inputs['Base Color'])
    nb.link(nb.mixf(foam, 0.04, 0.6), bs.inputs['Roughness'])
    nb.link(bs.outputs[0], out.inputs[0]); return m

def mat_foam():
    m, nb = new_mat('Espuma'); out = nb.n('ShaderNodeOutputMaterial'); bs = nb.n('ShaderNodeBsdfPrincipled')
    tc = nb.n('ShaderNodeTexCoord'); n1 = nb.n('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 2.5; n1.inputs['Detail'].default_value = 8
    nb.link(tc.outputs['Object'], n1.inputs['Vector'])
    nb.link(nb.mixc(nb.sstep(0.35, 0.65, n1.outputs[0]), (0.55, 0.70, 0.72), (0.95, 0.97, 0.97)), bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.45; bs.inputs['Subsurface Weight'].default_value = 0.2
    bump = nb.n('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.8; nb.link(n1.outputs[0], bump.inputs['Height']); nb.link(bump.outputs[0], bs.inputs['Normal'])
    n2 = nb.n('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 1.2; n2.inputs['Detail'].default_value = 6; nb.link(tc.outputs['Object'], n2.inputs['Vector'])
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader'); nb.link(nb.sstep(0.42, 0.55, n2.outputs[0]), mx.inputs[0])
    nb.link(tr.outputs[0], mx.inputs[1]); nb.link(bs.outputs[0], mx.inputs[2]); nb.link(mx.outputs[0], out.inputs[0]); return m

def build_orla():
    C = B.new_coll('Orla'); L = Y1 - Y0; yc = (Y0 + Y1) / 2
    sand = B.mat_pbr('Areia', 'coast_sand_01', 3.0, tint=(1.05, 0.98, 0.86), var=0.15)
    asphalt = B.mat_pbr('Asfalto', 'asphalt_02', 4.0, tint=(0.80, 0.80, 0.82), var=0.22)
    walk = B.mat_pbr('Calcada', 'concrete_pavement', 1.6, tint=(0.95, 0.93, 0.9))
    curbm = B.mat_basic('MeioFio', (0.66, 0.66, 0.64), 0.75)
    # praia: plano inclinado de x=-40 (sob a água) até o calçadão
    bm = bmesh.new(); xs = [-60.0, X_WALK0]; vs = [bm.verts.new((x, y, sand_z(x))) for x in xs for y in (Y0, Y1)]
    bm.faces.new([vs[0], vs[2], vs[3], vs[1]]); o = B.mesh_obj('praia', bm, sand, C)
    sd = o.modifiers.new('sub', 'SUBSURF'); sd.subdivision_type = 'SIMPLE'; sd.levels = 4; sd.render_levels = 4
    # calçadão com mureta baixa do lado da praia
    box = B.box
    box('calcadao', (X_WALK1 - X_WALK0, L, 0.5), ((X_WALK0 + X_WALK1) / 2, yc, sand_z(X_WALK0) - 0.25 + 0.06), mat_calcadao(), C)
    box('mureta', (0.35, L, 0.55), (X_WALK0 + 0.17, yc, sand_z(X_WALK0) + 0.05), B.mat_pbr('Mureta', 'grey_plaster_02', 2.0, tint=(0.95, 0.93, 0.88)), C, bevel=0.04)
    zt = sand_z(X_WALK0) + 0.06   # topo do calçadão
    box('meiofio_a', (0.18, L, zt + 0.02), (X_WALK1 + 0.09, yc, (zt + 0.02) / 2), curbm, C, bevel=0.02)
    box('avenida', (X_ROAD1 - X_ROAD0 + 0.2, L, 0.1), ((X_ROAD0 + X_ROAD1) / 2, yc, zt - 0.17), asphalt, C)
    zr = zt - 0.12
    pw = B.mat_basic('TintaBranca', (0.85, 0.85, 0.82), 0.6)
    y = Y0
    while y < Y1:
        box('faixa_c', (0.12, 3.0, 0.004), ((X_ROAD0 + X_ROAD1) / 2, y + 1.5, zr + 0.002), pw, C); y += 7.0
    for xb in (X_ROAD0 + 0.3, X_ROAD1 - 0.3): box('faixa_b', (0.12, L, 0.004), (xb, yc, zr + 0.002), pw, C)
    box('meiofio_b', (0.18, L, zt + 0.02), (X_ROAD1 + 0.09, yc, (zt + 0.02) / 2), curbm, C, bevel=0.02)
    box('calcada_l', (X_SIDE1 - X_ROAD1, L, zt), ((X_ROAD1 + X_SIDE1) / 2 + 0.09, yc, zt / 2), walk, C)
    box('terreno', (260, L, 0.4), (X_SIDE1 + 130, yc, zt - 0.2), B.mat_pbr('Grama', 'leafy_grass', 2.5, tint=(0.55, 0.95, 0.35), var=0.3), C)
    build_buildings(C, zt)
    # morros ao fundo (leste) e ilhas no horizonte (oeste)
    hills = B.mat_pbr('Morros', 'leafy_grass', 30.0, tint=(0.30, 0.48, 0.22), var=0.45)
    for i in range(8):
        B.sphere('morro', 1.0, (rnd.uniform(300, 420), Y0 - 60 + i * 60 + rnd.uniform(-15, 15), -20), hills, C, scale=(rnd.uniform(60, 90), rnd.uniform(45, 70), rnd.uniform(50, 85)), seg=32)
    isl = B.mat_basic('Ilha', (0.16, 0.26, 0.16), 0.9)
    for (iy, sx, sz) in ((-60, 40, 14), (90, 60, 22)):
        B.sphere('ilha', 1.0, (-520, iy, -4), isl, C, scale=(sx * 0.6, sx, sz), seg=32)
    # quiosque na areia, perto do calçadão
    kiosk(C, (14.5, 7.5, sand_z(14.5)))
    return C, zt

def kiosk(C, loc):
    x, y, z = loc; wood = B.mat_pbr('Madeira', 'grey_plaster_02', 1.0, tint=(0.75, 0.55, 0.35)) if False else B.mat_basic('Madeira', (0.50, 0.33, 0.18), 0.7)
    straw = B.mat_basic('Palha', (0.78, 0.62, 0.32), 0.9)
    B.box('quiosque_balcao', (3.0, 3.0, 1.1), (x, y, z + 0.55), wood, C, bevel=0.03)
    for dx in (-1.4, 1.4):
        for dy in (-1.4, 1.4): B.cyl('quiosque_poste', 0.07, 2.6, (x + dx, y + dy, z + 1.3), wood, C, seg=10)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.2, radius2=0.05, depth=1.4)
    o = B.mesh_obj('quiosque_teto', bm, straw, C); o.location = (x, y, z + 3.25); o.rotation_euler = (0, 0, math.radians(45))
    B.box('quiosque_placa', (0.05, 1.8, 0.45), (x - 1.55, y, z + 1.3), B.mat_basic('PlacaQuiosque', (0.95, 0.85, 0.2), 0.5), C)

BUILD_COLORS = [(0.96, 0.92, 0.82), (0.82, 0.90, 0.96), (0.97, 0.84, 0.76), (0.88, 0.95, 0.86), (0.99, 0.97, 0.93), (0.95, 0.80, 0.62)]
def build_buildings(C, zt):
    glass = B.mat_basic('VidroJanela', (0.10, 0.14, 0.18), 0.05); frame = B.mat_basic('Moldura', (0.95, 0.95, 0.93), 0.4)
    balc = B.mat_basic('Varanda', (0.92, 0.92, 0.9), 0.5); awn = [B.mat_basic(f'Toldo{i}', c, 0.7) for i, c in enumerate([(0.85, 0.2, 0.15), (0.1, 0.45, 0.7), (0.95, 0.7, 0.1)])]
    y = Y0 + 4; k = 0
    while y < Y1 - 8:
        w = rnd.uniform(11, 16); d = rnd.uniform(10, 14); floors = rnd.choice([2, 3, 3, 4, 5]); hgt = floors * 3.1
        x0 = X_SIDE1 + 1.5; col = BUILD_COLORS[k % len(BUILD_COLORS)]
        wall = B.mat_pbr(f'ParedeOrla{k % 6}', 'painted_plaster_wall', 3.0, tint=col, var=0.12)
        B.box('predio', (d, w, hgt), (x0 + d / 2, y + w / 2, zt + hgt / 2), wall, C)
        B.box('platibanda', (d + 0.3, w + 0.3, 0.5), (x0 + d / 2, y + w / 2, zt + hgt + 0.25), B.mat_basic('Platibanda', (0.9, 0.9, 0.88), 0.6), C)
        fx = x0 - 0.02
        for fl in range(floors):
            zz = zt + 1.7 + fl * 3.1
            nw = int(w // 2.6)
            for wi in range(nw):
                wy = y + 1.3 + wi * (w - 2.6) / max(nw - 1, 1)
                if fl == 0 and abs(wy - (y + w / 2)) < 1.4: continue
                B.box('janela', (0.06, 1.3, 1.4), (fx, wy, zz), frame, C); B.box('vidro', (0.08, 1.1, 1.2), (fx, wy, zz), glass, C)
            if fl > 0 and k % 2 == 0: B.box('varanda', (0.9, w * 0.8, 0.12), (fx - 0.45, y + w / 2, zz - 0.85), balc, C)
        B.box('porta', (0.08, 1.6, 2.3), (fx, y + w / 2, zt + 1.15), B.mat_basic('Porta', (0.38, 0.22, 0.12), 0.5), C)
        if k % 3 != 1: B.box('toldo', (1.4, w * 0.7, 0.08), (fx - 0.7, y + w / 2, zt + 2.9), awn[k % 3], C, rot=(0, math.radians(-12), 0))
        y += w + rnd.uniform(0.0, 2.5); k += 1

# ------------------------------------------------------------------ coqueiro articulado
def build_palm(C, loc, h=8.0, seed=0, lean=0.0, n_frond=11):
    r = random.Random(seed); trunk = B.mat_basic('Tronco', (0.38, 0.30, 0.22), 0.85)
    leaf = bpy.data.materials.get('Folha') or B.mat_basic('Folha', (0.16, 0.40, 0.08), 0.6)
    leaf.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = 0.15
    root = B.link(bpy.data.objects.new('coqueiro', None), C); root.location = loc; root.rotation_euler = (0, 0, r.uniform(0, 6.28))
    nseg = 7; segs = []; parent = root; L = h / nseg
    for i in range(nseg):
        e = B.link(bpy.data.objects.new('coq_seg', None), C); e.parent = parent; e.location = (0, 0, 0 if i == 0 else L); e.rotation_mode = 'XYZ'
        rr = 0.21 - 0.07 * i / nseg
        s = B.cyl('coq_tronco', rr, L * 1.06, (0, 0, L / 2), trunk, C, seg=14); s.parent = e
        rg = B.cyl('coq_anel', rr * 1.08, 0.06, (0, 0, L * 0.98), trunk, C, seg=14); rg.parent = e
        segs.append(e); parent = e
    top = B.link(bpy.data.objects.new('coq_copa', None), C); top.parent = parent; top.location = (0, 0, L)
    nut = B.mat_basic('Coco', (0.30, 0.38, 0.12), 0.5)
    for k in range(4):
        a = k * 1.6; c = B.sphere('coco', 0.13, (0.16 * math.cos(a), 0.16 * math.sin(a), -0.15), nut, C, seg=12); c.parent = top
    fronds = []
    for k in range(n_frond):
        p = B.link(bpy.data.objects.new('coq_folha_piv', None), C); p.parent = top; p.rotation_mode = 'XYZ'
        yaw = 2 * math.pi * k / n_frond + r.uniform(-0.2, 0.2); pitch = r.uniform(-0.15, 0.35)
        p.rotation_euler = (0, -pitch, yaw)
        f = frond_mesh(C, r.uniform(3.0, 4.0), leaf, r); f.parent = p
        fronds.append((p, yaw, pitch))
    return dict(root=root, segs=segs, fronds=fronds, h=h, lean=lean, seed=seed)

def frond_mesh(C, Lf, mat, r):
    bm = bmesh.new(); n = 26
    def rach(s): return Vector((Lf * s, 0, 0.55 * Lf * s * (1 - s) * 1.2 - 0.55 * Lf * s * s))
    n = 34
    for i in range(n):
        s0, s1 = i / n, (i + 1) / n; p0, p1 = rach(s0), rach(s1)
        w = 0.025 * (1 - s0) + 0.01
        v = [bm.verts.new(p0 + Vector((0, -w, 0))), bm.verts.new(p1 + Vector((0, -w, 0))), bm.verts.new(p1 + Vector((0, w, 0))), bm.verts.new(p0 + Vector((0, w, 0)))]
        bm.faces.new(v)
        if i < 2: continue
        ll = 0.62 * math.sin(math.pi * min(1, s0 * 1.15)) + 0.12
        for sd in (-1, 1):
            d = Vector((0.45, sd * 1.0, -0.55)).normalized()
            tip = p0 + d * ll; side = Vector((0.11, 0, 0))
            v = [bm.verts.new(p0), bm.verts.new(p0 + side), bm.verts.new(tip + side * 0.2), bm.verts.new(tip)]
            bm.faces.new(v)
    o = B.mesh_obj('coq_folha', bm, mat, C)
    for p in o.data.polygons: p.use_smooth = True
    return o

def pose_palm(p, wind, T, f=None):
    """wind 0..1: vergada para +X mundial. Oscilação leve sempre; com vento as folhas se alinham ao leste e tremem."""
    r = p['root']; base_yaw = r.rotation_euler[2]
    # direção leste no referencial do coqueiro
    east = -base_yaw
    sway = 0.03 * math.sin(T * 1.1 + p['seed']) * (1 - wind) + wind * 0.05 * math.sin(T * 9 + p['seed'] * 3)
    bend = 0.55 * wind + sway
    for i, e in enumerate(p['segs']):
        a = bend / len(p['segs']) * (0.4 + 1.2 * i / len(p['segs']))
        e.rotation_euler = (-a * math.sin(east), a * math.cos(east), 0)
        if f is not None: e.keyframe_insert('rotation_euler', frame=f)
    for k, (piv, yaw, pitch) in enumerate(p['fronds']):
        d = (east - yaw + math.pi) % (2 * math.pi) - math.pi
        y2 = yaw + d * 0.75 * wind
        fl = math.sin(T * (11 + k) + k) * 0.18 * wind + 0.04 * math.sin(T * 1.7 + k) * (1 - wind)
        pt = pitch * (1 - wind) + (-0.15) * wind + fl
        piv.rotation_euler = (0.25 * wind * math.sin(T * 13 + k), -pt, y2)
        if f is not None: piv.keyframe_insert('rotation_euler', frame=f)

# ------------------------------------------------------------------ ônibus
def build_bus(name='Onibus'):
    """Ônibus urbano (12 m): carroceria com chanfros, faixa de janelas em vidro fino, portas, rodas duplas atrás,
    faróis, lanternas (emissão controlável), interior com bancos e balaústre. Frente em +X local, origem no chão."""
    C = B.new_coll(name); root = B.link(bpy.data.objects.new(name, None), C)
    body = B.link(bpy.data.objects.new(name + '_susp', None), C); body.parent = root
    paint = B.mat_basic(name + '_Pintura', (0.95, 0.95, 0.93), 0.35, 0.2, coat=0.6)
    stripe = B.mat_basic(name + '_Faixa', (0.05, 0.45, 0.62), 0.4, coat=0.5)
    stripe2 = B.mat_basic(name + '_Faixa2', (0.98, 0.70, 0.08), 0.4, coat=0.5)
    glass = B.mat_thin_glass('VidroOnibus', (0.62, 0.70, 0.74))
    for nd in glass.node_tree.nodes:
        if nd.bl_idname == 'ShaderNodeMath': nd.inputs[1].default_value = 0.03
    trim = B.mat_basic('PlasticoPreto', (0.025, 0.025, 0.028), 0.55)
    rubber = B.mat_basic('Borracha', (0.035, 0.035, 0.035), 0.8); rim = B.mat_basic('AroOnibus', (0.75, 0.76, 0.78), 0.3, 1.0)
    head = B.mat_basic('Farol', (0.95, 0.95, 0.9), 0.05, 0.0, emit=(1, 0.95, 0.85), emit_s=1.5)
    tail = B.mat_basic(name + '_Lanterna', (0.5, 0.02, 0.02), 0.2, emit=(1, 0.05, 0.03), emit_s=0.6)
    inter = B.mat_basic('InteriorOnibus', (0.55, 0.56, 0.58), 0.6); seat = B.mat_basic('BancoOnibus', (0.10, 0.25, 0.45), 0.7)
    Lb, Wb, Hb, z0 = 12.0, 2.5, 3.0, 0.35
    B.box(name + '_saia', (Lb, Wb, 0.95), (0, 0, z0 + 0.475), paint, C, bevel=0.12, seg=3).parent = body
    B.box(name + '_teto', (Lb, Wb, 0.42), (0, 0, z0 + Hb - 0.21), paint, C, bevel=0.15, seg=3).parent = body
    B.box(name + '_janelas', (Lb - 0.3, Wb - 0.04, Hb - 0.95 - 0.42 + 0.04), (0, 0, z0 + 0.95 + (Hb - 1.37) / 2), glass, C).parent = body
    for sgn in (-1, 1):
        B.box('faixa', (Lb - 0.6, 0.02, 0.22), (0, sgn * (Wb / 2 + 0.005), z0 + 0.62), stripe, C).parent = body
        B.box('faixa2', (Lb - 0.6, 0.02, 0.07), (0, sgn * (Wb / 2 + 0.005), z0 + 0.82), stripe2, C).parent = body
        for k in range(7):
            B.box('coluna', (0.10, 0.06, Hb - 1.37), (-Lb / 2 + 0.6 + k * (Lb - 1.2) / 6, sgn * (Wb / 2 - 0.01), z0 + 0.95 + (Hb - 1.37) / 2), trim, C).parent = body
        B.box('retrovisor', (0.12, 0.35, 0.3), (Lb / 2 + 0.05, sgn * (Wb / 2 + 0.2), z0 + 2.0), trim, C, bevel=0.03).parent = body
        B.box('farol', (0.05, 0.4, 0.18), (Lb / 2 + 0.01, sgn * 0.85, z0 + 0.5), head, C, bevel=0.02).parent = body
        B.box('lanterna', (0.05, 0.3, 0.35), (-Lb / 2 - 0.01, sgn * 0.95, z0 + 0.7), tail, C, bevel=0.02).parent = body
    B.box('letreiro', (0.04, 1.8, 0.3), (Lb / 2 + 0.01, 0, z0 + Hb - 0.25), B.mat_basic('Letreiro', (1.0, 0.6, 0.05), 0.3, emit=(1.0, 0.6, 0.05), emit_s=2.0), C).parent = body
    B.box('parachoque', (0.2, Wb + 0.02, 0.28), (Lb / 2 + 0.05, 0, z0 + 0.15), trim, C, bevel=0.05).parent = body
    # interior: piso, bancos em pares, balaústres
    B.box('piso', (Lb - 0.4, Wb - 0.3, 0.06), (0, 0, z0 + 0.4), inter, C).parent = body
    for k in range(9):
        x = -Lb / 2 + 1.0 + k * 1.15
        if abs(x - 0.4) < 1.2: continue
        for sy in (-0.75, 0.75):
            B.box('banco', (0.45, 0.85, 0.12), (x, sy, z0 + 0.85), seat, C, bevel=0.04).parent = body
            B.box('encosto', (0.10, 0.85, 0.6), (x - 0.22, sy, z0 + 1.2), seat, C, bevel=0.04).parent = body
    for x in (-3.0, 0.4, 2.6):
        B.cyl('balaustre', 0.025, Hb - 0.5, (x, 0.3, z0 + 0.4 + (Hb - 0.5) / 2), rim, C, seg=10).parent = body
    B.cyl('corrimao', 0.02, Lb - 1.5, (0, 0.55, z0 + Hb - 0.55), rim, C, seg=10, rot=(0, math.radians(90), 0)).parent = body
    for x in (-3.5, 0.0, 3.5):
        lt = bpy.data.lights.new('LuzOnibus', 'POINT'); lt.energy = 90; lt.color = (1.0, 0.92, 0.80); lt.shadow_soft_size = 0.4
        lo = B.link(bpy.data.objects.new('LuzOnibus', lt), C); lo.parent = body; lo.location = (x, 0, z0 + Hb - 0.6)
    wheels = []
    for wx in (Lb / 2 - 2.4, -Lb / 2 + 3.0):
        for sgn in (-1, 1):
            hub = B.link(bpy.data.objects.new('roda_eixo', None), C); hub.parent = root; hub.location = (wx, sgn * (Wb / 2 - 0.25), 0.5)
            spin = B.link(bpy.data.objects.new('roda_giro', None), C); spin.parent = hub; spin.rotation_mode = 'XYZ'
            t = B.cyl('pneu', 0.5, 0.32, (0, 0, 0), rubber, C, seg=40, rot=(math.radians(90), 0, 0)); t.parent = spin
            bv = t.modifiers.new('b', 'BEVEL'); bv.width = 0.07; bv.segments = 3
            rd = B.cyl('aro', 0.3, 0.34, (0, 0, 0), rim, C, seg=32, rot=(math.radians(90), 0, 0)); rd.parent = spin
            for k in range(8):
                a = 2 * math.pi * k / 8
                B.box('furo', (0.06, 0.36, 0.06), (0.2 * math.cos(a), 0, 0.2 * math.sin(a)), trim, C).parent = spin
            wheels.append(spin)
    for wx in (Lb / 2 - 2.4, -Lb / 2 + 3.0):          # caixas de roda escuras
        for sgn in (-1, 1): B.box('caixa_roda', (1.25, 0.04, 0.6), (wx, sgn * (Wb / 2 + 0.01), z0 + 0.3), trim, C).parent = body
    return dict(root=root, body=body, wheels=wheels, tail=tail, coll=C, L=Lb, z_floor=z0 + 0.43)

# ------------------------------------------------------------------ detritos do vento
def debris_block(C, name, n, box_size, kind, seed):
    """Um objeto com n partículas fixas (areia, folhas miúdas ou riscos de vento); o bloco inteiro é deslocado no tempo."""
    r = random.Random(seed); bm = bmesh.new(); X, Y, Z = box_size
    for i in range(n):
        c = Vector((r.uniform(0, X), r.uniform(-Y / 2, Y / 2), r.uniform(*Z) if isinstance(Z, tuple) else r.uniform(0, Z)))
        if kind == 'risco':
            ln = r.uniform(2.5, 6.0); w = r.uniform(0.02, 0.05)
            v = [bm.verts.new(c + Vector(p)) for p in ((0, 0, -w), (ln, 0, -w), (ln, 0, w), (0, 0, w))]; bm.faces.new(v)
        elif kind == 'areia':
            s = r.uniform(0.025, 0.06); ln = s * r.uniform(5, 12)
            v = [bm.verts.new(c + Vector(p)) for p in ((0, -s, 0), (ln, 0, 0), (0, s, 0), (0, 0, s))]
            for f in ((0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)): bm.faces.new([v[j] for j in f])
        else:  # folha
            s = r.uniform(0.07, 0.14); a = r.uniform(0, 6.28); b = r.uniform(0, 6.28)
            d1 = Vector((math.cos(a), math.sin(a), math.sin(b))) * s; d2 = Vector((-math.sin(a), math.cos(a), math.cos(b))) * s * 0.45
            v = [bm.verts.new(c + p) for p in (-d1, -d2, d1, d2)]; bm.faces.new(v)
    mats = dict(risco=B.mat_basic('Risco', (1, 1, 1), 0.5, emit=(0.9, 0.95, 1.0), emit_s=0.6, alpha=0.18),
                areia=B.mat_basic('AreiaVoando', (0.78, 0.68, 0.50), 0.9), folha=bpy.data.materials.get('Folha') or B.mat_basic('Folha', (0.16, 0.40, 0.08), 0.6))
    o = B.mesh_obj(name, bm, mats[kind], C)
    if kind == 'risco':
        m = mats[kind]; m.blend_method = 'BLEND'; o.visible_shadow = False
    return o
