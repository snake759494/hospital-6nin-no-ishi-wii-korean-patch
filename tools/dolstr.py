import re,struct,json
def sections(d):
    offs=struct.unpack_from('>18I',d,0); addr=struct.unpack_from('>18I',d,0x48); size=struct.unpack_from('>18I',d,0x90)
    return [(i,offs[i],addr[i],size[i]) for i in range(18) if size[i]]
def find(d):
    out=[]
    for i,o,a,s in sections(d):
        if i<7: continue  # text sections
        seg=d[o:o+s]
        for m in re.finditer(rb'(?<=\x00)(?:[\x81-\x9f\xe0-\xef][\x40-\xfc]|[\x20-\x7e]|[\xa1-\xdf])+(?=\x00)',seg):
            s_=m.group()
            if len(re.findall(rb'[\x81-\x9f\xe0-\xef][\x40-\xfc]',s_))<2: continue
            try: t=s_.decode('cp932')
            except: continue
            if not re.search('[぀-ヿ一-鿿]',t): continue
            st=o+m.start(); e=o+m.end()
            # slot: zeros after string up to next nonzero, keep 4-align conservative
            k=e
            while k<o+s and d[k]==0: k+=1
            out.append(dict(off=st,addr=a+m.start(),ja=t,len=len(s_),slot=k-st-1))
    return out
if __name__=='__main__':
    d=open('ext/DATA/sys/main.dol','rb').read()
    r=find(d); print(len(r), sum(len(x['ja']) for x in r))
    json.dump(r,open('text/dol_ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
