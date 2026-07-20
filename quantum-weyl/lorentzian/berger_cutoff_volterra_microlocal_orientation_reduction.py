"""Reduce cutoff orientation to one microlocal Volterra convergence gate.

Every finite term in the same-sided cutoff Volterra series is a composition
of normally-hyperbolic Green kernels and local differential kernels.  On a
compact time slab, the standard properly-supported wavefront calculus keeps
those terms in the same oriented canonical relation.  The existing factorial
estimate proves Sobolev operator-norm convergence, but not convergence in a
fixed Hörmander distribution space.  This module certifies the finite-term
induction and records that stronger convergence as the single sufficient
gate for the infinite kernel.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TYPED = HERE / "certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json"
CUTOFF = HERE / "certificates/BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY.json"
MICROLOCAL = (
    HERE
    / "certificates/BERGER_CUTOFF_COMPANION_MICROLOCAL_RESPONSE_PREFLIGHT.json"
)
DILATION = (
    HERE / "certificates/BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION.json"
)
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
STATIONARY = (
    HERE / "certificates/BERGER_COMPANION_STATIONARY_DECOMPOSABILITY.json"
)

DEPENDENCIES = {
    "typed_Volterra_import": TYPED,
    "cutoff_Green_family": CUTOFF,
    "cutoff_microlocal_preflight": MICROLOCAL,
    "cutoff_Hermitian_dilation": DILATION,
    "base_wave_parametrix": BASE,
    "stationary_full_companion_decomposability": STATIONARY,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _compose(left: frozenset[str], right: frozenset[str]) -> frozenset[str]:
    """Exact abstract relation calculus for one null time orientation."""

    result: set[str] = set()
    for first in left:
        for second in right:
            if first == "DELTA":
                result.add(second)
            elif second == "DELTA":
                result.add(first)
            elif first == second and first in {"R_PLUS", "R_MINUS"}:
                result.add(first)
            else:
                result.add("MIXED_DIRECTION")
    return frozenset(result)


def finite_term_orientation_replay(
    *, sign: str = "PLUS", sample_order: int = 8
) -> dict[str, Any]:
    """Replay the arbitrary-order relation induction and finite samples."""

    if sign not in {"PLUS", "MINUS"}:
        raise ValueError("sign must be PLUS or MINUS")
    ray = f"R_{sign}"
    gamma = frozenset({"DELTA", ray})
    local = frozenset({"DELTA"})
    base_blocks = {
        "G1": gamma,
        "G2": gamma,
        "G2_V_G1": _compose(_compose(gamma, local), gamma),
        "N": local,
    }
    g0 = frozenset().union(
        base_blocks["G1"], base_blocks["G2"], base_blocks["G2_V_G1"]
    )
    sampled: list[dict[str, Any]] = []
    term = g0
    for order in range(sample_order + 1):
        sampled.append(
            {
                "order": order,
                "term": f"(-1)^{order}(G0_{sign} N)^{order}G0_{sign}",
                "relation": sorted(term),
                "contained_in_Gamma": term <= gamma,
            }
        )
        term = _compose(_compose(term, local), g0)
    induction = {
        "base_G0_in_Gamma": g0 <= gamma,
        "local_N_in_Delta": local == frozenset({"DELTA"}),
        "Gamma_comp_Delta_comp_Gamma_in_Gamma": _compose(
            _compose(gamma, local), gamma
        )
        <= gamma,
        "all_sampled_terms_in_Gamma": all(
            row["contained_in_Gamma"] for row in sampled
        ),
    }
    return {
        "sign": sign,
        "Gamma": sorted(gamma),
        "base_block_relations": {
            name: sorted(relation) for name, relation in base_blocks.items()
        },
        "series_formula": f"G_C,{sign}=sum_(n>=0)(-1)^n(G0_{sign}N)^nG0_{sign}",
        "sampled_terms": sampled,
        "induction": induction,
        "arbitrary_order_conclusion": all(induction.values()),
    }


def mixed_side_negative_control() -> dict[str, Any]:
    plus = frozenset({"DELTA", "R_PLUS"})
    minus = frozenset({"DELTA", "R_MINUS"})
    mixed = _compose(plus, minus)
    return {
        "composition": "Gamma_PLUS composed with Gamma_MINUS",
        "relation": sorted(mixed),
        "contains_mixed_direction": "MIXED_DIRECTION" in mixed,
        "contained_in_one_oriented_Gamma": mixed <= plus or mixed <= minus,
    }


def convergence_gate_replay(
    *,
    hormander_normal_convergence: bool = False,
    sobolev_operator_convergence: bool = True,
) -> dict[str, Any]:
    """Record exactly which infinite-series implication is authorized."""

    conditions = {
        "finite_partial_sums_have_uniform_declared_wavefront_cone": True,
        "partial_sums_converge_in_Dprime_Gamma_normal_topology": (
            hormander_normal_convergence
        ),
        "formal_transpose_series_has_same_opposite_side_control": (
            hormander_normal_convergence
        ),
    }
    sufficient_gate = all(conditions.values())
    conclusions = {
        "infinite_Green_kernels_oriented": sufficient_gate,
        "cutoff_Pauli_Jordan_decomposable": sufficient_gate,
        "dilated_cutoff_RFHGHO_decomposable": sufficient_gate,
        "regular_Cauchy_morphism_cone_action": sufficient_gate,
    }
    return {
        "existing_convergence": {
            "finite_slab_all_Sobolev_operator_norm": sobolev_operator_convergence,
            "implies_Hormander_normal_convergence": False,
        },
        "required_sufficient_statement": (
            "On every compact time slab and for each advanced/retarded sign, "
            "the Volterra partial-sum kernels and their formal transposes "
            "converge in the normal topology of D'_Gamma, with "
            "Gamma=Delta union R_sign."
        ),
        "conditions": conditions,
        "gate_passes": sufficient_gate,
        "conditional_conclusions": conclusions,
    }


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    typed = values["typed_Volterra_import"]
    cutoff = values["cutoff_Green_family"]
    microlocal = values["cutoff_microlocal_preflight"]
    dilation = values["cutoff_Hermitian_dilation"]
    base = values["base_wave_parametrix"]
    stationary = values["stationary_full_companion_decomposability"]

    input_checks = {
        "typed_Volterra_factorial_convergence_imported": typed["claim_flags"][
            "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED"
        ]
        is True,
        "cutoff_two_sided_causal_Green_family": cutoff["claim_flags"][
            "BERGER_TEMPORAL_CUTOFF_COMPANION_GREEN_FAMILY"
        ]
        is True,
        "cutoff_factorwise_null_bound": microlocal["claim_flags"][
            "BERGER_CUTOFF_COMPANION_FACTORWISE_NULL_WAVEFRONT_BOUND"
        ]
        is True,
        "cutoff_orientation_not_previously_certified": microlocal["claim_flags"][
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION"
        ]
        is False,
        "regular_dilated_Cauchy_legs": dilation["claim_flags"][
            "BERGER_DILATED_FREE_CUTOFF_REGULAR_CAUCHY_MORPHISM"
        ]
        is True
        and dilation["claim_flags"][
            "BERGER_DILATED_CUTOFF_FULL_REGULAR_CAUCHY_MORPHISM"
        ]
        is True,
        "base_factor_normally_hyperbolic": base["operator_family"][
            "principal_symbol"
        ]
        == "g^{-1}(xi,xi) times the fibre identity",
        "stationary_full_companion_decomposable": stationary["claim_flags"][
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
        ]
        is True,
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"microlocal Volterra reduction input drift: {failed}")

    plus = finite_term_orientation_replay(sign="PLUS")
    minus = finite_term_orientation_replay(sign="MINUS")
    mixed = mixed_side_negative_control()
    open_gate = convergence_gate_replay()
    hypothetical_gate = convergence_gate_replay(hormander_normal_convergence=True)
    sobolev_missing = convergence_gate_replay(
        hormander_normal_convergence=False, sobolev_operator_convergence=False
    )
    if (
        not plus["arbitrary_order_conclusion"]
        or not minus["arbitrary_order_conclusion"]
        or not mixed["contains_mixed_direction"]
        or mixed["contained_in_one_oriented_Gamma"]
        or open_gate["gate_passes"]
        or not hypothetical_gate["gate_passes"]
        or sobolev_missing["gate_passes"]
    ):
        raise ValueError("microlocal Volterra reduction replay failed")

    result = {
        "schema": "quantum-weyl-berger-cutoff-volterra-microlocal-orientation-reduction-v1",
        "result_id": "BERGER_CUTOFF_VOLTERRA_MICROLOCAL_ORIENTATION_REDUCTION",
        "result_state": "FINITE_VOLTERRA_TERMS_ORIENTED_SINGLE_HORMANDER_CONVERGENCE_GATE_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_REDUCTION",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": cutoff["classical_commit"],
        "setting_id": cutoff["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "finite_term_orientation": {
            "advanced_or_retarded_convention": (
                "The labels PLUS/MINUS denote the two same-sided Green families; "
                "the certificate does not rename the repository advanced/retarded convention."
            ),
            "proper_support": (
                "All compositions are restricted to a compact time slab; causal "
                "support and the local differential insertions give the properness "
                "required for kernel composition."
            ),
            "local_differential_relation": "WF'(K_D) subset Delta for D in {V_chi,N}",
            "normally_hyperbolic_relation": (
                "WF'(G_P,sign) subset Gamma_sign=Delta union R_sign"
            ),
            "plus": plus,
            "minus": minus,
            "status": "ALL_FINITE_SAME_SIDED_VOLTERRA_TERMS_ORIENTED",
        },
        "negative_control": mixed,
        "infinite_series_gate": {
            **open_gate,
            "status": "OPEN_NOT_SUPPLIED_BY_ALL_SOBOLEV_FACTORIAL_BOUNDS",
            "conditional_replay": hypothetical_gate,
            "missing_Sobolev_control_replay": sobolev_missing,
        },
        "conditional_transport_chain": [
            "Dprime_Gamma convergence -> WF'(G_chi,+/-) subset Delta union R_+/-",
            "oriented G_chi,+/- -> E_chi is N_plus/N_minus decomposable",
            "direct-sum adjoint dilation preserves decomposability",
            "finite differential time-slice commutators preserve cone orientation",
            "the two regular Cauchy GreenHyp morphisms satisfy the Fewster 5.16 cone action",
            "a separately supplied free Hadamard covariance can then be transported",
        ],
        "literature_provenance": {
            "source": "Christopher J. Fewster, Hadamard States for Decomposable Green-Hyperbolic Operators, arXiv:2503.12537",
            "normally_hyperbolic_wavefront_relation": "Equation (5.7) and Theorem 5.3",
            "decomposability_definition": "Definition 5.2",
            "regular_morphism_transport": "Theorem 5.16",
            "distribution_topology": (
                "Hörmander spaces D'_Gamma with their normal topology; this "
                "strengthens the currently certified Sobolev operator convergence."
            ),
        },
        "claim_flags": {
            "BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED": True,
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED": True,
            "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_CERTIFIED": False,
            "BERGER_CUTOFF_COMPANION_PAULI_JORDAN_ORIENTATION_EXCLUSION": False,
            "BERGER_CUTOFF_COMPANION_NULL_CONE_DECOMPOSABLE": False,
            "BERGER_DILATED_RESPONSE_MORPHISM_CONE_MAPPING": False,
            "BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "PROVE_COMPACT_SLAB_VOLTERRA_CONVERGENCE_IN_DPRIME_GAMMA_NORMAL_TOPOLOGY_THEN_CONSTRUCT_FREE_SEED_COVARIANCE",
        "provenance": {
            "typed_result_id": typed["result_id"],
            "cutoff_result_id": cutoff["result_id"],
            "microlocal_result_id": microlocal["result_id"],
            "dilation_result_id": dilation["result_id"],
        },
        "claim_boundary": (
            "Certifies the oriented wavefront relation of every finite same-sided "
            "Volterra term and reduces the infinite cutoff orientation and regular-"
            "morphism cone action to one sufficient compact-slab convergence statement "
            "in a fixed Hörmander distribution space. The required convergence is not "
            "proved by the existing all-Sobolev factorial estimate. This result does "
            "not certify the infinite-series orientation, cutoff decomposability, cone "
            "mapping, a free seed covariance, restriction to the full graded BV "
            "carrier, BRST Ward identities, a Hadamard state, positivity, a Lorentzian "
            "QME, or a quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_CUTOFF_VOLTERRA_MICROLOCAL_ORIENTATION_REDUCTION"
        or result.get("result_state")
        != "FINITE_VOLTERRA_TERMS_ORIENTED_SINGLE_HORMANDER_CONVERGENCE_GATE_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "PROVE_COMPACT_SLAB_VOLTERRA_CONVERGENCE_IN_DPRIME_GAMMA_NORMAL_TOPOLOGY_THEN_CONSTRUCT_FREE_SEED_COVARIANCE"
    ):
        raise ValueError("microlocal Volterra reduction identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("microlocal Volterra reduction inputs failed")
    finite = result.get("finite_term_orientation", {})
    if (
        finite.get("status") != "ALL_FINITE_SAME_SIDED_VOLTERRA_TERMS_ORIENTED"
        or finite.get("plus", {}).get("arbitrary_order_conclusion") is not True
        or finite.get("minus", {}).get("arbitrary_order_conclusion") is not True
    ):
        raise ValueError("finite Volterra orientation was not certified")
    gate = result.get("infinite_series_gate", {})
    if (
        gate.get("gate_passes") is not False
        or gate.get("status") != "OPEN_NOT_SUPPLIED_BY_ALL_SOBOLEV_FACTORIAL_BOUNDS"
        or gate.get("conditional_replay", {}).get("gate_passes") is not True
        or any(gate.get("conditional_conclusions", {}).values())
    ):
        raise ValueError("infinite Volterra orientation was over-promoted")
    true_flags = {
        name for name, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_FINITE_VOLTERRA_TERMS_MICROLOCALLY_ORIENTED",
        "BERGER_HORMANDER_VOLTERRA_CONVERGENCE_GATE_ISOLATED",
    }:
        raise ValueError("Hadamard or infinite-series claim over-promoted")
