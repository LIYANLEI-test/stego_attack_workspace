#!/usr/bin/env python3
"""Monitor the selected quality-budget attack queue and refresh reports.

The monitor is intentionally conservative: it does not launch or kill attack
jobs. It only watches the existing queue, regenerates live CSV/table artifacts,
and writes a small progress snapshot under the experiment root.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from selected_attack_matrix import (  # noqa: E402
    CALIBRATION_SAMPLE_COUNT,
    default_count_for,
    heldout_count_for,
    selected_for_methods,
)


DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527")
PYTHON = Path("/data2/liyanlei/envs/stego_attack/bin/python")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--queue-pid", type=int, default=None)
    parser.add_argument("--poll-seconds", type=float, default=300.0)
    parser.add_argument("--once", action="store_true", help="Write one snapshot and exit.")
    parser.add_argument("--finalize-when-done", action="store_true")
    parser.add_argument("--skip-report-refresh", action="store_true")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def read_heldout_count(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                sample_index = int(row.get("sample_index", ""))
            except (TypeError, ValueError):
                continue
            if sample_index >= CALIBRATION_SAMPLE_COUNT:
                count += 1
    return count


def result_counts(out_dir: Path) -> tuple[int, int, int]:
    rows = read_count(out_dir / "identity_results.csv")
    failures = read_count(out_dir / "identity_failures.csv")
    return rows, failures, rows + failures


def heldout_result_counts(out_dir: Path) -> tuple[int, int, int]:
    rows = read_heldout_count(out_dir / "identity_results.csv")
    failures = read_heldout_count(out_dir / "identity_failures.csv")
    return rows, failures, rows + failures


def pid_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def proc_cmdline(pid: str) -> str:
    try:
        data = (Path("/proc") / pid / "cmdline").read_bytes()
    except OSError:
        return ""
    return data.replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()


def matching_processes(root: Path) -> list[dict[str, object]]:
    root_text = str(root)
    matches = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        cmdline = proc_cmdline(entry.name)
        if not cmdline:
            continue
        interesting = (
            "run_selected_attack_queue.py" in cmdline
            or "run_cross_identity.py" in cmdline
            or "run_gsd_identity.py" in cmdline
            or "run_mas_grdh_identity.py" in cmdline
            or "run_mddm_identity.py" in cmdline
            or "run_pulsar_identity.py" in cmdline
        )
        if interesting and root_text in cmdline:
            matches.append({"pid": int(entry.name), "cmdline": cmdline})
    return sorted(matches, key=lambda item: int(item["pid"]))


def queue_alive(root: Path, explicit_pid: int | None) -> bool:
    if explicit_pid is not None:
        return pid_alive(explicit_pid)
    return any("run_selected_attack_queue.py" in item["cmdline"] for item in matching_processes(root))


def run_report(cmd: list[str]) -> dict[str, object]:
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=WORKSPACE_ROOT,
        env=clean_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "runtime_s": round(time.perf_counter() - started, 3),
        "output_tail": proc.stdout[-4000:],
    }


def clean_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("LD_LIBRARY_PATH", None)
    env["PATH"] = f"{PYTHON.parent}:{env.get('PATH', '')}"
    env.setdefault("HF_HOME", "/data2/liyanlei/huggingface")
    env.setdefault("TORCH_HOME", "/data2/liyanlei/torch")
    return env


def refresh_reports(root: Path, final: bool) -> list[dict[str, object]]:
    suffix = "" if final else "_live"
    summary = root / f"selected_attack_summary{suffix}.csv"
    deltas = root / f"selected_attack_deltas{suffix}.csv"
    md = root / f"paper_tables{suffix}.md"
    tex = root / f"paper_tables{suffix}.tex"
    manifest = root / f"experiment_manifest{suffix}.json"
    audit_csv = root / f"selected_attack_paper_audit{suffix}.csv"
    audit_md = root / f"selected_attack_paper_audit{suffix}.md"

    commands = [
        [
            str(PYTHON),
            "scripts/summarize_selected_attack_runs.py",
            "--root",
            str(root),
            "--output",
            str(summary),
            *(["--include-lpips"] if final else []),
        ],
        [
            str(PYTHON),
            "scripts/summarize_attack_deltas.py",
            "--attack-root",
            str(root),
            "--output",
            str(deltas),
        ],
        [
            str(PYTHON),
            "scripts/render_paper_tables.py",
            "--summary",
            str(summary),
            "--deltas",
            str(deltas),
            "--output-md",
            str(md),
            "--output-tex",
            str(tex),
            *(["--include-incomplete"] if not final else []),
        ],
        [
            str(PYTHON),
            "scripts/capture_experiment_manifest.py",
            "--root",
            str(root),
            "--output",
            str(manifest),
        ],
        [
            str(PYTHON),
            "scripts/audit_selected_attack_results.py",
            "--root",
            str(root),
            "--summary",
            str(summary),
            "--deltas",
            str(deltas),
            "--output-csv",
            str(audit_csv),
            "--output-md",
            str(audit_md),
            *(["--include-incomplete"] if not final else []),
        ],
    ]
    return [run_report(command) for command in commands]


def build_snapshot(root: Path, queue_pid: int | None, report_results: list[dict[str, object]]) -> dict[str, object]:
    jobs = []
    raw_done = 0
    raw_target_total = 0
    formal_done = 0
    formal_target_total = 0
    for spec in selected_for_methods(None):
        raw_target = default_count_for(spec.method)
        formal_target = heldout_count_for(spec.method)
        out_dir = root / f"{spec.method}_{spec.name_part}_{raw_target}"
        rows, failures, total = result_counts(out_dir)
        formal_rows, formal_failures, formal_total = heldout_result_counts(out_dir)
        jobs.append(
            {
                "name": out_dir.name,
                "method": spec.method,
                "attack": spec.attack,
                "factor": spec.factor,
                "target": raw_target,
                "raw_target": raw_target,
                "rows": rows,
                "failures": failures,
                "total": total,
                "complete": total >= raw_target,
                "formal_target": formal_target,
                "formal_rows": formal_rows,
                "formal_failures": formal_failures,
                "formal_total": formal_total,
                "formal_complete": formal_total >= formal_target,
                "output_dir": str(out_dir),
            }
        )
        raw_done += min(total, raw_target)
        raw_target_total += raw_target
        formal_done += min(formal_total, formal_target)
        formal_target_total += formal_target

    processes = matching_processes(root)
    all_complete = bool(jobs) and all(job["complete"] for job in jobs)
    return {
        "created_at_utc": utc_now(),
        "root": str(root),
        "queue_pid": queue_pid,
        "queue_alive": queue_alive(root, queue_pid),
        "all_complete": all_complete,
        "complete_jobs": sum(1 for job in jobs if job["complete"]),
        "total_jobs": len(jobs),
        "total_done": raw_done,
        "total_target": raw_target_total,
        "progress_fraction": (raw_done / raw_target_total) if raw_target_total else 0.0,
        "raw_done": raw_done,
        "raw_target": raw_target_total,
        "formal_done": formal_done,
        "formal_target": formal_target_total,
        "formal_progress_fraction": (formal_done / formal_target_total) if formal_target_total else 0.0,
        "calibration_sample_indices": "0-9",
        "processes": processes,
        "jobs": jobs,
        "report_results": report_results,
    }


def write_snapshot(root: Path, snapshot: dict[str, object]) -> None:
    json_path = root / "queue_progress_snapshot.json"
    md_path = root / "queue_progress_snapshot.md"
    json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    lines = [
        "# Selected Quality-Budget Queue Progress",
        "",
        f"- Updated UTC: `{snapshot['created_at_utc']}`",
        f"- Queue alive: `{snapshot['queue_alive']}`",
        f"- Jobs complete: `{snapshot['complete_jobs']}/{snapshot['total_jobs']}`",
        f"- Raw generated records: `{snapshot['raw_done']}/{snapshot['raw_target']}`",
        f"- Formal held-out records: `{snapshot['formal_done']}/{snapshot['formal_target']}`",
        "- Formal rows exclude calibration sample indices `0-9`.",
        "",
        "| Job | Raw Done | Raw Failures | Formal Done | Formal Failures |",
        "|-----|----------|--------------|-------------|-----------------|",
    ]
    for job in snapshot["jobs"]:
        lines.append(
            f"| {job['name']} | {job['total']}/{job['raw_target']} | {job['failures']} | "
            f"{job['formal_total']}/{job['formal_target']} | {job['formal_failures']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    finalized = False
    while True:
        report_results: list[dict[str, object]] = []
        if not args.skip_report_refresh:
            report_results = refresh_reports(root, final=False)
        snapshot = build_snapshot(root, args.queue_pid, report_results)
        write_snapshot(root, snapshot)

        print(
            "[monitor] "
            f"{snapshot['created_at_utc']} jobs={snapshot['complete_jobs']}/{snapshot['total_jobs']} "
            f"raw_records={snapshot['raw_done']}/{snapshot['raw_target']} "
            f"formal_records={snapshot['formal_done']}/{snapshot['formal_target']} "
            f"queue_alive={snapshot['queue_alive']}",
            flush=True,
        )

        if args.once:
            return 0
        if snapshot["all_complete"] and args.finalize_when_done and not finalized:
            final_results = refresh_reports(root, final=True)
            final_snapshot = build_snapshot(root, args.queue_pid, final_results)
            write_snapshot(root, final_snapshot)
            finalized = True
            print("[monitor] final reports written", flush=True)
            return 0
        if not snapshot["queue_alive"] and not snapshot["all_complete"]:
            print("[monitor] queue exited before all selected jobs completed", flush=True)
            return 2
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
