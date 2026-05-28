#!/usr/bin/env python3
"""Prepare deterministic payload and input manifests for identity experiments."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_OUTPUT = Path("/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522")
DEFAULT_SECRET_IMAGES = Path("/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images")
DEFAULT_PROMPTS = Path("/home/liyanlei/work/stego_attack_workspace/references/mas_GRDH/text_prompt_dataset/laion_dataset.txt")
PROTOCOL_ID = "native_identity_v1_20260522"
PROTOCOL_SEED = "stego-attack-native-identity-v1-20260522"


METHOD_PAYLOAD_SPECS = [
    {
        "method": "pulsar",
        "payload_unit": "bytes",
        "payload_length": "dynamic_capacity",
        "note": "Capacity is estimated by Pulsar per sample with estimate_regions(); derive that many bytes.",
    },
    {
        "method": "mddm",
        "payload_unit": "text_bytes",
        "payload_length": 2048,
        "note": "SD1.5 latent capacity is 4*64*64 bits. Use 2048 ASCII bytes for the native text interface.",
    },
    {
        "method": "mas_grdh",
        "payload_unit": "bits",
        "payload_length": 16384,
        "note": "Native SD latent shape is 4*64*64 with bit_num=1.",
    },
    {
        "method": "gsd_cifar10",
        "payload_unit": "bits",
        "payload_length": 3072,
        "note": "CIFAR-10 DDPM shape is 3*32*32.",
    },
    {
        "method": "gsd_celeba64",
        "payload_unit": "bits",
        "payload_length": 12288,
        "note": "CelebA-64 DDPM shape is 3*64*64.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--bit-count", type=int, default=500)
    parser.add_argument("--image-count", type=int, default=100)
    parser.add_argument("--secret-image-dir", default=str(DEFAULT_SECRET_IMAGES))
    parser.add_argument("--prompt-source", default=str(DEFAULT_PROMPTS))
    return parser.parse_args()


def derive_bytes(method: str, index: int, length: int) -> bytes:
    return hashlib.shake_256(
        f"{PROTOCOL_SEED}|{method}|{index:06d}|{length}".encode("utf-8")
    ).digest(length)


def bytes_to_bits(payload: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in payload)


def printable_ascii_payload(method: str, index: int, length: int) -> str:
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    raw = derive_bytes(method, index, length)
    return "".join(chr(alphabet[byte % len(alphabet)]) for byte in raw)


def bit_payload_for_index(method: str, index: int, bit_length: int) -> dict[str, object]:
    byte_length = (bit_length + 7) // 8
    payload = derive_bytes(method, index, byte_length)
    bits = bytes_to_bits(payload)[:bit_length]
    return {
        "method": method,
        "sample_index": index,
        "payload_unit": "bits",
        "payload_bits_len": bit_length,
        "payload_bits": bits,
        "payload_bytes_source_len": byte_length,
        "payload_sha256": hashlib.sha256(bits.encode("ascii")).hexdigest(),
    }


def text_payload_for_index(method: str, index: int, byte_length: int) -> dict[str, object]:
    text = printable_ascii_payload(method, index, byte_length)
    payload = text.encode("ascii")
    return {
        "method": method,
        "sample_index": index,
        "payload_unit": "text_bytes",
        "payload_text": text,
        "payload_bytes": len(payload),
        "payload_bits_len": len(payload) * 8,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }


def load_prompts(path: Path, count: int) -> list[str]:
    prompts: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            prompt = " ".join(line.strip().split())
            if prompt:
                prompts.append(prompt)
            if len(prompts) >= count:
                break
    if len(prompts) < count:
        raise ValueError(f"Need {count} prompts, found {len(prompts)} in {path}")
    return prompts


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    spec_path = output_dir / "method_payload_specs.json"
    spec_path.write_text(json.dumps(METHOD_PAYLOAD_SPECS, indent=2, ensure_ascii=False), encoding="utf-8")

    method_files: dict[str, str] = {}
    for spec in METHOD_PAYLOAD_SPECS:
        method = str(spec["method"])
        payload_length = spec["payload_length"]
        if payload_length == "dynamic_capacity":
            continue
        rows: list[dict[str, object]]
        if spec["payload_unit"] == "text_bytes":
            rows = [text_payload_for_index(method, index, int(payload_length)) for index in range(args.bit_count)]
        else:
            rows = [bit_payload_for_index(method, index, int(payload_length)) for index in range(args.bit_count)]
        jsonl_path = output_dir / f"{method}_messages_500.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        csv_path = output_dir / f"{method}_messages_500.csv"
        write_csv(csv_path, rows)
        method_files[method] = str(jsonl_path)

    prompt_source = Path(args.prompt_source).resolve()
    prompts = load_prompts(prompt_source, args.bit_count)
    prompt_rows = [{"sample_index": index, "prompt": prompt} for index, prompt in enumerate(prompts)]
    write_csv(output_dir / "prompts_500.csv", prompt_rows)
    (output_dir / "prompts_500.txt").write_text("\n".join(prompts) + "\n", encoding="utf-8")

    secret_dir = Path(args.secret_image_dir).resolve()
    secret_images = sorted(
        path for path in secret_dir.iterdir() if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if len(secret_images) < args.image_count:
        raise ValueError(f"Need {args.image_count} secret images, found {len(secret_images)} in {secret_dir}")
    image_rows = [
        {
            "sample_index": index,
            "secret_image_path": str(path),
            "source_set": str(secret_dir),
        }
        for index, path in enumerate(secret_images[: args.image_count])
    ]
    write_csv(output_dir / "image_payloads_100.csv", image_rows)

    manifest = {
        "protocol_id": PROTOCOL_ID,
        "protocol_seed": PROTOCOL_SEED,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "bit_methods": {
            "sample_count": args.bit_count,
            "message_rule": (
                "All methods derive messages from the same protocol seed. "
                "Each method uses its own native payload length/capacity."
            ),
            "method_payload_specs": str(spec_path),
            "static_message_files": method_files,
            "dynamic_methods": {
                "pulsar": (
                    "After estimate_regions() returns capacity_bytes for a sample, derive exactly "
                    "capacity_bytes with SHAKE256(protocol_seed | pulsar | sample_index | capacity_bytes)."
                )
            },
            "prompt_files": {
                "txt": str(output_dir / "prompts_500.txt"),
                "csv": str(output_dir / "prompts_500.csv"),
                "source": str(prompt_source),
            },
        },
        "image_payload_methods": {
            "sample_count": args.image_count,
            "secret_image_set": str(secret_dir),
            "manifest_csv": str(output_dir / "image_payloads_100.csv"),
            "note": "CRoSS and RGS use these images as payloads and are reported in a separate image-recovery table.",
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"protocol_dir={output_dir}")
    print(f"manifest={manifest_path}")
    print(f"method_payload_specs={spec_path}")
    print(f"prompts={output_dir / 'prompts_500.txt'}")
    print(f"image_payloads={output_dir / 'image_payloads_100.csv'}")


if __name__ == "__main__":
    main()
