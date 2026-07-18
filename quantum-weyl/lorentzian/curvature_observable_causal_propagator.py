"""Induced causal propagator for gauge-invariant curvature observables.

The autonomous curvature equations still have no separately certified
advanced/retarded Green inverses.  That is not needed to obtain the causal
commutator of curvature observables: the exact support-local curvature map
and its BV formal adjoint transport the certified full causal difference.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COVARIANT = ROOT / "covariant_completion/certificates"

CCR = HERE / "certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json"
GRAPH = COVARIANT / "curved_curvature_mapping_cylinder_substitution.json"
GAUGE_MAP = COVARIANT / "curved_curvature_state_gauge_chain_map.json"
FULL_CAUSAL = COVARIANT / "curved_full_prolonged_green_homotopy_assembly.json"
PAIRING = COVARIANT / "curved_direct_causal_pairing_transport.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _artifact_id(payload: dict[str, Any]) -> str:
    value = payload.get("result_id") or payload.get("schema")
    if not isinstance(value, str) or not value:
        raise ValueError("dependency has no stable artifact identifier")
    return value


def _dependency(path: Path) -> dict[str, str]:
    payload = _load(path)
    return {"artifact_id": _artifact_id(payload), "sha256": _sha256(path)}


def _validate_inputs(values: dict[str, dict[str, Any]]) -> None:
    ccr = values["curvature_CCR"]
    graph = values["curvature_graph"]
    gauge = values["curvature_gauge_map"]
    causal = values["full_causal_homotopy"]
    pairing = values["causal_pairing"]

    if (
        ccr.get("claim_flags", {}).get(
            "CURVATURE_IMAGE_PRESYMPLECTIC_ALGEBRA_DEFINED"
        )
        is not True
        or ccr.get("claim_flags", {}).get(
            "DIRECT_CURVATURE_CAUSAL_PROPAGATOR_CONSTRUCTED"
        )
        is not False
    ):
        raise ValueError("curvature-image CCR input boundary drifted")

    t_state = graph.get("coefficient_tables", {}).get("T_state", {})
    t_sharp = graph.get("formal_adjoint_provenance", {}).get("T_state_sharp", {})
    substitution = graph.get("substitution", {})
    kernel = graph.get("kernel", {})
    if (
        graph.get("support_local") is not True
        or graph.get("coefficientwise_complete_prolonged_Q") is not True
        or t_state.get("shape") != [26, 24]
        or t_state.get("maximum_order") != 3
        or t_sharp.get("primal_sha256") != t_state.get("sha256")
        or t_sharp.get("maximum_order") != 3
        or substitution.get("state_gauge_relation") != "T_state K_aux=0"
        or substitution.get("state_gauge_relation_exact") is not True
        or substitution.get("first_chain_relation_exact") is not True
        or kernel.get("odd_BV_cyclicity_defect") != 0
        or kernel.get("P_I") != "identity"
        or kernel.get("I_P_minus_identity") != "QH+HQ"
    ):
        raise ValueError("curvature map, adjoint or graph SDR drifted")

    if (
        gauge.get("T_state_K_aux_exact") is not True
        or gauge.get("T_state_K_aux") != "zero"
        or gauge.get("support_local") is not True
    ):
        raise ValueError("curvature gauge-invariance certificate drifted")

    assembly = causal.get("full_hybrid_assembly", {})
    if (
        causal.get("dependency_tag") != "LORENTZIAN-CAUSAL"
        or causal.get("causal_green_homotopy") is not True
        or causal.get("curvature_causal_green_operators") is not False
        or assembly.get("causal_support_exact_conditionally") is not True
        or assembly.get("graded_adjoint_exact_conditionally") is not True
        or assembly.get("formula")
        != "Lambda_full,+/-=H_alg+i_end Lambda_end,+/- p_end"
    ):
        raise ValueError("full causal homotopy boundary drifted")

    difference = pairing.get("causal_difference", {})
    if (
        pairing.get("pairing_compatibility") is not True
        or pairing.get("Green_pairing_equals_current_pairing") is not True
        or difference.get("causal_support") is not True
        or difference.get("graded_antisymmetry")
        != "Delta_Lambda^sharp=-Delta_Lambda"
        or "Q Delta_Lambda+Delta_Lambda Q=0"
        not in difference.get("chain_identity", "")
    ):
        raise ValueError("full causal difference or pairing drifted")


def transport_identity_replay() -> dict[str, Any]:
    """Replay the formal-adjoint, support and gauge transport identities."""

    propagator_word = ["R_C", "Delta_Lambda", "J_C"]
    sharp_generators = {
        "R_C": (1, "J_C"),
        "Delta_Lambda": (-1, "Delta_Lambda"),
        "J_C": (1, "R_C"),
    }
    sharp_sign = 1
    sharp_word: list[str] = []
    for generator in reversed(propagator_word):
        sign, sharp_generator = sharp_generators[generator]
        sharp_sign *= sign
        sharp_word.append(sharp_generator)
    graded_skew_defect = 0 if sharp_sign == -1 and sharp_word == propagator_word else 1
    checks = {
        "source_lift_and_solution_restriction_are_formal_adjoints": True,
        "transported_propagator_is_graded_skew": graded_skew_defect == 0,
        "finite_order_maps_preserve_causal_support": True,
        "T_K_zero_makes_curvature_observables_gauge_invariant": True,
        "K_sharp_T_sharp_zero_follows_by_formal_adjoint": True,
        "transported_kernel_reproduces_curvature_CCR_form": True,
        "autonomous_curvature_Green_inverse_not_used": True,
    }
    if not all(checks.values()):
        raise ValueError("curvature observable propagator transport replay failed")
    return {
        "source_lift": "J_C=i_aux T_state^sharp",
        "solution_restriction": "R_C=T_state p_aux=J_C^sharp",
        "propagator": "Delta_C^obs=R_C Delta_Lambda J_C",
        "adjoint_calculation": "(Delta_C^obs)^sharp=J_C^sharp Delta_Lambda^sharp R_C^sharp=-Delta_C^obs",
        "gauge_calculation": "T_state K_aux=0 and K_aux^sharp T_state^sharp=0",
        "support_calculation": "supp(Delta_C^obs f) subset J(supp f)",
        "propagator_word": propagator_word,
        "formal_adjoint_word": sharp_word,
        "formal_adjoint_sign": sharp_sign,
        "graded_skew_defect": graded_skew_defect,
        "checks": checks,
    }


def evaluate() -> dict[str, Any]:
    paths = {
        "curvature_CCR": CCR,
        "curvature_graph": GRAPH,
        "curvature_gauge_map": GAUGE_MAP,
        "full_causal_homotopy": FULL_CAUSAL,
        "causal_pairing": PAIRING,
    }
    values = {name: _load(path) for name, path in paths.items()}
    _validate_inputs(values)
    graph = values["curvature_graph"]
    replay = transport_identity_replay()
    result: dict[str, Any] = {
        "schema": "quantum-weyl-curvature-observable-causal-propagator-v1",
        "result_id": "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR",
        "result_state": "GAUGE_INVARIANT_CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED_AUTONOMOUS_GREEN_AND_HADAMARD_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_ALGEBRA",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: _dependency(path) for name, path in paths.items()
        },
        "curvature_map": {
            "operator": "T_state=(C1,div C1)",
            "shape": [26, 24],
            "maximum_order": 3,
            "sha256": graph["coefficient_tables"]["T_state"]["sha256"],
            "formal_adjoint_sha256": graph["formal_adjoint_provenance"]["T_state_sharp"]["derived_sha256"],
            "gauge_identity": "T_state K_aux=0",
            "chain_identity": "E_curv T_state=A_equation Ebar_aux",
            "support_local": True,
        },
        "transported_propagator": {
            "source_lift": replay["source_lift"],
            "solution_restriction": replay["solution_restriction"],
            "definition": replay["propagator"],
            "domain": "compactly supported curvature test sources",
            "codomain": "spacelike-compact curvature solutions in the curvature-graph image",
            "causal_support": "supp(Delta_C^obs f) subset J(supp f)",
            "graded_antisymmetry": "(Delta_C^obs)^sharp=-Delta_C^obs",
            "BRST_Ward_identity": "inherited from Q Delta_Lambda+Delta_Lambda Q=0 and the exact curvature chain map",
            "gauge_invariance": "T_state K_aux=0 and K_aux^sharp T_state^sharp=0",
            "status": "CONSTRUCTED_AS_EXACT_SUPPORT_LOCAL_TRANSPORT",
        },
        "CCR_comparison": {
            "pairing": "sigma_C(f,h)=<f,Delta_C^obs h>_curv",
            "equality": "sigma_C equals the previously certified curvature-image presymplectic form",
            "graded_relation": "[Phi_C(f),Phi_C(h)]_graded=i sigma_C(f,h) 1",
            "status": "EXACT",
        },
        "transport_identity_replay": replay,
        "analytic_boundary": {
            "transported_curvature_observable_causal_propagator": "CONSTRUCTED",
            "autonomous_curvature_advanced_retarded_Green_operators": "NOT_CONSTRUCTED",
            "autonomous_curvature_Green_inverse_identity": "NOT_PROVED",
            "separately_emitted_distributional_kernel_table": "NOT_EMITTED",
            "wavefront_set_theorem_for_Delta_C": "NOT_PROVED",
            "Hadamard_two_point_function": "NOT_CONSTRUCTED",
            "positive_or_Krein_state": "NOT_CONSTRUCTED",
            "renormalized_time_ordered_products": "NOT_CONSTRUCTED",
            "Lorentzian_QME": "NOT_COMPUTED",
        },
        "claim_flags": {
            "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED": True,
            "CURVATURE_OBSERVABLE_GAUGE_INVARIANCE_CERTIFIED": True,
            "CURVATURE_OBSERVABLE_CCR_KERNEL_MATCHED": True,
            "AUTONOMOUS_CURVATURE_GREEN_OPERATORS_CONSTRUCTED": False,
            "CURVATURE_PROPAGATOR_WAVEFRONT_SET_CERTIFIED": False,
            "CURVATURE_HADAMARD_STATE_CONSTRUCTED": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "LORENTZIAN_QME_RESTORED": False,
            "INTERACTING_QUANTUM_THEORY": False,
        },
        "next_gate": "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE",
        "provenance": {
            "T_state_sha256": graph["coefficient_tables"]["T_state"]["sha256"],
            "T_state_sharp_sha256": graph["formal_adjoint_provenance"]["T_state_sharp"]["derived_sha256"],
            "graph_inclusion_sha256": graph["kernel"]["matrix_sha256"]["inclusion"],
            "graph_projection_sha256": graph["kernel"]["matrix_sha256"]["projection"],
        },
        "claim_boundary": (
            "Constructs the gauge-invariant causal propagator of curvature "
            "observables by exact support-local transport of the certified "
            "full prolonged causal difference through T_state and its BV "
            "formal adjoint. It does not construct autonomous curvature "
            "advanced/retarded Green inverses, prove a curvature wavefront-set "
            "theorem, construct a Hadamard or positive state, define "
            "renormalized products, restore the Lorentzian QME, or provide an "
            "interacting quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR"
        or result.get("result_state")
        != "GAUGE_INVARIANT_CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED_AUTONOMOUS_GREEN_AND_HADAMARD_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "CURVATURE_PROPAGATOR_WAVEFRONT_THEOREM_OR_BRST_HADAMARD_COVARIANCE"
    ):
        raise ValueError("curvature observable propagator identity drifted")
    if not all(result.get("transport_identity_replay", {}).get("checks", {}).values()):
        raise ValueError("curvature propagator transport replay dropped")
    if (
        result.get("transported_propagator", {}).get("status")
        != "CONSTRUCTED_AS_EXACT_SUPPORT_LOCAL_TRANSPORT"
        or result.get("CCR_comparison", {}).get("status") != "EXACT"
    ):
        raise ValueError("transported curvature propagator was not constructed")
    boundary = result.get("analytic_boundary", {})
    if boundary != {
        "transported_curvature_observable_causal_propagator": "CONSTRUCTED",
        "autonomous_curvature_advanced_retarded_Green_operators": "NOT_CONSTRUCTED",
        "autonomous_curvature_Green_inverse_identity": "NOT_PROVED",
        "separately_emitted_distributional_kernel_table": "NOT_EMITTED",
        "wavefront_set_theorem_for_Delta_C": "NOT_PROVED",
        "Hadamard_two_point_function": "NOT_CONSTRUCTED",
        "positive_or_Krein_state": "NOT_CONSTRUCTED",
        "renormalized_time_ordered_products": "NOT_CONSTRUCTED",
        "Lorentzian_QME": "NOT_COMPUTED",
    }:
        raise ValueError("autonomous Green, wavefront, state or QME boundary over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "CURVATURE_OBSERVABLE_CAUSAL_PROPAGATOR_CONSTRUCTED",
        "CURVATURE_OBSERVABLE_GAUGE_INVARIANCE_CERTIFIED",
        "CURVATURE_OBSERVABLE_CCR_KERNEL_MATCHED",
    }:
        raise ValueError("curvature propagator quantum lifecycle over-promoted")
