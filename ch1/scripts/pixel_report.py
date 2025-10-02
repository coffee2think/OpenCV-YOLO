"""한글 주석 버전: 이미지 픽셀 통계를 출력하고 로그로 저장하는 스크립트."""

from __future__ import annotations

import argparse
import sys
from io import StringIO
from pathlib import Path
from textwrap import indent

import cv2
import numpy as np


# 기본 로그 파일 경로(생략 시 자동 저장)
DEFAULT_LOG_PATH = Path("logs/ch1_pixel_report.txt")


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Generate a pixel-level report for an image.")
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source image (jpg/png/webp).",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=5,
        help="Number of sample points per axis for the pixel grid display (>=1).",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Destination file for the report (set to '-' to disable logging).",
    )
    return parser.parse_args()


def load_image(path: Path) -> np.ndarray:
    """이미지를 로드하고 실패 시 예외를 발생시킨다."""
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Unable to load image: {path}")
    return image


def format_pixel(value: np.ndarray) -> str:
    """픽셀 값을 사람이 읽기 쉬운 문자열로 변환한다."""
    if value.ndim == 0:
        return f"({int(value):3d})"
    channels = [int(channel) for channel in value]
    formatted = ", ".join(f"{c:3d}" for c in channels)
    return f"({formatted})"


def sample_grid(image: np.ndarray, grid_size: int) -> list[str]:
    """이미지 전체에서 균등 간격으로 픽셀을 샘플링한다."""
    height, width = image.shape[:2]
    ys = np.linspace(0, height - 1, grid_size, dtype=int)
    xs = np.linspace(0, width - 1, grid_size, dtype=int)

    rows: list[str] = []
    for y in ys:
        samples = [format_pixel(image[y, x]) for x in xs]
        rows.append("  ".join(samples))
    return rows


def mean_color(image: np.ndarray) -> np.ndarray:
    """이미지의 평균 색상(또는 밝기)을 계산한다."""
    if image.ndim == 2:
        return np.array([float(image.mean())])
    channels = image.reshape(-1, image.shape[2]).mean(axis=0)
    return channels


def build_report(image: np.ndarray, source: Path, grid_size: int) -> str:
    """픽셀 통계와 샘플 그리드를 포함한 보고서를 문자열로 생성한다."""
    buffer = StringIO()
    height, width = image.shape[:2]
    channels = 1 if image.ndim == 2 else image.shape[2]

    buffer.write("=== SmartCam Mini · Chapter 1 Pixel Report ===\n")
    buffer.write(f"Source: {source}\n")
    buffer.write(f"Resolution: {width} x {height}\n")
    buffer.write(f"Channels: {channels}\n")
    buffer.write(f"Data type: {image.dtype}\n")

    mean_bgr = mean_color(image)
    if channels == 1:
        buffer.write(f"Mean intensity: {mean_bgr[0]:.2f}\n")
    else:
        buffer.write(
            "Mean BGR: "
            + ", ".join(f"{value:.2f}" for value in mean_bgr)
            + "\n"
        )

    if grid_size >= 1:
        buffer.write("\nSample pixel grid (top-left to bottom-right):\n")
        grid_rows = sample_grid(image, grid_size)
        buffer.write(indent("\n".join(grid_rows), prefix="  "))
        buffer.write("\n")

    min_val = image.min()
    max_val = image.max()
    buffer.write(f"\nPixel value range: {int(min_val)} to {int(max_val)}\n")

    return buffer.getvalue()


def maybe_write_log(report: str, log_path: Path) -> None:
    """로그 파일 경로가 지정되면 내용을 저장한다."""
    if str(log_path) == "-":
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(report, encoding="utf-8")


def main() -> int:
    """메인 실행부: 보고서를 생성하고 출력/저장한다."""
    args = parse_args()

    if args.grid_size < 1:
        print("[ERROR] --grid-size must be at least 1.", file=sys.stderr)
        return 1

    source_path: Path = args.source
    if not source_path.is_file():
        print(f"[ERROR] Source image not found: {source_path}", file=sys.stderr)
        return 1

    try:
        image = load_image(source_path)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    # 콘솔 출력 및 로그 저장용 보고서 생성
    report = build_report(image, source_path, args.grid_size)
    print(report)

    try:
        maybe_write_log(report, args.log)
    except OSError as err:
        print(f"[WARN] Failed to write log file: {err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
