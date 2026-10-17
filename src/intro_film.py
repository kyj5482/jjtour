"""Render the JJ Tour intro film: photos with Ken Burns + Korean titles + stat cards, muxed with music.wav."""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

IMG = sys.argv[1]; OUT = sys.argv[2]; WAV = sys.argv[3]
PREVIEW = len(sys.argv) > 4 and sys.argv[4]  # comma list of seconds -> png stills
W, H, FPS = 1280, 720, 30
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
F = lambda size, idx: ImageFont.truetype(FONT, size, index=idx)
REG, MED, SEMI, BOLD, LIGHT, XB, HEAVY = 0, 2, 4, 6, 8, 14, 16

ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, x)))

# ---------------- timeline ----------------
# photo shot: ("ph", t0, t1, key, zoom from, zoom to, pan (dx,dy) in fraction, chapter label, title, sub)
# card: ("card", t0, t1, kind, data)
S = []
def ph(t0, d, key, title="", sub="", ch="", z=(1.04, 1.16), pan=(0.0, 0.0)):
    S.append(dict(k="ph", t0=t0, t1=t0 + d, key=key, title=title, sub=sub, ch=ch, z=z, pan=pan))
def card(t0, d, kind, **kw):
    S.append(dict(k="card", t0=t0, t1=t0 + d, kind=kind, **kw))

card(0, 6.4, "heart")
card(6.0, 5.6, "flight")
ph(11.0, 4.6, "tunnel_view", "미국 서부는 어떤 곳일까?", "부모님과 동생네에게 보내는 여행 예고편", z=(1.18, 1.04))
C1 = "CHAPTER 1 · 바다  THE COAST"
ph(15.0, 3.2, "laguna", "끝없는 태평양 해안선", "얼바인에서 차로 20분, 매일 아침이 바다", C1, pan=(0.04, 0))
ph(18.0, 3.2, "sb_mission", "250년 전 스페인 신부들이 세운 미션", "캘리포니아의 시작은 21개의 성당이었습니다", C1, pan=(-0.03, 0.02))
ph(21.0, 3.4, "solvang", "덴마크 이민자 마을까지", "서부는 세계 곳곳에서 온 사람들이 만든 땅", C1, pan=(0.03, -0.02))
card(24.2, 4.2, "stat", big="1.9배", line1="캘리포니아 한 주가", line2="한반도보다 약 1.9배 넓습니다", photo="sb_wharf")
C2 = "CHAPTER 2 · 산  THE SIERRA"
ph(28.2, 3.2, "mariposa", "수천 년을 산 거인들", "자이언트 세쿼이아, 지구에서 가장 큰 나무", C2, z=(1.14, 1.02), pan=(0, 0.04))
ph(31.2, 3.2, "glacier_point", "빙하가 깎은 화강암 계곡", "요세미티, 하프 돔", C2, pan=(-0.04, 0))
ph(34.2, 3.2, "yosemite_falls", "6월, 폭포가 가장 세찬 계절", "눈 녹은 물이 739m를 떨어집니다", C2, pan=(0, -0.03))
ph(37.2, 3.2, "tioga", "해발 3,031m 하늘길", "티오가 고개를 넘어 타호 호수로", C2, pan=(0.04, 0))
card(40.2, 4.2, "stat", big="1864", line1="링컨이 처음으로", line2="자연을 ‘국민의 것’으로 지정한 해", photo="yose_history")
C3 = "CHAPTER 3 · 협곡  THE CANYONS"
ph(44.2, 3.0, "zion", "붉은 절벽의 자이언", "동생네 가족의 3일 캐년 투어", C3, pan=(0.03, 0))
ph(47.0, 3.0, "bryce", "돌기둥 수천 개, 브라이스", "얼음과 바람이 깎은 ‘후두’", C3, z=(1.02, 1.14))
ph(50.0, 3.0, "antelope", "빛이 춤추는 협곡", "홍수가 바위를 깎아 만든 길", C3, pan=(0, 0.04))
ph(53.0, 3.2, "grand_canyon", "20억 년, 지구의 나이테", "그랜드캐년", C3, pan=(-0.05, 0))
card(56.2, 4.0, "stat", big="4 · 4", line1="4개 주, 4개 국립공원", line2="캘리포니아 · 네바다 · 유타 · 애리조나", photo="monument")
C4 = "CHAPTER 4 · 호수와 도시  LAKES & CITIES"
ph(60.2, 3.0, "emerald_bay", "미국에서 두 번째로 깊은 호수", "타호, 에메랄드 베이", C4, pan=(0.05, 0))
ph(63.0, 3.0, "napa", "1976년, 프랑스를 이긴 와인", "나파 밸리", C4, pan=(-0.03, 0.02))
ph(66.0, 3.0, "golden_gate", "골드러시가 만든 도시", "샌프란시스코, 금문교", C4, pan=(0.04, 0))
ph(69.0, 3.2, "stanford", "차고에서 시작된 실리콘밸리", "스탠퍼드, 팰로앨토", C4, pan=(0, -0.02))
CF = "OUR FAMILY"
ph(72.2, 3.0, "disneyland", "아이들에겐 꿈의 나라", "디즈니랜드 이틀", CF, pan=(0, 0.03))
ph(75.2, 3.0, "sjc_mission", "손주들의 졸업식", "Jaei & Jia, 축하해!", CF, pan=(0.03, 0))
ph(78.2, 3.4, "tunnel_view", "트래킹화 끈을 꽉 묶으세요", "3대가 함께 걷는 길, 13코스", CF, z=(1.02, 1.12))
ph(81.6, 3.0, "cable_car", "6월 9일, 샌프란시스코", "열 명이 모두 만나는 날", CF, pan=(-0.03, 0))
card(84.4, 7.6, "end", photo="golden_gate")
DUR = 92.0

# ---------------- assets ----------------
cache = {}
def photo(key):
    if key not in cache:
        im = Image.open(os.path.join(IMG, key + ".jpg")).convert("RGB")
        # cover-fit to 1.25x output so zooms stay sharp-ish
        s = max(W * 1.25 / im.width, H * 1.25 / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32)
        # warm, slightly faded cinematic grade
        a = a * np.array([1.04, 1.0, 0.94]) + np.array([4, 2, 0])
        a = 255 * (a / 255) ** 0.95
        cache[key] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return cache[key]

def kenburns(key, p, z, pan):
    im = photo(key)
    zz = z[0] + (z[1] - z[0]) * ease(p)
    bw, bh = im.width / zz / 1.25 * 1.25, im.height / zz / 1.25 * 1.25
    # visible window in source px: output aspect at current zoom
    s = max(W / im.width, H / im.height)
    vw, vh = W / s / zz * 1.25 / 1.25, H / s / zz * 1.25 / 1.25
    vw = min(vw, im.width); vh = min(vh, im.height)
    cx = im.width / 2 + pan[0] * im.width * (p - 0.5)
    cy = im.height / 2 + pan[1] * im.height * (p - 0.5)
    cx = min(max(cx, vw / 2), im.width - vw / 2); cy = min(max(cy, vh / 2), im.height - vh / 2)
    return im.resize((W, H), Image.BILINEAR, box=(cx - vw/2, cy - vh/2, cx + vw/2, cy + vh/2))

yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W/2) / (W/2)) ** 2 + ((yy - H/2) / (H/2)) ** 2)
VIG = np.clip(1 - 0.45 * np.clip(d - 0.55, 0, 1) ** 1.4, 0, 1)[..., None].astype(np.float32)
grad = np.clip((yy / H - 0.42) / 0.58, 0, 1) ** 1.3
GRAD = (1 - 0.72 * grad)[..., None].astype(np.float32)

text_cache = {}
def text_layer(lines, anchor="ls", shadow=True):
    """lines: list of (text, font, color(rgba), dy). Returns RGBA full-frame layer."""
    key = (tuple((t, id(f), c, dy) for t, f, c, dy in lines), anchor)
    if key in text_cache: return text_cache[key]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    for t, f, c, (x, y) in lines:
        dr.text((x, y), t, font=f, fill=c, anchor=anchor)
    if shadow:
        a = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * 0.65)))
        lay = Image.alpha_composite(sh, lay)
    text_cache[key] = lay
    return lay

def over(base, lay, alpha=1.0, dy=0):
    if alpha <= 0: return base
    if dy: lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay2.paste(lay, (0, int(dy))); lay = lay2
    if alpha < 1:
        a = lay.split()[3].point(lambda v: int(v * alpha)); lay = lay.copy(); lay.putalpha(a)
    return Image.alpha_composite(base, lay)

def appear(t, t0, t1, fin=0.6, fout=0.5):
    a = ease((t - t0) / fin) * (1 - ease((t - (t1 - fout)) / fout))
    return a, (1 - ease((t - t0) / (fin * 1.3))) * 22

f_ch = F(19, SEMI); f_title = F(60, XB); f_sub = F(28, MED)

def render_ph(s, t):
    p = (t - s["t0"]) / (s["t1"] - s["t0"])
    im = kenburns(s["key"], p, s["z"], s["pan"])
    a = np.asarray(im).astype(np.float32) * VIG * GRAD
    base = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    x = 84
    if s["ch"]:
        al, dy = appear(t, s["t0"] + 0.1, s["t1"], 0.5, 0.4)
        base = over(base, text_layer([(s["ch"], f_ch, (255, 226, 160, 255), (x, 70))]), al, 0)
    if s["title"]:
        al, dy = appear(t, s["t0"] + 0.35, s["t1"] + 0.2)
        base = over(base, text_layer([(s["title"], f_title, (255, 255, 255, 255), (x, H - 128))]), al, dy)
    if s["sub"]:
        al, dy = appear(t, s["t0"] + 0.75, s["t1"] + 0.2)
        base = over(base, text_layer([(s["sub"], f_sub, (230, 236, 238, 255), (x, H - 76))]), al, dy)
    return base

def dark(alpha=1.0, col=(6, 12, 18)):
    return Image.new("RGBA", (W, H), col + (255,))

def blurred_bg(key, t, s, darkness=0.42):
    p = (t - s["t0"]) / (s["t1"] - s["t0"])
    im = kenburns(key, p, (1.1, 1.18), (0.02, 0))
    k = ("blur", key)
    if k not in cache:
        cache[k] = 1
    im = im.filter(ImageFilter.GaussianBlur(6))
    a = np.asarray(im).astype(np.float32) * darkness
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")

f_heart = F(74, XB); f_heart2 = F(30, MED); f_small = F(22, MED)
f_big = F(168, HEAVY); f_l1 = F(34, MED); f_l2 = F(40, BOLD)
f_end = F(120, HEAVY); f_end2 = F(30, SEMI); f_end3 = F(24, REG)

# heartbeat pulse times (match music.py)
HB = []; tt = 0.4; hb = 0.86
while tt < 11: HB.append(tt); tt += hb; hb = max(0.62, hb - 0.012)

def render_card(s, t):
    kind = s["kind"]; t0, t1 = s["t0"], s["t1"]
    if kind == "heart":
        base = dark()
        pulse = max([math.exp(-max(0, t - h) * 6) * (t >= h) for h in HB] + [0])
        r = 150 + 40 * pulse
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
        g.ellipse((W/2 - r, H/2 - 40 - r, W/2 + r, H/2 - 40 + r), fill=(190, 60, 50, int(60 + 120 * pulse)))
        glow = glow.filter(ImageFilter.GaussianBlur(70))
        base = Image.alpha_composite(base, glow)
        al, dy = appear(t, 1.0, t1 + 1, 0.8)
        base = over(base, text_layer([("두근, 두근.", f_heart, (255, 255, 255, 255), (W/2, H/2 - 20))], "ms"), al, dy)
        al, dy = appear(t, 3.0, t1 + 1, 0.8)
        base = over(base, text_layer([("2027년 6월, 3대 열 명이 미국 서부에서 만납니다", f_heart2, (230, 230, 230, 255), (W/2, H/2 + 50))], "ms"), al, dy)
        return base
    if kind == "flight":
        base = dark(col=(8, 18, 30))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
        p = ease((t - t0 - 0.4) / 3.6)
        A = (200, 470); B = (1080, 470); top = 200
        pts = []
        for i in range(121):
            u = i / 120
            x = A[0] + (B[0] - A[0]) * u; y = A[1] - (A[1] - top) * 4 * u * (1 - u)
            pts.append((x, y))
        n = int(120 * p)
        for i in range(0, n, 2):
            dr.line([pts[i], pts[i + 1]], fill=(255, 210, 140, 230), width=4)
        # faint full path
        for i in range(0, 120, 4):
            dr.line([pts[i], pts[i + 1]], fill=(255, 255, 255, 40), width=2)
        for (x, y), lab, sub in [(A, "인천", "ICN"), (B, "로스앤젤레스", "LAX")]:
            dr.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255, 255))
            dr.text((x, y + 44), lab, font=F(34, BOLD), fill=(255, 255, 255, 255), anchor="ms")
            dr.text((x, y + 78), sub, font=f_small, fill=(160, 180, 195, 255), anchor="ms")
        px, py = pts[min(n, 120)]
        dr.ellipse((px - 12, py - 12, px + 12, py + 12), fill=(255, 210, 140, 255))
        dr.text((W/2, 330), "태평양", font=F(26, LIGHT), fill=(150, 175, 195, 255), anchor="ms")
        al, _ = appear(t, t0, t1, 0.5, 0.5)
        base = over(base, lay, al)
        al, dy = appear(t, t0 + 1.2, t1, 0.7, 0.5)
        base = over(base, text_layer([("11시간, 9,600km", F(52, XB), (255, 255, 255, 255), (W/2, 640))], "ms"), al, dy)
        return base
    if kind == "stat":
        base = blurred_bg(s["photo"], t, s)
        al, dy = appear(t, t0 + 0.2, t1, 0.7, 0.5)
        base = over(base, text_layer([(s["line1"], f_l1, (230, 235, 238, 255), (W/2, 230))], "ms"), al, dy)
        al, dy = appear(t, t0 + 0.5, t1, 0.7, 0.5)
        base = over(base, text_layer([(s["big"], f_big, (255, 214, 140, 255), (W/2, 430))], "ms"), al, dy * 1.5)
        al, dy = appear(t, t0 + 0.9, t1, 0.7, 0.5)
        base = over(base, text_layer([(s["line2"], f_l2, (255, 255, 255, 255), (W/2, 520))], "ms"), al, dy)
        return base
    if kind == "end":
        p = (t - t0) / (t1 - t0)
        im = kenburns(s["photo"], p, (1.16, 1.0), (0, 0))
        a = np.asarray(im).astype(np.float32) * VIG * (0.62 - 0.12 * ease(p))
        base = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
        al, dy = appear(t, t0 + 0.6, t1 + 2, 0.9)
        base = over(base, text_layer([("JJ TOUR", f_end, (255, 255, 255, 255), (W/2, 380))], "ms"), al, dy)
        al, dy = appear(t, t0 + 1.4, t1 + 2, 0.9)
        base = over(base, text_layer([("캘리포니아 · 네바다 · 유타 · 애리조나", f_end2, (255, 220, 160, 255), (W/2, 450))], "ms"), al, dy)
        al, dy = appear(t, t0 + 2.2, t1 + 2, 0.9)
        base = over(base, text_layer([("2027. 5. 30 – 6. 11   ·   얼바인에서 기다릴게요", f_end3, (225, 230, 232, 255), (W/2, 500))], "ms"), al, dy)
        fo = ease((t - (t1 - 2.0)) / 2.0)
        if fo > 0:
            base = Image.blend(base, dark(), fo)
        return base

def frame(t):
    act = [s for s in S if s["t0"] <= t < s["t1"] + 0.6]
    act.sort(key=lambda s: s["t0"])
    out = None
    for s in act:
        im = render_ph(s, t) if s["k"] == "ph" else render_card(s, t)
        if out is None: out = im
        else:
            a = ease((t - s["t0"]) / 0.6)
            out = Image.blend(out, im, a) if a < 1 else im
    if out is None: out = dark()
    # last shot of each overlap is the newcomer; ensure old one fades only after its end
    return out.convert("RGB")

# fix overlaps: each shot persists 0.6s past its end so the next one cross-fades over it
for i, s in enumerate(S):
    nxt = S[i + 1]["t0"] if i + 1 < len(S) else DUR
    s["t1"] = max(s["t1"], nxt)  # hold until next starts

if PREVIEW:
    for sec in PREVIEW.split(","):
        frame(float(sec)).save(f"{OUT}_{sec}.png")
    sys.exit()

ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", WAV, "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "160k", "-shortest", OUT]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
nf = int(DUR * FPS)
for i in range(nf):
    pr.stdin.write(frame(i / FPS).tobytes())
    if i % 300 == 0: print(f"{i}/{nf}", flush=True)
pr.stdin.close(); pr.wait()
frame(84.4 + 3.5).save(OUT.replace(".mp4", "_poster.jpg"), quality=88)
print("done", OUT)
