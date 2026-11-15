"""Estilo 2 (teste a partir do vídeo 07): câmera viva, snap de poses e acabamento em camadas.
Liga só com STYLE2=1, para não mudar nada que já funciona.

- cam_fx: chicote (whip) na entrada e na saída do plano, push-in rápido nos tempos de shot.push, deriva leve contínua
  (a câmera nunca fica parada).
- snap / pose_seq: poses que entram em ~5 quadros com leve passagem do ponto (ease-out-back), mais respiração contínua
  (o personagem nunca congela).
- finish: compositor com brilho (glare), profundidade de campo pelo canal Z, correção de cor, leve aberração e vinheta.
  Não aumenta o tempo do Cycles (só o do compositor, alguns décimos de segundo por quadro).
"""
import math, os
from mathutils import Vector, Matrix

ON = bool(os.environ.get('STYLE2'))


def ease_out_back(u, s=1.70158):
    u = min(max(u, 0.0), 1.0) - 1.0
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def ease_out_cubic(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def snap(x, dur=0.17, back=True):
    """0 antes de x=0; chega a 1 em `dur` s (5 quadros a 30 fps), com leve passagem do ponto se back=True."""
    if x <= 0: return 0.0
    u = x / dur
    return ease_out_back(u) if back else ease_out_cubic(u)


# ------------------------------------------------------------------ câmera
def cam_fx(c, T, shot, whip_deg=16.0, whip_in=0.20, whip_out=0.13, push=0.16, drift=0.035):
    """Recebe o dict da câmera do plano (pos, look, lens) e devolve outro com os efeitos aplicados."""
    pos = Vector(c['pos']); look = Vector(c['look']); lens = c['lens']; lt = T - shot.t0; rt = shot.t1 - T
    ang = 0.0
    if getattr(shot, 'whip', True):
        if lt < whip_in: ang += math.radians(whip_deg) * (1 - lt / whip_in) ** 2          # entra rápido e desacelera
        if rt < whip_out: ang -= math.radians(whip_deg) * (1 - rt / whip_out) ** 2        # sai acelerando para o mesmo lado
    if ang:
        d = look - pos; look = pos + Matrix.Rotation(ang, 3, 'Z') @ d
    for tp in getattr(shot, 'push', ()):
        lens *= 1 + push * snap(T - tp, 0.20, back=False)
    pos = pos + Vector((math.sin(T * 0.83), math.sin(T * 0.61 + 1.3), math.sin(T * 0.97 + 2.1) * 0.5)) * drift
    out = dict(c); out.update(pos=tuple(pos), look=tuple(look), lens=lens)
    return out


# ------------------------------------------------------------------ poses
def blend(a, b, k):
    keys = set(a) | set(b); z = (0.0, 0.0, 0.0)
    return {n: tuple(a.get(n, z)[i] + (b.get(n, z)[i] - a.get(n, z)[i]) * k for i in range(3)) for n in keys}


def pose_seq(seq, t, breath=1.0):
    """seq: [(t0, pose_dict), ...] em ordem. Cada pose entra com snap a partir do seu t0.
    Soma respiração e balanço de cabeça contínuos. Devolve (dict de rotações, índice da pose atual, k do snap)."""
    cur = dict(seq[0][1]); idx = 0; k = 1.0
    for i, (t0, p) in enumerate(seq[1:], 1):
        if t >= t0:
            k = snap(t - t0); cur = blend(cur, p, k); idx = i
    z = (0.0, 0.0, 0.0)
    sp = cur.get('spine', z); hd = cur.get('head', z)
    cur['spine'] = (sp[0] + 1.6 * breath * math.sin(t * 2.4), sp[1], sp[2] + 1.2 * breath * math.sin(t * 0.9))
    cur['head'] = (hd[0] + 1.5 * breath * math.sin(t * 1.7 + 0.5), hd[1], hd[2] + 2.5 * breath * math.sin(t * 1.1 + 1.0))
    return cur, idx, k


# ------------------------------------------------------------------ acabamento
def finish(sc, cam, focus_dist, f_stop=2.2, grade=((0.98, 1.0, 1.04), (1.0, 1.0, 1.0), (1.04, 1.0, 0.95)),
           glare_mix=-0.75, glare_threshold=0.85, vignette=0.32, dispersion=0.012):
    """Monta o compositor: Render → Glare → Defocus (Z) → ColorBalance → LensDist → vinheta → Composite."""
    import bpy
    sc.view_layers[0].use_pass_z = True
    cam.data.dof.use_dof = False; cam.data.dof.focus_distance = focus_dist
    sc.use_nodes = True; nt = sc.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    N = nt.nodes.new; L = nt.links.new
    rl = N('CompositorNodeRLayers'); comp = N('CompositorNodeComposite')
    gl = N('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.quality = 'MEDIUM'; gl.mix = glare_mix; gl.threshold = glare_threshold; gl.size = 8
    df = N('CompositorNodeDefocus'); df.use_zbuffer = True; df.f_stop = f_stop; df.blur_max = 24; df.scene = sc
    cb = N('CompositorNodeColorBalance'); cb.correction_method = 'LIFT_GAMMA_GAIN'
    cb.lift, cb.gamma, cb.gain = grade[0], grade[1], grade[2]
    ld = N('CompositorNodeLensdist'); ld.inputs['Dispersion'].default_value = dispersion; ld.inputs['Distortion'].default_value = 0.0
    em = N('CompositorNodeEllipseMask'); em.width = 0.95; em.height = 0.80
    bl = N('CompositorNodeBlur'); bl.filter_type = 'FAST_GAUSS'; bl.use_relative = True; bl.factor_x = bl.factor_y = 30
    mx = N('CompositorNodeMixRGB'); mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = vignette
    inv = N('CompositorNodeInvert'); inv.inputs[0].default_value = 0.0      # máscara: 1 no centro, cai nas bordas
    L(rl.outputs['Image'], gl.inputs['Image']); L(gl.outputs['Image'], df.inputs['Image']); L(rl.outputs['Depth'], df.inputs['Z'])
    L(df.outputs['Image'], cb.inputs['Image']); L(cb.outputs['Image'], ld.inputs['Image'])
    L(em.outputs['Mask'], bl.inputs['Image']); L(bl.outputs['Image'], inv.inputs['Color'])
    L(ld.outputs['Image'], mx.inputs[1]); L(inv.outputs['Color'], mx.inputs[2]); L(mx.outputs['Image'], comp.inputs['Image'])
    sc.render.use_compositing = True
    return nt


def motion_blur(sc, shutter=0.5):
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = shutter
