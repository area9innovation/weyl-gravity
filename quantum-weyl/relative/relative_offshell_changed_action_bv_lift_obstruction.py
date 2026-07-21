"""Exact quantum-side import of the four-derivative changed-action no-lift.

The selected repair orbit is the quadratic-action deformation only.  The
upstream bridge certificate supplies a complete real parity-even local
Einstein--Maxwell action quotient through four derivatives and its exact
reduced Hessian response.  This module checks the two cokernel witnesses and
the p-shell cross-response rank, then emits the fail-closed disposition of the
off-shell BV/QME gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/RELATIVE_OFFSHELL_CHANGED_ACTION_BV_LIFT_OBSTRUCTION_V1.json"
)
ATLAS = ROOT / "residual_atlas/relative-offshell-changed-action-bv-lift-obstruction-fragment-v1.json"

PAIRING_CLASSIFICATION = (
    ROOT
    / "quantum-weyl/transfer/certificates/RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION.json"
)
PAIRING_RECEIPT = (
    ROOT
    / "quantum-weyl/transfer/receipts/RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION_V1_TIER_RECEIPT.json"
)
QME_NONDEFINITION = (
    ROOT
    / "quantum-weyl/transfer/certificates/RELATIVE_CHANGED_THEORY_QME_NONDEFINITION.json"
)
QME_RECEIPT = (
    ROOT
    / "quantum-weyl/transfer/receipts/RELATIVE_CHANGED_THEORY_QME_NONDEFINITION_V1_TIER_RECEIPT.json"
)
ACTION_RESPONSE = (
    ROOT
    / "bridge/certificates/EINSTEIN_MAXWELL_FOUR_DERIVATIVE_ACTION_RESPONSE_V1.json"
)
ACTION_RESPONSE_RECEIPT = (
    ROOT
    / "bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_FOUR_DERIVATIVE_ACTION_RESPONSE_V1_TIER_RECEIPT.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _ref(path: Path) -> dict[str, str]:
    value = _load(path)
    artifact_id = (
        value.get("result_id")
        or value.get("receipt_id")
        or value.get("schema")
    )
    if not isinstance(artifact_id, str) or not artifact_id:
        raise ValueError(f"missing artifact identity: {path}")
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
    }


def _expr(value: object, lam: sp.Symbol) -> sp.Expr:
    return sp.factor(
        sp.sympify(str(value).replace("lambda", "lam"), locals={"lam": lam})
    )


def _matrix(values: object, lam: sp.Symbol) -> sp.Matrix:
    if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
        raise ValueError("matrix record is malformed")
    return sp.Matrix([[_expr(value, lam) for value in row] for row in values])


def exact_replay(action: dict[str, Any]) -> dict[str, Any]:
    """Recompute the finite exact obstruction from the imported response."""

    lam = sp.symbols("lambda", real=True)
    basis = action["basis_reduction"]
    response = action["q_primary_response"]
    cokernel = action["exact_cokernel"]
    p_shell = action["p_shell_cross_response"]

    relation_matrix = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in basis["relation_matrix"]]
    )
    if relation_matrix.rank() != 7:
        raise ValueError("four-derivative relation rank drifted")
    if len(basis["raw_four_derivative_order"]) - relation_matrix.rank() != 3:
        raise ValueError("four-derivative quotient dimension drifted")

    axial = _matrix(response["general_axial"], lam)
    polar = _matrix(response["general_polar"], lam)
    target_axial = _matrix(cokernel["requested_source_action_shift"]["axial"], lam)
    target_polar = _matrix(cokernel["requested_source_action_shift"]["polar"], lam)

    axial_on_image = sp.Poly(sp.expand(axial[1, 1]), lam).coeff_monomial(lam)
    axial_on_target = sp.Poly(sp.expand(target_axial[1, 1]), lam).coeff_monomial(lam)
    polar_on_image = sp.Poly(sp.expand(polar[1, 1]), lam).coeff_monomial(lam**2)
    polar_on_target = sp.Poly(sp.expand(target_polar[1, 1]), lam).coeff_monomial(lam**2)
    if (axial_on_image, axial_on_target, polar_on_image, polar_on_target) != (
        0,
        -9,
        0,
        sp.Rational(-9, 4),
    ):
        raise ValueError("exact cokernel witness drifted")

    cross = sp.Matrix(
        [[sp.Rational(value) for value in row] for row in p_shell["zero_cross_constraint_matrix"]]
    )
    cross_rank = cross.rank()
    cross_nullity = cross.cols - cross_rank
    if (cross.rows, cross.cols, cross_rank, cross_nullity) != (17, 6, 6, 0):
        raise ValueError("p-shell cross-response obstruction drifted")

    return {
        "coefficient_field": "Q",
        "relation_matrix_shape": [relation_matrix.rows, relation_matrix.cols],
        "relation_rank": relation_matrix.rank(),
        "four_derivative_quotient_dimension": 3,
        "complete_action_basis_dimension": len(basis["complete_action_basis"]),
        "axial_witness": {
            "functional": "coefficient_of_lambda_in_axial_22",
            "on_action_response_image": str(axial_on_image),
            "on_requested_shift": str(axial_on_target),
        },
        "polar_witness": {
            "functional": "coefficient_of_lambda_squared_in_polar_22",
            "on_action_response_image": str(polar_on_image),
            "on_requested_shift": str(polar_on_target),
        },
        "p_shell_cross_response_shape": [cross.rows, cross.cols],
        "p_shell_cross_response_rank": cross_rank,
        "p_shell_cross_response_kernel_dimension": cross_nullity,
    }


def _validate_inputs(
    pairing: dict[str, Any], qme: dict[str, Any], action: dict[str, Any]
) -> None:
    if (
        pairing.get("result_id")
        != "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION"
        or pairing.get("lifecycle_status") != "CLASSIFIED"
    ):
        raise ValueError("terminal repair classification drifted")
    action_disposition = pairing.get("quadratic_action_disposition", {})
    sector_labels = {
        row.get("dual_minimal_source_action_repair", {}).get("theory_label")
        for row in pairing.get("sector_classification", [])
    }
    if (
        action_disposition.get("support_local_selected_representatives", {}).get("status")
        != "FINITE_ORDER_PRODUCT_EQUIVARIANT_REDUCED_ACTION"
        or sector_labels != {"ACTION_CHANGED_EINSTEIN_Q_PRIMARY_REDUCED_THEORY"}
    ):
        raise ValueError("quadratic-action orbit label drifted")
    if (
        qme.get("result_id") != "RELATIVE_CHANGED_THEORY_QME_NONDEFINITION"
        or qme.get("claim_flags", {}).get("RELATIVE_ONE_LOOP_QME_DEFINED_ON_ANY_REPAIR_ORBIT")
        is not False
    ):
        raise ValueError("relative changed-theory QME boundary drifted")
    if (
        action.get("result_id")
        != "EINSTEIN_MAXWELL_FOUR_DERIVATIVE_ACTION_RESPONSE_V1"
        or action.get("result_state")
        != "COMPLETE_FOUR_DERIVATIVE_ACTION_RESPONSE_EXACT_NO_LIFT"
        or action.get("exact_cokernel", {}).get("verdict")
        != "EXACT_LOCAL_ACTION_NO_LIFT_THROUGH_FOUR_DERIVATIVES"
    ):
        raise ValueError("four-derivative action response boundary drifted")


def build_certificate() -> dict[str, Any]:
    pairing = _load(PAIRING_CLASSIFICATION)
    qme = _load(QME_NONDEFINITION)
    action = _load(ACTION_RESPONSE)
    _validate_inputs(pairing, qme, action)
    replay = exact_replay(action)

    basis = action["basis_reduction"]
    exact_cokernel = action["exact_cokernel"]
    q_response = action["q_primary_response"]
    p_shell = action["p_shell_cross_response"]
    receipt = _load(ACTION_RESPONSE_RECEIPT)
    if receipt.get("subject_result_id") != action["result_id"]:
        raise ValueError("action-response receipt subject drifted")
    if receipt.get("independent_rail", {}).get("status") != "PASS":
        raise ValueError("upstream independent action-variation rail is not PASS")

    return {
        "schema": "relative-offshell-changed-action-bv-lift-obstruction-v1",
        "result_id": "RELATIVE_OFFSHELL_CHANGED_ACTION_BV_LIFT_OBSTRUCTION_V1",
        "result_state": "OBSTRUCTED_COMPLETE_PARITY_EVEN_FOUR_DERIVATIVE_LOCAL_ACTION_ANSATZ",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": action["scope"],
        "selected_repair_orbit": {
            "orbit": "quadratic_action_deformation",
            "selection": "QUADRATIC_ACTION_DEFORMATION_ONLY",
            "theory_label": "ACTION_CHANGED_EINSTEIN_Q_PRIMARY_REDUCED_THEORY",
            "axial_and_polar_treated_together": True,
            "reason": "one real parity-even covariant action must reproduce both parity-sector Hessian responses",
            "pairing_deformation_mixed_in": False,
            "physical_auxiliary_extension_mixed_in": False,
        },
        "input_pins": {
            "terminal_pairing_deformation_classification": _ref(PAIRING_CLASSIFICATION),
            "terminal_pairing_deformation_receipt": _ref(PAIRING_RECEIPT),
            "terminal_changed_theory_qme_nondefinition": _ref(QME_NONDEFINITION),
            "terminal_changed_theory_qme_receipt": _ref(QME_RECEIPT),
            "complete_action_response": _ref(ACTION_RESPONSE),
            "complete_action_response_receipt": _ref(ACTION_RESPONSE_RECEIPT),
        },
        "complete_action_ansatz": {
            "field_content": "metric plus fixed-bundle U1 connection",
            "symmetry": "real parity-even Diff x U(1)",
            "derivative_bound": "at most four covariant derivatives; F counts one and curvature two",
            "raw_four_derivative_generators": basis["raw_four_derivative_order"],
            "exact_relation_order": basis["relation_order"],
            "relation_rank": basis["rank"],
            "four_derivative_quotient_representatives": basis["quotient_representatives"],
            "lower_derivative_completion": basis["lower_derivative_completion"],
            "complete_action_basis": basis["complete_action_basis"],
            "bounded_field_redefinitions": basis["bounded_field_redefinitions"],
            "external_completeness_anchor": basis["external_completeness_anchor"],
            "same_background_incidence": action["background_incidence"]["same_background_linear_constraints"],
        },
        "requested_reduced_action_shift": exact_cokernel["requested_source_action_shift"],
        "general_action_response": {
            "coefficient_order": q_response["coefficient_order"],
            "axial": q_response["general_axial"],
            "polar": q_response["general_polar"],
        },
        "exact_obstruction": {
            "first_invariant_obstruction": "AXIAL_22_LAMBDA_COEFFICIENT",
            "witnesses": exact_cokernel["witnesses"],
            "unrestricted_q_primary_preimage_exists": False,
            "same_background_preimage_exists": False,
            "p_shell_separation_preserving_preimage_exists": False,
            "logic": exact_cokernel["logic"],
        },
        "exact_replay": replay,
        "p_shell_control": {
            "constraint_matrix_shape": [
                len(p_shell["zero_cross_constraint_matrix"]),
                len(p_shell["zero_cross_constraint_matrix"][0]),
            ],
            "rank": p_shell["zero_cross_constraint_rank"],
            "kernel_dimension": p_shell["zero_cross_kernel_dimension"],
            "verdict": p_shell["zero_cross_verdict"],
        },
        "noether_and_bv_disposition": {
            "unchanged_gauge_group": action["noether_completion"]["gauge_group"],
            "conditional_action_density_noether_completion": "CERTIFIED_FOR_EACH_ACTION_ANSATZ_MEMBER",
            "conditional_finite_carrier_rows": 38,
            "requested_changed_local_action": "OBSTRUCTED",
            "requested_changed_master_action": "NOT_ACTIVATED",
            "requested_changed_BV_differential": "NOT_ACTIVATED",
            "requested_changed_odd_pairing": "NOT_ACTIVATED",
            "requested_changed_nonminimal_sector": "NOT_ACTIVATED",
            "requested_changed_gauge_fixed_operator": "NOT_ACTIVATED",
            "requested_full_40_to_38_cyclic_chain_lift": "NOT_ACTIVATED",
            "common_density_measure_domain_regulator": "NOT_ACTIVATED",
        },
        "relative_quantum_disposition": {
            "changed_theory_local_cohomology": "UNDEFINED",
            "relative_anomaly_coefficients": "NOT_COMPUTED",
            "relative_one_loop_QME": "UNDEFINED",
            "strict_pure_Weyl_coefficients_imported_as_relative": False,
            "paper12_lifecycle": "SCOPED_FOUR_DERIVATIVE_CHANGED_ACTION_ROUTE_OBSTRUCTED_RELATIVE_QME_REMAINS_UNDEFINED",
        },
        "independent_rails": {
            "upstream_action_variation": {
                "status": receipt["independent_rail"]["status"],
                "method": receipt["independent_rail"]["method"],
                "elapsed_seconds": receipt["independent_rail"]["elapsed_seconds"],
                "imports_producer_matrices": False,
            },
            "quantum_integration": "independent exact extraction of both cokernel functionals, relation rank, and 17x6 p-shell rank from pinned artifacts",
        },
        "open_routes": [
            "six_or_more_derivative_local_actions",
            "nonlocal_actions",
            "pairing_deformation_orbit",
            "new_physical_auxiliary_orbit",
        ],
        "claim_flags": {
            "COMPLETE_FOUR_DERIVATIVE_PARITY_EVEN_ACTION_ANSATZ_IMPORTED": True,
            "QUADRATIC_ACTION_ORBIT_SELECTED_EXCLUSIVELY": True,
            "REQUESTED_REDUCED_REPAIR_HAS_LOCAL_ACTION_PREIMAGE": False,
            "FULL_OFFSHELL_CHANGED_BV_LIFT_CONSTRUCTED": False,
            "RELATIVE_ANOMALY_COEFFICIENT_COMPUTED": False,
            "RELATIVE_QME_DEFINED": False,
            "LORENTZIAN_CAUSAL_CLAIM": False,
        },
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m relative.relative_offshell_changed_action_bv_lift_obstruction --check",
            "PYTHONPATH=quantum-weyl python3 -m relative.verify_relative_offshell_changed_action_bv_lift_obstruction",
            "PYTHONPATH=quantum-weyl python3 -m unittest relative.tests.test_relative_offshell_changed_action_bv_lift_obstruction",
            "python3 residual_atlas/validate_fragment.py residual_atlas/relative-offshell-changed-action-bv-lift-obstruction-fragment-v1.json",
        ],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem obstructs only the selected quadratic-action repair orbit within the complete real parity-even "
            "Diff x U(1) metric-plus-connection local action quotient through four derivatives on the declared compact magnetic product. It does not "
            "rule out higher-derivative, nonlocal, changed-pairing, or new-physical-auxiliary theories. Because no requested action preimage exists, "
            "the changed master action, BV differential, cyclic lift, common regulator and relative anomaly/QME are not activated. No anomaly, "
            "Lorentzian causal, Hadamard, positivity, particle, scattering or unitarity conclusion follows."
        ),
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    boundary = certificate["claim_boundary"]
    scope = {
        key: certificate["scope"][key]
        for key in (
            "theory",
            "background",
            "boundaries",
            "charge_sector",
            "carrier",
            "degree",
            "parity",
            "ell",
            "m",
            "k",
            "omega",
        )
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "status_vocabulary": [
            "CERTIFIED",
            "OBSTRUCTED",
            "OPEN",
            "NOT_APPLICABLE",
            "NO_CERTIFIED_MAP",
        ],
        "description_axes": [
            "causal",
            "symplectic",
            "nonlinear",
            "observational",
            "quantum",
        ],
        "generated_by": str(Path(__file__).resolve().relative_to(ROOT)),
        "generated_by_sha256": sha256(Path(__file__).resolve()),
        "verification_commands": certificate["verification_commands"],
        "entries": [
            {
                "id": "quantum.relative.einstein_weyl.changed_action.four_derivative_bv_lift_gate",
                "scope": scope,
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OBSTRUCTED",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NOT_APPLICABLE",
                    "quantum": "OPEN",
                },
                "mode_data": {
                    "dispersion": {"status": "NOT_APPLICABLE", "statement": "This is an action-lift gate, not a mode dispersion relation."},
                    "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "No requested changed action exists in the declared ansatz, so no changed Lee--Wald current is defined."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "No resonance or tangent-cone claim is made."},
                    "taub_maps": {"status": "NOT_APPLICABLE", "statement": "No Taub map is computed by this action-lift obstruction."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "NOT_APPLICABLE", "statement": "No second-order solution class is selected."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "No second-order solution class is selected."},
                        "causal_retarded": {"status": "NOT_APPLICABLE", "statement": "No second-order solution class is selected."},
                    },
                },
                "quantum_data": {
                    "entry_kind": "NON_MODE_PARTICLE_GUARD",
                    "dependency_tags": certificate["dependency_tags"],
                    "classical_mode_imported": {"status": "NOT_APPLICABLE", "statement": "The imported object is a bounded covariant action-response classification, not a residual mode."},
                    "BRST_cocycle": {"status": "NO_CERTIFIED_MAP", "statement": "The requested changed BRST differential is not activated because its action has no preimage."},
                    "BRST_exactness": {"status": "NO_CERTIFIED_MAP", "statement": "No changed-theory cocycle exists to test for exactness."},
                    "pairing_status": {"status": "OBSTRUCTED", "statement": "The selected action orbit has no local action preimage; pairing-only repair is a distinct, unselected orbit."},
                    "compatible_complex_structure": {"status": "NOT_APPLICABLE", "statement": "No one-particle carrier is constructed."},
                    "Hadamard_two_point_function": {"status": "NO_CERTIFIED_MAP", "statement": "No causal Green carrier or changed off-shell BV theory is supplied."},
                    "state_space_status": {"status": "NOT_APPLICABLE", "statement": "No state space follows from a reduced action-response obstruction."},
                    "anomaly_QME_dependency": {"status": "OPEN", "statement": "Relative anomaly coefficients and QME remain undefined because the changed action and common regulator do not activate."},
                    "lifecycle_state": {"status": "OBSTRUCTED", "statement": "The four-derivative parity-even local changed-action route is exactly obstructed."},
                    "carrier_crosswalk": {"status": "NO_CERTIFIED_MAP", "statement": "The reduced rank-one shift has no 4D local action/BV carrier crosswalk in the declared ansatz."},
                    "particle_interpretation": {"status": "NOT_APPLICABLE", "statement": "An action-response cokernel witness is not a particle state."},
                },
                "evidence": [
                    {
                        "result_id": certificate["result_id"],
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "sha256": sha256(OUTPUT),
                    }
                ],
                "claim_boundary": boundary,
            }
        ],
    }


def validate(certificate: dict[str, Any]) -> None:
    expected = build_certificate()
    if certificate != expected:
        raise ValueError("certificate differs from exact regenerated result")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        atlas = build_atlas(certificate)
        ATLAS.parent.mkdir(parents=True, exist_ok=True)
        ATLAS.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {ATLAS.relative_to(ROOT)}")
    else:
        validate(_load(OUTPUT))
        if _load(ATLAS) != build_atlas(certificate):
            raise ValueError("atlas differs from exact regenerated result")
        print("RELATIVE OFFSHELL CHANGED-ACTION BV-LIFT obstruction replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
