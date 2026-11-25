#!/usr/bin/env python3
"""Write the 25 November 2026 world-news image to /output/entry.png
for make.fun's 'news-image-20261125' bounty.

The poster was drawn by draw_poster.py in this repository (run locally,
where Pillow and the DejaVu fonts exist) and committed here as
entry.png. This entrypoint only copies that committed poster into the
graded output directory, using the standard library alone.

Why a copy: the v1 entrypoint drew the poster at runtime and the
grader's pinned python image carries neither Pillow nor the DejaVu
fonts, so its run exited 1 and the entry was rejected
(run_completes fail, submission 01a2107e). The 23 and 24 November
editions both used this copy pattern and passed.

The day's stories: a Houthi projectile hits Riyadh's PIF Tower
(11 wounded); Kyiv admits the Baltic drone strike on the Sparta II;
Beijing probes Politburo member Chen Jining; a US jury convicts
Huawei on 10 of 12 counts; plus Huang, Giuliani and Senegal briefs.
"""

import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
POSTER_PIXELS = 1024


def png_dimensions(path):
    # read the IHDR chunk of a PNG with the standard library
    # alone: 8-byte signature, then length, "IHDR", width, height
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != PNG_SIGNATURE or head[12:16] != b"IHDR":
        raise RuntimeError(f"{path} is not a PNG with an IHDR")
    return struct.unpack(">II", head[16:24])


def verify_poster(path):
    width, height = png_dimensions(path)
    if (width, height) != (POSTER_PIXELS, POSTER_PIXELS):
        raise RuntimeError(
            f"poster is {width}x{height}, not {POSTER_PIXELS} square")


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        raise RuntimeError(f"committed poster missing: {src}")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    if os.path.getsize(dst) != os.path.getsize(src):
        raise RuntimeError("entry.png copy is incomplete")
    verify_poster(dst)
    os.chmod(dst, 0o644)
    print("wrote", dst, f"{os.path.getsize(dst)} bytes",
          f"(from committed {os.path.getsize(src)} bytes)")


if __name__ == "__main__":
    main()
