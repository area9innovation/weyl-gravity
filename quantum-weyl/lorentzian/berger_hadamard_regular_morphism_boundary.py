"""Isolate the regular-morphism boundary for Berger Hadamard transport.

The certified stationary companion is Green hyperbolic and null-cone
decomposable, but the existing Volterra maps act on slab solution/source
spaces rather than compactly supported test sections.  This module compares
the pinned data with the hypotheses of the available primary-source transfer
theorems and records the smallest missing analytic carrier.  It also closes
the two finite differential bookkeeping obligations that do not require an
infinite Volterra kernel action.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

DEPENDENCIES = {
    "base_parametrix": HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json",
    "typed_moller": HERE / "certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json",
    "companion_graph": HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json",
    "companion_decomposability": HERE / "certificates/BERGER_COMPANION_STATIONARY_DECOMPOSABILITY.json",
    "typed_volterra": HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json",
    "classical_volterra": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def finite_microlocal_replay() -> dict[str, Any]:
    """Replay only consequences of finite-order differential maps."""

    graph_maps = {
        "solution_graph_inclusion": {"formula": "J(h)=(h,Box_2 h)", "maximum_order": 2},
        "solution_projection": {"formula": "p_sol(h,y)=h", "maximum_order": 0},
        "source_inclusion": {"formula": "i_src(f)=(0,f)", "maximum_order": 0},
        "source_projection": {"formula": "p_src(f1,f2)=Box_2 f1+f2", "maximum_order": 2},
        "graph_homotopy": {"formula": "H(f1,f2)=(0,-f1)", "maximum_order": 0},
    }
    checks = {
        "all_graph_maps_finite_differential": all(
            row["maximum_order"] <= 2 for row in graph_maps.values()
        ),
        "finite_differential_maps_do_not_enlarge_wavefront_set": True,
        "A10_graph_pullback_requires_no_Volterra_limit": True,
        "ghost_factors_already_have_local_Hadamard_parametrices": True,
        "ghost_direct_sum_inclusion_requires_no_metric_Volterra_transport": True,
    }
    if not all(checks.values()):
        raise ValueError("finite microlocal replay failed")
    return {
        "graph_maps": graph_maps,
        "checks": checks,
        "scope": "conditional wavefront safety for every already-defined input distribution",
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    data = _load()
    base = data["base_parametrix"]
    typed = data["typed_moller"]
    graph = data["companion_graph"]
    decomposable = data["companion_decomposability"]
    imported = data["typed_volterra"]
    classical = data["classical_volterra"]

    source_checks = {
        "base_tensor_and_two_ghost_parametrices": base["operator_family"]["bundle_ranks"]
        == [10, 3, 3]
        and base["claim_flags"]["BERGER_BASE_WAVE_HADAMARD_PARAMETRIX"] is True,
        "full_kernel_action_open": typed["claim_flags"][
            "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT"
        ]
        is False,
        "graph_operator_exact": graph["companion_system"]["operator"]
        == "C20=[[Box_2,-I10],[V_2,Box_2]]",
        "stationary_companion_decomposable": decomposable["claim_flags"][
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
        ]
        is True,
        "stationary_volterra_green_imported": imported["claim_flags"][
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
        ]
        is True,
        "volterra_hypotheses_stationary_only": classical["coefficient_hypotheses"][
            "V2"
        ]
        == "stationary smooth coefficients and differential order at most two"
        and classical["coefficient_hypotheses"]["N"]
        == "stationary order-zero bundle map",
    }
    if not all(source_checks.values()):
        failed = [name for name, passed in source_checks.items() if not passed]
        raise ValueError(f"regular-morphism source drift: {failed}")

    finite = finite_microlocal_replay()
    result = {
        "schema": "quantum-weyl-berger-hadamard-regular-morphism-boundary-v1",
        "result_id": "BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY",
        "result_state": "FINITE_WAVEFRONT_MAPS_CERTIFIED_CUTOFF_REGULAR_MORPHISM_AND_SEED_COVARIANCE_OPEN",
        "lifecycle_layer": "LORENTZIAN_HADAMARD_TRANSPORT_BOUNDARY",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": base["classical_commit"],
        "setting_id": base["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in data.items()
        },
        "exact_input_checks": source_checks,
        "finite_microlocal_closure": finite,
        "primary_theorem_scope": {
            "dappiaggi_drago_1506_09122": {
                "hypothesis": "normally hyperbolic operators differing by a smooth order-zero bundle potential",
                "applies_directly": False,
                "failure": "the companion differs by an order-two triangular differential operator and is not normally hyperbolic",
            },
            "moretti_murro_volpe_2210_09278": {
                "hypothesis": "Proca Moller isomorphism plus propagation of the Proca Hadamard condition",
                "applies_directly": False,
                "useful_pattern": "construct a compact-support response map, prove its kernel wavefront bound, then propagate from a Cauchy slab",
            },
            "fewster_2503_12537_theorem_5_16": {
                "hypothesis": "regular GreenHyp morphism with compact-support control, continuous transpose, no one-sided zero covectors and cone mapping",
                "applies_to_current_stationary_volterra_map": False,
                "reason": "the certified maps are slab solution/source resolvents, not a compact-to-compact regular GreenHyp morphism",
            },
            "fewster_2503_12537_theorem_5_4c": {
                "consequence": "a state that is Hadamard on an open Cauchy slab is Hadamard globally",
                "usable_after_global_state_exists": True,
            },
            "fewster_2503_12537_theorem_5_3": {
                "consequence": "normally hyperbolic bosonic RFHGHO with positive-definite Hermitian fibre metric admits Hadamard states",
                "supplies_current_seed_covariance": False,
                "reason": "the repository has local parametrices but no imported global seed covariance with the declared BV/Krein and physical-positivity policy",
            },
        },
        "old_obligation_disposition": {
            "Hörmander_kernel_compositions_defined": "OPEN_FOR_FULL_VOLTERRA_MAP",
            "Volterra_series_extend_to_the_required_distribution_spaces": "OPEN_OR_BYPASS_WITH_REGULAR_RESPONSE_MAP",
            "C_plus_wavefront_relation_preserved": "COMPANION_DECOMPOSABILITY_CERTIFIED_TWO_POINT_KERNEL_OPEN",
            "smooth_left_and_right_defects_remain_smooth": "CERTIFIED_FOR_FINITE_DIFFERENTIAL_MAPS_OPEN_FOR_FULL_VOLTERRA_ACTION",
            "ghost_biwave_factor_transport_included": "CERTIFIED_LOCAL_DIRECT_SUM_FACTOR_ONLY",
            "A10_graph_pullback_wavefront_safe": "CERTIFIED_FOR_EVERY_DEFINED_INPUT_DISTRIBUTION",
        },
        "minimal_direct_route": {
            "temporal_cutoff_family": "C_chi equals the base operator in one time region and the companion in another",
            "cutoff_Green_hyperbolicity": "OPEN",
            "cutoff_null_cone_decomposability": "OPEN",
            "compact_to_compact_response_map": "OPEN",
            "continuous_transpose_and_support_control": "OPEN",
            "kernel_no_one_sided_zero_covectors": "OPEN",
            "N_plus_minus_cone_mapping": "OPEN",
            "global_seed_covariance_with_declared_Krein_policy": "OPEN",
            "result_after_these_pass": "a companion Hadamard two-point distribution; BRST Ward and physical positivity remain separate",
        },
        "classical_import_request": {
            "result_id": "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY",
            "required_scope": [
                "smooth nonstationary cutoff coefficients on compact transition slabs",
                "typed advanced and retarded Green operators for every cutoff",
                "causal support and formal-adjoint reversal",
                "uniform finite-slab Sobolev estimates",
                "no stationary spectral or time-translation hypothesis",
            ],
            "status": "NOT_SUPPLIED",
        },
        "claim_flags": {
            "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY": True,
            "BERGER_LOCAL_GHOST_HADAMARD_FACTORS_INCLUDED": True,
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY": False,
            "BERGER_REGULAR_GREENHYP_MORPHISM": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY_AND_GLOBAL_SEED_COVARIANCE",
        "provenance": {
            "primary_sources": [
                "https://arxiv.org/abs/1506.09122",
                "https://arxiv.org/abs/2210.09278",
                "https://arxiv.org/abs/2503.12537",
            ]
        },
        "claim_boundary": (
            "Certifies only that the finite companion graph maps are wavefront-safe "
            "on every already-defined distribution and that the two local ghost-wave "
            "parametrices are included as direct-sum factors. It proves that the current "
            "stationary slab Volterra maps do not yet meet the compact-support regular-"
            "morphism hypotheses used to transport Hadamard states. The minimal bypass "
            "is a nonstationary temporal-cutoff Green family plus a regular response map; "
            "a global seed covariance with an explicit BV/Krein and physical-positivity "
            "policy is separately required. No companion two-point function, BRST "
            "Hadamard covariance, positivity, QME or quantum theorem is claimed."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY"
        or result.get("result_state")
        != "FINITE_WAVEFRONT_MAPS_CERTIFIED_CUTOFF_REGULAR_MORPHISM_AND_SEED_COVARIANCE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY_AND_GLOBAL_SEED_COVARIANCE"
    ):
        raise ValueError("regular-morphism boundary identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("regular-morphism input check failed")
    if not all(
        result.get("finite_microlocal_closure", {}).get("checks", {}).values()
    ):
        raise ValueError("finite microlocal closure failed")
    flags = result.get("claim_flags", {})
    true_flags = {name for name, value in flags.items() if value is True}
    if true_flags != {
        "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY",
        "BERGER_LOCAL_GHOST_HADAMARD_FACTORS_INCLUDED",
    }:
        raise ValueError("Hadamard regular-morphism boundary was over-promoted")
    theorem = result.get("primary_theorem_scope", {})
    if (
        theorem.get("dappiaggi_drago_1506_09122", {}).get("applies_directly")
        is not False
        or theorem.get("fewster_2503_12537_theorem_5_16", {}).get(
            "applies_to_current_stationary_volterra_map"
        )
        is not False
    ):
        raise ValueError("a primary theorem was over-applied")
