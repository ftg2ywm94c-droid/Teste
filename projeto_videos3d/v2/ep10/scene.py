"""Cenários do vídeo 10 (e se o Brasil cobrasse menos impostos?).
Tudo acontece num palco escuro em degradê (estúdio do vídeo 08 com outra cor). Os números, gráficos e textos são uma camada de motion
graphics separada (v2/ep10/mograph.py); aqui ficam só os objetos 3D.
Objetos: cofre, moedas, calendário de folhas, cadeado, pizza do PIB, colunas, pacote com etiqueta de preço que se divide,
bomba de combustível, colunas de arrecadação, balança, café, xícara e tesoura. Nada de bandeiras, partidos, políticos ou logos."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Euler, Matrix
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S8 = _load('scene08', os.path.join(HERE, '..', 'ep08', 'scene.py'))
emit_mat, lathe = S8.emit_mat, S8.lathe

YEL, RED, WHITE, TEAL, GREEN = (1.0, 0.80, 0.08), (0.95, 0.20, 0.14), (0.95, 0.95, 0.95), (0.10, 0.62, 0.66), (0.30, 0.85, 0.40)
SUIT = dict(B.TEO, shirt=(0.10, 0.11, 0.14), pants=(0.10, 0.11, 0.14), shoes=(0.08, 0.06, 0.05), cap=None, hair=(0.22, 0.14, 0.08))

def palco():
    R = S8.build_estudio(top=(0.035, 0.07, 0.13), bottom=(0.006, 0.010, 0.02))
    return R

def gold(): return B.mat_basic('Ouro', (1.0, 0.72, 0.22), 0.25, metal=1.0)

# ------------------------------------------------------------------ moedas
def coins(n, C, r=0.075, seed=3):
    m = gold(); out = []
    for i in range(n):
        o = B.cyl(f'moeda{i}', r, 0.018, (0, 0, -50), m, C, seg=28); o.rotation_euler = (math.radians(90), 0, 0); out.append(o)
    return out

# ------------------------------------------------------------------ cofre
def cofre(name, C, loc=(0, 0, 0), s=1.0, hole=False):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc; root.scale = (s, s, s)
    body_m = B.mat_basic('CofreCorpo', (0.16, 0.30, 0.30), 0.35, metal=0.6); door_m = B.mat_basic('CofrePorta', (0.20, 0.36, 0.36), 0.3, metal=0.6)
    steel = B.mat_basic('CofreAco', (0.75, 0.76, 0.78), 0.2, metal=1.0)
    def P(o): o.parent = root; return o
    P(B.box(name + '_corpo', (1.5, 1.2, 1.7), (0, 0, 0.85), body_m, C, bevel=0.06, seg=3))
    P(B.box(name + '_porta', (1.22, 0.06, 1.42), (0, -0.62, 0.85), door_m, C, bevel=0.03))
    P(B.cyl(name + '_disco', 0.17, 0.06, (0.25, -0.67, 1.05), steel, C, seg=32, rot=(math.radians(90), 0, 0)))
    for k in range(3):
        a = k * math.pi / 3; P(B.cyl(name + '_raio', 0.022, 0.42, (-0.28, -0.69, 0.75), steel, C, seg=12, rot=(0, a, 0)))
    P(B.cyl(name + '_cubo', 0.06, 0.08, (-0.28, -0.69, 0.75), steel, C, seg=16, rot=(math.radians(90), 0, 0)))
    P(B.box(name + '_fenda', (0.7, 0.14, 0.03), (0, 0, 1.705), B.mat_basic('Fenda', (0.01, 0.01, 0.01), 0.9), C))
    for x in (-0.6, 0.6):
        P(B.box(name + '_pe', (0.18, 0.18, 0.1), (x, 0.4, -0.04), steel, C)); P(B.box(name + '_pe', (0.18, 0.18, 0.1), (x, -0.4, -0.04), steel, C))
    hole_o = None
    if hole:
        hole_o = P(B.cyl(name + '_rombo', 0.32, 0.03, (0.76, -0.1, 0.35), B.mat_basic('Rombo', (0.0, 0.0, 0.0), 1.0), C, seg=10, rot=(0, math.radians(90), 0)))
        hole_o.scale = (1.0, 1.0, 1.0)
        for i in range(7):
            a = i / 7 * 2 * math.pi; P(B.box(name + '_lasca', (0.05, 0.12, 0.03), (0.77, -0.1 + 0.36 * math.cos(a), 0.35 + 0.36 * math.sin(a)), body_m, C, rot=(a, 0, 0)))
    return dict(root=root, hole=hole_o)

# ------------------------------------------------------------------ texto 3D simples
FONT = None
def txt3d(name, body, size, color, C, loc=(0, 0, 0), rot=(math.radians(90), 0, 0), emit=0.0, extrude=0.004):
    global FONT
    FONT = FONT or bpy.data.fonts.load(B.FONT, check_existing=True)
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = FONT; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = extrude
    o = B.link(bpy.data.objects.new(name, cu), C); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(B.mat_basic('T3_%.2f%.2f%.2f' % color, color, 0.5, emit=color if emit else None, emit_s=emit)); return o

# ------------------------------------------------------------------ calendário de folhas
MESES = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN']
def calendario(name, C, loc=(0, 0, 0), s=1.0, months=MESES, day=None):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc; root.scale = (s, s, s)
    paper = B.mat_basic('Papel', (0.96, 0.95, 0.92), 0.8); band = B.mat_basic('FaixaCal', (0.90, 0.18, 0.14), 0.6)
    base = B.box(name + '_base', (1.0, 0.25, 0.12), (0, 0.05, 0.06), B.mat_basic('BaseCal', (0.12, 0.12, 0.14), 0.6), C, bevel=0.03); base.parent = root
    pages = []
    for i, mname in enumerate(months):
        pv = B.link(bpy.data.objects.new(f'{name}_piv{i}', None), C); pv.parent = root; pv.location = (0, -0.02 * (len(months) - 1 - i), 1.32)   # gira pela argola de cima
        pg = B.box(f'{name}_pag{i}', (0.92, 0.012, 1.18), (0, 0, -0.62), paper, C); pg.parent = pv
        bd = B.box(f'{name}_band{i}', (0.92, 0.014, 0.26), (0, -0.002, -0.16), band, C); bd.parent = pv
        t1 = txt3d(f'{name}_mes{i}', mname, 0.17, WHITE, C, (0, -0.012, -0.16)); t1.parent = pv
        if day and i == len(months) - 1:
            t2 = txt3d(f'{name}_dia{i}', day, 0.5, (0.12, 0.12, 0.14), C, (0, -0.012, -0.72)); t2.parent = pv
        pages.append(pv)
    for k in range(2):
        r_ = B.cyl(f'{name}_argola{k}', 0.035, 0.12, ((-0.28 + 0.56 * k), -0.05, 1.32), B.mat_basic('Argola', (0.7, 0.7, 0.72), 0.3, metal=1.0), C, seg=12, rot=(math.radians(90), 0, 0)); r_.parent = root
    return dict(root=root, pages=pages)

# ------------------------------------------------------------------ cadeado
def cadeado(name, C, loc=(0, 0, 0), s=1.0):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc; root.scale = (s, s, s)
    g = gold(); steel = B.mat_basic('AlcaAco', (0.8, 0.8, 0.83), 0.2, metal=1.0)
    b = B.box(name + '_corpo', (0.8, 0.32, 0.7), (0, 0, 0.35), g, C, bevel=0.08, seg=4); b.parent = root
    cu = bpy.data.curves.new(name + '_alca', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.06; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for i, (x, z) in enumerate(((-0.24, 0.7), (0.0, 1.12), (0.24, 0.7))):
        p = sp.bezier_points[i]; p.co = (x, 0, z); p.handle_left_type = p.handle_right_type = 'AUTO'
    a = B.link(bpy.data.objects.new(name + '_alca', cu), C); a.data.materials.append(steel); a.parent = root
    kh = B.cyl(name + '_fechadura', 0.07, 0.02, (0, -0.165, 0.38), B.mat_basic('Fechadura', (0.02, 0.02, 0.02), 0.8), C, seg=20, rot=(math.radians(90), 0, 0)); kh.parent = root
    q = txt3d(name + '_q', '?', 0.36, (0.08, 0.06, 0.02), C, (0, -0.17, 0.33)); q.parent = root
    return dict(root=root, alca=a)

# ------------------------------------------------------------------ pizza do PIB e colunas
def wedge(name, r, h, a0, a1, mat, C, seg=40):
    bm = bmesh.new(); n = max(3, int(seg * (a1 - a0) / (2 * math.pi)) + 1)
    top, bot = [bm.verts.new((0, 0, h))], [bm.verts.new((0, 0, 0))]
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n; top.append(bm.verts.new((r * math.cos(a), r * math.sin(a), h))); bot.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0)))
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(len(top) - 1):
        j = i + 1; bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.faces.new((bot[-1], bot[0], top[0], top[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = B.mesh_obj(name, bm, mat, C); m = o.modifiers.new('bev', 'BEVEL'); m.width = 0.02; m.segments = 2; m.limit_method = 'ANGLE'; return o

def pizza(name, C, loc=(0, 0, 0), r=1.2, frac=0.323):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc
    rest = wedge(name + '_resto', r, 0.28, 2 * math.pi * frac, 2 * math.pi, B.mat_basic('PizzaResto', (0.10, 0.45, 0.50), 0.45), C); rest.parent = root
    piv = B.link(bpy.data.objects.new(name + '_fatiapiv', None), C); piv.parent = root
    sl = wedge(name + '_fatia', r, 0.28, 0.0, 2 * math.pi * frac, B.mat_basic('PizzaFatia', YEL, 0.35, emit=YEL, emit_s=0.15), C); sl.parent = piv
    return dict(root=root, slice=piv, mid_ang=math.pi * frac)

def colunas(name, C, specs, loc=(0, 0, 0), gap=0.75, w=0.5):
    """specs: [(chave, cor, altura_final)]; devolve objetos com origem na base (escala Z anima)."""
    out = {}
    for i, (k, col, h) in enumerate(specs):
        x = loc[0] + (i - (len(specs) - 1) / 2) * gap
        o = B.box(f'{name}_{k}', (w, w, 1.0), (0, 0, 0), B.mat_basic('Col_' + k, col, 0.4, emit=col, emit_s=0.12), C, bevel=0.03)
        for v in o.data.vertices: v.co.z += 0.5
        o.location = (x, loc[1], loc[2]); o.scale = (1, 1, 1e-3); out[k] = (o, h)
    return out

# ------------------------------------------------------------------ pacote e etiqueta de preço
def pacote(name, C, loc=(0, 0, 0), s=1.0, color=(0.45, 0.24, 0.12)):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc; root.scale = (s, s, s)
    b = B.box(name + '_corpo', (0.5, 0.3, 0.75), (0, 0, 0.375), B.mat_basic('Pacote_%s' % name, color, 0.55), C, bevel=0.03); b.parent = root
    bd = B.box(name + '_faixa', (0.505, 0.305, 0.18), (0, 0, 0.45), B.mat_basic('PacoteFaixa', (0.92, 0.85, 0.66), 0.6), C, bevel=0.01); bd.parent = root
    gr = B.cyl(name + '_grao', 0.05, 0.02, (0, -0.155, 0.45), B.mat_basic('Grao', (0.30, 0.15, 0.06), 0.5), C, seg=16, rot=(math.radians(90), 0, 0)); gr.scale = (1, 1.4, 1); gr.parent = root
    top = B.box(name + '_dobra', (0.5, 0.08, 0.1), (0, 0, 0.78), B.mat_basic('Pacote_%s' % name, color, 0.55), C, bevel=0.02); top.parent = root
    return dict(root=root)

def etiqueta(name, C, loc=(0, 0, 0), frac=0.43, w=1.0, h=0.5):
    """Etiqueta de preço em duas partes: produto (branca, 1-frac) e imposto (vermelha, frac). Cada parte tem um pivô."""
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc
    wp, wi = w * (1 - frac), w * frac
    pa = B.link(bpy.data.objects.new(name + '_pa', None), C); pa.parent = root; pa.location = (-w / 2 + wp / 2, 0, 0)
    pb = B.link(bpy.data.objects.new(name + '_pb', None), C); pb.parent = root; pb.location = (w / 2 - wi / 2, 0, 0)
    a = B.box(name + '_prod', (wp, 0.03, h), (0, 0, 0), B.mat_basic('EtqBranca', (0.96, 0.95, 0.9), 0.6), C, bevel=0.02); a.parent = pa
    b = B.box(name + '_imp', (wi, 0.03, h), (0, 0, 0), B.mat_basic('EtqVermelha', RED, 0.5, emit=RED, emit_s=0.2), C, bevel=0.02); b.parent = pb
    hole = B.cyl(name + '_furo', 0.04, 0.04, (-wp / 2 + 0.09, 0, h / 2 - 0.09), B.mat_basic('Furo', (0.02, 0.02, 0.02), 0.9), C, seg=16, rot=(math.radians(90), 0, 0)); hole.parent = pa
    return dict(root=root, a=pa, b=pb, wp=wp, wi=wi)

# ------------------------------------------------------------------ bomba de combustível
def bomba(name, C, loc=(0, 0, 0)):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc
    red = B.mat_basic('BombaVermelha', (0.80, 0.12, 0.10), 0.35, coat=0.4); wh = B.mat_basic('BombaBranca', (0.92, 0.92, 0.9), 0.4)
    dk = B.mat_basic('Visor', (0.02, 0.03, 0.03), 0.2, emit=(0.05, 0.2, 0.12), emit_s=0.6)
    def P(o): o.parent = root; return o
    P(B.box(name + '_corpo', (0.95, 0.6, 1.75), (0, 0, 0.875), red, C, bevel=0.05, seg=3))
    P(B.box(name + '_topo', (1.0, 0.65, 0.3), (0, 0, 1.9), wh, C, bevel=0.05, seg=3))
    P(B.box(name + '_visor', (0.72, 0.04, 0.42), (0, -0.31, 1.28), dk, C, bevel=0.02))
    P(B.box(name + '_base', (1.2, 0.85, 0.12), (0, 0, 0.06), B.mat_basic('BaseBomba', (0.3, 0.3, 0.32), 0.6), C))
    P(B.box(name + '_suporte', (0.18, 0.14, 0.32), (0.56, -0.05, 0.95), wh, C, bevel=0.02))
    noz = P(B.box(name + '_bico', (0.08, 0.32, 0.08), (0.56, -0.2, 1.05), B.mat_basic('Bico', (0.1, 0.1, 0.1), 0.4), C, bevel=0.02))
    cu = bpy.data.curves.new(name + '_mangueira', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.03; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for i, co in enumerate(((0.48, -0.05, 1.5), (0.75, -0.2, 0.55), (0.6, -0.1, 0.95))):
        p = sp.bezier_points[i]; p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    h = B.link(bpy.data.objects.new(name + '_mangueira', cu), C); h.data.materials.append(B.mat_basic('Borracha', (0.05, 0.05, 0.05), 0.7)); h.parent = root
    return dict(root=root, visor=(0, -0.34, 1.28))

# ------------------------------------------------------------------ balança
def balanca(name, C, loc=(0, 0, 0), arm=1.3):
    root = B.link(bpy.data.objects.new(name, None), C); root.location = loc
    brass = B.mat_basic('Latao', (0.85, 0.62, 0.25), 0.3, metal=1.0)
    B.cyl(name + '_base', 0.45, 0.1, (0, 0, 0.05), brass, C, seg=40).parent = root
    B.cyl(name + '_poste', 0.05, 1.9, (0, 0, 1.0), brass, C, seg=16).parent = root
    piv = B.link(bpy.data.objects.new(name + '_piv', None), C); piv.parent = root; piv.location = (0, 0, 1.95)
    bm_ = B.box(name + '_braco', (2 * arm + 0.1, 0.07, 0.07), (0, 0, 0), brass, C, bevel=0.02); bm_.parent = piv
    B.sphere(name + '_topo', 0.08, (0, 0, 2.02), brass, C).parent = root
    pans = []
    for sx in (-1, 1):
        hp = B.link(bpy.data.objects.new(f'{name}_pend{sx}', None), C); hp.parent = root
        pan = B.cyl(f'{name}_prato{sx}', 0.42, 0.04, (0, 0, -0.95), brass, C, seg=40); pan.parent = hp
        for k in range(3):
            a = k * 2 * math.pi / 3; x, y = 0.36 * math.cos(a), 0.36 * math.sin(a)
            st = B.cyl(f'{name}_fio', 0.008, 1.0, (x / 2, y / 2, -0.47), B.mat_basic('Fio', (0.2, 0.2, 0.2), 0.6), C, seg=6)
            d = Vector((x, y, -0.95)); st.rotation_mode = 'QUATERNION'; st.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(d.normalized()); st.location = d / 2; st.scale = (1, 1, d.length); st.parent = hp
        pans.append(hp)
    return dict(root=root, piv=piv, pans=pans, arm=arm, top=1.95)

def balanca_pose(Bz, ang):
    """ang > 0 abaixa o lado esquerdo (pans[0])."""
    Bz['piv'].rotation_euler = (0, ang, 0)
    for hp, sx in zip(Bz['pans'], (-1, 1)):
        x = sx * Bz['arm'] * math.cos(ang); z = Bz['top'] - sx * Bz['arm'] * math.sin(ang)
        hp.location = (x, 0, z)

# ------------------------------------------------------------------ xícara e tesoura
def xicara(name, C):
    root = B.link(bpy.data.objects.new(name, None), C)
    por = B.mat_basic('Porcelana', (0.96, 0.95, 0.93), 0.25, coat=0.5)
    cup = lathe(name + '_copo', [(0.0, 0.0), (0.045, 0.0), (0.055, 0.02), (0.06, 0.09), (0.056, 0.095), (0.05, 0.02), (0.0, 0.015)], por, C); cup.parent = root
    cf = B.cyl(name + '_cafe', 0.051, 0.004, (0, 0, 0.08), B.mat_basic('CafeLiq', (0.18, 0.08, 0.03), 0.15), C, seg=24); cf.parent = root
    cu = bpy.data.curves.new(name + '_asa', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.008
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for i, co in enumerate(((0.057, 0, 0.075), (0.09, 0, 0.05), (0.055, 0, 0.025))):
        p = sp.bezier_points[i]; p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    a = B.link(bpy.data.objects.new(name + '_asa', cu), C); a.data.materials.append(por); a.parent = root
    return root

def tesoura(name, C, s=1.0):
    root = B.link(bpy.data.objects.new(name, None), C); root.scale = (s, s, s)
    steel = B.mat_basic('Lamina', (0.85, 0.86, 0.9), 0.15, metal=1.0); hm = B.mat_basic('CaboTesoura', YEL, 0.4)
    halves = []
    for sd in (1, -1):
        hv = B.link(bpy.data.objects.new(f'{name}_meia{sd}', None), C); hv.parent = root
        bl = B.box(f'{name}_lamina{sd}', (0.62, 0.02, 0.08), (0.33, sd * 0.012, 0), steel, C, bevel=0.01)
        for v in bl.data.vertices:
            if v.co.x > 0: v.co.z *= 0.25
        bl.parent = hv
        bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.022, location=(-0.17, sd * 0.012, sd * 0.07), rotation=(math.radians(90), 0, 0))
        t = bpy.context.active_object; t.name = f'{name}_cabo{sd}'; t.data.materials.append(hm)
        for c_ in t.users_collection: c_.objects.unlink(t)
        C.objects.link(t); t.parent = hv
        halves.append(hv)
    B.cyl(name + '_eixo', 0.025, 0.06, (0, 0, 0), B.mat_basic('Eixo', (0.3, 0.3, 0.32), 0.3, metal=1.0), C, seg=12, rot=(math.radians(90), 0, 0)).parent = root
    return dict(root=root, halves=halves)

def tesoura_pose(Tz, open_deg):
    for hv, sd in zip(Tz['halves'], (1, -1)): hv.rotation_euler = (0, math.radians(sd * open_deg / 2), 0)

# ------------------------------------------------------------------ acabamento de superfície (procedural, sem imagens externas)
# Aplicado por cima dos materiais básicos depois de montar a cena: variação de rugosidade, microrrelevo e leve variação de cor,
# para os objetos não parecerem de plástico liso. Piso do palco: brilhante, com manchas suaves e grade luminosa que some nas bordas.
KINDS = {'metal': ('Ouro', 'CofreAco', 'Latao', 'Lamina', 'Argola', 'AlcaAco', 'Eixo'),
         'pintado': ('CofreCorpo', 'CofrePorta', 'BombaVermelha', 'BombaBranca', 'Col_', 'Arrec', 'PizzaResto', 'PizzaFatia', 'Pedestal', 'BaseCal', 'BaseBomba', 'CaboTesoura', 'SetaVerde'),
         'papel': ('Papel', 'EtqBranca', 'EtqVermelha', 'PacoteFaixa', 'FaixaCal'),
         'papelao': ('Pacote_',)}
def _detail(mat, scale, rough_var, bump, col_var=0.0, stretch=(1, 1, 1), seed=0.0):
    nt = mat.node_tree; b = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'), None)
    if b is None or b.inputs['Roughness'].is_linked: return
    N = nt.nodes.new; L = nt.links.new
    tc = N('ShaderNodeTexCoord'); mp = N('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stretch; mp.inputs['Location'].default_value = (seed, seed * 1.7, 0)
    L(tc.outputs['Object'], mp.inputs['Vector'])
    nz = N('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 8; nz.inputs['Roughness'].default_value = 0.6
    L(mp.outputs['Vector'], nz.inputs['Vector'])
    r0 = b.inputs['Roughness'].default_value
    mr = N('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.02, r0 - rough_var); mr.inputs['To Max'].default_value = min(1.0, r0 + rough_var)
    L(nz.outputs['Fac'], mr.inputs['Value']); L(mr.outputs['Result'], b.inputs['Roughness'])
    bp_ = N('ShaderNodeBump'); bp_.inputs['Strength'].default_value = bump; bp_.inputs['Distance'].default_value = 0.002
    L(nz.outputs['Fac'], bp_.inputs['Height']); L(bp_.outputs['Normal'], b.inputs['Normal'])
    if col_var and not b.inputs['Base Color'].is_linked:
        c = b.inputs['Base Color'].default_value; hsv = N('ShaderNodeHueSaturation'); hsv.inputs['Color'].default_value = c
        mv = N('ShaderNodeMapRange'); mv.inputs['To Min'].default_value = 1 - col_var; mv.inputs['To Max'].default_value = 1 + col_var
        L(nz.outputs['Fac'], mv.inputs['Value']); L(mv.outputs['Result'], hsv.inputs['Value']); L(hsv.outputs['Color'], b.inputs['Base Color'])

def piso_brilhante(mat):
    nt = mat.node_tree; b = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'); N = nt.nodes.new; L = nt.links.new
    b.inputs['Base Color'].default_value = (0.025, 0.03, 0.04, 1); b.inputs['Coat Weight'].default_value = 0.35; b.inputs['Coat Roughness'].default_value = 0.12
    tc = N('ShaderNodeTexCoord')
    nz = N('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.9; nz.inputs['Detail'].default_value = 4; L(tc.outputs['Object'], nz.inputs['Vector'])
    mr = N('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.12; mr.inputs['To Max'].default_value = 0.42; L(nz.outputs['Fac'], mr.inputs['Value']); L(mr.outputs['Result'], b.inputs['Roughness'])
    sep = N('ShaderNodeSeparateXYZ'); L(tc.outputs['Object'], sep.inputs['Vector'])
    def line(o):
        m1 = N('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 1.25; L(o, m1.inputs[0])
        fr = N('ShaderNodeMath'); fr.operation = 'PINGPONG'; fr.inputs[1].default_value = 0.5; L(m1.outputs[0], fr.inputs[0])
        lt = N('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.011; L(fr.outputs[0], lt.inputs[0]); return lt.outputs[0]
    mx = N('ShaderNodeMath'); mx.operation = 'MAXIMUM'; L(line(sep.outputs['X']), mx.inputs[0]); L(line(sep.outputs['Y']), mx.inputs[1])
    ln = N('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; L(tc.outputs['Object'], ln.inputs[0])
    fd = N('ShaderNodeMapRange'); fd.inputs['From Min'].default_value = 1.5; fd.inputs['From Max'].default_value = 6.5; fd.inputs['To Min'].default_value = 1.0; fd.inputs['To Max'].default_value = 0.0
    L(ln.outputs['Value'], fd.inputs['Value'])
    em = N('ShaderNodeMath'); em.operation = 'MULTIPLY'; L(mx.outputs[0], em.inputs[0]); L(fd.outputs['Result'], em.inputs[1])
    es = N('ShaderNodeMath'); es.operation = 'MULTIPLY'; es.inputs[1].default_value = 0.7; L(em.outputs[0], es.inputs[0])
    b.inputs['Emission Color'].default_value = (0.10, 0.62, 0.70, 1); L(es.outputs[0], b.inputs['Emission Strength'])

def acabamento():
    import bpy as _b
    for m in _b.data.materials:
        if not m.use_nodes: continue
        n = m.name
        if n == 'ChaoEstudio': piso_brilhante(m); continue
        if n.startswith(KINDS['metal']): _detail(m, 60, 0.12, 0.04, 0.0, stretch=(1, 1, 30))
        elif n.startswith(KINDS['pintado']): _detail(m, 45, 0.07, 0.02, 0.03)
        elif n.startswith(KINDS['papel']): _detail(m, 140, 0.05, 0.06, 0.02)
        elif n.startswith(KINDS['papelao']): _detail(m, 35, 0.08, 0.12, 0.06)

def luzes_recorte():
    """Duas luzes de recorte coloridas atrás (ciano à esquerda, laranja à direita): separam os objetos do fundo escuro."""
    import bpy as _b
    for nm, loc, col, e in (('RecorteCiano', (-4.5, 4.5, 3.0), (0.3, 0.85, 1.0), 260), ('RecorteLaranja', (4.5, 4.0, 2.6), (1.0, 0.55, 0.2), 200)):
        l = _b.data.lights.new(nm, 'AREA'); l.energy = e; l.size = 2.5; l.color = col
        o = B.link(_b.data.objects.new(nm, l)); o.location = loc
        d = Vector((0, 0, 1.0)) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
