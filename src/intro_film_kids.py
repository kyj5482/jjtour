"""Render the kids' adventure intro: sticker-style Jua titles over photos, missions, Junior Ranger badges, English bubble.
usage: intro_film_kids.py IMG_DIR OUT.mp4 MUSIC.wav JUA.ttf [comma-separated preview seconds]"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

IMG, OUT, WAV, JUA = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else ""
W, H, FPS = 1280, 720, 30
SD = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
J = lambda size: ImageFont.truetype(JUA, size)
G = lambda size, idx=6: ImageFont.truetype(SD, size, index=idx)
ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, x)))
def pop(x):  # overshoot ease for bouncy entrances
    x = min(1, max(0, x)); return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2

ORANGE, NAVY, YELLOW, SKY = (242, 140, 40), (24, 42, 72), (255, 214, 90), (90, 170, 230)

S = []
def ph(t0, d, key, title, sub="", ch="", z=(1.05, 1.16), pan=(0.0, 0.0)):
    S.append(dict(k="ph", t0=t0, t1=t0 + d, key=key, title=title, sub=sub, ch=ch, z=z, pan=pan))
def card(t0, d, kind, **kw):
    S.append(dict(k="card", t0=t0, t1=t0 + d, kind=kind, **kw))

card(0, 4.6, "start")
card(4.2, 5.4, "flight")
M1, M2, M3 = "미션 1 · 사막과 협곡", "미션 2 · 꿈의 나라와 바다", "미션 3 · 언덕 위 바다 도시"
ph(9.4, 3.1, "bellagio", "사막 한가운데서 분수가 춤춰요!", "라스베이거스", M1, pan=(0.04, 0))
ph(12.5, 3.0, "zion", "빨간 절벽 탐험!", "자이언 국립공원", M1, pan=(0.03, 0))
ph(15.5, 3.0, "bryce", "돌 요정 “후두”가 수천 개!", "브라이스 캐니언", M1, z=(1.02, 1.14))
ph(18.5, 3.0, "antelope", "빛이 춤추는 비밀 협곡", "앤텔로프 캐니언", M1, pan=(0, 0.04))
ph(21.5, 3.0, "horseshoe", "말발굽처럼 휜 강", "호스슈 벤드", M1, pan=(0.03, 0.02))
ph(24.5, 3.0, "monument", "서부영화 속 바위 언덕", "모뉴먼트 밸리", M1, pan=(-0.04, 0))
ph(27.5, 3.0, "grand_canyon", "지구에서 제일 큰 협곡!", "그랜드캐년", M1, pan=(-0.05, 0))
card(30.5, 4.0, "stat", big="18억 살", line1="그랜드캐년 맨 아래 바위는", line2="공룡보다 훨씬, 훨씬 오래됐어요", photo="grand_canyon")
ph(34.5, 3.0, "route66", "영화 “카”의 그 길!", "루트 66", M2, pan=(0.03, 0))
ph(37.5, 3.0, "griffith", "할리우드 사인을 찾아라", "그리피스 천문대", M2, pan=(0, -0.02))
ph(40.5, 2.8, "sd_zoo", "판다를 만날까?", "샌디에이고 동물원", M2, pan=(0.02, 0))
ph(43.3, 3.0, "seaworld", "범고래를 만날까?", "씨월드 · 둘 중 골라 봐요!", M2, pan=(-0.03, 0))
ph(46.3, 3.0, "disneyland", "꿈의 나라에서 이틀!", "디즈니랜드", M2, z=(1.02, 1.12))
ph(49.3, 3.0, "dca", "라이트닝 맥퀸 마을", "카 랜드", M2, pan=(0.03, 0))
ph(52.3, 3.0, "cable_car", "언덕을 오르는 케이블카", "샌프란시스코", M3, pan=(-0.03, 0))
ph(55.3, 3.0, "alcatraz", "탈출 불가! 감옥 섬", "알카트라즈", M3, pan=(0.03, 0))
card(58.3, 6.2, "badges")
card(64.3, 5.2, "english")
card(69.3, 8.7, "end", photo="golden_gate")
DUR = 78.0
for i, s in enumerate(S):
    nxt = S[i + 1]["t0"] if i + 1 < len(S) else DUR
    s["t1"] = max(s["t1"], nxt)

cache = {}
def photo(key):
    if key not in cache:
        im = Image.open(os.path.join(IMG, key + ".jpg")).convert("RGB")
        s = max(W * 1.25 / im.width, H * 1.25 / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32)
        a = 255 * ((a / 255) ** 0.92) * np.array([1.05, 1.02, 0.97])     # brighter, sunnier grade for kids
        cache[key] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return cache[key]

def kenburns(key, p, z, pan):
    im = photo(key); zz = z[0] + (z[1] - z[0]) * ease(p)
    s = max(W / im.width, H / im.height)
    vw, vh = min(W / s / zz, im.width), min(H / s / zz, im.height)
    cx = min(max(im.width / 2 + pan[0] * im.width * (p - 0.5), vw / 2), im.width - vw / 2)
    cy = min(max(im.height / 2 + pan[1] * im.height * (p - 0.5), vh / 2), im.height - vh / 2)
    return im.resize((W, H), Image.BILINEAR, box=(cx - vw/2, cy - vh/2, cx + vw/2, cy + vh/2))

yy, xx = np.mgrid[0:H, 0:W]
GRAD = (1 - 0.6 * np.clip((yy / H - 0.5) / 0.5, 0, 1) ** 1.4)[..., None].astype(np.float32)

tcache = {}
def sticker(text, font, fill=(255, 255, 255), stroke=NAVY, sw=6):
    """Text drawn with a thick outline and a soft drop shadow, cropped to its box."""
    key = (text, id(font), fill, stroke, sw)
    if key in tcache: return tcache[key]
    l, t, r, b = font.getbbox(text, stroke_width=sw)
    im = Image.new("RGBA", (r - l + 24, b - t + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.text((12 - l, 12 - t), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .45)))
    out = Image.new("RGBA", (im.width + 6, im.height + 6), (0, 0, 0, 0)); out.alpha_composite(sh, (6, 6)); out.alpha_composite(im, (0, 0))
    tcache[key] = out; return out

def pill(text, font, bg=ORANGE, fg=(255, 255, 255)):
    key = ("pill", text, id(font), bg)
    if key in tcache: return tcache[key]
    l, t, r, b = font.getbbox(text)
    im = Image.new("RGBA", (r - l + 40, b - t + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=bg + (255,))
    d.text((20 - l, 11 - t), text, font=font, fill=fg); tcache[key] = im; return im

def place(base, img, x, y, alpha=1.0, scale=1.0, anchor="lt"):
    if alpha <= 0 or scale <= 0.02: return
    if scale != 1.0: img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if alpha < 1: img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    if anchor == "mm": x, y = x - img.width // 2, y - img.height // 2
    elif anchor == "mb": x, y = x - img.width // 2, y - img.height
    elif anchor == "lb": y = y - img.height
    base.alpha_composite(img, (int(x), int(y)))

def appear(t, t0, t1, fin=0.45, fout=0.35):
    return ease((t - t0) / fin) * (1 - ease((t - (t1 - fout)) / fout)), pop((t - t0) / (fin * 1.4))

f_title, f_sub, f_pill = J(66), G(30, 6), G(24, 6)

def render_ph(s, t):
    p = (t - s["t0"]) / (s["t1"] - s["t0"])
    a = np.asarray(kenburns(s["key"], p, s["z"], s["pan"])).astype(np.float32) * GRAD
    base = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    al, sc = appear(t, s["t0"] + 0.1, s["t1"])
    place(base, pill(s["ch"], f_pill), 60, 46, al)
    al, sc = appear(t, s["t0"] + 0.3, s["t1"] + 0.1)
    place(base, sticker(s["title"], f_title), 60, H - 98, al, sc, "lb")
    al, _ = appear(t, s["t0"] + 0.6, s["t1"] + 0.1)
    place(base, sticker(s["sub"], f_sub, (255, 240, 200), NAVY, 4), 66, H - 46, al, 1, "lb")
    return base

def bg(col_top, col_bot):
    g = np.linspace(0, 1, H)[:, None, None]
    a = np.array(col_top)[None, None, :] * (1 - g) + np.array(col_bot)[None, None, :] * g
    return Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8)).convert("RGBA")
BG_SUN = bg((255, 196, 92), (242, 120, 52))
BG_SKY = bg((120, 196, 245), (52, 120, 200))
rng = np.random.default_rng(3)
DOTS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 16), tuple(int(c) for c in rng.choice([[255,255,255],[255,230,120],[120,210,255],[255,150,190]]))) for _ in range(40)]

def confetti(base, t, strength=1.0):
    d = ImageDraw.Draw(base)
    for i, (x, y, r, c) in enumerate(DOTS):
        yy_ = (y + t * (40 + i % 7 * 12)) % (H + 40) - 20
        xx_ = x + 18 * math.sin(t * 2 + i)
        d.ellipse((xx_ - r, yy_ - r, xx_ + r, yy_ + r), fill=c + (int(200 * strength),))

def badge(key, size, gold=True):
    k = ("badge", key, size, gold)
    if k in tcache: return tcache[k]
    im = photo(key); s = min(im.width, im.height)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2)).resize((size, size), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255); im.putalpha(m)
    out = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    d.ellipse((0, 0, size + 23, size + 23), fill=(250, 196, 60, 255) if gold else (220, 220, 220, 255))
    d.ellipse((6, 6, size + 17, size + 17), fill=(170, 112, 20, 255))
    out.alpha_composite(im, (12, 12)); tcache[k] = out; return out

def render_card(s, t):
    kind, t0, t1 = s["kind"], s["t0"], s["t1"]
    if kind == "start":
        base = BG_SUN.copy(); confetti(base, t, min(1, t / 2))
        al, sc = appear(t, 0.3, t1 + 1, 0.5)
        place(base, sticker("탐험대, 출동 준비!", J(104), (255, 255, 255), NAVY, 9), W // 2, H // 2 - 30, al, sc, "mm")
        al, sc = appear(t, 1.6, t1 + 1, 0.5)
        place(base, sticker("13일 동안 사막·협곡·꿈의 나라·바다를 탐험해요", G(32), (255, 255, 255), (170, 70, 20), 4), W // 2, H // 2 + 70, al, sc, "mm")
        return base
    if kind == "flight":
        base = BG_SKY.copy(); d = ImageDraw.Draw(base)
        P = [(150, 470, "인천"), (760, 470, "LA"), (1110, 330, "라스베이거스")]
        def arc(a, b, h, u):
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - h * 4 * u * (1 - u)
        p = ease((t - t0 - 0.3) / 4.0)
        legs = [(P[0], P[1], 220, 0.0, 0.7), (P[1], P[2], 110, 0.7, 1.0)]
        plane = None
        for a, b, h, u0, u1 in legs:
            for i in range(0, 60, 2):
                u = i / 60
                if p >= u0 + (u1 - u0) * u:
                    d.line([arc(a, b, h, u), arc(a, b, h, u + 1/60)], fill=(255, 255, 255, 255), width=6)
            if u0 <= p <= u1: plane = arc(a, b, h, (p - u0) / (u1 - u0))
        if p >= 1: plane = P[2][:2]
        for x, y, n in P:
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(255, 255, 255, 255), outline=NAVY, width=4)
            lab = sticker(n, J(44), (255, 255, 255), NAVY, 5); place(base, lab, x - lab.width // 2, y + 24)
        if plane:
            x, y = plane; d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=YELLOW + (255,), outline=NAVY, width=4)
        al, sc = appear(t, t0 + 1.2, t1, 0.5)
        place(base, sticker("비행기를 두 번 타요!", J(70), (255, 255, 255), NAVY, 7), W // 2, 130, al, sc, "mm")
        return base
    if kind == "stat":
        p = (t - t0) / (t1 - t0)
        im = kenburns(s["photo"], p, (1.1, 1.2), (0.02, 0)).filter(ImageFilter.GaussianBlur(5))
        base = Image.fromarray((np.asarray(im).astype(np.float32) * 0.5).astype(np.uint8)).convert("RGBA")
        al, sc = appear(t, t0 + 0.2, t1); place(base, sticker(s["line1"], G(36), (255, 255, 255), NAVY, 4), W // 2, 210, al, 1, "mm")
        al, sc = appear(t, t0 + 0.5, t1); place(base, sticker(s["big"], J(190), YELLOW, NAVY, 12), W // 2, 370, al, sc, "mm")
        al, sc = appear(t, t0 + 1.0, t1); place(base, sticker(s["line2"], J(56), (255, 255, 255), NAVY, 6), W // 2, 530, al, sc, "mm")
        return base
    if kind == "badges":
        base = BG_SUN.copy(); confetti(base, t, 0.5)
        al, sc = appear(t, t0 + 0.2, t1)
        place(base, sticker("주니어 레인저 배지 4개를 모아라!", J(72), (255, 255, 255), NAVY, 7), W // 2, 120, al, sc, "mm")
        names = [("zion", "자이언"), ("bryce", "브라이스"), ("grand_canyon", "그랜드캐년"), ("alcatraz", "알카트라즈")]
        for i, (k, n) in enumerate(names):
            x = 220 + i * 280; ti = t0 + 0.9 + i * 0.55
            al, sc = appear(t, ti, t1, 0.4)
            place(base, badge(k, 190), x, 380, al, sc, "mm")
            place(base, sticker(n, J(40), (255, 255, 255), NAVY, 5), x, 510, al, 1, "mm")
        al, sc = appear(t, t0 + 3.4, t1)
        place(base, sticker("책자를 다 풀고 오른손 들고 선서하면 배지를 받아요", G(30), (255, 255, 255), (170, 70, 20), 4), W // 2, 610, al, 1, "mm")
        return base
    if kind == "english":
        base = BG_SKY.copy(); d = ImageDraw.Draw(base)
        al, sc = appear(t, t0 + 0.2, t1, 0.5)
        bw, bh = 940, 230
        bub = Image.new("RGBA", (bw + 60, bh + 70), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle((0, 0, bw, bh), radius=60, fill=(255, 255, 255, 255), outline=NAVY, width=8)
        bd.polygon([(170, bh - 4), (250, bh - 4), (150, bh + 64)], fill=(255, 255, 255, 255), outline=NAVY)
        bd.line([(170, bh - 4), (150, bh + 64), (250, bh - 4)], fill=NAVY, width=8)
        fe = J(70); txt = "Hi! I'm a Junior Ranger"; txt2 = "from Korea."
        for i, line in enumerate((txt, txt2)):
            l_, t_, r_, b_ = fe.getbbox(line); bd.text(((bw - (r_ - l_)) // 2 - l_, 38 + i * 82 - t_), line, font=fe, fill=NAVY)
        place(base, bub, W // 2, 330, al, sc, "mm")
        al, sc = appear(t, t0 + 1.4, t1)
        place(base, sticker("레인저에게 영어로 말 걸기 도전!", J(60), YELLOW, NAVY, 7), W // 2, 600, al, sc, "mm")
        return base
    if kind == "end":
        p = (t - t0) / (t1 - t0)
        a = np.asarray(kenburns(s["photo"], p, (1.16, 1.0), (0, 0))).astype(np.float32) * (0.62 - 0.1 * ease(p))
        base = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA"); confetti(base, t, 0.6)
        al, sc = appear(t, t0 + 0.5, t1 + 2, 0.6)
        place(base, sticker("탐험대, 준비됐나요?", J(110), (255, 255, 255), ORANGE, 10), W // 2, 320, al, sc, "mm")
        al, sc = appear(t, t0 + 1.5, t1 + 2, 0.6)
        place(base, sticker("2027. 5. 30 ~ 6. 11", J(54), YELLOW, NAVY, 6), W // 2, 440, al, sc, "mm")
        al, sc = appear(t, t0 + 2.3, t1 + 2, 0.6)
        place(base, sticker("사촌들과 샌프란시스코에서 만나요!", G(34), (255, 255, 255), NAVY, 4), W // 2, 515, al, 1, "mm")
        fo = ease((t - (t1 - 1.6)) / 1.6)
        if fo > 0: base = Image.blend(base, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fo)
        return base

def frame(t):
    act = sorted([s for s in S if s["t0"] <= t < s["t1"] + 0.5], key=lambda s: s["t0"])
    out = None
    for s in act:
        im = render_ph(s, t) if s["k"] == "ph" else render_card(s, t)
        out = im if out is None else (Image.blend(out, im, ease((t - s["t0"]) / 0.5)) if t - s["t0"] < 0.5 else im)
    return (out or Image.new("RGBA", (W, H), (0, 0, 0, 255))).convert("RGB")

if PREVIEW:
    for sec in PREVIEW.split(","): frame(float(sec)).save(f"{OUT}_{sec}.png")
    sys.exit()
ff = imageio_ffmpeg.get_ffmpeg_exe()
pr = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", WAV, "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    pr.stdin.write(frame(i / FPS).tobytes())
pr.stdin.close(); pr.wait()
frame(1.8).save(OUT.replace(".mp4", "_poster.jpg"), quality=88)
print("done", OUT)
