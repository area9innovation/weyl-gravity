#!/usr/bin/env python3
"""Run a bounded parallel batch of exact dyadic radial replacement leaves."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..affine_rail import build_microfactor_render_context, render_microfactor_adapter
from .run_microfactor_batch import _run_one
from .split_microfactor import WIDTH_LIMIT, split_geometry, trace_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-parent", type=int, required=True)
    parser.add_argument("--end-parent", type=int, required=True)
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--run-timeout", type=float, default=900.0)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    if not (0 <= args.start_parent < args.end_parent <= 224):
        raise SystemExit("bad parent range")
    if args.depth not in (1, 2, 3):
        raise SystemExit("depth must lie in [1,3]")
    if not (1 <= args.workers <= 8):
        raise SystemExit("workers must lie in [1,8]")

    args.scratch.mkdir(parents=True, exist_ok=True)
    sources = args.scratch / "sources"
    binaries = args.scratch / "bin"
    logs = args.scratch / "logs"
    for directory in (sources, binaries, logs):
        directory.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    context = build_microfactor_render_context()
    jobs = []
    source_receipts = []
    for parent in range(args.start_parent, args.end_parent):
        for child in range(1 << args.depth):
            start, count = split_geometry(parent, args.depth, child)
            tid = trace_id(parent, args.depth, child)
            text, metadata = render_microfactor_adapter(
                parent,
                context=context,
                panel_start=start,
                panel_count=count,
                trace_id=tid,
            )
            source = sources / f"split_{parent:03d}_d{args.depth}_c{child}.forge"
            source.write_text(text)
            digest = hashlib.sha256(text.encode()).hexdigest()
            log = logs / f"split_{parent:03d}_d{args.depth}_c{child}.log"
            jobs.append(
                (
                    tid, source,
                    binaries / f"split_{parent:03d}_d{args.depth}_c{child}",
                    log, digest, WIDTH_LIMIT, args.run_timeout,
                )
            )
            source_receipts.append({
                "parent": parent,
                "depth": args.depth,
                "child": child,
                "trace_id": tid,
                "global_panel_start": start,
                "panel_count": count,
                "source_sha256": digest,
                "frame_table_sha256": metadata["frame_table_sha256"],
            })

    results = []
    refusal = False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_run_one, *job): job[0] for job in jobs}
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
            tid = result["micro"]
            job = next(job for job in jobs if job[0] == tid)
            job[1].unlink(missing_ok=True)
            job[2].unlink(missing_ok=True)

    results.sort(key=lambda value: value["micro"])
    failed = [item for item in results if item["status"] != "PASS"]
    summary = {
        "schema": "phase3-axial-dyadic-split-batch-v1",
        "parent_range": [args.start_parent, args.end_parent],
        "depth": args.depth,
        "workers": args.workers,
        "width_limit": WIDTH_LIMIT,
        "run_timeout": args.run_timeout,
        "render_seconds": time.perf_counter() - started,
        "all_passed": not failed,
        "first_failure": failed[0] if failed else None,
        "sources": source_receipts,
        "results": results,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    shutil.rmtree(sources, ignore_errors=True)
    shutil.rmtree(binaries, ignore_errors=True)
    print(f"SUMMARY {args.summary} all_passed={not failed}")
    return 0 if not failed else 3


if __name__ == "__main__":
    raise SystemExit(main())
