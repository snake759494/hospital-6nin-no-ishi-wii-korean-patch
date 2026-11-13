import sys,os,struct,json;sys.path.insert(0,os.path.dirname(__file__))
import brfnt,fontmap,charmap
from PIL import Image,ImageDraw,ImageFont
W=os.path.join(os.path.dirname(__file__),'..')
def make(orig, ttf=None, size=17, ss=4, yoff=2):
    d=bytearray(orig); info=brfnt.load(d)
    cm,m=charmap.build_map(d)
    base,_,_=fontmap.cwdh(d)
    if ttf is None:
        from fontpath import fp; ttf=fp('NanumSquareNeo-bRg.ttf')
    f=ImageFont.truetype(ttf,size*ss)
    sheets={}
    def sheet(k):
        if k not in sheets: sheets[k]=brfnt.sheet_img(d,info,k)
        return sheets[k]
    cw,ch=info['cw'],info['ch']
    for c,code in cm.items():
        g=m[code]; k=g//65; r=g%65; x0=(r%13)*(cw+1); y0=(r//13)*(ch+1)
        im=Image.new('L',(cw*ss,ch*ss),0); dr=ImageDraw.Draw(im)
        bb=f.getbbox(c)
        w=bb[2]-bb[0]
        if '가'<=c<='힣':
            x=(cw*ss-w)//2-bb[0]; y=yoff*ss-f.getbbox('한')[1]
        else:
            x=(cw*ss-w)//2-bb[0]; y=yoff*ss-f.getbbox('한')[1]
        dr.text((x,y),c,font=f,fill=255)
        if '가'<=c<='힣':
            bx=im.getbbox()
            if bx:
                g_=im.crop((bx[0],0,bx[2],ch*ss)); nw=min(cw*ss,int(g_.width*1.12))
                im=Image.new('L',(cw*ss,ch*ss),0); im.paste(g_.resize((nw,ch*ss),Image.LANCZOS),((cw*ss-nw)//2,0))
        im=im.resize((cw,ch),Image.LANCZOS).point(lambda v:min(255,int(v*1.15)))
        im=im.point(lambda v:(v//17)*17)
        sheet(k).paste(im,(x0,y0))
        d[base+3*g:base+3*g+3]=bytes([0,cw,cw]) if '가'<=c<='힣' else bytes([0,cw-2,cw-2])
    for k,im in sheets.items():
        o=info['doff']+k*info['ssz']; d[o:o+info['ssz']]=brfnt.sheet_bytes(im)
    return bytes(d),cm
