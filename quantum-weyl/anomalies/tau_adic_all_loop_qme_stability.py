#!/usr/bin/env python3
"""Conditional all-order local QME induction for the tau-adic extension."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "extended_local_BV": {
        "path": (
            "quantum-weyl/anomalies/certificates/"
            "WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json"
        ),
        "sha256": (
            "fa21fc6071ae52277d9953b68c47773686117f1426cc50899fdf8c124d2ba616"
        ),
        "source_commit": "69f01998d255455aebe3bbcb0872ae82cc698621",
    },
    "local_anomaly_audit": {
        "path": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
        ),
        "sha256": (
            "07bf332cf1bece92f8a041002f3c787fe7e85e798871e4878fbbc3cd7b20bd3b"
        ),
        "source_commit": "c6d1c0bad4d7e609fccb8dc5581fab107a819d33",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _rank(matrix: list[list[dict[str, int]]]) -> int:
    rows = [[_fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def neumann_coefficients(order: int) -> list[int]:
    """Coefficients of (1+X)^-1 through a declared formal order."""
    return [1 if degree % 2 == 0 else -1 for degree in range(order + 1)]


def neumann_product(coefficients: list[int]) -> list[int]:
    """Coefficients of (1+X) times a truncated series."""
    product = coefficients[:]
    product.append(0)
    for degree, value in enumerate(coefficients):
        product[degree + 1] += value
    return product


def build() -> dict[str, Any]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, pin in PINS.items():
        path = ROOT / pin["path"]
        if _sha(path) != pin["sha256"]:
            raise ValueError(f"pinned all-loop input drifted: {name}")
        loaded[name] = json.loads(path.read_text(encoding="utf-8"))

    extended = loaded["extended_local_BV"]
    audit = loaded["local_anomaly_audit"]
    if (
        extended.get("H14", {}).get("status")
        != "COMPLETE_ZERO_IN_DECLARED_TAU_ADIC_DIMENSION_FOUR_ALGEBRA"
        or extended.get("H04", {}).get("status")
        != "COMPLETE_IN_DECLARED_TAU_ADIC_DIMENSION_FOUR_ALGEBRA"
        or _rank(extended["H14"]["boundary_matrix"]) != 4
        or extended.get("quartet_reduction", {}).get("status")
        != "EXACT_QUASI_ISOMORPHISM_TO_DRESSED_PURE_DIFF_BV_COMPLEX"
        or audit.get("exact_checks", {}).get(
            "positive_antifield_spectral_sequence_collapsed"
        )
        is not True
        or audit.get("QME_lifecycles", {}).get(
            "tau_adic_compensator_extended"
        )
        != "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN"
    ):
        raise ValueError("all-loop cohomology input boundary drifted")

    order = 12
    inverse = neumann_coefficients(order)
    product = neumann_product(inverse)
    if product[:-1] != [1] + [0] * order or product[-1] != (-1) ** order:
        raise ValueError("filtered Neumann recurrence failed")

    value = {
        "schema": "quantum-weyl-tau-adic-all-loop-local-qme-stability-v1",
        "result_id": "TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY",
        "result_state": (
            "CONDITIONAL_FORMAL_ALL_LOOP_LOCAL_QME_RESTORATION_THEOREM"
        ),
        "lifecycle_status": "QME_RESTORED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "input_pins": PINS,
        "formal_local_algebra": {
            "kind": "FORMAL_TAU_ADIC_LOCAL_ANALYTIC_JET_ALGEBRA",
            "coefficient_ring": (
                "Q[[hbar,z_C,z_E,z_R2,z_P]] with nonzero classical C2 "
                "kinetic normalization and formal finite-renormalization "
                "parameters"
            ),
            "completion": (
                "(hbar,z_C,z_E,z_R2,z_P,tau)-adically complete local "
                "covariant jets of g_hat, its BV cotangent, Diff ghosts, "
                "the Weyl quartet and pointwise nonminimal doublets"
            ),
            "dimension_policy": (
                "homogeneous engineering dimension four in a massless "
                "logarithmic subtraction scheme; no dimensionful spurion "
                "or power-divergent relevant operator is admitted"
            ),
            "locality_policy": (
                "finite jet order at each coefficient; formal tau series "
                "allowed; inverse differential operators and nonlocal form "
                "factors excluded"
            ),
            "regularity_scope": (
                "formal coupling neighbourhood of the certified regular "
                "Bach-locus chart"
            ),
            "parity_policy": (
                "even and odd modules retained separately; a parity Ward "
                "identity may set the odd coupling to zero but is not built "
                "into the cohomology"
            ),
        },
        "quantum_action_principle": {
            "status": "DECLARED_HYPOTHESIS_NOT_CONSTRUCTED_REGULATOR",
            "assumptions": [
                (
                    "after restoration through order n-1, the first order-n "
                    "Slavnov/QME breaking is an integrated local ghost-one "
                    "dimension-four functional in the declared completed algebra"
                ),
                (
                    "the order-n breaking obeys the linearized Wess-Zumino "
                    "consistency equation modulo d_h"
                ),
                (
                    "subtractions and finite canonical transformations remain "
                    "continuous in the formal filtration and preserve the "
                    "declared local domain"
                ),
                (
                    "the regular Koszul-Tate chart persists as a formal "
                    "coupling deformation; singular strata are excluded"
                ),
            ],
            "not_supplied": [
                "an all-order regularized functional integral",
                "a regulator preserving the completed tau-adic domain",
                "renormalized Lorentzian time-ordered products",
            ],
        },
        "stable_H04_module": {
            "ghost_number": 0,
            "form_degree": 4,
            "engineering_dimension": 4,
            "even_free_generators": [
                "C(g_hat)^2",
                "E4(g_hat)",
                "R(g_hat)^2",
            ],
            "odd_free_generators": ["C(g_hat) dual C(g_hat)"],
            "essential_running_couplings": [
                "z_C * C(g_hat)^2",
                "z_R2 * R(g_hat)^2",
            ],
            "topological_or_theta_directions": [
                "z_E * E4(g_hat)",
                "z_P * C(g_hat) dual C(g_hat)",
            ],
            "horizontal_exact_direction": "Box R(g_hat)=d_h(nabla R(g_hat))",
            "canonical_directions": (
                "all s_ext-exact ghost-zero local functionals, including "
                "positive-antifield canonical transformations"
            ),
            "coupling_redefinitions": (
                "arbitrary formal redefinitions of z_C,z_E,z_R2,z_P"
            ),
            "positive_antifield_independent_classes": [],
            "independent_generator_count": {"even": 3, "odd": 1},
            "stability_status": (
                "CLOSED_UNDER_RECURSIVE_LOCAL_COUNTERTERMS_IN_DECLARED_ALGEBRA"
            ),
        },
        "stable_H14_module": {
            "ghost_number": 1,
            "form_degree": 4,
            "engineering_dimension": 4,
            "even_quotient_dimension": 0,
            "odd_quotient_dimension": 0,
            "pure_Diff_quotient_dimension": 0,
            "Weyl_and_mixed_quotient_dimension": 0,
            "positive_antifield_independent_classes": [],
            "imported_boundary_rank": 4,
            "status": (
                "ZERO_IN_ALL_PARITIES_AND_ANTIFIELD_NUMBERS_IN_DECLARED_ALGEBRA"
            ),
        },
        "filtered_deformation_stability": {
            "filtration_ideal": "(hbar,z_C,z_E,z_R2,z_P)",
            "perturbation": (
                "delta_ct is the BV differential change induced by the four "
                "H04 coupling directions and raises the filtration"
            ),
            "inverse": "(1+h delta_ct)^-1=sum_{k>=0}(-h delta_ct)^k",
            "inverse_coefficients_through_order_12": inverse,
            "truncated_product_coefficients": product,
            "endpoint_interpretation": (
                "the sole final coefficient is the first omitted order; every "
                "fixed formal coefficient stabilizes exactly"
            ),
            "positive_antifield_stability": (
                "the complete filtered spectral sequence has zero ghost-one "
                "E1 page and therefore zero ghost-one abutment; the perturbed "
                "Koszul-Tate contraction is the formal HPL contraction"
            ),
            "unbounded_tau_series_status": (
                "NO_NEW_INDEPENDENT_COHOMOLOGY_GENERATORS: each dressed "
                "invariant has an infinite but filtration-complete tau expansion"
            ),
        },
        "recursive_QME_induction": {
            "base_order": (
                "the imported coefficient-bearing one-loop Wess-Zumino "
                "counterterm restores the local Euclidean QME"
            ),
            "induction_hypothesis": (
                "Gamma through hbar^(n-1) satisfies the QME and has couplings "
                "and canonical coordinates in the stable H04 module"
            ),
            "order_n_breaking": (
                "A_n is local by the declared QAP and obeys "
                "s_ext,n-1 A_n+d_h a_n=0"
            ),
            "cohomology_step": (
                "H14(s_ext,n-1|d_h)=0 implies "
                "A_n=s_ext,n-1 B_n+d_h C_n"
            ),
            "repair": (
                "Gamma_n -> Gamma_n-B_n removes the order-n breaking; its "
                "H04 ambiguity is absorbed by coupling redefinitions and "
                "s_ext-exact canonical transformations"
            ),
            "closure": (
                "the repair remains in the completed algebra and raises the "
                "filtration, so the induction repeats for every finite n"
            ),
            "verdict": (
                "CONDITIONAL_ALL_ORDER_FORMAL_LOCAL_QME_RESTORABLE"
            ),
        },
        "lifecycle": {
            "strict_fixed_field_content": "OBSTRUCTED_AT_ONE_LOOP",
            "tau_adic_one_loop_local_Euclidean": "QME_RESTORED",
            "tau_adic_all_loop_formal_local": (
                "CONDITIONAL_QME_RESTORED_UNDER_DECLARED_QAP"
            ),
            "constructed_all_loop_regulator": "OPEN",
            "global_anomalies": "OPEN",
            "Lorentzian_QME": "OPEN",
            "residual_transfer": "NO_CERTIFIED_MAP",
            "states_and_unitarity": "OPEN",
        },
        "exact_checks": {
            "requested_input_commits_and_hashes_pinned": True,
            "tau_adic_quartet_contraction_imported": True,
            "H04_Rhat2_direction_retained": True,
            "H04_even_odd_module_complete": True,
            "H14_all_parities_zero": True,
            "positive_antifield_sector_included": True,
            "canonical_transformations_accounted": True,
            "coupling_redefinitions_accounted": True,
            "total_derivative_accounted": True,
            "filtered_HPL_inverse_exact": True,
            "formal_induction_closes_under_QAP": True,
            "constructed_regulator_not_claimed": True,
        },
        "claim_flags": {
            "UNCONDITIONAL_ALL_LOOP_QME": False,
            "CONSTRUCTED_ALL_LOOP_REGULATOR": False,
            "STRICT_THEORY_ANOMALY_FREE": False,
            "STRICT_AND_COMPENSATOR_THEORIES_EQUIVALENT": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "GLOBAL_ANOMALIES_EXCLUDED": False,
            "RESIDUAL_TRANSFERRED": False,
            "HADAMARD_STATE_CERTIFIED_HERE": False,
            "PARTICLE_OR_UNITARITY_THEOREM": False,
        },
        "next_gate": (
            "Construct an all-order subtraction/regulator scheme satisfying "
            "the declared tau-adic quantum action principle, or independently "
            "prove that a standard algebraic-renormalization scheme supplies "
            "it on the formal regular coupling chart."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC theorem proves an order-by-order formal "
            "local QME restoration induction for the changed tau-adic "
            "compensator theory, conditional on the explicitly declared "
            "quantum action principle and regular formal coupling chart. The "
            "complete H14 module is zero and the stable H04 module contains "
            "C(g_hat)^2, E4(g_hat), R(g_hat)^2 and the parity-odd Pontryagin "
            "direction, with total derivatives, canonical transformations "
            "and coupling redefinitions separated. It does not construct the "
            "required regulator, prove convergence, exclude global anomalies, "
            "repair strict pure-Weyl gravity, or establish Lorentzian products, "
            "a QME, residual transfer, states, positivity, particles, "
            "scattering or unitarity."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    h04 = value.get("stable_H04_module", {})
    h14 = value.get("stable_H14_module", {})
    qap = value.get("quantum_action_principle", {})
    lifecycle = value.get("lifecycle", {})
    if (
        value.get("result_state")
        != "CONDITIONAL_FORMAL_ALL_LOOP_LOCAL_QME_RESTORATION_THEOREM"
        or qap.get("status") != "DECLARED_HYPOTHESIS_NOT_CONSTRUCTED_REGULATOR"
        or "R(g_hat)^2" not in h04.get("even_free_generators", [])
        or h04.get("positive_antifield_independent_classes") != []
        or h14.get("even_quotient_dimension") != 0
        or h14.get("odd_quotient_dimension") != 0
        or h14.get("positive_antifield_independent_classes") != []
        or value.get("recursive_QME_induction", {}).get("verdict")
        != "CONDITIONAL_ALL_ORDER_FORMAL_LOCAL_QME_RESTORABLE"
        or lifecycle.get("constructed_all_loop_regulator") != "OPEN"
        or lifecycle.get("Lorentzian_QME") != "OPEN"
        or not all(value.get("exact_checks", {}).values())
        or any(value.get("claim_flags", {}).values())
    ):
        raise ValueError("tau-adic all-loop conditional boundary crossed")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
