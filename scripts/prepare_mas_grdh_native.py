#!/usr/bin/env python3
"""Prepare/check assets for the official MAS/GRDH repository path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REF = WORKSPACE_ROOT / "references" / "mas_GRDH"
DEFAULT_MODEL_ROOT = Path("/data2/liyanlei/stego_attack_models/mas_grdh")
DEFAULT_CKPT = DEFAULT_MODEL_ROOT / "v1-5-pruned.ckpt"
DEFAULT_CLIP = DEFAULT_MODEL_ROOT / "clip" / "clip-vit-large-patch14-local"
DEFAULT_CONFIG = WORKSPACE_ROOT / "configs" / "mas_grdh_native_ldm.yaml"
DEFAULT_MANIFEST = DEFAULT_MODEL_ROOT / "native_assets_manifest.json"


REQUIRED_CLIP_FILES = [
    "config.json",
    "pytorch_model.bin",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", default=str(DEFAULT_REF))
    parser.add_argument("--ckpt", default=str(DEFAULT_CKPT))
    parser.add_argument("--clip-dir", default=str(DEFAULT_CLIP))
    parser.add_argument("--output-config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ref = Path(args.reference_dir).resolve()
    source_config = ref / "configs" / "stable-diffusion" / "ldm.yaml"
    ckpt = Path(args.ckpt)
    clip_dir = Path(args.clip_dir)
    output_config = Path(args.output_config)
    manifest_path = Path(args.manifest)

    if not source_config.exists():
        raise FileNotFoundError(f"MAS/GRDH source config not found: {source_config}")
    if not ckpt.exists():
        raise FileNotFoundError(
            "Missing SD1.5 .ckpt for MAS/GRDH native path. Expected at "
            f"{ckpt}. Download runwayml/stable-diffusion-v1-5 "
            "v1-5-pruned-emaonly.ckpt or v1-5-pruned.ckpt and link it here."
        )
    missing_clip = [name for name in REQUIRED_CLIP_FILES if not (clip_dir / name).exists()]
    if missing_clip:
        raise FileNotFoundError(
            "Missing CLIP files for MAS/GRDH native path under "
            f"{clip_dir}: {', '.join(missing_clip)}"
        )

    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    config["model"]["params"]["cond_stage_config"]["params"]["version"] = str(
        clip_dir.resolve()
    )
    output_config.parent.mkdir(parents=True, exist_ok=True)
    output_config.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    manifest = {
        "method": "mas_grdh",
        "reproduction_label": "native_official",
        "source_code": "https://github.com/HXX5656/mas_GRDH",
        "reference_checkout": str(ref),
        "official_script": str(ref / "scripts" / "txt2img.py"),
        "prepared_config": str(output_config.resolve()),
        "sd15_ckpt": str(ckpt.resolve()),
        "clip_dir": str(clip_dir.resolve()),
        "large_asset_root": str(DEFAULT_MODEL_ROOT),
        "download_sources": {
            "sd15_ckpt": "runwayml/stable-diffusion-v1-5/v1-5-pruned-emaonly.ckpt",
            "clip": "openai/clip-vit-large-patch14",
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"prepared_config={output_config}")
    print(f"manifest={manifest_path}")
    print(f"ckpt={ckpt}")
    print(f"clip_dir={clip_dir}")


if __name__ == "__main__":
    main()
