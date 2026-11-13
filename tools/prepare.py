"""원본 준비: RVZ/ISO -> orig.iso (MD5 확인) -> ext/ 추출 -> 원문 표(text/units.json, text/dol_ja.json) 생성
사용: python tools/prepare.py <DolphinTool.exe> <원본 .rvz 또는 .iso> [wit.exe]"""
import sys, os, subprocess, hashlib, shutil
W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MD5 = '146599f594be2c56cace65c7616ca905'
dt, src = sys.argv[1], sys.argv[2]
wit = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else 'wit'
iso = os.path.join(W, 'orig.iso')
if src.lower().endswith('.iso'):
    shutil.copyfile(src, iso)
else:
    subprocess.check_call([dt, 'convert', '-i', src, '-o', iso, '-f', 'iso'])
h = hashlib.md5()
with open(iso, 'rb') as f:
    for b in iter(lambda: f.read(1 << 24), b''): h.update(b)
if h.hexdigest() != MD5: raise SystemExit('원본 MD5 불일치: ' + h.hexdigest())
subprocess.check_call([wit, 'extract', iso, os.path.join(W, 'ext'), '--psel', 'all', '-q', '-o'])
subprocess.check_call([sys.executable, os.path.join(W, 'tools', 'extract.py')], cwd=W)
subprocess.check_call([sys.executable, os.path.join(W, 'tools', 'dolstr.py')], cwd=W)
print('ok')
