#!/usr/bin/env python3
"""Prepare a fixed secret-image set for image-payload steganography baselines."""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


DEFAULT_SOURCE = Path("/data2/liyanlei/stego_attack_data/source_images/00000")
DEFAULT_OUTPUT = Path("/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260522)
    parser.add_argument("--dataset-name", default="ffhq_100_512_secret_images")
    parser.add_argument(
        "--source-dataset",
        default="FFHQ 1024x1024 image release or local mirror",
    )
    parser.add_argument(
        "--selection",
        choices=["random", "first"],
        default="random",
        help="Deterministic selection strategy.",
    )
    return parser.parse_args()


def center_crop_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def image_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {"path": str(path), "mode": image.mode, "size": list(image.size)}


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    candidates = sorted(
        path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )
    if len(candidates) < args.count:
        raise ValueError(f"Need {args.count} images, found {len(candidates)} in {source_dir}")

    if args.selection == "random":
        rng = random.Random(args.seed)
        selected = sorted(rng.sample(candidates, args.count))
    else:
        selected = candidates[: args.count]

    rows: list[dict[str, object]] = []
    for index, source in enumerate(selected):
        output = image_dir / f"{index:05d}.png"
        with Image.open(source) as image:
            original_mode = image.mode
            original_size = list(image.size)
            prepared = center_crop_square(image.convert("RGB"))
            prepared = prepared.resize((args.size, args.size), Image.Resampling.LANCZOS)
            prepared.save(output)
        rows.append(
            {
                "index": index,
                "output_path": str(output),
                "source_path": str(source),
                "source_name": source.name,
                "source_mode": original_mode,
                "source_size": original_size,
                "output_mode": "RGB",
                "output_size": [args.size, args.size],
            }
        )

    csv_path = output_dir / "manifest.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "dataset": args.dataset_name,
        "role": "secret_image_payload_set",
        "source_dataset": args.source_dataset,
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "image_dir": str(image_dir),
        "count": args.count,
        "size": [args.size, args.size],
        "selection": args.selection,
        "seed": args.seed,
        "preprocess": (
            "This script converts source images to RGB, center-crops to a square, "
            "and resizes to the requested PNG size with LANCZOS. For square FFHQ "
            "1024x1024 sources, the crop is a no-op and only resizing is applied."
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "csv_manifest": str(csv_path),
        "first_image": image_info(image_dir / "00000.png"),
        "last_image": image_info(image_dir / f"{args.count - 1:05d}.png"),
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"image_dir={image_dir}")
    print(f"manifest={manifest_path}")
    print(f"csv={csv_path}")
    print(f"count={len(rows)}")


if __name__ == "__main__":
    main()
