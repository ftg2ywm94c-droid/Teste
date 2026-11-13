"""Vídeo 04: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep06/render.py -- --shot C1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep06/frames/<plano>/NNNN.png (final) ou v2/ep06/preview/<plano>/ (prévia). Retomável."""
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
if K not in ('rua', 'cidade'):
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
C6 = B.new_coll('Ep06')
# ================================================================== cenários
if K in ('rua', 'cidade'):
    R = SC.build_cidade(abandoned=(K == 'cidade')); items.update(R)
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
    if not hasattr(shot, 'teo'):
        for o in teo['root'].children_recursive + [teo['root']]: o.hide_render = True
    car = R['car']
    if K == 'rua': car['coll'].hide_render = True
    flames = [R['candle']] + R['gas']
    if K == 'cidade':
        for fl in flames: fl['root'].scale = (1e-4,) * 3; fl['light'].data.energy = 0.0
    else:
        for i, fl in enumerate(flames): SC.flicker(fl['obj'], 0.10, 4.0, i)
    if hasattr(shot, 'dog'):
        d = SC.build_dog('Cao', C6, tag=len(shot.dog) > 2 and shot.dog[2]); d['root'].location = shot.dog[1]
        d['root'].rotation_euler = (0, 0, math.radians(-25)); items['dog'] = d
    if getattr(shot, 'bat', False): items['bat'] = SC.build_bat('Morcego', C6)
    if hasattr(shot, 'shield'):
        m, nb = SC.new_mat('Escudo'); out = nb.n('ShaderNodeOutputMaterial'); tr = nb.n('ShaderNodeBsdfTransparent'); em = nb.n('ShaderNodeEmission')
        em.inputs[0].default_value = (0.35, 0.95, 1.0, 1); em.inputs[1].default_value = 2.5
        lw = nb.n('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.25; mx = nb.n('ShaderNodeMixShader')
        nb.link(lw.outputs['Facing'], mx.inputs[0]); nb.link(tr.outputs[0], mx.inputs[1]); nb.link(em.outputs[0], mx.inputs[2]); nb.link(mx.outputs[0], out.inputs[0])
        sh = B.sphere('escudo', 1.15, (P.TEO[0], P.TEO[1], 1.05), m, C6, scale=(0.85, 0.85, 1.05), seg=48); sh.visible_shadow = False; items['shield'] = sh
        items['shield_spores'] = SC.spores(C6, 40, (P.TEO[0] - 3.0, P.TEO[1], 1.2), seed=13)
elif K == 'mata':
    items.update(SC.build_mata())
    sc.render.film_transparent = False
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8
    tints = [SC.ANT_COL, (0.30, 0.10, 0.04), (0.12, 0.09, 0.05), (0.22, 0.15, 0.07)]
    if getattr(shot, 'four', False):
        ants = []
        for i, (x, y) in enumerate(((1.3, -0.7), (2.3, 0.6), (3.5, -0.5), (4.6, 0.5))):
            a_ = SC.build_ant(f'Formiga{i}', C6, col=tints[i]); st = SC.build_stroma(f'Fungo{i}', C6); st.parent = a_['root']; st.location = (0.3, 0, 0.12); st.scale = (1, 1, 1)
            ants.append((a_, x, y))
        items['four'] = ants
    else:
        a_ = SC.build_ant('Formiga', C6); items['ant'] = a_
        if hasattr(shot, 'stroma'):
            st = SC.build_stroma('Fungo', C6); st.parent = a_['root']; st.location = (0.3, 0, 0.12); items['stroma'] = st
            if shot.stroma == 0.0: st.scale = (1, 1, 1)
        if hasattr(shot, 'spore_t'): items['spores'] = SC.spores(C6, 120, (0, 0, 0))
elif K == 'globo':
    items.update(SC.build_globo())
elif K == 'lab':
    items.update(SC.build_lab())
elif K == 'virus':
    items.update(SC.build_virus())
ms = sc.world.mist_settings; ms.start = 25 if K == 'cidade' else 60; ms.depth = 120 if K == 'cidade' else 260; ms.falloff = 'QUADRATIC'
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)

# ------------------------------------------------------------------ orientação da formiga
def basis(X, Z):
    X = Vector(X).normalized(); Z = Vector(Z).normalized(); Y = Z.cross(X); return Matrix((X, Y, Z)).transposed().to_euler()
def ant_place(a_, T):
    """Posição/orientação da formiga conforme o estado do plano."""
    st = shot.ant; tl = math.radians(12)
    if st == 'climb':
        z = 1.5 + 7.1 * min(max((T - 15.0) / 4.4, 0), 1.0)
        return (0.0, -0.12 - 0.05, z), basis((0, 0, 1), (0, -1, 0)), True
    X = (math.cos(tl), 0, math.sin(tl)); Zd = (math.sin(tl), 0, -math.cos(tl))
    if st == 'bite':
        u = min(max((T - 19.4) / 0.5, 0), 1.0); x = 1.7 + 0.9 * u
        p = P.leaf_pt(x, 0.13); return p, basis(X, Zd), T < P.T_MORDE
    return P.BITE, basis(X, Zd), False
def ant_dead_legs(a_, f, k=1.0):
    for hip, kk, sd in a_['legs']:
        hip.rotation_euler = (math.radians(-25 * k * sd), 0, math.radians((kk - 1) * -45 * sd)); hip.keyframe_insert('rotation_euler', frame=f)

# ------------------------------------------------------------------ painéis presos à câmera
PANEL_S = dict(curve=0.85, cal=0.8, sir=0.9); PANEL_Y = dict(curve=-1.7, cal=1.75, sir=-1.6)
def panel_root(name, y):
    g = B.link(bpy.data.objects.new(name, None), RC); g.parent = cam; g.location = (0.0, y, -5.0); g.scale = (1e-4,) * 3; return g
def plate(g, w, h, alpha=0.86):
    p = B.box(g.name + '_placa', (w, h, 0.01), (0, 0, -0.02), B.mat_basic('PainelFundo', (0.03, 0.035, 0.05), 0.6, alpha=alpha), RC, bevel=0.08)
    p.parent = g; p.visible_shadow = False; return p
def segline(name, pts, col, g, w=0.025, z=0.01):
    """Polilinha como faixas finas (uma por segmento) para poder revelar aos poucos."""
    mat = SC.emit_mat('Linha_' + name, col, 1.6); segs = []
    for i in range(len(pts) - 1):
        a0, b0 = Vector((*pts[i], z)), Vector((*pts[i + 1], z)); d = b0 - a0; L_ = d.length
        o = B.box(f'{name}_{i}', (L_ + w * 0.6, w, 0.004), ((a0 + b0) / 2)[:], mat, RC); o.rotation_euler = (0, 0, math.atan2(d.y, d.x))
        o.parent = g; o.visible_shadow = False; segs.append(o)
    return segs
def growth(c):
    pts = [(0, 0.05), (5, 0.15), (10, 0.35), (15, 0.55), (20, 0.78), (25, 0.95), (28, 1.0), (30, 0.92), (32, 0.62), (34, 0.32), (37, 0.08), (40, 0.02)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= c <= x1: return y0 + (y1 - y0) * (c - x0) / (x1 - x0)
    return 0.0
def sir_sim(act, T=10.0, dt=0.002):
    a, b, z_, d = 0.005, 0.0095, 0.0001, 0.0001; S_, Z_, R_ = 500.0, 1.0, 0.0; out = []; t_ = 0.0; kills = [1.0 * i for i in range(1, 11)]; k = 0
    while t_ <= T:
        if act and k < len(kills) and t_ >= kills[k]: Z_ *= 0.12; k += 1
        out.append((t_, S_, Z_))
        dS = -b * S_ * Z_ - d * S_; dZ = b * S_ * Z_ + z_ * R_ - a * S_ * Z_; dR = d * S_ + a * S_ * Z_ - z_ * R_
        S_ += dS * dt; Z_ += dZ * dt; R_ += dR * dt; t_ += dt
    return out[::50], kills

if shot.panel:
    kind = shot.panel[0]
    if kind == 'curve':
        g = panel_root('curva', -1.7); plate(g, 2.7, 1.6); W_, H_ = 2.1, 0.95; ox, oy = -1.05, -0.55
        ax = B.mat_basic('Eixo', (0.8, 0.82, 0.88), 0.5)
        for o in (B.box('eixo_x', (W_, 0.012, 0.004), (ox + W_ / 2, oy, 0.008), ax, RC), B.box('eixo_y', (0.012, H_, 0.004), (ox, oy + H_ / 2, 0.008), ax, RC)): o.parent = g
        cpts = [(ox + W_ * c / 40, oy + H_ * growth(c)) for c in [i * 0.5 for i in range(81)]]
        items['curve_segs'] = segline('crescimento', cpts, (0.85, 0.75, 0.3), g)
        for c in (0, 10, 20, 30, 40):
            t_ = txt(f'tick{c}', f'{c}', 0.075, (0.8, 0.82, 0.88), g, (ox + W_ * c / 40, oy - 0.09, 0.01))
        txt('titulo_curva', 'fungos: crescimento x temperatura', 0.095, (1, 1, 1), g, (0, 0.66, 0.01))
        txt('eixo_t', 'temperatura (°C)', 0.07, (0.75, 0.78, 0.85), g, (0.55, oy - 0.2, 0.01))
        m30 = B.box('marca30', (0.012, H_ * 1.05, 0.004), (ox + W_ * 30 / 40, oy + H_ / 2, 0.012), SC.emit_mat('Marca30', (1, 1, 1), 1.2), RC); m30.parent = g
        l30 = txt('rot30', '30 °C', 0.08, (1, 1, 1), g, (ox + W_ * 30 / 40, oy + H_ + 0.07, 0.01))
        items['m30'] = (m30, l30)
        items['panel'] = g
    elif kind == 'cal':
        g = panel_root('calendario', 1.75); plate(g, 1.9, 0.9)
        txt('tit_cal', 'raiva: incubação', 0.1, (0.8, 0.85, 0.95), g, (0, 0.3, 0.02))
        t1, t2 = shot.panel[3]; wk = lambda T: 1 + int(7 * sstep(t1, t2, T) + 1e-6)
        rd = txt('leitura_cal', 'semana 1', 0.24, P.YEL, g, (0, 0.03, 0.02)); dyn_text(rd, lambda T: f'semana {wk(T)}')
        txt('sub_cal', 'típico: 2 a 3 meses (OMS)', 0.075, (0.75, 0.78, 0.85), g, (0, -0.27, 0.02))
        items['panel'] = g
    elif kind == 'sir':
        g = panel_root('sir', -1.6); plate(g, 2.8, 1.7); W_, H_ = 2.2, 0.95; ox, oy = -1.1, -0.58
        ax = B.mat_basic('Eixo', (0.8, 0.82, 0.88), 0.5)
        for o in (B.box('eixo_x', (W_, 0.012, 0.004), (ox + W_ / 2, oy, 0.008), ax, RC), B.box('eixo_y', (0.012, H_, 0.004), (ox, oy + H_ / 2, 0.008), ax, RC)): o.parent = g
        act = shot.panel[3] == 'agir'; data, kills = sir_sim(act)
        hum = [(ox + W_ * t_ / 10, oy + H_ * S_ / 500) for t_, S_, Z_ in data]; zom = [(ox + W_ * t_ / 10, oy + H_ * min(Z_ / 500, 1)) for t_, S_, Z_ in data]
        items['sir_h'] = segline('humanos', hum, (0.45, 0.72, 1.0), g, 0.03); items['sir_z'] = segline('zumbis', zom, (0.45, 0.95, 0.35), g, 0.03)
        if act:
            km = SC.emit_mat('Ataque', (1.0, 0.8, 0.1), 1.4); items['kills'] = []
            for kt in kills:
                o = B.box('ataque', (0.01, H_ * 0.25, 0.004), (ox + W_ * kt / 10, oy + 0.05, 0.014), km, RC); o.parent = g; o.scale = (1e-4,) * 3; items['kills'].append((o, kt))
        txt('tit_sir', 'simulação de surto zumbi', 0.1, (1, 1, 1), g, (0, 0.72, 0.01))
        txt('sub_sir', 'modelo simplificado de Munz et al. (2009)', 0.06, (0.7, 0.72, 0.78), g, (0, 0.6, 0.01))
        txt('leg_h', 'humanos', 0.075, (0.45, 0.72, 1.0), g, (-0.75, oy - 0.12, 0.01)); txt('leg_z', 'zumbis', 0.075, (0.45, 0.95, 0.35), g, (-0.2, oy - 0.12, 0.01))
        txt('eixo_t', 'tempo', 0.065, (0.75, 0.78, 0.85), g, (0.85, oy - 0.12, 0.01))
        if hasattr(shot, 'sir_tag'):
            tx, col, ton = shot.sir_tag; objs, w = rich('tag_sir', tx, 0.11, col, g, (0, 0.45, 0.02)); items['sir_tag'] = (objs, ton)
            for o in objs: o.scale = (1e-4,) * 3
        items['panel'] = g

# ================================================================== poses do Téo
def walk_pose(teo, f, T):
    ph = T * 2 * math.pi * 0.95; s = math.sin(ph)
    B.pose(teo, frame=f, spine=(4, 0, 2 * s), head=(2, 0, -3 * s),
           **{'thigh.L': (-26 * s, 0, 0), 'thigh.R': (26 * s, 0, 0), 'shin.L': (max(0, 40 * math.sin(ph + 1.6)), 0, 0), 'shin.R': (max(0, -40 * math.sin(ph + 1.6)), 0, 0),
              'upper_arm.L': (22 * s, 0, -8), 'upper_arm.R': (-22 * s, 0, 8), 'forearm.L': (-18, 0, 0), 'forearm.R': (-18, 0, 0)})
def teo_anim(mode, teo, f, T):
    r = teo['root']; br = math.sin(T * 1.7); lt = T - shot.t0
    r.location = P.TEO; r.rotation_euler = (0, 0, 0)
    arms0 = {'upper_arm.L': (0, 0, -7), 'upper_arm.R': (0, 0, 7), 'forearm.L': (-12, 0, 0), 'forearm.R': (-12, 0, 0)}
    if mode == 'idle':
        B.pose(teo, frame=f, spine=(1.5 * br, 0, 0), head=(-2, 0, 14 * math.sin(T * 0.6)), **arms0); B.set_face(teo, {'neutral': 1.0}, f)
    elif mode == 'alarm':
        k = sstep(0.1, 0.5, lt); r.rotation_euler = (0, 0, math.radians(-25 * k))
        B.pose(teo, frame=f, spine=(-5 * k, 0, 0), head=(-8 * k, 0, -20 * k), **{'upper_arm.L': (-30 * k, 0, -7 - 20 * k), 'upper_arm.R': (-30 * k, 0, 7 + 20 * k), 'forearm.L': (-12 - 40 * k, 0, 0), 'forearm.R': (-12 - 40 * k, 0, 0)})
        B.set_face(teo, {'alarm': k, 'neutral': 1 - k}, f)
    elif mode == 'relief':
        B.pose(teo, frame=f, spine=(1.5 * br, 0, 0), head=(-4, 0, 8 * math.sin(T * 0.8)), **arms0); B.set_face(teo, {'relief': 1.0}, f)
    elif mode == 'wave':
        k = sstep(0.2, 0.6, lt); wv = math.sin(lt * 9) * k
        B.pose(teo, frame=f, spine=(0, 0, 0), head=(-4, 0, 6 * math.sin(T)),
               **{'upper_arm.R': (-10 * k, 0, 7 + 128 * k), 'forearm.R': (-12 - 50 * k - 25 * wv, 0, 0), 'upper_arm.L': (0, 0, -7), 'forearm.L': (-12, 0, 0)})
        B.set_face(teo, {'relief': 1.0}, f)

# ================================================================== animação quadro a quadro
fr = list(shot.frames)
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4)); lt = T - shot.t0
    if K in ('rua', 'cidade'):
        if hasattr(shot, 'teo'): teo_anim(shot.teo, items['teo'], f, T); key(items['teo']['root'], 'location', 'rotation_euler', f=f)
        for zd in items.get('zombies', []): SC.zombie_pose(zd, f, lt + 2.0)
        if 'dog' in items: SC.dog_anim(items['dog'], f, T, shot.dog[0])
        if 'bat' in items:
            b_ = items['bat']; u = lt / (shot.t1 - shot.t0)
            b_['root'].location = (14.0 + 9.0 * u, 3.0 + 1.5 * math.sin(u * 6), 3.2 + 0.4 * math.sin(u * 11)); b_['root'].rotation_euler = (0, 0, math.radians(-90 + 15 * math.cos(u * 6)))
            key(b_['root'], 'location', 'rotation_euler', f=f); SC.bat_anim(b_, f, T)
        if 'shield' in items:
            k = sstep(shot.shield, shot.shield + 0.35, T); s_ = max(k, 1e-4); items['shield'].scale = (0.85 * s_, 0.85 * s_, 1.05 * s_); key(items['shield'], 'scale', f=f)
            ctr = Vector((P.TEO[0], P.TEO[1], 1.05))
            for i, (o, v, d) in enumerate(items['shield_spores']):
                u = (lt * 0.9 + d) % 1.6; p0 = Vector((P.TEO[0] - 3.0, P.TEO[1] + v.y * 0.8, 1.0 + v.z * 0.6))
                hit = ctr + (p0 - ctr).normalized() * 1.05
                p_ = p0.lerp(hit, min(u / 0.8, 1)) if u < 0.8 else hit + (hit - ctr).normalized() * (u - 0.8) * 1.6 + Vector((0, 0, -0.3 * (u - 0.8)))
                o.location = p_; o.scale = (2.5 if k > 0.5 else 1e-4,) * 3; key(o, 'location', 'scale', f=f)
    elif K == 'mata':
        if 'four' in items:
            for a_, x, y in items['four']:
                p = P.leaf_pt(x, 0.13); a_['root'].location = (p[0], y, p[2] + 0.02 * abs(y)); a_['root'].rotation_euler = basis((math.cos(math.radians(12)), 0, math.sin(math.radians(12))), (math.sin(math.radians(12)), 0, -math.cos(math.radians(12))))
                ant_dead_legs(a_, f)
        else:
            a_ = items['ant']; p, rot, walking = ant_place(a_, T); a_['root'].location = p; a_['root'].rotation_euler = rot; key(a_['root'], 'location', 'rotation_euler', f=f)
            if walking: SC.ant_walk(a_, f, T)
            elif shot.ant == 'bite':
                k = sstep(P.T_MORRE - 0.3, P.T_MORRE, T); ant_dead_legs(a_, f, k)
                a_['head'].rotation_euler = (0, math.radians(-25 * sstep(P.T_MORDE, P.T_MORDE + 0.3, T)), 0); a_['head'].keyframe_insert('rotation_euler', frame=f)
            else: ant_dead_legs(a_, f)
            if 'stroma' in items and shot.stroma > 0:
                k = sstep(shot.stroma, shot.stroma + 1.0, T); items['stroma'].scale = (1, 1, max(k, 1e-3)); key(items['stroma'], 'scale', f=f)
            if 'spores' in items:
                bpy.context.view_layer.update(); tip = a_['root'].matrix_world @ Vector((0.24, 0, 1.02))
                for o, v, d in items['spores']:
                    u = T - shot.spore_t - d * 0.8
                    if u <= 0: o.scale = (1e-4,) * 3; o.location = tip
                    else: o.location = tip + v * u * 0.8 + Vector((0, 0, -0.25 * u)); o.scale = (1.0,) * 3
                    key(o, 'location', 'scale', f=f)
    elif K == 'globo':
        k = pop_scale(T, shot.pin_on) if shot.pin_on > 0 else 1.0; items['pin'].scale = (k,) * 3; key(items['pin'], 'scale', f=f)
    elif K == 'lab':
        c = shot.temp(T); items['column'].scale = (1, 1, max(items['temp_z'](c), 0.01)); key(items['column'], 'scale', f=f)
    elif K == 'virus':
        h = items['hero']; h.rotation_euler = (math.radians(70), math.radians(10), math.radians(30) + 0.35 * T); key(h, 'rotation_euler', f=f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    c = shot.cam(T); cam.location = c['pos']; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    if K == 'mata':
        cam.data.dof.focus_distance = (Vector(c['pos']) - Vector(c['look'])).length; cam.data.dof.keyframe_insert('focus_distance', frame=f)
    if shot.panel:
        kind = shot.panel[0]; L = 35.0 / c['lens']; g = items['panel']
        s = PANEL_S[kind] * L * pop_scale(T, shot.panel[1], shot.panel[2]) / 5 if shot.panel[1] > 0 else PANEL_S[kind] * L / 5
        g.scale = (s,) * 3; g.location = (0.0, PANEL_Y[kind] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if kind == 'curve':
            t1, t2 = shot.panel[3]; segs = items['curve_segs']
            for i, o in enumerate(segs):
                vis = T >= t1 + (t2 - t1) * i / len(segs); o.scale = (1.0 if vis else 1e-4,) * 3; key(o, 'scale', f=f)
            for o in items['m30']: k = pop_scale(T, 30.26); o.scale = (k,) * 3; key(o, 'scale', f=f)
        if kind == 'sir':
            t1, t2 = shot.panel[4]
            for segs in (items['sir_h'], items['sir_z']):
                for i, o in enumerate(segs):
                    vis = T >= t1 + (t2 - t1) * i / len(segs); o.scale = (1.0 if vis else 1e-4,) * 3; key(o, 'scale', f=f)
            for o, kt in items.get('kills', []):
                vis = T >= t1 + (t2 - t1) * kt / 10; o.scale = (1.0 if vis else 1e-4,) * 3; key(o, 'scale', f=f)
            if 'sir_tag' in items:
                objs, ton = items['sir_tag']; k = pop_scale(T, ton)
                for o in objs: o.scale = (k,) * 3; key(o, 'scale', f=f)
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
