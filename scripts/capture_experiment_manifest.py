#!/usr/bin/env python3
"""Capture a small reproducibility manifest for a formal experiment root."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--output", default="")
    return parser.parse_args()


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"UNAVAILABLE: {type(exc).__name__}: {exc}"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output).resolve() if args.output else root / "experiment_manifest.json"
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "repo": run(["git", "remote", "get-url", "origin"]),
        "git_head": run(["git", "rev-parse", "HEAD"]),
        "git_status_short": run(["git", "status", "--short"]),
        "python": run(["/data2/liyanlei/envs/stego_attack/bin/python", "--version"]),
        "platform": platform.platform(),
        "hostname": platform.node(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "nvidia_smi": run(["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version", "--format=csv,noheader"]),
        "quality_budget": {
            "psnr_min_db": 30.0,
            "lpips_max": 0.10,
            "source_doc": "docs/quality_budget_attack_selection_20260527.md",
        },
        "evaluation_split": {
            "calibration_sample_indices": "0-9",
            "paper_summary": "heldout_excluding_calibration_0_9",
            "reason": "Attack parameters were selected on the 10-sample calibration set.",
            "raw_generated_counts": {
                "cross": 100,
                "gsd_cifar10": 500,
                "mas_grdh": 500,
                "mddm_128_pilot": 50,
                "pulsar": 500,
            },
            "formal_heldout_counts": {
                "cross": 90,
                "gsd_cifar10": 490,
                "mas_grdh": 490,
                "mddm_128_pilot": 40,
                "pulsar": 490,
            },
        },
        "budget_interpretation": "Mean stego-vs-attacked quality over each held-out row must satisfy both thresholds; failing rows are not retuned on held-out data.",
        "selected_matrix": "scripts/selected_attack_matrix.py",
        "formal_queue": "scripts/run_selected_attack_queue.py",
        "summary_script": "scripts/summarize_selected_attack_runs.py",
        "delta_script": "scripts/summarize_attack_deltas.py",
    }
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
