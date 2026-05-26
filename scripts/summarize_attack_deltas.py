#!/usr/bin/env python3
"""Build identity-vs-attacked delta tables for selected formal attacks."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from selected_attack_matrix import SELECTED_ATTACKS, default_count_for  # noqa: E402


DEFAULT_IDENTITY_ROOT = Path("/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522")
DEFAULT_ATTACK_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")
IDENTITY_DIRS = {
    "cross": "cross",
    "gsd_cifar10": "gsd_cifar10",
    "mas_grdh": "mas_grdh",
    "mddm_128_pilot": "mddm_128_pilot",
    "pulsar": "pulsar",
}
BIT_METHODS = {"gsd_cifar10", "mas_grdh", "mddm_128_pilot", "pulsar"}
IMAGE_METHODS = {"cross", "rgs"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity-root", default=str(DEFAULT_IDENTITY_ROOT))
    parser.add_argument("--attack-root", default=str(DEFAULT_ATTACK_ROOT))
    parser.add_argument("--output", default="")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(out):
        return None
    return out


def sample_id(row: dict[str, str]) -> int | None:
    try:
        return int(row.get("sample_index", ""))
    except ValueError:
        return None


def metric_name_for(method: str) -> str:
    if method in BIT_METHODS:
        return "bit_accuracy"
    if method in IMAGE_METHODS:
        return "recovery_psnr"
    return "metric"


def load_metric_map(directory: Path, method: str) -> tuple[dict[int, float], int, int]:
    metric_name = metric_name_for(method)
    values: dict[int, float] = {}
    rows = read_rows(directory / "identity_results.csv")
    failures = read_rows(directory / "identity_failures.csv")
    for row in rows:
        idx = sample_id(row)
        value = as_float(row.get(metric_name))
        if idx is not None and value is not None:
            values[idx] = value
    for row in failures:
        idx = sample_id(row)
        if idx is not None:
            values[idx] = 0.0
    return values, len(rows), len(failures)


def find_attack_dir(root: Path, spec) -> Path | None:
    matches = sorted(root.glob(f"{spec.method}_{spec.name_part}_*"))
    matches = [
        path
        for path in matches
        if path.is_dir()
        and not path.name.endswith(".running")
        and ((path / "identity_results.csv").exists() or (path / "identity_failures.csv").exists())
    ]
    return matches[-1] if matches else None


def mean(values: list[float]) -> float | str:
    return statistics.mean(values) if values else ""


def ci95(values: list[float]) -> float | str:
    if len(values) < 2:
        return ""
    return 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def fmt(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.6f}"
    return value


def summarize_spec(identity_root: Path, attack_root: Path, spec) -> dict[str, object]:
    identity_dir = identity_root / IDENTITY_DIRS[spec.method]
    attack_dir = find_attack_dir(attack_root, spec)
    identity_values, identity_rows, identity_failures = load_metric_map(identity_dir, spec.method)
    if attack_dir is None:
        attack_values: dict[int, float] = {}
        attack_rows = 0
        attack_failures = 0
        attack_dir_text = ""
    else:
        attack_values, attack_rows, attack_failures = load_metric_map(attack_dir, spec.method)
        attack_dir_text = str(attack_dir)

    overlap_ids = sorted(set(identity_values) & set(attack_values))
    identity_overlap = [identity_values[idx] for idx in overlap_ids]
    attack_overlap = [attack_values[idx] for idx in overlap_ids]
    deltas = [base - attacked for base, attacked in zip(identity_overlap, attack_overlap)]
    baseline_mean = mean(identity_overlap)
    attacked_mean = mean(attack_overlap)
    if isinstance(baseline_mean, float) and isinstance(attacked_mean, float):
        delta_mean: float | str = baseline_mean - attacked_mean
        relative_drop: float | str = delta_mean / baseline_mean if baseline_mean else ""
    else:
        delta_mean = ""
        relative_drop = ""
    target = default_count_for(spec.method)
    return {
        "method": spec.method,
        "attack": spec.attack,
        "factor": spec.factor,
        "label": spec.label,
        "metric": metric_name_for(spec.method),
        "target": target,
        "overlap": len(overlap_ids),
        "identity_rows": identity_rows,
        "identity_failures": identity_failures,
        "identity_failure_rate": identity_failures / target if target else "",
        "attack_rows": attack_rows,
        "attack_failures": attack_failures,
        "attack_failure_rate": attack_failures / target if target else "",
        "identity_overlap_mean": baseline_mean,
        "attack_overlap_mean": attacked_mean,
        "delta_mean": delta_mean,
        "delta_ci95": ci95(deltas),
        "relative_drop": relative_drop,
        "attack_dir": attack_dir_text,
        "note": spec.note,
    }


def main() -> int:
    args = parse_args()
    identity_root = Path(args.identity_root).resolve()
    attack_root = Path(args.attack_root).resolve()
    summaries = [summarize_spec(identity_root, attack_root, spec) for spec in SELECTED_ATTACKS]
    fields = [
        "method",
        "attack",
        "factor",
        "label",
        "metric",
        "target",
        "overlap",
        "identity_rows",
        "identity_failures",
        "identity_failure_rate",
        "attack_rows",
        "attack_failures",
        "attack_failure_rate",
        "identity_overlap_mean",
        "attack_overlap_mean",
        "delta_mean",
        "delta_ci95",
        "relative_drop",
        "attack_dir",
        "note",
    ]
    output = Path(args.output).resolve() if args.output else attack_root / "selected_attack_deltas.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({field: fmt(row.get(field, "")) for field in fields})

    print(f"identity_root: {identity_root}")
    print(f"attack_root: {attack_root}")
    print(f"delta_csv: {output}")
    print(f"{'method':16s} {'attack':10s} {'overlap':>8s} {'metric':14s} {'base':>10s} {'attacked':>10s} {'drop':>10s}")
    for row in summaries:
        print(
            f"{row['method']:16s} {row['attack']:10s} {str(row['overlap']):>8s} {row['metric']:14s} "
            f"{fmt(row['identity_overlap_mean']):>10s} {fmt(row['attack_overlap_mean']):>10s} {fmt(row['delta_mean']):>10s}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
