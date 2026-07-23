#!/usr/bin/env python3
"""Emit the frozen mixed-depth split part of the exact radial prefix cover."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from ..affine_rail import build_microfactor_render_context, render_microfactor_adapter
from .split_microfactor import (
    build_split_handoff,
    split_geometry,
    trace_id,
)


PLAN = {
    182: 1,
    183: 1,
    184: 1,
    185: 2,
    186: 2,
    187: 2,
    188: 2,
    189: 2,
    190: 2,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs-182-a", type=Path, required=True)
    parser.add_argument("--logs-182-b", type=Path, required=True)
    parser.add_argument("--logs-d1", type=Path, required=True)
    parser.add_argument("--logs-d2", type=Path, required=True)
    parser.add_argument("--logs-d2-tail", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    context = build_microfactor_render_context()
    emitted = []
    with tempfile.TemporaryDirectory(prefix="axial-prefix-split-") as temp:
        runner = Path(temp) / "runner.forge"
        for parent, depth in PLAN.items():
            for child in range(1 << depth):
                if parent == 182:
                    log = args.logs_182_a if child == 0 else args.logs_182_b
                elif parent <= 184:
                    log = args.logs_d1 / (
                        f"split_{parent:03d}_d{depth}_c{child}.log"
                    )
                elif parent <= 186:
                    log = args.logs_d2 / (
                        f"split_{parent:03d}_d{depth}_c{child}.log"
                    )
                else:
                    log = args.logs_d2_tail / (
                        f"split_{parent:03d}_d{depth}_c{child}.log"
                    )
                if not log.is_file():
                    raise SystemExit(f"REFUSED: missing prefix log {log}")
                start, count = split_geometry(parent, depth, child)
                tid = trace_id(parent, depth, child)
                source, _ = render_microfactor_adapter(
                    parent, context=context, panel_start=start,
                    panel_count=count, trace_id=tid,
                )
                runner.write_text(source)
                payload = build_split_handoff(
                    parent, depth, child, log.read_text(), args.repo_root,
                    runner=runner, context=context,
                )
                output = (
                    args.output
                    / f"splitfactor_{parent:03d}_d{depth}_c{child}.json"
                )
                output.write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n"
                )
                emitted.append(payload["factor_id"])
                print(f"PASS artifact {payload['factor_id']}", flush=True)
    receipt = {
        "schema": "phase3-axial-prefix-split-cover-emission-v1",
        "status": "CERTIFIED",
        "parent_depth_plan": {str(key): value for key, value in PLAN.items()},
        "factor_count": len(emitted),
        "factor_ids": emitted,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"PASS prefix split cover factors={len(emitted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
