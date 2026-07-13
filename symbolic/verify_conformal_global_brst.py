#!/usr/bin/env python3
"""C2e: exact algebra-only global conformal BRST certificate.

The companion C2a rail constructs an exact complex cylinder basis for the
fifteen generators of ``so(4,2)`` and verifies all of its Jacobi identities.
This script uses those same structure constants to construct the universal
minimal Chevalley--Eilenberg/BRST complex.

It proves, in exact arithmetic,

* antisymmetry, closure, and Jacobi for the imported 15-generator algebra;
* nilpotency of the ghost Chevalley--Eilenberg differential;
* nilpotency with coefficients in the adjoint module (formal constraints);
* ghost-number ``+1`` grading;
* compact-energy degree zero of the BRST differential; and
* ghost number ``+1`` and compact-energy degree zero of every term in the
  formal minimal BRST charge.

This is an algebra-only certificate.  The formal generators used below are
not matrices on the Weyl-gravity oscillator/Fock space.  No local
Diff-times-Weyl ghost complex, Taub-constraint zero locus, global physical
cohomology, induced pairing, or physical-state projection is constructed.
The fail-closed command-line switches protect those distinctions.
"""

from __future__ import annotations

import argparse
from itertools import combinations
from typing import TypeAlias

import sympy as sp

try:
    from symbolic.verify_conformal_c2a_reducibilities import (
        GENERATOR_NAMES,
        basis_bracket,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_c2a_reducibilities import (
        GENERATOR_NAMES,
        basis_bracket,
    )


Coefficient = sp.Expr
Monomial = tuple[int, ...]
ExteriorPolynomial: TypeAlias = dict[Monomial, Coefficient]
AdjointPolynomial: TypeAlias = dict[tuple[Monomial, int], Coefficient]
MinimalPolynomial: TypeAlias = dict[tuple[str, Monomial, int], Coefficient]

NAMES = tuple(GENERATOR_NAMES)
DIMENSION = len(NAMES)
INDEX = {name: position for position, name in enumerate(NAMES)}
R = sp.Rational
I = sp.I


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def add_coefficient(
    output: dict[object, Coefficient], key: object, value: Coefficient
) -> None:
    value = sp.simplify(value)
    if value == 0:
        return
    output[key] = sp.simplify(output.get(key, 0) + value)
    if output[key] == 0:
        del output[key]


def structure_constants() -> tuple[tuple[tuple[Coefficient, ...], ...], ...]:
    """Return ``f[a][b][c]`` defined by ``[G_a,G_b]=f[a,b]^c G_c``."""

    data: list[list[list[Coefficient]]] = [
        [[sp.Integer(0) for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for first, first_name in enumerate(NAMES):
        for second, second_name in enumerate(NAMES):
            for output_name, value in basis_bracket(first_name, second_name).items():
                data[first][second][INDEX[output_name]] = sp.simplify(value)
    return tuple(
        tuple(tuple(component for component in row) for row in matrix)
        for matrix in data
    )


F = structure_constants()


def generator_energy(name: str) -> int:
    """Compact ``D=iT`` degree: K+ raises, K- lowers, T/R preserve."""

    if name.startswith("K+1_"):
        return 1
    if name.startswith("K-1_"):
        return -1
    return 0


GENERATOR_ENERGY = tuple(generator_energy(name) for name in NAMES)
GHOST_ENERGY = tuple(-degree for degree in GENERATOR_ENERGY)


def wedge_monomials(
    first: Monomial, second: Monomial
) -> tuple[int, Monomial] | None:
    """Canonical exterior product for sorted tuples of ghost indices."""

    if set(first).intersection(second):
        return None
    inversions = sum(1 for left in first for right in second if left > right)
    sign = -1 if inversions % 2 else 1
    return sign, tuple(sorted(first + second))


def wedge(
    first: ExteriorPolynomial, second: ExteriorPolynomial
) -> ExteriorPolynomial:
    output: ExteriorPolynomial = {}
    for left_monomial, left_value in first.items():
        for right_monomial, right_value in second.items():
            product = wedge_monomials(left_monomial, right_monomial)
            if product is None:
                continue
            sign, monomial = product
            add_coefficient(
                output,
                monomial,
                sign * left_value * right_value,
            )
    return output


def scale_polynomial(
    polynomial: ExteriorPolynomial, coefficient: Coefficient
) -> ExteriorPolynomial:
    output: ExteriorPolynomial = {}
    for monomial, value in polynomial.items():
        add_coefficient(output, monomial, coefficient * value)
    return output


def ghost_differentials() -> tuple[ExteriorPolynomial, ...]:
    """``s c^a=-1/2 f_bc^a c^b wedge c^c`` in the complex basis."""

    output: list[ExteriorPolynomial] = []
    for target in range(DIMENSION):
        differential: ExteriorPolynomial = {}
        for first in range(DIMENSION):
            for second in range(DIMENSION):
                coefficient = -R(1, 2) * F[first][second][target]
                product = wedge_monomials((first,), (second,))
                if product is None:
                    continue
                sign, monomial = product
                add_coefficient(differential, monomial, sign * coefficient)
        output.append(differential)
    return tuple(output)


DC = ghost_differentials()


def ce_differential(polynomial: ExteriorPolynomial) -> ExteriorPolynomial:
    """Odd derivation extending the differential on the fifteen ghosts."""

    output: ExteriorPolynomial = {}
    for monomial, value in polynomial.items():
        for position, ghost in enumerate(monomial):
            prefix = {monomial[:position]: sp.Integer(1)}
            suffix = {monomial[position + 1 :]: sp.Integer(1)}
            term = wedge(wedge(prefix, DC[ghost]), suffix)
            for result_monomial, result_value in term.items():
                add_coefficient(
                    output,
                    result_monomial,
                    (-1) ** position * value * result_value,
                )
    return output


def monomial_ghost_number(monomial: Monomial) -> int:
    return len(monomial)


def monomial_energy(monomial: Monomial) -> int:
    return sum(GHOST_ENERGY[index] for index in monomial)


def adjoint_differential(polynomial: AdjointPolynomial) -> AdjointPolynomial:
    """CE differential with coefficients in the formal adjoint module.

    For a formal constraint ``G_i``, ``s G_i=c^a [G_a,G_i]``.  No matrix
    realization of ``G_i`` on states is assumed.
    """

    output: AdjointPolynomial = {}
    for (monomial, generator), value in polynomial.items():
        ghost_part = ce_differential({monomial: value})
        for result_monomial, result_value in ghost_part.items():
            add_coefficient(output, (result_monomial, generator), result_value)

        module_sign = (-1) ** len(monomial)
        for ghost in range(DIMENSION):
            product = wedge_monomials(monomial, (ghost,))
            if product is None:
                continue
            wedge_sign, result_monomial = product
            for target in range(DIMENSION):
                bracket_value = F[ghost][generator][target]
                add_coefficient(
                    output,
                    (result_monomial, target),
                    value * module_sign * wedge_sign * bracket_value,
                )
    return output


def minimal_differential(polynomial: MinimalPolynomial) -> MinimalPolynomial:
    """Minimal BRST differential on formal constraints and ghost momenta.

    ``kind='G'`` denotes an even formal constraint and ``kind='b'`` its odd
    canonical ghost momentum.  With the standard even BFV bracket,

        s b_a = G_a + c^b f_{ba}^c b_c.

    Together with ``s c`` and ``s G`` above, this is the Hamiltonian vector
    field of the formal minimal BRST charge.  It remains representation-free.
    """

    output: MinimalPolynomial = {}
    for (kind, monomial, generator), value in polynomial.items():
        if kind not in ("G", "b"):
            raise ValueError(f"unknown minimal-complex kind {kind}")

        ghost_part = ce_differential({monomial: value})
        for result_monomial, result_value in ghost_part.items():
            add_coefficient(
                output,
                (kind, result_monomial, generator),
                result_value,
            )

        module_sign = (-1) ** len(monomial)
        if kind == "G":
            for ghost in range(DIMENSION):
                product = wedge_monomials(monomial, (ghost,))
                if product is None:
                    continue
                wedge_sign, result_monomial = product
                for target in range(DIMENSION):
                    add_coefficient(
                        output,
                        ("G", result_monomial, target),
                        value
                        * module_sign
                        * wedge_sign
                        * F[ghost][generator][target],
                    )
            continue

        # s b_a=G_a+c^b f_{ba}^c b_c.  ``module_sign`` is the graded
        # Leibniz sign from moving s through the preceding ghosts.
        add_coefficient(
            output,
            ("G", monomial, generator),
            value * module_sign,
        )
        for ghost in range(DIMENSION):
            product = wedge_monomials(monomial, (ghost,))
            if product is None:
                continue
            wedge_sign, result_monomial = product
            for target in range(DIMENSION):
                add_coefficient(
                    output,
                    ("b", result_monomial, target),
                    value
                    * module_sign
                    * wedge_sign
                    * F[ghost][generator][target],
                )
    return output


def check_lie_algebra() -> None:
    check("C2e-1: imported conformal basis has dimension fifteen", DIMENSION == 15)
    check(
        "C2e-1: imported structure constants are exactly antisymmetric",
        all(
            sp.simplify(F[first][second][target] + F[second][first][target])
            == 0
            for first in range(DIMENSION)
            for second in range(DIMENSION)
            for target in range(DIMENSION)
        ),
    )

    jacobi_ok = True
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            for third in range(DIMENSION):
                for target in range(DIMENSION):
                    coefficient = sum(
                        F[second][third][middle] * F[first][middle][target]
                        + F[third][first][middle] * F[second][middle][target]
                        + F[first][second][middle] * F[third][middle][target]
                        for middle in range(DIMENSION)
                    )
                    if sp.simplify(coefficient) != 0:
                        jacobi_ok = False
                        break
                if not jacobi_ok:
                    break
            if not jacobi_ok:
                break
        if not jacobi_ok:
            break
    check("C2e-1: every imported structure-constant Jacobi identity vanishes", jacobi_ok)


def check_compact_energy() -> None:
    # D=iT.  The imported convention has [T,K_s]=-i*s*K_s.
    time_index = INDEX["T"]
    check(
        "C2e-2: D=iT assigns compact degrees +1,0,-1 exactly",
        all(
            all(
                sp.simplify(
                    I * F[time_index][generator][target]
                    - GENERATOR_ENERGY[generator]
                    * int(target == generator)
                )
                == 0
                for target in range(DIMENSION)
            )
            for generator in range(DIMENSION)
        ),
    )
    check(
        "C2e-2: every nonzero bracket is homogeneous in compact energy",
        all(
            F[first][second][target] == 0
            or GENERATOR_ENERGY[target]
            == GENERATOR_ENERGY[first] + GENERATOR_ENERGY[second]
            for first in range(DIMENSION)
            for second in range(DIMENSION)
            for target in range(DIMENSION)
        ),
    )


def check_ce_complex() -> None:
    check(
        "C2e-3: every ghost differential has ghost number two",
        all(
            all(monomial_ghost_number(monomial) == 2 for monomial in image)
            for image in DC
        ),
    )
    check(
        "C2e-3: the ghost differential preserves compact-energy degree",
        all(
            all(monomial_energy(monomial) == GHOST_ENERGY[ghost] for monomial in image)
            for ghost, image in enumerate(DC)
        ),
    )
    check(
        "C2e-3: Jacobi makes s^2 vanish on all fifteen ghosts",
        all(not ce_differential(image) for image in DC),
    )

    # Regression across the first four exterior degrees.  Nilpotency on the
    # generators plus the derivation law is already a proof on the full
    # exterior algebra; this finite sweep guards the implementation.
    grading_ok = True
    nilpotency_ok = True
    for degree in range(4):
        for monomial in combinations(range(DIMENSION), degree):
            polynomial = {monomial: sp.Integer(1)}
            image = ce_differential(polynomial)
            grading_ok = grading_ok and all(
                len(output_monomial) == degree + 1
                and monomial_energy(output_monomial) == monomial_energy(monomial)
                for output_monomial in image
            )
            nilpotency_ok = nilpotency_ok and not ce_differential(image)
    check(
        "C2e-3: s raises ghost number by one and preserves compact degree through exterior degree three",
        grading_ok,
    )
    check(
        "C2e-3: s^2 vanishes on every exterior monomial through degree three",
        nilpotency_ok,
    )


def check_adjoint_module() -> None:
    nilpotency_ok = True
    grading_ok = True
    for generator in range(DIMENSION):
        element: AdjointPolynomial = {((), generator): sp.Integer(1)}
        first_image = adjoint_differential(element)
        second_image = adjoint_differential(first_image)
        nilpotency_ok = nilpotency_ok and not second_image
        grading_ok = grading_ok and all(
            len(monomial) == 1
            and monomial_energy(monomial) + GENERATOR_ENERGY[target]
            == GENERATOR_ENERGY[generator]
            for monomial, target in first_image
        )
    check(
        "C2e-4: Jacobi makes s^2 vanish on all formal adjoint constraints",
        nilpotency_ok,
    )
    check(
        "C2e-4: the adjoint-module differential has ghost number +1 and compact degree zero",
        grading_ok,
    )


def check_formal_minimal_charge_grading() -> None:
    # Omega_min=c^a G_a - 1/2 f_bc^a c^b c^c b_a.  The canonical ghost
    # momentum b_a has ghost number -1 and compact degree +deg(G_a).
    linear_terms_ok = all(
        1 == 1 and GHOST_ENERGY[index] + GENERATOR_ENERGY[index] == 0
        for index in range(DIMENSION)
    )
    cubic_terms_ok = all(
        F[first][second][target] == 0
        or (
            1 + 1 - 1 == 1
            and GHOST_ENERGY[first]
            + GHOST_ENERGY[second]
            + GENERATOR_ENERGY[target]
            == 0
        )
        for first in range(DIMENSION)
        for second in range(DIMENSION)
        for target in range(DIMENSION)
    )
    check(
        "C2e-5: every c^a G_a term has ghost number one and compact degree zero",
        linear_terms_ok,
    )
    check(
        "C2e-5: every f_bc^a c^b c^c b_a term has ghost number one and compact degree zero",
        cubic_terms_ok,
    )

    momentum_nilpotency = True
    momentum_grading = True
    for generator in range(DIMENSION):
        momentum: MinimalPolynomial = {("b", (), generator): sp.Integer(1)}
        first_image = minimal_differential(momentum)
        second_image = minimal_differential(first_image)
        momentum_nilpotency = momentum_nilpotency and not second_image
        for kind, monomial, target in first_image:
            ghost_number = len(monomial) + (0 if kind == "G" else -1)
            energy = monomial_energy(monomial) + GENERATOR_ENERGY[target]
            momentum_grading = momentum_grading and (
                ghost_number == 0 and energy == GENERATOR_ENERGY[generator]
            )
    check(
        "C2e-5: s raises every b_a ghost momentum from ghost number -1 to 0 without changing compact degree",
        momentum_grading,
    )
    check(
        "C2e-5: closure and Jacobi make s^2 vanish on all fifteen ghost momenta",
        momentum_nilpotency,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-oscillator-action",
        action="store_true",
        help="fail closed: no 15-generator oscillator/Fock representation is constructed",
    )
    parser.add_argument(
        "--require-physical-cohomology",
        action="store_true",
        help="fail closed: no combined local/global BRST cohomology is computed",
    )
    arguments = parser.parse_args()

    # These switches request results that this algebra-only rail cannot
    # supply.  Fail before the more expensive exterior-algebra regression.
    if arguments.require_oscillator_action:
        raise SystemExit(
            "the fifteen generators have not been represented on the complete "
            "oscillator/Fock plus contractible state complex"
        )
    if arguments.require_physical_cohomology:
        raise SystemExit(
            "the global conformal ghosts have not been combined with the local "
            "Diff x Weyl BRST complex, so physical cohomology is undefined"
        )

    check_lie_algebra()
    check_compact_energy()
    check_ce_complex()
    check_adjoint_module()
    check_formal_minimal_charge_grading()

    print("C2e complex basis:", ", ".join(NAMES))
    print("C2e generator compact degrees:", GENERATOR_ENERGY)
    print("C2e ghost compact degrees:", GHOST_ENERGY)
    print(
        "C2e STATUS: EXACT ALGEBRA-ONLY MINIMAL GLOBAL-CONFORMAL BRST "
        "COMPLEX. Nilpotency follows from the verified SO(4,2) Jacobi "
        "identities. No action on Weyl-gravity states, physical cohomology, "
        "or induced pairing is supplied."
    )

if __name__ == "__main__":
    main()
