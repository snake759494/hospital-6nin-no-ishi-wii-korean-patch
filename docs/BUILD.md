# 재빌드

## 준비물

- Python 3.11 이상
- `numpy`, `Pillow`, `opencv-python` (`pip install numpy pillow opencv-python`)
- Dolphin에 들어 있는 `DolphinTool.exe`
- [Wiimms ISO Tools](https://wit.wiimm.de/)의 `wit.exe`
- 원본 일본판 SPTJEB 디스크(RVZ 또는 ISO)
  - ISO로 바꿨을 때 MD5가 `146599f594be2c56cace65c7616ca905`이어야 합니다.
- 글꼴(`docs/FONT_CREDITS.md`). 저장소 최상위나 `fonts/` 폴더에 둡니다.
  - `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`
  - `SeoulHangangEB.ttf`
  - `Galmuri7.ttf`, `Galmuri9.ttf`, `Galmuri11.ttf`, `Galmuri11-Bold.ttf`, `Galmuri11-Condensed.ttf`
- (배포 파일을 만들 때) xdelta3

## 순서

```powershell
python tools/prepare.py 'C:\Dolphin\DolphinTool.exe' '.\Hospital. 6-nin no Ishi (Japan).rvz' 'C:\wit\wit.exe'
```

이 명령이 하는 일은 다음과 같습니다.
1. 원본을 `orig.iso`로 변환하고 MD5를 확인합니다.
2. 디스크 파일을 `ext/`에 풉니다.
3. `tools/extract.py`로 대사 원문 표(`text/units.json`)를, `tools/dolstr.py`로 실행파일 문자열 표(`text/dol_ja.json`)를 만듭니다.

```powershell
python tools/build.py
python tools/makeiso.py '.\Hospital. 6-nin no Ishi (Korean).iso' 'C:\wit\wit.exe'
```

- `build.py`: 바뀐 파일만 `patch/` 아래에 원본 경로대로 출력합니다.
  - 대사·메시지, 글꼴, 실행파일 문자열을 바꾸고 이어서 그림 글자(`tools/texjobs.py`)를 처리합니다.
  - 마지막 줄에 `files 2296 dol 2691 {'pages': 52799, ...}`가 나오면 성공입니다.
  - 화면 폭을 넘는 쪽은 `text/overflow.json`에 기록합니다.
- `makeiso.py`: 원본 ISO를 복호화하고, `patch/`의 파일을 원래 자리에 덮어써 한글판 ISO를 만듭니다. 자세한 방식은 `docs/TECHNICAL.md`를 보세요.

## 배포 파일 만들기

```powershell
xdelta3 -e -0 -S none -A -s orig.iso '.\Hospital. 6-nin no Ishi (Korean).iso' Hospital_6nin_no_Ishi_Wii_KO_v1.0.xdelta
```

결과 ISO의 SHA-256이 README 표의 값과 같으면 배포판과 같은 결과입니다.

## 생성·무시되는 파일

다음 파일은 `.gitignore`에 들어 있어 커밋되지 않습니다.
- `orig.iso`, `ext/`, `patch/`
- 원문 표(`text/units.json`, `text/dol_ja.json` 등)
- 결과 ISO와 xdelta
- 글꼴
