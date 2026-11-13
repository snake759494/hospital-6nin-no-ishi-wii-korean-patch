"""그림 글자 텍스처 한글화: ext 원본 tpx -> patch/files/... (C4 + 알파 램프 팔레트)"""
import sys, os, struct, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import tpx, tpl
W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')).replace(chr(92), '/')
SRC = W + '/ext/DATA/files/'
OUT = W + '/patch/files/'

def c4_get(t, im):
    """C4 인덱스 배열 (h,w)"""
    w, h = im['w'], im['h']; d = np.frombuffer(t, np.uint8, (w * h) // 2, im['doff'])
    tiles = d.reshape(h // 8, w // 8, 8, 4)
    hi = tiles >> 4; lo = tiles & 15
    px = np.stack([hi, lo], -1).reshape(h // 8, w // 8, 8, 8)
    return px.transpose(0, 2, 1, 3).reshape(h, w)

def c4_put(t, im, a):
    w, h = im['w'], im['h']
    px = a.reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(h // 8, w // 8, 8, 4, 2)
    b = (px[..., 0] << 4 | px[..., 1]).astype(np.uint8).tobytes()
    t[im['doff']:im['doff'] + len(b)] = b

def ramp_of(t, im):
    """팔레트 hi 바이트(알파) 램프. 형식255 팔레트는 0x20 뒤 16엔트리가 알파 램프"""
    return [t[0x40 + 2 * i] for i in range(16)]

def render(text, font, size, w, h, sx=1.0, dy=0):
    from fontpath import fp
    f = ImageFont.truetype(fp(font), size)
    bb = f.getbbox(text)
    tw = bb[2] - bb[0]
    img = Image.new('L', (tw + 4, h * 2), 0)
    ImageDraw.Draw(img).text((2 - bb[0], (h * 2 - size) // 2 - (bb[1] - (size - (bb[3] - bb[1])) // 2) + dy), text, 255, font=f)
    # 세로 위치: 원래 글자 높이 가운데로
    nw = max(1, int(round(img.width * sx)))
    if nw > w: nw = w
    img = img.resize((nw, img.height), Image.LANCZOS)
    box = img.getbbox() or (0, 0, 1, 1)
    out = Image.new('L', (w, h), 0)
    cy = (box[1] + box[3]) // 2
    out.paste(img, ((w - nw) // 2, h // 2 - cy))
    return np.array(out)

def patch_tpx(rel, items, font, size, sx=1.0):
    d = bytearray(open(SRC + rel, 'rb').read())
    tex, spr = tpx.parse(bytes(d))
    for i, text in items.items():
        s = spr[i]; T = tex[s['tex'] >> 16]
        t = bytearray(d[T['off']:T['off'] + T['size']])
        im = tpl.tpl_images(bytes(t))[0]
        ramp = np.array(ramp_of(t, im))
        a = c4_get(t, im).copy()
        g = render(text, font, size, s['w'], s['h'], sx).astype(int)
        idx = np.abs(g[..., None] - ramp[None, None, :]).argmin(-1)
        a[s['y']:s['y'] + s['h'], s['x']:s['x'] + s['w']] = idx
        c4_put(t, im, a)
        d[T['off']:T['off'] + T['size']] = t
    p = OUT + rel; os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(d)
    return d

if __name__ == '__main__':
    J = json.load(open(W + '/text/tex.json', encoding='utf-8'))
    for rel, cfg in J.items():
        patch_tpx(rel, {int(k): v for k, v in cfg['items'].items()}, cfg['font'], cfg['size'], cfg.get('sx', 1.0))
        print('tex', rel, len(cfg['items']))
