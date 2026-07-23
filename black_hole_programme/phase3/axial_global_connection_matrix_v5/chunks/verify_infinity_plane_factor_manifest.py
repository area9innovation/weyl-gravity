#!/usr/bin/env python3
"""Replay one exact infinity-plane radial factor manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .infinity_plane_factor_manifest import verify_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--child", type=int, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    verify_manifest(
        json.loads(args.artifact.read_text()),
        args.child, args.artifact_dir, args.repo_root,
    )
    print("PASS infinity physical-plane factor manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
