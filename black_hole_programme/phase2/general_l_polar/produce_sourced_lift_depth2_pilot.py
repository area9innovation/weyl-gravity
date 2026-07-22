#!/usr/bin/env python3
"""Produce the bounded, per-branch depth-2 sourced-lift pilot artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from black_hole_programme.phase2.general_l_polar.sourced_lift import derive_sourced_lift_branch


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
OUTPUT = HERE / "sourced_lift_depth2_pilot.json"


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _solution_denominator_factors(branches: list[dict[str, Any]]) -> list[str]:
    local = {
        "Lambda": sp.Symbol("Lambda"),
        "omega": sp.Symbol("omega", real=True, nonzero=True),
        "m": sp.Symbol("m", positive=True),
        "I": sp.I,
    }
    factors: set[str] = set()
    for branch in branches:
        for log_jets in branch["metric_jets_by_log_power"].values():
            for vector in log_jets:
                for serialized in vector:
                    denominator = sp.denom(sp.cancel(sp.sympify(serialized, locals=local)))
                    for factor, _ in sp.factor_list(denominator, extension=sp.I)[1]:
                        if factor.free_symbols:
                            factors.add(sp.sstr(sp.factor(factor)))
    return sorted(factors)


def build() -> dict[str, Any]:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    exact = certificate["exact_symbolic_lambda_result"]
    reconstruction = exact["ricci_to_metric_reconstruction"]
    carrier = exact["generic_carrier_asymptotics"]
    solved = [derive_sourced_lift_branch(reconstruction, carrier, "zero", index, depth=2) for index in range(3)]
    solved.append(derive_sourced_lift_branch(reconstruction, carrier, "oscillatory", 1, depth=2))
    factors = _solution_denominator_factors(solved)
    if factors != ["Lambda", "Lambda - 2"]:
        raise RuntimeError(f"solution denominator factors changed: {factors}")
    return {
        "schema": "phase2-sourced-lift-depth2-pilot-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "method": "DomainMatrix exact fraction-field augmented RREF (GJ), one simple branch per solve",
        "depth": 2,
        "input_subobject_sha256": {
            "ricci_to_metric_reconstruction": _canonical_sha256(reconstruction),
            "generic_carrier_asymptotics": _canonical_sha256(carrier),
        },
        "solved_branches": solved,
        "observed_elapsed_seconds": {"zero:0": "8.17", "zero:1": "10.27", "zero:2": "14.48", "oscillatory:1": "167.99"},
        "bounded_nonresults": [
            {"sector": "oscillatory", "branch_index": 0, "bound_seconds": 180, "reading": "NO_RESULT_WITHIN_BOUND_NOT_AN_OBSTRUCTION"},
            {"sector": "oscillatory", "branch_index": 2, "bound_seconds": 180, "reading": "NO_RESULT_WITHIN_BOUND_NOT_AN_OBSTRUCTION"},
        ],
        "solution_denominator_factors": factors,
        "rref_pivot_denominator_audit": "NOT_EXPOSED; additional generic-field pivot walls are not yet excluded",
        "scope": "finite depth-2 recurrence only; log degrees may change when deeper compatibility equations are imposed",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
            raise RuntimeError("sourced-lift depth-2 pilot regeneration drift")
    else:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("sourced-lift depth-2 pilot: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
