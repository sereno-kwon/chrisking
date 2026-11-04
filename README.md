# Chris King Korea

chrisking.rubiworkshop.com 원페이지 정적 사이트 (GitHub Pages). quoc.rubiworkshop.com과 같은 구조와 디자인 체계입니다.

- `index.html` 한국어 원페이지 (CHRIS KING · RANGE · HEADSETS · HUBS · BOTTOM BRACKETS · COLORS · SERVICE · STORY · SHOWROOM)
- 디자인은 rubi.kr 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `index.src.html` 편집용 한국어 원본
- `i18n/` 번역 사전 (`ko.json` 원문 목록, `en.json` · `ja.json` 원문→번역)
- `tools/build.py` 한국어 페이지, 번역 페이지, sitemap.xml을 한 번에 생성
- `404.html` 하위 주소(/headsets, /hubs, /r45, /iso, /threadfit, /colors, /warranty, /dealers 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `brand`, `headset`, `hub`, `bb`)와 로고(`logo.svg`). chrisking.com 공식 사이트 이미지를 크기 조정해 넣었습니다. 이미지가 없는 자리는 회색 자리 표시로 나옵니다.
- `.github/image-manifest.txt` + `fetch-images.yml` 이미지 URL 목록을 받아 `images/`에 커밋하는 워크플로

## 처음 올릴 때
1. Settings → Pages → Source: Deploy from a branch, Branch: main / (root).
2. 도메인 DNS에 `chrisking` CNAME 레코드를 `sereno-kwon.github.io`로 추가하고, Pages 설정에서 Custom domain에 `chrisking.rubiworkshop.com`을 넣습니다 (CNAME 파일은 이미 들어 있음). 인증서가 발급되면 Enforce HTTPS를 켭니다.
3. 이미지: `.github/image-manifest.txt`에 `<URL> <저장 경로>`를 한 줄씩 적어 main에 푸시하면 Actions가 받아 커밋합니다. 직접 촬영한 사진은 같은 경로에 바로 올려도 됩니다. 필요한 경로와 비율은 매니페스트 주석에 있습니다.
4. 로고: `images/logo.svg`(chrisking.com 공식 로고). CSS에서 헤더는 검정, 다크모드는 흰색으로 칠해집니다.
5. 파비콘: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px), `images/logo-512.png`.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` 로 한국어 페이지를 만들고, `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 새로 생기거나 바뀐 한국어 문장을 `en.json` · `ja.json`에 같은 키로 추가합니다. HTML 태그는 원문과 똑같이 유지합니다.
4. 다시 `python3 tools/build.py` 를 실행하면 번역되지 않은 문장이 있을 때 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다 (`pip install beautifulsoup4`).

## 링크
- 헤더 SHOP, "루비워크샵에서 보기" 버튼: `https://rubiworkshop.com/chrisking`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 INSTAGRAM: `https://www.instagram.com/chriskingbuzz` (크리스킹 본사 계정)
