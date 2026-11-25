"""Maquete da camada de texto nova (aprendizado das referências, no nosso estilo Poppins + amarelo):
HUD fixo (relógio + contador), palavra-chave no topo, legenda com palavra-chave colorida, onomatopeia carimbada, círculo.
Gera 4 quadros de exemplo em analysis/19_mock_overlays.jpg a partir dos quadros de conferência."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf'); f = lambda s: ImageFont.truetype(F, s)
ST = '/home/user/Teste/teste_xavier/out/nl_stills'
YEL, RED, WHT, INK = (255, 210, 20), (232, 52, 52), (255, 255, 255), (16, 14, 22)
W, H = 1080, 1920

def text(d, x, y, s, fill, size, anchor='mm', stroke=7):
    d.text((x, y), s, font=f(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)

def hud(d, clock, falta):
    d.rounded_rectangle((48, 150, 330, 330), 26, fill=(10, 12, 24, 170))
    d.ellipse((74, 178, 92, 196), fill=RED); text(d, 104, 187, 'NOITE LIVRE', WHT, 30, 'lm', 0)
    text(d, 72, 250, clock, WHT, 74, 'lm', 0)
    text(d, 74, 306, falta, RED, 32, 'lm', 0)

def keyword(d, s, color=YEL):
    text(d, W / 2, 420, s, WHT, 58, 'mm', 6)
    w = d.textlength(s, font=f(58)); d.rectangle((W / 2 - w / 2, 458, W / 2 + w / 2, 468), fill=color)

def caption(d, parts):   # [(texto, cor)]
    fo = f(76); total = sum(d.textlength(p + ' ', font=fo) for p, _ in parts); x = (W - total) / 2
    for p, c in parts:
        d.text((x, 1390), p, font=fo, fill=c, anchor='lm', stroke_width=8, stroke_fill=INK); x += d.textlength(p + ' ', font=fo)

def stamp(im, s, x, y, ang, color=RED):
    lay = Image.new('RGBA', (520, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((10, 10, 510, 190), 24, outline=color, width=12, fill=(255, 255, 255, 30))
    d.text((260, 100), s, font=f(96), fill=color, anchor='mm', stroke_width=5, stroke_fill=INK)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); im.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def frame(name, fn):
    im = Image.open(os.path.join(ST, name)).convert('RGBA').resize((W, H), Image.LANCZOS)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); fn(im, d)
    return Image.alpha_composite(im, ov)

out = [
    frame('0054.png', lambda im, d: (hud(d, '21:57', 'FALTAM 3 MIN'), caption(d, [('IMAGINA A', WHT), ('NOITE LIVRE', YEL)]))),
    frame('0945.png', lambda im, d: (hud(d, '21:58', 'FALTAM 2 MIN'), keyword(d, 'O PORTÃO ABERTO'), stamp(im, 'AU! AU!', 760, 860, 10),
                                     caption(d, [('O THOR TÁ', WHT), ('NA RUA', YEL)]))),
    frame('1048.png', lambda im, d: (hud(d, '21:58', 'FALTAM 2 MIN'), keyword(d, '3 MÁSCARAS', RED), d.ellipse((400, 650, 700, 1050), outline=YEL, width=10),
                                     caption(d, [('OLHANDO PRO', WHT), ('THOR', YEL)]))),
    frame('1377.png', lambda im, d: (hud(d, '21:59', 'FALTA 1 MIN'), keyword(d, 'ELE VIU', RED), caption(d, [('E VIROU PRA', WHT), ('SUA CASA', RED)]))),
]
sheet = Image.new('RGB', (4 * 540 + 5 * 12, 960 + 24), 'white')
for i, im in enumerate(out): sheet.paste(im.convert('RGB').resize((540, 960), Image.LANCZOS), (12 + i * 552, 12))
sheet.save(os.path.join(ROOT, 'analysis', '19_mock_overlays.jpg'), quality=88)
print('ok')
