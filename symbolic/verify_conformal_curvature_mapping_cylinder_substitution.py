#!/usr/bin/env python3
"""Verify coefficient substitution into the curvature cotangent cylinder."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_mapping_cylinder_substitution import (
    CurvatureMappingCylinderSubstitution,
)
from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    CurvatureMappingCylinderKernel,
)
from covariant_completion.curved_retract.curved_core_curvature_chain_map import (
    CurvedCoreCurvatureChainMap,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
STATE_GAUGE = CERTIFICATE_DIR / "curved_curvature_state_gauge_chain_map.json"
LINEARIZED_BACH = CERTIFICATE_DIR / "linearized_bach.json"
EQUATION = CERTIFICATE_DIR / "curved_curvature_auxiliary_chain_map.json"
CORE_CHAIN = CERTIFICATE_DIR / "curved_core_curvature_chain_map.json"
CURVED_RETRACT = CERTIFICATE_DIR / "curved_deformation_retract_status.json"
KERNEL = CERTIFICATE_DIR / "curved_curvature_mapping_cylinder_kernel.json"
COTANGENT = CERTIFICATE_DIR / "curved_prolonged_bv_differential_audit.json"
OUTPUT = CERTIFICATE_DIR / "curved_curvature_mapping_cylinder_substitution.json"


def _load(path: Path) -> dict[str, object]:
    if not path.exists():
        raise AssertionError(f"required certificate is absent: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path.relative_to(ROOT)}")
    return value


def _rejects(
    state_gauge: dict[str, object],
    linearized_bach: dict[str, object],
    equation: dict[str, object],
    core_chain: dict[str, object],
    curved_retract: dict[str, object],
    kernel: dict[str, object],
    cotangent: dict[str, object],
) -> bool:
    try:
        CurvatureMappingCylinderSubstitution(
            state_gauge,
            linearized_bach,
            equation,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    state_gauge = _load(STATE_GAUGE)
    linearized_bach = _load(LINEARIZED_BACH)
    equation = _load(EQUATION)
    core_chain = _load(CORE_CHAIN)
    curved_retract = _load(CURVED_RETRACT)
    kernel = _load(KERNEL)
    cotangent = _load(COTANGENT)

    # Rebuild both exact algebraic inputs in this process.  This prevents a
    # hand-edited JSON flag from standing in for the corrected p_E/p_I square
    # or for any of the sixteen mapping-cylinder matrix identities.
    rebuilt_core_chain = CurvedCoreCurvatureChainMap.build().certificate(
        equation_certificate=equation,
        curved_retract_certificate=curved_retract,
    )
    if rebuilt_core_chain != core_chain:
        raise AssertionError("curved core-chain certificate is not reproducible")
    rebuilt_kernel = CurvatureMappingCylinderKernel.build().certificate()
    if rebuilt_kernel != kernel:
        raise AssertionError("sixteen-block mapping-cylinder kernel drifted")

    audit = CurvatureMappingCylinderSubstitution(
        state_gauge,
        linearized_bach,
        equation,
        core_chain,
        curved_retract,
        kernel,
        cotangent,
    )
    certificate = audit.certificate()

    broken_a_order = deepcopy(equation)
    broken_a_order["A_equation"]["maximum_order"] = 3
    broken_a_hash = deepcopy(equation)
    broken_a_hash["A_equation"]["sha256"] = "not-a-digest"
    broken_first_square = deepcopy(equation)
    broken_first_square["first_chain_relation_exact"] = False
    broken_b_hash = deepcopy(core_chain)
    broken_b_hash["identity_attachment"]["sha256"] = "not-a-digest"
    broken_second_square = deepcopy(core_chain)
    broken_second_square["lifted_chain_squares"]["exact"] = False
    broken_projection = deepcopy(core_chain)
    broken_projection["coordinate_correction"][
        "ordinary_symbol_substitution_used"
    ] = True
    broken_degree = deepcopy(kernel)
    broken_degree["degree_checks"][
        "every_split_Q_arrow_raises_degree_by_one"
    ] = False
    broken_pairing = deepcopy(kernel)
    broken_pairing["mapping_cylinder"]["BV_pairing_defect"] = 1
    broken_state_gauge = deepcopy(state_gauge)
    broken_state_gauge["T_state_K_aux_exact"] = False
    broken_bach_input = deepcopy(linearized_bach)
    broken_bach_input["gauge_jet_test"]["exhaustive"] = False
    broken_retract = deepcopy(curved_retract)
    broken_retract["promotion_criteria"]["curved_p_is_chain_map"] = False
    broken_cotangent = deepcopy(cotangent)
    broken_cotangent["exact_results"]["cotangent_adjoint_Q_squared"] = False

    mutations = {
        "wrong_A_order_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_a_order,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ),
        "bad_A_hash_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_a_hash,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ),
        "broken_first_square_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_first_square,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ),
        "bad_corrected_B_hash_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_b_hash,
            curved_retract,
            kernel,
            cotangent,
        ),
        "broken_second_square_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_second_square,
            curved_retract,
            kernel,
            cotangent,
        ),
        "broken_degree_ledger_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            core_chain,
            curved_retract,
            broken_degree,
            cotangent,
        ),
        "broken_BV_pairing_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            core_chain,
            curved_retract,
            broken_pairing,
            cotangent,
        ),
        "broken_state_gauge_square_rejected": _rejects(
            broken_state_gauge,
            linearized_bach,
            equation,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ),
        "incomplete_Bach_gauge_jets_rejected": _rejects(
            state_gauge,
            broken_bach_input,
            equation,
            core_chain,
            curved_retract,
            kernel,
            cotangent,
        ),
        "stale_flat_Fourier_projection_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_projection,
            curved_retract,
            kernel,
            cotangent,
        ),
        "broken_actual_curved_retract_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            core_chain,
            broken_retract,
            kernel,
            cotangent,
        ),
        "broken_cotangent_audit_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            core_chain,
            curved_retract,
            kernel,
            broken_cotangent,
        ),
    }

    OUTPUT.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = {
        "coefficientwise_complete": certificate[
            "coefficientwise_complete_prolonged_Q"
        ],
        "support_local": certificate["support_local"],
        "all_new_blocks_accounted_for": certificate["substitution"][
            "all_new_blocks_accounted_for"
        ],
        "formal_adjoints_forced": certificate["substitution"][
            "formal_adjoint_tables_generated_from_primal_tables"
        ],
        "first_chain_square": certificate["substitution"][
            "first_chain_relation_exact"
        ],
        "second_chain_square": certificate["substitution"][
            "second_chain_relation_exact"
        ],
        "Q_squared": certificate["kernel"]["Q_squared"] == "zero",
        "BV_pairing": certificate["kernel"]["BV_pairing_defect"] == 0,
        "odd_BV_cyclicity": certificate["kernel"][
            "odd_BV_cyclicity_defect"
        ] == 0,
        "SDR_identity": certificate["kernel"]["I_P_minus_identity"] == "QH+HQ",
        "all_16_rows_enumerated": certificate["kernel"]["row_coverage"]
        == {
            "rows_enumerated": 16,
            "rows_expected": 16,
            "silent_rows_dropped": 0,
            "fields_equations_identities_and_cotangents": True,
        },
        "all_16_Q_squared_checked": certificate["kernel"][
            "all_16_blocks_Q_squared_checked"
        ],
        "all_16_graph_SDR_checked": certificate["kernel"][
            "all_16_blocks_graph_SDR_checked"
        ],
        "curved_pE_pI_used": not certificate["substitution"][
            "flat_Fourier_projection_used"
        ],
        "stale_rank_four_not_operator_obstruction": not certificate[
            "superseded_diagnostic"
        ]["rank_four_defect_is_operator_obstruction"],
        "curved_core_rebuilt_exact": rebuilt_core_chain == core_chain,
        "sixteen_block_kernel_rebuilt_exact": rebuilt_kernel == kernel,
        "three_adjoint_tables_content_addressed": all(
            len(entry["derived_sha256"]) == 64
            and len(entry["source_pairing_sha256"]) == 64
            and len(entry["target_pairing_sha256"]) == 64
            for entry in certificate["formal_adjoint_provenance"].values()
            if isinstance(entry, dict)
        ),
        "two_atomic_flags_warranted": certificate["warranted_atomic_flags"]
        == [
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
        ],
        "no_status_file_mutation": not certificate["status_flags_promoted"],
        **mutations,
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {OUTPUT.relative_to(ROOT)}")
    print(
        "CURVATURE MAPPING-CYLINDER SUBSTITUTION GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
