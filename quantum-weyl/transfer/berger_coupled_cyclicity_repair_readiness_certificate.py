#!/usr/bin/env python3
"""Emit or check coupled Berger q2 repair-acceptance readiness."""

from __future__ import annotations

import argparse
import json

try:
    from .berger_coupled_cyclicity_repair_readiness import FIXTURE, HERE, build
except ImportError:
    from berger_coupled_cyclicity_repair_readiness import FIXTURE, HERE, build


OUTPUT = HERE / "certificates/BERGER_COUPLED_CYCLICITY_REPAIR_ACCEPTANCE_READINESS.json"


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, fixture = build()
    certificate_text = _json(certificate)
    fixture_text = _json(fixture)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(certificate_text)
        FIXTURE.write_text(fixture_text)
    if args.check and (
        not OUTPUT.exists()
        or OUTPUT.read_text() != certificate_text
        or not FIXTURE.exists()
        or FIXTURE.read_text() != fixture_text
    ):
        raise SystemExit("stale repair-acceptance readiness certificate or fixture")
    print("BERGER COUPLED Q2 REPAIR ACCEPTANCE: CONSUMER READY; CORRECTED INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
