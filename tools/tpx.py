import struct
def parse(d):
    ns,so,nt=struct.unpack_from('>III',d,4)
    tex=[]
    for i in range(nt):
        o=0x20+i*0x20; idx,off,size=struct.unpack_from('>III',d,o)
        tex.append(dict(off=off,size=size,name=d[o+12:o+32].split(b'\0')[0].decode('latin1')))
    spr=[]
    for i in range(ns):
        o=so+i*0x60; t=struct.unpack_from('>H',d,o+6)[0] if False else struct.unpack_from('>I',d,o+4)[0]
        x,y,w,h=struct.unpack_from('>HHHH',d,o+8)
        nm=d[o+0x48:o+0x60].split(b'\0')[0]
        try: nm=nm.decode('cp932')
        except: nm=repr(nm)
        spr.append(dict(i=i,o=o,tex=t,x=x,y=y,w=w,h=h,name=nm))
    return tex,spr
