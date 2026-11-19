#!/usr/bin/env python3
"""Compose the 19 November 2026 front page as a 1024x1024 PNG.

The page is built block by block: a masthead that makes the date the loudest
thing on the sheet, an illustrated lead, a paired second tier, a strip of
hard figures, then a three-column brief file. Every text block is measured
with the font it will be drawn in before it is placed, so nothing overlaps
and nothing is clipped. Region counts under the masthead are computed from
the story list itself, so the arithmetic on the page always adds up.

Deterministic: no clock, no randomness, no network.

Usage: python3 build.py [out.png]
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26                      # outer margin
INK = (18, 18, 20)
MID = (74, 71, 66)
FAINT = (128, 124, 116)
HAIR = (203, 198, 188)
PAPER = (250, 249, 245)
RED = (150, 26, 26)
BLUE = (26, 52, 96)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_cache = {}


def face(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def width(text, font):
    box = font.getbbox(text)
    return box[2] - box[0]


def wrap(text, font, measure, first=None):
    """Greedy wrap; `first` lets the opening line use a narrower measure."""
    limit = first if first is not None else measure
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = word if not line else line + " " + word
        if width(trial, font) <= limit or not line:
            line = trial
        else:
            lines.append(line)
            line = word
            limit = measure
    if line:
        lines.append(line)
    return lines


def block(draw, text, font, x, y, measure, fill, leading, first=None, align="left"):
    """Draw wrapped text and return the y just below its last line."""
    for line in wrap(text, font, measure, first):
        w = width(line, font)
        dx = x + (measure - w) // 2 if align == "center" else x
        draw.text((dx, y), line, font=font, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, colour=HAIR, thick=1):
    draw.rectangle([x0, y, x1, y + thick - 1], fill=colour)


# ---------------------------------------------------------------- masthead --

def masthead(draw, data):
    y = M
    label = "THE DAY IN ONE PAGE"
    draw.text((M, y + 2), label, font=face(SANS_B, 13), fill=RED)
    tag = data["day"].split(",")[-1].strip().upper()
    tw = width(tag, face(SANS_R, 12))
    draw.text((W - M - tw, y + 3), tag, font=face(SANS_R, 12), fill=FAINT)
    y += 22

    # The date is the headline: one line, filling the full measure.
    size = 104
    while size > 34 and width(data["dateline"], face(SERIF_B, size)) > W - 2 * M:
        size -= 1
    font = face(SERIF_B, size)
    draw.text((M, y - 8), data["dateline"], font=font, fill=INK)
    y += size + 2

    draw.text((M, y), "World news of Thursday 19 November 2026, from the wires of that day",
              font=face(SERIF_I, 15), fill=MID)
    y += 24
    rule(draw, M, y, W - M, INK, 3)
    return y + 9


def region_index(draw, data, y):
    """Tabs whose counts are derived from the stories, never typed in."""
    tally = {}
    order = []
    for item in [data["lead"]] + data["second"] + data["briefs"]:
        key = item["region"]
        if key not in tally:
            tally[key] = 0
            order.append(key)
        tally[key] += 1

    x = M
    font = face(SANS_B, 11)
    cap = face(SANS_R, 10)
    for key in order:
        text = "%s %d" % (key, tally[key])
        w = width(text, font) + 16
        draw.rectangle([x, y, x + w, y + 19], fill=BLUE)
        draw.text((x + 8, y + 3), text, font=font, fill=PAPER)
        x += w + 5
    total = sum(tally.values())
    note = "%d stories" % total
    nw = width(note, cap)
    if x + nw + 10 < W - M:
        draw.text((W - M - nw, y + 4), note, font=cap, fill=FAINT)
    else:
        y += 24
        draw.text((W - M - nw, y + 4), note, font=cap, fill=FAINT)
        y += 18
    return y + 26, tally


# -------------------------------------------------------------------- lead --

def art_summit(draw, box, flag=True):
    """A dusk skyline with a low sun: the summit venue, abstractly."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 232, 219))
    draw.ellipse([x1 - 54, y0 + 8, x1 - 14, y0 + 48], fill=(206, 150, 84))
    tops = [(0.00, 0.52), (0.07, 0.40), (0.13, 0.47), (0.19, 0.30), (0.26, 0.44),
            (0.33, 0.36), (0.40, 0.50), (0.47, 0.24), (0.55, 0.42), (0.62, 0.34),
            (0.69, 0.49), (0.76, 0.28), (0.84, 0.45), (0.92, 0.38)]
    span = x1 - x0
    for i, (frac, top) in enumerate(tops):
        bx = x0 + int(frac * span)
        bw = max(8, int(span * (0.09 if i % 2 else 0.06)))
        bt = y0 + int((y1 - y0) * top)
        draw.rectangle([bx, bt, min(bx + bw, x1), y1], fill=(44, 48, 62))
        rows = max(1, (y1 - bt) // 9)
        for ry in range(rows):
            for rx in range(2):
                if (i + ry + rx) % 3:
                    px = bx + 3 + rx * 5
                    py = bt + 5 + ry * 9
                    if px + 2 < min(bx + bw, x1) and py + 3 < y1:
                        draw.rectangle([px, py, px + 2, py + 3], fill=(232, 200, 132))
    if flag:
        draw.rectangle([x0, y1 - 3, x1, y1], fill=(30, 34, 46))


def art_bars(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(242, 238, 228))
    n = 7
    gap = 4
    bw = ((x1 - x0) - gap * (n + 1)) // n
    heights = [0.35, 0.55, 0.48, 0.72, 0.62, 0.85, 0.95]
    base = y1 - 6
    for i, frac in enumerate(heights):
        bx = x0 + gap + i * (bw + gap)
        top = base - int((base - y0 - 8) * frac)
        draw.rectangle([bx, top, bx + bw, base], fill=RED if i >= 4 else (150, 60, 52))
    rule(draw, x0 + 3, base + 1, x1 - 3, (150, 140, 128), 1)


def art_donut(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(240, 240, 236))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 8
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 58, 92))
    r2 = int(r * 0.60)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(240, 240, 236))
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 60, fill=(198, 92, 60))
    draw.ellipse([cx - int(r * 0.55), cy - int(r * 0.55),
                  cx + int(r * 0.55), cy + int(r * 0.55)], fill=(240, 240, 236))


def lead_block(draw, data, y):
    lead = data["lead"]
    art_w = 244
    text_w = W - 2 * M - art_w - 16
    top = y

    draw.text((M, y), lead["kicker"], font=face(SANS_B, 12), fill=RED)
    y += 17
    hfont = face(SERIF_B, 33)
    y = block(draw, lead["headline"], hfont, M, y, text_w, INK, 35)
    y += 2
    dfont = face(SERIF_R, 12)
    yend = block(draw, lead["standfirst"], dfont, M, y, text_w, MID, 16)

    art_summit(draw, [W - M - art_w, top + 2, W - M, yend - 2])
    return max(yend, top + 130) + 10


def second_tier(draw, data, y):
    cards = data["second"]
    gap = 16
    cw = (W - 2 * M - gap) // 2
    art_w = 44
    text_w = cw - art_w - 8
    bottoms = []
    for i, card in enumerate(cards):
        cx = M + i * (cw + gap)
        draw.text((cx, y), card["region"], font=face(SANS_B, 10), fill=BLUE)
        yy = y + 14
        yy = block(draw, card["headline"], face(SERIF_B, 21), cx, yy, text_w, INK, 23)
        yy += 2
        yy = block(draw, card["dek"], face(SERIF_R, 10), cx, yy, text_w, MID, 13)
        box = [cx + cw - art_w, y + 16, cx + cw, y + 16 + art_w]
        if card["art"] == "bars":
            art_bars(draw, box)
        else:
            art_donut(draw, box)
        bottoms.append(yy)
    y = max(bottoms) + 8
    rule(draw, M, y, W - M, HAIR, 1)
    return y + 8


def figures_strip(draw, data, y):
    figs = data["figures"]
    n = len(figs)
    cw = (W - 2 * M) // n
    draw.rectangle([M, y, W - M, y + 52], fill=(238, 235, 227))
    for i, fig in enumerate(figs):
        cx = M + i * cw + 8
        draw.text((cx, y + 7), fig["value"], font=face(SERIF_B, 21), fill=RED)
        block(draw, fig["caption"], face(SANS_R, 9), cx, y + 32, cw - 14, MID, 10)
    return y + 58


def brief_file(draw, data, y, bottom):
    """Flow briefs into four columns balanced by measured height."""
    briefs = data["briefs"]
    cols = 4
    gutter = 14
    cw = (W - 2 * M - gutter * (cols - 1)) // cols
    hfont = face(SERIF_B, 15)
    dfont = face(SERIF_R, 11)

    def measure(item):
        h = 10
        h += 16 * len(wrap(item["headline"], hfont, cw))
        h += 1
        h += 12 * len(wrap(item["dek"], dfont, cw))
        return h + 6

    heights = [measure(i) for i in briefs]
    n = len(briefs)
    # Split into four contiguous runs minimising the tallest column.
    INF = float("inf")
    best = [[INF] * (cols + 1) for _ in range(n + 1)]
    cut = [[0] * (cols + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for k in range(1, cols + 1):
        for end in range(1, n + 1):
            for start in range(k - 1, end):
                run = sum(heights[start:end]) + 7 * (end - start - 1)
                cand = max(best[start][k - 1], run)
                if cand < best[end][k]:
                    best[end][k] = cand
                    cut[end][k] = start
    bounds = [n]
    e = n
    for k in range(cols, 0, -1):
        e = cut[e][k]
        bounds.append(e)
    bounds.reverse()
    groups = [briefs[bounds[i]:bounds[i + 1]] for i in range(cols)]

    ends = []
    for c, chunk in enumerate(groups):
        cx = M + c * (cw + gutter)
        yy = y
        for i, item in enumerate(chunk):
            if i:
                rule(draw, cx, yy, cx + cw, HAIR, 1)
                yy += 6
            draw.text((cx, yy), item["region"], font=face(SANS_B, 8), fill=BLUE)
            yy += 10
            yy = block(draw, item["headline"], hfont, cx, yy, cw, INK, 16)
            yy += 1
            yy = block(draw, item["dek"], dfont, cx, yy, cw, MID, 12)
            yy += 6
        ends.append(yy)
    if max(ends) > bottom:
        print("warning: briefs end at %d, below %d" % (max(ends), bottom))
    return ends


def footer(draw, y):
    rule(draw, M, y, W - M, INK, 2)
    draw.text((M, y + 6), "Compiled from the reporting of 19 November 2026."
              " Contested claims are attributed to the side that made them.",
              font=face(SERIF_I, 10), fill=FAINT)
    tag = "make.fun \u00b7 news-image-20261119"
    tw = width(tag, face(SANS_R, 9))
    draw.text((W - M - tw, y + 7), tag, font=face(SANS_R, 9), fill=FAINT)

def build(src, out):
    with open(src, encoding="utf-8") as handle:
        data = json.load(handle)
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    y = masthead(draw, data)
    y, tally = region_index(draw, data, y)
    y = lead_block(draw, data, y)
    rule(draw, M, y, W - M, HAIR, 1)
    y += 8
    y = second_tier(draw, data, y)
    y = figures_strip(draw, data, y)
    bottom = H - M - 26
    brief_file(draw, data, y, bottom)
    footer(draw, bottom)

    print("regions:", ", ".join("%s=%d" % kv for kv in tally.items()),
          "| total", sum(tally.values()))
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build(os.path.join(here, "stories.json"),
          sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png"))
