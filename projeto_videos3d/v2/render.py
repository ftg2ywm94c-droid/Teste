"""Monta a cena, anima um plano e renderiza.
Uso: blender -b --python v2/render.py -- --shot C [--mode preview|final] [--spp 12] [--step 1] [--frames 330-360] [--still 400]
Saída: v2/frames/<plano>/NNNN.png (final, número = quadro global a 30 fps) ou v2/preview/<plano>/NNNN.png.
Retomável: quadros já existentes são pulados (placeholders + sem sobrescrever)."""
import bpy, sys, os, math, json, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, 'lib'), HERE]
import build as B
import story as S
import shots as SH
from mathutils import Vector

ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--mode', default='preview')
ap.add_argument('--spp', type=int, default=None); ap.add_argument('--step', type=int, default=None); ap.add_argument('--frames'); ap.add_argument('--still', type=int)
ap.add_argument('--save-blend', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
shot = SH.BY_NAME[a.shot]; FINAL = a.mode == 'final'
ap2 = None
W, H = (720, 1280) if FINAL else (270, 480)
if os.environ.get('PREVIEW_RES'): W, H = map(int, os.environ['PREVIEW_RES'].split('x'))
spp = a.spp or (12 if FINAL else 5); step = a.step or (1 if FINAL else 3)

bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
B.setup_world(); B.build_street(signs=((-150.0, 50), (-75.0, 50)))
B.setup_render(W, H, spp, preview=not FINAL)
sc = bpy.context.scene

# ---------------------------------------------------------------- atores
teo = B.build_car('CarroTeo', (0.80, 0.10, 0.04))
need_blue = shot.name in ('F', 'G')
blue = B.build_car('CarroAzul', (0.06, 0.28, 0.75), driver=False) if need_blue else None
kidC = B.new_coll('Menino'); kid = B.build_character('Menino', B.KID, kidC)
ballc = B.gltf_collection('football')
_m = sorted([o for o in ballc.objects if o.type == 'MESH'], key=lambda o: o.name)
for o in _m[1:]: ballc.objects.unlink(o)          # o glTF traz duas bolas (variações); usa só uma
ball = bpy.data.objects.new('bola', None); ball.instance_type = 'COLLECTION'; ball.instance_collection = ballc; B.link(ball, kidC)
mins = [min((o.matrix_world @ Vector(c))[k] for o in ballc.objects if o.type == 'MESH' for c in o.bound_box) for k in range(3)]
maxs = [max((o.matrix_world @ Vector(c))[k] for o in ballc.objects if o.type == 'MESH' for c in o.bound_box) for k in range(3)]
ball_scale = 2 * S.BALL_R / max(maxs[k] - mins[k] for k in range(3)); ball_off = -(mins[2] + maxs[2]) / 2 * ball_scale
ball.scale = (ball_scale,) * 3; ball.rotation_mode = 'XYZ'
show_kid = shot.name not in ('F', 'G')
kidC.hide_render = not show_kid

cam = B.link(bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.05; cam.data.clip_end = 1500

# ---------------------------------------------------------------- faixas e rótulos
RC = B.new_coll('Marcacoes')
def strip(name, color, y, width=0.9, z=0.012, emit=0.35):
    m = B.mat_basic('Faixa_' + name, color, 0.6, emit=color, emit_s=emit)
    o = B.box(name, (1.0, width, 0.006), (0, y, z), m, RC); o.data.transform(__import__('mathutils').Matrix.Translation((0.5, 0, 0)))
    o.scale = (0.0001, 1, 1); return o
def bill(text, loc, size=0.9, color=(1, 1, 1)):
    r = B.label(text, loc, size, color, coll=RC, name='rot_' + text.replace(' ', '_'))
    c = r.constraints.new('TRACK_TO'); c.target = cam; c.track_axis = 'TRACK_Z'; c.up_axis = 'UP_Y'
    r.scale = (0.0001,) * 3; return r
YEL, RED, WHITE = (1.0, 0.78, 0.05), (0.95, 0.12, 0.08), (0.95, 0.95, 0.95)
items = {}
names = getattr(shot, 'strips', [])
if 'react_story' in names:
    items['react'] = strip('reacao', YEL, S.LANE_R); items['lbl25'] = bill('25 m', (-22.5, S.LANE_R, 2.4), 1.0, YEL)
if 'gap10' in names:
    items['gap'] = strip('sobra', RED, S.LANE_R); items['gap'].location.x = -10; items['lbl10'] = bill('10 m', (-5, S.LANE_R, 2.4), 1.0, RED)
if 'sim50' in names or 'sim60' in names:
    line = B.box('linha_perigo', (0.25, 7.0, 0.006), (S.X_HAZARD, 0, 0.012), B.mat_basic('LinhaPerigo', WHITE, 0.5, emit=WHITE, emit_s=0.6), RC)
    if shot.name == 'F': items['lblP'] = bill('PERIGO', (S.X_HAZARD, 0, 3.0), 1.1, WHITE)
    for lane, v, tag in ((S.LANE_L, S.V50, '50'), (S.LANE_R, S.V60, '60')):
        if f'sim{tag}' not in names: continue
        items[f'r{tag}'] = strip(f'reacao{tag}', YEL, lane); items[f'b{tag}'] = strip(f'frenagem{tag}', RED, lane)
        items[f'b{tag}'].location.x = S.X_HAZARD + v * S.REACT
        d = S.stop_dist(v); FS = 1.0 if shot.name == 'F' else 1.0
        if shot.name == 'F':
            items[f'lbl{tag}'] = bill(f'{d:.0f} m', (S.X_HAZARD + d + 1.0, lane, 4.2), 2.2, WHITE)
            items[f'tag{tag}'] = bill(f'{tag} km/h', (0, lane, 3.6), 1.5, (0.6, 0.85, 1.0) if tag == '50' else (1.0, 0.6, 0.5))

if 'gap10_after' in names:
    items['after'] = strip('dez_metros', RED, S.LANE_R - 1.25, width=0.35); items['lblA'] = bill('10 m', (5.0, S.LANE_R - 1.25, 2.2), 1.0, RED)

def pop(obj, T, t_on, base=1.0):
    k = S.sstep(t_on, t_on + 0.25, T); s = base * max(k, 0.0001) * (1 + 0.15 * math.sin(math.pi * min(k, 1)))
    obj.scale = (s, s, s)

# ---------------------------------------------------------------- animação
def gh(y):   # altura do chão: calçada/quintal 0,15 m, pista 0
    return 0.15 * S.sstep(3.50, 3.66, abs(y))

def place_car(car, xf, lane, braking, t_brake, t_stop_since):
    c = car['root']; c.location = (xf - S.FRONT, lane, 0.0)
    for w in car['wheels']: w.rotation_euler = (0, xf / S.WHEEL_R, 0)
    if braking: pitch = 0.032 * S.sstep(0, 0.2, t_brake)
    elif t_stop_since is not None: u = t_stop_since; pitch = 0.032 * math.exp(-4.5 * u) * math.cos(2 * math.pi * 1.4 * u)
    else: pitch = 0.0
    car['body'].rotation_euler = (0, pitch, 0); car['body'].location = (0.25 * math.sin(pitch), 0, -0.6 * abs(pitch))
    car['tail'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 7.0 if (braking or t_stop_since is not None) else 0.6

def car_state(tau, v0):
    xf, v = S.car_front(tau, v0); braking = S.REACT < tau < S.stop_tau(v0)
    since = (tau - S.stop_tau(v0)) if tau >= S.stop_tau(v0) else None
    return xf, braking, tau - S.REACT, since

def key_car(car, f):
    car['root'].keyframe_insert('location', frame=f); car['body'].keyframe_insert('rotation_euler', frame=f); car['body'].keyframe_insert('location', frame=f)
    for w in car['wheels']: w.keyframe_insert('rotation_euler', frame=f)
    car['tail'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

DIST = {}
def kid_dist(tau):
    """Distância percorrida pelo menino (para a fase da passada), integrada numericamente."""
    k = round(tau, 3)
    if k in DIST: return DIST[k]
    n = 200; t0 = S.KID_PATH[0][0]; s = 0.0; px, py = S.kid_xy(t0)
    for i in range(1, n + 1):
        t = t0 + (tau - t0) * i / n; x, y = S.kid_xy(t); s += math.hypot(x - px, y - py); px, py = x, y
    DIST[k] = s; return s

def anim_kid(tau, T, f, wave=0.0, idle_spot=None):
    r = kid['root']; P = {}
    if idle_spot:
        x, y, rz = idle_spot; z = gh(y); speed = 0.0; ph = 0.0
        r.location = (x, y, z); r.rotation_euler = (0, 0, rz)
        P['spine'] = (2 * math.sin(T * 1.7), 0, 0)
        P['head'] = (0, 25 * math.sin(T * 0.6) + 20, 0)
        P['upper_arm.L'] = (0, 0, -8); P['upper_arm.R'] = (-150 * wave, 0, 25 * wave + 8 * (1 - wave)); P['forearm.R'] = (-30 * wave * (1 + 0.4 * math.sin(T * 9)), 0, 0)
        B.pose(kid, frame=f, **P); r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f); return
    x, y = S.kid_xy(tau); x2, y2 = S.kid_xy(tau + 0.02); vx, vy = (x2 - x) / 0.02, (y2 - y) / 0.02
    speed = math.hypot(vx, vy); hop = S.kid_hop(tau)
    if tau < 1.55: rz = math.atan2(vy, vx) + math.pi / 2 if speed > 0.3 else math.pi
    else: rz = math.pi * (1 - S.sstep(1.55, 1.72, tau)) + math.radians(-20) * S.sstep(2.1, 2.6, tau) * 0
    if tau > 2.25: rz = math.pi - math.radians(30) * S.sstep(2.25, 2.8, tau)        # vira para a rua e vê o carro passar
    a = min(speed / 3.0, 1.0) if tau < 1.55 else 0.0
    ph = 2 * math.pi * kid_dist(tau) / 1.05
    bob = 0.035 * a * abs(math.sin(ph))
    r.location = (x, y, gh(y) + hop + bob); r.rotation_euler = (0, 0, rz)
    s_ = math.sin(ph)
    P = {'thigh.L': (-42 * a * s_, 0, 0), 'thigh.R': (42 * a * s_, 0, 0),
         'shin.L': (15 * a + 55 * a * max(0, math.sin(ph - 1.2)), 0, 0), 'shin.R': (15 * a + 55 * a * max(0, -math.sin(ph - 1.2)), 0, 0),
         'upper_arm.L': (38 * a * s_, 0, -8), 'upper_arm.R': (-38 * a * s_, 0, 8), 'forearm.L': (-65 * a, 0, 0), 'forearm.R': (-65 * a, 0, 0),
         'spine': (14 * a, 0, 0)}
    fright = S.sstep(0.85, 1.05, tau) * (1 - S.sstep(1.5, 1.6, tau))
    if fright > 0:   # parado no meio da rua: vira a cabeça para o carro, braços se erguem
        P['head'] = (0, 65 * fright, 0); P['spine'] = (-6 * fright, 0, 0)
        P['upper_arm.L'] = (-40 * fright, 0, -25 * fright); P['upper_arm.R'] = (-40 * fright, 0, 25 * fright)
        P['forearm.L'] = (-70 * fright, 0, 0); P['forearm.R'] = (-70 * fright, 0, 0)
    if 1.5 <= tau < 2.4:   # pulo para trás: agacha, impulsiona, aterrissa com amortecimento
        crouch = S.sstep(1.5, 1.56, tau) * (1 - S.sstep(1.56, 1.66, tau)) + S.sstep(1.95, 2.0, tau) * (1 - S.sstep(2.05, 2.35, tau))
        air = S.sstep(1.56, 1.62, tau) * (1 - S.sstep(1.93, 2.0, tau))
        P = {'thigh.L': (-55 * crouch - 35 * air, 0, 0), 'thigh.R': (-55 * crouch + 10 * air, 0, 0),
             'shin.L': (75 * crouch + 60 * air, 0, 0), 'shin.R': (75 * crouch + 25 * air, 0, 0), 'spine': (25 * crouch + 15 * air, 0, 0),
             'upper_arm.L': (60 * crouch - 120 * air, 0, -20), 'upper_arm.R': (60 * crouch - 120 * air, 0, 20), 'forearm.L': (-30, 0, 0), 'forearm.R': (-30, 0, 0),
             'head': (0, 0, 0)}
        r.location.z -= 0.12 * crouch
    if tau >= 2.4:
        k = S.sstep(2.4, 2.9, tau); xf = S.car_front(tau, S.V60)[0]
        look = max(-75, min(75, math.degrees(math.atan2(-(xf - 2 - x), 2.5)))) if True else 0
        P = {'head': (0, look * 0.8, 0), 'spine': (-4, 0, 0), 'upper_arm.L': (-10, 0, -10), 'upper_arm.R': (-10, 0, 10), 'forearm.L': (-20, 0, 0), 'forearm.R': (-20, 0, 0)}
    B.pose(kid, frame=f, **P)
    r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)

def anim_ball(tau, f, spot=None):
    if spot: x, y = spot; ball.location = (x, y, gh(y) + S.BALL_R + ball_off); ball.keyframe_insert('location', frame=f); ball.keyframe_insert('rotation_euler', frame=f); return
    x, y, _ = S.ball_xy(tau); s = y - (-8.5)
    drop = 0.0
    ball.location = (x, y, gh(y) + S.BALL_R + ball_off); ball.rotation_euler = (-s / S.BALL_R, 0, 0)
    ball.keyframe_insert('location', frame=f); ball.keyframe_insert('rotation_euler', frame=f)

def anim_driver(face, f, T, tau=None):
    d = teo['driver']; B.set_face(d, face, f)
    alarm = face.get('alarm', 0)
    B.pose(d, frame=f, sit=1.0, **{'head': (0, 6 * math.sin(T * 0.7) * (1 - alarm), 0), 'spine': (8 + 10 * alarm, 0, 0),
                                   'upper_arm.L': (-55 - 12 * alarm, 0, -8), 'upper_arm.R': (-55 - 12 * alarm, 0, 8)})

events = dict(shot=shot.name, fps=SH.FPS, frames=[])
fr = list(shot.frames)
for f in fr:
    T = f / SH.FPS; ev = dict(f=f, T=round(T, 4))
    if hasattr(shot, 'car'):
        xf, v = shot.car(T); place_car(teo, xf, S.LANE_R, False, 0, None); ev.update(car_x=xf, car_v=v, brake=0)
    elif shot.name in ('F', 'G'):
        tau60 = (T - shot.T60) if shot.name == 'F' else shot.tau60(T)
        tau50 = (T - shot.T50) if shot.name == 'F' else 99.0
        x60, br60, tb60, st60 = car_state(tau60, S.V60); place_car(teo, x60, S.LANE_R, br60, tb60, st60)
        x50, br50, tb50, st50 = car_state(tau50, S.V50); place_car(blue, x50, S.LANE_L, br50, tb50, st50); key_car(blue, f)
        ev.update(car_x=x60, car_v=S.car_front(tau60, S.V60)[1], brake=int(br60), car2_x=x50, car2_v=S.car_front(tau50, S.V50)[1], brake2=int(br50), tau=tau60)
        for tag, xx in (('50', x50), ('60', x60)):
            if f'r{tag}' in items:
                v0 = S.V50 if tag == '50' else S.V60; xr = S.X_HAZARD + v0 * S.REACT
                items[f'r{tag}'].location.x = S.X_HAZARD; items[f'r{tag}'].scale.x = max(min(xx, xr) - S.X_HAZARD, 0.0001)
                items[f'b{tag}'].scale.x = max(xx - xr, 0.0001)
                for k in (f'r{tag}', f'b{tag}'): items[k].keyframe_insert('scale', frame=f); items[k].keyframe_insert('location', frame=f)
                if shot.name == 'F':
                    stopT = (shot.T50 if tag == '50' else shot.T60) + S.stop_tau(v0)
                    pop(items[f'lbl{tag}'], T, stopT)
                    items[f'tag{tag}'].location = (xx - 2.0, S.LANE_L if tag == '50' else S.LANE_R, 3.6)
                    pop(items[f'tag{tag}'], T, 32.4)
                    for k in (f'lbl{tag}', f'tag{tag}'): items[k].keyframe_insert('scale', frame=f); items[k].keyframe_insert('location', frame=f)
        if 'lblP' in items: pop(items['lblP'], T, 32.0 if shot.name == 'F' else 0); items['lblP'].keyframe_insert('scale', frame=f)
        if 'lbl43' in items:
            items['lbl43'].location = (x60 - 2.0, S.LANE_R, 2.7); pop(items['lbl43'], T, 47.2)
            items['lbl43'].keyframe_insert('location', frame=f); items['lbl43'].keyframe_insert('scale', frame=f)
    else:
        tau = shot.tau(T); xf, br, tb, st = car_state(tau, S.V60); place_car(teo, xf, S.LANE_R, br, tb, st)
        ev.update(car_x=xf, car_v=S.car_front(tau, S.V60)[1], brake=int(br), tau=tau)
        if 'react' in items:
            items['react'].location.x = S.X_HAZARD; items['react'].scale.x = max(min(xf, -10.0) - S.X_HAZARD, 0.0001); items['react'].keyframe_insert('scale', frame=f)
            pop(items['lbl25'], T, 23.55 if shot.name == 'D2' else 0); items['lbl25'].keyframe_insert('scale', frame=f)
        if 'gap' in items:
            items['gap'].scale.x = 10.0 * S.sstep(26.25, 26.75, T) if shot.name == 'D2' else 10.0; items['gap'].keyframe_insert('scale', frame=f)
            pop(items['lbl10'], T, 26.3 if shot.name == 'D2' else 0); items['lbl10'].keyframe_insert('scale', frame=f)
        if 'after' in items:
            items['after'].location.x = 0.0; items['after'].scale.x = max(9.84 * S.sstep(57.75, 58.3, T), 0.0001); items['after'].keyframe_insert('scale', frame=f)
            pop(items['lblA'], T, 57.85); items['lblA'].keyframe_insert('scale', frame=f)
    key_car(teo, f)
    anim_driver(shot.face(T), f, T)
    if show_kid:
        if shot.name in ('A', 'B'):
            anim_kid(0, T, f, idle_spot=(-1.5, -9.5, math.pi)); anim_ball(0, f, spot=(-0.8, -9.2))
        elif shot.name == 'I':
            xf = shot.car(T)[0]; wave = S.sstep(-14, -6, xf) * (1 - S.sstep(4, 12, xf))
            anim_kid(0, T, f, wave=wave, idle_spot=(0.8, -4.7, math.pi + math.radians(25))); anim_ball(0, f, spot=(0.4, -4.45))
        else:
            tau = shot.tau(T); anim_kid(tau, T, f); anim_ball(tau, f)
            kx, ky = S.kid_xy(tau); ev.update(kid_x=kx, kid_y=ky, hop=S.kid_hop(tau), ball=S.ball_xy(tau)[1])
    c = shot.cam(T); cam.location = c['pos']; d = Vector(c['look']) - Vector(c['pos'])
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = c['lens']
    cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f); cam.data.keyframe_insert('lens', frame=f)
    events['frames'].append(ev)

# interpolação linear entre as chaves por quadro (o desfoque de movimento usa subquadros)
for ob in list(bpy.data.objects) + [cam.data] + list(bpy.data.materials) + list(bpy.data.armatures):
    ad = getattr(ob, 'animation_data', None) or (ob.node_tree.animation_data if hasattr(ob, 'node_tree') and ob.node_tree else None)
    for adx in [getattr(ob, 'animation_data', None)] + ([ob.node_tree.animation_data] if hasattr(ob, 'node_tree') and ob.node_tree else []):
        if adx and adx.action:
            for fc in adx.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

sc.frame_start, sc.frame_end = fr[0], fr[-1]; sc.frame_step = step
out = os.path.join(HERE, 'frames' if FINAL else 'preview', shot.name); os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(HERE, 'events'), exist_ok=True)
json.dump(events, open(os.path.join(HERE, 'events', f'{shot.name}.json'), 'w'))
print(f'[{shot.name}] cena pronta em {time.time() - t0:.1f}s; quadros {fr[0]}–{fr[-1]} ({len(fr)}), {W}x{H}, {spp} spp, passo {step}', flush=True)
if a.save_blend: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'build', f'{shot.name}.blend'))
if a.still is not None:
    sc.frame_set(a.still); sc.render.filepath = os.path.join(out, f'still_{a.still:04d}.png'); sc.render.use_overwrite = True
    bpy.ops.render.render(write_still=True)
else:
    if a.frames:
        f0, f1 = map(int, a.frames.split('-')); sc.frame_start, sc.frame_end = f0, f1
    sc.render.filepath = os.path.join(out, '####')
    t1 = time.time(); bpy.ops.render.render(animation=True)
    print(f'[{shot.name}] render {time.time() - t1:.1f}s', flush=True)
