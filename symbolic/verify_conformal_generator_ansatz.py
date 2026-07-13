#!/usr/bin/env python3
"""Exact C2f-A proper-conformal generator ansatz through source energy four.

This script reconstructs an actual one-particle *generator* ansatz, distinct
from the action-normalized Taub kernels of C2a--C2c.  There is one lowering
reduced coefficient for each parity orbit allowed through source energy four:

    E3->E2, A3->E2,
    E4->E3, A4->E3, A4->A3, L4->E3, L4->A3.

Independent raising coefficients are introduced first.  Exact SO(4,2)
commutators are imposed on energy-two and energy-three states, the largest
subspace whose two orderings are complete with lowering data only through
source energy four.  The convention is Hamada's cylinder convention

    [K^-_M,K^+_N] = 2 delta_MN D + 2 R_MN.

Writing the anti-Hermitian time generator as T=-iD converts the scalar term
to ``2 i delta_MN T``.  Reversing the commutator order changes the overall
sign.  No physics is hidden in this convention choice.

The solve fixes invariant lowering/raising products and two cross-family
relations, while five lowering parameters remain as independent basis
rescalings.  A general diagonal form then converts those products to exact
Gram-ratio equations.  In the canonical oscillator form

    eta_E=+1, eta_A=eta_L=-1,

all coefficients are fixed up to harmless mode phases.  Only after this step
are the two curvature Taub seeds compared through a separate relation

    M_kernel = lambda J K_generator.

They yield the same lambda.  The script never commutes the Taub kernels as if
they were generators.

Closure on source energy four itself would require the missing source-energy
five lowering blocks in the K^-K^+ ordering and therefore fails closed.

Hamada--Horata (hep-th/0307008, Eqs. 4.42, 4.60, 4.62--4.63) already give
the all-level traceless-mode oscillator charge.  This finite solve is an
independent convention and normalization audit whose new use is the bridge
to the separately computed C2a Taub kernels, not a priority claim for the
conformal-generator coefficients.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

import sympy as sp

try:
    from symbolic.verify_conformal_taub_multiplets import (
        HALF,
        MAGNETIC_COMPONENTS,
        R,
        Irrep,
        component_matrix,
        exact_matrix_equal,
        spin_operators,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_taub_multiplets import (
        HALF,
        MAGNETIC_COMPONENTS,
        R,
        Irrep,
        component_matrix,
        exact_matrix_equal,
        spin_operators,
    )


I = sp.I


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


@dataclass(frozen=True)
class GeneratorBlock:
    label: str
    source: str
    target: str


BLOCKS = (
    GeneratorBlock("a", "E3", "E2"),
    GeneratorBlock("b", "A3", "E2"),
    GeneratorBlock("c", "E4", "E3"),
    GeneratorBlock("d", "A4", "E3"),
    GeneratorBlock("e", "A4", "A3"),
    GeneratorBlock("f", "L4", "E3"),
    GeneratorBlock("g", "L4", "A3"),
)

LOWERING_SYMBOLS = sp.symbols("a b c d e f g", real=True, nonzero=True)
RAISING_SYMBOLS = sp.symbols("A B C D E F G", real=True, nonzero=True)


def irreps(chirality: int) -> tuple[Irrep, ...]:
    if chirality not in (-1, 1):
        raise ValueError("chirality must be +/-1")

    def oriented(label: str, energy: int, left: sp.Rational, right: sp.Rational) -> Irrep:
        return (
            Irrep(label, energy, left, right)
            if chirality == 1
            else Irrep(label, energy, right, left)
        )

    return (
        oriented("E2", 2, R(2), R(0)),
        oriented("E3", 3, R(5, 2), HALF),
        oriented("A3", 3, R(3, 2), HALF),
        oriented("E4", 4, R(3), R(1)),
        oriented("A4", 4, R(2), R(1)),
        oriented("L4", 4, R(2), R(0)),
    )


@dataclass(frozen=True)
class RepresentationSpace:
    chirality: int
    irreps: tuple[Irrep, ...]
    offsets: dict[str, int]
    dimension: int
    energy: sp.Matrix
    left: dict[str, sp.Matrix]
    right: dict[str, sp.Matrix]


def product_operator(irrep: Irrep, side: str, axis: str) -> sp.Matrix:
    spin = irrep.left if side == "left" else irrep.right
    z_axis, raising, lowering = spin_operators(spin)
    selected = {
        "x": (raising + lowering) / 2,
        "y": (raising - lowering) / (2 * I),
        "z": z_axis,
    }[axis]
    if side == "left":
        return sp.kronecker_product(
            selected, sp.eye(int(2 * irrep.right + 1))
        )
    return sp.kronecker_product(
        sp.eye(int(2 * irrep.left + 1)), selected
    )


def representation_space(chirality: int) -> RepresentationSpace:
    modes = irreps(chirality)
    offsets: dict[str, int] = {}
    cursor = 0
    for mode in modes:
        offsets[mode.label] = cursor
        cursor += mode.dimension
    energy = sp.diag(
        *(mode.energy for mode in modes for _ in range(mode.dimension))
    )
    left = {
        axis: sp.diag(*(product_operator(mode, "left", axis) for mode in modes))
        for axis in ("x", "y", "z")
    }
    right = {
        axis: sp.diag(*(product_operator(mode, "right", axis) for mode in modes))
        for axis in ("x", "y", "z")
    }
    return RepresentationSpace(
        chirality, modes, offsets, cursor, energy, left, right
    )


@dataclass(frozen=True)
class GeneratorAnsatz:
    lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]


def assemble_ansatz(
    space: RepresentationSpace,
    lowering_values: tuple[sp.Expr, ...],
    raising_values: tuple[sp.Expr, ...],
) -> GeneratorAnsatz:
    by_label = {mode.label: mode for mode in space.irreps}
    lowering = {
        component: sp.zeros(space.dimension) for component in MAGNETIC_COMPONENTS
    }
    raising = {
        component: sp.zeros(space.dimension) for component in MAGNETIC_COMPONENTS
    }
    for block, down, up in zip(BLOCKS, lowering_values, raising_values):
        source = by_label[block.source]
        target = by_label[block.target]
        row = space.offsets[target.label]
        column = space.offsets[source.label]
        for component in MAGNETIC_COMPONENTS:
            unit = component_matrix(source, target, component)
            lowering[component][
                row : row + target.dimension,
                column : column + source.dimension,
            ] = down * unit
            raising[component][
                column : column + source.dimension,
                row : row + target.dimension,
            ] = up * unit.conjugate().T
    return GeneratorAnsatz(lowering, raising)


def epsilon(component: tuple[sp.Rational, sp.Rational]) -> sp.Integer:
    return sp.Integer(-1) ** int(component[0] - component[1])


def negated(
    component: tuple[sp.Rational, sp.Rational],
) -> tuple[sp.Rational, sp.Rational]:
    return -component[0], -component[1]


def vector_rotation_matrix(
    first: tuple[sp.Rational, sp.Rational],
    second: tuple[sp.Rational, sp.Rational],
) -> sp.Matrix:
    """The action of R_(first,second) on the four-vector K^-_M.

    This is the exact spherical cylinder convention

      [R_AB,K^-_M] = -delta_MB K^-_A
                     +eps_A eps_B delta_M,-A K^-_-B.
    """

    output = sp.zeros(4)
    for column, component in enumerate(MAGNETIC_COMPONENTS):
        if component == second:
            output[MAGNETIC_COMPONENTS.index(first), column] -= 1
        if component == negated(first):
            output[
                MAGNETIC_COMPONENTS.index(negated(second)), column
            ] += epsilon(first) * epsilon(second)
    return output


def vector_spin_basis() -> tuple[sp.Matrix, ...]:
    z_axis, raising, lowering = spin_operators(HALF)
    axes = (
        (raising + lowering) / 2,
        (raising - lowering) / (2 * I),
        z_axis,
    )
    return tuple(
        [sp.kronecker_product(axis, sp.eye(2)) for axis in axes]
        + [sp.kronecker_product(sp.eye(2), axis) for axis in axes]
    )


@lru_cache(maxsize=None)
def rotation_coefficients(
    first: tuple[sp.Rational, sp.Rational],
    second: tuple[sp.Rational, sp.Rational],
) -> tuple[sp.Expr, ...]:
    unknowns = sp.symbols("rho0:6")
    target = vector_rotation_matrix(first, second)
    trial = sum(
        (unknown * basis for unknown, basis in zip(unknowns, vector_spin_basis())),
        sp.zeros(4),
    )
    solution = tuple(sp.linsolve(list(trial - target), unknowns))
    if len(solution) != 1:
        raise AssertionError("rotation tensor did not have a unique SO(4) decomposition")
    return solution[0]


def state_rotation(
    space: RepresentationSpace,
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
    return sum(
        (
            coefficient * generator
            for coefficient, generator in zip(
                rotation_coefficients(first, second), compact
            )
        ),
        sp.zeros(space.dimension),
    )


def retained_indices(space: RepresentationSpace) -> tuple[int, ...]:
    return tuple(
        index
        for mode in space.irreps
        if mode.energy <= 3
        for index in range(
            space.offsets[mode.label],
            space.offsets[mode.label] + mode.dimension,
        )
    )


def commutator_equations(
    space: RepresentationSpace, ansatz: GeneratorAnsatz
) -> tuple[sp.Expr, ...]:
    retained = retained_indices(space)
    equations: dict[str, sp.Expr] = {}
    zero = sp.zeros(space.dimension)
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        left = (
            ansatz.lowering[first] * ansatz.raising[second]
            - ansatz.raising[second] * ansatz.lowering[first]
        )
        right = 2 * (space.energy if first == second else zero) + 2 * state_rotation(
            space, first, second
        )
        difference = (left - right).extract(retained, retained)
        for entry in difference:
            value = sp.factor(entry)
            if value != 0:
                equations.setdefault(sp.srepr(value), value)
    return tuple(equations.values())


def solve_ansatz() -> dict[sp.Symbol, sp.Expr]:
    space = representation_space(1)
    ansatz = assemble_ansatz(space, LOWERING_SYMBOLS, RAISING_SYMBOLS)
    equations = commutator_equations(space, ansatz)
    solutions = sp.solve(
        equations,
        (*LOWERING_SYMBOLS, *RAISING_SYMBOLS),
        dict=True,
        simplify=False,
    )
    check("C2f-A: exact commutator equations have one nondegenerate solution family", len(solutions) == 1)
    solution = solutions[0]
    a, b, c, d, e, f, g = LOWERING_SYMBOLS
    A, B, C, D, E, F, G = RAISING_SYMBOLS
    expected = {
        b: sp.sqrt(6) * a * d / (2 * e),
        g: -2 * e * f / (3 * d),
        A: R(96, 5) / a,
        B: -16 * sp.sqrt(6) * e / (15 * a * d),
        C: 35 / c,
        D: -2 / d,
        E: 18 / e,
        F: -1 / f,
        G: -6 * d / (e * f),
    }
    check(
        "C2f-A: solver fixes exactly two lowering relations and all seven raising coefficients",
        set(solution) == set(expected)
        and all(sp.simplify(solution[key] - value) == 0 for key, value in expected.items()),
    )
    check(
        "C2f-A: five lowering coefficients remain as diagonal-basis rescalings",
        set(LOWERING_SYMBOLS) - set(solution) == {a, c, d, e, f},
    )
    check(
        "C2f-A: solved family satisfies every exact matrix equation",
        all(sp.simplify(equation.subs(solution)) == 0 for equation in equations),
    )
    return solution


PRODUCTS = {
    "a": R(96, 5),
    "b": -R(16, 5),
    "c": sp.Integer(35),
    "d": sp.Integer(-2),
    "e": sp.Integer(18),
    "f": sp.Integer(-1),
    "g": sp.Integer(4),
}


def invariant_product_checks(solution: dict[sp.Symbol, sp.Expr]) -> None:
    completed_lowering = tuple(solution.get(symbol, symbol) for symbol in LOWERING_SYMBOLS)
    completed_raising = tuple(solution[symbol] for symbol in RAISING_SYMBOLS)
    check(
        "C2f-A: all seven lowering-raising products are basis-invariant constants",
        all(
            sp.simplify(down * up - PRODUCTS[block.label]) == 0
            for block, down, up in zip(
                BLOCKS, completed_lowering, completed_raising
            )
        ),
    )


CANONICAL_LOWERING = (
    4 * sp.sqrt(R(6, 5)),
    4 / sp.sqrt(5),
    sp.sqrt(35),
    sp.sqrt(2),
    3 * sp.sqrt(2),
    -1,
    2,
)
CANONICAL_SIGNS = {
    "E2": 1,
    "E3": 1,
    "A3": -1,
    "E4": 1,
    "A4": -1,
    "L4": -1,
}


def canonical_raising() -> tuple[sp.Expr, ...]:
    return tuple(
        sp.simplify(
            sp.sympify(down)
            * sp.Integer(CANONICAL_SIGNS[block.target])
            / sp.Integer(CANONICAL_SIGNS[block.source])
        )
        for block, down in zip(BLOCKS, CANONICAL_LOWERING)
    )


def compact_covariance_checks(
    space: RepresentationSpace, ansatz: GeneratorAnsatz
) -> None:
    check(
        f"C2f-A: chirality {space.chirality:+d} lowering generators have grade -1",
        all(
            exact_matrix_equal(
                space.energy * matrix - matrix * space.energy, -matrix
            )
            for matrix in ansatz.lowering.values()
        ),
    )
    check(
        f"C2f-A: chirality {space.chirality:+d} raising generators have grade +1",
        all(
            exact_matrix_equal(
                space.energy * matrix - matrix * space.energy, matrix
            )
            for matrix in ansatz.raising.values()
        ),
    )
    for first, second in product(MAGNETIC_COMPONENTS, repeat=2):
        rotation = state_rotation(space, first, second)
        vector_action = vector_rotation_matrix(first, second)
        for kernels, sign_label in (
            (ansatz.lowering, "lowering"),
        ):
            for column, component in enumerate(MAGNETIC_COMPONENTS):
                expected = sp.zeros(space.dimension)
                for row, target_component in enumerate(MAGNETIC_COMPONENTS):
                    expected += vector_action[row, column] * kernels[target_component]
                check_value = (
                    rotation * kernels[component] - kernels[component] * rotation
                )
                if not exact_matrix_equal(check_value, expected):
                    raise AssertionError(
                        f"{sign_label} SO(4) tensor covariance failed"
                    )
    print(
        f"[OK ] C2f-A: chirality {space.chirality:+d} lowering family has exact SO(4) vector covariance"
    )


def canonical_algebra_checks() -> None:
    raising = canonical_raising()
    check(
        "C2f-A: canonical diagonal form converts lowering to the solved raising family",
        all(
            sp.simplify(down * up - PRODUCTS[block.label]) == 0
            for block, down, up in zip(BLOCKS, CANONICAL_LOWERING, raising)
        ),
    )
    for chirality in (1, -1):
        space = representation_space(chirality)
        ansatz = assemble_ansatz(space, CANONICAL_LOWERING, raising)
        compact_covariance_checks(space, ansatz)
        check(
            f"C2f-A: chirality {chirality:+d} canonical generators close on energies two and three",
            all(equation == 0 for equation in commutator_equations(space, ansatz)),
        )
        check(
            f"C2f-A: chirality {chirality:+d} known lowering blocks commute through source energy four",
            all(
                exact_matrix_equal(
                    ansatz.lowering[first] * ansatz.lowering[second]
                    - ansatz.lowering[second] * ansatz.lowering[first],
                    sp.zeros(space.dimension),
                )
                for first, second in product(MAGNETIC_COMPONENTS, repeat=2)
            ),
        )


@dataclass(frozen=True)
class TaubKernelSeed:
    block: str
    reduced_coefficient: sp.Expr


def kernel_normalization_checks() -> None:
    """Compare kernels only after supplying J and a global map lambda."""

    seeds = (
        TaubKernelSeed("b", -sp.sqrt(10) / (5 * sp.pi)),
        TaubKernelSeed("g", sp.sqrt(2) / (2 * sp.pi)),
    )
    coefficient = {
        block.label: value for block, value in zip(BLOCKS, CANONICAL_LOWERING)
    }
    target_sign = {block.label: CANONICAL_SIGNS[block.target] for block in BLOCKS}
    lambdas = tuple(
        sp.simplify(
            seed.reduced_coefficient
            / (target_sign[seed.block] * coefficient[seed.block])
        )
        for seed in seeds
    )
    check(
        "C2f-A: the two independent Taub seeds give one kernel-to-generator normalization",
        lambdas[0] == lambdas[1] == -sp.sqrt(2) / (4 * sp.pi),
    )

    # Without fixing canonical Gram magnitudes, the seed ratio determines
    # only eta_E2/eta_L4.  Algebra gives
    # (eta_E2*b/(eta_A3*g))^2=-(4/5) eta_E2/eta_L4.
    measured_ratio_squared = sp.simplify(
        (seeds[0].reduced_coefficient / seeds[1].reduced_coefficient) ** 2
    )
    inferred_e_to_l = sp.simplify(-R(5, 4) * measured_ratio_squared)
    check(
        "C2f-A: seed ratio fixes eta_E2/eta_L4=-1 before canonical magnitude normalization",
        measured_ratio_squared == R(4, 5) and inferred_e_to_l == -1,
    )

    # Freeze the actual highest-weight entries as well as their reduced
    # coefficients.  These are the two C2b curvature entries; keeping both
    # forms prevents a Clebsch--Gordan normalization from being silently
    # absorbed into the global kernel-to-generator scale.
    plus = {mode.label: mode for mode in irreps(1)}
    b_unit_entry = component_matrix(
        plus["A3"], plus["E2"], (HALF, -HALF)
    )[0, 0]
    g_unit_entry = component_matrix(
        plus["L4"], plus["A3"], (-HALF, HALF)
    )[0, 0]
    b_generator_entry = sp.simplify(coefficient["b"] * b_unit_entry)
    g_generator_entry = sp.simplify(coefficient["g"] * g_unit_entry)
    check(
        "C2f-A: canonical selected generator entries match both C2b seeds",
        b_unit_entry == 1 / sp.sqrt(2)
        and g_unit_entry == 2 / sp.sqrt(5)
        and b_generator_entry == 2 * sp.sqrt(10) / 5
        and g_generator_entry == 4 * sp.sqrt(5) / 5,
    )
    kernel_scale = lambdas[0]
    b_kernel_entry = sp.simplify(
        kernel_scale * CANONICAL_SIGNS["E2"] * b_generator_entry
    )
    g_kernel_entry = sp.simplify(
        kernel_scale * CANONICAL_SIGNS["A3"] * g_generator_entry
    )
    check(
        "C2f-A: M=lambda J K reproduces the two action-normalized curvature entries",
        b_kernel_entry == -sp.sqrt(5) / (5 * sp.pi)
        and g_kernel_entry == sp.sqrt(10) / (5 * sp.pi),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-energy-four-closure",
        action="store_true",
        help="fail closed: K^-K^+ on energy four needs source-energy-five blocks",
    )
    parser.add_argument(
        "--require-all-levels",
        action="store_true",
        help="fail closed: the ansatz is truncated at source energy four",
    )
    parser.add_argument(
        "--identify-taub-kernels-directly",
        action="store_true",
        help="fail closed: kernels require J and lambda before becoming generators",
    )
    args = parser.parse_args()

    solution = solve_ansatz()
    invariant_product_checks(solution)
    canonical_algebra_checks()
    kernel_normalization_checks()

    print("block order:", tuple(block.label for block in BLOCKS))
    print("canonical lowering coefficients:", CANONICAL_LOWERING)
    print("canonical raising coefficients:", canonical_raising())
    print("invariant lowering*raising products:", PRODUCTS)
    print("Taub-kernel map in canonical normalization: lambda=-sqrt(2)/(4*pi)")
    print(
        "C2f-A STATUS: EXACT SO(4,2) GENERATOR ANSATZ THROUGH SOURCE "
        "ENERGY FOUR. Closure is complete only on energies two and three. "
        "Five free lowering parameters are diagonal basis rescalings; a "
        "canonical (+E,-A,-L) form fixes them up to mode phases. Taub kernels "
        "are compared only through M=lambda J K."
    )
    if args.require_energy_four_closure:
        raise SystemExit(
            "energy-four K^-K^+ closure requires source-energy-five lowering blocks"
        )
    if args.require_all_levels:
        raise SystemExit("all-level conformal-generator recursion remains open")
    if args.identify_taub_kernels_directly:
        raise SystemExit(
            "refusing to identify action Taub kernels with generator matrices without J and lambda"
        )


if __name__ == "__main__":
    main()
