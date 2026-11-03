"""11/4 课件，深色版第二版：照讲师给的参考截图排版，右下角留头像位，不加页码。"""
import json
import sys
from pptx.util import Inches, Emu
from pptx.dml.color import RGBColor
import deckkit_v2 as K
from deckkit_v2 import *

K.PARTS.update({2: '00', 3: '01', 4: '01', 5: '01', 6: '01', 7: '01', 8: '02', 9: '02', 10: '02',
                11: '03', 12: '03', 13: '03', 14: '04', 15: '04', 16: '04', 17: '04', 18: '04', 19: '05', 20: '06'})
K.PCOL.update({'00': GREEN, '01': RED, '02': GOLD, '03': GREEN, '04': RED, '05': GOLD, '06': GREEN})

NOTES = json.load(open('notes1104.json', encoding='utf-8'))
d = Deck('tpl/t0902a.pptx')
T = d.text
TITLES = []
Y = 1.85          # 正文起点
BOT = 5.42        # 右边内容最低到这里（再往下是头像位）


def S(image=None):
    title, notes = NOTES[len(TITLES)]
    s = d.slide('title' if image else 'light', notes=notes, image=image)
    TITLES.append((title, notes))
    return s


def border(shp, color, w=15875):
    shp.line.color.rgb = RGBColor.from_string(color)
    shp.line.width = Emu(w)
    return shp


def line(s, x1, y1, x2, y2, color='3A4A68', w=12700):
    c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = RGBColor.from_string(color)
    c.line.width = Emu(w)
    return c


def card(s, x, y, w, h, accent, fill=CARD):
    return border(d.box(s, x, y, w, h, fill, rounded=True, adj=0.05), accent)


def bcard(s, x, y, w, h, accent, title, lines=(), label=None, tsize=20, bsize=15.5, fill=CARD, tcolor=None):
    card(s, x, y, w, h, accent, fill)
    yy = y + 0.2
    if label:
        T(s, x + 0.25, yy, w - 0.4, 0.3, label, 13, color=MUTED, bold=True, wrap=False)
        yy += 0.32
    T(s, x + 0.25, yy, w - 0.4, 0.45, title, tsize, color=tcolor or accent, bold=True, ln=1.3, wrap=False)
    yy += tsize * 1.3 / 72 + 0.1
    if lines:
        T(s, x + 0.25, yy, w - 0.45, y + h - yy - 0.05, list(lines), bsize, ln=1.5)


def grid(s, y, items, cols, h, gap=0.2, accents=None, **kw):
    w = (CW - gap * (cols - 1)) / cols
    for i, it in enumerate(items):
        label, title, lines = it
        x = X0 + (i % cols) * (w + gap)
        yy = y + (i // cols) * (h + gap)
        bcard(s, x, yy, w, h, (accents or [RED] * 99)[i], title, lines, label=label, **kw)
    rows = (len(items) + cols - 1) // cols
    return y + rows * h + (rows - 1) * gap


def rowcard(s, x, y, w, h, accent, label, desc, key=None, lsize=18, dsize=15, lw=2.4):
    d.box(s, x, y, w, h, CARD, rounded=True, adj=0.08)
    d.box(s, x, y + 0.06, 0.06, h - 0.12, accent)
    th = lsize * 1.4 / 72
    T(s, x + 0.3, y + (h - th) / 2, lw, th + 0.02, label, lsize, bold=True, ln=1.4, wrap=False)
    dh = dsize * 1.4 / 72
    T(s, x + 0.3 + lw, y + (h - dh) / 2, w - lw - 2.0, dh + 0.02, desc, dsize, color='C9D0DC', ln=1.4, wrap=False)
    if key:
        T(s, x + w - 1.9, y + (h - dh) / 2, 1.65, dh + 0.02, key, dsize + 1, color=accent, bold=True, ln=1.4,
          wrap=False, align='r')


def prompt(s, x, y, w, h, label, lines, size=15.5, accent=RED, tip=None):
    card(s, x, y, w, h, LINE, fill='101827')
    d.box(s, x, y + 0.12, 0.06, 0.34, accent)
    T(s, x + 0.28, y + 0.12, w - 0.4, 0.35, label, 14, color=accent, bold=True, wrap=False)
    T(s, x + 0.28, y + 0.62, w - 0.5, h - 0.7, lines, size, ln=1.6)
    if tip:
        T(s, x + 0.28, y + h - 0.45, w - 0.5, 0.35, tip, 13, color=MUTED, wrap=False)


def step(s, x, y, w, h, num, text, accent, size=17):
    card(s, x, y, w, h, accent)
    T(s, x + 0.22, y + (h - 0.4) / 2, 0.7, 0.42, num, 20, color=accent, bold=True, wrap=False)
    lines = text if isinstance(text, list) else [text]
    th = len(lines) * size * 1.4 / 72
    T(s, x + 0.82, y + (h - th) / 2, w - 0.95, th + 0.03, lines, size, bold=True, ln=1.4)


def pill(s, x, y, label, color=GREEN, size=13, h=0.36, fill='0E1F22'):
    w = text_w(label, size) + 0.36
    border(d.box(s, x, y, w, h, fill, rounded=True, adj=0.5), color, 12700)
    T(s, x + 0.18, y + (h - size * 1.45 / 72) / 2, w, h, label, size, color=color, bold=True, ln=1.45, wrap=False, check=False)
    return w


def mindmap(s, y, center, left, right, row_h=0.66, gap=0.07, cw=2.5, sw=4.35, tsize=16.5, dsize=12.5):
    n = max(len(left), len(right))
    total = n * row_h + (n - 1) * gap
    cx = X0 + sw + (CW - 2 * sw - cw) / 2
    ch = 1.2
    cy = y + total / 2 - ch / 2
    for side, items, acc in (('L', left, RED), ('R', right, GOLD)):
        bx = X0 if side == 'L' else XR - sw
        for i, (a, b) in enumerate(items):
            by = y + i * (row_h + gap)
            if side == 'L':
                line(s, bx + sw, by + row_h / 2, cx, cy + ch / 2)
            else:
                line(s, cx + cw, cy + ch / 2, bx, by + row_h / 2)
            card(s, bx, by, sw, row_h, acc)
            T(s, bx + 0.22, by + 0.06, sw - 0.3, 0.36, a, tsize, bold=True, wrap=False)
            T(s, bx + 0.22, by + 0.07 + tsize * 1.32 / 72, sw - 0.3, 0.3, b, dsize, color=MUTED, wrap=False)
    d.box(s, cx, cy, cw, ch, RED, rounded=True, adj=0.12)
    T(s, cx + 0.1, cy + 0.2, cw - 0.2, 0.8, center, 20, color='FFFFFF', bold=True, ln=1.3, align='ctr')
    return y + total


# 1 封面 =============================================================
s = S(image='cover.jpg')
pill(s, X0, 0.62, '一周一课 · AI 下半场')
T(s, 0.75, 2.0, 6, 0.35, 'PROMPT · KNOWLEDGE BASE · 2026.11.04', 13, color=GREEN, bold=True, spc=150, wrap=False)
T(s, 0.7, 2.42, 6.2, 1.9, ['先问对，', [('再让 ', {}), ('AI 懂你', {'color': GOLD})]], 54, bold=True, ln=1.18, wrap=False)
T(s, 0.75, 4.42, 6, 0.8, ['今天学会两件事：', '把需求说清楚，让 AI 用你的资料干活。'], 17, color='C9D0DC', ln=1.6)
x = X0
for t_ in ('会提问', '避误区', '建知识库'):
    x += pill(s, x, 6.45, t_, size=12.5, h=0.34) + 0.12
T(s, x + 0.1, 6.5, 3, 0.3, '闫亚老师 主讲', 13, color=MUTED, bold=True, wrap=False)

# 2 =================================================================
s = S()
d.header(s, '上节课讲到哪了', '上节课还差两块，今天四步走', aside=['工具会选了，', '问法不对，照样白搭。'])
w = (CW - 0.25) / 2
bcard(s, X0, Y, w, 1.9, GREEN, '上节课讲了', ['Chat 用来想，Work 用来干', 'AI 的三个阶段：会聊、会想、会干', '模型是大脑，工具是工位'])
bcard(s, X0 + w + 0.25, Y, w, 1.9, RED, '还差两块', ['怎么问 AI：提问框架', '用 AI 的八个误区'])
T(s, 0.75, 4.0, 3, 0.3, '今天四步走', 14, color=MUTED, bold=True, wrap=False)
w4 = (CW - 0.6) / 4
for i, (t_, a) in enumerate([('怎么问', RED), ('八个误区', GOLD), (['为什么要', '有知识库'], GREEN), (['怎么搭', '+ 现场演示'], RED)]):
    step(s, X0 + i * (w4 + 0.2), 4.4, w4, 1.0, f'0{i + 1}', t_, a)

# 3 =================================================================
s = S()
d.header(s, '先看一张对比', '同一个 AI，差在会不会提需求', aside=['2 月份讲过：', '提示词就是刀工。'])
y = d.table(s, Y, [3.0, 5.43], ['一句话问法', '说清楚的问法'],
            [['帮我写一条朋友圈', ['我是杭州做二奢寄卖的，客户多是 30 岁上班族。', '帮我写一条上新朋友圈，120 字左右，口气实在。']],
             ['LV Neverfull 回收价多少？', ['我收了一只中号，九成新、配件齐。', '定价要看哪几方面？每样怎么影响价格？']],
             ['双 11 怎么搞活动？', ['我有 8 只货超过 30 天。双 11 有哪几种做法？', '各有什么坑？先问我几个问题。']],
             ['客户问完价就不回了，怎么办？', ['这是聊天记录（已删名字电话）。', '她为什么不回？断在哪一步？下次怎么接？']]],
            size=15, head_size=14.4, first_color=MUTED, first_bold=False, row_pad=0.06)
d.callout(s, y + 0.25, '右边多出来的，就是下一页的框架。', size=18)

# 4 =================================================================
s = S()
d.header(s, '2 月份讲过，今天完整过一遍', '提问框架：角目人书风', aside=['六个字，', '一个字一件事。'])
items = [('角 · 角色', '你让它当谁', ['例：做了十年的寄卖老板']),
         ('任 · 任务', '要它干什么', ['例：写一条上新朋友圈']),
         ('目 · 目的', '为了什么', ['例：让想买的人来问']),
         ('人 · 人群', '给谁看', ['例：30 岁左右的上班族']),
         ('书 · 输出', '要什么样的东西', ['例：1 条，120 字左右']),
         ('风 · 风格', '什么口气', ['例：实在，不夸张'])]
y = grid(s, Y, items, 3, 1.62, accents=[RED, RED, RED, GOLD, GOLD, GOLD], tsize=21)
d.note(s, y + 0.25, '六格的“例”连起来，就是“写一条上新朋友圈”的完整填法。', size=15, w=9.0)

# 5 =================================================================
s = S()
d.header(s, '六个字记不住，最少说清这四件', '最少说清四件事', aside=['漏了“前提”，', 'AI 只能自己编。'])
rows = [('01', '我是谁', '做回收还是寄卖、在哪、做了几年', RED),
        ('02', '要干什么', '写朋友圈、写话术、做表格', GOLD),
        ('03', '前提', '这只货什么样、这周发生了什么', RED),
        ('04', '给谁看', '想出手的姐，还是想买的上班族', GOLD)]
lw = 4.7
for i, (n_, a, b, acc) in enumerate(rows):
    yy = Y + i * 0.93
    card(s, X0, yy, lw, 0.8, acc)
    T(s, X0 + 0.22, yy + 0.17, 0.7, 0.45, n_, 22, color=acc, bold=True, wrap=False)
    T(s, X0 + 0.9, yy + 0.08, lw - 1.0, 0.35, a, 18, bold=True, wrap=False)
    T(s, X0 + 0.9, yy + 0.43, lw - 1.0, 0.3, b, 13.5, color=MUTED, wrap=False)
prompt(s, X0 + lw + 0.3, Y, CW - lw - 0.3, 3.59, '拼起来是这样（课后发群）',
       ['我是杭州做二奢寄卖的老板，做了 6 年，说话实在、不夸张。',
        '帮我写一条朋友圈，推这周到的一只链条小方包。',
        '包是八五新，链条有正常使用痕迹，配件齐全；昨天有位老客户问过同款。',
        '给 30 岁左右、想买第一只包的上班族看。',
        '120 字左右，第一句 15 字以内，不写“鉴定”和绝对化用语。'], size=15.5)
d.callout(s, 5.72, '四件事说清楚，AI 就不用瞎猜。', size=18)

# 6 =================================================================
s = S()
d.header(s, '问 AI 别只问“是什么”', '六个引导词，让 AI 帮你想', aside=['只问“是什么”，它给答案；', '加上这六个词，它帮你想。'])
items = [('1 · 找原因', '为什么', ['为什么点赞多、私聊少？']),
         ('2 · 要步骤', '怎么做', ['分几步？第一步做什么？']),
         ('3 · 推演后果', '如果', ['如果降价 10%，会怎样？']),
         ('4 · 要多个方案', '有哪几种', ['给我 3 种，各有什么坑']),
         ('5 · 找盲点', '我漏了什么', ['站在客户角度挑我的毛病']),
         ('6 · 让它了解你', '先问我', ['先别答，一次问我一个问题'])]
y = grid(s, Y, items, 3, 1.5, accents=[RED, RED, RED, GOLD, GOLD, GREEN], tsize=22)
d.callout(s, y + 0.3, '先说你的情况，再用引导词。', size=18)

# 7 =================================================================
s = S()
d.header(s, '写不好也没关系', '写不好，就让 AI 帮你写提示词', aside=['自己硬写，总漏东西；', '让它问你，问完就齐了。'])
bw, bh = 2.65, 1.3
pos = [(X0, Y), (X0 + bw + 0.55, Y), (X0 + bw + 0.55, Y + bh + 0.6), (X0, Y + bh + 0.6)]
txt = [['你说', '要干什么'], ['它按六项', '一个个问你'], ['整理成', '一段提示词'], ['存起来', '下次直接用']]
acc = [RED, GOLD, GREEN, GOLD]
for i, ((x, yy), t_, a) in enumerate(zip(pos, txt, acc)):
    step(s, x, yy, bw, bh, f'0{i + 1}', t_, a, size=17)
T(s, X0 + bw + 0.1, Y + 0.38, 0.4, 0.5, '→', 26, color=GREEN, bold=True, wrap=False, check=False)
T(s, X0 + bw + 0.55 + bw / 2 - 0.15, Y + bh + 0.05, 0.4, 0.5, '↓', 26, color=GREEN, bold=True, wrap=False, check=False)
T(s, X0 + bw + 0.1, Y + bh + 0.98, 0.4, 0.5, '←', 26, color=GREEN, bold=True, wrap=False, check=False)
px = X0 + 2 * bw + 0.95
prompt(s, px, Y, XR - px, 3.2, '润色提示词的话（课后发群）',
       ['我想让你帮我[写一条朋友圈 / 写一段话术 / 做一张表]。',
        '先别写。请按“角色、任务、目的、人群、输出、风格”六项，看我还缺哪些信息，一次只问我一个问题。',
        '问完以后，帮我整理成一段完整的提示词，我存起来以后直接用。'], size=15.5)
d.callout(s, 5.62, '先把提示词想清楚，再拿去干活。', size=18)

# 8 =================================================================
s = S()
d.header(s, '上节课没讲完的，今天补上', '用 AI 的八个误区', aside=['每条先问：', '这话你说过没有？'])
mindmap(s, Y, ['用 AI 的', '八个误区'],
        [('1 只会聊天？', '3.0 已经能干活，交给你做好的文件'),
         ('2 它什么都懂？', '不懂你的店和行情，还会编'),
         ('3 一句话就行？', '最少说清四件事'),
         ('4 写完直接发？', 'AI 出初稿，你过嘴改稿')],
        [('5 工具越多越好？', '一个 Chat、一个 Work 用熟'),
         ('6 能辨真假、定价格？', '它不能拍板，最后是你'),
         ('7 会抢饭碗、学不会？', '抢的是重复活；会说话就会用'),
         ('8 资料随便给？', '身份证、银行卡、手机号不给')], row_h=0.8, gap=0.12, tsize=17, dsize=13.5)
d.callout(s, 5.72, '八条中了几条？公屏打数字。第 6、8 条是底线。', size=18)

# 9 =================================================================
s = S()
d.header(s, '边界', '什么交给它，什么你拍板', aside=['左边是活，', '右边是责任。'])
w = (CW - 0.25) / 2
for k, (t_, items, a, mark) in enumerate([('放心交给它', ['写初稿、改稿、换说法', '整理、汇总、做表格', '批量出东西、定时提醒', '出框架、出选题、陪你练话术'], GREEN, '✓'),
                                          ('必须你拍板', ['这只包是真是假', '最终报价，收不收', '和客户建立信任', '合不合规、客户故事真不真'], RED, '!')]):
    x = X0 + k * (w + 0.25)
    card(s, x, Y, w, 3.35, a, fill='0E1F22' if a == GREEN else '1D1420')
    T(s, x + 0.3, Y + 0.22, w - 0.5, 0.45, t_, 21, color=a, bold=True, wrap=False)
    for i, it in enumerate(items):
        yy = Y + 0.9 + i * 0.6
        border(d.box(s, x + 0.3, yy + 0.04, 0.3, 0.3, CARD, rounded=True, adj=0.15), a, 12700)
        T(s, x + 0.3, yy + 0.02, 0.3, 0.3, mark, 13, color=a, bold=True, align='ctr', wrap=False, check=False)
        T(s, x + 0.8, yy, w - 1.0, 0.36, it, 17, wrap=False)
d.callout(s, 5.5, ['能交出去的是活，交不出去的是责任。', '身份证、银行卡、手机号，客户的、自己的都不给。'], size=18)

# 10 ================================================================
s = S()
d.header(s, '提示词会写了，新问题来了', '问得再好，它还是不懂你')
T(s, 0.75, 1.95, 2.6, 0.3, '每次都要讲', 13, color=MUTED, bold=True, wrap=False)
T(s, 10.0, 1.95, 2.58, 0.3, '老伙计早知道', 13, color=MUTED, bold=True, wrap=False, align='r')
for (x, yy, t_), side in zip([(0.9, 2.35, '你是谁'), (0.75, 3.35, '客户是谁'), (1.05, 4.35, '以前怎么说的')], 'LLL'):
    wv = text_w(t_, 18) + 0.5
    border(d.box(s, x, yy, wv, 0.66, CARD, rounded=True, adj=0.12), LINE)
    T(s, x + 0.25, yy + 0.15, wv, 0.4, t_, 18, wrap=False)
    line(s, x + wv, yy + 0.33, x + wv + 0.6, yy + 0.33, RED)
for x, yy, t_ in [(10.85, 2.35, '你的脾气'), (11.05, 3.35, '你的客户'), (10.2, 4.35, '上次怎么处理')]:
    wv = text_w(t_, 18) + 0.5
    x = min(x, XR - wv)
    border(d.box(s, x, yy, wv, 0.66, CARD, rounded=True, adj=0.12), LINE)
    T(s, x + 0.25, yy + 0.15, wv, 0.4, t_, 18, wrap=False)
    line(s, x - 0.6, yy + 0.33, x, yy + 0.33, GREEN)
T(s, 3.3, 2.5, 6.7, 1.4, ['每次都要现教，', [('它还是记不住。', {'color': RED})]], 34, bold=True, ln=1.3, align='ctr')
T(s, 3.3, 4.0, 6.7, 0.8, ['第一次见面的人，只能按常理给建议；', '跟了你十年的老伙计，知道你的脾气、你的客户。'], 15.5,
  color='C9D0DC', ln=1.65, align='ctr')
d.callout(s, 5.62, ['它能干多好，取决于你给它多少。', '每次都现教？太累，所以要有知识库。'], size=18)

# 11 ================================================================
s = S()
d.header(s, '一页讲清楚', '为什么要有知识库', aside=['员工走了，经验带走一半；', '存下来，AI 每次都能翻。'])
items = [('为什么要有', '每次现教，太累', ['人走经验走，新人带不出来，', '每次都要从头讲']),
         ('有没有用', '喂了资料，像你说的', ['不喂，最好的模型也就 80 分；', '喂了，还能指出出自哪段素材']),
         ('值不值', '最值钱的在你脑子里', ['哪类客户爱砍价、什么成色报什么价，', '都是你亏过钱才换来的']),
         ('是什么', '决策系统，不是资料堆', ['存你怎么想、怎么判断；', '网上能搜到的不存，只存你有的'])]
y = grid(s, Y, items, 2, 1.65, accents=[RED, GOLD, GOLD, GREEN], tsize=21, bsize=14.5)
d.callout(s, y + 0.25, '知识库，就是把你这个老板装进 AI。', size=18)

# 12 ================================================================
s = S()
d.header(s, '存进去以后', '知识库能干的十件事', aside=['你最想先用哪个？', '公屏打数字。'])
mindmap(s, 1.8, ['知识库', '能干的十件事'],
        [('1 写文案', '口播、脚本，用你的说法写'),
         ('2 写朋友圈', '客户原话变成一周 7 条'),
         ('3 经营思考', '让它跟你辩，下一页细讲'),
         ('4 选题库', '客户反复问的，就是好选题'),
         ('5 证言和案例', '找出客户原话做朋友圈')],
        [('6 话术和客服', '新问题先查以前怎么答'),
         ('7 新员工培训', '员工先问 AI，等于问老板'),
         ('8 报价依据', '查同款历史成交，你来定价'),
         ('9 防骗核查', '收货前对照骗局案例'),
         ('10 人设一致', '都按你的观点写，不说两套')])
d.callout(s, 5.7, '存进去的越真，它干得越像你。', size=18)

# 13 ================================================================
s = S()
d.header(s, '十件事里最值钱的一件', '洞察对话：你是主公，AI 是幕僚', aside=['一个人拍脑袋，', '不如辩完再定。'])
lw = 4.9
for i, (t_, a) in enumerate([('拖进会议记录', GREEN), ('提一个问题', GREEN), ('让它翻库反驳你', GOLD), ('辩三到五轮', GOLD), ('结论加入知识库', RED)]):
    yy = Y + i * 0.72
    card(s, X0, yy, lw, 0.6, a)
    T(s, X0 + 0.22, yy + 0.12, 0.6, 0.38, f'0{i + 1}', 17, color=a, bold=True, wrap=False)
    T(s, X0 + 0.85, yy + 0.12, lw - 1.0, 0.38, t_, 17, bold=True, wrap=False)
px = X0 + lw + 0.3
prompt(s, px, Y, XR - px, 3.48, '例子（课后发群）',
       ['结合知识库，我们讨论一个问题：', '双 11 要不要给超过 30 天的货降价。',
        '你先说判断和理由，再反驳我的想法，我们来回辩三轮。', '最后把结论加入知识库。'], size=16,
       tip='时间固定：晚上十点后或早上，语音跟它聊。')
d.callout(s, 5.65, '幕僚天天挑战主公，辩完了，想法就清楚了。', size=18)

# 14 ================================================================
s = S()
d.header(s, '存什么', '知识库的十大来源', aside=['左边：你说出来的，录下来；', '右边：你手上有的，整理进来。'])
mindmap(s, 1.8, ['知识库的', '十大来源'],
        [('接待客户录音', '客户原话、真实顾虑'),
         ('日常感悟', '开车、散步时随口录'),
         ('会议和复盘', '决策过程和理由'),
         ('拍视频、直播', '讲过的干货'),
         ('同行爆款、好文章', '拆写法，不照搬')],
        [('成交和报价记录', '下次报价有依据'),
         ('好评截图（打码）', '做证言'),
         ('自己的爆款文案', '让 AI 学你的口气'),
         ('踩过的坑、骗局', '防骗和新人培训'),
         ('SOP 和经营数据', '培训和月度复盘')])
d.callout(s, 5.7, '只存你有的，越真越好：能录的都录下来。', size=18)

# 15 ================================================================
s = S()
d.header(s, '放在哪', '一个文件夹，十一个格子', aside=['大杂烩和分好格子，', 'AI 翻起来差很多。'])
y = d.table(s, Y, [0.8, 1.9, 1.5, 0.8, 1.9, 1.53], ['编号', '文件夹', '放什么', '编号', '文件夹', '放什么'],
            [['00', '待整理', '先扔这里', '06', '话术库', '回收、销售'],
             ['01', '客户原话', '接待录音', '07', 'SOP', '各环节流程'],
             ['02', '报价与成交', '成交记录', '08', '风控与踩坑', '骗局案例'],
             ['03', '内容素材', '选题、爆款', '09', '经营数据', '库存、月报'],
             ['04', '我的观点', '日常感悟', '10', '外部资料', '链接、文章'],
             ['05', '会议与复盘', '会议纪要', '', '', '']], size=15, head_size=14.4, row_pad=0.08)
d.callout(s, y + 0.25, '换工具、换模型，文件夹不用动，积累不会丢。', size=18,
          sub='命名：日期_主题_来源，例：1103_回收LV客户_接待录音')

# 16 ================================================================
s = S()
d.header(s, '光有格子不够', '让 AI 看懂你的库', aside=['三个文件让它看得懂，', '三类内容让它分得清。'])
items = [('文件 1 · 说明书', 'README', ['这个库干什么、有哪些格子']),
         ('文件 2 · 总目录', '索引', ['先看目录再找，省时间省积分']),
         ('文件 3 · 你这个人', '核心认知', ['定价原则、做事方法，聊完就加'])]
grid(s, Y, items, 3, 1.45, accents=[BLUE, BLUE, GOLD], tsize=21, bsize=15)
for i, (a, b, c, acc) in enumerate([('长期认知', '超 30 天的货必须动；先查验再报价', '长期留下', GOLD),
                                    ('当前工作', '双 11 在做什么、做到哪一步', '接着做', GREEN),
                                    ('证据', '这个判断出自哪段录音、哪单成交', '能回查', RED)]):
    rowcard(s, X0, 3.55 + i * 0.64, CW, 0.54, acc, a, b, c, lsize=17, dsize=15)

# 17 ================================================================
s = S()
d.header(s, '不用自己建', '复制就能用：一段话建好知识库', aside=['自己建要半小时，', '发一段话一分钟。'])
prompt(s, X0, Y, CW, 3.05, '建库的话（发给 WorkBuddy，课后发群）',
       ['在桌面建一个“知识库”文件夹，里面建好这些子文件夹：',
        '00 待整理、01 客户原话、02 报价与成交、03 内容素材、04 我的观点、05 会议与复盘、',
        '06 话术库、07 SOP、08 风控与踩坑、09 经营数据、10 外部资料。',
        '再写好三个文件：README（说明每个文件夹放什么）、索引、核心认知。',
        '文件统一按“日期_主题_来源”命名。以后我说“加入知识库”，你就按这个结构归档。',
        [('身份证、银行卡、手机号一律不存。', {'color': RED, 'bold': True})]], size=16)
d.callout(s, 5.2, '以后只要说一句“加入知识库”，它就按这个结构归档。', size=18)

# 18 ================================================================
s = S()
d.header(s, '建好不是终点', '库是养出来的：三个习惯', aside=['建了不用，就是死库；', '天天用，它越来越懂你。'])
items = [('每天', '一句话', ['聊出好东西就说：', '“把今天聊的核心内容', '加入知识库，加入记忆”']),
         ('每周', '整理一次', ['让 AI 把“待整理”归档，', '你看一眼就行']),
         ('一直', '在活里养', ['不为优化而优化，', '在真实的活里用，', '用完告诉它改了哪'])]
w3 = (CW - 0.4) / 3
for i, ((a, b, c), acc) in enumerate(zip(items, [RED, GOLD, GREEN])):
    x = X0 + i * (w3 + 0.2)
    card(s, x, Y, w3, 2.62, acc)
    T(s, x + 0.28, Y + 0.22, w3 - 0.4, 0.6, a, 30, color=acc, bold=True, wrap=False)
    T(s, x + 0.28, Y + 0.85, w3 - 0.4, 0.4, b, 20, bold=True, wrap=False)
    T(s, x + 0.28, Y + 1.32, w3 - 0.45, 1.1, c, 15, color='C9D0DC', ln=1.5)
d.callout(s, Y + 2.92, '换工具、换模型，都回到同一个文件夹干活。', size=18)

# 19 ================================================================
s = S()
d.header(s, '现场做一遍', '现场演示：四步走', aside=['模型慢就放录屏，', '字号放大。'])
w4 = (CW - 0.6) / 4
for i, (t_, a) in enumerate([('润色提示词', RED), ('看我的知识库', GOLD), ('一段录音进库', GREEN), ('从库里出活', RED)]):
    step(s, X0 + i * (w4 + 0.2), Y, w4, 0.75, f'0{i + 1}', t_, a, size=16.5)
w2 = (CW - 0.25) / 2
prompt(s, X0, 2.85, w2, 2.5, '③ 进库的话', ['这是我今天接待一位回收客户的录音转文字，已删掉姓名电话。',
                                         '整理成：客户要什么、客户原话、顾虑、怎么报价、结果。',
                                         '存进“01 客户原话”，按“日期_主题_来源”命名。'], size=15, accent=GREEN)
prompt(s, X0 + w2 + 0.25, 2.85, w2, 2.5, '④ 出活的话', ['结合知识库里这位客户的原话和我的核心认知：',
                                                     '1. 总结她的 3 个顾虑；2. 给 1 条话术改进；',
                                                     '3. 按朋友圈提示词写 2 条朋友圈。只用素材里有的。'], size=15)
d.note(s, 5.65, '共享屏幕前，先确认屏幕上没有身份证、银行卡、客户信息。', size=15, w=9.0)

# 20 ================================================================
s = S()
d.header(s, '这周就开始', '作业和最后一句')
items = [('起步店', '三件事', ['① 用一段话建好库', '② 录 3 段接待录音', '③ 转好文字放进去']),
         ('成熟店', '三件事', ['① 写好核心认知文件', '② 用四件事写提示词', '③ 做一次洞察对话']),
         ('所有人', '一句话', ['聊出好东西，', '说一句“加入知识库”'])]
w3 = (CW - 0.4) / 3
for i, ((a, b, c), acc) in enumerate(zip(items, [RED, GOLD, GREEN])):
    x = X0 + i * (w3 + 0.2)
    card(s, x, Y, w3, 2.0, acc)
    T(s, x + 0.28, Y + 0.2, w3 - 0.4, 0.45, a, 22, color=acc, bold=True, wrap=False)
    T(s, x + 0.28, Y + 0.72, w3 - 0.45, 1.2, c, 16, ln=1.5)
y = d.callout(s, Y + 2.3, ['先问对，再让 AI 懂你。', '提示词说清四件事，知识库存你自己的东西。'], size=21)
T(s, 0.75, y + 0.28, 9.0, 0.6, ['课后发群：润色提示词、建库、进库、出活、洞察对话',
                               '下节课投票：1 Skill 专场　2 防骗专题'], 13.5, color=MUTED, ln=1.6)

d.prs.save(sys.argv[1])
print('slides', d.n)
for w_ in WARN:
    print('WARN', w_)
md = ['# 11/04 逐页讲稿：先问对，再让 AI 懂你', '',
      '- 20 页，90 分钟。一件事讲一页，页面放整理好的结论，例子由你现场举。',
      '- 每页右下角空着，留给直播头像。',
      '- 每页备注按五步写：问（先问学员什么）→ 例（讲哪个例子）→ 比（拿什么对比）→ 句（亮出页面上那句话）→ 做（让学员干什么，或者怎么过渡）。', '']
for i, (t, n) in enumerate(TITLES, 1):
    md += [f'## 第 {i} 页 · {t}', '', n, '']
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(md))
