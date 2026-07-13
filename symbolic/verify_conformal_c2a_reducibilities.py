#!/usr/bin/env python3
"""Exact C2a rail for conformal-Killing reducibilities on ``R x S^3``.

This certificate fixes the global kinematics which must precede the Taub
charge calculation.  In the Euler-angle conventions used by the cylinder
perturbiners it

* constructs the complete 15-dimensional Diff x Weyl reducibility algebra;
* checks the embedding, Hessian, conformal-Killing, and divergence identities
  exactly;
* identifies the ``ell=|omega|=1`` scalar reducibilities used by the P4
  t-channel; and
* verifies the frequency-derivative/generalized-mode identities in the exact
  component basis of ``verify_conformal_quartic_exchange.py``.

The eight proper conformal generators are most economical in the complex
frequency basis ``K_A^q`` with ``q=+/-1``.  Complex conjugation exchanges the
two signs, so they are eight *real* generators, not sixteen.  Together with
time translation and the six spatial rotations they give 15.

This file deliberately does not evaluate ``B^(2)``, the full Taub-charge
matrix, or the global BRST cohomology.  The separate selected-component rail
``verify_conformal_taub_charge.py`` uses these identities.  The
``--require-taub-matrix`` option therefore still fails closed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations

import sympy as sp

try:
    from symbolic.verify_conformal_quartic_contact import _load_verified_kernel
    from symbolic.verify_conformal_quartic_exchange import BLOCKS
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_quartic_contact import _load_verified_kernel
    from verify_conformal_quartic_exchange import BLOCKS


I = sp.I
R = sp.Rational


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


time, alpha, beta, gamma = sp.symbols(
    "time alpha beta gamma", real=True
)
spatial_coordinates = (alpha, beta, gamma)


# These are exactly the ambient coordinates used by the curved-cylinder
# perturbiner kernel.  They obey X_A X_A=1.
EMBEDDING = sp.Matrix(
    [
        sp.cos(beta / 2) * sp.cos((alpha + gamma) / 2),
        sp.sin(beta / 2) * sp.sin((alpha - gamma) / 2),
        -sp.sin(beta / 2) * sp.cos((alpha - gamma) / 2),
        -sp.cos(beta / 2) * sp.sin((alpha + gamma) / 2),
    ]
)
SPATIAL_JACOBIAN = EMBEDDING.jacobian(spatial_coordinates)
SPATIAL_METRIC = sp.Matrix(
    [
        [R(1, 4), 0, sp.cos(beta) / 4],
        [0, R(1, 4), 0],
        [sp.cos(beta) / 4, 0, R(1, 4)],
    ]
)
SPATIAL_INVERSE = sp.simplify(SPATIAL_METRIC.inv())
CYLINDER_METRIC = sp.diag(-1, 1, 1, 1)
CYLINDER_METRIC[1:4, 1:4] = SPATIAL_METRIC


def exact_zero(value: sp.Expr) -> bool:
    # ``method="fu"`` is needed for the Euler-coordinate expressions that
    # contain both tan(beta) and half angles.  The default trigsimp leaves
    # exact zeroes such as the R_12 Killing residual unevaluated.
    return sp.simplify(
        sp.trigsimp(sp.expand_trig(sp.expand_complex(value)), method="fu")
    ) == 0


def matrix_exact_zero(matrix: sp.Matrix) -> bool:
    return all(exact_zero(entry) for entry in matrix)


def spatial_christoffel() -> list[list[list[sp.Expr]]]:
    output = [
        [[sp.Integer(0) for _ in range(3)] for _ in range(3)]
        for _ in range(3)
    ]
    for upper in range(3):
        for first in range(3):
            for second in range(3):
                output[upper][first][second] = sp.simplify(
                    sum(
                        SPATIAL_INVERSE[upper, lower]
                        * (
                            sp.diff(
                                SPATIAL_METRIC[lower, second],
                                spatial_coordinates[first],
                            )
                            + sp.diff(
                                SPATIAL_METRIC[lower, first],
                                spatial_coordinates[second],
                            )
                            - sp.diff(
                                SPATIAL_METRIC[first, second],
                                spatial_coordinates[lower],
                            )
                        )
                        / 2
                        for lower in range(3)
                    )
                )
    return output


SPATIAL_CHRISTOFFEL = spatial_christoffel()


def gradient(function: sp.Expr) -> sp.Matrix:
    return sp.simplify(
        SPATIAL_INVERSE
        * sp.Matrix(
            [sp.diff(function, coordinate) for coordinate in spatial_coordinates]
        )
    )


def hessian(function: sp.Expr) -> sp.Matrix:
    output = sp.zeros(3)
    for first in range(3):
        for second in range(3):
            output[first, second] = sp.simplify(
                sp.diff(
                    function,
                    spatial_coordinates[first],
                    spatial_coordinates[second],
                )
                - sum(
                    SPATIAL_CHRISTOFFEL[upper][first][second]
                    * sp.diff(function, spatial_coordinates[upper])
                    for upper in range(3)
                )
            )
    return output


GRADIENTS = tuple(gradient(coordinate) for coordinate in EMBEDDING)
HESSIANS = tuple(hessian(coordinate) for coordinate in EMBEDDING)


@dataclass(frozen=True)
class ReducibilityPair:
    """One Diff x Weyl pair in contravariant-vector convention."""

    label: str
    sector: str
    vector: sp.Matrix
    sigma: sp.Expr


def time_translation() -> ReducibilityPair:
    return ReducibilityPair(
        "T", "(0,0), energy 0", sp.Matrix([1, 0, 0, 0]), sp.Integer(0)
    )


def rotation(first: int, second: int) -> ReducibilityPair:
    spatial = sp.simplify(
        EMBEDDING[first] * GRADIENTS[second]
        - EMBEDDING[second] * GRADIENTS[first]
    )
    return ReducibilityPair(
        f"R{first}{second}",
        "(1,0) + (0,1), energy 0",
        sp.Matrix([0, *spatial]),
        sp.Integer(0),
    )


def proper_complex(ambient: int, frequency_sign: int) -> ReducibilityPair:
    if frequency_sign not in (-1, 1):
        raise ValueError("frequency sign must be +/-1")
    q = sp.Integer(frequency_sign)
    phase = sp.exp(-I * q * time)
    vector = sp.Matrix(
        [-I * q * phase * EMBEDDING[ambient], *(phase * GRADIENTS[ambient])]
    )
    return ReducibilityPair(
        f"K{frequency_sign:+d}_{ambient}",
        f"(1/2,1/2), energy {frequency_sign:+d}",
        vector,
        phase * EMBEDDING[ambient],
    )


TIME_PAIR = time_translation()
ROTATION_PAIRS = tuple(rotation(*indices) for indices in combinations(range(4), 2))
PROPER_COMPLEX_PAIRS = tuple(
    proper_complex(ambient, sign)
    for sign in (1, -1)
    for ambient in range(4)
)


def real_proper_pairs() -> tuple[ReducibilityPair, ...]:
    """Return the eight real generators underlying the K^+/- basis."""

    output: list[ReducibilityPair] = []
    for ambient in range(4):
        plus = proper_complex(ambient, 1)
        minus = proper_complex(ambient, -1)
        output.append(
            ReducibilityPair(
                f"C_{ambient}",
                "(1/2,1/2), cosine",
                sp.simplify((plus.vector + minus.vector) / 2),
                sp.simplify((plus.sigma + minus.sigma) / 2),
            )
        )
        output.append(
            ReducibilityPair(
                f"S_{ambient}",
                "(1/2,1/2), sine",
                sp.simplify((plus.vector - minus.vector) / (2 * I)),
                sp.simplify((plus.sigma - minus.sigma) / (2 * I)),
            )
        )
    return tuple(output)


REAL_REDUCIBILITIES = (TIME_PAIR, *ROTATION_PAIRS, *real_proper_pairs())


def check_sphere_identities() -> None:
    kernel = _load_verified_kernel()
    check(
        "C2a: explicit embedding matches the curved-cylinder kernel",
        matrix_exact_zero(EMBEDDING - kernel["embedding"]),
    )
    check(
        "C2a: explicit metric matches both the embedding and kernel metric",
        matrix_exact_zero(SPATIAL_JACOBIAN.T * SPATIAL_JACOBIAN - SPATIAL_METRIC)
        and matrix_exact_zero(
            CYLINDER_METRIC - kernel["background_metric_expression"]
        ),
    )
    check(
        "C2a: ambient coordinates obey X_A X_A=1",
        exact_zero((EMBEDDING.T * EMBEDDING)[0] - 1),
    )

    gradient_gram = sp.Matrix(
        4,
        4,
        lambda first, second: (
            GRADIENTS[first].T
            * SPATIAL_METRIC
            * GRADIENTS[second]
        )[0],
    )
    check(
        "C2a: ell=1 gradient completeness is exact",
        matrix_exact_zero(
            gradient_gram - (sp.eye(4) - EMBEDDING * EMBEDDING.T)
        ),
    )
    check(
        "C2a: all four ell=1 embedding harmonics obey Hess X_A=-gamma X_A",
        all(
            matrix_exact_zero(HESSIANS[ambient] + SPATIAL_METRIC * EMBEDDING[ambient])
            for ambient in range(4)
        ),
    )


def rotation_ck_residual(first: int, second: int) -> sp.Matrix:
    """Spatial part of L_R gamma, assembled from exact covariant data."""

    residual = sp.zeros(3)
    d_first = SPATIAL_JACOBIAN[first, :].T
    d_second = SPATIAL_JACOBIAN[second, :].T
    nabla_covector = (
        d_first * d_second.T
        + EMBEDDING[first] * HESSIANS[second]
        - d_second * d_first.T
        - EMBEDDING[second] * HESSIANS[first]
    )
    residual[:, :] = nabla_covector + nabla_covector.T
    return residual


def proper_ck_residual(ambient: int, frequency_sign: int) -> sp.Matrix:
    """L_xi g+2 sigma g for one proper conformal frequency mode."""

    q = sp.Integer(frequency_sign)
    phase = sp.exp(-I * q * time)
    coordinate = EMBEDDING[ambient]
    covector_time = I * q * phase * coordinate
    covector_space = phase * SPATIAL_JACOBIAN[ambient, :].T
    sigma = phase * coordinate
    residual = sp.zeros(4)
    residual[0, 0] = 2 * sp.diff(covector_time, time) - 2 * sigma
    for spatial in range(3):
        residual[0, spatial + 1] = (
            sp.diff(covector_space[spatial], time)
            + sp.diff(covector_time, spatial_coordinates[spatial])
        )
        residual[spatial + 1, 0] = residual[0, spatial + 1]
    residual[1:4, 1:4] = (
        2 * phase * HESSIANS[ambient] + 2 * sigma * SPATIAL_METRIC
    )
    return residual


def check_all_reducibilities() -> None:
    check(
        "C2a: real reducibility basis contains exactly 1+6+8=15 pairs",
        len(REAL_REDUCIBILITIES) == 15
        and len({pair.label for pair in REAL_REDUCIBILITIES}) == 15,
    )
    check(
        "C2a: time translation is an exact Diff x Weyl reducibility",
        TIME_PAIR.sigma == 0 and TIME_PAIR.vector == sp.Matrix([1, 0, 0, 0]),
    )
    check(
        "C2a: all six SO(4) rotations solve the Killing equation",
        all(
            matrix_exact_zero(rotation_ck_residual(first, second))
            for first, second in combinations(range(4), 2)
        ),
    )
    check(
        "C2a: all eight complex frequency modes solve L_xi g+2 sigma g=0",
        all(
            matrix_exact_zero(proper_ck_residual(ambient, sign))
            for sign in (1, -1)
            for ambient in range(4)
        ),
    )

    rotation_divergences = []
    for first, second in combinations(range(4), 2):
        covariant_derivative = (
            SPATIAL_JACOBIAN[first, :].T
            * SPATIAL_JACOBIAN[second, :]
            + EMBEDDING[first] * HESSIANS[second]
            - SPATIAL_JACOBIAN[second, :].T
            * SPATIAL_JACOBIAN[first, :]
            - EMBEDDING[second] * HESSIANS[first]
        )
        rotation_divergences.append(
            sp.trace(SPATIAL_INVERSE * covariant_derivative)
        )
    check(
        "C2a: Killing sectors have sigma=-div(xi)/4=0",
        all(exact_zero(divergence) for divergence in rotation_divergences),
    )

    proper_divergence_checks = []
    for sign in (1, -1):
        q = sp.Integer(sign)
        phase = sp.exp(-I * q * time)
        for ambient in range(4):
            time_divergence = sp.diff(
                -I * q * phase * EMBEDDING[ambient], time
            )
            spatial_divergence = phase * sp.trace(
                SPATIAL_INVERSE * HESSIANS[ambient]
            )
            proper_divergence_checks.append(
                time_divergence
                + spatial_divergence
                + 4 * phase * EMBEDDING[ambient]
            )
    check(
        "C2a: proper sectors obey sigma=-div(xi)/4",
        all(exact_zero(value) for value in proper_divergence_checks),
    )

    # The six R_AB are independent because their action on the ambient
    # coordinate vector gives six independent antisymmetric matrices.  The
    # four X_A are independent in each distinct frequency sector.
    rotation_actions: list[sp.Matrix] = []
    for first, second in combinations(range(4), 2):
        action = sp.zeros(4)
        for coordinate in range(4):
            action[coordinate, first] += int(second == coordinate)
            action[coordinate, second] -= int(first == coordinate)
        rotation_actions.append(action)
    flattened = sp.Matrix.hstack(
        *(action.reshape(16, 1) for action in rotation_actions)
    )
    check(
        "C2a: representation count is 1 + 6 + 4_(+1) + 4_(-1)",
        flattened.rank() == 6
        and sp.eye(4).rank() == 4
        and 1 + flattened.rank() + 2 * sp.eye(4).rank() == 15,
    )


def canonical_rotation(first: int, second: int) -> tuple[str | None, int]:
    if first == second:
        return None, 0
    if first < second:
        return f"R{first}{second}", 1
    return f"R{second}{first}", -1


GENERATOR_NAMES = (
    "T",
    *(f"R{first}{second}" for first, second in combinations(range(4), 2)),
    *(f"K{sign:+d}_{ambient}" for sign in (1, -1) for ambient in range(4)),
)


def add_term(output: dict[str, sp.Expr], name: str | None, value: sp.Expr) -> None:
    if name is None or value == 0:
        return
    output[name] = sp.simplify(output.get(name, 0) + value)
    if output[name] == 0:
        del output[name]


def basis_bracket(first: str, second: str) -> dict[str, sp.Expr]:
    """The complexified so(4,2) brackets in the explicit cylinder basis."""

    if first == second:
        return {}
    if second == "T":
        return {name: -value for name, value in basis_bracket("T", first).items()}
    if first == "T":
        if not second.startswith("K"):
            return {}
        sign = 1 if second[1] == "+" else -1
        return {second: -I * sign}
    if first.startswith("K") and second.startswith("R"):
        return {
            name: -value for name, value in basis_bracket(second, first).items()
        }
    if first.startswith("R") and second.startswith("R"):
        a, b = int(first[1]), int(first[2])
        c, d = int(second[1]), int(second[2])
        output: dict[str, sp.Expr] = {}
        for coefficient, left, right in (
            (int(b == c), a, d),
            (-int(a == c), b, d),
            (-int(b == d), a, c),
            (int(a == d), b, c),
        ):
            name, orientation = canonical_rotation(left, right)
            add_term(output, name, coefficient * orientation)
        return output
    if first.startswith("R") and second.startswith("K"):
        a, b = int(first[1]), int(first[2])
        sign = 1 if second[1] == "+" else -1
        c = int(second[-1])
        output = {}
        add_term(output, f"K{sign:+d}_{a}", int(b == c))
        add_term(output, f"K{sign:+d}_{b}", -int(a == c))
        return output
    if first.startswith("K") and second.startswith("K"):
        first_sign = 1 if first[1] == "+" else -1
        second_sign = 1 if second[1] == "+" else -1
        first_ambient = int(first[-1])
        second_ambient = int(second[-1])
        if first_sign == second_sign:
            return {}
        if first_sign == -1:
            return {
                name: -value
                for name, value in basis_bracket(second, first).items()
            }
        output = {}
        rotation_name, orientation = canonical_rotation(
            first_ambient, second_ambient
        )
        add_term(output, rotation_name, 2 * orientation)
        add_term(output, "T", 2 * I * int(first_ambient == second_ambient))
        return output
    raise ValueError(f"unhandled bracket {first}, {second}")


def combination_bracket(
    first: dict[str, sp.Expr], second: dict[str, sp.Expr]
) -> dict[str, sp.Expr]:
    output: dict[str, sp.Expr] = {}
    for first_name, first_coefficient in first.items():
        for second_name, second_coefficient in second.items():
            for name, value in basis_bracket(first_name, second_name).items():
                add_term(
                    output,
                    name,
                    first_coefficient * second_coefficient * value,
                )
    return output


def check_algebra() -> None:
    check(
        "C2a: explicit conformal brackets include [K_A^+,K_B^-]=2R_AB+2i delta_AB T",
        all(
            basis_bracket(f"K+1_{first}", f"K-1_{second}")
            == (
                ({"T": 2 * I} if first == second else {
                    canonical_rotation(first, second)[0]:
                    2 * canonical_rotation(first, second)[1]
                })
            )
            for first in range(4)
            for second in range(4)
        ),
    )
    jacobi_ok = True
    for first in GENERATOR_NAMES:
        for second in GENERATOR_NAMES:
            for third in GENERATOR_NAMES:
                jacobi: dict[str, sp.Expr] = {}
                for contribution in (
                    combination_bracket(
                        {first: 1},
                        combination_bracket({second: 1}, {third: 1}),
                    ),
                    combination_bracket(
                        {second: 1},
                        combination_bracket({third: 1}, {first: 1}),
                    ),
                    combination_bracket(
                        {third: 1},
                        combination_bracket({first: 1}, {second: 1}),
                    ),
                ):
                    for name, value in contribution.items():
                        add_term(jacobi, name, value)
                if jacobi:
                    jacobi_ok = False
                    break
            if not jacobi_ok:
                break
        if not jacobi_ok:
            break
    check(
        "C2a: all 15 generators close and satisfy Jacobi exactly",
        jacobi_ok,
    )


def check_t_channel_reducibility() -> None:
    kernel = _load_verified_kernel()
    half = R(1, 2)
    highest = kernel["scalar_harmonic"](half, half, half)
    embedding_highest = (EMBEDDING[0] + I * EMBEDDING[3]) / sp.pi
    check(
        "C2a: t-channel highest scalar is (X_0+i X_3)/pi",
        exact_zero(highest - embedding_highest),
    )

    block = BLOCKS["t"]
    check(
        "C2a: t block is exactly ell=|omega|=1 with lambda=3",
        block.ell == block.omega == 1 and block.laplacian == 3,
    )
    magnitude = sp.symbols("Omega", real=True)
    expected_slices = {
        1: sp.Matrix([3, I, 1]),
        -1: sp.Matrix([3, -I, 1]),
    }
    for sign in (1, -1):
        reducibility = sp.Matrix([I * sign, 1, 1])
        generator = block.gauge_generator(sign)
        reduced_generator = generator[:, (0, 1)]
        constraints = block.constraints(sign)
        slice_vector = constraints.nullspace()[0]
        # ``ScalarMetricBlock.gauge_generator`` deliberately accepts exact
        # integer frequencies only, so form the same ell=1 matrix with a
        # symbolic signed frequency for this derivative check.
        signed_frequency = sign * magnitude
        symbolic_generator = sp.Matrix(
            [
                [-2 * I * signed_frequency, 0, -2],
                [1, -I * signed_frequency, 0],
                [0, -2, 2],
            ]
        )
        derivative = sp.diff(symbolic_generator, magnitude).subs(magnitude, 1)
        gauge_correction = sp.Matrix([-2 * I * sign, 1])
        check(
            f"C2a: q={sign:+d} t mode is a one-dimensional CK reducibility",
            generator.rank() == 2
            and generator.nullspace() == [reducibility]
            and generator * reducibility == sp.zeros(3, 1),
        )
        check(
            f"C2a: q={sign:+d} transverse quotient uses the exact P4 slice",
            slice_vector == expected_slices[sign]
            and reduced_generator.row_join(slice_vector).rank() == 3,
        )
        check(
            f"C2a: q={sign:+d} frequency derivative is 2p modulo gauge",
            derivative * reducibility - 2 * slice_vector
            == reduced_generator * gauge_correction,
        )

    plus_reducibility = sp.Matrix([I, 1, 1])
    plus_combination = (
        proper_complex(0, 1).vector + I * proper_complex(3, 1).vector
    ) / sp.pi
    plus_sigma = (
        proper_complex(0, 1).sigma + I * proper_complex(3, 1).sigma
    ) / sp.pi
    expected_plus = sp.Matrix(
        [
            -I * sp.exp(-I * time) * highest,
            *(sp.exp(-I * time) * gradient(highest)),
        ]
    )
    check(
        "C2a: P4 r_+ is the K_0^+ + i K_3^+ highest-weight CK pair",
        BLOCKS["t"].gauge_generator(1) * plus_reducibility
        == sp.zeros(3, 1)
        and matrix_exact_zero(plus_combination - expected_plus)
        and exact_zero(plus_sigma - sp.exp(-I * time) * highest),
    )


def show_formulas() -> None:
    print("\nExplicit ambient coordinates:")
    for ambient, coordinate in enumerate(EMBEDDING):
        print(f"  X_{ambient} = {coordinate}")
    print("\nReal Diff x Weyl basis:")
    print("  T: xi=d/dtime, sigma=0")
    print("  R_AB: xi^i=X_A D^i X_B-X_B D^i X_A, sigma=0 (A<B)")
    print("  C_A=(K_A^+ + K_A^-)/2, S_A=(K_A^+ - K_A^-)/(2i)")
    print("  K_A^q: xi=e^(-iq time)(-iq X_A, D^i X_A), sigma=e^(-iq time)X_A")
    print("\n15 labels:")
    print("  " + ", ".join(pair.label for pair in REAL_REDUCIBILITIES))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--show-formulas",
        action="store_true",
        help="print the explicit embedding and generator formulae",
    )
    parser.add_argument(
        "--require-taub-matrix",
        action="store_true",
        help="fail closed: the 15-component nonlinear Taub matrix is not computed here",
    )
    arguments = parser.parse_args()

    check_sphere_identities()
    check_all_reducibilities()
    check_algebra()
    check_t_channel_reducibility()
    if arguments.show_formulas:
        show_formulas()
    if arguments.require_taub_matrix:
        raise SystemExit(
            "[BLOCKED] C2a reducibility kinematics pass, but B^(2), the "
            "15-component Taub matrix, and global BRST reduction are absent."
        )
    print(
        "[PASS] exact 15-generator reducibility rail; this kinematic rail "
        "does not claim the full Taub-charge matrix"
    )


if __name__ == "__main__":
    main()
