import struct
def u32(d,o): return struct.unpack_from('>I',d,o)[0]
def parse(d):
    assert d[4:8]==b'MSG2'
    nspk,spkoff,nlab,laboff=struct.unpack_from('>4I',d,0x20)
    spk=[]
    for i in range(nspk):
        a,sz,off,b=struct.unpack_from('>4I',d,spkoff+i*16)
        spk.append(d[off:off+sz]); spkraw=(a,b)
    labs=[]
    for i in range(nlab):
        o=laboff+i*0x40
        name=d[o:o+0x20].split(b'\0')[0]
        typ,sz,off,sp,sp2=struct.unpack_from('>IIIHH',d,o+0x20)
        rest=d[o+0x30:o+0x40]
        blk=d[off:off+sz]
        if sz<4:
            labs.append(dict(name=name,type=typ,spk=sp,spk2=sp2,rest=rest,pages=[],raw=blk,hdr=b'')); continue
        n=u32(blk,0); offs=[u32(blk,4+4*k) for k in range(n)]
        pages=[]
        for k in range(n):
            e=offs[k+1] if k+1<n else len(blk)
            pages.append(blk[offs[k]:e])
        labs.append(dict(name=name,type=typ,spk=sp,spk2=sp2,rest=rest,pages=pages,hdr=blk[:4] ))
    return dict(spk=spk,labs=labs,head=d[:0x20])

def tokens(p):
    """yield ('t',str) for text runs, ('c',bytes) for control, ('n',) newline"""
    out=[];i=0;buf=b''
    def flush():
        nonlocal buf
        if buf: out.append(('t',buf.decode('cp932'))); buf=b''
    while i<len(p):
        c=p[i]
        if c==0xff:
            flush(); n=struct.unpack_from('>H',p,i+3)[0]; L=5+6*n
            out.append(('c',p[i:i+L])); i+=L
        elif c==0:
            flush(); out.append(('n',)); i+=1
        elif 0x81<=c<=0x9f or 0xe0<=c<=0xfc: buf+=p[i:i+2]; i+=2
        else: buf+=p[i:i+1]; i+=1
    flush(); return out

def build(m):
    """m from parse(); pages list of bytes per label. returns bytes"""
    head=bytearray(m['head']); spk=m['spk']; labs=m['labs']
    nspk=len(spk)
    out=bytearray(0x30)
    spkdesc=len(out); out+=b'\0'*(16*nspk)
    names=[]
    for s in spk:
        names.append(len(out)); out+=s
    laboff=len(out); out+=b'\0'*(0x40*len(labs))
    for i,l in enumerate(labs):
        pages=l['pages']; n=len(pages)
        blk=bytearray(struct.pack('>I',n)+b'\0'*(4*n)); 
        for k,p in enumerate(pages):
            struct.pack_into('>I',blk,4+4*k,len(blk)); blk+=p
        off=len(out); out+=blk
        o=laboff+i*0x40
        out[o:o+0x20]=l['name'].ljust(0x20,b'\0')
        struct.pack_into('>IIIHH',out,o+0x20,l['type'],len(blk),off,l['spk'],l['spk2'])
        out[o+0x30:o+0x40]=l['rest']
    for i,s in enumerate(spk):
        struct.pack_into('>4I',out,spkdesc+16*i,0,len(s),names[i],0)
    out[0:0x20]=head
    struct.pack_into('>4I',out,0x20,nspk,spkdesc if nspk else 0x30,len(labs),laboff)
    struct.pack_into('>I',out,0x0c,len(out))
    return bytes(out)
