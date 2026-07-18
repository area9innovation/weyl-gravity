#!/usr/bin/env python3
"""Certify what the restored one-loop QME does and does not determine about Q1."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json"
SCHEMA = HERE / "schema/one-loop-slavnov-q1-disposition-v1.schema.json"
DEPENDENCIES = {
    "extended_QME": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
    "WZ_primitive": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "cotangent_lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _rank(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix]
    rank = 0
    if not rows:
        return rank
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(rows[row], rows[rank])
            ]
        rank += 1
    return rank


def _curvature_responses(h: list[list[Fraction]]) -> tuple[Fraction, Fraction]:
    """Return the exact flat p=(1,0,0,0) quadratic C2 and R2 responses."""

    dimension = 4
    momentum = [Fraction(1), Fraction(), Fraction(), Fraction()]
    riemann: dict[tuple[int, int, int, int], Fraction] = {}
    for a in range(dimension):
        for b in range(dimension):
            for c in range(dimension):
                for d in range(dimension):
                    riemann[a, b, c, d] = Fraction(1, 2) * (
                        momentum[c] * momentum[b] * h[a][d]
                        + momentum[d] * momentum[a] * h[b][c]
                        - momentum[d] * momentum[b] * h[a][c]
                        - momentum[c] * momentum[a] * h[b][d]
                    )
    ricci = [
        [sum((riemann[a, b, a, d] for a in range(dimension)), Fraction()) for d in range(dimension)]
        for b in range(dimension)
    ]
    scalar = sum((ricci[index][index] for index in range(dimension)), Fraction())
    riemann_squared = sum((entry * entry for entry in riemann.values()), Fraction())
    ricci_squared = sum((entry * entry for row in ricci for entry in row), Fraction())
    c_squared = riemann_squared - 2 * ricci_squared + Fraction(1, 3) * scalar * scalar
    return c_squared, scalar * scalar


def _bulk_response_matrix() -> list[list[Fraction]]:
    tt = [
        [Fraction(), Fraction(), Fraction(), Fraction()],
        [Fraction(), Fraction(1), Fraction(), Fraction()],
        [Fraction(), Fraction(), Fraction(-1), Fraction()],
        [Fraction(), Fraction(), Fraction(), Fraction()],
    ]
    conformal = [
        [Fraction(1), Fraction(), Fraction(), Fraction()],
        [Fraction(), Fraction(1), Fraction(), Fraction()],
        [Fraction(), Fraction(), Fraction(1), Fraction()],
        [Fraction(), Fraction(), Fraction(), Fraction(1)],
    ]
    tt_c2, tt_r2 = _curvature_responses(tt)
    conf_c2, conf_r2 = _curvature_responses(conformal)
    # Columns are C(g_hat)^2, E4(g_hat), R(g_hat)^2, and C dual C(g_hat).
    # The Euler and Pontryagin columns have zero compactly supported bulk
    # Euler derivative because their integrated representatives are topological.
    return [
        [tt_c2, Fraction(), tt_r2, Fraction()],
        [conf_c2, Fraction(), conf_r2, Fraction()],
    ]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    extended = values["extended_QME"]
    primitive = values["WZ_primitive"]
    lift = values["cotangent_lift"]
    breaking = values["regulated_breaking"]
    if (
        extended.get("one_loop_QME", {}).get("status")
        != "QME_RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN_TAU_ADIC_EXTENDED_THEORY"
        or extended.get("H04", {}).get("even_quotient_dimension") != 3
        or extended.get("H04", {}).get("odd_quotient_dimension") != 1
        or primitive.get("local_primitives", {}).get("coefficient_bearing_primitive")
        != "(199/30) B_C-(87/20) B_E"
        or lift.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
    ):
        raise ValueError("one-loop Q1 inputs drifted")

    response = _bulk_response_matrix()
    if response != [
        [Fraction(1), Fraction(), Fraction(), Fraction()],
        [Fraction(), Fraction(), Fraction(9), Fraction()],
    ] or _rank(response) != 2:
        raise ValueError("finite-counterterm bulk ambiguity witness drifted")

    coefficients = [Fraction(199, 30), Fraction(-87, 20)]
    imported = [
        Fraction(
            breaking["coefficients"][name]["numerator"],
            breaking["coefficients"][name]["denominator"],
        )
        for name in ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4")
    ]
    if imported != coefficients:
        raise ValueError("coefficient-bearing Q1 contribution drifted")

    result = {
        "schema": "quantum-weyl-one-loop-slavnov-q1-disposition-v1",
        "result_id": "ONE_LOOP_SLAVNOV_Q1_DISPOSITION",
        "result_state": "LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED_COMPLETE_Q1_UNDERDETERMINED_RESIDUAL_TRANSFER_FORBIDDEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": extended["classical_commit"],
        "operator_convention": {
            "effective_action": "Gamma=S+hbar Gamma_1^ren+O(hbar^2)",
            "first_slavnov_operator": "Q_1^ren=(Gamma_1^ren,.) plus the declared renormalized BV-Laplacian contribution",
            "counterterm_hamiltonian": "Q_1^WZ=(C_1^WZ,.)",
            "counterterm": "C_1^WZ=-(4 pi)^(-2)[(199/30)B_C-(87/20)B_E]",
        },
        "fixed_local_contribution": {
            "coefficient_basis": ["B_C", "B_E"],
            "coefficient_vector": [_q(value) for value in coefficients],
            "field_and_ghost_rows": "ZERO_BECAUSE_C_1_WZ_HAS_ANTIFIELD_NUMBER_ZERO",
            "cotangent_rows": {
                "g_hat_star": "Euler_g_hat(C_1^WZ)",
                "tau_hat_star": "Euler_tau(C_1^WZ)",
            },
            "status": "COEFFICIENT_BEARING_LOCAL_HAMILTONIAN_CONTRIBUTION_FIXED",
        },
        "finite_counterterm_ambiguity": {
            "H04_basis": ["C(g_hat)^2", "E4(g_hat)", "R(g_hat)^2", "C(g_hat) dual C(g_hat)"],
            "parameters": ["z_C", "z_E", "z_R", "z_P"],
            "family": "Gamma_1^ren -> Gamma_1^ren + z_C C_hat^2 + z_E E4_hat + z_R R_hat^2 + z_P C_hat dual C_hat",
            "flat_fixture": {
                "signature": "Euclidean",
                "momentum": [1, 0, 0, 0],
                "TT_polarization": [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 0]],
                "conformal_polarization": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            },
            "bulk_quadratic_response_rows": ["TT", "CONFORMAL"],
            "bulk_quadratic_response_matrix": [[_q(entry) for entry in row] for row in response],
            "bulk_response_rank": _rank(response),
            "bulk_kernel": ["E4(g_hat)", "C(g_hat) dual C(g_hat)"],
            "kernel_reason": "Euler and Pontryagin have zero compactly supported bulk Euler derivative; boundary and global data remain separate",
            "conclusion": "AT_LEAST_TWO_INDEPENDENT_LOCAL_BULK_SCHEME_DIRECTIONS_CHANGE_Q1",
        },
        "missing_operator_data": {
            "renormalized_finite_nonlocal_Gamma1": "NOT_SUPPLIED",
            "renormalized_BV_laplacian_or_time_ordered_product": "NOT_SUPPLIED",
            "finite_normalization_conditions_for_C2_and_R2": "NOT_SUPPLIED",
            "extended_classical_residual_contraction": "NOT_SUPPLIED",
        },
        "decision": {
            "local_QME_disposition": "RESTORED_IN_DECLARED_TAU_ADIC_ONE_LOOP_LOCAL_EUCLIDEAN_THEORY",
            "coefficient_bearing_WZ_Q1_piece": "CERTIFIED",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "Q1_uniqueness": "REFUTED_WITH_EXACT_RANK_TWO_BULK_WITNESS",
            "residual_transfer": "FORBIDDEN",
            "quantum_D_Cartan_defect": "NOT_COMPUTABLE_FROM_CURRENT_INPUTS",
            "Bridge_4": "NO_CERTIFIED_MAP",
            "Bridge_5": "NO_CERTIFIED_MAP_BRIDGE_2_ABSENT",
        },
        "claim_flags": {
            "WZ_LOCAL_COUNTERTERM_HAMILTONIAN_CONTRIBUTION_FIXED": True,
            "FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO": True,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "RENORMALIZED_GAMMA1_NORMALIZATION_AND_EXTENDED_CLASSICAL_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate fixes the "
            "coefficient-bearing local Hamiltonian contribution to the first Slavnov "
            "operator from the Wess-Zumino counterterm. It independently exhibits a "
            "rank-two compactly supported bulk ambiguity from the allowed C(g_hat)^2 "
            "and R(g_hat)^2 finite counterterms. The Euler and Pontryagin directions "
            "have zero bulk Euler derivative but may retain boundary or global content. "
            "The available QME restoration therefore does not supply a unique complete "
            "Q1, because the finite nonlocal effective action, renormalized BV Laplacian "
            "or time-ordered product, and finite normalization conditions are absent. "
            "It does not authorize residual transfer, compute the quantum D-Cartan "
            "defect, establish a Lorentzian QME or state, or identify a particle."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    ambiguity = value.get("finite_counterterm_ambiguity", {})
    decision = value.get("decision", {})
    flags = value.get("claim_flags", {})
    if (
        value.get("result_state")
        != "LOCAL_COUNTERTERM_Q1_CONTRIBUTION_FIXED_COMPLETE_Q1_UNDERDETERMINED_RESIDUAL_TRANSFER_FORBIDDEN"
        or ambiguity.get("bulk_response_rank") != 2
        or ambiguity.get("conclusion")
        != "AT_LEAST_TWO_INDEPENDENT_LOCAL_BULK_SCHEME_DIRECTIONS_CHANGE_Q1"
        or decision.get("complete_Q1") != "NO_CERTIFIED_OPERATOR"
        or decision.get("residual_transfer") != "FORBIDDEN"
        or flags.get("WZ_LOCAL_COUNTERTERM_HAMILTONIAN_CONTRIBUTION_FIXED") is not True
        or flags.get("FINITE_COUNTERTERM_BULK_Q1_AMBIGUITY_RANK_TWO") is not True
        or flags.get("COMPLETE_RENORMALIZED_Q1_SUPPLIED") is not False
        or flags.get("EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED") is not False
        or flags.get("RESIDUAL_TRANSFER_AUTHORIZED") is not False
    ):
        raise ValueError("one-loop Slavnov Q1 disposition crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale one-loop Slavnov Q1 disposition: {OUTPUT}")
    print("ONE-LOOP SLAVNOV Q1: LOCAL WZ PIECE FIXED; COMPLETE OPERATOR UNDERDETERMINED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
