"""한글 주석 버전: HSV 임계값으로 색상 마스크를 적용하는 데모."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


# 마스크 결과를 저장할 기본 폴더
DEFAULT_OUTPUT_DIR = Path("data/outputs/ch2")


def parse_hsv_triplet(value: str) -> np.ndarray:
    """쉼표로 구분된 HSV 문자열을 uint8 배열로 변환한다."""
    try:
        parts = [int(part.strip()) for part in value.split(",")]
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"Invalid HSV triplet '{value}': {err}") from err
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("HSV triplet must contain exactly 3 integers.")
    return np.array(parts, dtype=np.uint8)


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Apply an HSV color mask to isolate a region.")
    parser.add_argument("--source", type=Path, required=True, help="Input image path.")
    parser.add_argument(
        "--lower-hsv",
        type=parse_hsv_triplet,
        required=True,
        help="Lower HSV bound as comma-separated ints (e.g., 35,80,80).",
    )
    parser.add_argument(
        "--upper-hsv",
        type=parse_hsv_triplet,
        required=True,
        help="Upper HSV bound as comma-separated ints (e.g., 90,255,255).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for saving the mask results.",
    )
    return parser.parse_args()


def load_image(path: Path) -> np.ndarray:
    """이미지를 로드하고 실패 시 예외를 발생시킨다."""
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Unable to load image: {path}")
    return image


def main() -> int:
    """스크립트 진입점: HSV 마스크를 적용하고 파일로 저장한다."""
    args = parse_args()

    if not args.source.is_file():
        print(f"[ERROR] Source image not found: {args.source}", file=sys.stderr)
        return 1

    try:
        image = load_image(args.source)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # BGR → HSV 변환 후 원하는 범위만 마스킹
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, args.lower_hsv, args.upper_hsv)
    masked = cv2.bitwise_and(image, image, mask=mask)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = args.source.stem
    before_path = output_dir / f"{stem}_mask_before.png"
    mask_path = output_dir / f"{stem}_mask.png"
    after_path = output_dir / f"{stem}_mask_after.png"

    success = True
    success &= cv2.imwrite(str(before_path), image)
    success &= cv2.imwrite(str(mask_path), mask)
    success &= cv2.imwrite(str(after_path), masked)
    if not success:
        print("[ERROR] Failed to write one or more output files.", file=sys.stderr)
        return 1

    print("Color mask generated with the following ranges:")
    print(f"  Lower HSV: {args.lower_hsv.tolist()}")
    print(f"  Upper HSV: {args.upper_hsv.tolist()}")
    print("Saved results:")
    print(f"  Original : {before_path}")
    print(f"  Mask     : {mask_path}")
    print(f"  Masked   : {after_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
