#!/usr/bin/env python3
"""Render selected attack summaries into Markdown/LaTeX paper tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")
MAIN_METHODS = {"cross", "gsd_cifar10", "mas_grdh", "pulsar"}
APPENDIX_METHODS = {"mddm_128_pilot"}
PSNR_MIN = 30.0
LPIPS_MAX = 0.10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default=str(DEFAULT_ROOT / "selected_attack_summary.csv"))
    parser.add_argument("--deltas", default=str(DEFAULT_ROOT / "selected_attack_deltas.csv"))
    parser.add_argument("--output-md", default=str(DEFAULT_ROOT / "paper_tables.md"))
    parser.add_argument("--output-tex", default=str(DEFAULT_ROOT / "paper_tables.tex"))
    parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Deprecated compatibility flag; rendered readiness tables always retain incomplete selected rows.",
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


def fmt(value: object, digits: int = 3) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{number:.{digits}f}"


def pct(value: object) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{100.0 * number:.1f}%"


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row.get("method", ""), row.get("attack", ""), row.get("factor", ""))


def display_attack(row: dict[str, str]) -> str:
    label = row.get("label") or f"{row.get('attack', '')}_{row.get('factor', '')}"
    attack = row.get("attack", "")
    factor = row.get("factor", "")
    if attack == "resize":
        return f"resize {factor}x"
    if attack == "jpeg":
        return f"JPEG q={factor}"
    if attack == "mblur":
        if factor.startswith("0."):
            return f"median blur blend a={factor}"
        return f"median blur k={factor}"
    if attack == "gblur":
        try:
            if float(factor) < 3:
                return f"Gaussian blur r={factor}"
        except ValueError:
            pass
        return f"Gaussian blur k={factor}"
    if attack == "regen_vae":
        return f"Regen-VAE q={factor}"
    if attack == "unmarker":
        return "UnMarker high-smoke-25"
    return label.replace("_", " ")


def display_metric(row: dict[str, str]) -> str:
    metric = row.get("metric", "")
    if metric == "bit_accuracy":
        return "Bit acc."
    if metric == "recovery_psnr":
        return "Rec. PSNR"
    return metric


def merged_rows(summary_rows: list[dict[str, str]], delta_rows: list[dict[str, str]], include_incomplete: bool):
    delta_by_key = {key(row): row for row in delta_rows}
    out = []
    for row in summary_rows:
        merged = dict(row)
        merged.update({f"delta_{k}": v for k, v in delta_by_key.get(key(row), {}).items()})
        out.append(merged)
    return out


def failure_display(row: dict[str, str]) -> str:
    if row.get("total") in {"", "0", "0.0"}:
        return ""
    return pct(row.get("failure_rate"))


def table_tier(row: dict[str, str]) -> str:
    if row.get("method") in APPENDIX_METHODS or row.get("provenance") == "native_third_party":
        return "appendix"
    if row.get("method") in MAIN_METHODS:
        return "main"
    return "exclude"


def budget_status(row: dict[str, str]) -> str:
    total = as_float(row.get("total"))
    psnr = as_float(row.get("quality_psnr_mean"))
    lpips = as_float(row.get("quality_lpips_mean"))
    psnr_n = as_float(row.get("quality_psnr_n"))
    lpips_n = as_float(row.get("quality_lpips_n"))
    unscorable = as_float(row.get("unscorable_failures"))
    if unscorable is not None and unscorable > 0:
        return "fail"
    if psnr is None:
        return "pending"
    if lpips is None:
        return "partial"
    if total is not None and (psnr_n != total or lpips_n != total):
        return "fail"
    if psnr >= PSNR_MIN and lpips <= LPIPS_MAX:
        return "pass"
    return "fail"


def markdown_table(rows: list[dict[str, str]], heading: str) -> list[str]:
    lines = [
        f"## {heading}",
        "",
        "| Method | Attack | Done | Metric | Attacked | Delta (all) | Delta (ID-ok) | PSNR | LPIPS | Budget | Failure |",
        "|--------|--------|------|--------|----------|-------------|---------------|------|-------|--------|---------|",
    ]
    for row in rows:
        done = f"{row.get('total', '')}/{row.get('target', '')}"
        lines.append(
            "| {method} | {attack} | {done} | {metric} | {attacked} | {delta} | {conditional_delta} | {psnr} | {lpips} | {budget} | {failure} |".format(
                method=row.get("method", ""),
                attack=display_attack(row),
                done=done,
                metric=display_metric(row),
                attacked=fmt(row.get("recovery_mean"), 4),
                delta=fmt(row.get("delta_delta_mean"), 4),
                conditional_delta=fmt(row.get("delta_delta_on_identity_success_mean"), 4),
                psnr=fmt(row.get("quality_psnr_mean"), 2),
                lpips=fmt(row.get("quality_lpips_mean"), 4),
                budget=budget_status(row),
                failure=failure_display(row),
            )
        )
    lines.append("")
    return lines


def render_markdown(rows: list[dict[str, str]]) -> str:
    main_rows = [row for row in rows if table_tier(row) == "main"]
    appendix_rows = [row for row in rows if table_tier(row) == "appendix"]
    lines = ["# Selected Attack Paper Tables", ""]
    lines.extend(markdown_table(main_rows, "Main Table"))
    if appendix_rows:
        lines.extend(markdown_table(appendix_rows, "Appendix Pilot Table"))
    lines.extend(
        [
            "Notes:",
            "",
            "- `Delta (all)` is identity metric minus attacked metric over overlapping sample indices.",
            "- `Delta (ID-ok)` restricts comparison to indices successfully recovered in the no-attack identity run.",
            "- Formal rows exclude calibration sample indices `0-9`, which were used to select attack parameters.",
            "- A row supports fixed-budget claims only when `Budget` is `pass` (PSNR >= 30 dB and LPIPS <= 0.10).",
            "- Only native failures after a saved attacked image exists are scored as zero recovery; unscorable runner failures invalidate a row.",
            "- For bit payload methods, lower attacked bit accuracy means stronger attack.",
            "- For image payload methods, lower recovered-secret PSNR means stronger attack.",
            "- Regen-VAE and UnMarker rows are adapted attack baselines, not full reproductions of their papers.",
            "- Incomplete rows remain visible in readiness tables; after queue completion they must be resolved or excluded with explanation.",
            "",
        ]
    )
    return "\n".join(lines)


def latex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def latex_table(rows: list[dict[str, str]], caption: str) -> list[str]:
    lines = [
        f"% {caption}",
        "\\begin{tabular}{lllrrrrrr}",
        "\\toprule",
        "Method & Attack & Metric & Attacked & $\\Delta$ all & $\\Delta$ ID-ok & PSNR & LPIPS & Fail. \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            "{method} & {attack} & {metric} & {attacked} & {delta} & {conditional_delta} & {psnr} & {lpips} & {failure} \\\\".format(
                method=latex_escape(row.get("method", "")),
                attack=latex_escape(display_attack(row)),
                metric=latex_escape(display_metric(row)),
                attacked=fmt(row.get("recovery_mean"), 4),
                delta=fmt(row.get("delta_delta_mean"), 4),
                conditional_delta=fmt(row.get("delta_delta_on_identity_success_mean"), 4),
                psnr=fmt(row.get("quality_psnr_mean"), 2),
                lpips=fmt(row.get("quality_lpips_mean"), 4),
                failure=latex_escape(failure_display(row)),
            )
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    return lines


def render_latex(rows: list[dict[str, str]]) -> str:
    main_rows = [row for row in rows if table_tier(row) == "main"]
    appendix_rows = [row for row in rows if table_tier(row) == "appendix"]
    lines = latex_table(main_rows, "Main table; include only quality-budget passing rows in formal claims.")
    if appendix_rows:
        lines.extend(latex_table(appendix_rows, "Appendix pilot table."))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    summary_rows = read_rows(Path(args.summary).resolve())
    delta_rows = read_rows(Path(args.deltas).resolve())
    rows = merged_rows(summary_rows, delta_rows, args.include_incomplete)
    md = render_markdown(rows)
    tex = render_latex(rows)
    md_path = Path(args.output_md).resolve()
    tex_path = Path(args.output_tex).resolve()
    md_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    tex_path.write_text(tex, encoding="utf-8")
    print(f"rows: {len(rows)}")
    print(f"markdown: {md_path}")
    print(f"latex: {tex_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
