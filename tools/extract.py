from common import *
import json,collections
units={};order=[];spk={};bad=[]
for sid,d in sources():
    try:
        m=msg_of(d)
        if not m: continue
        P=bm2.parse(m)
    except Exception as e: bad.append(sid); continue
    for s in P['spk']:
        s=s.split(b'\0')[0].decode('cp932')
        spk.setdefault(s,sid)
    for l in P['labs']:
        for p in l['pages']:
            pre,body,suf=split_page(p)
            k=tok2str(body)
            if not re.search('[぀-ヿ一-鿿！-～]',k): continue
            if k not in units: units[k]=sid+'#'+l['name'].decode(); order.append(k)
json.dump([{'id':i,'src':units[k],'ja':k} for i,k in enumerate(order)],open('text/units.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
json.dump(spk,open('text/speakers_ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(order),sum(len(k) for k in order),len(spk),len(bad),bad)
