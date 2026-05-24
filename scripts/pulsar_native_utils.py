"""Utilities for calling the official Pulsar repository directly."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PULSAR_REF = WORKSPACE_ROOT / "references" / "pulsar"
DEFAULT_HF_HOME = Path("/data2/liyanlei/huggingface")
DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"
DEFAULT_SAGE_BIN = Path("/data2/liyanlei/envs/stego_attack/bin/sage")


def ensure_hf_cache(
    cache_dir: Path | str = DEFAULT_HF_HOME,
    endpoint: str | None = DEFAULT_HF_ENDPOINT,
) -> Path:
    """Route Hugging Face caches to data storage before diffusers loads models."""

    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_path))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(cache_path / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(cache_path / "transformers"))
    os.environ.setdefault("DIFFUSERS_CACHE", str(cache_path / "diffusers"))
    if endpoint:
        os.environ.setdefault("HF_ENDPOINT", endpoint)
    return cache_path


def load_official_pulsar(reference_dir: Path | str = DEFAULT_PULSAR_REF):
    """Import the official Pulsar module from the reference checkout."""

    ref = Path(reference_dir).resolve()
    source = ref / "pulsar.py"
    if not source.exists():
        raise FileNotFoundError(f"Official Pulsar source not found: {source}")

    ref_str = str(ref)
    if ref_str not in sys.path:
        sys.path.insert(0, ref_str)

    spec = importlib.util.spec_from_file_location("pulsar_official", source)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import official Pulsar module from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure_sage(
    sage_bin: Path | str = DEFAULT_SAGE_BIN,
    reference_dir: Path | str = DEFAULT_PULSAR_REF,
) -> None:
    """Make the official Pulsar Sage scripts callable from this workspace."""

    sage_path = Path(sage_bin)
    if not sage_path.exists():
        raise FileNotFoundError(f"Sage executable not found: {sage_path}")

    sage_dir = str(sage_path.parent)
    current_path = os.environ.get("PATH", "")
    if sage_dir not in current_path.split(os.pathsep):
        os.environ["PATH"] = sage_dir + os.pathsep + current_path

    load_official_pulsar(reference_dir)
    coding = sys.modules["coding"]
    coding.SageCode._SCRIPT_DIR = str(Path(reference_dir).resolve() / "sage")


def sage_smoke_test(
    sage_bin: Path | str = DEFAULT_SAGE_BIN,
    reference_dir: Path | str = DEFAULT_PULSAR_REF,
) -> dict[str, Any]:
    """Run a tiny official Sage encode/decode roundtrip."""

    configure_sage(sage_bin=sage_bin, reference_dir=reference_dir)
    coding = sys.modules["coding"]
    params = coding.SageCode.CODE_LIBRARY[0.10][0]
    message = [65] * params["input_size"]
    task = coding.SageCode._make_code_info(params, message, 0, params["input_size"])
    encoded = coding.SageCode.call_sage("encode", [task])
    decode_task = coding.SageCode._make_code_info(
        params, encoded[0], 0, params["output_size"]
    )
    decoded = coding.SageCode.call_sage("decode", [decode_task])
    return {
        "sage_bin": str(Path(sage_bin).resolve()),
        "encoded_count": len(encoded),
        "encoded_bits": len(encoded[0]),
        "decoded_count": len(decoded),
        "decoded_bytes": len(decoded[0]),
        "matches": decoded[0] == message,
    }
