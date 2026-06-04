#!/usr/bin/env python3
"""Selected bit-payload target-PSNR attack matrix for formal experiments.

These parameters were calibrated on the 2026-05-27/2026-05-29 10-sample grid
and reselected on 2026-06-05 under:
  target stego-vs-attacked PSNR ~= 30 dB

Keep this file as the single source of truth for formal selected-attack queues
and paper-table aggregation. Exploratory grids should use separate scripts.
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FORMAL_COUNTS = {
    "gsd_cifar10": 500,
    "mas_grdh": 500,
    "mddm_128_pilot": 50,
    "pulsar": 500,
}

BASELINE_PROVENANCE = {
    "gsd_cifar10": "native_official",
    "mas_grdh": "native_official",
    "mddm_128_pilot": "native_third_party",
    "pulsar": "native_official",
}

# Attack parameters were selected on these sample IDs in the calibration grid.
# Formal paper summaries exclude them to avoid selection/test leakage.
CALIBRATION_SAMPLE_COUNT = 10


@dataclass(frozen=True)
class SelectedAttack:
    method: str
    attack: str
    factor: str
    label: str
    metric: str
    provenance: str
    note: str = ""

    @property
    def safe_factor(self) -> str:
        return self.factor.replace(".", "_").replace("-", "_")

    @property
    def name_part(self) -> str:
        return f"{self.attack}_{self.safe_factor}"


SELECTED_ATTACKS: tuple[SelectedAttack, ...] = (
    SelectedAttack("gsd_cifar10", "resize", "1.5", "resize_1_5", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "jpeg", "70", "jpeg_q70", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "mblur", "0.75", "median_blur_soft_0_75", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "gblur", "0.75", "gaussian_blur_radius_0_75", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "regen_vae", "5", "regen_vae_q5", "bit_accuracy", "adapted_attack"),
    SelectedAttack("mas_grdh", "resize", "1.5", "resize_1_5", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "jpeg", "50", "jpeg_q50", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "mblur", "0.75", "median_blur_soft_0_75", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "gblur", "0.75", "gaussian_blur_radius_0_75", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "regen_vae", "4", "regen_vae_q4", "bit_accuracy", "adapted_attack"),
    SelectedAttack(
        "mddm_128_pilot",
        "resize",
        "0.5",
        "resize_0_5",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "mddm_128_pilot",
        "jpeg",
        "50",
        "jpeg_q50",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "mddm_128_pilot",
        "mblur",
        "3",
        "median_blur_k3",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "mddm_128_pilot",
        "gblur",
        "1",
        "gaussian_blur_radius_1",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "mddm_128_pilot",
        "regen_vae",
        "4",
        "regen_vae_q4",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "pulsar",
        "resize",
        "0.5",
        "resize_0_5",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures; closest current candidate is above target PSNR.",
    ),
    SelectedAttack(
        "pulsar",
        "jpeg",
        "50",
        "jpeg_q50",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures; closest current candidate is above target PSNR.",
    ),
    SelectedAttack(
        "pulsar",
        "mblur",
        "7",
        "median_blur_k7",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures; closest current candidate is above target PSNR.",
    ),
    SelectedAttack(
        "pulsar",
        "gblur",
        "7",
        "gaussian_blur_k7",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures; closest current candidate is above target PSNR.",
    ),
    SelectedAttack(
        "pulsar",
        "regen_vae",
        "1",
        "regen_vae_q1",
        "bit_accuracy",
        "adapted_attack",
        "Calibration produced native reveal failures; closest current candidate is above target PSNR.",
    ),
)


def selected_for_methods(methods: set[str] | None = None) -> list[SelectedAttack]:
    if methods is None:
        return list(SELECTED_ATTACKS)
    return [item for item in SELECTED_ATTACKS if item.method in methods]


def default_count_for(method: str) -> int:
    try:
        return DEFAULT_FORMAL_COUNTS[method]
    except KeyError as exc:
        raise ValueError(f"unsupported method for selected attack matrix: {method}") from exc


def heldout_count_for(method: str) -> int:
    count = default_count_for(method) - CALIBRATION_SAMPLE_COUNT
    if count <= 0:
        raise ValueError(f"no held-out samples remain for method: {method}")
    return count


def baseline_provenance_for(method: str) -> str:
    try:
        return BASELINE_PROVENANCE[method]
    except KeyError as exc:
        raise ValueError(f"unsupported method for selected attack matrix: {method}") from exc


def attack_provenance_for(spec: SelectedAttack) -> str:
    if spec.attack == "regen_vae":
        return "adapted_watermarkattacker_regen_vae"
    if spec.attack == "unmarker":
        return "adapted_unmarker_smoke"
    return "common_image_transform"
