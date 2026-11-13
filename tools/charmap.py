import json,glob,re,os,sys
sys.path.insert(0,os.path.dirname(__file__))
import fontmap
W=os.path.join(os.path.dirname(__file__),'..')
def needed():
    s=set()
    for f in glob.glob(W+'/text/out/*.json'):
        for v in json.load(open(f,encoding='utf-8')).values():
            for c in re.sub(r'\{[0-9a-f]+\}','',v):
                if '가'<=c<='힣': s.add(c)
                else:
                    try: c.encode('cp932')
                    except UnicodeEncodeError: s.add(c)
    return s
def build_map(fontdata):
    ks=set()
    for b1 in range(0xb0,0xc9):
        for b2 in range(0xa1,0xff):
            try: ks.add(bytes([b1,b2]).decode('euc-kr'))
            except: pass
    chars=sorted(ks|(needed()-{'・'})|{'·'})
    m=fontmap.cmaps(fontdata)
    codes=sorted(c for c in m if c>=0x889f)
    assert len(chars)<=len(codes),(len(chars),len(codes))
    return {ch:codes[i] for i,ch in enumerate(chars)}, m
def encode(s,cmap):
    out=bytearray()
    s=s.replace('…。','…').replace('。','.').replace('、',',')
    for c in s:
        if c=='・': c='·'
        if c=='~': c='～'
        if c in cmap: out+=cmap[c].to_bytes(2,'big')
        else: out+=c.encode('cp932')
    return bytes(out)
