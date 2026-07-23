#!/usr/bin/env python3
"""Emit canonical split-leaf artifacts from a completed split batch."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from ..affine_rail import build_microfactor_render_context, render_microfactor_adapter
from .split_microfactor import build_split_handoff, split_geometry, trace_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    if (
        summary.get("schema") != "phase3-axial-dyadic-split-batch-v1"
        or summary.get("all_passed") is not True
    ):
        raise SystemExit("split batch is absent, incomplete, or refused")
    start, end = summary["parent_range"]
    depth = summary["depth"]
    args.output.mkdir(parents=True, exist_ok=True)
    context = build_microfactor_render_context()
    with tempfile.TemporaryDirectory(prefix="axial-split-emit-") as temp:
        temp_root = Path(temp)
        for parent in range(start, end):
            for child in range(1 << depth):
                panel_start, panel_count = split_geometry(parent, depth, child)
                tid = trace_id(parent, depth, child)
                source, _ = render_microfactor_adapter(
                    parent,
                    context=context,
                    panel_start=panel_start,
                    panel_count=panel_count,
                    trace_id=tid,
                )
                runner = temp_root / f"{tid}.forge"
                runner.write_text(source)
                log = args.logs / f"split_{parent:03d}_d{depth}_c{child}.log"
                if not log.is_file():
                    raise SystemExit(f"missing split log {log}")
                payload = build_split_handoff(
                    parent, depth, child, log.read_text(), args.repo_root,
                    runner=runner, context=context,
                )
                path = args.output / f"splitfactor_{parent:03d}_d{depth}_c{child}.json"
                path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
                print(f"PASS artifact {payload['factor_id']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
