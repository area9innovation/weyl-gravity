#!/usr/bin/env python3
"""Method-distinct replay of the active-clock background-stability theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-active-clock-background-stability-v1.schema.json"
)
AUDIT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json"
)
AUDIT_SHA256 = "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(entry["coefficient"])
    return value


def _expected_matrix(
    k: sp.Symbol, q: sp.Symbol, n: sp.Symbol
) -> sp.Matrix:
    cylinder = sp.Matrix(
        [[0, 36 * k**2, 3 * k, 1, 0, 0], [0, 12 * k**2, -k, -1, 0, 0]]
    )
    R = (4 - q) / 2
    ricci = [0, (2 - q) / 2, q / 2]
    bach = [
        (1 - q) ** 2 / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (5 * q - 1) / 6,
    ]
    rows: list[list[sp.Expr]] = []
    for slot, metric, time in ((0, -1, True), (1, 1, False), (2, 1, False)):
        gravity = [
            bach[slot],
            4 * R * ricci[slot] - R**2 * metric,
            ricci[slot] - R * metric / 2,
        ]
        matter = [1, n**2, -3 * n**4] if time else [-1, n**2, -n**4]
        rows.append(gravity + matter)
    return cylinder.col_join(sp.Matrix(rows))


def _kernel(k: sp.Symbol, q: sp.Symbol, n: sp.Symbol) -> sp.Matrix:
    A = 4 * q - 1
    F = 12 * k + q - 4
    J = 16 * k * q - 4 * k - q
    return sp.Matrix(
        [
            8 * n**4 * F,
            -sp.Rational(4, 3) * n**4 * A,
            32 * k * n**4 * A,
            -48 * k**2 * n**4 * A,
            -8 * k * n**2 * A * F,
            -F * J,
        ]
    )


def _verify_exact_algebra(payload: dict[str, Any]) -> None:
    k, q, n, lam, D, zeta = sp.symbols("kappa q nu lambda D zeta")
    expected = _expected_matrix(k, q, n)
    serialized = _dense(payload["stationary_evaluation"]["stacked_matrix"])
    if (serialized - expected).applyfunc(sp.factor) != sp.zeros(5, 6):
        raise AssertionError("STATIONARY_MATRIX_MISMATCH")
    K = _kernel(k, q, n)
    if (expected * K).applyfunc(sp.factor) != sp.zeros(5, 1):
        raise AssertionError("KERNEL_IDENTITY_MISMATCH")
    serialized_K = sp.Matrix(
        [
            sp.sympify(value)
            for value in payload["stationary_locus_and_rank_strata"][
                "kernel_generator_K"
            ]
        ]
    )
    if (serialized_K - K).applyfunc(sp.factor) != sp.zeros(6, 1):
        raise AssertionError("SERIALIZED_KERNEL_MISMATCH")

    # This rail does not solve a symbolic nullspace. It verifies the kernel
    # directly and proves rank five with a single exact minor; the producer
    # separately factors all six signed maximal cofactors.
    witness = sp.factor(expected[:, [1, 2, 3, 4, 5]].det())
    if witness != 8 * k * n**6 * (q - 1) * (12 * k + q - 4):
        raise AssertionError("RANK_WITNESS_MISMATCH")
    serialized_cofactors = [
        sp.sympify(value)
        for value in payload["stationary_locus_and_rank_strata"][
            "signed_maximal_cofactors_delete_columns_0_to_5"
        ]
    ]
    direct_cofactors = [
        sp.factor(
            (-1) ** column
            * expected[:, [j for j in range(6) if j != column]].det()
        )
        for column in range(6)
    ]
    if any(
        sp.factor(left - right) != 0
        for left, right in zip(serialized_cofactors, direct_cofactors)
    ):
        raise AssertionError("COFACTOR_LEDGER_MISMATCH")

    fixed = {k: 1, q: sp.Rational(9, 40), n: sp.Rational(3, 4)}
    ray = [sp.factor(value.subs(fixed)) for value in K]
    normalized = [sp.factor(value / ray[-1]) for value in ray]
    if normalized != [
        sp.Rational(81, 20),
        sp.Rational(27, 3290),
        -sp.Rational(324, 1645),
        sp.Rational(486, 1645),
        sp.Rational(18, 25),
        1,
    ]:
        raise AssertionError("FROZEN_RAY_MISMATCH")

    coefficients = lam * K
    p1 = coefficients[4]
    mass = coefficients[2]
    velocity = sp.Matrix([[0, -3, 0], [-3, 0, 0], [0, 0, -2 * p1]])
    C = sp.Matrix([[1, 1, 0], [1, -1, 0], [0, 0, 1]])
    if (C.T * velocity * C).applyfunc(sp.factor) != sp.diag(-6, 6, -2 * p1):
        raise AssertionError("INERTIA_CONGRUENCE_MISMATCH")
    hessian = sp.Matrix(
        [
            [0, 3 * (D**2 - 2 * k), 0],
            [3 * (D**2 - 2 * k), 12 / mass, 0],
            [0, 0, 2 * p1 * D**2],
        ]
    )
    if sp.factor(hessian.det() + 18 * p1 * D**2 * (D**2 - 2 * k) ** 2) != 0:
        raise AssertionError("HESSIAN_DETERMINANT_MISMATCH")
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0, 0, 0],
            [2 * k, 0, -4 / mass, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 2 * k, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    if sp.expand(
        evolution.charpoly(zeta).as_expr() - zeta**2 * (zeta**2 - 2 * k) ** 2
    ) != 0:
        raise AssertionError("EVOLUTION_POLYNOMIAL_MISMATCH")


def _verify_box_and_bifurcation(payload: dict[str, Any]) -> None:
    k, q = sp.symbols("kappa q", real=True)
    kl, ku = sp.Rational(15, 16), sp.Rational(17, 16)
    ql, qu = sp.Rational(1, 5), sp.Rational(1, 4)
    G = 16 * q**2 * k + q**2 - 56 * q * k - 4 * q + 16 * k
    E = 16 * q**2 * k - 3 * q**2 - 104 * q * k + 12 * q + 16 * k
    if not (
        sp.factor((12 * kl + ql - 4) - sp.Rational(149, 20)) == 0
        and sp.factor(G.subs({k: kl, q: qu}) - sp.Rational(15, 8)) == 0
        and sp.factor(E.subs({k: kl, q: ql}) + sp.Rational(81, 50)) == 0
    ):
        raise AssertionError("BOX_ENDPOINT_ARITHMETIC_MISMATCH")
    if not (
        sp.factor(sp.diff(G, k).subs(q, qu)) > 0
        and sp.factor(sp.diff(G, q).subs({k: kl, q: ql})) < 0
        and sp.factor(sp.diff(E, k).subs(q, ql)) < 0
        and sp.factor(sp.diff(E, q).subs({k: kl, q: ql})) < 0
    ):
        raise AssertionError("BOX_MONOTONICITY_MISMATCH")
    box = payload["certified_open_neighbourhood"]
    if (
        box["exact_box"]["kappa"] != ["15/16", "17/16"]
        or box["exact_box"]["q"] != ["1/5", "1/4"]
        or box["exact_box"]["nu"] != ["2/3", "5/6"]
        or box["rank"]["value"] != 5
        or box["health_half_lines"]["common_clock_health"] != "EMPTY"
    ):
        raise AssertionError("DECLARED_BOX_DRIFT")

    below = payload["first_bifurcation"]["below_witness"][
        "p1_PX_longitudinal"
    ]
    above = payload["first_bifurcation"]["above_witness"][
        "p1_PX_longitudinal"
    ]
    below_q = [sp.sympify(value) for value in below]
    above_q = [sp.sympify(value) for value in above]
    if not (
        below_q[0] > 0
        and below_q[1] < 0
        and below_q[2] < 0
        and all(value < 0 for value in above_q)
        and payload["first_bifurcation"]["surface_data"]["stationary_rank"] == 5
    ):
        raise AssertionError("BIFURCATION_WITNESS_MISMATCH")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if _sha(AUDIT) != AUDIT_SHA256:
        raise AssertionError("FROZEN_AUDIT_HASH_DRIFT")
    if payload["frozen_import"]["sha256"] != AUDIT_SHA256:
        raise AssertionError("FROZEN_IMPORT_MISMATCH")
    _verify_exact_algebra(payload)
    _verify_box_and_bifurcation(payload)
    for field, section in (
        ("stationary_sha256", "stationary_evaluation"),
        ("locus_sha256", "stationary_locus_and_rank_strata"),
        ("quadratic_sha256", "coupled_scalar_principal_velocity"),
        ("clock_sha256", "clock_cone_charge_and_relational_inequalities"),
        ("neighbourhood_sha256", "certified_open_neighbourhood"),
        ("bifurcation_sha256", "first_bifurcation"),
        ("gates_sha256", "seven_gate_stability"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")
    if (
        payload["seven_gate_stability"]["good_locus"]
        != "EMPTY_FOR_EVERY_PARAMETER_POINT_IN_N_box"
        or payload["seven_gate_stability"]["candidate_C_active_selected"]
        or payload["claim_flags"]["ONE_FIXED_ACTION_BACKGROUND_STABILITY"]
        or payload["claim_flags"]["GENERIC_BACKGROUND_NO_GO"]
        or payload["claim_flags"]["HADAMARD_ANOMALY_QME_OR_QUANTUM"]
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print("COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1 replay: PASS")


if __name__ == "__main__":
    main()
