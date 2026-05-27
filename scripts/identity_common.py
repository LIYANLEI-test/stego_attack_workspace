#!/usr/bin/env python3
"""Small helpers shared by native identity runners."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image


PROTOCOL_ID = "native_identity_v1_20260522"
PROTOCOL_SEED = "stego-attack-native-identity-v1-20260522"
DEFAULT_PROTOCOL_DIR = Path("/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522")
DEFAULT_RUN_ROOT = Path("/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522")
DEFAULT_HF_HOME = Path("/data2/liyanlei/huggingface")


def ensure_hf_cache(cache_dir: str | Path = DEFAULT_HF_HOME, endpoint: str | None = "https://hf-mirror.com") -> None:
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(cache / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(cache / "transformers"))
    os.environ.setdefault("DIFFUSERS_CACHE", str(cache / "diffusers"))
    if endpoint:
        os.environ.setdefault("HF_ENDPOINT", endpoint)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_prompts(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_image_payloads(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_done(csv_path: Path) -> set[int]:
    if not csv_path.exists():
        return set()
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return {int(row["sample_index"]) for row in csv.DictReader(handle) if row.get("sample_index") not in (None, "")}


def append_csv_row(csv_path: Path, row: dict[str, object], fieldnames: list[str] | None = None) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    exists = csv_path.exists()
    names = fieldnames or list(row.keys())
    with csv_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in names})
        handle.flush()
        os.fsync(handle.fileno())


def append_failure(csv_path: Path, row: dict[str, object]) -> None:
    fieldnames = [
        "method",
        "variant",
        "sample_index",
        "attack_kind",
        "resize_factor",
        "attack_factor",
        "image_path",
        "stego_path",
        "attacked_path",
        "recovered_path",
        "stage",
        "error_type",
        "error_summary",
        "traceback_summary",
        "runtime_s",
        "created_at_utc",
    ]
    append_csv_row(csv_path, row, fieldnames=fieldnames)


def summarize_exception(exc: Exception, max_chars: int = 1000) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = " ".join(text.split())
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def traceback_summary(limit: int = 4, max_chars: int = 2000) -> str:
    return traceback.format_exc(limit=limit).strip()[-max_chars:]


def bits_from_payload_row(row: dict[str, object]) -> list[int]:
    bits = str(row["payload_bits"]).strip()
    return [1 if char == "1" else 0 for char in bits]


def bit_metrics(expected: Iterable[int], recovered: Iterable[int]) -> dict[str, object]:
    ref = [int(x) & 1 for x in expected]
    pred = [int(x) & 1 for x in recovered]
    n = min(len(ref), len(pred))
    if not n:
        return {
            "bit_errors": max(len(ref), len(pred)),
            "bit_count": max(len(ref), len(pred)),
            "bit_accuracy": 0.0,
            "ber": 1.0,
            "exact_match": False,
        }
    errors = sum(int(ref[i] != pred[i]) for i in range(n))
    errors += abs(len(ref) - len(pred))
    count = max(len(ref), len(pred))
    return {
        "bit_errors": errors,
        "bit_count": count,
        "bit_accuracy": 1.0 - errors / count,
        "ber": errors / count,
        "exact_match": errors == 0 and len(ref) == len(pred),
    }


def bits_sha256(bits: Iterable[int]) -> str:
    text = "".join(str(int(bit) & 1) for bit in bits)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def deterministic_u32(method: str, sample_index: int, label: str) -> int:
    raw = hashlib.shake_256(
        f"{PROTOCOL_SEED}|{method}|{sample_index:06d}|{label}".encode("utf-8")
    ).digest(4)
    return int.from_bytes(raw, "big", signed=False)


def image_metrics(reference_path: Path, recovered_path: Path) -> dict[str, object]:
    ref = np.asarray(Image.open(reference_path).convert("RGB"), dtype=np.float32)
    rec = np.asarray(Image.open(recovered_path).convert("RGB"), dtype=np.float32)
    if ref.shape != rec.shape:
        rec_img = Image.fromarray(rec.astype(np.uint8)).resize((ref.shape[1], ref.shape[0]))
        rec = np.asarray(rec_img.convert("RGB"), dtype=np.float32)
    mse = float(np.mean((ref - rec) ** 2))
    psnr = float("inf") if mse == 0 else 20.0 * math.log10(255.0 / math.sqrt(mse))
    mae = float(np.mean(np.abs(ref - rec)))
    out: dict[str, object] = {"mse": mse, "psnr": psnr, "mae": mae}
    try:
        from skimage.metrics import structural_similarity

        out["ssim"] = float(structural_similarity(ref, rec, channel_axis=2, data_range=255))
    except Exception:
        out["ssim"] = ""
    return out


def image_lpips(reference_path: Path, recovered_path: Path, device: str = "cuda") -> float | str:
    """Compute LPIPS(Alex) for a saved RGB image pair.

    LPIPS expects reasonably sized tensors. Tiny images are upsampled to 64x64 so
    CIFAR-scale GSD outputs can still be ranked consistently inside this project.
    """

    try:
        import torch
        import torch.nn.functional as F
        import lpips

        cache_key = "_lpips_alex_model"
        model = getattr(image_lpips, cache_key, None)
        model_device = device if torch.cuda.is_available() and device.startswith("cuda") else "cpu"
        if model is None or getattr(image_lpips, "_lpips_alex_device", None) != model_device:
            model = lpips.LPIPS(net="alex").to(model_device).eval()
            setattr(image_lpips, cache_key, model)
            setattr(image_lpips, "_lpips_alex_device", model_device)

        def load(path: Path) -> torch.Tensor:
            arr = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
            tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
            tensor = tensor * 2.0 - 1.0
            if tensor.shape[-1] < 64 or tensor.shape[-2] < 64:
                tensor = F.interpolate(tensor, size=(64, 64), mode="bilinear", align_corners=False)
            return tensor.to(model_device)

        with torch.no_grad():
            return float(model(load(reference_path), load(recovered_path)).item())
    except Exception:
        return ""
