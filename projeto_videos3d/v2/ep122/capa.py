# Capa do V122 (v3): quadro do próprio vídeo + textos Poppins (identidade da série).
import glob, sys
from PIL import Image, ImageDraw, ImageFont
F = int(sys.argv[1]) if len(sys.argv) > 1 else 360
m = {int(p.split('/')[-1][:4]): p for p in glob.glob('v2/ep122/frames/*/*.jpg')}
im = Image.open(m[F]).convert('RGB'); d = ImageDraw.Draw(im)
font = lambda s: ImageFont.truetype('fonts/Poppins-Bold.ttf', s)
INK, Y, W = (26, 18, 30), (255, 214, 10), (255, 255, 255)
def centered(txt, y, size, fill):
    f = font(size); w = d.textlength(txt, font=f)
    d.text(((1080 - w) / 2, y), txt, font=f, fill=fill, stroke_width=max(6, size // 14), stroke_fill=INK)
# selo do episódio
f = font(46); t = "THE KEY · EP. 2"; w = d.textlength(t, font=f)
d.rounded_rectangle(((1080 - w) / 2 - 34, 96, (1080 + w) / 2 + 34, 166), radius=35, fill=Y, outline=INK, width=4)
d.text(((1080 - w) / 2, 101), t, font=f, fill=INK)
centered("RUN.", 1350, 128, W)
centered("HE'S", 1500, 150, Y)
centered("CHASING YOU", 1665, 134, Y)
im.save('thumbnails/122_the_key_ep2_cover.jpg', quality=93)
print('capa do quadro', F, m[F])
