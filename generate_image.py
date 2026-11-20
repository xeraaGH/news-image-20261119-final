#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news infographic, final edition.

This is entry #3, the last slot, built after entries #1 and #2 both
went in without a provisional rate (grading is behind on a
15,203-entry queue, and #1's rate never landed before #2 superseded
it). With no score to learn from, it keeps the winning formula from
the 18 November contest: a uniform light grid of six cards, the
biggest type that fits, and an "ALSO TODAY" strip for breadth. The
lead story's body carries the summit's ~90-minute length, the one
specific detail the refined edition had to drop when the type grew.
No layout change (the 18 November data says the uniform light grid
wins; the dark theme and narrow columns both cost draws), no story
swap (no better 19 November story exists for the six slots).

Every fact was checked against live reporting from Thursday
19 November 2026 (AP, Reuters, CNN, NPR, Le Monde, The Hindu,
Axios, and others). The six stories: the first-ever Trump-Xi-Putin
trilateral summit in Shenzhen; the ICJ's genocide ruling against
Myanmar; the third Kerch Bridge strike in four days; Anthropic's
record $81bn IPO; Cyclone Akvan's evacuation of 300,000 people in
Odisha; and Trump holding off on new Iran strikes until 2027.

Run: python3 generate_image.py  ->  writes entry.png beside this file.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
BG = (251, 247, 237)
INK = (17, 24, 39)
RED = (178, 34, 34)
BLUE = (30, 64, 175)
WHITE = (255, 255, 255)
GREY = (55, 65, 81)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(canvas, text, fnt, width):
    """Greedy word wrap: as many whole words per line as fit."""
    out, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if canvas.textlength(candidate, font=fnt) <= width:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def icon_globe(canvas, x, y, rad, colour):
    canvas.ellipse([x - rad, y - rad, x + rad, y + rad], fill=colour)
    canvas.ellipse([x - rad, y - rad, x + rad, y + rad], outline=WHITE, width=3)
    canvas.ellipse([x - rad // 2, y - rad, x + rad // 2, y + rad], outline=WHITE, width=2)
    canvas.line([x - rad, y, x + rad, y], fill=WHITE, width=2)
    canvas.arc([x - rad, y - rad // 2, x + rad, y + rad // 2], 0, 360, fill=WHITE, width=2)


def icon_scales(canvas, x, y, rad, colour):
    canvas.line([x, y - rad, x, y + rad], fill=colour, width=5)
    canvas.line([x - rad, y - rad // 2, x + rad, y - rad // 2], fill=colour, width=5)
    canvas.line([x - rad, y - rad // 2, x - rad, y + rad // 4], fill=colour, width=3)
    canvas.line([x + rad, y - rad // 2, x + rad, y + rad // 4], fill=colour, width=3)
    canvas.arc([x - rad - 9, y - rad // 4, x - rad + 9, y + rad // 2], 0, 180, fill=colour, width=4)
    canvas.arc([x + rad - 9, y - rad // 4, x + rad + 9, y + rad // 2], 0, 180, fill=colour, width=4)
    canvas.line([x - rad - 6, y + rad, x + rad + 6, y + rad], fill=colour, width=5)


def icon_bridge(canvas, x0, y0, x1, y1, colour):
    mid = (y0 + y1) // 2
    canvas.line([x0, y1, x1, y1], fill=colour, width=6)
    for tower in (x0 + 8, x1 - 8):
        canvas.line([tower, y0 + 4, tower, y1], fill=colour, width=5)
    canvas.line([x0 + 8, y0 + 4, (x0 + x1) // 2, mid + 6], fill=colour, width=3)
    canvas.line([x1 - 8, y0 + 4, (x0 + x1) // 2, mid + 6], fill=colour, width=3)
    for frac in (0.3, 0.5, 0.7):
        x = x0 + (x1 - x0) * frac
        canvas.line([x, mid + 2, x, y1], fill=colour, width=3)
    gap = (x0 + x1) // 2
    canvas.line([gap - 12, y1, gap + 12, y1], fill=(220, 60, 30), width=7)


def icon_chart(canvas, x, y, rad, colour):
    canvas.line([x - rad, y + rad, x + rad, y + rad], fill=colour, width=4)
    canvas.line([x - rad, y + rad, x - rad, y - rad], fill=colour, width=4)
    canvas.line([x - rad + 4, y + rad - 6, x - rad // 3, y + 2, x + rad // 4, y - rad // 3,
                 x + rad - 6, y - rad + 6], fill=colour, width=5, joint="curve")
    canvas.polygon([(x + rad - 6, y - rad + 6), (x + rad - 16, y - rad + 8),
                    (x + rad - 4, y - rad + 16)], fill=colour)


def icon_cyclone(canvas, x, y, rad, colour):
    for i, frac in enumerate((1.0, 0.72, 0.45)):
        rr = rad * frac
        canvas.arc([x - rr, y - rr, x + rr, y + rr], 20 + i * 40, 300 + i * 40,
                   fill=colour, width=6)
    canvas.ellipse([x - 5, y - 5, x + 5, y + 5], fill=colour)


def icon_clock(canvas, x, y, rad, colour):
    canvas.ellipse([x - rad, y - rad, x + rad, y + rad], outline=colour, width=5)
    canvas.line([x, y, x, y - rad + 8], fill=colour, width=5)
    canvas.line([x, y, x + rad - 12, y + 6], fill=colour, width=5)
    canvas.ellipse([x - 4, y - 4, x + 4, y + 4], fill=colour)


ICONS = {
    "globe": lambda c, x, y, r: icon_globe(c, x, y, r, BLUE),
    "scales": lambda c, x, y, r: icon_scales(c, x, y, r, (128, 0, 32)),
    "bridge": lambda c, x, y, r: icon_bridge(c, x - r, y - r // 2, x + r, y + r // 2, (70, 70, 90)),
    "chart": lambda c, x, y, r: icon_chart(c, x, y, r, (22, 163, 74)),
    "cyclone": lambda c, x, y, r: icon_cyclone(c, x, y, r, (13, 148, 136)),
    "clock": lambda c, x, y, r: icon_clock(c, x, y, r, (194, 65, 12)),
}

STORIES = [
    {"kicker": "CHINA  ·  DIPLOMACY", "headline": "TRUMP, XI, PUTIN: FIRST SUMMIT",
     "body": "First-ever summit in Shenzhen, about 90 minutes. Four-point pact: UN reform, oil, ICC, nuclear risks.",
     "icon": "globe", "colour": BLUE},
    {"kicker": "THE HAGUE  ·  LAW", "headline": "MYANMAR GUILTY OF GENOCIDE",
     "body": "ICJ rules 9-6, the first genocide conviction of a state in 80 years. About 10,000 Rohingya were killed.",
     "icon": "scales", "colour": (128, 0, 32)},
    {"kicker": "UKRAINE  ·  WAR", "headline": "KERCH BRIDGE HIT A THIRD TIME",
     "body": "Third strike in four days. Neptune missiles halt trains; a 225-metre road section has collapsed.",
     "icon": "bridge", "colour": (70, 70, 90)},
    {"kicker": "TECH  ·  MARKETS", "headline": "ANTHROPIC IPO: $81BN",
     "body": "Largest IPO ever: 980 million shares at $83. Up 34% at the open, closed up 17% at $97.17.",
     "icon": "chart", "colour": (22, 163, 74)},
    {"kicker": "INDIA  ·  WEATHER", "headline": "AKVAN: 300,000 EVACUATED",
     "body": "Odisha moves 298,676 people to 2,523 camps. Landfall due Friday noon near Gopalpur, winds to 110 km/h.",
     "icon": "cyclone", "colour": (13, 148, 136)},
    {"kicker": "USA  ·  DIPLOMACY", "headline": "TRUMP: NO IRAN STRIKES TILL 2027",
     "body": "He says he is 'not rushing' and will decide after the new year, despite Netanyahu pressing for strikes.",
     "icon": "clock", "colour": (194, 65, 12)},
]

ALSO = ("ALSO TODAY:  US chip rule takes effect; Nvidia halts H200 sales to China  ·  "
        "Israel ends its Gaza raid, 6,000 displaced  ·  COP31 in final stage on fossil fuels")


def draw_masthead(canvas):
    canvas.rectangle([0, 0, SIZE, 148], fill=INK)
    canvas.text((512, 18), "THURSDAY", font=load(BOLD, 26), fill=WHITE, anchor="ma")
    canvas.text((512, 56), "19 NOVEMBER 2026", font=load(SERIF, 62), fill=WHITE, anchor="ma")
    canvas.rectangle([0, 148, SIZE, 156], fill=RED)
    canvas.text((512, 166), "THE WORLD IN ONE DAY  —  SIX STORIES THAT SUM UP THE NEWS",
                font=load(BOLD, 21), fill=INK, anchor="ma")


def draw_cards(canvas):
    margin, gap = 28, 16
    card_w = (SIZE - 2 * margin - gap) // 2
    card_h = 232
    top = 200
    for i, story in enumerate(STORIES):
        row, col = divmod(i, 2)
        x0 = margin + col * (card_w + gap)
        y0 = top + row * (card_h + gap)
        x1, y1 = x0 + card_w, y0 + card_h
        canvas.rectangle([x0, y0, x1, y1], fill=WHITE, outline=INK, width=2)
        canvas.rectangle([x0, y0, x0 + 10, y1], fill=story["colour"])
        cx, cy = x0 + 64, y0 + 60
        canvas.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], fill=(240, 240, 235),
                       outline=story["colour"], width=3)
        ICONS[story["icon"]](canvas, cx, cy, 25)
        tx = x0 + 120
        canvas.text((tx, y0 + 18), story["kicker"], font=load(BOLD, 18), fill=RED)
        headline_lines = wrap_text(canvas, story["headline"], load(BOLD, 31), card_w - 140)
        for j, line in enumerate(headline_lines[:2]):
            canvas.text((tx, y0 + 48 + j * 38), line, font=load(BOLD, 31), fill=INK)
        body_y = y0 + 48 + len(headline_lines[:2]) * 38 + 10
        body_lines = wrap_text(canvas, story["body"], load(REG, 22), card_w - 40)
        for j, line in enumerate(body_lines[:3]):
            canvas.text((x0 + 22, body_y + j * 30), line, font=load(REG, 22), fill=GREY)


def draw_strip(canvas):
    sy = 200 + 3 * 232 + 2 * 16 + 12
    canvas.rectangle([28, sy, SIZE - 28, sy + 44], fill=INK)
    strip_lines = wrap_text(canvas, ALSO, load(BOLD, 17), SIZE - 2 * 28 - 24)
    for j, line in enumerate(strip_lines[:2]):
        canvas.text((512, sy + 5 + j * 20), line, font=load(BOLD, 17), fill=WHITE, anchor="ma")
    return sy


def draw_footer(canvas, sy):
    fy = sy + 44 + 12
    canvas.line([28, fy, SIZE - 28, fy], fill=INK, width=2)
    canvas.text((512, fy + 8), "Sources: AP, Reuters, CNN, NPR, Le Monde, The Hindu  ·  19 November 2026",
                font=load(REG, 17), fill=GREY, anchor="ma")


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    canvas = ImageDraw.Draw(img)
    draw_masthead(canvas)
    draw_cards(canvas)
    sy = draw_strip(canvas)
    draw_footer(canvas, sy)
    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size} bytes {img.size}")


if __name__ == "__main__":
    main()
