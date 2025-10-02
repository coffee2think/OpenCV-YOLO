"""한글 주석 버전: Ch1에서 OpenCV 환경을 점검하고
회색조/블러 이미지를 저장하는 도우미 스크립트입니다."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2


# 기본 출력 디렉터리(회색조 및 블러 이미지를 저장)
DEFAULT_OUTPUT_DIR = Path("data/outputs/ch1")


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="Validate OpenCV install and export grayscale/blurred images.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source image (jpg/png/webp).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where processed images will be stored.",
    )
    parser.add_argument(
        "--blur-kernel",
        type=int,
        default=11,
        help="Gaussian blur kernel size (odd positive integer).",
    )
    return parser.parse_args()


def ensure_kernel(kernel: int) -> int:
    """블러 커널 값이 홀수이면서 양수인지 확인한다."""
    if kernel <= 0 or kernel % 2 == 0:
        raise ValueError("--blur-kernel must be an odd positive integer.")
    return kernel


def load_image(path: Path) -> cv2.Mat:
    """이미지 파일을 로드하고 실패 시 예외를 발생시킨다."""
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Unable to load image: {path}")
    return image


def build_output_paths(output_dir: Path, source_path: Path) -> tuple[Path, Path]:
    """원본 파일명을 기반으로 회색조/블러 출력 경로를 생성한다."""
    stem = source_path.stem
    gray_path = output_dir / f"{stem}_gray.png"
    blur_path = output_dir / f"{stem}_blur.png"
    return gray_path, blur_path


def main() -> int:
    """스크립트 진입점: 환경 점검 및 이미지 전처리를 수행한다."""
    args = parse_args()

    try:
        ensure_kernel(args.blur_kernel)
    except ValueError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    source_path: Path = args.source
    if not source_path.is_file():
        print(f"[ERROR] Source image not found: {source_path}", file=sys.stderr)
        return 1

    print(f"OpenCV version: {cv2.__version__}")
    print(f"Loading image: {source_path}")
    try:
        image = load_image(source_path)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 회색조 변환 및 가우시안 블러 적용
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(image, (args.blur_kernel, args.blur_kernel), sigmaX=0)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    gray_path, blur_path = build_output_paths(output_dir, source_path)

    if not cv2.imwrite(str(gray_path), gray):
        print(f"[ERROR] Failed to write grayscale image: {gray_path}", file=sys.stderr)
        return 1
    if not cv2.imwrite(str(blur_path), blur):
        print(f"[ERROR] Failed to write blurred image: {blur_path}", file=sys.stderr)
        return 1

    # 저장 경로 로그
    print("Saved processed images:")
    print(f"  Grayscale: {gray_path}")
    print(f"  Blur     : {blur_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
