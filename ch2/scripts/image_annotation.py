"""한글 주석 버전: YOLO 결과를 참고해 정적 이미지에 박스/라벨을 그리는 스크립트."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import cv2


# 기본 출력 이미지 경로(생략 시 이 경로로 저장)
DEFAULT_OUTPUT_PATH = Path("data/outputs/ch2/annotated.jpg")


def parse_bbox(value: str | None) -> tuple[int, int, int, int] | None:
    """문자열로 전달된 박스 좌표를 정수 튜플로 변환한다."""
    if value is None:
        return None
    try:
        x1_str, y1_str, x2_str, y2_str = value.split(",")
        coords = tuple(int(v.strip()) for v in (x1_str, y1_str, x2_str, y2_str))
    except ValueError as err:
        raise argparse.ArgumentTypeError("--bbox must be four integers separated by commas.") from err
    x1, y1, x2, y2 = coords
    if x1 >= x2 or y1 >= y2:
        raise argparse.ArgumentTypeError("Bounding box must satisfy x1 < x2 and y1 < y2.")
    return coords


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Draw YOLO-inspired ROI overlays on an image.")
    parser.add_argument("--source", type=Path, required=True, help="Input image path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output image path (default: data/outputs/ch2/annotated.jpg).",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="YOLO ROI",
        help="Label text displayed near the bounding box.",
    )
    parser.add_argument(
        "--bbox",
        type=parse_bbox,
        default=None,
        help="Optional YOLO bounding box as x1,y1,x2,y2 (pixels).",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.15,
        help="Fallback fractional margin for synthetic bounding boxes when --bbox is omitted.",
    )
    parser.add_argument(
        "--timestamp-format",
        type=str,
        default="%Y-%m-%d %H:%M:%S",
        help="Datetime format string for the footer timestamp.",
    )
    return parser.parse_args()


def compute_box(width: int, height: int, margin_ratio: float) -> tuple[int, int, int, int]:
    """폭/높이 대비 마진 비율을 적용해 임시 박스를 계산한다."""
    margin_ratio = min(max(margin_ratio, 0.0), 0.4)
    margin_x = int(width * margin_ratio)
    margin_y = int(height * margin_ratio)
    x1, y1 = margin_x, margin_y
    x2, y2 = width - margin_x, height - margin_y
    return x1, y1, x2, y2


def main() -> int:
    """스크립트 진입점: 이미지에 박스를 그리고 저장한다."""
    args = parse_args()

    if not args.source.is_file():
        raise SystemExit(f"Source image not found: {args.source}")

    # 원본 이미지 로드
    image = cv2.imread(str(args.source))
    if image is None:
        raise SystemExit(f"Failed to read image: {args.source}")

    # YOLO 박스가 주어지지 않으면 마진 비율로 생성
    height, width = image.shape[:2]
    if args.bbox is None:
        x1, y1, x2, y2 = compute_box(width, height, args.margin)
    else:
        x1, y1, x2, y2 = args.bbox

    # 시각화용 복사본 생성
    annotated = image.copy()
    cv2.rectangle(annotated, (x1, y1), (x2, y2), color=(0, 180, 255), thickness=3)

    center = ((x1 + x2) // 2, (y1 + y2) // 2)
    cv2.circle(annotated, center, radius=8, color=(0, 255, 0), thickness=-1)

    label_position = (x1, max(y1 - 12, 24))
    cv2.putText(
        annotated,
        args.label,
        label_position,
        fontFace=cv2.FONT_HERSHEY_DUPLEX,
        fontScale=0.9,
        color=(255, 255, 255),
        thickness=2,
    )

    timestamp = datetime.now().strftime(args.timestamp_format)
    footer_y = min(y2 + 30, height - 12)
    cv2.putText(
        annotated,
        timestamp,
        (x1, footer_y),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.7,
        color=(200, 200, 200),
        thickness=2,
    )

    output_path = args.output
    # 출력 경로 확보 후 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), annotated):
        raise SystemExit(f"Failed to write annotated image: {output_path}")

    print("Annotation completed")
    print(f"  Input : {args.source}")
    print(f"  Output: {output_path}")
    print(f"  Box   : {(x1, y1, x2, y2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
