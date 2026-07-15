#!/usr/bin/env python3
"""Verify the fail-closed conditional all-row Green assembly."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_all_row_assembly import (  # noqa: E402
    ExpandedRelativeAllRowAssembly,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
SHIFTED = CERTIFICATES / "curved_expanded_relative_witness_shifted_green_filtration.json"
RANK34 = CERTIFICATES / "curved_expanded_relative_witness_rank34_module.json"
VECTOR = CERTIFICATES / "curved_expanded_relative_witness_vector_contraction.json"
SUBSTITUTION = CERTIFICATES / "curved_curvature_mapping_cylinder_substitution.json"
MAPPING_WITNESS = CERTIFICATES / "curved_curvature_mapping_cylinder_witness.json"
CURVATURE_WITNESS = CERTIFICATES / "curved_weyl_cotton_block_green_witness.json"
CURVATURE_CAUSAL = CERTIFICATES / "curved_weyl_cotton_causal_pde.json"
BRIDGE = CERTIFICATES / "curved_prolonged_green_bridge.json"
OUTPUT = CERTIFICATES / "curved_expanded_relative_witness_all_row_assembly.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _certificate(
    audit: ExpandedRelativeAllRowAssembly,
    shifted: dict[str, object],
    rank34: dict[str, object],
    vector: dict[str, object],
    substitution: dict[str, object],
    mapping_witness: dict[str, object],
    curvature_witness: dict[str, object],
    curvature_causal: dict[str, object],
    bridge: dict[str, object],
) -> dict[str, object]:
    return audit.certificate(
        shifted_certificate=shifted,
        rank34_certificate=rank34,
        vector_certificate=vector,
        mapping_substitution_certificate=substitution,
        mapping_witness_certificate=mapping_witness,
        curvature_witness_certificate=curvature_witness,
        curvature_causal_certificate=curvature_causal,
        bridge_certificate=bridge,
    )


def _rejects(*args: object) -> bool:
    try:
        _certificate(*args)  # type: ignore[arg-type]
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-complete-green", action="store_true")
    args = parser.parse_args()
    if args.claim_complete_green:
        raise SystemExit(
            "REFUSED: the projector-free rank-14 field-cokernel operator, "
            "Green maps and residual-source lifts have not been constructed"
        )

    shifted = _load(SHIFTED)
    rank34 = _load(RANK34)
    vector = _load(VECTOR)
    substitution = _load(SUBSTITUTION)
    mapping_witness = _load(MAPPING_WITNESS)
    curvature_witness = _load(CURVATURE_WITNESS)
    curvature_causal = _load(CURVATURE_CAUSAL)
    bridge = _load(BRIDGE)
    audit = ExpandedRelativeAllRowAssembly.build()
    certificate = _certificate(
        audit,
        shifted,
        rank34,
        vector,
        substitution,
        mapping_witness,
        curvature_witness,
        curvature_causal,
        bridge,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    analytic = certificate["analytic_116_coverage"]
    all_rows = certificate["all_BV_row_coverage"]
    formal = certificate["conditional_formal_assembly"]
    known = certificate["known_green_blocks"]
    missing = certificate["rank14_required_package"]
    closure = certificate["conditional_closure_theorem"]
    boundary = certificate["current_boundary"]
    atomic = certificate["warranted_atomic_flags"]
    checks = {
        "analytic_rank116_covered_once": analytic["rank_sum"] == 116,
        "rank34_filtration_complete": analytic["rank34_filtration_sum"] == 34,
        "restricted_block_not_double_counted": analytic[
            "restricted_TT_biwave_plus_fhat_is_inside_rank14"
        ]
        and not analytic["restricted_TT_block_counted_as_disjoint_sector"],
        "all_16_mapping_rows": all_rows["mapping_cylinder_blocks"] == 16
        and all_rows["coefficientwise_Q"],
        "all_row_SDR_exact": all_rows["Q_squared_defect"] == 0
        and all_rows["BV_pairing_defect"] == 0
        and all_rows["support_local_SDR"],
        "vector_BV_closure": all_rows["rank4_field_closes_to_vector_BV_rank"] == 16
        and all_rows["vector_primal_and_cotangent_rows"],
        "blockwise_QW": all(
            row["QW_plus_WQ_defect"] == 0
            for row in certificate["blockwise_witness_ledger"]
        ),
        "formal_Q_squared": formal["Q_squared_defect"] == 0,
        "formal_QW": formal["P_equals_QW_plus_WQ_defect"] == 0,
        "conditional_G_two_sided": formal["conditional_G_left_defect"] == 0
        and formal["conditional_G_right_defect"] == 0,
        "conditional_chain_commutation": formal[
            "conditional_QG_minus_GQ_defect"
        ]
        == 0,
        "conditional_homotopy": formal[
            "conditional_QWG_plus_WGQ_minus_identity_defect"
        ]
        == 0,
        "all_known_blocks_present": all(known.values()),
        "rank14_is_only_missing_sector": sum(
            not row["Green_input_supplied"]
            for row in certificate["blockwise_witness_ledger"]
        )
        == 1,
        "rank14_fail_closed": not missing["supplied"]
        and missing["field_cokernel_rank"] == 14
        and missing["must_be_projector_free"],
        "rank14_witness_required": any(
            "degree-minus-one V14" in item
            for item in missing["required_operator_data"]
        ),
        "source_lift_equations_explicit": len(
            missing["required_source_lift_equations"]
        )
        >= 8,
        "conditional_closure_exact": all(
            value
            for key, value in closure.items()
            if key not in ("hypothesis",)
        ),
        "boundary_names_rank14_only": boundary[
            "only_remaining_analytic_assembly_input"
        ].startswith("projector-free rank-14"),
        "unsplit_vs_graded_distinguished": boundary[
            "coefficientwise_existing_mapping_W_QW_identity"
        ]
        and boundary[
            "rank12_and_rank8_are_filtration_subquotients_not_split_W_blocks"
        ]
        and not boundary["coefficientwise_all_row_replacement_W_realized"],
        "no_global_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
        "atomic_conditional_flags": all(atomic.values()),
        "project_status_unchanged": certificate["status_flags_promoted"] == [],
    }

    if args.guards:
        bad_shifted = deepcopy(shifted)
        bad_shifted["actual_local_physical_replacement_witness"][
            "Q_Lambda_plus_Lambda_Q_defect"
        ] = 1
        bad_rank34 = deepcopy(rank34)
        bad_rank34["quotient_presentation"]["constraint_quotient_rank"] = 7
        bad_vector = deepcopy(vector)
        bad_vector["warranted_atomic_flags"][
            "shifted_rank4_vector_Green_homotopy"
        ] = False
        bad_substitution = deepcopy(substitution)
        bad_substitution["coefficientwise_complete_prolonged_Q"] = False
        bad_mapping = deepcopy(mapping_witness)
        bad_mapping["exact_identities"]["P_prol_equals_QW_plus_WQ"] = False
        bad_curvature = deepcopy(curvature_causal)
        bad_curvature["compatible_source_restriction"]["unique"] = False
        bad_bridge = deepcopy(bridge)
        bad_bridge["finite_triangular_green_theorem"]["left_inverse_defect"] = 1
        common = (
            audit,
            shifted,
            rank34,
            vector,
            substitution,
            mapping_witness,
            curvature_witness,
            curvature_causal,
            bridge,
        )
        checks.update(
            {
                "broken_physical_homotopy_rejected": _rejects(
                    audit,
                    bad_shifted,
                    *common[2:],
                ),
                "broken_rank8_ledger_rejected": _rejects(
                    audit,
                    shifted,
                    bad_rank34,
                    *common[3:],
                ),
                "broken_vector_contraction_rejected": _rejects(
                    audit,
                    shifted,
                    rank34,
                    bad_vector,
                    *common[4:],
                ),
                "incomplete_mapping_Q_rejected": _rejects(
                    audit,
                    shifted,
                    rank34,
                    vector,
                    bad_substitution,
                    *common[5:],
                ),
                "broken_mapping_QW_rejected": _rejects(
                    audit,
                    shifted,
                    rank34,
                    vector,
                    substitution,
                    bad_mapping,
                    *common[6:],
                ),
                "broken_source_compatibility_rejected": _rejects(
                    audit,
                    shifted,
                    rank34,
                    vector,
                    substitution,
                    mapping_witness,
                    curvature_witness,
                    bad_curvature,
                    bridge,
                ),
                "broken_triangular_theorem_rejected": _rejects(
                    audit,
                    shifted,
                    rank34,
                    vector,
                    substitution,
                    mapping_witness,
                    curvature_witness,
                    curvature_causal,
                    bad_bridge,
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"ALL-ROW ASSEMBLY: {sum(checks.values())}/{len(checks)} PASS")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
