#!/usr/bin/env python3
"""Emit canonical artifacts from a completed ephemeral-source batch run."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from ..affine_rail import (
    MICROFACTOR_COUNT,
    build_microfactor_render_context,
    render_microfactor_adapter,
)
from .emit_microfactor import build_handoff
from .verify_microfactor import verify_microfactor, verify_microfactor_chain


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=MICROFACTOR_COUNT)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--verify-chain", action="store_true",
        help="require and verify the complete ordered 224-factor chain",
    )
    args = parser.parse_args()
    if not (0 <= args.start < args.end <= MICROFACTOR_COUNT):
        raise SystemExit("expected 0 <= start < end <= 224")

    args.output.mkdir(parents=True, exist_ok=True)
    context = build_microfactor_render_context()
    artifacts = []
    with tempfile.TemporaryDirectory(prefix="axial-v6-emit-") as temp:
        temp_root = Path(temp)
        for micro in range(args.start, args.end):
            log = args.logs / f"microfactor_{micro:03d}.log"
            if not log.is_file():
                raise SystemExit(f"missing log for micro {micro}: {log}")
            text, _ = render_microfactor_adapter(micro, context=context)
            runner = temp_root / f"microfactor_{micro:03d}.forge"
            runner.write_text(text)
            artifact = build_handoff(
                micro, log.read_text(), args.repo_root, runner_override=runner
            )
            verify_microfactor(artifact, args.repo_root)
            path = args.output / f"microfactor_{micro:03d}.json"
            path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
            artifacts.append(artifact)
            print(f"PASS artifact micro={micro}", flush=True)
    if args.verify_chain:
        if args.start != 0 or args.end != MICROFACTOR_COUNT:
            raise SystemExit("--verify-chain requires the full range [0,224)")
        verify_microfactor_chain(artifacts, args.repo_root)
        print("PASS complete ordered microfactor chain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
