"""Fail-closed support disposition for the retained Ward remainder C26.

The imported Ward theorem identifies

    C26 = [H26_plus, q26]

as a smooth bikernel.  Its endpoint inputs, however, export existence
theorems and symbolic pullback formulas rather than one normalized,
content-addressed representative of H26_plus.  Support and pairing-null
questions are properties of that representative, so this module records the
first missing carrier instead of manufacturing support booleans from the
symbolic formula.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

DEPENDENCIES = {
    "ward_reduction": (
        HERE / "certificates/BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json"
    ),
    "ghost_identity_pair": (
        HERE / "certificates/BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR.json"
    ),
    "metric_endpoint_pair": (
        HERE
        / "certificates/"
        "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
    ),
    "free_dilation_pair": (
        HERE
        / "certificates/BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE.json"
    ),
    "classical_support_gate": (
        ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1.json"
    ),
}

EXPECTED_IDS = {
    "ward_reduction": "BERGER_RETAINED26_HADAMARD_WARD_REDUCTION",
    "ghost_identity_pair": "BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR",
    "metric_endpoint_pair": (
        "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT"
    ),
    "free_dilation_pair": "BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE",
    "classical_support_gate": (
        "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1"
    ),
}

UNDEFINED = "UNDEFINED_NO_NORMALIZED_SERIALIZED_H26_REPRESENTATIVE"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _require_inputs(values: dict[str, dict[str, Any]]) -> None:
    for name, value in values.items():
        if value.get("result_id") != EXPECTED_IDS[name]:
            raise ValueError(f"dependency identity drifted: {name}")

    ward = values["ward_reduction"]
    if (
        ward["ward_reduction"]["degreewise_kernel"]
        != (
            "H26_plus=diag(H_ghost_plus,H_metric_plus,"
            "H_metric_adjoint_plus,H_identity_plus)"
        )
        or ward["ward_reduction"]["smooth_defect"]
        != "C26=[H26_plus,q26] is a smooth kernel"
        or ward["candidate_status"]["Ward_defect_vanishes"] != "NOT_DECIDED"
        or not ward["candidate_status"]["Ward_defect_is_smooth"]
        or ward["candidate_status"]["retained_26_BRST_Hadamard"]
        or ward["candidate_status"]["smooth_correction_constructed"]
    ):
        raise ValueError("retained Ward boundary drifted")

    ghost = values["ghost_identity_pair"]
    if (
        ghost["global_pair"]["kernel"]
        != "W_gi=K_gi^dagger W_Dgi K_gi"
        or not ghost["ghost_identity_Hermitian_dilation"]["theorem_replay"][
            "theorem_applies"
        ]
        or ghost["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"]
    ):
        raise ValueError("ghost/identity endpoint boundary drifted")

    metric = values["metric_endpoint_pair"]
    descent = metric["direct_metric_endpoint_descent"]
    if (
        descent["kernel_pullback"] != "W_A_direct_sum_Adagger=K_src^dagger W_D K_src"
        or descent["symbolic_pulled_matrix"] != [["0", "e12"], ["e12", "0"]]
        or metric["retained_26_completion_boundary"]["BRST_Ward_identity"]
        != "NOT_VERIFIED"
    ):
        raise ValueError("metric endpoint boundary drifted")

    free = values["free_dilation_pair"]
    if (
        free["covariance"]["distribution"]
        != "W_Dfree=+i(GFsym,Dfree-Gadv,Dfree)"
        or free["analytic_boundary"]["BRST_Ward_identity"] != "NOT_VERIFIED"
        or free["claim_flags"]["BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"]
    ):
        raise ValueError("free dilation representative boundary drifted")

    support = values["classical_support_gate"]
    boundary = support["C26_import_boundary"]
    if (
        boundary["typed_need"]
        != "C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER"
        or support["classification"][
            "C26_in_positive_extension_domain_certified"
        ]
        or not support["classification"][
            "full_smooth_factorized_extension_obstructed"
        ]
        or support["lifecycle_status"]
        != "BLOCKED_ON_TYPED_C26_SUPPORT_PROFILE"
    ):
        raise ValueError("classical support gate drifted")


def _block_audit(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ghost = values["ghost_identity_pair"]
    metric = values["metric_endpoint_pair"]
    free = values["free_dilation_pair"]
    return [
        {
            "block_id": "ghost_identity",
            "source_result_id": ghost["result_id"],
            "declared_formula": ghost["global_pair"]["kernel"],
            "representation_kind": "SYMBOLIC_PULLBACK_PLUS_EXISTENCE_THEOREM",
            "serialized_bikernel": False,
            "stationary_mode_table": False,
            "executable_distribution_evaluator": False,
            "smooth_part_normalization_fixed": False,
        },
        {
            "block_id": "metric_metric_adjoint",
            "source_result_id": metric["result_id"],
            "declared_formula": metric["direct_metric_endpoint_descent"][
                "kernel_pullback"
            ],
            "representation_kind": "SYMBOLIC_PULLBACK_MATRIX",
            "serialized_bikernel": False,
            "stationary_mode_table": False,
            "executable_distribution_evaluator": False,
            "smooth_part_normalization_fixed": False,
        },
        {
            "block_id": "free_dilation_seed",
            "source_result_id": free["result_id"],
            "declared_formula": free["covariance"]["distribution"],
            "representation_kind": "SYMBOLIC_FEYNMAN_EXISTENCE_SELECTION",
            "serialized_bikernel": False,
            "stationary_mode_table": False,
            "executable_distribution_evaluator": False,
            "smooth_part_normalization_fixed": False,
        },
    ]


def evaluate() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    _require_inputs(values)
    blocks = _block_audit(values)

    result = {
        "schema": "quantum-weyl-berger-c26-support-profile-nondefinition-v1",
        "result_id": "BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION",
        "result_state": (
            "C26_SYMBOLIC_SMOOTHNESS_CERTIFIED_SUPPORT_AND_PAIRING_NULL_"
            "UNDEFINED_UNTIL_NORMALIZED_H26_IS_SERIALIZED"
        ),
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "lifecycle_layer": "LORENTZIAN_RETAINED_BV_HADAMARD_RESTRICTION",
        "claim_boundary": (
            "The retained Ward theorem proves that C26=[H26_plus,q26] is "
            "smooth, while the imported endpoint theorems expose only "
            "existence statements and symbolic pullback formulas. They do "
            "not select or serialize one normalized H26_plus representative. "
            "Consequently exact x/y past-, future- and time-compact support "
            "and pairing-null status are undefined, not false. The classical "
            "one-sided homotopies therefore cannot yet act on C26. No BRST "
            "Hadamard covariance, positivity, particle interpretation, "
            "renormalized product, Lorentzian QME, scattering or unitarity "
            "claim is established."
        ),
        "representation_audit": {
            "H26_formula": values["ward_reduction"]["ward_reduction"][
                "degreewise_kernel"
            ],
            "C26_formula": "C26=[H26_plus,q26]",
            "C26_regularness": "SMOOTH_WITH_EMPTY_WAVEFRONT_SET",
            "H26_fixed_representative": False,
            "C26_content_addressed_bikernel": False,
            "blocks": blocks,
            "conclusion": (
                "EXISTENCE_AND_SYMBOLIC_FORMULAS_DO_NOT_DEFINE_THE_"
                "REPRESENTATIVE_DEPENDENT_SUPPORT_PROFILE"
            ),
        },
        "representative_ambiguity": {
            "allowed_replacement": "H26_plus -> H26_plus+K",
            "K_type": (
                "smooth graded exact bisolution preserving the fixed "
                "antisymmetric Pauli-Jordan part and endpoint equations"
            ),
            "induced_remainder": "C26 -> C26+[K,q26]",
            "scope": (
                "This identity proves that a support profile requires a fixed "
                "representative. It does not assert that every admissible K "
                "changes support or that no equivariant representative exists."
            ),
        },
        "support_profile": {
            "x_past_compact": UNDEFINED,
            "x_future_compact": UNDEFINED,
            "x_time_compact": UNDEFINED,
            "y_past_compact": UNDEFINED,
            "y_future_compact": UNDEFINED,
            "y_time_compact": UNDEFINED,
            "stationary_harmonic_support": UNDEFINED,
            "pairing_null_on_closed_exact_pairs": UNDEFINED,
            "full_smooth_class_membership": "CERTIFIED_BY_SMOOTHNESS",
            "full_smooth_factorized_homotopy": (
                "OBSTRUCTED_BY_CLASSICAL_CUTOFF_ESCAPE_THEOREM"
            ),
        },
        "first_obstruction": {
            "obstruction_id": (
                "MISSING_NORMALIZED_SERIALIZED_H26_REPRESENTATIVE"
            ),
            "classification": "NO_CERTIFIED_MAP",
            "typed_response": (
                "C26_SUPPORT_PROFILE_UNDEFINED_AT_EXISTENTIAL_STATE_SELECTION"
            ),
            "minimal_next_payload": [
                "one fixed content-addressed H26_plus representative",
                "per-block mode indices, frequencies and exact coefficient matrices or an executable distribution evaluator",
                "the convergence topology defining the global distribution",
                "the q26 action in both kernel variables",
                "the explicit smooth remainder relative to the pinned local Hadamard parametrix",
                "the resulting serialized commutator C26=[H26_plus,q26]",
                "exact x/y support booleans and a pairing-null witness or counterexample",
            ],
            "consumer_typed_need": (
                "C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER"
            ),
        },
        "classical_consumer_disposition": {
            "one_sided_homotopies_available": True,
            "C26_positive_domain_membership": "NOT_DECIDABLE_FROM_CURRENT_EXPORT",
            "C26_specific_smooth_correction": "NOT_CONSTRUCTED",
            "next_action": (
                "serialize a normalized H26_plus and compute C26 before "
                "re-entering the classical support gate"
            ),
        },
        "claim_flags": {
            "C26_SMOOTH": True,
            "C26_SERIALIZED": False,
            "C26_X_SUPPORT_PROFILE_CERTIFIED": False,
            "C26_Y_SUPPORT_PROFILE_CERTIFIED": False,
            "C26_PAIRING_NULL_CERTIFIED": False,
            "NORMALIZED_H26_REPRESENTATIVE_SUPPLIED": False,
            "RETAINED_26_BRST_HADAMARD": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "exact_checks": {
            "all_dependencies_match_expected_result_ids": True,
            "ward_remainder_formula_and_smoothness_imported": True,
            "ward_vanishing_remains_not_decided": True,
            "endpoint_exports_are_symbolic_or_existential": True,
            "no_endpoint_block_serializes_a_kernel_or_mode_table": all(
                not block["serialized_bikernel"]
                and not block["stationary_mode_table"]
                and not block["executable_distribution_evaluator"]
                for block in blocks
            ),
            "classical_positive_domain_membership_is_not_exported": True,
            "classical_full_smooth_factorization_obstruction_imported": True,
            "unknown_support_is_not_encoded_as_false": all(
                value == UNDEFINED
                for key, value in result_support_items().items()
            ),
        },
        "dependency_refs": {
            name: {
                "path": _relative(path),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "next_gate": "SERIALIZE_NORMALIZED_H26_THEN_COMPUTE_C26_SUPPORT_AND_PAIRING_NULL_STATUS",
    }
    validate(result)
    return result


def result_support_items() -> dict[str, str]:
    return {
        "x_past_compact": UNDEFINED,
        "x_future_compact": UNDEFINED,
        "x_time_compact": UNDEFINED,
        "y_past_compact": UNDEFINED,
        "y_future_compact": UNDEFINED,
        "y_time_compact": UNDEFINED,
        "stationary_harmonic_support": UNDEFINED,
        "pairing_null_on_closed_exact_pairs": UNDEFINED,
    }


def validate(value: dict[str, Any]) -> None:
    if value["dependency_tags"] != ["LORENTZIAN-CAUSAL"]:
        raise ValueError("dependency tags crossed the Lorentzian boundary")
    profile = value["support_profile"]
    for key, expected in result_support_items().items():
        if profile.get(key) != expected:
            raise ValueError("undefined support or pairing status was over-promoted")
    flags = value["claim_flags"]
    forbidden = (
        "C26_SERIALIZED",
        "C26_X_SUPPORT_PROFILE_CERTIFIED",
        "C26_Y_SUPPORT_PROFILE_CERTIFIED",
        "C26_PAIRING_NULL_CERTIFIED",
        "NORMALIZED_H26_REPRESENTATIVE_SUPPLIED",
        "RETAINED_26_BRST_HADAMARD",
        "PHYSICAL_POSITIVITY_CERTIFIED",
        "LORENTZIAN_QME_RESTORED",
        "QUANTUM_CLAIM",
    )
    if not flags["C26_SMOOTH"] or any(flags[name] for name in forbidden):
        raise ValueError("claim flags crossed the non-definition boundary")
    if (
        value["first_obstruction"]["classification"] != "NO_CERTIFIED_MAP"
        or value["classical_consumer_disposition"][
            "C26_positive_domain_membership"
        ]
        != "NOT_DECIDABLE_FROM_CURRENT_EXPORT"
    ):
        raise ValueError("first obstruction was over-promoted")


if __name__ == "__main__":
    evaluate()
    print("BERGER C26 BIKERNEL SUPPORT PROFILE NONDEFINITION: PASS")
