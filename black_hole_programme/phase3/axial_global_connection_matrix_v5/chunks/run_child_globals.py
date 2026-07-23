#!/usr/bin/env python3
"""Execute and emit all sixteen exact child global radial maps."""
from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import frequency_cell
from .compose_child_global import build_global, composition_factors
from .join_microfactors import render_join_source


def _run(source: Path, binary: Path, log: Path, timeout: float) -> dict:
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
    return {"status": "PASS", "log": str(log)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument(
        "--tail-factor-dir",
        type=Path,
        required=True,
        help="Directory containing the emitted child tail factor artifacts.",
    )
    parser.add_argument("--tail-join-dir", type=Path, required=True)
    parser.add_argument("--prefix", type=Path, required=True)
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
    prefix = json.loads(args.prefix.read_text())
    prefix_context = build_microfactor_render_context()
    contexts, tails, sources, jobs = {}, {}, {}, []
    child_range = range(args.start_child, args.end_child)
    for child in child_range:
        context = build_microfactor_render_context(frequency_cell(child))
        contexts[child] = context
        tail_path = args.tail_join_dir / f"child_tail_join_q{child:02d}.json"
        if not tail_path.is_file():
            raise SystemExit(f"missing tail join {tail_path}")
        tail = json.loads(tail_path.read_text())
        tails[child] = (tail_path, tail)
        source = args.scratch / f"global_q{child:02d}.forge"
        binary = args.scratch / f"global_q{child:02d}"
        log = args.scratch / f"global_q{child:02d}.log"
        factors = composition_factors(prefix, tail, child)
        source.write_text(
            render_join_source(factors, certify_join_rank=False)
        )
        crosswalk_source = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank.forge"
        )
        crosswalk_binary = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank"
        )
        crosswalk_log = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank.log"
        )
        crosswalk_source.write_text(render_join_source([factors[1]]))
        sources[child] = source
        jobs.append((
            child, source, binary, log,
            crosswalk_source, crosswalk_binary, crosswalk_log,
        ))
    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _run, source, binary, log, args.run_timeout
            ): child
            for child, source, binary, log, _, _, _ in jobs
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
        tail_path, tail = tails[child]
        crosswalk_source = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank.forge"
        )
        crosswalk_binary = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank"
        )
        crosswalk_log = (
            args.scratch / f"global_q{child:02d}_crosswalk_rank.log"
        )
        crosswalk_result = _run(
            crosswalk_source, crosswalk_binary, crosswalk_log,
            args.run_timeout,
        )
        if crosswalk_result["status"] != "PASS":
            results[child] = {
                "status": "REFUSED",
                "stage": "crosswalk-rank-" + crosswalk_result.get(
                    "stage", "unknown"
                ),
            }
            continue
        payload = build_global(
            child=child,
            trace=Path(result["log"]).read_text(),
            prefix=prefix,
            prefix_path=args.prefix,
            tail=tail,
            tail_path=tail_path,
            source=sources[child],
            crosswalk_trace=crosswalk_log.read_text(),
            crosswalk_source=crosswalk_source,
            prefix_artifact_dir=args.artifact_dir,
            tail_artifact_dir=args.tail_factor_dir,
            repo_root=args.repo_root,
            prefix_context=prefix_context,
            child_context=contexts[child],
        )
        output = args.output_dir / f"global_map_q{child:02d}.json"
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        artifacts.append(str(output))
    all_passed = (
        len(results) == len(child_range)
        and all(result["status"] == "PASS" for result in results.values())
        and len(artifacts) == len(child_range)
    )
    summary = {
        "schema": "phase3-axial-final-frequency-child-global-maps-v1",
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
