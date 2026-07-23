#!/usr/bin/env python3
"""Bounded-parallel ephemeral-source runner for the 224 v6 microfactors."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..affine_rail import (
    MICROFACTOR_COUNT,
    build_microfactor_render_context,
    render_microfactor_adapter,
)
from .emit_microfactor import parse_trace


HERE = Path(__file__).resolve().parent


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_one(
    micro: int, source: Path, binary: Path, log: Path, expected_hash: str,
    width_limit: float, run_timeout: float,
) -> dict:
    source_bytes = source.read_bytes()
    actual_hash = _sha256(source_bytes)
    if actual_hash != expected_hash:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "source-hash",
            "expected": expected_hash,
            "actual": actual_hash,
        }
    compile_start = time.perf_counter()
    try:
        compiled = subprocess.run(
            ["forge", "-o", str(binary), str(source)],
            text=True,
            capture_output=True,
            timeout=240,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"micro": micro, "status": "REFUSED", "stage": "compile-timeout"}
    compile_seconds = time.perf_counter() - compile_start
    if compiled.returncode:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "compile",
            "returncode": compiled.returncode,
            "stderr": compiled.stderr[-4000:],
            "compile_seconds": compile_seconds,
        }

    run_start = time.perf_counter()
    try:
        ran = subprocess.run(
            [str(binary), str(micro)],
            text=True,
            capture_output=True,
            timeout=run_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "run-timeout",
            "compile_seconds": compile_seconds,
        }
    run_seconds = time.perf_counter() - run_start
    log.write_text(ran.stdout)
    if ran.returncode != 42:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "run",
            "returncode": ran.returncode,
            "stderr": ran.stderr[-4000:],
            "compile_seconds": compile_seconds,
            "run_seconds": run_seconds,
        }
    try:
        _, rank, widths = parse_trace(ran.stdout, micro)
    except ValueError as exc:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "trace",
            "error": str(exc),
            "compile_seconds": compile_seconds,
            "run_seconds": run_seconds,
        }
    maximum_width = max(float(value) for value in widths.values())
    if maximum_width > width_limit:
        return {
            "micro": micro,
            "status": "REFUSED",
            "stage": "width-limit",
            "maximum_width": maximum_width,
            "width_limit": width_limit,
            "block_max_width": widths,
            "compile_seconds": compile_seconds,
            "run_seconds": run_seconds,
        }
    return {
        "micro": micro,
        "status": "PASS",
        "source_sha256": actual_hash,
        "rank": rank,
        "block_max_width": widths,
        "compile_seconds": compile_seconds,
        "run_seconds": run_seconds,
        "log": str(log),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=MICROFACTOR_COUNT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--width-limit", type=float, default=1000.0)
    parser.add_argument("--run-timeout", type=float, default=900.0)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not (0 <= args.start < args.end <= MICROFACTOR_COUNT):
        raise SystemExit("expected 0 <= start < end <= 224")
    if not (1 <= args.workers <= 8):
        raise SystemExit("workers must lie in [1,8]")
    if not (0.0 < args.width_limit < float("inf")):
        raise SystemExit("width limit must be finite and positive")
    if not (1.0 <= args.run_timeout <= 3600.0):
        raise SystemExit("run timeout must lie in [1,3600] seconds")

    manifest = json.loads((HERE / "manifest.json").read_text())
    if manifest.get("schema") != "axial-affine-microfactor-runner-manifest-v3":
        raise SystemExit("wrong complete source manifest")
    if len(manifest.get("chunks", [])) != MICROFACTOR_COUNT:
        raise SystemExit("incomplete source manifest")

    args.scratch.mkdir(parents=True, exist_ok=True)
    source_dir = args.scratch / "sources"
    binary_dir = args.scratch / "bin"
    log_dir = args.scratch / "logs"
    for directory in (source_dir, binary_dir, log_dir):
        directory.mkdir(parents=True, exist_ok=True)

    render_start = time.perf_counter()
    context = build_microfactor_render_context()
    jobs = []
    for micro in range(args.start, args.end):
        text, metadata = render_microfactor_adapter(micro, context=context)
        if metadata["frame_table_sha256"] != manifest["frame_table_sha256"]:
            raise SystemExit("global frame-table hash drift")
        source = source_dir / f"microfactor_{micro:03d}.forge"
        source.write_text(text)
        expected = manifest["chunks"][micro]["sha256"]
        if expected is None or _sha256(text.encode()) != expected:
            raise SystemExit(f"specialized source hash drift at micro {micro}")
        jobs.append(
            (
                micro,
                source,
                binary_dir / f"microfactor_{micro:03d}",
                log_dir / f"microfactor_{micro:03d}.log",
                expected,
                args.width_limit,
                args.run_timeout,
            )
        )
    render_seconds = time.perf_counter() - render_start

    results = []
    refusal_seen = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {pool.submit(_run_one, *job): job[0] for job in jobs}
        for future in as_completed(future_map):
            if future.cancelled():
                continue
            result = future.result()
            results.append(result)
            print(
                f"{result['status']} micro={result['micro']} "
                f"stage={result.get('stage', 'complete')} "
                f"run={result.get('run_seconds', -1):.3f}",
                flush=True,
            )
            if result["status"] != "PASS" and not refusal_seen:
                refusal_seen = True
                for pending in future_map:
                    if pending is not future:
                        pending.cancel()
            # Sources and binaries are mechanically reproducible and are not
            # proof artifacts.  Logs remain for canonical artifact emission.
            micro = result["micro"]
            (source_dir / f"microfactor_{micro:03d}.forge").unlink(missing_ok=True)
            (binary_dir / f"microfactor_{micro:03d}").unlink(missing_ok=True)

    results.sort(key=lambda value: value["micro"])
    failed = [item for item in results if item["status"] != "PASS"]
    summary = {
        "schema": "phase3-axial-microfactor-batch-run-v1",
        "manifest_sha256": _sha256((HERE / "manifest.json").read_bytes()),
        "frame_table_sha256": manifest["frame_table_sha256"],
        "range": [args.start, args.end],
        "workers": args.workers,
        "width_limit": args.width_limit,
        "run_timeout": args.run_timeout,
        "render_seconds": render_seconds,
        "all_passed": not failed,
        "first_failure": failed[0] if failed else None,
        "results": results,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.rmtree(source_dir, ignore_errors=True)
    shutil.rmtree(binary_dir, ignore_errors=True)
    print(f"SUMMARY {args.summary} all_passed={not failed}")
    return 0 if not failed else 3


if __name__ == "__main__":
    raise SystemExit(main())
