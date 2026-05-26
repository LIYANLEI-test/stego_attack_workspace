#!/usr/bin/env python3
"""Aggregate selected-attack formal runs into paper-table CSVs."""

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

from identity_common import image_lpips, image_metrics  # noqa: E402
from selected_attack_matrix import SELECTED_ATTACKS, default_count_for  # noqa: E402


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")
BIT_METHODS = {"gsd_cifar10", "mas_grdh", "mddm_128_pilot", "pulsar"}
IMAGE_METHODS = {"cross", "rgs"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--output", default="")
    parser.add_argument("--method-counts", default="", help="Comma-separated target overrides, e.g. cross=100,gsd_cifar10=500.")
    parser.add_argument("--include-lpips", action="store_true", help="Compute LPIPS from saved images when not already present.")
    return parser.parse_args()


def parse_method_counts(raw: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not raw.strip():
        return counts
    for item in raw.split(","):
        if not item.strip():
            continue
        if "=" not in item:
            raise ValueError(f"invalid method-count item: {item!r}")
        method, value = item.split("=", 1)
        counts[method.strip()] = int(value.strip())
    return counts


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


def mean(values: list[float]) -> float | str:
    return statistics.mean(values) if values else ""


def stdev(values: list[float]) -> float | str:
    return statistics.stdev(values) if len(values) > 1 else ""


def ci95(values: list[float]) -> float | str:
    if len(values) < 2:
        return ""
    return 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def pair_paths(row: dict[str, str]) -> tuple[Path, Path] | None:
    stego = row.get("image_path") or row.get("stego_path")
    attacked = row.get("attacked_path")
    if not stego or not attacked:
        return None
    stego_path = Path(stego)
    attacked_path = Path(attacked)
    if not stego_path.exists() or not attacked_path.exists():
        return None
    return stego_path, attacked_path


def values_from_rows(rows: list[dict[str, str]], field: str) -> list[float]:
    return [value for row in rows if (value := as_float(row.get(field))) is not None]


def quality_values(rows: list[dict[str, str]], failures: list[dict[str, str]], device: str, include_lpips: bool):
    psnr_values: list[float] = []
    ssim_values: list[float] = []
    lpips_values: list[float] = []
    for row in rows + failures:
        pair = pair_paths(row)
        if pair is None:
            psnr = as_float(row.get("attack_psnr"))
            if psnr is not None:
                psnr_values.append(psnr)
            ssim = as_float(row.get("attack_ssim"))
            if ssim is not None:
                ssim_values.append(ssim)
            continue
        metrics = image_metrics(pair[0], pair[1])
        psnr = as_float(metrics.get("psnr"))
        if psnr is not None:
            psnr_values.append(psnr)
        ssim = as_float(metrics.get("ssim"))
        if ssim is not None:
            ssim_values.append(ssim)
        if include_lpips:
            lp = as_float(image_lpips(pair[0], pair[1], device=device))
            if lp is not None:
                lpips_values.append(lp)
    return psnr_values, ssim_values, lpips_values


def recovery_values(method: str, rows: list[dict[str, str]], failures: list[dict[str, str]]) -> tuple[str, list[float]]:
    if method in BIT_METHODS:
        values = values_from_rows(rows, "bit_accuracy")
        values.extend(0.0 for _ in failures)
        return "bit_accuracy", values
    if method in IMAGE_METHODS:
        values = values_from_rows(rows, "recovery_psnr")
        values.extend(0.0 for _ in failures)
        return "recovery_psnr", values
    return "metric", []


def summarize_one(root: Path, spec, device: str, include_lpips: bool, target_count: int) -> dict[str, object]:
    matches = sorted(root.glob(f"{spec.method}_{spec.name_part}_*"))
    matches = [
        path
        for path in matches
        if path.is_dir()
        and not path.name.endswith(".running")
        and ((path / "identity_results.csv").exists() or (path / "identity_failures.csv").exists())
    ]
    out_dir = matches[-1] if matches else root / f"{spec.method}_{spec.name_part}_MISSING"
    rows = read_rows(out_dir / "identity_results.csv")
    failures = read_rows(out_dir / "identity_failures.csv")
    metric_name, metric_values = recovery_values(spec.method, rows, failures)
    psnr_values, ssim_values, lpips_values = quality_values(rows, failures, device, include_lpips)
    total = len(rows) + len(failures)
    exact = sum(1 for row in rows if str(row.get("exact_match", "")).lower() == "true")
    return {
        "method": spec.method,
        "attack": spec.attack,
        "factor": spec.factor,
        "label": spec.label,
        "provenance": spec.provenance,
        "metric": metric_name,
        "rows": len(rows),
        "failures": len(failures),
        "total": total,
        "target": target_count,
        "complete": total >= target_count,
        "failure_rate": (len(failures) / target_count) if target_count else "",
        "exact": exact,
        "exact_rate": (exact / target_count) if target_count else "",
        "recovery_mean": mean(metric_values),
        "recovery_std": stdev(metric_values),
        "recovery_ci95": ci95(metric_values),
        "quality_psnr_mean": mean(psnr_values),
        "quality_psnr_std": stdev(psnr_values),
        "quality_psnr_ci95": ci95(psnr_values),
        "quality_ssim_mean": mean(ssim_values),
        "quality_lpips_mean": mean(lpips_values),
        "runtime_s_mean": mean(values_from_rows(rows + failures, "runtime_s")),
        "output_dir": str(out_dir),
        "note": spec.note,
    }


def fmt(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.6f}"
    return value


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    target_overrides = parse_method_counts(args.method_counts)
    summaries = [
        summarize_one(
            root,
            spec,
            args.device,
            args.include_lpips,
            target_overrides.get(spec.method, default_count_for(spec.method)),
        )
        for spec in SELECTED_ATTACKS
    ]
    fields = [
        "method",
        "attack",
        "factor",
        "label",
        "provenance",
        "metric",
        "rows",
        "failures",
        "total",
        "target",
        "complete",
        "failure_rate",
        "exact",
        "exact_rate",
        "recovery_mean",
        "recovery_std",
        "recovery_ci95",
        "quality_psnr_mean",
        "quality_psnr_std",
        "quality_psnr_ci95",
        "quality_ssim_mean",
        "quality_lpips_mean",
        "runtime_s_mean",
        "output_dir",
        "note",
    ]
    output = Path(args.output).resolve() if args.output else root / "selected_attack_summary.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({field: fmt(row.get(field, "")) for field in fields})

    print(f"root: {root}")
    print(f"summary_csv: {output}")
    print(
        f"{'method':16s} {'attack':10s} {'factor':12s} {'done':>9s} {'complete':>8s} "
        f"{'metric':14s} {'mean':>10s} {'psnr':>10s}"
    )
    for row in summaries:
        done = f"{row['total']}/{row['target']}"
        print(
            f"{row['method']:16s} {row['attack']:10s} {row['factor']:12s} {done:>9s} "
            f"{str(row['complete']):>8s} {row['metric']:14s} "
            f"{fmt(row['recovery_mean']):>10s} {fmt(row['quality_psnr_mean']):>10s}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
