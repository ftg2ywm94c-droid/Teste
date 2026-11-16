"""Planos do vídeo 08 (e se o fogo nunca tivesse sido descoberto?). T = tempo da narração (s), amarrado a analysis/narracao/08_words.json.
Estilo 2 (v2/ESTILO.md): chicote de câmera entre planos, push-in nas palavras-chave, snap nas poses, acabamento em camadas.
Tipos de cenário: dia / noite (savana), estudio (objetos, cérebro), globo (Terra à noite)."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, '..', 'lib'), os.path.join(HERE, '..'), HERE]
from story import sstep
from shots import pchip, ease

FPS = 30
END = 65.90           # narração termina em 65,86 s

class Shot:
    def __init__(self, name, t0, t1, kind, desc):
        self.name, self.t0, self.t1, self.kind, self.desc = name, t0, t1, kind, desc
        self.labels = []; self.panel = None
    @property
    def frames(self): return range(round(self.t0 * FPS), round(self.t1 * FPS))

def _front(c, d, up):
    p, l = c['pos'], c['look']; v = [b - a for a, b in zip(p, l)]; n = math.sqrt(sum(x * x for x in v))
    return (p[0] + v[0] / n * d, p[1] + v[1] / n * d, p[2] + v[2] / n * d + up)
def follow(shot, d, up): return lambda T: _front(shot.cam(T), d, up)
def eased(knots):
    f = ease(knots); a, b = knots[0][0], knots[-1][0]
    return lambda T: f(min(max(T, a), b))
def cam(pos_knots, look_knots, lens=35):
    P, L = eased(pos_knots), eased(look_knots)
    return lambda T: dict(pos=P(T), look=L(T), lens=lens)
def _ll(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return (r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la))

YEL, RED, WHITE, BLUE, GREEN, CYAN, ORANGE = (1.0, 0.80, 0.08), (1.0, 0.22, 0.14), (0.97, 0.97, 0.97), (0.45, 0.72, 1.0), (0.35, 0.95, 0.45), (0.35, 0.95, 1.0), (1.0, 0.55, 0.12)
SHOTS = []
def S(*a):
    s = Shot(*a); SHOTS.append(s); return s

TEO = (0.0, 0.0, 0.0)            # Téo sentado numa pedra, de frente para -Y
FIRE = (0.0, 1.9, 0.0)           # fogueira atrás/à frente conforme o plano
RING = [(FIRE[0] + 1.75 * math.cos(a), FIRE[1] + 1.75 * math.sin(a)) for a in (math.radians(d) for d in (25, 70, 115, 160))]

# ================================================================= CHOQUE
A1 = S('A1', 0.00, 5.08, 'dia', 'sem fogo, você passaria quase metade do dia mastigando')
A1.cam = cam([(0.0, (1.6, -4.2, 1.3)), (5.08, (0.7, -2.4, 1.05))], [(0.0, (0.0, 0.0, 0.85)), (5.08, (0.0, 0.0, 0.95))], 35)
A1.teo = 'chew'; A1.push = (2.34,); A1.whip = False
A1.panel = ('relogio', 1.70, 99, (2.34, 3.60), 0.48, 'quase metade do dia', RED)
# ================================================================= O COMENTÁRIO
B1 = S('B1', 5.08, 10.24, 'dia', 'essa pergunta veio de um inscrito, o desORDEM2026')
B1.cam = cam([(5.08, (-2.6, -5.0, 1.6)), (10.24, (-2.0, -4.2, 1.5))], [(5.08, (0.0, 0.0, 0.9)), (10.24, (0.0, 0.0, 0.9))], 35)
B1.teo = 'chew'; B1.dim = 0.45
B1.panel = ('card', 5.20, 99, 6.60)
B2 = S('B2', 10.24, 14.06, 'noite', 'e se o fogo nunca tivesse sido descoberto?')
B2.cam = cam([(10.24, (0.0, -2.2, 1.2)), (14.06, (0.0, -1.5, 0.9))], [(10.24, FIRE[:2] + (0.5,)), (14.06, FIRE[:2] + (0.45,))], 30)
B2.fire = (0.0, 12.56)            # acesa até "descoberto", depois apaga em 5 quadros
B2.panel = ('card_top', 10.24, 99)
# ================================================================= COMIDA
C1 = S('C1', 14.06, 16.44, 'dia', 'e o pior nem é a comida')
C1.cam = cam([(14.06, (0.6, -2.9, 1.15)), (16.44, (0.4, -2.3, 1.1))], [(14.06, (0.0, 0.0, 0.95)), (16.44, (0.0, 0.0, 1.0))], 35)
C1.teo = 'alarm'; C1.push = (14.36,); C1.t_pose = 14.30
C2 = S('C2', 16.44, 19.36, 'estudio', 'comida crua rende menos energia')
C2.cam = cam([(16.44, (0.0, -6.2, 2.4)), (19.36, (0.6, -5.4, 2.2))], [(16.44, (0.0, 0.0, 0.9)), (19.36, (0.0, 0.0, 0.9))], 35)
C2.food = True; C2.panel = ('energia', 16.60, 99, (17.70, 18.30))
C2.labels = [('crua', 'crua', WHITE, 0.32, 16.88, 99, lambda T: (-1.2, 0.0, 1.9)), ('cozida', 'cozida', ORANGE, 0.32, 17.40, 99, lambda T: (1.2, 0.0, 1.9))]
C3 = S('C3', 19.36, 24.08, 'dia', 'um primata do nosso tamanho passaria metade do dia comendo')
C3.cam = cam([(19.36, (-4.5, -7.5, 2.6)), (24.08, (-3.4, -6.4, 2.2))], [(19.36, (0.0, 0.0, 0.9)), (24.08, (0.0, 0.0, 0.9))], 30)
C3.teo = 'chew'; C3.timelapse = (19.4, 24.0)
C3.panel = ('relogio', 19.50, 99, (21.14, 23.00), 0.48, 'primata do nosso tamanho: 48%', RED)
C4 = S('C4', 24.08, 26.76, 'dia', 'a gente passa cinco por cento')
C4.cam = cam([(24.08, (1.4, -3.4, 1.2)), (26.76, (0.9, -2.6, 1.1))], [(24.08, (0.0, 0.0, 0.95)), (26.76, (0.0, 0.0, 1.0))], 35)
C4.teo = 'relief'; C4.t_pose = 24.40; C4.push = (24.90,)
C4.panel = ('relogio', 24.10, 99, (24.90, 25.70), 0.05, 'a gente: ~5% (4,7%)', GREEN)
# ================================================================= NOITE
D1 = S('D1', 26.76, 30.24, 'noite', 'sem fogueira, a noite é só escuridão')
D1.cam = cam([(26.76, (2.5, -4.5, 1.4)), (30.24, (1.6, -3.2, 1.2))], [(26.76, (0.0, 0.0, 1.0)), (30.24, (0.0, 0.0, 1.0))], 32)
D1.teo = 'scared'; D1.fire = None; D1.teo_stand = True
D2 = S('D2', 30.24, 34.14, 'noite', 'e é em volta do fogo que a conversa vira história')
D2.cam = cam([(30.24, (2.4, -1.6, 2.0)), (34.14, (1.3, -0.9, 1.4))], [(30.24, FIRE[:2] + (0.7,)), (34.14, FIRE[:2] + (0.8,))], 30)
D2.fire = (30.40, 99); D2.group = True; D2.bubbles = (31.84, 32.36, 32.74)
# ================================================================= MUNDO MODERNO
E1 = S('E1', 34.14, 38.12, 'estudio', 'sem fogo, não tem aço, cerâmica nem vidro')
E1.cam = cam([(34.14, (0.0, -8.6, 2.6)), (38.12, (0.0, -7.8, 2.3))], [(34.14, (0.0, 0.0, 0.9)), (38.12, (0.0, 0.0, 0.9))], 26)
E1.objs = ((35.24, 'aço'), (36.06, 'cerâmica'), (37.06, 'vidro')); E1.objs_off = 37.70
E2 = S('E2', 38.12, 44.42, 'globo', 'quase sessenta por cento da eletricidade do mundo vem de queimar alguma coisa')
E2.cam = cam([(38.12, _ll(5, -10, 28.0)), (44.42, _ll(20, 15, 23.0))], [(38.12, (0, 0, 0)), (44.42, (0, 0, 0))], 35)
E2.panel = ('eletricidade', 38.30, 99, (38.86, 40.00))
# ================================================================= VIRADA
F1 = S('F1', 44.42, 47.30, 'noite', 'mas tem um detalhe que muda tudo')
F1.cam = cam([(44.42, (0.9, -2.2, 1.25)), (47.30, (0.5, -1.4, 1.15))], [(44.42, (0.0, 0.0, 1.1)), (47.30, (0.0, 0.0, 1.12))], 40)
F1.teo = 'think'; F1.t_pose = 44.70; F1.push = (45.24,); F1.fire = (0.0, 99); F1.fire_behind = True
F2 = S('F2', 47.30, 50.62, 'estudio', 'seu cérebro gasta um quinto da sua energia')
F2.cam = cam([(47.30, (1.2, -4.8, 2.4)), (50.62, (0.6, -4.0, 2.0))], [(47.30, (0.0, 0.0, 1.0)), (50.62, (0.0, 0.0, 1.0))], 35)
F2.brain = True; F2.panel = ('quinto', 47.40, 99, 48.70)
F3 = S('F3', 50.62, 55.66, 'estudio', 'a ciência suspeita que foi a comida cozida que pagou essa conta')
F3.cam = cam([(50.62, (-0.4, -8.4, 2.3)), (55.66, (0.3, -7.4, 2.1))], [(50.62, (0.0, 0.0, 1.1)), (55.66, (0.0, 0.0, 1.15))], 26)
F3.brain = True; F3.food_feed = (53.24, 54.30); F3.brain_glow = 54.02
F3.labels = [('hipotese', 'hipótese científica (Wrangham)', YEL, 0.22, 51.42, 99, lambda T: (0.0, 0.0, 2.85))]
# ================================================================= FINAL EM LOOP
G1 = S('G1', 55.66, 60.26, 'noite', 'sem fogo, talvez nem existisse alguém pra perguntar')
G1.cam = cam([(55.66, (0.0, -6.0, 1.8)), (60.26, (0.0, -7.5, 2.2))], [(55.66, (0.0, 0.0, 1.0)), (60.26, (0.0, 0.0, 1.0))], 32)
G1.fire = None; G1.panel = ('card_fade', 55.80, 99, 57.80)
G2 = S('G2', 60.26, 63.30, 'dia', 'e você ainda estaria mastigando')
G2.cam = cam([(60.26, (1.6, -4.2, 1.3)), (63.30, (0.9, -2.8, 1.1))], [(60.26, (0.0, 0.0, 0.85)), (63.30, (0.0, 0.0, 0.92))], 35)
G2.teo = 'chew'; G2.push = (61.66,)
H1 = S('H1', 63.30, END, 'dia', 'comenta o próximo e se. pode ser o seu')
H1.cam = cam([(63.30, (0.9, -2.8, 1.1)), (END, (2.4, -6.5, 2.0))], [(63.30, (0.0, 0.0, 0.92)), (END, (0.0, 0.0, 1.0))], 35)
H1.teo = 'wave'; H1.t_pose = 63.40; H1.dim = 0.4
H1.panel = ('cta', 63.35, 99, 65.02)

NOTES = {}   # notas na tela ficam no captions_cfg.py

BY_NAME = {s.name: s for s in SHOTS}
for a, b in zip(SHOTS, SHOTS[1:]): assert abs(a.t1 - b.t0) < 1e-6, (a.name, b.name)
assert SHOTS[0].t0 == 0.0 and abs(SHOTS[-1].t1 - END) < 1e-6
