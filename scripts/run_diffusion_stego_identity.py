#!/usr/bin/env python3
"""Run Diffusion-Stego identity recovery through the NS-DSer reference implementation."""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image


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
    bit_metrics,
    bits_from_payload_row,
    bits_sha256,
    ensure_hf_cache,
    load_done,
    load_jsonl,
    load_prompts,
    summarize_exception,
    traceback_summary,
    utc_now,
)


DEFAULT_NSD_SER_ROOT = Path("/home/liyanlei/work/NS-DSer-master/NS-DSer-master")
DEFAULT_MODEL_ID = Path("/home/liyanlei/work/NS-DSer-master/sd_ckpt/stable-diffusion-v1-5")
MAPPING_TO_METHOD = {
    "mn": "diffusion_stego_mn",
    "mb": "diffusion_stego_mb",
    "mc": "diffusion_stego_mc",
    "multi_bits": "diffusion_stego_multi_bits",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", default="mn", choices=sorted(MAPPING_TO_METHOD))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--protocol-dir", default=str(DEFAULT_PROTOCOL_DIR))
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--guidance-scale", type=float, default=1.5)
    parser.add_argument("--sampling-strategy", default="ddim", choices=["ddim", "heun"])
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--code-len", type=int, default=None)
    parser.add_argument("--delta", type=float, default=0.0)
    parser.add_argument("--seed-kernel", type=int, default=100)
    parser.add_argument("--seed-shuffle", type=int, default=101)
    parser.add_argument("--model-id", default=str(DEFAULT_MODEL_ID))
    parser.add_argument("--nsdser-root", default=str(DEFAULT_NSD_SER_ROOT))
    parser.add_argument("--hf-cache-dir", default=str(DEFAULT_HF_HOME))
    parser.add_argument("--hf-endpoint", default="https://hf-mirror.com")
    parser.add_argument("--dtype", default="float16", choices=["float16", "float32"])
    parser.add_argument("--vae-device", default="cuda", choices=["cuda", "cpu"])
    parser.add_argument("--attention-slicing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--vae-slicing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--offload-between-stages",
        action="store_true",
        help="Move non-active pipeline modules to CPU between UNet and VAE stages to reduce peak VRAM.",
    )
    parser.add_argument("--save-images", action="store_true")
    parser.add_argument("--skip-image", action="store_true", help="Only test reference projection encode/decode.")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def load_nsdser_symbols(nsdser_root: Path):
    root = nsdser_root.resolve()
    if not (root / "utils" / "projection.py").exists():
        raise FileNotFoundError(f"NS-DSer projection.py not found under {root}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from ldm.models.diffusion.heun import HeunSampler_CF
    from utils.projection import Projection, secret_shape_for_mapping

    return Projection, secret_shape_for_mapping, HeunSampler_CF


def bits_to_secret_tensor(bits: list[int], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    expected_len = int(np.prod(shape))
    if len(bits) != expected_len:
        raise ValueError(f"Protocol bits length {len(bits)} does not match reference secret shape {shape}")
    return torch.tensor(bits, dtype=torch.int64, device=device).reshape(shape)


def save_image_tensor(images: torch.Tensor, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image_np = (
        ((images[0] / 2 + 0.5).clamp(0, 1) * 255)
        .to(torch.uint8)
        .permute(1, 2, 0)
        .detach()
        .cpu()
        .numpy()
    )
    Image.fromarray(image_np, "RGB").save(path)


def move_if_present(obj: object, name: str, device: torch.device | str) -> None:
    module = getattr(obj, name, None)
    if module is not None and hasattr(module, "to"):
        module.to(device)


def main() -> None:
    args = parse_args()
    method = MAPPING_TO_METHOD[args.mapping]
    out = Path(args.output_dir or (DEFAULT_RUN_ROOT / method)).resolve()
    image_dir = out / "images"
    out.mkdir(parents=True, exist_ok=True)

    csv_path = out / "identity_results.csv"
    failures_path = out / "identity_failures.csv"
    if args.force:
        csv_path.unlink(missing_ok=True)
        failures_path.unlink(missing_ok=True)
    done = load_done(csv_path)
    done.update(load_done(failures_path))

    protocol_dir = Path(args.protocol_dir).resolve()
    messages = load_jsonl(protocol_dir / f"{method}_messages_500.jsonl")
    prompts = load_prompts(protocol_dir / "prompts_500.txt")

    ensure_hf_cache(args.hf_cache_dir, args.hf_endpoint)
    Projection, secret_shape_for_mapping, HeunSampler_CF = load_nsdser_symbols(Path(args.nsdser_root))
    code_len = args.code_len if args.code_len is not None else (2 if args.mapping == "multi_bits" else 1)
    if args.mapping == "multi_bits" and code_len != 2:
        raise ValueError("NS-DSer Diffusion-Stego multi_bits supports code_len=2")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipe = None
    dtype = torch.float16 if args.dtype == "float16" and torch.cuda.is_available() else torch.float32
    if args.skip_image:
        latent_channels = 4
        latent_size = args.height // 8
        sampler = None
    else:
        from diffusers import AutoPipelineForText2Image

        model_id = Path(args.model_id)
        pipe = AutoPipelineForText2Image.from_pretrained(
            str(model_id),
            torch_dtype=dtype,
            local_files_only=model_id.exists(),
        )
        pipe.to(device)
        if args.attention_slicing:
            pipe.enable_attention_slicing()
        if args.vae_slicing and hasattr(pipe, "enable_vae_slicing"):
            pipe.enable_vae_slicing()
        if hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
        if args.vae_device == "cpu":
            move_if_present(pipe, "vae", "cpu")
            move_if_present(pipe, "unet", device)
            move_if_present(pipe, "text_encoder", device)
        latent_channels = int(pipe.unet.config.in_channels)
        latent_size = int(pipe.unet.config.sample_size)
        sampler = HeunSampler_CF(pipe)

    latent_shape = (1, latent_channels, latent_size, latent_size)
    secret_shape = secret_shape_for_mapping(args.mapping, code_len, latent_shape)

    for sample_index in range(args.start_index, args.count):
        if sample_index in done:
            continue
        started = time.perf_counter()
        stage = "init"
        try:
            stage = "payload"
            payload_bits = bits_from_payload_row(messages[sample_index])
            secret_bits = bits_to_secret_tensor(payload_bits, secret_shape, device)
            prompt = prompts[sample_index % len(prompts)]

            stage = "encode_message"
            np.random.seed(sample_index)
            random.seed(sample_index)
            torch.manual_seed(sample_index)
            generator = Projection(
                args.mapping,
                code_len,
                latent_shape,
                args.delta,
                args.seed_kernel,
                args.seed_shuffle,
                device,
            )
            initial_noise = generator.encode_message(secret_bits)
            recovered_from_initial = generator.decode_message(initial_noise)
            clean = bit_metrics(payload_bits, recovered_from_initial.reshape(-1).detach().cpu().tolist())

            image_path = ""
            inversion: dict[str, object] | None = None
            if pipe is not None and sampler is not None:
                stage = "prompt_embedding"
                move_if_present(pipe, "text_encoder", device)
                prompt_embeds = sampler._encode_prompt(prompt=[prompt], negative_prompt=[""], batch_size=1)
                stage = "generate_image"
                latents = sampler.sampling(
                    args.steps,
                    1,
                    precision=dtype,
                    initial_noise=initial_noise,
                    is_denoising=True,
                    prompt_embeds=prompt_embeds,
                    guidance_scale=args.guidance_scale,
                    is_ddim=args.sampling_strategy == "ddim",
                )
                vae_device = torch.device("cpu") if args.vae_device == "cpu" else device
                vae_dtype = next(pipe.vae.parameters()).dtype
                if args.offload_between_stages and args.vae_device != "cpu":
                    move_if_present(pipe, "unet", "cpu")
                    move_if_present(pipe, "text_encoder", "cpu")
                    torch.cuda.empty_cache()
                images = pipe.vae.decode((latents / pipe.vae.config.scaling_factor).to(device=vae_device, dtype=vae_dtype)).sample
                if args.save_images:
                    image_path = str(image_dir / f"{sample_index:06d}.jpg")
                    save_image_tensor(images, Path(image_path))

                stage = "invert_image"
                del latents
                torch.cuda.empty_cache()
                img_latents = pipe.vae.encode(images.to(device=vae_device, dtype=vae_dtype), return_dict=False)[0].sample()
                latents_for_inversion = (pipe.vae.config.scaling_factor * img_latents).to(device=device, dtype=dtype)
                del images, img_latents
                if args.offload_between_stages and args.vae_device != "cpu":
                    move_if_present(pipe, "vae", "cpu")
                    torch.cuda.empty_cache()
                    move_if_present(pipe, "unet", device)
                    torch.cuda.empty_cache()
                torch.cuda.empty_cache()
                recovered_noise = sampler.sampling(
                    args.steps,
                    1,
                    precision=dtype,
                    initial_noise=latents_for_inversion,
                    is_denoising=False,
                    prompt_embeds=prompt_embeds,
                    guidance_scale=args.guidance_scale,
                    is_ddim=True,
                )
                recovered_bits = generator.decode_message(recovered_noise)
                inversion = bit_metrics(payload_bits, recovered_bits.reshape(-1).detach().cpu().tolist())

            row = {
                "method": "diffusion_stego",
                "variant": args.mapping,
                "sample_index": sample_index,
                "prompt": prompt,
                "steps": args.steps,
                "sampling_strategy": args.sampling_strategy,
                "guidance_scale": args.guidance_scale,
                "code_len": code_len,
                "payload_bits": len(payload_bits),
                "payload_sha256": bits_sha256(payload_bits),
                "clean_bit_errors": clean["bit_errors"],
                "clean_bit_accuracy": clean["bit_accuracy"],
                "clean_exact_match": clean["exact_match"],
                "bit_errors": (inversion or clean)["bit_errors"],
                "bit_count": (inversion or clean)["bit_count"],
                "bit_accuracy": (inversion or clean)["bit_accuracy"],
                "ber": (inversion or clean)["ber"],
                "exact_match": (inversion or clean)["exact_match"],
                "skip_image": args.skip_image,
                "image_path": image_path,
                "runtime_s": time.perf_counter() - started,
            }
            append_csv_row(csv_path, row)
            print(
                f"[diffusion-stego:{args.mapping}] {sample_index + 1}/{args.count} "
                f"acc={float(row['bit_accuracy']):.6f} exact={row['exact_match']} runtime={row['runtime_s']:.2f}s",
                flush=True,
            )
        except Exception as exc:
            append_failure(
                failures_path,
                {
                    "method": "diffusion_stego",
                    "variant": args.mapping,
                    "sample_index": sample_index,
                    "stage": stage,
                    "error_type": type(exc).__name__,
                    "error_summary": summarize_exception(exc),
                    "traceback_summary": traceback_summary(),
                    "runtime_s": time.perf_counter() - started,
                    "created_at_utc": utc_now(),
                },
            )
            print(f"[diffusion-stego:{args.mapping}] {sample_index + 1}/{args.count} FAILED stage={stage}: {exc}", flush=True)

    manifest = {
        "method": "diffusion_stego",
        "variant": args.mapping,
        "protocol_id": PROTOCOL_ID,
        "reproduction_label": "nsdser_reference",
        "reference_root": str(Path(args.nsdser_root).resolve()),
        "source_projection": str((Path(args.nsdser_root) / "utils" / "projection.py").resolve()),
        "source_sampler": str((Path(args.nsdser_root) / "ldm" / "models" / "diffusion" / "heun.py").resolve()),
        "protocol_payload_file": str(protocol_dir / f"{method}_messages_500.jsonl"),
        "prompt_file": str(protocol_dir / "prompts_500.txt"),
        "count": args.count,
        "steps": args.steps,
        "sampling_strategy": args.sampling_strategy,
        "guidance_scale": args.guidance_scale,
        "code_len": code_len,
        "dtype": args.dtype,
        "vae_device": args.vae_device,
        "attention_slicing": args.attention_slicing,
        "vae_slicing": args.vae_slicing,
        "offload_between_stages": args.offload_between_stages,
        "skip_image": args.skip_image,
        "results_csv": str(csv_path),
        "failures_csv": str(failures_path),
        "created_at_utc": utc_now(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"results={csv_path}")


if __name__ == "__main__":
    main()
