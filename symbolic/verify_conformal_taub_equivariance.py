#!/usr/bin/env python3
"""Exact C2c-E covariance rail for the reconstructed Taub kernels.

The C2a/C2b certificates reconstruct four proper-conformal lowering kernels
``M^-_(q_L,q_R)`` on the 36-dimensional low-mode oscillator sum.  They are
coefficients of quadratic functions

    mu^-_q(z, zbar) = zbar M^-_q z,

not yet Hamiltonian conformal-generator matrices.  This rail verifies the
partial coadjoint-equivariance identities under the *known* compact
``SU(2)_L x SU(2)_R`` oscillator generators and the cylinder Hamiltonian
``D``.  It also constructs the conjugate raising kernels and canonical exact
quadratic polynomials.

No symplectic/Krein form has been supplied that would turn a kernel ``M``
into a Hamiltonian vector-field generator.  Consequently the proper-
conformal commutator, the seven Killing kernels, other tower blocks, and the
global BRST complex remain open.  Dedicated command-line switches fail
closed for each of those missing claims.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp

try:
    from symbolic import verify_conformal_taub_multiplets as multiplets
except ImportError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_taub_multiplets as multiplets


I = sp.I
R = sp.Rational
HALF = R(1, 2)
COMPONENTS = multiplets.MAGNETIC_COMPONENTS


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def exact_matrix_equal(first: sp.Matrix, second: sp.Matrix) -> bool:
    return multiplets.exact_matrix_equal(first, second)


@dataclass(frozen=True)
class KernelBundle:
    """Bilinear moment kernels, deliberately not oscillator generators."""

    lowering: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]
    raising: dict[tuple[sp.Rational, sp.Rational], sp.Matrix]

    @property
    def dimension(self) -> int:
        return next(iter(self.lowering.values())).rows


@dataclass(frozen=True)
class CompactStateGenerators:
    """The actual reconstructed action of D and compact rotations on z."""

    energy: sp.Matrix
    left: dict[str, sp.Matrix]
    right: dict[str, sp.Matrix]


def reconstruct_kernel_bundle() -> KernelBundle:
    seed_component = (HALF, -HALF)
    ea = multiplets.reconstruct(
        multiplets.Seed(
            "C2c-E A+ -> E+",
            multiplets.A_PLUS,
            multiplets.E_PLUS,
            (R(3, 2), HALF),
            (R(2), R(0)),
            seed_component,
            multiplets.charge_from_slice(-1, reverse=False),
        )
    )
    al = multiplets.reconstruct(
        multiplets.Seed(
            "C2c-E L- -> A-",
            multiplets.L_MINUS,
            multiplets.A_MINUS,
            (R(0), R(2)),
            (HALF, R(3, 2)),
            seed_component,
            multiplets.charge_from_slice(-1, reverse=True),
        )
    )
    parity_component = (-HALF, HALF)
    ea_parity = multiplets.reconstruct(
        multiplets.Seed(
            "C2c-E A- -> E- (parity)",
            multiplets.A_MINUS,
            multiplets.E_MINUS,
            (HALF, R(3, 2)),
            (R(0), R(2)),
            parity_component,
            multiplets.charge_from_slice(
                -1, reverse=False, parity=True
            ),
        )
    )
    al_parity = multiplets.reconstruct(
        multiplets.Seed(
            "C2c-E L+ -> A+ (parity)",
            multiplets.L_PLUS,
            multiplets.A_PLUS,
            (R(2), R(0)),
            (R(3, 2), HALF),
            parity_component,
            multiplets.charge_from_slice(
                -1, reverse=True, parity=True
            ),
        )
    )
    lowering = multiplets.low_energy_kernels(
        (ea, ea_parity, al_parity, al)
    )
    # Spherical-tensor conjugation carries the standard product phase
    # (-1)^(1-q_L-q_R).  With that phase the dagger family transforms in the
    # same (1/2,1/2) Condon--Shortley basis as the lowering family.
    raising = {
        component: conjugation_phase(component)
        * lowering[(-component[0], -component[1])].conjugate().T
        for component in COMPONENTS
    }
    return KernelBundle(lowering, raising)


def conjugation_phase(
    component: tuple[sp.Rational, sp.Rational],
) -> sp.Integer:
    exponent = int(1 - component[0] - component[1])
    return sp.Integer(-1) ** exponent


def axis_operators(
    spin: sp.Rational,
) -> dict[str, sp.Matrix]:
    z_axis, raising, lowering = multiplets.spin_operators(spin)
    return {
        "x": sp.simplify((raising + lowering) / 2),
        "y": sp.simplify((raising - lowering) / (2 * I)),
        "z": z_axis,
        "+": raising,
        "-": lowering,
    }


def compact_state_generators() -> CompactStateGenerators:
    dimension = sum(irrep.dimension for irrep in multiplets.LOW_IRREPS)
    energy = sp.diag(
        *(
            sp.Integer(irrep.energy)
            for irrep in multiplets.LOW_IRREPS
            for _ in range(irrep.dimension)
        )
    )

    def direct_sum(side: str, axis: str) -> sp.Matrix:
        blocks = []
        for irrep in multiplets.LOW_IRREPS:
            spin = irrep.left if side == "left" else irrep.right
            local = axis_operators(spin)[axis]
            if side == "left":
                blocks.append(
                    sp.kronecker_product(
                        local, sp.eye(int(2 * irrep.right + 1))
                    )
                )
            else:
                blocks.append(
                    sp.kronecker_product(
                        sp.eye(int(2 * irrep.left + 1)), local
                    )
                )
        return sp.diag(*blocks) if blocks else sp.zeros(dimension)

    left = {axis: direct_sum("left", axis) for axis in ("x", "y", "z")}
    right = {axis: direct_sum("right", axis) for axis in ("x", "y", "z")}
    return CompactStateGenerators(energy, left, right)


def tensor_axis(side: str, axis: str) -> sp.Matrix:
    half = axis_operators(HALF)[axis]
    identity = sp.eye(2)
    if side == "left":
        return sp.kronecker_product(half, identity)
    if side == "right":
        return sp.kronecker_product(identity, half)
    raise ValueError(side)


def expected_tensor_transform(
    kernels: dict[tuple[sp.Rational, sp.Rational], sp.Matrix],
    side: str,
    axis: str,
    component: tuple[sp.Rational, sp.Rational],
) -> sp.Matrix:
    tensor = tensor_axis(side, axis)
    column = COMPONENTS.index(component)
    output = sp.zeros(next(iter(kernels.values())).rows)
    for row, target_component in enumerate(COMPONENTS):
        output += tensor[row, column] * kernels[target_component]
    return sp.simplify(output)


def verify_compact_representations(generators: CompactStateGenerators) -> None:
    check(
        "C2c-E: oscillator left compact generators obey su(2)",
        exact_matrix_equal(
            generators.left["x"] * generators.left["y"]
            - generators.left["y"] * generators.left["x"],
            I * generators.left["z"],
        ),
    )
    check(
        "C2c-E: oscillator right compact generators obey su(2)",
        exact_matrix_equal(
            generators.right["x"] * generators.right["y"]
            - generators.right["y"] * generators.right["x"],
            I * generators.right["z"],
        ),
    )
    check(
        "C2c-E: left and right compact actions commute",
        all(
            exact_matrix_equal(
                generators.left[left_axis] * generators.right[right_axis]
                - generators.right[right_axis] * generators.left[left_axis],
                sp.zeros(generators.energy.rows),
            )
            for left_axis in ("x", "y", "z")
            for right_axis in ("x", "y", "z")
        ),
    )
    check(
        "C2c-E: D commutes with the compact rotation representation",
        all(
            exact_matrix_equal(
                generators.energy * rotation
                - rotation * generators.energy,
                sp.zeros(generators.energy.rows),
            )
            for rotation in (*generators.left.values(), *generators.right.values())
        ),
    )


def verify_partial_coadjoint_equivariance(
    bundle: KernelBundle, generators: CompactStateGenerators
) -> None:
    """Check delta_X mu_a=(ad*_X mu)_a at the kernel level.

    For a compact Hermitian oscillator generator J, use

        delta z=-i J z,
        delta zbar=+i zbar J.

    Hence ``delta mu_M=i zbar[J,M]z``.  The checks below show that this is
    exactly the spin-(1/2,1/2) coadjoint/tensor action on the four kernels.
    """

    for signed_grade, kernels in ((-1, bundle.lowering), (1, bundle.raising)):
        check(
            f"C2c-E: grade {signed_grade:+d} kernels have exact D coadjoint grading",
            all(
                exact_matrix_equal(
                    I
                    * (
                        generators.energy * matrix
                        - matrix * generators.energy
                    ),
                    I * signed_grade * matrix,
                )
                for matrix in kernels.values()
            ),
        )
        for side, rotations in (
            ("left", generators.left),
            ("right", generators.right),
        ):
            for axis in ("x", "y", "z"):
                check(
                    f"C2c-E: grade {signed_grade:+d} {side} J{axis} coadjoint equivariance",
                    all(
                        exact_matrix_equal(
                            I
                            * (
                                rotations[axis] * matrix
                                - matrix * rotations[axis]
                            ),
                            I
                            * expected_tensor_transform(
                                kernels, side, axis, component
                            ),
                        )
                        for component, matrix in kernels.items()
                    ),
                )


def coordinate_label(
    irrep: multiplets.Irrep,
    magnetic: tuple[sp.Rational, sp.Rational],
) -> str:
    def encode(value: sp.Rational) -> str:
        doubled = int(2 * value)
        if doubled > 0:
            return f"p{doubled}h"
        if doubled < 0:
            return f"m{-doubled}h"
        return "0"

    family = irrep.label.replace("+", "p").replace("-", "m")
    return f"{family}_L{encode(magnetic[0])}_R{encode(magnetic[1])}"


def oscillator_coordinates() -> tuple[list[sp.Symbol], list[sp.Symbol]]:
    names = [
        coordinate_label(irrep, magnetic)
        for irrep in multiplets.LOW_IRREPS
        for magnetic in irrep.basis
    ]
    coordinates = [sp.Symbol("z_" + name) for name in names]
    duals = [sp.Symbol("zb_" + name) for name in names]
    return coordinates, duals


def quadratic_polynomial(
    matrix: sp.Matrix,
    coordinates: list[sp.Symbol],
    duals: list[sp.Symbol],
) -> sp.Expr:
    terms = [
        sp.simplify(duals[row] * value * coordinates[column])
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if (value := matrix[row, column]) != 0
    ]
    return sp.Add(*terms)


def verify_canonical_polynomials(bundle: KernelBundle) -> dict[
    tuple[sp.Rational, sp.Rational], sp.Expr
]:
    coordinates, duals = oscillator_coordinates()
    polynomials = {
        component: quadratic_polynomial(matrix, coordinates, duals)
        for component, matrix in bundle.lowering.items()
    }
    check(
        "C2c-E: every seeded proper-CK lowering polynomial has 16 exact monomials",
        all(len(sp.Add.make_args(polynomial)) == 16 for polynomial in polynomials.values()),
    )

    offsets: dict[str, int] = {}
    cursor = 0
    for irrep in multiplets.LOW_IRREPS:
        offsets[irrep.label] = cursor
        cursor += irrep.dimension

    def index(
        irrep: multiplets.Irrep,
        magnetic: tuple[sp.Rational, sp.Rational],
    ) -> int:
        return offsets[irrep.label] + irrep.basis.index(magnetic)

    component = (HALF, -HALF)
    seed_matrix = bundle.lowering[component]
    check(
        "C2c-E: seeded polynomial retains both direct action-normalized coefficients",
        seed_matrix[
            index(multiplets.E_PLUS, (R(2), R(0))),
            index(multiplets.A_PLUS, (R(3, 2), HALF)),
        ]
        == -sp.sqrt(5) / (5 * sp.pi)
        and seed_matrix[
            index(multiplets.A_MINUS, (HALF, R(3, 2))),
            index(multiplets.L_MINUS, (R(0), R(2))),
        ]
        == sp.sqrt(10) / (5 * sp.pi),
    )
    check(
        "C2c-E: constructed raising kernels obey the chosen phase-adjusted dagger convention",
        all(
            exact_matrix_equal(
                bundle.raising[component],
                conjugation_phase(component)
                * bundle.lowering[
                    (-component[0], -component[1])
                ].conjugate().T,
            )
            for component in COMPONENTS
        ),
    )
    return polynomials


def show_polynomials(
    polynomials: dict[tuple[sp.Rational, sp.Rational], sp.Expr]
) -> None:
    print("\nCanonical exact lowering moment polynomials mu^-_q=zb M^-_q z:")
    for component in COMPONENTS:
        print(f"\nq={component}")
        print(sp.sstr(polynomials[component], order="lex"))
    print(
        "\nRaising convention: mu^+_q=(-1)^(1-q_L-q_R) times the "
        "formal ordinary dagger of mu^-_{-q}; zb and z are independent "
        "polynomial variables here."
    )


def fail_closed(arguments: argparse.Namespace) -> None:
    missing = []
    if arguments.require_full_so42:
        missing.append(
            "full SO(4,2): proper-conformal Hamiltonian generators and their "
            "[K+,K-] brackets are not reconstructed from the kernels M"
        )
    if arguments.require_all_towers:
        missing.append("remaining oscillator-tower and diagonal Taub blocks")
    if arguments.require_seven_killing:
        missing.append("time-translation plus six rotation Taub kernels")
    if arguments.require_global_brst:
        missing.append("global Diff x Weyl BRST/BFV reduction")
    if missing:
        raise SystemExit("[BLOCKED] " + "; ".join(missing))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show-polynomials", action="store_true")
    parser.add_argument("--require-full-so42", action="store_true")
    parser.add_argument("--require-all-towers", action="store_true")
    parser.add_argument("--require-seven-killing", action="store_true")
    parser.add_argument("--require-global-brst", action="store_true")
    arguments = parser.parse_args()

    bundle = reconstruct_kernel_bundle()
    generators = compact_state_generators()
    check(
        "C2c-E: kernels and compact oscillator generators are separate typed data",
        isinstance(bundle, KernelBundle)
        and isinstance(generators, CompactStateGenerators)
        and bundle.dimension == generators.energy.rows == 36,
    )
    verify_compact_representations(generators)
    verify_partial_coadjoint_equivariance(bundle, generators)
    polynomials = verify_canonical_polynomials(bundle)
    if arguments.show_polynomials:
        show_polynomials(polynomials)
    fail_closed(arguments)
    print(
        "[PASS] C2c-E partial SU(2)_L x SU(2)_R x D coadjoint equivariance of "
        "the reconstructed low-mode Taub kernels; no full SO(4,2) or "
        "global-BRST claim"
    )


if __name__ == "__main__":
    main()
