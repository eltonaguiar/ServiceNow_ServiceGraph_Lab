#!/usr/bin/env python3
"""Re-apply privacy crops for lab05 PNGs from maintainer source uploads."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytesseract
from PIL import Image, ImageDraw

SRC = Path("lab-walkthrough-screenshots/lab05")
OUT = Path("assets/img/lab05")

# Cropped list view: one data row (~y 74–108 at x≈215–420 is Object ID on walkthrough capture).
_CROP_TOP = 72
_OBJ_BOX = (178, 64, 440, 114)  # covers full Object ID cell on walkthrough capture
_TOP_RIGHT = lambda w: (int(w * 0.78), 0, w, 52)

INSTANCE_ID = re.compile(r"i-0|i-[0-9a-f]{8,}", re.I)


def discovery(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im = im.crop((0, _CROP_TOP, w, h))
    w, h = im.size
    dr = ImageDraw.Draw(im)
    dr.rectangle(_OBJ_BOX, fill=(230, 232, 235))
    x0, y0, x1, y1 = _TOP_RIGHT(w)
    dr.rectangle((x0, y0, x1, y1), fill=(230, 232, 235))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)
    text = pytesseract.image_to_string(im)
    if INSTANCE_ID.search(text):
        sys.exit("redaction failed: instance id still visible to OCR")


def crop_top(src: Path, dst: Path, top: int = 100) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im.crop((0, top, w, h)).save(dst, optimize=True)


def copy(src: Path, dst: Path) -> None:
    Image.open(src).convert("RGB").save(dst, optimize=True)


def main() -> None:
    discovery(SRC / "discovery-source.png", OUT / "vm-discovery-source.png")
    crop_top(SRC / "ire-ident-rule-1.png", OUT / "vm-identification-rule.png")
    copy(SRC / "ire-dependent-rels.png", OUT / "vm-dependent-relationships.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
