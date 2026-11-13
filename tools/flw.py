import struct
def sections(d):
    assert d[8:12]==b'FLW0'
    n=struct.unpack_from('>I',d,0x10)[0]
    return [list(struct.unpack_from('>4I',d,0x20+16*i)) for i in range(n)]
def get_msg(d):
    for t,es,c,o in sections(d):
        if t==3 and c: return d[o:o+es*c]
    return None
def set_msg(d,m):
    d=bytearray(d); secs=sections(d)
    for i,(t,es,c,o) in enumerate(secs):
        if t==3:
            old=es*c; delta=len(m)-old
            d[o:o+old]=m
            struct.pack_into('>I',d,0x20+16*i+8,len(m))
            for j,(t2,es2,c2,o2) in enumerate(secs):
                if o2>o or (o2==o and j>i): struct.pack_into('>I',d,0x20+16*j+12,o2+delta)
            struct.pack_into('>I',d,4,len(d))
            return bytes(d)
    raise Exception('no msg')
