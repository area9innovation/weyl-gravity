#!/usr/bin/env python3
"""Emit or check the residual mixed-ell3 branch-projection readiness receipt."""

from __future__ import annotations

import argparse
import json

from .berger_residual_ell3_branch_projection_readiness import HERE, build


OUTPUT = HERE / "certificates/BERGER_RESIDUAL_MIXED_ELL3_BRANCH_PROJECTION_READINESS.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit("stale residual ell3 branch-projection readiness certificate")
    print("BERGER RESIDUAL ELL3 BRANCH PROJECTION: CONSUMER READY; INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
