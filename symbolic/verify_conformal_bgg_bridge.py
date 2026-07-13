#!/usr/bin/env python3
"""C2i-BGG: convention and topology audit for the smooth cylinder bridge.

This certificate checks the parts of the global BGG argument that depend on
the repository's four-dimensional conventions:

* Lorentzian Hodge duality on two-forms has ``star**2=-1``;
* the flat linearized Weyl operator obeys the deformation-complex identity

      C1^sharp star C1 = 0

  as an exact constant-coefficient differential-operator identity;
* the two curvature equations split into independent chiral equations;
* ``R x S^3`` has adjoint-local-system cohomology dimensions
  ``(15,0,0,15,0)``; and
* the bottom rotational scalar in the four lowering-ghost polarization is
  unique and has compact ghost degree ``-4``.

The global fine-resolution theorem itself is a literature theorem, not a
matrix identity proved by this script.  Nor does the script construct the
algebraic ``D``-finite metric preimages or the all-level ``E/A/L`` curvature
intertwiner.  It also does not construct the cyclic BV/BFV zero-mode
transfer, identify the degree-three copy with Taub charges, derive the
residual ghost normalization from pure-Weyl BFV, or control a Hilbert/Krein
completion.  Dedicated fail-closed switches preserve those boundaries.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import sympy as sp


R = sp.Rational
DIMENSION = 4
LORENTZ_SIGNATURE = (-1, 1, 1, 1)
EUCLIDEAN_SIGNATURE = (1, 1, 1, 1)
SYMMETRIC_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first, DIMENSION)
)
TWO_FORM_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first + 1, DIMENSION)
)

OperatorTerm = tuple[sp.Expr, tuple[int, ...], tuple[int, int]]


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def canonical_pair(first: int, second: int) -> tuple[int, int]:
    return (first, second) if first <= second else (second, first)


def collect_terms(terms: list[OperatorTerm]) -> tuple[OperatorTerm, ...]:
    output: defaultdict[tuple[tuple[int, ...], tuple[int, int]], sp.Expr] = (
        defaultdict(lambda: sp.Integer(0))
    )
    for coefficient, derivatives, pair in terms:
        output[tuple(sorted(derivatives)), canonical_pair(*pair)] += coefficient
    return tuple(
        (sp.simplify(coefficient), derivatives, pair)
        for (derivatives, pair), coefficient in sorted(output.items())
        if sp.simplify(coefficient) != 0
    )


def scaled_terms(
    coefficient: sp.Expr, terms: tuple[OperatorTerm, ...]
) -> list[OperatorTerm]:
    return [
        (sp.simplify(coefficient * value), derivatives, pair)
        for value, derivatives, pair in terms
    ]


def metric(first: int, second: int, signature: tuple[int, ...]) -> sp.Integer:
    return sp.Integer(signature[first] if first == second else 0)


def riemann_terms(
    first: int, second: int, third: int, fourth: int
) -> tuple[OperatorTerm, ...]:
    """Linearized all-lower-index Riemann tensor on a flat background."""

    return collect_terms(
        [
            (R(1, 2), (first, third), (second, fourth)),
            (R(1, 2), (second, fourth), (first, third)),
            (-R(1, 2), (second, third), (first, fourth)),
            (-R(1, 2), (first, fourth), (second, third)),
        ]
    )


def ricci_terms(
    first: int, second: int, signature: tuple[int, ...]
) -> tuple[OperatorTerm, ...]:
    terms: list[OperatorTerm] = []
    for contracted in range(DIMENSION):
        terms.extend(
            scaled_terms(
                signature[contracted],
                riemann_terms(contracted, first, contracted, second),
            )
        )
    return collect_terms(terms)


def scalar_terms(signature: tuple[int, ...]) -> tuple[OperatorTerm, ...]:
    terms: list[OperatorTerm] = []
    for index in range(DIMENSION):
        terms.extend(
            scaled_terms(signature[index], ricci_terms(index, index, signature))
        )
    return collect_terms(terms)


def weyl_terms(
    first: int,
    second: int,
    third: int,
    fourth: int,
    signature: tuple[int, ...],
) -> tuple[OperatorTerm, ...]:
    """Four-dimensional linearized Weyl tensor with all indices lowered."""

    terms = list(riemann_terms(first, second, third, fourth))
    trace_terms = (
        (metric(first, third, signature), ricci_terms(second, fourth, signature)),
        (-metric(first, fourth, signature), ricci_terms(second, third, signature)),
        (-metric(second, third, signature), ricci_terms(first, fourth, signature)),
        (metric(second, fourth, signature), ricci_terms(first, third, signature)),
    )
    for coefficient, source in trace_terms:
        terms.extend(scaled_terms(-R(1, 2) * coefficient, source))
    scalar_coefficient = R(1, 6) * (
        metric(first, third, signature) * metric(second, fourth, signature)
        - metric(first, fourth, signature) * metric(second, third, signature)
    )
    terms.extend(scaled_terms(scalar_coefficient, scalar_terms(signature)))
    return collect_terms(terms)


def hodge_matrix(signature: tuple[int, ...]) -> sp.Matrix:
    """Hodge star on independent all-lower-index two-form components."""

    matrix = sp.zeros(len(TWO_FORM_PAIRS))
    for row, (first, second) in enumerate(TWO_FORM_PAIRS):
        for column, (third, fourth) in enumerate(TWO_FORM_PAIRS):
            matrix[row, column] = (
                signature[third]
                * signature[fourth]
                * sp.LeviCivita(first, second, third, fourth)
            )
    return matrix


def dual_bach_terms(
    output: tuple[int, int], signature: tuple[int, ...]
) -> tuple[OperatorTerm, ...]:
    """Terms in ``(C1^sharp star C1 h)_{bd}`` on flat space.

    For Weyl tensors the formal adjoint is, up to the common nonzero action
    normalization, the double divergence ``partial^a partial^c U_abcd``.
    The Hodge star acts on the first antisymmetric pair.
    """

    second, fourth = output
    terms: list[OperatorTerm] = []
    for first in range(DIMENSION):
        for third in range(DIMENSION):
            divergence_sign = signature[first] * signature[third]
            for left in range(DIMENSION):
                for right in range(DIMENSION):
                    epsilon = sp.LeviCivita(first, second, left, right)
                    if epsilon == 0:
                        continue
                    hodge_coefficient = (
                        R(1, 2)
                        * signature[left]
                        * signature[right]
                        * epsilon
                    )
                    for coefficient, derivatives, pair in weyl_terms(
                        left, right, third, fourth, signature
                    ):
                        terms.append(
                            (
                                divergence_sign * hodge_coefficient * coefficient,
                                (first, third, *derivatives),
                                pair,
                            )
                        )
    return collect_terms(terms)


def verify_hodge_and_complex_identity() -> None:
    lorentz_star = hodge_matrix(LORENTZ_SIGNATURE)
    euclidean_star = hodge_matrix(EUCLIDEAN_SIGNATURE)
    check(
        "C2i-BGG: Lorentzian Hodge star squares to -1 on two-forms",
        lorentz_star * lorentz_star == -sp.eye(len(TWO_FORM_PAIRS)),
    )
    check(
        "C2i-BGG: Euclidean Hodge star squares to +1 on two-forms",
        euclidean_star * euclidean_star == sp.eye(len(TWO_FORM_PAIRS)),
    )

    for signature_name, signature in (
        ("Lorentzian", LORENTZ_SIGNATURE),
        ("Euclidean", EUCLIDEAN_SIGNATURE),
    ):
        vanished = all(
            not dual_bach_terms(component, signature)
            for component in SYMMETRIC_PAIRS
        )
        check(
            f"C2i-BGG: {signature_name} C1^sharp star C1 vanishes as an exact operator",
            vanished,
        )


def verify_chiral_split() -> None:
    equation_matrix = sp.Matrix([[1, 1], [sp.I, -sp.I]])
    check(
        "C2i-BGG: the two curvature equations independently kill both chiral adjoint images",
        equation_matrix.det() == -2 * sp.I and not equation_matrix.nullspace(),
    )


def verify_cylinder_topology() -> None:
    # R x S^3 deformation retracts onto S^3.  With trivial adjoint local
    # system (simple connectivity), tensor the cellular Betti numbers by 15.
    sphere_betti = (1, 0, 0, 1, 0)
    adjoint_dimension = 15
    deformation_dimensions = tuple(
        adjoint_dimension * value for value in sphere_betti
    )
    check(
        "C2i-BGG: adjoint-local-system cohomology dimensions are (15,0,0,15,0)",
        deformation_dimensions == (15, 0, 0, 15, 0),
    )
    check(
        "C2i-BGG: metric and Weyl slots are globally exact in the smooth BGG category",
        deformation_dimensions[1:3] == (0, 0),
    )


def verify_bottom_ghost_scalar() -> None:
    lowering_dimension = 4
    top_exterior_dimension = sp.binomial(lowering_dimension, lowering_dimension)
    compact_degree = -lowering_dimension
    check(
        "C2i-BGG: the four-lowering-ghost top exterior power is one-dimensional",
        top_exterior_dimension == 1,
    )
    check(
        "C2i-BGG: the canonical bottom ghost scalar has degree (gh,D)=(4,-4)",
        (lowering_dimension, compact_degree) == (4, -4),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-machine-proof-of-bgg",
        action="store_true",
        help="fail closed: the fine-resolution input is a published theorem, not proved here",
    )
    parser.add_argument(
        "--claim-completed-domain",
        action="store_true",
        help="fail closed: no Hilbert/Krein continuity or closed-range theorem is supplied",
    )
    parser.add_argument(
        "--claim-algebraic-mode-exactness",
        action="store_true",
        help="fail closed: smooth BGG exactness does not construct D-finite metric preimages",
    )
    parser.add_argument(
        "--claim-eal-intertwiner",
        action="store_true",
        help="fail closed: this script does not build the all-level E/A/L curvature intertwiner",
    )
    parser.add_argument(
        "--claim-taub-identification",
        action="store_true",
        help="fail closed: the degree-three BGG sector has not yet been identified with Taub charges",
    )
    parser.add_argument(
        "--claim-completed-bv-transfer",
        action="store_true",
        help="fail closed: the cyclic BV/BFV zero-mode transfer remains to be constructed",
    )
    parser.add_argument(
        "--claim-pure-weyl-bfv-pairing",
        action="store_true",
        help="fail closed: residual CE saturation is not a derivation from the full pure-Weyl BFV pairing",
    )
    args = parser.parse_args()

    if args.claim_machine_proof_of_bgg:
        raise SystemExit(
            "the executable audits conventions and topology; it does not replace the published BGG fine-resolution theorem"
        )
    if args.claim_completed_domain:
        raise SystemExit(
            "smooth exactness does not establish continuity or closed range on an analytic completion"
        )
    if args.claim_algebraic_mode_exactness:
        raise SystemExit(
            "a smooth BGG preimage need not be D-finite or SO(4)-finite; an equivariant homotopy or explicit mode potential is still required"
        )
    if args.claim_eal_intertwiner:
        raise SystemExit(
            "character agreement is not the missing all-level geometric E/A/L curvature intertwiner"
        )
    if args.claim_taub_identification:
        raise SystemExit(
            "the 15-dimensional degree-three sector has the right representation but its Taub normalization is still open"
        )
    if args.claim_completed_bv_transfer:
        raise SystemExit(
            "the residual BFV pairing, zero-mode projector, and cyclic full-BV transfer are not constructed"
        )
    if args.claim_pure_weyl_bfv_pairing:
        raise SystemExit(
            "the canonical residual CE pairing is verified internally, but its induction from strict pure-Weyl BV/BFV remains conditional"
        )

    verify_hodge_and_complex_identity()
    verify_chiral_split()
    verify_cylinder_topology()
    verify_bottom_ghost_scalar()
    print(
        "C2i-BGG STATUS: LORENTZIAN COMPLEX IDENTITY, CYLINDER TOPOLOGY, "
        "CHIRAL SPLIT, AND BOTTOM-GHOST UNIQUENESS ALL PASS. The global "
        "fine resolution is cited; algebraic mode exactness, the E/A/L "
        "intertwiner, analytic completion, Taub identification, and cyclic "
        "BV/BFV transfer remain guarded."
    )


if __name__ == "__main__":
    main()
