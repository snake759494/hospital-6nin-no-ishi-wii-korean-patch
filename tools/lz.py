def dec(d):
    assert d[0]==0x10
    n=d[1]|d[2]<<8|d[3]<<16; o=bytearray(); i=4
    while len(o)<n:
        f=d[i]; i+=1
        for b in range(8):
            if len(o)>=n: break
            if f&(0x80>>b):
                x=d[i]<<8|d[i+1]; i+=2; L=(x>>12)+3; disp=(x&0xfff)+1
                for _ in range(L): o.append(o[-disp])
            else: o.append(d[i]); i+=1
    return bytes(o)
def enc(d):
    n=len(d); out=bytearray([0x10,n&255,n>>8&255,n>>16&255]); i=0
    from collections import defaultdict
    tab=defaultdict(list)
    while i<n:
        fpos=len(out); out.append(0); flag=0
        for b in range(8):
            if i>=n: break
            best=0;bd=0
            if i+3<=n:
                for j in reversed(tab.get(d[i:i+3],[])[-64:]):
                    if i-j>4096: break
                    L=3
                    while L<18 and i+L<n and d[j+L]==d[i+L]: L+=1
                    if L>best: best=L;bd=i-j
                    if L==18: break
            if best>=3:
                flag|=0x80>>b; x=(best-3)<<12|(bd-1); out+=bytes([x>>8,x&255])
                for k in range(best):
                    if i+k+3<=n: tab[d[i+k:i+k+3]].append(i+k)
                i+=best
            else:
                out.append(d[i])
                if i+3<=n: tab[d[i:i+3]].append(i)
                i+=1
        out[fpos]=flag
    while len(out)%4: out.append(0)
    return bytes(out)
