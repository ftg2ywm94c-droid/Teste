"""PROVA DE CONCEITO EQUIVALENTE EM BLENDER (bpy) — *** NÃO TESTADO: não havia Blender no ambiente onde foi escrito ***
Rodar no notebook:  blender -b -P blender/poc_blender.py -- --out renders/blender_poc --res 540x960
Depois:  ffmpeg -framerate 30 -i renders/blender_poc/f_%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p poc_blender.mp4
Usa só API básica (primitivas, parent, keyframes, Track To) e funciona de 3.6 a 4.x; ajuste fino é esperado na 1ª execução."""
import bpy, sys, math
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
arg = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
OUT = arg('--out', '//renders/blender_poc'); RX, RY = map(int, arg('--res', '540x960').split('x'))
FPS, DUR = 30, 10; NF = FPS * DUR; V0, STRIDE = 1.283, 0.85
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = NF; sc.render.resolution_x, sc.render.resolution_y = RX, RY
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try: sc.render.engine = eng; break
    except TypeError: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = OUT + '/f_'
try: sc.view_settings.view_transform = 'Standard'
except Exception: pass

def mat(name, rgb, rough=0.6, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    if emit:
        for k in ('Emission Color', 'Emission'):
            if k in b.inputs: b.inputs[k].default_value = (*rgb, 1)
        b.inputs['Emission Strength'].default_value = emit
    return m
def add(kind, name, loc, scale, m, parent=None, rot=(0, 0, 0)):
    {'sph': lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24),
     'cube': bpy.ops.mesh.primitive_cube_add, 'cyl': lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=32)}[kind]()
    o = bpy.context.object; o.name = name; o.location = loc; o.scale = scale; o.rotation_euler = rot; o.data.materials.append(m)
    if kind != 'cube': bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; e.parent = parent; return e
def key(o, f, loc=None, rot=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)

# Blender: Z para cima. Rua ao longo de X; calçada em Y=-4 (equivale a z=+4 do renderizador próprio).
M = dict(skin=mat('skin', (1, .86, .66)), cap=mat('cap', (.95, .42, .10)), shirt=mat('shirt', (.10, .62, .60)), pants=mat('pants', (.16, .20, .42)),
         ink=mat('ink', (.03, .03, .04)), shoe=mat('shoe', (.93, .93, .95)), grass=mat('grass', (.30, .64, .18)), road=mat('road', (.22, .23, .27)),
         walk=mat('walk', (.62, .60, .55)), white=mat('white', (.95, .95, .95)), car=mat('car', (.93, .25, .42), .3), tire=mat('tire', (.05, .05, .06)),
         wall=mat('wall', (.98, .90, .82)), roof=mat('roof', (.75, .25, .20)), leaf=mat('leaf', (.20, .58, .20)), trunk=mat('trunk', (.42, .27, .16)),
         glass=mat('glass', (.10, .16, .26), .1), lamp=mat('lamp', (1, .96, .75), emit=2.0))
add('cube', 'grass', (0, 0, -.05), (120, 60, .05), M['grass']); add('cube', 'road', (0, 0, -.04), (120, 3, .05), M['road'])
for sy in (-4, 4): add('cube', 'walk', (0, sy, -.03), (120, 1, .05), M['walk'])
for k in range(7): add('cube', 'stripe', (0, -2.4 + k * .8, -.02), (1.3, .21, .04), M['white'])
for k, x in enumerate(range(-76, 40, 11)):
    for sy in (-1, 1):
        add('cube', 'house', (x, sy * 10.6, 1.5), (2.7, 2.2, 1.5), M['wall']); add('cube', 'roof', (x, sy * 10.6, 3.0), (2.95, 1.62, 1.0), M['roof'], rot=(math.pi / 4, 0, 0))
        add('cyl', 'trunk', (x + 5.3, sy * 7.5, .9), (.16, .16, .9), M['trunk']); add('sph', 'leaf', (x + 5.3, sy * 7.5, 2.4), (1.1, 1.1, 1.0), M['leaf'])

# --- personagem: hierarquia FK (root > hips > torso > head / braços / pernas). Sem armature: troca-se por rig com ossos na produção.
root = empty('teo_root', (-14, -4, 0)); hips = empty('hips', (0, 0, .55), root)
add('sph', 'torso', (0, 0, .28), (.195, .235, .31), M['shirt'], hips)
head = empty('head', (0, 0, .93), hips); add('sph', 'head_m', (0, 0, 0), (.40, .40, .40), M['skin'], head)
add('sph', 'cap', (0, 0, .13), (.405, .405, .30), M['cap'], head); add('sph', 'brim', (.36, 0, .2), (.19, .25, .03), M['cap'], head)
for s in (-1, 1): add('sph', 'eye', (.37, s * .11, .02), (.03, .035, .06), M['ink'], head)
limbs = {}
for s in (-1, 1):
    h = empty(f'hip{s}', (0, s * .10, 0), hips); add('cyl', 'leg', (0, 0, -.27), (.055, .055, .27), M['pants'], h); add('sph', 'shoe', (.05, 0, -.52), (.135, .075, .055), M['shoe'], h)
    a = empty(f'arm{s}', (0, s * .23, .43), hips); add('cyl', 'arm_m', (0, s * .04, -.2), (.048, .048, .2), M['shirt'], a); add('sph', 'hand', (0, s * .05, -.42), (.066,) * 3, M['skin'], a)
    limbs[s] = (h, a)
# --- carro
car = empty('car', (-80, -0.95, 0)); add('cube', 'body', (0, 0, .52), (1.72, .78, .26), M['car'], car); add('sph', 'cabin', (-.2, 0, .8), (1.05, .72, .56), M['glass'], car)
wheels = [add('cyl', 'wheel', (wx, wy, .34), (.34, .34, .13), M['tire'], car, rot=(math.pi / 2, 0, 0)) for wx in (1.12, -1.12) for wy in (.74, -.74)]
for s in (-1, 1): add('sph', 'hl', (1.74, s * .52, .58), (.08, .15, .11), M['lamp'], car)

# --- animação (mesma linha do tempo do renderizador próprio, simplificada: Téo em linha reta até x≈-2 e para)
def teo_x(t): return -14 + V0 * min(t, 7.2) + (V0 * (min(max(t - 7.2, 0), .9) - min(max(t - 7.2, 0), .9) ** 2 / 1.8))
def car_x(t):
    if t < 6.9: return -4.1 - 7.0 - 10 * (6.9 - t)
    if t < 8.3: u = t - 6.9; v = 10 * (1 - u / 1.4); return -4.1 - v * (1.4 - u) / 2
    return -4.1
for f in range(1, NF + 1):
    t = (f - 1) / FPS; x = teo_x(t); ph = 2 * math.pi * (x + 14) / STRIDE; w = 1.0 if t < 7.4 else max(0, 1 - (t - 7.4) / .7)
    hop = .16 * max(0, math.sin(math.pi * (t - 7.55) / .38)) if 7.55 < t < 7.93 else 0
    key(root, f, loc=(x, -4, hop)); key(hips, f, loc=(0, 0, .53 + .028 * math.sin(ph) ** 2 * w))
    for s in (-1, 1):
        h, a = limbs[s]; key(h, f, rot=(0, -.55 * math.cos(ph) * s * w, 0))
        sc_ = 1 if 7.6 < t < 8.8 else 0
        key(a, f, rot=(s * -2.3 * sc_, .7 * math.cos(ph) * s * w, 0))
    key(head, f, rot=(0, 0, .6 if t > 7.3 else 0))
    cx = car_x(t); key(car, f, loc=(cx, -0.95, 0))
    for wobj in wheels: key(wobj, f, rot=(math.pi / 2, cx / .34, 0))
# --- câmera tracking com Track To + 2 cortes (markers)
tgt = empty('cam_target', (0, 0, 1.1), root)
def cam(name, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(c); c.data.lens = lens; c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 36
    k = c.constraints.new('TRACK_TO'); k.target = tgt; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; return c
c1 = cam('cam_S1', 32); c1.parent = root; key(c1, 1, loc=(6.6, 2.5, 1.75)); key(c1, 150, loc=(3.1, 1.7, 1.30))
c2 = cam('cam_S2', 36); key(c2, 151, loc=(3.6, -4.9, 1.45)); key(c2, 228, loc=(2.5, -5.15, 1.6))
c3 = cam('cam_S3', 50); key(c3, 229, loc=(-2.2, 2.8, 1.2)); key(c3, 300, loc=(-3.0, 2.3, 1.45))
for fr_, c in ((1, c1), (151, c2), (229, c3)):
    mk = sc.timeline_markers.new(c.name, frame=fr_); mk.camera = c
sc.camera = c1
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 4.0; sun.data.angle = math.radians(3)
sun.rotation_euler = (math.radians(50), 0, math.radians(150))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (.35, .58, .95, 1); bg.inputs[1].default_value = 1.0
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath('//poc_blender.blend'))
bpy.ops.render.render(animation=True)
