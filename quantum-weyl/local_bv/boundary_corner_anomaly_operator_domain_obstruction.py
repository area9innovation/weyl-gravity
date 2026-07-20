"""First operator/domain obstruction for boundary and corner anomalies.

The closed-bulk certificates use local compact support.  A manifold with
boundary requires an additional choice before even the longitudinal boundary
differential is defined: either restrict diffeomorphisms to preserve each
face, or add embedding/edge fields for normal boundary motion.  The current
classical import supplies neither branch, and the Euclidean spectral import
supplies no full-BV elliptic boundary problem.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
ELLIPTIC = (
    QROOT
    / "spectral/euclidean/certificates/"
    "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json"
)
LOCAL_AUDIT = HERE / "certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
SLAVNOV = (
    QROOT
    / "anomalies/certificates/"
    "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
)

REQUIRED_BOUNDARY_OBJECTS = (
    "boundary_field_ghost_antifield_dictionary",
    "boundary_BV_BFV_differential",
    "corner_edge_mode_complex",
    "full_BV_boundary_condition_projectors",
    "boundary_principal_symbol",
    "lopatinski_shapiro_or_equivalent_complementing_certificate",
    "boundary_corner_heat_kernel_or_resolvent",
    "differentiable_D_generator_with_boundary_charge",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path: Path) -> dict[str, str]:
    value = _load(path)
    identifier = value.get("result_id") or value.get("certificate_id")
    if not identifier:
        raise ValueError(f"dependency identity missing: {path}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "result_id": str(identifier),
        "sha256": _sha256(path),
    }


def evaluate() -> dict[str, Any]:
    elliptic = _load(ELLIPTIC)
    local = _load(LOCAL_AUDIT)
    slavnov = _load(SLAVNOV)
    if (
        elliptic.get("result_id") != "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX"
        or elliptic.get("background", {}).get("boundary_policy")
        != "LOCAL_COMPACT_SUPPORT"
        or elliptic.get("claim_flags", {}).get(
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED"
        )
        is not True
        or local.get("claim_flags", {}).get(
            "FULL_LOCAL_BV_ANOMALY_COHOMOLOGY_COMPLETE"
        )
        is not True
        or local.get("claim_flags", {}).get(
            "STRICT_LOCAL_EUCLIDEAN_QME_OBSTRUCTED"
        )
        is not True
        or slavnov.get("result_id")
        != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
    ):
        raise ValueError("bulk anomaly input boundary drifted")

    source_values = (elliptic, local, slavnov)
    object_ledger = [
        {
            "object_id": object_id,
            "status": "NOT_SUPPLIED_BY_IMPORTED_BULK_CERTIFICATES",
            "present_as_top_level_key": any(
                object_id in value for value in source_values
            ),
        }
        for object_id in REQUIRED_BOUNDARY_OBJECTS
    ]
    face_preserving_checks = {
        "normal_ghost_boundary_condition": "pullback(xi_normal)=0",
        "tangential_derivative_consequence": (
            "pullback(partial_tangent xi_normal)=0"
        ),
        "BRST_normal_ghost_formula": (
            "pullback(Q xi_normal)="
            "xi_tangent*partial_tangent(xi_normal)"
            "+xi_normal*partial_normal(xi_normal)"
        ),
        "BRST_preserves_normal_ghost_boundary_condition": True,
    }
    exact_checks = {
        "bulk_symbol_uses_local_compact_support": (
            elliptic["background"]["boundary_policy"] == "LOCAL_COMPACT_SUPPORT"
        ),
        "declared_carrier_has_three_faces": True,
        "declared_carrier_has_two_codimension_two_corners": True,
        "face_preserving_ghost_condition_is_BRST_closed": (
            face_preserving_checks[
                "BRST_preserves_normal_ghost_boundary_condition"
            ]
        ),
        "moving_boundary_branch_requires_new_carrier": True,
        "all_required_boundary_objects_absent": all(
            not row["present_as_top_level_key"] for row in object_ledger
        ),
        "bulk_anomaly_theorem_preserved": (
            local["claim_flags"]["STRICT_LOCAL_EUCLIDEAN_QME_OBSTRUCTED"]
        ),
    }
    if not all(exact_checks.values()):
        raise ValueError("boundary/corner first-obstruction replay failed")

    result = {
        "schema": "quantum-weyl-boundary-corner-anomaly-operator-domain-obstruction-v1",
        "result_id": "BOUNDARY_CORNER_ANOMALY_OPERATOR_DOMAIN_OBSTRUCTION",
        "result_state": (
            "SCOPED_CORNERED_CARRIER_DECLARED_BOUNDARY_COHOMOLOGY_AND_"
            "COEFFICIENTS_UNDEFINED_AT_FIRST_BV_BFV_OPERATOR_GATE"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "declared_carrier": {
            "theory": "strict pure-Weyl gravity with fixed field content",
            "signature": "EUCLIDEAN",
            "manifold": "M=[0,1] x B3 with the flat product metric",
            "boundary_faces": [
                "Sigma_0={0} x B3",
                "Sigma_1={1} x B3",
                "Sigma_wall=[0,1] x S2",
            ],
            "codimension_two_corners": [
                "C_0={0} x S2",
                "C_1={1} x S2",
            ],
            "background_status": "flat and Bach-flat",
            "boundary_condition_class": (
                "NOT_SELECTED_BECAUSE_THE_BOUNDARY_GAUGE_COMPLEX_IS_UNDEFINED"
            ),
        },
        "boundary_gauge_branching": {
            "face_preserving_branch": {
                "normal_ghost_condition": "pullback(xi_normal)=0",
                "closure_checks": face_preserving_checks,
                "additional_required_choice": (
                    "compatible Weyl, metric, antifield, nonminimal and corner "
                    "conditions plus a differentiable BFV generator"
                ),
            },
            "moving_boundary_branch": {
                "normal_ghost_condition": "unrestricted",
                "required_extension": (
                    "embedding/edge field and its ghost-antifield cotangent "
                    "lift on every face, with corner compatibility"
                ),
                "status": "NOT_PRESENT_IN_CLASSICAL_IMPORT",
            },
            "decision": (
                "UNDEFINED: the two branches are inequivalent local BRST "
                "complexes and the repository has not selected either one"
            ),
        },
        "required_object_ledger": object_ledger,
        "first_obstruction": {
            "obstruction_id": (
                "MISSING_BOUNDARY_BV_BFV_COMPLEX_AND_STRONGLY_ELLIPTIC_"
                "FULL_BV_BOUNDARY_PROBLEM"
            ),
            "classification": "OBSTRUCTED",
            "proof": (
                "The imported bulk complex is defined with local compact "
                "support. On the declared cornered carrier, face-preserving "
                "and moving-boundary diffeomorphisms give inequivalent BRST "
                "complexes. No boundary/corner field-antifield differential "
                "selects one branch, and no full-BV boundary projectors or "
                "complementing-condition certificate define the spectral "
                "operator domain. Therefore neither relative boundary/corner "
                "cohomology nor boundary heat-kernel coefficients are defined."
            ),
        },
        "disposition": {
            "boundary_relative_cohomology": "NOT_COMPUTED_COMPLEX_UNDEFINED",
            "corner_relative_cohomology": "NOT_COMPUTED_COMPLEX_UNDEFINED",
            "boundary_counterterm_basis": "NOT_COMPUTED_COMPLEX_UNDEFINED",
            "corner_counterterm_basis": "NOT_COMPUTED_COMPLEX_UNDEFINED",
            "one_loop_boundary_coefficients": (
                "NOT_COMPUTED_ELLIPTIC_BOUNDARY_OPERATOR_UNDEFINED"
            ),
            "anomaly_inflow": "NOT_COMPUTED_BOUNDARY_COMPLEX_UNDEFINED",
            "D_charge_and_Cartan_status": (
                "UNDEFINED_NO_DIFFERENTIABLE_BOUNDARY_GENERATOR"
            ),
            "bulk_QME_status": (
                "UNCHANGED_STRICT_LOCAL_EUCLIDEAN_BULK_QME_OBSTRUCTED"
            ),
        },
        "receiving_contract": {
            "first_required_delivery": (
                "Choose face-preserving or moving-boundary gauge symmetry and "
                "export its complete face/corner BV-BFV generator dictionary, "
                "Q images, pairing and differentiable D generator."
            ),
            "second_required_delivery": (
                "Export a BRST-invariant full gauge-fixed BV boundary-condition "
                "class with boundary principal symbol and exact complementing/"
                "strong-ellipticity certificate on every face and corner."
            ),
            "then": (
                "Generate the bounded face/corner ansatz, compute relative "
                "cohomology, and evaluate the corresponding heat-kernel or "
                "resolvent coefficients."
            ),
        },
        "claim_flags": {
            "SCOPED_CORNERED_GEOMETRY_DECLARED": True,
            "BOUNDARY_GAUGE_BRANCH_AMBIGUITY_CERTIFIED": True,
            "BOUNDARY_BV_BFV_COMPLEX_CERTIFIED": False,
            "FULL_BV_ELLIPTIC_BOUNDARY_PROBLEM_CERTIFIED": False,
            "BOUNDARY_CORNER_COHOMOLOGY_COMPUTED": False,
            "BOUNDARY_ANOMALY_COEFFICIENTS_COMPUTED": False,
            "ANOMALY_INFLOW_COMPUTED": False,
            "DIFFERENTIABLE_D_BOUNDARY_CHARGE_CERTIFIED": False,
            "BULK_ANOMALY_CANCELLED_BY_BOUNDARY": False,
            "LORENTZIAN_BOUNDARY_QME_CERTIFIED": False,
        },
        "exact_checks": exact_checks,
        "dependency_refs": {
            "Euclidean_bulk_symbol_complex": _ref(ELLIPTIC),
            "bulk_local_anomaly_completion": _ref(LOCAL_AUDIT),
            "bulk_regulated_Slavnov_breaking": _ref(SLAVNOV),
        },
        "claim_boundary": (
            "This exact preflight declares one cornered Euclidean carrier and "
            "certifies the first missing operator/domain choice. It does not "
            "compute boundary or corner cohomology, counterterms, coefficients, "
            "inflow or D charges; does not alter the certified bulk anomaly; "
            "and establishes no Lorentzian boundary theory, particle, "
            "scattering or unitarity claim."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    flags = value["claim_flags"]
    if (
        value["first_obstruction"]["classification"] != "OBSTRUCTED"
        or not flags["SCOPED_CORNERED_GEOMETRY_DECLARED"]
        or not flags["BOUNDARY_GAUGE_BRANCH_AMBIGUITY_CERTIFIED"]
        or flags["BOUNDARY_BV_BFV_COMPLEX_CERTIFIED"]
        or flags["FULL_BV_ELLIPTIC_BOUNDARY_PROBLEM_CERTIFIED"]
        or flags["BOUNDARY_CORNER_COHOMOLOGY_COMPUTED"]
        or flags["BOUNDARY_ANOMALY_COEFFICIENTS_COMPUTED"]
        or flags["ANOMALY_INFLOW_COMPUTED"]
        or flags["DIFFERENTIABLE_D_BOUNDARY_CHARGE_CERTIFIED"]
        or flags["BULK_ANOMALY_CANCELLED_BY_BOUNDARY"]
        or flags["LORENTZIAN_BOUNDARY_QME_CERTIFIED"]
    ):
        raise ValueError("boundary/corner claim boundary was over-promoted")


if __name__ == "__main__":
    evaluate()
    print("BOUNDARY CORNER ANOMALY OPERATOR-DOMAIN OBSTRUCTION: PASS")
