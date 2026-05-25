#!/usr/bin/env python3
"""Run queued non-RGS unified attack pilots on available GPUs."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = Path("/data2/liyanlei/stego_attack_data/attack_runs/unified_image_attacks_20260526")
PYTHON = Path("/data2/liyanlei/envs/stego_attack/bin/python")
ENV_BIN = Path("/data2/liyanlei/envs/stego_attack/bin")
HF_HOME = Path("/data2/liyanlei/huggingface")

ATTACK_FACTORS = {
    "jpeg": ["90", "70", "50"],
    "mblur": ["3", "5", "7"],
    "gblur": ["3", "5", "7"],
}
METHODS = ["cross", "gsd_cifar10", "mas_grdh", "pulsar", "mddm_128_pilot"]


@dataclass(frozen=True)
class Job:
    method: str
    attack: str
    factor: str
    count: int

    @property
    def safe_factor(self) -> str:
        return self.factor.replace(".", "_")

    @property
    def name(self) -> str:
        return f"{self.method}_{self.attack}_{self.safe_factor}_{self.count}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--gpus", default="0,2,3")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--attacks", default="jpeg,mblur,gblur")
    parser.add_argument("--methods", default=",".join(METHODS))
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    parser.add_argument("--force", action="store_true", help="Delete prior runner CSVs via each runner's --force.")
    return parser.parse_args()


def result_total(out_dir: Path) -> int:
    total = 0
    for name in ("identity_results.csv", "identity_failures.csv"):
        path = out_dir / name
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            total += sum(1 for _ in csv.DictReader(handle))
    return total


def lock_dir(out_dir: Path) -> Path:
    return out_dir.with_name(out_dir.name + ".running")


def try_lock(out_dir: Path) -> bool:
    try:
        lock_dir(out_dir).mkdir()
        return True
    except FileExistsError:
        return False


def unlock(out_dir: Path) -> None:
    shutil.rmtree(lock_dir(out_dir), ignore_errors=True)


def base_env(gpu: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("LD_LIBRARY_PATH", None)
    env["CUDA_VISIBLE_DEVICES"] = gpu
    env["HF_HOME"] = str(HF_HOME)
    env["HUGGINGFACE_HUB_CACHE"] = str(HF_HOME / "hub")
    env["TRANSFORMERS_CACHE"] = str(HF_HOME / "transformers")
    env["DIFFUSERS_CACHE"] = str(HF_HOME / "diffusers")
    env["HF_ENDPOINT"] = "https://hf-mirror.com"
    env["PATH"] = f"{ENV_BIN}:{env.get('PATH', '')}"
    return env


def command_for(job: Job, out_dir: Path, force: bool) -> list[str]:
    factor = str(job.factor)
    force_flag = ["--force"] if force else []
    if job.method == "cross":
        return [
            str(PYTHON),
            "scripts/run_cross_identity.py",
            "--count",
            str(job.count),
            "--num-steps",
            "50",
            "--attack-kind",
            job.attack,
            "--attack-factor",
            factor,
            "--output-dir",
            str(out_dir),
            *force_flag,
        ]
    if job.method == "gsd_cifar10":
        return [
            str(PYTHON),
            "scripts/run_gsd_identity.py",
            "--count",
            str(job.count),
            "--timesteps",
            "1000",
            "--attack-kind",
            job.attack,
            "--attack-factor",
            factor,
            "--device",
            "cuda",
            "--output-dir",
            str(out_dir),
            *force_flag,
        ]
    if job.method == "mas_grdh":
        return [
            str(PYTHON),
            "scripts/run_mas_grdh_identity.py",
            "--count",
            str(job.count),
            "--dpm-steps",
            "20",
            "--scale",
            "5.0",
            "--attack-kind",
            job.attack,
            "--attack-factor",
            factor,
            "--gpu",
            "cuda:0",
            "--output-dir",
            str(out_dir),
            *force_flag,
        ]
    if job.method == "pulsar":
        return [
            str(PYTHON),
            "scripts/run_pulsar_identity.py",
            "--count",
            str(job.count),
            "--steps",
            "50",
            "--region-estimate-samples",
            "1",
            "--hist-bins",
            "100",
            "--attack-kind",
            job.attack,
            "--attack-factor",
            factor,
            "--sample-dtype",
            "uint8",
            "--output-dir",
            str(out_dir),
            *force_flag,
        ]
    if job.method == "mddm_128_pilot":
        return [
            str(PYTHON),
            "scripts/run_mddm_identity.py",
            "--count",
            str(job.count),
            "--steps",
            "20",
            "--guidance-scale",
            "1.0",
            "--payload-bytes",
            "128",
            "--attack-kind",
            job.attack,
            "--attack-factor",
            factor,
            "--output-dir",
            str(out_dir),
            *force_flag,
        ]
    raise ValueError(f"unsupported method: {job.method}")


def make_jobs(attacks: list[str], methods: list[str], count: int) -> list[Job]:
    jobs: list[Job] = []
    for attack in attacks:
        if attack not in ATTACK_FACTORS:
            raise ValueError(f"unsupported attack: {attack}")
        for factor in ATTACK_FACTORS[attack]:
            for method in methods:
                jobs.append(Job(method=method, attack=attack, factor=factor, count=count))
    return jobs


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    logs = root / "logs"
    root.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    gpus = [gpu.strip() for gpu in args.gpus.split(",") if gpu.strip()]
    attacks = [attack.strip() for attack in args.attacks.split(",") if attack.strip()]
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    pending = make_jobs(attacks, methods, args.count)
    print(f"[queue] root={root}")
    print(f"[queue] pending={len(pending)} gpus={','.join(gpus)}", flush=True)

    active: dict[str, tuple[Job, subprocess.Popen[bytes], object]] = {}
    failures: list[tuple[Job, int]] = []
    while pending or active:
        for gpu in gpus:
            if gpu in active or not pending:
                continue
            job = None
            out_dir = None
            while pending:
                candidate = pending.pop(0)
                candidate_out = root / candidate.name
                if not args.force and result_total(candidate_out) >= args.count:
                    continue
                if try_lock(candidate_out):
                    job = candidate
                    out_dir = candidate_out
                    break
            if job is None or out_dir is None:
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            log_path = logs / f"{job.name}.log"
            log_handle = log_path.open("ab")
            cmd = command_for(job, out_dir, args.force)
            print(f"[queue] START gpu={gpu} job={job.name}", flush=True)
            log_handle.write(("COMMAND " + " ".join(cmd) + "\n").encode("utf-8"))
            log_handle.flush()
            proc = subprocess.Popen(
                cmd,
                cwd=WORKSPACE_ROOT,
                env=base_env(gpu),
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            active[gpu] = (job, proc, log_handle)

        time.sleep(args.poll_seconds)
        for gpu, (job, proc, log_handle) in list(active.items()):
            code = proc.poll()
            if code is None:
                continue
            log_handle.close()
            total = result_total(root / job.name)
            print(f"[queue] DONE gpu={gpu} job={job.name} exit={code} records={total}", flush=True)
            if code != 0:
                failures.append((job, code))
            unlock(root / job.name)
            del active[gpu]

    if failures:
        print("[queue] command failures:", flush=True)
        for job, code in failures:
            print(f"[queue] {job.name} exit={code}", flush=True)
        return 1
    print("[queue] all jobs finished", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
