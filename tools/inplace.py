"""복호화된 원본 ISO(dec.iso)의 데이터 파티션에 patch/ 파일을 제자리로 덮어쓴다.
원래 자리보다 커진 파일은 파티션 안의 빈 공간(파일들 사이 틈, 끝 여유)으로 옮기고 FST를 고친다.
사용: python tools/inplace.py dec.iso   (파일을 직접 수정)
그 뒤 wit copy dec.iso out.iso --enc encrypt 로 해시·암호화를 다시 한다."""
import sys, os, struct

W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')).replace(chr(92), '/')
PATCH = W + '/patch'
f = open(sys.argv[1], 'r+b')


def rd(o, n): f.seek(o); return f.read(n)


# 데이터 파티션 찾기
n, tbl = struct.unpack('>II', rd(0x40000, 8)); tbl <<= 2
part = None
for i in range(n):
    po, pt = struct.unpack('>II', rd(tbl + 8 * i, 8))
    if pt == 0: part = po << 2
doff, dsize = struct.unpack('>II', rd(part + 0x2b8, 8)); doff = part + (doff << 2); dsize <<= 2
NSEC = dsize // 0x8000; LSIZE = NSEC * 0x7c00


def lread(o, n):
    out = bytearray()
    while n:
        s, r = divmod(o, 0x7c00); k = min(n, 0x7c00 - r)
        out += rd(doff + s * 0x8000 + 0x400 + r, k); o += k; n -= k
    return bytes(out)


def lwrite(o, b):
    i = 0
    while i < len(b):
        s, r = divmod(o, 0x7c00); k = min(len(b) - i, 0x7c00 - r)
        f.seek(doff + s * 0x8000 + 0x400 + r); f.write(b[i:i + k]); o += k; i += k


boot = lread(0, 0x440)
dol_off = struct.unpack_from('>I', boot, 0x420)[0] << 2
fst_off = struct.unpack_from('>I', boot, 0x424)[0] << 2
fst_sz = struct.unpack_from('>I', boot, 0x428)[0] << 2
fst = bytearray(lread(fst_off, fst_sz))
cnt = struct.unpack_from('>I', fst, 8)[0]
strs = 12 * cnt


def name(i):
    no = struct.unpack_from('>I', fst, 12 * i)[0] & 0xffffff
    return fst[strs + no:fst.index(b'\0', strs + no)].decode('cp932')


# 경로 -> 엔트리 번호
paths = {}
stack = [(cnt, '')]
i = 1
while i < cnt:
    while stack and i >= stack[-1][0]: stack.pop()
    pre = stack[-1][1] if stack else ''
    isdir = fst[12 * i] == 1
    nm = name(i)
    if isdir:
        stack.append((struct.unpack_from('>I', fst, 12 * i + 8)[0], pre + nm + '/'))
    else:
        paths[pre + nm] = i
    i += 1

# 사용 중인 영역 (FST, DOL, 모든 파일) -> 빈 공간 목록
used = [(0, 0x2440 + 0x10000), (fst_off, fst_off + fst_sz)]
for p, e in paths.items():
    o, s = struct.unpack_from('>II', fst, 12 * e + 4); used.append((o << 2, (o << 2) + s))
dol_hdr = lread(dol_off, 0x100)
dol_size = max(struct.unpack_from('>I', dol_hdr, 4 * k)[0] + struct.unpack_from('>I', dol_hdr, 0x90 + 4 * k)[0] for k in range(18))
used.append((dol_off, dol_off + dol_size))
used.sort()
free = []; cur = 0
for a, b in used:
    if a > cur: free.append([cur, a])
    cur = max(cur, b)
free.append([cur, LSIZE])
free = [[(a + 31) & ~31, b] for a, b in free if b - ((a + 31) & ~31) >= 0x8000]


def alloc(n):
    for fr in sorted(free, key=lambda x: x[1] - x[0]):
        if fr[1] - fr[0] >= n:
            o = fr[0]; fr[0] = (o + n + 31) & ~31; return o
    raise SystemExit('no free space for %d bytes' % n)


moved = same = 0
for root, _, fs in os.walk(PATCH + '/files'):
    for fn in fs:
        full = os.path.join(root, fn).replace(chr(92), '/')
        rel = full[len(PATCH) + 7:]
        e = paths[rel]
        data = open(full, 'rb').read()
        o, s = struct.unpack_from('>II', fst, 12 * e + 4); o <<= 2
        if len(data) > s:
            o = alloc(len(data)); moved += 1
        else:
            same += 1
        lwrite(o, data)
        struct.pack_into('>II', fst, 12 * e + 4, o >> 2, len(data))
lwrite(fst_off, bytes(fst))
dol = open(PATCH + '/sys/main.dol', 'rb').read()
assert len(dol) <= dol_size + 0x100, 'dol grew'
lwrite(dol_off, dol)
f.close()
print('in place', same, 'moved', moved)
