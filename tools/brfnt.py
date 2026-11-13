import struct
from PIL import Image
def load(d):
    o=0x30; t=d[o:]
    cw,ch,base,mw,ssz,ns,fmt,cols,rows,sw,sh,doff=struct.unpack_from('>BBBBIHHHHHHI',d,o+8)
    return dict(cw=cw,ch=ch,base=base,mw=mw,ssz=ssz,ns=ns,fmt=fmt,cols=cols,rows=rows,sw=sw,sh=sh,doff=doff)
def sheet_img(d,info,k):
    sw,sh=info['sw'],info['sh']; raw=d[info['doff']+k*info['ssz']:][:info['ssz']]
    im=Image.new('L',(sw,sh)); px=im.load(); i=0
    for by in range(0,sh,8):
        for bx in range(0,sw,8):
            for y in range(8):
                for x in range(0,8,2):
                    b=raw[i]; i+=1
                    px[bx+x,by+y]=(b>>4)*17; px[bx+x+1,by+y]=(b&15)*17
    return im
def sheet_bytes(im):
    sw,sh=im.size; px=im.load(); out=bytearray()
    for by in range(0,sh,8):
        for bx in range(0,sw,8):
            for y in range(8):
                for x in range(0,8,2):
                    out.append((px[bx+x,by+y]//17)<<4|(px[bx+x+1,by+y]//17))
    return bytes(out)
