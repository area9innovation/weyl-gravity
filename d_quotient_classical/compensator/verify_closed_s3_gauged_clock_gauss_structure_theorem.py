#!/usr/bin/env python3
"""Independent exact replay of the closed-S3 compact-Gauss theorem."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rat_matrix(rows: list[list[str]]) -> sp.Matrix:
    if not rows:
        return sp.zeros(0, 0)
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def _integer_kernel_basis(matrix: sp.Matrix) -> sp.Matrix:
    vectors: list[sp.Matrix] = []
    for vector in matrix.T.nullspace():
        denominators = [int(value.q) for value in vector]
        scale = math.lcm(*denominators) if denominators else 1
        integral = [int(value * scale) for value in vector]
        divisor = math.gcd(*[abs(value) for value in integral])
        if divisor:
            integral = [value // divisor for value in integral]
        vectors.append(sp.Matrix(integral))
    return (
        sp.zeros(matrix.rows, 0)
        if not vectors
        else sp.Matrix.hstack(*vectors)
    )


def _check_fixture(fixture: dict[str, object]) -> None:
    q = sp.Matrix(fixture["Q"])
    n = (
        sp.zeros(q.rows, 0)
        if fixture["relative_dimension"] == 0
        else sp.Matrix(fixture["integer_relative_character_basis_N"])
    )
    m = _rat_matrix(fixture["phase_inertia_M"])
    pi = sp.Matrix([sp.Rational(value) for value in fixture["relative_momentum_Pi"]])
    if fixture["relative_dimension"] == 0:
        pi = sp.zeros(0, 1)
    p = n * pi
    velocity = m.inv() * p
    a = n.T * m.inv() * n
    g_rel = sp.zeros(0, 0) if not a.rows else a.inv()
    relative_velocity = n.T * velocity
    energy = sp.Rational(1, 2) * (p.T * m.inv() * p)[0]
    reduced_energy = (
        sp.Rational(1, 2)
        * (relative_velocity.T * g_rel * relative_velocity)[0]
    )
    diagonal = smith_normal_form(q, domain=ZZ)
    factors = [
        abs(int(diagonal[i, i]))
        for i in range(min(diagonal.rows, diagonal.cols))
        if diagonal[i, i] != 0
    ]
    if (
        q.T * n != sp.zeros(q.cols, n.cols)
        or q.T * p != sp.zeros(q.cols, 1)
        or int(q.rank()) != fixture["rank"]
        or q.rows - int(q.rank()) != fixture["relative_dimension"]
        or factors != fixture["smith_invariant_factors"]
        or energy != reduced_energy
        or (
            relative_velocity.T * pi
        )[0]
        != sp.Rational(fixture["raw_D_phase_moment_map"])
    ):
        raise AssertionError(f"fixture replay failed: {fixture['fixture_id']}")
    if a.rows and (not a.is_positive_definite or not g_rel.is_positive_definite):
        raise AssertionError(f"reduced positivity failed: {fixture['fixture_id']}")


def _check_two_field_charge_census() -> None:
    """Independent finite census of every small nonzero rank-one charge."""
    m = sp.diag(2, 3)
    for q1, q2 in itertools.product(range(-2, 3), repeat=2):
        if q1 == q2 == 0:
            continue
        divisor = math.gcd(abs(q1), abs(q2))
        q = sp.Matrix([[q1], [q2]])
        n = sp.Matrix([[q2 // divisor], [-q1 // divisor]])
        if q.T * n != sp.zeros(1, 1):
            raise AssertionError("two-field integer kernel census failed")
        a = (n.T * m.inv() * n)[0]
        if a <= 0:
            raise AssertionError("positive quotient census failed")
        # All phase momenta can be nonzero precisely when both charges do.
        p = n
        if bool(all(value != 0 for value in p)) != bool(q1 and q2):
            raise AssertionError("component-support criterion failed")


def verify() -> None:
    payload = json.loads(RESULT.read_text())
    for record in payload["imports"]:
        if (
            _sha(ROOT / record["path"]) != record["sha256"]
            or record["actual_sha256"] != record["sha256"]
        ):
            raise AssertionError("import hash replay failed")
    for fixture in payload["exact_fixtures"]:
        _check_fixture(fixture)
    _check_two_field_charge_census()

    sigma = payload["exact_sigma_model_projector_fixture"]
    g = _rat_matrix(sigma["full_positive_kinetic_G"])
    k_sigma = sp.Matrix(
        [sp.Rational(value) for value in sigma["gauge_K"]]
    )
    p_sigma = _rat_matrix(sigma["horizontal_projector_P_G"])
    h_sigma = _rat_matrix(sigma["horizontal_basis_H"])
    reduced_sigma = _rat_matrix(sigma["reduced_metric_HT_G_H"])
    if (
        p_sigma * p_sigma != p_sigma
        or p_sigma * k_sigma != sp.zeros(3, 1)
        or k_sigma.T * g * p_sigma != sp.zeros(1, 3)
        or g * p_sigma != p_sigma.T * g
        or h_sigma.T * g * h_sigma != reduced_sigma
        or not g.is_positive_definite
        or not reduced_sigma.is_positive_definite
    ):
        raise AssertionError("full sigma-model projector replay failed")

    q = sp.Matrix([[1, 0], [0, 1], [1, 1]])
    n = _integer_kernel_basis(q)
    if (
        n.shape != (3, 1)
        or q.T * n != sp.zeros(2, 1)
        or int(n.rank()) != 1
    ):
        raise AssertionError("independent integer-kernel replay failed")

    terminal = payload["terminal_verdict"]
    if (
        terminal["total_compact_gauge_charge_on_closed_S3"] != "ZERO"
        or terminal["individual_phase_momenta_forced_zero"]
        or terminal["relative_clock_exists_with_positive_inertia_iff"]
        != "n-rank(Q)>0"
        or terminal["boundary_or_external_source_needed_for_relative_clock"]
        or not terminal[
            "boundary_or_external_source_needed_for_nonzero_total_gauge_charge"
        ]
        or terminal["full_BV_or_causal_successor_activated"]
    ):
        raise AssertionError("terminal disposition replay failed")
    flags = payload["claim_flags"]
    if (
        flags["NONZERO_TOTAL_GAUGE_CHARGE_ON_CLOSED_SOURCE_FREE_S3"]
        or flags["MODEL_SPECIFIC_ACTION_SELECTED"]
        or flags["FULL_BV_OR_CAUSAL_PARENT"]
        or flags["HADAMARD_OR_QUANTUM"]
    ):
        raise AssertionError("forbidden promotion detected")
    print(
        "CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1 "
        "independent exact replay: PASS"
    )


if __name__ == "__main__":
    verify()
