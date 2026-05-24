#!/usr/bin/env python3
"""Run the official RGS hide-and-reveal pipeline from its repository checkout."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RGS_ROOT = WORKSPACE_ROOT / "references" / "RGS"
DEFAULT_OUTPUT_DIR = Path("/data2/liyanlei/stego_attack_data/baselines/rgs/native_official")
DEFAULT_SECRET = DEFAULT_RGS_ROOT / "inputs" / "00000.png"
DEFAULT_CLIP = Path("/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local")
DEFAULT_SD15_BIN = Path("/data2/liyanlei/stego_attack_models/rgs/sd15-bin")
DEFAULT_VQGAN = Path("/data2/liyanlei/stego_attack_models/rgs/vqgan_code1024.pth")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--secret-image", default=str(DEFAULT_SECRET))
    parser.add_argument("--rgs-root", default=str(DEFAULT_RGS_ROOT))
    parser.add_argument("--python-bin", default="/data2/liyanlei/envs/stego_attack/bin/python")
    parser.add_argument("--clip-model", default=str(DEFAULT_CLIP))
    parser.add_argument("--sd-model", default=str(DEFAULT_SD15_BIN))
    parser.add_argument("--vqgan-ckpt", default=str(DEFAULT_VQGAN))
    parser.add_argument("--jpeg-qf", type=int, default=90)
    parser.add_argument("--gaussian-var", type=float, default=0.005)
    parser.add_argument("--fidelity-weight", type=float, default=0.5)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--hide-only", action="store_true")
    parser.add_argument("--identity-only", action="store_true")
    parser.add_argument("--hf-cache-dir", default="/data2/liyanlei/huggingface")
    parser.add_argument("--hf-endpoint", default="https://hf-mirror.com")
    return parser.parse_args()


def image_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {"path": str(path), "mode": image.mode, "size": list(image.size)}


def main() -> None:
    args = parse_args()
    rgs_root = Path(args.rgs_root).resolve()
    secret = Path(args.secret_image).resolve()
    out = Path(args.output_dir).resolve()
    input_dir = out / "_input"
    result_dir = out / "results"

    if not (rgs_root / "hide_and_reveal.py").exists():
        raise FileNotFoundError(f"RGS hide_and_reveal.py not found: {rgs_root}")
    if not secret.exists():
        raise FileNotFoundError(f"Secret image not found: {secret}")
    if not Path(args.vqgan_ckpt).exists():
        raise FileNotFoundError(f"RGS VQGAN checkpoint not found: {args.vqgan_ckpt}")

    out.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    copied_secret = input_dir / secret.name
    shutil.copy2(secret, copied_secret)

    weights_dir = rgs_root / "weights"
    weights_dir.mkdir(exist_ok=True)
    expected_ckpt = weights_dir / "vqgan_code1024.pth"
    if not expected_ckpt.exists():
        expected_ckpt.symlink_to(Path(args.vqgan_ckpt).resolve())

    env = os.environ.copy()
    env["RGS_CLIP_MODEL"] = str(Path(args.clip_model).resolve())
    env["RGS_SD_MODEL"] = str(Path(args.sd_model).resolve())
    env.setdefault("HF_HOME", args.hf_cache_dir)
    env.setdefault("HUGGINGFACE_HUB_CACHE", str(Path(args.hf_cache_dir) / "hub"))
    env.setdefault("TRANSFORMERS_CACHE", str(Path(args.hf_cache_dir) / "transformers"))
    env.setdefault("DIFFUSERS_CACHE", str(Path(args.hf_cache_dir) / "diffusers"))
    if args.hf_endpoint:
        env.setdefault("HF_ENDPOINT", args.hf_endpoint)
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
    if args.identity_only:
        command.append("--identity_only")
    log_path = out / "rgs_run.log"
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

    produced = sorted(path for path in result_dir.rglob("*") if path.is_file())
    image_outputs = [
        str(path)
        for path in produced
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ]
    manifest = {
        "method": "rgs",
        "protocol_id": "native_official_code_smoke",
        "baseline_role": "attack_object",
        "strict_original_reproduction": False,
        "reproduction_label": "native_official",
        "implementation": "official_rgs_hide_and_reveal",
        "paper": "Robust Generative Steganography for Image Hiding Using Concatenated Mappings",
        "source_code": "https://github.com/FBW-JNU/RGS",
        "reference_checkout": str(rgs_root),
        "secret_input": image_info(copied_secret),
        "clip_model": str(Path(args.clip_model).resolve()),
        "sd_model": str(Path(args.sd_model).resolve()),
        "vqgan_ckpt": str(Path(args.vqgan_ckpt).resolve()),
        "jpeg_qf": args.jpeg_qf,
        "gaussian_var": args.gaussian_var,
        "fidelity_weight": args.fidelity_weight,
        "steps": args.steps,
        "hide_only": args.hide_only,
        "identity_only": args.identity_only,
        "result_dir": str(result_dir),
        "image_outputs": image_outputs,
        "log_path": str(log_path),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_note": (
            "This runner calls the official RGS hide_and_reveal.py. Local edits "
            "only parameterize paths/output directories and keep model assets on /data2."
        ),
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"manifest={manifest_path}")
    print(f"log={log_path}")
    print(f"result_dir={result_dir}")
    for path in image_outputs[:10]:
        print(f"image={path}")


if __name__ == "__main__":
    main()
