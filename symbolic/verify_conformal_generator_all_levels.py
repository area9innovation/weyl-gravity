#!/usr/bin/env python3
"""C2g-A: cutoff-stable exact conformal oscillator representation.

The C2f-A certificate solved the proper-conformal generator through source
energy four.  This module encodes the resulting all-level Hamada--Horata
recursion on the three physical oscillator towers

    E_n,  n >= 2;       A_n,  n >= 3;       L_n,  n >= 4.

For either chirality the six stable lowering families are

    E_n -> E_(n-1),  A_n -> E_(n-1),  A_n -> A_(n-1),
    L_n -> E_(n-1),  L_n -> A_(n-1),  L_n -> L_(n-1).

Every block is the unique Condon--Shortley (1/2,1/2) intertwiner.  The
functions below expose the exact reduced coefficient at arbitrary source
energy and assemble a reusable finite *buffer* through ``max_energy``.

The buffer is not a finite representation.  Its SO(4,2) brackets are
complete on energies at most ``max_energy-1``; the top shell lacks the
raising blocks into ``max_energy+1``.  This is precisely the one-shell buffer
needed before a fixed-energy global-BRST kernel/image calculation.  The
script verifies the complete interior algebra and checks that the top-shell
defect is present rather than silently projecting it away.

The canonical one-particle form is

    J = diag(+1 on E, -1 on A and L),

and raising generators are constructed from the exact J-adjoint.  Taub
charge kernels remain separate objects ``M=lambda J K`` and are not used as
generator matrices here.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product

import sympy as sp

try:
    from symbolic import verify_conformal_generator_ansatz as finite
    from symbolic.verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        R,
        Irrep,
        component_matrix,
        exact_matrix_equal,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_ansatz as finite
    from verify_conformal_taub_multiplets import (
        MAGNETIC_COMPONENTS,
        R,
        Irrep,
        component_matrix,
        exact_matrix_equal,
    )


I = sp.I
BRANCHES = ("E", "A", "L")
BRANCH_MINIMUM = {"E": 2, "A": 3, "L": 4}
FORM_SIGN = {"E": 1, "A": -1, "L": -1}
FAMILIES = ("EE", "AE", "AA", "LE", "LA", "LL")


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def branch(label: str) -> str:
    if not label or label[0] not in BRANCHES:
        raise ValueError(f"unknown tower label {label}")
    return label[0]


def mode_irrep(branch_name: str, energy: int, chirality: int) -> Irrep:
    """Return one physical E/A/L irrep in exact half-integer notation."""

    if branch_name not in BRANCHES:
        raise ValueError(f"unknown branch {branch_name}")
    if chirality not in (-1, 1):
        raise ValueError("chirality must be +/-1")
    if energy < BRANCH_MINIMUM[branch_name]:
        raise ValueError(f"{branch_name}_{energy} is below its tower minimum")

    if branch_name == "E":
        left, right = R(energy, 2) + 1, R(energy, 2) - 1
    elif branch_name == "A":
        left, right = R(energy, 2), R(energy, 2) - 1
    else:
        left, right = R(energy, 2), R(energy, 2) - 2
    if chirality == -1:
        left, right = right, left
    return Irrep(f"{branch_name}{energy}", energy, left, right)


def tower_irreps(max_energy: int, chirality: int) -> tuple[Irrep, ...]:
    if max_energy < 3:
        raise ValueError("use max_energy >= 3")
    return tuple(
        mode_irrep(branch_name, energy, chirality)
        for energy in range(2, max_energy + 1)
        for branch_name in BRANCHES
        if energy >= BRANCH_MINIMUM[branch_name]
    )


def reduced_coefficient(family: str, source_energy: int) -> sp.Expr:
    """Canonical all-level lowering coefficient in the C2f-A phase choice."""

    n = sp.Integer(source_energy)
    minima = {"EE": 3, "AE": 3, "AA": 4, "LE": 4, "LA": 4, "LL": 5}
    if family not in minima:
        raise ValueError(f"unknown lowering family {family}")
    if source_energy < minima[family]:
        raise ValueError(f"family {family} begins at source energy {minima[family]}")

    squares = {
        "EE": 2 * (n - 1) * (n + 1) * (n + 3) / (n + 2),
        "AE": 8 * (n - 1) / ((n - 2) * (n + 2)),
        "AA": 2 * (n - 3) * (n - 1) * (n + 2) / (n - 2),
        "LE": 2 * (n - 3) / (n - 2),
        "LA": 8 / (n - 2),
        "LL": 2 * (n - 2) * (n + 1),
    }
    phase = -1 if family == "LE" else 1
    return sp.simplify(phase * sp.sqrt(squares[family]))


@dataclass(frozen=True)
class LevelBlock:
    family: str
    source: str
    target: str
    source_energy: int
    coefficient: sp.Expr


def lowering_blocks(max_energy: int) -> tuple[LevelBlock, ...]:
    output: list[LevelBlock] = []
    for energy in range(3, max_energy + 1):
        for family in FAMILIES:
            source_branch, target_branch = family
            if energy < BRANCH_MINIMUM[source_branch]:
                continue
            if energy - 1 < BRANCH_MINIMUM[target_branch]:
                continue
            output.append(
                LevelBlock(
                    family,
                    f"{source_branch}{energy}",
                    f"{target_branch}{energy - 1}",
                    energy,
                    reduced_coefficient(family, energy),
                )
            )
    return tuple(output)


def product_operator(irrep: Irrep, side: str, axis: str) -> sp.Matrix:
    return finite.product_operator(irrep, side, axis)


def direct_sum(blocks: tuple[sp.Matrix, ...]) -> sp.Matrix:
    return (
        sp.diag(*blocks, cls=sp.SparseMatrix)
        if blocks
        else sp.SparseMatrix(0, 0, {})
    )


@dataclass(frozen=True)
class CutoffRepresentation:
    max_energy: int
    chirality: int
    irreps: tuple[Irrep, ...]
    offsets: dict[str, int]
    dimension: int
    energy: sp.Matrix
    left: dict[str, sp.Matrix]
    right: dict[str, sp.Matrix]
    form: sp.Matrix
    lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]

    def indices_through(self, energy: int) -> tuple[int, ...]:
        return tuple(
            index
            for mode in self.irreps
            if mode.energy <= energy
            for index in range(
                self.offsets[mode.label],
                self.offsets[mode.label] + mode.dimension,
            )
        )

    def indices_at(self, energy: int) -> tuple[int, ...]:
        return tuple(
            index
            for mode in self.irreps
            if mode.energy == energy
            for index in range(
                self.offsets[mode.label],
                self.offsets[mode.label] + mode.dimension,
            )
        )

    @property
    def interior_energy(self) -> int:
        return self.max_energy - 1


def representation_space(max_energy: int, chirality: int) -> CutoffRepresentation:
    modes = tower_irreps(max_energy, chirality)
    offsets: dict[str, int] = {}
    cursor = 0
    for mode in modes:
        offsets[mode.label] = cursor
        cursor += mode.dimension

    energy = sp.diag(
        *(mode.energy for mode in modes for _ in range(mode.dimension)),
        cls=sp.SparseMatrix,
    )
    left = {
        axis: direct_sum(tuple(product_operator(mode, "left", axis) for mode in modes))
        for axis in ("x", "y", "z")
    }
    right = {
        axis: direct_sum(tuple(product_operator(mode, "right", axis) for mode in modes))
        for axis in ("x", "y", "z")
    }
    form = direct_sum(
        tuple(FORM_SIGN[branch(mode.label)] * sp.eye(mode.dimension) for mode in modes)
    )

    lowering = {
        component: sp.MutableSparseMatrix(cursor, cursor, {})
        for component in MAGNETIC_COMPONENTS
    }
    raising = {
        component: sp.MutableSparseMatrix(cursor, cursor, {})
        for component in MAGNETIC_COMPONENTS
    }
    by_label = {mode.label: mode for mode in modes}
    for block in lowering_blocks(max_energy):
        source = by_label[block.source]
        target = by_label[block.target]
        row = offsets[target.label]
        column = offsets[source.label]
        target_sign = FORM_SIGN[branch(target.label)]
        source_sign = FORM_SIGN[branch(source.label)]
        raising_coefficient = sp.simplify(
            block.coefficient * sp.Integer(target_sign) / sp.Integer(source_sign)
        )
        for component in MAGNETIC_COMPONENTS:
            unit = component_matrix(source, target, component)
            lowering[component][
                row : row + target.dimension,
                column : column + source.dimension,
            ] = block.coefficient * unit
            raising[component][
                column : column + source.dimension,
                row : row + target.dimension,
            ] = raising_coefficient * unit.conjugate().T

    return CutoffRepresentation(
        max_energy,
        chirality,
        modes,
        offsets,
        cursor,
        energy,
        left,
        right,
        form,
        lowering,
        raising,
    )


def as_finite_space(space: CutoffRepresentation) -> finite.RepresentationSpace:
    """Adapter for the independently verified compact-generator routines."""

    return finite.RepresentationSpace(
        space.chirality,
        space.irreps,
        space.offsets,
        space.dimension,
        space.energy,
        space.left,
        space.right,
    )


def state_rotation(
    space: CutoffRepresentation,
    first: tuple[sp.Rational, sp.Rational],
    second: tuple[sp.Rational, sp.Rational],
) -> sp.Matrix:
    compact = (
        space.left["x"],
        space.left["y"],
        space.left["z"],
        space.right["x"],
        space.right["y"],
        space.right["z"],
    )
    output = sp.SparseMatrix(space.dimension, space.dimension, {})
    for coefficient, generator in zip(
        finite.rotation_coefficients(first, second), compact
    ):
        if coefficient != 0:
            output += coefficient * generator
    return output


def restricted_zero(matrix: sp.Matrix, indices: tuple[int, ...]) -> bool:
    return exact_matrix_equal(
        matrix.extract(indices, indices), sp.zeros(len(indices))
    )


def interior_bracket_defects(space: CutoffRepresentation) -> tuple[sp.Matrix, ...]:
    indices = space.indices_through(space.interior_energy)
    zero = sp.SparseMatrix(space.dimension, space.dimension, {})
    output: list[sp.Matrix] = []
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        left = (
            space.lowering[first] * space.raising[second]
            - space.raising[second] * space.lowering[first]
        )
        right = 2 * (space.energy if first == second else zero) + 2 * state_rotation(
            space, first, second
        )
        output.append((left - right).extract(indices, indices))
    return tuple(output)


def top_shell_bracket_defects(space: CutoffRepresentation) -> tuple[sp.Matrix, ...]:
    indices = space.indices_at(space.max_energy)
    zero = sp.SparseMatrix(space.dimension, space.dimension, {})
    output: list[sp.Matrix] = []
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        left = (
            space.lowering[first] * space.raising[second]
            - space.raising[second] * space.lowering[first]
        )
        right = 2 * (space.energy if first == second else zero) + 2 * state_rotation(
            space, first, second
        )
        output.append((left - right).extract(indices, indices))
    return tuple(output)


def verify_formulas_against_c2f() -> None:
    values = {
        ("EE", 3): 4 * sp.sqrt(R(6, 5)),
        ("AE", 3): 4 / sp.sqrt(5),
        ("EE", 4): sp.sqrt(35),
        ("AE", 4): sp.sqrt(2),
        ("AA", 4): 3 * sp.sqrt(2),
        ("LE", 4): -1,
        ("LA", 4): 2,
    }
    check(
        "C2g-A: all-level formulas reproduce every C2f-A coefficient through energy four",
        all(
            sp.simplify(reduced_coefficient(family, energy) - expected) == 0
            for (family, energy), expected in values.items()
        ),
    )


def verify_compact_covariance(space: CutoffRepresentation) -> None:
    """Check the complete spherical SO(4) tensor law with sparse matrices."""

    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        rotation = state_rotation(space, first, second)
        vector_action = finite.vector_rotation_matrix(first, second)
        for column, component in enumerate(MAGNETIC_COMPONENTS):
            expected = sp.SparseMatrix(space.dimension, space.dimension, {})
            for row, target_component in enumerate(MAGNETIC_COMPONENTS):
                coefficient = vector_action[row, column]
                if coefficient != 0:
                    expected += coefficient * space.lowering[target_component]
            actual = (
                rotation * space.lowering[component]
                - space.lowering[component] * rotation
            )
            if not exact_matrix_equal(actual, expected):
                raise AssertionError("lowering SO(4) tensor covariance failed")
    print(
        f"[OK ] C2g-A: chirality {space.chirality:+d} lowering family has exact SO(4) vector covariance"
    )


def verify_representation(space: CutoffRepresentation) -> None:
    identity = sp.eye(space.dimension, cls=sp.SparseMatrix)
    check(
        f"C2g-A: chirality {space.chirality:+d} canonical form is an exact involution",
        exact_matrix_equal(space.form * space.form, identity),
    )
    check(
        f"C2g-A: chirality {space.chirality:+d} lowering family has compact grade -1",
        all(
            exact_matrix_equal(
                space.energy * matrix - matrix * space.energy, -matrix
            )
            for matrix in space.lowering.values()
        ),
    )
    check(
        f"C2g-A: chirality {space.chirality:+d} raising family has compact grade +1",
        all(
            exact_matrix_equal(
                space.energy * matrix - matrix * space.energy, matrix
            )
            for matrix in space.raising.values()
        ),
    )
    check(
        f"C2g-A: chirality {space.chirality:+d} exact J-adjoint relates every raising/lowering component",
        all(
            exact_matrix_equal(
                space.raising[component],
                space.form * space.lowering[component].conjugate().T * space.form,
            )
            for component in MAGNETIC_COMPONENTS
        ),
    )
    check(
        f"C2g-A: chirality {space.chirality:+d} compact generators are J-self-adjoint",
        all(
            exact_matrix_equal(generator.conjugate().T * space.form, space.form * generator)
            for generator in (
                space.energy,
                *space.left.values(),
                *space.right.values(),
            )
        ),
    )

    verify_compact_covariance(space)
    check(
        f"C2g-A: chirality {space.chirality:+d} exact [K-,K+] algebra closes through energy {space.interior_energy}",
        all(exact_matrix_equal(defect, sp.zeros(defect.rows)) for defect in interior_bracket_defects(space)),
    )
    check(
        f"C2g-A: chirality {space.chirality:+d} lowering components commute through source energy {space.max_energy}",
        all(
            exact_matrix_equal(
                space.lowering[first] * space.lowering[second]
                - space.lowering[second] * space.lowering[first],
                sp.SparseMatrix(space.dimension, space.dimension, {}),
            )
            for first, second in product(MAGNETIC_COMPONENTS, repeat=2)
        ),
    )

    raising_interior = space.indices_through(space.max_energy - 2)
    check(
        f"C2g-A: chirality {space.chirality:+d} raising components commute on their complete interior",
        all(
            restricted_zero(
                space.raising[first] * space.raising[second]
                - space.raising[second] * space.raising[first],
                raising_interior,
            )
            for first, second in product(MAGNETIC_COMPONENTS, repeat=2)
        ),
    )
    top_defects = top_shell_bracket_defects(space)
    check(
        f"C2g-A: chirality {space.chirality:+d} top-shell omission is explicitly detected",
        any(not exact_matrix_equal(defect, sp.zeros(defect.rows)) for defect in top_defects),
    )


def first_brst_buffer(target_energy: int) -> int:
    """One-particle cutoff needed for one action of a grade +/-1 generator."""

    if target_energy < 2:
        raise ValueError("target energy must be at least two")
    return target_energy + 1


def expected_level_dimension(energy: int) -> int:
    """Dimension of one chirality at a fixed compact energy."""

    if energy < 2:
        return 0
    e_dimension = (energy + 3) * (energy - 1)
    a_dimension = energy**2 - 1 if energy >= 3 else 0
    l_dimension = (energy + 1) * (energy - 3) if energy >= 4 else 0
    return e_dimension + a_dimension + l_dimension


def expected_cumulative_dimension(max_energy: int) -> int:
    return sum(expected_level_dimension(energy) for energy in range(2, max_energy + 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-energy",
        type=int,
        default=5,
        help="one-particle buffer cutoff; brackets close through one lower energy",
    )
    parser.add_argument(
        "--require-top-shell-closure",
        action="store_true",
        help="fail closed: the top shell needs one more oscillator level",
    )
    parser.add_argument(
        "--require-infinite-module",
        action="store_true",
        help="fail closed: a finite buffer is not the all-level Hilbert-space domain",
    )
    parser.add_argument(
        "--require-fock-brst-cohomology",
        action="store_true",
        help="fail closed: this supplies the one-particle action, not its Fock/ghost cohomology",
    )
    args = parser.parse_args()
    if args.max_energy < 5:
        raise SystemExit(
            "use --max-energy >=5: energy five is the first extension beyond C2f-A"
        )

    verify_formulas_against_c2f()
    spaces = tuple(representation_space(args.max_energy, chirality) for chirality in (1, -1))
    for space in spaces:
        verify_representation(space)

    expected_blocks = 7 + 6 * (args.max_energy - 4)
    check(
        "C2g-A: exact all-level inventory contains six new parity-reduced blocks per added energy",
        len(lowering_blocks(args.max_energy)) == expected_blocks,
    )
    check(
        "C2g-A: cutoff dimensions match the independent E/A/L character inventory",
        all(
            space.dimension == expected_cumulative_dimension(args.max_energy)
            for space in spaces
        )
        and expected_level_dimension(5) == 68
        and expected_level_dimension(6) == 101
        and expected_cumulative_dimension(6) == 235,
    )
    check(
        "C2g-A: an energy-five buffer is sufficient for the first energy-four one-particle BRST action",
        first_brst_buffer(4) == 5 and args.max_energy >= first_brst_buffer(4),
    )

    print("buffer cutoff:", args.max_energy)
    print("complete bracket interior: energies 2 through", args.max_energy - 1)
    print("dimension per chirality:", spaces[0].dimension)
    print("parity-reduced lowering blocks:", len(lowering_blocks(args.max_energy)))
    print(
        "C2g-A STATUS: EXACT CUTOFF-STABLE ONE-PARTICLE SO(4,2) ACTION. "
        "The all-level reduced coefficients are encoded; the finite buffer "
        "closes exactly one shell below its cutoff and exposes its top-shell "
        "defect. This is generator data for a global-BRST calculation, not "
        "the Fock/ghost kernel or cohomology itself."
    )
    if args.require_top_shell_closure:
        raise SystemExit(
            f"top energy {args.max_energy} requires source-energy {args.max_energy + 1} blocks"
        )
    if args.require_infinite_module:
        raise SystemExit("a finite cutoff buffer does not certify the unbounded module domain")
    if args.require_fock_brst_cohomology:
        raise SystemExit(
            "the second-quantized oscillator-plus-ghost BRST kernel/image remains a separate calculation"
        )


if __name__ == "__main__":
    main()
