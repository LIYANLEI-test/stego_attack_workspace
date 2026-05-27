#!/usr/bin/env python3
"""Audit selected attack summaries for paper-readiness constraints."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")
PSNR_MIN = 30.0
LPIPS_MAX = 0.10
MAIN_METHODS = {"cross", "gsd_cifar10", "mas_grdh", "pulsar"}
APPENDIX_METHODS = {"mddm_128_pilot"}
ADAPTED_PROVENANCE = {"adapted_attack"}
PILOT_PROVENANCE = {"native_third_party"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--summary", default="")
    parser.add_argument("--deltas", default="")
    parser.add_argument("--output-csv", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Deprecated compatibility flag; audits always retain incomplete selected rows.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row.get("method", ""), row.get("attack", ""), row.get("factor", ""))


def budget_status(row: dict[str, str]) -> tuple[str, str]:
    unscorable_failures = as_float(row.get("unscorable_failures"))
    if unscorable_failures is not None and unscorable_failures > 0:
        return "fail", "Unscorable runner failures are present; do not interpret them as attack success."
    if str(row.get("total", "")).strip() in {"", "0", "0.0"}:
        return "pending", "No held-out results recorded yet."
    total = as_float(row.get("total"))
    psnr_n = as_float(row.get("quality_psnr_n"))
    lpips_n = as_float(row.get("quality_lpips_n"))
    if total is not None and psnr_n != total:
        return "fail", "PSNR coverage is incomplete for recorded held-out samples."
    psnr = as_float(row.get("quality_psnr_mean"))
    lpips = as_float(row.get("quality_lpips_mean"))
    problems = []
    if psnr is None:
        problems.append("missing_psnr")
    elif psnr < PSNR_MIN:
        problems.append(f"psnr<{PSNR_MIN:g}")
    if lpips is None:
        problems.append("lpips_not_computed")
    elif total is not None and lpips_n != total:
        problems.append("lpips_coverage_incomplete")
    elif lpips > LPIPS_MAX:
        problems.append(f"lpips>{LPIPS_MAX:g}")
    if problems == ["lpips_not_computed"]:
        return "partial", "LPIPS not recomputed in summary; PSNR budget passes."
    if not problems:
        return "pass", "PSNR and LPIPS budget pass."
    return "fail", "; ".join(problems)


def table_tier(row: dict[str, str]) -> str:
    method = row.get("method", "")
    provenance = row.get("provenance", "")
    if method in APPENDIX_METHODS or provenance in PILOT_PROVENANCE:
        return "appendix"
    if method in MAIN_METHODS:
        return "main"
    return "exclude"


def caveats(row: dict[str, str], budget: str) -> str:
    out = []
    if not as_bool(row.get("complete")):
        out.append("incomplete")
    if row.get("provenance") in ADAPTED_PROVENANCE:
        out.append("adapted_attack_not_full_reproduction")
    if row.get("provenance") in PILOT_PROVENANCE:
        out.append("pilot_third_party")
    unscorable = as_float(row.get("unscorable_failures"))
    if unscorable is not None and unscorable > 0:
        out.append(f"unscorable_failures={int(unscorable)}")
    failure_rate = as_float(row.get("failure_rate"))
    if failure_rate is not None and failure_rate > 0:
        out.append(f"failure_rate={failure_rate:.3f}")
    if budget != "pass":
        out.append(f"budget={budget}")
    note = row.get("note", "").strip()
    if note:
        out.append(note)
    return "; ".join(out)


def audit_rows(summary_rows: list[dict[str, str]], delta_rows: list[dict[str, str]], include_incomplete: bool):
    deltas_by_key = {key(row): row for row in delta_rows}
    audited = []
    for row in summary_rows:
        delta = deltas_by_key.get(key(row), {})
        budget, budget_note = budget_status(row)
        audited.append(
            {
                "method": row.get("method", ""),
                "attack": row.get("attack", ""),
                "factor": row.get("factor", ""),
                "tier": table_tier(row),
                "provenance": row.get("provenance", ""),
                "baseline_provenance": row.get("baseline_provenance", ""),
                "attack_provenance": row.get("attack_provenance", ""),
                "complete": row.get("complete", ""),
                "evaluation_split": row.get("evaluation_split", ""),
                "excluded_calibration_samples": row.get("excluded_calibration_samples", ""),
                "budget_status": budget,
                "budget_note": budget_note,
                "metric": row.get("metric", ""),
                "recovery_mean": row.get("recovery_mean", ""),
                "delta_mean": delta.get("delta_mean", ""),
                "relative_drop": delta.get("relative_drop", ""),
                "identity_success_overlap": delta.get("identity_success_overlap", ""),
                "delta_on_identity_success_mean": delta.get("delta_on_identity_success_mean", ""),
                "quality_psnr_mean": row.get("quality_psnr_mean", ""),
                "quality_psnr_n": row.get("quality_psnr_n", ""),
                "quality_lpips_mean": row.get("quality_lpips_mean", ""),
                "quality_lpips_n": row.get("quality_lpips_n", ""),
                "failure_rate": row.get("failure_rate", ""),
                "unscorable_failures": row.get("unscorable_failures", ""),
                "paper_caveats": caveats(row, budget),
            }
        )
    return audited


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "method",
        "attack",
        "factor",
        "tier",
        "provenance",
        "baseline_provenance",
        "attack_provenance",
        "complete",
        "evaluation_split",
        "excluded_calibration_samples",
        "budget_status",
        "budget_note",
        "metric",
        "recovery_mean",
        "delta_mean",
        "relative_drop",
        "identity_success_overlap",
        "delta_on_identity_success_mean",
        "quality_psnr_mean",
        "quality_psnr_n",
        "quality_lpips_mean",
        "quality_lpips_n",
        "failure_rate",
        "unscorable_failures",
        "paper_caveats",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Selected Attack Paper-Readiness Audit",
        "",
        f"Quality budget: PSNR >= {PSNR_MIN:g} dB and LPIPS <= {LPIPS_MAX:g}.",
        "",
        "| Method | Attack | Tier | Complete | Budget | Recovery | Delta | PSNR | Caveats |",
        "|--------|--------|------|----------|--------|----------|-------|------|---------|",
    ]
    for row in rows:
        attack = f"{row['attack']} {row['factor']}".strip()
        lines.append(
            "| {method} | {attack} | {tier} | {complete} | {budget} | {recovery} | {delta} | {psnr} | {caveats} |".format(
                method=row["method"],
                attack=attack,
                tier=row["tier"],
                complete=row["complete"],
                budget=row["budget_status"],
                recovery=row["recovery_mean"],
                delta=row["delta_mean"],
                psnr=row["quality_psnr_mean"],
                caveats=row["paper_caveats"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    summary = Path(args.summary).resolve() if args.summary else root / "selected_attack_summary.csv"
    deltas = Path(args.deltas).resolve() if args.deltas else root / "selected_attack_deltas.csv"
    if not summary.exists() and not args.summary:
        summary = root / "selected_attack_summary_live.csv"
    if not deltas.exists() and not args.deltas:
        deltas = root / "selected_attack_deltas_live.csv"
    output_csv = Path(args.output_csv).resolve() if args.output_csv else root / "selected_attack_paper_audit.csv"
    output_md = Path(args.output_md).resolve() if args.output_md else root / "selected_attack_paper_audit.md"

    rows = audit_rows(read_rows(summary), read_rows(deltas), args.include_incomplete)
    write_csv(output_csv, rows)
    write_markdown(output_md, rows)

    print(f"summary: {summary}")
    print(f"deltas: {deltas}")
    print(f"audit_csv: {output_csv}")
    print(f"audit_md: {output_md}")
    print(f"rows: {len(rows)}")
    by_budget = {}
    for row in rows:
        by_budget[row["budget_status"]] = by_budget.get(row["budget_status"], 0) + 1
    print("budget_status: " + ", ".join(f"{key}={value}" for key, value in sorted(by_budget.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
