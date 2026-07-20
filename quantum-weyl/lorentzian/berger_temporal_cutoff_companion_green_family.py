"""Specialize the generic typed Volterra theorem to a Berger time cutoff.

The generic theorem already permits smooth time-dependent coefficients.  A
smooth switch chi(t) therefore turns the stationary Berger remainder V2 into
an admissible nonstationary remainder chi V2.  The resulting companion agrees
with the normally-hyperbolic free companion in the past and with the full
Berger companion in the future.  This closes Green existence, not microlocal
Hadamard propagation.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

GENERIC_IMPORT = HERE / "certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json"
GENERIC_CLASSICAL = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json"
BERGER_COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
BERGER_VOLTERRA = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"
BASE_PARAMETRIX = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"

DEPENDENCIES = {
    "generic_typed_volterra_import": GENERIC_IMPORT,
    "pinned_generic_classical_theorem": GENERIC_CLASSICAL,
    "Berger_companion": BERGER_COMPANION,
    "Berger_stationary_volterra": BERGER_VOLTERRA,
    "base_wave_parametrix": BASE_PARAMETRIX,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def cutoff_specialization_replay(*, drop_time_dependence: bool = False) -> dict[str, Any]:
    """Replay the implication from the generic theorem to chi(t)V2."""

    assumptions = {
        "chi_smooth": True,
        "chi_zero_on_past_Cauchy_neighborhood": True,
        "chi_one_on_future_Cauchy_neighborhood": True,
        "d_chi_temporally_compact": True,
        "smooth_multiplication_bounded_on_each_slab_Sobolev_space": True,
        "V2_graph_bounded_order_at_most_two": True,
        "generic_theorem_allows_smooth_time_dependence": not drop_time_dependence,
    }
    checks = {
        "cutoff_remainder_has_order_at_most_two": assumptions[
            "V2_graph_bounded_order_at_most_two"
        ],
        "cutoff_remainder_preserves_graph_domain_bound": assumptions[
            "chi_smooth"
        ]
        and assumptions["smooth_multiplication_bounded_on_each_slab_Sobolev_space"],
        "cutoff_coefficients_are_smoothly_time_dependent": assumptions["chi_smooth"],
        "generic_theorem_accepts_cutoff_time_dependence": assumptions[
            "generic_theorem_allows_smooth_time_dependence"
        ],
        "past_operator_is_free_companion": assumptions[
            "chi_zero_on_past_Cauchy_neighborhood"
        ],
        "future_operator_is_full_Berger_companion": assumptions[
            "chi_one_on_future_Cauchy_neighborhood"
        ],
        "transition_is_temporally_compact": assumptions["d_chi_temporally_compact"],
    }
    return {
        "assumptions": assumptions,
        "checks": checks,
        "all_pass": all(checks.values()),
        "operators": {
            "free_biwave": "A_free=Box_2^2",
            "cutoff_biwave": "A_chi=Box_2^2+chi(t)V_2",
            "full_biwave": "A_full=Box_2^2+V_2=A10",
            "free_companion": "C_free=[[Box_2,-I10],[0,Box_2]]",
            "cutoff_companion": "C_chi=[[Box_2,-I10],[chi(t)V_2,Box_2]]",
            "full_companion": "C_full=[[Box_2,-I10],[V_2,Box_2]]",
        },
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    data = _load()
    imported = data["generic_typed_volterra_import"]
    generic = data["pinned_generic_classical_theorem"]
    companion = data["Berger_companion"]
    stationary = data["Berger_stationary_volterra"]
    base = data["base_wave_parametrix"]

    pinned = imported["provenance"]["classical_artifacts"]["certificate"]
    source_checks = {
        "generic_theorem_imported": imported["claim_flags"][
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"
        ]
        is True,
        "working_classical_theorem_matches_pinned_hash": pinned["sha256"]
        == _sha256(GENERIC_CLASSICAL),
        "generic_theorem_allows_time_dependence": generic["operator_hypotheses"][
            "stationarity_required"
        ]
        is False
        and "smooth time dependence allowed"
        in generic["geometric_hypotheses"]["temporal_dependence"],
        "generic_theorem_accepts_order_two_graph_bounded_remainder": "order at most two"
        in generic["operator_hypotheses"]["V"],
        "generic_theorem_supplies_Green_family_properties": all(
            generic["theorem"][name] is True
            for name in (
                "companion_green_hyperbolic",
                "biwave_green_hyperbolic",
                "both_inverse_identities",
                "causal_support",
                "globalization_by_uniqueness",
            )
        ),
        "Berger_normal_form_is_lower_order_biwave": companion["companion_system"][
            "operator"
        ]
        == "C20=[[Box_2,-I10],[V_2,Box_2]]"
        and companion["causal_policy"]["off_diagonal_local_orders"]
        == {"lower_left": 2, "upper_right": 0},
        "Berger_stationary_consumer_already_satisfies_energy_hypotheses": stationary[
            "claim_flags"
        ]["BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"]
        is True,
        "base_tensor_wave_is_normally_hyperbolic": base["operator_family"][
            "principal_symbol"
        ]
        == "g^{-1}(xi,xi) times the fibre identity",
    }
    if not all(source_checks.values()):
        failed = [name for name, passed in source_checks.items() if not passed]
        raise ValueError(f"cutoff Green-family source drift: {failed}")

    replay = cutoff_specialization_replay()
    if not replay["all_pass"]:
        raise ValueError("Berger cutoff specialization failed")
    negative = cutoff_specialization_replay(drop_time_dependence=True)
    if negative["all_pass"]:
        raise ValueError("time-dependence negative control was accepted")

    result = {
        "schema": "quantum-weyl-berger-temporal-cutoff-companion-green-family-v1",
        "result_id": "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY",
        "result_state": "NONSTATIONARY_CUTOFF_GREEN_FAMILY_CERTIFIED_MICROLOCAL_PROPAGATION_AND_SEED_COVARIANCE_OPEN",
        "lifecycle_layer": "LORENTZIAN_CAUSAL_CUTOFF_FAMILY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": base["classical_commit"],
        "setting_id": base["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in data.items()
        },
        "exact_input_checks": source_checks,
        "cutoff_policy": {
            "chi": "smooth real function of Berger time t",
            "past": "chi=0 on and before a past Cauchy neighborhood",
            "future": "chi=1 on and after a future Cauchy neighborhood",
            "transition": "supp(d chi) lies in a compact time slab",
            "multiplication_side": "V_chi=chi V_2",
        },
        "specialization_replay": replay,
        "negative_control": {
            "mutation": "forbid smooth time dependence in the generic theorem",
            "all_pass": negative["all_pass"],
            "failed_check": "generic_theorem_accepts_cutoff_time_dependence",
        },
        "Green_family_theorem": {
            "family": "all smooth cutoffs satisfying cutoff_policy",
            "advanced_retarded_companion": "G_Cchi,+/-:Y_s(I)->X_s(I)",
            "advanced_retarded_biwave": "G_Achi,+/-=p G_Cchi,+/- i",
            "both_inverse_identities": "CERTIFIED",
            "causal_support": "CERTIFIED",
            "nested_slab_globalization": "CERTIFIED",
            "formal_adjoint_reversal": "(G_Achi,+)^sharp=G_(Achi^sharp),- and conversely",
            "stationarity_required": False,
            "status": "CERTIFIED_CONDITIONAL_ON_THE_ALREADY_VERIFIED_BERGER_GRAPH_DOMAIN_HYPOTHESES",
        },
        "Hadamard_route": {
            "past_seed_operator": "C_free=[[Box_2,-I10],[0,Box_2]], normally hyperbolic principal symbol",
            "future_target_operator": "C_full=[[Box_2,-I10],[V_2,Box_2]]",
            "cutoff_Green_hyperbolicity": "CERTIFIED",
            "cutoff_kernel_wavefront_bound": "OPEN",
            "cutoff_null_cone_decomposability": "OPEN",
            "regular_response_morphism": "OPEN",
            "global_seed_covariance_with_Krein_policy": "OPEN",
            "BRST_Ward_identity": "OPEN",
        },
        "claim_flags": {
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY": True,
            "BERGER_CUTOFF_COMPANION_BOTH_INVERSE_IDENTITIES": True,
            "BERGER_CUTOFF_COMPANION_CAUSAL_SUPPORT": True,
            "BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL": True,
            "BERGER_CUTOFF_COMPANION_WAVEFRONT_THEOREM": False,
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE": False,
            "BERGER_REGULAR_GREENHYP_MORPHISM": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_CUTOFF_COMPANION_MICROLOCAL_PROPAGATION_AND_REGULAR_RESPONSE_MORPHISM",
        "provenance": {
            "generic_theorem_result_id": generic["result_id"],
            "generic_import_result_id": imported["result_id"],
            "Berger_companion_result_id": companion["result_id"],
        },
        "claim_boundary": (
            "Specializes the pinned generic typed Volterra theorem to the smooth "
            "nonstationary family V_chi=chi(t)V_2. It certifies global advanced and "
            "retarded Green operators, both inverse identities, causal support and "
            "formal-adjoint reversal for every declared cutoff. It does not control "
            "the wavefront set of the cutoff Green kernel, prove cutoff companion "
            "decomposability or regular response-map transport, choose a global seed "
            "covariance, verify BRST Ward identities or construct a Hadamard state, "
            "positivity, QME or quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY"
        or result.get("result_state")
        != "NONSTATIONARY_CUTOFF_GREEN_FAMILY_CERTIFIED_MICROLOCAL_PROPAGATION_AND_SEED_COVARIANCE_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_CUTOFF_COMPANION_MICROLOCAL_PROPAGATION_AND_REGULAR_RESPONSE_MORPHISM"
    ):
        raise ValueError("cutoff Green-family identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("cutoff Green-family inputs failed")
    if result.get("specialization_replay", {}).get("all_pass") is not True:
        raise ValueError("cutoff specialization replay failed")
    if result.get("negative_control", {}).get("all_pass") is not False:
        raise ValueError("cutoff time-dependence negative control failed")
    flags = result.get("claim_flags", {})
    true_flags = {name for name, value in flags.items() if value is True}
    if true_flags != {
        "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY",
        "BERGER_CUTOFF_COMPANION_BOTH_INVERSE_IDENTITIES",
        "BERGER_CUTOFF_COMPANION_CAUSAL_SUPPORT",
        "BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL",
    }:
        raise ValueError("cutoff Green-family lifecycle was over-promoted")


def mutate_overpromotion(result: dict[str, Any]) -> dict[str, Any]:
    mutant = deepcopy(result)
    mutant["claim_flags"]["BERGER_CUTOFF_COMPANION_WAVEFRONT_THEOREM"] = True
    return mutant
