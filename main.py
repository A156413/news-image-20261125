#!/usr/bin/env python3
"""news-image-20261125: draw one front-page image summing up the world news
of Wednesday 25 November 2026. Pure PIL, no network, deterministic output.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (20, 20, 24)
NAVY = (18, 33, 61)
NAVY2 = (28, 52, 92)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
DUSK_TOP = (46, 52, 88)
DUSK_BOT = (214, 128, 64)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def center(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def skyline(draw, x0, y_base, heights, color, width=46, gap=8):
    x = x0
    for h in heights:
        draw.rectangle([x, y_base - h, x + width, y_base], fill=color)
        x += width + gap
    return x


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.rectangle([0, 108, W, 112], fill=GOLD)
    center(d, W // 2, 12, "THE WORLD TODAY", font(FSB, 54), (247, 243, 234))
    center(d, W // 2, 76, "WEDNESDAY  •  25 NOVEMBER 2026  •  ONE DAY, ONE PICTURE",
           font(FB, 20), GOLD)

    # ---------- lead story: Riyadh tower strike ----------
    # Drawn on its own layer so the burst and smoke are clipped to the panel.
    lx, ly, lw, lh = 24, 128, 976, 330
    panel = Image.new("RGB", (lw, lh))
    p = ImageDraw.Draw(panel, "RGBA")
    for i in range(lh):
        t = i / lh
        r = int(DUSK_TOP[0] + (DUSK_BOT[0] - DUSK_TOP[0]) * t)
        g = int(DUSK_TOP[1] + (DUSK_BOT[1] - DUSK_TOP[1]) * t)
        b = int(DUSK_TOP[2] + (DUSK_BOT[2] - DUSK_TOP[2]) * t)
        p.line([(0, i), (lw, i)], fill=(r, g, b))
    # sun low on the horizon
    p.ellipse([820, 172, 940, 292], fill=(255, 196, 110))
    # city skyline silhouettes
    def skyline_p(x0, y_base, heights, color, width=46, gap=8):
        x = x0
        for h in heights:
            p.rectangle([x, y_base - h, x + width, y_base], fill=color)
            x += width + gap
    skyline_p(10, lh - 78, [90, 130, 70, 150, 100, 60], (30, 32, 56))
    skyline_p(430, lh - 78, [80, 120, 65, 95], (38, 40, 66))
    # PIF tower: tall, tapering, twisted crown (right of centre)
    tx = 620
    p.polygon([(tx, 40), (tx + 84, 40), (tx + 72, lh - 78),
               (tx + 12, lh - 78)], fill=(24, 26, 48))
    p.polygon([(tx, 40), (tx + 84, 40), (tx + 62, 8),
               (tx + 22, 8)], fill=(52, 56, 92))
    for wy in range(60, lh - 90, 16):
        p.line([(tx + 8, wy), (tx + 76, wy)], fill=(255, 196, 110), width=2)
    # jagged explosion burst at the tower crown
    import math
    cx, cy = tx + 42, 26
    pts = []
    for k in range(24):
        ang = math.radians(k * 15)
        rr = 78 if k % 2 == 0 else 34
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    p.polygon(pts, fill=(255, 120, 20))
    p.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(255, 170, 40))
    p.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 230, 120))
    # smoke plume drifting up-left, kept inside the panel
    p.ellipse([cx - 150, cy - 18, cx - 70, cy + 44], fill=(70, 66, 70))
    p.ellipse([cx - 110, cy - 26, cx - 20, cy + 30], fill=(88, 84, 88))
    p.ellipse([cx - 60, cy - 14, cx + 20, cy + 40], fill=(70, 66, 70))
    img.paste(panel, (lx, ly))
    d = ImageDraw.Draw(img, "RGBA")
    # caption strip over the bottom of the panel
    d.rectangle([lx, ly + lh - 78, lx + lw, ly + lh], fill=(0, 0, 0))
    d.rectangle([lx, ly + lh - 78, lx + lw, ly + lh - 74], fill=RED)
    center(d, W // 2, ly + lh - 68, "MISSILES HIT RIYADH'S TALLEST TOWER",
           font(FB, 34), (255, 255, 255))
    center(d, W // 2, ly + lh - 30,
           "Houthi strike wounds 11 at the Saudi wealth-fund HQ — second hit in a week",
           font(FR, 19), (220, 220, 220))
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=3)

    # ---------- three stories ----------
    stories = [
        {
            "tag": "UKRAINE  •  THE WAR AT SEA",
            "head": "KYIV ADMITS\nBALTIC SHIP STRIKE",
            "deck": "Zelenskiy confirms the drone hit on a Russian cargo vessel in the Gulf of Finland; Moscow calls it \u201cterrorism\u201d.",
            "kind": "sea",
        },
        {
            "tag": "CHINA  •  POLITICS",
            "head": "BEIJING PROBES\nTOP OFFICIAL",
            "deck": "Shock corruption inquiry opens into Politburo member and Shanghai party chief Chen Jining.",
            "kind": "beijing",
        },
        {
            "tag": "COURTS  •  TECH",
            "head": "HUAWEI GUILTY\nOF STEALING SECRETS",
            "deck": "A US jury convicts the Chinese tech giant of trade-secret theft and bank fraud.",
            "kind": "court",
        },
    ]
    col_w, gap = 312, 20
    x = 24
    y0, panel_h = 482, 150
    for s in stories:
        # illustrated panel
        px, py = x, y0
        if s["kind"] == "sea":
            for i in range(panel_h):
                t = i / panel_h
                d.line([(px, py + i), (px + col_w, py + i)],
                       fill=(int(16 + 120 * t), int(60 + 90 * t), int(110 + 60 * t)))
            d.ellipse([px + 220, py + 12, px + 262, py + 54], fill=(255, 220, 150))
            d.polygon([(px + 60, py + 108), (px + 250, py + 108), (px + 225, py + 132),
                       (px + 85, py + 132)], fill=(40, 44, 60))
            d.rectangle([px + 130, py + 78, px + 140, py + 108], fill=(40, 44, 60))
            d.rectangle([px + 170, py + 88, px + 178, py + 108], fill=(40, 44, 60))
            d.ellipse([px + 96, py + 60, px + 116, py + 80], fill=(255, 150, 40))
            for wx in range(px + 10, px + col_w - 10, 26):
                d.arc([wx, py + 128, wx + 22, py + 140], 180, 360, fill=(200, 220, 240), width=2)
        elif s["kind"] == "beijing":
            for i in range(panel_h):
                t = i / panel_h
                d.line([(px, py + i), (px + col_w, py + i)],
                       fill=(int(120 + 60 * t), int(20 + 20 * t), int(20 + 10 * t)))
            d.rectangle([px + 66, py + 66, px + 246, py + 138], fill=(90, 8, 8))
            d.polygon([(px + 46, py + 66), (px + 266, py + 66), (px + 156, py + 30)],
                      fill=(140, 16, 16))
            for cx2 in range(px + 86, px + 240, 28):
                d.rectangle([cx2, py + 84, cx2 + 14, py + 118], fill=(255, 210, 90))
            d.ellipse([px + 246, py + 14, px + 282, py + 50], fill=(255, 210, 90))
        else:  # court / chip
            for i in range(panel_h):
                t = i / panel_h
                d.line([(px, py + i), (px + col_w, py + i)],
                       fill=(int(30 + 40 * t), int(34 + 40 * t), int(52 + 50 * t)))
            d.rectangle([px + 106, py + 34, px + 206, py + 116], fill=(16, 20, 34))
            d.rectangle([px + 118, py + 46, px + 194, py + 104], fill=(60, 90, 150))
            for gx in range(px + 130, px + 190, 16):
                d.line([(gx, py + 58), (gx, py + 92)], fill=(140, 180, 255), width=2)
            for gy in range(py + 58, py + 92, 16):
                d.line([(px + 130, gy), (px + 182, gy)], fill=(140, 180, 255), width=2)
            for pin in range(4):
                d.rectangle([px + 118 + pin * 26, py + 26, px + 126 + pin * 26, py + 34],
                            fill=(200, 210, 230))
                d.rectangle([px + 118 + pin * 26, py + 116, px + 126 + pin * 26, py + 124],
                            fill=(200, 210, 230))
            d.text((px + 226, py + 100), "§", font=font(FSB, 44), fill=(255, 210, 90))
        d.rectangle([px, py, px + col_w, py + panel_h], outline=INK, width=2)
        # tag
        d.text((x, y0 + panel_h + 12), s["tag"], font=font(FB, 15), fill=RED)
        # headline (two lines)
        hy = y0 + panel_h + 36
        for line in s["head"].split("\n"):
            d.text((x, hy), line, font=font(FB, 25), fill=INK)
            hy += 30
        # deck
        dy = hy + 6
        for line in wrap(d, s["deck"], font(FR, 17), col_w):
            d.text((x, dy), line, font=font(FR, 17), fill=(60, 60, 66))
            dy += 22
        x += col_w + gap

    # ---------- also today ----------
    by = 862
    d.rectangle([24, by, 1000, by + 2], fill=INK)
    d.text((24, by + 12), "ALSO TODAY", font=font(FB, 18), fill=RED)
    briefs = [
        "Nvidia chief Jensen Huang returns as CEO — and says he is in therapy",
        "Trump awards Rudy Giuliani the Medal of Freedom",
        "Senegal regain the Africa Cup title after a CAS ruling",
    ]
    yy = by + 42
    for b in briefs:
        d.text((24, yy), "•", font=font(FB, 18), fill=RED)
        for line in wrap(d, b, font(FR, 18), 940):
            d.text((48, yy), line, font=font(FR, 18), fill=INK)
            yy += 24
        yy += 2

    # ---------- footer ----------
    d.rectangle([0, 992, W, H], fill=NAVY)
    center(d, W // 2, 999, "25 NOVEMBER 2026  —  THE DAY IN ONE IMAGE",
           font(FB, 17), (247, 243, 234))

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img.save(os.path.join(outdir, "entry.png"))
    print("wrote", os.path.join(outdir, "entry.png"), img.size)


if __name__ == "__main__":
    main()
