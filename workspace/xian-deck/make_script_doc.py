# -*- coding: utf-8 -*-
"""Build a printable speaker script (.docx) straight from the deck's notes,
so the script and the PPT can never disagree."""
import os
import json
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pptx import Presentation

HERE = os.path.dirname(os.path.abspath(__file__))
PPTX = os.path.join(HERE, "Xi'an - An Interesting Place.pptx")
OUT = os.path.join(HERE, "\u897f\u5b89\u5c55\u793a-\u82f1\u6587\u8bb2\u7a3f.docx")

LATIN = "Segoe UI"
CJK = "Microsoft YaHei"

# page -> (slide title, section label, who)
PAGES = [
    (1, "Cover \u2014 XI'AN", "\u5f00\u573a", "\u5f00\u573a\u4eba"),
    (2, "Where in the world is Xi'an?", "01 Introduction and general facts", "\u5f20\u5ead\u8bed"),
    (3, "How old \u2014 and who made it", "02 Facts", ""),
    (4, "What we loved", "03 Opinion (positives)", ""),
    (5, "The honest part", "04 Opinion (negatives)", ""),
    (6, "Go \u2014 but go smart.", "05 Summary", ""),
    (7, "Thank you", "05 Summary", ""),
]


def setfont(run, size, bold=False, color=None, cjk=CJK, latin=LATIN):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = latin
    if color:
        run.font.color.rgb = RGBColor(*color)
    rPr = run._r.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    rf.set(qn('w:ascii'), latin)
    rf.set(qn('w:hAnsi'), latin)
    rf.set(qn('w:eastAsia'), cjk)


def para(doc, text, size=11, bold=False, color=None, space_after=6,
         space_before=0, line=1.25, align=None, indent=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line
    if indent is not None:
        pf.left_indent = Cm(indent)
    setfont(p.add_run(text), size, bold, color)
    return p


def rule(doc, color="C8BCA8", space_after=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single')
    b.set(qn('w:sz'), '6')
    b.set(qn('w:space'), '1')
    b.set(qn('w:color'), color)
    bdr.append(b)
    pPr.append(bdr)
    return p


def main():
    # the deck ships with an empty notes pane, so the script text is read from
    # the build sidecar that build_deck.py writes (same single source of truth)
    with open(os.path.join(HERE, "build", "notes.json"), encoding="utf-8") as f:
        notes = [t.strip() for t in json.load(f)]
    n_slides = len(Presentation(PPTX).slides._sldIdLst) if os.path.exists(PPTX) else len(notes)
    if len(notes) != n_slides:
        raise SystemExit("notes.json has %d entries but the deck has %d slides - "
                         "run build_deck.py first" % (len(notes), n_slides))

    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.4)
        sec.right_margin = Cm(2.4)

    normal = doc.styles['Normal']
    normal.font.name = LATIN
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), CJK)

    # ---------------- cover block ----------------
    para(doc, "Xi'an \u2014 An Interesting Place", 20, True, (0x17, 0x19, 0x22),
         space_after=2)
    para(doc, "\u5c0f\u7ec4\u5c55\u793a\u82f1\u6587\u8bb2\u7a3f  \u00b7  Group Presentation Script",
         12, False, (0x7A, 0x72, 0x66), space_after=14)
    rule(doc)

    total = sum(len(n.split()) for n in notes)
    para(doc, "\u4f7f\u7528\u8bf4\u660e", 13, True, (0x9A, 0x45, 0x27), space_after=4)
    for b in [
        "\u8bb2\u7a3f\u4e0e PPT \u6309\u9875\u4e00\u4e00\u5bf9\u5e94\uff0c\u5171 7 \u9875\uff08\u5c01\u9762 + \u4e94\u4e2a\u8981\u70b9\u5404\u4e00\u9875 + \u81f4\u8c22\uff09\u3002"
        "\u6bcf\u9875\u4e0b\u65b9\u7559\u4e86\u7a7a\u767d\uff0c\u53ef\u4ee5\u5199\u6279\u6ce8\u6216\u6362\u6210\u81ea\u5df1\u7684\u8bf4\u6cd5\u3002",
        "\u5168\u6587\u7ea6 %d \u8bcd\u3002\u6309 120\u2013140 \u8bcd/\u5206\u949f\u7684\u8bed\u901f\uff0c"
        "\u7ea6 7 \u5206\u949f\uff1b\u52a0\u4e0a\u5207\u9875\u548c\u505c\u987f\uff0c\u5b9e\u9645\u7ea6 8\u20139 \u5206\u949f\u3002" % total,
        "\u26a0 \u897f\u5b89\u6240\u5728\u7684\u7701\u662f Shaanxi\uff08\u9655\u897f\uff09\uff0c"
        "\u4e0d\u662f Shanxi\uff08\u5c71\u897f\uff09\u2014\u2014\u4e24\u4e2a\u8bcd\u53ea\u5dee\u4e00\u4e2a a\uff0c"
        "\u8bf4\u7684\u65f6\u5019\u4e5f\u8981\u5206\u6e05\u695a\u3002",
        "\u2139 \u7b2c 1 \u9875\u548c\u7b2c 3 \u9875\u539f\u672c\u90fd\u5728\u4ecb\u7ecd\u897f\u5b89\u7684\u57fa\u672c\u60c5\u51b5\uff0c"
        "\u5df2\u7ecf\u7406\u987a\uff1a\u5f00\u573a\u767d\u548c\u57ce\u5e02\u6982\u51b5\u653e\u5728\u7b2c 1 \u9875\uff0c"
        "\u7b2c 3 \u9875\u76f4\u63a5\u8fdb\u5165\u7b2c\u4e00\u90e8\u5206\u3002",
    ]:
        para(doc, b, 10, False, (0x3A, 0x38, 0x33), space_after=3, line=1.3)

    # ---------------- who reads what ----------------
    para(doc, "\u5206\u5de5", 13, True, (0x9A, 0x45, 0x27), space_before=12, space_after=4)
    tbl = doc.add_table(rows=1, cols=3)
    tbl.style = 'Table Grid'
    hdr = ["\u9875", "\u5185\u5bb9", "\u53d1\u8a00\u4eba"]
    for i, h in enumerate(hdr):
        c = tbl.rows[0].cells[i]
        c.text = ""
        setfont(c.paragraphs[0].add_run(h), 10, True, (0x17, 0x19, 0x22))
    groups = [("1", "\u5f00\u573a", "\u5f00\u573a\u4eba"),
              ("2", "01 Introduction and general facts", "\u5f20\u5ead\u8bed"),
              ("3", "02 Facts", ""),
              ("4", "03 Opinion (positives)", ""),
              ("5", "04 Opinion (negatives)", ""),
              ("6\u20137", "05 Summary + \u81f4\u8c22", "")]
    for g in groups:
        cells = tbl.add_row().cells
        for i, v in enumerate(g):
            cells[i].text = ""
            setfont(cells[i].paragraphs[0].add_run(v), 10, False, (0x3A, 0x38, 0x33))

    # ---------------- page by page ----------------
    for idx, (num, title, section, who) in enumerate(PAGES):
        doc.add_paragraph()
        para(doc, "Page %d  \u00b7  %s" % (num, title), 14, True, (0x17, 0x19, 0x22),
             space_before=8, space_after=1)
        meta = "%s" % section
        if who:
            meta += "\u3000\u00b7\u3000\u53d1\u8a00\u4eba\uff1a%s" % who
        wc = len(notes[idx].split())
        meta += "\u3000\u00b7\u3000\u7ea6 %d \u8bcd\uff08\u7ea6 %.0f \u79d2\uff09" % (wc, wc / 130.0 * 60)
        para(doc, meta, 9.5, False, (0x7A, 0x72, 0x66), space_after=6)
        rule(doc, space_after=6)

        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(10)
        setfont(p.add_run(notes[idx]), 12, False, (0x1A, 0x1A, 0x1A))

        for _ in range(3):
            e = doc.add_paragraph()
            e.paragraph_format.space_after = Pt(2)
            setfont(e.add_run(" "), 11)

    doc.save(OUT)
    print("saved:", OUT)
    print("total words:", total)


if __name__ == "__main__":
    main()
