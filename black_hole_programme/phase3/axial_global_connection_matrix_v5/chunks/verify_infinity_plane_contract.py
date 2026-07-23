#!/usr/bin/env python3
"""Replay the exact two-plane infinity propagation contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .infinity_plane_contract import verify_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    verify_contract(json.loads(args.artifact.read_text()))
    print("PASS infinity physical-plane contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
