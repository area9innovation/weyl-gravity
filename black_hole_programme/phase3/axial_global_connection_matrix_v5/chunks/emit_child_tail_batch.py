#!/usr/bin/env python3
"""Emit typed child-tail factor artifacts from an all-pass batch summary."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from ..affine_rail import build_microfactor_render_context
from .child_cell_factor import (
    SCHEMA,
    build_factor,
    frequency_cell,
    render_factor,
    trace_id,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    if summary.get("schema") != "phase3-axial-final-frequency-child-tail-batch-v1":
        raise SystemExit("wrong child-tail batch schema")
    if not summary.get("all_passed"):
        raise SystemExit("REFUSED: child-tail batch did not pass completely")
    expected = summary["expected_factor_count"]
    if (
        summary["completed_factor_count"] != expected
        or len(summary["sources"]) != expected
        or len(summary["results"]) != expected
    ):
        raise SystemExit("REFUSED: child-tail batch is incomplete")
    source_by_trace = {item["trace_id"]: item for item in summary["sources"]}
    result_by_trace = {item["micro"]: item for item in summary["results"]}
    if len(source_by_trace) != expected or len(result_by_trace) != expected:
        raise SystemExit("REFUSED: duplicate trace ids in child-tail batch")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix_context = build_microfactor_render_context()
    emitted = []
    child_lo, child_hi = summary["frequency_child_range"]
    parent_lo, parent_hi = summary["tail_parent_range"]
    with tempfile.TemporaryDirectory(prefix="axial-child-tail-emit-") as temp:
        runner = Path(temp) / "runner.forge"
        for child in range(child_lo, child_hi):
            context = build_microfactor_render_context(frequency_cell(child))
            for parent in range(parent_lo, parent_hi):
                for leaf in (0, 1):
                    source, _, _ = render_factor(
                        child, parent, leaf, context=context
                    )
                    tid = trace_id(child, parent, leaf)
                    source_receipt = source_by_trace.get(tid)
                    result = result_by_trace.get(tid)
                    digest = hashlib.sha256(source.encode()).hexdigest()
                    if (
                        source_receipt is None or result is None
                        or source_receipt["source_sha256"] != digest
                        or result.get("source_sha256") != digest
                        or result.get("status") != "PASS"
                    ):
                        raise SystemExit(
                            f"REFUSED: source/result drift at trace {tid}"
                        )
                    log = Path(result["log"])
                    if not log.is_file():
                        raise SystemExit(f"REFUSED: missing log at trace {tid}")
                    runner.write_text(source)
                    payload = build_factor(
                        child, parent, leaf, log.read_text(), args.repo_root,
                        runner=runner, context=context,
                        prefix_context=prefix_context,
                    )
                    if payload["schema"] != SCHEMA:
                        raise SystemExit("REFUSED: wrong emitted factor schema")
                    output = (
                        args.output_dir
                        / f"child_q{child:02d}_p{parent:03d}_l{leaf}.json"
                    )
                    output.write_text(
                        json.dumps(payload, indent=2, sort_keys=True) + "\n"
                    )
                    emitted.append({
                        "factor_id": payload["factor_id"],
                        "path": output.resolve().relative_to(
                            args.repo_root.resolve()
                        ).as_posix(),
                        "sha256": _sha256(output),
                    })

    receipt = {
        "schema": "phase3-axial-final-frequency-child-tail-emission-v1",
        "status": "CERTIFIED",
        "batch_summary_sha256": _sha256(args.summary),
        "expected_factor_count": expected,
        "emitted_factor_count": len(emitted),
        "frequency_child_range": summary["frequency_child_range"],
        "tail_parent_range": summary["tail_parent_range"],
        "artifacts": emitted,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"PASS emitted {len(emitted)} typed child-tail factors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
