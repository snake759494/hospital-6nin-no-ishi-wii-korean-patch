import struct
def read(d):
    o=0;out=[]
    while o<len(d):
        name=d[o:o+252].split(b'\0')[0].decode(); sz=struct.unpack_from('<I',d,o+252)[0]
        out.append([name,d[o+256:o+256+sz]]); o+=256+sz; o=(o+63)&~63
    return out
def write(ents):
    b=bytearray()
    for name,data in ents:
        h=name.encode().ljust(252,b'\0')+struct.pack('<I',len(data))
        b+=h+data
        while len(b)%64: b+=b'\0'
    return bytes(b)
