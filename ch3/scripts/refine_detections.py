"""한글 주석 버전: YOLO 감지 JSON을 신뢰도/클래스 기준으로 정제한다."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Refine detection JSON by confidence and class filters.")
    parser.add_argument("--input", type=Path, required=True, help="Source JSON produced by export_detections.py")
    parser.add_argument("--output", type=Path, required=True, help="Destination JSON file")
    parser.add_argument("--min-conf", type=float, default=0.0, help="Minimum confidence threshold (inclusive)")
    parser.add_argument(
        "--classes",
        type=str,
        default=None,
        help="Comma-separated class filter (accepts names and/or numeric ids).",
    )
    parser.add_argument(
        "--drop-empty",
        action="store_true",
        help="Skip images with zero detections after filtering.",
    )
    parser.add_argument(
        "--sort-desc",
        action="store_true",
        help="Sort detections by confidence descending (default keeps original order).",
    )
    return parser.parse_args()


def load_json(path: Path) -> list[dict[str, Any]]:
    """JSON 파일을 로드하고 리스트로 반환한다."""
    if not path.is_file():
        raise FileNotFoundError(f"Input JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_class_filter(spec: str | None) -> tuple[set[int], set[str]]:
    """클래스 필터 문자열을 id 집합/이름 집합으로 분리한다."""
    if spec is None:
        return set(), set()
    ids: set[int] = set()
    names: set[str] = set()
    for item in spec.split(","):
        token = item.strip()
        if not token:
            continue
        try:
            ids.add(int(token))
            continue
        except ValueError:
            names.add(token.lower())
    return ids, names


def detection_passes(
    detection: dict[str, Any],
    min_conf: float,
    allowed_ids: set[int],
    allowed_names: set[str],
) -> bool:
    """감지가 필터 조건을 통과하는지 판단한다."""
    conf = detection.get("confidence")
    conf_value = float(conf) if conf is not None else 0.0
    if conf_value < min_conf:
        return False

    if not allowed_ids and not allowed_names:
        return True

    class_id = detection.get("class_id")
    class_name = detection.get("class_name")

    if allowed_ids and isinstance(class_id, int) and class_id in allowed_ids:
        return True
    if allowed_names and isinstance(class_name, str) and class_name.lower() in allowed_names:
        return True

    return False


def refine_records(
    records: list[dict[str, Any]],
    min_conf: float,
    allowed_ids: set[int],
    allowed_names: set[str],
    drop_empty: bool,
    sort_desc: bool,
) -> list[dict[str, Any]]:
    """전체 이미지 레코드에 대해 필터링을 적용한다."""
    refined: list[dict[str, Any]] = []
    for record in records:
        detections = record.get("detections", [])
        filtered = [
            det
            for det in detections
            if detection_passes(det, min_conf, allowed_ids, allowed_names)
        ]

        if sort_desc:
            filtered.sort(key=lambda d: float(d.get("confidence") or 0.0), reverse=True)

        if drop_empty and not filtered:
            continue

        new_record = {
            "image": record.get("image"),
            "image_path": record.get("image_path"),
            "width": record.get("width"),
            "height": record.get("height"),
            "detections": filtered,
            "meta": {
                "num_detections": len(filtered),
                "num_original": len(detections),
                "min_conf_applied": min_conf,
            },
        }

        if allowed_ids or allowed_names:
            new_record["meta"]["class_filter"] = sorted(
                [*map(str, sorted(allowed_ids)), *sorted(allowed_names)]
            )

        refined.append(new_record)
    return refined


def main() -> int:
    """스크립트 진입점: 감지 JSON을 정제하고 저장한다."""
    args = parse_args()

    try:
        records = load_json(args.input)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    allowed_ids, allowed_names = parse_class_filter(args.classes)

    refined_records = refine_records(
        records,
        min_conf=args.min_conf,
        allowed_ids=allowed_ids,
        allowed_names=allowed_names,
        drop_empty=args.drop_empty,
        sort_desc=args.sort_desc,
    )

    if not refined_records:
        print("[WARN] No records remaining after refinement.", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(refined_records, indent=2), encoding="utf-8")
    print(f"Saved refined detections to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
