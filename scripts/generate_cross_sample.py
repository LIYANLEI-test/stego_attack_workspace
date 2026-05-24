#!/usr/bin/env python3
"""Run the official CRoSS demo and write a native-code smoke manifest."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CROSS_REF = WORKSPACE_ROOT / "references" / "CRoSS"
NATIVE_PROTOCOL_ID = "native_official_code_smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001",
        help="Directory for gt.png, hide.png, reverse.png, and manifest.json.",
    )
    parser.add_argument(
        "--image-path",
        default=str(DEFAULT_CROSS_REF / "asserts" / "1.png"),
        help="Input secret image. CRoSS is image-based rather than bit-payload based.",
    )
    parser.add_argument("--private-key", default="Effiel tower")
    parser.add_argument("--public-key", default="a tree")
    parser.add_argument("--num-steps", type=int, default=20)
    parser.add_argument(
        "--python-bin",
        default="/data2/liyanlei/envs/stego_attack/bin/python",
        help="Python executable used to run the official CRoSS demo.",
    )
    parser.add_argument(
        "--hf-cache-dir",
        default="/data2/liyanlei/huggingface",
        help="HuggingFace cache location. Keep this on /data2 to avoid filling home.",
    )
    parser.add_argument(
        "--hf-endpoint",
        default="https://hf-mirror.com",
        help="HuggingFace endpoint used by diffusers.",
    )
    parser.add_argument(
        "--reference-dir",
        default=str(DEFAULT_CROSS_REF),
        help="Path to the official CRoSS reference checkout.",
    )
    return parser.parse_args()


def image_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "path": str(path),
            "mode": image.mode,
            "size": list(image.size),
        }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reference_dir = Path(args.reference_dir).resolve()
    demo_path = reference_dir / "demo.py"
    if not demo_path.exists():
        raise FileNotFoundError(f"CRoSS demo.py not found: {demo_path}")

    image_path = Path(args.image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"CRoSS input image not found: {image_path}")

    env = os.environ.copy()
    env["HF_HOME"] = args.hf_cache_dir
    env["HUGGINGFACE_HUB_CACHE"] = str(Path(args.hf_cache_dir) / "hub")
    env["TRANSFORMERS_CACHE"] = str(Path(args.hf_cache_dir) / "transformers")
    env["DIFFUSERS_CACHE"] = str(Path(args.hf_cache_dir) / "diffusers")
    if args.hf_endpoint:
        env["HF_ENDPOINT"] = args.hf_endpoint
    env.pop("LD_LIBRARY_PATH", None)

    command = [
        args.python_bin,
        str(demo_path),
        "--image_path",
        str(image_path),
        "--private_key",
        args.private_key,
        "--public_key",
        args.public_key,
        "--save_path",
        str(output_dir),
        "--num_steps",
        str(args.num_steps),
    ]
    subprocess.run(command, cwd=str(reference_dir), env=env, check=True)

    outputs = {
        "secret_input": image_info(image_path),
        "gt": image_info(output_dir / "gt.png"),
        "stego": image_info(output_dir / "hide.png"),
        "recovered": image_info(output_dir / "reverse.png"),
    }
    manifest = {
        "method": "cross",
        "protocol_id": NATIVE_PROTOCOL_ID,
        "baseline_role": "attack_object",
        "strict_original_reproduction": False,
        "reproduction_label": "native_official",
        "mode": "official_demo_native_wrapper",
        "payload_type": "secret_image",
        "private_key": args.private_key,
        "public_key": args.public_key,
        "num_steps": args.num_steps,
        "model_repo": "runwayml/stable-diffusion-v1-5",
        "scheduler": "DDIMScheduler",
        "guidance_scale": 1.0,
        "official_reference": str(reference_dir),
        "wrapper": str(Path(__file__).resolve()),
        "hf_cache_dir": str(Path(args.hf_cache_dir).resolve()),
        "hf_endpoint": args.hf_endpoint,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "outputs": outputs,
        "protocol_note": (
            "This wrapper calls the official CRoSS demo.py directly and only "
            "adds cache/output handling plus a manifest. It is a smoke sample, "
            "not the full CRoSS paper evaluation."
        ),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"stego: {output_dir / 'hide.png'}")
    print(f"recovered: {output_dir / 'reverse.png'}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
