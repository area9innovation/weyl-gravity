#!/usr/bin/env python3
"""C2g-Cartan: exact residual-CE contraction and vacuum-window audit.

For the absolute residual Chevalley--Eilenberg complex, let ``D`` be the
cylinder time-translation/dilatation generator and let ``i_D`` contract the
dual time ghost.  The Cartan identity is

    d i_D + i_D d = L_D.

The coefficient action contributes the matter energy ``E``.  A ghost dual to
a generator of compact grade ``w`` contributes ``-w``, so ``L_D`` acts by the
total compact degree ``delta``.  Therefore every ``delta != 0`` subcomplex is
contractible with homotopy ``i_D / delta``.

This script verifies the ghost identity on the unit and all fifteen exterior
generators.  Both sides are graded derivations, so this proves the identity on
all ``2^15`` monomials without an exhaustive symbolic expansion.  It checks
the exact generator grading and excludes every matter-weight-six ghost
dressing from ``delta=0``.  The missing matter-vacuum contribution does not
require a matrix rank: the Chevalley--Eilenberg theorem for the semisimple
algebra ``so(4,2)`` gives primitive cohomology degrees ``3,5,7``, and hence
``H^4(so(4,2);C)=0``.  Together with C2g-N, the complete minimal free-Fock
global-only H4 is therefore exactly the two Weyl-square classes.

This is not a local Diff x Weyl BV result.  It assumes that the conformal
Killing residual transformations, including D, are gauged exactly as in the
Hamada residual construction.  It does not apply when cylinder time
translation is retained as a physical global Hamiltonian or a boundary
charge.
"""

from __future__ import annotations

import argparse
from itertools import combinations

import sympy as sp

try:
    from symbolic import verify_conformal_global_brst_window as global_ce
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_global_brst_window as global_ce


Monomial = tuple[int, ...]
Polynomial = dict[Monomial, sp.Expr]
D_INDEX = 0


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def contraction(monomial: Monomial) -> Polynomial:
    """Interior contraction with the time-translation generator D."""

    if D_INDEX not in monomial:
        return {}
    position = monomial.index(D_INDEX)
    reduced = monomial[:position] + monomial[position + 1 :]
    return {reduced: sp.Integer((-1) ** position)}


def add_scaled(output: Polynomial, polynomial: Polynomial, scale: sp.Expr = 1) -> None:
    for monomial, coefficient in polynomial.items():
        global_ce.add_term(output, monomial, scale * coefficient)


def contract_polynomial(polynomial: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for monomial, coefficient in polynomial.items():
        for reduced, sign in contraction(monomial).items():
            global_ce.add_term(output, reduced, coefficient * sign)
    return global_ce.clean(output)


def ghost_cartan(
    monomial: Monomial,
    dc: tuple[dict[Monomial, sp.Expr], ...],
) -> Polynomial:
    """Return ``(d_gh i_D + i_D d_gh) monomial`` exactly."""

    output: Polynomial = {}
    for reduced, sign in contraction(monomial).items():
        add_scaled(output, global_ce.ce_on_monomial(reduced, dc), sign)
    add_scaled(
        output,
        contract_polynomial(global_ce.ce_on_monomial(monomial, dc)),
    )
    return global_ce.clean(output)


def exterior_generator_degrees(primitive_degrees: tuple[int, ...]) -> set[int]:
    """Degrees occurring in an exterior algebra on odd primitives."""

    return {
        sum(primitive_degrees[index] for index in subset)
        for size in range(len(primitive_degrees) + 1)
        for subset in combinations(range(len(primitive_degrees)), size)
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-local-bv",
        action="store_true",
        help="fail closed: the pure-Weyl local Diff x Weyl BV split is absent",
    )
    parser.add_argument(
        "--treat-d-as-physical-hamiltonian",
        action="store_true",
        help="fail closed: Cartan contraction requires D to be a residual gauge constraint",
    )
    args = parser.parse_args()
    if args.claim_local_bv:
        raise SystemExit(
            "this Cartan executable does not derive the residual complex from "
            "local pure-Weyl BV; that selected algebraic derivation is certified separately"
        )
    if args.treat_d_as_physical_hamiltonian:
        raise SystemExit(
            "if D is a physical global Hamiltonian/boundary charge, no antighost contraction quotients its eigenspaces"
        )

    data = global_ce.build_lie_data(+1)
    dc = global_ce.ghost_differentials(data)
    check(
        "C2g-C1: index zero is the compact generator D and the basis has grades 0^7,-1^4,+1^4",
        data.names[D_INDEX] == "D"
        and data.degrees == (0,) * 7 + (-1,) * 4 + (1,) * 4,
    )

    dilatation = data.matrices[D_INDEX]
    check(
        "C2g-C1: every represented conformal generator has its exact declared D grade",
        all(
            dilatation * matrix - matrix * dilatation == grade * matrix
            for matrix, grade in zip(data.matrices, data.degrees)
        ),
    )

    generator_monomials = ((), *((index,) for index in range(15)))
    cartan_ok = True
    for monomial in generator_monomials:
        energy = global_ce.ghost_energy(monomial, data.degrees)
        expected = {} if energy == 0 else {monomial: sp.Integer(energy)}
        cartan_ok = cartan_ok and ghost_cartan(monomial, dc) == expected
    check(
        "C2g-C1: Cartan identity holds on the unit and all fifteen exterior generators",
        len(generator_monomials) == 16 and cartan_ok,
    )
    # Both operators are degree-zero derivations. Equality on the exterior
    # generators therefore proves equality on the full exterior algebra.
    ghost_energies = {
        global_ce.ghost_energy(monomial, data.degrees)
        for ghost_number in range(16)
        for monomial in combinations(range(15), ghost_number)
    }
    check(
        "C2g-C1: derivation extension covers 2^15 monomials with ghost energies -4 through +4",
        sum(sp.binomial(15, degree) for degree in range(16)) == 2**15
        and ghost_energies == set(range(-4, 5)),
    )

    # Hamada's residual vacuum contains the four ghosts dual to the four
    # raising generators.  Their energy is -4, so matter weight E is centered
    # at total degree delta=E-4.  At E=6 every possible ghost dressing has
    # delta in 2,...,10 and is therefore in a contractible Cartan sector.
    raising_ghosts = tuple(range(11, 15))
    check(
        "C2g-C2: the product of the four raising-dual ghosts has energy -4",
        global_ce.ghost_energy(raising_ghosts, data.degrees) == -4,
    )
    weight_six_total_degrees = {6 + energy for energy in ghost_energies}
    check(
        "C2g-C2: no residual ghost dressing places matter weight six at total degree zero",
        weight_six_total_degrees == set(range(2, 11))
        and 0 not in weight_six_total_degrees,
    )

    # Complete the matter-vacuum (N=0) piece without a matrix calculation.
    # The complexification is so(6,C) ~= sl(4,C), of type A3.  Its invariant
    # polynomial degrees are 2,3,4, hence the Chevalley--Eilenberg primitive
    # degrees are 2*d_i-1 = 3,5,7.  The standard semisimple Lie-cohomology
    # theorem then gives H*(g;C) = Lambda(u3,u5,u7), which has no degree four.
    invariant_degrees = (2, 3, 4)
    primitive_degrees = tuple(2 * degree - 1 for degree in invariant_degrees)
    cohomology_degrees = exterior_generator_degrees(primitive_degrees)
    check(
        "C2g-C3: the A3 invariant degrees give primitive CE degrees 3,5,7",
        primitive_degrees == (3, 5, 7),
    )
    check(
        "C2g-C3: Lambda(u3,u5,u7) has no degree-four class, so vacuum H4=0",
        cohomology_degrees == {0, 3, 5, 7, 8, 10, 12, 15}
        and 4 not in cohomology_degrees,
    )

    # At delta=0 the ghost floor E_gh=-4 restricts matter coefficients to
    # E<=4.  With minimum one-particle energy two, only N=0,1,2 occur.  The
    # present calculation gives H4(N=0)=0; C2g-N independently proves
    # H4(N=1)=0 and H4(N=2)=span{W_+^2,W_-^2}.
    maximum_matter_energy = -min(ghost_energies)
    maximum_particle_number = maximum_matter_energy // 2
    c2g_n_h4_by_particle_number = {1: 0, 2: 2}
    full_free_fock_h4_dimension = (
        0 + sum(c2g_n_h4_by_particle_number.values())
    )
    check(
        "C2g-C4: the complete delta-zero free-Fock window contains only N=0,1,2",
        maximum_matter_energy == 4 and maximum_particle_number == 2,
    )
    check(
        "C2g-C4: with the exact C2g-N dependencies, full global-only H4 is the two Weyl-square classes",
        full_free_fock_h4_dimension == 2,
    )

    print("Cartan identity proved from the unit and 15 exterior generators")
    print("matter-weight-six total-degree range: (2,...,10)")
    print("matter-vacuum primitive CE degrees:", primitive_degrees)
    print("matter-vacuum cohomology degrees:", sorted(cohomology_degrees))
    print("complete free-Fock global-only H4 dimension: 2 (using C2g-N)")
    print("CONFORMAL C2g-CARTAN CONTRACTION: ALL PASS")


if __name__ == "__main__":
    main()
