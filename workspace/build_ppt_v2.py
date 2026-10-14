# -*- coding: utf-8 -*-
"""躺平与内卷——青年学生的为与不为（精修版 PPT 生成）。"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------- 主题色 ----------------
RED        = RGBColor(0xB0, 0x2E, 0x2E)   # 主红
RED_DEEP   = RGBColor(0x7E, 0x1A, 0x1A)   # 深红（渐变深端）
RED_SOFT   = RGBColor(0xC8, 0x4B, 0x4B)   # 亮红（渐变亮端）
RED_DARK   = RGBColor(0x6E, 0x16, 0x18)   # 标题深红
GOLD       = RGBColor(0xC9, 0x9A, 0x2E)   # 金
GOLD_SOFT  = RGBColor(0xE3, 0xC6, 0x7D)   # 浅金
INK        = RGBColor(0x2A, 0x2A, 0x2E)   # 正文
GREY       = RGBColor(0x76, 0x74, 0x70)   # 次级文字
CREAM      = RGBColor(0xFB, 0xF7, 0xEF)   # 米白底
CARD       = RGBColor(0xFF, 0xFF, 0xFF)   # 卡片白
GREEN      = RGBColor(0x2F, 0x7D, 0x5B)   # 「利」绿
GREEN_BG   = RGBColor(0xEC, 0xF4, 0xEF)   # 绿浅底
RED_BAD    = RGBColor(0xB0, 0x2E, 0x2E)   # 「弊」红
RED_BAD_BG = RGBColor(0xF9, 0xEB, 0xEB)   # 红浅底

FONT = "微软雅黑"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]

EMU_IN = 914400.0


# ================= 基础工具 =================
def set_run(run, text, size, bold=False, color=INK, font=FONT, spacing=None):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', font)
    if spacing is not None:
        rPr.set('spc', str(int(spacing * 100)))


def add_textbox(slide, x, y, w, h, anchor=None):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    if anchor is not None:
        tf.vertical_anchor = anchor
    return tb, tf


def no_line(shape):
    shape.line.fill.background()


def fill_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def solid_fill(shape, rgb, alpha_pct=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    if alpha_pct is not None and alpha_pct < 100:
        spPr = shape._element.spPr
        solidFill = spPr.find(qn('a:solidFill'))
        if solidFill is not None:
            srgbClr = solidFill.find(qn('a:srgbClr'))
            if srgbClr is not None:
                for a in srgbClr.findall(qn('a:alpha')):
                    srgbClr.remove(a)
                a = srgbClr.makeelement(qn('a:alpha'), {'val': str(int(alpha_pct * 1000))})
                srgbClr.append(a)


def gradient_fill(shape, c1, c2, angle=135.0):
    shape.fill.gradient()
    stops = shape.fill.gradient_stops
    stops[0].color.rgb = c1
    stops[0].position = 0.0
    stops[1].color.rgb = c2
    stops[1].position = 1.0
    try:
        shape.fill.gradient_angle = angle
    except Exception:
        pass


def soft_shadow(shape, blur=0.09, dist=0.035, alpha_pct=22, angle_deg=90):
    spPr = shape._element.spPr
    for el in spPr.findall(qn('a:effectLst')):
        spPr.remove(el)
    effectLst = spPr.makeelement(qn('a:effectLst'), {})
    outer = spPr.makeelement(qn('a:outerShdw'), {
        'blurRad': str(int(blur * EMU_IN)),
        'dist': str(int(dist * EMU_IN)),
        'dir': str(int(angle_deg * 60000)),
        'rotWithShape': '0',
    })
    clr = spPr.makeelement(qn('a:srgbClr'), {'val': '000000'})
    a = spPr.makeelement(qn('a:alpha'), {'val': str(int(alpha_pct * 1000))})
    clr.append(a)
    outer.append(clr)
    effectLst.append(outer)
    spPr.append(effectLst)


def shape(slide, kind, x, y, w, h, fill=None, alpha=None, line=None, line_w=None):
    sp = slide.shapes.add_shape(kind, x, y, w, h)
    if fill is not None:
        solid_fill(sp, fill, alpha)
    else:
        sp.fill.background()
    if line is not None:
        sp.line.color.rgb = line
        sp.line.width = Pt(line_w or 1)
    else:
        no_line(sp)
    sp.shadow.inherit = False
    return sp


def round_card(slide, x, y, w, h, fill=CARD, radius=0.055, shadow=True, line=None):
    sp = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line)
    try:
        sp.adjustments[0] = radius
    except Exception:
        pass
    if shadow:
        soft_shadow(sp)
    return sp


def text_in_shape(sp, text, size, color, bold=False, spacing=None, anchor=MSO_ANCHOR.MIDDLE):
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), text, size, bold, color, spacing=spacing)
    return sp


# ---------------- 页头 ----------------
def content_header(slide, title, kicker, page_no, total=12):
    # 右上角装饰大圆（浅金，半透明）
    shape(slide, MSO_SHAPE.OVAL, Inches(10.7), Inches(-1.9), Inches(4.6), Inches(4.6),
          fill=GOLD, alpha=7)
    # 左下角装饰小圆（浅红，半透明）
    shape(slide, MSO_SHAPE.OVAL, Inches(-0.9), Inches(6.3), Inches(2.6), Inches(2.6),
          fill=RED, alpha=5)

    # 眉题胶囊
    pill_w = Inches(0.24 + len(kicker) * 0.115)
    pill = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.52), pill_w, Inches(0.4),
                 fill=None, line=GOLD, line_w=1.2)
    try:
        pill.adjustments[0] = 0.5
    except Exception:
        pass
    text_in_shape(pill, kicker, 11.5, GOLD, True, spacing=1.6)

    # 主标题
    _, ttf = add_textbox(slide, Inches(0.88), Inches(1.02), Inches(11.6), Inches(0.8))
    set_run(ttf.paragraphs[0].add_run(), title, 28, True, RED_DARK)

    # 金色装饰线 + 红色菱形
    shape(slide, MSO_SHAPE.DIAMOND, Inches(0.92), Inches(1.86), Inches(0.16), Inches(0.16), fill=RED)
    shape(slide, MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.9), Inches(1.9), Inches(0.035), fill=GOLD)

    # 页码胶囊（右下）
    chip = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.35), Inches(6.88), Inches(0.66), Inches(0.4),
                 fill=RED, alpha=None)
    try:
        chip.adjustments[0] = 0.5
    except Exception:
        pass
    text_in_shape(chip, f"{page_no:02d}/{total:02d}", 11, RGBColor(0xFF, 0xFF, 0xFF), True)


def banner_note(slide, y, text_runs, bg=RED_BAD_BG, accent=RED, x=Inches(0.9), w=Inches(11.53)):
    card = round_card(slide, x, y, w, Inches(0.95), fill=bg, radius=0.10, shadow=False)
    shape(slide, MSO_SHAPE.RECTANGLE, x, y, Inches(0.12), Inches(0.95), fill=accent)
    _, tf = add_textbox(slide, x + Inches(0.42), y + Inches(0.1), w - Inches(0.7), Inches(0.75),
                        anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]
    for txt, sz, bold, col in text_runs:
        set_run(p.add_run(), txt, sz, bold, col)
    return card


def bullet_row(slide, x, y, w, glyph, glyph_color, text, size=14.5):
    shape(slide, MSO_SHAPE.OVAL, x, y + Inches(0.05), Inches(0.26), Inches(0.26), fill=glyph_color)
    shape(slide, MSO_SHAPE.OVAL, x + Inches(0.05), y + Inches(0.1), Inches(0.16), Inches(0.16),
          fill=RGBColor(0xFF, 0xFF, 0xFF), alpha=28)
    _, tf = add_textbox(slide, x + Inches(0.42), y, w - Inches(0.42), Inches(0.5))
    set_run(tf.paragraphs[0].add_run(), text, size, False, INK)


# ================= 第 1 页：封面 =================
s = prs.slides.add_slide(BLANK)
# 渐变背景
bg = shape(s, MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H, fill=RED)
gradient_fill(bg, RED_SOFT, RED_DEEP, 120.0)
# 顶部 / 底部金线
shape(s, MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.14), fill=GOLD)
shape(s, MSO_SHAPE.RECTANGLE, 0, Inches(7.36), SLIDE_W, Inches(0.14), fill=GOLD)
# 装饰半透明大圆
shape(s, MSO_SHAPE.OVAL, Inches(9.4), Inches(-2.6), Inches(6.2), Inches(6.2), fill=GOLD, alpha=10)
shape(s, MSO_SHAPE.OVAL, Inches(9.9), Inches(-2.1), Inches(5.2), Inches(5.2), fill=GOLD, alpha=8)
shape(s, MSO_SHAPE.OVAL, Inches(-2.2), Inches(5.3), Inches(5.0), Inches(5.0), fill=RED_DEEP, alpha=60)
# 课程标签
_, ltf = add_textbox(s, Inches(1.15), Inches(1.15), Inches(8), Inches(0.5))
set_run(ltf.paragraphs[0].add_run(), "思想政治课 · 主题讨论", 15, True, GOLD_SOFT, spacing=2.0)
# 主标题
_, ttf = add_textbox(s, Inches(1.05), Inches(1.95), Inches(11.2), Inches(1.7))
p = ttf.paragraphs[0]
set_run(p.add_run(), "躺平", 62, True, RGBColor(0xFF, 0xFF, 0xFF))
set_run(p.add_run(), "  与  ", 40, True, GOLD_SOFT)
set_run(p.add_run(), "内卷", 62, True, RGBColor(0xFF, 0xFF, 0xFF))
# 副标题
_, stf = add_textbox(s, Inches(1.1), Inches(3.55), Inches(11.3), Inches(0.8))
set_run(stf.paragraphs[0].add_run(), "—— 青年学生的「为」与「不为」", 27, True, GOLD_SOFT, spacing=1.0)
# 金色装饰线
shape(s, MSO_SHAPE.RECTANGLE, Inches(1.12), Inches(4.75), Inches(2.6), Inches(0.045), fill=GOLD)
# 引导语
_, gtf = add_textbox(s, Inches(1.12), Inches(5.05), Inches(11.0), Inches(1.4))
gp = gtf.paragraphs[0]
set_run(gp.add_run(), "拒绝无效内卷  ·  不做消极躺平", 21, False, RGBColor(0xFF, 0xFF, 0xFF), spacing=1.0)
gp2 = gtf.add_paragraph()
gp2.space_before = Pt(12)
set_run(gp2.add_run(), "在可为之事上全力以赴，在不可为之事上保持清醒", 14.5, False, GOLD_SOFT, spacing=0.6)


# ================= 第 2 页：目录 =================
s = prs.slides.add_slide(BLANK)
fill_bg(s, CREAM)
content_header(s, "议题导航", "CONTENTS", 2)

items = [
    ("01", "现象观察", "什么是「内卷」？什么是「躺平」？"),
    ("02", "追根溯源", "两种社会心态为何在青年中流行？"),
    ("03", "辩证审视", "内卷与躺平的利与弊、误区何在？"),
    ("04", "青年之「为」", "应当做什么——该担当、该奋斗之处"),
    ("05", "青年之「不为」", "不应做什么——该拒绝、该清醒之处"),
    ("06", "总结寄语", "在奋斗与从容之间，找到自己的人生节奏"),
]
# 竖线
shape(s, MSO_SHAPE.RECTANGLE, Inches(1.34), Inches(1.95), Inches(0.02), Inches(4.55), fill=GOLD, alpha=45)
y = Inches(1.85)
for i, (num, t, d) in enumerate(items):
    cx = Inches(1.35)
    cy = y + Inches(0.3)
    # 连接点圆
    dot = shape(s, MSO_SHAPE.OVAL, cx - Inches(0.09), cy - Inches(0.09), Inches(0.18), Inches(0.18), fill=GOLD)
    # 编号圆
    badge = shape(s, MSO_SHAPE.OVAL, Inches(1.05), y, Inches(0.6), Inches(0.6), fill=RED)
    text_in_shape(badge, num, 14, RGBColor(0xFF, 0xFF, 0xFF), True)
    # 标题 + 描述
    _, ttf = add_textbox(s, Inches(1.95), y - Inches(0.03), Inches(10.3), Inches(0.85))
    set_run(ttf.paragraphs[0].add_run(), t, 17.5, True, INK)
    dp = ttf.add_paragraph()
    dp.space_before = Pt(2)
    set_run(dp.add_run(), d, 12.5, False, GREY)
    y += Inches(0.86)


# ================= 现象页（3、4） =================
def phenomenon_slide(page_no, title, kicker, concept, shows, judgement):
    s = prs.slides.add_slide(BLANK)
    fill_bg(s, CREAM)
    content_header(s, title, kicker, page_no)

    # 概念卡片
    card = round_card(s, Inches(0.9), Inches(2.15), Inches(11.53), Inches(1.15), radius=0.09)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(2.15), Inches(0.14), Inches(1.15), fill=GOLD)
    _, ctf = add_textbox(s, Inches(1.32), Inches(2.28), Inches(10.85), Inches(0.95), anchor=MSO_ANCHOR.MIDDLE)
    cp = ctf.paragraphs[0]
    set_run(cp.add_run(), "概念解读   ", 14.5, True, RED)
    set_run(cp.add_run(), concept, 14.5, False, INK)

    # 常见表现
    _, htf = add_textbox(s, Inches(0.9), Inches(3.5), Inches(6), Inches(0.5))
    set_run(htf.paragraphs[0].add_run(), "常见表现", 16, True, RED_DARK, spacing=1.0)
    y = Inches(4.0)
    for i, b in enumerate(shows):
        bullet_row(s, Inches(1.05), y, Inches(11.0), "•", GOLD, b)
        y += Inches(0.5)

    # 核心判断
    banner_note(s, Inches(6.0), [
        ("核心判断  ", 14.5, True, RED),
        (judgement, 14.5, False, INK),
    ])


phenomenon_slide(
    3, "现象观察 · 什么是「内卷」", "PHENOMENON 01",
    "「内卷」原指社会或组织发展到一定阶段后，无法向外拓展，只能在内部展开过度、低效的重复竞争的状态。",
    ["加班熬夜、无效内耗，比拼谁更“辛苦”",
     "同质化竞争，千军万马挤同一座独木桥",
     "“剧场效应”：前排站起，后排被迫站起"],
    "竞争本身并不可怕，可怕的是无意义、低效率、耗竭身心的“内耗式竞争”。",
)

phenomenon_slide(
    4, "现象观察 · 什么是「躺平」", "PHENOMENON 02",
    "「躺平」指部分年轻人面对压力，选择放弃过度竞争、主动降低欲望，追求低消耗、低期待生活的一种态度。",
    ["降低物质消费，追求“够用就好”",
     "拒绝无意义加班，主张工作与生活平衡",
     "佛系心态，对结果看得更淡、更从容"],
    "适度放松是自我调节，彻底放弃是逃避；关键在于“度”。",
)


# ================= 原因页（5、6） =================
def reason_slide(page_no, title, kicker, reasons, summary, accent_top=RED):
    s = prs.slides.add_slide(BLANK)
    fill_bg(s, CREAM)
    content_header(s, title, kicker, page_no)
    pos = [(0.9, 2.15), (6.85, 2.15), (0.9, 4.35), (6.85, 4.35)]
    glyphs = ["①", "②", "③", "④"]
    for (x, y), (t, d), g in zip(pos, reasons, glyphs):
        card = round_card(s, Inches(x), Inches(y), Inches(5.58), Inches(2.0), radius=0.08)
        # 顶部渐变条
        bar = shape(s, MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(5.58), Inches(0.12), fill=accent_top)
        # 序号
        shape(s, MSO_SHAPE.OVAL, Inches(x + 0.3), Inches(y + 0.34), Inches(0.52), Inches(0.52), fill=accent_top)
        _, ntf = add_textbox(s, Inches(x + 0.3), Inches(y + 0.36), Inches(0.52), Inches(0.48))
        np_ = ntf.paragraphs[0]
        np_.alignment = PP_ALIGN.CENTER
        set_run(np_.add_run(), g, 13, True, RGBColor(0xFF, 0xFF, 0xFF))
        # 标题 + 描述
        _, ttf = add_textbox(s, Inches(x + 0.98), Inches(y + 0.36), Inches(4.35), Inches(1.5))
        set_run(ttf.paragraphs[0].add_run(), t, 16.5, True, RED_DARK)
        dp = ttf.add_paragraph()
        dp.space_before = Pt(5)
        set_run(dp.add_run(), d, 12.5, False, GREY)
    banner_note(s, Inches(6.35), [
        ("小结  ", 13.5, True, GOLD),
        (summary, 13.5, False, INK),
    ])


reason_slide(
    5, "追根溯源 · 内卷为何流行", "REASON 01", [
        ("资源有限", "优质岗位、升学机会相对稀缺，需求远超供给，形成竞争压力。"),
        ("标准单一", "评价体系趋于同质化，“分数”“排名”成为衡量价值的主要尺度。"),
        ("焦虑传导", "社会、家庭、同辈的焦虑相互放大，个体被迫卷入竞争漩涡。"),
        ("发展约束", "特定发展阶段内，增量空间收窄，竞争转向存量“内耗”。"),
    ],
    "内卷不是某一个人的问题，而是发展阶段、评价机制与群体心理共同作用的结果。",
    RED,
)

reason_slide(
    6, "追根溯源 · 躺平为何出现", "REASON 02", [
        ("对内卷的逆反", "当竞争变得无意义且过度时，部分人选择主动退出，以“躺”表达不满。"),
        ("高压下的自保", "长期高压透支身心，躺平成为一种心理上的自我保护与缓冲。"),
        ("反思单一成功", "对“唯成功论”的质疑，促使人们重新思考人生价值的多元可能。"),
        ("时代提供选择", "物质基础改善、价值取向多元，让“按自己的节奏生活”成为可能。"),
    ],
    "躺平既是社会心态的折射，也包含对人生意义与生活方式的一次认真追问。",
    GOLD,
)


# ================= 辩证页（7、8） =================
def dialectic_slide(page_no, title, kicker, goods, bads, conclusion):
    s = prs.slides.add_slide(BLANK)
    fill_bg(s, CREAM)
    content_header(s, title, kicker, page_no)

    # 左：利
    card = round_card(s, Inches(0.9), Inches(2.1), Inches(5.6), Inches(4.05), fill=GREEN_BG, radius=0.06, shadow=False)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(2.1), Inches(5.6), Inches(0.12), fill=GREEN)
    _, htf = add_textbox(s, Inches(1.2), Inches(2.34), Inches(5.0), Inches(0.5))
    set_run(htf.paragraphs[0].add_run(), "积极一面（利）", 17, True, GREEN, spacing=1.0)
    y = Inches(3.0)
    for g in goods:
        bullet_row(s, Inches(1.2), y, Inches(4.9), "✓", GREEN, g, 13.5)
        y += Inches(0.72)

    # 右：弊
    card = round_card(s, Inches(6.85), Inches(2.1), Inches(5.6), Inches(4.05), fill=RED_BAD_BG, radius=0.06, shadow=False)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(6.85), Inches(2.1), Inches(5.6), Inches(0.12), fill=RED_BAD)
    _, htf2 = add_textbox(s, Inches(7.15), Inches(2.34), Inches(5.0), Inches(0.5))
    set_run(htf2.paragraphs[0].add_run(), "消极一面（弊）", 17, True, RED_BAD, spacing=1.0)
    y = Inches(3.0)
    for b in bads:
        bullet_row(s, Inches(7.15), y, Inches(4.9), "✗", RED_BAD, b, 13.5)
        y += Inches(0.72)

    banner_note(s, Inches(6.35), [
        ("结论  ", 13.5, True, GOLD),
        (conclusion, 13.5, False, INK),
    ])


dialectic_slide(
    7, "辩证审视 · 内卷的利与弊", "DIALECTIC 01",
    ["适度竞争能够激发潜能、催人奋进",
     "推动个人成长与集体事业不断进步",
     "让努力与才华有更多被看见的机会"],
    ["过度内耗透支身心，侵蚀健康与生活",
     "挤占创造空间，陷入低水平重复",
     "催生焦虑攀比，扭曲奋斗的意义"],
    "我们要警惕的不是“努力”，而是“无效的内耗”。",
)

dialectic_slide(
    8, "辩证审视 · 躺平的利与弊", "DIALECTIC 02",
    ["提供喘息空间，及时调整身心状态",
     "反思人生意义，拒绝盲目跟风攀比",
     "倡导生活平衡，重视质量与幸福感"],
    ["彻底躺平丧失斗志，虚度大好青春",
     "以“佛系”之名逃避责任与成长",
     "放弃奋斗，最终失去选择的能力"],
    "躺平可以“歇脚”，但不能“就地长眠”；休息是为了更好地出发。",
)


# ================= 为 / 不为页（9、10） =================
def action_slide(page_no, title, kicker, items, accent, glyphs):
    s = prs.slides.add_slide(BLANK)
    fill_bg(s, CREAM)
    content_header(s, title, kicker, page_no)
    pos = [(0.9, 2.1), (6.85, 2.1), (0.9, 4.3), (6.85, 4.3)]
    for (x, y), (t, d), g in zip(pos, items, glyphs):
        card = round_card(s, Inches(x), Inches(y), Inches(5.58), Inches(2.05), radius=0.08)
        # 左侧色条
        shape(s, MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.12), Inches(2.05), fill=accent)
        # 圆形图标
        shape(s, MSO_SHAPE.OVAL, Inches(x + 0.42), Inches(y + 0.32), Inches(0.56), Inches(0.56), fill=accent)
        _, ntf = add_textbox(s, Inches(x + 0.42), Inches(y + 0.33), Inches(0.56), Inches(0.54))
        np_ = ntf.paragraphs[0]
        np_.alignment = PP_ALIGN.CENTER
        set_run(np_.add_run(), g, 14, True, RGBColor(0xFF, 0xFF, 0xFF))
        # 标题 + 描述
        _, ttf = add_textbox(s, Inches(x + 1.16), Inches(y + 0.32), Inches(4.2), Inches(1.6))
        set_run(ttf.paragraphs[0].add_run(), t, 16.5, True, RED_DARK)
        dp = ttf.add_paragraph()
        dp.space_before = Pt(5)
        set_run(dp.add_run(), d, 12.5, False, GREY)


action_slide(
    9, "青年之「为」· 应当做什么", "WHAT TO DO", [
        ("为理想而奋斗", "立大志、明大德，把个人小我融入国家大我，做有志向的青年。"),
        ("为成长而学习", "打牢知识根基、练就过硬本领，做有本领、能担当的青年。"),
        ("为担当而奉献", "在服务他人、奉献社会中实现价值，做有责任感的青年。"),
        ("为健康而自律", "强健体魄、磨炼意志、张弛有度，做有韧性的青年。"),
    ], RED, ["01", "02", "03", "04"],
)

action_slide(
    10, "青年之「不为」· 不应做什么", "WHAT NOT TO DO", [
        ("不为无效内卷", "拒绝盲目跟风、虚耗时日的低效竞争，把力气用在刀刃上。"),
        ("不为消极躺平", "拒绝逃避责任、自暴自弃，不做“精致的利己”与“消极的看客”。"),
        ("不为攀比焦虑", "拒绝被单一标准绑架，不被分数、排名、面子牵着走。"),
        ("不为急功近利", "拒绝投机取巧、走捷径，脚踏实地走好每一步。"),
    ], GOLD, ["01", "02", "03", "04"],
)


# ================= 第 11 页：正确选择 =================
s = prs.slides.add_slide(BLANK)
fill_bg(s, CREAM)
content_header(s, "正确选择 · 在奋斗与从容间找到平衡", "THE RIGHT PATH", 11)

points = [
    "奋斗是青春最亮丽的底色——人生因奋斗而精彩。",
    "拒绝无效内卷，追求高效成长——让努力更有意义。",
    "避免消极躺平，保持向上姿态——让心态始终在线。",
    "找到自己的节奏，实现有意义的人生——不盲从、不虚度。",
]
y = Inches(2.05)
for i, ptext in enumerate(points):
    # 序号圆
    circle = shape(s, MSO_SHAPE.OVAL, Inches(1.0), y, Inches(0.55), Inches(0.55), fill=RED)
    text_in_shape(circle, str(i + 1), 15, RGBColor(0xFF, 0xFF, 0xFF), True)
    # 连接线
    if i < len(points) - 1:
        shape(s, MSO_SHAPE.RECTANGLE, Inches(1.26), y + Inches(0.55), Inches(0.03), Inches(0.28), fill=GOLD, alpha=60)
    _, ttf = add_textbox(s, Inches(1.85), y - Inches(0.02), Inches(10.4), Inches(0.7))
    set_run(ttf.paragraphs[0].add_run(), ptext, 15, False, INK)
    y += Inches(0.83)

# 金句卡
card = round_card(s, Inches(0.9), Inches(5.6), Inches(11.53), Inches(1.15), radius=0.09)
shape(s, MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(5.6), Inches(0.14), Inches(1.15), fill=GOLD)
_, qtf = add_textbox(s, Inches(1.32), Inches(5.72), Inches(10.7), Inches(0.9), anchor=MSO_ANCHOR.MIDDLE)
qp = qtf.paragraphs[0]
set_run(qp.add_run(), "青春由磨砺而出彩，人生因奋斗而升华。", 20, True, RED_DARK, spacing=1.0)


# ================= 第 12 页：结语 =================
s = prs.slides.add_slide(BLANK)
bg = shape(s, MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H, fill=RED)
gradient_fill(bg, RED_SOFT, RED_DEEP, 120.0)
shape(s, MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.14), fill=GOLD)
shape(s, MSO_SHAPE.RECTANGLE, 0, Inches(7.36), SLIDE_W, Inches(0.14), fill=GOLD)
shape(s, MSO_SHAPE.OVAL, Inches(9.6), Inches(-2.6), Inches(6.0), Inches(6.0), fill=GOLD, alpha=10)
shape(s, MSO_SHAPE.OVAL, Inches(-2.0), Inches(5.4), Inches(4.6), Inches(4.6), fill=RED_DEEP, alpha=60)

_, htf = add_textbox(s, Inches(1.1), Inches(1.1), Inches(11.0), Inches(0.6))
set_run(htf.paragraphs[0].add_run(), "结语 · 与青年共勉", 22, True, GOLD_SOFT, spacing=2.0)
shape(s, MSO_SHAPE.RECTANGLE, Inches(1.12), Inches(1.85), Inches(1.8), Inches(0.045), fill=GOLD)

_, btf = add_textbox(s, Inches(1.1), Inches(2.5), Inches(11.2), Inches(1.9))
lines = [
    "内卷不可怕，可怕的是迷失方向的盲目消耗；",
    "躺平不可取，可贵的是张弛有度的清醒选择。",
]
for i, ln in enumerate(lines):
    p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
    p.space_after = Pt(14)
    set_run(p.add_run(), ln, 21, False, RGBColor(0xFF, 0xFF, 0xFF), spacing=0.5)

_, gtf = add_textbox(s, Inches(1.1), Inches(4.55), Inches(11.2), Inches(1.7))
gp = gtf.paragraphs[0]
gp.alignment = PP_ALIGN.CENTER
set_run(gp.add_run(), "愿每一位青年：", 18, True, GOLD_SOFT, spacing=2.0)
gp2 = gtf.add_paragraph()
gp2.alignment = PP_ALIGN.CENTER
gp2.space_before = Pt(12)
set_run(gp2.add_run(), "在可为之事上全力以赴，在不可为之事上保持清醒，", 16, False, RGBColor(0xFF, 0xFF, 0xFF), spacing=0.5)
gp3 = gtf.add_paragraph()
gp3.alignment = PP_ALIGN.CENTER
gp3.space_before = Pt(6)
set_run(gp3.add_run(), "拒绝无效内卷，不做消极躺平，书写无愧于时代的青春篇章。", 16, False, RGBColor(0xFF, 0xFF, 0xFF), spacing=0.5)

# 讨论环节胶囊
chip = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.17), Inches(6.35), Inches(7.0), Inches(0.62),
             fill=None, line=GOLD_SOFT, line_w=1.2)
try:
    chip.adjustments[0] = 0.5
except Exception:
    pass
text_in_shape(chip, "课堂讨论：你如何看待身边的「内卷」与「躺平」？", 14, GOLD_SOFT, True, spacing=0.5)


out = "躺平与内卷——青年学生的为与不为.pptx"
prs.save(out)
print("saved:", out)
