import sys,glob,os,re
sys.path.insert(0,os.path.dirname(__file__))
import bm2,flw,pak,lz
ROOT=os.path.join(os.path.dirname(__file__),'..','ext','DATA','files').replace(chr(92),'/')
def is_lang_ok(path): return '/eng/' not in path and '.svn' not in path
def sources():
    """yield (srcid, kind, bytes) kind: 'bm2' or 'bf'; srcid 'path' or 'pak::name'"""
    for f in sorted(glob.glob(ROOT+'/**/*',recursive=True)):
        f=f.replace(chr(92),'/')
        if not is_lang_ok(f) or os.path.isdir(f): continue
        rel=f[len(ROOT)+1:]
        if f.endswith('.pak'):
            for n,x in pak.read(open(f,'rb').read()):
                if n and is_lang_ok('/'+n) and n.endswith(('.bf','.bm2')) and x[:1]==b'\x10':
                    yield rel+'::'+n, lz.dec(x)
        elif f.endswith(('.bf','.bm2')):
            yield rel, open(f,'rb').read()
def msg_of(d):
    if d[8:12]==b'FLW0': return flw.get_msg(d)
    if d[4:8]==b'MSG2': return d
def split_page(p):
    """returns (prefix_bytes, body_tokens, suffix_bytes)"""
    t=bm2.tokens(p); a=0; b=len(t)
    while a<b and t[a][0]=='c': a+=1
    while b>a and t[b-1][0]!='t': b-=1
    return t[:a],t[a:b],t[b:]
def tok2str(ts):
    s=''
    for t in ts:
        if t[0]=='t': s+=t[1]
        elif t[0]=='n': s+='\n'
        else: s+='{'+t[1].hex()+'}'
    return s
