"""11/11 封面图：竖屏取景框（REC）对准查验台两边的老板和客人，台上的包在前景虚掉。
意思：二奢 Vlog 最难拍的不是货，是人。左边压暗放标题，右下角压暗给头像。"""
import math
import random
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2667, 1500
random.seed(11)
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = np.clip((xx / W) * 0.7 + (yy / H) * 0.3, 0, 1)[..., None]
bg = np.array([10, 15, 28], np.float32) * (1 - t) + np.array([14, 28, 36], np.float32) * t


def glow(cx, cy, r, color, k):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    return np.exp(-d ** 2)[..., None] * k * np.array(color, np.float32)


bg += glow(W * 0.66, H * 0.36, 560, (245, 165, 36), 0.26)   # 头顶一盏暖灯
bg += glow(W * 0.88, H * 0.22, 480, (34, 195, 166), 0.18)
bg += glow(W * 0.60, H * 0.70, 650, (255, 90, 78), 0.06)
bg *= (1 - 0.5 * np.exp(-(((xx - W) / 720) ** 2 + ((yy - H) / 520) ** 2)))[..., None]
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')

gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(gl)
step = int(W / 13.33 * 0.9)
for x in range(step, W, step):
    gd.line([(x, 0), (x, H)], fill=(40, 56, 84, 55), width=2)
for y in range(step, H, step):
    gd.line([(0, y), (W, y)], fill=(40, 56, 84, 55), width=2)
img = Image.alpha_composite(img, gl)


def comp(layer, blur=0):
    global img
    img = Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(blur)) if blur else layer)


def L():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def grad_fill(mask, top, bot, y0, y1):
    """用竖向渐变填充 mask（L 模式）。"""
    g = np.zeros((H, W, 4), np.uint8)
    u = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)[..., None]
    col = np.array(top[:3], np.float32) * (1 - u) + np.array(bot[:3], np.float32) * u
    g[..., :3] = col.astype(np.uint8)
    ta = top[3] if len(top) > 3 else 255
    ba = bot[3] if len(bot) > 3 else 255
    g[..., 3] = (np.asarray(mask).astype(np.float32) * (ta * (1 - u[..., 0]) + ba * u[..., 0]) / 255).astype(np.uint8)
    return Image.fromarray(g, 'RGBA')


# ---------- 寄卖柜（背景，虚） ----------
cab = L()
cd = ImageDraw.Draw(cab)
for i in range(4):
    x0 = 1480 + i * 280
    cd.rounded_rectangle([x0, 150, x0 + 250, 760], 10, outline=(70, 110, 120, 120), width=4)
    for j in range(3):
        y0 = 190 + j * 190
        cd.line([(x0 + 15, y0 + 150), (x0 + 235, y0 + 150)], fill=(90, 140, 140, 110), width=5)
        # 架上的小包剪影
        if (i + j) % 2 == 0:
            bx = x0 + 70 + (j * 23) % 60
            cd.rounded_rectangle([bx, y0 + 85, bx + 90, y0 + 148], 10, fill=(150, 120, 80, 90))
            cd.arc([bx + 18, y0 + 50, bx + 72, y0 + 110], 180, 360, fill=(150, 120, 80, 90), width=6)
comp(cab, 6)


# ---------- 两个人（老板 + 客人） ----------
def bust(cx, base_y, scale, face_dir, top, bot, rim):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    hr = 72 * scale
    hx, hy = cx + face_dir * 10 * scale, base_y - 330 * scale
    d.ellipse([hx - hr, hy - hr * 1.15, hx + hr, hy + hr * 1.1], fill=255)          # 头
    d.rectangle([cx - 30 * scale, hy + 50 * scale, cx + 30 * scale, hy + 120 * scale], fill=255)  # 脖子
    sw = 190 * scale
    pts = []
    for k in range(41):  # 肩膀弧线
        a = math.pi * k / 40
        pts.append((cx - sw * math.cos(a), base_y - 200 * scale - 70 * scale * math.sin(a) ** 0.6))
    pts += [(cx + sw * 1.05, base_y), (cx - sw * 1.05, base_y)]
    d.polygon(pts, fill=255)
    # 头发
    hair = Image.new('L', (W, H), 0)
    ImageDraw.Draw(hair).ellipse([hx - hr * 1.05, hy - hr * 1.25, hx + hr * 1.05, hy + hr * 0.2], fill=255)
    body = grad_fill(m, top, bot, hy - hr, base_y)
    rim_l = L()
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    rim_l = grad_fill(edge, rim + (230,), rim + (60,), hy - hr, base_y)
    return body, rim_l, grad_fill(hair, (20, 24, 34), (34, 40, 52), hy - hr * 1.3, hy)


base = 905
for cx, fd, top, bot, rim in [(1630, 1, (70, 160, 150), (20, 60, 66), (120, 255, 225)),
                              (2130, -1, (230, 140, 110), (90, 44, 44), (255, 170, 120))]:
    b, r, hair = bust(cx, base, 1.0, fd, top + (255,), bot + (255,), rim)
    comp(b)
    comp(hair)
    comp(r, 6)
    comp(r, 1)

# 对话气泡
bub = L()
bdr = ImageDraw.Draw(bub)
for (x, y, col) in [(1700, 330, (34, 195, 166)), (1960, 420, (255, 110, 78))]:
    bdr.rounded_rectangle([x, y, x + 150, y + 78], 36, fill=col + (235,))
    for k in range(3):
        cx = x + 40 + k * 35
        bdr.ellipse([cx - 9, y + 30, cx + 9, y + 48], fill=(255, 255, 255, 240))
comp(bub, 1)

# ---------- 查验台 ----------
tb = L()
td = ImageDraw.Draw(tb)
td.polygon([(1300, 900), (2560, 860), (2640, 1000), (1240, 1050)], fill=(24, 40, 46, 255))
td.polygon([(1240, 1050), (2640, 1000), (2640, 1050), (1240, 1100)], fill=(14, 24, 30, 255))
comp(tb)
ed = L()
ImageDraw.Draw(ed).line([(1300, 900), (2560, 860), (2640, 1000), (1240, 1050), (1300, 900)], fill=(245, 190, 90, 200), width=4)
comp(ed, 8)
comp(ed, 1)


# ---------- 台上的货（前景，虚一点：货不是主角） ----------
def handbag(layer, x, y, w, col):
    d = ImageDraw.Draw(layer)
    h = w * 0.7
    d.arc([x + w * 0.22, y - h * 0.55, x + w * 0.78, y + h * 0.35], 180, 360, fill=lerp(col, (0, 0, 0), 0.3) + (255,), width=int(w * 0.06))
    d.polygon([(x + w * 0.06, y), (x + w * 0.94, y), (x + w, y + h), (x, y + h)], fill=col + (255,))
    d.polygon([(x + w * 0.06, y), (x + w * 0.94, y), (x + w * 0.9, y + h * 0.42), (x + w * 0.1, y + h * 0.42)], fill=lerp(col, (255, 255, 255), 0.18) + (255,))
    d.rounded_rectangle([x + w * 0.44, y + h * 0.34, x + w * 0.56, y + h * 0.5], 6, fill=(245, 190, 90, 255))  # 五金
    d.line([(x + w * 0.06, y), (x + w * 0.94, y)], fill=(255, 240, 210, 200), width=3)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


goods = L()
handbag(goods, 1760, 840, 230, (196, 150, 98))
gd2 = ImageDraw.Draw(goods)
gd2.ellipse([2040, 900, 2130, 990], outline=(220, 230, 235, 230), width=10)   # 放大镜
gd2.line([(2120, 980), (2190, 1030)], fill=(150, 110, 70, 255), width=16)
gd2.rounded_rectangle([1430, 960, 1640, 1010], 20, fill=(200, 190, 175, 220))  # 防尘袋
comp(goods, 3.5)

# ---------- 竖屏取景框 + REC ----------
vf = L()
vd = ImageDraw.Draw(vf)
fx0, fy0, fx1, fy1 = 1400, 170, 2340, 1080   # 接近 9:16 的竖框（偏上，避开右下）
c = 70
for (x, y, sx, sy) in [(fx0, fy0, 1, 1), (fx1, fy0, -1, 1), (fx0, fy1, 1, -1), (fx1, fy1, -1, -1)]:
    vd.line([(x, y), (x + sx * c, y)], fill=(255, 255, 255, 235), width=7)
    vd.line([(x, y), (x, y + sy * c)], fill=(255, 255, 255, 235), width=7)
vd.ellipse([fx0 + 40, fy0 + 40, fx0 + 72, fy0 + 72], fill=(255, 70, 60, 255))
f = ImageFont.truetype(FONT, 40)
vd.text((fx0 + 88, fy0 + 34), 'REC', font=f, fill=(255, 255, 255, 235))
vd.text((fx1 - 230, fy0 + 34), '00:03:12', font=f, fill=(255, 255, 255, 200))
cx, cy = 2130 + 10, 905 - 330   # 对焦框套在客人脸上
vd.rectangle([cx - 105, cy - 105, cx + 105, cy + 105], outline=(245, 190, 90, 220), width=4)
comp(vf, 0)

# ---------- 手持云台相机（右上，对准取景框） ----------
cam = L()
cmd = ImageDraw.Draw(cam)
gx, gy = 2440, 420
cmd.rounded_rectangle([gx - 22, gy + 70, gx + 22, gy + 360], 18, fill=(40, 48, 62, 255))      # 手柄
cmd.line([(gx, gy + 70), (gx, gy + 20), (gx - 30, gy + 20)], fill=(60, 70, 86, 255), width=16)  # 云台臂
cmd.rounded_rectangle([gx - 150, gy - 40, gx - 10, gy + 50], 14, fill=(52, 60, 76, 255))       # 机身
cmd.ellipse([gx - 205, gy - 35, gx - 125, gy + 45], fill=(20, 24, 32, 255), outline=(120, 255, 225, 230), width=6)  # 镜头
cmd.ellipse([gx - 30, gy - 25, gx - 16, gy - 11], fill=(255, 70, 60, 255))
comp(cam, 1)

# 光点
sp = L()
sd = ImageDraw.Draw(sp)
for i in range(110):
    x, y = random.uniform(1300, 2620), random.uniform(120, 1050)
    r = random.uniform(1.5, 4)
    sd.ellipse([x - r, y - r, x + r, y + r], fill=random.choice([(255, 220, 150), (140, 255, 230)]) + (random.randint(60, 190),))
comp(sp, 1.2)

# 左侧压暗，整体上移一点
a = np.clip((xx - W * 0.32) / (W * 0.25), 0, 1)
a = (a * a * (3 - 2 * a))[..., None]
arr = np.asarray(img.convert('RGB')).astype(np.float32) * (0.62 + 0.38 * a)
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(sys.argv[1], quality=92)
