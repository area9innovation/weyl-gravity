#!/usr/bin/env python3
"""Verify the exact shifted rank-four vector Green contraction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_vector_contraction import (  # noqa: E402
    ExpandedRelativeVectorContraction,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
RETRACT = CERTIFICATES / "curved_deformation_retract_status.json"
CANONICAL = CERTIFICATES / "curved_auxiliary_canonical_split.json"
SHIFTED = CERTIFICATES / "curved_expanded_relative_witness_shifted_green_filtration.json"
OUTPUT = CERTIFICATES / "curved_expanded_relative_witness_vector_contraction.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _rejects(
    audit: ExpandedRelativeVectorContraction,
    retract: dict[str, object],
    canonical: dict[str, object],
    shifted: dict[str, object],
) -> bool:
    try:
        audit.certificate(
            retract_certificate=retract,
            canonical_shift_certificate=canonical,
            shifted_filtration_certificate=shifted,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-full-green", action="store_true")
    args = parser.parse_args()
    if args.claim_full_green:
        raise SystemExit(
            "REFUSED: the vector replacement has not been inserted into a "
            "complete prolonged witness and the rank-34 block remains open"
        )

    retract = _load(RETRACT)
    canonical = _load(CANONICAL)
    shifted = _load(SHIFTED)
    audit = ExpandedRelativeVectorContraction.build()
    certificate = audit.certificate(
        retract_certificate=retract,
        canonical_shift_certificate=canonical,
        shifted_filtration_certificate=shifted,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    complex_data = certificate["shifted_vector_complex"]
    operator = certificate["exact_local_operator"]
    green = certificate["same_sided_green_operators"]
    homotopy = certificate["green_homotopy_contribution"]
    boundary = certificate["full_complex_boundary"]
    atomic = certificate["warranted_atomic_flags"]
    checks = {
        "actual_Q_direct_summand": complex_data["direct_summand_of_actual_curved_Q"],
        "rank4_field_singleton": complex_data["field_singleton_rank"] == 4
        and complex_data["dimension"] == 16,
        "all_vector_rows": complex_data["all_primal_and_cotangent_vector_rows_included"],
        "Q_squared": complex_data["Q_squared_defect"] == 0,
        "complete_operator_identity": operator["operator_identity_defect"] == 0
        and operator["complete_zeroth_order_coefficient"] == "I_16",
        "no_hidden_lower_order": operator["principal_derivative_coefficients"] == 0
        and operator["curvature_lower_order_terms"] == 0,
        "formal_adjoint": operator["formal_adjoint_defect"] == 0
        and green["G_plus_sharp_equals_G_minus"],
        "contractible_green_not_wave": operator["Green_hyperbolic"]
        and not operator["normally_hyperbolic"],
        "advanced_two_sided": green["advanced_left_defect"] == 0
        and green["advanced_right_defect"] == 0,
        "retarded_two_sided": green["retarded_left_defect"] == 0
        and green["retarded_right_defect"] == 0,
        "same_sided_support": green["finite_propagation"],
        "advanced_homotopy": homotopy[
            "Q_Lambda_plus_plus_Lambda_plus_Q_defect"
        ]
        == 0,
        "retarded_homotopy": homotopy[
            "Q_Lambda_minus_plus_Lambda_minus_Q_defect"
        ]
        == 0,
        "atomic_vector_flags": all(atomic.values()),
        "atomic_vector_flags_promoted": certificate["status_flags_promoted"]
        == atomic,
        "fixed_candidate_not_overclaimed": not boundary[
            "fixed_witness_second_order_vector_block_inverted"
        ],
        "all_row_boundary_visible": not boundary[
            "replacement_inserted_into_complete_prolonged_W"
        ]
        and not boundary["all_BV_rows_complete_QLambda_identity"],
        "no_global_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_retract = deepcopy(retract)
        bad_retract["factorized_actual_curved_Q"][
            "actual_curved_Q_conjugation_verified"
        ] = False
        bad_canonical = deepcopy(canonical)
        bad_canonical["universal_generalized_auxiliary_split"][
            "pointwise_after_shift"
        ] = False
        bad_shifted = deepcopy(shifted)
        bad_shifted["full_complex_boundary"][
            "rank4_vector_singleton_Green_inverse"
        ] = True
        checks.update(
            {
                "broken_curved_Q_split_rejected": _rejects(
                    audit, bad_retract, canonical, shifted
                ),
                "broken_pointwise_split_rejected": _rejects(
                    audit, retract, bad_canonical, shifted
                ),
                "stale_open-ledger_mutation_rejected": _rejects(
                    audit, retract, canonical, bad_shifted
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"VECTOR CONTRACTION: {sum(checks.values())}/{len(checks)} PASS")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
