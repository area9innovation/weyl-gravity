#!/usr/bin/env python3
"""C2g-F: exact bosonic second quantization through matter energy four.

This certificate applies ordinary bosonic second quantization to the exact
all-level one-particle conformal generators supplied by C2g-A.  The complete
pure-Weyl matter space through total compact energy four contains

* the vacuum;
* all one-particle E/A/L modes through energy four; and
* ``Sym^2(E_2^+ direct-sum E_2^-)`` at energy four.

The construction uses normalized occupation states, including the exact
square-root multiplicities in ``dGamma(K)``.  It verifies the cutoff-interior
SO(4,2) action, the induced Fock fundamental symmetry, and independently
computes the relative weight-four kernel

    D=4,       R_ab=0,       K^-_M=0.

The result is the two-dimensional span of the two chiral E2-pair singlets.
No absolute residual-ghost, local Diff x Weyl, or nonlinear cohomology is
claimed.  Reusable homogeneous generator blocks and the relative inclusion
are exposed for that later calculation.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations_with_replacement, product

import sympy as sp

try:
    from symbolic import verify_conformal_generator_all_levels as levels
    from symbolic import verify_conformal_generator_ansatz as finite
    from symbolic.verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_all_levels as levels
    import verify_conformal_generator_ansatz as finite
    from verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )


R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def sparse_zero(rows: int, columns: int | None = None) -> sp.SparseMatrix:
    return sp.SparseMatrix(rows, rows if columns is None else columns, {})


def direct_sum(*matrices: sp.Matrix) -> sp.Matrix:
    return sp.diag(*matrices, cls=sp.SparseMatrix)


@dataclass(frozen=True)
class OneParticleState:
    index: int
    chirality: int
    mode: str
    energy: int
    magnetic: tuple[sp.Rational, sp.Rational]
    sign: int


@dataclass(frozen=True)
class OneParticleModule:
    max_energy: int
    plus: levels.CutoffRepresentation
    minus: levels.CutoffRepresentation
    states: tuple[OneParticleState, ...]
    energy: sp.Matrix
    form: sp.Matrix
    compact: dict[str, sp.Matrix]
    lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]

    @property
    def dimension(self) -> int:
        return len(self.states)


def one_particle_states(
    plus: levels.CutoffRepresentation,
    minus: levels.CutoffRepresentation,
) -> tuple[OneParticleState, ...]:
    output: list[OneParticleState] = []
    offset = 0
    for chirality, space in ((1, plus), (-1, minus)):
        for mode in space.irreps:
            for local, magnetic in enumerate(mode.basis):
                output.append(
                    OneParticleState(
                        offset + space.offsets[mode.label] + local,
                        chirality,
                        mode.label,
                        mode.energy,
                        magnetic,
                        levels.FORM_SIGN[levels.branch(mode.label)],
                    )
                )
        offset += space.dimension
    return tuple(output)


def assemble_one_particle(max_energy: int) -> OneParticleModule:
    plus = levels.representation_space(max_energy, 1)
    minus = levels.representation_space(max_energy, -1)
    states = one_particle_states(plus, minus)
    compact = {
        "D": direct_sum(plus.energy, minus.energy),
        **{
            f"L{axis}": direct_sum(plus.left[axis], minus.left[axis])
            for axis in ("x", "y", "z")
        },
        **{
            f"R{axis}": direct_sum(plus.right[axis], minus.right[axis])
            for axis in ("x", "y", "z")
        },
    }
    lowering = {
        component: direct_sum(
            plus.lowering[component], minus.lowering[component]
        )
        for component in MAGNETIC_COMPONENTS
    }
    raising = {
        component: direct_sum(plus.raising[component], minus.raising[component])
        for component in MAGNETIC_COMPONENTS
    }
    return OneParticleModule(
        max_energy,
        plus,
        minus,
        states,
        compact["D"],
        direct_sum(plus.form, minus.form),
        compact,
        lowering,
        raising,
    )


Occupation = tuple[int, ...]


@dataclass(frozen=True)
class FockModule:
    max_energy: int
    one_particle: OneParticleModule
    basis: tuple[Occupation, ...]
    state_energy: tuple[int, ...]
    form: sp.Matrix
    compact: dict[str, sp.Matrix]
    lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]

    @property
    def dimension(self) -> int:
        return len(self.basis)

    @property
    def index(self) -> dict[Occupation, int]:
        return {state: position for position, state in enumerate(self.basis)}

    def indices_at(self, energy: int) -> tuple[int, ...]:
        return tuple(
            index
            for index, state_energy in enumerate(self.state_energy)
            if state_energy == energy
        )

    def homogeneous_block(
        self, matrix: sp.Matrix, source_energy: int, target_energy: int
    ) -> sp.Matrix:
        return matrix.extract(
            self.indices_at(target_energy), self.indices_at(source_energy)
        )


def enumerate_fock_basis(
    one_particle: OneParticleModule, max_energy: int
) -> tuple[Occupation, ...]:
    """Enumerate the exact bosonic Fock basis for ``max_energy <= 5``.

    The lowest oscillator energy is two, so at most two particles occur in
    the energy-four/five windows needed here.
    """

    if max_energy > 5:
        raise ValueError(
            "this low-energy enumerator is intentionally bounded at five; "
            "add higher particle sectors before increasing it"
        )
    one_states = tuple(
        (state.index,) for state in one_particle.states if state.energy <= max_energy
    )
    pairs = tuple(
        (first.index, second.index)
        for first, second in combinations_with_replacement(one_particle.states, 2)
        if first.energy + second.energy <= max_energy
    )
    states = ((), *one_states, *pairs)
    energy = {
        state.index: state.energy for state in one_particle.states
    }
    return tuple(
        sorted(
            states,
            key=lambda occupation: (
                sum(energy[index] for index in occupation),
                len(occupation),
                occupation,
            ),
        )
    )


def column_entries(matrix: sp.Matrix) -> dict[int, tuple[tuple[int, sp.Expr], ...]]:
    output: dict[int, list[tuple[int, sp.Expr]]] = defaultdict(list)
    for (row, column), value in sp.SparseMatrix(matrix).todok().items():
        if value != 0:
            output[column].append((row, value))
    return {column: tuple(entries) for column, entries in output.items()}


def second_quantize(matrix: sp.Matrix, basis: tuple[Occupation, ...]) -> sp.Matrix:
    """Return ``dGamma(matrix)`` on normalized occupation states."""

    basis_index = {occupation: index for index, occupation in enumerate(basis)}
    entries = column_entries(matrix)
    output: dict[tuple[int, int], sp.Expr] = {}
    for column, occupation in enumerate(basis):
        counts = Counter(occupation)
        for source, source_count in counts.items():
            for target, value in entries.get(source, ()):
                if target == source:
                    coefficient = source_count * value
                    result = occupation
                else:
                    target_count = counts.get(target, 0)
                    coefficient = sp.sqrt(source_count * (target_count + 1)) * value
                    result_list = list(occupation)
                    result_list.remove(source)
                    result_list.append(target)
                    result = tuple(sorted(result_list))
                row = basis_index.get(result)
                if row is None:
                    continue
                key = (row, column)
                output[key] = sp.simplify(output.get(key, 0) + coefficient)
                if output[key] == 0:
                    del output[key]
    return sp.SparseMatrix(len(basis), len(basis), output)


def occupation_energy(
    occupation: Occupation, one_particle: OneParticleModule
) -> int:
    energies = tuple(state.energy for state in one_particle.states)
    return sum(energies[index] for index in occupation)


def occupation_sign(
    occupation: Occupation, one_particle: OneParticleModule
) -> int:
    signs = tuple(state.sign for state in one_particle.states)
    result = 1
    for index in occupation:
        result *= signs[index]
    return result


def assemble_fock(max_energy: int = 4) -> FockModule:
    one_particle = assemble_one_particle(max_energy)
    basis = enumerate_fock_basis(one_particle, max_energy)
    state_energy = tuple(
        occupation_energy(occupation, one_particle) for occupation in basis
    )
    form = sp.diag(
        *(occupation_sign(occupation, one_particle) for occupation in basis),
        cls=sp.SparseMatrix,
    )
    compact = {
        label: second_quantize(matrix, basis)
        for label, matrix in one_particle.compact.items()
    }
    lowering = {
        component: second_quantize(matrix, basis)
        for component, matrix in one_particle.lowering.items()
    }
    raising = {
        component: second_quantize(matrix, basis)
        for component, matrix in one_particle.raising.items()
    }
    return FockModule(
        max_energy,
        one_particle,
        basis,
        state_energy,
        form,
        compact,
        lowering,
        raising,
    )


def fock_rotation(
    fock: FockModule,
    first: tuple[sp.Rational, sp.Rational],
    second: tuple[sp.Rational, sp.Rational],
) -> sp.Matrix:
    compact = tuple(
        fock.compact[label]
        for label in ("Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
    )
    output = sparse_zero(fock.dimension)
    for coefficient, generator in zip(
        finite.rotation_coefficients(first, second), compact
    ):
        if coefficient != 0:
            output += coefficient * generator
    return output


def verify_fock_inventory(fock: FockModule) -> None:
    counts = Counter(fock.state_energy)
    check(
        "C2g-F: complete matter inventory through energy four has dimensions 1,10,40,137",
        fock.max_energy == 4
        and counts == {0: 1, 2: 10, 3: 40, 4: 137}
        and fock.dimension == 188,
    )
    energy_four = [fock.basis[index] for index in fock.indices_at(4)]
    check(
        "C2g-F: energy four is 82 one-particle states plus Sym^2 of ten E2 states",
        sum(len(state) == 1 for state in energy_four) == 82
        and sum(len(state) == 2 for state in energy_four) == 55,
    )


def verify_fock_action(fock: FockModule) -> None:
    identity = sp.eye(fock.dimension, cls=sp.SparseMatrix)
    check(
        "C2g-F: induced Fock form is an exact involution",
        exact_matrix_equal(fock.form * fock.form, identity),
    )
    check(
        "C2g-F: second-quantized compact generators are J-Fock self-adjoint",
        all(
            exact_matrix_equal(
                generator.conjugate().T * fock.form,
                fock.form * generator,
            )
            for generator in fock.compact.values()
        ),
    )
    check(
        "C2g-F: second-quantized raising/lowering generators obey the J-Fock adjoint",
        all(
            exact_matrix_equal(
                fock.raising[component],
                fock.form * fock.lowering[component].conjugate().T * fock.form,
            )
            for component in MAGNETIC_COMPONENTS
        ),
    )
    energy = fock.compact["D"]
    check(
        "C2g-F: Fock proper-conformal generators have exact grades +/-1",
        all(
            exact_matrix_equal(energy * matrix - matrix * energy, -matrix)
            for matrix in fock.lowering.values()
        )
        and all(
            exact_matrix_equal(energy * matrix - matrix * energy, matrix)
            for matrix in fock.raising.values()
        ),
    )
    compact = fock.compact
    cyclic = (("x", "y", "z"), ("y", "z", "x"), ("z", "x", "y"))
    check(
        "C2g-F: second-quantized compact generators obey exact su(2)_L plus su(2)_R",
        all(
            exact_matrix_equal(
                compact[f"L{first}"] * compact[f"L{second}"]
                - compact[f"L{second}"] * compact[f"L{first}"],
                sp.I * compact[f"L{third}"],
            )
            and exact_matrix_equal(
                compact[f"R{first}"] * compact[f"R{second}"]
                - compact[f"R{second}"] * compact[f"R{first}"],
                sp.I * compact[f"R{third}"],
            )
            for first, second, third in cyclic
        )
        and all(
            exact_matrix_equal(
                compact[f"L{left}"] * compact[f"R{right}"]
                - compact[f"R{right}"] * compact[f"L{left}"],
                sparse_zero(fock.dimension),
            )
            for left, right in product(("x", "y", "z"), repeat=2)
        ),
    )
    check(
        "C2g-F: compact rotations commute exactly with Fock energy",
        all(
            exact_matrix_equal(
                energy * compact[label] - compact[label] * energy,
                sparse_zero(fock.dimension),
            )
            for label in ("Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
        ),
    )

    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        rotation = fock_rotation(fock, first, second)
        vector_action = finite.vector_rotation_matrix(first, second)
        for column, component in enumerate(MAGNETIC_COMPONENTS):
            expected = sparse_zero(fock.dimension)
            for row, target_component in enumerate(MAGNETIC_COMPONENTS):
                coefficient = vector_action[row, column]
                if coefficient != 0:
                    expected += coefficient * fock.lowering[target_component]
            actual = (
                rotation * fock.lowering[component]
                - fock.lowering[component] * rotation
            )
            if not exact_matrix_equal(actual, expected):
                raise AssertionError("Fock lowering SO(4) covariance failed")
    print("[OK ] C2g-F: Fock lowering family has exact SO(4) vector covariance")

    interior = tuple(
        index for index, value in enumerate(fock.state_energy) if value <= 3
    )
    zero = sparse_zero(fock.dimension)
    defects = []
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        left = (
            fock.lowering[first] * fock.raising[second]
            - fock.raising[second] * fock.lowering[first]
        )
        right = 2 * (energy if first == second else zero) + 2 * fock_rotation(
            fock, first, second
        )
        defects.append((left - right).extract(interior, interior))
    check(
        "C2g-F: exact SO(4,2) proper-conformal bracket closes on the complete Fock interior",
        all(exact_matrix_equal(defect, sparse_zero(defect.rows)) for defect in defects),
    )

    check(
        "C2g-F: second quantization preserves the commuting lowering algebra",
        all(
            exact_matrix_equal(
                fock.lowering[first] * fock.lowering[second]
                - fock.lowering[second] * fock.lowering[first],
                sparse_zero(fock.dimension),
            )
            for first, second in product(MAGNETIC_COMPONENTS, repeat=2)
        ),
    )
    raising_interior = tuple(
        index for index, value in enumerate(fock.state_energy) if value <= 2
    )
    check(
        "C2g-F: raising components commute on the complete two-step interior",
        all(
            exact_matrix_equal(
                (
                    fock.raising[first] * fock.raising[second]
                    - fock.raising[second] * fock.raising[first]
                ).extract(raising_interior, raising_interior),
                sparse_zero(len(raising_interior)),
            )
            for first, second in product(MAGNETIC_COMPONENTS, repeat=2)
        ),
    )


def expected_pair_singlet(fock: FockModule, chirality: int) -> sp.Matrix:
    """Normalized scalar in ``Sym^2(E2^chirality)``."""

    if chirality not in (-1, 1):
        raise ValueError("chirality must be +/-1")
    states = {
        state.magnetic: state.index
        for state in fock.one_particle.states
        if state.chirality == chirality and state.mode == "E2"
    }
    vector = sp.zeros(fock.dimension, 1)
    basis_index = fock.index
    spin_axis = 0 if chirality == 1 else 1
    for magnetic, state_index in states.items():
        m = magnetic[spin_axis]
        opposite = list(magnetic)
        opposite[spin_axis] = -m
        opposite_index = states[tuple(opposite)]
        occupation = tuple(sorted((state_index, opposite_index)))
        coefficient = sp.Integer(-1) ** int(2 - m)
        if state_index == opposite_index:
            coefficient *= sp.sqrt(2)
        vector[basis_index[occupation]] += coefficient
    norm = sp.simplify((vector.conjugate().T * vector)[0])
    return sp.simplify(vector / sp.sqrt(norm))


@dataclass(frozen=True)
class RelativeKernel:
    energy: int
    energy_indices: tuple[int, ...]
    inclusion: sp.Matrix
    plus_singlet: sp.Matrix
    minus_singlet: sp.Matrix


def relative_weight_four_kernel(fock: FockModule) -> RelativeKernel:
    energy_indices = fock.indices_at(4)
    rotations = tuple(
        fock.compact[label].extract(energy_indices, energy_indices)
        for label in ("Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
    )
    casimir = sum(
        (rotation * rotation for rotation in rotations),
        sparse_zero(len(energy_indices)),
    )
    rotation_kernel = casimir.nullspace()
    check(
        "C2g-F: exact compact Casimir has a two-dimensional energy-four singlet kernel",
        len(rotation_kernel) == 2
        and all(
            all(exact_matrix_equal(rotation * vector, sp.zeros(vector.rows, 1)) for rotation in rotations)
            for vector in rotation_kernel
        ),
    )

    plus = expected_pair_singlet(fock, 1)
    minus = expected_pair_singlet(fock, -1)
    expected_full = sp.Matrix.hstack(plus, minus)
    expected_restricted = expected_full.extract(energy_indices, (0, 1))
    computed = sp.Matrix.hstack(*rotation_kernel)
    check(
        "C2g-F: computed rotation kernel equals the two chiral E2-pair singlets",
        expected_restricted.rank() == 2
        and computed.rank() == 2
        and sp.Matrix.hstack(computed, expected_restricted).rank() == 2,
    )
    check(
        "C2g-F: both singlets have positive unit J-Fock norm and are mutually orthogonal",
        sp.simplify(expected_full.conjugate().T * fock.form * expected_full)
        == sp.eye(2),
    )
    check(
        "C2g-F: all four lowering generators annihilate the complete relative kernel",
        all(
            exact_matrix_equal(matrix * expected_full, sp.zeros(fock.dimension, 2))
            for matrix in fock.lowering.values()
        ),
    )
    check(
        "C2g-F: D acts with weight four on the complete relative kernel",
        exact_matrix_equal(
            fock.compact["D"] * expected_full, 4 * expected_full
        ),
    )
    return RelativeKernel(4, energy_indices, expected_full, plus, minus)


def residual_ghost_window_maps(
    fock: FockModule, relative: RelativeKernel
) -> dict[str, object]:
    """Expose exact graded maps without constructing absolute cohomology."""

    return {
        "matter_indices": {
            energy: fock.indices_at(energy) for energy in range(fock.max_energy + 1)
        },
        "compact_degree_zero": dict(fock.compact),
        "proper_lowering": dict(fock.lowering),
        "proper_raising": dict(fock.raising),
        "relative_inclusion": relative.inclusion,
        "relative_form": sp.simplify(
            relative.inclusion.conjugate().T
            * fock.form
            * relative.inclusion
        ),
        "generator_degrees": {
            **{label: 0 for label in fock.compact},
            **{f"K-_{component}": -1 for component in MAGNETIC_COMPONENTS},
            **{f"K+_{component}": 1 for component in MAGNETIC_COMPONENTS},
        },
    }


@dataclass(frozen=True)
class AbsoluteMatterWindow:
    """Matter maps adjacent to weight four, before tensoring with ghosts."""

    fock: FockModule
    dimensions: dict[int, int]
    outgoing_compact: dict[str, sp.Matrix]
    outgoing_lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    outgoing_raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    incoming_compact: dict[str, sp.Matrix]
    incoming_lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    incoming_raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]


def absolute_weight_four_matter_window() -> AbsoluteMatterWindow:
    """Build the matter blocks needed for one global-ghost action.

    A ghost paired with a generator of compact degree ``g`` has degree
    ``-g``.  Thus an absolute total-degree-four calculation needs matter
    energies three, four, and five.  This function supplies the exact maps
    among those spaces, but introduces no ghost exterior algebra.
    """

    fock = assemble_fock(5)
    dimensions = {
        energy: len(fock.indices_at(energy)) for energy in (3, 4, 5)
    }
    outgoing_compact = {
        label: fock.homogeneous_block(matrix, 4, 4)
        for label, matrix in fock.compact.items()
    }
    outgoing_lowering = {
        component: fock.homogeneous_block(matrix, 4, 3)
        for component, matrix in fock.lowering.items()
    }
    outgoing_raising = {
        component: fock.homogeneous_block(matrix, 4, 5)
        for component, matrix in fock.raising.items()
    }
    incoming_compact = dict(outgoing_compact)
    incoming_lowering = {
        component: fock.homogeneous_block(matrix, 5, 4)
        for component, matrix in fock.lowering.items()
    }
    incoming_raising = {
        component: fock.homogeneous_block(matrix, 3, 4)
        for component, matrix in fock.raising.items()
    }
    return AbsoluteMatterWindow(
        fock,
        dimensions,
        outgoing_compact,
        outgoing_lowering,
        outgoing_raising,
        incoming_compact,
        incoming_lowering,
        incoming_raising,
    )


def verify_absolute_matter_window(window: AbsoluteMatterWindow) -> None:
    fock = window.fock
    indices = {energy: fock.indices_at(energy) for energy in (3, 4, 5)}
    forms = {
        energy: fock.form.extract(index, index) for energy, index in indices.items()
    }
    check(
        "C2g-F: absolute one-ghost matter window has exact dimensions 40,137,536",
        window.dimensions == {3: 40, 4: 137, 5: 536}
        and fock.dimension == 724,
    )
    check(
        "C2g-F: outgoing 4->5 raising maps are J-adjoint to incoming 5->4 lowering maps",
        all(
            exact_matrix_equal(
                window.outgoing_raising[component],
                forms[5]
                * window.incoming_lowering[component].conjugate().T
                * forms[4],
            )
            for component in MAGNETIC_COMPONENTS
        ),
    )
    check(
        "C2g-F: outgoing 4->3 lowering maps are J-adjoint to incoming 3->4 raising maps",
        all(
            exact_matrix_equal(
                window.outgoing_lowering[component],
                forms[3]
                * window.incoming_raising[component].conjugate().T
                * forms[4],
            )
            for component in MAGNETIC_COMPONENTS
        ),
    )
    check(
        "C2g-F: degree-zero weight-four matter blocks remain J-self-adjoint",
        all(
            exact_matrix_equal(
                matrix.conjugate().T * forms[4], forms[4] * matrix
            )
            for matrix in window.outgoing_compact.values()
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-absolute-cohomology",
        action="store_true",
        help="fail closed: only exact matter maps for that window are exposed",
    )
    parser.add_argument(
        "--require-local-global-brst",
        action="store_true",
        help="fail closed: local Diff x Weyl ghosts are not combined here",
    )
    parser.add_argument(
        "--require-top-shell-closure",
        action="store_true",
        help="fail closed: total energy four is the top of this Fock buffer",
    )
    parser.add_argument(
        "--verify-absolute-window-inputs",
        action="store_true",
        help="also build and verify the matter E=3,4,5 blocks needed by one global-ghost action",
    )
    args = parser.parse_args()

    fock = assemble_fock(4)
    verify_fock_inventory(fock)
    verify_fock_action(fock)
    relative = relative_weight_four_kernel(fock)
    window = residual_ghost_window_maps(fock, relative)
    check(
        "C2g-F: reusable residual-window data expose all graded matter maps and the relative inclusion",
        window["relative_inclusion"].shape == (188, 2)
        and window["relative_form"] == sp.eye(2)
        and set(window["generator_degrees"].values()) == {-1, 0, 1},
    )
    if args.verify_absolute_window_inputs:
        verify_absolute_matter_window(absolute_weight_four_matter_window())

    print("Fock dimensions by energy:", dict(sorted(Counter(fock.state_energy).items())))
    print("relative weight-four dimension:", relative.inclusion.cols)
    print(
        "independent cross-check: C2g-N finds C3=0 and rank(d4)=53 on "
        "the 55-state global-only particle-number-two window, leaving the "
        "same two Weyl-square states"
    )
    print(
        "C2g-F STATUS: EXACT SECOND-QUANTIZED RELATIVE WEIGHT-FOUR RAIL. "
        "The complete pure-Weyl matter Fock space through energy four and "
        "its two-dimensional D=4,R=0,K-=0 kernel are certified. The "
        "independent C2g-N global-only absolute window retains the same two "
        "states; local-BV and local-plus-global physical cohomology are not "
        "claimed."
    )
    if args.require_absolute_cohomology:
        raise SystemExit(
            "absolute residual-ghost cohomology has not been constructed from the exposed maps"
        )
    if args.require_local_global_brst:
        raise SystemExit("the local Diff x Weyl BRST complex is not included")
    if args.require_top_shell_closure:
        raise SystemExit("top energy four requires the total-energy-five Fock buffer")


if __name__ == "__main__":
    main()
