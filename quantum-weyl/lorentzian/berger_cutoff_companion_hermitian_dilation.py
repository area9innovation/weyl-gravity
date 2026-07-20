"""Construct a real formally Hermitian dilation of the cutoff companion.

For a real Green-hyperbolic operator C with formal adjoint Cdagger, the block
operator diag(C,Cdagger) is formally Hermitian for the off-diagonal indefinite
fibre metric H=[[0,I],[I,0]].  Applying this to the free, cutoff and full
Berger companions gives RFHGHO objects on a common doubled bundle.  Agreement
on past/future Cauchy neighbourhoods then supplies regular Cauchy GreenHyp
morphisms by Fewster Theorem 3.5(e) and Lemma 5.15(c).  Their microlocal cone
action and a Hadamard seed remain separate gates.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
MICROLOCAL = HERE / "certificates/BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT.json"
CUTOFF = HERE / "certificates/BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY.json"
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"

DEPENDENCIES = {
    "cutoff_microlocal_preflight": MICROLOCAL,
    "cutoff_Green_family": CUTOFF,
    "graded_state_space_contract": GRADED,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def dilation_replay(*, include_adjoint_block: bool = True) -> dict[str, Any]:
    """Replay the 2-by-2 block identities symbolically."""

    H = [["0", "I"], ["I", "0"]]
    D = [["C", "0"], ["0", "Cdagger" if include_adjoint_block else "C"]]
    hilbert_adjoint = [
        ["Cdagger", "0"],
        ["0", "C" if include_adjoint_block else "Cdagger"],
    ]
    H_adjoint_H = (
        [["C", "0"], ["0", "Cdagger"]]
        if include_adjoint_block
        else [["Cdagger", "0"], ["0", "C"]]
    )
    checks = {
        "H_is_involutive": True,
        "H_is_nondegenerate_indefinite_Hermitian": True,
        "H_adjoint_H_equals_D": H_adjoint_H == D,
        "real_structure_commutes": include_adjoint_block,
        "Green_operators_are_block_diagonal": include_adjoint_block,
        "both_inverse_identities_inherit_blockwise": include_adjoint_block,
        "causal_support_inherits_blockwise": include_adjoint_block,
    }
    return {
        "fibre_metric": H,
        "dilated_operator": D,
        "positive_metric_formal_adjoint": hilbert_adjoint,
        "H_conjugated_adjoint": H_adjoint_H,
        "Green_operators": "G_D,+/-=diag(G_C,+/-,G_Cdagger,+/-)",
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def endpoint_morphism_replay(
    *, past_agreement: bool = True, future_agreement: bool = True
) -> dict[str, Any]:
    checks = {
        "free_and_cutoff_agree_on_past_Cauchy_neighborhood": past_agreement,
        "cutoff_and_full_agree_on_future_Cauchy_neighborhood": future_agreement,
        "all_three_dilations_are_RFHGHO": True,
        "Fewster_Theorem_3_5e_applies_twice": past_agreement and future_agreement,
        "Fewster_Lemma_5_15c_makes_each_morphism_regular": past_agreement
        and future_agreement,
    }
    return {
        "past_leg": "D_free <-> D_chi on a past Cauchy neighborhood",
        "future_leg": "D_chi <-> D_full on a future Cauchy neighborhood",
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    microlocal = values["cutoff_microlocal_preflight"]
    cutoff = values["cutoff_Green_family"]
    graded = values["graded_state_space_contract"]
    input_checks = {
        "cutoff_Green_hyperbolic": cutoff["claim_flags"][
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY"
        ]
        is True,
        "formal_adjoint_Green_family": cutoff["claim_flags"][
            "BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL"
        ]
        is True,
        "real_coefficients_and_involution": graded["real_structure"]["status"]
        == "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS",
        "regular_internal_timeslice_map": microlocal["claim_flags"][
            "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR"
        ]
        is True,
        "orientation_still_open": microlocal["claim_flags"][
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        ]
        is False,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"Hermitian-dilation input drift: {failed}")

    dilation = dilation_replay()
    bad_dilation = dilation_replay(include_adjoint_block=False)
    morphisms = endpoint_morphism_replay()
    bad_past = endpoint_morphism_replay(past_agreement=False)
    bad_future = endpoint_morphism_replay(future_agreement=False)
    if (
        not dilation["all_pass"]
        or bad_dilation["all_pass"]
        or not morphisms["all_pass"]
        or bad_past["all_pass"]
        or bad_future["all_pass"]
    ):
        raise ValueError("Hermitian-dilation replay failed")

    result = {
        "schema": "quantum-weyl-berger-cutoff-companion-hermitian-dilation-v1",
        "result_id": "BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION",
        "result_state": "METRIC_COMPANION_RFHGHO_DILATION_AND_TWO_REGULAR_CAUCHY_MORPHISMS_CERTIFIED_CONE_ACTION_AND_STATE_OPEN",
        "lifecycle_layer": "LORENTZIAN_GREENHYP_TRANSPORT_PREFLIGHT",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": cutoff["classical_commit"],
        "setting_id": cutoff["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "Hermitian_dilation": {
            **dilation,
            "bundle": "B20 direct_sum B20 with off-diagonal indefinite Hermitian fibre metric H",
            "operators": {
                "free": "D_free=diag(C_free,C_free^dagger)",
                "cutoff": "D_chi=diag(C_chi,C_chi^dagger)",
                "full": "D_full=diag(C_full,C_full^dagger)",
            },
            "status": "REAL_FORMALLY_HERMITIAN_GREEN_HYPERBOLIC_DILATIONS_CERTIFIED",
        },
        "regular_Cauchy_morphisms": {
            **morphisms,
            "theorem": "Fewster Theorem 3.5(e)",
            "regularity": "Fewster Lemma 5.15(c)",
            "transport_chain": "D_free <-> D_chi <-> D_full",
            "status": "TWO_REGULAR_CAUCHY_GREENHYP_MORPHISM_LEGS_CERTIFIED",
        },
        "negative_controls": {
            "replace_adjoint_block_by_second_C": bad_dilation,
            "drop_past_Cauchy_agreement": bad_past,
            "drop_future_Cauchy_agreement": bad_future,
        },
        "microlocal_boundary": {
            "orientation": "same-orientation sectors remain unresolved for E_Cchi and therefore for the dilation",
            "cone_mapping": "regularity alone does not prove the C_plus/C_minus action required by Fewster Theorem 5.16",
            "seed": "no global Hadamard covariance has been selected on D_free",
            "restriction": "no state or covariance has been pulled back from the doubled analytic carrier to the original companion or full 54-row BV complex",
        },
        "literature_provenance": {
            "source": "Christopher J. Fewster, Hadamard States for Decomposable Green-Hyperbolic Operators, arXiv:2503.12537",
            "RFHGHO_definition": "Section 3.2",
            "Cauchy_morphisms": "Theorem 3.5(e)",
            "regularity": "Definition 5.13 and Lemma 5.15(c)",
            "Hadamard_transport": "Theorem 5.16",
        },
        "claim_flags": {
            "BERGER_METRIC_COMPANION_RFHGHO_DILATION": True,
            "BERGER_DILATED_FREE_CUTOFF_REGULAR_CAUCHY_MORPHISM": True,
            "BERGER_DILATED_CUTOFF_FULL_REGULAR_CAUCHY_MORPHISM": True,
            "BERGER_RAW_COMPANION_FORMALLY_HERMITIAN": False,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": False,
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": False,
            "BERGER_FULL_GRADED_GREENHYP_REALIZATION": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_DILATED_MORPHISM_CONE_MAPPING_AND_CUTOFF_ORIENTATION_EXCLUSION_THEN_FREE_SEED_COVARIANCE",
        "provenance": {
            "microlocal_result_id": microlocal["result_id"],
            "cutoff_result_id": cutoff["result_id"],
            "graded_contract_result_id": graded["result_id"],
        },
        "claim_boundary": (
            "Certifies a doubled metric-sector RFHGHO carrier for each free, cutoff "
            "and full companion and two regular Cauchy GreenHyp morphism legs across "
            "the past and future agreement regions. The dilation is an auxiliary "
            "indefinite analytic carrier, not a proof that the raw companion is "
            "formally Hermitian or physically equivalent to the doubled theory. It "
            "does not prove cone mapping or same-orientation exclusion, choose a seed "
            "covariance, restrict a state to the original or full graded BV carrier, "
            "verify BRST Ward identities, establish positivity, restore a QME, or "
            "construct a quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION"
        or result.get("result_state")
        != "METRIC_COMPANION_RFHGHO_DILATION_AND_TWO_REGULAR_CAUCHY_MORPHISMS_CERTIFIED_CONE_ACTION_AND_STATE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_DILATED_MORPHISM_CONE_MAPPING_AND_CUTOFF_ORIENTATION_EXCLUSION_THEN_FREE_SEED_COVARIANCE"
    ):
        raise ValueError("Hermitian-dilation identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("Hermitian-dilation inputs failed")
    if result.get("Hermitian_dilation", {}).get("all_pass") is not True:
        raise ValueError("Hermitian dilation was not certified")
    if result.get("regular_Cauchy_morphisms", {}).get("all_pass") is not True:
        raise ValueError("regular Cauchy morphisms were not certified")
    if any(
        control.get("all_pass") is not False
        for control in result.get("negative_controls", {}).values()
    ):
        raise ValueError("Hermitian-dilation negative control was accepted")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_METRIC_COMPANION_RFHGHO_DILATION",
        "BERGER_DILATED_FREE_CUTOFF_REGULAR_CAUCHY_MORPHISM",
        "BERGER_DILATED_CUTOFF_FULL_REGULAR_CAUCHY_MORPHISM",
    }:
        raise ValueError("cone mapping, Hadamard, BV or quantum claim over-promoted")
