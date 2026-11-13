"""CMPR(DXT1) 인코더 - 불투명 이미지용 (RGB numpy h,w,3)"""
import numpy as np, struct
def c565(c): return (int(c[0])>>3)<<11|(int(c[1])>>2)<<5|(int(c[2])>>3)
def d565(v): return np.array([(v>>11&31)*255//31,(v>>5&63)*255//63,(v&31)*255//31])
def block(px):
    lum=px@np.array([.3,.59,.11]); a=px[lum.argmax()]; b=px[lum.argmin()]
    c0,c1=c565(a),c565(b)
    if c0==c1:
        if c0==0xffff: c1=c0-1
        else: c0=c0+1 if c0<0xffff else c0
    if c0<c1: c0,c1=c1,c0
    p0,p1=d565(c0),d565(c1); pal=np.array([p0,p1,(2*p0+p1)//3,(p0+2*p1)//3])
    idx=((px[:,None,:].astype(int)-pal[None])**2).sum(-1).argmin(-1)
    bits=0
    for i in idx: bits=bits<<2|int(i)
    return struct.pack('>HHI',c0,c1,bits)
def encode(img):
    h,w,_=img.shape; out=bytearray()
    for by in range(0,h,8):
        for bx in range(0,w,8):
            for sy in (0,4):
                for sx in (0,4):
                    out+=block(img[by+sy:by+sy+4,bx+sx:bx+sx+4].reshape(16,3))
    return bytes(out)
