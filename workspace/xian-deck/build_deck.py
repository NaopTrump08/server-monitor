# -*- coding: utf-8 -*-
"""Build the Xi'an group-presentation deck.

7 pages: a cover, then exactly one page for each of the five required points
(introduction / facts / opinion(+) / opinion(-) / summary), then a thank-you.
All-English slides with English speaker notes. Facts are the verified ones from
the research pass; unverified figures are avoided.
"""
import os
import json
from pptx.util import Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from deckkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Xi'an - An Interesting Place.pptx")

BODY = 2.28          # content top when the header has a subtitle
LIGHT = (232, 222, 205)
LIGHT_2 = (196, 187, 172)

PARTS = [
    ("01", "Introduction"),
    ("02", "Facts"),
    ("03", "Opinion (positives)"),
    ("04", "Opinion (negatives)"),
    ("05", "Summary"),
]

_N = [0]


def bump():
    """Next slide number in build order. The cover counts but prints nothing."""
    _N[0] += 1
    return _N[0]


def five_part_strip(sl, y, dark=True, x=MARGIN, size=8.5, center=False):
    fg = MUTED_D if dark else MUTED
    acc = GOLD if dark else CLAY
    tf = textbox(sl, x, y, SW if center else CW, 0.30)
    runs = []
    for i, (num, label) in enumerate(PARTS):
        if i:
            runs.append(("     \u00b7     ", {"color": acc}))
        runs.append((num + "  ", {"color": acc, "font": SERIF, "bold": True, "size": size + 1.5}))
        runs.append((label.upper(), {"color": fg}))
    para(tf, runs, size=size, font=SANS, spc=1.8, line=1.0, first=True,
         align=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT)


# =====================================================================
# 01  cover
# =====================================================================
def s01_cover(prs):
    bump()
    sl = slide(prs)
    bg(sl, "bg_ink.jpg")

    wm = textbox(sl, 8.55, 1.05, 5.4, 4.4)
    para(wm, "\u897f\u5b89", size=210, font=CJK, bold=True, color=(40, 37, 49),
         line=0.92, first=True, cjk_font=CJK)
    vline(sl, 0.42, 0.0, SH, (58, 50, 44), lw=1.0)

    eyebrow(sl, "Group presentation  \u00b7  An interesting place", color=GOLD)

    tf = textbox(sl, MARGIN - 0.08, 1.28, 10.4, 1.9)
    para(tf, "XI'AN", size=112, font=SERIF, bold=True, color=PAPER, spc=3.0, line=0.88, first=True)

    tf = textbox(sl, MARGIN, 2.94, 10.4, 0.5)
    para(tf, "\u897f\u5b89   \u00b7   once called Chang'an \u957f\u5b89, \"lasting peace\"",
         size=17, font=SANS, color=GOLD_SOFT, line=1.2, first=True, cjk_font=CJK)

    hairline(sl, MARGIN, 3.50, 1.75, GOLD, lw=1.6)

    tf = textbox(sl, MARGIN, 3.72, 7.8, 1.5)
    para(tf, "Where ancient China still breathes.", size=24, font=SERIF,
         color=(238, 228, 210), line=1.24, first=True)
    para(tf, "3,100 years old  \u00b7  capital of 13 dynasties  \u00b7  home of the Terracotta Army",
         size=12.5, font=SANS, color=MUTED_D, line=1.3, before=6)

    # the city itself, drawn as one faint horizon line of landmarks
    SKY_H = SW * 530.0 / 4200.0
    pic_alpha(sl, "skyline.png", 0, 6.14 + 0.0264 * SKY_H - SKY_H, w=SW, alpha=0.34)

    hairline(sl, MARGIN, 6.16, CW - 0.9, (58, 62, 76), lw=1.0)
    five_part_strip(sl, 6.42, dark=True)
    seal(sl, SW - MARGIN - 0.62, 6.24, size=0.62, chars="\u957f\u5b89")

    notes(sl, "Dear teacher and fellow students, good morning. It is our great honour to "
              "introduce Xi'an, one of the oldest cities in China. It lies in Shaanxi Province, "
              "in the northwest of the country, and thirteen dynasties made it their capital. "
              "You may know it by its older name, Chang'an, which means 'lasting peace'. We will "
              "follow five steps: the general facts, the history, what we liked, what we did not "
              "like, and finally our answer to one question - should you go? Let's begin.")


# =====================================================================
# 02  our plan
# =====================================================================
def s02_plan(prs):
    sl = slide(prs)
    bg(sl, "bg_paper.jpg")
    header(sl, "How we will present it", "Five questions, one city",
           sub="Our group follows the five-part plan: what Xi'an is, how it began, "
               "what we loved, what we did not, and whether it is worth your holiday.")

    rows = [
        ("01", "Introduction and general facts", "Name of the place? Country? Location?"),
        ("02", "Facts", "How old? Who made it? Other events?"),
        ("03", "Opinion (positives)", "Interesting? Beautiful? Why visit?"),
        ("04", "Opinion (negatives)", "Expensive? Too crowded? Problems?"),
        ("05", "Summary", "Good? Go or not?"),
    ]
    y0, step = 2.52, 0.85
    for i, (num, head, q) in enumerate(rows):
        y = y0 + i * step
        hairline(sl, MARGIN, y - 0.20, CW, PAPER_LINE, lw=1.0)
        tf = textbox(sl, MARGIN, y - 0.02, 0.8, 0.5)
        para(tf, num, size=21, font=SERIF, bold=True, color=CLAY, line=1.0, first=True)
        tf = textbox(sl, MARGIN + 0.80, y + 0.02, 4.1, 0.6)
        para(tf, head, size=15, font=SERIF, bold=True, color=INK, line=1.1, first=True)
        tf = textbox(sl, MARGIN + 5.05, y + 0.055, CW - 5.05, 0.5)
        para(tf, q, size=12.5, font=SANS, color=MUTED, line=1.2, first=True)
    hairline(sl, MARGIN, y0 + 4 * step + 0.60, CW, PAPER_LINE, lw=1.0)

    footer(sl, 2)
    notes(sl, "Before we start, here is our plan. We divided the presentation into five parts, "
              "exactly as the task asks. Part one gives the general facts - the name, the country "
              "and the location. Part two covers the history: how old the city is, who built it "
              "and what happened here. Parts three and four are our own opinions, the good points "
              "and the bad points. And part five is our summary - our answer to the question: "
              "is Xi'an worth visiting?")


# =====================================================================
# 03  where is Xi'an
# =====================================================================
def s03_where(prs):
    sl = slide(prs)
    bg(sl, "bg_paper.jpg")
    header(sl, "01  \u00b7  Introduction and general facts", "Where in the world is Xi'an?",
           sub="An ancient city in the northwest of China, and the best-known starting point "
               "of the Silk Road.")

    blocks = [
        ("Name", "Xi'an  \u897f\u5b89  \u2014  \"western peace\"",
         "For a thousand years it was called Chang'an \u957f\u5b89, \"lasting peace\". "
         "The name changed in the Ming dynasty."),
        ("Country", "China  \u00b7  Shaanxi Province  \u00b7  Northwest China",
         "Also called the \"Thirteen-Dynasty Ancient Capital\" \u2014 with Athens, Rome and "
         "Cairo, one of the world's four great ancient capitals."),
        ("Location", "34.3\u00b0N, 108.9\u00b0E  \u00b7  the Guanzhong Plain",
         "Far from the sea, in a river valley surrounded by mountains \u2014 the door between "
         "the plains and the west."),
    ]
    for i, (label, value, note) in enumerate(blocks):
        y = 2.28 + i * 1.28
        tf = textbox(sl, MARGIN, y, 5.4, 0.26)
        para(tf, label.upper(), size=9.5, font=SANSB, color=CLAY, spc=2.4, line=1.0, first=True)
        tf = textbox(sl, MARGIN, y + 0.28, 5.4, 0.32)
        para(tf, value, size=15, font=SERIF, bold=True, color=INK, line=1.1,
             first=True, cjk_font=CJK)
        tf = textbox(sl, MARGIN, y + 0.66, 5.25, 0.60)
        para(tf, note, size=11, font=SANS, color=MUTED, line=1.26, first=True)

    hairline(sl, MARGIN, 6.06, 5.40, PAPER_LINE, lw=1.0)
    tf = textbox(sl, MARGIN, 6.22, 5.40, 0.34)
    para(tf, [("13.2 million", {"font": SERIF, "bold": True, "size": 13, "color": CLAY}),
              (" people   \u00b7   ", {"color": MUTED}),
              ("4 h 10", {"font": SERIF, "bold": True, "size": 13, "color": CLAY}),
              (" from Beijing by train   \u00b7   ", {"color": MUTED}),
              ("63", {"font": SERIF, "bold": True, "size": 13, "color": CLAY}),
              (" universities", {"color": MUTED})],
         size=11.5, font=SANS, color=MUTED, line=1.2, first=True)

    card(sl, 6.60, 2.28, 5.91, 4.30)
    pic(sl, "art_map.png", 6.88, 2.58, w=5.35)
    tf = textbox(sl, 6.88, 6.02, 5.35, 0.46)
    para(tf, "Xi'an sits in the centre of China's northwest \u2014 where the plains meet "
             "the deserts of the west.", size=11, font=SANS, color=MUTED, line=1.3, first=True)

    footer(sl, bump())
    notes(sl, "Part one: the general facts. The name Xi'an means 'western peace' - it was "
              "changed from Chang'an in the Ming dynasty. On the map you can see where the city "
              "sits: in a river valley in the northwest, surrounded by mountains, which is why "
              "so many dynasties chose it. The Tang, the most famous of them all, ruled from "
              "here. Today about thirteen million people live in Xi'an, and it is only four "
              "hours from Beijing by high-speed train.")


# =====================================================================
# 04  by the numbers
# =====================================================================
def s04_numbers(prs):
    sl = slide(prs)
    bg(sl, "bg_paper.jpg")
    header(sl, "01  \u00b7  Introduction and general facts", "Xi'an by the numbers",
           sub="Six figures that explain the city faster than a history book can.")

    stats = [
        ("3,100", "years old", "People have lived here since the Western Zhou \u2014 one of China's oldest cities."),
        ("13", "dynasties", "Zhou to Tang: 1,129 years as the capital of China."),
        ("8,000+", "soldiers", "The army buried with Qin Shi Huang \u2014 found in 1974."),
        ("13.74", "kilometres", "The Ming city wall: the longest and best kept in China."),
        ("1.7", "million objects", "In the Shaanxi History Museum \u2014 and it is free to enter."),
        ("13.2", "million people", "Living in Xi'an today \u2014 one of China's biggest cities."),
    ]
    cw, gap = (CW - 2 * 0.30) / 3.0, 0.30
    for i, (num, label, ctx) in enumerate(stats):
        r, c = divmod(i, 3)
        x = MARGIN + c * (cw + gap)
        y = 2.30 + r * 2.12
        card(sl, x, y, cw, 1.95)
        tf = textbox(sl, x + 0.32, y + 0.20, cw - 0.64, 0.70)
        para(tf, num, size=36, font=SERIF, bold=True, color=CLAY, line=1.0, first=True)
        hairline(sl, x + 0.32, y + 0.92, 0.52, GOLD, lw=1.4)
        tf = textbox(sl, x + 0.32, y + 1.04, cw - 0.64, 0.24)
        para(tf, label.upper(), size=9, font=SANSB, color=MUTED, spc=1.8, line=1.0, first=True)
        tf = textbox(sl, x + 0.32, y + 1.30, cw - 0.64, 0.55)
        para(tf, ctx, size=11, font=SANS, color=MUTED, line=1.24, first=True)

    footer(sl, 4)
    notes(sl, "Here is Xi'an in six numbers. Three thousand one hundred years old. Capital of "
              "thirteen dynasties, for one thousand one hundred and twenty-nine years in total - "
              "longer than any other city in China. Eight thousand soldiers were buried with "
              "the First Emperor. The city wall is almost fourteen kilometres around. The Shaanxi "
              "History Museum holds one point seven million objects and is free to enter. And "
              "thirteen million people live here today.")


# =====================================================================
# 05  timeline
# =====================================================================
def s05_timeline(prs):
    sl = slide(prs)
    bg(sl, "bg_paper.jpg")
    header(sl, "02  \u00b7  Facts", "How old is Xi'an?",
           sub="Five moments that turned a small river town into the capital of China.")

    nodes = [
        ("221 BC", "Qin unites China",
         "Qin Shi Huang ends the wars between the states and rules from Xianyang, beside Xi'an."),
        ("202 BC", "The Han dynasty",
         "Chang'an becomes the capital and the eastern end of the Silk Road."),
        ("AD 618\u2013907", "The Tang golden age",
         "Chang'an is one of the largest cities in the world, and the most international."),
        ("14th century", "The Ming wall",
         "The wall you can still walk and cycle on today is built in brick and stone."),
        ("1974", "The army found",
         "Farmers digging a well near Lintong find the Terracotta Army."),
    ]
    y_line = 4.15
    x0, x1 = MARGIN + 1.10, SW - MARGIN - 1.10
    step = (x1 - x0) / (len(nodes) - 1.0)
    bw = 2.20

    hairline(sl, MARGIN, y_line, CW, PAPER_LINE, lw=1.4)
    for i, (year, title, detail) in enumerate(nodes):
        cx = x0 + i * step
        above = (i % 2 == 0)
        circle(sl, cx, y_line, 0.155, fill=CLAY)
        circle(sl, cx, y_line, 0.34, line=CLAY, lw=1.0)
        if above:
            vline(sl, cx - 0.005, y_line - 0.24, 0.16, PAPER_LINE, lw=1.2)
            ys = y_line - 1.62
        else:
            vline(sl, cx - 0.005, y_line + 0.08, 0.16, PAPER_LINE, lw=1.2)
            ys = y_line + 0.42
        bx = min(max(cx - bw / 2.0, MARGIN), SW - MARGIN - bw)
        tf = textbox(sl, bx, ys, bw, 0.34)
        para(tf, year, size=16, font=SERIF, bold=True, color=CLAY, line=1.0, first=True)
        tf = textbox(sl, bx, ys + 0.34, bw, 0.30)
        para(tf, title, size=12, font=SANSB, color=INK, line=1.05, first=True)
        tf = textbox(sl, bx, ys + 0.64, bw, 0.72)
        para(tf, detail, size=10.5, font=SANS, color=MUTED, line=1.26, first=True)

    rect(sl, MARGIN, 6.06, CW, 0.60, fill=(236, 227, 211))
    rect(sl, MARGIN, 6.06, 0.055, 0.60, fill=CLAY)
    tf = textbox(sl, MARGIN + 0.34, 6.21, CW - 0.5, 0.34)
    para(tf, [("3,100 years old", {"font": SERIF, "bold": True, "size": 13, "color": CLAY}),
              ("   \u2014   capital of 13 dynasties for 1,129 years, and the wall is still standing.",
               {"color": INK})],
         size=12.5, font=SANS, line=1.2, first=True)

    footer(sl, 5)
    notes(sl, "So how old is Xi'an? People have lived here for more than three thousand years. "
              "In 221 BC, Qin Shi Huang made China one country and ruled from the city next door. Under the "
              "Han dynasty, Chang'an became the capital and the starting point of the Silk Road. "
              "The Tang dynasty made it one of the largest and most international cities in the "
              "world. In the fourteenth century the Ming built the wall we still see today. And in "
              "1974, farmers digging a well found the Terracotta Army.")


# =====================================================================
# 06  who made it / other events
# =====================================================================
def s06_builders(prs):
    sl = slide(prs)
    bg(sl, "bg_paper_brick.jpg")
    header(sl, "02  \u00b7  Facts", "How old \u2014 and who made it",
           sub="Over 3,000 years old and an ancient capital of 13 dynasties \u2014 but not "
               "made by one person.")

    # ---- who made it?  four dynasties, not one person -------------------
    tf = textbox(sl, MARGIN, 2.14, 7.4, 0.24)
    para(tf, "WHO MADE IT?", size=9, font=SANSB, color=CLAY, spc=2.4, line=1.0, first=True)
    tf = textbox(sl, MARGIN + 1.55, 2.16, 8.0, 0.24)
    para(tf, "Xi'an grew over time \u2014 four dynasties built it.", size=11, font=SANS,
         color=MUTED, line=1.0, first=True)

    dynasties = [
        ("Zhou", "ABOUT 3,000 YEARS AGO",
         "King Wen built Feng Jing and King Wu built Gao Jing. This is where the history "
         "of Xi'an begins."),
        ("Western Han", "202 BC",
         "Liu Bang made the city his capital and named it Chang'an \u2014 long-term peace "
         "and order."),
        ("Sui", "AD 582",
         "Emperor Wen, Yang Jian, built Daxing City to the southeast of the old city."),
        ("Tang", "AD 618\u2013907",
         "Chang'an became the largest city in the world, and guests came from everywhere."),
    ]
    cw4, gap4 = (CW - 3 * 0.30) / 4.0, 0.30
    for i, (name, year, body) in enumerate(dynasties):
        x = MARGIN + i * (cw4 + gap4)
        hairline(sl, x, 2.44, cw4, GOLD, lw=1.4)
        tf = textbox(sl, x, 2.54, cw4, 0.28)
        para(tf, name, size=14, font=SERIF, bold=True, color=INK, line=1.05, first=True)
        tf = textbox(sl, x, 2.86, cw4, 0.20)
        para(tf, year, size=8.5, font=SANSB, color=CLAY, spc=1.8, line=1.0, first=True)
        tf = textbox(sl, x, 3.10, cw4, 0.78)
        para(tf, body, size=10.5, font=SANS, color=MUTED, line=1.26, first=True)

    # ---- what it left the world, with pictures --------------------------
    tf = textbox(sl, MARGIN, 3.98, 7.4, 0.24)
    para(tf, "WHAT IT LEFT THE WORLD", size=9, font=SANSB, color=CLAY, spc=2.4, line=1.0,
         first=True)

    marks = [
        ("bld_pit.jpg", "The Terracotta Army",
         "The Qin swept across the Six States here. The army is what it left behind."),
        ("bld_pagoda.jpg", "Big Wild Goose Pagoda",
         "The Silk Road started here, by Zhang Qian. In Tang times visitors came from all "
         "over the world."),
        ("bld_wall.jpg", "The city wall today",
         "The ancient walls and the old Bell Tower still draw visitors. The subway now runs "
         "through Han and Tang layers."),
    ]
    cw3, gap3 = (CW - 2 * 0.34) / 3.0, 0.34
    for i, (g, title, body) in enumerate(marks):
        x = MARGIN + i * (cw3 + gap3)
        card(sl, x, 4.22, cw3, 1.46)
        shot = pic(sl, g, x + 0.22, 4.42, h=1.10)
        shot.line.color.rgb = rgb((214, 201, 180))
        shot.line.width = Pt(0.75)
        tf = textbox(sl, x + 1.14, 4.42, cw3 - 1.36, 0.26)
        para(tf, title, size=11.5, font=SERIF, bold=True, color=INK, line=1.05, first=True)
        tf = textbox(sl, x + 1.14, 4.70, cw3 - 1.36, 0.92)
        para(tf, body, size=10, font=SANS, color=MUTED, line=1.26, first=True)

    # ---- the turning points ---------------------------------------------
    card(sl, MARGIN, 5.82, CW, 0.60)
    half = (CW - 0.68 - 0.30) / 2.0
    for i, (era, text) in enumerate([
        ("AD 755 \u00b7 THE AN SHI REBELLION",
         "The Tang turned to decline, and in 904 the city was destroyed."),
        ("1936 \u00b7 THE XI'AN INCIDENT",
         "The turning point that stopped the civil war and united the country against Japan."),
    ]):
        x = MARGIN + 0.34 + i * (half + 0.30)
        tf = textbox(sl, x, 5.94, half, 0.44)
        para(tf, [(era + "  ", {"size": 9, "font": SANSB, "color": GOLD, "spc": 1.6}),
                  (text, {"size": 10.5, "color": MUTED})],
             size=10.5, font=SANS, line=1.26, first=True)

    footer(sl, bump())
    notes(sl, "Part two: the facts. Xi'an has a history of over three thousand years, and it "
              "was the capital of thirteen dynasties. But it was not made by one person at a "
              "time. About three thousand years ago, King Wen of Zhou built Feng Jing and King "
              "Wu of Zhou built Gao Jing - that is where the history of Xi'an begins. In the "
              "Western Han, Liu Bang made the city his capital and named it Chang'an, which "
              "means long-term peace and order. In the Sui dynasty, Emperor Wen, Yang Jian, "
              "built Daxing City to the southeast of the old city. And by the Tang dynasty, "
              "Chang'an had become the largest city in the world. The Qin swept across the Six "
              "States here. The Silk Road started from here, by Zhang Qian, and in Tang times "
              "visitors came from all over the world. The Giant Wild Goose Pagoda, the Great "
              "Ming Palace and the Terracotta Army are the footprints Xi'an left for the world. "
              "But history has a turning point too. After the An Shi Rebellion the Tang went "
              "into decline, and in 904 the city was destroyed. In 1936 the Xi'an Incident "
              "happened here - the turning point that stopped the civil war and united the "
              "country against Japan. Today Xi'an still has its ancient walls and its old Bell "
              "Tower, and the subway now runs through Han and Tang layers. It is not only an "
              "ancient city, but a witness to Chinese history.")


# =====================================================================
# 07  opinion (+) - sights
# =====================================================================
def s07_loved(prs):
    sl = slide(prs)
    bg(sl, "bg_paper.jpg")
    header(sl, "03  \u00b7  Opinion (positives)", "What we loved",
           sub="Four things we would go back for \u2014 and one line on why each one is worth it.")

    items = [
        ("Must-see", "The Terracotta Army",
         "8,000 life-size soldiers, no two faces the same, buried for 2,200 years.",
         "40 km east  \u00b7  half a day  \u00b7  book ahead",
         ("photo", "terracotta_head.jpg")),
        ("Best two hours", "Cycling the city wall",
         "You ride on top of 13.74 km of Ming bricks, 12 m above the town.",
         "Rent at the South Gate  \u00b7  \u00a545",
         ("photo", "card_wall.jpg")),
        ("Best food", "The Muslim Quarter",
         "A living Hui area full of lamb on sticks, flat bread and hot pepper.",
         "Behind the Drum Tower  \u00b7  go at night",
         ("photo", "card_muslim.jpg")),
        ("Best at night", "Datang Everbright City",
         "A Tang street that comes alive with lights, beside the Big Wild Goose Pagoda.",
         "Free to walk  \u00b7  go after dark",
         ("photo", "card_datang.jpg")),
    ]
    cw, gap = (CW - 0.34) / 2.0, 0.34
    for i, (tg, title, body, gold, gname) in enumerate(items):
        r, c = divmod(i, 2)
        x = MARGIN + c * (cw + gap)
        y = 2.24 + r * 2.08
        card(sl, x, y, cw, 2.00)
        tag(sl, x + 0.34, y + 0.26, tg)
        if isinstance(gname, tuple):
            # a real photograph gets a tall slot on the right of the card
            ph = 1.55
            pw = ph * 0.75
            ph_pic = pic(sl, gname[1], x + cw - 0.30 - pw, y + 0.24, h=ph)
            ph_pic.line.color.rgb = rgb(PAPER_LINE)
            ph_pic.line.width = Pt(0.75)
            tw = cw - 0.68 - pw - 0.26
            grw = tw - 0.48
        else:
            gw = pic_right(sl, gname, x + cw - 0.34, y + 0.24, h=0.58)
            tw = cw - 0.68 - gw - 0.22
            grw = cw - 1.16
        tf = textbox(sl, x + 0.34, y + 0.58, tw, 0.32)
        para(tf, title, size=16.5, font=SERIF, bold=True, color=INK, line=1.05, first=True)
        tf = textbox(sl, x + 0.34, y + 0.94, tw, 0.50)
        para(tf, body, size=11.5, font=SANS, color=MUTED, line=1.28, first=True)
        hairline(sl, x + 0.34, y + 1.56, 0.36, GOLD, lw=1.3)
        tf = textbox(sl, x + 0.82, y + 1.48, grw, 0.44)
        para(tf, gold, size=10.5, font=SANS, color=CLAY_DEEP, line=1.2, first=True)

    tf = textbox(sl, MARGIN, 6.50, CW, 0.34)
    para(tf, [("ALSO WORTH IT   ", {"font": SANSB, "size": 9, "color": CLAY, "spc": 2.2}),
              ("Shaanxi History Museum, 1.7 million objects, free   \u00b7   Bell and Drum Tower   "
               "\u00b7   Mount Hua day trip   \u00b7   Huaqing Palace", {"color": MUTED})],
         size=11, font=SANS, line=1.2, first=True)

    footer(sl, bump())
    notes(sl, "Now our own opinion, starting with the good news. Four things we loved. The "
              "Terracotta Army: eight thousand soldiers, every face different, and they waited "
              "there for two thousand two hundred years. Cycling the city wall - fourteen "
              "kilometres along the top of the Ming wall, and it costs about forty-five yuan. The "
              "Muslim Quarter for street food. And Datang Everbright City at night, which is free. "
              "If you have more time, the Shaanxi History Museum and Mount Hua are both excellent.")


# =====================================================================
# 08  opinion (+) - food
# =====================================================================
def s08_food(prs):
    sl = slide(prs)
    bg(sl, "bg_clay.jpg")
    header(sl, "03  \u00b7  Opinion (positives)", "And then there is the food",
           dark=True, accent=GOLD,
           sub="Xi'an eats wheat instead of rice, and lamb instead of pork. Four things you "
               "should not leave without trying.")

    foods = [
        ("Roujiamo", "\u8089\u5939\u998d", "Pork cooked slowly in a warm flat bread \u2014 China's oldest sandwich.", "\u00a510\u201315", "food_roujiamo.jpg"),
        ("Yangrou paomo", "\u7f8a\u8089\u6ce1\u998d", "Lamb soup that you break your own flat bread into.", "\u00a540\u201360", "food_paomo.jpg"),
        ("Biangbiang noodles", "\u6cb9\u6cfc\u9762", "Noodles as wide as a belt, made by hand, with hot pepper oil.", "\u00a518\u201328", "food_yopo.jpg"),
        ("Liangpi", "\u51c9\u76ae", "Cold noodles with hot pepper oil \u2014 cheap and popular.", "\u00a510\u201315", "food_liangpi.jpg"),
    ]
    for i, (name, cjk, desc, price, shot) in enumerate(foods):
        y = 2.42 + i * 1.00
        hairline(sl, MARGIN, y - 0.18, 6.90, (146, 96, 72), lw=1.0)
        thumb = pic(sl, shot, MARGIN, y - 0.04, h=0.76)
        thumb.line.color.rgb = rgb((226, 190, 165))
        thumb.line.width = Pt(0.75)
        tf = textbox(sl, MARGIN + 0.90, y - 0.02, 4.30, 0.32)
        para(tf, [(name, {"font": SERIF, "bold": True, "size": 15, "color": PAPER}),
                  ("     " + cjk, {"size": 12, "color": GOLD_SOFT, "cjk": CJK})],
             size=15, font=SERIF, line=1.05, first=True)
        tf = textbox(sl, MARGIN + 0.90, y + 0.34, 4.30, 0.54)
        para(tf, desc, size=11, font=SANS, color=(238, 220, 204), line=1.26, first=True)
        tf = textbox(sl, MARGIN + 6.00, y + 0.02, 0.90, 0.30)
        para(tf, price, size=12.5, font=SERIF, bold=True, color=GOLD_SOFT,
             align=PP_ALIGN.RIGHT, line=1.0, first=True)
    hairline(sl, MARGIN, 6.42, 6.90, (146, 96, 72), lw=1.0)

    card(sl, 8.10, 2.42, 4.41, 4.00, fill=(250, 245, 236), line=None)
    shot = pic(sl, "food_market.jpg", 8.44, 2.66, w=3.73)
    shot.line.color.rgb = rgb((214, 201, 180))
    shot.line.width = Pt(0.75)
    tf = textbox(sl, 8.44, 4.12, 3.73, 0.32)
    para(tf, "Eat like a local", size=17, font=SERIF, bold=True, color=INK, line=1.05, first=True)
    hairline(sl, 8.44, 4.54, 0.42, GOLD, lw=1.4)
    tips = [
        "The Muslim Quarter is the famous one \u2014 and the busiest. Local people eat one street further in.",
        "Lao Sun Jia has served yangrou paomo since 1898.",
        "A full street-food dinner costs about \u00a540\u201360. It is the best meal for your money.",
    ]
    for i, t in enumerate(tips):
        y = 4.68 + i * 0.62
        rect(sl, 8.44, y + 0.07, 0.075, 0.075, fill=CLAY)
        tf = textbox(sl, 8.66, y, 3.51, 0.60)
        para(tf, t, size=11, font=SANS, color=(84, 76, 66), line=1.28, first=True)

    footer(sl, 8, dark=True)
    notes(sl, "And then there is the food. Xi'an is a wheat-and-lamb city, which makes it "
              "different from most of China. Roujiamo is pork cooked slowly in a flat bread - people call "
              "it China's oldest sandwich, and it costs about ten yuan. Yangrou paomo is lamb "
              "soup that you break your own bread into. Biangbiang noodles are as wide as a "
              "belt. And liangpi are cold noodles with hot pepper oil. A whole dinner costs less than "
              "sixty yuan. The Muslim Quarter is the famous place to try them.")


# =====================================================================
# 09  opinion (-)
# =====================================================================
def s09_honest(prs):
    sl = slide(prs)
    bg(sl, "bg_slate.jpg")
    header(sl, "04  \u00b7  Opinion (negatives)", "The honest part",
           dark=True, accent=GOLD,
           sub="Nothing is perfect. These are the things visitors really complain about.")

    rows = [
        ("Booking is the hard part",
         "You must book with your real name and choose a time. Only 65,000 people can go in "
         "each day, and at Spring Festival it sells out. You also need your passport number."),
        ("Crowds \u2014 and a long way out",
         "On the busiest days all the tickets go, and the site is 40 km east of town. The "
         "subway and bus take about two hours each way, so the trip takes half a day."),
        ("Tickets are not cheap",
         "\u00a5120 for the army, \u00a554 for the wall, \u00a545 for a bike: "
         "\u00a5174 before you have eaten anything."),
        ("Summer is hard",
         "In July the temperature is about 35 \u00b0C in the day, and 33 \u00b0C in August. "
         "Fog can make the view from the wall less clear."),
        ("Tourist food is not always good",
         "The Muslim Quarter is the famous food street, but the prices are high and it is "
         "always full of visitors. Local people eat one street further in."),
        ("Watch out near the site",
         "Local news has reported guides and drivers taking visitors to fake \"underground "
         "palace\" shows \u2014 one family paid \u00a5564 for ten minutes."),
    ]
    for i, (head, body) in enumerate(rows):
        y = 2.30 + i * 0.72
        hairline(sl, MARGIN, y - 0.17, CW, (66, 71, 85), lw=1.0)
        rect(sl, MARGIN, y + 0.045, 0.09, 0.09, fill=CLAY, rot=45)
        tf = textbox(sl, MARGIN + 0.42, y - 0.01, 3.85, 0.32)
        para(tf, head, size=13.5, font=SERIF, bold=True, color=PAPER, line=1.05, first=True)
        tf = textbox(sl, MARGIN + 4.45, y + 0.01, CW - 4.45, 0.50)
        para(tf, body, size=11, font=SANS, color=LIGHT_2, line=1.26, first=True)
    hairline(sl, MARGIN, 2.30 + 5 * 0.72 + 0.52, CW, (66, 71, 85), lw=1.0)

    footer(sl, bump(), dark=True)
    notes(sl, "But we have to be honest about the bad points too. First, booking. For the "
              "Terracotta Army you must use your real name and choose a time, and only a certain "
              "number of people can go in each day. At Spring Festival it sells out completely. "
              "Second, crowds - and the site is forty kilometres out of town, so it takes half a "
              "day. Third, the prices: a hundred and twenty yuan for the army, fifty-four for "
              "the wall and forty-five for a bike. Fourth, the summer heat - thirty-five degrees "
              "in July. Fifth, the food: the Muslim Quarter is famous, but it is really a "
              "tourist street, and local people eat one street further in. And sixth, near the "
              "site some guides and drivers take visitors to fake shows. Knowing all this in "
              "advance makes the trip much easier.")


# =====================================================================
# 10  opinion (-) continued
# =====================================================================
def s10_more(prs):
    sl = slide(prs)
    bg(sl, "bg_slate.jpg")
    header(sl, "04  \u00b7  Opinion (negatives)", "And a few more warnings",
           dark=True, accent=GOLD,
           sub="Small problems that can make a trip less fun \u2014 and how to be "
               "ready for them.")

    rows = [
        ("Tourist food is not always good",
         "The Muslim Quarter is the famous food street, but the prices are high and it is "
         "always full of visitors. Local people eat one street further in."),
        ("The free museum is hard to book",
         "The Shaanxi History Museum costs nothing, but the daily number is limited, and "
         "some people sell the tickets again at high prices."),
        ("English is not widely spoken",
         "Outside the big hotels, few people speak English. A translation app on your "
         "phone is worth having."),
        ("The air is not always clean",
         "Xi'an's air has improved only in the last few years. On some days it is still "
         "not clear, and the view from the wall is poor."),
    ]
    for i, (head, body) in enumerate(rows):
        y = 2.32 + i * 1.05
        hairline(sl, MARGIN, y - 0.22, CW, (66, 71, 85), lw=1.0)
        rect(sl, MARGIN, y + 0.055, 0.10, 0.10, fill=CLAY, rot=45)
        tf = textbox(sl, MARGIN + 0.42, y - 0.01, 3.85, 0.62)
        para(tf, head, size=14, font=SERIF, bold=True, color=PAPER, line=1.1, first=True)
        tf = textbox(sl, MARGIN + 4.45, y + 0.02, CW - 4.45, 0.62)
        para(tf, body, size=11.5, font=SANS, color=LIGHT_2, line=1.28, first=True)
    hairline(sl, MARGIN, 2.32 + 3 * 1.05 + 0.72, CW, (66, 71, 85), lw=1.0)

    footer(sl, 10, dark=True)
    notes(sl, "Now a few more small problems. First, food. The Muslim Quarter is famous, but "
              "it is really a tourist street: the prices are high and the food is not always "
              "the best. Local people eat one street further in. Second, the Shaanxi History "
              "Museum is free, but only a limited number of people can go in each day, and "
              "some tickets are sold again at high prices. Third, outside the big hotels, few "
              "people speak English. And fourth, the air: it has got cleaner in recent years, "
              "but some days are still not clear.")


# =====================================================================
# 11  summary
# =====================================================================
def s10_summary(prs):
    sl = slide(prs)
    bg(sl, "bg_ink.jpg")
    eyebrow(sl, "05  \u00b7  Summary", color=GOLD)

    tf = textbox(sl, MARGIN, 1.24, 11.0, 1.00)
    para(tf, "Go \u2014 but go smart.", size=52, font=SERIF, bold=True, color=PAPER,
         line=1.0, first=True)
    hairline(sl, MARGIN, 2.44, 1.85, GOLD, lw=1.8)

    tf = textbox(sl, MARGIN, 2.76, 6.05, 2.9)
    para(tf, "Xi'an is not a relaxing city, and it is not a hidden one. But nowhere else gives "
             "you three thousand years in a single weekend: an emperor's army, a wall you can "
             "cycle, and the food that other Chinese cities try to match.",
         size=13, font=SANS, color=LIGHT, line=1.42, first=True)
    para(tf, "The good parts win easily. Just do not go in July, and do not arrive without a "
             "booking.", size=13, font=SANS, color=GOLD_SOFT, line=1.42, before=14)

    card(sl, 7.30, 2.66, 5.21, 3.34, fill=(32, 35, 46), line=(62, 67, 82))
    tf = textbox(sl, 7.64, 2.90, 4.53, 0.28)
    para(tf, "IF YOU GO", size=9, font=SANSB, color=GOLD, spc=2.4, line=1.0, first=True)
    pic_right(sl, "glyph_belltower_gold.png", 12.17, 2.84, h=0.44)
    tips = [
        ("Best time", "April to May, or September to October."),
        ("How long", "Three to four days; the army takes a full day."),
        ("Where to stay", "Inside the city wall, near the Bell Tower."),
        ("Book ahead", "Book the army and the museum online."),
    ]
    for i, (k, v) in enumerate(tips):
        y = 3.26 + i * 0.68
        tf = textbox(sl, 7.64, y, 1.42, 0.26)
        para(tf, k.upper(), size=8.5, font=SANSB, color=CLAY_SOFT, spc=1.6, line=1.0, first=True)
        tf = textbox(sl, 7.64, y + 0.25, 3.95, 0.34)
        para(tf, v, size=11, font=SANS, color=(206, 199, 187), line=1.24, first=True)

    hairline(sl, MARGIN, 6.28, CW, (58, 62, 76), lw=1.0)
    tf = textbox(sl, MARGIN, 6.46, CW, 0.34)
    para(tf, [("One-line answer:  ", {"color": MUTED_D}),
              ("yes \u2014 go in the right season, and book before you fly.",
               {"color": PAPER, "font": SERIF, "bold": True, "size": 13})],
         size=12.5, font=SANS, line=1.2, first=True)

    footer(sl, bump(), dark=True)
    notes(sl, "So, our summary. Our answer is yes - go, but go smart. Xi'an is not relaxing and "
              "it is not a secret place, but nowhere else gives you three thousand years of "
              "history in one weekend. The good parts win easily. If you go: April, May, "
              "September or October are the best months. Give it three or four days. Stay inside "
              "the city wall, near the Bell Tower. And book your tickets online before you "
              "travel, especially for the Terracotta Army.")


# =====================================================================
# 11  thank you
# =====================================================================
def s11_thanks(prs):
    bump()
    sl = slide(prs)
    bg(sl, "bg_ink_gold.jpg")
    vline(sl, 0.42, 0.0, SH, (58, 50, 44), lw=1.0)

    tf = textbox(sl, 0, 1.72, SW, 0.80)
    para(tf, "\u8c22\u8c22", size=40, font=CJK, color=GOLD, align=PP_ALIGN.CENTER,
         line=1.0, first=True, cjk_font=CJK)

    tf = textbox(sl, 0, 2.62, SW, 1.20)
    para(tf, "Thank you", size=68, font=SERIF, bold=True, color=PAPER,
         align=PP_ALIGN.CENTER, line=1.0, first=True)

    hairline(sl, SW / 2 - 0.75, 4.06, 1.5, GOLD, lw=1.6)

    tf = textbox(sl, 0, 4.30, SW, 0.50)
    para(tf, "Questions?", size=17, font=SANS, color=LIGHT,
         align=PP_ALIGN.CENTER, line=1.0, first=True)

    tf = textbox(sl, 0, 5.32, SW, 0.36)
    para(tf, "Xi'an  \u00b7  \u897f\u5b89  \u00b7  Shaanxi, China", size=11, font=SANS,
         color=MUTED_D, spc=2.4, align=PP_ALIGN.CENTER, line=1.0, first=True, cjk_font=CJK)

    five_part_strip(sl, 6.42, dark=True, x=0, size=8.5, center=True)
    seal(sl, SW - MARGIN - 0.62, 0.62, size=0.62, chars="\u957f\u5b89")

    notes(sl, "To finish, our answer is simple: yes, go - but go smart. Xi'an gives you more than "
              "three thousand years of history in three days, and the food alone is worth the "
              "trip. Just avoid July and August, book your tickets early, and stay near the Bell "
              "Tower. Thank you for listening. We are happy to take your questions.")


BUILDERS = [s01_cover, s03_where, s06_builders, s07_loved,
            s09_honest, s10_summary, s11_thanks]


def main():
    prs = new_deck()
    for b in BUILDERS:
        b(prs)

    # The speaker notes belong to the printed script, not to the deck: the group
    # asked for a clean PPT with nothing in the notes pane. Keep the text in a
    # sidecar (the .docx reads it) and drop the notes parts before saving.
    notes = []
    for sl in prs.slides:
        notes.append(sl.notes_slide.notes_text_frame.text.strip()
                     if sl.has_notes_slide else "")
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    with open(os.path.join(HERE, "build", "notes.json"), "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=1)
    stripped = 0
    for sl in prs.slides:
        for rel in list(sl.part.rels.values()):
            if rel.reltype.endswith("/notesSlide"):
                sl.part.drop_rel(rel.rId)
                stripped += 1

    prs.save(OUT)
    print("saved:", OUT)
    print("slides:", len(prs.slides._sldIdLst))
    print("notes kept in build/notes.json: %d | notes parts removed from deck: %d"
          % (sum(1 for n in notes if n), stripped))


if __name__ == "__main__":
    main()
