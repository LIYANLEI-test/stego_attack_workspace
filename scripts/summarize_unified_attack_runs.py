#!/usr/bin/env python3
"""Summarize unified attack result directories under a run root."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path


KNOWN_METHODS = ["mddm_128_pilot", "gsd_cifar10", "mas_grdh", "pulsar", "cross"]
TARGET_COUNTS = {
    "cross": 100,
    "gsd_cifar10": 500,
    "mas_grdh": 500,
    "pulsar": 500,
    "mddm_128_pilot": 50,
}
ATTACKS = {"resize", "storage", "jpeg", "mblur", "gblur"}


@dataclass(frozen=True)
class ParsedName:
    method: str
    attack: str
    factor: str
    target_count: int | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Unified attack run root under /data2.")
    parser.add_argument("--format", choices=["table", "csv"], default="table")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_dir_name(name: str) -> ParsedName | None:
    for method in KNOWN_METHODS:
        prefix = f"{method}_"
        if not name.startswith(prefix):
            continue
        rest = name[len(prefix) :]
        parts = rest.split("_")
        if not parts or parts[0] not in ATTACKS:
            return None
        attack = parts[0]
        if attack == "storage":
            target_count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else TARGET_COUNTS.get(method)
            return ParsedName(method, attack, "", target_count)
        if len(parts) < 2:
            return None
        target_count = int(parts[-1]) if parts[-1].isdigit() else TARGET_COUNTS.get(method)
        factor = ".".join(parts[1:-1]) if parts[-1].isdigit() else ".".join(parts[1:])
        return ParsedName(method, attack, factor, target_count)
    return None


def as_float(value: object) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(out):
        return None
    return out


def has_empty_payload(row: dict[str, str]) -> bool:
    for field in ("bit_count", "payload_bits"):
        value = as_float(row.get(field))
        if value == 0:
            return True
    return False


def mean_field(rows: list[dict[str, str]], field: str) -> float | None:
    usable = [row for row in rows if field != "bit_accuracy" or not has_empty_payload(row)]
    values = [value for row in usable if (value := as_float(row.get(field))) is not None]
    return statistics.mean(values) if values else None


def exact_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if str(row.get("exact_match", "")).lower() == "true")


def summarize_dir(path: Path) -> dict[str, object] | None:
    parsed = parse_dir_name(path.name)
    if parsed is None:
        return None
    result_rows = read_rows(path / "identity_results.csv")
    failure_rows = read_rows(path / "identity_failures.csv")
    total = len(result_rows) + len(failure_rows)
    metric_name = "bit_accuracy"
    metric_value = mean_field(result_rows, "bit_accuracy")
    if metric_value is None:
        metric_name = "recovery_psnr"
        metric_value = mean_field(result_rows, "recovery_psnr")
    attack_psnr = mean_field(result_rows, "attack_psnr")
    runtime_s = mean_field(result_rows + failure_rows, "runtime_s")
    empty_payload_rows = sum(1 for row in result_rows if has_empty_payload(row))
    sample_ids = [row.get("sample_index", "") for row in result_rows + failure_rows]
    duplicate_ids = len(sample_ids) - len(set(sample_ids))
    target = parsed.target_count or TARGET_COUNTS.get(parsed.method, 0)
    return {
        "name": path.name,
        "method": parsed.method,
        "attack": parsed.attack,
        "factor": parsed.factor,
        "target": target,
        "rows": len(result_rows),
        "failures": len(failure_rows),
        "total": total,
        "complete": total >= target if target else False,
        "duplicate_ids": duplicate_ids,
        "metric": metric_name,
        "metric_mean": metric_value,
        "attack_psnr_mean": attack_psnr,
        "exact": exact_count(result_rows),
        "empty_payload_rows": empty_payload_rows,
        "runtime_s_mean": runtime_s,
    }


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    summaries = []
    for path in sorted(root.iterdir()):
        if path.name == "logs" or path.name.endswith(".running") or not path.is_dir():
            continue
        summary = summarize_dir(path)
        if summary is not None:
            summaries.append(summary)

    fields = [
        "method",
        "attack",
        "factor",
        "target",
        "rows",
        "failures",
        "total",
        "complete",
        "duplicate_ids",
        "metric",
        "metric_mean",
        "attack_psnr_mean",
        "exact",
        "empty_payload_rows",
        "runtime_s_mean",
        "name",
    ]
    if args.format == "csv":
        writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({field: row.get(field, "") for field in fields})
        return 0

    print(f"root: {root}")
    print(f"dirs: {len(summaries)}")
    print(
        f"{'method':18s} {'attack':7s} {'factor':6s} {'done':>9s} "
        f"{'fail':>5s} {'empty':>5s} {'metric':14s} {'mean':>10s} {'atk_psnr':>10s} {'dup':>3s} name"
    )
    for row in summaries:
        done = f"{row['total']}/{row['target']}"
        print(
            f"{str(row['method']):18s} {str(row['attack']):7s} {str(row['factor']):6s} "
            f"{done:>9s} {str(row['failures']):>5s} {str(row['empty_payload_rows']):>5s} {str(row['metric']):14s} "
            f"{fmt(row['metric_mean']):>10s} {fmt(row['attack_psnr_mean']):>10s} "
            f"{str(row['duplicate_ids']):>3s} {row['name']}"
        )
    incomplete = [row for row in summaries if not row["complete"]]
    duplicate = [row for row in summaries if row["duplicate_ids"]]
    print(f"incomplete_dirs: {len(incomplete)}")
    print(f"duplicate_id_dirs: {len(duplicate)}")
    return 1 if duplicate else 0


if __name__ == "__main__":
    raise SystemExit(main())
