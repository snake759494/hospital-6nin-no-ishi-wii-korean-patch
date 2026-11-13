"""복호화된 Wii ISO 데이터 파티션의 H0~H3 해시와 TMD 콘텐츠 해시를 다시 계산한다.
사용: python tools/rehash.py dec.iso  -> 이후 wit copy --enc sign 으로 암호화·가짜 서명"""
import sys, struct, hashlib

f = open(sys.argv[1], 'r+b')


def rd(o, n): f.seek(o); return f.read(n)


n, tbl = struct.unpack('>II', rd(0x40000, 8)); tbl <<= 2
part = None
for i in range(n):
    po, pt = struct.unpack('>II', rd(tbl + 8 * i, 8))
    if pt == 0: part = po << 2
tmd_sz, tmd_off, _, _, h3_off, doff, dsize = struct.unpack('>7I', rd(part + 0x2a4, 28))
tmd_off = part + (tmd_off << 2); h3_off = part + (h3_off << 2); doff = part + (doff << 2); dsize <<= 2
nsec = dsize // 0x8000; ngrp = (nsec + 63) // 64
sha = lambda b: hashlib.sha1(b).digest()
h3 = bytearray(rd(h3_off, 0x18000))
for g in range(ngrp):
    base = doff + g * 64 * 0x8000
    cnt = min(64, nsec - g * 64)
    f.seek(base); raw = bytearray(f.read(cnt * 0x8000))
    if len(raw) < 64 * 0x8000: raw += bytes(64 * 0x8000 - len(raw))
    h0 = []
    for s in range(64):
        d = memoryview(raw)[s * 0x8000 + 0x400:(s + 1) * 0x8000]
        h0.append(b''.join(sha(d[k * 0x400:(k + 1) * 0x400]) for k in range(31)))
    h1 = [b''.join(sha(h0[sg * 8 + k]) for k in range(8)) for sg in range(8)]
    h2 = b''.join(sha(h1[sg]) for sg in range(8))
    for s in range(cnt):
        hb = bytearray(0x400)
        hb[0:0x26c] = h0[s]; hb[0x280:0x320] = h1[s // 8]; hb[0x340:0x3e0] = h2
        raw[s * 0x8000:s * 0x8000 + 0x400] = hb
    f.seek(base); f.write(raw[:cnt * 0x8000])
    h3[g * 20:(g + 1) * 20] = sha(h2)
f.seek(h3_off); f.write(h3)
tmd = bytearray(rd(tmd_off, tmd_sz))
tmd[0x1e4 + 0x10:0x1e4 + 0x24] = sha(bytes(h3))
f.seek(tmd_off); f.write(tmd)
f.close()
print('groups', ngrp)
