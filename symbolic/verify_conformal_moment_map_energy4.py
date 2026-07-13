#!/usr/bin/env python3
"""Exact C2f-M conformal moment-map jet through compact energy four.

The C2f-N oscillator certificate fixes the canonical one-particle form

    J = diag(+E,-A,-L),

while C2f-A fixes all seven parity-reduced proper-conformal generator blocks
whose source energy is at most four.  This script combines those independent
inputs.  On the 132-dimensional two-chirality buffer it constructs

* the cylinder Hamiltonian and six compact rotation generators;
* four lowering and four raising proper-conformal generators;
* their fifteen quadratic charge kernels ``M_X=J K_X``; and
* the corresponding Hamiltonian-vector identity for
  ``Omega=i d(zbar) J wedge dz``.

The energy-four space is a *buffer*, not a finite conformal representation.
All ``[K^-,K^+]`` brackets are exact on energies two and three, where both
operator orderings fit inside the buffer.  Closure on an energy-four source
would require the source-energy-five blocks.  The executable therefore calls
the result an energy-four moment-map jet and fails closed if full finite-cutoff
closure or physical BRST cohomology is requested.

In the canonical Condon--Shortley convention the raw C2a Euler/Bach kernels
are related to the lowering generators by

    M_Taub = lambda J K^-,   lambda=-sqrt(2)/(4 pi).

The block-independent quadratic Noether identity then predicts all seven
reduced coefficients through source energy four and reproduces the two
direct-curvature seeds.  It does not replace a direct curvature regression
of the implementation for the other five coefficients.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp

try:
    from symbolic import verify_conformal_generator_ansatz as generators
    from symbolic.verify_conformal_taub_multiplets import (
        HALF,
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_ansatz as generators
    from verify_conformal_taub_multiplets import (
        HALF,
        MAGNETIC_COMPONENTS,
        exact_matrix_equal,
    )


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def direct_sum(first: sp.Matrix, second: sp.Matrix) -> sp.Matrix:
    return sp.diag(first, second)


@dataclass(frozen=True)
class MomentMapJet:
    dimension: int
    plus: generators.RepresentationSpace
    minus: generators.RepresentationSpace
    form: sp.Matrix
    compact_generators: dict[str, sp.Matrix]
    lowering_generators: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising_generators: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    compact_kernels: dict[str, sp.Matrix]
    lowering_kernels: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising_kernels: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]


def canonical_form(space: generators.RepresentationSpace) -> sp.Matrix:
    blocks = []
    for mode in space.irreps:
        sign = 1 if mode.label.startswith("E") else -1
        blocks.append(sign * sp.eye(mode.dimension))
    return sp.diag(*blocks)


def assemble_jet() -> MomentMapJet:
    plus = generators.representation_space(1)
    minus = generators.representation_space(-1)
    raising_coefficients = generators.canonical_raising()
    plus_ansatz = generators.assemble_ansatz(
        plus, generators.CANONICAL_LOWERING, raising_coefficients
    )
    minus_ansatz = generators.assemble_ansatz(
        minus, generators.CANONICAL_LOWERING, raising_coefficients
    )

    form = direct_sum(canonical_form(plus), canonical_form(minus))
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
            plus_ansatz.lowering[component], minus_ansatz.lowering[component]
        )
        for component in MAGNETIC_COMPONENTS
    }
    raising = {
        component: direct_sum(
            plus_ansatz.raising[component], minus_ansatz.raising[component]
        )
        for component in MAGNETIC_COMPONENTS
    }
    compact_kernels = {label: form * matrix for label, matrix in compact.items()}
    lowering_kernels = {
        component: form * matrix for component, matrix in lowering.items()
    }
    raising_kernels = {
        component: form * matrix for component, matrix in raising.items()
    }
    return MomentMapJet(
        plus.dimension + minus.dimension,
        plus,
        minus,
        form,
        compact,
        lowering,
        raising,
        compact_kernels,
        lowering_kernels,
        raising_kernels,
    )


def verify_pairing_and_moment_identity(jet: MomentMapJet) -> None:
    identity = sp.eye(jet.dimension)
    check(
        "C2f-M: energy-four two-chirality buffer has dimension 132",
        jet.dimension == 132 and jet.form.shape == (132, 132),
    )
    check("C2f-M: canonical oscillator form is an exact involution", jet.form**2 == identity)

    all_generators = (
        *jet.compact_generators.values(),
        *jet.lowering_generators.values(),
        *jet.raising_generators.values(),
    )
    all_kernels = (
        *jet.compact_kernels.values(),
        *jet.lowering_kernels.values(),
        *jet.raising_kernels.values(),
    )
    check(
        "C2f-M: every quadratic kernel generates its declared Hamiltonian vector field",
        all(
            exact_matrix_equal(jet.form * kernel, generator)
            for generator, kernel in zip(all_generators, all_kernels)
        ),
    )
    check(
        "C2f-M: all seven compact charge kernels are Hermitian",
        all(kernel == kernel.conjugate().T for kernel in jet.compact_kernels.values()),
    )
    check(
        "C2f-M: raising charge kernels are the ordinary daggers of lowering kernels",
        all(
            jet.raising_kernels[component]
            == jet.lowering_kernels[component].conjugate().T
            for component in MAGNETIC_COMPONENTS
        ),
    )
    check(
        "C2f-M: the proper-conformal generators obey the J-adjoint relation",
        all(
            jet.raising_generators[component]
            == jet.form
            * jet.lowering_generators[component].conjugate().T
            * jet.form
            for component in MAGNETIC_COMPONENTS
        ),
    )


def verify_exact_interior_algebra(jet: MomentMapJet) -> None:
    # The detailed matrix equations and SO(4) tensor identities are generated
    # independently for each chirality by C2f-A.  Re-evaluate them here before
    # calling the combined kernels a moment-map jet.
    raising_coefficients = generators.canonical_raising()
    for chirality, space in ((1, jet.plus), (-1, jet.minus)):
        ansatz = generators.assemble_ansatz(
            space, generators.CANONICAL_LOWERING, raising_coefficients
        )
        check(
            f"C2f-M: chirality {chirality:+d} closes exactly on energies two and three",
            all(value == 0 for value in generators.commutator_equations(space, ansatz)),
        )
    check(
        "C2f-M: compact Hamiltonian is J-self-adjoint",
        jet.compact_generators["D"].conjugate().T * jet.form
        == jet.form * jet.compact_generators["D"],
    )
    check(
        "C2f-M: all six compact rotations are J-self-adjoint",
        all(
            matrix.conjugate().T * jet.form == jet.form * matrix
            for label, matrix in jet.compact_generators.items()
            if label != "D"
        ),
    )


def predicted_taub_coefficients() -> dict[str, sp.Expr]:
    target_sign = {
        block.label: generators.CANONICAL_SIGNS[block.target]
        for block in generators.BLOCKS
    }
    lam = -sp.sqrt(2) / (4 * sp.pi)
    return {
        block.label: sp.simplify(lam * target_sign[block.label] * coefficient)
        for block, coefficient in zip(
            generators.BLOCKS, generators.CANONICAL_LOWERING
        )
    }


def verify_taub_prediction() -> dict[str, sp.Expr]:
    coefficients = predicted_taub_coefficients()
    expected = {
        "a": -2 * sp.sqrt(15) / (5 * sp.pi),
        "b": -sp.sqrt(10) / (5 * sp.pi),
        "c": -sp.sqrt(70) / (4 * sp.pi),
        "d": -1 / (2 * sp.pi),
        "e": 3 / (2 * sp.pi),
        "f": sp.sqrt(2) / (4 * sp.pi),
        "g": sp.sqrt(2) / (2 * sp.pi),
    }
    check(
        "C2f-M: symplectic generator bridge fixes all seven raw Taub coefficients through energy four",
        coefficients == expected,
    )
    check(
        "C2f-M: the A3->E2 prediction reproduces the direct curvature seed",
        coefficients["b"] == -sp.sqrt(10) / (5 * sp.pi),
    )
    check(
        "C2f-M: the L4->A3 prediction reproduces the independent direct curvature seed",
        coefficients["g"] == sp.sqrt(2) / (2 * sp.pi),
    )
    return coefficients


def state_index(
    space: generators.RepresentationSpace,
    label: str,
    magnetic: tuple[sp.Rational, sp.Rational],
    global_offset: int,
) -> int:
    mode = next(mode for mode in space.irreps if mode.label == label)
    return global_offset + space.offsets[label] + mode.basis.index(magnetic)


def verify_seeded_cancellation_is_not_full(jet: MomentMapJet) -> None:
    """Revisit the four-mode C2b cancellation with all compact kernels present."""

    vector = sp.zeros(jet.dimension, 1)
    vector[state_index(jet.plus, "E2", (R(2), R(0)), 0)] = 1
    vector[state_index(jet.plus, "A3", (R(3, 2), HALF), 0)] = 1
    minus_offset = jet.plus.dimension
    vector[
        state_index(jet.minus, "A3", (HALF, R(3, 2)), minus_offset)
    ] = 1
    vector[
        state_index(jet.minus, "L4", (R(0), R(2)), minus_offset)
    ] = 1 / sp.sqrt(2)

    lowering_values = {
        component: sp.simplify(
            (vector.conjugate().T * kernel * vector)[0]
        )
        for component, kernel in jet.lowering_kernels.items()
    }
    compact_values = {
        label: sp.simplify((vector.conjugate().T * kernel * vector)[0])
        for label, kernel in jet.compact_kernels.items()
    }
    check(
        "C2f-M: the old four-mode vector still cancels every proper-CK lowering component",
        all(value == 0 for value in lowering_values.values()),
    )
    check(
        "C2f-M: that vector is not on the full fifteen-component zero locus",
        compact_values["D"] == -6 and compact_values["Rz"] == -3,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-energy-four-closure",
        action="store_true",
        help="fail closed: the top buffer needs source-energy-five blocks",
    )
    parser.add_argument(
        "--require-physical-cohomology",
        action="store_true",
        help="fail closed: a finite moment-map jet is not global BRST cohomology",
    )
    args = parser.parse_args()

    jet = assemble_jet()
    verify_pairing_and_moment_identity(jet)
    verify_exact_interior_algebra(jet)
    coefficients = verify_taub_prediction()
    verify_seeded_cancellation_is_not_full(jet)

    print("two-chirality buffer dimension:", jet.dimension)
    print("compact kernels:", tuple(jet.compact_kernels))
    print("proper-CK components:", MAGNETIC_COMPONENTS)
    print("predicted raw Taub reduced coefficients:", coefficients)
    print(
        "C2f-M STATUS: EXACT FIFTEEN-COMPONENT MOMENT-MAP JET THROUGH "
        "SOURCE ENERGY FOUR, WITH FULL ALGEBRA ON INTERIOR ENERGIES TWO "
        "AND THREE. The top cutoff is a buffer, not a finite conformal "
        "module; no global BRST cohomology or physical quotient is claimed."
    )
    if args.require_energy_four_closure:
        raise SystemExit(
            "energy-four closure requires the source-energy-five generator blocks"
        )
    if args.require_physical_cohomology:
        raise SystemExit(
            "the infinite energy-graded state action and local-plus-global BRST cohomology remain open"
        )


if __name__ == "__main__":
    main()
