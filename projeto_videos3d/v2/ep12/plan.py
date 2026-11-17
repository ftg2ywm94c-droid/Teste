"""Planos do vídeo 12 (suspense em 2ª pessoa: vendaval à noite, escolha A/B) na skill Xavier (Remotion + three.js).
O 3D é renderizado em 1080x1920 NATIVO em teste_xavier/src/videos/vendaval (story.ts tem os mesmos cortes)."""
FPS = 30; END = 71.16
NATIVE = True
SFX_BUS = (2.0, 2)   # ESTILO §9: efeitos num canal próprio, ducking leve
RENDER_RES = '1080x1920 nativo (Remotion + three.js, skill Xavier)'
W = dict(quando=3.78, tela=9.28, vendaval=13.16, voceOlha=17.28, dez=22.1, primeiro=25.12, depois=28.06, telha=31.62, luz=34.16, apaga=35.8,
         arvoreE=39.92, inclinando=43.28, celular2=46.02, opcaoA=50.34, opcaoB=54.34, eai=60.06, nao=66.74)
F = lambda t: round(t * FPS)
_keys = ['quando', 'tela', 'vendaval', 'voceOlha', 'dez', 'primeiro', 'depois', 'telha', 'luz', 'apaga', 'arvoreE', 'inclinando', 'celular2', 'opcaoA', 'opcaoB', 'eai', 'nao']
_cuts = [0] + [F(W[k]) - 1 for k in _keys] + [round(END * FPS)]
_names = ['S01_gancho', 'S02_alarme', 'S03_tela', 'S04_vendaval', 'S05_janela', 'S06_vento_chega', 'S07_fresta', 'S08_arvores', 'S09_telha',
          'S10_pisca', 'S11_escuro', 'S12_arvore', 'S13_inclina', 'S14_bateria', 'S15_opcao_a', 'S16_opcao_b', 'S17_escolha', 'S18_cta']
class Shot:
    def __init__(self, name, a, b): self.name, self.a, self.b, self.t0, self.t1 = name, a, b, a / FPS, b / FPS
    @property
    def frames(self): return range(self.a, self.b)
SHOTS = [Shot(n, _cuts[i], _cuts[i + 1]) for i, n in enumerate(_names)]
