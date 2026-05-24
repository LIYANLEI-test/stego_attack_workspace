#!/usr/bin/env python3
"""Run Pulsar's official region/Sage path as a native-code smoke sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
from pulsar_native_utils import (
    DEFAULT_HF_ENDPOINT,
    DEFAULT_HF_HOME,
    DEFAULT_PULSAR_REF,
    configure_sage,
    ensure_hf_cache,
    load_official_pulsar,
)


PULSAR_REPOS = {
    "church": "google/ddpm-church-256",
    "celebahq": "google/ddpm-celebahq-256",
    "bedroom": "google/ddpm-bedroom-256",
    "cat": "google/ddpm-cat-256",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="/data2/liyanlei/stego_attack_data/baselines/pulsar/native_regions_smoke")
    parser.add_argument("--message", default="Pulsar native regions smoke")
    parser.add_argument("--model", default="bedroom")
    parser.add_argument("--scheduler", default="ddim", choices=["ddim", "ddpm"])
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--region-estimate-samples", type=int, default=1)
    parser.add_argument("--hist-bins", type=int, default=20)
    parser.add_argument("--seed", default="native-region-seed-0001")
    parser.add_argument("--key", default="stego-attack-workspace-pulsar-key")
    parser.add_argument("--reference-dir", default=str(DEFAULT_PULSAR_REF))
    parser.add_argument("--hf-cache-dir", default=str(DEFAULT_HF_HOME))
    parser.add_argument("--hf-endpoint", default=DEFAULT_HF_ENDPOINT)
    parser.add_argument(
        "--sage-bin",
        default="/data2/liyanlei/envs/stego_attack/bin/sage",
        help="Sage executable used by the official Pulsar ECC path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_hf_cache(args.hf_cache_dir, args.hf_endpoint)
    configure_sage(sage_bin=args.sage_bin, reference_dir=args.reference_dir)
    pulsar = load_official_pulsar(args.reference_dir)

    from diffusers import DDIMScheduler, DDPMScheduler

    scheduler_cls = {"ddim": DDIMScheduler, "ddpm": DDPMScheduler}[args.scheduler]
    repo = PULSAR_REPOS.get(args.model, args.model)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    stego = pulsar.Pulsar(
        repo=repo,
        scheduler=scheduler_cls,
        num_inference_steps=args.steps,
        seed=args.seed.encode("utf-8"),
        key=args.key.encode("utf-8").ljust(64, b"\x00")[:64],
        benchmarks=False,
    )

    capacity = stego.estimate_regions(
        n_to_gen=args.region_estimate_samples,
        n_hist_bins=args.hist_bins,
        end_to_end=False,
    )
    payload_raw = args.message.encode("utf-8")
    payload = len(payload_raw).to_bytes(4, "big") + payload_raw
    if len(payload) > capacity:
        payload = payload[:capacity]
    generated = stego.generate_with_regions(payload)
    last = stego.scheduler.num_inference_steps - 1
    hidden = generated["samples"][last]["hidden"]
    image_path = out / "pulsar_native_regions.png"
    stego.save_sample(hidden, str(image_path))

    recovered = stego.reveal_with_regions(hidden)
    recovered = recovered[: len(payload)]
    matches = recovered == payload
    bit_errors = sum(
        bit_a != bit_b
        for byte_a, byte_b in zip(payload, recovered)
        for bit_a, bit_b in zip(f"{byte_a:08b}", f"{byte_b:08b}")
    )
    bit_count = min(len(payload), len(recovered)) * 8

    manifest = {
        "method": "pulsar",
        "protocol_id": "native_official_regions_smoke",
        "baseline_role": "attack_object",
        "strict_original_reproduction": False,
        "reproduction_label": "native_official",
        "implementation": "official_pulsar_region_sage_path",
        "source_code": "https://github.com/spacelab-ccny/pulsar",
        "reference_checkout": str(Path(args.reference_dir).resolve()),
        "model_repo": repo,
        "scheduler": args.scheduler,
        "steps": args.steps,
        "seed": args.seed,
        "region_estimate_samples": args.region_estimate_samples,
        "hist_bins": args.hist_bins,
        "estimated_capacity_bytes": int(capacity),
        "payload_bytes": len(payload),
        "bit_errors": bit_errors,
        "bit_count": bit_count,
        "bit_accuracy": 1.0 - (bit_errors / bit_count if bit_count else 0.0),
        "message_matches": matches,
        "image_path": str(image_path),
        "output_dir": str(out),
        "protocol_note": (
            "This uses Pulsar's official estimate_regions/generate_with_regions/"
            "reveal_with_regions path with Sage. The small defaults are for smoke "
            "testing; scale samples and steps for formal native evaluation."
        ),
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"image={image_path}")
    print(f"manifest={manifest_path}")
    print(f"capacity_bytes={capacity}")
    print(f"bit_accuracy={manifest['bit_accuracy']:.6f}")
    print(f"message_matches={matches}")


if __name__ == "__main__":
    main()
