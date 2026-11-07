#!/usr/bin/env python3
"""Privacy redaction for lab04 walkthrough PNGs (VPC/dopt IDs; keep CIDR/counters)."""
from __future__ import annotations

import re
from pathlib import Path

import pytesseract
from PIL import Image, ImageDraw

SRC = Path("lab-walkthrough-screenshots")
DST = Path("assets/img/lab04")

REDACT_TEXT = re.compile(
    r"vpc[\-–][0-9a-zA-Z]+|dopt[\-–][0-9a-zA-Z]+|"
    r"10\.42\.0\.0/16\[vpc|172\.31\.0\.0/16\[vpc",
    re.I,
)


def pad(box: tuple[int, int, int, int], px: int = 4) -> tuple[int, int, int, int]:
    x, y, w, h = box
    return (max(0, x - px), max(0, y - px), w + 2 * px, h + 2 * px)


def fill_boxes(im: Image.Image, boxes: list[tuple[int, int, int, int]], color=(235, 237, 240)) -> None:
    dr = ImageDraw.Draw(im)
    for x, y, w, h in boxes:
        dr.rectangle((x, y, x + w, y + h), fill=color)


def ocr_redact_boxes(im: Image.Image) -> list[tuple[int, int, int, int]]:
    data = pytesseract.image_to_data(im, output_type=pytesseract.Output.DICT)
    boxes = []
    for i, text in enumerate(data["text"]):
        t = (text or "").strip()
        if not t:
            continue
        if REDACT_TEXT.search(t) or ("vpc" in t.lower() and re.search(r"vpc[\-–]", t, re.I)):
            boxes.append(pad((data["left"][i], data["top"][i], data["width"][i], data["height"][i]), 6))
    return boxes


def redact_aws_vpcs(im: Image.Image) -> None:
    boxes = ocr_redact_boxes(im)
    # OCR often misses one VPC id — cover the VPC ID column for both data rows.
    boxes.extend([(480, 232, 280, 85), (1720, 232, 170, 85)])
    fill_boxes(im, boxes)


def redact_vpc_success(im: Image.Image) -> None:
    # Keep CIDR in Name; redact only the [vpc-…] suffix and Object ID column.
    boxes = [
        (700, 88, 200, 28),
        (700, 116, 200, 28),
        (128, 92, 150, 22),
        (128, 120, 160, 22),
    ]
    fill_boxes(im, boxes)


def process(name: str, extra=None) -> None:
    src = SRC / name
    dst = DST / name
    im = Image.open(src).convert("RGB")
    if extra:
        extra(im)
    else:
        fill_boxes(im, ocr_redact_boxes(im))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, optimize=True)
    print("wrote", dst)


def main() -> None:
    process("datacenter.png")
    process("pending.png")
    process("vpc-transform.png")
    process("vpc-rerun.png")
    process("aws-vpcs.png", redact_aws_vpcs)
    process("vpc-success.png", redact_vpc_success)


if __name__ == "__main__":
    main()
