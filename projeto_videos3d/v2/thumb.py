"""Thumbnail vertical (1080x1920) a partir de um render nativo em 1080x1920.
Uso: python3 v2/thumb.py <config.json> <saida.png>
O config define: base (render), título em linhas [(texto, cor)], recorte opcional em círculo (inset) com etiqueta, e a gradação de cor.
Margem de segurança: nada importante nos 330 px de baixo nem nos 130 px da direita abaixo do meio (botões do TikTok/Reels)."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FONT = os.path.join(ROOT, 'fonts', 'Poppins-Bold.ttf')
W, H = 1080, 1920

def font(px): return ImageFont.truetype(FONT, px)

def grade(img, sky=(255, 90, 30), sky_amt=0.55, sky_to=0.55, contrast=1.18, sat=1.15, vignette=0.55, shadow_tint=(40, 0, 10)):
    sky, shadow_tint = tuple(sky), tuple(shadow_tint); img = img.convert('RGB').resize((W, H), Image.LANCZOS)
    # céu: gradiente quente de cima para baixo, aplicado mais nas áreas claras (céu) que nas escuras
    grad = Image.new('L', (1, H))
    for y in range(H): grad.putpixel((0, y), int(255 * max(0.0, 1 - y / (H * sky_to)) ** 1.2 * sky_amt))
    grad = grad.resize((W, H))
    lum = img.convert('L').point(lambda v: min(255, max(0, (v - 70) * 2)))
    mask = ImageChops.multiply(grad, lum)
    warm = ImageChops.multiply(img, Image.new('RGB', (W, H), sky))
    warm = ImageChops.screen(warm, Image.new('RGB', (W, H), (60, 10, 0)))
    img = Image.composite(warm, img, mask)
    img = ImageEnhance.Contrast(img).enhance(contrast); img = ImageEnhance.Color(img).enhance(sat)
    # sombras levemente avermelhadas
    img = ImageChops.add(img, Image.new('RGB', (W, H), shadow_tint).point(lambda v: v // 3))
    # vinheta
    v = Image.new('L', (W, H), 0); d = ImageDraw.Draw(v); d.ellipse((-W * 0.35, -H * 0.2, W * 1.35, H * 1.2), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220)); dark = ImageEnhance.Brightness(img).enhance(1 - vignette)
    return Image.composite(img, dark, v)

def text_block(img, lines, top, max_w=1000, gap=6):
    """lines: [(texto, cor RGB, tamanho máx)]. Texto centralizado, contorno preto grosso e sombra."""
    d = ImageDraw.Draw(img); y = top
    for txt, col, size in lines:
        px = size
        while px > 30 and d.textlength(txt, font=font(px)) > max_w: px -= 4
        f = font(px); tw = d.textlength(txt, font=f); x = (W - tw) / 2
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).text((x + 8, y + 12), txt, font=f, fill=200, stroke_width=px // 9)
        img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(img); d.text((x, y), txt, font=f, fill=tuple(col), stroke_width=max(6, px // 11), stroke_fill=(0, 0, 0))
        asc, desc = f.getmetrics(); y += asc + desc * 0.2 + gap
    return y

def inset(img, src, crop, center, diam, ring=(255, 45, 30), ring_w=14, tag=None):
    s = Image.open(src).convert('RGB').crop(tuple(crop)).resize((diam, diam), Image.LANCZOS)
    s = ImageEnhance.Contrast(s).enhance(1.12); s = ImageEnhance.Color(s).enhance(1.1)
    m = Image.new('L', (diam * 4, diam * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, diam * 4 - 1, diam * 4 - 1), fill=255); m = m.resize((diam, diam), Image.LANCZOS)
    cx, cy = center; x0, y0 = cx - diam // 2, cy - diam // 2
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((x0 - 30, y0 - 30, x0 + diam + 30, y0 + diam + 30), fill=255)
    img.paste(tuple(ring), (0, 0), glow.filter(ImageFilter.GaussianBlur(28)).point(lambda v: v * 0.7))
    d = ImageDraw.Draw(img); d.ellipse((x0 - ring_w, y0 - ring_w, x0 + diam + ring_w, y0 + diam + ring_w), fill=tuple(ring))
    img.paste(s, (x0, y0), m)
    if tag:
        txt, bg, fg, px = tag; f = font(px); tw = d.textlength(txt, font=f); asc, desc = f.getmetrics()
        bw, bh = tw + 44, asc + desc + 16; bx, by = cx - bw / 2, y0 + diam - bh * 0.35
        bx = min(max(bx, 20), W - 20 - bw)
        d.rounded_rectangle((bx + 6, by + 8, bx + bw + 6, by + bh + 8), 14, fill=(0, 0, 0))
        d.rounded_rectangle((bx, by, bx + bw, by + bh), 14, fill=tuple(bg), outline=(0, 0, 0), width=5)
        d.text((bx + 22, by + 6), txt, font=f, fill=tuple(fg))
    return img

def build(cfg):
    img = grade(Image.open(os.path.join(ROOT, cfg['base'])), **cfg.get('grade', {}))
    if 'inset' in cfg:
        i = cfg['inset']; img = inset(img, os.path.join(ROOT, i['src']), i['crop'], i['center'], i['diam'], i.get('ring', (255, 45, 30)), tag=i.get('tag'))
    text_block(img, cfg['title'], cfg.get('title_top', 110))
    return img

if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    img = build(cfg); img.save(out, optimize=True)
    img.convert('RGB').save(out.rsplit('.', 1)[0] + '.jpg', quality=93)
    print('ok', out)
