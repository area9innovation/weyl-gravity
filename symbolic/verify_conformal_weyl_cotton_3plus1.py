#!/usr/bin/env python3
"""Verify and emit the exact algebraic Weyl/Cotton 3+1 decomposition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_3plus1 import (
    COTTON_DIMENSION,
    WEYL_DIMENSION,
    WeylCottonBachFirstOrder,
    WeylCottonThreePlusOne,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_3plus1.json"
)
BACH_CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_bach_first_order.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    decomposition = WeylCottonThreePlusOne.build()
    certificate = decomposition.certificate()
    bach = WeylCottonBachFirstOrder.build()
    bach_certificate = bach.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))
        BACH_CERTIFICATE.write_text(
            json.dumps(bach_certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", BACH_CERTIFICATE.relative_to(ROOT))
    if args.guards:
        checks = {
            "Weyl rank": certificate["weyl_reconstruction_rank"] == WEYL_DIMENSION,
            "E/B inverse": certificate["electric_magnetic_extraction_inverse"],
            "Weyl identities": certificate["weyl_symmetries_trace_and_bianchi"],
            "Weyl Hodge": certificate["weyl_hodge_square"] == "-I_10",
            "Cotton rank": certificate["cotton_bundle_dimension"] == COTTON_DIMENSION,
            "dual Cotton slot": certificate["dual_divergence_joint_dimension"]
            == COTTON_DIMENSION,
            "Cotton Hodge": certificate["cotton_hodge_square"] == "-I_16",
            "Cotton coefficient tables": certificate[
                "cotton_first_order_table_shapes"
            ]
            == [[COTTON_DIMENSION, WEYL_DIMENSION]] * 4,
            "dual Cotton algebraic": certificate["dual_cotton_is_algebraic"],
            "four directional ranks": certificate["directional_divergence_ranks"]
            == [WEYL_DIMENSION] * 4,
            "Cotton SO(3) decomposition": certificate["SO3_decomposition"]
            == "2 x (STF_2[5] + vector[3])",
            "no E/B-only closure": not certificate[
                "ten_component_EB_first_order_closure_assumed"
            ],
            "no fitted coefficients": not certificate["fitted_coefficients"],
            "Weyl/Cotton state rank": bach_certificate["state_bundle"]["total"]
            == 26,
            "covariant row count": bach_certificate["equation_rows"]["total"]
            == 34,
            "all time derivatives": bach_certificate["temporal_matrix_rank"] == 26,
            "eight principal constraints": bach_certificate[
                "principal_constraint_count"
            ]
            == 8,
            "Ricci lower term": bach_certificate[
                "cylinder_Ricci_lower_term_included"
            ],
            "exact Hodge dual rows": bach_certificate[
                "dual_rows_induced_by_exact_Hodge"
            ],
            "first-order closure table": bach_certificate[
                "first_order_covariant_closure_table_derived"
            ],
            "unadjusted reduction rejected": not bach_certificate[
                "canonical_unadjusted_reduction_hyperbolic"
            ],
            "constraint addition required": bach_certificate[
                "constraint_addition_required_for_hyperbolic_reduction"
            ],
            "no premature evolution split": not bach_certificate[
                "evolution_constraint_split_derived"
            ],
            "no premature hyperbolicity": not bach_certificate[
                "symmetric_hyperbolicity_proved"
            ],
            "no premature sourced identity": not bach_certificate[
                "sourced_constraint_identity_proved"
            ],
            "no premature jet theorem": not bach_certificate[
                "exhaustive_curved_jet_comparison_proved"
            ],
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise AssertionError(f"Weyl/Cotton 3+1 guards failed: {failed}")
        print(f"WEYL/COTTON 3+1 GUARDS: {len(checks)}/{len(checks)} PASS")
    print("WEYL/COTTON 3+1: EXACT ALGEBRAIC DECOMPOSITION CERTIFIED")


if __name__ == "__main__":
    main()
