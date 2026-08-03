"""Rail B: independent verification of the G0 Hamiltonian-privilege separation.

This is NOT a rerun of the generator.  Every number the certificate asserts is
recomputed here by a different route:

    dimension       rail A: ambient minus rank of the DEFINING CONSTRAINTS
                    rail B: rank of an EXPLICIT SPANNING SET

    elimination     rail A: Gauss--Jordan over Q
                    rail B: fraction-free Bareiss over Z

    Hamiltonian     rail A: "Omega A is symmetric"
                    rail B: "A^T Omega + Omega A = 0" (the Lie-algebra relation)

    inclusion chain rail A: rank of stacked constraint systems
                    rail B: elementwise predicate evaluation on every basis vector

    determinant     rail A: Gaussian elimination
                    rail B: the Leibniz permutation sum

The two rails share only ``carriers.py``, which declares Omega and the witness
matrices and computes nothing.  Agreement is the evidence.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_linear_g0
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

from reverse_physics import carriers
from reverse_physics.exact_linalg import (
    add,
    identity,
    is_zero,
    matmul,
    rank_bareiss,
    subtract,
    transpose,
)
from reverse_physics.hamiltonian_privilege_linear_g0 import OUTPUT, RESULT_ID

FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


# --- independent membership predicates -------------------------------------


def hamiltonian_lie_relation(matrix, dof: int) -> bool:
    """A in sp(2n) iff A^T Omega + Omega A = 0."""
    omega = carriers.symplectic_form(dof)
    return is_zero(add(matmul(transpose(matrix), omega), matmul(omega, matrix)))


def marginal_predicate(matrix, dof: int) -> bool:
    return all(
        matrix[2 * k][2 * k] + matrix[2 * k + 1][2 * k + 1] == 0 for k in range(dof)
    )


def liouville_predicate(matrix, dof: int) -> bool:
    return sum((matrix[i][i] for i in range(2 * dof)), Fraction(0)) == 0


def leibniz_determinant(matrix) -> Fraction:
    """Determinant by the permutation sum -- no elimination involved."""
    size = len(matrix)
    total = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        sign = _permutation_sign(permutation)
        term = Fraction(sign)
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def _permutation_sign(permutation) -> int:
    inversions = sum(
        1
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
        if permutation[i] > permutation[j]
    )
    return -1 if inversions % 2 else 1


# --- explicit spanning sets ------------------------------------------------


def _unit(size: int, i: int, j: int) -> list[Fraction]:
    vector = [Fraction(0)] * (size * size)
    vector[size * i + j] = Fraction(1)
    return vector


def _flatten(matrix) -> list[Fraction]:
    return [entry for row in matrix for entry in row]


def sp_spanning_set(dof: int) -> list[list[Fraction]]:
    """sp(2n) = Omega . Sym(2n), spanned by images of the symmetric basis."""
    size = 2 * dof
    omega = carriers.symplectic_form(dof)
    vectors = []
    for i in range(size):
        for j in range(i, size):
            symmetric = [[Fraction(0)] * size for _ in range(size)]
            symmetric[i][j] += Fraction(1)
            symmetric[j][i] += Fraction(1)
            vectors.append(_flatten(matmul(omega, symmetric)))
    return vectors


def marginal_spanning_set(dof: int) -> list[list[Fraction]]:
    size = 2 * dof
    vectors = [_unit(size, i, j) for i in range(size) for j in range(size) if i != j]
    for k in range(dof):
        vector = _unit(size, 2 * k, 2 * k)
        vector[size * (2 * k + 1) + (2 * k + 1)] = Fraction(-1)
        vectors.append(vector)
    return vectors


def sl_spanning_set(dof: int) -> list[list[Fraction]]:
    size = 2 * dof
    vectors = [_unit(size, i, j) for i in range(size) for j in range(size) if i != j]
    for i in range(size - 1):
        vector = _unit(size, i, i)
        vector[size * (i + 1) + (i + 1)] = Fraction(-1)
        vectors.append(vector)
    return vectors


SPANNING = {
    "hamiltonian_sp_dimension": sp_spanning_set,
    "marginal_dimension": marginal_spanning_set,
    "liouville_sl_dimension": sl_spanning_set,
}


def _unflatten(vector, size: int):
    return [[vector[size * i + j] for j in range(size)] for i in range(size)]


def main() -> int:
    if not OUTPUT.exists():
        print(f"{RESULT_ID}: FAIL (certificate missing at {OUTPUT})")
        return 1
    certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))

    for dof in (1, 2):
        size = 2 * dof
        recorded = certificate["dimensions"][f"dof_{dof}"]
        check(
            recorded["ambient_gl_dimension"] == size * size,
            f"n={dof}: ambient dimension disagrees",
        )

        computed = {}
        for key, factory in SPANNING.items():
            vectors = factory(dof)
            computed[key] = rank_bareiss(vectors)
            check(
                computed[key] == recorded[key],
                f"n={dof}: {key} rail B={computed[key]} rail A={recorded[key]}",
            )

        # The inclusion chain, elementwise on every spanning vector.
        for vector in sp_spanning_set(dof):
            matrix = _unflatten(vector, size)
            check(hamiltonian_lie_relation(matrix, dof), f"n={dof}: sp generator fails the Lie relation")
            check(marginal_predicate(matrix, dof), f"n={dof}: sp generator is not marginal")
            check(liouville_predicate(matrix, dof), f"n={dof}: sp generator is not Liouville")
        for vector in marginal_spanning_set(dof):
            check(
                liouville_predicate(_unflatten(vector, size), dof),
                f"n={dof}: marginal generator is not Liouville",
            )

        check(
            recorded["codimension_sp_in_liouville"]
            == computed["liouville_sl_dimension"] - computed["hamiltonian_sp_dimension"],
            f"n={dof}: codimension of sp in sl disagrees",
        )
        check(
            recorded["codimension_sp_in_marginal"]
            == computed["marginal_dimension"] - computed["hamiltonian_sp_dimension"],
            f"n={dof}: codimension of sp in marginal disagrees",
        )

    # The witnesses, under rail B's predicates.
    for name, factory in carriers.WITNESSES.items():
        matrix = factory()
        recorded = certificate["witnesses"][name]
        check(
            recorded["satisfies_hamiltonian"] == hamiltonian_lie_relation(matrix, 2),
            f"witness {name}: Hamiltonian verdict disagrees between rails",
        )
        check(
            recorded["satisfies_marginal"] == marginal_predicate(matrix, 2),
            f"witness {name}: marginal verdict disagrees between rails",
        )
        check(
            recorded["satisfies_liouville"] == liouville_predicate(matrix, 2),
            f"witness {name}: Liouville verdict disagrees between rails",
        )

    # The separation itself, restated so a silently-vacuous certificate fails.
    separating = carriers.witness_marginal_not_hamiltonian()
    check(marginal_predicate(separating, 2), "the separating witness is not marginal")
    check(not hamiltonian_lie_relation(separating, 2), "the separating witness is Hamiltonian")
    control = carriers.witness_hamiltonian_control()
    check(hamiltonian_lie_relation(control, 2), "the positive control is not Hamiltonian")

    # The finite flow map, with a Leibniz determinant.
    flow = add(identity(4), separating)
    omega = carriers.symplectic_form(2)
    defect = subtract(matmul(transpose(flow), matmul(omega, flow)), omega)
    recorded_flow = certificate["finite_flow_strengthening"]
    check(
        str(leibniz_determinant(flow)) == recorded_flow["determinant_of_flow_map"],
        "finite flow determinant disagrees between rails",
    )
    check(leibniz_determinant(flow) == 1, "finite flow is not volume preserving")
    check(not is_zero(defect), "finite flow defect vanished under rail B")
    check(
        [[str(entry) for entry in row] for row in defect]
        == recorded_flow["symplectic_defect_M_transpose_Omega_M_minus_Omega"],
        "finite flow symplectic defect disagrees between rails",
    )

    if FAILURES:
        print(f"{RESULT_ID}: FAIL")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"{RESULT_ID}: independent rail PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
