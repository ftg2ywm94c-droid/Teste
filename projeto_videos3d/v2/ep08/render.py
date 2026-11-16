"""Vídeo 08: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep08/render.py -- --shot C1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep08/frames/<plano>/NNNN.png (final) ou v2/ep08/preview/<plano>/ (prévia). Retomável."""
import bpy, sys, os, math, json, time, argparse, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import build as B
import scene as SC
import plan as P
os.environ.setdefault('STYLE2', '1')          # estilo 2 é o padrão a partir do vídeo 08 (v2/ESTILO.md)
import style2 as S2
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
if K in ('estudio', 'globo'):
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
C8 = B.new_coll('Ep08')
ASSETS = os.path.join(HERE, '..', '..', 'assets', 'comentarios')
# ================================================================== cenários
if K == 'dia':
    items.update(SC.build_savana(night=False))
elif K == 'noite':
    items.update(SC.build_savana(night=True)); sc.view_settings.exposure = 0.9
elif K == 'estudio':
    items.update(SC.build_estudio())
elif K == 'globo':
    items.update(SC.build_globo_noite())
if K in ('dia', 'noite'):
    seat = SC.rock_mesh('assento', 0.42, (0, 0.08, 0.0), C8, 99, B.mat_basic('Pedra', (0.36, 0.33, 0.30), 0.85)); seat.scale = (1.0, 0.9, 1.05)
    if (getattr(shot, 'fire', None) is not None) or getattr(shot, 'group', False): items['fire'] = SC.build_fogueira(P.FIRE, C8)
    if getattr(shot, 'group', False):
        anc = []
        for i, (x, y) in enumerate(P.RING):
            a_ = SC.ancestor(i, C8); a_['root'].location = (x, y, 0.0)
            a_['root'].rotation_euler = (0, 0, math.atan2(P.FIRE[0] - x, -(P.FIRE[1] - y)) + math.pi)   # de frente para o fogo (frente = -Y local)
            st_ = SC.rock_mesh(f'assento_anc{i}', 0.36, (x, y, 0.0), C8, 120 + i, B.mat_basic('Pedra', (0.36, 0.33, 0.30), 0.85)); st_.scale = (1.0, 0.9, 1.05)
            anc.append(a_)
        items['anc'] = anc
        fl_ = bpy.data.lights.new('LuzRostos', 'AREA'); fl_.energy = 60; fl_.size = 2.5; fl_.color = (1.0, 0.7, 0.45)
        flo = B.link(bpy.data.objects.new('LuzRostos', fl_), C8); flo.location = (P.FIRE[0], P.FIRE[1] - 0.6, 1.0); flo.rotation_euler = (math.radians(90), 0, 0)
    if hasattr(shot, 'teo'):
        teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
        if shot.teo in ('chew',):
            tb = SC.tuber('raiz_mao', (0, 0, 0), C8, seed=3); tb.scale = (0.14,) * 3
            tb.parent = teo['arm']; tb.parent_type = 'BONE'; tb.parent_bone = 'forearm.R'; tb.location = (0, 0.04, 0); items['tuber_hand'] = tb
    else:
        seat.hide_render = True
if K == 'estudio':
    if getattr(shot, 'food', False):
        items['raw'] = SC.tuber('raiz_crua', (-1.2, 0, 0.55), C8, seed=2); items['raw'].scale = (0.42,) * 3
        items['cooked'] = SC.tuber('raiz_assada', (1.2, 0, 0.72), C8, cooked=True, seed=5); items['cooked'].scale = (0.42,) * 3
        items['fire'] = SC.build_fogueira((1.2, 0, 0.0), C8, scale=0.45)
    if hasattr(shot, 'objs'):
        ob = SC.build_objetos(C8); items['objs'] = [ob['aco'], ob['ceramica'], ob['vidro']]
        for o, x in zip(items['objs'], (-1.6, 0.0, 1.6)): o.location = (x, 0, 0.45 if o.name == 'aco' else 0.0); o.scale = (1e-4,) * 3
    if getattr(shot, 'brain', False):
        br = SC.build_cerebro(C8, loc=(0.0 if not hasattr(shot, 'food_feed') else 1.5, 0, 1.4), r=0.85); items['brain'] = br
        if hasattr(shot, 'food_feed'):
            items['cooked'] = SC.tuber('raiz_assada', (-1.6, 0, 0.72), C8, cooked=True, seed=5); items['cooked'].scale = (0.42,) * 3
            items['fire'] = SC.build_fogueira((-1.6, 0, 0.0), C8, scale=0.45)
            sm = SC.emit_mat('Energia', (1.0, 0.7, 0.25), 18.0); items['stream'] = []
            for i in range(28):
                s = B.sphere(f'energia{i}', 0.045, (0, 0, 0), sm, C8, seg=8); s.visible_shadow = False; s.scale = (1e-4,) * 3; items['stream'].append(s)
if shot.name == 'THUMB':   # só a thumbnail: luz quente baixa no rosto (reflexo da fogueira)
    tl_ = bpy.data.lights.new('LuzThumb', 'AREA'); tl_.energy = 55; tl_.size = 1.2; tl_.color = (1.0, 0.55, 0.28)
    tlo = B.link(bpy.data.objects.new('LuzThumb', tl_), C8); tlo.location = (0.5, -2.2, 0.5); tlo.rotation_euler = (math.radians(70), 0, math.radians(15))
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
for n in ('LuzFogo',):
    if n in bpy.data.lights: pass
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)
if getattr(shot, 'bubbles', None):
    for i, (t_on, tx) in enumerate(zip(shot.bubbles, ('...', '!', 'era uma vez...'))):
        bp = [(-0.75, P.FIRE[1] + 1.2, 1.95), (0.5, P.FIRE[1] + 1.3, 2.05), (0.0, P.FIRE[1] + 1.0, 2.45)][i]; items['lbl_bolha%d' % i] = (bill('bolha%d' % i, tx, bp, 0.16 if i < 2 else 0.15, P.WHITE if i < 2 else P.YEL), t_on, 99, (lambda p: (lambda T: p))(bp))
if hasattr(shot, 'objs'):
    for i, (t_on, nm) in enumerate(shot.objs):
        x = (-1.6, 0.0, 1.6)[i]; z_ = (1.3, 1.75, 2.1)[i]; items['lbl_obj%d' % i] = (bill('obj%d' % i, nm, (x, 0, z_), 0.26, P.WHITE), t_on + 0.05, shot.objs_off, (lambda p: (lambda T: p))((x, 0, z_)))
    items['lbl_naoexiste'] = (bill('naoexiste', 'não existiriam', (0, 0, 1.0), 0.42, P.RED), shot.objs_off + 0.1, 99, lambda T: (0, 0, 1.0))
if getattr(shot, 'dim', 0): sc.view_settings.exposure -= 1.6 * shot.dim

# ------------------------------------------------------------------ painéis presos à câmera
def panel_root(name, y, z=-5.0):
    g = B.link(bpy.data.objects.new(name, None), RC); g.parent = cam; g.location = (0.0, y, z); g.scale = (1e-4,) * 3; g['y0'] = y; return g
def plate(g, w, h, alpha=0.88, col=(0.03, 0.035, 0.05), name=None):
    p = B.box((name or g.name) + '_placa', (w, h, 0.01), (0, 0, -0.02), B.mat_basic('PainelFundo_%.2f' % col[0], col, 0.6, alpha=alpha), RC, bevel=0.08)
    p.parent = g; p.visible_shadow = False; return p
def lbar(name, w, h, col, g, loc, emit=1.3):
    o = B.box(name, (w, h, 0.01), (0, 0, 0), SC.emit_mat('Barra_' + name, col, emit), RC)
    for v in o.data.vertices: v.co.x += w / 2
    o.parent = g; o.location = loc; o.visible_shadow = False; o.scale = (1e-4, 1, 1); return o
def hide(o): o.scale = (1e-4,) * 3
def avatar_disc(name, img, g, loc, d):
    m, nb = SC.new_mat('Avatar_' + name); out = nb.n('ShaderNodeOutputMaterial'); e = nb.n('ShaderNodeEmission'); e.inputs[1].default_value = 1.0
    uv = nb.n('ShaderNodeTexCoord'); t = nb.img(img, uv.outputs['UV']) if img else None
    if t: nb.link(t.outputs[0], e.inputs[0])
    else: e.inputs[0].default_value = (0.35, 0.37, 0.42, 1)
    dist = nb.vmath('DISTANCE', uv.outputs['UV'], (0.5, 0.5, 0.0)); mask = nb.math('LESS_THAN', dist, 0.5)
    tr = nb.n('ShaderNodeBsdfTransparent'); mx = nb.n('ShaderNodeMixShader'); nb.link(mask, mx.inputs[0]); nb.link(tr.outputs[0], mx.inputs[1]); nb.link(e.outputs[0], mx.inputs[2])
    nb.link(mx.outputs[0], out.inputs[0])
    bm = SC.bmesh.new(); bm.loops.layers.uv.new('UVMap'); SC.bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=d / 2, calc_uvs=True)
    o = B.mesh_obj(name, bm, m, RC); o.parent = g; o.location = loc; o.visible_shadow = False
    ring = B.cyl(name + '_aro', d / 2 + 0.025, 0.004, (loc[0], loc[1], loc[2] - 0.006), SC.emit_mat('AroAvatar', (1.0, 0.55, 0.12), 2.0), RC, seg=48, rot=(0, 0, 0))
    ring.parent = g; ring.visible_shadow = False
    return o, ring

def comment_card(name, y, s=1.0, handle='@desORDEM2026', lines=('E se o fogo nunca tivesse', 'sido descoberto?'), img=os.path.join(ASSETS, '08_avatar_desORDEM2026.png'), tag='tema enviado por um inscrito'):
    g = panel_root(name, y); parts = {}
    parts['plate'] = plate(g, 3.4, 1.35, alpha=0.95, col=(0.14, 0.14, 0.16))
    parts['avatar'] = avatar_disc(name + '_av', img, g, (-1.25, 0.14, 0.02), 0.6)
    parts['handle'] = txt(name + '_handle', handle, 0.125, (0.78, 0.80, 0.86), g, (-0.8, 0.4, 0.02), 'LEFT')
    parts['lines'] = [txt(name + f'_l{i}', ln, 0.16, (1, 1, 1), g, (-0.8, 0.13 - i * 0.24, 0.02), 'LEFT') for i, ln in enumerate(lines)]
    parts['like'] = txt(name + '_like', '', 0.09, (0.65, 0.67, 0.72), g, (-0.8, -0.47, 0.02), 'LEFT')
    tg = B.link(bpy.data.objects.new(name + '_tag', None), RC); tg.parent = g; tg.location = (0, 0.92, 0.0)
    tt = txt(name + '_tagtxt', tag, 0.12, (0.05, 0.05, 0.05), tg, (0, 0, 0.03)); w = text_width(tt)
    pl = B.box(name + '_tagpl', (w + 0.28, 0.26, 0.01), (0, 0, 0), SC.emit_mat('TagAmarela', P.YEL, 1.4), RC, bevel=0.1); pl.parent = tg; pl.visible_shadow = False
    hide(tg); parts['tag'] = tg; parts['s'] = s
    return g, parts

if shot.panel:
    kind = shot.panel[0]
    if kind == 'relogio':
        g = panel_root('relogio', 1.62); plate(g, 2.7, 1.0)
        R_ = 0.32; segs = []; segm_bg = SC.emit_mat('SegFundo', (0.22, 0.23, 0.27), 1.0); col = shot.panel[6]
        for i in range(48):
            ang = math.pi / 2 - (i + 0.5) / 48 * 2 * math.pi
            bg_ = B.box(f'segbg{i}', (0.035, 0.11, 0.01), (-0.85 + R_ * math.cos(ang), R_ * math.sin(ang), 0.0), segm_bg, RC, rot=(0, 0, ang - math.pi / 2)); bg_.parent = g; bg_.visible_shadow = False
            sg = B.box(f'seg{i}', (0.035, 0.11, 0.01), (-0.85 + R_ * math.cos(ang), R_ * math.sin(ang), 0.01), SC.emit_mat('Seg_%.2f' % col[1], col, 1.6), RC, rot=(0, 0, ang - math.pi / 2)); sg.parent = g; sg.visible_shadow = False; hide(sg); segs.append(sg)
        txt('rel24', '24 h', 0.08, (0.8, 0.82, 0.88), g, (-0.85, 0.0, 0.02))
        lines = shot.panel[5].split(': ')
        txt('rel_t1', lines[0] + (':' if len(lines) > 1 else ''), 0.13, (1, 1, 1), g, (-0.32, 0.12 if len(lines) > 1 else 0.0, 0.02), 'LEFT')
        if len(lines) > 1: txt('rel_t2', lines[1], 0.17, col, g, (-0.32, -0.12, 0.02), 'LEFT')
        txt('rel_t0', 'tempo comendo por dia', 0.08, (0.7, 0.72, 0.78), g, (-0.32, 0.36, 0.02), 'LEFT')
        items['segs'] = segs; items['panel'] = g
    elif kind in ('card', 'card_top', 'card_fade'):
        y = {'card': 0.25, 'card_top': 1.55, 'card_fade': 0.25}[kind]
        g, parts = comment_card('card', y); items['card'] = parts; items['panel'] = g
    elif kind == 'cta':
        g, parts = comment_card('card', 0.1, handle='@você', lines=('E se...', ''), img=None, tag='comenta o próximo e se')
        cur = txt('cursor', '|', 0.17, P.YEL, g, (-0.22, 0.13, 0.02)); items['cursor'] = cur
        q = txt('av_q', '?', 0.3, (1, 1, 1), g, (-1.25, 0.1, 0.03))
        p2 = B.link(bpy.data.objects.new('pode_ser', None), RC); p2.parent = g; p2.location = (0, -0.9, 0.0)
        t2 = txt('pode_txt', 'pode ser o seu!', 0.14, P.YEL, p2, (0, 0, 0.03)); hide(p2); items['pode'] = p2
        items['card'] = parts; items['panel'] = g
    elif kind == 'energia':
        g = panel_root('energia', -1.6); plate(g, 2.8, 1.0)
        txt('en_t', 'energia que o corpo aproveita', 0.095, (1, 1, 1), g, (0, 0.33, 0.02))
        txt('en_r1', 'crua', 0.085, (0.85, 0.87, 0.92), g, (-1.25, 0.08, 0.02), 'LEFT'); txt('en_r2', 'cozida', 0.085, P.ORANGE, g, (-1.25, -0.2, 0.02), 'LEFT')
        b1 = lbar('en_b1', 1.05, 0.14, (0.8, 0.82, 0.88), g, (-0.6, 0.08, 0.02)); b2 = lbar('en_b2', 1.75, 0.14, P.ORANGE, g, (-0.6, -0.2, 0.02))
        txt('en_n', 'ilustração: a comida cozida é mais fácil de digerir', 0.055, (0.65, 0.67, 0.72), g, (0, -0.4, 0.02))
        items['bars'] = (b1, b2); items['panel'] = g
    elif kind == 'eletricidade':
        g = panel_root('eletricidade', -1.6); plate(g, 2.9, 1.1)
        txt('el_t', 'eletricidade do mundo em 2024', 0.1, (1, 1, 1), g, (0, 0.36, 0.02))
        bgb = B.box('el_bg', (2.4, 0.2, 0.01), (0, 0.06, 0.0), SC.emit_mat('ElFundo', (0.25, 0.27, 0.32), 1.0), RC); bgb.parent = g; bgb.visible_shadow = False
        bf = lbar('el_foss', 2.4 * 0.591, 0.2, P.ORANGE, g, (-1.2, 0.06, 0.01)); items['bars'] = (bf,)
        lt_ = txt('el_v', '59% vem de queimar carvão, gás e petróleo', 0.08, P.ORANGE, g, (0, -0.17, 0.02)); hide(lt_); items['el_v'] = lt_
        txt('el_src', 'fonte: Ember, Global Electricity Review 2025', 0.055, (0.65, 0.67, 0.72), g, (0, -0.4, 0.02))
        items['panel'] = g
    elif kind == 'quinto':
        g = panel_root('quinto', -1.6); plate(g, 2.8, 1.05)
        txt('q_t', 'energia do corpo em repouso', 0.1, (1, 1, 1), g, (0, 0.36, 0.02)); qs = []
        for i in range(5):
            o = B.box(f'q{i}', (0.44, 0.24, 0.01), (-0.96 + i * 0.48, 0.06, 0.0), SC.emit_mat('QCinza', (0.30, 0.32, 0.38), 1.0) if i else SC.emit_mat('QCerebro', (1.0, 0.55, 0.62), 1.6), RC, bevel=0.03)
            o.parent = g; o.visible_shadow = False; qs.append(o)
        q1 = txt('q_lab', '1/5 vai para o cérebro', 0.1, (1.0, 0.65, 0.7), g, (0, -0.2, 0.02)); hide(q1)
        txt('q_n', 'o cérebro é só ~2% do peso do corpo', 0.06, (0.65, 0.67, 0.72), g, (0, -0.4, 0.02))
        items['q'] = (qs, q1); items['panel'] = g

# ------------------------------------------------------------------ Téo
SIT = {'thigh.L': (-85, 0, 0), 'thigh.R': (-85, 0, 0), 'shin.L': (80, 0, 0), 'shin.R': (80, 0, 0), 'spine': (6, 0, 0),
       'upper_arm.L': (-30, 0, -8), 'upper_arm.R': (-30, 0, 8), 'forearm.L': (-50, 0, 0), 'forearm.R': (-50, 0, 0)}
HAND_MOUTH = {'upper_arm.R': (-62, 0, 22), 'forearm.R': (-118, 0, 0)}
POSES = {
    'neutral': dict(SIT, head=(0, 0, 0)),
    'chew': dict(SIT, **HAND_MOUTH, head=(-4, 0, 0)),
    'alarm': dict(SIT, spine=(-6, 0, 0), head=(-12, 0, 0), **{'upper_arm.L': (-75, 0, -35), 'upper_arm.R': (-75, 0, 35), 'forearm.L': (-70, 0, 0), 'forearm.R': (-70, 0, 0)}),
    'relief': dict(SIT, spine=(-4, 0, 0), head=(-8, 0, 6), **{'upper_arm.L': (-20, 0, -10), 'upper_arm.R': (-20, 0, 10), 'forearm.L': (-30, 0, 0), 'forearm.R': (-30, 0, 0)}),
    'think': dict(SIT, spine=(10, 0, 0), head=(-6, 0, 12), **{'upper_arm.R': (-70, 0, 20), 'forearm.R': (-115, 0, 0)}),
    'wave': dict(SIT, head=(-6, 0, -8), **{'upper_arm.R': (-150, 0, 30), 'forearm.R': (-40, 0, 0)}),
    'stand': {'head': (0, 0, 0)},
    'scared_l': {'spine': (4, 0, 0), 'head': (-4, 0, 38), 'upper_arm.L': (-30, 0, -25), 'upper_arm.R': (-30, 0, 25), 'forearm.L': (-60, 0, 0), 'forearm.R': (-60, 0, 0)},
    'scared_r': {'spine': (4, 0, 0), 'head': (-4, 0, -38), 'upper_arm.L': (-30, 0, -25), 'upper_arm.R': (-30, 0, 25), 'forearm.L': (-60, 0, 0), 'forearm.R': (-60, 0, 0)},
}
def teo_anim(mode, teo, f, T):
    r = teo['root']; stand = getattr(shot, 'teo_stand', False)
    r.location = (P.TEO[0], P.TEO[1] - (0.0 if stand else 0.02), (0.0 if stand else 0.47 - teo['hip_z'])) if not stand else (0.0, -0.8, 0.0)
    r.rotation_euler = (0, 0, 0)
    tp = getattr(shot, 't_pose', shot.t0 + 0.2)
    if mode == 'chew':
        seq = [(shot.t0 - 1, POSES['chew'])]; face = 'focus' if int(T * 7.5) % 2 else 'neutral'
        rot, idx, k = S2.pose_seq(seq, T); h = rot['head']; rot['head'] = (h[0] + 5 * math.sin(T * 15.7), h[1], h[2])
        fr_ = rot['forearm.R']; rot['forearm.R'] = (fr_[0] + 6 * math.sin(T * 15.7), fr_[1], fr_[2])
        B.pose(teo, frame=f, **rot); B.set_face(teo, {face: 1.0}, f); return
    if mode == 'scared':
        seq = [(shot.t0 - 1, POSES['stand']), (shot.t0 + 0.4, POSES['scared_l']), (shot.t0 + 1.5, POSES['scared_r']), (shot.t0 + 2.5, POSES['scared_l'])]
        faces = ['neutral', 'alarm', 'alarm', 'alarm']
    else:
        prev = 'chew' if mode in ('alarm', 'relief') else 'neutral'
        seq = [(shot.t0 - 1, POSES[prev]), (tp, POSES[mode])]
        faces = ['neutral', {'alarm': 'alarm', 'relief': 'relief', 'think': 'focus', 'wave': 'relief'}[mode]]
    rot, idx, k = S2.pose_seq(seq, T)
    if mode == 'wave' and T > tp + 0.2: rot['forearm.R'] = (rot['forearm.R'][0] + 25 * math.sin((T - tp) * 9), 0, 0)
    B.pose(teo, frame=f, **rot); kk = min(max(k, 0.0), 1.0); a_, b_ = faces[max(idx - 1, 0)], faces[idx]
    B.set_face(teo, {a_: 1 - kk + (kk if a_ == b_ else 0), **({b_: kk} if a_ != b_ else {})}, f)

def anc_anim(a_, i, f, T):
    talk = 0.5 + 0.5 * math.sin(T * (2.0 + 0.4 * i) + i)
    rot = dict(SIT, head=(-6 + 6 * math.sin(T * 1.3 + i), 0, 10 * math.sin(T * 0.7 + 2 * i)),
               **{'upper_arm.R': (-40 - 40 * talk * (i % 2), 0, 12), 'forearm.R': (-60 - 30 * talk * (i % 2), 0, 0)})
    B.pose(a_, frame=f, **rot); B.set_face(a_, {'relief': 1.0} if (i + int(T * 1.5)) % 3 else {'focus': 1.0}, f)

def snap_pop(T, t_on, t_off=99):
    k = S2.snap(T - t_on) * (1 - S2.snap(T - t_off, back=False)); return max(k, 1e-4)

# ================================================================== animação quadro a quadro
fr = list(shot.frames)
sun = bpy.data.objects.get('Sol')
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4)); lt = T - shot.t0
    c = shot.cam(T)
    if S2.ON: c = S2.cam_fx(c, T, shot)
    cpos = Vector(c['pos'])
    if 'teo' in items: teo_anim(shot.teo, items['teo'], f, T); key(items['teo']['root'], 'location', 'rotation_euler', f=f)
    if 'anc' in items:
        for i, a_ in enumerate(items['anc']):
            r_ = a_['root']; r_.location.z = 0.47 - a_['hip_z']; key(r_, 'location', f=f); anc_anim(a_, i, f, T)
    if 'fire' in items:
        fw = getattr(shot, 'fire', (shot.t0 - 1, 99))
        if fw is None: on = 0.0
        else: on = S2.snap(T - fw[0], 0.3, back=False) * (1 - S2.snap(T - fw[1], 0.17, back=False))
        if K == 'estudio': on = 1.0
        SC.fire_pose(items['fire'], T, f, on=on)
    if hasattr(shot, 'timelapse') and sun:
        u = sstep(*shot.timelapse, T); sun.rotation_euler = Euler((math.radians(70 - 40 * math.sin(math.pi * u)), math.radians(6), math.radians(-80 + 160 * u))); key(sun, 'rotation_euler', f=f)
        sun.data.energy = 2.5 + 2.0 * math.sin(math.pi * u); sun.data.keyframe_insert('energy', frame=f)
    if 'objs' in items:
        for i, o in enumerate(items['objs']):
            k = 0.95 * snap_pop(T, shot.objs[i][0], shot.objs_off); o.scale = (k,) * 3; o.rotation_euler.z = (0.5 if i == 0 else 0) + 0.25 * T; key(o, 'scale', 'rotation_euler', f=f)
    if 'raw' in items:
        for o in (items['raw'], items['cooked']): o.rotation_euler.z = 0.3 * T; key(o, 'rotation_euler', f=f)
    if 'brain' in items:
        br = items['brain']; br['root'].rotation_euler.z = math.pi / 2 + 0.25 * math.sin(T * 0.7); br['root'].rotation_euler.x = math.radians(-8); s_ = 1 + 0.02 * math.sin(T * 5); br['root'].scale = (s_,) * 3; key(br['root'], 'rotation_euler', 'scale', f=f)
        gl_ = 0.0
        if hasattr(shot, 'brain_glow'): gl_ = 0.45 * sstep(shot.brain_glow, shot.brain_glow + 0.4, T)
        if getattr(shot, 'panel', None) and shot.panel[0] == 'quinto': gl_ = 0.18 * sstep(shot.panel[3], shot.panel[3] + 0.3, T)
        set_input(br['mat'], 'Principled BSDF', 'Emission Strength', gl_, f)
    if 'stream' in items:
        t1_, t2_ = shot.food_feed; a0 = Vector((-1.6, 0, 1.05)); a1 = Vector((1.5, 0, 1.4))
        for i, s in enumerate(items['stream']):
            u = ((T - t1_) * 0.9 + i / len(items['stream'])) % 1.0
            p = a0.lerp(a1, u) + Vector((0, 0, 0.9 * math.sin(math.pi * u)))
            vis = sstep(t1_, t1_ + 0.3, T) * math.sin(math.pi * u) ** 0.5
            s.location = p; s.scale = (max(vis, 1e-4),) * 3; key(s, 'location', 'scale', f=f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    cam.location = cpos; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    if shot.panel:
        kind = shot.panel[0]; L = 35.0 / c['lens']; g = items['panel']
        s = 0.85 * L * snap_pop(T, shot.panel[1], shot.panel[2]) / 5
        if kind in ('relogio', 'energia', 'eletricidade', 'quinto'): s *= 1.15
        if kind == 'card_top': s *= 0.62
        elif kind in ('card', 'card_fade', 'cta'): s *= 0.8
        g.scale = (s,) * 3; g.location = (0.0, g['y0'] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if kind == 'relogio':
            t1_, t2_ = shot.panel[3]; frac = shot.panel[4] * sstep(t1_, t2_, T); n = frac * 48
            for i, sg in enumerate(items['segs']):
                k = 1.0 if i < int(n) else (1e-4 if i > n else max(n - i, 1e-4)); sg.scale = (1, k, 1) if k > 1e-3 else (1e-4,) * 3; key(sg, 'scale', f=f)
        if kind in ('card', 'card_top', 'card_fade', 'cta'):
            pt = items['card']; tk = snap_pop(T, shot.panel[3] if kind in ('card', 'cta') else shot.panel[1] + 0.3)
            pt['tag'].scale = (tk,) * 3; key(pt['tag'], 'scale', f=f)
            if kind == 'card_fade':
                tf = shot.panel[3]; parts_ = [pt['avatar'][0], pt['avatar'][1], pt['handle']] + pt['lines'] + [pt['like'], pt['tag']]
                for j, o in enumerate(parts_):
                    k = max(1 - S2.snap(T - (tf + 0.12 * j), 0.17, back=False), 1e-4); o.scale = (k,) * 3; key(o, 'scale', f=f)
            if kind == 'cta':
                items['cursor'].scale = ((1.0 if int(T * 2.5) % 2 else 1e-4),) * 3; key(items['cursor'], 'scale', f=f)
                k = snap_pop(T, shot.panel[3]); items['pode'].scale = (k,) * 3; key(items['pode'], 'scale', f=f)
        if kind == 'energia':
            t1_, t2_ = shot.panel[3]
            for b, tt in zip(items['bars'], (t1_, t2_)): k = sstep(tt - 0.5, tt + 0.1, T); b.scale = (max(k, 1e-4), 1, 1); key(b, 'scale', f=f)
        if kind == 'eletricidade':
            t1_, t2_ = shot.panel[3]; k = sstep(t1_, t2_, T); b = items['bars'][0]; b.scale = (max(k, 1e-4), 1, 1); key(b, 'scale', f=f)
            items['el_v'].scale = (snap_pop(T, t2_),) * 3; key(items['el_v'], 'scale', f=f)
        if kind == 'quinto':
            qs, q1 = items['q']; tq = shot.panel[3]
            for i, o in enumerate(qs):
                k = 1 + (0.25 * S2.snap(T - tq) if i == 0 else 0); o.scale = (k, k, 1); key(o, 'scale', f=f)
            q1.scale = (snap_pop(T, tq),) * 3; key(q1, 'scale', f=f)
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
if S2.ON:
    _c0 = shot.cam(shot.t0); _tp = Vector(P.TEO) + Vector((0, 0, 1.05)) if hasattr(shot, 'teo') else Vector(_c0['look'])
    S2.finish(sc, cam, focus_dist=(Vector(_c0['pos']) - _tp).length, f_stop=float(os.environ.get('S2_FSTOP', '2.2'))); S2.motion_blur(sc)
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
