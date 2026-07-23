#!/usr/bin/env python3
"""Regenerate every inward radial factor at one exact frequency."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path

from ..affine_rail import (
    INWARD_PANELS,
    MICROFACTOR_COUNT,
    FrameTaylor,
    _canonical_sha256,
    _frame_payload,
    _structured_kernel_source,
    exact_inputs,
    numerical_frames_with_sensitivity,
    render_microfactor_adapter,
    render_runtime_taylor_builder,
)
from .run_microfactor_batch import _run_one
from .split_microfactor import WIDTH_LIMIT


OMEGA0 = Fraction(4097, 8192)
TRACE_BASE = 400_000


def point_trace_id(micro: int) -> int:
    if not 0 <= micro < MICROFACTOR_COUNT:
        raise ValueError("point microfactor out of range")
    return TRACE_BASE + micro


def build_point_context() -> dict:
    """Regenerate coefficient and frame data at exactly ``OMEGA0``."""
    import sympy as sp

    data = exact_inputs()
    omega = data["omega"]
    t = next(s for s in data["inward"].free_symbols if s.name == "t")
    point_matrix = data["inward"].subs(
        omega, sp.Rational(OMEGA0.numerator, OMEGA0.denominator)
    ).applyfunc(sp.cancel)
    raw_frames = numerical_frames_with_sensitivity(
        data["inward"], t, omega, OMEGA0,
        Fraction(0), Fraction(28), INWARD_PANELS, bits=34,
    )
    zero = tuple(
        tuple(Fraction(0) for _ in row) for row in raw_frames[0].derivative
    )
    frames = tuple(FrameTaylor(frame.center, zero) for frame in raw_frames)
    frame_payloads = [_frame_payload(frame) for frame in frames]
    return {
        "data": data,
        "t": t,
        "omega_cell": (OMEGA0, OMEGA0),
        "omega_center": OMEGA0,
        # IvAffineCell rejects zero radius.  The renderer is patched locally
        # below to a unit bookkeeping radius after all frequency derivatives
        # have been made exactly zero.
        "omega_radius": Fraction(1),
        "declared_frequency_radius": Fraction(0),
        "point_frequency": True,
        "frame_bits": 34,
        "frames": frames,
        "runtime_lines": render_runtime_taylor_builder(
            "gc_micro_runtime", point_matrix, t, omega,
            OMEGA0, Fraction(0),
        ),
        "structured_kernel_source": _structured_kernel_source(),
        "frame_sha256": [
            _canonical_sha256(payload) for payload in frame_payloads
        ],
        "frame_table_sha256": _canonical_sha256(frame_payloads),
    }


def render_point_factor(micro: int, context: dict) -> tuple[str, dict]:
    source, metadata = render_microfactor_adapter(
        micro, context=context, trace_id=point_trace_id(micro)
    )
    metadata["omega_radius"] = "0"
    metadata["affine_bookkeeping_radius"] = "1"
    verify_point_source(source)
    return source, metadata


def verify_point_source(source: str) -> bool:
    """Refuse any accidental frequency-linear coefficient in a point source."""
    if "d=qm_set" in source:
        raise ValueError("point coefficient builder has nonzero linear terms")
    derivative_bodies = re.findall(
        r"fn gc_micro_[^{]*_frame_\d+_derivative\(\) -> QMat \{(.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    if not derivative_bodies or any("qm_set" in body for body in derivative_bodies):
        raise ValueError("point frame table has nonzero frequency derivatives")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--run-timeout", type=float, default=900.0)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("workers must lie in [1,8]")

    sources = args.scratch / "sources"
    binaries = args.scratch / "bin"
    logs = args.scratch / "logs"
    for directory in (sources, binaries, logs):
        directory.mkdir(parents=True, exist_ok=True)

    context = build_point_context()
    jobs, source_receipts = [], []
    started = time.perf_counter()
    for micro in range(MICROFACTOR_COUNT):
        trace = point_trace_id(micro)
        text, metadata = render_point_factor(micro, context)
        source = sources / f"point_micro_{micro:03d}.forge"
        binary = binaries / f"point_micro_{micro:03d}"
        log = logs / f"point_micro_{micro:03d}.log"
        source.write_text(text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        jobs.append((
            trace, source, binary, log, digest, WIDTH_LIMIT,
            args.run_timeout,
        ))
        source_receipts.append({
            "micro": micro,
            "trace_id": trace,
            "source_sha256": digest,
            "frame_table_sha256": metadata["frame_table_sha256"],
            "left_boundary_sha256": metadata["left_boundary_sha256"],
            "right_boundary_sha256": metadata["right_boundary_sha256"],
        })

    results, refusal = [], False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_run_one, *job): job for job in jobs}
        for future in as_completed(futures):
            if future.cancelled():
                continue
            result = future.result()
            results.append(result)
            print(
                f"{result['status']} trace={result['micro']} "
                f"stage={result.get('stage', 'complete')} "
                f"run={result.get('run_seconds', -1):.3f}",
                flush=True,
            )
            if result["status"] != "PASS" and not refusal:
                refusal = True
                for pending in futures:
                    if pending is not future:
                        pending.cancel()
            future_job = futures[future]
            future_job[1].unlink(missing_ok=True)
            future_job[2].unlink(missing_ok=True)

    results.sort(key=lambda value: value["micro"])
    failed = [item for item in results if item["status"] != "PASS"]
    summary = {
        "schema": "phase3-axial-exact-point-microfactor-batch-v1",
        "frequency": {
            "parameter": "Momega",
            "value": f"{OMEGA0.numerator}/{OMEGA0.denominator}",
            "radius": "0/1",
        },
        "factor_range": [0, MICROFACTOR_COUNT],
        "expected_factor_count": MICROFACTOR_COUNT,
        "completed_factor_count": len(results),
        "workers": args.workers,
        "width_limit": WIDTH_LIMIT,
        "run_timeout": args.run_timeout,
        "elapsed_seconds": time.perf_counter() - started,
        "all_passed": not failed and len(results) == MICROFACTOR_COUNT,
        "first_failure": failed[0] if failed else None,
        "construction": (
            "regenerated from A(r,omega0) with identically zero frequency "
            "Taylor coefficients; not a centre evaluation of a whole-cell hull"
        ),
        "sources": source_receipts,
        "results": results,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.rmtree(sources, ignore_errors=True)
    shutil.rmtree(binaries, ignore_errors=True)
    print(
        f"SUMMARY {args.summary} all_passed={summary['all_passed']} "
        f"completed={len(results)}/{MICROFACTOR_COUNT}"
    )
    return 0 if summary["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
