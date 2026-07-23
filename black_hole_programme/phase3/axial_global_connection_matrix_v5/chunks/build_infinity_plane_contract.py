#!/usr/bin/env python3
"""Emit the exact two-plane infinity propagation contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .infinity_plane_contract import contract_payload, verify_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = contract_payload()
    verify_contract(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
