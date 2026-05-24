#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/data2/liyanlei/envs/stego_attack/bin/python}"
OUTPUT_DIR="${OUTPUT_DIR:-/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001}"
IMAGE_PATH="${IMAGE_PATH:-${WORKSPACE_ROOT}/references/CRoSS/asserts/1.png}"
PRIVATE_KEY="${PRIVATE_KEY:-Effiel tower}"
PUBLIC_KEY="${PUBLIC_KEY:-a tree}"
NUM_STEPS="${NUM_STEPS:-20}"

"${PYTHON_BIN}" "${WORKSPACE_ROOT}/scripts/generate_cross_sample.py" \
  --python-bin "${PYTHON_BIN}" \
  --output-dir "${OUTPUT_DIR}" \
  --image-path "${IMAGE_PATH}" \
  --private-key "${PRIVATE_KEY}" \
  --public-key "${PUBLIC_KEY}" \
  --num-steps "${NUM_STEPS}"
