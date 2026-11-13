"""그림 글자 한글화 작업 목록 (빌드 후 실행: patch/files 에 출력)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from texedit import *
from PIL import ImageDraw
OR = (217, 167, 1, 255); BL = (20, 40, 220, 255); GR = (118, 118, 118, 255); DG = (111, 112, 112, 255)
NB = 'NanumSquareNeo-cBd.ttf'; NE = 'NanumSquareNeo-dEb.ttf'; SH = 'SeoulHangangEB.ttf'

def clear(img, box, c=(0, 0, 0, 0)):
    ImageDraw.Draw(img).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=c)

def strap_lower(img):
    clear(img, (35, 345, 605, 445), (255, 255, 255, 255)); f = font(NE, 23)
    draw_line(img, (42, 357), [('스트랩을 손목에 걸고, ', OR), ('스토퍼', BL), ('를 조여 고정하세요', OR)], f, 560)
    draw_line(img, (42, 386), [('리모컨을 단단히 쥐고, 손에서 놓거나 던지지 마세요', OR)], f, 560)
    draw_line(img, (42, 415), [('Wii 리모컨 재킷 장착을 권장합니다', OR)], f, 560)
    return img

def strapA(img):
    strap_lower(img); clear(img, (250, 212, 610, 285), (255, 255, 255, 255)); f = font(NB, 22)
    draw_line(img, (258, 226), [('주위에 사람이나 물건이 없는지', GR)], f, 345)
    draw_line(img, (258, 256), [('잘 확인하세요', GR)], f, 345)
    return img

def strapB(img):
    strap_lower(img); clear(img, (290, 212, 610, 312), (255, 255, 255, 255)); f = font(NB, 22)
    draw_line(img, (298, 228), [('확장 컨트롤러를 사용할 때는', GR)], f, 305)
    draw_line(img, (298, 257), [('스트랩 끈을', GR)], f, 305)
    draw_line(img, (298, 286), [('플러그의 고리', BL), ('에 걸어 주세요', GR)], f, 305)
    return img

def nunchaku(img):
    clear(img, (265, 170, 625, 240), (255, 255, 255, 255)); f = font(NB, 19)
    draw_line(img, (273, 182), [('이 게임은 눈차크를 사용합니다.', DG)], f, 345)
    draw_line(img, (273, 211), [('눈차크 스타일로 즐겨 주세요.', DG)], f, 345)
    return img

def disclaimer(img):
    clear(img, (1, 136, 256, 286)); f = font(NB, 16); c = (200, 200, 200, 230)
    L = ['이 게임은 픽션이며,', '실존 인물, 국가, 단체, 지명 등과', '일절 관계가 없습니다.', '또한 게임에 등장하는 병명,', '의료 기술 등은 모두 가공의 것입니다.', '양해 바랍니다.']
    for i, s in enumerate(L): draw_line(img, (128, 139 + 24 * i), [(s, c)], f, 252, 'center')
    return img

def diffhelp(img):
    clear(img, (28, 184, 418, 250), (0, 0, 0, 128)); f = font(NB, 16)
    draw_line(img, (222, 189), [('시작할 때의 난이도를 선택하세요.', (255, 255, 255, 255))], f, 380, 'center')
    draw_line(img, (222, 219), [('난이도는 게임 도중에도 바꿀 수 있습니다.', (255, 255, 255, 255))], f, 380, 'center')
    return img

def opstart(img):
    f = font(SH, 34)
    for (x, y, w, h), s in zip([(353, 2, 157, 42), (353, 45, 157, 42), (353, 88, 157, 42)], ['수술 개시', '수술 실패', '수술 성공']):
        clear(img, (x, y, x + w, y + h)); draw_line(img, (x + w // 2, y), [(s, (255, 255, 255, 255))], f, w - 2, 'center')
    return img

def logo(img):
    import cv2, numpy as np
    from PIL import ImageFilter
    a = np.array(img); box = (168, 201, 270, 234)
    m = np.zeros(a.shape[:2], np.uint8); reg = a[box[1]:box[3], box[0]:box[2]]
    m[box[1]:box[3], box[0]:box[2]] = ((reg[..., :3].min(-1) > 150) & (reg[..., 3] > 100)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, 4, cv2.INPAINT_TELEA)
    al = cv2.inpaint(np.ascontiguousarray(a[..., 3]), m, 4, cv2.INPAINT_TELEA)
    img = Image.fromarray(np.dstack([rgb, al]), 'RGBA')
    L = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f6 = font(SH, 30); fk = font(SH, 19)
    w6 = f6.getlength('6'); wk = fk.getlength('인의 의사'); x0 = 219 - (w6 + 3 + wk) / 2
    for f, x, y, t in ((f6, x0, 199, '6'), (fk, x0 + w6 + 3, 207, '인의 의사')):
        d.text((x, y), t, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    sh = L.filter(ImageFilter.GaussianBlur(1.5)); img.alpha_composite(sh); img.alpha_composite(L)
    return img

FLOW_TITLES = {
 0: ['꽃에 잠든 소녀', '가면의 죄수', '얼어붙은 시간 속에서', '불청객', '저주받은 과거', '악몽에서 깨어나다', '결의의 칼날', '각성하는 신의 손', '죄인이여 편히 잠들라'],
 1: ['잿빛 일상', '진단의의 우울', '불꽃과 어둠', '움직이는 마음', '가장 쉬운 사실', '떠나가는 남자'],
 2: ['캡틴 이글', '어 빅 가이', '이즈 인 트러블', '더트 앤드 러브', '어 하트브로큰', '렛 미 빌리브', '저스트 어 히어로'],
 3: ['불덩이 GIRL', '험악 MOOD', '짜증 MAX', '슬픈 HERO', '당황 GHOST', '결사의 RESCUE', '열정 TEAM'],
 4: ['뜻밖의 재회', '밀실의 습격자', '방랑 소녀', '거짓의 진실', '분노의 살인자', '속죄의 추격', '여정의 끝에'],
 5: ['종가의 딸', '망설임과 미소', '충실한 한때', '꼭두각시의 근심', '무신의 피를 이은 자', '각오', '보지 못한 미래로'],
 6: ['감염자 제로', '그리고 죽음이 시작된다', '긍지 높은 자', '빼앗긴 기억과 공포', '감염 확대', '클로이의 병변', '죽음과 악마'],
 7: ['소녀의 행방', '동료', '푸른 죽음의 병상', '절망', '환희의 순간', '로잘리아 변이종', '7번째 의사에게'],
}

def sprite_text(rel, table, fname, size, color, align='left'):
    T = Tex(rel)
    by = {}
    for sp in T.spr:
        k = sp['tex'] >> 16
        if k in table: by.setdefault(k, []).append(sp)
    jobs = []
    for k, L in table.items():
        sps = sorted(by[k], key=lambda q: q['y'])
        def fn(img, sps=sps, L=L):
            f = font(fname, size)
            for sp, txt in zip(sps, L):
                if txt is None: continue
                clear(img, (sp['x'], sp['y'], sp['x'] + sp['w'], sp['y'] + sp['h']))
                asc, desc = f.getmetrics(); y = sp['y'] + (sp['h'] - (asc + desc)) // 2 - 2
                x = sp['x'] + (sp['w'] // 2 if align == 'center' else 0)
                draw_line(img, (x, y), [(txt, color)], f, sp['w'], align)
            return img
        T.edit(k, fn)
    T.save(); print('tex', rel)

CARDS = {'110_010':'얼어붙은 시간 속에서','120_010':'불청객','130_010':'저주받은 과거','140_010':'악몽에서 깨어나다','150_010':'결의의 칼날',
 '160_010':'각성하는 신의 손','210_010':'진단의의 우울','220_010':'불꽃과 어둠','230_010':'움직이는 마음','240_010':'가장 쉬운 사실',
 '310_010':'어 빅 가이','320_010':'이즈 인 트러블','330_010':'더트 앤드 러브','340_010':'어 하트브로큰','350_010':'렛 미 빌리브',
 '410_010':'험악 MOOD','420_010':'짜증 MAX','430_010':'슬픈 HERO','440_010':'당황 GHOST','450_010':'결사의 RESCUE',
 '510_010':'밀실의 습격자','520_010':'방랑 소녀','530_010':'거짓의 진실','540_010':'분노의 살인자','550_010':'속죄의 추격',
 '610_010':'망설임과 미소','620_010':'충실한 한때','630_010':'꼭두각시의 근심','640_010':'무신의 피를 이은 자','650_010':'각오',
 '710_010':'그리고 죽음이 시작된다','720_010':'긍지 높은 자','730_010':'빼앗긴 기억과 공포','740_010':'감염 확대','750_010':'클로이의 병변',
 '760_010':'죽음과 악마','770_010':'소녀의 행방','780_013':'동료','790_010':'푸른 죽음의 병상에서','7A0_010':'절망','7B0_010':'환희의 순간','7C0_010':'로잘리아 변이종'}

def cards():
    import brres, cmpr, numpy as np
    f = font(SH, 32)
    for k, txt in CARDS.items():
        rel = f'model/comic/{k}_990.brres'; d = bytearray(open(SRC + rel, 'rb').read())
        t = [x for x in brres.tex0s(bytes(d)) if x['name'] == k + '_990'][0]
        img = Image.new('RGB', (512, 128), (0, 0, 0)); dr = ImageDraw.Draw(img)
        sp = 6; ws = [f.getlength(c) for c in txt]; tw = sum(ws) + sp * (len(txt) - 1)
        sc = min(1.0, 480 / tw); x = 256 - tw * sc / 2
        layer = Image.new('RGB', (int(tw) + 8, 128), (0, 0, 0)); ld = ImageDraw.Draw(layer); xx = 4
        for c, w in zip(txt, ws): ld.text((xx, 62), c, font=f, fill=(255, 255, 255), anchor='lm'); xx += w + sp
        if sc < 1: layer = layer.resize((int(layer.width * sc), 128), Image.LANCZOS)
        img.paste(layer, (int(256 - layer.width / 2), 0))
        b = cmpr.encode(np.array(img)); d[t['doff']:t['doff'] + len(b)] = b
        os.makedirs(os.path.dirname(OUT + rel), exist_ok=True); open(OUT + rel, 'wb').write(d)
    print('cards', len(CARDS))

def sprite_idx(rel, items, fname, size, color):
    T = Tex(rel); by = {}
    for i, txt in items.items(): sp = T.spr[i]; by.setdefault(sp['tex'] >> 16, []).append((sp, txt))
    for k, L in by.items():
        def fn(img, L=L):
            f = font(fname, size)
            for sp, txt in L:
                clear(img, (sp['x'], sp['y'], sp['x'] + sp['w'], sp['y'] + sp['h']))
                asc, desc = f.getmetrics(); y = sp['y'] + (sp['h'] - (asc + desc)) // 2 - 1
                draw_line(img, (sp['x'] + sp['w'] // 2, y), [(txt, color)], f, sp['w'], 'center')
            return img
        T.edit(k, fn)
    T.save(); print('tex', rel)

def glow_text(txt, glow, size, sp=0):
    def fn(img):
        from PIL import ImageFilter
        W, H = img.size; clear(img, (0, 0, W, H))
        f = font(NE, size); L = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        ws = [f.getlength(c) for c in txt]; tw = sum(ws) + sp * (len(txt) - 1); x = (W - tw) / 2
        for c, w in zip(txt, ws): d.text((x, H / 2), c, font=f, fill=(255, 255, 255, 255), anchor='lm'); x += w + sp
        a = L.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5))
        G = Image.new('RGBA', img.size, glow); G.putalpha(a.point(lambda v: min(255, v * 2)))
        img.alpha_composite(G); img.alpha_composite(L); return img
    return fn

EXTRA = ['sprite/autopsy/desktop/pc_win.tpx', 'sprite/diagnostic/menu/top.tpx', 'sprite/flow/title_jpn.tpx']
JOBS = {
    'sprite/autopsy/desktop/pc_win.tpx': [(16, glow_text('규 명', (230, 90, 20, 255), 40, 10)), (17, glow_text('증거 완성', (40, 150, 255, 255), 30))],
    'title/title.tpx': [(5, logo)],
    'title/hanken.tpx': [(1, strapA), (2, strapB), (9, nunchaku), (0, disclaimer)],
    'title/k_title00.tpx': [(12, diffhelp)],
    'operation/i_op_start01tpx.tpx': [(0, opstart)],
}

def run(preview=None):
    for rel, jobs in JOBS.items():
        T = Tex(rel)
        for k, fn in jobs:
            im = T.edit(k, fn)
            if preview:
                b = Image.new('RGBA', im.size, (40, 60, 90, 255)); b.alpha_composite(im)
                b.convert('RGB').save(f"{preview}/{rel.split('/')[-1][:-4]}_{k}.png")
        T.save(); print('tex', rel)
    cards()
    sprite_idx('sprite/diagnostic/menu/top.tpx', {0: '발견된 증상', 1: '문진', 2: '청진', 3: '심전도', 4: '분석 검사'}, NE, 19, (255, 255, 255, 255))
    sprite_text('sprite/flow/title_jpn.tpx', FLOW_TITLES, NB, 19, (205, 205, 205, 255))
    import texpatch, json
    J = json.load(open(texpatch.W + '/text/tex.json', encoding='utf-8'))
    for rel, cfg in J.items():
        texpatch.patch_tpx(rel, {int(k): v for k, v in cfg['items'].items()}, cfg['font'], cfg['size'], cfg.get('sx', 1.0)); print('tex', rel)
    import tutpatch; tutpatch.run()
    endlogo_job()
    sync_paks()

def sync_paks():
    import glob, pak, lz
    import tutpatch
    done = {r for r in JOBS} | set(EXTRA) | set(__import__('json').load(open(W + '/text/tex.json', encoding='utf-8'))) | {k.split('#')[0] for k in tutpatch.load_all()}
    for f in glob.glob(SRC + '**/*.pak', recursive=True):
        f = f.replace(chr(92), '/'); rel = f[len(SRC):]
        src = OUT + rel if os.path.exists(OUT + rel) else f
        try: ents = pak.read(open(src, 'rb').read())
        except Exception: continue
        ch = False
        for e in ents:
            for r in done:
                if e[0] and e[0] == r.split('/')[-1] and os.path.dirname(r) == os.path.dirname(rel):
                    e[1] = lz.enc(open(OUT + r, 'rb').read()); ch = True
        if ch:
            os.makedirs(os.path.dirname(OUT + rel), exist_ok=True); open(OUT + rel, 'wb').write(pak.write(ents)); print('pak', rel)

def endlogo(img):
    import cv2, numpy as np
    from PIL import ImageFilter
    a = np.array(img.convert('RGB')); box = (392, 330, 615, 392)
    m = np.zeros(a.shape[:2], np.uint8); reg = a[box[1]:box[3], box[0]:box[2]]
    m[box[1]:box[3], box[0]:box[2]] = (reg.min(-1) > 150).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    img = Image.fromarray(cv2.inpaint(np.ascontiguousarray(a), m, 6, cv2.INPAINT_TELEA)).convert('RGBA')
    L = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f6 = font(SH, 62); fk = font(SH, 40)
    w6 = f6.getlength('6'); wk = fk.getlength('인의 의사'); x0 = 503 - (w6 + 6 + wk) / 2
    for f, x, y, t in ((f6, x0, 326, '6'), (fk, x0 + w6 + 6, 343, '인의 의사')):
        d.text((x, y), t, font=f, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
    sh = L.filter(ImageFilter.GaussianBlur(3)); img.alpha_composite(sh); img.alpha_composite(L)
    return img

def endlogo_job(preview=None):
    import brres, cmpr, tpl, numpy as np
    rel = 'model/comic/800_010_990.brres'; d = bytearray(open(SRC + rel, 'rb').read())
    t = [x for x in brres.tex0s(bytes(d)) if x['name'] == '800_010_logo_TITLE_J'][0]
    img = endlogo(tpl.decode(bytes(d), t))
    if preview: img.save(preview); return
    b = cmpr.encode(np.array(img.convert('RGB'))); d[t['doff']:t['doff'] + len(b)] = b
    os.makedirs(os.path.dirname(OUT + rel), exist_ok=True); open(OUT + rel, 'wb').write(d); print('tex', rel)


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else None)
