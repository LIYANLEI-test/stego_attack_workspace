#!/usr/bin/env python3
"""Render selected attack summaries into Markdown/LaTeX paper tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", default=str(DEFAULT_ROOT / "selected_attack_summary.csv"))
    parser.add_argument("--deltas", default=str(DEFAULT_ROOT / "selected_attack_deltas.csv"))
    parser.add_argument("--output-md", default=str(DEFAULT_ROOT / "paper_tables.md"))
    parser.add_argument("--output-tex", default=str(DEFAULT_ROOT / "paper_tables.tex"))
    parser.add_argument("--include-incomplete", action="store_true")
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
        if not include_incomplete and row.get("complete") != "True":
            continue
        merged = dict(row)
        merged.update({f"delta_{k}": v for k, v in delta_by_key.get(key(row), {}).items()})
        out.append(merged)
    return out


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Selected Attack Paper Tables",
        "",
        "## Main Table",
        "",
        "| Method | Attack | Done | Metric | Attacked | Delta | Quality PSNR | Failure |",
        "|--------|--------|------|--------|----------|-------|--------------|---------|",
    ]
    for row in rows:
        done = f"{row.get('total', '')}/{row.get('target', '')}"
        lines.append(
            "| {method} | {attack} | {done} | {metric} | {attacked} | {delta} | {psnr} | {failure} |".format(
                method=row.get("method", ""),
                attack=display_attack(row),
                done=done,
                metric=display_metric(row),
                attacked=fmt(row.get("recovery_mean"), 4),
                delta=fmt(row.get("delta_delta_mean"), 4),
                psnr=fmt(row.get("quality_psnr_mean"), 2),
                failure=pct(row.get("failure_rate")),
            )
        )
    lines.extend(
        [
            "",
            "Notes:",
            "",
            "- `Delta` is identity metric minus attacked metric over overlapping sample indices.",
            "- For bit payload methods, lower attacked bit accuracy means stronger attack.",
            "- For image payload methods, lower recovered-secret PSNR means stronger attack.",
            "- Incomplete rows are live-progress rows unless rendered after the queue completes.",
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


def render_latex(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{tabular}{lllrrrr}",
        "\\toprule",
        "Method & Attack & Metric & Attacked & Delta & PSNR & Fail. \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            "{method} & {attack} & {metric} & {attacked} & {delta} & {psnr} & {failure} \\\\".format(
                method=latex_escape(row.get("method", "")),
                attack=latex_escape(display_attack(row)),
                metric=latex_escape(display_metric(row)),
                attacked=fmt(row.get("recovery_mean"), 4),
                delta=fmt(row.get("delta_delta_mean"), 4),
                psnr=fmt(row.get("quality_psnr_mean"), 2),
                failure=latex_escape(pct(row.get("failure_rate"))),
            )
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
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
