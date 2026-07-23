#!/usr/bin/env python3
"""Run a staged degree-two infinity-plane transport sentinel."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .infinity_plane_factor_manifest import STAGE_BOUNDARIES
from .infinity_plane_taylor_transport import run_stage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", type=int, default=0)
    parser.add_argument("--start-stage", type=int, default=0)
    parser.add_argument(
        "--end-stage", type=int, default=len(STAGE_BOUNDARIES) - 1
    )
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not (
        0 <= args.start_stage < args.end_stage
        <= len(STAGE_BOUNDARIES) - 1
    ):
        raise SystemExit("bad stage range")
    previous = None
    if args.start_stage:
        path = (
            args.output_dir
            / f"q{args.child:02d}-stage{args.start_stage - 1}.json"
        )
        previous = json.loads(path.read_text())
    for stage in range(args.start_stage, args.end_stage):
        output = args.output_dir / f"q{args.child:02d}-stage{stage}.json"
        previous = run_stage(
            child=args.child,
            stage=stage,
            artifact_dir=args.artifact_dir,
            repo_root=args.repo_root,
            previous=previous,
            scratch=args.scratch,
            output=output,
        )
        print(
            f"PASS child={args.child} stage={stage} "
            f"ranks={previous['terminal_ranks']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
