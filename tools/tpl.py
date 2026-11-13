import struct, numpy as np
from PIL import Image
BW={0:(8,8,4),1:(8,4,8),2:(8,4,8),3:(4,4,16),4:(4,4,16),5:(4,4,16),6:(4,4,32),8:(8,8,4),9:(8,4,8),10:(4,4,16),14:(8,8,4)}
def tpx_read(d):
    n=struct.unpack_from('>I',d,4)[0]; out=[]
    for i in range(n):
        o=0x20+i*0x20
        idx,off,size=struct.unpack_from('>III',d,o); name=d[o+12:o+32].split(b'\0')[0].decode('latin1')
        out.append(dict(name=name,off=off,size=size))
    return out
def tpl_images(t):
    n=struct.unpack_from('>I',t,4)[0]; to=struct.unpack_from('>I',t,8)[0]; res=[]
    for i in range(n):
        io,po=struct.unpack_from('>II',t,to+8*i)
        h,w,fmt,doff=struct.unpack_from('>HHII',t,io)
        pal=None
        if po:
            pn,_,pf,pd=struct.unpack_from('>HBxII',t,po); pal=(pf,t[pd:pd+pn*(4 if pf==255 else 2)])
        res.append(dict(w=w,h=h,fmt=fmt,doff=doff,hdr=io,pal=pal))
    return res
def c565(v): return ((v>>11&31)*255//31,(v>>5&63)*255//63,(v&31)*255//31,255)
def c5a3(v):
    if v&0x8000: return ((v>>10&31)*255//31,(v>>5&31)*255//31,(v&31)*255//31,255)
    return ((v>>8&15)*17,(v>>4&15)*17,(v&15)*17,(v>>12&7)*255//7)
def palcol(pal,i):
    pf,pd=pal; v=struct.unpack_from('>H',pd,2*i)[0]
    if pf==0: a=v>>8; l=v&255; return (l,l,l,a)
    if pf==1: return c565(v)
    if pf==255:
        n=len(pd)//4; return (pd[2*n+2*i+1],v>>8,v&255,pd[2*n+2*i])
    return c5a3(v)
def decode(t,im):
    w,h,fmt=im['w'],im['h'],im['fmt']; bw,bh,bpp=BW[fmt]; d=t[im['doff']:]
    W=(w+bw-1)//bw*bw; H=(h+bh-1)//bh*bh
    out=np.zeros((H,W,4),np.uint8); i=0
    if fmt==14:
        for by in range(0,H,8):
            for bx in range(0,W,8):
                for sb in range(4):
                    c0,c1=struct.unpack_from('>HH',d,i); bits=struct.unpack_from('>I',d,i+4)[0]; i+=8
                    a=c565(c0);b=c565(c1)
                    if c0>c1: cs=[a,b,tuple((2*a[k]+b[k])//3 for k in range(3))+(255,),tuple((a[k]+2*b[k])//3 for k in range(3))+(255,)]
                    else: cs=[a,b,tuple((a[k]+b[k])//2 for k in range(3))+(255,),(0,0,0,0)]
                    ox=bx+(sb&1)*4; oy=by+(sb>>1)*4
                    for p in range(16):
                        out[oy+p//4,ox+p%4]=cs[bits>>(30-2*p)&3]
        return Image.fromarray(out[:h,:w],'RGBA')
    for by in range(0,H,bh):
        for bx in range(0,W,bw):
            if fmt==6:
                ar=d[i:i+32]; gb=d[i+32:i+64]; i+=64
                for p in range(16):
                    out[by+p//4,bx+p%4]=(ar[2*p+1],gb[2*p],gb[2*p+1],ar[2*p])
                continue
            for y in range(bh):
                for x in range(bw):
                    if fmt in(0,8,14):
                        b=d[i//2]; v=(b>>4) if i%2==0 else b&15; i+=1
                        if fmt==0: c=(v*17,)*3+(255,)
                        else: c=palcol(im['pal'],v)
                    elif fmt in(1,2,9):
                        b=d[i//2*0+i] if False else None
                        b=d[i]; i+=1
                        if fmt==1: c=(b,b,b,255)
                        elif fmt==2: c=((b&15)*17,)*3+((b>>4)*17,)
                        else: c=palcol(im['pal'],b)
                    else:
                        v=struct.unpack_from('>H',d,i)[0]; i+=2
                        if fmt==3: c=(v&255,)*3+(v>>8,)
                        elif fmt==4: c=c565(v)
                        elif fmt==5: c=c5a3(v)
                        else: c=palcol(im['pal'],v&0x3fff)
                    out[by+y,bx+x]=c
    return Image.fromarray(out[:h,:w],'RGBA')
