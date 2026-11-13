"""한글패치 빌드: work/patch/ 아래에 바뀐 파일만 원본 경로 구조로 출력"""
import sys, os, json, glob, re, struct, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import mkfont, charmap, fontmap, brfnt

W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')).replace(chr(92), '/')
OUT = W + '/patch'
SYS = W + '/ext/DATA/sys'
TAG = re.compile(r'\{([0-9a-f]+)\}')

# ---------- 번역 로드 ----------
import hashlib
tr = {}
for f in glob.glob(W + '/text/out/b*.json'):
    tr.update(json.load(open(f, encoding='utf-8')))
H = lambda s: hashlib.sha1(s.encode('utf-8')).hexdigest()[:16]   # 원문 대신 원문 해시로 번역 연결

# ---------- 폰트 ----------
font_orig = open(ROOT + '/font/font.brfnt', 'rb').read()
font_new, CM = mkfont.make(font_orig)
FM = fontmap.cmaps(font_new)
CWB, _, _ = fontmap.cwdh(font_new)


def char_w(code):
    g = FM.get(code, 0)
    return font_new[CWB + 3 * g + 2]


def text_bytes(s):
    """번역문(태그 포함) -> 바이트"""
    out = bytearray()
    pos = 0
    for m in TAG.finditer(s):
        out += charmap.encode(s[pos:m.start()].replace('\n', '\0'), CM)
        tag = bytes.fromhex(m.group(1))
        if tag[:3] != b'\xff\x00\x01':          # 루비(후리가나) 명령은 제거
            out += tag
        pos = m.end()
    out += charmap.encode(s[pos:].replace('\n', '\0'), CM)
    return bytes(out)


def line_widths(b):
    """바이트 페이지 -> 줄별 픽셀 폭"""
    ws = [0]; i = 0
    while i < len(b):
        c = b[i]
        if c == 0xff:
            n = struct.unpack_from('>H', b, i + 3)[0]; i += 5 + 6 * n; continue
        if c == 0:
            ws.append(0); i += 1; continue
        if 0x81 <= c <= 0x9f or 0xe0 <= c <= 0xfc:
            ws[-1] += char_w(c << 8 | b[i + 1]); i += 2
        else:
            ws[-1] += char_w(c); i += 1
    return ws


stats = collections.Counter()
overflow = []


def tr_page(p):
    pre, body, suf = split_page(p)
    k = tok2str(body)
    ko = tr.get(H(k))
    if ko is None:
        return p
    stats['pages'] += 1
    ow = max(line_widths(b''.join(bm2_tok_bytes(body))) or [0])
    lim = max(ow, 300)
    ko = fit(ko, lim, k.count('\n') + 1)
    nb = text_bytes(ko)
    nw = max(line_widths(nb) or [0])
    if nw > lim + 4:
        overflow.append((nw, ow, ko))
    return b''.join(bm2_tok_bytes(pre)) + nb + b''.join(bm2_tok_bytes(suf))


def str_w(s):
    return max(line_widths(text_bytes(s)) or [0])


def wrap(words, nl, lim):
    # 단어들을 nl줄 이하로 폭 lim 안에 탐욕적으로 배치
    lines = ['']
    for w in words:
        t = (lines[-1] + ' ' + w) if lines[-1] else w
        if str_w(t) <= lim or not lines[-1]:
            lines[-1] = t
        else:
            lines.append(w)
    return lines


def fit(ko, lim, nl):
    if str_w(ko) <= lim + 4: return ko
    if TAG.search(ko) or '　' in ko: return ko
    words = ko.replace('\n', ' ').split(' ')
    words = [w for w in words if w]
    for n in (nl, nl + 1) if nl <= 2 else (nl,):
        # 폭을 조금씩 줄여 가며 균형 잡힌 n줄 배치 탐색
        best = None
        for L in range(lim, 120, -8):
            ls = wrap(words, n, L)
            if len(ls) > n: break
            best = ls
        if best and len(best) <= n and max(str_w(x) for x in best) <= lim + 4:
            stats['rewrap'] += 1
            return '\n'.join(best)
    return ko


def bm2_tok_bytes(ts):
    for t in ts:
        if t[0] == 't': yield t[1].encode('cp932')
        elif t[0] == 'n': yield b'\0'
        else: yield t[1]


def tr_msg(m):
    P = bm2.parse(m)
    for l in P['labs']:
        l['pages'] = [tr_page(p) for p in l['pages']]
    return bm2.build(P)


def tr_file(d):
    if d[8:12] == b'FLW0':
        m = flw.get_msg(d)
        if not m: return d
        return flw.set_msg(d, tr_msg(m))
    if d[4:8] == b'MSG2':
        return tr_msg(d)
    return d


def put(rel, data):
    p = OUT + '/files/' + rel
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(data)


def main():
    import shutil
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    nfile = 0
    for f in sorted(glob.glob(ROOT + '/**/*', recursive=True)):
        f = f.replace(chr(92), '/')
        if not is_lang_ok(f) or os.path.isdir(f): continue
        rel = f[len(ROOT) + 1:]
        if f.endswith('.pak'):
            d = open(f, 'rb').read()
            ents = pak.read(d); changed = False
            for e in ents:
                n, x = e
                if n and is_lang_ok('/' + n) and n.endswith(('.bf', '.bm2')) and x[:1] == b'\x10':
                    u = lz.dec(x); v = tr_file(u)
                    if v != u:
                        e[1] = lz.enc(v); changed = True
            if changed:
                put(rel, pak.write(ents)); nfile += 1
        elif f.endswith(('.bf', '.bm2')):
            d = open(f, 'rb').read(); v = tr_file(d)
            if v != d: put(rel, v); nfile += 1
    put('font/font.brfnt', font_new)
    # ---------- DOL ----------
    import doltest
    dol, nd = doltest.patch_dol(open(SYS + '/main.dol', 'rb').read())
    os.makedirs(OUT + '/sys', exist_ok=True)
    open(OUT + '/sys/main.dol', 'wb').write(dol)
    import texjobs; texjobs.run()
    json.dump(sorted(overflow, reverse=True)[:400], open(W + '/text/overflow.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('files', nfile, 'dol', nd, dict(stats), 'overflow', len(overflow))


if __name__ == '__main__':
    main()
