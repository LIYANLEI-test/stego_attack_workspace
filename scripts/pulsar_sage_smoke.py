#!/usr/bin/env python3
"""Smoke-test Pulsar's official Sage ECC path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
from pulsar_native_utils import sage_smoke_test


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sage-bin",
        default="/data2/liyanlei/envs/stego_attack/bin/sage",
        help="Sage executable path.",
    )
    parser.add_argument(
        "--reference-dir",
        default=str(WORKSPACE_ROOT / "references" / "pulsar"),
        help="Official Pulsar reference checkout.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(sage_smoke_test(args.sage_bin, args.reference_dir), indent=2))


if __name__ == "__main__":
    main()
