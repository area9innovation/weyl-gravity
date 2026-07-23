#!/usr/bin/env python3
"""Run the exact final-frequency child tail factors in bounded parallel."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import (
    FREQUENCY_CHILDREN,
    TAIL_END_PARENT,
    TAIL_START_PARENT,
    frequency_cell,
    render_factor,
    trace_id,
)
from .run_microfactor_batch import _run_one
from .split_microfactor import WIDTH_LIMIT


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-child", type=int, default=0)
    parser.add_argument("--end-child", type=int, default=FREQUENCY_CHILDREN)
    parser.add_argument("--start-parent", type=int, default=TAIL_START_PARENT)
    parser.add_argument("--end-parent", type=int, default=TAIL_END_PARENT)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--run-timeout", type=float, default=900.0)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not 0 <= args.start_child < args.end_child <= FREQUENCY_CHILDREN:
        raise SystemExit("bad frequency-child range")
    if not (
        TAIL_START_PARENT <= args.start_parent
        < args.end_parent <= TAIL_END_PARENT
    ):
        raise SystemExit("bad tail-parent range")
    if not 1 <= args.workers <= 8:
        raise SystemExit("workers must lie in [1,8]")

    sources = args.scratch / "sources"
    binaries = args.scratch / "bin"
    logs = args.scratch / "logs"
    for directory in (sources, binaries, logs):
        directory.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    jobs, source_receipts = [], []
    for child in range(args.start_child, args.end_child):
        context = build_microfactor_render_context(frequency_cell(child))
        for parent in range(args.start_parent, args.end_parent):
            for leaf in (0, 1):
                tid = trace_id(child, parent, leaf)
                text, metadata, _ = render_factor(
                    child, parent, leaf, context=context
                )
                stem = f"q{child:02d}_micro_{parent:03d}_leaf_{leaf}"
                source = sources / f"{stem}.forge"
                binary = binaries / stem
                log = logs / f"{stem}.log"
                source.write_text(text)
                digest = hashlib.sha256(text.encode()).hexdigest()
                jobs.append((
                    tid, source, binary, log, digest, WIDTH_LIMIT,
                    args.run_timeout,
                ))
                source_receipts.append({
                    "frequency_child": child,
                    "parent": parent,
                    "leaf": leaf,
                    "trace_id": tid,
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
            job = futures[future]
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
            job[1].unlink(missing_ok=True)
            job[2].unlink(missing_ok=True)

    results.sort(key=lambda value: value["micro"])
    failed = [item for item in results if item["status"] != "PASS"]
    expected = (
        (args.end_child - args.start_child)
        * (args.end_parent - args.start_parent) * 2
    )
    summary = {
        "schema": "phase3-axial-final-frequency-child-tail-batch-v1",
        "frequency_child_range": [args.start_child, args.end_child],
        "tail_parent_range": [args.start_parent, args.end_parent],
        "leaves_per_parent": 2,
        "expected_factor_count": expected,
        "completed_factor_count": len(results),
        "workers": args.workers,
        "width_limit": WIDTH_LIMIT,
        "run_timeout": args.run_timeout,
        "elapsed_seconds": time.perf_counter() - started,
        "all_passed": not failed and len(results) == expected,
        "first_failure": failed[0] if failed else None,
        "sources": source_receipts,
        "results": results,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.rmtree(sources, ignore_errors=True)
    shutil.rmtree(binaries, ignore_errors=True)
    print(
        f"SUMMARY {args.summary} all_passed={summary['all_passed']} "
        f"completed={len(results)}/{expected}"
    )
    return 0 if summary["all_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
