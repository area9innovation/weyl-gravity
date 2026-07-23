#!/usr/bin/env python3
"""Render, execute, and emit the sixteen exact child-tail joins."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import frequency_cell
from .child_tail_join import build_join, load_cover
from .join_microfactors import render_join_source


def _run(source: Path, binary: Path, log: Path, timeout: float) -> dict:
    started = time.perf_counter()
    compiled = subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        text=True, capture_output=True, timeout=300, check=False,
    )
    if compiled.returncode:
        return {
            "status": "REFUSED", "stage": "compile",
            "stderr": compiled.stderr[-4000:],
        }
    ran = subprocess.run(
        [str(binary)], text=True, capture_output=True,
        timeout=timeout, check=False,
    )
    log.write_text(ran.stdout)
    binary.unlink(missing_ok=True)
    if ran.returncode != 42:
        return {
            "status": "REFUSED", "stage": "run",
            "returncode": ran.returncode, "stderr": ran.stderr[-4000:],
        }
    return {
        "status": "PASS",
        "elapsed_seconds": time.perf_counter() - started,
        "log": str(log),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--start-child", type=int, default=0)
    parser.add_argument("--end-child", type=int, default=16)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--run-timeout", type=float, default=900.0)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise SystemExit("workers must lie in [1,4]")
    if not 0 <= args.start_child < args.end_child <= 16:
        raise SystemExit("expected 0 <= start-child < end-child <= 16")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    prefix_context = build_microfactor_render_context()
    contexts, sources, jobs = {}, {}, []
    child_range = range(args.start_child, args.end_child)
    for child in child_range:
        context = build_microfactor_render_context(frequency_cell(child))
        contexts[child] = context
        _, payloads = load_cover(
            args.artifact_dir, child, args.repo_root,
            context=context, prefix_context=prefix_context,
        )
        source = args.scratch / f"child_tail_q{child:02d}.forge"
        binary = args.scratch / f"child_tail_q{child:02d}"
        log = args.scratch / f"child_tail_q{child:02d}.log"
        source.write_text(
            render_join_source(payloads, certify_join_rank=False)
        )
        sources[child] = source
        jobs.append((child, source, binary, log))

    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _run, source, binary, log, args.run_timeout
            ): child
            for child, source, binary, log in jobs
        }
        for future in as_completed(futures):
            child = futures[future]
            result = future.result()
            results[child] = result
            print(
                f"{result['status']} child=q{child:02d} "
                f"stage={result.get('stage', 'complete')}",
                flush=True,
            )

    artifacts = []
    for child in child_range:
        result = results[child]
        if result["status"] != "PASS":
            continue
        payload = build_join(
            child=child,
            trace=Path(result["log"]).read_text(),
            artifact_dir=args.artifact_dir,
            source=sources[child],
            repo_root=args.repo_root,
            context=contexts[child],
            prefix_context=prefix_context,
        )
        output = args.output_dir / f"child_tail_join_q{child:02d}.json"
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        artifacts.append(str(output))
    all_passed = (
        len(results) == len(child_range)
        and all(result["status"] == "PASS" for result in results.values())
        and len(artifacts) == len(child_range)
    )
    summary = {
        "schema": "phase3-axial-final-frequency-child-tail-joins-v1",
        "frequency_child_range": [
            args.start_child, args.end_child,
        ],
        "all_passed": all_passed,
        "results": [
            {"frequency_child": child, **results[child]}
            for child in sorted(results)
        ],
        "artifacts": artifacts,
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        f"SUMMARY all_passed={all_passed} "
        f"artifacts={len(artifacts)}/{len(child_range)}"
    )
    return 0 if all_passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
