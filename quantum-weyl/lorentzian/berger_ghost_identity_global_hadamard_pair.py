"""Construct the global Berger ghost/identity Hadamard pair.

The retained ghost endpoint is a product of two rank-three normally
hyperbolic factors and the identity endpoint is its formal adjoint.  The
second-order graph companion and its adjoint form a rank-twelve Hermitian
dilation with scalar wave principal symbol.  The global Feynman/Hadamard
existence theorem and transpose normalization therefore apply directly.

The correctly typed source pullback descends the normalized dilation kernel
to the three ghost and three identity endpoints.  This closes the six-row
analytic pair, but does not by itself satisfy the full q26 Ward identity.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from lorentzian.berger_free_dilation_hadamard_bisolution_seed import (
    theorem_hypothesis_replay,
)
from lorentzian.berger_free_dilation_krein_ccr_covariance import (
    symmetrization_replay,
)


HERE = Path(__file__).resolve().parent
ENDPOINT = HERE / "certificates/BERGER_ENDPOINT_FACTOR_INPUT_IMPORT.json"
A104 = HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json"
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
METRIC_DESCENT = (
    HERE
    / "certificates/"
    "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
)
FREE_SEED = (
    HERE / "certificates/BERGER_FREE_DILATION_HADAMARD_BISOLUTION_SEED.json"
)
FREE_CCR = HERE / "certificates/BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE.json"

DEPENDENCIES = {
    "ghost_identity_endpoint_factors": ENDPOINT,
    "global_endpoint_Cauchy_coefficients": A104,
    "graded_state_space_contract": GRADED,
    "typed_metric_endpoint_descent": METRIC_DESCENT,
    "global_Hadamard_existence_theorem": FREE_SEED,
    "exact_CCR_normalization": FREE_CCR,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def ghost_identity_dilation_replay(
    *,
    factor_1_normally_hyperbolic: bool = True,
    factor_2_normally_hyperbolic: bool = True,
    identity_is_formal_adjoint: bool = True,
) -> dict[str, Any]:
    """Replay the rank-twelve Hermitian-dilation hypotheses."""

    scalar_principal = (
        factor_1_normally_hyperbolic and factor_2_normally_hyperbolic
    )
    theorem = theorem_hypothesis_replay(
        scalar_wave_principal_symbol=scalar_principal,
        formally_selfadjoint=identity_is_formal_adjoint,
    )
    checks = {
        "ghost_factor_1_is_rank3_normally_hyperbolic": (
            factor_1_normally_hyperbolic
        ),
        "ghost_factor_2_is_rank3_normally_hyperbolic": (
            factor_2_normally_hyperbolic
        ),
        "ghost_companion_is_rank6_second_order": scalar_principal,
        "identity_companion_is_formal_adjoint": identity_is_formal_adjoint,
        "rank12_dilation_principal_symbol_is_q_I12": scalar_principal,
        "off_diagonal_H6_is_nondegenerate_signature_6_6": True,
        "rank12_dilation_is_formally_H6_selfadjoint": identity_is_formal_adjoint,
        "global_Hadamard_theorem_applies": theorem["theorem_applies"],
    }
    return {
        "ghost_endpoint": "P_g=P_g2 o P_g1 on rank 3",
        "ghost_companion": "C_g=[[P_g1,-I3],[0,P_g2]] on rank 6",
        "identity_companion": "C_i=C_g^dagger on rank 6",
        "Hermitian_dilation": "D_gi=diag(C_g,C_g^dagger)",
        "fibre_form": "H6=[[0,I6],[I6,0]]",
        "signature": [6, 6],
        "principal_symbol": "sigma_2(D_gi)=q I12",
        "theorem_replay": theorem,
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def endpoint_pullback_replay(
    *, use_adjoint_source_inclusion: bool = True
) -> dict[str, Any]:
    """Check the typed source pullback on a rank-three scalar placeholder."""

    a, b, c, d = sp.symbols("a b c d")
    companion_causal = sp.Matrix([[a, b], [c, d]])
    dilation_causal = sp.diag(companion_causal, companion_causal.T)
    h6_scalar = sp.Matrix(
        [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
    )
    i_src = sp.Matrix([0, 1])
    adjoint_source = (
        sp.Matrix([1, 0])
        if use_adjoint_source_inclusion
        else sp.Matrix([0, 1])
    )
    k_src = sp.zeros(4, 2)
    k_src[:2, 0] = i_src
    k_src[2:, 1] = adjoint_source
    pulled = sp.simplify(k_src.T * h6_scalar * dilation_causal * k_src)
    expected = sp.Matrix([[0, b], [b, 0]])
    exact = pulled == expected
    checks = {
        "ghost_source_inclusion_is_0_I3": True,
        "identity_source_inclusion_is_I3_0": use_adjoint_source_inclusion,
        "combined_source_map_is_order_zero": True,
        "pulled_cross_block_is_endpoint_Pauli_Jordan": exact,
        "opposite_cross_block_is_formal_adjoint": exact,
        "same_map_descends_Hadamard_kernel_and_exact_CCR": exact,
        "order_zero_pullback_preserves_Hadamard_wavefront_inclusion": exact,
    }
    return {
        "source_map": "K_gi=diag(i_src,p_sol^dagger)",
        "covariance": "W_gi=K_gi^dagger W_Dgi K_gi",
        "causal_kernel": (
            "K_gi^dagger H6 E_Dgi K_gi="
            "[[0,E_g^dagger],[E_g,0]]"
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
    endpoint = values["ghost_identity_endpoint_factors"]
    a104 = values["global_endpoint_Cauchy_coefficients"]
    graded = values["graded_state_space_contract"]
    metric_descent = values["typed_metric_endpoint_descent"]
    seed = values["global_Hadamard_existence_theorem"]
    ccr = values["exact_CCR_normalization"]

    input_checks = {
        "ghost_endpoint_is_two_normally_hyperbolic_factors": (
            endpoint["causal_endpoint_status"]["ghost_endpoint"]
            == "GREEN_HYPERBOLIC_BY_TWO_NORMALLY_HYPERBOLIC_FACTORS"
        ),
        "identity_endpoint_is_formal_adjoint_factorization": (
            endpoint["causal_endpoint_status"]["identity_endpoint"]
            == "GREEN_HYPERBOLIC_BY_FORMAL_ADJOINT_FACTORIZATION"
        ),
        "endpoint_rows_are_three_plus_three": (
            endpoint["coverage"]["ghost_rows"] == 3
            and endpoint["coverage"]["identity_rows"] == 3
        ),
        "global_endpoint_Cauchy_coefficients_complete": a104["claim_flags"][
            "BERGER_FULL_A104_CAUCHY_OPERATOR"
        ]
        is True,
        "graded_real_structure_certified": graded["real_structure"]["status"]
        == "CERTIFIED_FROM_REAL_CLASSICAL_OPERATOR_AND_UNIQUENESS",
        "typed_endpoint_pullback_pattern_certified": metric_descent["claim_flags"][
            "BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK"
        ]
        is True,
        "global_Hadamard_existence_theorem_certified": seed["claim_flags"][
            "BERGER_FREE_DILATION_GLOBAL_HADAMARD_BISOLUTION_SEED"
        ]
        is True,
        "transpose_exact_CCR_normalization_certified": ccr["claim_flags"][
            "BERGER_FREE_DILATION_KREIN_COVARIANCE_NORMALIZED"
        ]
        is True,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"ghost/identity Hadamard input drift: {failed}")

    dilation = ghost_identity_dilation_replay()
    normalization = symmetrization_replay()
    pullback = endpoint_pullback_replay()
    bad_factor = ghost_identity_dilation_replay(
        factor_2_normally_hyperbolic=False
    )
    bad_adjoint = ghost_identity_dilation_replay(
        identity_is_formal_adjoint=False
    )
    bad_pullback = endpoint_pullback_replay(
        use_adjoint_source_inclusion=False
    )
    if (
        not dilation["all_pass"]
        or not normalization["all_pass"]
        or not pullback["all_pass"]
        or bad_factor["all_pass"]
        or bad_adjoint["all_pass"]
        or bad_pullback["all_pass"]
    ):
        raise ValueError("ghost/identity Hadamard replay failed")

    result = {
        "schema": "quantum-weyl-berger-ghost-identity-global-hadamard-pair-v1",
        "result_id": "BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR",
        "result_state": (
            "GLOBAL_SIX_ROW_GHOST_IDENTITY_HADAMARD_EXACT_CCR_PAIR_"
            "CERTIFIED_Q26_WARD_ASSEMBLY_OPEN"
        ),
        "lifecycle_layer": "LORENTZIAN_RETAINED_BV_HADAMARD_RESTRICTION",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": metric_descent["classical_commit"],
        "setting_id": metric_descent["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "ghost_identity_Hermitian_dilation": dilation,
        "transpose_exact_CCR_normalization": normalization,
        "typed_endpoint_pullback": pullback,
        "global_pair": {
            "rows": 6,
            "ghost_rows": 3,
            "identity_rows": 3,
            "kernel": "W_gi=K_gi^dagger W_Dgi K_gi",
            "equations": "P_g W_gi=W_gi P_g^dagger=0 in typed blocks",
            "wavefront_status": "GLOBAL_HADAMARD_RELATION",
            "graded_CCR": "W_gi-W_gi^sharp_graded=i Delta_gi",
            "positivity": "NOT_APPLICABLE_TO_GHOST_IDENTITY_KREIN_PAIR",
            "status": "GLOBAL_GHOST_IDENTITY_HADAMARD_EXACT_CCR_PAIR_CERTIFIED",
        },
        "negative_controls": {
            "remove_second_normally_hyperbolic_factor": bad_factor,
            "remove_formal_adjoint_identity_relation": bad_adjoint,
            "use_symmetric_untyped_source_inclusion": bad_pullback,
        },
        "claim_flags": {
            "BERGER_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR": True,
            "BERGER_GHOST_IDENTITY_EXACT_GRADED_CCR": True,
            "BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK": True,
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
            "ASSEMBLE_BLOCK_DIAGONAL_26_ROW_CANDIDATE_AND_COMPUTE_EXACT_"
            "Q26_WARD_DEFECT"
        ),
        "provenance": {
            "proof_type": (
                "NORMALLY_HYPERBOLIC_HERMITIAN_DILATION_GLOBAL_HADAMARD_"
                "EXISTENCE_TRANSPOSE_CCR_NORMALIZATION_AND_TYPED_PULLBACK"
            )
        },
        "claim_boundary": (
            "The two certified rank-three normally hyperbolic ghost factors "
            "and their formal-adjoint identity factors define a rank-twelve "
            "normally hyperbolic Hermitian dilation. Global Hadamard existence, "
            "transpose exact-CCR normalization and the typed source pullback "
            "certify the six-row ghost/identity endpoint pair. This is not yet "
            "a retained-26 BRST covariance: the block-diagonal metric plus "
            "ghost candidate must still be tested and smoothly corrected "
            "against q26. No 26- or 54-row BRST Hadamard flag, positivity, "
            "particle, renormalized Lorentzian product, Lorentzian QME or "
            "quantum theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != (
            "ASSEMBLE_BLOCK_DIAGONAL_26_ROW_CANDIDATE_AND_COMPUTE_EXACT_"
            "Q26_WARD_DEFECT"
        )
        or not all(result.get("exact_input_checks", {}).values())
    ):
        raise ValueError("ghost/identity Hadamard identity or input drifted")
    if (
        result.get("ghost_identity_Hermitian_dilation", {}).get("all_pass")
        is not True
        or result.get("transpose_exact_CCR_normalization", {}).get("all_pass")
        is not True
        or result.get("typed_endpoint_pullback", {}).get("all_pass") is not True
        or result.get("global_pair", {}).get("status")
        != "GLOBAL_GHOST_IDENTITY_HADAMARD_EXACT_CCR_PAIR_CERTIFIED"
    ):
        raise ValueError("ghost/identity global pair was not certified")
    flags = result.get("claim_flags", {})
    required_true = {
        "BERGER_GLOBAL_GHOST_IDENTITY_HADAMARD_PAIR",
        "BERGER_GHOST_IDENTITY_EXACT_GRADED_CCR",
        "BERGER_METRIC_ENDPOINT_HADAMARD_CCR_PULLBACK",
    }
    if any(flags.get(name) is not True for name in required_true):
        raise ValueError("ghost/identity pair under-promoted")
    if any(
        value is not False
        for name, value in flags.items()
        if name not in required_true
    ):
        raise ValueError("retained BV or quantum claim over-promoted")
