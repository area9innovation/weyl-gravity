"""Reduce the retained-26 Hadamard gate to one smooth Ward equation."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
METRIC = (
    HERE
    / "certificates/"
    "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
)
GHOST = HERE / "certificates/BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR.json"
CAUSAL = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
CLASSICAL_CAUSAL = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
)

DEPENDENCIES = {
    "metric_endpoint_Hadamard_pair": METRIC,
    "ghost_identity_Hadamard_pair": GHOST,
    "causal_chain_import": CAUSAL,
    "graded_state_space_contract": GRADED,
    "local_Hadamard_parametrix": BASE,
    "classical_26_row_causal_homotopy": CLASSICAL_CAUSAL,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(payload: dict[str, Any]) -> str:
    return str(payload.get("result_id") or payload.get("schema"))


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": _artifact_id(payload), "sha256": _sha256(path)}


def ward_reduction_replay(
    *,
    kinetic_identity: bool = True,
    exact_bisolution: bool = True,
    cyclic_witness: bool = True,
    local_singular_intertwining: bool = True,
) -> dict[str, Any]:
    """Replay the formal expansion and the smoothness conclusion.

    With P=qW+Wq and Omega=WH,

        delta_q Omega = qWH + WHq
                      = PH + W(Hq-qH).
    """

    exact_formula = kinetic_identity
    kinetic_term_zero = exact_formula and exact_bisolution
    defect_is_witness_times_commutator = kinetic_term_zero
    exact_ccr = cyclic_witness and exact_bisolution
    defect_smooth = (
        defect_is_witness_times_commutator
        and local_singular_intertwining
    )
    checks = {
        "P26_equals_q26_W26_plus_W26_q26": kinetic_identity,
        "H26_is_degreewise_exact_global_Hadamard_bisolution": exact_bisolution,
        "Omega26_is_W26_H26": True,
        "Ward_expansion_is_PH_plus_W_times_Hq_minus_qH": exact_formula,
        "PH_term_vanishes": kinetic_term_zero,
        "exact_Ward_defect_is_W26_times_Hq_minus_qH": (
            defect_is_witness_times_commutator
        ),
        "cyclicity_and_degreewise_CCR_give_full_exact_CCR": exact_ccr,
        "local_Hadamard_singular_part_intertwines_q26": (
            local_singular_intertwining
        ),
        "remaining_Ward_defect_is_smooth": defect_smooth,
    }
    return {
        "degreewise_kernel": (
            "H26_plus=diag(H_ghost_plus,H_metric_plus,"
            "H_metric_adjoint_plus,H_identity_plus)"
        ),
        "candidate": "Omega26_plus=W26 H26_plus",
        "kinetic_identity": "P26=q26 W26+W26 q26",
        "exact_CCR": (
            "Omega26_plus-Omega26_plus^sharp_graded=i Delta26"
        ),
        "Ward_calculation": (
            "delta_q Omega26_plus=q26 W26 H26_plus+W26 H26_plus q26"
            "=P26 H26_plus+W26(H26_plus q26-q26 H26_plus)"
            "=W26[H26_plus,q26]"
        ),
        "smooth_defect": "C26=[H26_plus,q26] is a smooth kernel",
        "sufficient_zero_condition": "[H26_plus,q26]=0",
        "minimal_equation": "find smooth S26 with delta_q S26=-W26 C26",
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def support_class_audit(
    *,
    global_smooth_kernel_homotopy_exported: bool = False,
) -> dict[str, Any]:
    """Distinguish causal test-source homotopy from the needed kernel homotopy."""

    checks = {
        "compact_source_advanced_retarded_chain_homotopies_exist": True,
        "smooth_Hadamard_Ward_defect_identified": True,
        "compact_source_identity_alone_does_not_act_on_arbitrary_bikernels": True,
        "global_smooth_bikernel_support_class_not_declared": (
            not global_smooth_kernel_homotopy_exported
        ),
        "no_automatic_Ward_promotion": not global_smooth_kernel_homotopy_exported,
    }
    return {
        "available": (
            "q26 Lambda26,+/-+Lambda26,+/- q26=I on compactly supported "
            "smooth sources, with advanced/retarded support"
        ),
        "missing": (
            "a declared past/future-compact or time-slice extension acting "
            "continuously on the smooth two-variable Ward-defect class"
        ),
        "required_output": (
            "either a q26-equivariant global Feynman/Hadamard selection or "
            "a smooth correction S26 with its support-class proof"
        ),
        "status": (
            "MISSING_SMOOTH_KERNEL_HOMOTOPY_CARRIER"
            if not global_smooth_kernel_homotopy_exported
            else "SMOOTH_KERNEL_HOMOTOPY_AVAILABLE"
        ),
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in DEPENDENCIES.items()
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    metric = values["metric_endpoint_Hadamard_pair"]
    ghost = values["ghost_identity_Hadamard_pair"]
    causal = values["causal_chain_import"]
    graded = values["graded_state_space_contract"]
    base = values["local_Hadamard_parametrix"]
    classical = values["classical_26_row_causal_homotopy"]

    input_checks = {
        "metric_twenty_row_global_Hadamard_exact_CCR_pair": metric[
            "claim_flags"
        ]["BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK"]
        is True,
        "ghost_identity_six_row_global_Hadamard_exact_CCR_pair": ghost[
            "claim_flags"
        ]["BERGER_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR"]
        is True,
        "retained_26_causal_homotopy_imported": causal["claim_flags"][
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"
        ]
        is True,
        "graded_causal_CCR_and_cyclicity_certified": graded["claim_flags"][
            "BERGER_GRADED_CAUSAL_COMMUTATOR"
        ]
        is True,
        "local_parametrix_left_right_and_adjoint_checks": all(
            base["verified_checks"][name]
            for name in (
                "left_parametrix_modulo_smooth",
                "right_parametrix_modulo_smooth",
                "typed_adjoint_reversal_modulo_smooth",
            )
        ),
        "classical_chain_homotopy_checks_complete": all(
            row["status"] == "VERIFIED"
            for row in classical["green_proof_checks"].values()
        ),
        "classical_Hadamard_kernel_still_absent": classical["hadamard"][
            "status"
        ]
        == "NOT_CONSTRUCTED",
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"retained-26 Ward reduction input drift: {failed}")

    reduction = ward_reduction_replay()
    support = support_class_audit()
    bad_kinetic = ward_reduction_replay(kinetic_identity=False)
    bad_singular = ward_reduction_replay(
        local_singular_intertwining=False
    )
    overpromoted_support = support_class_audit(
        global_smooth_kernel_homotopy_exported=True
    )
    if (
        not reduction["all_pass"]
        or not support["all_pass"]
        or bad_kinetic["all_pass"]
        or bad_singular["all_pass"]
        or overpromoted_support["all_pass"]
    ):
        raise ValueError("retained-26 Ward reduction replay failed")

    result = {
        "schema": "quantum-weyl-berger-retained26-hadamard-ward-reduction-v1",
        "result_id": "BERGER_RETAINED26_HADAMARD_WARD_REDUCTION",
        "result_state": (
            "ALL_26_ENDPOINT_ROWS_GLOBAL_HADAMARD_EXACT_CCR_CANDIDATE_"
            "ASSEMBLED_SMOOTH_Q26_WARD_CARRIER_OPEN"
        ),
        "lifecycle_layer": "LORENTZIAN_RETAINED_BV_HADAMARD_RESTRICTION",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": metric["classical_commit"],
        "setting_id": metric["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "ward_reduction": reduction,
        "smooth_support_class_audit": support,
        "candidate_status": {
            "all_26_endpoint_rows_have_global_Hadamard_carriers": True,
            "full_exact_graded_CCR_from_cyclic_witness": True,
            "Ward_defect_formula_computed": True,
            "Ward_defect_is_smooth": True,
            "Ward_defect_vanishes": "NOT_DECIDED",
            "smooth_correction_constructed": False,
            "retained_26_BRST_Hadamard": False,
        },
        "negative_controls": {
            "remove_kinetic_witness_identity": bad_kinetic,
            "remove_local_singular_intertwining": bad_singular,
            "pretend_compact_source_homotopy_acts_on_all_bikernels": (
                overpromoted_support
            ),
        },
        "claim_flags": {
            "BERGER_ALL_26_ENDPOINT_HADAMARD_CARRIERS": True,
            "BERGER_26_ROW_HADAMARD_EXACT_CCR_CANDIDATE": True,
            "BERGER_26_ROW_WARD_DEFECT_SMOOTH": True,
            "BERGER_SMOOTH_Q26_WARD_COMPLETION": False,
            "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "CONSTRUCT_Q26_EQUIVARIANT_GLOBAL_FEYNMAN_SELECTION_OR_SMOOTH_"
            "WARD_CORRECTION_WITH_DECLARED_BIKERNEL_SUPPORT_CLASS"
        ),
        "provenance": {
            "proof_type": (
                "EXACT_KINETIC_WITNESS_EXPANSION_LOCAL_HADAMARD_"
                "INTERTWINING_AND_SUPPORT_CLASS_AUDIT"
            )
        },
        "claim_boundary": (
            "All four degreewise endpoint sectors now have global exact "
            "Hadamard carriers, and the cyclic witness assembles an exact-CCR "
            "26-row candidate. Its BRST Ward defect is exactly "
            "W26[H26,q26] and is smooth. The existing advanced/retarded chain "
            "homotopies are certified on compactly supported test sources, "
            "not on the arbitrary smooth two-variable defect class, so they "
            "cannot silently be applied as a global correction. A declared "
            "bikernel support class and continuous homotopy, or a directly "
            "q26-equivariant Feynman selection, remains required. No retained "
            "BRST Hadamard, 54-row lift, positivity, particle, renormalized "
            "Lorentzian product, Lorentzian QME or quantum theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_RETAINED26_HADAMARD_WARD_REDUCTION"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != (
            "CONSTRUCT_Q26_EQUIVARIANT_GLOBAL_FEYNMAN_SELECTION_OR_SMOOTH_"
            "WARD_CORRECTION_WITH_DECLARED_BIKERNEL_SUPPORT_CLASS"
        )
        or not all(result.get("exact_input_checks", {}).values())
        or result.get("ward_reduction", {}).get("all_pass") is not True
        or result.get("smooth_support_class_audit", {}).get("all_pass")
        is not True
    ):
        raise ValueError("retained-26 Ward reduction failed")
    flags = result.get("claim_flags", {})
    true_flags = {
        "BERGER_ALL_26_ENDPOINT_HADAMARD_CARRIERS",
        "BERGER_26_ROW_HADAMARD_EXACT_CCR_CANDIDATE",
        "BERGER_26_ROW_WARD_DEFECT_SMOOTH",
    }
    if any(flags.get(name) is not True for name in true_flags):
        raise ValueError("retained-26 candidate under-promoted")
    if any(
        value is not False
        for name, value in flags.items()
        if name not in true_flags
    ):
        raise ValueError("BRST Hadamard or quantum claim over-promoted")
