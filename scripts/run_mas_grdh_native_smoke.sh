#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAS_ROOT="${MAS_ROOT:-${WORKSPACE_ROOT}/references/mas_GRDH}"
PYTHON_BIN="${PYTHON_BIN:-/data2/liyanlei/envs/stego_attack/bin/python}"
CKPT="${CKPT:-/data2/liyanlei/stego_attack_models/mas_grdh/v1-5-pruned.ckpt}"
CLIP_DIR="${CLIP_DIR:-/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local}"
CONFIG="${CONFIG:-${WORKSPACE_ROOT}/configs/mas_grdh_native_ldm.yaml}"
PROMPTS="${PROMPTS:-${WORKSPACE_ROOT}/configs/mas_grdh_native_smoke_prompts.txt}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/data2/liyanlei/stego_attack_data/baselines/mas_grdh/native_official_smoke}"
DPM_STEPS="${DPM_STEPS:-2}"
DPM_GEN_STEPS="${DPM_GEN_STEPS:-${DPM_STEPS}}"
DPM_INV_STEPS="${DPM_INV_STEPS:-${DPM_STEPS}}"
SCALE="${SCALE:-1.0}"
ATTACK_LAYER="${ATTACK_LAYER:-storage}"
ATTACK_FACTOR="${ATTACK_FACTOR:-0.0}"
MAPPING_FUNC="${MAPPING_FUNC:-ours_mapping}"
BIT_NUM="${BIT_NUM:-1}"
GPU="${GPU:-cuda:0}"

unset LD_LIBRARY_PATH
export HF_HOME="${HF_HOME:-/data2/liyanlei/huggingface}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-/data2/liyanlei/huggingface/hub}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/data2/liyanlei/huggingface/transformers}"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

"${PYTHON_BIN}" "${WORKSPACE_ROOT}/scripts/prepare_mas_grdh_native.py" \
  --reference-dir "${MAS_ROOT}" \
  --ckpt "${CKPT}" \
  --clip-dir "${CLIP_DIR}" \
  --output-config "${CONFIG}"

if [[ ! -f "${PROMPTS}" ]]; then
  mkdir -p "$(dirname "${PROMPTS}")"
  printf 'A small cabin beside a calm lake under morning light.\n' > "${PROMPTS}"
fi

mkdir -p "${OUTPUT_ROOT}"
cd "${MAS_ROOT}/scripts"

"${PYTHON_BIN}" txt2img.py \
  --ckpt "${CKPT}" \
  --config "${CONFIG}" \
  --dpm_steps "${DPM_STEPS}" \
  --dpm_gen_steps "${DPM_GEN_STEPS}" \
  --dpm_inv_steps "${DPM_INV_STEPS}" \
  --scale "${SCALE}" \
  --test_prompts "${PROMPTS}" \
  --attack_layer "${ATTACK_LAYER}" \
  --attack_factor "${ATTACK_FACTOR}" \
  --mapping_func "${MAPPING_FUNC}" \
  --bit_num "${BIT_NUM}" \
  --outdir "${OUTPUT_ROOT}" \
  --gpu "${GPU}"

cat > "${OUTPUT_ROOT}/manifest.json" <<EOF
{
  "method": "mas_grdh",
  "protocol_id": "native_official_code_smoke",
  "baseline_role": "attack_object",
  "strict_original_reproduction": false,
  "reproduction_label": "native_official",
  "implementation": "official_mas_grdh_txt2img_smoke",
  "source_code": "https://github.com/HXX5656/mas_GRDH",
  "reference_checkout": "${MAS_ROOT}",
  "official_script": "${MAS_ROOT}/scripts/txt2img.py",
  "sd15_ckpt": "${CKPT}",
  "clip_dir": "${CLIP_DIR}",
  "config": "${CONFIG}",
  "prompt_file": "${PROMPTS}",
  "dpm_steps": ${DPM_STEPS},
  "dpm_gen_steps": ${DPM_GEN_STEPS},
  "dpm_inv_steps": ${DPM_INV_STEPS},
  "scale": ${SCALE},
  "attack_layer": "${ATTACK_LAYER}",
  "attack_factor": ${ATTACK_FACTOR},
  "mapping_func": "${MAPPING_FUNC}",
  "bit_num": ${BIT_NUM},
  "output_root": "${OUTPUT_ROOT}",
  "protocol_note": "Native MAS/GRDH public-code smoke only. Increase DPM steps and prompt count for formal native evaluation."
}
EOF
