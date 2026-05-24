#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

apply_patch_if_needed() {
  local repo_dir="$1"
  local patch_file="$2"

  if git -C "${repo_dir}" apply --check "${patch_file}" >/dev/null 2>&1; then
    git -C "${repo_dir}" apply "${patch_file}"
    printf 'applied %s\n' "${patch_file}"
  elif git -C "${repo_dir}" apply --reverse --check "${patch_file}" >/dev/null 2>&1; then
    printf 'already applied %s\n' "${patch_file}"
  else
    printf 'cannot apply %s cleanly\n' "${patch_file}" >&2
    return 1
  fi
}

apply_patch_if_needed \
  "${WORKSPACE_ROOT}/references/RGS" \
  "${WORKSPACE_ROOT}/patches/rgs-local-compat.patch"

apply_patch_if_needed \
  "${WORKSPACE_ROOT}/references/mas_GRDH" \
  "${WORKSPACE_ROOT}/patches/mas-grdh-lr-scheduler-shim.patch"
