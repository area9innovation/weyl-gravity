"""Disposition physical positivity after the retained Ward shortfall."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WARD = HERE / "certificates/BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json"
GRAPH = (
    HERE
    / "certificates/"
    "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
)
DILATION = (
    HERE
    / "certificates/BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE.json"
)
RESTRICTION = (
    HERE
    / "certificates/BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT.json"
)
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
CURVATURE = HERE / "certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json"
REDUCED = ROOT / "analytic_completion/certificates/one_particle_krein.json"

DEPENDENCIES = {
    "retained26_Ward_reduction": WARD,
    "regular_graph_obstruction": GRAPH,
    "rank40_auxiliary_covariance": DILATION,
    "canonical_restriction_audit": RESTRICTION,
    "graded_state_space_contract": GRADED,
    "curvature_CCR_algebra": CURVATURE,
    "reduced_EAL_Krein_ledger": REDUCED,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(payload: dict[str, Any]) -> str:
    return str(
        payload.get("result_id")
        or payload.get("schema")
        or "one_particle_krein"
    )


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": _artifact_id(payload), "sha256": _sha256(path)}


def representative_change_replay(
    *,
    ward_defect_certified_pairing_null: bool = False,
    closed_first_argument: bool = True,
    closed_second_argument: bool = True,
) -> dict[str, Any]:
    """Replay the exact even, ghost-number-zero descent condition."""

    first_variation_reduces_to_defect = closed_second_argument
    second_variation_reduces_to_defect = closed_first_argument
    descends = (
        ward_defect_certified_pairing_null
        and closed_first_argument
        and closed_second_argument
    )
    checks = {
        "candidate_pairing_is_B_f_h_equals_bracket_f_Omega_h": True,
        "sector_is_even_ghost_number_zero": True,
        "first_representative_change_is_f_to_f_plus_q_u": True,
        "first_variation_is_bracket_u_DeltaWard_h_for_qh_zero": (
            first_variation_reduces_to_defect
        ),
        "second_representative_change_is_h_to_h_plus_q_v": True,
        "second_variation_is_bracket_f_DeltaWard_v_for_qf_zero": (
            second_variation_reduces_to_defect
        ),
        "descent_requires_Ward_defect_to_be_pairing_null_on_closed_arguments": True,
        "current_Ward_defect_is_not_certified_pairing_null": (
            not ward_defect_certified_pairing_null
        ),
        "physical_form_is_not_defined_from_current_candidate": not descends,
    }
    return {
        "pairing": "B_Omega(f,h)=<f,Omega26_plus h>",
        "sector": "even ghost-number-zero homogeneous representatives",
        "adjoint_convention": (
            "<q26 u,v>=<u,q26sharp v> in the declared even sector"
        ),
        "first_representative_change": "[f]->[f+q26 u]",
        "first_exact_variation": (
            "B_Omega(f+q26 u,h)-B_Omega(f,h)="
            "<u,(q26sharp Omega26_plus+Omega26_plus q26)h>"
            "=<u,W26[H26_plus,q26]h> for q26 h=0"
        ),
        "second_representative_change": "[h]->[h+q26 v]",
        "second_exact_variation": (
            "B_Omega(f,h+q26 v)-B_Omega(f,h)="
            "<f,(q26sharp Omega26_plus+Omega26_plus q26)v>"
            "=<f,W26[H26_plus,q26]v> for q26 f=0"
        ),
        "descent_criterion": (
            "the Ward defect pairs to zero with every exact/closed "
            "representative pair; the certified sufficient condition is "
            "W26[H26_plus,q26]=0"
        ),
        "ward_defect_certified_pairing_null": (
            ward_defect_certified_pairing_null
        ),
        "pairing_descends": descends,
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def carrier_classification() -> list[dict[str, str]]:
    return [
        {
            "carrier": "retained_26_exact_CCR_candidate",
            "BRST_descent": "NOT_CERTIFIED_SMOOTH_WARD_DEFECT_OPEN",
            "physical_form": "UNDEFINED",
            "positivity_status": "NOT_APPLICABLE_BEFORE_DESCENT",
        },
        {
            "carrier": "rank_40_auxiliary_Hermitian_dilation",
            "BRST_descent": "NO_RETAINED_CHAIN_MAP_GRAPH_CLASS_OBSTRUCTED",
            "physical_form": "NO_CERTIFIED_MAP",
            "positivity_status": "AUXILIARY_KREIN_SIGNATURE_NOT_A_PHYSICAL_NORM",
        },
        {
            "carrier": "vacuum_cylinder_reduced_E_A_L_Krein_space",
            "BRST_descent": "DIFFERENT_BACKGROUND_AND_REDUCED_MODE_CARRIER",
            "physical_form": "NO_CERTIFIED_MAP",
            "positivity_status": "REDUCED_MODE_KREIN_ONLY",
        },
        {
            "carrier": "curvature_image_CCR_algebra",
            "BRST_descent": "ALGEBRAIC_COHOMOLOGY_PRESENTATION_CERTIFIED",
            "physical_form": "NO_HADAMARD_TWO_POINT_FUNCTION",
            "positivity_status": "OPEN",
        },
    ]


def _load() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in DEPENDENCIES.items()
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    ward = values["retained26_Ward_reduction"]
    graph = values["regular_graph_obstruction"]
    dilation = values["rank40_auxiliary_covariance"]
    restriction = values["canonical_restriction_audit"]
    graded = values["graded_state_space_contract"]
    curvature = values["curvature_CCR_algebra"]
    reduced = values["reduced_EAL_Krein_ledger"]

    input_checks = {
        "retained_candidate_exact_CCR_but_Ward_open": (
            ward["claim_flags"]["BERGER_26_ROW_HADAMARD_EXACT_CCR_CANDIDATE"]
            is True
            and ward["claim_flags"]["BERGER_26_ROW_WARD_DEFECT_SMOOTH"] is True
            and ward["claim_flags"]["BERGER_SMOOTH_Q26_WARD_COMPLETION"]
            is False
        ),
        "retained_BRST_Hadamard_not_certified": ward["claim_flags"][
            "BERGER_26_ROW_BRST_HADAMARD"
        ]
        is False,
        "regular_graph_route_obstructed": (
            graph["claim_flags"]["BERGER_REGULAR_GRAPH_INTERTWINER_CLASS_COMPLETE"]
            is True
            and graph["claim_flags"][
                "BERGER_NONDEGENERATE_REGULAR_GRAPH_INTERTWINER_EXISTS"
            ]
            is False
        ),
        "canonical_auxiliary_restriction_annihilates_CCR": restriction[
            "claim_flags"
        ]["BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR"]
        is False,
        "rank40_form_is_indefinite_auxiliary": dilation[
            "transported_covariances"
        ]["full"]["state_space_status"]
        == "INDEFINITE_KREIN_QUASIFREE_FUNCTIONAL_NOT_A_POSITIVE_STATE",
        "graded_policy_requires_descent_before_positivity": graded[
            "positivity_and_krein_policy"
        ]["full_BV_positive_state"]
        == "NOT_CLAIMED",
        "curvature_Hadamard_state_open": curvature["claim_flags"][
            "CURVATURE_HADAMARD_STATE_CONSTRUCTED"
        ]
        is False,
        "reduced_Krein_is_not_distributional": (
            "not a distributional completion" in reduced["scope_guards"]
        ),
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"physical positivity input drift: {failed}")

    descent = representative_change_replay()
    positive_mutant = representative_change_replay(
        ward_defect_certified_pairing_null=True
    )
    unclosed_first_mutant = representative_change_replay(
        closed_first_argument=False
    )
    unclosed_mutant = representative_change_replay(
        closed_second_argument=False
    )
    carriers = carrier_classification()
    if (
        not descent["all_pass"]
        or positive_mutant["all_pass"]
        or unclosed_first_mutant["all_pass"]
        or unclosed_mutant["all_pass"]
        or len(carriers) != 4
    ):
        raise ValueError("physical positivity disposition replay failed")

    result = {
        "schema": (
            "quantum-weyl-berger-physical-cohomology-positivity-"
            "disposition-v1"
        ),
        "result_id": "BERGER_PHYSICAL_COHOMOLOGY_POSITIVITY_DISPOSITION",
        "result_state": (
            "PHYSICAL_SESQUILINEAR_FORM_UNDEFINED_BEFORE_Q26_WARD_DESCENT_"
            "AUXILIARY_AND_REDUCED_SIGNS_NOT_PHYSICAL"
        ),
        "lifecycle_layer": "LORENTZIAN_PHYSICAL_COHOMOLOGY_STATE_DISPOSITION",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "science_forge": {
            "work_item": (
                "sf:program/work/"
                "quantum-berger-physical-cohomology-positivity"
            ),
            "stop_condition_status": "SHORTFALL_PRECONDITION_NOT_MET",
            "activation_gate": (
                "CERTIFY_Q26_WARD_DESCENT_BEFORE_PHYSICAL_PAIRING"
            ),
            "forbidden_promotions_respected": True,
        },
        "classical_commit": ward["classical_commit"],
        "setting_id": ward["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "BRST_representative_change": descent,
        "carrier_disposition": carriers,
        "physical_cohomology": {
            "complex": "ker(q26)/im(q26) on the declared physical solution/test quotient",
            "exact_basis": "NOT_COMPUTED_NO_STATIONARY_PHYSICAL_CROSSWALK",
            "candidate_pairing_descent": "NOT_CERTIFIED",
            "induced_sesquilinear_form": "UNDEFINED",
            "nondegeneracy": "NOT_APPLICABLE",
            "complex_structure_classification": "NOT_ACTIVATED",
            "positivity_verdict": "NOT_ACTIVATED_BEFORE_WARD_DESCENT",
        },
        "negative_controls": {
            "pretend_Ward_defect_is_pairing_null": positive_mutant,
            "drop_first_closed_representative_hypothesis": (
                unclosed_first_mutant
            ),
            "drop_closed_representative_hypothesis": unclosed_mutant,
        },
        "claim_flags": {
            "BERGER_PHYSICAL_PAIRING_DESCENDS_TO_BRST_COHOMOLOGY": False,
            "BERGER_PHYSICAL_COHOMOLOGY_BASIS_COMPUTED": False,
            "BERGER_SYMMETRY_COMPATIBLE_COMPLEX_STRUCTURES_CLASSIFIED": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_PHYSICAL_KREIN_SECTOR_UNAVOIDABLE": False,
            "BERGER_POSITIVE_HILBERT_STATE_EXISTS": False,
            "BERGER_AUXILIARY_SIGNATURE_NOT_PHYSICAL_NORM": True,
            "BERGER_REDUCED_EAL_SIGN_NOT_BERGER_PHYSICAL_NORM": True,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "RESTORE_Q26_WARD_DESCENT_THEN_COMPUTE_EXACT_PHYSICAL_"
            "COHOMOLOGY_PAIRING_AND_COMPLEX_STRUCTURES"
        ),
        "provenance": {
            "proof_type": (
                "EXACT_BRST_REPRESENTATIVE_CHANGE_AND_FAIL_CLOSED_"
                "ALTERNATIVE_CARRIER_CLASSIFICATION"
            )
        },
        "does_not_establish": [
            "a q26-invariant retained Hadamard two-point function",
            "a sesquilinear form on Berger BRST cohomology",
            "an exact Berger physical-cohomology basis",
            "nondegeneracy or positivity of a physical form",
            "an unavoidable physical Krein sector",
            "a positive Hilbert state or particle interpretation",
            "renormalized Lorentzian products",
            "a restored Lorentzian quantum master equation",
            "a Lorentzian quantum theory",
        ],
        "claim_boundary": (
            "The exact representative-change formula proves that the current "
            "exact-CCR candidate does not yet define a sesquilinear form on "
            "BRST cohomology because its smooth Ward defect is not certified "
            "zero or pairing-null. This is an undefined-before-descent result, "
            "not a negative-norm theorem. The rank-40 signature is auxiliary, "
            "the vacuum-cylinder E/A/L Krein ledger is a different reduced "
            "carrier, and the curvature CCR algebra has no Hadamard state. "
            "No physical cohomology basis, nondegenerate form, complex "
            "structure, positive Hilbert state, unavoidable physical Krein "
            "sector, particle, renormalized Lorentzian product, Lorentzian QME "
            "or quantum theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_PHYSICAL_COHOMOLOGY_POSITIVITY_DISPOSITION"
        or result.get("dependency_tags")
        != ["REDUCED-MODE", "LORENTZIAN-CAUSAL"]
        or not all(result.get("exact_input_checks", {}).values())
        or result.get("BRST_representative_change", {}).get("all_pass")
        is not True
        or result.get("physical_cohomology", {}).get(
            "induced_sesquilinear_form"
        )
        != "UNDEFINED"
        or result.get("science_forge", {}).get("stop_condition_status")
        != "SHORTFALL_PRECONDITION_NOT_MET"
    ):
        raise ValueError("physical positivity disposition failed")
    flags = result.get("claim_flags", {})
    required_true = {
        "BERGER_AUXILIARY_SIGNATURE_NOT_PHYSICAL_NORM",
        "BERGER_REDUCED_EAL_SIGN_NOT_BERGER_PHYSICAL_NORM",
    }
    if any(flags.get(name) is not True for name in required_true):
        raise ValueError("carrier boundary under-promoted")
    if any(
        value is not False
        for name, value in flags.items()
        if name not in required_true
    ):
        raise ValueError("physical positivity or quantum claim over-promoted")
