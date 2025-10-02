"""한글 주석 버전: 정제된 감지 JSON을 표 형태로 요약한다."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:  # pragma: no cover - handled at runtime
    pd = None  # type: ignore


def parse_args() -> argparse.Namespace:
    """CLI 인자를 정의하고 파싱한다."""
    parser = argparse.ArgumentParser(description="Create a summary table from detection JSON.")
    parser.add_argument("--input", type=Path, required=True, help="Refined detection JSON path")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output file (.csv or .json). If omitted, prints only.",
    )
    parser.add_argument(
        "--sort-by",
        type=str,
        default="num_detections",
        choices=["num_detections", "mean_confidence", "max_confidence"],
        help="Column used to sort the summary (descending).",
    )
    return parser.parse_args()


def load_detections(path: Path) -> list[dict]:
    """JSON 파일을 읽어 파이썬 객체로 변환한다."""
    if not path.is_file():
        raise FileNotFoundError(f"Input JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_dataframe(records: list[dict]):
    """감지 리스트를 pandas DataFrame으로 변환한다."""
    if pd is None:
        raise RuntimeError("pandas is required for detection_summary.py")

    rows = []
    for record in records:
        image = record.get("image")
        for det in record.get("detections", []):
            rows.append(
                {
                    "image": image,
                    "class_id": det.get("class_id"),
                    "class_name": det.get("class_name"),
                    "confidence": float(det.get("confidence") or 0.0),
                }
            )

    if not rows:
        return pd.DataFrame(columns=["class_id", "class_name", "confidence", "image"])

    return pd.DataFrame(rows)


def summarise(df, sort_by: str):
    """클래스별 통계(건수/평균/최대 신뢰도)를 계산한다."""
    if df.empty:
        return pd.DataFrame(columns=["class_display", "class_id", "num_detections", "mean_confidence", "max_confidence"])

    df = df.assign(
        class_display=df.apply(
            lambda row: row["class_name"] if row["class_name"] else f"class_{row['class_id']}",
            axis=1,
        )
    )

    summary = (
        df.groupby(["class_display", "class_id"], dropna=False)
        .agg(
            num_detections=("confidence", "size"),
            mean_confidence=("confidence", "mean"),
            max_confidence=("confidence", "max"),
        )
        .reset_index()
    )

    summary = summary.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
    return summary


def save_output(df, path: Path) -> None:
    """요약 결과를 CSV/JSON 파일로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
    elif suffix == ".json":
        df.to_json(path, orient="records", indent=2)
    else:
        raise ValueError("Unsupported output format; use .csv or .json")


def main() -> int:
    """스크립트 진입점: 감지 요약표를 출력/저장한다."""
    args = parse_args()

    try:
        records = load_detections(args.input)
    except FileNotFoundError as err:
        print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    if pd is None:
        print("[ERROR] pandas is required. Install with 'pip install pandas'.", file=sys.stderr)
        return 1

    df = build_dataframe(records)
    summary = summarise(df, sort_by=args.sort_by)

    if summary.empty:
        print("No detections to summarise.")
    else:
        print(
            summary.to_string(
                index=False,
                formatters={
                    "mean_confidence": "{:.3f}".format,
                    "max_confidence": "{:.3f}".format,
                },
            )
        )

    if args.output:
        try:
            save_output(summary, args.output)
        except ValueError as err:
            print(f"[ERROR] {err}", file=sys.stderr)
            return 1
        print(f"Summary saved to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
