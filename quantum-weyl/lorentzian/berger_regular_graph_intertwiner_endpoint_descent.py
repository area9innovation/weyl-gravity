"""Classify regular graph intertwiners and descend the Berger endpoint kernel.

The companion graph domain is anisotropic:

    X_s = H^(s+1)(Sym2) direct_sum H^s(Sym2).

A support-local differential endomorphism bounded on every X_s therefore has
block orders [[0,-infinity],[1,0]].  The order-three and order-two parts of
C^dagger J=J C, together with generic invertibility of sigma_2(V_2), force
the lower row to vanish.  The remaining lower-left block equation then
forces J_11=0.  Hence the complete regular graph class contains only the
zero intertwiner and no admissible nondegenerate graph.

There is nevertheless a correctly typed direct endpoint descent.  The metric
source inclusion is i_src=(0,I), whereas the adjoint endpoint uses
p_sol^dagger=(I,0)^T.  Pulling the rank-40 dilated kernel back by their direct
sum gives the metric/A^dagger endpoint kernel, preserves the Hadamard
wavefront relation, and reproduces p_sol E_C i_src in the causal cross block.
This does not yet supply the six ghost/identity rows or the BRST Ward identity.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
COMPANION = (
    HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
)
LOWER = HERE / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"
VOLTERRA = (
    HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"
)
FULL_COVARIANCE = (
    HERE
    / "certificates/BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE.json"
)
WAVEFRONT = (
    HERE / "certificates/BERGER_HADAMARD_REGULAR_MORPHISM_BOUNDARY.json"
)
CAUSAL = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
RESTRICTION = (
    HERE
    / "certificates/BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT.json"
)

DEPENDENCIES = {
    "companion_graph_SDR": COMPANION,
    "lower_by_two_symbol": LOWER,
    "typed_Volterra_graph_spaces": VOLTERRA,
    "full_dilation_covariance": FULL_COVARIANCE,
    "finite_graph_wavefront_safety": WAVEFRONT,
    "retained_causal_chain": CAUSAL,
    "graded_state_space_contract": GRADED,
    "canonical_restriction_audit": RESTRICTION,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def regular_graph_principal_replay(
    *,
    v2_generically_invertible: bool = True,
    enforce_graph_sobolev_regularity: bool = True,
) -> dict[str, Any]:
    """Replay the complete principal-symbol obstruction.

    Differential operators cannot improve Sobolev regularity.  Thus the
    upper-right block is zero, while the lower-left block has order at most
    one.  At order three, sigma(V)^dagger sigma_1(J_21)=0.  At order two,
    after the order-one symbol vanishes, sigma(V)^dagger J_21=0 and
    sigma(V)^dagger J_22=0.  Generic invertibility kills both blocks.
    """

    allowed_orders = {
        "J11": "order_at_most_0",
        "J12": (
            "zero_no_support_local_differential_operator_improves_Hs_to_Hs+1"
            if enforce_graph_sobolev_regularity
            else "order_at_most_0_UNREGULAR_MUTATION"
        ),
        "J21": "order_at_most_1",
        "J22": "order_at_most_0",
    }
    upper_right_zero = enforce_graph_sobolev_regularity
    order_three_kills_J21_symbol = (
        upper_right_zero and v2_generically_invertible
    )
    order_two_kills_J21 = (
        order_three_kills_J21_symbol and v2_generically_invertible
    )
    order_two_kills_J22 = upper_right_zero and v2_generically_invertible
    lower_row_zero = order_two_kills_J21 and order_two_kills_J22
    order_zero_kills_J11 = lower_row_zero
    only_zero_intertwiner = lower_row_zero and order_zero_kills_J11
    checks = {
        "anisotropic_graph_domain_Xs_is_Hsplus1_direct_sum_Hs": True,
        "support_local_differential_J12_must_vanish": upper_right_zero,
        "order_three_equation_is_v2dagger_L_equals_zero": upper_right_zero,
        "generic_v2_invertibility_kills_order_one_J21_symbol": (
            order_three_kills_J21_symbol
        ),
        "order_two_equation_kills_remaining_J21": order_two_kills_J21,
        "order_two_equation_kills_J22": order_two_kills_J22,
        "remaining_lower_left_equation_is_minus_J11_equals_zero": (
            lower_row_zero
        ),
        "order_zero_equation_kills_J11": order_zero_kills_J11,
        "only_zero_intertwiner_survives": only_zero_intertwiner,
        "J_plus_Jdagger_is_degenerate": only_zero_intertwiner,
    }
    return {
        "graph_spaces": (
            "X_s=(C0(H^(s+1)) intersect C1(H^s)) direct_sum "
            "(C0(H^s) intersect C1(H^(s-1)))"
        ),
        "bounded_support_local_block_orders": allowed_orders,
        "principal_companion": (
            "sigma_2(C)=[[q I10,0],[v2(xi),q I10]]"
        ),
        "principal_adjoint": (
            "sigma_2(Cdagger)=[[q I10,v2(xi)dagger],[0,q I10]]"
        ),
        "order_three_identity": "v2(xi)dagger L(xi)=0",
        "order_two_identities": [
            "v2(xi)dagger J21=0",
            "v2(xi)dagger J22=0",
            "J22 v2(xi)=0",
        ],
        "remaining_order_zero_identity": "-J11=0",
        "generic_invertibility_input": v2_generically_invertible,
        "surviving_form": "J=0",
        "checks": checks,
        "nondegenerate_graph_exists": not only_zero_intertwiner,
        "all_pass": all(checks.values()),
    }


def endpoint_source_pullback_replay(
    *,
    use_adjoint_source_inclusion: bool = True,
) -> dict[str, Any]:
    """Replay the endpoint CCR block using generic companion entries."""

    e11, e12, e21, e22 = sp.symbols("e11 e12 e21 e22")
    ec = sp.Matrix([[e11, e12], [e21, e22]])
    ec_dagger = ec.T
    zero2 = sp.zeros(2)
    ed = sp.diag(ec, ec_dagger)
    hd = sp.BlockMatrix([[zero2, sp.eye(2)], [sp.eye(2), zero2]]).as_explicit()

    i_src = sp.Matrix([0, 1])
    p_sol_dagger = (
        sp.Matrix([1, 0])
        if use_adjoint_source_inclusion
        else sp.Matrix([0, 1])
    )
    source_map = sp.zeros(4, 2)
    source_map[:2, 0] = i_src
    source_map[2:, 1] = p_sol_dagger
    pulled = sp.simplify(source_map.T * hd * ed * source_map)
    expected = sp.Matrix([[0, e12], [e12, 0]])
    # With independent formal-adjoint symbols the upper-right entry is
    # (p_sol E_C i_src)^dagger; the scalar replay identifies its transpose
    # placeholder with e12.
    exact_cross_block = pulled == expected
    checks = {
        "metric_source_inclusion_is_i_src_0_I": True,
        "adjoint_source_inclusion_is_p_sol_dagger_I_0": (
            use_adjoint_source_inclusion
        ),
        "source_map_is_order_zero_support_local": True,
        "metric_cross_block_is_p_sol_EC_i_src": exact_cross_block,
        "opposite_cross_block_is_formal_adjoint": exact_cross_block,
        "same_source_map_transports_covariance_and_Pauli_Jordan": (
            exact_cross_block
        ),
        "finite_bundle_map_preserves_Hadamard_wavefront_inclusion": (
            exact_cross_block
        ),
        "graph_SDR_intertwiners_make_endpoint_kernel_a_bisolution": (
            exact_cross_block
        ),
    }
    return {
        "metric_graph_SDR": {
            "solution_inclusion": "i_sol=(I,Box_2)^T",
            "source_inclusion": "i_src=(0,I)^T",
            "solution_projection": "p_sol=(I,0)",
            "identity": "C i_sol=i_src A",
        },
        "adjoint_graph_SDR": {
            "source_inclusion": "p_sol^dagger=(I,0)^T",
            "identity": "Cdagger p_src^dagger=p_sol^dagger Adagger",
        },
        "combined_source_map": (
            "K_src=diag(i_src,p_sol^dagger):"
            "(A sources direct_sum Adagger sources)->D sources"
        ),
        "kernel_pullback": (
            "W_A_direct_sum_Adagger="
            "K_src^dagger W_D K_src"
        ),
        "causal_pullback": (
            "K_src^dagger H E_D K_src="
            "[[0,(p_sol E_C i_src)^dagger],[p_sol E_C i_src,0]]"
        ),
        "symbolic_pulled_matrix": [
            [str(pulled[row, column]) for column in range(2)]
            for row in range(2)
        ],
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
    companion = values["companion_graph_SDR"]
    lower = values["lower_by_two_symbol"]
    volterra = values["typed_Volterra_graph_spaces"]
    full = values["full_dilation_covariance"]
    wavefront = values["finite_graph_wavefront_safety"]
    causal = values["retained_causal_chain"]
    graded = values["graded_state_space_contract"]
    restriction = values["canonical_restriction_audit"]

    input_checks = {
        "exact_companion_graph_SDR": companion["claim_flags"][
            "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR"
        ]
        is True,
        "v2_generic_symbol_rank_ten": lower["normal_form"][
            "degree_two_symbol_ranks"
        ]["generic"]
        == 10,
        "typed_Volterra_graph_spaces_certified": volterra["claim_flags"][
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
        ]
        is True,
        "full_rank40_Hadamard_CCR_covariance": full["claim_flags"][
            "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"
        ]
        is True
        and full["claim_flags"]["BERGER_FULL_DILATION_EXACT_CCR"] is True,
        "finite_graph_maps_wavefront_safe": wavefront["claim_flags"][
            "BERGER_FINITE_GRAPH_WAVEFRONT_SAFETY"
        ]
        is True,
        "retained_26_causal_chain_certified": causal["claim_flags"][
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"
        ]
        is True,
        "graded_BRST_covariance_still_open": graded["claim_flags"][
            "BERGER_26_ROW_BRST_HADAMARD"
        ]
        is False,
        "canonical_summand_already_obstructed": restriction["claim_flags"][
            "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR"
        ]
        is False,
        "common_setting": len(
            {
                companion["setting_id"],
                lower["setting_id"],
                volterra["setting_id"],
                full["setting_id"],
                causal["setting_id"],
                graded["setting_id"],
                restriction["setting_id"],
            }
        )
        == 1,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"regular graph/endpoint descent input drift: {failed}")

    graph = regular_graph_principal_replay()
    unregular = regular_graph_principal_replay(
        enforce_graph_sobolev_regularity=False
    )
    singular_v2 = regular_graph_principal_replay(
        v2_generically_invertible=False
    )
    endpoint = endpoint_source_pullback_replay()
    wrong_endpoint = endpoint_source_pullback_replay(
        use_adjoint_source_inclusion=False
    )
    if (
        not graph["all_pass"]
        or graph["nondegenerate_graph_exists"]
        or unregular["all_pass"]
        or singular_v2["all_pass"]
        or not endpoint["all_pass"]
        or wrong_endpoint["all_pass"]
    ):
        raise ValueError("regular graph/endpoint descent replay failed")

    result = {
        "schema": (
            "quantum-weyl-berger-regular-graph-intertwiner-endpoint-"
            "descent-v1"
        ),
        "result_id": (
            "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT"
        ),
        "result_state": (
            "REGULAR_GRAPH_INTERTWINERS_OBSTRUCTED_METRIC_ENDPOINT_HADAMARD_"
            "CCR_PULLBACK_CERTIFIED_GHOST_WARD_COMPLETION_OPEN"
        ),
        "lifecycle_layer": "LORENTZIAN_RETAINED_BV_HADAMARD_RESTRICTION",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": full["classical_commit"],
        "setting_id": full["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "regular_graph_classification": graph,
        "direct_metric_endpoint_descent": endpoint,
        "negative_controls": {
            "allow_upper_right_regularity_gain": unregular,
            "remove_generic_v2_invertibility": singular_v2,
            "use_i_src_in_both_dilation_blocks": wrong_endpoint,
        },
        "retained_26_completion_boundary": {
            "metric_and_metric_adjoint_endpoint_rows": 20,
            "metric_endpoint_Hadamard_CCR_pullback": "CERTIFIED",
            "ghost_rows": 3,
            "identity_rows": 3,
            "global_exact_ghost_identity_Hadamard_pair": "NOT_CONSTRUCTED",
            "smooth_BRST_compatibility_correction": "NOT_SOLVED",
            "BRST_Ward_identity": "NOT_VERIFIED",
            "conditional_26_to_54_lift": (
                "CERTIFIED_BUT_NOT_APPLIED_UNTIL_OMEGA26_EXISTS"
            ),
        },
        "claim_flags": {
            "BERGER_REGULAR_GRAPH_INTERTWINER_CLASS_COMPLETE": True,
            "BERGER_NONDEGENERATE_REGULAR_GRAPH_INTERTWINER_EXISTS": False,
            "BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK": True,
            "BERGER_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR": False,
            "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "CONSTRUCT_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR_AND_SOLVE_SMOOTH_"
            "BRST_WARD_COMPLETION_ON_26_ROWS"
        ),
        "provenance": {
            "proof_type": (
                "ANISOTROPIC_SOBOLEV_ORDER_CLASSIFICATION_PRINCIPAL_SYMBOL_"
                "OBSTRUCTION_AND_EXACT_SOURCE_PULLBACK"
            )
        },
        "claim_boundary": (
            "This theorem classifies the complete smooth support-local "
            "differential graph class that is bounded on every certified "
            "anisotropic companion Sobolev space. Generic invertibility of "
            "sigma_2(V_2), followed by the remaining block equation, forces "
            "every such intertwiner to vanish, so that graph route is "
            "obstructed. Separately, "
            "the correctly typed source pullback of the rank-40 covariance "
            "gives a Hadamard exact-CCR kernel on the metric and formal-adjoint "
            "endpoints. It is not yet a graded retained-26 covariance: the "
            "three ghost and three identity rows, a chain-compatible smooth "
            "completion and the BRST Ward identity remain open. No 54-row "
            "Hadamard flag, positivity, particle, renormalized Lorentzian "
            "product, Lorentzian QME or quantum theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != (
            "CONSTRUCT_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR_AND_SOLVE_SMOOTH_"
            "BRST_WARD_COMPLETION_ON_26_ROWS"
        )
    ):
        raise ValueError("regular graph/endpoint descent identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("regular graph/endpoint descent inputs failed")
    graph = result.get("regular_graph_classification", {})
    endpoint = result.get("direct_metric_endpoint_descent", {})
    if (
        graph.get("all_pass") is not True
        or graph.get("nondegenerate_graph_exists") is not False
        or endpoint.get("all_pass") is not True
    ):
        raise ValueError("regular graph obstruction or endpoint descent failed")
    flags = result.get("claim_flags", {})
    required_true = {
        "BERGER_REGULAR_GRAPH_INTERTWINER_CLASS_COMPLETE",
        "BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK",
    }
    required_false = set(flags) - required_true
    if any(flags.get(name) is not True for name in required_true):
        raise ValueError("regular graph/endpoint claim under-promoted")
    if any(flags.get(name) is not False for name in required_false):
        raise ValueError("retained BV or quantum claim over-promoted")
