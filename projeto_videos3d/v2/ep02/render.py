"""Vídeo 02: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep02/render.py -- --shot C [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep02/frames/<plano>/NNNN.png (final) ou v2/ep02/preview/<plano>/ (prévia). Retomável."""
import bpy, sys, os, math, json, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import build as B
import scene as SC
import plan as P
from story import sstep
from mathutils import Vector, Matrix

ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--mode', default='preview')
ap.add_argument('--spp', type=int); ap.add_argument('--step', type=int); ap.add_argument('--frames'); ap.add_argument('--still', type=int)
ap.add_argument('--save-blend', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
shot = P.BY_NAME[a.shot]; FINAL = a.mode == 'final'
W, H = (720, 1280) if FINAL else (270, 480)
if os.environ.get('PREVIEW_RES'): W, H = map(int, os.environ['PREVIEW_RES'].split('x'))
spp = a.spp or (12 if FINAL else 5); step = a.step or (1 if FINAL else 3)
SPACE = shot.kind in ('globe', 'orbit')

bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
if SPACE: SC.setup_space_world()
else: B.setup_world()
B.setup_render(W, H, spp, preview=not FINAL)
sc = bpy.context.scene
if SPACE:   # sem névoa atmosférica no espaço
    for n in sc.node_tree.nodes:
        if n.bl_idname == 'CompositorNodeMath': n.inputs[1].default_value = 0.0
    sc.view_settings.exposure = 0.0
cam = B.link(bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.05; cam.data.clip_end = 5000
RC = B.new_coll('Rotulos3D')

def bill(key, text, loc, size, color):
    r = B.label(text, loc, size, color, coll=RC, name='rot_' + key)
    for ch in r.children: ch.visible_shadow = False
    c = r.constraints.new('COPY_ROTATION'); c.target = cam      # sempre de frente e na vertical da tela
    r.scale = (0.0001,) * 3; return r

def pop_scale(T, t_on, t_off=99):
    k = sstep(t_on, t_on + 0.25, T) * (1 - sstep(t_off, t_off + 0.2, T))
    return max(k, 0.0001) * (1 + 0.15 * math.sin(math.pi * min(sstep(t_on, t_on + 0.25, T), 1)))

def key(o, *props, f):
    for p in props: o.keyframe_insert(p, frame=f)

def arrow(name, loc, length, color):
    m = B.mat_basic('Seta_' + name, color, 0.4, emit=color, emit_s=1.4)
    root = B.link(bpy.data.objects.new('seta_' + name, None), RC); root.location = loc
    s = B.box('seta_haste', (length * 0.72, length * 0.09, length * 0.09), (length * 0.36, 0, 0), m, RC, bevel=length * 0.02); s.parent = root
    hd = B.cyl('seta_ponta', length * 0.17, length * 0.3, (length * 0.85, 0, 0), m, RC, seg=24, rot=(0, math.radians(90), 0))
    me = hd.data
    for v in me.vertices:
        if v.co.z > 0: v.co.x *= 0.02; v.co.y *= 0.02
    hd.parent = root; root.scale = (0.0001,) * 3; return root

def look_rot(pos, look, up=(0, 0, 1)):
    z = (Vector(pos) - Vector(look)).normalized(); u = Vector(up)
    x = u.cross(z)
    if x.length < 1e-6: x = Vector((1, 0, 0))
    x.normalize(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_euler()

items = {}; events = dict(shot=shot.name, fps=P.FPS, frames=[])
# ================================================================== ESPAÇO
if shot.kind == 'globe':
    earth = SC.build_earth(P.R)
    sd = Vector(shot.sun).normalized(); SC.sun_lamp(sd, 4.5); SC.set_sunpos(tuple(sd * 1e5))
    if getattr(shot, 'marker', False): items['pin'] = SC.marker(earth, P.LAT_B, P.LON_B, size=1.6)
    if hasattr(shot, 'equator'): items['eq'] = SC.lat_ring(earth, 0.0, (1.0, 0.22, 0.10), 'equador', width=0.0001)
    if hasattr(shot, 'polar'): items['pol'] = SC.lat_ring(earth, 72.0, (0.35, 0.70, 1.0), 'polo', width=0.0001)
    if hasattr(shot, 'arrow'):     # seta curva sobre o Equador indicando o sentido do giro (para leste)
        cu = bpy.data.curves.new('seta_giro', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0001; cu.bevel_resolution = 3
        sp = cu.splines.new('POLY'); n = 40; sp.points.add(n - 1); a0, a1 = math.radians(-95), math.radians(-55)
        for i in range(n):
            t = a0 + (a1 - a0) * i / (n - 1); sp.points[i].co = (1.06 * math.cos(t), 1.06 * math.sin(t), 0.0, 1)
        ao = B.link(bpy.data.objects.new('seta_giro', cu), earth['coll']); ao.parent = earth['root']
        m = B.mat_basic('SetaGiro', (1.0, 0.25, 0.12), 0.4, emit=(1.0, 0.25, 0.12), emit_s=2.5); ao.data.materials.append(m)
        hd = B.cyl('seta_giro_ponta', 0.035, 0.08, (0, 0, 0), m, earth['coll'], seg=20)
        for v in hd.data.vertices:
            if v.co.z > 0: v.co.x *= 0.02; v.co.y *= 0.02
        hd.parent = earth['root']; hd.location = (1.06 * math.cos(a1), 1.06 * math.sin(a1), 0); hd.rotation_euler = (math.radians(-90), 0, a1 + 0)
        hd.rotation_mode = 'QUATERNION'; hd.rotation_quaternion = Vector((-math.sin(a1), math.cos(a1), 0)).to_track_quat('Z', 'X')
        items['arc'] = (cu, hd)
    if hasattr(shot, 'moon'): SC.build_moon(shot.moon, 2.7)
elif shot.kind == 'orbit':
    SC.build_sun((0, 0, 0), P.SUN_R)
    earth = SC.build_earth(P.I_ER); SC.set_sunpos((0, 0, 0))
    items['pin'] = SC.marker(earth, P.LAT_B, P.LON_B, size=3.2)
    cu = bpy.data.curves.new('orbita', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.035
    sp = cu.splines.new('POLY'); n = 256; sp.points.add(n - 1)
    for i in range(n):
        t = 2 * math.pi * i / n; sp.points[i].co = (P.ORB_R * math.cos(t), P.ORB_R * math.sin(t), 0, 1)
    sp.use_cyclic_u = True
    ob = B.link(bpy.data.objects.new('orbita', cu)); ob.data.materials.append(B.mat_basic('Orbita', (0.6, 0.7, 0.9), 0.5, emit=(0.6, 0.7, 0.9), emit_s=0.5))
    ob.visible_shadow = False; items['orb'] = cu
# ================================================================== ORLA / ÔNIBUS
else:
    OC, ZT = SC.build_orla()
    sea = B.box('mar', (1400, 1400, 6.0), (-700, 0, -3.0), SC.mat_water(), OC)
    sea.data.transform(Matrix.Translation((0, 0, 0)))
    items['sea'] = sea
    foam_m = SC.mat_foam()
    lip = B.cyl('crista', 0.55, 1400, (0, 0, 0), foam_m, OC, seg=24, rot=(math.radians(90), 0, 0)); lip.scale = (1, 1, 1); items['lip'] = lip
    shore = B.box('espuma_beira', (1.2, 320, 0.02), (-0.3, 0, 0.01), foam_m, OC); items['shore'] = shore
    PC = B.new_coll('Coqueiros'); palms = []
    k = 0
    for y in range(-91, 92, 14):
        palms.append(SC.build_palm(PC, (26.0 + (k % 2) * 0.6, y + 0.0, ZT), h=7.5 + (k * 37 % 10) / 5, seed=k)); k += 1
    for (x, y) in ((P.PALM_HUG[0], P.PALM_HUG[1]), (11.0, -30.0), (8.0, 22.0), (14.0, 48.0), (10.0, -62.0)):
        palms.append(SC.build_palm(PC, (x, y, SC.sand_z(x)), h=6.5 + (k % 3), seed=k)); k += 1
    LC = B.new_coll('Postes')
    y = 0.55 - 100
    while y < 160:
        B.instance('street_lamp_01', (30.35, y, ZT), math.radians(180), 1.0, LC); y += 25
    for yy in (-40.0, 12.0, 60.0): B.instance('metal_trash_can', (30.0, yy, ZT), 0.0, 1.0, LC)
    for yy in (-20.0, 30.0, 75.0): B.instance(['shrub_01', 'shrub_02', 'shrub_04'][int(yy) % 3], (40.6, yy, ZT), 0.0, 1.2, LC)
    # vento: riscos, areia e folhas em blocos que correm para o leste
    WC = B.new_coll('Vento'); blocks = []
    for kind, n, Z, speed, seed in (('risco', 220, (1.0, 12.0), 42.0, 1), ('areia', 2500, (0.0, 2.0), 26.0, 2), ('folha', 300, (0.3, 7.0), 20.0, 3)):
        for c in range(3):
            o = SC.debris_block(WC, f'{kind}{c}', n, (120.0, 120.0, Z), kind, seed * 10 + c); blocks.append((o, kind, c, speed))
    items['blocks'] = blocks
    if shot.kind == 'orla' and shot.name in ('C', 'D'):
        teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
        capm = bpy.data.materials['Teo_Bone']
        fc = B.new_coll('BoneVoando'); fcap = B.link(bpy.data.objects.new('bone_voando', None), fc)
        hr = B.TEO['head_r']
        B.sphere('bv_copa', hr * 1.03, (0, 0, 0), capm, fc, scale=(1, 1, 0.45)).parent = fcap
        B.box('bv_aba', (hr * 1.5, hr * 1.1, 0.02), (0, -hr * 0.95, -hr * 0.28), capm, fc, bevel=0.01).parent = fcap
        fcap.rotation_mode = 'XYZ'; fcap.scale = (0.0001,) * 3; items['fcap'] = fcap
        items['caps'] = [o for o in bpy.data.objects if o.name in ('Teo_bone', 'Teo_aba')]
    if shot.kind == 'bus':
        bus = SC.build_bus(); bus['root'].location = (P.BUS_X, 0, ZT - 0.12); bus['root'].rotation_euler = (0, 0, math.radians(90)); items['bus'] = bus
        pax = []
        teo = B.build_character('Teo', B.TEO, bus['coll']); teo['root'].parent = bus['body']
        teo['root'].location = (0.95, 0.42, bus['z_floor']); teo['root'].rotation_euler = (0, 0, math.radians(90)); items['teo'] = teo
        for i, (x, Pp) in enumerate(((-2.7, dict(B.TEO, shirt=(0.75, 0.15, 0.18), cap=None, hair=(0.12, 0.08, 0.05), h=0.95)),
                                     (2.15, dict(B.TEO, shirt=(0.45, 0.25, 0.65), cap=None, hair=(0.6, 0.6, 0.6), h=0.97)))):
            ch = B.build_character(f'Pass{i}', Pp, bus['coll'], seated=True); ch['root'].parent = bus['body']
            ch['root'].location = (x + 0.05, 0.75, 0.35 + 0.91 - ch['hip_z'] + 0.02); ch['root'].rotation_euler = (0, 0, math.radians(90)); pax.append(ch)
        items['pax'] = pax
    if shot.name == 'H':   # barras comparativas de vento
        bo = shot.bars['origin']
        def bar(key_, text, color, length, dz):
            root = B.link(bpy.data.objects.new('barra_' + key_, None), RC); root.location = (bo[0], bo[1], bo[2] + dz)
            c = root.constraints.new('COPY_ROTATION'); c.target = cam
            m = B.mat_basic('Barra_' + key_, color, 0.4, emit=color, emit_s=1.6)
            b = B.box('barra', (1.0, 0.75, 0.06), (0.5, 0, 0), m, RC, bevel=0.08); b.parent = root
            b.data.transform(Matrix.Translation((0, 0, 0))); b.location = (-4.6, 0, 0); b.scale = (0.0001, 1, 1)
            lb = B.label(text, (0, 0, 0), 0.8, color, coll=RC, name='rot_barra_' + key_); lb.parent = root
            for ch in lb.children: ch.visible_shadow = False; lb.location = (-4.6 + 2.3, 0.85, 0.0)
            lb.scale = (0.0001,) * 3
            return root, b, lb, length
        items['bar_big'] = bar('big', '1.670 km/h', (1.0, 0.25, 0.15), 9.2, 0.0)
        items['bar_small'] = bar('small', 'maior rajada: 408 km/h', (1.0, 0.80, 0.08), 9.2 * 408 / 1670, 2.35)
        x4 = B.label('4× mais forte', (0, 0, 0), 0.7, (1.0, 1.0, 1.0), coll=RC, name='rot_x4'); x4.parent = items['bar_big'][0]
        for ch in x4.children: ch.visible_shadow = False
        x4.location = (1.3, -1.05, 0.02); x4.scale = (1e-4,) * 3; items['x4'] = x4
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)
for (kk, loc, length, t_on) in getattr(shot, 'arrows', []): items['arr_' + kk] = (arrow(kk, loc, length, P.YEL if kk != 'vento' else P.RED), t_on)

# ================================================================== animação
def teo_pose_orla(T, f):
    teo = items['teo']; r = teo['root']; x0, y0 = P.TEO_SPOT
    face0 = 2 * math.pi * 150 / 360 + math.pi / 2           # olhando o mar (noroeste)
    if shot.name == 'C' or T < P.T_CHAO:
        jolt = sstep(P.T_TRAVA, P.T_TRAVA + 0.12, T) * (1 - sstep(P.T_TRAVA + 0.25, P.T_TRAVA + 1.0, T)) if shot.name == 'D' else 0.0
        r.location = (x0 + 0.06 * jolt, y0, SC.sand_z(x0)); r.rotation_euler = (0, 0, face0 - 0.25 * jolt)
        br = math.sin(T * 1.6)
        shrug = sstep(17.7, 18.0, T) * (1 - sstep(18.4, 18.9, T)) if shot.name == 'C' else 0.0
        alarm = sstep(P.T_TRAVA, P.T_TRAVA + 0.2, T) if shot.name == 'D' else 0.0
        B.pose(teo, frame=f, spine=(1.5 * br - 6 * jolt, 0, 0), head=(4 * math.sin(T * 0.5) + 8 * jolt, 10 * math.sin(T * 0.35) - 20 * alarm, 0),
               **{'upper_arm.L': (-8 - 30 * shrug - 25 * alarm, 0, -6 - 30 * shrug - 20 * jolt), 'upper_arm.R': (-8 - 30 * shrug - 25 * alarm, 0, 6 + 30 * shrug + 20 * jolt),
                  'forearm.L': (-18 - 70 * shrug - 40 * alarm, 0, 0), 'forearm.R': (-18 - 70 * shrug - 40 * alarm, 0, 0),
                  'thigh.L': (-4 * jolt, 0, 0), 'shin.L': (6 * jolt, 0, 0)})
        B.set_face(teo, {'neutral': 1 - alarm, 'alarm': alarm} if alarm else ({'relief': shrug, 'neutral': 1 - shrug}), f)
    else:
        u = sstep(P.T_CHAO, P.T_CHAO + 0.55, T); w = shot.wind(T)
        x1, y1 = P.PALM_HUG[0] - 0.40, P.PALM_HUG[1] - 0.05
        hop = 0.10 * math.sin(math.pi * min(1, (T - P.T_CHAO) / 0.55)) if T < P.T_CHAO + 0.55 else 0.0
        r.location = (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, SC.sand_z(x0) + hop)
        r.rotation_euler = (0, 0, face0 + (math.pi / 2 - face0) * u)
        fl = 0.5 + 0.5 * math.sin(T * 13)
        B.pose(teo, frame=f, spine=(18 * u + 3 * w * fl, 0, 0), head=(-10 * u, 0, 0),
               **{'upper_arm.L': (-82 * u, 0, -6 + 14 * u), 'upper_arm.R': (-82 * u, 0, 6 - 14 * u),
                  'forearm.L': (-58 * u, 0, -10 * u), 'forearm.R': (-58 * u, 0, 10 * u),
                  'thigh.L': (-15 * u + (18 + 4 * fl) * w, 0, 0), 'thigh.R': (10 * u + (24 + 5 * fl) * w, 0, 0),
                  'shin.L': (20 * u + 10 * w, 0, 0), 'shin.R': (14 * u + 12 * w, 0, 0)})
        B.set_face(teo, {'alarm': 1.0}, f)
    key(r, 'location', 'rotation_euler', f=f)
    # boné voa no tranco
    if 'fcap' in items:
        tc = P.T_CHAO + 0.15; flying = shot.name == 'D' and T >= tc
        for o in items['caps']: o.hide_render = flying; o.keyframe_insert('hide_render', frame=f)
        fc = items['fcap']
        if flying:
            t = T - tc; head = Vector((x0 + 0.3, y0, SC.sand_z(x0) + 1.75))
            fc.location = head + Vector((5.5 * t + 3.0 * t * t, 0.6 * t, 1.6 * t - 0.25 * t * t)); fc.scale = (1, 1, 1)
            fc.rotation_euler = (3.1 * t, 5.3 * t, 1.7 * t)
        else: fc.scale = (0.0001,) * 3
        key(fc, 'location', 'scale', 'rotation_euler', f=f)

def spring_series(Tq, drive, k=60.0, c=7.0, t_from=None):
    """Integra θ'' = -kθ - cθ' + drive(t) de shot.t0 até Tq (passo 1/600 s)."""
    t = t_from if t_from is not None else shot.t0; th = 0.0; om = 0.0; dt = 1 / 600
    while t < Tq:
        acc = -k * th - c * om + drive(t); om += acc * dt; th += om * dt; t += dt
    return th

def decel(t): return P.BUS_DEC if P.T_BRAKE <= t < P.T_BRAKE + P.BUS_V / P.BUS_DEC else 0.0

fr = list(shot.frames)
wphase = 0.0; prevT = None; sphase = {}
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4))
    if SPACE:
        sp = earth['spin']; sp.rotation_euler = (0, 0, shot.spin(T)); key(sp, 'rotation_euler', f=f); ev['spin'] = shot.spin(T)
        if shot.kind == 'orbit':
            earth['root'].location = shot.earth_pos(T); key(earth['root'], 'location', f=f)
            items['orb'].bevel_depth = 0.0001 + 0.035 * (1 - sstep(53.6, 54.6, T)); items['orb'].keyframe_insert('bevel_depth', frame=f)
        if 'eq' in items: items['eq'].data.bevel_depth = 0.0001 + 0.0055 * shot.equator(T); items['eq'].data.keyframe_insert('bevel_depth', frame=f)
        if 'pol' in items: items['pol'].data.bevel_depth = 0.0001 + 0.0055 * shot.polar(T); items['pol'].data.keyframe_insert('bevel_depth', frame=f)
        if 'arc' in items:
            cu, hd = items['arc']; k_ = shot.arrow(T); cu.bevel_depth = 0.0001 + 0.012 * k_; cu.keyframe_insert('bevel_depth', frame=f)
            hd.scale = (max(k_, 1e-4),) * 3; key(hd, 'scale', f=f)
        SC.set_value('Terra', 'K_faixas', shot.bands(T) if hasattr(shot, 'bands') else 0.0, f)
        SC.set_value('Terra', 'K_oceano', shot.ocean(T) if hasattr(shot, 'ocean') else 0.0, f)
        if hasattr(shot, 'ocean'):
            SC.set_value('Nuvens', 'K_nuvem', 0.9 * (1 - 0.85 * shot.ocean(T)), f)
            SC.set_value('Terra', 'K_luzes', 1 - shot.ocean(T), f)
    else:
        w = shot.wind(T); ev['wind'] = w
        dt = 0 if prevT is None else T - prevT; prevT = T
        wphase += dt * (0.9 + 16.0 * w); SC.set_value('Mar', 'W_fase', wphase, f)
        surge = shot.surge(T) if hasattr(shot, 'surge') else 0.0; ev['surge'] = surge
        xf = 46.0 * surge; lvl = 2.0 * sstep(0.0, 0.55, surge) + 0.0
        sea = items['sea']; sea.location = (-700 + xf, 0, -3.0 + lvl); key(sea, 'location', f=f)
        lip = items['lip']; lip.location = (xf - 0.1, 0, lvl - 0.05); lip.scale = (1.0, 1.0, 1.0) if surge > 0.001 else (1e-4, 1e-4, 1e-4)
        lip.scale = (1 + 0.6 * sstep(0.0, 0.3, surge),) * 2 + (1.0,) if surge > 0.001 else (1e-4,) * 3; key(lip, 'location', 'scale', f=f)
        sh = items['shore']; sh.location = (-0.3 + 0.25 * math.sin(T * 0.9) + xf, 0, 0.006 + lvl); key(sh, 'location', f=f)
        for p in palms: SC.pose_palm(p, w, T, f)
        for (o, kind, c, speed) in items['blocks']:
            sphase[(kind, c)] = sphase.get((kind, c), 0.0) + dt * speed * (w ** 1.5 if kind != 'risco' else w)
            o.location = (-150 + ((sphase[(kind, c)] + c * 120) % 360), 0.0 if kind != 'areia' else 0.0, 0.0 if kind == 'risco' else ZT * 0.0)
            zs = 1.0 if kind == 'risco' else max(w, 1e-3)
            o.scale = (1, 1, zs); key(o, 'location', 'scale', f=f)
            o.hide_render = w < 0.02; o.keyframe_insert('hide_render', frame=f)
        bpy.data.materials['Risco'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.45 * w
        bpy.data.materials['Risco'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].keyframe_insert('default_value', frame=f)
        if 'teo' in items and shot.kind == 'orla': teo_pose_orla(T, f)
        if shot.kind == 'bus':
            bus = items['bus']; yb = shot.bus_y(T); bus['root'].location = (P.BUS_X, yb, ZT - 0.12); key(bus['root'], 'location', f=f)
            for wh in bus['wheels']: wh.rotation_euler = (0, (yb + 40) / 0.5, 0); key(wh, 'rotation_euler', f=f)
            pitch = 0.004 * spring_series(T, decel, 45.0, 6.0)
            bus['body'].rotation_euler = (0, pitch, 0); key(bus['body'], 'rotation_euler', f=f)
            braking = P.T_BRAKE <= T
            nd = bus['tail'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']; nd.default_value = 7.0 if braking else 0.6; nd.keyframe_insert('default_value', frame=f)
            lean = spring_series(T, decel, 30.0, 4.5)          # graus por (m/s²)·(1/k): ~1,3° por m/s² no regime
            teo = items['teo']; lt = 1.6 * lean
            teo['root'].location = (0.95 + 0.012 * lt, 0.42, bus['z_floor']); key(teo['root'], 'location', f=f)
            B.pose(teo, frame=f, spine=(lt, 0, 0), head=(0.4 * lt, 8 * math.sin(T * 0.6), 0),
                   **{'upper_arm.R': (-150 + 0.3 * lt, 0, 12), 'forearm.R': (-25, 0, 0), 'upper_arm.L': (-10 - 1.5 * lt, 0, -8), 'forearm.L': (-20 - 1.0 * lt, 0, 0),
                      'thigh.L': (-0.3 * lt, 0, 0), 'thigh.R': (0.4 * lt, 0, 0)})
            B.set_face(teo, {'alarm': 1.0} if T > P.T_BRAKE + 0.15 and T < P.T_BRAKE + 2.6 else {'neutral': 1.0}, f)
            for i, ch in enumerate(items['pax']):
                lp = 1.25 * lean * (1.0 if i == 0 else 0.85)
                B.pose(ch, frame=f, sit=1.0, spine=(8 + lp, 0, 0), head=(0.5 * lp, 6 * math.sin(T * 0.7 + i), 0),
                       **{'upper_arm.L': (-30 - 1.2 * lp, 0, -8), 'upper_arm.R': (-30 - 1.2 * lp, 0, 8)})
                B.set_face(ch, {'alarm': 1.0} if T > P.T_BRAKE + 0.2 and T < P.T_BRAKE + 2.6 else {'neutral': 1.0}, f)
            ev.update(bus_y=yb, bus_v=shot.bus_v(T), lean=lean)
        if shot.name == 'H':
            bb = shot.bars
            for kb, t_on in (('bar_big', bb['t_big']), ('bar_small', bb['t_small'])):
                root, b, lb, length = items[kb]; g = sstep(t_on, t_on + 0.7, T)
                b.scale = (max(length * g, 1e-4), 1, 1); key(b, 'scale', f=f)
                s = pop_scale(T, t_on); lb.scale = (s, s, s); key(lb, 'scale', f=f)
            s = pop_scale(T, bb['t_x4']); items['x4'].scale = (s, s, s); key(items['x4'], 'scale', f=f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off); o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
        elif kk.startswith('arr_'):
            o, t_on = v; s = pop_scale(T, t_on); o.scale = (s, s, s); key(o, 'scale', f=f)
    c = shot.cam(T); cam.location = c['pos']; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    ev['cam'] = [round(x, 3) for x in c['pos']]; events['frames'].append(ev)

# interpolação linear (desfoque de movimento usa subquadros); visibilidade em degrau
def all_ads():
    for ob in list(bpy.data.objects) + [cam.data] + list(bpy.data.curves) + list(bpy.data.armatures):
        if getattr(ob, 'animation_data', None) and ob.animation_data.action: yield ob.animation_data
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action: yield m.node_tree.animation_data
for ad in all_ads():
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
# rotações de câmera: evita salto de ±π entre quadros (euler compatível)
fcs = [fc for fc in (cam.animation_data.action.fcurves if cam.animation_data else []) if fc.data_path == 'rotation_euler']
for fc in fcs:
    pts = fc.keyframe_points
    for i in range(1, len(pts)):
        d = pts[i].co[1] - pts[i - 1].co[1]
        while d > math.pi: pts[i].co[1] -= 2 * math.pi; d -= 2 * math.pi
        while d < -math.pi: pts[i].co[1] += 2 * math.pi; d += 2 * math.pi
sc.frame_start, sc.frame_end = fr[0], fr[-1]; sc.frame_step = step
out = os.path.join(HERE, 'frames' if FINAL else 'preview', shot.name); os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(HERE, 'events'), exist_ok=True); json.dump(events, open(os.path.join(HERE, 'events', f'{shot.name}.json'), 'w'))
print(f'[{shot.name}] cena pronta em {time.time() - t0:.1f}s; quadros {fr[0]}–{fr[-1]} ({len(fr)}), {W}x{H}, {spp} spp, passo {step}', flush=True)
if a.save_blend: os.makedirs(os.path.join(HERE, 'build'), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'build', f'{shot.name}.blend'))
if a.still is not None:
    sc.frame_set(a.still); sc.render.filepath = os.path.join(out, f'still_{a.still:04d}.png'); sc.render.use_overwrite = True
    bpy.ops.render.render(write_still=True)
else:
    if a.frames:
        f0, f1 = map(int, a.frames.split('-')); sc.frame_start, sc.frame_end = f0, f1
    sc.render.filepath = os.path.join(out, '####'); t1 = time.time(); bpy.ops.render.render(animation=True)
    print(f'[{shot.name}] render {time.time() - t1:.1f}s', flush=True)
