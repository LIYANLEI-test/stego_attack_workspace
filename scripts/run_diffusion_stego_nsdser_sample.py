#!/usr/bin/env python3
"""Generate Diffusion-Stego samples through the NS-DSer reference implementation."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from PIL import Image


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NSD_SER_ROOT = Path("/home/liyanlei/work/NS-DSer-master/NS-DSer-master")
DEFAULT_MODEL_ID = Path("/home/liyanlei/work/NS-DSer-master/sd_ckpt/stable-diffusion-v1-5")
DEFAULT_PROMPT_FILE = DEFAULT_NSD_SER_ROOT / "text_prompt_dataset" / "flickr_dataset.txt"
DEFAULT_OUTPUT_DIR = Path("/data2/liyanlei/stego_attack_data/baselines/diffusion_stego/nsdser_reference")
DEFAULT_HF_HOME = Path("/data2/liyanlei/huggingface")
MAPPINGS = ("mn", "mb", "mc", "multi_bits")


def parse_int_list(text: str) -> list[int]:
    values: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            values.extend(range(int(start), int(end) + 1))
        else:
            values.append(int(part))
    if not values:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", default="mn", choices=MAPPINGS)
    parser.add_argument("--seeds", type=parse_int_list, default=parse_int_list("0"))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--model-id", default=str(DEFAULT_MODEL_ID))
    parser.add_argument("--prompt-file", default=str(DEFAULT_PROMPT_FILE))
    parser.add_argument("--nsdser-root", default=str(DEFAULT_NSD_SER_ROOT))
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--guidance-scale", type=float, default=7.5)
    parser.add_argument("--sampling-strategy", default="ddim", choices=["ddim", "heun"])
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--code-len", type=int, default=None)
    parser.add_argument("--delta", type=float, default=0.0)
    parser.add_argument("--seed-kernel", type=int, default=100)
    parser.add_argument("--seed-shuffle", type=int, default=101)
    parser.add_argument("--hf-cache-dir", default=str(DEFAULT_HF_HOME))
    parser.add_argument("--hf-endpoint", default="https://hf-mirror.com")
    parser.add_argument("--skip-image", action="store_true", help="Only test mapping encode/decode.")
    parser.add_argument("--extract", action="store_true", help="Try VAE+DDIM inversion after image generation.")
    return parser.parse_args()


def ensure_hf_cache(cache_dir: str, endpoint: str | None) -> None:
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(cache / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(cache / "transformers"))
    os.environ.setdefault("DIFFUSERS_CACHE", str(cache / "diffusers"))
    if endpoint:
        os.environ.setdefault("HF_ENDPOINT", endpoint)


def load_nsdser_symbols(nsdser_root: Path):
    root = nsdser_root.resolve()
    if not (root / "utils" / "projection.py").exists():
        raise FileNotFoundError(f"NS-DSer projection.py not found under {root}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from ldm.models.diffusion.heun import HeunSampler_CF
    from utils.projection import Projection, secret_shape_for_mapping

    return Projection, secret_shape_for_mapping, HeunSampler_CF


class StackedRandomGenerator:
    def __init__(self, device: torch.device, seeds: list[int]) -> None:
        self.generators = [
            torch.Generator(device).manual_seed(int(seed) % (1 << 32)) for seed in seeds
        ]

    def randint(self, *args, size, **kwargs):
        if size[0] != len(self.generators):
            raise ValueError("batch dimension must match number of seeds")
        return torch.stack(
            [torch.randint(*args, size=size[1:], generator=gen, **kwargs) for gen in self.generators]
        )


def prompt_for_seed(prompt_file: Path, seeds: list[int]) -> list[str]:
    prompts = [line.strip() for line in prompt_file.read_text(encoding="utf-8").splitlines()]
    prompts = [line for line in prompts if line]
    if not prompts:
        raise ValueError(f"No prompts found in {prompt_file}")
    return [prompts[seed % len(prompts)] for seed in seeds]


def save_tensor_images(images: torch.Tensor, seeds: list[int], out: Path) -> list[str]:
    image_paths: list[str] = []
    images_np = (
        ((images / 2 + 0.5).clamp(0, 1) * 255)
        .to(torch.uint8)
        .permute(0, 2, 3, 1)
        .cpu()
        .numpy()
    )
    for seed, image_np in zip(seeds, images_np):
        path = out / f"{seed:06d}.jpg"
        Image.fromarray(image_np, "RGB").save(path)
        image_paths.append(str(path))
    return image_paths


def bit_accuracy(expected: torch.Tensor, recovered: torch.Tensor) -> float:
    expected = expected.detach().cpu().reshape(expected.shape[0], -1).to(torch.int64)
    recovered = recovered.detach().cpu().reshape(recovered.shape[0], -1).to(torch.int64)
    count = min(expected.shape[1], recovered.shape[1])
    if count == 0:
        return 0.0
    return float((expected[:, :count] == recovered[:, :count]).float().mean().item())


def main() -> None:
    args = parse_args()
    nsdser_root = Path(args.nsdser_root)
    model_id = Path(args.model_id)
    prompt_file = Path(args.prompt_file)
    out = Path(args.output_dir) / args.mapping
    out.mkdir(parents=True, exist_ok=True)

    ensure_hf_cache(args.hf_cache_dir, args.hf_endpoint)
    Projection, secret_shape_for_mapping, HeunSampler_CF = load_nsdser_symbols(nsdser_root)

    if args.code_len is None:
        code_len = 2 if args.mapping == "multi_bits" else 1
    else:
        code_len = args.code_len
    if args.mapping == "multi_bits" and code_len != 2:
        raise ValueError("NS-DSer Diffusion-Stego multi_bits supports code_len=2")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seeds = args.seeds[: args.batch_size]
    if len(seeds) != args.batch_size:
        raise ValueError("--batch-size cannot exceed number of parsed seeds")

    from diffusers import AutoPipelineForText2Image

    pipe = None
    if args.skip_image:
        latent_channels = 4
        latent_size = args.height // 8
    else:
        pipe = AutoPipelineForText2Image.from_pretrained(
            str(model_id),
            torch_dtype=torch.float32,
            local_files_only=model_id.exists(),
        )
        pipe.to(device)
        latent_channels = int(pipe.unet.config.in_channels)
        latent_size = int(pipe.unet.config.sample_size)

    latent_shape = (len(seeds), latent_channels, latent_size, latent_size)
    rnd = StackedRandomGenerator(device, seeds)
    secret_shape = secret_shape_for_mapping(args.mapping, code_len, latent_shape)
    secret_bits = rnd.randint(2, size=secret_shape, device=device)

    np.random.seed(seeds[0])
    random.seed(seeds[0])
    torch.manual_seed(seeds[0])
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
    clean_mapping_bit_accuracy = bit_accuracy(secret_bits, recovered_from_initial)

    image_paths: list[str] = []
    inversion_bit_accuracy = None
    prompts = prompt_for_seed(prompt_file, seeds)

    if pipe is not None:
        sampler = HeunSampler_CF(pipe)
        latents = sampler.sampling(
            args.steps,
            len(seeds),
            precision=torch.float32,
            initial_noise=initial_noise,
            is_denoising=True,
            prompt=prompts,
            negative_prompt=[""] * len(seeds),
            guidance_scale=args.guidance_scale,
            is_ddim=args.sampling_strategy == "ddim",
        )
        images = pipe.vae.decode(latents / pipe.vae.config.scaling_factor).sample
        image_paths = save_tensor_images(images, seeds, out)

        if args.extract:
            img_latents = pipe.vae.encode(images, return_dict=False)[0].sample()
            latents_for_inversion = pipe.vae.config.scaling_factor * img_latents
            recovered_noise = sampler.sampling(
                args.steps,
                len(seeds),
                precision=torch.float32,
                initial_noise=latents_for_inversion,
                is_denoising=False,
                prompt=prompts,
                negative_prompt=[""] * len(seeds),
                guidance_scale=args.guidance_scale,
                is_ddim=True,
            )
            recovered_bits = generator.decode_message(recovered_noise)
            inversion_bit_accuracy = bit_accuracy(secret_bits, recovered_bits)

    manifest = {
        "method": "diffusion_stego",
        "variant": args.mapping,
        "protocol_id": "nsdser_reference_smoke",
        "baseline_role": "attack_object",
        "strict_original_reproduction": False,
        "reproduction_label": "nsdser_reference",
        "implementation": "nsdser_projection_with_nsdser_heun_sampler_cf",
        "source_reference": str(nsdser_root.resolve()),
        "source_projection": str((nsdser_root / "utils" / "projection.py").resolve()),
        "source_sampler": str((nsdser_root / "ldm" / "models" / "diffusion" / "heun.py").resolve()),
        "paper": "Diffusion-Stego: Training-free Diffusion Generative Steganography via Message Projection",
        "model_id": str(model_id),
        "prompt_file": str(prompt_file),
        "prompts": prompts,
        "seeds": seeds,
        "steps": args.steps,
        "sampling_strategy": args.sampling_strategy,
        "guidance_scale": args.guidance_scale,
        "code_len": code_len,
        "latent_shape": list(latent_shape),
        "secret_shape": list(secret_shape),
        "clean_mapping_bit_accuracy": clean_mapping_bit_accuracy,
        "inversion_bit_accuracy": inversion_bit_accuracy,
        "image_paths": image_paths,
        "output_dir": str(out),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_note": (
            "This runner imports NS-DSer's Projection implementation for "
            "Diffusion-Stego MN/MB/MC/Multi-bits. It avoids NS-DSer's full "
            "msghiding_t2i.py top-level attack-library imports, but uses the "
            "same projection API and HeunSampler_CF sampler file."
        ),
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"mapping={args.mapping}")
    print(f"manifest={manifest_path}")
    print(f"clean_mapping_bit_accuracy={clean_mapping_bit_accuracy:.6f}")
    if inversion_bit_accuracy is not None:
        print(f"inversion_bit_accuracy={inversion_bit_accuracy:.6f}")
    for path in image_paths:
        print(f"image={path}")


if __name__ == "__main__":
    main()
