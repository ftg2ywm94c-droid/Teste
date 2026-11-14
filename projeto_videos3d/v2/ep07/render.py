"""Vídeo 07: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep07/render.py -- --shot C1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep07/frames/<plano>/NNNN.png (final) ou v2/ep07/preview/<plano>/ (prévia). Retomável."""
import bpy, sys, os, math, json, time, argparse, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import build as B
import scene as SC
import plan as P
from story import sstep
from mathutils import Vector, Matrix, Euler

ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--mode', default='preview')
ap.add_argument('--spp', type=int); ap.add_argument('--step', type=int); ap.add_argument('--frames'); ap.add_argument('--still', type=int)
ap.add_argument('--save-blend', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
shot = P.BY_NAME[a.shot]; FINAL = a.mode == 'final'; K = shot.kind
W, H = (720, 1280) if FINAL else (270, 480)
if os.environ.get('PREVIEW_RES'): W, H = map(int, os.environ['PREVIEW_RES'].split('x'))
spp = a.spp or (8 if FINAL else 5); step = a.step or (1 if FINAL else 3)

bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
sc = bpy.context.scene; sc.world = bpy.data.worlds.new('tmp')
B.setup_render(W, H, spp, preview=not FINAL)
sc.cycles.use_light_tree = False          # teste de desempenho de 2026-11-13 (v2/DESEMPENHO.md): 2–3× mais rápido, sem diferença visível
if K not in ('rua', 'paulista', 'relevo'):
    for n in sc.node_tree.nodes:
        if n.bl_idname == 'CompositorNodeMath': n.inputs[1].default_value = 0.0
cam = B.link(bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.02; cam.data.clip_end = 60000
RC = B.new_coll('Rotulos3D')
FONT = bpy.data.fonts.load(B.FONT, check_existing=True)
ADV = json.load(open(os.path.join(HERE, 'poppins_widths.json')))

# ------------------------------------------------------------------ texto e rótulos (com subscrito "₂" montado à mão: a Poppins não tem o glifo)
def txt(name, body, size, color, parent=None, loc=(0, 0, 0), align='CENTER', emit=1.2, coll=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = FONT; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    o = B.link(bpy.data.objects.new(name, cu), coll or RC); o.parent = parent; o.location = loc
    o.data.materials.append(B.mat_basic('Txt_%.2f%.2f%.2f' % color, color, 0.5, emit=color, emit_s=emit)); o.visible_shadow = False
    return o

def rich(name, text, size, color, parent, loc=(0, 0, 0), emit=1.2):
    """Texto centrado em loc; '₂' vira um '2' menor e rebaixado. Devolve (lista de objetos, largura)."""
    parts = []; cur = ''
    for ch in text:
        if ch == '₂':
            if cur: parts.append((cur, False)); cur = ''
            parts.append(('2', True))
        else: cur += ch
    if cur: parts.append((cur, False))
    objs = []; x = 0.0
    for i, (s, sub) in enumerate(parts):
        sz = size * (0.62 if sub else 1.0)
        o = txt(f'{name}_{i}', s, sz, color, parent, (0, 0, 0), 'LEFT', emit)
        w = text_width(o)                                       # largura real da geometria do texto
        lead = (len(s) - len(s.lstrip(' '))) * 0.27 * sz
        objs.append((o, x + (lead if False else 0), sub)); x += w + (size * 0.03 if sub else 0)
    for o, xo, sub in objs: o.location = (loc[0] - x / 2 + xo, loc[1] + (-size * 0.22 if sub else 0), loc[2])
    return [o for o, _, _ in objs], x

def text_width(o):
    if not o.data.body.strip(): return 0.3 * o.data.size * len(o.data.body)
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh()
    xs = [v.co.x for v in me.vertices]; ev.to_mesh_clear()
    w = (max(xs) - min(xs)) if xs else 0.0
    trail = len(o.data.body) - len(o.data.body.rstrip(' ')); lead = len(o.data.body) - len(o.data.body.lstrip(' '))
    return w + (trail + lead) * 0.27 * o.data.size + 0.06 * o.data.size

LBL_FAC = {}
def bill(key, text, loc, size, color):
    fac = 1.0
    if size < 0.2: fac = size / 0.5; size = 0.5
    LBL_FAC[key] = fac
    root = B.link(bpy.data.objects.new('rot_' + key, None), RC); root.location = loc
    objs, w = rich('rot_' + key, text, size, color, root, (0, 0, 0.02))
    for o in objs: o.data.extrude = 0.01
    pl = B.box('rot_' + key + '_placa', (w + size * 0.9, size * 1.35, 0.02), (0, 0, 0), B.mat_basic('RotuloFundo', (0.05, 0.05, 0.06), 0.6), RC, bevel=size * 0.3, seg=4)
    pl.parent = root; pl.visible_shadow = False
    c = root.constraints.new('COPY_ROTATION'); c.target = cam
    root.scale = (0.0001,) * 3; return root

def pop_scale(T, t_on, t_off=99):
    k = sstep(t_on, t_on + 0.25, T) * (1 - sstep(t_off, t_off + 0.2, T))
    return max(k, 0.0001) * (1 + 0.15 * math.sin(math.pi * min(sstep(t_on, t_on + 0.25, T), 1)))

def key(o, *props, f):
    for p in props: o.keyframe_insert(p, frame=f)

def look_rot(pos, look, up=(0, 0, 1)):
    z = (Vector(pos) - Vector(look)).normalized(); u = Vector(up)
    x = u.cross(z)
    if x.length < 1e-6: x = Vector((1, 0, 0))
    x.normalize(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_euler()

def set_input(mat, node, inp, v, f):
    n = mat.node_tree.nodes[node]; n.inputs[inp].default_value = v; n.inputs[inp].keyframe_insert('default_value', frame=f)

DYN = []          # textos que mudam com o tempo: (objeto, função T -> texto). Viram cópias ligadas/desligadas por escala
def dyn_text(o, fn): DYN.append((o, fn))   # (trocar o texto num handler não funciona com dados persistentes do Cycles)
def bake_dyn(frames):
    for o, fn in DYN:
        copies = {}
        for f in frames:
            b = fn(f / P.FPS)
            if b not in copies:
                c = o.copy(); c.data = o.data.copy(); c.data.body = b; RC.objects.link(c); copies[b] = c
        o.scale = (1e-4,) * 3; o.keyframe_insert('scale', frame=frames[0])
        for f in frames:
            b = fn(f / P.FPS)
            for txt_, c in copies.items():
                c.scale = (1.0,) * 3 if txt_ == b else (1e-4,) * 3; c.keyframe_insert('scale', frame=f)


items = {}; events = dict(shot=shot.name, fps=P.FPS, frames=[])
C7 = B.new_coll('Ep07')
def mist_look(color, mul, start, depth):
    for n in sc.node_tree.nodes:
        if n.bl_idname == 'CompositorNodeMixRGB': n.inputs[2].default_value = (*color, 1)
        if n.bl_idname == 'CompositorNodeMath': n.inputs[1].default_value = mul
    ms = sc.world.mist_settings; ms.start = start; ms.depth = depth; ms.falloff = 'QUADRATIC'
# ================================================================== cenários
if K == 'paulista':
    items.update(SC.build_paulista())
    mist_look((0.30, 0.33, 0.37), 0.55, 30, 260); sc.view_settings.exposure = 0.7
elif K == 'rua':
    R = SC.build_cidade(abandoned=False); items.update(R); SC.storm_world((0.05, 0.055, 0.065), (0.2, 0.21, 0.23))
    sun_ = bpy.data.objects['Sol']; sun_.data.energy = 1.0; sun_.data.color = (0.8, 0.85, 0.95)
    R['car']['coll'].hide_render = True
    for fl in [R['candle']] + R['gas']: fl['root'].scale = (1e-4,) * 3; fl['light'].data.energy = 0.0
    mist_look((0.32, 0.34, 0.38), 0.45, 20, 160)
elif K == 'globo':
    items.update(SC.build_globo7(*shot.hur, size=shot.hur_size))
    if getattr(shot, 'no_pin', False):
        for o in [items['pin']] + list(items['pin'].children_recursive): o.hide_render = True
elif K == 'relevo':
    items.update(SC.build_relevo())
    mist_look((0.6, 0.66, 0.75), 0.12, 120, 600)
if K in ('paulista', 'rua'):
    items['gusts'] = SC.build_gusts(C7)
    if getattr(shot, 'rain', 0): items['rain'] = SC.build_rain(cam, n=int(420 * shot.rain))
    if hasattr(shot, 'debris'): items['debris'] = SC.build_debris(C7, kinds=('placa', 'vidro', 'galho') if K == 'paulista' else ('placa', 'galho'))
    if hasattr(shot, 'arrows'): items['arrows'] = SC.build_arrows(C7)
    if K == 'paulista' and (hasattr(shot, 'tree') or getattr(shot, 'tree_down', False)): items['ftree'] = SC.falling_tree(C7, P.TREE)
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
    if not hasattr(shot, 'teo'):
        for o in teo['root'].children_recursive + [teo['root']]: o.hide_render = True
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)

# ------------------------------------------------------------------ painéis presos à câmera
PANEL_S = dict(speed=0.8, compare=0.9, forca=0.9); PANEL_Y = dict(speed=1.75, compare=-1.55, forca=-1.55)
def panel_root(name, y):
    g = B.link(bpy.data.objects.new(name, None), RC); g.parent = cam; g.location = (0.0, y, -5.0); g.scale = (1e-4,) * 3; return g
def plate(g, w, h, alpha=0.86):
    p = B.box(g.name + '_placa', (w, h, 0.01), (0, 0, -0.02), B.mat_basic('PainelFundo', (0.03, 0.035, 0.05), 0.6, alpha=alpha), RC, bevel=0.08)
    p.parent = g; p.visible_shadow = False; return p
def lbar(name, w, h, col, g, loc):
    """Barra com origem na borda esquerda (para crescer em X)."""
    o = B.box(name, (w, h, 0.01), (0, 0, 0), SC.emit_mat('Barra_' + name, col, 1.3), RC)
    for v in o.data.vertices: v.co.x += w / 2
    o.parent = g; o.location = loc; o.visible_shadow = False; o.scale = (1e-4, 1, 1); return o
def hide(o): o.scale = (1e-4,) * 3
if shot.panel:
    kind = shot.panel[0]
    if kind == 'speed':
        g = panel_root('velocidade', 1.75); plate(g, 2.3, 0.85)
        txt('tit_vel', 'vento', 0.09, (0.8, 0.85, 0.95), g, (0, 0.27, 0.02))
        if shot.panel[4] == 'up':
            t1, t2 = shot.panel[3]; rd = txt('leitura_vel', '0 km/h', 0.3, P.RED, g, (0, -0.06, 0.02))
            dyn_text(rd, lambda T: f'{int(round(250 * sstep(t1, t2, T) / 5) * 5)} km/h')
        else:
            txt('leitura_vel', '250 km/h', 0.3, P.RED, g, (0, -0.06, 0.02))
            st = B.box('risco', (1.9, 0.07, 0.01), (0, 0, 0), SC.emit_mat('Risco', (1, 1, 1), 2.0), RC)
            for v in st.data.vertices: v.co.x += 0.95
            st.parent = g; st.location = (-0.95, -0.06, 0.04); st.rotation_euler = (0, 0, math.radians(-8)); st.scale = (1e-4, 1, 1); items['strike'] = st
        items['panel'] = g
    elif kind == 'compare':
        g = panel_root('comparacao', -1.55); plate(g, 2.9, 1.45)
        txt('tit_cmp', 'velocidade do vento', 0.1, (1, 1, 1), g, (0, 0.55, 0.02))
        txt('r1', '2023 em São Paulo', 0.075, (0.8, 0.82, 0.88), g, (-1.25, 0.28, 0.02), 'LEFT')
        txt('r2', 'furacão categoria 5', 0.075, (1.0, 0.6, 0.55), g, (-1.25, -0.2, 0.02), 'LEFT')
        b1 = lbar('b104', 2.3 * 104 / 252, 0.17, (0.75, 0.78, 0.85), g, (-1.25, 0.1, 0.02)); b2 = lbar('b252', 2.3, 0.17, P.RED, g, (-1.25, -0.38, 0.02))
        v1 = txt('v104', '104 km/h', 0.09, (1, 1, 1), g, (-1.25 + 2.3 * 104 / 252 + 0.08, 0.1, 0.03), 'LEFT'); v2 = txt('v252', '252 km/h', 0.09, (1, 1, 1), g, (0.92, -0.38, 0.03), 'RIGHT')
        tag = txt('tag_dobro', 'mais que o dobro', 0.1, P.YEL, g, (0, -0.6, 0.02))
        for o in (v1, v2, tag): hide(o)
        items.update(cmp=(b1, b2, v1, v2, tag)); items['panel'] = g
    elif kind == 'forca':
        g = panel_root('forca', -1.55); plate(g, 2.9, 1.6)
        txt('tit_f', 'força do vento numa parede', 0.095, (1, 1, 1), g, (0, 0.63, 0.02))
        txt('sub_f', 'cresce com o quadrado da velocidade', 0.065, (0.75, 0.78, 0.85), g, (0, 0.5, 0.02))
        txt('vel1', 'vento 1x', 0.085, (0.8, 0.82, 0.88), g, (-0.75, 0.3, 0.02)); vel2 = txt('vel2', 'vento 2x', 0.085, P.YEL, g, (0.65, 0.3, 0.02))
        bm_ = SC.emit_mat('Bloco', (1.0, 0.35, 0.2), 1.2); S_ = 0.3
        b0 = B.box('bloco0', (S_, S_, 0.01), (-0.75, -0.12, 0.02), bm_, RC); b0.parent = g
        blocks = []
        for i, (dx, dy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
            o = B.box(f'bloco{i + 1}', (S_, S_, 0.01), (0.65 + dx * (S_ / 2 + 0.02), -0.12 + dy * (S_ / 2 + 0.02), 0.02), bm_, RC); o.parent = g; hide(o); blocks.append(o)
        f1 = txt('f1', 'força 1x', 0.085, (1, 1, 1), g, (-0.75, -0.55, 0.02)); f4 = txt('f4', 'força 4x', 0.11, P.RED, g, (0.65, -0.55, 0.02))
        hide(vel2); hide(f4); items.update(fz=(vel2, blocks, f4)); items['panel'] = g

# ================================================================== Téo
def teo_anim(mode, teo, f, T):
    r = teo['root']; lt = T - shot.t0; r.location = getattr(shot, 'teo_pos', P.TEO); r.rotation_euler = (0, 0, math.radians(float(os.environ.get('TEO_ROT', '-155'))))
    if mode == 'look_up':
        k = sstep(0.2, 0.8, lt); g = math.sin(T * 7) * 0.5
        B.pose(teo, frame=f, spine=(-4 * k, 0, 0), head=(-26 * k, 0, 6 * math.sin(T * 0.9)),
               **{'upper_arm.L': (-55 * k, 0, -10), 'upper_arm.R': (-20 * k, 0, 18 * k), 'forearm.L': (-95 * k + 4 * g, 0, 0), 'forearm.R': (-30 * k, 0, 0)})
        B.set_face(teo, {'alarm': k, 'neutral': 1 - k}, f)

# ================================================================== animação quadro a quadro
def shake(T, a):
    return Vector((math.sin(T * 37.0) + 0.5 * math.sin(T * 71.0), math.sin(T * 29.0 + 1.0), math.sin(T * 43.0 + 2.0) * 0.6)) * 0.045 * a
fr = list(shot.frames)
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4)); lt = T - shot.t0; u_ = lt / (shot.t1 - shot.t0)
    c = shot.cam(T); cpos = Vector(c['pos'])
    if K in ('paulista', 'rua'):
        wind = getattr(shot, 'wind', 0.0)
        SC.gust_pose(items['gusts'], T, f, 18 + 28 * wind, span=(cpos.x - 20, cpos.x + 120), vis=wind)
        if 'rain' in items: SC.rain_pose(items['rain'], T, f, slant=0.2 + 0.45 * wind)
        if 'debris' in items: SC.debris_pose(items['debris'], T, shot.debris, f, speed=10 + 18 * wind)
        if 'arrows' in items: SC.arrows_pose(items['arrows'], T, f, vis=pop_scale(T, shot.arrows))
        if 'ftree' in items:
            k = 1.0 if getattr(shot, 'tree_down', False) else sstep(shot.tree, shot.tree + 0.75, T) ** 1.6
            items['ftree'].rotation_euler.x = -math.radians(84 * k); key(items['ftree'], 'rotation_euler', f=f)
        if hasattr(shot, 'teo'): teo_anim(shot.teo, items['teo'], f, T); key(items['teo']['root'], 'location', 'rotation_euler', f=f)
        if K == 'paulista':
            lv = 0.0 if getattr(shot, 'lights_off', False) else (1 - sstep(shot.blackout, shot.blackout + 0.15, T) if hasattr(shot, 'blackout') else 1.0)
            SC.set_lights(lv, f)
            e = 0.0
            for tf in getattr(shot, 'flash', ()): e += math.exp(-((T - tf) / 0.07) ** 2) + 0.5 * math.exp(-((T - tf - 0.18) / 0.05) ** 2)
            items['flash'].energy = 4.0e6 * e; items['flash'].keyframe_insert('energy', frame=f)
        cpos = cpos + shake(T, getattr(shot, 'shake', 0.0))
    elif K == 'globo':
        h = items['hurricane']; h.rotation_euler = (0, 0, -0.9 * T); key(h, 'rotation_euler', f=f)
        SC.set_mat_value(items['hmat'], 'Giro', -0.9 * T, f)
    elif K == 'relevo':
        h = items['hurricane']; x0, x1 = shot.hur_x; x = x0 + (x1 - x0) * (sstep(shot.t0, shot.t1, T) if x1 != x0 else 0)
        wk = sstep(*shot.weaken, T) if hasattr(shot, 'weaken') else 0.0
        h.location = (x, 0.0, 8.5 - 1.5 * wk); s_ = 18.0 * (1 - 0.45 * wk); h.scale = (s_, s_, s_ * 0.2); h.rotation_euler = (0, 0, -0.9 * T)
        key(h, 'location', 'scale', 'rotation_euler', f=f); SC.set_mat_value(items['hmat'], 'Forca', 1.5 - 1.1 * wk, f)
        if hasattr(shot, 'dim'):
            d0, d1 = shot.dim; k = 1.0 if d1 <= d0 else sstep(d0, d1, T)
            items['dim'].scale = (max(k, 1e-4), 1, 1); items['dim'].location.x = 30.0 * k; key(items['dim'], 'scale', 'location', f=f)
        else:
            items['dim'].scale = (1e-4, 1, 1); key(items['dim'], 'scale', f=f)
            for o in items['ticks']: hide(o); key(o, 'scale', f=f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    cam.location = cpos; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    if shot.panel:
        kind = shot.panel[0]; L = 35.0 / c['lens']; g = items['panel']
        s = PANEL_S[kind] * L * pop_scale(T, shot.panel[1], shot.panel[2]) / 5
        g.scale = (s,) * 3; g.location = (0.0, PANEL_Y[kind] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if kind == 'speed' and 'strike' in items:
            k = sstep(shot.panel[5], shot.panel[5] + 0.3, T); items['strike'].scale = (max(k, 1e-4), 1, 1); key(items['strike'], 'scale', f=f)
        if kind == 'compare':
            t1, t2 = shot.panel[3]; b1, b2, v1, v2, tag = items['cmp']; tm = (t1 + t2) / 2
            k1 = sstep(t1, tm, T); k2 = sstep(tm, t2, T)
            b1.scale = (max(k1, 1e-4), 1, 1); b2.scale = (max(k2, 1e-4), 1, 1)
            for o, ton in ((v1, tm), (v2, t2), (tag, 21.80)): o.scale = (pop_scale(T, ton),) * 3; key(o, 'scale', f=f)
            key(b1, 'scale', f=f); key(b2, 'scale', f=f)
        if kind == 'forca':
            t1, t2 = shot.panel[3]; vel2, blocks, f4 = items['fz']
            vel2.scale = (pop_scale(T, t1),) * 3; key(vel2, 'scale', f=f)
            for i, o in enumerate(blocks): o.scale = (pop_scale(T, t2 - 0.6 + 0.2 * i),) * 3; key(o, 'scale', f=f)
            f4.scale = (pop_scale(T, t2 + 0.2),) * 3; key(f4, 'scale', f=f)
    ev['cam'] = [round(x, 3) for x in c['pos']]; events['frames'].append(ev)
bake_dyn(fr)

def all_ads():
    for ob in list(bpy.data.objects) + [cam.data] + list(bpy.data.curves) + list(bpy.data.armatures) + list(bpy.data.lights):
        if getattr(ob, 'animation_data', None) and ob.animation_data.action: yield ob.animation_data
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action: yield m.node_tree.animation_data
for ad in all_ads():
    for fc in ad.action.fcurves:
        if fc.modifiers: continue                      # curvas com ruído (moléculas, chamas) ficam como estão
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if ('hide' in fc.data_path or (fc.id_data.name.startswith(('leitura', 'leg')) and fc.data_path == 'scale')) else 'LINEAR'
fcs = [fc for fc in (cam.animation_data.action.fcurves if cam.animation_data else []) if fc.data_path == 'rotation_euler']
for fc in fcs:
    pts = fc.keyframe_points
    for i in range(1, len(pts)):
        d = pts[i].co[1] - pts[i - 1].co[1]
        while d > math.pi: pts[i].co[1] -= 2 * math.pi; d -= 2 * math.pi
        while d < -math.pi: pts[i].co[1] += 2 * math.pi; d += 2 * math.pi
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
