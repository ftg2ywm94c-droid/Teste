"""Vídeo 09: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep09/render.py -- --shot C1 [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep09/frames/<plano>/NNNN.png (final) ou v2/ep09/preview/<plano>/ (prévia). Retomável."""
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
C9 = B.new_coll('Ep09')
assert K in ('rua', 'estudio'), 'planos de trailer são gerados por v2/ep09/trailer.py'
# ================================================================== cenários
if K == 'rua':
    items.update(SC.build_rua9())
    if hasattr(shot, 'car'): SC.place_car(items['car'], *shot.car)
else:
    items.update(SC.build_lab())
    SC.place_car(items['car'], -40.0, 0.0, 0.0)
if hasattr(shot, 'teo'):
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
    if getattr(shot, 'cafe', False):
        items['gesso'] = SC.cast(teo, 'L')
        if shot.teo == 'eat':
            hd_ = SC.hotdog('hotdog', C9); hd_.parent = teo['arm']; hd_.parent_type = 'BONE'; hd_.parent_bone = 'forearm.R'
            hd_.location = (0.0, 0.05, 0.0); hd_.rotation_euler = (0, 0, math.radians(90)); items['hotdog'] = hd_
if getattr(shot, 'dummy', False) or getattr(shot, 'dummy_roof', False):
    items['dummy'] = SC.build_dummy('Boneco', B.new_coll('BonecoCol'))
if getattr(shot, 'armored', None):
    items['arm9'] = SC.build_armored('Blindado', B.new_coll('BlindadoCol'))
    sp = bpy.data.lights.new('Holofote', 'SPOT'); sp.energy = 0.0; sp.spot_size = math.radians(40); sp.spot_blend = 0.5; sp.color = (1.0, 0.93, 0.85)
    so = B.link(bpy.data.objects.new('Holofote', sp), C9); so.location = (0.6, -2.6, 4.2); so.rotation_euler = look_rot((0.6, -2.6, 4.2), (0, 0, 1.0)); items['spot'] = sp
    if hasattr(shot, 'compare'):
        t2 = B.build_character('TeoComp', B.TEO, B.new_coll('TeoCompCol')); t2['root'].location = (1.0, 0.0, 0.0); t2['root'].scale = (1e-4,) * 3; items['teo2'] = t2
if hasattr(shot, 'floors'):
    for i in range(1, 5):
        z_ = 0.15 + i * 3.2 + 1.5; t_on = shot.floors[0] + (shot.floors[1] - shot.floors[0]) * (i - 1) / 3
        items[f'lbl_andar{i}'] = (bill(f'andar{i}', f'{i}º andar', (23.6, P.BLD_Y0 - 0.6, z_), 1.1 if i == 4 else 0.8, P.YEL if i == 4 else P.WHITE), t_on, 99, (lambda p: (lambda T: p))((23.6, P.BLD_Y0 - 0.6, z_)))
if hasattr(shot, 'button'):
    bt = B.link(bpy.data.objects.new('botao', None), RC); bt.location = (21.75, 2.7, 1.75)
    c_ = bt.constraints.new('COPY_ROTATION'); c_.target = cam
    tt = txt('botao_txt', 'TENTAR DE NOVO', 0.16, (0.04, 0.04, 0.04), bt, (0, 0, 0.03)); w_ = text_width(tt)
    pl = B.box('botao_placa', (w_ + 0.36, 0.42, 0.04), (0, 0, 0), SC.emit_mat('BotaoAmarelo', P.YEL, 1.6), RC, bevel=0.12, seg=4); pl.parent = bt; pl.visible_shadow = False
    sh_ = B.box('botao_sombra', (w_ + 0.36, 0.42, 0.04), (0.03, -0.04, -0.03), B.mat_basic('BotaoSombra', (0.0, 0.0, 0.0), 0.8, alpha=0.6), RC, bevel=0.12, seg=4); sh_.parent = bt; sh_.visible_shadow = False
    bt.scale = (1e-4,) * 3; items['button'] = bt
for m in bpy.data.materials: m.cycles.emission_sampling = 'NONE'
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)
if getattr(shot, 'dim', 0): sc.view_settings.exposure -= 1.6 * shot.dim
if hasattr(shot, 'flash'):
    fl = B.box('flash', (4.0, 4.0, 0.001), (0, 0, 0), SC.emit_mat('Flash', (1.0, 1.0, 1.0), 6.0), RC); fl.parent = cam; fl.location = (0, 0, -0.3); fl.visible_shadow = False; fl.scale = (1e-4,) * 3; items['flash'] = fl

# ------------------------------------------------------------------ painéis presos à câmera
def panel_root(name, y, z=-5.0, x=0.0):
    g = B.link(bpy.data.objects.new(name, None), RC); g.parent = cam; g.location = (x, y, z); g.scale = (1e-4,) * 3; g['y0'] = y; g['x0'] = x; return g
def plate(g, w, h, alpha=0.88, col=(0.03, 0.035, 0.05), name=None):
    p = B.box((name or g.name) + '_placa', (w, h, 0.01), (0, 0, -0.02), B.mat_basic('PainelFundo_%.2f' % col[0], col, 0.6, alpha=alpha), RC, bevel=0.08)
    p.parent = g; p.visible_shadow = False; return p
def lbar(name, w, h, col, g, loc, emit=1.3):
    o = B.box(name, (w, h, 0.01), (0, 0, 0), SC.emit_mat('Barra_' + name, col, emit), RC)
    for v in o.data.vertices: v.co.x += w / 2
    o.parent = g; o.location = loc; o.visible_shadow = False; o.scale = (1e-4, 1, 1); return o
def hide(o): o.scale = (1e-4,) * 3
def person_icon(name, g, loc, mat):
    b_ = B.capsule(name + '_c', 0.065, 0.07, mat, RC); b_.parent = g; b_.location = (loc[0], loc[1] - 0.09, loc[2]); b_.rotation_euler = (math.radians(90), 0, 0); b_.visible_shadow = False
    h_ = B.sphere(name + '_h', 0.06, (0, 0, 0), mat, RC, seg=16); h_.parent = g; h_.location = (loc[0], loc[1] + 0.11, loc[2]); h_.visible_shadow = False
    return (b_, h_)

def comment_card(name, y, handle='@você', lines=('missão:', ''), tag='comenta a próxima missão'):
    g = panel_root(name, y); parts = {}
    parts['plate'] = plate(g, 3.4, 1.35, alpha=0.95, col=(0.14, 0.14, 0.16))
    av = B.cyl(name + '_av', 0.3, 0.004, (-1.25, 0.14, 0.02), SC.emit_mat('AvatarCinza', (0.35, 0.37, 0.42), 1.0), RC, seg=48); av.parent = g; av.visible_shadow = False
    ring = B.cyl(name + '_aro', 0.325, 0.004, (-1.25, 0.14, 0.014), SC.emit_mat('AroAvatar', (1.0, 0.55, 0.12), 2.0), RC, seg=48); ring.parent = g; ring.visible_shadow = False
    txt('av_q', '?', 0.3, (1, 1, 1), g, (-1.25, 0.1, 0.03))
    parts['handle'] = txt(name + '_handle', handle, 0.125, (0.78, 0.80, 0.86), g, (-0.8, 0.4, 0.02), 'LEFT')
    parts['lines'] = [txt(name + f'_l{i}', ln, 0.16, (1, 1, 1), g, (-0.8, 0.13 - i * 0.24, 0.02), 'LEFT') for i, ln in enumerate(lines)]
    tg = B.link(bpy.data.objects.new(name + '_tag', None), RC); tg.parent = g; tg.location = (0, 0.92, 0.0)
    tt_ = txt(name + '_tagtxt', tag, 0.12, (0.05, 0.05, 0.05), tg, (0, 0, 0.03)); w = text_width(tt_)
    pl_ = B.box(name + '_tagpl', (w + 0.28, 0.26, 0.01), (0, 0, 0), SC.emit_mat('TagAmarela', P.YEL, 1.4), RC, bevel=0.1); pl_.parent = tg; pl_.visible_shadow = False
    hide(tg); parts['tag'] = tg
    return g, parts

if hasattr(shot, 'hud'):
    hg = panel_root('hud', 1.85, x=-0.62); plate(hg, 1.9, 0.5, alpha=0.75)
    hm = SC.emit_mat('Coracao', (1.0, 0.18, 0.2), 2.0)
    for sx in (1, -1):
        o = B.sphere(f'cor{sx}', 0.065, (-0.72 + sx * 0.045, 0.03, 0.02), hm, RC, seg=16); o.parent = hg; o.visible_shadow = False
    o = B.box('cor_v', (0.12, 0.12, 0.02), (-0.72, -0.03, 0.02), hm, RC, rot=(0, 0, math.radians(45))); o.parent = hg; o.visible_shadow = False
    bgb = B.box('hud_bg', (1.2, 0.14, 0.01), (0.03, 0.0, 0.0), SC.emit_mat('HudFundo', (0.22, 0.23, 0.27), 1.0), RC); bgb.parent = hg; bgb.visible_shadow = False
    hgreen = lbar('hud_g', 1.2, 0.14, P.GREEN, hg, (-0.57, 0.0, 0.01)); hred = lbar('hud_r', 1.2, 0.14, P.RED, hg, (-0.57, 0.0, 0.012))
    nr = txt('hud_nr', 'não regenera', 0.075, P.RED, hg, (0.03, -0.17, 0.02)); hide(nr)
    items['hud'] = dict(g=hg, green=hgreen, red=hred, nr=nr)

if shot.panel:
    kind = shot.panel[0]
    if kind == 'risco':
        g = panel_root('risco', 1.62); plate(g, 2.8, 1.15)
        txt('ri_v', f'{shot.panel[3]} km/h', 0.2, (1, 1, 1), g, (-0.85, 0.3, 0.02))
        txt('ri_t', 'risco de morte do pedestre', 0.075, (0.75, 0.77, 0.83), g, (0.45, 0.33, 0.02))
        gm = SC.emit_mat('PessoaCinza', (0.45, 0.47, 0.53), 1.0); rm = SC.emit_mat('PessoaVermelha', P.RED, 1.8); icons = []
        for i in range(10):
            x_ = -1.08 + i * 0.24
            a_ = person_icon(f'pg{i}', g, (x_, -0.12, 0.0), gm); b_ = person_icon(f'pr{i}', g, (x_, -0.12, 0.01), rm)
            for o in b_: hide(o)
            icons.append(b_)
        res = txt('ri_res', '1 em cada 10' if shot.panel[5] == 1 else 'metade', 0.13, P.RED, g, (0.6, 0.12, 0.02)); hide(res)
        txt('ri_src', 'fonte: AAA Foundation (2011), dados dos EUA', 0.055, (0.65, 0.67, 0.72), g, (0, -0.47, 0.02))
        items['icons'] = icons; items['res'] = res; items['panel'] = g
    elif kind == 'queda':
        g = panel_root('queda', 1.45); plate(g, 2.8, 0.95)
        txt('qd_t', '~4 andares (12 a 15 m)', 0.14, (1, 1, 1), g, (0, 0.22, 0.02))
        r_ = txt('qd_r', 'cerca de metade não sobrevive', 0.11, P.RED, g, (0, -0.08, 0.02)); hide(r_); items['res'] = r_
        txt('qd_src', 'estimativa clássica de estudos de trauma (adultos)', 0.055, (0.65, 0.67, 0.72), g, (0, -0.34, 0.02))
        items['panel'] = g
    elif kind == 'semanas':
        g = panel_root('semanas', 1.62); plate(g, 2.8, 1.0)
        txt('se_t', 'osso quebrado: tempo para colar', 0.095, (1, 1, 1), g, (0, 0.33, 0.02)); wk = []
        for i in range(8):
            bg_ = B.box(f'sem_bg{i}', (0.26, 0.26, 0.01), (-0.98 + i * 0.28, 0.04, 0.0), SC.emit_mat('SemFundo', (0.25, 0.27, 0.32), 1.0), RC, bevel=0.03); bg_.parent = g; bg_.visible_shadow = False
            o = B.box(f'sem{i}', (0.26, 0.26, 0.01), (-0.98 + i * 0.28, 0.04, 0.01), SC.emit_mat('SemCheia' if i < 6 else 'SemCheia2', P.GREEN if i < 6 else P.YEL, 1.6), RC, bevel=0.03); o.parent = g; o.visible_shadow = False; hide(o); wk.append(o)
            txt(f'sem_n{i}', str(i + 1), 0.07, (1, 1, 1), g, (-0.98 + i * 0.28, 0.04, 0.03))
        r_ = txt('se_r', '6 a 8 semanas, em média', 0.11, P.YEL, g, (0, -0.24, 0.02)); hide(r_); items['res'] = r_
        txt('se_src', 'ossos grandes podem levar meses', 0.055, (0.65, 0.67, 0.72), g, (0, -0.42, 0.02))
        items['weeks'] = wk; items['panel'] = g
    elif kind == 'equipe':
        g = panel_root('equipe', 1.62); plate(g, 2.6, 1.15); rows = []
        for i, (lab, col) in enumerate((('uma artista', P.YEL), ('um cirurgião de trauma', P.WHITE), ('um investigador de acidentes', P.WHITE))):
            rg = B.link(bpy.data.objects.new(f'eq{i}', None), RC); rg.parent = g; rg.location = (0, 0.3 - i * 0.3, 0.0)
            txt(f'eq_t{i}', lab, 0.16, col, rg, (0, 0, 0.02)); hide(rg); rows.append(rg)
        items['rows'] = rows; items['panel'] = g
    elif kind == 'cta':
        g, parts = comment_card('card', 1.45)
        cur = txt('cursor', '|', 0.17, P.YEL, g, (0.05, 0.13, 0.02)); items['cursor'] = cur
        p2 = B.link(bpy.data.objects.new('pode_ser', None), RC); p2.parent = g; p2.location = (0, -0.9, 0.0)
        txt('pode_txt', 'a gente testa na vida real!', 0.14, P.YEL, p2, (0, 0, 0.03)); hide(p2); items['pode'] = p2
        items['card'] = parts; items['panel'] = g

# ------------------------------------------------------------------ poses
WALK_ARMS = {'upper_arm.L': (0, 0, -6), 'upper_arm.R': (0, 0, 6)}
POSES = {
    'stand': {'head': (0, 0, 0), 'upper_arm.L': (0, 0, -6), 'upper_arm.R': (0, 0, 6), 'forearm.L': (-12, 0, 0), 'forearm.R': (-12, 0, 0)},
    'lying': {'head': (-10, 0, 20), 'upper_arm.L': (0, 0, -55), 'upper_arm.R': (0, 0, 50), 'forearm.L': (-20, 0, 0), 'forearm.R': (-30, 0, 0), 'thigh.L': (0, 0, -8), 'thigh.R': (-10, 0, 8), 'shin.R': (20, 0, 0)},
    'think': {'spine': (6, 0, 0), 'head': (-8, 0, 14), 'upper_arm.L': (0, 0, -6), 'forearm.L': (-12, 0, 0), 'upper_arm.R': (-70, 0, 20), 'forearm.R': (-115, 0, 0)},
    'shrug': {'head': (-6, 0, 10), 'upper_arm.L': (-15, 0, -40), 'upper_arm.R': (-15, 0, 40), 'forearm.L': (-85, 0, 0), 'forearm.R': (-85, 0, 0)},
    'wave': {'head': (-6, 0, -8), 'upper_arm.L': (0, 0, -6), 'forearm.L': (-12, 0, 0), 'upper_arm.R': (-150, 0, 30), 'forearm.R': (-40, 0, 0)},
    'scared': {'spine': (6, 0, 0), 'head': (12, 0, 0), 'upper_arm.L': (-30, 0, -35), 'upper_arm.R': (-30, 0, 35), 'forearm.L': (-50, 0, 0), 'forearm.R': (-50, 0, 0)},
}
SIT = {'thigh.L': (-85, 0, 0), 'thigh.R': (-85, 0, 0), 'shin.L': (80, 0, 0), 'shin.R': (80, 0, 0), 'spine': (6, 0, 0)}
POSES['sit_hold'] = dict(SIT, head=(-4, 0, 0), **{'upper_arm.L': (-35, 0, -10), 'forearm.L': (-60, 0, 0), 'upper_arm.R': (-40, 0, 10), 'forearm.R': (-70, 0, 0)})
POSES['sit_eat'] = dict(SIT, head=(-4, 0, 0), **{'upper_arm.L': (-35, 0, -10), 'forearm.L': (-60, 0, 0), 'upper_arm.R': (-62, 0, 22), 'forearm.R': (-118, 0, 0)})
POSES['sit_sad'] = dict(SIT, spine=(14, 0, 0), head=(22, 0, -10), **{'upper_arm.L': (-50, 0, -10), 'forearm.L': (-75, 0, 0), 'upper_arm.R': (-20, 0, 10), 'forearm.R': (-40, 0, 0)})
CHAIR = (P.CAFE[0] + 0.62 * math.cos(math.radians(220)), P.CAFE[1] + 0.62 * math.sin(math.radians(220)))

def walk_rot(T, base):
    s = math.sin(T * 2 * math.pi * 1.1); r = dict(base)
    r.update({'thigh.L': (-22 * s, 0, 0), 'thigh.R': (22 * s, 0, 0), 'shin.L': (max(0, 30 * math.sin(T * 2 * math.pi * 1.1 + 1.6)), 0, 0), 'shin.R': (max(0, -30 * math.sin(T * 2 * math.pi * 1.1 + 1.6)), 0, 0),
              'upper_arm.L': (18 * s, 0, -6), 'upper_arm.R': (-18 * s, 0, 6)})
    return r

def teo_anim(mode, teo, f, T):
    r = teo['root']; tp = getattr(shot, 't_pose', shot.t0 + 0.2); face = {'neutral': 1.0}
    r.rotation_euler = (0, 0, 0); r.location = P.TEO
    if mode == 'game_getup':
        tu, tw, tr = shot.t_up, shot.t_walk, shot.t_real
        up = S2.snap(T - tu, 0.30) if T < tr else 0.0
        r.location = (P.ROAD[0] + (0.9 * sstep(tw, tr, T) if T < tr else 0.0), P.ROAD[1], 0.13 * (1 - min(up, 1.0)))
        r.rotation_euler = (math.radians(-90) * (1 - up), 0, 0)
        if tw <= T < tr: rot = walk_rot(T, POSES['stand'])
        else: rot = S2.blend(POSES['lying'], POSES['stand'], min(max(up, 0), 1))
        face = {'relief': 1.0} if tu <= T < tr else ({'alarm': 1.0} if T >= tr else {'neutral': 1.0})
        rot, _, _ = S2.pose_seq([(shot.t0 - 1, rot)], T, breath=0.0 if T >= tr or T < tu else 1.0)
    elif mode in ('eat', 'sad'):
        r.location = (CHAIR[0], CHAIR[1], 0.64 - teo['hip_z']); r.rotation_euler = (0, 0, math.atan2(19.2 - CHAIR[0], -(2.6 - CHAIR[1])))
        if mode == 'eat':
            seq = [(shot.t0 - 1, POSES['sit_hold']), (shot.t_eat - 0.3, POSES['sit_eat'])]
            rot, idx, k = S2.pose_seq(seq, T)
            if T > shot.t_eat:
                h = rot['head']; rot['head'] = (h[0] + 5 * math.sin(T * 15.7), h[1], h[2]); face = {'focus' if int(T * 7.5) % 2 else 'neutral': 1.0}
            if T > shot.t_eat + 0.8: face = {'alarm': 1.0}
        else:
            rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['sit_hold']), (tp, POSES['sit_sad'])], T); face = {'focus': 1.0}
    elif mode == 'think':
        rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['stand']), (tp, POSES['think'])], T); face = {'focus': 1.0}
    elif mode == 'stand':
        rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['stand']), (shot.button[1] + 0.1, POSES['shrug'])], T)
        face = {'relief': 1.0} if T < shot.button[1] else {'alarm': 1.0}
    elif mode == 'wave':
        rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['shrug']), (tp, POSES['wave'])], T); face = {'relief': 1.0}
        if T > tp + 0.2: rot['forearm.R'] = (rot['forearm.R'][0] + 25 * math.sin((T - tp) * 9), 0, 0)
    B.pose(teo, frame=f, **rot); B.set_face(teo, face, f)

def snap_pop(T, t_on, t_off=99):
    k = S2.snap(T - t_on) * (1 - S2.snap(T - t_off, back=False)); return max(k, 1e-4)

# luzes do estúdio: na silhueta ficam baixas até o holofote acender
LIGHTS0 = {l.name: l.energy for l in bpy.data.lights if l.name not in ('Holofote',)}

# ================================================================== animação quadro a quadro
fr = list(shot.frames)
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4)); lt = T - shot.t0
    c = shot.cam(T)
    if S2.ON: c = S2.cam_fx(c, T, shot)
    cpos = Vector(c['pos'])
    if 'teo' in items: teo_anim(shot.teo, items['teo'], f, T); key(items['teo']['root'], 'location', 'rotation_euler', f=f)
    if 'dummy' in items:
        d_ = items['dummy']; r_ = d_['root']
        if getattr(shot, 'dummy_roof', False):
            r_.location = (21.0, P.BLD_Y0 - 0.2, 0.15 + 4 * 3.2 + 0.21); r_.rotation_euler = (0, 0, 0)
            rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['scared'])], T); B.set_face(d_, {'alarm': 1.0}, f)
        else:
            t_hit = shot.drive[1]; down = S2.snap(T - t_hit - 0.05, 0.25, back=False)
            r_.location = (0.0, 0.0, 0.13 * down); r_.rotation_euler = (math.radians(-90) * down, 0, math.radians(-90) * down)
            rot = S2.blend(POSES['stand'], POSES['lying'], down); rot, _, _ = S2.pose_seq([(shot.t0 - 1, rot)], T, breath=0.0); B.set_face(d_, {'neutral': 1.0}, f)
        B.pose(d_, frame=f, **rot); key(r_, 'location', 'rotation_euler', f=f)
    if hasattr(shot, 'drive'):
        t_go, t_hit, kmh = shot.drive; v = 5.0 if kmh < 50 else 10.0
        x_ = -2.55 - v * max(t_hit - T, 0.0); SC.place_car(items['car'], x_, -0.15, 0.0); key(items['car']['root'], 'location', f=f)
    if 'flash' in items:
        k = math.exp(-max(T - shot.flash, 0) / 0.08) if T >= shot.flash else 0.0; items['flash'].scale = ((k if k > 0.02 else 1e-4),) * 3; key(items['flash'], 'scale', f=f)
        sp_ = (math.exp(-max(T - shot.flash, 0) / 0.15) if T >= shot.flash else 0.0)
    if 'arm9' in items:
        ar = items['arm9']; ar['root'].location = (0, 0, 0); ar['root'].rotation_euler = (0, 0, math.radians(18 * math.sin(T * 0.6)))
        rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['stand'])], T); B.pose(ar, frame=f, **rot); B.set_face(ar, {'neutral': 1.0}, f); key(ar['root'], 'rotation_euler', f=f)
        for i, bg_ in enumerate(ar['bags']):
            s_ = 1 + 0.05 * math.sin(T * 3 + i); bg_.scale = (s_, s_ * 0.75, s_ * 0.85); key(bg_, 'scale', f=f)
        lit = 1.0 if shot.armored == 'lit' else sstep(shot.t_light, shot.t_light + 0.3, T)
        items['spot'].energy = 900 * lit; items['spot'].keyframe_insert('energy', frame=f)
        for n_, e0 in LIGHTS0.items():
            l_ = bpy.data.lights[n_]; l_.energy = e0 * (0.12 + 0.88 * lit) if n_ != 'Recorte' else e0 * 1.4; l_.keyframe_insert('energy', frame=f)
        if 'teo2' in items:
            t2 = items['teo2']; k = snap_pop(T, shot.compare); t2['root'].scale = (k,) * 3; key(t2['root'], 'scale', f=f)
            rot, _, _ = S2.pose_seq([(shot.t0 - 1, POSES['stand'])], T); B.pose(t2, frame=f, **rot); B.set_face(t2, {'relief': 1.0}, f)
    if 'button' in items:
        t_on, t_br = shot.button; k = snap_pop(T, t_on)
        brk = sstep(t_br, t_br + 0.35, T); bt = items['button']
        bt.scale = (max(k * (1 - brk), 1e-4),) * 3; bt.location = (21.75, 2.7, 1.75 - 0.6 * brk * brk); key(bt, 'scale', 'location', f=f)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    cam.location = cpos; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    L = 35.0 / c['lens']
    if 'hud' in items:
        hd = items['hud']; g = hd['g']; t_on, t_off, mode = shot.hud
        g.scale = (0.55 * L * snap_pop(T, t_on, t_off) / 5,) * 3; g.location = (g['x0'] * L / 5, g['y0'] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if mode == 'game_getup':
            if T < shot.t_up: gv, rv = 0.0, 0.18
            elif T < shot.t_real: gv, rv = 0.18 + 0.82 * sstep(shot.t_up, shot.t_up + 0.5, T), 0.0
            else: gv, rv = 0.0, max(0.18 * (1 - sstep(shot.t_real, shot.t_real + 0.3, T)), 0.0)
        elif mode == 'full': gv, rv = 1.0, 0.0
        else:
            gv = 0.0; rv = 0.18 + 0.1 * math.exp(-((T - shot.t_eat - 0.3) / 0.25) ** 2)
        hd['green'].scale = (max(gv, 1e-4), 1, 1); hd['red'].scale = (max(rv, 1e-4), 1, 1); key(hd['green'], 'scale', f=f); key(hd['red'], 'scale', f=f)
        nr_on = (mode == 'eat' and T > shot.t_eat + 0.8) or (mode == 'game_getup' and T > shot.t_real + 0.1)
        hd['nr'].scale = ((snap_pop(T, (shot.t_eat + 0.8) if mode == 'eat' else shot.t_real + 0.1) if nr_on else 1e-4),) * 3; key(hd['nr'], 'scale', f=f)
    if shot.panel:
        kind = shot.panel[0]; g = items['panel']
        s = 0.85 * L * snap_pop(T, shot.panel[1], shot.panel[2]) / 5
        if kind != 'cta': s *= 1.15
        else: s *= 0.8
        g.scale = (s,) * 3; g.location = (0.0, g['y0'] * L / 5, -1.0); key(g, 'scale', 'location', f=f)
        if kind == 'risco':
            n_red, t_r = shot.panel[5], shot.panel[4]
            for i, ic in enumerate(items['icons']):
                k = snap_pop(T, t_r + 0.06 * i) if i < n_red else 1e-4
                for o in ic: o.scale = (k,) * 3; key(o, 'scale', f=f)
            items['res'].scale = (snap_pop(T, t_r + 0.06 * n_red),) * 3; key(items['res'], 'scale', f=f)
        if kind == 'queda':
            items['res'].scale = (snap_pop(T, shot.panel[3]),) * 3; key(items['res'], 'scale', f=f)
        if kind == 'semanas':
            t1_, t2_ = shot.panel[3]
            for i, o in enumerate(items['weeks']):
                k = snap_pop(T, t1_ - 1.6 + 0.2 * i) if i < 6 else snap_pop(T, t2_ - 0.3 + 0.25 * (i - 6))
                o.scale = (k,) * 3; key(o, 'scale', f=f)
            items['res'].scale = (snap_pop(T, t2_),) * 3; key(items['res'], 'scale', f=f)
        if kind == 'equipe':
            for i, rg in enumerate(items['rows']): rg.scale = (snap_pop(T, shot.panel[3][i]),) * 3; key(rg, 'scale', f=f)
        if kind == 'cta':
            pt = items['card']; pt['tag'].scale = (snap_pop(T, shot.panel[1] + 0.3),) * 3; key(pt['tag'], 'scale', f=f)
            items['cursor'].scale = ((1.0 if int(T * 2.5) % 2 else 1e-4),) * 3; key(items['cursor'], 'scale', f=f)
            k = snap_pop(T, shot.panel[3]); items['pode'].scale = (k,) * 3; key(items['pode'], 'scale', f=f)
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
    _c0 = shot.cam(shot.t0); _tp = Vector(_c0['look'])
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
