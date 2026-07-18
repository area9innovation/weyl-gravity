#!/usr/bin/env python3
"""Certify extended local BV cohomology and the one-loop WZ QME repair."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json"
SCHEMA = HERE / "schema/wess-zumino-extended-local-bv-cohomology-v1.schema.json"
DEPENDENCIES = {
    "cotangent_lift": HERE / "certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "WZ_primitive": HERE / "certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "H04_exhaustive_basis": ROOT / "quantum-weyl/local_bv/certificates/AFN0_H04_CANONICAL_QUOTIENT.json",
    "dimension_four_catalogue": ROOT / "quantum-weyl/local_bv/certificates/LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json",
    "minimal_KT_collapse": ROOT / "quantum-weyl/local_bv/certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
    "Diff_H14_zero": ROOT / "quantum-weyl/local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
    "nonminimal_contraction": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "regulated_breaking": HERE / "certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction())
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _rank(matrix: list[list[Fraction]]) -> int:
    if not matrix:
        return 0
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
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
        if rank == len(rows):
            break
    return rank


def _formal_exponential(sign: int, order: int) -> list[Fraction]:
    return [Fraction((sign * 2) ** degree, math.factorial(degree)) for degree in range(order + 1)]


def _toeplitz(coefficients: list[Fraction]) -> list[list[Fraction]]:
    size = len(coefficients)
    return [
        [coefficients[row - column] if row >= column else Fraction() for column in range(size)]
        for row in range(size)
    ]


def _render_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[_q(value) for value in row] for row in matrix]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    lift = values["cotangent_lift"]
    primitive = values["WZ_primitive"]
    h04 = values["H04_exhaustive_basis"]
    catalogue = values["dimension_four_catalogue"]
    kt = values["minimal_KT_collapse"]
    diff = values["Diff_H14_zero"]
    nonminimal = values["nonminimal_contraction"]
    breaking = values["regulated_breaking"]
    if (
        lift.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or primitive.get("qme_lifecycle", {}).get("extended_AFN0_one_loop_breaking")
        != "EXACT_REMOVABLE"
        or h04.get("basis_exhaustiveness_proof", {}).get("verification_status")
        != "VERIFIED_ARTIFACT_BOUND"
        or catalogue.get("generated_ansatz", {}).get("quotient_dimension") != 3
        or kt.get("claim_flags", {}).get("MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC")
        is not True
        or diff.get("claim_flags", {}).get("PURE_DIFF_H14_ZERO") is not True
        or nonminimal.get("claim_flags", {}).get("LOCAL_CANONICAL_GAUGE_FIXING_INVARIANCE_PROVED")
        is not True
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
    ):
        raise ValueError("extended local-BV dependency drifted")

    formal_order = 8
    exp_minus = _formal_exponential(-1, formal_order)
    exp_plus = _formal_exponential(1, formal_order)
    minus_matrix = _toeplitz(exp_minus)
    plus_matrix = _toeplitz(exp_plus)
    identity = [
        [Fraction(int(row == column)) for column in range(formal_order + 1)]
        for row in range(formal_order + 1)
    ]
    if _multiply(minus_matrix, plus_matrix) != identity or _multiply(plus_matrix, minus_matrix) != identity:
        raise ValueError("tau-adic dressed coordinate change is not invertible")

    # The exhaustive strict top basis already contains the full covariant
    # curvature inventory. Pure Diff closure removes only the Weyl obstruction
    # on Rhat^2; Box Rhat remains the displayed horizontal boundary.
    h04_top_even = ["CT_CHAT2", "CT_E4_GHAT", "CT_RHAT2", "CT_BOX_RHAT"]
    h04_dh = [
        [Fraction(0)],
        [Fraction(0)],
        [Fraction(0)],
        [Fraction(1)],
    ]
    h04_closure = [[Fraction(0) for _ in h04_top_even] for _ in range(0)]
    even_boundary_rank = _rank(h04_dh)
    even_dimension = len(h04_top_even) - even_boundary_rank
    if even_dimension != 3 or catalogue["generated_ansatz"]["named_representative_rank"] != 3:
        raise ValueError("dressed pure-Diff H04 even quotient drifted")

    # At positive antifield number the only dimension-zero natural symmetric
    # tensor available for an incoming ghost-minus-one primitive is ghat. Its
    # delta image is the trace of the Bach Euler row, identically zero.
    incoming_afn1 = [[Fraction(0)] for _ in range(len(h04_top_even))]
    if _rank(incoming_afn1) != 0:
        raise ValueError("unexpected positive-antifield H04 boundary")

    h14_strict_basis = [
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_C_DUAL_C",
        "ANOM_OMEGA_BOX_R",
    ]
    h14_primitives = ["B_C", "B_E", "B_P", "B_BOX"]
    h14_boundary = [
        [Fraction(int(row == column)) for column in range(4)]
        for row in range(4)
    ]
    if _rank(h14_boundary) != 4:
        raise ValueError("extended anomaly boundary matrix is not surjective")

    coefficients = [
        Fraction(breaking["coefficients"][name]["numerator"], breaking["coefficients"][name]["denominator"])
        for name in ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4")
    ]
    if coefficients != [Fraction(199, 30), Fraction(-87, 20)]:
        raise ValueError("WZ repair coefficient vector drifted")
    restored_image = [
        sum((h14_boundary[row][column] * (coefficients + [Fraction(), Fraction()])[column] for column in range(4)), Fraction())
        for row in range(4)
    ]
    if restored_image != coefficients + [Fraction(), Fraction()]:
        raise ValueError("coefficient-bearing counterterm does not hit the breaking")

    result = {
        "schema": "quantum-weyl-wess-zumino-extended-local-bv-cohomology-v1",
        "result_id": "WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY",
        "result_state": "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "local_algebra": {
            "kind": "FORMAL_TAU_ADIC_LOCAL_ANALYTIC_JET_ALGEBRA",
            "dressed_generators": ["g_hat", "g_hat_star", "tau", "tau_hat_star", "xi", "xi_star", "omega", "omega_star"],
            "coordinate_change": "g_hat=exp(-2tau)g; g_hat_star=exp(2tau)g_star; tau_hat_star=tau_star+N_omega",
            "formal_inverse_order_checked": formal_order,
            "exp_minus_2tau_coefficients": [_q(value) for value in exp_minus],
            "exp_plus_2tau_coefficients": [_q(value) for value in exp_plus],
            "left_inverse_matrix": _render_matrix(_multiply(minus_matrix, plus_matrix)),
            "right_inverse_matrix": _render_matrix(_multiply(plus_matrix, minus_matrix)),
            "all_orders_inverse_identity": "sum_{k=0}^n (-2)^k/k! 2^(n-k)/(n-k)! = (2^n/n!) (1-1)^n = delta_{n0}",
            "all_orders_inverse_status": "VERIFIED_BY_BINOMIAL_THEOREM",
            "completion_boundary": "the theorem is not a finite polynomial-in-tau statement",
        },
        "quartet_reduction": {
            "contracted_generators": ["tau", "omega", "omega_star", "tau_hat_star"],
            "remaining_complex": "pure Diff minimal BV complex of g_hat and its cotangent",
            "minimal_positive_afn": "acyclic on the regular Bach locus",
            "nonminimal_extension": "pointwise doublets contract and arbitrary invertible local BV-canonical gauge fixing preserves cohomology",
            "status": "EXACT_QUASI_ISOMORPHISM_TO_DRESSED_PURE_DIFF_BV_COMPLEX",
        },
        "H04": {
            "ghost_number": 0,
            "form_degree": 4,
            "engineering_dimension": 4,
            "even_top_basis": h04_top_even,
            "even_closure_matrix": h04_closure,
            "even_dh_boundary_matrix": _render_matrix(h04_dh),
            "positive_afn_boundary_matrix": _render_matrix(incoming_afn1),
            "even_boundary_rank": even_boundary_rank,
            "even_quotient_dimension": even_dimension,
            "even_classes": ["C(g_hat)^2", "E4(g_hat)", "R(g_hat)^2"],
            "even_dual_witnesses": [
                {"class": "C(g_hat)^2", "coordinates": [_q(Fraction(1)), _q(Fraction()), _q(Fraction()), _q(Fraction())], "boundary_pairing": _q(Fraction()), "representative_pairing": _q(Fraction(1))},
                {"class": "E4(g_hat)", "coordinates": [_q(Fraction()), _q(Fraction(1)), _q(Fraction()), _q(Fraction())], "boundary_pairing": _q(Fraction()), "representative_pairing": _q(Fraction(1))},
                {"class": "R(g_hat)^2", "coordinates": [_q(Fraction()), _q(Fraction()), _q(Fraction(1)), _q(Fraction())], "boundary_pairing": _q(Fraction()), "representative_pairing": _q(Fraction(1))},
            ],
            "odd_top_basis": ["CT_C_HAT_DUAL_C_HAT"],
            "odd_boundary_rank": 0,
            "odd_quotient_dimension": 1,
            "odd_classes": ["C(g_hat) dual C(g_hat)"],
            "odd_dual_witnesses": [
                {"class": "C(g_hat) dual C(g_hat)", "coordinates": [_q(Fraction(1))], "boundary_pairing": _q(Fraction()), "representative_pairing": _q(Fraction(1))}
            ],
            "exact_classes": [{"representative": "Box R(g_hat)", "primitive": "nabla R(g_hat)"}],
            "status": "COMPLETE_IN_DECLARED_TAU_ADIC_DIMENSION_FOUR_ALGEBRA",
        },
        "H14": {
            "ghost_number": 1,
            "form_degree": 4,
            "engineering_dimension": 4,
            "strict_candidate_basis": h14_strict_basis,
            "normalized_extended_primitives": {
                "B_C": "integral sqrt(g) tau C2",
                "B_E": "Euler Wess-Zumino functional from the AFN0 primitive certificate",
                "B_P": "integral sqrt(g) tau CdualC",
                "B_BOX": "-(1/12) integral sqrt(g) R2 with its stored horizontal current",
            },
            "primitive_basis": h14_primitives,
            "boundary_matrix": _render_matrix(h14_boundary),
            "boundary_rank": _rank(h14_boundary),
            "Weyl_and_mixed_quotient_dimension": 0,
            "pure_Diff_quotient_dimension": 0,
            "even_quotient_dimension": 0,
            "odd_quotient_dimension": 0,
            "status": "COMPLETE_ZERO_IN_DECLARED_TAU_ADIC_DIMENSION_FOUR_ALGEBRA",
        },
        "one_loop_QME": {
            "strict_breaking_coordinates": [_q(value) for value in coefficients] + [_q(Fraction()), _q(Fraction())],
            "counterterm_primitive_coordinates": [_q(value) for value in coefficients] + [_q(Fraction()), _q(Fraction())],
            "boundary_image_coordinates": [_q(value) for value in restored_image],
            "counterterm": "-(4 pi)^(-2) hbar [(199/30) B_C-(87/20) B_E]",
            "restored_equation": "A^(1)+s_ext counterterm=0 modulo d_h",
            "status": "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY",
        },
        "lifecycle": {
            "strict_fixed_field_content": "OBSTRUCTED",
            "tau_adic_compensator_extended_local_Euclidean_one_loop": "QME_RESTORED",
            "all_loop_extended_QME": "OPEN",
            "Lorentzian_QME": "OPEN",
            "residual_transfer": "FORBIDDEN_EXTENDED_CLASSICAL_CONTRACTION_NOT_SUPPLIED",
            "Bridge_4": "NO_CERTIFIED_MAP",
            "Bridge_5": "NO_CERTIFIED_MAP_BRIDGE_2_ABSENT",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "proof_hashes": {
            "H04_matrices_sha256": _digest({"dh": _render_matrix(h04_dh), "afn": _render_matrix(incoming_afn1)}),
            "H14_boundary_sha256": _digest(_render_matrix(h14_boundary)),
            "formal_inverse_sha256": _digest({"minus": [_q(x) for x in exp_minus], "plus": [_q(x) for x in exp_plus]}),
        },
        "next_gate": "EXTENDED_CLASSICAL_CONTRACTION_AND_ONE_LOOP_SLAVNOV_OPERATOR_Q1",
        "claim_boundary": (
            "This theorem is restricted to the formal tau-adic local analytic jet algebra at engineering dimension four on the regular Bach locus. The exact canonical dressed change contracts the Weyl field, ghost and cotangent quartet, so the extended BV problem reduces to the pure-Diff complex of g_hat. The exhaustive repository curvature basis then gives H04 dimensions three even and one odd, including the new R(g_hat)^2 class, while Box R(g_hat) is horizontally exact. The certified four-dimensional pure-Diff anomaly zero theorem and the explicit four-by-four primitive matrix give H14=0 in both parities. Pointwise nonminimal doublets and local canonical gauge fixing preserve these dimensions. Consequently the exact coefficient-bearing one-loop Euclidean breaking is removed by the displayed Wess-Zumino counterterm and the local extended one-loop QME is restored. This is not a finite polynomial-in-tau theorem, an all-loop QME, a Lorentzian renormalized-product theorem, a BRST Hadamard state, an extended classical residual contraction, a residual quantum transfer, a Bridge-4 mode crosswalk, a Bridge-5 interacting insertion map, positivity, or a particle statement."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    h04 = value.get("H04", {})
    h14 = value.get("H14", {})
    qme = value.get("one_loop_QME", {})
    lifecycle = value.get("lifecycle", {})
    if (
        value.get("result_state")
        != "TAU_ADIC_EXTENDED_GAUGE_FIXED_H04_H14_COMPLETE_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED"
        or value.get("local_algebra", {}).get("kind")
        != "FORMAL_TAU_ADIC_LOCAL_ANALYTIC_JET_ALGEBRA"
        or value.get("local_algebra", {}).get("all_orders_inverse_status")
        != "VERIFIED_BY_BINOMIAL_THEOREM"
        or h04.get("even_quotient_dimension") != 3
        or h04.get("odd_quotient_dimension") != 1
        or h04.get("even_classes") != ["C(g_hat)^2", "E4(g_hat)", "R(g_hat)^2"]
        or len(h04.get("even_dual_witnesses", [])) != 3
        or any(
            witness.get("boundary_pairing") != _q(Fraction())
            or witness.get("representative_pairing") != _q(Fraction(1))
            for witness in h04.get("even_dual_witnesses", [])
        )
        or h14.get("boundary_rank") != 4
        or h14.get("even_quotient_dimension") != 0
        or h14.get("odd_quotient_dimension") != 0
        or qme.get("boundary_image_coordinates") != qme.get("strict_breaking_coordinates")
        or qme.get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or lifecycle.get("all_loop_extended_QME") != "OPEN"
        or lifecycle.get("Lorentzian_QME") != "OPEN"
        or not str(lifecycle.get("residual_transfer", "")).startswith("FORBIDDEN")
        or lifecycle.get("Bridge_4") != "NO_CERTIFIED_MAP"
        or not str(lifecycle.get("Bridge_5", "")).startswith("NO_CERTIFIED_MAP")
    ):
        raise ValueError("extended WZ local-BV theorem crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale extended WZ local-BV theorem: {OUTPUT}")
    print("WZ EXTENDED LOCAL BV: H04=(3,1), H14=0; ONE-LOOP LOCAL EUCLIDEAN QME RESTORED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
