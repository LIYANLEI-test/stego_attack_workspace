#!/usr/bin/env python3
"""Select attack settings closest to a target stego-vs-attacked PSNR."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


DEFAULT_SUMMARY = Path(
    "/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary.csv"
)
BIT_PAYLOAD_METHODS = {"gsd_cifar10", "mas_grdh", "mddm_128_pilot", "pulsar"}
IMAGE_PAYLOAD_METHODS = {"cross", "rgs"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary_csv", nargs="?", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--target-psnr", type=float, default=30.0)
    parser.add_argument("--tolerance", type=float, default=1.0)
    parser.add_argument("--lpips-max", type=float, default=None)
    parser.add_argument("--output", default="")
    parser.add_argument("--attack-summary-output", default="")
    parser.add_argument(
        "--exclude-method-from-summary",
        action="append",
        default=[],
        help="Exclude a method from the attack-family bit-payload summary.",
    )
    return parser.parse_args()


def as_float(value: object) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(out):
        return None
    return out


def as_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_valid_candidate(row: dict[str, str], lpips_max: float | None = None) -> bool:
    scored_total = as_int(row.get("scored_total"))
    if scored_total <= 0 or as_int(row.get("unscorable_failures")):
        return False
    if as_int(row.get("quality_psnr_n")) != scored_total:
        return False
    if as_int(row.get("quality_lpips_n")) != scored_total:
        return False
    psnr = as_float(row.get("quality_psnr_mean"))
    lpips = as_float(row.get("quality_lpips_mean"))
    if psnr is None or lpips is None:
        return False
    if lpips_max is not None and lpips > lpips_max:
        return False
    return True


def destruction_rate(row: dict[str, object]) -> float | None:
    if row.get("metric") != "bit_accuracy":
        return None
    metric = as_float(row.get("metric_mean"))
    if metric is None:
        return None
    return 1.0 - metric


def exact_destruction_rate(row: dict[str, object]) -> float | None:
    scored_total = as_int(row.get("scored_total"))
    if scored_total <= 0:
        return None
    return 1.0 - (as_int(row.get("exact")) / scored_total)


def reveal_failure_rate(row: dict[str, object]) -> float | None:
    scored_total = as_int(row.get("scored_total"))
    if scored_total <= 0:
        return None
    return as_int(row.get("failures")) / scored_total


def selection_key(row: dict[str, object], target_psnr: float) -> tuple[float, float, float]:
    psnr = as_float(row.get("quality_psnr_mean"))
    metric = as_float(row.get("metric_mean"))
    lpips = as_float(row.get("quality_lpips_mean"))
    if psnr is None:
        return (float("inf"), float("inf"), float("inf"))
    # Primary key is quality alignment. At essentially the same PSNR, choose the
    # stronger recovery degradation, then lower LPIPS.
    return (abs(psnr - target_psnr), metric if metric is not None else float("inf"), lpips or float("inf"))


def annotate_row(row: dict[str, str], target_psnr: float, tolerance: float) -> dict[str, object]:
    out: dict[str, object] = dict(row)
    psnr = as_float(row.get("quality_psnr_mean"))
    gap = abs((psnr or 0.0) - target_psnr) if psnr is not None else None
    out["target_psnr"] = target_psnr
    out["psnr_gap_abs"] = gap
    out["psnr_band_status"] = "inside" if gap is not None and gap <= tolerance else "outside"
    out["bit_destruction_rate"] = destruction_rate(out)
    out["exact_destruction_rate"] = exact_destruction_rate(out)
    out["reveal_failure_rate"] = reveal_failure_rate(out)
    if row.get("metric") == "bit_accuracy":
        out["comparison_metric"] = "bit_destruction_rate"
    elif row.get("metric") == "recovery_psnr":
        out["comparison_metric"] = "recovered_secret_psnr"
    else:
        out["comparison_metric"] = row.get("metric", "")
    return out


def select_rows(
    rows: list[dict[str, str]],
    target_psnr: float,
    tolerance: float,
    lpips_max: float | None = None,
) -> list[dict[str, object]]:
    selected: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if not is_valid_candidate(row, lpips_max):
            continue
        key = (row.get("method", ""), row.get("attack", ""))
        incumbent = selected.get(key)
        if incumbent is None or selection_key(row, target_psnr) < selection_key(incumbent, target_psnr):
            selected[key] = row
    return [
        annotate_row(row, target_psnr, tolerance)
        for row in sorted(selected.values(), key=lambda item: (item.get("method", ""), item.get("attack", "")))
    ]


def mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def summarize_bit_attacks(
    selected: list[dict[str, object]], excluded_methods: set[str] | None = None
) -> list[dict[str, object]]:
    excluded_methods = excluded_methods or set()
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in selected:
        method = str(row.get("method", ""))
        if method not in BIT_PAYLOAD_METHODS or method in excluded_methods:
            continue
        if row.get("metric") != "bit_accuracy":
            continue
        grouped.setdefault(str(row.get("attack", "")), []).append(row)

    summaries: list[dict[str, object]] = []
    for attack, rows in sorted(grouped.items()):
        psnr_values = [value for row in rows if (value := as_float(row.get("quality_psnr_mean"))) is not None]
        lpips_values = [value for row in rows if (value := as_float(row.get("quality_lpips_mean"))) is not None]
        gap_values = [value for row in rows if (value := as_float(row.get("psnr_gap_abs"))) is not None]
        destruction_values = [value for row in rows if (value := as_float(row.get("bit_destruction_rate"))) is not None]
        reveal_values = [value for row in rows if (value := as_float(row.get("reveal_failure_rate"))) is not None]
        exact_values = [value for row in rows if (value := as_float(row.get("exact_destruction_rate"))) is not None]
        summaries.append(
            {
                "attack": attack,
                "n_targets": len(rows),
                "methods": ";".join(str(row.get("method", "")) for row in rows),
                "params": ";".join(f"{row.get('method')}:{row.get('factor')}" for row in rows),
                "mean_quality_psnr": mean(psnr_values),
                "mean_psnr_gap_abs": mean(gap_values),
                "mean_quality_lpips": mean(lpips_values),
                "mean_bit_destruction_rate": mean(destruction_values),
                "mean_reveal_failure_rate": mean(reveal_values),
                "mean_exact_destruction_rate": mean(exact_values),
            }
        )
    return summaries


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: fmt(row.get(field, "")) for field in fields})


def print_selection(rows: list[dict[str, object]]) -> None:
    print(
        f"{'method':16s} {'attack':10s} {'factor':14s} {'psnr':>9s} "
        f"{'gap':>8s} {'lpips':>8s} {'metric':>12s} {'destroy':>10s} {'fail':>7s}"
    )
    for row in rows:
        print(
            f"{str(row.get('method', '')):16s} {str(row.get('attack', '')):10s} "
            f"{str(row.get('factor', '')):14s} {fmt(as_float(row.get('quality_psnr_mean'))):>9s} "
            f"{fmt(as_float(row.get('psnr_gap_abs'))):>8s} {fmt(as_float(row.get('quality_lpips_mean'))):>8s} "
            f"{str(row.get('comparison_metric', '')):>12s} "
            f"{fmt(as_float(row.get('bit_destruction_rate'))):>10s} "
            f"{fmt(as_float(row.get('reveal_failure_rate'))):>7s}"
        )


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    output = Path(args.output).resolve() if args.output else summary_csv.with_name("target_psnr_30_selection.csv")
    attack_summary_output = (
        Path(args.attack_summary_output).resolve()
        if args.attack_summary_output
        else summary_csv.with_name("target_psnr_30_attack_summary_bit_methods.csv")
    )
    selected = select_rows(read_rows(summary_csv), args.target_psnr, args.tolerance, args.lpips_max)
    attack_summary = summarize_bit_attacks(selected, set(args.exclude_method_from_summary))

    selection_fields = [
        "method",
        "attack",
        "factor",
        "target_psnr",
        "psnr_gap_abs",
        "psnr_band_status",
        "rows",
        "failures",
        "unscorable_failures",
        "scored_total",
        "metric",
        "metric_mean",
        "comparison_metric",
        "bit_destruction_rate",
        "exact_destruction_rate",
        "reveal_failure_rate",
        "quality_psnr_mean",
        "quality_lpips_mean",
        "quality_ssim_mean",
        "exact",
        "runtime_s_mean",
        "name",
    ]
    attack_summary_fields = [
        "attack",
        "n_targets",
        "methods",
        "params",
        "mean_quality_psnr",
        "mean_psnr_gap_abs",
        "mean_quality_lpips",
        "mean_bit_destruction_rate",
        "mean_reveal_failure_rate",
        "mean_exact_destruction_rate",
    ]
    write_csv(output, selected, selection_fields)
    write_csv(attack_summary_output, attack_summary, attack_summary_fields)

    print(f"summary_csv: {summary_csv}")
    print(f"target_psnr: {args.target_psnr:g} dB")
    print(f"tolerance: +/- {args.tolerance:g} dB")
    print(f"lpips_filter: {args.lpips_max if args.lpips_max is not None else 'none'}")
    print(f"selected_csv: {output}")
    print(f"attack_summary_csv: {attack_summary_output}")
    print_selection(selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
