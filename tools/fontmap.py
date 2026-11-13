import struct
def cmaps(d):
    o=struct.unpack_from('>I',d,0x28)[0]-8  # FINF pCMAP
    res={}
    while o:
        lo,hi,meth,_,nxt=struct.unpack_from('>HHHHI',d,o+8)
        b=o+20
        if meth==0:
            idx0=struct.unpack_from('>H',d,b)[0]
            for c in range(lo,hi+1): res[c]=idx0+c-lo
        elif meth==1:
            for c in range(lo,hi+1):
                g=struct.unpack_from('>H',d,b+2*(c-lo))[0]
                if g!=0xffff: res[c]=g
        else:
            n=struct.unpack_from('>H',d,b)[0]
            for k in range(n):
                c,g=struct.unpack_from('>HH',d,b+2+4*k); res[c]=g
        o=nxt-8 if nxt else 0
    return res
def cwdh(d):
    o=struct.unpack_from('>I',d,0x24)[0]-8
    s,e,nxt=struct.unpack_from('>HHI',d,o+8)
    return o+16,s,e
