#!/usr/bin/env python3
"""Verify the rank-14 Green-witness companion-cycle diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_equation_cycle_gate import (  # noqa: E402
    Rank14EquationCycleGate,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_equation_cycle_gate.json"
)


def _validate(value: dict[str, object]) -> None:
    typed = value.get("typed_translation")
    literal = value.get("literal_shorthand_audit")
    decision = value.get("decision")
    atomic = value.get("warranted_atomic_flags")
    if not all(isinstance(item, dict) for item in (typed, literal, decision, atomic)):
        raise AssertionError("equation-cycle sections are missing")
    assert isinstance(typed, dict) and isinstance(literal, dict)
    assert isinstance(decision, dict) and isinstance(atomic, dict)
    if typed.get("cycle_relation_defect") != 0:
        raise AssertionError("typed cycle relation was promoted with a defect")
    if literal.get("literally_well_typed"):
        raise AssertionError("order/type-mismatched shorthand was accepted")
    if not decision.get("canonical_equation_cone_certified"):
        raise AssertionError("exact equation cone was lost")
    if decision.get("strict_F_only_lift_certified"):
        raise AssertionError("an F-only lift was inferred by dropping A_C")
    if atomic != {
        "rank14_witness_companion_cycle_gate_exact": True,
    }:
        raise AssertionError("equation-cycle atomic flag metadata drifted")
    if value.get("prolonged_green_witness"):
        raise AssertionError("principal gate overpromoted Green witness")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    certificate = Rank14EquationCycleGate.build(workers=args.workers).certificate()
    _validate(certificate)
    if args.guards:
        bad = json.loads(json.dumps(certificate))
        bad["literal_shorthand_audit"]["literally_well_typed"] = True
        try:
            _validate(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("literal-shorthand mutation was accepted")
        bad = json.loads(json.dumps(certificate))
        bad["decision"]["strict_F_only_lift_certified"] = True
        try:
            _validate(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("A_C-deletion mutation was accepted")
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "rank14 equation-cycle gate: "
        f"cone rank={certificate['canonical_equation_cone']['generic_rank']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
