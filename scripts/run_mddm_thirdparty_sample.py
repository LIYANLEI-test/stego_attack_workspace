#!/usr/bin/env python3
"""Run the third-party MDDM repository pipeline and write a workspace manifest."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MDDM_REF = WORKSPACE_ROOT / "references" / "MDDM-thirdparty"
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
if str(MDDM_REF) not in sys.path:
    sys.path.insert(0, str(MDDM_REF))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="/data2/liyanlei/stego_attack_data/baselines/mddm/thirdparty_native")
    parser.add_argument("--prompt", default="A small cabin beside a calm lake under morning light.")
    parser.add_argument("--hidden-message", default="MDDM third-party native pipeline sample.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--guidance-scale", type=float, default=1.0)
    parser.add_argument("--negative-prompt", default=None)
    parser.add_argument("--ecc-mode", default="none", choices=["none", "rep3", "hamming74"])
    parser.add_argument("--model-id", default="runwayml/stable-diffusion-v1-5")
    parser.add_argument("--hf-cache-dir", default="/data2/liyanlei/huggingface")
    parser.add_argument("--hf-endpoint", default="https://hf-mirror.com")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.output_dir)
    image_dir = out / "images"
    record_dir = out / "records"
    image_dir.mkdir(parents=True, exist_ok=True)
    record_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HF_HOME", args.hf_cache_dir)
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(Path(args.hf_cache_dir) / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(Path(args.hf_cache_dir) / "transformers"))
    os.environ.setdefault("DIFFUSERS_CACHE", str(Path(args.hf_cache_dir) / "diffusers"))
    if args.hf_endpoint:
        os.environ.setdefault("HF_ENDPOINT", args.hf_endpoint)
    os.environ.setdefault("SD_MODEL_ID", args.model_id)

    from backend.pipeline import MDDMService

    service = MDDMService(image_dir=image_dir, record_dir=record_dir)
    generated = service.generate(
        prompt=args.prompt,
        hidden_message=args.hidden_message,
        seed=args.seed,
        num_steps=args.steps,
        guidance_scale=args.guidance_scale,
        negative_prompt=args.negative_prompt,
        ecc_mode=args.ecc_mode,
    )
    record_path = record_dir / f"{generated['image_id']}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    decoded = service.decode(record)

    manifest = {
        "method": "mddm",
        "protocol_id": "native_third_party_pipeline",
        "baseline_role": "attack_object",
        "strict_original_reproduction": False,
        "reproduction_label": "native_third_party",
        "implementation": "third_party_mddm_backend_pipeline",
        "source_paper": "MDDM: Practical Message-Driven Generative Image Steganography Based on Diffusion Models",
        "source_paper_url": "https://proceedings.mlr.press/v267/xu25ah.html",
        "third_party_reference_code": "https://github.com/RGlodAkshat/MDDM-Generative-Image-Steganography-Based-on-Diffusion-Models",
        "reference_checkout": str(MDDM_REF),
        "model_id": args.model_id,
        "prompt": args.prompt,
        "hidden_message": args.hidden_message,
        "seed": args.seed,
        "steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "ecc_mode": args.ecc_mode,
        "image_path": record["image_path"],
        "record_path": str(record_path),
        "decode_metrics": decoded["metrics"],
        "output_dir": str(out),
        "protocol_note": (
            "This uses the third-party MDDM repository backend pipeline directly. "
            "It is not official author code."
        ),
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"image={record['image_path']}")
    print(f"record={record_path}")
    print(f"manifest={manifest_path}")
    print(f"bit_accuracy={decoded['metrics']['bit_accuracy']:.6f}")
    print(f"exact_match={decoded['metrics']['exact_match']}")


if __name__ == "__main__":
    main()
