#!/usr/bin/env python3
"""Run the official RGS hide-and-reveal path as a resumable identity baseline."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from identity_common import (  # noqa: E402
    DEFAULT_HF_HOME,
    DEFAULT_PROTOCOL_DIR,
    DEFAULT_RUN_ROOT,
    PROTOCOL_ID,
    append_csv_row,
    append_failure,
    ensure_hf_cache,
    image_metrics,
    load_done,
    load_image_payloads,
    summarize_exception,
    traceback_summary,
    utc_now,
)


DEFAULT_RGS_ROOT = WORKSPACE_ROOT / "references" / "RGS"
DEFAULT_CLIP = Path("/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local")
DEFAULT_SD15_BIN = Path("/data2/liyanlei/stego_attack_models/rgs/sd15-bin")
DEFAULT_VQGAN = Path("/data2/liyanlei/stego_attack_models/rgs/vqgan_code1024.pth")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_RUN_ROOT / "rgs"))
    parser.add_argument("--protocol-dir", default=str(DEFAULT_PROTOCOL_DIR))
    parser.add_argument("--rgs-root", default=str(DEFAULT_RGS_ROOT))
    parser.add_argument("--python-bin", default="/data2/liyanlei/envs/stego_attack/bin/python")
    parser.add_argument("--clip-model", default=str(DEFAULT_CLIP))
    parser.add_argument("--sd-model", default=str(DEFAULT_SD15_BIN))
    parser.add_argument("--vqgan-ckpt", default=str(DEFAULT_VQGAN))
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--jpeg-qf", type=int, default=90)
    parser.add_argument("--gaussian-var", type=float, default=0.005)
    parser.add_argument("--fidelity-weight", type=float, default=0.5)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--hide-only", action="store_true")
    parser.add_argument("--identity-only", action="store_true", default=True)
    parser.add_argument("--include-built-in-attacks", action="store_true")
    parser.add_argument("--hf-cache-dir", default=str(DEFAULT_HF_HOME))
    parser.add_argument("--hf-endpoint", default="https://hf-mirror.com")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def run_rgs(args: argparse.Namespace, rgs_root: Path, secret_path: Path, sample_dir: Path) -> Path:
    input_dir = sample_dir / "_input"
    result_dir = sample_dir / "results"
    input_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(secret_path, input_dir / secret_path.name)

    weights_dir = rgs_root / "weights"
    weights_dir.mkdir(exist_ok=True)
    expected_ckpt = weights_dir / "vqgan_code1024.pth"
    if not expected_ckpt.exists():
        expected_ckpt.symlink_to(Path(args.vqgan_ckpt).resolve())

    env = os.environ.copy()
    ensure_hf_cache(args.hf_cache_dir, args.hf_endpoint)
    env["RGS_CLIP_MODEL"] = str(Path(args.clip_model).resolve())
    env["RGS_SD_MODEL"] = str(Path(args.sd_model).resolve())
    env["HF_HOME"] = args.hf_cache_dir
    env["HUGGINGFACE_HUB_CACHE"] = str(Path(args.hf_cache_dir) / "hub")
    env["TRANSFORMERS_CACHE"] = str(Path(args.hf_cache_dir) / "transformers")
    env["DIFFUSERS_CACHE"] = str(Path(args.hf_cache_dir) / "diffusers")
    if args.hf_endpoint:
        env["HF_ENDPOINT"] = args.hf_endpoint
    env.pop("LD_LIBRARY_PATH", None)

    command = [
        args.python_bin,
        "hide_and_reveal.py",
        "--input_path",
        str(input_dir),
        "--output_root",
        str(result_dir),
        "--jpeg_qf",
        str(args.jpeg_qf),
        "--gaussian_var",
        str(args.gaussian_var),
        "--fidelity_weight",
        str(args.fidelity_weight),
        "--steps",
        str(args.steps),
    ]
    if args.hide_only:
        command.append("--hide_only")
    if args.identity_only and not args.include_built_in_attacks:
        command.append("--identity_only")

    log_path = sample_dir / "rgs_run.log"
    with log_path.open("w", encoding="utf-8") as log_file:
        completed = subprocess.run(
            command,
            cwd=str(rgs_root),
            env=env,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"RGS run failed with code {completed.returncode}; see {log_path}")
    return log_path


def parse_info_metrics(info_path: Path, attack: str = "origin") -> dict[str, object]:
    if not info_path.exists():
        return {}
    text = info_path.read_text(encoding="utf-8", errors="ignore")
    out: dict[str, object] = {}
    patterns = {
        "bit_acc_2560": rf"{re.escape(attack)}_2560_Acc:\s*([0-9.]+)",
        "flag_acc_1024": rf"{re.escape(attack)}_1024_Acc:\s*([0-9.]+)",
        "indice_acc": rf"{re.escape(attack)}_indice_Acc:\s*([0-9.]+)",
        "psnr": r"After Correction.*?PSNR:\s*([0-9.]+)",
        "ssim": r"After Correction.*?SSIM:\s*([0-9.]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.S)
        if match:
            out[key] = float(match.group(1))
    return out


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir).resolve()
    sample_root = out / "samples"
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "identity_results.csv"
    failures_path = out / "identity_failures.csv"
    if args.force:
        csv_path.unlink(missing_ok=True)
        failures_path.unlink(missing_ok=True)
    done = load_done(csv_path)
    done.update(load_done(failures_path))

    protocol_dir = Path(args.protocol_dir).resolve()
    payloads = load_image_payloads(protocol_dir / "image_payloads_100.csv")
    rgs_root = Path(args.rgs_root).resolve()

    for sample_index in range(args.start_index, args.count):
        if sample_index in done:
            continue
        started = time.perf_counter()
        stage = "init"
        try:
            stage = "payload"
            secret_path = Path(payloads[sample_index]["secret_image_path"]).resolve()
            sample_dir = sample_root / f"{sample_index:06d}"
            stage = "official_hide_reveal"
            log_path = run_rgs(args, rgs_root, secret_path, sample_dir)

            basename = secret_path.stem
            result_dir = sample_dir / "results" / basename
            stego_path = result_dir / f"{basename}_stego.png"
            recovered_path = result_dir / f"{basename}_recon_correction_origin.png"
            raw_recovered_path = result_dir / f"{basename}_recon_origin.png"
            info_path = result_dir / f"{basename}_info.txt"

            metrics = {}
            image_stats = {}
            if recovered_path.exists():
                image_stats = image_metrics(secret_path, recovered_path)
            if info_path.exists():
                metrics = parse_info_metrics(info_path)

            row = {
                "method": "rgs",
                "variant": "official_hide_and_reveal",
                "sample_index": sample_index,
                "secret_image_path": str(secret_path),
                "stego_path": str(stego_path),
                "recovered_path": str(recovered_path),
                "raw_recovered_path": str(raw_recovered_path),
                "steps": args.steps,
                "identity_only": args.identity_only and not args.include_built_in_attacks,
                "hide_only": args.hide_only,
                "jpeg_qf": args.jpeg_qf,
                "gaussian_var": args.gaussian_var,
                "bit_acc_2560": metrics.get("bit_acc_2560", ""),
                "flag_acc_1024": metrics.get("flag_acc_1024", ""),
                "indice_acc": metrics.get("indice_acc", ""),
                "reported_psnr": metrics.get("psnr", ""),
                "reported_ssim": metrics.get("ssim", ""),
                "recovery_mse": image_stats.get("mse", ""),
                "recovery_mae": image_stats.get("mae", ""),
                "recovery_psnr": image_stats.get("psnr", ""),
                "recovery_ssim": image_stats.get("ssim", ""),
                "exact_match": image_stats.get("mse", "") == 0.0,
                "log_path": str(log_path),
                "runtime_s": time.perf_counter() - started,
            }
            append_csv_row(csv_path, row)
            print(
                f"[rgs] {sample_index + 1}/{args.count} "
                f"indice_acc={row['indice_acc']} psnr={row['recovery_psnr']} runtime={row['runtime_s']:.2f}s",
                flush=True,
            )
        except Exception as exc:
            append_failure(
                failures_path,
                {
                    "method": "rgs",
                    "variant": "official_hide_and_reveal",
                    "sample_index": sample_index,
                    "stage": stage,
                    "error_type": type(exc).__name__,
                    "error_summary": summarize_exception(exc),
                    "traceback_summary": traceback_summary(),
                    "runtime_s": time.perf_counter() - started,
                    "created_at_utc": utc_now(),
                },
            )
            print(f"[rgs] {sample_index + 1}/{args.count} FAILED stage={stage}: {exc}", flush=True)

    manifest = {
        "method": "rgs",
        "protocol_id": PROTOCOL_ID,
        "reproduction_label": "native_official",
        "reference_checkout": str(rgs_root),
        "official_script": str(rgs_root / "hide_and_reveal.py"),
        "protocol_image_payload_file": str(protocol_dir / "image_payloads_100.csv"),
        "count": args.count,
        "steps": args.steps,
        "identity_only": args.identity_only and not args.include_built_in_attacks,
        "hide_only": args.hide_only,
        "results_csv": str(csv_path),
        "failures_csv": str(failures_path),
        "created_at_utc": utc_now(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"results={csv_path}")


if __name__ == "__main__":
    main()

