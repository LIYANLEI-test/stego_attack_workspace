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

from selected_attack_matrix import (  # noqa: E402
    CALIBRATION_SAMPLE_COUNT,
    SELECTED_ATTACKS,
    attack_provenance_for,
    baseline_provenance_for,
    default_count_for,
    heldout_count_for,
)


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
    parser.add_argument(
        "--include-calibration",
        action="store_true",
        help="Include sample indices used for the 10-sample attack-parameter calibration.",
    )
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
    except (TypeError, ValueError):
        return None


def metric_name_for(method: str) -> str:
    if method in BIT_METHODS:
        return "bit_accuracy"
    if method in IMAGE_METHODS:
        return "recovery_psnr"
    return "metric"


def inferred_saved_attack_pair(directory: Path, method: str, row: dict[str, str]) -> bool:
    try:
        idx = int(row.get("sample_index", ""))
    except (TypeError, ValueError):
        return False
    if method == "cross":
        base = directory / "samples" / f"{idx:06d}"
        stego = base / "hide.png"
        attacked = sorted(base.glob("hide_*.png"))
    elif method == "gsd_cifar10":
        stego = directory / "images" / f"stego_{idx:06d}.png"
        attacked = sorted((directory / "images").glob(f"stego_{idx:06d}_*.png"))
    elif method in {"mas_grdh", "pulsar"}:
        stego = directory / "images" / f"{idx:06d}.png"
        attacked = sorted((directory / "images").glob(f"{idx:06d}_*.png"))
    else:
        return False
    return stego.exists() and len(attacked) == 1 and attacked[0].exists()


def has_saved_attack_pair(directory: Path, method: str, row: dict[str, str]) -> bool:
    stego = row.get("stego_path") or row.get("image_path")
    attacked = row.get("attacked_path")
    if stego and attacked and Path(stego).exists() and Path(attacked).exists():
        return True
    return inferred_saved_attack_pair(directory, method, row)


def load_metric_map(
    directory: Path,
    method: str,
    include_calibration: bool,
    attacked_run: bool,
) -> tuple[dict[int, float], int, int, int, set[int]]:
    metric_name = metric_name_for(method)
    values: dict[int, float] = {}
    rows = read_rows(directory / "identity_results.csv")
    failures = read_rows(directory / "identity_failures.csv")
    if not include_calibration:
        rows = [row for row in rows if (idx := sample_id(row)) is not None and idx >= CALIBRATION_SAMPLE_COUNT]
        failures = [
            row for row in failures if (idx := sample_id(row)) is not None and idx >= CALIBRATION_SAMPLE_COUNT
        ]
    for row in rows:
        idx = sample_id(row)
        value = as_float(row.get(metric_name))
        if idx is not None and value is not None:
            values[idx] = value
    successful_ids = set(values)
    scorable_failures = 0
    unscorable_failures = 0
    for row in failures:
        idx = sample_id(row)
        if idx is not None and (not attacked_run or has_saved_attack_pair(directory, method, row)):
            values[idx] = 0.0
            scorable_failures += 1
        elif idx is not None:
            unscorable_failures += 1
    return values, len(rows), scorable_failures, unscorable_failures, successful_ids


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


def summarize_spec(identity_root: Path, attack_root: Path, spec, include_calibration: bool) -> dict[str, object]:
    identity_dir = identity_root / IDENTITY_DIRS[spec.method]
    attack_dir = find_attack_dir(attack_root, spec)
    identity_values, identity_rows, identity_failures, identity_unscorable, identity_success_ids = load_metric_map(
        identity_dir, spec.method, include_calibration, attacked_run=False
    )
    if attack_dir is None:
        attack_values: dict[int, float] = {}
        attack_rows = 0
        attack_failures = 0
        attack_unscorable = 0
        attack_dir_text = ""
    else:
        attack_values, attack_rows, attack_failures, attack_unscorable, _ = load_metric_map(
            attack_dir, spec.method, include_calibration, attacked_run=True
        )
        attack_dir_text = str(attack_dir)

    overlap_ids = sorted(set(identity_values) & set(attack_values))
    identity_overlap = [identity_values[idx] for idx in overlap_ids]
    attack_overlap = [attack_values[idx] for idx in overlap_ids]
    deltas = [base - attacked for base, attacked in zip(identity_overlap, attack_overlap)]
    identity_success_overlap_ids = [idx for idx in overlap_ids if idx in identity_success_ids]
    identity_success_overlap = [identity_values[idx] for idx in identity_success_overlap_ids]
    attack_on_identity_success = [attack_values[idx] for idx in identity_success_overlap_ids]
    identity_success_deltas = [
        base - attacked for base, attacked in zip(identity_success_overlap, attack_on_identity_success)
    ]
    baseline_mean = mean(identity_overlap)
    attacked_mean = mean(attack_overlap)
    if isinstance(baseline_mean, float) and isinstance(attacked_mean, float):
        delta_mean: float | str = baseline_mean - attacked_mean
        relative_drop: float | str = delta_mean / baseline_mean if baseline_mean else ""
    else:
        delta_mean = ""
        relative_drop = ""
    clean_success_mean = mean(identity_success_overlap)
    attack_clean_success_mean = mean(attack_on_identity_success)
    conditional_delta_mean = mean(identity_success_deltas)
    target = default_count_for(spec.method) if include_calibration else heldout_count_for(spec.method)
    return {
        "method": spec.method,
        "attack": spec.attack,
        "factor": spec.factor,
        "label": spec.label,
        "baseline_provenance": baseline_provenance_for(spec.method),
        "attack_provenance": attack_provenance_for(spec),
        "metric": metric_name_for(spec.method),
        "target": target,
        "evaluation_split": "all_samples" if include_calibration else "heldout_excluding_calibration_0_9",
        "excluded_calibration_samples": 0 if include_calibration else CALIBRATION_SAMPLE_COUNT,
        "overlap": len(overlap_ids),
        "identity_rows": identity_rows,
        "identity_failures": identity_failures,
        "identity_unscorable_failures": identity_unscorable,
        "identity_failure_rate": identity_failures / target if target else "",
        "attack_rows": attack_rows,
        "attack_failures": attack_failures,
        "attack_unscorable_failures": attack_unscorable,
        "attack_failure_rate": attack_failures / target if target else "",
        "identity_overlap_mean": baseline_mean,
        "attack_overlap_mean": attacked_mean,
        "delta_mean": delta_mean,
        "delta_ci95": ci95(deltas),
        "relative_drop": relative_drop,
        "identity_success_overlap": len(identity_success_overlap_ids),
        "identity_success_mean": clean_success_mean,
        "attack_on_identity_success_mean": attack_clean_success_mean,
        "delta_on_identity_success_mean": conditional_delta_mean,
        "delta_on_identity_success_ci95": ci95(identity_success_deltas),
        "attack_dir": attack_dir_text,
        "note": spec.note,
    }


def main() -> int:
    args = parse_args()
    identity_root = Path(args.identity_root).resolve()
    attack_root = Path(args.attack_root).resolve()
    summaries = [
        summarize_spec(identity_root, attack_root, spec, args.include_calibration) for spec in SELECTED_ATTACKS
    ]
    fields = [
        "method",
        "attack",
        "factor",
        "label",
        "baseline_provenance",
        "attack_provenance",
        "metric",
        "target",
        "evaluation_split",
        "excluded_calibration_samples",
        "overlap",
        "identity_rows",
        "identity_failures",
        "identity_unscorable_failures",
        "identity_failure_rate",
        "attack_rows",
        "attack_failures",
        "attack_unscorable_failures",
        "attack_failure_rate",
        "identity_overlap_mean",
        "attack_overlap_mean",
        "delta_mean",
        "delta_ci95",
        "relative_drop",
        "identity_success_overlap",
        "identity_success_mean",
        "attack_on_identity_success_mean",
        "delta_on_identity_success_mean",
        "delta_on_identity_success_ci95",
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
