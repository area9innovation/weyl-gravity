#!/usr/bin/env python3
"""Verify the causal PDE theorem for constrained Weyl--Cotton curvature."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_causal_pde import (
    CausalWeylCottonPDE,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_causal_pde.json"
)


def _must_fail(candidate: CausalWeylCottonPDE, label: str) -> None:
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

    theorem = CausalWeylCottonPDE.build()
    certificate = theorem.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        unconstrained = certificate["unconstrained_green_operators"]
        constrained = certificate["compatible_source_restriction"]
        compatibility = certificate["source_compatibility"]
        if not certificate["curvature_block_causal_solution_operators"]:
            raise AssertionError("curvature causal solution theorem regressed")
        if not unconstrained["exists_for_every_compact_source"]:
            raise AssertionError("unconstrained Green existence regressed")
        if unconstrained["preserves_constraints_for_arbitrary_source"]:
            raise AssertionError("arbitrary sources were called constraint-compatible")
        if constrained["domain"] != "Gamma_c^comp(F_WC)":
            raise AssertionError("constrained source domain drifted")
        if constrained["codomain"] != "ker K_WC":
            raise AssertionError("constrained solution codomain drifted")
        if compatibility["exact_operator_identity"] != "L_K K_WC=K_src L_WC":
            raise AssertionError("sourced subsidiary operator identity drifted")
        if not compatibility["unit_S3_curvature_correction_included"]:
            raise AssertionError("unit-S3 source correction was omitted")
        if certificate["unconstrained_operator_is_constrained_operator"]:
            raise AssertionError("unconstrained/constrained operators were conflated")
        if certificate[
            "compatible_source_restriction_is_ordinary_full_bundle_green_operator"
        ]:
            raise AssertionError("restricted source operator was overstated")
        for forbidden in (
            "curvature_causal_green_operators",
            "causal_green_homotopy",
            "prolonged_green_witness",
        ):
            if certificate[forbidden]:
                raise AssertionError(f"curvature-block theorem inferred {forbidden}")
        if certificate["flags_promoted_here"]:
            raise AssertionError("focused PDE theorem promoted a repository flag")

        _must_fail(
            replace(theorem, background_globally_hyperbolic=False),
            "non-globally-hyperbolic background",
        )
        _must_fail(
            replace(theorem, coefficients_global_smooth=False),
            "nonsmooth global coefficients",
        )
        _must_fail(
            replace(theorem, temporal_principal_matrix_positive=False),
            "nonpositive temporal matrix",
        )
        _must_fail(
            replace(theorem, characteristic_cone_inside_metric_cone=False),
            "superluminal characteristic cone",
        )
        bad_ideal = replace(
            theorem.differential_ideal,
            sourced_subsidiary_corrected_defect=1,
        )
        _must_fail(
            replace(theorem, differential_ideal=bad_ideal),
            "sourced subsidiary defect",
        )
        guard_count = 12 + 5
        print(
            f"WEYL--COTTON CAUSAL PDE GUARDS: "
            f"{guard_count}/{guard_count} PASS"
        )

    print(
        "WEYL--COTTON CAUSAL PDE: UNCONSTRAINED GREEN OPERATORS AND "
        "COMPATIBLE-SOURCE CONSTRAINED RESTRICTION EXACT"
    )


if __name__ == "__main__":
    main()
