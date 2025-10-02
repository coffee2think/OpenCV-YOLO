"""한글 주석 버전: YOLO TXT 결과를 픽셀 좌표 JSON으로 변환하는 스크립트."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2


# 이미지 파일을 찾을 때 사용할 확장자 목록
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")


@dataclass
class Detection:
    """각 감지 객체 정보를 표현하는 데이터 구조."""

    class_id: int
    class_name: str | None
    confidence: float | None
    bbox_norm: tuple[float, float, float, float]
    bbox_pixels: tuple[int, int, int, int]


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Export YOLO TXT detections to JSON.")
    parser.add_argument("--runs-dir", type=Path, required=True, help="Directory containing YOLO outputs (images + labels).")
    parser.add_argument("--output", type=Path, required=True, help="Destination JSON file.")
    parser.add_argument(
        "--labels-dir",
        type=Path,
        default=None,
        help="Explicit labels directory (defaults to <runs-dir>/labels or first nested labels directory).",
    )
    parser.add_argument(
        "--class-names",
        type=Path,
        default=None,
        help="Optional text file with class names (one per line, index = class id).",
    )
    parser.add_argument(
        "--relative-paths",
        action="store_true",
        help="Store image_path relative to --runs-dir instead of absolute paths.",
    )
    return parser.parse_args()


def load_class_names(path: Path | None) -> list[str] | None:
    """클래스 이름 파일을 읽어 리스트로 반환한다."""
    if path is None:
        return None
    if not path.is_file():
        raise FileNotFoundError(f"Class names file not found: {path}")
    names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return names or None


def resolve_labels_dir(runs_dir: Path, override: Path | None) -> Path:
    """레이블 파일이 위치한 폴더를 탐색한다."""
    if override is not None:
        if not override.is_dir():
            raise FileNotFoundError(f"Labels directory not found: {override}")
        return override
    candidate = runs_dir / "labels"
    if candidate.is_dir():
        return candidate
    for path in runs_dir.rglob("labels"):
        if path.is_dir():
            return path
    raise FileNotFoundError(f"Could not locate a 'labels' directory under {runs_dir}")


def find_image_for_label(runs_dir: Path, label_path: Path) -> Path:
    """레이블 파일과 동일한 이름의 이미지를 찾는다."""
    stem = label_path.stem
    base_dir = label_path.parent.parent if label_path.parent.name == "labels" else runs_dir
    for directory in {runs_dir, base_dir}:
        for ext in IMAGE_EXTENSIONS:
            candidate = directory / f"{stem}{ext}"
            if candidate.is_file():
                return candidate
    # Search recursively as fallback
    for ext in IMAGE_EXTENSIONS:
        matches = list(runs_dir.rglob(f"{stem}{ext}"))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"Image for label not found: {stem}")


def clamp(value: float, min_value: float, max_value: float) -> float:
    """값을 min/max 범위로 제한한다."""
    return max(min_value, min(value, max_value))


def parse_label_line(line: str) -> tuple[int, float, float, float, float, float | None]:
    """YOLO TXT 한 줄을 파싱해 클래스/좌표/신뢰도를 반환한다."""
    parts = line.strip().split()
    if len(parts) < 5:
        raise ValueError("Label line must contain at least 5 values: class cx cy w h [conf]")
    class_id = int(float(parts[0]))
    cx = float(parts[1])
    cy = float(parts[2])
    w = float(parts[3])
    h = float(parts[4])
    confidence = float(parts[5]) if len(parts) > 5 else None
    return class_id, cx, cy, w, h, confidence


def convert_to_pixels(
    cx: float,
    cy: float,
    w: float,
    h: float,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    """정규화 좌표를 픽셀 단위 (x1,y1,x2,y2)로 변환한다."""
    x_center = cx * width
    y_center = cy * height
    box_w = w * width
    box_h = h * height
    x1 = clamp(x_center - box_w / 2, 0, width)
    y1 = clamp(y_center - box_h / 2, 0, height)
    x2 = clamp(x_center + box_w / 2, 0, width)
    y2 = clamp(y_center + box_h / 2, 0, height)
    return int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))


def iter_label_files(labels_dir: Path) -> Iterable[Path]:
    """레이블 폴더 아래의 TXT 파일을 순회한다."""
    yield from sorted(labels_dir.rglob("*.txt"))


def build_detection(
    class_id: int,
    class_names: list[str] | None,
    confidence: float | None,
    cx: float,
    cy: float,
    w: float,
    h: float,
    width: int,
    height: int,
) -> Detection:
    """정규화 좌표를 포함한 Detection 인스턴스를 생성한다."""
    class_name = None
    if class_names and 0 <= class_id < len(class_names):
        class_name = class_names[class_id]
    bbox_pixels = convert_to_pixels(cx, cy, w, h, width, height)
    return Detection(
        class_id=class_id,
        class_name=class_name,
        confidence=confidence,
        bbox_norm=(cx, cy, w, h),
        bbox_pixels=bbox_pixels,
    )


def detection_to_dict(det: Detection) -> dict:
    """Detection 객체를 JSON 직렬화 가능한 dict로 변환한다."""
    x1, y1, x2, y2 = det.bbox_pixels
    cx, cy, w, h = det.bbox_norm
    return {
        "class_id": det.class_id,
        "class_name": det.class_name,
        "confidence": det.confidence,
        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "bbox_norm": {"cx": cx, "cy": cy, "w": w, "h": h},
    }


def main() -> int:
    """스크립트 진입점: YOLO TXT를 JSON으로 변환한다."""
    args = parse_args()

    runs_dir = args.runs_dir
    if not runs_dir.is_dir():
        print(f"[ERROR] Runs directory not found: {runs_dir}", file=sys.stderr)
        return 1

    try:
        labels_dir = resolve_labels_dir(runs_dir, args.labels_dir)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    try:
        class_names = load_class_names(args.class_names)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    records: list[dict] = []
    # 각 레이블 파일을 순회하며 JSON 레코드 생성
    for label_file in iter_label_files(labels_dir):
        try:
            image_path = find_image_for_label(runs_dir, label_file)
        except FileNotFoundError as err:
            print(f"[WARN] {err}", file=sys.stderr)
            continue

        image = cv2.imread(str(image_path))
        if image is None:
            print(f"[WARN] Failed to load image for {label_file}", file=sys.stderr)
            continue
        height, width = image.shape[:2]

        detections: list[dict] = []
        # YOLO TXT 각 줄(감지 정보)을 파싱
        for raw_line in label_file.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            try:
                class_id, cx, cy, w, h, confidence = parse_label_line(raw_line)
                detection = build_detection(
                    class_id,
                    class_names,
                    confidence,
                    cx,
                    cy,
                    w,
                    h,
                    width,
                    height,
                )
                detections.append(detection_to_dict(detection))
            except ValueError as err:
                print(f"[WARN] Skipping malformed line in {label_file}: {err}", file=sys.stderr)

        # 이미지 단위 레코드 구성
        image_record = {
            "image": image_path.name,
            "image_path": str(image_path.relative_to(runs_dir) if args.relative_paths else image_path),
            "width": width,
            "height": height,
            "detections": detections,
        }
        records.append(image_record)

    if not records:
        print("[WARN] No detections exported; check the runs directory and label files.", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Exported {len(records)} image entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
