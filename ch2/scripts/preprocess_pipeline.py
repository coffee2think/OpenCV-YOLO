"""한글 주석 버전: 단일 이미지에 리사이즈→그레이스케일→블러→에지 추출을 수행."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2


# 중간 산출물을 저장할 기본 폴더
DEFAULT_OUTPUT_DIR = Path("data/outputs/ch2")


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Run resize -> gray -> blur -> edges pipeline on an image.")
    parser.add_argument("--source", type=Path, required=True, help="Input image path.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where intermediate outputs will be stored.",
    )
    parser.add_argument("--scale", type=float, default=0.6, help="Resize scale factor (0 < scale <= 1.5).")
    parser.add_argument(
        "--blur-kernel",
        type=int,
        default=9,
        help="Gaussian blur kernel size (odd positive integer).",
    )
    parser.add_argument(
        "--canny-thresholds",
        type=str,
        default="80,160",
        help="Low,High thresholds for Canny edge detector (comma separated).",
    )
    return parser.parse_args()


def validate_args(scale: float, kernel: int) -> None:
    """리사이즈 배율과 블러 커널 조건을 검증한다."""
    if not (0 < scale <= 1.5):
        raise ValueError("--scale must be between 0 and 1.5 (exclusive of 0).")
    if kernel <= 0 or kernel % 2 == 0:
        raise ValueError("--blur-kernel must be an odd positive integer.")


def parse_canny_thresholds(value: str) -> tuple[int, int]:
    """문자열로 전달된 캐니 임계값을 (low, high) 정수쌍으로 변환한다."""
    try:
        low_str, high_str = value.split(",")
        low = int(low_str.strip())
        high = int(high_str.strip())
    except ValueError as err:
        raise ValueError("--canny-thresholds must be two integers separated by a comma.") from err
    if low < 0 or high < 0 or low >= high:
        raise ValueError("Canny thresholds must be non-negative integers with low < high.")
    return low, high


def load_image(path: Path) -> cv2.Mat:
    """이미지를 로드하고 실패 시 예외를 발생시킨다."""
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Unable to load image: {path}")
    return image


def save_image(path: Path, image: cv2.Mat) -> None:
    """결과 이미지를 저장하고 실패 시 예외를 발생시킨다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Failed to write image: {path}")


def main() -> int:
    """스크립트 진입점: 전처리 파이프라인을 순차 실행한다."""
    args = parse_args()

    try:
        validate_args(args.scale, args.blur_kernel)
        canny_low, canny_high = parse_canny_thresholds(args.canny_thresholds)
    except ValueError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 입력 이미지 존재 여부 확인
    if not args.source.is_file():
        print(f"[ERROR] Source image not found: {args.source}", file=sys.stderr)
        return 1

    try:
        image = load_image(args.source)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    stem = args.source.stem

    # 1단계: 리사이즈
    resized = cv2.resize(image, None, fx=args.scale, fy=args.scale, interpolation=cv2.INTER_AREA)
    resized_path = args.output_dir / f"{stem}_step1_resized.png"
    try:
        save_image(resized_path, resized)
    except OSError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 2단계: 그레이스케일 변환
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray_path = args.output_dir / f"{stem}_step2_gray.png"
    try:
        save_image(gray_path, gray)
    except OSError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 3단계: 가우시안 블러
    blur = cv2.GaussianBlur(gray, (args.blur_kernel, args.blur_kernel), sigmaX=0)
    blur_path = args.output_dir / f"{stem}_step3_blur.png"
    try:
        save_image(blur_path, blur)
    except OSError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 4단계: 캐니 에지 추출
    edges = cv2.Canny(blur, threshold1=canny_low, threshold2=canny_high)
    edges_path = args.output_dir / f"{stem}_edges.png"
    try:
        save_image(edges_path, edges)
    except OSError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    print("Preprocessing pipeline complete:")
    print(f"  Resize : {resized_path}")
    print(f"  Gray   : {gray_path}")
    print(f"  Blur   : {blur_path}")
    print(f"  Edges  : {edges_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
