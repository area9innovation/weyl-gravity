#!/usr/bin/env python3
"""C2g-E6: exact pure-Weyl bosonic Fock rail through matter energy six.

The energy-six shell contains all one-particle modes, every two-particle
partition ``2+4`` and ``3+3``, and ``Sym^3(H_2)``.  This script constructs
the normalized occupation basis and second-quantizes the exact C2g-A
one-particle conformal action.

The full shell has dimension 2062.  Compact representation theory reduces
its scalar subspace to eight explicit invariant vectors.  The complete
relative-primary condition is then computed exactly on that small space:

    D=6,       L_a=R_a=0,       K^-_M=0.

Particle number and chirality are retained throughout.  The four resulting
relative vectors are diagnostics only: the independent C2g-N6 Cartan
identity contracts the absolute residual complex at degree two.  Local
BV/BRST reduction and interaction matrix elements remain outside this
certificate and are guarded explicitly.
"""

from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, product

import sympy as sp
from sympy.physics.wigner import wigner_3j

try:
    from symbolic import verify_conformal_fock_energy4 as fock4
    from symbolic.verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_fock_energy4 as fock4
    from verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )


Occupation = fock4.Occupation


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def sparse_exact_equal(first: sp.Matrix, second: sp.Matrix) -> bool:
    """Exact equality visiting only stored entries of a sparse difference."""

    if first.shape != second.shape:
        return False
    difference = sp.SparseMatrix(first - second)
    return all(sp.simplify(value) == 0 for value in difference.todok().values())


def enumerate_fock_basis_energy6(
    one_particle: fock4.OneParticleModule,
) -> tuple[Occupation, ...]:
    energy = tuple(state.energy for state in one_particle.states)
    singles = tuple((state.index,) for state in one_particle.states)
    pairs = tuple(
        (first.index, second.index)
        for first, second in combinations_with_replacement(one_particle.states, 2)
        if first.energy + second.energy <= 6
    )
    lowest_states = tuple(
        state for state in one_particle.states if state.energy == 2
    )
    triples = tuple(
        (first.index, second.index, third.index)
        for first, second, third in combinations_with_replacement(
            lowest_states, 3
        )
    )
    return tuple(
        sorted(
            ((), *singles, *pairs, *triples),
            key=lambda state: (
                sum(energy[index] for index in state),
                len(state),
                state,
            ),
        )
    )


def assemble_fock_energy6() -> fock4.FockModule:
    one_particle = fock4.assemble_one_particle(6)
    basis = enumerate_fock_basis_energy6(one_particle)
    state_energy = tuple(
        fock4.occupation_energy(state, one_particle) for state in basis
    )
    form = sp.diag(
        *(fock4.occupation_sign(state, one_particle) for state in basis),
        cls=sp.SparseMatrix,
    )
    compact = {
        label: fock4.second_quantize(matrix, basis)
        for label, matrix in one_particle.compact.items()
    }
    lowering = {
        component: fock4.second_quantize(matrix, basis)
        for component, matrix in one_particle.lowering.items()
    }
    raising = {
        component: fock4.second_quantize(matrix, basis)
        for component, matrix in one_particle.raising.items()
    }
    return fock4.FockModule(
        6,
        one_particle,
        basis,
        state_energy,
        form,
        compact,
        lowering,
        raising,
    )


def shell_sector_counts(fock: fock4.FockModule, energy: int) -> Counter[int]:
    return Counter(len(fock.basis[index]) for index in fock.indices_at(energy))


def verify_inventory(fock: fock4.FockModule) -> None:
    counts = Counter(fock.state_energy)
    check(
        "C2g-E6: complete energy-six shell has dimension 2062",
        counts[6] == 2062 and len(fock.indices_at(6)) == 2062,
    )
    check(
        "C2g-E6: energy-six particle sectors have dimensions 202+1640+220",
        shell_sector_counts(fock, 6) == {1: 202, 2: 1640, 3: 220},
    )
    check(
        "C2g-E6: complete Fock buffer through energy six has dimension 2786",
        counts == {0: 1, 2: 10, 3: 40, 4: 137, 5: 536, 6: 2062}
        and fock.dimension == 2786,
    )


def shell_block(
    fock: fock4.FockModule,
    matrix: sp.Matrix,
    source_energy: int,
    target_energy: int,
) -> sp.Matrix:
    return fock.homogeneous_block(matrix, source_energy, target_energy)


def verify_induced_action(fock: fock4.FockModule) -> None:
    energies = fock.compact["D"]
    check(
        "C2g-E6: induced Fock form is an exact involution",
        sparse_exact_equal(
            fock.form * fock.form,
            sp.eye(fock.dimension, cls=sp.SparseMatrix),
        ),
    )
    check(
        "C2g-E6: compact Fock generators are exactly J-self-adjoint",
        all(
            sparse_exact_equal(
                matrix.conjugate().T * fock.form, fock.form * matrix
            )
            for matrix in fock.compact.values()
        ),
    )
    check(
        "C2g-E6: proper-conformal Fock generators obey the exact J-adjoint relation",
        all(
            sparse_exact_equal(
                fock.raising[component],
                fock.form
                * fock.lowering[component].conjugate().T
                * fock.form,
            )
            for component in MAGNETIC_COMPONENTS
        ),
    )
    check(
        "C2g-E6: proper-conformal Fock generators have exact grades +/-1",
        all(
            sparse_exact_equal(energies * matrix - matrix * energies, -matrix)
            for matrix in fock.lowering.values()
        )
        and all(
            sparse_exact_equal(energies * matrix - matrix * energies, matrix)
            for matrix in fock.raising.values()
        ),
    )

    # The full 2786-square products are unnecessary.  Verify every bracket
    # on the largest complete shell by composing its exact homogeneous maps.
    source_energy = 5
    form_source = fock.form.extract(
        fock.indices_at(source_energy), fock.indices_at(source_energy)
    )
    del form_source  # shape check is implicit in the products below
    zero_source = fock4.sparse_zero(len(fock.indices_at(source_energy)))
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        lower_after_raise = (
            shell_block(fock, fock.lowering[first], 6, 5)
            * shell_block(fock, fock.raising[second], 5, 6)
        )
        raise_after_lower = (
            shell_block(fock, fock.raising[second], 4, 5)
            * shell_block(fock, fock.lowering[first], 5, 4)
        )
        rotation = shell_block(
            fock, fock4.fock_rotation(fock, first, second), 5, 5
        )
        energy = shell_block(fock, energies, 5, 5)
        expected = 2 * (energy if first == second else zero_source) + 2 * rotation
        if not sparse_exact_equal(lower_after_raise - raise_after_lower, expected):
            raise AssertionError("energy-five proper-conformal bracket failed")
    print(
        "[OK ] C2g-E6: exact [K-,K+] algebra closes on the largest complete Fock shell"
    )


def states_for_mode(
    fock: fock4.FockModule, chirality: int, mode: str
) -> dict[tuple[sp.Rational, sp.Rational], int]:
    return {
        state.magnetic: state.index
        for state in fock.one_particle.states
        if state.chirality == chirality and state.mode == mode
    }


def normalized(vector: sp.Matrix) -> sp.Matrix:
    norm = sp.simplify((vector.conjugate().T * vector)[0])
    if norm == 0:
        raise ValueError("cannot normalize the zero vector")
    return sp.SparseMatrix(vector / sp.sqrt(norm))


def same_mode_pair_singlet(
    fock: fock4.FockModule, chirality: int, mode: str
) -> sp.Matrix:
    states = states_for_mode(fock, chirality, mode)
    if not states:
        raise ValueError(f"missing {mode} chirality {chirality:+d}")
    sample = next(
        state
        for state in fock.one_particle.states
        if state.chirality == chirality and state.mode == mode
    )
    irrep = next(
        item
        for item in (
            *fock.one_particle.plus.irreps,
            *fock.one_particle.minus.irreps,
        )
        if item.label == mode
        and (
            (chirality == 1 and item in fock.one_particle.plus.irreps)
            or (chirality == -1 and item in fock.one_particle.minus.irreps)
        )
    )
    del sample
    vector = sp.MutableSparseMatrix(fock.dimension, 1, {})
    for magnetic, state_index in states.items():
        opposite = (-magnetic[0], -magnetic[1])
        opposite_index = states[opposite]
        occupation = tuple(sorted((state_index, opposite_index)))
        exponent = int(irrep.left - magnetic[0] + irrep.right - magnetic[1])
        coefficient = sp.Integer(-1) ** exponent
        if state_index == opposite_index:
            coefficient *= sp.sqrt(2)
        vector[fock.index[occupation]] += coefficient
    return normalized(vector)


def mixed_mode_pair_singlet(
    fock: fock4.FockModule,
    chirality: int,
    first_mode: str,
    second_mode: str,
) -> sp.Matrix:
    first = states_for_mode(fock, chirality, first_mode)
    second = states_for_mode(fock, chirality, second_mode)
    first_irrep = (
        fock.one_particle.plus if chirality == 1 else fock.one_particle.minus
    )
    first_irrep = next(mode for mode in first_irrep.irreps if mode.label == first_mode)
    second_irrep = (
        fock.one_particle.plus if chirality == 1 else fock.one_particle.minus
    )
    second_irrep = next(mode for mode in second_irrep.irreps if mode.label == second_mode)
    if (first_irrep.left, first_irrep.right) != (
        second_irrep.left,
        second_irrep.right,
    ):
        raise ValueError("a scalar pair requires equivalent SO(4) irreps")
    vector = sp.MutableSparseMatrix(fock.dimension, 1, {})
    for magnetic, first_index in first.items():
        opposite = (-magnetic[0], -magnetic[1])
        second_index = second[opposite]
        exponent = int(
            first_irrep.left
            - magnetic[0]
            + first_irrep.right
            - magnetic[1]
        )
        occupation = tuple(sorted((first_index, second_index)))
        vector[fock.index[occupation]] += sp.Integer(-1) ** exponent
    return normalized(vector)


def e2_cubic_singlet(fock: fock4.FockModule, chirality: int) -> sp.Matrix:
    states = states_for_mode(fock, chirality, "E2")
    spin_axis = 0 if chirality == 1 else 1
    ordered = tuple(states.items())
    vector = sp.MutableSparseMatrix(fock.dimension, 1, {})
    for first_magnetic, first_index in ordered:
        for second_magnetic, second_index in ordered:
            for third_magnetic, third_index in ordered:
                first_m = first_magnetic[spin_axis]
                second_m = second_magnetic[spin_axis]
                third_m = third_magnetic[spin_axis]
                coefficient = wigner_3j(
                    2, 2, 2, first_m, second_m, third_m
                )
                if coefficient == 0:
                    continue
                occupation = tuple(sorted((first_index, second_index, third_index)))
                multiplicities = Counter(occupation)
                occupation_factor = sp.sqrt(
                    math.prod(math.factorial(value) for value in multiplicities.values())
                )
                vector[fock.index[occupation]] += coefficient * occupation_factor
    return normalized(vector)


@dataclass(frozen=True)
class ScalarCandidate:
    label: str
    particles: int
    chirality_counts: tuple[int, int]
    vector: sp.Matrix


def scalar_candidates(fock: fock4.FockModule) -> tuple[ScalarCandidate, ...]:
    output: list[ScalarCandidate] = []
    for chirality, suffix, counts_two, counts_three in (
        (1, "+", (2, 0), (3, 0)),
        (-1, "-", (0, 2), (0, 3)),
    ):
        output.extend(
            (
                ScalarCandidate(
                    f"E2{suffix}L4{suffix}",
                    2,
                    counts_two,
                    mixed_mode_pair_singlet(fock, chirality, "E2", "L4"),
                ),
                ScalarCandidate(
                    f"Sym2(E3{suffix})",
                    2,
                    counts_two,
                    same_mode_pair_singlet(fock, chirality, "E3"),
                ),
                ScalarCandidate(
                    f"Sym2(A3{suffix})",
                    2,
                    counts_two,
                    same_mode_pair_singlet(fock, chirality, "A3"),
                ),
                ScalarCandidate(
                    f"Sym3(E2{suffix})",
                    3,
                    counts_three,
                    e2_cubic_singlet(fock, chirality),
                ),
            )
        )
    return tuple(output)


def verify_scalar_inventory(
    fock: fock4.FockModule, candidates: tuple[ScalarCandidate, ...]
) -> None:
    matrix = sp.SparseMatrix.hstack(*(candidate.vector for candidate in candidates))
    check(
        "C2g-E6: representation inventory gives exactly eight independent scalar candidates",
        len(candidates) == 8
        and matrix.rank() == 8
        and {candidate.label for candidate in candidates}
        == {
            "E2+L4+",
            "Sym2(E3+)",
            "Sym2(A3+)",
            "Sym3(E2+)",
            "E2-L4-",
            "Sym2(E3-)",
            "Sym2(A3-)",
            "Sym3(E2-)",
        },
    )
    check(
        "C2g-E6: every displayed candidate is an exact D=6 compact scalar",
        sparse_exact_equal(fock.compact["D"] * matrix, 6 * matrix)
        and all(
            sparse_exact_equal(
                fock.compact[label] * matrix, sp.zeros(fock.dimension, 8)
            )
            for label in ("Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
        ),
    )


@dataclass(frozen=True)
class RelativeEnergySix:
    scalar_candidates: tuple[ScalarCandidate, ...]
    scalar_inclusion: sp.Matrix
    coefficient_kernel: sp.Matrix
    inclusion: sp.Matrix
    gram: sp.Matrix
    labels: tuple[str, ...]


def relative_energy_six_kernel(
    fock: fock4.FockModule, candidates: tuple[ScalarCandidate, ...]
) -> RelativeEnergySix:
    scalar = sp.SparseMatrix.hstack(*(candidate.vector for candidate in candidates))
    energy_five = fock.indices_at(5)
    lowered = tuple(
        (matrix * scalar).extract(energy_five, tuple(range(scalar.cols)))
        for matrix in fock.lowering.values()
    )
    stacked = sp.Matrix.vstack(*lowered)
    kernel_vectors = stacked.nullspace()
    coefficient_kernel = sp.Matrix.hstack(*kernel_vectors)
    inclusion = scalar * sp.SparseMatrix(coefficient_kernel)
    check(
        "C2g-E6: exact all-component K-minus kernel has dimension four",
        coefficient_kernel.shape == (8, 4)
        and sparse_exact_equal(stacked * coefficient_kernel, sp.zeros(stacked.rows, 4)),
    )

    # Particle number and chirality make four invariant blocks.  Fix a basis
    # by intersecting the kernel with each declared scalar-coordinate block.
    coordinate_groups = (
        ("N2(+,+)", (0, 1, 2)),
        ("N3(+,+,+)", (3,)),
        ("N2(-,-)", (4, 5, 6)),
        ("N3(-,-,-)", (7,)),
    )
    selected: list[sp.Matrix] = []
    labels: list[str] = []
    for label, support in coordinate_groups:
        complement = tuple(index for index in range(8) if index not in support)
        constraints = coefficient_kernel.extract(complement, tuple(range(4)))
        combinations = constraints.nullspace()
        if len(combinations) != 1:
            raise AssertionError(f"expected one primary in {label}")
        vector = sp.simplify(coefficient_kernel * combinations[0])
        selected.append(vector)
        labels.append(label)
    coefficient_kernel = sp.Matrix.hstack(*selected)
    inclusion = scalar * sp.SparseMatrix(coefficient_kernel)
    gram = sp.simplify(inclusion.conjugate().T * fock.form * inclusion)
    check(
        "C2g-E6: relative primaries decompose as one in each pure-chirality N=2 and N=3 sector",
        coefficient_kernel.rank() == 4 and tuple(labels) == (
            "N2(+,+)",
            "N3(+,+,+)",
            "N2(-,-)",
            "N3(-,-,-)",
        ),
    )
    check(
        "C2g-E6: every relative primary is annihilated by rotations and all K-minus components",
        all(
            sparse_exact_equal(matrix * inclusion, sp.zeros(fock.dimension, 4))
            for matrix in fock.lowering.values()
        )
        and all(
            sparse_exact_equal(
                fock.compact[label] * inclusion, sp.zeros(fock.dimension, 4)
            )
            for label in ("Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
        ),
    )
    return RelativeEnergySix(
        candidates,
        scalar,
        coefficient_kernel,
        inclusion,
        gram,
        tuple(labels),
    )


def normalize_relative_basis(
    result: RelativeEnergySix,
) -> tuple[sp.Matrix, sp.Matrix]:
    diagonal = tuple(sp.simplify(result.gram[index, index]) for index in range(4))
    if any(value == 0 for value in diagonal):
        raise AssertionError("relative Gram matrix is degenerate")
    scales = sp.diag(*(1 / sp.sqrt(abs(value)) for value in diagonal))
    normalized_inclusion = result.inclusion * sp.SparseMatrix(scales)
    normalized_gram = sp.simplify(scales.conjugate().T * result.gram * scales)
    return normalized_inclusion, normalized_gram


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-absolute-global-brst",
        action="store_true",
        help="fail closed: only the relative matter kernel is computed",
    )
    parser.add_argument(
        "--require-local-bv",
        action="store_true",
        help="fail closed: the local Diff x Weyl BV complex is absent",
    )
    parser.add_argument(
        "--require-interactions",
        action="store_true",
        help="fail closed: no cubic or quartic interaction acts on this kernel",
    )
    args = parser.parse_args()
    if args.require_absolute_global_brst:
        raise SystemExit(
            "absolute delta=2 cohomology is contractible by the C2g-N6 D-antighost homotopy; it is not recomputed here"
        )
    if args.require_local_bv:
        raise SystemExit("the local Diff x Weyl BV/BRST complex is absent")
    if args.require_interactions:
        raise SystemExit("no interaction operator has been restricted to this kernel")

    fock = assemble_fock_energy6()
    verify_inventory(fock)
    verify_induced_action(fock)
    candidates = scalar_candidates(fock)
    verify_scalar_inventory(fock, candidates)
    result = relative_energy_six_kernel(fock, candidates)
    _, normalized_gram = normalize_relative_basis(result)
    signature = tuple(normalized_gram[index, index] for index in range(4))
    check(
        "C2g-E6: restricted relative Gram matrix is exact, diagonal, and nondegenerate",
        normalized_gram == sp.diag(*signature)
        and all(value in (-1, 1) for value in signature),
    )

    print("energy-six shell dimension:", len(fock.indices_at(6)))
    print("scalar candidate labels:", tuple(candidate.label for candidate in candidates))
    print("relative primary labels:", result.labels)
    print("relative coefficient matrix in scalar basis:")
    sp.print_latex(result.coefficient_kernel)
    print("unnormalized relative Gram matrix:", result.gram)
    print("normalized relative Gram signature:", signature)
    print(
        "absolute diagnostic: residual degree delta=6-4=2 obeys "
        "d*i_D+i_D*d=2I in C2g-N6, so these relative vectors are "
        "contractible in the absolute residual complex"
    )
    print(
        "C2g-E6 STATUS: EXACT FOUR-DIMENSIONAL RELATIVE PRIMARY-SCALAR "
        "DIAGNOSTIC AT MATTER WEIGHT SIX. Absolute delta=2 residual "
        "cohomology is killed by the independent Cartan homotopy; local BV "
        "and interactions are not claimed."
    )


if __name__ == "__main__":
    main()
