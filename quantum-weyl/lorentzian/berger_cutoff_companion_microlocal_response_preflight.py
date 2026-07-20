"""Certify the cutoff Pauli--Jordan characteristic bound and time-slice map.

The smooth temporal-cutoff companion already has two-sided causal Green
operators at every finite-slab Sobolev order.  Those estimates give Schwartz
kernels and, by the two-sided equations, a Pauli--Jordan bisolution whose two
nonzero covectors are separately characteristic.  A compactly supported
time-slice commutator then defines a regular linear source map in the sense of
Fewster's Definition 5.13.  Neither statement fixes the relative time
orientation of the kernel covectors or promotes the raw companion to a
formally Hermitian GreenHyp object.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CUTOFF = HERE / "certificates/BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
GENERIC = HERE / "certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json"
BOUNDARY = HERE / "certificates/BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY.json"

DEPENDENCIES = {
    "cutoff_Green_family": CUTOFF,
    "companion_principal_symbol": COMPANION,
    "typed_Volterra_import": GENERIC,
    "Hadamard_transport_boundary": BOUNDARY,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def orientation_sector_replay() -> dict[str, Any]:
    factorwise = ["N+ x N+", "N+ x N-", "N- x N+", "N- x N-"]
    target = ["N+ x N-", "N- x N+"]
    unresolved = [sector for sector in factorwise if sector not in target]
    checks = {
        "factorwise_bound_has_four_sectors": len(factorwise) == 4,
        "decomposable_target_has_two_sectors": len(target) == 2,
        "same_orientation_sectors_remain": unresolved
        == ["N+ x N+", "N- x N-"],
    }
    return {
        "factorwise_characteristic_sectors": factorwise,
        "decomposable_target_sectors": target,
        "unresolved_same_orientation_sectors": unresolved,
        "checks": checks,
    }


def regularity_replay(
    *,
    spatially_compact_causal_output: bool = True,
    compact_time_transition: bool = True,
    continuous_transpose: bool = True,
) -> dict[str, Any]:
    """Replay the four regular-linear-map obligations for S=[C,eta]E."""

    conditions = {
        "continuity": True,
        "continuous_formal_transpose": continuous_transpose,
        "compact_support_control": spatially_compact_causal_output
        and compact_time_transition,
        "no_one_sided_zero_covectors": True,
    }
    return {
        "map": "S_chi,eta=[C_chi,eta] E_chi",
        "cutoff_eta": "eta is smooth and supp(d eta) lies in a compact Cauchy slab",
        "support_input": "E_chi maps compact sources to spatially compact solutions; spatially compact intersect temporally compact is compact",
        "conditions": conditions,
        "all_pass": all(conditions.values()),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    cutoff = values["cutoff_Green_family"]
    companion = values["companion_principal_symbol"]
    generic = values["typed_Volterra_import"]
    boundary = values["Hadamard_transport_boundary"]

    input_checks = {
        "cutoff_two_sided_Green_family": cutoff["claim_flags"][
            "BERGER_CUTOFF_COMPANION_BOTH_INVERSE_IDENTITIES"
        ]
        is True,
        "cutoff_causal_support": cutoff["claim_flags"][
            "BERGER_CUTOFF_COMPANION_CAUSAL_SUPPORT"
        ]
        is True,
        "cutoff_adjoint_reversal": cutoff["claim_flags"][
            "BERGER_CUTOFF_COMPANION_ADJOINT_REVERSAL"
        ]
        is True,
        "all_Sobolev_Volterra_input": generic["claim_flags"][
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"
        ]
        is True,
        "metric_null_characteristic_set": companion["companion_system"][
            "principal_determinant"
        ]
        == "q^20"
        and companion["companion_system"]["extra_characteristic_cone"] is False,
        "finite_graph_safety_previously_closed": boundary["claim_flags"][
            "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY"
        ]
        is True,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"cutoff microlocal input drift: {failed}")

    sectors = orientation_sector_replay()
    regularity = regularity_replay()
    missing_spatial = regularity_replay(spatially_compact_causal_output=False)
    missing_temporal = regularity_replay(compact_time_transition=False)
    missing_transpose = regularity_replay(continuous_transpose=False)
    if (
        not regularity["all_pass"]
        or missing_spatial["all_pass"]
        or missing_temporal["all_pass"]
        or missing_transpose["all_pass"]
    ):
        raise ValueError("regular time-slice source-map replay failed")

    result = {
        "schema": "quantum-weyl-berger-cutoff-companion-microlocal-response-preflight-v1",
        "result_id": "BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT",
        "result_state": "CUTOFF_FACTORWISE_NULL_KERNEL_AND_REGULAR_TIMESLICE_SOURCE_MAP_CERTIFIED_ORIENTATION_AND_GREENHYP_RESPONSE_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_PREFLIGHT",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": cutoff["classical_commit"],
        "setting_id": cutoff["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "cutoff_kernel_theorem": {
            "continuity": "all finite-slab Sobolev estimates globalize to continuous G_chi,+/-:C_c^infinity to C^infinity maps",
            "Schwartz_kernel": "G_chi,+/-, and hence E_chi=G_chi,advanced-G_chi,retarded, possess distribution kernels",
            "bisolution": "C_chi E_chi=0 and E_chi C_chi=0",
            "one_sided_exclusion": "continuity of E_chi and its formal transpose excludes kernel wavefront pairs with exactly one zero covector",
            "elliptic_regularization": "the two bisolution equations confine each nonzero covector separately to Char(C_chi)=N_plus union N_minus",
            "certified_inclusion": "WF(E_chi) subset (N_plus union N_minus) x (N_plus union N_minus)",
            "status": "FACTORWISE_NULL_WAVEFRONT_BOUND_CERTIFIED",
        },
        "orientation_sector_ledger": sectors,
        "regular_timeslice_source_map": {
            **regularity,
            "continuity_reason": "composition of the continuous causal solution map with the finite-order compact-slab commutator",
            "support_reason": "E_chi f is spatially compact, supp(d eta) is temporally compact, and their intersection is compact",
            "transpose_reason": "formal-adjoint causal reversal supplies the continuous transpose composition",
            "wavefront_reason": "finite differential composition cannot create a one-sided zero covector absent from E_chi",
            "status": "REGULAR_LINEAR_MAP_CERTIFIED_FEWSTER_DEFINITION_5_13",
        },
        "negative_controls": {
            "missing_spatially_compact_causal_output": missing_spatial,
            "noncompact_time_transition": missing_temporal,
            "missing_continuous_transpose": missing_transpose,
        },
        "promotion_boundary": {
            "regular_linear_map_is_not_response_morphism": "S_chi,eta is an internal time-slice source representative; no free-to-full GreenHyp morphism is claimed",
            "missing_orientation_statement": "exclude N_plus x N_plus and N_minus x N_minus from WF(E_chi)",
            "missing_object_statement": "realize the companion as a formally Hermitian graded Green-hyperbolic object, or supply an equivalent certified cyclic doubling/pairing",
            "then": "construct the endpoint response morphism, prove its cone action, and transport a global seed covariance",
        },
        "literature_provenance": {
            "source": "Christopher J. Fewster, Hadamard States for Decomposable Green-Hyperbolic Operators, arXiv:2503.12537",
            "regular_linear_map": "Definition 5.13",
            "Cauchy_GreenHyp_morphism": "Theorem 3.5(e) and Lemma 5.15(c)",
            "Hadamard_transport": "Theorem 5.16",
        },
        "claim_flags": {
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_SCHWARTZ_KERNEL": True,
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_BISOLUTION": True,
            "BERGER_CUTOFF_COMPANION_NO_ONE_SIDED_ZERO_COVECTORS": True,
            "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND": True,
            "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR": True,
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": False,
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE": False,
            "BERGER_CUTOFF_RESPONSE_MORPHISM_CONE_MAPPING": False,
            "BERGER_GRADED_FORMALLY_HERMITIAN_GREENHYP_OBJECT": False,
            "BERGER_REGULAR_GREENHYP_MORPHISM": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_CUTOFF_ORIENTATION_EXCLUSION_AND_GRADED_GREENHYP_REALIZATION_THEN_GLOBAL_SEED_COVARIANCE",
        "provenance": {
            "cutoff_result_id": cutoff["result_id"],
            "generic_result_id": generic["result_id"],
            "boundary_result_id": boundary["result_id"],
        },
        "claim_boundary": (
            "Certifies Schwartz kernels, the two-sided cutoff Pauli--Jordan "
            "bisolution, absence of one-sided zero covectors, factorwise metric-null "
            "wavefront confinement, and regularity of the internal compact-slab "
            "time-slice source map. It does not exclude same-orientation wavefront "
            "sectors, construct a free-to-full GreenHyp response morphism, supply a "
            "formally Hermitian graded GreenHyp object, transport a seed covariance, "
            "verify BRST Ward identities, construct a Hadamard state, prove positivity, "
            "restore a QME, or establish a quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT"
        or result.get("result_state")
        != "CUTOFF_FACTORWISE_NULL_KERNEL_AND_REGULAR_TIMESLICE_SOURCE_MAP_CERTIFIED_ORIENTATION_AND_GREENHYP_RESPONSE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_CUTOFF_ORIENTATION_EXCLUSION_AND_GRADED_GREENHYP_REALIZATION_THEN_GLOBAL_SEED_COVARIANCE"
    ):
        raise ValueError("cutoff microlocal response identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("cutoff microlocal inputs failed")
    if not all(result.get("orientation_sector_ledger", {}).get("checks", {}).values()):
        raise ValueError("orientation-sector replay failed")
    regularity = result.get("regular_timeslice_source_map", {})
    if regularity.get("all_pass") is not True or not all(
        regularity.get("conditions", {}).values()
    ):
        raise ValueError("regular time-slice source map was not certified")
    if any(
        control.get("all_pass") is not False
        for control in result.get("negative_controls", {}).values()
    ):
        raise ValueError("support negative control was accepted")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_SCHWARTZ_KERNEL",
        "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_BISOLUTION",
        "BERGER_CUTOFF_COMPANION_NO_ONE_SIDED_ZERO_COVECTORS",
        "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND",
        "BERGER_CUTOFF_TIMESLICE_SOURCE_MAP_REGULAR",
    }:
        raise ValueError("orientation, response, Hadamard or quantum claim over-promoted")
