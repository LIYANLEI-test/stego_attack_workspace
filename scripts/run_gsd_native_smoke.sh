#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GSD_ROOT="${GSD_ROOT:-${WORKSPACE_ROOT}/references/GSD}"
PYTHON_BIN="${PYTHON_BIN:-/data2/liyanlei/envs/stego_attack/bin/python}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/data2/liyanlei/stego_attack_data/baselines/gsd/native_smoke}"
CONFIG="${CONFIG:-cifar10.yml}"
DOC="${DOC:-ddpm_public_checkpoint}"
TIMESTEPS="${TIMESTEPS:-2}"
ETA="${ETA:-0.0}"
USE_OWNMODEL="${USE_OWNMODEL:-false}"

mkdir -p /data/job/ddim
if [[ ! -e /data/job/ddim/.cache ]]; then
  ln -s /data2/liyanlei/stego_attack_models/gsd/ddim_cache /data/job/ddim/.cache
fi
mkdir -p /data2/liyanlei/stego_attack_models/gsd/ddim_cache
mkdir -p "${OUTPUT_ROOT}/images/zs"

unset LD_LIBRARY_PATH
cd "${GSD_ROOT}"
EXTRA_ARGS=()
if [[ "${USE_OWNMODEL}" == "true" || "${USE_OWNMODEL}" == "1" ]]; then
  EXTRA_ARGS+=(--use_ownmodel)
fi
"${PYTHON_BIN}" main.py \
  --config "${CONFIG}" \
  --exp "${OUTPUT_ROOT}" \
  --doc "${DOC}" \
  --sample \
  --reverse_dct \
  --timesteps "${TIMESTEPS}" \
  --eta "${ETA}" \
  --ni True \
  "${EXTRA_ARGS[@]}"

cat > "${OUTPUT_ROOT}/manifest.json" <<EOF
{
  "method": "gsd",
  "protocol_id": "native_official_code_smoke",
  "baseline_role": "attack_object",
  "strict_original_reproduction": false,
  "reproduction_label": "native_official",
  "mode": "public_gsd_reverse_dct_native_smoke",
  "config": "${CONFIG}",
  "doc": "${DOC}",
  "timesteps": ${TIMESTEPS},
  "eta": ${ETA},
  "use_ownmodel": "${USE_OWNMODEL}",
  "public_reference": "${GSD_ROOT}",
  "checkpoint_cache": "/data2/liyanlei/stego_attack_models/gsd/ddim_cache",
  "output_root": "${OUTPUT_ROOT}",
  "protocol_note": "Native GSD public-code smoke only. Increase timesteps and use the intended native checkpoint/config for formal evaluation."
}
EOF
