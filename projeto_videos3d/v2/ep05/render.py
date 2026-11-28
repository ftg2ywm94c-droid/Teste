"""Vídeo 04: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep05/render.py -- --shot C1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep05/frames/<plano>/NNNN.png (final) ou v2/ep05/preview/<plano>/ (prévia). Retomável."""
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
if K != 'rua':
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
# ================================================================== cenários
if K == 'rua':
    R = SC.build_rua(); items.update(R)
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
    car = R['car']; car['coll'].hide_render = not hasattr(shot, 'car')
    if hasattr(shot, 'car'): car['root'].location = shot.car(shot.t0)[:3]
    flames = [R['candle']] + R['gas']
    for i, fl in enumerate(flames): SC.flicker(fl['obj'], 0.10, 4.0, i)
    out_t = getattr(shot, 'fire_out', None)
    if out_t == 0.0 or (out_t is None and shot.t0 > P.T_FOGO):
        for fl in flames: fl['root'].scale = (0.0001,) * 3; fl['light'].data.energy = 0.0
    if hasattr(shot, 'wisp'):
        cu = bpy.data.curves.new('fio_fumaca', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0008; cu.bevel_resolution = 3
        sp = cu.splines.new('POLY'); sp.points.add(23); wo = B.link(bpy.data.objects.new('fio_fumaca', cu), RC); wo.visible_shadow = False
        m_, nb_ = SC.new_mat('FioFumaca'); o_ = nb_.n('ShaderNodeOutputMaterial'); tr_ = nb_.n('ShaderNodeBsdfTransparent'); df_ = nb_.n('ShaderNodeBsdfDiffuse')
        df_.inputs[0].default_value = (0.8, 0.8, 0.82, 1); mx_ = nb_.n('ShaderNodeMixShader'); mx_.inputs[0].default_value = 0.1
        nb_.link(tr_.outputs[0], mx_.inputs[1]); nb_.link(df_.outputs[0], mx_.inputs[2]); nb_.link(mx_.outputs[0], o_.inputs[0]); cu.materials.append(m_)
        items['wisp'] = sp
    if hasattr(shot, 'crumble') or getattr(shot, 'crumbled', False):
        CC = B.new_coll('Entulho'); items['chunks'] = SC.build_chunks(CC); items['bld'] = SC.building_objects()
        if getattr(shot, 'crumbled', False):
            for o in items['bld']: bpy.data.objects.remove(o)
            for c in items['chunks']:
                p_, r_, s_ = SC.chunk_state(c, 999.0, 0.0); c['obj'].location = p_; c['obj'].rotation_euler = r_; c['obj'].scale = (s_,) * 3
            items['chunks'] = None
        else:
            items['dust'] = SC.dust_puffs(CC)
    if getattr(shot, 'no_teo', False):
        for o in teo['root'].children_recursive + [teo['root']]: o.hide_render = True
    if hasattr(shot, 'fade'):
        fm = set()
        for o in teo['root'].children_recursive:
            if o.type == 'MESH':
                for m in o.data.materials:
                    if m: fm.add(m)
        items['fade'] = []
        for m in fm:
            nt = m.node_tree; outn = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'][0]
            lk = outn.inputs['Surface'].links[0]; src = lk.from_socket; nt.links.remove(lk)
            tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.name = 'Sumir'
            nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], outn.inputs['Surface'])
            items['fade'].append(m)
    if hasattr(shot, 'loose'): items['loose'] = SC.loose_O(RC, shot.loose[3], shot.loose[1], shot.loose[2], r_=shot.loose[4])
    if hasattr(shot, 'o2back'):
        pO = SC.molecule_proto('O2', SC.O2_COL, glow=1.2); r = random.Random(5); items['back'] = []
        for i in range(70):
            o = bpy.data.objects.new(f'o2volta{i}', None); o.instance_type = 'COLLECTION'; o.instance_collection = pO; B.link(o, RC)
            o.location = (P.TEO[0] + r.uniform(-6, 6), P.TEO[1] + r.uniform(-1.2, 2), r.uniform(0.6, 3.2)); o.rotation_euler = (r.uniform(0, 6), r.uniform(0, 6), r.uniform(0, 6))
            items['back'].append((o, r.uniform(0, 0.4), r.uniform(0.10, 0.15)))
elif K == 'mol':
    items['mols'] = SC.build_molecules()
elif K == 'cristal':
    items.update(SC.build_cristal5())
    if hasattr(shot, 'loose'): items['loose'] = SC.loose_O(RC, shot.loose[3], shot.loose[1], shot.loose[2], r_=shot.loose[4])
elif K == 'agua':
    items['agua'] = SC.build_agua()
    if hasattr(shot, 'loose'): items['loose'] = SC.loose_O(RC, shot.loose[3], shot.loose[1], shot.loose[2], r_=shot.loose[4])
elif K == 'mar':
    items.update(SC.build_mar())
elif K == 'terra':
    items['earth'] = SC.build_terra()
ms = sc.world.mist_settings; ms.start = 60; ms.depth = 260; ms.falloff = 'QUADRATIC'
# desempenho: emissivos não iluminam a cena (luzes reais fazem esse papel)
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)

# ------------------------------------------------------------------ painéis presos à câmera
PANEL_S = dict(pie=0.8, pie46=0.8, body=0.8, gauge=0.8, alt=1.0); PANEL_Y = dict(pie=-1.75, pie46=-1.75, body=-1.75, gauge=-1.75, alt=1.85)
def panel_root(name, y):
    g = B.link(bpy.data.objects.new(name, None), RC); g.parent = cam; g.location = (0.0, y, -5.0); g.scale = (1e-4,) * 3; return g
def plate(g, w, h, alpha=0.84):
    p = B.box(g.name + '_placa', (w, h, 0.01), (0, 0, -0.02), B.mat_basic('PainelFundo', (0.03, 0.035, 0.05), 0.6, alpha=alpha), RC, bevel=0.08)
    p.parent = g; p.visible_shadow = False; return p
def sector(name, a0, a1, r, col, g, z=0.0, emit=1.6):
    n = max(int(abs(a1 - a0) / 4) + 2, 3); vs = [(0, 0, z)] + [(r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))), r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1))), z) for i in range(n)]
    o = SC.mesh_from(name, vs, [(0, i, i + 1) for i in range(1, n)], SC.emit_mat('Fatia_' + name, col, 0.9), RC)
    o.parent = g; o.visible_shadow = False; return o

if shot.panel:
    kind = shot.panel[0]; t_on = shot.panel[1]
    if kind in ('pie', 'pie46', 'body'):
        g = panel_root('pizza', -2.05); plate(g, 2.6, 1.45)
        if kind == 'pie':
            segs = [('N2', 0.78, SC.N2_COL), ('O2', 0.21, SC.O2_COL), ('Ar', 0.01, (0.7, 0.7, 0.72))]
            leg = [('N₂ 78%', SC.N2_COL), ('O₂ 21%', SC.O2_COL), ('argônio 1%', (0.75, 0.75, 0.78))]
        elif kind == 'body':
            segs = [('O', 0.65, SC.O2_COL), ('resto', 0.35, (0.5, 0.52, 0.56))]
            leg = [('oxigênio 65%', SC.O2_COL), ('o resto 35%', (0.75, 0.75, 0.78))]
        else:
            segs = [('O', 0.46, SC.O2_COL), ('Si', 0.28, (0.80, 0.72, 0.52)), ('outros', 0.26, (0.5, 0.52, 0.56))]
            leg = [('oxigênio 46%', SC.O2_COL), ('silício 28%', (0.85, 0.78, 0.6)), ('outros 26%', (0.75, 0.75, 0.78))]
        a0 = 90.0; sec = {}
        for nm, fr_, col in segs:
            o = sector('fatia_' + nm, a0, a0 - 360 * fr_, 0.52, col, g); o.location = (-0.62, 0.0, 0.0); sec[nm] = o; a0 -= 360 * fr_
        texts = []
        for i, (t, col) in enumerate(leg):
            objs, w = rich(f'leg{i}', t, 0.2, col, g, (0, 0, 0.01))
            for o in objs: o.location.x += 0.42 + w / 2; o.location.y += 0.36 - 0.36 * i
            texts.append(objs)
        if kind == 'pie46':
            tt, w = rich('tit46', 'crosta da Terra (massa)', 0.13, (1, 1, 1), g, (0, 0.58, 0.01))
        if kind == 'body':
            tt, w = rich('titcorpo', 'seu corpo (massa)', 0.13, (1, 1, 1), g, (0, 0.58, 0.01))
            for o in texts[1]: o.location.y -= 0.18
        items['pie'] = (g, sec, texts)
    elif kind == 'gauge':
        g = panel_root('medidor', -2.0); plate(g, 1.9, 1.55)
        ring = B.cyl('mostrador', 0.6, 0.01, (0, -0.05, 0), B.mat_basic('Mostrador', (0.92, 0.92, 0.9), 0.4), RC, seg=64)
        ring.parent = g
        def ang(kpa): return math.radians(120 - (kpa - 70) / 40 * 240)
        for kpa in range(70, 111, 5):
            t_ = B.box('tick', (0.012, 0.07 if kpa % 10 else 0.11, 0.004), (0, 0, 0.01), B.mat_basic('Tick', (0.1, 0.1, 0.12), 0.5), RC)
            t_.parent = g; aa = ang(kpa); t_.location = (0.5 * math.sin(-aa + math.pi), 0, 0); t_.location = (0.5 * math.cos(aa + math.pi / 2), -0.05 + 0.5 * math.sin(aa + math.pi / 2), 0.012)
            t_.rotation_euler = (0, 0, aa)
        nd = B.box('ponteiro', (0.025, 0.46, 0.01), (0, 0.23, 0), B.mat_basic('Ponteiro', (0.9, 0.1, 0.08), 0.4, emit=(0.9, 0.1, 0.08), emit_s=1.0), RC)
        piv = B.link(bpy.data.objects.new('pivo', None), RC); piv.parent = g; piv.location = (0, -0.05, 0.02); nd.parent = piv
        cap = B.cyl('eixo', 0.05, 0.02, (0, 0, 0.01), B.mat_basic('Eixo', (0.15, 0.15, 0.17), 0.4), RC, seg=24); cap.parent = piv
        t1, t2 = shot.panel[3]
        kpa = lambda T: 101.3 - 21.3 * sstep(t1, t2, T)
        rd = txt('leitura', '101 kPa', 0.16, (1, 1, 1), g, (0, -0.42, 0.02)); dyn_text(rd, lambda T: f'{kpa(T):.0f} kPa')
        tt = txt('titulo_med', 'pressão do ar', 0.15, (0.8, 0.85, 0.95), g, (0, 0.67, 0.02))
        neg = bill('menos21', '−21%', (0, 0, 0), 0.28, P.RED); neg.constraints.clear(); neg.parent = g; neg.location = (0.62, -0.55, 0.05)
        items['gauge'] = (g, piv, kpa, ang, neg)
    elif kind == 'alt':
        g = panel_root('altimetro', 1.9); plate(g, 1.9, 0.75)
        tt = txt('titulo_alt', 'altitude', 0.11, (0.8, 0.85, 0.95), g, (0, 0.22, 0.02))
        t1, t2 = shot.panel[3]; h = lambda T: 2000.0 * sstep(t1, t2, T)
        rd = txt('leitura_alt', '0 m', 0.32, P.YEL, g, (0, -0.08, 0.02)); dyn_text(rd, lambda T: f'{h(T):,.0f} m'.replace(',', '.'))
        items['alt'] = (g,)

# ================================================================== poses do Téo
def walk_pose(teo, f, T):
    ph = T * 2 * math.pi * 0.95; s = math.sin(ph)
    B.pose(teo, frame=f, spine=(4, 0, 2 * s), head=(2, 0, -3 * s),
           **{'thigh.L': (-26 * s, 0, 0), 'thigh.R': (26 * s, 0, 0), 'shin.L': (max(0, 40 * math.sin(ph + 1.6)), 0, 0), 'shin.R': (max(0, -40 * math.sin(ph + 1.6)), 0, 0),
              'upper_arm.L': (22 * s, 0, -8), 'upper_arm.R': (-22 * s, 0, 8), 'forearm.L': (-18, 0, 0), 'forearm.R': (-18, 0, 0)})

EARS_Y = float(os.environ.get('EARS_Y', '90'))
def teo_anim(mode, teo, f, T):
    r = teo['root']; br = math.sin(T * 1.7); hz = teo['hip_z']
    if mode == 'walk':
        r.location = (P.TEO[0] + 2.0 - 1.15 * T, P.TEO[1], P.TEO[2] + 0.02 * abs(math.sin(T * 6))); r.rotation_euler = (0, 0, math.radians(-90))
        walk_pose(teo, f, T); B.set_face(teo, {'neutral': 1.0}, f); return
    r.location = P.TEO; r.rotation_euler = (0, 0, 0)
    arms0 = {'upper_arm.L': (0, 0, -7), 'upper_arm.R': (0, 0, 7), 'forearm.L': (-12, 0, 0), 'forearm.R': (-12, 0, 0)}
    if mode == 'idle':
        B.pose(teo, frame=f, spine=(1.5 * br, 0, 0), head=(-2, 0, 14 * math.sin(T * 0.6)), **arms0); B.set_face(teo, {'neutral': 1.0}, f)
    elif mode == 'inhale':
        k = sstep(1.45, 2.3, T)
        B.pose(teo, frame=f, spine=(-7 * k, 0, 0), head=(-14 * k, 0, 0), **{'upper_arm.L': (10 * k, 0, -14), 'upper_arm.R': (10 * k, 0, 14), 'forearm.L': (-10, 0, 0), 'forearm.R': (-10, 0, 0)})
        B.set_face(teo, {'relief': k, 'neutral': 1 - k}, f)
    elif mode == 'throat':
        k = sstep(7.35, 7.9, T); sh = sstep(8.3, 8.6, T) * math.sin((T - 8.3) * 14) * (1 - sstep(9.0, 9.3, T))
        B.pose(teo, frame=f, spine=(6 * k, 0, 0), head=(-8 * k, 0, 12 * sh),
               **{'upper_arm.R': (-35 * k, 0, 7 - 67 * k), 'forearm.R': (-12 - 138 * k, 0, 0), 'upper_arm.L': (-10 * k, 0, -7 - 6 * k), 'forearm.L': (-12 - 25 * k, 0, 0)})
        B.set_face(teo, {'alarm': k, 'neutral': 1 - k}, f)
    elif mode == 'ears':
        k = sstep(20.55, 20.7, T); jolt = math.exp(-max(T - 20.62, 0) * 6) * sstep(20.58, 20.64, T)
        B.pose(teo, frame=f, spine=(-3 * jolt, 0, 0), head=(-10 * jolt, 0, -14 * jolt + 6 * k), **arms0)
        B.set_face(teo, {'alarm': k, 'neutral': 1 - k}, f)
    elif mode == 'hold':
        k = sstep(32.4, 32.85, T); sh = sstep(33.6, 33.8, T) * math.sin((T - 33.6) * 13) * (1 - sstep(34.2, 34.4, T))
        B.pose(teo, frame=f, spine=(-4 * k, 0, 0), head=(-4 * k, 0, 10 * sh),
               **{'upper_arm.R': (-62 * k, 0, 7 - 34 * k), 'forearm.R': (-12 - 128 * k, 0, 0), 'upper_arm.L': (0, 0, -7), 'forearm.L': (-12, 0, 0)})
        B.set_face(teo, {'focus': k, 'neutral': 1 - k}, f)
    elif mode == 'wave':
        k = sstep(48.05, 48.5, T); wv = math.sin((T - 48.0) * 9) * k
        B.pose(teo, frame=f, spine=(0, 0, 0), head=(-4, 0, 6 * math.sin(T)),
               **{'upper_arm.R': (-10 * k, 0, 7 + 128 * k), 'forearm.R': (-12 - 50 * k - 25 * wv, 0, 0), 'upper_arm.L': (0, 0, -7), 'forearm.L': (-12, 0, 0)})
        B.set_face(teo, {'relief': 1.0}, f)
    elif mode in ('lying', 'situp', 'sitting'):
        k = {'lying': 0.0, 'sitting': 1.0}.get(mode, sstep(69.15, 69.95, T))
        r.location = (P.TEO[0] - 0.2, P.TEO[1], P.TEO[2] + 0.13 - hz); r.rotation_euler = (0, 0, math.radians(-90))   # pernas para -X: de frente para a câmera
        sp = -86 + 96 * k
        B.pose(teo, frame=f, spine=(sp, 0, 0), head=(-6 + 10 * k, 0, 8 * k * math.sin(T * 0.8)),
               **{'thigh.L': (-90 - 22 * k, 0, -5), 'thigh.R': (-90 - 14 * k, 0, 5), 'shin.L': (48 * k, 0, 0), 'shin.R': (34 * k, 0, 0),
                  'upper_arm.L': (-10 + 40 * k, 0, -18 - 12 * k), 'upper_arm.R': (-10 + 40 * k, 0, 18 + 12 * k), 'forearm.L': (-15 + 10 * k, 0, 0), 'forearm.R': (-15 + 10 * k, 0, 0)})
        B.set_face(teo, {'neutral': 1 - k, 'relief': k} if mode != 'lying' else {'neutral': 1.0}, f)

def car_set(car, x, y, z, yaw, f, dist):
    car['root'].location = (x, y, z); car['root'].rotation_euler = (0, 0, yaw); key(car['root'], 'location', 'rotation_euler', f=f)
    for w in car['wheels']: w.rotation_euler = (0, dist / 0.33, 0); key(w, 'rotation_euler', f=f)

# ================================================================== animação quadro a quadro
fr = list(shot.frames); prev = None; dist = 0.0
rr = random.Random(11); van = None
if K == 'mol' and hasattr(shot, 'vanish'):
    van = [(o, shot.vanish + rr.uniform(0.0, 0.35)) for o, is_o in items['mols'] if is_o]
if K == 'pulmao' and hasattr(shot, 'vanish'):
    van_dots = [(o, shot.vanish + rr.uniform(0.0, 0.4)) for o in items['dots']]
if K == 'cabine':
    SC_m = items['masks']; drop_t = [shot.drop + 0.025 * i + rr.uniform(0, 0.08) for i in range(len(SC_m))]

def path_pt(path, s):
    s = s % 1.0; n = len(path) - 1; x = s * n; i = min(int(x), n - 1); t = x - i
    return Vector(path[i]).lerp(Vector(path[i + 1]), t)

for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4))
    if K == 'rua':
        if hasattr(shot, 'teo'): teo_anim(shot.teo, items['teo'], f, T); key(items['teo']['root'], 'location', 'rotation_euler', f=f)
        else: items['teo']['root'].location = (P.TEO[0] - 0.2, P.TEO[1], P.TEO[2]); teo_anim('idle', items['teo'], f, T)
        if out_t and out_t > 0:
            k = 1 - sstep(out_t, out_t + 0.22, T)
            for fl in [items['candle']] + items['gas']:
                fl['root'].scale = (max(k, 1e-4),) * 3; key(fl['root'], 'scale', f=f)
                fl['light'].data.energy = fl['energy'] * k; fl['light'].data.keyframe_insert('energy', frame=f)
        if 'wisp' in items:
            for i, pt in enumerate(items['wisp'].points):
                u = i / 23; amp = 0.004 + 0.035 * u * u
                pt.co = (P.CANDLE[0] + amp * math.sin(9 * u - 5 * T), P.CANDLE[1] + amp * 0.6 * math.cos(7 * u - 4 * T), P.CANDLE[2] - 0.01 + 0.32 * u, 1)
                pt.radius = 1.0 + 3.0 * u; pt.keyframe_insert('co', frame=f); pt.keyframe_insert('radius', frame=f)
        if hasattr(shot, 'car'):
            x, y, z, yaw = shot.car(T)
            if prev is not None: dist += abs(x - prev)
            prev = x; car = items['car']; car_set(car, x, y, z, yaw, f, dist)
            drv = car['driver']
            if getattr(shot, 'crashed', False):
                B.pose(drv, frame=f, sit=1.0, spine=(38, 0, 6), head=(32, 0, 10), **{'upper_arm.L': (-20, 0, -10), 'upper_arm.R': (-20, 0, 10), 'forearm.L': (-10, 0, 0), 'forearm.R': (-10, 0, 0)})
                blink = 1.0 if (T * 1.6) % 1.0 < 0.5 else 0.0
                set_input(car['tail'], 'Principled BSDF', 'Emission Strength', 0.3 + 7.0 * blink, f)
            else:
                B.pose(drv, frame=f, sit=1.0, head=(0, 0, 6 * math.sin(T)))
            if hasattr(shot, 'engine_off'):
                k = 1 - sstep(shot.engine_off, shot.engine_off + 0.25, T)
                for i, p in enumerate(car['puffs']):
                    u = ((T * 2.2 + i / 6) % 1.0); p.location = (-2.35 - 0.9 * u, -0.55, 0.3 + 0.15 * u); p.scale = (max(k * (0.6 + 1.2 * u), 1e-4),) * 3
                    key(p, 'location', 'scale', f=f)
            else:
                for p in car['puffs']: p.scale = (1e-4,) * 3; key(p, 'scale', f=f)
        if 'back' in items:
            for o, d, s in items['back']:
                t_ = shot.o2back + d; k = sstep(t_, t_ + 0.18, T) if shot.o2back > 0 else 1.0
                o.scale = (max(s * k * (1 + 0.3 * math.sin(math.pi * min(sstep(t_, t_ + 0.18, T), 1))), 1e-4),) * 3; key(o, 'scale', f=f)
        if items.get('chunks'):
            vis = T >= shot.crumble
            for o in items['bld']:
                o.hide_render = vis; o.keyframe_insert('hide_render', frame=f)
            for c in items['chunks']:
                p_, r_, s_ = SC.chunk_state(c, T, shot.crumble); o = c['obj']
                o.location = p_; o.rotation_euler = r_; o.scale = (s_ if vis else 1e-4,) * 3; key(o, 'location', 'rotation_euler', 'scale', f=f)
            for o, d, sz in items['dust']:
                u = sstep(shot.crumble + d, shot.crumble + d + 1.0, T); o.scale = (max(sz * u, 1e-4),) * 3; key(o, 'scale', f=f)
        if 'fade' in items:
            k = sstep(shot.fade[0], shot.fade[1], T)
            for m in items['fade']: set_input(m, 'Sumir', 0, k, f)
    if 'loose' in items:
        t_l = shot.loose[0]
        for i, (o, p0, d, ph) in enumerate(items['loose']):
            k = sstep(t_l + d, t_l + d + 0.2, T) if t_l > 0 else 1.0
            o.location = (p0[0] + 0.3 * math.sin(T * 0.9 + ph), p0[1] + 0.3 * math.cos(T * 0.7 + ph), p0[2] + 0.25 * math.sin(T * 1.1 + 2 * ph))
            o.scale = (max(k * (1 + 0.4 * math.sin(math.pi * min(sstep(t_l + d, t_l + d + 0.2, T), 1))) if t_l > 0 else 1.0, 1e-4),) * 3
            key(o, 'location', 'scale', f=f)
    if K == 'cristal':
        A_ = items['atoms']; drift = items['drift']; p0 = items['p0']
        tv = getattr(shot, 'vanish', None); scat = getattr(shot, 'scatter', None)
        u = (T - tv) if tv is not None else (scat if scat is not None else 0.0)
        gone = tv is not None and T >= tv or scat is not None
        for o in A_['O'] + A_['bond']:
            k = (1 - sstep(tv, tv + 0.15, T)) if tv is not None else (0.0 if scat is not None else 1.0)
            o.scale = (max(k, 1e-4),) * 3; key(o, 'scale', f=f)
        if gone:
            for o in A_['Si'] + A_['Ca'] + A_['H']:
                d_ = drift[o.name] * (max(u, 0) ** 1.3); o.location = (p0[o.name] + d_)[:]; key(o, 'location', f=f)
        if hasattr(shot, 'oglow'):
            g0, g1 = shot.oglow; k = math.sin(math.pi * sstep(g0, g1, T))
            set_input(bpy.data.materials['Atomo_O'], 'Principled BSDF', 'Emission Strength', 0.25 + 3.0 * k, f)
    elif K == 'agua':
        tg = getattr(shot, 'vanish', 999.0); scat = getattr(shot, 'scatter', None)
        for m in items['agua']:
            if scat is not None:
                st = SC.agua_state(m, T, -scat + T, False); kO = 0.0
            else:
                st = SC.agua_state(m, T, tg); kO = st['kO']
            m['O'].location = st['O']; m['O'].scale = (max(kO, 1e-4),) * 3; key(m['O'], 'location', 'scale', f=f)
            for h, pp in zip(m['H'], (st['H1'], st['H2'])): h.location = pp; key(h, 'location', f=f)
            c_ = st['O']
            for b, hp in zip(m['bonds'], (st['H1'], st['H2'])):
                d = Vector(hp) - Vector(c_); b.location = ((Vector(c_) + Vector(hp)) / 2)[:]
                b.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); b.scale = (max(kO, 1e-4), max(kO, 1e-4), max(d.length / 0.75 * kO, 1e-4))
                key(b, 'location', 'rotation_quaternion', 'scale', f=f)
    elif K == 'mar':
        items['ocean'].time = 10 + T; items['ocean'].keyframe_insert('time', frame=f)
        items['sea'].location.z = -10.0 * sstep(P.T_MAR, P.T_MAR + 1.6, T); key(items['sea'], 'location', f=f)
        for o, p0, d, sz, rise in items['vapor']:
            u = max(T - P.T_MAR - d, 0.0); k = sstep(0, 0.6, u)
            o.location = (p0[0], p0[1], p0[2] + rise * u - 10.0 * sstep(P.T_MAR, P.T_MAR + 1.6, T) * (1 - k)); o.scale = (max(sz * k * (0.6 + 0.4 * min(u, 1)), 1e-4),) * 3
            key(o, 'location', 'scale', f=f)
    elif K == 'terra' and hasattr(shot, 'shake'):
        e = items['earth']; k = sstep(shot.shake, shot.shake + 0.4, T)
        e['root'].location = (0.12 * k * math.sin(T * 47), 0.12 * k * math.sin(T * 53 + 1), 0.10 * k * math.sin(T * 41 + 2)); key(e['root'], 'location', f=f)
        sup = bpy.data.objects['TerraSup']; s_ = 1 - 0.04 * sstep(shot.shake, shot.shake + 2.0, T); sup.scale = (s_,) * 3; key(sup, 'scale', f=f)
    elif K == 'mol':
        if van:
            for o, tv in van:
                k = 1 - sstep(tv, tv + 0.12, T); bump = 1 + 0.35 * math.sin(math.pi * min(max((T - tv + 0.08) / 0.2, 0), 1))
                o.scale = (max(k * bump, 1e-4),) * 3; key(o, 'scale', f=f)
        if hasattr(shot, 'o2glow'):
            g0, g1 = shot.o2glow; k = sstep(g0, g1, T)
            set_input(bpy.data.materials['AtomoO2'], 'Principled BSDF', 'Emission Strength', 0.6 + 2.2 * k, f)
    elif K == 'ceu':
        jet = items['jet']
        if hasattr(shot, 'jet'):
            jet['root'].location = shot.jet(T); key(jet['root'], 'location', f=f)
            e = shot.engines(T)
            for gl in jet['glows']: set_input(gl.data.materials[0], 'Emission', 'Strength', 6.0 * e, f)
    elif K == 'pulmao':
        if hasattr(shot, 'vanish'):
            for o, tv in van_dots:
                k = 1 - sstep(tv, tv + 0.15, T); o.scale = (max(k, 1e-4),) * 3; key(o, 'scale', f=f)
        if hasattr(shot, 'leak'):
            X = items['X']; path = items['path']; l0, l1 = shot.leak
            cells = items['cells']
            for i, c in enumerate(cells):
                c.location = path_pt(path, i / len(cells) + 0.05 * T)[:]; c.rotation_euler = (T + i, 0.5 * i, 0); key(c, 'location', 'rotation_euler', f=f)
            for j, o in enumerate(items['o2s']):
                ci = j % len(cells); ts = l0 + (l1 - l0 - 0.6) * j / len(items['o2s'])
                cp = path_pt(path, ci / len(cells) + 0.05 * min(T, ts)) + Vector((0.12 * math.cos(j), 0.12 * math.sin(j), 0.1))
                tgt = Vector((X, 0, 0)) + (cp - Vector((X, 0, 0))).normalized() * 1.2
                u = sstep(ts, ts + 0.9, T); p = cp.lerp(tgt, u) if T > ts else path_pt(path, ci / len(cells) + 0.05 * T) + Vector((0.12 * math.cos(j), 0.12 * math.sin(j), 0.1))
                o.location = p[:]; o.scale = ((1 - 0.4 * u),) * 3; key(o, 'location', 'scale', f=f)
    elif K == 'cabine':
        for (root, tube), td in zip(SC_m, drop_t):
            u = (T - td)
            z = 2.42 if u < 0 else 1.75 + 0.67 * max(0.0, 1 - u / 0.25) ** 2 + (0.06 * math.exp(-u * 5) * math.sin(u * 25) if u > 0.25 else 0)
            root.location.z = z; key(root, 'location', f=f)
        teo = items['teo']; dz = sstep(46.3, 47.5, T); al = sstep(shot.drop, shot.drop + 0.3, T)
        B.pose(teo, frame=f, sit=1.0, spine=(8 + 22 * dz, 0, 4 * dz), head=(-14 * al * (1 - dz) + 30 * dz, 0, 10 * dz),
               **{'upper_arm.L': (-55, 0, -8), 'upper_arm.R': (-55 - 40 * al * (1 - dz), 0, 8), 'forearm.L': (-35, 0, 0), 'forearm.R': (-35 - 50 * al * (1 - dz), 0, 0)})
        B.set_face(teo, {'alarm': al * (1 - dz), 'neutral': 1 - al + al * dz}, f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    c = shot.cam(T); cam.location = c['pos']; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    if shot.panel:
        kind = shot.panel[0]; L = 35.0 / c['lens']
        g = items.get('pie', items.get('gauge', items.get('alt')))[0]
        s = PANEL_S[kind] * L * pop_scale(T, shot.panel[1], shot.panel[2]) / 5; g.scale = (s,) * 3; g.location = (0.0, PANEL_Y[kind] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if kind == 'body':
            g_, sec, texts = items['pie']; mode = shot.panel[3]; o = sec['O']
            kk_ = 1 + 0.14 * math.sin(math.pi * sstep(23.85, 24.5, T)) if mode == 'hi' else max(1 - sstep(P.T_CORPO, P.T_CORPO + 0.5, T), 1e-4)
            o.scale = (kk_,) * 3; key(o, 'scale', f=f)
        if kind == 'pie':
            g_, sec, texts = items['pie']; mode = shot.panel[3]
            hi = {'N2': ('N2', 10.4, 11.2), 'O2': ('O2', 12.6, 13.2)}.get(mode)
            for nm, o in sec.items():
                kk_ = 1.0
                if hi and nm == hi[0]: kk_ = 1 + 0.12 * math.sin(math.pi * sstep(hi[1], hi[2], T))
                if mode == 'gone' and nm == 'O2': kk_ = max(1 - sstep(P.T_SOME_B, P.T_SOME_B + 0.3, T), 1e-4)
                o.scale = (kk_,) * 3; key(o, 'scale', f=f)
        if kind == 'gauge':
            g_, piv, kpa, ang, neg = items['gauge']; piv.rotation_euler = (0, 0, ang(kpa(T))); key(piv, 'rotation_euler', f=f)
            sn = pop_scale(T, 19.3); neg.scale = (sn,) * 3; key(neg, 'scale', f=f)
    ev['cam'] = [round(x, 3) for x in c['pos']]; events['frames'].append(ev)

# ------------------------------------------------------------------ painel da pizza (B3): o "21%" vira "0%"
if shot.panel and shot.panel[0] == 'pie' and shot.panel[3] == 'gone':
    o = items['pie'][2][1][-1]; dyn_text(o, lambda T: ' 21%' if T < P.T_SOME_B + 0.15 else ' 0%')

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
