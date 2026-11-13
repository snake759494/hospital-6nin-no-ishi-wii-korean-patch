"""patch/ 결과를 원본 디스크 배치 그대로 덮어써서 한글판 ISO를 만든다 (xdelta를 작게 유지)
  1) wit로 orig.iso 를 복호화 (dec.iso)
  2) inplace.py: patch/ 파일을 제자리(커진 파일은 빈 공간)로 기록, FST·DOL 갱신
  3) rehash.py : H0~H3·TMD 해시 재계산
  4) wit로 가짜 서명·암호화 -> 출력 ISO
사용: python tools/makeiso.py <출력.iso> [wit.exe]"""
import sys, os, subprocess
W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
out = os.path.abspath(sys.argv[1]); wit = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else 'wit'
dec = os.path.join(W, 'dec.iso')
py = lambda s, *a: subprocess.check_call([sys.executable, os.path.join(W, 'tools', s), *a])
subprocess.check_call([wit, 'copy', os.path.join(W, 'orig.iso'), dec, '--enc', 'decrypt', '--psel', 'all', '-q', '-o'])
py('inplace.py', dec)
py('rehash.py', dec)
subprocess.check_call([wit, 'copy', dec, out, '--enc', 'sign', '--psel', 'all', '-q', '-o'])
os.remove(dec)
print('built', out)
