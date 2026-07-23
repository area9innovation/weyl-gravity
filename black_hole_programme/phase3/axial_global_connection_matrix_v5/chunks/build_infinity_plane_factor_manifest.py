#!/usr/bin/env python3
"""Emit one exact infinity-plane radial factor manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .infinity_plane_factor_manifest import build_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", type=int, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_manifest(args.child, args.artifact_dir, args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
