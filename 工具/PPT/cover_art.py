"""生成封面背景图：左边留暗给标题，右边是一堆散纸顺着光带飞进一排整齐的卡片（知识库）。"""
import math
import random
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2667, 1500
random.seed(7)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def hexc(h, a=255):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# ---------- 背景 ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = np.clip((xx / W) * 0.7 + (yy / H) * 0.3, 0, 1)[..., None]
c0 = np.array([10, 15, 28], np.float32)
c1 = np.array([12, 30, 36], np.float32)
bg = c0 * (1 - t) + c1 * t


def glow(cx, cy, r, color, k):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    g = np.exp(-d ** 2)[..., None] * k
    return g * np.array(color, np.float32)


bg += glow(W * 0.70, H * 0.48, 620, (245, 165, 36), 0.30)
bg += glow(W * 0.86, H * 0.18, 520, (34, 195, 166), 0.22)
bg += glow(W * 0.52, H * 0.80, 700, (255, 90, 78), 0.08)
# 右下角压暗，给头像
bg *= (1 - 0.45 * np.exp(-(((xx - W) / 700) ** 2 + ((yy - H) / 520) ** 2)))[..., None]
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')

# 淡网格
gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(gl)
step = int(W / 13.33 * 0.9)
for x in range(step, W, step):
    gd.line([(x, 0), (x, H)], fill=(40, 56, 84, 60), width=2)
for y in range(step, H, step):
    gd.line([(0, y), (W, y)], fill=(40, 56, 84, 60), width=2)
img = Image.alpha_composite(img, gl)


# ---------- 光带 ----------
def bezier(p0, p1, p2, p3, n=400):
    pts = []
    for i in range(n + 1):
        u = i / n
        a = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
        pts.append((a[0] * p0[0] + a[1] * p1[0] + a[2] * p2[0] + a[3] * p3[0],
                    a[0] * p0[1] + a[1] * p1[1] + a[2] * p2[1] + a[3] * p3[1]))
    return pts


def ribbon(layer, pts, w0, w1, c0, c1, a0, a1):
    d = ImageDraw.Draw(layer)
    n = len(pts)
    for i in range(n - 1):
        u = i / (n - 1)
        col = lerp(c0, c1, u) + (int(a0 + (a1 - a0) * u),)
        d.line([pts[i], pts[i + 1]], fill=col, width=max(1, int(w0 + (w1 - w0) * u)))


rib = Image.new('RGBA', (W, H), (0, 0, 0, 0))
TEAL, AMBER, CORAL, CREAM = (34, 195, 166), (245, 165, 36), (255, 110, 78), (255, 226, 170)
ribs = [
    ((1180, 1080), (1500, 1250), (1700, 700), (2050, 760), 8, 54, CORAL, AMBER, 70, 255),
    ((1250, 1180), (1600, 1300), (1800, 820), (2150, 860), 6, 40, TEAL, CREAM, 60, 240),
    ((1150, 980), (1450, 1100), (1650, 600), (1980, 640), 3, 22, CORAL, CREAM, 30, 190),
    ((1320, 1260), (1700, 1360), (1950, 980), (2300, 980), 5, 30, TEAL, TEAL, 50, 210),
]
for p0, p1, p2, p3, w0, w1, c0_, c1_, a0, a1 in ribs:
    ribbon(rib, bezier(p0, p1, p2, p3), w0, w1, c0_, c1_, a0, a1)
img = Image.alpha_composite(img, rib.filter(ImageFilter.GaussianBlur(22)))
img = Image.alpha_composite(img, rib.filter(ImageFilter.GaussianBlur(3)))

# ---------- 散纸（原始素材） ----------
def paper(layer, cx, cy, s, ang, col, alpha):
    pw, ph = s, s * 0.78
    pts = [(-pw / 2, -ph / 2), (pw / 2, -ph / 2), (pw / 2, ph / 2), (-pw / 2, ph / 2)]
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    ImageDraw.Draw(layer).polygon(pts, fill=col + (alpha,))


far = Image.new('RGBA', (W, H), (0, 0, 0, 0))
near = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for i in range(70):
    u = random.random()
    cx = 1020 + u * 760 + random.gauss(0, 60)
    cy = 1080 - u * 380 + random.gauss(0, 150)
    s = random.uniform(18, 62)
    col = random.choice([(255, 90, 78), (240, 120, 90), (230, 100, 80), (250, 150, 110)])
    layer = far if s < 34 else near
    paper(layer, cx, cy, s, random.uniform(0, math.pi), col, random.randint(120, 230))
img = Image.alpha_composite(img, far.filter(ImageFilter.GaussianBlur(4)))
img = Image.alpha_composite(img, near.filter(ImageFilter.GaussianBlur(1)))

# ---------- 底座 ----------
base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(base)
bx, by = 2060, 1010
bd.polygon([(bx - 560, by), (bx + 40, by - 190), (bx + 560, by - 40), (bx - 40, by + 160)], fill=(18, 70, 72, 255))
bd.polygon([(bx - 560, by), (bx - 40, by + 160), (bx - 40, by + 200), (bx - 560, by + 40)], fill=(12, 44, 48, 255))
bd.polygon([(bx - 40, by + 160), (bx + 560, by - 40), (bx + 560, by), (bx - 40, by + 200)], fill=(10, 36, 40, 255))
edge = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(edge).line([(bx - 560, by), (bx + 40, by - 190), (bx + 560, by - 40), (bx - 40, by + 160), (bx - 560, by)],
                          fill=(60, 230, 200, 200), width=5)
img = Image.alpha_composite(img, base)
img = Image.alpha_composite(img, edge.filter(ImageFilter.GaussianBlur(10)))
img = Image.alpha_composite(img, edge.filter(ImageFilter.GaussianBlur(1)))


# ---------- 卡片（整理好的知识库） ----------
def card(cx, cy, w, h, tone, icon):
    """立在底座上的一张卡：正面 + 侧边厚度，向右上斜。"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    sk = w * 0.32
    fl, fr = (cx - w / 2, cy), (cx + w / 2, cy - sk)
    tl, tr = (fl[0], fl[1] - h), (fr[0], fr[1] - h)
    th = w * 0.09
    d.polygon([fr, (fr[0] + th, fr[1] + th * 0.25), (tr[0] + th, tr[1] + th * 0.25), tr], fill=lerp(tone, (0, 0, 0), 0.45) + (255,))
    # 正面渐变：逐条横线
    for i in range(int(h)):
        u = i / h
        col = lerp(lerp(tone, (255, 255, 255), 0.35), tone, u) + (255,)
        d.line([(fl[0], fl[1] - h + i), (fr[0], fr[1] - h + i)], fill=col, width=2)
    d.line([tl, tr], fill=(255, 255, 255, 200), width=3)
    d.line([tl, fl], fill=(255, 255, 255, 120), width=2)
    # 图标：内框 + 山 + 太阳
    m = 0.16

    def P(u, v):
        x = fl[0] + (fr[0] - fl[0]) * u
        y = fl[1] + (fr[1] - fl[1]) * u - h * v
        return (x, y)
    ink = lerp(tone, (0, 0, 0), 0.38) + (255,)
    d.line([P(m, 1 - m), P(1 - m, 1 - m), P(1 - m, m), P(m, m), P(m, 1 - m)], fill=ink, width=4)
    if icon == 'mt':
        d.polygon([P(m + .02, m + .02), P(.42, .52), P(.55, .38), P(.68, .6), P(1 - m - .02, m + .02)], fill=ink)
        sx, sy = P(.66, .74)
        d.ellipse([sx - w * .07, sy - w * .07, sx + w * .07, sy + w * .07], fill=(245, 165, 36, 255))
    elif icon == 'lines':
        for k, v in enumerate((.68, .55, .42, .29)):
            d.line([P(m + .08, v), P(1 - m - .08 - (k % 2) * .18, v)], fill=ink, width=6)
    else:
        d.line([P(.5, m + .08), P(.5, .62)], fill=ink, width=6)
        for k in (-1, 1):
            d.line([P(.5, .62), P(.5 + .14 * k, .74)], fill=ink, width=6)
        sx, sy = P(.5, .45)
        d.ellipse([sx - w * .09, sy - w * .06, sx + w * .09, sy + w * .06], outline=ink, width=5)
    return lay


# 阴影
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse([1600, 860, 2500, 1080], fill=(0, 0, 0, 150))
img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(40)))

rows = [
    # 后排（远、暗、小）
    [(1880, 840, 150, 230, (60, 150, 140), 'lines'), (2030, 795, 150, 250, (70, 165, 150), 'mt'),
     (2180, 750, 150, 220, (60, 150, 140), 'tree'), (2330, 705, 150, 240, (70, 165, 150), 'lines')],
    # 中排
    [(1760, 925, 175, 290, (120, 200, 180), 'mt'), (1930, 875, 175, 330, (150, 215, 190), 'lines'),
     (2100, 825, 175, 300, (130, 205, 185), 'tree'), (2270, 775, 175, 280, (150, 215, 190), 'mt')],
    # 前排（近、亮、大）
    [(1640, 1015, 200, 330, (210, 225, 200), 'lines'), (1835, 960, 210, 400, (238, 226, 196), 'mt'),
     (2035, 905, 200, 350, (215, 230, 205), 'tree')],
]
for r in rows:
    for cx, cy, w, h, tone, icon in r:
        img = Image.alpha_composite(img, card(cx, cy, w, h, tone, icon))

# 一张“高”卡（金色，代表核心认知）
img = Image.alpha_composite(img, card(2250, 880, 230, 520, (240, 200, 120), 'mt'))

# 前景几片散纸 + 光点
fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for i in range(14):
    paper(fg, random.uniform(1250, 1700), random.uniform(450, 900), random.uniform(40, 90),
          random.uniform(0, math.pi), (255, 100, 80), random.randint(150, 230))
img = Image.alpha_composite(img, fg.filter(ImageFilter.GaussianBlur(2.5)))
sp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sp)
for i in range(120):
    x, y = random.uniform(1300, 2600), random.uniform(250, 1150)
    r = random.uniform(1.5, 4.5)
    sd.ellipse([x - r, y - r, x + r, y + r], fill=random.choice([(255, 220, 150), (140, 255, 230)]) + (random.randint(80, 220),))
img = Image.alpha_composite(img, sp.filter(ImageFilter.GaussianBlur(1.2)))

# 左侧渐暗，保证标题清楚
a = np.clip((xx - W * 0.30) / (W * 0.28), 0, 1)
a = (a * a * (3 - 2 * a))[..., None]
arr = np.asarray(img.convert('RGB')).astype(np.float32)
arr = arr * (0.62 + 0.38 * a)  # 左边压暗
DY = 120
arr = np.concatenate([arr[DY:], np.repeat(arr[-1:], DY, axis=0)], axis=0)
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(sys.argv[1], quality=92)
