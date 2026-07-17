#!/usr/bin/env python3
"""Emit or check retained stationary-generator import readiness."""

from __future__ import annotations

import argparse
import json

try:
    from .berger_retained_stationary_generator_acceptance import HERE
    from .berger_retained_stationary_generator_readiness import build
except ImportError:
    from berger_retained_stationary_generator_acceptance import HERE
    from berger_retained_stationary_generator_readiness import build


OUTPUT = HERE / "certificates/BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(text)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != text):
        raise SystemExit("stale stationary-generator import-readiness certificate")
    print("BERGER STATIONARY GENERATOR IMPORT: CONSUMER READY; INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
