"""튜토리얼(HELP) 그림 속 일본어 -> 한국어 덧칠
text/tut/*.json : {"tutorial/di/xxx.tpx": [{"box":[x0,y0,x1,y1], "t":"텍스트", "f":"g9", "c":[r,g,b], "bg":[r,g,b], "a":"l"}, ...]}
  box : 지울 영역 (원본 픽셀 좌표, x1/y1 미포함)
  t   : 쓸 글자 ("\n" 줄바꿈 가능). 빈 문자열이면 지우기만.
  f   : g7 / g9 / g11 / g11b / g11c / n<크기>(나눔스퀘어네오 Bold)   기본 g9
  c   : 글자색 (생략하면 상자 안 원래 글자색 자동)
  bg  : 바탕색 (생략하면 상자 안 최빈색). "none" 이면 바탕 안 칠함
  a   : l(왼쪽, 기본) / c(가운데) / r(오른쪽)  — 세로는 상자 가운데
  dx,dy : 글자 위치 미세 조정
사용:
  python tools/tutpatch.py dump <폴더(di 등)>        -> shots/tut/<폴더>/<이름>.png (3배 확대 + 10px 격자)
  python tools/tutpatch.py prev <json파일>           -> shots/tutprev/<이름>.png (원본|결과 3배)
  (빌드) run() : patch/files 에 저장
"""
import sys, os, json, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from texedit import Tex, SRC, W
from fontpath import fp
FD = W + '/fonts/'
FONTS = {'g7': ('Galmuri7.ttf', 8), 'g9': ('Galmuri9.ttf', 10), 'g11': ('Galmuri11.ttf', 12),
         'g11b': ('Galmuri11-Bold.ttf', 12), 'g11c': ('Galmuri11-Condensed.ttf', 12)}


def fnt(name):
    if name.startswith('n'):
        return ImageFont.truetype(fp('NanumSquareNeo-cBd.ttf'), int(name[1:]))
    f, s = FONTS[name]
    return ImageFont.truetype(fp(f), s)


def apply(img, items):
    a = np.array(img)
    dr = ImageDraw.Draw(img)
    for it in items:
        x0, y0, x1, y1 = it['box']
        reg = a[y0:y1, x0:x1].reshape(-1, 4).astype(int)
        vals, cnt = np.unique(reg, axis=0, return_counts=True)
        bgc = tuple(int(v) for v in vals[cnt.argmax()])
        if 'bg' in it and it['bg'] != 'none':
            bgc = tuple(it['bg']) + ((255,) if len(it['bg']) == 3 else ())
        if 'c' in it:
            fg = tuple(it['c']) + ((255,) if len(it['c']) == 3 else ())
        else:
            d = np.abs(reg[:, :3] - np.array(bgc[:3])).sum(1)
            far = reg[d >= np.percentile(d, 97)] if len(reg) else reg
            fg = tuple(int(v) for v in np.median(far, 0)) if len(far) else (0, 0, 0, 255)
            fg = fg[:3] + (255,)
        if it.get('bg') != 'none':
            dr.rectangle((x0, y0, x1 - 1, y1 - 1), fill=bgc)
        t = it.get('t', '')
        if not t: continue
        f = fnt(it.get('f', 'g9'))
        lines = t.split('\n')
        asc, desc = f.getmetrics(); lh = asc + desc
        total = lh * len(lines)
        y = y0 + (y1 - y0 - total) / 2 + it.get('dy', 0)
        for ln in lines:
            w = f.getlength(ln)
            lay = Image.new('RGBA', (int(w) + 2, lh), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((0, 0), ln, font=f, fill=fg)
            bw = x1 - x0
            if lay.width > bw:
                lay = lay.resize((bw, lh), Image.LANCZOS)
            al = it.get('a', 'l')
            x = x0 if al == 'l' else (x1 - lay.width if al == 'r' else x0 + (bw - lay.width) // 2)
            img.alpha_composite(lay, (int(x + it.get('dx', 0)), int(round(y))))
            y += lh
    return img


def load_all():
    J = {}
    for f in sorted(glob.glob(W + '/text/tut/*.json')):
        J.update(json.load(open(f, encoding='utf-8')))
    return J


def run():
    by = {}
    for key, items in load_all().items():
        if not items: continue
        rel, k = (key.split('#') + ['0'])[:2]
        by.setdefault(rel, []).append((int(k), items))
    for rel, jobs in by.items():
        T = Tex(rel)
        for k, items in jobs:
            T.edit(k, lambda im, items=items: apply(im, items))
        T.save()
    print('tut', len(load_all()))


def decode(rel, k=0):
    import tpl
    from texedit import palette, get_idx
    if '#' in rel: rel, k = rel.split('#'); k = int(k)
    T = Tex(rel); t = bytes(T.d[T.tex[k]['off']:T.tex[k]['off'] + T.tex[k]['size']])
    im = tpl.tpl_images(t)[0]
    return Image.fromarray(palette(t)[get_idx(t, im)].astype(np.uint8), 'RGBA')


def big(img, s=3, grid=True):
    b = Image.new('RGBA', img.size, (0, 0, 0, 255)); b.alpha_composite(img)
    b = b.convert('RGB').resize((img.width * s, img.height * s), Image.NEAREST)
    if grid:
        d = ImageDraw.Draw(b)
        for x in range(0, img.width, 10):
            d.line((x * s, 0, x * s, b.height), fill=(255, 0, 255) if x % 50 == 0 else (90, 90, 90))
        for y in range(0, img.height, 10):
            d.line((0, y * s, b.width, y * s), fill=(255, 0, 255) if y % 50 == 0 else (90, 90, 90))
        for x in range(0, img.width, 50): d.text((x * s + 2, 2), str(x), fill=(255, 255, 0))
        for y in range(50, img.height, 50): d.text((2, y * s + 2), str(y), fill=(255, 255, 0))
    return b


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'dump':
        out = W + '/shots/tut/' + sys.argv[2]; os.makedirs(out, exist_ok=True)
        for f in sorted(glob.glob(SRC + 'tutorial/' + sys.argv[2] + '/*.tpx')):
            rel = f.replace(chr(92), '/')[len(SRC):]
            try: big(decode(rel)).save(out + '/' + os.path.basename(f)[:-4] + '.png')
            except Exception as e: print('ERR', rel, e)
        print(out)
    elif c == 'one':
        out = W + '/shots/tut/one'; os.makedirs(out, exist_ok=True)
        for key in sys.argv[2:]:
            big(decode(key)).save(out + '/' + os.path.basename(key).replace('.tpx', '').replace('#', '_') + '.png')
        print(out)
    elif c == 'prev':
        J = json.load(open(sys.argv[2], encoding='utf-8'))
        out = W + '/shots/tutprev'; os.makedirs(out, exist_ok=True)
        names = sys.argv[3:]
        for rel, items in J.items():
            n = os.path.basename(rel).replace('.tpx', '').replace('#', '_')
            if names and n not in names: continue
            o = decode(rel); r = apply(o.copy(), items)
            a, b = big(o, 3, False), big(r, 3, False)
            s = Image.new('RGB', (a.width * 2 + 6, a.height), (255, 0, 0)); s.paste(a, (0, 0)); s.paste(b, (a.width + 6, 0))
            s.save(out + '/' + n + '.png')
        print(out)
