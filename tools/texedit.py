"""팔레트(형식255) C4/C8 텍스처 편집: 디코드 -> PIL 편집 -> 기존 팔레트로 재양자화"""
import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import tpx, tpl
W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')).replace(chr(92), '/')
SRC = W + '/ext/DATA/files/'; OUT = W + '/patch/files/'

def palette(t):
    pn = struct.unpack_from('>H', t, 0x14)[0]; pd = struct.unpack_from('>I', t, 0x1c)[0]
    a = np.frombuffer(t, np.uint8, pn * 4, pd).reshape(2, pn, 2)
    return np.stack([a[1, :, 1], a[0, :, 0], a[0, :, 1], a[1, :, 0]], -1).astype(int)  # RGBA

def geom(im):
    return (8, 8, 4) if im['fmt'] == 8 else (8, 4, 8)

def get_idx(t, im):
    w, h = im['w'], im['h']; bw, bh, bpp = geom(im)
    n = w * h * bpp // 8; d = np.frombuffer(t, np.uint8, n, im['doff'])
    if bpp == 4: d = np.stack([d >> 4, d & 15], -1).reshape(-1)
    return d.reshape(h // bh, w // bw, bh, bw).transpose(0, 2, 1, 3).reshape(h, w)

def put_idx(t, im, a):
    w, h = im['w'], im['h']; bw, bh, bpp = geom(im)
    d = a.reshape(h // bh, bh, w // bw, bw).transpose(0, 2, 1, 3).reshape(-1)
    if bpp == 4: d = d.reshape(-1, 2); d = d[:, 0] << 4 | d[:, 1]
    b = d.astype(np.uint8).tobytes(); t[im['doff']:im['doff'] + len(b)] = b

def quant(rgba, pal):
    def pm(c):
        c = c.astype(int); return np.concatenate([c[..., :3] * c[..., 3:4] // 255, c[..., 3:4] * 2], -1)
    px = pm(rgba.reshape(-1, 4)); pal = pm(pal); out = np.empty(len(px), np.int64)
    wgt = np.array([1, 1, 1, 1])
    for i in range(0, len(px), 20000):
        c = px[i:i + 20000]
        out[i:i + 20000] = ((((c[:, None, :] - pal[None]) ** 2) * wgt).sum(-1)).argmin(-1)
    return out.reshape(rgba.shape[:-1])

class Tex:
    def __init__(self, rel):
        self.rel = rel; self.d = bytearray(open(SRC + rel, 'rb').read())
        self.tex, self.spr = tpx.parse(bytes(self.d))
    def edit(self, k, fn):
        T = self.tex[k]; t = bytearray(self.d[T['off']:T['off'] + T['size']])
        im = tpl.tpl_images(bytes(t))[0]; pal = palette(t)
        idx = get_idx(t, im); rgba = pal[idx].astype(np.uint8)
        img = Image.fromarray(rgba, 'RGBA'); orig = np.array(img).copy()
        img = fn(img)
        new = np.array(img); ch = (new != orig).any(-1)
        q = quant(new[ch], pal) if ch.any() else None
        if ch.any(): idx = idx.copy(); idx[ch] = q.reshape(-1)
        put_idx(t, im, idx); self.d[T['off']:T['off'] + T['size']] = t
        return Image.fromarray(pal[idx].astype(np.uint8), 'RGBA')
    def save(self):
        p = OUT + self.rel; os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(self.d)

def font(name, size):
    from fontpath import fp
    return ImageFont.truetype(fp(name), size)

def fill_auto(img, box):
    reg = np.array(img.crop(box)).reshape(-1, 4)
    vals, cnt = np.unique(reg, axis=0, return_counts=True); c = tuple(int(x) for x in vals[cnt.argmax()])
    ImageDraw.Draw(img).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=c)

def draw_line(img, xy, segs, fnt, maxw=None, align='left', stroke=0, stroke_fill=None):
    """segs: [(text, color)], 폭 넘치면 가로 압축. xy=(x, y_top)"""
    tw = sum(fnt.getlength(s) for s, _ in segs)
    asc, desc = fnt.getmetrics(); H = asc + desc + 2 * stroke + 4
    layer = Image.new('RGBA', (int(tw) + 2 * stroke + 4, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer); x = stroke + 2
    for s, c in segs:
        dr.text((x, stroke + 2), s, fill=c, font=fnt, stroke_width=stroke, stroke_fill=stroke_fill); x += fnt.getlength(s)
    if maxw and layer.width > maxw: layer = layer.resize((maxw, H), Image.LANCZOS)
    X = xy[0] - (layer.width // 2 if align == 'center' else 0)
    img.alpha_composite(layer, (int(X), int(xy[1])))
