"""Vídeo 10: monta a cena 3D de um plano, anima quadro a quadro e renderiza. Os textos e gráficos NÃO estão aqui:
ficam na camada de motion graphics (v2/ep10/mograph.py), que lê as âncoras 3D projetadas que este script grava em events/<plano>.json.
Uso: blender -b --python v2/ep10/render.py -- --shot A1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]"""
import bpy, sys, os, math, json, time, argparse, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import build as B
import scene as SC
import plan as P
os.environ.setdefault('STYLE2', '1')
import style2 as S2
from story import sstep
from mathutils import Vector, Matrix, Euler

ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--mode', default='preview')
ap.add_argument('--spp', type=int); ap.add_argument('--step', type=int); ap.add_argument('--frames'); ap.add_argument('--still', type=int)
ap.add_argument('--save-blend', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
shot = P.BY_NAME[a.shot]; FINAL = a.mode == 'final'; K = shot.set
W, H = (720, 1280) if FINAL else (270, 480)
if os.environ.get('PREVIEW_RES'): W, H = map(int, os.environ['PREVIEW_RES'].split('x'))
spp = a.spp or (8 if FINAL else 5); step = a.step or (1 if FINAL else 3)

bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
sc = bpy.context.scene; sc.world = bpy.data.worlds.new('tmp')
B.setup_render(W, H, spp, preview=not FINAL)
sc.cycles.use_light_tree = False
for n in sc.node_tree.nodes:
    if n.bl_idname == 'CompositorNodeMath': n.inputs[1].default_value = 0.0
cam = B.link(bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.02; cam.data.clip_end = 600
C = B.new_coll('Ep10')

def key(o, *props, f):
    for p in props: o.keyframe_insert(p, frame=f)
def look_rot(pos, look, up=(0, 0, 1)):
    z = (Vector(pos) - Vector(look)).normalized(); u = Vector(up); x = u.cross(z)
    if x.length < 1e-6: x = Vector((1, 0, 0))
    x.normalize(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_euler()
def project(p, pos, rot, lens):
    """Projeção pinhole igual à do Blender (sensor 36 mm no lado maior). Devolve (u, v) em fração da imagem e profundidade."""
    R = rot.to_matrix(); pc = R.transposed() @ (Vector(p) - Vector(pos))
    if pc.z > -1e-3: return None
    f = lens / 36.0 * max(W, H)
    return [round((W / 2 + f * pc.x / -pc.z) / W, 4), round((H / 2 - f * pc.y / -pc.z) / H, 4), round(-pc.z, 3)]
def snap_pop(T, t_on, t_off=99):
    k = S2.snap(T - t_on) * (1 - S2.snap(T - t_off, back=False)); return max(k, 1e-4)

# ------------------------------------------------------------------ luz extra para os personagens no palco escuro
R = SC.palco()
fill = bpy.data.lights.new('Preenchimento', 'AREA'); fill.energy = 160; fill.size = 5; fill.color = (0.85, 0.9, 1.0)
fo = B.link(bpy.data.objects.new('Preenchimento', fill)); fo.location = (2.5, -5.5, 2.2); fo.rotation_euler = look_rot((2.5, -5.5, 2.2), (0, 0, 1.0))

# ------------------------------------------------------------------ poses
POSES = {
    'stand': {'head': (0, 0, 0), 'upper_arm.L': (0, 0, -6), 'upper_arm.R': (0, 0, 6), 'forearm.L': (-12, 0, 0), 'forearm.R': (-12, 0, 0)},
    'give': {'head': (6, 0, 6), 'upper_arm.L': (0, 0, -6), 'forearm.L': (-12, 0, 0), 'upper_arm.R': (-72, 0, 12), 'forearm.R': (-25, 0, 0)},
    'look': {'spine': (-4, 0, 0), 'head': (-22, 0, 8), 'upper_arm.L': (-10, 0, -25), 'upper_arm.R': (-10, 0, 25), 'forearm.L': (-40, 0, 0), 'forearm.R': (-40, 0, 0)},
    'shrug': {'head': (-6, 0, 10), 'upper_arm.L': (-15, 0, -40), 'upper_arm.R': (-15, 0, 40), 'forearm.L': (-85, 0, 0), 'forearm.R': (-85, 0, 0)},
    'scared': {'spine': (6, 0, 0), 'head': (12, 0, 0), 'upper_arm.L': (-30, 0, -35), 'upper_arm.R': (-30, 0, 35), 'forearm.L': (-50, 0, 0), 'forearm.R': (-50, 0, 0)},
    'proud': {'spine': (-4, 0, 0), 'head': (-8, 0, 0), 'upper_arm.L': (-8, 0, -14), 'upper_arm.R': (-8, 0, 14), 'forearm.L': (-95, 0, 25), 'forearm.R': (-95, 0, -25)},
    'cup': {'head': (8, 0, -6), 'upper_arm.L': (0, 0, -6), 'forearm.L': (-12, 0, 0), 'upper_arm.R': (-38, 0, 12), 'forearm.R': (-92, 0, 0)},
    'hold': {'head': (4, 0, 0), 'upper_arm.L': (-62, 0, 14), 'upper_arm.R': (-62, 0, -14), 'forearm.L': (-30, 0, 0), 'forearm.R': (-30, 0, 0)},
    'wave': {'head': (-6, 0, -8), 'upper_arm.L': (0, 0, -6), 'forearm.L': (-12, 0, 0), 'upper_arm.R': (-150, 0, 30), 'forearm.R': (-40, 0, 0)},
}
def place_teo(ch, loc, rz=0.0):
    ch['root'].location = loc; ch['root'].rotation_euler = (0, 0, math.radians(rz))
def hand_world(ch, side='R'):
    bpy.context.view_layer.update(); pb = ch['arm'].pose.bones[f'forearm.{side}']; return ch['arm'].matrix_world @ pb.tail

items = {}; ANC = {}            # ANC: nome -> função T -> ponto 3D
events = dict(shot=shot.name, fps=P.FPS, frames=[])

# ================================================================== cenários
def coin_path(p0, p1, u, h=0.6):
    p0, p1 = Vector(p0), Vector(p1); p = p0.lerp(p1, u); p.z += h * 4 * u * (1 - u); return p

if K == 'cofre':
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo; place_teo(teo, P.TEO_A, 35)
    cf = SC.cofre('Cofre', C, P.COFRE, 0.9); items['cofre'] = cf
    cal = SC.calendario('Cal', C, P.CAL, 1.25); items['cal'] = cal
    items['coins'] = SC.coins(22, C)
    B.pose(teo, **POSES['give']); hand = hand_world(teo) + Vector((0.0, -0.04, -0.05))
    slot = Vector(P.COFRE) + Vector((0, 0, 1.72 * 0.9 + 0.05))
    items['hand'], items['slot'] = hand, slot
elif K == 'cadeado':
    items['lock'] = SC.cadeado('Cadeado', C, (0, 0, 0.45), 1.0); ANC['lock'] = lambda T: (0, 0, 1.05)
    ped = B.cyl('pedestal', 0.5, 0.45, (0, 0, 0.225), B.mat_basic('Pedestal', (0.12, 0.13, 0.16), 0.4), C, seg=48)
elif K == 'pib':
    pz = SC.pizza('PIB', C, (0, 0, 0.0), 1.2, 0.323); pz['root'].rotation_euler = (0, 0, -math.pi / 2 - pz['mid_ang']); items['pizza'] = pz
    items['bars'] = SC.colunas('Barra', C, [('br', SC.YEL, 32.3 * 0.05), ('al', (0.55, 0.58, 0.64), 21.3 * 0.05)], loc=(3.4, 0.0, 0.0), gap=1.0, w=0.6)
    for k_, (o, h_) in items['bars'].items(): ANC['bar_' + k_] = (lambda o, h_: (lambda T: (o.location.x, 0.0, h_ + 0.32)))(o, h_)
elif K == 'preco':
    SC.pacote('Pacote', C, (0, 0.55, 0), 1.35)
    tg = SC.etiqueta('Etq', C, (0.0, -0.3, 1.25), 0.43, 1.0, 0.46); items['tag'] = tg
    st = B.cyl('barbante', 0.006, 0.7, (-0.25, 0.1, 1.55), B.mat_basic('Barbante', (0.85, 0.8, 0.7), 0.8), C, seg=6, rot=(math.radians(-50), 0, math.radians(20)))
elif K == 'bomba':
    bb = SC.bomba('Bomba', C, (0, 0.3, 0)); items['bomba'] = bb; ANC['visor'] = lambda T: (0, 0.3 - 0.34, 1.28)
elif K == 'rombo':
    cf = SC.cofre('CofreEstado', C, (0, 0.3, 0), 1.1, hole=True); items['cofre'] = cf; ANC['cofre_top'] = lambda T: (0, 0.3, 2.15)
    items['coins'] = SC.coins(60, C, r=0.08)
    items['hole'] = Vector((0.76 * 1.1 + 0.05, 0.3 - 0.1 * 1.1, 0.35 * 1.1))
elif K == 'kansas':
    bars = []
    for i in range(6):
        o = B.box(f'arrec{i}', (0.42, 0.42, 1.0), (0, 0, 0), B.mat_basic('Arrec', (0.10, 0.62, 0.66), 0.4, emit=(0.10, 0.62, 0.66), emit_s=0.1), C, bevel=0.03)
        for v in o.data.vertices: v.co.z += 0.5
        o.location = (-1.5 + 0.6 * i, 0.0, 0.0); bars.append(o)
    items['kbars'] = bars; ANC['bars_top'] = lambda T: (0.0, 0.0, 2.05)
    ar = B.link(bpy.data.objects.new('seta', None), C); ar.location = (0.75, -1.3, 0.25)
    gm = B.mat_basic('SetaVerde', (0.30, 0.85, 0.40), 0.35, emit=(0.30, 0.85, 0.40), emit_s=0.3)
    sh_ = B.cyl('seta_haste', 0.07, 1.3, (0, 0, 0.65), gm, C, seg=20); sh_.parent = ar
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.0, depth=0.38, location=(0, 0, 1.45)); cn = bpy.context.active_object
    for c_ in cn.users_collection: c_.objects.unlink(cn)
    C.objects.link(cn); cn.data.materials.append(gm); cn.parent = ar; items['arrow'] = ar
    ANC['arrow_tip'] = lambda T: tuple(ar.matrix_world @ Vector((0, 0, 1.75)))
elif K == 'balanca':
    bz = SC.balanca('Balanca', C, (0, 0.5, 0), 1.3); items['bal'] = bz
    poor = B.build_character('TeoPobre', B.TEO, B.new_coll('PobreCol')); place_teo(poor, P.POOR, 18); items['poor'] = poor
    rich = B.build_character('TeoRico', SC.SUIT, B.new_coll('RicoCol')); place_teo(rich, P.RICH, -18); items['rich'] = rich
    tie = B.box('gravata', (0.06, 0.02, 0.26), (P.RICH[0], P.RICH[1] - 0.13, 1.22), B.mat_basic('Gravata', (0.8, 0.12, 0.12), 0.5), C); tie.parent = rich['root']; tie.matrix_parent_inverse = rich['root'].matrix_world.inverted()
    items['packs'] = [SC.pacote(f'Cafe{i}', C, (0, 0, -50), 0.32, (0.55, 0.16, 0.10))['root'] for i in range(2)]
    def pan_pos(i):
        return lambda T: tuple(items['bal']['root'].matrix_world @ (items['bal']['pans'][i].location + Vector((0, 0, -0.45))))
    ANC['pan_l'], ANC['pan_r'] = pan_pos(0), pan_pos(1)
    ANC['head_l'] = lambda T: (P.POOR[0], P.POOR[1], 2.15); ANC['head_r'] = lambda T: (P.RICH[0], P.RICH[1], 2.15)
elif K == 'cafe':
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo; place_teo(teo, (0, 0, 0), 0)
    B.pose(teo, **POSES['cup']); hw = hand_world(teo)
    cup = SC.xicara('Xicara', C); cup.location = hw + Vector((0.0, -0.02, -0.03)); cup.scale = (1.5,) * 3; items['cup'] = cup
    cal = SC.calendario('Cal', C, (0.95, 1.2, 0), 1.0, months=['MAI'], day='31'); items['cal'] = cal; ANC['cal'] = lambda T: (0.95, 1.2, 0.75)
    items['coins'] = SC.coins(16, C, r=0.05)
elif K == 'tesoura':
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo; place_teo(teo, (0, 0, 0), 0)
if hasattr(shot, 'scissors') or K == 'tesoura':
    ts = SC.tesoura('Tesoura', C, 1.6); items['scissors'] = ts
if os.environ.get('ACAB', '1') == '1': SC.acabamento(); SC.luzes_recorte()           # texturas procedurais, piso com grade e recortes coloridos (melhoria de 17/11)
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
if getattr(shot, 'dim', 0): sc.view_settings.exposure -= 1.6 * shot.dim

# ================================================================== animação quadro a quadro
def teo_pose(ch, seq, f, T, face='neutral', breath=1.0):
    rot, _, _ = S2.pose_seq(seq, T, breath=breath); B.pose(ch, frame=f, **rot); B.set_face(ch, {face: 1.0}, f)

def scissors_anim(ts, T, f, loc, t_on, t_off, snips, rot_z=0.0):
    k = snap_pop(T, t_on, t_off); ts['root'].scale = (k * 1.6,) * 3
    ts['root'].location = loc; ts['root'].rotation_euler = (math.radians(90), 0, rot_z)
    op = 50.0
    for sn in snips:
        if sn - 0.18 <= T < sn + 0.35: op = 50 * min(1, abs(T - sn) / (0.18 if T < sn else 0.35))
    SC.tesoura_pose(ts, op); key(ts['root'], 'scale', 'location', 'rotation_euler', f=f)
    for hv in ts['halves']: key(hv, 'rotation_euler', f=f)

rng = random.Random(7)
fr = list(shot.frames)
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4))
    c = shot.cam(T)
    if K == 'cadeado' and T > shot.shake: c = dict(c); c['pos'] = tuple(Vector(c['pos']) + Vector((0.03 * math.sin(T * 70), 0, 0.02 * math.sin(T * 55))) * math.exp(-(T - shot.shake) / 0.25))
    if S2.ON: c = S2.cam_fx(c, T, shot)
    # ------------------------------------------------ cofre, moedas e calendário
    if K == 'cofre':
        teo = items['teo']
        if shot.teo == 'give': teo_pose(teo, [(shot.t0 - 1, POSES['give'])], f, T, 'focus', 0.4)
        else: teo_pose(teo, [(shot.t0 - 1, POSES['give']), (5.30, POSES['look'])], f, T, 'alarm' if T < 5.9 else 'relief')
        mode, ta, tb = shot.coins; n = len(items['coins'])
        for i, o in enumerate(items['coins']):
            ts_ = ta + (tb - 0.6 - ta) * i / (n - 1); u = (T - ts_) / 0.55
            if mode == 'out': u = 1 - (T - ts_) / 0.55; u = 1.0 - u if False else u
            if 0 <= (T - ts_) <= 0.55:
                uu = (T - ts_) / 0.55
                p = coin_path(items['hand'], items['slot'], uu if mode == 'in' else 1 - uu, 0.7)
                o.location = p; o.rotation_euler = (math.radians(90), T * 9 + i, T * 4 + i); o.scale = (1, 1, 1)
            else: o.location = (0, 0, -50)
            key(o, 'location', 'rotation_euler', f=f)
        pages = items['cal']['pages']
        times = getattr(shot, 'pages', None)
        for i, pv in enumerate(pages):
            tp = times[i] if (times and i < len(times)) else (-1 if getattr(shot, 'pages_done', False) and i < 5 else 999)
            u = S2.snap(T - tp, 0.35, back=False) if tp >= 0 else 1.0
            if tp == 999: u = 0.0
            pv.rotation_euler = (math.radians(-150) * u, 0, math.radians(25 * u) * (1 if i % 2 else -1))
            pv.location = (0.4 * u * (1 if i % 2 else -1), -0.02 * (len(pages) - 1 - i) - 1.5 * u, 1.32 + 1.6 * u)
            s_ = 1.0 if u < 0.6 else max(1e-4, 1 - (u - 0.6) / 0.4); pv.scale = (s_,) * 3
            key(pv, 'rotation_euler', 'location', 'scale', f=f)
    # ------------------------------------------------ cadeado
    elif K == 'cadeado':
        lk = items['lock']; sh = math.exp(-max(T - shot.shake, 0) / 0.3) * (1 if T >= shot.shake else 0)
        lk['root'].rotation_euler = (0, math.radians(9 * sh * math.sin((T - shot.shake) * 40)), math.radians(-20 + 6 * math.sin(T * 0.8)))
        lk['alca'].location = (0, 0, 0.16 * S2.snap(T - shot.shake - 0.05, 0.2)); key(lk['root'], 'rotation_euler', f=f); key(lk['alca'], 'location', f=f)
    # ------------------------------------------------ PIB
    elif K == 'pib':
        pz = items['pizza']; u = S2.snap(T - shot.slice, 0.35); m = pz['mid_ang']
        pz['slice'].location = (0.45 * u * math.cos(m), 0.45 * u * math.sin(m), 0.25 * u); key(pz['slice'], 'location', f=f)
        pz['root'].rotation_euler = (0, 0, -math.pi / 2 - m + 0.15 * math.sin(T * 0.5)); key(pz['root'], 'rotation_euler', f=f)
        for i, (k_, (o, h_)) in enumerate(items['bars'].items()):
            u = S2.snap(T - shot.bars[i], 0.45); o.scale = (1, 1, max(h_ * u, 1e-3)); key(o, 'scale', f=f)
    # ------------------------------------------------ etiqueta
    elif K == 'preco':
        tg = items['tag']; u = S2.snap(T - shot.split, 0.3)
        tg['root'].rotation_euler = (0, 0, math.radians(6 * math.sin(T * 1.3))); key(tg['root'], 'rotation_euler', f=f)
        tg['a'].location = (-0.5 + tg['wp'] / 2 - 0.12 * u, 0, 0); tg['b'].location = (0.5 - tg['wi'] / 2 + 0.28 * u, -0.05 * u, 0.06 * u)
        tg['b'].rotation_euler = (0, math.radians(-14 * u), 0); key(tg['a'], 'location', f=f); key(tg['b'], 'location', 'rotation_euler', f=f)
        ANC['tag_a'] = (lambda pa: (lambda T: tuple(pa.matrix_world @ Vector((0, 0, 0.4)))))(tg['a']); ANC['tag_b'] = (lambda pb: (lambda T: tuple(pb.matrix_world @ Vector((0, 0, 0.4)))))(tg['b'])
    # ------------------------------------------------ rombo
    elif K == 'rombo':
        n = len(items['coins']); hole = items['hole']
        for i, o in enumerate(items['coins']):
            ts_ = shot.drain + i * 0.07; dt = T - ts_
            if dt < 0: o.location = (0, 0, -50)
            else:
                rr = random.Random(i); vx, vy = 1.2 + rr.random() * 1.2, -0.6 + rr.random() * 1.0
                z = hole.z + 0.6 * dt - 4.9 * dt * dt
                if z > 0.012: o.location = (hole.x + vx * dt, hole.y + vy * dt, z); o.rotation_euler = (dt * 12 + i, dt * 7, 0)
                else:
                    tl = (hole.z + 0.6 * (0.6 + math.sqrt(0.36 + 19.6 * hole.z)) / 9.8)        # instante do toque no chão (aprox.)
                    dl = (0.6 + math.sqrt(0.36 + 19.6 * (hole.z - 0.012))) / 9.8
                    o.location = (hole.x + vx * dl, hole.y + vy * dl, 0.012 + 0.003 * (i % 4)); o.rotation_euler = (0, 0, i)
            key(o, 'location', 'rotation_euler', f=f)
    # ------------------------------------------------ Kansas
    elif K == 'kansas':
        for i, o in enumerate(items['kbars']):
            h_ = 1.35 + 0.05 * math.sin(i * 1.7)
            if hasattr(shot, 'drop'):
                d_ = S2.snap(T - shot.drop - 0.07 * i, 0.3, back=False); r_ = S2.snap(T - shot.rewind - 0.06 * (5 - i), 0.35)
                h_ = h_ * (1 - 0.62 * d_ * (1 - r_))
            o.scale = (1, 1, h_); key(o, 'scale', f=f)
        ar = items['arrow']
        if hasattr(shot, 'arrow_up'):
            u = S2.snap(T - shot.arrow_up, 0.4); ar.scale = (max(u, 1e-4),) * 3; ar.rotation_euler = (0, math.radians(30), 0)
        else:
            dr = S2.snap(T - shot.droop, 0.5, back=False); ar.scale = (1, 1, 1); ar.rotation_euler = (0, math.radians(30 + 95 * dr), 0)
            ar.location = (0.75, -1.3, 0.25 - 0.1 * dr)
        key(ar, 'scale', 'rotation_euler', 'location', f=f)
    # ------------------------------------------------ balança
    elif K == 'balanca':
        bz = items['bal']; tilt = getattr(shot, 'tilt', None)
        ang = 0.0 if tilt is None else 0.26 * S2.snap(T - tilt, 0.5)
        ang += 0.015 * math.sin(T * 1.7)
        SC.balanca_pose(bz, ang); key(bz['piv'], 'rotation_euler', f=f)
        for hp in bz['pans']: key(hp, 'location', f=f)
        k_ = snap_pop(T, shot.packets) if shot.packets else 1.0
        for i, pk in enumerate(items['packs']):
            pw = bz['root'].matrix_world @ (bz['pans'][i].location + Vector((0, 0, -0.93))); pk.location = pw; pk.scale = (0.32 * k_,) * 3; key(pk, 'location', 'scale', f=f)
        sad = tilt is not None and T > tilt
        teo_pose(items['poor'], [(shot.t0 - 1, POSES['stand'])] + ([(tilt, POSES['scared'])] if tilt is not None else []), f, T, 'alarm' if sad else 'neutral')
        teo_pose(items['rich'], [(shot.t0 - 1, POSES['stand'])] + ([(tilt + 0.15, POSES['proud'])] if tilt is not None else []), f, T, 'relief')
    # ------------------------------------------------ café
    elif K == 'cafe':
        teo_pose(items['teo'], [(shot.t0 - 1, POSES['cup'])], f, T, 'relief' if T < shot.burst else 'alarm', 0.0)
        k_ = snap_pop(T, shot.cal_on); items['cal']['root'].scale = (k_,) * 3; key(items['cal']['root'], 'scale', f=f)
        for i, o in enumerate(items['coins']):
            dt = T - shot.burst - 0.03 * i
            if dt < 0: o.location = (0, 0, -50)
            else:
                rr = random.Random(i); v = Vector((0.6 + rr.random() * 1.4, -0.4 + rr.random() * 0.6, 2.2 + rr.random() * 1.2))
                o.location = items['cup'].location + Vector((0, 0, 0.12)) + v * dt + Vector((0, 0, -2.0 * dt * dt)); o.rotation_euler = (dt * 10 + i, dt * 6, 0)
            key(o, 'location', 'rotation_euler', f=f)
    # ------------------------------------------------ tesoura final
    elif K == 'tesoura':
        teo_pose(items['teo'], [(shot.t0 - 1, POSES['hold'])], f, T, 'relief')
    if 'scissors' in items:
        if K == 'tesoura': scissors_anim(items['scissors'], T, f, (0.15, -0.7, 1.15), shot.t0 - 1, 99, shot.snips)
        elif K == 'bomba': scissors_anim(items['scissors'], T, f, (-1.05, -1.1, 1.75), shot.scissors[0], shot.scissors[1], shot.snips, math.radians(-20))
        else: scissors_anim(items['scissors'], T, f, (-0.3, -0.9, 1.75), shot.scissors[0], shot.scissors[1], shot.snips, math.radians(10))
    cam.location = Vector(c['pos']); rot = look_rot(c['pos'], c['look']); cam.rotation_euler = rot; cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    if ANC:
        if any(k_ in ('tag_a', 'tag_b', 'pan_l', 'pan_r', 'arrow_tip') for k_ in ANC): sc.frame_set(f) if False else bpy.context.view_layer.update()
        ev['anc'] = {k_: project(fn(T), c['pos'], rot, c['lens']) for k_, fn in ANC.items()}
    ev['cam'] = [round(x, 3) for x in c['pos']]; events['frames'].append(ev)

def all_ads():
    for ob in list(bpy.data.objects) + [cam.data] + list(bpy.data.armatures) + list(bpy.data.lights):
        if getattr(ob, 'animation_data', None) and ob.animation_data.action: yield ob.animation_data
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action: yield m.node_tree.animation_data
for ad in all_ads():
    for fc in ad.action.fcurves:
        if fc.modifiers: continue
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
for fc in [fc for fc in (cam.animation_data.action.fcurves if cam.animation_data else []) if fc.data_path == 'rotation_euler']:
    pts = fc.keyframe_points
    for i in range(1, len(pts)):
        d = pts[i].co[1] - pts[i - 1].co[1]
        while d > math.pi: pts[i].co[1] -= 2 * math.pi; d -= 2 * math.pi
        while d < -math.pi: pts[i].co[1] += 2 * math.pi; d += 2 * math.pi
if S2.ON:
    _c0 = shot.cam(shot.t0)
    S2.finish(sc, cam, focus_dist=(Vector(_c0['pos']) - Vector(_c0['look'])).length, f_stop=float(os.environ.get('S2_FSTOP', '2.8'))); S2.motion_blur(sc)
sc.frame_start, sc.frame_end = fr[0], fr[-1]; sc.frame_step = step
out = os.environ.get('RENDER_OUT') or os.path.join(HERE, 'frames' if FINAL else 'preview', shot.name); os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(HERE, 'events'), exist_ok=True); json.dump(events, open(os.path.join(HERE, 'events', f'{shot.name}.json'), 'w'))
print(f'[{shot.name}] cena pronta em {time.time() - t0:.1f}s; quadros {fr[0]}–{fr[-1]} ({len(fr)}), {W}x{H}, {spp} spp, passo {step}', flush=True)
if a.save_blend: os.makedirs(os.path.join(HERE, 'build'), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'build', f'{shot.name}.blend'))
if a.still is not None:
    sc.frame_set(a.still); sc.render.filepath = os.path.join(out, f'still_{a.still:04d}.png'); sc.render.use_overwrite = True
    t1 = time.time(); bpy.ops.render.render(write_still=True); print(f'[{shot.name}] still {time.time() - t1:.1f}s', flush=True)
else:
    if a.frames:
        f0, f1 = map(int, a.frames.split('-')); sc.frame_start, sc.frame_end = f0, f1
    sc.render.filepath = os.path.join(out, '####'); t1 = time.time(); bpy.ops.render.render(animation=True)
    print(f'[{shot.name}] render {time.time() - t1:.1f}s', flush=True)
