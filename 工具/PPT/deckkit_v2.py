"""照讲师 09-02 模板的视觉语言出图的小工具。"""
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

FONT = 'PingFang SC'
BG, INK, MUTED = '0B1120', 'F2F4F8', '8E98AA'
RED, DRED, GOLD, GREEN, BLUE = 'FF5A4E', 'FF5A4E', 'F5A524', '22C3A6', '5B9BFF'
CARD, YEL, YEL_INK = '121A2B', '1A1622', 'F2F4F8'
PINK, MINT, QUOTE, LINE = '1D1420', '0E1F22', '131C2E', '2A3650'
DARK, SUN, DARK_MUTED = '0B1120', 'F5A524', '8E98AA'
MONO = 'Consolas'
PARTS = {}
PCOL = {}
AZ = (9.95, 5.45)  # 右下角留给头像：x 和 y 都超过就算压到


def _hit(x, y, w, h):
    return x + w > AZ[0] + 0.01 and y + h > AZ[1] + 0.01
X0, CW = 0.75, 11.83
XR = X0 + CW
WARN = []


def char_w(ch, size):
    o = ord(ch)
    if ch == ' ':
        em = 0.4
    elif o < 128:
        em = 0.68 if ch.isupper() or ch.isdigit() else 0.56
    else:
        em = 1.0
    return em * size / 72


def text_w(s, size, spc=0):
    return sum(char_w(c, size) + spc / 7200 for c in s)


def wrap_lines(s, size, width, spc=0):
    if not s:
        return 1
    lines, cur = 1, 0.0
    for c in s:
        w = char_w(c, size) + spc / 7200
        if cur + w > width + 1e-6:
            lines += 1
            cur = w
        else:
            cur += w
    return lines


class Deck:
    def __init__(self, template):
        self.prs = Presentation(template)
        lst = self.prs.slides._sldIdLst
        for sid in list(lst):
            self.prs.part.drop_rel(sid.get(qn('r:id')))
            lst.remove(sid)
        self.blank = [l for l in self.prs.slide_layouts if l.part.partname.endswith('slideLayout7.xml')][0]
        self.n = 0

    def slide(self, kind='light', notes=None, image=None):
        s = self.prs.slides.add_slide(self.blank)
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        fill = s.background.fill
        fill.gradient()
        fill.gradient_angle = 30 if kind == 'title' else 20
        st = fill.gradient_stops
        st[0].position, st[1].position = 0.0, 1.0
        st[0].color.rgb = RGBColor.from_string('0A0F1C')
        st[1].color.rgb = RGBColor.from_string('0E2228' if kind == 'title' else '1A1420')
        if image:
            s.shapes.add_picture(image, 0, 0, self.prs.slide_width, self.prs.slide_height)
        else:
            for i in range(1, 15):
                self._grid(s, i * 0.9, 0, i * 0.9, 7.5)
            for i in range(1, 9):
                self._grid(s, 0, i * 0.9, 13.33, i * 0.9)
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        self.n += 1
        s._deck_no = self.n
        return s

    def _grid(self, s, x1, y1, x2, y2):
        c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = RGBColor.from_string('141C2E')
        c.line.width = Emu(6350)

    def box(self, s, x, y, w, h, fill, rounded=False, adj=0.04, line=None, name=None):
        if line is None and rounded and fill in (CARD, PINK, MINT, QUOTE):
            line = LINE
        shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor.from_string(fill)
        if line:
            shp.line.color.rgb = RGBColor.from_string(line)
            shp.line.width = Emu(9525)
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False
        st = shp._element.find(qn('p:style'))
        if st is not None:
            shp._element.remove(st)
        if rounded:
            shp.adjustments[0] = adj
        if name:
            shp.name = name
        if _hit(x, y, w, h):
            WARN.append(f'第 {s._deck_no} 页 色块压到头像区 ({x:.2f},{y:.2f},{w:.2f},{h:.2f})')
        return shp

    def text(self, s, x, y, w, h, paras, size, color=INK, bold=False, ln=1.55, spc=0,
             wrap=True, anchor='t', align='l', name=None, check=True):
        if isinstance(paras, str):
            paras = [paras]
        shp = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            shp.name = name
        tf = shp.text_frame
        body = tf._txBody.find(qn('a:bodyPr'))
        for ch in list(body):
            body.remove(ch)
        body.attrib.clear()
        body.set('wrap', 'square' if wrap else 'none')
        for k in ('lIns', 'tIns', 'rIns', 'bIns'):
            body.set(k, '0')
        body.set('anchor', anchor)
        need_h = 0.0
        max_w = 0.0
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            runs = para if isinstance(para, list) else [(para, {})]
            psize = max(o.get('size', size) for _, o in runs)
            pPr = p._p.get_or_add_pPr()
            pPr.set('algn', align)
            lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
            etree.SubElement(lnSpc, qn('a:spcPts')).set('val', str(int(round(psize * ln * 100))))
            for tag in ('a:spcBef', 'a:spcAft'):
                etree.SubElement(etree.SubElement(pPr, qn(tag)), qn('a:spcPts')).set('val', '0')
            full = ''
            for t, o in runs:
                r = p.add_run()
                r.text = t
                full += t
                rPr = r._r.get_or_add_rPr()
                rPr.set('lang', 'zh-CN')
                rPr.set('sz', str(int(round(o.get('size', size) * 100))))
                rPr.set('b', '1' if o.get('bold', bold) else '0')
                rPr.set('i', '0')
                if o.get('spc', spc):
                    rPr.set('spc', str(o.get('spc', spc)))
                sf = etree.SubElement(rPr, qn('a:solidFill'))
                etree.SubElement(sf, qn('a:srgbClr')).set('val', o.get('color', color))
                for tag in ('a:latin', 'a:ea', 'a:cs'):
                    etree.SubElement(rPr, qn(tag)).set('typeface', FONT)
            line_h = psize * ln / 72
            if wrap:
                need_h += wrap_lines(full, psize, w, spc) * line_h
            else:
                need_h += line_h
                max_w = max(max_w, text_w(full, psize, spc))
        if check:
            where = f'第 {s._deck_no} 页'
            first = paras[0] if isinstance(paras[0], str) else paras[0][0][0]
            if not wrap and max_w > w + 0.02:
                WARN.append(f'{where} 文字超宽 {max_w:.2f} > {w:.2f}: {first[:16]}')
            if need_h > h + 0.05:
                WARN.append(f'{where} 文字超高 {need_h:.2f} > {h:.2f}: {first[:16]}')
            if y + max(h, need_h) > 7.3:
                WARN.append(f'{where} 超出页面底部')
            tw_ = max_w if not wrap else w
            if _hit(x, y, tw_, max(h, need_h)):
                WARN.append(f'{where} 文字压到头像区: {first[:16]}')
        return shp, need_h

    def chip(self, s, x, y, label, fill=RED, color='FFFFFF', size=14.39, h=0.34, pad=0.1):
        w = text_w(label, size) + pad * 2
        self.box(s, x, y, w, h, fill, rounded=True, adj=0.098)
        self.text(s, x + pad, y + (h - size * 1.55 / 72) / 2 + 0.01, w, h, label, size, color=color,
                  bold=True, wrap=False, check=False)
        return w

    def header(self, s, kicker=None, title=None, aside=None, title_lines=None, **_):
        pre = PARTS.get(s._deck_no)
        kc = PCOL.get(pre, RED)
        if kicker:
            k = f'{pre} · {kicker}' if pre else kicker
            self.text(s, 0.74, 0.48, 8.5, 0.4, k, 14.4, color=kc, bold=True, wrap=False)
        lines = title_lines or [title]
        h = len(lines) * 40 * 1.2 / 72
        self.text(s, 0.72, 0.86, 9.4, h + 0.1, lines, 40, bold=True, ln=1.2, wrap=False)
        if aside:
            al = aside if isinstance(aside, list) else [aside]
            self.text(s, 9.2, 0.98, 3.38, 0.8, al, 14.4, color=MUTED, ln=1.6, align='r')
        return 0.86 + h

    def finalize(self):
        n = len(self.prs.slides)
        for i, sl in enumerate(self.prs.slides, 1):
            sl._deck_no = i
            t = f'{i:02d} / {n:02d}'
            self.text(sl, 11.2, 0.5, 1.4, 0.4, t, 14.39, color=GREEN, bold=True, wrap=False, align='r', check=False)

    def callout(self, s, y, lines, size=20, h=None, x=X0, w=9.0, color=YEL_INK, sub=None):
        if isinstance(lines, str):
            lines = [lines]
        th = len(lines) * size * 1.4 / 72
        sh = 0.36 if sub else 0
        h = h or th + sh + 0.36
        self.box(s, x, y, w, h, YEL)
        self.box(s, x, y, 0.06, h, RED)
        self.text(s, x + 0.3, y + 0.18, w - 0.5, th + 0.05, lines, size, color=color, bold=True, ln=1.4)
        if sub:
            self.text(s, x + 0.3, y + 0.18 + th + 0.04, w - 0.5, 0.35, sub, 13.2, color=MUTED, ln=1.55)
        return y + h

    def note(self, s, y, lines, size=16.2, color=MUTED, w=CW, x=0.74):
        if isinstance(lines, str):
            lines = [lines]
        h = sum(wrap_lines(l, size, w) for l in lines) * size * 1.55 / 72
        self.text(s, x, y, w, h + 0.05, lines, size, color=color)
        return y + h

    def scene_card(self, s, y, label, lines, size=19.2, bar=BLUE, h=None, fill=CARD):
        th = sum(wrap_lines(l, size, CW - 0.6) for l in lines) * size * 1.5 / 72
        h = h or th + 0.62
        self.box(s, X0, y, CW, h, fill)
        self.box(s, X0, y, 0.05, h, bar)
        self.text(s, 1.04, y + 0.18, 3, 0.3, label, 13.2, color=GREEN, bold=True, wrap=False, spc=200)
        self.text(s, 1.04, y + 0.48, CW - 0.6, th + 0.05, lines, size, ln=1.5)
        return y + h

    def pair_cards(self, s, y, left, right, h=None, size=16.8, colors=((PINK, DRED), (MINT, GREEN))):
        w = (CW - 0.17) / 2
        ths = []
        for _, lines in (left, right):
            ths.append(sum(wrap_lines(l, size, w - 0.5) for l in lines) * size * 1.55 / 72)
        h = h or max(ths) + 0.75
        for i, ((label, lines), (bg, bar)) in enumerate(zip((left, right), colors)):
            x = X0 + i * (w + 0.17)
            self.box(s, x, y, w, h, bg, rounded=True, adj=0.04)
            self.box(s, x, y, 0.07, h, bar)
            self.text(s, x + 0.26, y + 0.18, w - 0.4, 0.3, label, 13.2, color=bar, bold=True, wrap=False)
            self.text(s, x + 0.26, y + 0.52, w - 0.5, ths[i] + 0.05, lines, size)
        return y + h

    def top_cards(self, s, y, cards, h, n=None, gap=0.15, bars=None):
        n = n or len(cards)
        w = (CW - gap * (n - 1)) / n
        bars = bars or [RED] * n
        for i, draw in enumerate(cards):
            x = X0 + i * (w + gap)
            self.box(s, x, y, w, h, CARD, rounded=True, adj=0.03)
            self.box(s, x, y, w, 0.05, bars[i])
            draw(x, y, w)
        return y + h

    def numbered(self, s, y, rows, size=16.2, num_size=21.6, row_gap=0.18, num_w=0.63, sep=True):
        tx = 0.74 + num_w
        tw = XR - tx
        for i, (num, txt) in enumerate(rows):
            lines = txt if isinstance(txt, list) else [txt]
            th = sum(wrap_lines(l, size, tw) for l in lines) * size * 1.55 / 72
            rh = max(th, num_size * 1.3 / 72)
            self.text(s, 0.74, y - 0.06, num_w + 0.3, 0.45, num, num_size, color=RED, bold=True, ln=1.3, wrap=False)
            self.text(s, tx, y, tw, th + 0.05, lines, size)
            y += rh + row_gap
            if sep and i < len(rows) - 1:
                self.box(s, X0, y - row_gap / 2, CW, 0.01, LINE)
        return y

    def table(self, s, y, cols, header, rows, size=16.8, head_size=14.39, first_bold=True,
              first_color=RED, pad=0.14, row_pad=0.12):
        k = CW / sum(cols)
        cols = [c * k for c in cols]
        xs = [X0]
        for c in cols[:-1]:
            xs.append(xs[-1] + c)
        hh = 0.5
        for x, c, t in zip(xs, cols, header):
            self.box(s, x, y, c - 0.01, hh, CARD)
            self.box(s, x, y + hh - 0.02, c - 0.01, 0.02, LINE)
            self.text(s, x + pad, y + 0.11, c - pad * 2, 0.3, t, head_size, bold=True, wrap=False)
        y += hh
        for r in rows:
            hs = []
            for c, t in zip(cols, r):
                ls = t if isinstance(t, list) else [t]
                hs.append(sum(wrap_lines(l, size, c - pad * 2) for l in ls) * size * 1.5 / 72)
            rh = max(hs) + row_pad * 2
            for j, (x, c, t) in enumerate(zip(xs, cols, r)):
                first = j == 0
                self.text(s, x + pad, y + row_pad, c - pad * 2, hs[j] + 0.05, t, size, ln=1.5,
                          color=first_color if first else INK, bold=first and first_bold)
            y += rh
            for x, c in zip(xs, cols):
                self.box(s, x, y - 0.01, c - 0.01, 0.02, LINE)
        return y

    def chain(self, s, x, y, items, size=14.39, gap=0.42, w_limit=None, arrow=True, h=0.49, last_fill=None):
        w_limit = w_limit or (XR - 0.25)
        cx, cy = x, y
        for i, it in enumerate(items):
            w = text_w(it, size) + 0.34
            if cx + w > w_limit and cx > x:
                cx, cy = x + (0.26 if arrow else 0), cy + h + 0.12
                if arrow:
                    self.text(s, x - 0.02, cy + 0.08, 0.3, 0.3, '→', size, color=DRED, bold=True, wrap=False, check=False)
            special = last_fill and i == len(items) - 1
            self.box(s, cx, cy, w, h, last_fill if special else CARD, rounded=True, adj=0.1, line=None if special else GREEN)
            self.text(s, cx + 0.17, cy + (h - size * 1.55 / 72) / 2 + 0.01, w, 0.4, it, size,
                      color='FFFFFF' if special else INK, bold=True, wrap=False)
            cx += w
            if arrow and i < len(items) - 1:
                self.text(s, cx + 0.1, cy + (h - size * 1.55 / 72) / 2 + 0.01, 0.3, 0.4, '→', size,
                          color=DRED, bold=True, wrap=False, check=False)
                cx += gap
            else:
                cx += 0.15
        return cy + h

    def section(self, s, part, when, chip2, title_lines, sub):
        w = self.chip(s, X0, 1.62, part)
        self.text(s, X0 + w + 0.12, 1.65, 4, 0.4, when, 14.39, color=DARK_MUTED, bold=True, wrap=False)
        self.chip(s, X0, 2.09, chip2, fill=SUN, color=DARK, size=13.2, h=0.36)
        h = len(title_lines) * 62.4 * 1.06 / 72
        self.text(s, 0.74, 2.6, 9.5, h + 0.1, title_lines, 62.4, color='FFFFFF', bold=True, ln=1.06, wrap=False)
        self.text(s, 0.74, 2.6 + h + 0.2, 9.5, 0.6, sub, 27.6, color=SUN, bold=True, ln=1.2, wrap=False)
