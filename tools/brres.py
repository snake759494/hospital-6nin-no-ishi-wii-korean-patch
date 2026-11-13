import struct
def tex0s(d):
    out=[];i=-1
    while True:
        i=d.find(b'TEX0',i+1)
        if i<0:break
        sz,ver,_,doff,noff=struct.unpack_from('>IIiII',d,i+4)
        if sz>len(d) or ver not in (1,2,3): continue
        w,h,fmt,n=struct.unpack_from('>HHII',d,i+0x1c)
        name=d[i+noff:i+noff+40].split(b'\0')[0].decode('latin1')
        out.append(dict(off=i,doff=i+doff,w=w,h=h,fmt=fmt,name=name))
    return out
