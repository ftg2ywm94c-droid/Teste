"""Cenários do vídeo 09 (e se a vida real seguisse as regras do GTA?).
- rua: a rua de dia do vídeo 04 (prédio de 7 andares, café, carro), com o Téo.
- estudio: o estúdio escuro do vídeo 08, usado como laboratório de testes de batida (pista, carro e boneco de teste).
- Boneco de teste: o Téo com as cores de boneco de crash test (amarelo e preto, alvos nas juntas).
- Blindado: personagem nosso, o Téo com o corpo que aguentaria uma batida (cabeça grande acolchoada, sem pescoço,
  bolsas de ar no peito, almofadas). Ilustra a ideia do projeto Graham sem copiar a escultura.
Nada aqui copia o jogo (sem personagens, logos, mapa ou interface)."""
import bpy, bmesh, math, os, random, importlib.util
from mathutils import Vector, Euler, Matrix
import build as B

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
S4 = _load('scene04', os.path.join(HERE, '..', 'ep04', 'scene.py'))
S8 = _load('scene08', os.path.join(HERE, '..', 'ep08', 'scene.py'))
emit_mat, new_mat = S8.emit_mat, S8.new_mat

DUMMY = dict(B.TEO, skin=(0.95, 0.78, 0.18), shirt=(0.95, 0.78, 0.18), pants=(0.12, 0.12, 0.14), shoes=(0.12, 0.12, 0.14), cap=None)
ARMOR = dict(B.TEO, cap=None, hair=(0.25, 0.16, 0.10))

# ------------------------------------------------------------------ rua
def build_rua9():
    R = S4.build_rua()
    car = R['car']; car['root'].location = (-200, 0, 0)            # carro do vídeo 04 fora de cena; cada plano põe o seu
    for p in car['puffs']: p.hide_render = True
    return dict(car=car)

def place_car(car, x, y, rz=0.0):
    car['root'].location = (x, y, 0.0); car['root'].rotation_euler = (0, 0, rz)

# ------------------------------------------------------------------ estúdio de testes
def build_lab():
    R = S8.build_estudio()
    C = B.new_coll('Lab')
    pista = B.box('pista_teste', (40.0, 3.2, 0.02), (0.0, 0.0, 0.01), B.mat_basic('PistaTeste', (0.16, 0.16, 0.17), 0.7), C)
    faixa = B.mat_basic('FaixaTeste', (0.95, 0.78, 0.12), 0.5)
    for x in range(-20, 21, 2): B.box('faixa_teste', (1.0, 0.12, 0.005), (x, -1.45, 0.022), faixa, C); B.box('faixa_teste', (1.0, 0.12, 0.005), (x, 1.45, 0.022), faixa, C)
    car = B.build_car('CarroTeste', (0.75, 0.08, 0.06), driver=False)
    return dict(lab=C, car=car)

# ------------------------------------------------------------------ boneco de teste
def build_dummy(name, C):
    ch = B.build_character(name, DUMMY, C)
    bpy.context.view_layer.update()
    m1 = B.mat_basic('AlvoPreto', (0.03, 0.03, 0.03), 0.5); m2 = B.mat_basic('AlvoAmarelo2', (1.0, 0.85, 0.2), 0.5)
    hz, s = ch['hip_z'], 1.0
    # alvos colados no mundo (pose de pé) e depois presos ao osso: frente do tronco e lados da cabeça
    spots = [('spine', Vector((0.0, -0.125, hz + 0.30)), (math.radians(90), 0, 0)),
             ('head', Vector((0.172, 0.0, hz + 0.5 + 0.19)), (0, math.radians(90), 0)),
             ('head', Vector((-0.172, 0.0, hz + 0.5 + 0.19)), (0, math.radians(90), 0))]
    for bone_, w, rot in spots:
        for r, m, d in ((0.055, m1, 0.0), (0.028, m2, 0.003)):
            o = B.cyl(name + '_alvo', r, 0.004, (0, 0, 0), m, C, seg=24)
            n = Vector((0, -1, 0)) if bone_ == 'spine' else Vector((math.copysign(1, w.x), 0, 0))
            o.parent = ch['arm']; o.parent_type = 'BONE'; o.parent_bone = bone_
            bpy.context.view_layer.update()
            o.matrix_world = Matrix.Translation(w + n * d) @ Euler(rot).to_matrix().to_4x4()
    return ch

# ------------------------------------------------------------------ personagem blindado (ideia do projeto Graham, desenho nosso)
def build_armored(name, C):
    ch = B.build_character(name, ARMOR, C)
    bpy.context.view_layer.update()
    hz = ch['hip_z']; top = hz + 0.5
    # sem pescoço: esconde o pescoço e afunda a cabeça (maior) no tronco; capacete acolchoado por cima
    for o in ch['arm'].children:
        if o.name.startswith(name + '_pescoco'): o.hide_render = True
        if o.name.startswith((name + '_cabeca', name + '_cabelo')):
            mw = o.matrix_world.copy(); o.matrix_world = Matrix.Translation(Vector((0, 0, -0.10))) @ mw
            o.scale = tuple(v * 1.32 for v in o.scale)
    pad = B.mat_basic('Almofada', (0.86, 0.55, 0.42), 0.75)
    def att(o, bone_, w):
        o.parent = ch['arm']; o.parent_type = 'BONE'; o.parent_bone = bone_; bpy.context.view_layer.update(); o.matrix_world = Matrix.Translation(w) @ o.matrix_world.to_3x3().to_4x4()
    # dobras de gordura em volta da cabeça (no lugar do pescoço) e nos ombros
    for i, (r, z) in enumerate(((0.26, top + 0.02), (0.235, top + 0.09))):
        t = B.sphere(name + f'_dobra{i}', r, (0, 0, 0), pad, C, scale=(1.0, 0.8, 0.32)); att(t, 'spine', Vector((0, 0.01, z)))
    for sx in (1, -1):
        o = B.sphere(name + '_ombro', 0.12, (0, 0, 0), pad, C, scale=(1, 0.9, 0.75)); att(o, 'spine', Vector((sx * 0.22, 0, top - 0.04)))
    # bolsas de ar no peito (translúcidas, levemente brilhantes)
    bag = B.mat_basic('BolsaAr', (0.95, 0.75, 0.62), 0.25, coat=0.6, alpha=0.85)
    bags = []
    for sx in (1, -1):
        for dz in (0.0, -0.15):
            o = B.sphere(name + '_bolsa', 0.085, (0, 0, 0), bag, C, scale=(1.0, 0.75, 0.85)); att(o, 'spine', Vector((sx * 0.08, -0.14, top - 0.16 + dz))); bags.append(o)
    # rosto achatado: nariz e orelhas embutidos em almofadas
    return dict(ch, bags=bags)

# ------------------------------------------------------------------ objetos
def hotdog(name, C):
    root = B.link(bpy.data.objects.new(name, None), C)
    bun = B.capsule(name + '_pao', 0.045, 0.16, B.mat_basic('Pao', (0.86, 0.6, 0.3), 0.7), C); bun.parent = root; bun.rotation_euler = (0, math.radians(90), 0); bun.scale = (1.0, 1.25, 1.0)
    sau = B.capsule(name + '_salsicha', 0.025, 0.2, B.mat_basic('Salsicha', (0.65, 0.18, 0.1), 0.45, coat=0.3), C); sau.parent = root; sau.rotation_euler = (0, math.radians(90), 0); sau.location = (0, 0, 0.035)
    mus = B.capsule(name + '_mostarda', 0.008, 0.17, B.mat_basic('Mostarda', (1.0, 0.8, 0.05), 0.4), C); mus.parent = root; mus.rotation_euler = (0, math.radians(90), 0); mus.location = (0, 0, 0.06)
    return root

def cast(ch, side='L'):
    """Gesso no antebraço."""
    m = B.mat_basic('Gesso', (0.97, 0.97, 0.95), 0.9)
    o = B.capsule(ch['root'].name + '_gesso', 0.06, 0.24, m, ch['root'].users_collection[0]); o.parent = ch['arm']; o.parent_type = 'BONE'; o.parent_bone = f'forearm.{side}'
    bpy.context.view_layer.update()
    pb = ch['arm'].pose.bones[f'forearm.{side}']; head = ch['arm'].matrix_world @ pb.head
    o.matrix_world = Matrix.Translation(head + Vector((0, 0, -0.01)))
    return o

def floor_marks(C, x, y0, floors=7, fh=3.2):
    """Placas com o número do andar na frente do prédio (aparecem no plano da queda)."""
    return [(i, Vector((x, y0, 0.15 + i * fh + 1.4))) for i in range(1, floors + 1)]
