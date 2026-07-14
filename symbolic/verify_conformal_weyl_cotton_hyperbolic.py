#!/usr/bin/env python3
"""Verify the constraint-adjusted rank-26 Weyl--Cotton evolution."""

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

from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    CONSTRAINT_DIMENSION,
    EVOLUTION_DIMENSION,
    ConstraintAdjustedWeylCottonEvolution,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_hyperbolic.json"
)


def _must_fail(candidate: ConstraintAdjustedWeylCottonEvolution, label: str) -> None:
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

    system = ConstraintAdjustedWeylCottonEvolution.build()
    certificate = system.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        if certificate["state_rank"] != EVOLUTION_DIMENSION:
            raise AssertionError("rank-26 curvature state drifted")
        if certificate["constraint_rank"] != CONSTRAINT_DIMENSION:
            raise AssertionError("rank-14 constraint state drifted")
        if not certificate["evolution_symmetrizer_positive"]:
            raise AssertionError("positive evolution symmetrizer regressed")
        if not certificate["evolution_spatial_symbols_self_adjoint"]:
            raise AssertionError("evolution spatial adjointness regressed")
        if not certificate["exact_sourced_subsidiary_operator_identity"]:
            raise AssertionError("sourced subsidiary identity regressed")
        if not certificate["homogeneous_constraints_propagate"]:
            raise AssertionError("constraint propagation regressed")
        if not certificate["all_characteristics_causal"]:
            raise AssertionError("causal characteristic cone regressed")
        if certificate["flags_promoted_here"]:
            raise AssertionError("focused certificate promoted repository flags")
        expected_candidates = {
            "curved_EB_symmetric_hyperbolicity",
            "curved_sourced_constraint_identity",
            "curved_constraint_propagation",
        }
        if set(
            certificate[
                "candidate_atomic_flags_if_covariant_row_equivalence_is_proved"
            ]
        ) != expected_candidates:
            raise AssertionError("candidate atomic-flag boundary drifted")
        if certificate["warranted_atomic_flags"]:
            raise AssertionError("unaudited rank-26 rows warranted a covariant flag")
        for forbidden in (
            "EAL_curvature_spectrum_match",
            "prolonged_BV_operator_identity",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
            "causal_green_homotopy",
        ):
            if certificate[forbidden]:
                raise AssertionError(f"focused PDE certificate inferred {forbidden}")
        if len(certificate["commuting_symbol_defect_nonzero_entries"]) != 6:
            raise AssertionError("unit-sphere commutator defect support drifted")
        if any(
            entry[2] != "-1"
            for entry in certificate["commuting_symbol_defect_nonzero_entries"]
        ):
            raise AssertionError("unit-sphere commutator defect coefficient drifted")

        bad_correction = system.sphere_curvature_correction.copy()
        bad_correction[6, 20] = 0
        _must_fail(
            replace(system, sphere_curvature_correction=bad_correction),
            "missing sphere curvature correction",
        )
        bad_symmetrizer = system.evolution_symmetrizer.copy()
        bad_symmetrizer[0, 0] = -1
        _must_fail(
            replace(system, evolution_symmetrizer=bad_symmetrizer),
            "indefinite evolution symmetrizer",
        )
        bad_spatial = list(system.evolution_spatial_coefficients)
        bad_spatial[0] = bad_spatial[0].copy()
        bad_spatial[0][0, 5] += 1
        _must_fail(
            replace(system, evolution_spatial_coefficients=tuple(bad_spatial)),
            "nonsymmetric evolution coefficient",
        )
        bad_subsidiary = list(system.constraint_spatial_coefficients)
        bad_subsidiary[0] = bad_subsidiary[0].copy()
        bad_subsidiary[0][0, 3] += 1
        _must_fail(
            replace(system, constraint_spatial_coefficients=tuple(bad_subsidiary)),
            "nonsymmetric subsidiary coefficient",
        )
        _must_fail(
            replace(system, representative_characteristic=sp.Integer(0)),
            "evolution characteristic drift",
        )
        _must_fail(
            replace(system, subsidiary_characteristic=sp.Integer(0)),
            "subsidiary characteristic drift",
        )
        guard_count = 13 + 6
        print(f"WEYL--COTTON HYPERBOLIC GUARDS: {guard_count}/{guard_count} PASS")

    print(
        "WEYL--COTTON HYPERBOLIC: RANK-26 SYMMETRIC-HYPERBOLIC "
        "EVOLUTION AND SOURCED SUBSIDIARY IDENTITY EXACT"
    )


if __name__ == "__main__":
    main()
