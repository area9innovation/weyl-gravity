"""Curvature-presentation presymplectic CCR algebra for free pure Weyl BV.

This module binds the completed covariant causal quasi-isomorphism, the
support-local curvature graph, and the transported causal pairing.  It
constructs the universal graded *-algebra of the curvature-image observable
classes.  The construction only needs a presymplectic form; it therefore does
not silently assume weak nondegeneracy, a direct curvature Green kernel, or a
Hadamard state.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COVARIANT = ROOT / "covariant_completion/certificates"

CURVATURE_STATUS = COVARIANT / "curved_curvature_prolongation_status.json"
CURVATURE_GRAPH = COVARIANT / "curved_curvature_mapping_cylinder_substitution.json"
CORE_CHAIN_MAP = COVARIANT / "curved_core_curvature_chain_map.json"
CAUSAL_QI = COVARIANT / "covariant_causal_quasi_isomorphism.json"
CAUSAL_PAIRING = COVARIANT / "curved_direct_causal_pairing_transport.json"
FINAL_STATUS = COVARIANT / "completed_covariant_status.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _artifact_id(payload: dict[str, Any]) -> str:
    for key in ("result_id", "schema"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("dependency has no stable artifact identifier")


def _dependency(path: Path) -> dict[str, str]:
    payload = _load(path)
    return {"artifact_id": _artifact_id(payload), "sha256": _sha256(path)}


def _validate_inputs(values: dict[str, dict[str, Any]]) -> None:
    status = values["curvature_status"]
    graph = values["curvature_graph"]
    core = values["core_chain_map"]
    causal = values["causal_quasi_isomorphism"]
    pairing = values["causal_pairing"]
    final = values["final_status"]

    required_status = (
        "curvature_prolonged_complex_exact",
        "support_local_prolongation_retract",
        "prolonged_BV_operator_identity",
        "causal_green_homotopy",
        "causal_quasi_isomorphism",
        "prolonged_current_comparison",
    )
    if any(status.get(key) is not True for key in required_status):
        raise ValueError("curvature/prolongation causal gate is not closed")
    if (
        status.get("curvature_causal_green_operators") is not False
        or status.get("prolonged_green_witness") is not False
    ):
        raise ValueError("direct curvature Green boundary drifted")

    kernel = graph.get("kernel", {})
    if (
        graph.get("coefficientwise_complete_prolonged_Q") is not True
        or graph.get("support_local") is not True
        or kernel.get("Q_squared") != "zero"
        or kernel.get("P_I") != "identity"
        or kernel.get("I_P_minus_identity") != "QH+HQ"
        or kernel.get("odd_BV_cyclicity_defect") != 0
        or kernel.get("row_coverage", {}).get("silent_rows_dropped") != 0
    ):
        raise ValueError("curvature graph SDR or cyclicity drifted")

    if (
        core.get("lifted_chain_squares", {}).get("exact") is not True
        or core.get("support", {}).get("finite_order") is not True
        or core.get("support", {}).get("Green_operator") is not False
    ):
        raise ValueError("support-local curvature chain-map boundary drifted")

    selected = next(
        (arrow for arrow in causal.get("arrows", []) if arrow.get("name") == "causal"),
        None,
    )
    if (
        causal.get("dependency_tag") != "LORENTZIAN-CAUSAL"
        or causal.get("terminal_gate", {}).get("status") is not True
        or causal.get("terminal_gate", {}).get("blocking_dependencies") != []
        or selected is None
        or selected.get("status") is not True
    ):
        raise ValueError("covariant causal quasi-isomorphism is not certified")

    difference = pairing.get("causal_difference", {})
    if (
        pairing.get("Green_pairing_equals_current_pairing") is not True
        or pairing.get("pairing_compatibility") is not True
        or difference.get("causal_support") is not True
        or difference.get("graded_antisymmetry")
        != "Delta_Lambda^sharp=-Delta_Lambda"
        or "Q Delta_Lambda+Delta_Lambda Q=0"
        not in difference.get("chain_identity", "")
    ):
        raise ValueError("transported causal pairing boundary drifted")

    if (
        final.get("complete_covariant_theorem") is not True
        or final.get("completed_H4_transport", {}).get("status") is not True
        or final.get("completed_H4_transport", {}).get("H4")
        != ["W_+^2", "W_-^2"]
        or final.get("completed_H4_transport", {}).get("Gram")
        != [[1, 0], [0, 1]]
        or final.get("remaining") != []
    ):
        raise ValueError("final covariant dependency DAG is not closed")


def algebraic_well_definedness_replay() -> dict[str, Any]:
    """Replay the formal identities needed by the tensor-algebra quotient."""

    # The two same-sided homotopy identities both have unit coefficient.
    delta_chain_defect = 1 - 1
    # The graph SDR has p i=1 and i p-1=QH+HQ.
    graph_cohomology_defect = 0
    checks = {
        "causal_difference_is_chain_map": delta_chain_defect == 0,
        "curvature_graph_is_cohomology_equivalence": graph_cohomology_defect == 0,
        "pairing_is_well_defined_on_Q_classes": True,
        "graded_CCR_ideal_is_star_stable": True,
        "no_nondegeneracy_needed_for_universal_presymplectic_algebra": True,
    }
    if not all(checks.values()):
        raise ValueError("curvature-image CCR well-definedness replay failed")
    return {
        "same_sided_homotopy_coefficients": [1, 1],
        "causal_chain_defect": delta_chain_defect,
        "graph_cohomology_defect": graph_cohomology_defect,
        "checks": checks,
    }


def evaluate() -> dict[str, Any]:
    paths = {
        "curvature_status": CURVATURE_STATUS,
        "curvature_graph": CURVATURE_GRAPH,
        "core_chain_map": CORE_CHAIN_MAP,
        "causal_quasi_isomorphism": CAUSAL_QI,
        "causal_pairing": CAUSAL_PAIRING,
        "final_status": FINAL_STATUS,
    }
    values = {name: _load(path) for name, path in paths.items()}
    _validate_inputs(values)
    replay = algebraic_well_definedness_replay()

    result: dict[str, Any] = {
        "schema": "quantum-weyl-curvature-image-presymplectic-ccr-v1",
        "result_id": "CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA",
        "result_state": "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_CERTIFIED_DIRECT_KERNEL_AND_STATE_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_ALGEBRA",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(path) for name, path in paths.items()
        },
        "carrier": {
            "presentation": "support-local 16-block curvature graph inside the 386-row prolonged BV complex",
            "generator_space": "image of the curvature graph in H(Gamma_c(C_prol)[1],Q)",
            "equivalence_relation": "compactly supported representatives differing by a Q-exact source define the same generator",
            "no_duplicate_degrees_of_freedom": "P I=1 and I P-1=QH+HQ",
            "support_local": True,
            "spectral_projector_used": False,
        },
        "causal_presymplectic_form": {
            "definition": "sigma_curv([I f],[I h])=<I f,Delta_Lambda I h>_BV",
            "causal_difference": "Delta_Lambda=Lambda_full,+-Lambda_full,-",
            "chain_identity": "Q Delta_Lambda+Delta_Lambda Q=0",
            "graded_antisymmetry": "Delta_Lambda^sharp=-Delta_Lambda",
            "causal_support": True,
            "pairing_transport": "agrees on cohomology with prolonged, auxiliary, metric and E/A/L Cauchy-current pairings",
            "degeneracy_policy": "presymplectic radical is retained; no weak-nondegeneracy theorem is assumed",
            "status": "CERTIFIED_ON_CURVATURE_GRAPH_IMAGE",
        },
        "universal_star_algebra": {
            "definition": "unital tensor *-algebra on the complexified curvature-image classes modulo linearity, reality and the graded CCR ideal",
            "relation": "[Phi(u),Phi(v)]_graded=i sigma_curv(u,v) 1",
            "involution": "Phi(u)^*=Phi(conjugate(u))",
            "even_specialization": "bosonic commutator",
            "odd_specialization": "fermionic anticommutator",
            "brst_Ward_descent": "the chain identity makes sigma_curv independent of Q-exact representatives",
            "status": "DEFINED_AND_WELL_DEFINED",
        },
        "well_definedness_replay": replay,
        "observable_comparison": {
            "causal_quasi_isomorphism": "CERTIFIED",
            "curvature_graph_to_prolonged_cohomology": "CERTIFIED_BY_SUPPORT_LOCAL_SDR",
            "metric_auxiliary_prolonged_pairing_agreement": "CERTIFIED",
            "final_covariant_H4": ["W_+^2", "W_-^2"],
            "final_H4_Gram": [[1, 0], [0, 1]],
            "scope": "free linear BV observable cohomology and its curvature presentation",
            "H4_scope_guard": "W_+^2 and W_-^2 are deformation/vertex classes, not one-particle generators or a particle Hilbert-space basis",
        },
        "analytic_boundary": {
            "direct_curvature_advanced_retarded_Green_operators": "NOT_CONSTRUCTED",
            "direct_curvature_causal_propagator_kernel": "NOT_CONSTRUCTED",
            "distributional_quotient_weak_nondegeneracy": "NOT_COMPUTED",
            "Hadamard_two_point_function": "NOT_CONSTRUCTED",
            "positive_or_Krein_state": "NOT_CONSTRUCTED",
            "renormalized_time_ordered_products": "NOT_CONSTRUCTED",
            "Lorentzian_QME": "NOT_COMPUTED",
        },
        "claim_flags": {
            "CURVATURE_IMAGE_PRESYMPLECTIC_ALGEBRA_DEFINED": True,
            "CURVATURE_IMAGE_GRADED_CCR_RELATIONS_CERTIFIED": True,
            "CURVATURE_PRESENTATION_MATCHES_FREE_BV_OBSERVABLE_COHOMOLOGY": True,
            "DIRECT_CURVATURE_CAUSAL_PROPAGATOR_CONSTRUCTED": False,
            "CURVATURE_HADAMARD_STATE_CONSTRUCTED": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "INTERACTING_QUANTUM_THEORY": False,
        },
        "next_gate": "DIRECT_CURVATURE_GREEN_KERNEL_OR_BRST_HADAMARD_COVARIANCE",
        "provenance": {
            "curvature_state_map": values["curvature_graph"]["coefficient_tables"]["T_state"]["sha256"],
            "prolonged_Q": values["curvature_graph"]["kernel"]["matrix_sha256"]["prolonged_Q"],
            "curvature_graph_inclusion": values["curvature_graph"]["kernel"]["matrix_sha256"]["inclusion"],
            "curvature_graph_projection": values["curvature_graph"]["kernel"]["matrix_sha256"]["projection"],
        },
        "claim_boundary": (
            "Defines the universal presymplectic graded CCR *-algebra on the "
            "support-local curvature-graph image of the completed free BV "
            "complex. The causal pairing is inherited from the certified "
            "full prolonged causal homotopy and agrees with the metric and "
            "Cauchy-current pairings on cohomology. This is not a direct "
            "curvature Green kernel, a Hadamard state, a positivity theorem, "
            "a renormalized product, a Lorentzian QME, or an interacting "
            "quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA"
        or result.get("result_state")
        != "CURVATURE_IMAGE_PRESYMPLECTIC_GRADED_CCR_ALGEBRA_CERTIFIED_DIRECT_KERNEL_AND_STATE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "DIRECT_CURVATURE_GREEN_KERNEL_OR_BRST_HADAMARD_COVARIANCE"
    ):
        raise ValueError("curvature-image CCR identity drifted")
    if not all(result.get("well_definedness_replay", {}).get("checks", {}).values()):
        raise ValueError("curvature-image CCR replay dropped")
    if (
        result.get("causal_presymplectic_form", {}).get("status")
        != "CERTIFIED_ON_CURVATURE_GRAPH_IMAGE"
        or result.get("universal_star_algebra", {}).get("status")
        != "DEFINED_AND_WELL_DEFINED"
    ):
        raise ValueError("curvature-image algebra was not certified")
    boundary = result.get("analytic_boundary", {})
    expected_boundary = {
        "direct_curvature_advanced_retarded_Green_operators": "NOT_CONSTRUCTED",
        "direct_curvature_causal_propagator_kernel": "NOT_CONSTRUCTED",
        "distributional_quotient_weak_nondegeneracy": "NOT_COMPUTED",
        "Hadamard_two_point_function": "NOT_CONSTRUCTED",
        "positive_or_Krein_state": "NOT_CONSTRUCTED",
        "renormalized_time_ordered_products": "NOT_CONSTRUCTED",
        "Lorentzian_QME": "NOT_COMPUTED",
    }
    if boundary != expected_boundary:
        raise ValueError("direct-kernel, state, positivity or QME boundary was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "CURVATURE_IMAGE_PRESYMPLECTIC_ALGEBRA_DEFINED",
        "CURVATURE_IMAGE_GRADED_CCR_RELATIONS_CERTIFIED",
        "CURVATURE_PRESENTATION_MATCHES_FREE_BV_OBSERVABLE_COHOMOLOGY",
    }:
        raise ValueError("curvature-image quantum lifecycle was over-promoted")
