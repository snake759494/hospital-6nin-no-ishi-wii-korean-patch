"""글꼴 파일 찾기: 저장소 최상위 -> fonts/ -> 상위 폴더 순서로 찾는다 (글꼴은 저장소에 넣지 않음)"""
import os
W = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def fp(name):
    for d in (W, os.path.join(W, 'fonts'), os.path.dirname(W)):
        p = os.path.join(d, name)
        if os.path.exists(p): return p
    raise SystemExit('글꼴 없음: ' + name + ' (docs/FONT_CREDITS.md 참고)')
