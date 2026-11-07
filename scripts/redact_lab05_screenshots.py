#!/usr/bin/env python3
"""Re-apply privacy crops for lab05 PNGs from maintainer source uploads."""
from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path("lab-walkthrough-screenshots/lab05")
OUT = Path("assets/img/lab05")


def discovery(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im = im.crop((0, 72, w, h))
    w, _ = im.size
    dr = ImageDraw.Draw(im)
    dr.rectangle((200, 100, 450, 145), fill=(230, 232, 235))
    dr.rectangle((int(w * 0.82), 0, w, 48), fill=(230, 232, 235))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)


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


if __name__ == "__main__":
    main()
