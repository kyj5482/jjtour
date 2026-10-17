# JJ Tour · 2027 미국 서부 가족여행

3대 10명이 함께하는 2027년 5월 30일 – 6월 11일 미국 서부 여행 일정표입니다.

- 인트로 영상(어른용·아이용), 부모님 일정(트래킹 14코스), 동생네 가족 일정(주니어 레인저), 여행 경비 시뮬레이션, 준비물, 현지인 꿀팁, 여행 영어 롤플레이
- 페이지: `index.html` (GitHub Pages로 배포)

## 다시 빌드하기

```bash
python3 src/build.py
```

`src/template.html`, `src/days.js`, `src/meals.js`, `src/tips.js`, `src/geo.js`를 합쳐 `index.html`을 만듭니다.
인트로 영상은 `src/intro_music.py`·`src/intro_film.py`(어른용), `src/intro_music_kids.py`·`src/intro_film_kids.py`(아이용, 글꼴 `src/Jua-Regular.ttf`)로 만들었습니다 (numpy, Pillow, imageio-ffmpeg 필요).

사진 출처는 `credits.json`과 페이지 하단에 있습니다.
