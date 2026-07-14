#!/usr/bin/env python3
"""Verify the rank-32 promoted Cotton-constraint hyperbolic candidate."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_promoted_constraints import (
    PROMOTED_CONSTRAINT_DIMENSION,
    PROMOTED_STATE_DIMENSION,
    PromotedCottonConstraintEvolution,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_promoted_constraints.json"
)


def _must_fail(candidate: PromotedCottonConstraintEvolution, label: str) -> None:
    try:
        candidate.verify()
    except AssertionError:
        return
    raise AssertionError(f"negative guard did not fail: {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    system = PromotedCottonConstraintEvolution.build()
    certificate = system.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if certificate["state_rank"] != PROMOTED_STATE_DIMENSION:
            raise AssertionError("promoted state rank drifted")
        if certificate["constraint_rank"] != PROMOTED_CONSTRAINT_DIMENSION:
            raise AssertionError("promoted constraint rank drifted")
        if not certificate["symmetrizer_positive"]:
            raise AssertionError("promoted positive symmetrizer regressed")
        if not certificate["spatial_symbols_self_adjoint"]:
            raise AssertionError("promoted symbol adjointness regressed")
        if not certificate["all_characteristics_causal"]:
            raise AssertionError("promoted causal cone regressed")
        if certificate["literal_formal_integrability_is_first_order"]:
            raise AssertionError("literal second-order row was called first order")
        if certificate["literal_second_order_rank_at_nonzero_xi"] != 1:
            raise AssertionError("literal second-order defect rank drifted")
        if certificate["covariant_differential_ideal_equivalence_audited"]:
            raise AssertionError("pending covariant row audit was inferred")
        if certificate["warranted_atomic_flags"] or certificate["flags_promoted_here"]:
            raise AssertionError("candidate promoted or warranted a status flag")

        bad_symmetrizer = system.symmetrizer.copy()
        bad_symmetrizer[26, 26] = -1
        _must_fail(
            replace(system, symmetrizer=bad_symmetrizer),
            "indefinite promoted symmetrizer",
        )
        bad_spatial = list(system.spatial_coefficients)
        bad_spatial[0] = bad_spatial[0].copy()
        bad_spatial[0][26, 29] += 1
        _must_fail(
            replace(system, spatial_coefficients=tuple(bad_spatial)),
            "promoted curl sign drift",
        )
        bad_second_order = list(system.literal_second_order_symbols)
        bad_second_order[0] = sp.zeros(3)
        _must_fail(
            replace(system, literal_second_order_symbols=tuple(bad_second_order)),
            "hidden literal second-order defect",
        )
        _must_fail(
            replace(system, representative_characteristic=sp.Integer(0)),
            "promoted characteristic drift",
        )
        guard_count = 9 + 4
        print(
            f"PROMOTED COTTON-CONSTRAINT GUARDS: "
            f"{guard_count}/{guard_count} PASS"
        )

    print(
        "PROMOTED COTTON CONSTRAINTS: RANK-32 FIRST-ORDER CANDIDATE "
        "SYMMETRIC HYPERBOLIC; COVARIANT ROW EQUIVALENCE OPEN"
    )


if __name__ == "__main__":
    main()
