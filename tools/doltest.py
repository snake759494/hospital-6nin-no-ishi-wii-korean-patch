import sys,os,json,glob
sys.path.insert(0,os.path.dirname(__file__))
import charmap,mkfont
BAD={0,1,2,3,4,5,42,43,44,45,46,1920,1921,3473,3474,3475}|set(range(3635,3650))
W=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
def patch_dol(dol, sel=None, skip=()):
    font=open(W+'/ext/DATA/files/font/font.brfnt','rb').read()
    CM,_=charmap.build_map(font)
    dj=json.load(open(W+'/text/dol_ja.json',encoding='utf-8'))
    dk={};lim={}
    for f in glob.glob(W+'/text/out/dol*.json'): dk.update(json.load(open(f,encoding='utf-8')))
    lim=json.load(open(W+'/text/dol_limits.json',encoding='utf-8'))
    dol=bytearray(dol); n=0
    for i,x in enumerate(dj):
        key='d%d'%i
        if key not in dk or key not in lim: continue
        if 0x450000<=x['off']<0x46d000: continue
        if sel and not(sel[0]<=i<sel[1]): continue
        if i in skip or i in BAD: continue
        b=charmap.encode(dk[key],CM)
        if len(b)>lim[key]: continue
        o=x['off']; dol[o:o+x['len']+1]=b'\0'*(x['len']+1); dol[o:o+len(b)]=b; n+=1
    # 추가 추출분(여러 줄 문자열 등)
    nk={}
    for f in glob.glob(W+'/text/out/doln*.json'): nk.update(json.load(open(f,encoding='utf-8')))
    import hashlib
    for x in json.load(open(W+'/text/dol_new_meta.json',encoding='utf-8')):
        if sel or x['id'] not in nk: continue
        b=charmap.encode(nk[x['id']],CM)
        if len(b)>x['maxbytes']: continue
        o=x['off']; assert hashlib.sha1(bytes(dol[o:o+x['len']])).hexdigest()==x['sha1'],x['id']
        dol[o:o+x['len']+1]=b'\0'*(x['len']+1); dol[o:o+len(b)]=b; n+=1
    # 수동 추가분 (원문 뒤 0 패딩까지 사용)
    for x in json.load(open(W+'/text/dol_extra_ko.json',encoding='utf-8')):
        if sel: break
        o=int(x['off'],16); L=x['len']; assert hashlib.sha1(bytes(dol[o:o+L])).hexdigest()==x['sha1'],x
        room=L
        while o+room+1<len(dol) and dol[o+room+1]==0 and room<L+16: room+=1
        b=charmap.encode(x['ko'],CM)
        if len(b)>room: print('EXTRA too long',x['ko'],len(b),room); continue
        dol[o:o+room]=bytes(room); dol[o:o+len(b)]=b; n+=1
    return bytes(dol),n
if __name__=='__main__':
    lo,hi=int(sys.argv[1]),int(sys.argv[2])
    d,n=patch_dol(open(W+'/ext/DATA/sys/main.dol','rb').read(),(lo,hi))
    open(W+'/wfs/sys/main.dol','wb').write(d); print(n)
