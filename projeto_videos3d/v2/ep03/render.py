"""Vídeo 03: monta a cena de um plano, anima quadro a quadro e renderiza.
Uso: blender -b --python v2/ep03/render.py -- --shot C [--mode preview|final] [--spp N] [--step N] [--frames a-b] [--still F]
Saída: v2/ep03/frames/<plano>/NNNN.png (final) ou v2/ep03/preview/<plano>/ (prévia). Retomável."""
import bpy, sys, os, math, json, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
import build as B
import scene as SC
import plan as P
import fisica as F
from story import sstep
from mathutils import Vector, Matrix

ap = argparse.ArgumentParser(); ap.add_argument('--shot', required=True); ap.add_argument('--mode', default='preview')
ap.add_argument('--spp', type=int); ap.add_argument('--step', type=int); ap.add_argument('--frames'); ap.add_argument('--still', type=int)
ap.add_argument('--save-blend', action='store_true')
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
shot = P.BY_NAME[a.shot]; FINAL = a.mode == 'final'
W, H = (720, 1280) if FINAL else (270, 480)
if os.environ.get('PREVIEW_RES'): W, H = map(int, os.environ['PREVIEW_RES'].split('x'))
spp = a.spp or (8 if FINAL else 5); step = a.step or (1 if FINAL else 3)
SPACE = shot.kind == 'corte'

bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
if SPACE: SC.setup_space_world(stars=0.8)
elif shot.kind == 'polo': SC.cold_world()
else: SC.setup_space_world(stars=0.0)
B.setup_render(W, H, spp, preview=not FINAL)
sc = bpy.context.scene
if shot.kind != 'polo':   # sem névoa no espaço e dentro do túnel
    for n in sc.node_tree.nodes:
        if n.bl_idname == 'CompositorNodeMath': n.inputs[1].default_value = 0.0
    sc.view_settings.exposure = 0.0
cam = B.link(bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.01 if shot.name == 'J' else 0.05; cam.data.clip_end = 5000
RC = B.new_coll('Rotulos3D')

LBL_FAC = {}
def bill(key, text, loc, size, color):
    fac = 1.0
    if size < 0.2: fac = size / 0.5; size = 0.5          # rótulos minúsculos: cria em tamanho normal e reduz o objeto (espessuras proporcionais)
    LBL_FAC[key] = fac
    r = B.label(text, loc, size, color, coll=RC, name='rot_' + key)
    for ch in r.children: ch.visible_shadow = False
    c = r.constraints.new('COPY_ROTATION'); c.target = cam
    r.scale = (0.0001,) * 3; return r

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

def text_obj(name, body, size, color, parent, loc, align='CENTER', emit=1.3):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.font = bpy.data.fonts.load(B.FONT, check_existing=True)
    cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    o = B.link(bpy.data.objects.new(name, cu), RC); o.parent = parent; o.location = loc
    o.data.materials.append(B.mat_basic('Txt_' + name, color, 0.5, emit=color, emit_s=emit)); o.visible_shadow = False
    return o

def float_pose(teo, f, T, k=1.0, phase=0.0, extra=None):
    """Flutuando sem peso: braços abertos, pernas soltas, leve balanço."""
    s1, s2 = math.sin(T * 1.3 + phase), math.sin(T * 0.9 + phase + 1)
    rot = {'spine': (6 * s2 * k, 4 * s1 * k, 0), 'head': (-6 + 5 * s1 * k, 8 * s2 * k, 0),
           'upper_arm.L': (-15 - 8 * s1 * k, 0, -70 - 10 * s2 * k), 'upper_arm.R': (-15 + 8 * s2 * k, 0, 70 + 10 * s1 * k),
           'forearm.L': (-25 - 10 * s2 * k, 0, 0), 'forearm.R': (-25 - 10 * s1 * k, 0, 0),
           'thigh.L': (-22 - 8 * s1 * k, 0, -8), 'thigh.R': (-10 + 8 * s2 * k, 0, 8), 'shin.L': (30 + 6 * s2 * k, 0, 0), 'shin.R': (18, 0, 0)}
    if extra: rot.update(extra)
    B.pose(teo, frame=f, **rot)

items = {}; events = dict(shot=shot.name, fps=P.FPS, frames=[])
# ================================================================== CORTE (espaço)
if SPACE:
    earth = SC.build_cut_earth(P.R, shot.cut)
    sd = Vector(shot.sun).normalized(); SC.sun_lamp(sd, 4.2); SC.set_sunpos(tuple(sd * 1e5))
    items['tube'] = SC.tube(earth, 'TunelEixo', (0, 0, 1.012), (0, 0, -1.012), 0.0075, P.CYAN, emit_s=3.0)
    if hasattr(shot, 'eq_tube'):
        items['eqt'] = SC.tube(earth, 'TunelEquador', (1.012, 0, 0), (-1.012, 0, 0), P.EQ_TUBE_R, P.YEL, emit_s=3.0)
    if hasattr(shot, 'kola'): items['kola'] = SC.kola_tick(earth, shot.kola)
    if hasattr(shot, 'marker'):
        TC = B.new_coll('TeoCol'); teo = B.build_character('Teo', B.TEO, TC); items['teo'] = teo
        sz = 1.1
        teo['root'].scale = (sz,) * 3
        hm, hb = SC.new_mat('HaloTeo'); ho = hb.n('ShaderNodeOutputMaterial'); lw = hb.n('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.3
        e2 = hb.n('ShaderNodeEmission'); e2.inputs[0].default_value = (0.6, 0.95, 1.0, 1)
        hb.link(hb.math('MULTIPLY', hb.math('POWER', lw.outputs['Facing'], 3.0), 1.6), e2.inputs[1])
        tr = hb.n('ShaderNodeBsdfTransparent'); ad = hb.n('ShaderNodeAddShader'); hb.link(tr.outputs[0], ad.inputs[0]); hb.link(e2.outputs[0], ad.inputs[1]); hb.link(ad.outputs[0], ho.inputs[0])
        halo = B.sphere('HaloTeo', 0.75 * sz / 0.55 * 0.55 * 1.3, (0, 0, 0), hm, TC, seg=32); halo.visible_shadow = False; halo.visible_diffuse = False
        items['halo'] = halo
        kl = bpy.data.lights.new('LuzTeo', 'POINT'); kl.energy = 40.0 * sz; kl.shadow_soft_size = 0.3; kl.color = (0.85, 0.95, 1.0)
        items['klight'] = B.link(bpy.data.objects.new('LuzTeo', kl), TC)
    if hasattr(shot, 'graph'):   # gráfico da gravidade preso à câmera (parte de cima da tela)
        gr = B.link(bpy.data.objects.new('grafico', None), RC); gr.parent = cam; gr.location = (0.0, -1.62, -5.0); gr.scale = (1e-4,) * 3
        pm = B.mat_basic('PainelGraf', (0.03, 0.035, 0.05), 0.6, alpha=0.82)
        plate = B.box('painel', (2.35, 1.38, 0.01), (0, 0, -0.02), pm, RC, bevel=0.08); plate.parent = gr; plate.visible_shadow = False
        ax_m = B.mat_basic('Eixos', (0.75, 0.78, 0.85), 0.5, emit=(0.75, 0.78, 0.85), emit_s=0.6)
        X0, X1, Y0, YS = -0.95, 0.95, -0.42, 0.072
        for nm, sz_, loc in (('eixoX', (X1 - X0 + 0.04, 0.012, 0.004), ((X0 + X1) / 2, Y0, 0)), ('eixoY', (0.012, 0.86, 0.004), (X0, Y0 + 0.42, 0))):
            o = B.box(nm, sz_, loc, ax_m, RC); o.parent = gr; o.visible_shadow = False
        for nm, xk in (('lin_cmb', 2891.0), ('lin_icb', 6371 - 1221.5)):
            x = X0 + (X1 - X0) * xk / 6371; o = B.box(nm, (0.006, 0.82, 0.003), (x, Y0 + 0.41, -0.002), B.mat_basic('Grade', (0.35, 0.38, 0.45), 0.5, emit=(0.35, 0.38, 0.45), emit_s=0.4), RC)
            o.parent = gr; o.visible_shadow = False
        ref = B.box('ref98', (X1 - X0, 0.006, 0.003), ((X0 + X1) / 2, Y0 + YS * 9.82, -0.001), B.mat_basic('Ref98', (0.5, 0.55, 0.65), 0.5, emit=(0.5, 0.55, 0.65), emit_s=0.6), RC)
        ref.parent = gr; ref.visible_shadow = False
        cu = bpy.data.curves.new('curva_g', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.014; cu.bevel_resolution = 2
        sp = cu.splines.new('POLY'); n = 160; sp.points.add(n)
        for i in range(n + 1):
            d = 6371.0 * i / n; sp.points[i].co = (X0 + (X1 - X0) * d / 6371, Y0 + YS * F.g((6371 - d) * 1e3), 0.01, 1)
        cu.bevel_factor_mapping_end = 'SPLINE'; cu.bevel_factor_end = 0.0
        co = B.link(bpy.data.objects.new('curva_g', cu), RC); co.parent = gr; co.visible_shadow = False
        co.data.materials.append(B.mat_basic('CurvaG', P.YEL, 0.4, emit=P.YEL, emit_s=2.2))
        dot = B.sphere('ponto_g', 0.035, (X0, Y0 + YS * 9.82, 0.02), B.mat_basic('PontoG', (1, 1, 1), 0.4, emit=(1, 1, 1), emit_s=3.0), RC, seg=16)
        dot.parent = gr; dot.visible_shadow = False
        text_obj('g_tit', 'gravidade (m/s²)', 0.13, (1, 1, 1), gr, (X0 + 0.02, 0.54, 0.01), 'LEFT')
        text_obj('g_98', '9,8', 0.10, (0.85, 0.88, 0.95), gr, (X0 - 0.13, Y0 + YS * 9.82, 0.01), 'CENTER')
        g107 = text_obj('g_107', '10,7', 0.12, P.YEL, gr, (X0 + (X1 - X0) * 2891 / 6371, Y0 + YS * 10.69 + 0.1, 0.01), 'CENTER'); g107.scale = (1e-4,) * 3
        text_obj('g_sup', 'superfície', 0.095, (0.85, 0.88, 0.95), gr, (X0 + 0.02, Y0 - 0.11, 0.01), 'LEFT')
        text_obj('g_cen', 'centro', 0.095, (0.85, 0.88, 0.95), gr, (X1, Y0 - 0.11, 0.01), 'RIGHT')
        text_obj('g_nuc', 'núcleo', 0.085, P.ORANGE, gr, (X0 + (X1 - X0) * 2891 / 6371 + 0.04, Y0 + 0.08, 0.01), 'LEFT')
        items['graph'] = (gr, cu, dot, g107, (X0, X1, Y0, YS))
# ================================================================== POLO / TÚNEL
else:
    if shot.kind == 'polo':
        PC, tun = SC.build_pole(shot.pole_name)
        for o in [o for o in bpy.data.objects if o.name.startswith('anel')]: pass
    else:
        TCx = B.new_coll('Tunel'); tun = SC.build_tunnel(TCx, z_top=0.0, length=1100.0)
    items['tun'] = tun
    teo = B.build_character('Teo', B.TEO, B.new_coll('TeoCol')); items['teo'] = teo
    kl = bpy.data.lights.new('LuzChave', 'POINT'); kl.energy = 120.0 if shot.kind == 'tunel' else 60.0; kl.shadow_soft_size = 0.6; kl.color = (0.9, 0.95, 1.0)
    items['klight'] = B.link(bpy.data.objects.new('LuzChave', kl))
    if shot.kind == 'tunel': bpy.data.materials['ParedeTunel'].node_tree.nodes['K_prof'].outputs[0].default_value = 0.0
# desempenho: emissivos que não iluminam a cena não são amostrados (rótulos, texto, rastro); anéis do túnel continuam como luz
for m in bpy.data.materials:
    if m.name not in ('SolSup', 'AnelLuz', 'ParedeTunel'): m.cycles.emission_sampling = 'NONE'
if SPACE or shot.kind == 'tunel': sc.world.cycles.sampling_method = 'NONE'
for (kk, text, col, size, t_on, t_off, posf) in shot.labels: items['lbl_' + kk] = (bill(kk, text, posf(shot.t0), size, col), t_on, t_off, posf)

# ================================================================== animação
def teo_face_cam(T, pos):
    c = shot.cam(T)['pos']; return math.atan2(c[1] - pos[1], c[0] - pos[0]) + math.pi / 2

fr = list(shot.frames); s_dist = 0.0; prevT = None
for f in fr:
    T = f / P.FPS; ev = dict(f=f, T=round(T, 4)); dt = 0 if prevT is None else T - prevT; prevT = T
    if SPACE:
        sp = earth['spin']; sp.rotation_euler = (0, 0, shot.spin(T)); key(sp, 'rotation_euler', f=f); ev['spin'] = shot.spin(T)
        tb = items['tube']; k_ = shot.tube(T)
        if shot.name == 'B': tb.scale = (1, 1, max(k_, 1e-4))
        else: tb.scale = (max(k_, 1e-4), max(k_, 1e-4), 1)
        key(tb, 'scale', f=f)
        if 'eqt' in items:
            k2 = shot.eq_tube(T); items['eqt'].scale = (1, 1, max(k2, 1e-4)); key(items['eqt'], 'scale', f=f)
        if hasattr(shot, 'heat'): SC.set_value('Camadas', 'K_calor', shot.heat(T), f)
        if hasattr(shot, 'clouds'):
            SC.set_value('Nuvens', 'K_nuvem', 0.9 * shot.clouds(T), f)
            at = bpy.data.objects['AtmosferaSup']; at.hide_render = shot.clouds(T) < 0.5; at.keyframe_insert('hide_render', frame=f)
        if 'teo' in items:
            pos = Vector(shot.marker(T)); teo = items['teo']; r = teo['root']
            sz = r.scale[0]; r.location = pos - Vector((0, 0, 0.55 * sz)); r.rotation_euler = (0, 0, teo_face_cam(T, pos)); key(r, 'location', 'rotation_euler', f=f)
            float_pose(teo, f, T); B.set_face(teo, {'relief': 0.6, 'neutral': 0.4}, f)
            items['halo'].location = pos; key(items['halo'], 'location', f=f)
            cpos = Vector(shot.cam(T)['pos']); items['klight'].location = pos + (cpos - pos).normalized() * 1.2 * sz / 0.55; key(items['klight'], 'location', f=f)
            ev['teo'] = [round(x, 3) for x in pos]
        if 'graph' in items:
            gr, cu, dot, g107, (X0, X1, Y0, YS) = items['graph']; s = 0.72 * pop_scale(T, shot.graph['t_on'], shot.graph['t_off']); gr.scale = (s,) * 3; key(gr, 'scale', f=f)
            d = shot.depth(T); cu.bevel_factor_end = max(d / 6371.0, 0.0); cu.keyframe_insert('bevel_factor_end', frame=f)
            dot.location = (X0 + (X1 - X0) * d / 6371, Y0 + YS * F.g((6371 - d) * 1e3), 0.02); key(dot, 'location', f=f)
            s2 = pop_scale(T, 22.6); g107.scale = (s2,) * 3; key(g107, 'scale', f=f)
            ev['depth_km'] = round(d, 1); ev['g'] = round(F.g((6371 - d) * 1e3), 3)
    else:
        teo = items['teo']; r = teo['root']
        if shot.kind == 'tunel':
            s_dist += dt * shot.speed(T); items['tun'].location = (0, 0, s_dist); key(items['tun'], 'location', f=f)
            nd = bpy.data.materials['ParedeTunel'].node_tree.nodes['K_prof']; nd.outputs[0].default_value = shot.prof(T); nd.outputs[0].keyframe_insert('default_value', frame=f)
            zt = shot.teo_z(T); bob = 0.08 * math.sin(T * 1.1)
            if shot.name == 'E':
                r.location = (0.0, 0.0, zt - 0.6 + bob); r.rotation_euler = (math.radians(8 * math.sin(T * 0.7)), math.radians(6 * math.sin(T * 0.5)), math.radians(200))
                float_pose(teo, f, T, 1.2, extra={'upper_arm.L': (-150, 0, -30), 'upper_arm.R': (-150, 0, 30), 'forearm.L': (-10, 0, 0), 'forearm.R': (-10, 0, 0)})
                B.set_face(teo, {'alarm': 0.7, 'relief': 0.3}, f)
            elif shot.name == 'L':   # empurrado para o lado pelo giro da Terra até a parede
                x = shot.lat(T); hit = sstep(shot.T_HIT - 0.05, shot.T_HIT + 0.1, T)
                r.location = (x, 0.0, zt - 0.6 + bob * (1 - hit)); r.rotation_euler = (0, math.radians(-25 * hit), math.radians(10))
                float_pose(teo, f, T, 1.0 - hit, extra={'upper_arm.R': (-20, 0, 40 + 50 * hit), 'forearm.R': (-20, 0, 0), 'head': (0, -25 * hit, 0)} if hit > 0.01 else None)
                B.set_face(teo, {'alarm': 1.0} if T > 63.4 else {'neutral': 1.0}, f)
                ev['lat_m'] = round(x, 3); ev['tphys'] = round(shot.tphys(T), 2)
            else:   # F: vira para a câmera e encolhe os ombros
                turn = sstep(33.0, 34.2, T); shrug = sstep(34.85, 35.25, T) * (1 - sstep(36.2, 36.7, T))
                r.location = (0.0, 0.0, zt - 0.6 + bob); r.rotation_euler = (0, 0, math.radians(70 * (1 - turn)))
                float_pose(teo, f, T, 0.6, extra={'upper_arm.L': (-10 - 30 * shrug, 0, -60 + 25 * shrug), 'upper_arm.R': (-10 - 30 * shrug, 0, 60 - 25 * shrug),
                                                   'forearm.L': (-20 - 80 * shrug, 0, 0), 'forearm.R': (-20 - 80 * shrug, 0, 0), 'head': (-4, 12 * shrug, 0)})
                B.set_face(teo, {'relief': shrug, 'neutral': 1 - shrug} if T < 35.6 else {'focus': 1.0}, f)
            key(r, 'location', 'rotation_euler', f=f)
            c = shot.cam(T); items['klight'].location = add3 = (c['pos'][0] + 0.3, c['pos'][1] - 0.3, c['pos'][2] + 0.6); key(items['klight'], 'location', f=f)
            ev['s'] = round(s_dist, 2)
        elif shot.name == 'A':
            x0, y0 = P.TEO_RIM; r.location = (x0, y0, 0.02); r.rotation_euler = (0, 0, math.pi); key(r, 'location', 'rotation_euler', f=f)
            br = math.sin(T * 1.6); peek = sstep(0.4, 1.6, T); look_up = sstep(3.3, 4.0, T) * (1 - sstep(5.0, 5.8, T))
            B.pose(teo, frame=f, spine=(14 * peek + 1.5 * br, 0, 0), head=(28 * peek - 40 * look_up, 18 * look_up, 0),
                   **{'upper_arm.L': (-6, 0, -10), 'upper_arm.R': (-6, 0, 10), 'forearm.L': (-20, 0, 0), 'forearm.R': (-20, 0, 0)})
            B.set_face(teo, {'focus': 1 - look_up, 'neutral': look_up} if T < 3.3 else {'relief': look_up, 'focus': 1 - look_up}, f)
            items['klight'].location = (3.0, -6.0, 2.5); key(items['klight'], 'location', f=f)
        elif shot.name == 'C':
            x, y = shot.teo_xy(T); z = shot.teo_z(T)
            crouch = sstep(P.T_PULO - 0.45, P.T_PULO - 0.05, T) * (1 - sstep(P.T_PULO, P.T_PULO + 0.2, T))
            hop = 0.45 * math.sin(math.pi * min(max((T - P.T_PULO) / 0.5, 0), 1)) if T > P.T_PULO and T < P.T_PULO + 0.5 else 0.0
            r.location = (x, y, 0.02 + z + hop - 0.25 * crouch); r.rotation_euler = (math.radians(-12 * sstep(P.T_PULO, P.T_PULO + 0.6, T)), 0, math.pi); key(r, 'location', 'rotation_euler', f=f)
            relax = sstep(12.5, 13.3, T); flail = sstep(P.T_PULO, P.T_PULO + 0.3, T) * (1 - relax)
            if T < P.T_PULO + 0.05:
                B.pose(teo, frame=f, spine=(30 * crouch, 0, 0), head=(20 - 10 * crouch, 0, 0),
                       **{'thigh.L': (-60 * crouch, 0, 0), 'thigh.R': (-60 * crouch, 0, 0), 'shin.L': (90 * crouch, 0, 0), 'shin.R': (90 * crouch, 0, 0),
                          'upper_arm.L': (30 * crouch, 0, -10), 'upper_arm.R': (30 * crouch, 0, 10)})
                B.set_face(teo, {'focus': 1.0}, f)
            else:
                fl = math.sin(T * 14)
                ex = {'upper_arm.L': (-160 * flail + 12 * fl * flail, 0, -20 - 50 * relax), 'upper_arm.R': (-160 * flail - 12 * fl * flail, 0, 20 + 50 * relax)} if flail > 0.02 else None
                float_pose(teo, f, T, relax, extra=ex)
                B.set_face(teo, {'alarm': 1 - relax, 'relief': relax}, f)
            c = shot.cam(T); items['klight'].location = (c['pos'][0] + 0.4, c['pos'][1] + 0.2, c['pos'][2] + 1.5); key(items['klight'], 'location', f=f)
            ev['teo_z'] = round(z, 2)
        elif shot.name == 'H':
            z = shot.teo_z(T); r.location = (0.0, 0.0, z); r.rotation_euler = (0, 0, math.radians(-40)); key(r, 'location', 'rotation_euler', f=f)
            reach = sstep(43.6, 44.4, T) * (1 - sstep(45.4, 46.0, T)); fall = sstep(45.3, 45.9, T)
            B.pose(teo, frame=f, spine=(-4 * reach, 0, 0), head=(-10 * (1 - reach) + 10 * fall, -20 * reach, 0),
                   **{'upper_arm.L': (-170 * (1 - reach) - 70 * reach, 0, -10 - 20 * reach), 'upper_arm.R': (-170 * (1 - reach) - 95 * reach, 0, 10 + 15 * reach),
                      'forearm.L': (-10, 0, 0), 'forearm.R': (-5 - 10 * reach, 0, 0),
                      'thigh.L': (-10, 0, -6), 'thigh.R': (-4, 0, 6), 'shin.L': (16, 0, 0), 'shin.R': (10, 0, 0)})
            B.set_face(teo, {'focus': 1.0} if T < 45.3 else {'alarm': 1.0}, f)
            items['klight'].location = (3.0, -4.2, 2.6 + max(z, -3.0)); key(items['klight'], 'location', f=f)
            ev['teo_z'] = round(z, 3)
    for kk, v in items.items():
        if kk.startswith('lbl_'):
            o, t_on, t_off, posf = v; s = pop_scale(T, t_on, t_off) * LBL_FAC[kk[4:]]; o.scale = (s, s, s); o.location = posf(T); key(o, 'scale', 'location', f=f)
    c = shot.cam(T); cam.location = c['pos']; cam.rotation_euler = look_rot(c['pos'], c['look'], c.get('up', (0, 0, 1))); cam.data.lens = c['lens']
    key(cam, 'location', 'rotation_euler', f=f); cam.data.keyframe_insert('lens', frame=f)
    ev['cam'] = [round(x, 3) for x in c['pos']]; events['frames'].append(ev)

def all_ads():
    for ob in list(bpy.data.objects) + [cam.data] + list(bpy.data.curves) + list(bpy.data.armatures):
        if getattr(ob, 'animation_data', None) and ob.animation_data.action: yield ob.animation_data
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action: yield m.node_tree.animation_data
for ad in all_ads():
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
fcs = [fc for fc in (cam.animation_data.action.fcurves if cam.animation_data else []) if fc.data_path == 'rotation_euler']
for fc in fcs:
    pts = fc.keyframe_points
    for i in range(1, len(pts)):
        d = pts[i].co[1] - pts[i - 1].co[1]
        while d > math.pi: pts[i].co[1] -= 2 * math.pi; d -= 2 * math.pi
        while d < -math.pi: pts[i].co[1] += 2 * math.pi; d += 2 * math.pi
sc.frame_start, sc.frame_end = fr[0], fr[-1]; sc.frame_step = step
out = os.path.join(HERE, 'frames' if FINAL else 'preview', shot.name); os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(HERE, 'events'), exist_ok=True); json.dump(events, open(os.path.join(HERE, 'events', f'{shot.name}.json'), 'w'))
print(f'[{shot.name}] cena pronta em {time.time() - t0:.1f}s; quadros {fr[0]}–{fr[-1]} ({len(fr)}), {W}x{H}, {spp} spp, passo {step}', flush=True)
if a.save_blend: os.makedirs(os.path.join(HERE, 'build'), exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'build', f'{shot.name}.blend'))
if a.still is not None:
    sc.frame_set(a.still); sc.render.filepath = os.path.join(out, f'still_{a.still:04d}.png'); sc.render.use_overwrite = True
    bpy.ops.render.render(write_still=True)
else:
    if a.frames:
        f0, f1 = map(int, a.frames.split('-')); sc.frame_start, sc.frame_end = f0, f1
    sc.render.filepath = os.path.join(out, '####'); t1 = time.time(); bpy.ops.render.render(animation=True)
    print(f'[{shot.name}] render {time.time() - t1:.1f}s', flush=True)
