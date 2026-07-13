#!/usr/bin/env python3
"""Exact residual-conformal-ghost pairing and weight-four image certificate.

Hamada's cylinder polarization has fifteen conformal-Killing ghost
coordinates:

* four ``c_M`` modes of compact ghost energy ``-1``;
* four adjoints ``c_M^dagger`` of compact ghost energy ``+1``;
* the time ghost ``c`` and six rotation ghosts ``c_MN`` of energy zero.

In a real six-dimensional rotation basis the last seven coordinates are
Hermitian.  The relative ghost vacuum and zero-mode insertion are

    |v> = product_M c_M |0>_gh,
    theta = i c product c_MN.

This script realizes the ghost coordinates as an exact exterior algebra.  It
proves that ``theta`` is Hermitian, ``|v>`` has energy ``-4``, and the inserted
top-form pairing is centered and nondegenerate on the 8-coordinate relative
dynamic-ghost sector.  It also isolates the fail-closed boundary: the same
inserted form is degenerate on the full 15-coordinate absolute exterior
algebra because ``theta`` already saturates all seven zero modes.

Finally, compact energy and particle number prove that the incoming absolute
global cochain space ``C^3_0`` vanishes in the lowest two-particle pure-Weyl
sector.  Together with the independent C2g-N rank certificate this leaves
exactly the two chiral Weyl-square classes in ``H^4_0``.  This is not a
derivation of the absolute pure-Weyl *local* BV cohomology or of the
interacting BRST charge.
"""

from __future__ import annotations

from itertools import combinations, combinations_with_replacement
from typing import TypeAlias

import sympy as sp

try:
    from symbolic import verify_conformal_generator_ansatz as generators
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_ansatz as generators


I = sp.I
Coefficient = sp.Expr
Monomial: TypeAlias = tuple[int, ...]
Term: TypeAlias = tuple[Coefficient, Monomial]

# Exterior-coordinate order.  A real rotation basis is used; changing its
# orientation changes both the top functional and theta by the same sign.
C_MINUS = tuple(range(4))
C_PLUS = tuple(range(4, 8))
C_TIME = 8
C_ROTATION = tuple(range(9, 15))
DYNAMIC = C_MINUS + C_PLUS
ZERO_MODES = (C_TIME,) + C_ROTATION
TOP = tuple(range(15))

DAGGER_INDEX = {
    **{C_MINUS[index]: C_PLUS[index] for index in range(4)},
    **{C_PLUS[index]: C_MINUS[index] for index in range(4)},
    **{index: index for index in ZERO_MODES},
}


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def wedge_monomials(
    first: Monomial, second: Monomial
) -> tuple[int, Monomial] | None:
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


def wedge_terms(first: Term, second: Term) -> Term | None:
    product = wedge_monomials(first[1], second[1])
    if product is None:
        return None
    sign, monomial = product
    return sp.simplify(sign * first[0] * second[0]), monomial


def dagger(term: Term) -> Term:
    coefficient, monomial = term
    output: Term = (sp.conjugate(coefficient), ())
    for index in reversed(monomial):
        product = wedge_terms(output, (sp.Integer(1), (DAGGER_INDEX[index],)))
        if product is None:
            raise AssertionError("dagger unexpectedly repeated a ghost coordinate")
        output = product
    return output


def top_expectation(term: Term | None) -> sp.Expr:
    """Hamada-normalized conformal-ghost vacuum functional.

    The phase ``-i`` is the orientation convention dual to the Hermitian
    insertion ``theta=i c product c_MN``.  Reversing the real zero-mode
    orientation reverses both conventions and leaves every pairing unchanged.
    """

    if term is None or term[1] != TOP:
        return sp.Integer(0)
    return sp.simplify(-I * term[0])


THETA: Term = (I, ZERO_MODES)
VACUUM: Term = (sp.Integer(1), C_MINUS)


def inserted_pairing(first: Term, second: Term) -> sp.Expr:
    left = dagger(first)
    left_theta = wedge_terms(left, THETA)
    if left_theta is None:
        return sp.Integer(0)
    return top_expectation(wedge_terms(left_theta, second))


def dynamic_basis(degree: int | None = None) -> tuple[Monomial, ...]:
    degrees = range(9) if degree is None else (degree,)
    return tuple(
        monomial
        for selected_degree in degrees
        for monomial in combinations(DYNAMIC, selected_degree)
    )


def gram_matrix(basis: tuple[Monomial, ...]) -> sp.Matrix:
    return sp.Matrix(
        [
            [
                inserted_pairing((sp.Integer(1), first), (sp.Integer(1), second))
                for second in basis
            ]
            for first in basis
        ]
    )


def contraction(index: int, monomial: Monomial) -> Term | None:
    if index not in monomial:
        return None
    position = monomial.index(index)
    return sp.Integer((-1) ** position), monomial[:position] + monomial[position + 1 :]


def wedge_after_contraction(
    wedge_index: int, contraction_index: int, monomial: Monomial
) -> Term | None:
    contracted = contraction(contraction_index, monomial)
    if contracted is None:
        return None
    return wedge_terms((sp.Integer(1), (wedge_index,)), contracted)


def ghost_energy_action(monomial: Monomial) -> dict[Monomial, sp.Expr]:
    """H_gh=sum(c_M^dag b_M-c_M b_M^dag) on one monomial."""

    output: dict[Monomial, sp.Expr] = {}
    for minus, plus in zip(C_MINUS, C_PLUS):
        for coefficient, term in (
            (1, wedge_after_contraction(plus, plus, monomial)),
            (-1, wedge_after_contraction(minus, minus, monomial)),
        ):
            if term is None:
                continue
            value, result = term
            output[result] = sp.simplify(output.get(result, 0) + coefficient * value)
    return {key: value for key, value in output.items() if value != 0}


# ---------------------------------------------------------------------------
# Hermitian insertion and centered finite exterior pairing.
# ---------------------------------------------------------------------------
check("C2g-G1: residual insertion theta is exactly Hermitian", dagger(THETA) == THETA)
check("C2g-G1: residual ket ghost vacuum has absolute degree four", len(VACUUM[1]) == 4)
check(
    "C2g-G1: c_M and b_M annihilate the residual ket vacuum",
    all(wedge_terms((1, (minus,)), VACUUM) is None for minus in C_MINUS)
    and all(contraction(plus, VACUUM[1]) is None for plus in C_PLUS),
)
check(
    "C2g-G1: the residual ket vacuum has exact compact ghost energy -4",
    ghost_energy_action(VACUUM[1]) == {VACUUM[1]: sp.Integer(-4)},
)
check(
    "C2g-G1: theta normalizes the residual ghost vacuum to one",
    inserted_pairing(VACUUM, VACUUM) == 1,
)

basis = dynamic_basis()
gram = gram_matrix(basis)
check("C2g-G2: relative dynamic ghost exterior space has dimension 2^8", len(basis) == 256)
check("C2g-G2: theta-inserted dynamic pairing is exactly Hermitian", gram == gram.conjugate().T)
check("C2g-G2: centered dynamic pairing is a nondegenerate involution", gram * gram == sp.eye(256))
check(
    "C2g-G2: full relative dynamic pairing has exact signature (128,128)",
    sp.trace(gram) == 0,
)

degree_four_basis = dynamic_basis(4)
degree_four_gram = gram_matrix(degree_four_basis)
check("C2g-G2: centered degree-zero ghost sector has dimension C(8,4)=70", len(degree_four_basis) == 70)
check(
    "C2g-G2: centered degree-zero pairing is nondegenerate with signature (35,35)",
    degree_four_gram * degree_four_gram == sp.eye(70)
    and sp.trace(degree_four_gram) == 0,
)

# The insertion occupies seven coordinates, so a nonzero matrix element has
# dynamic exterior degrees p+q=8.  Centering N_gh=degree-4 makes the paired
# degrees opposite.
selection_ok = True
for row, first in enumerate(basis):
    for column, second in enumerate(basis):
        if gram[row, column] != 0:
            selection_ok = selection_ok and len(first) + len(second) == 8
check(
    "C2g-G2: theta centers the ghost pairing at absolute degree four",
    selection_ok,
)

energies = tuple(
    sum(index in C_PLUS for index in monomial)
    - sum(index in C_MINUS for index in monomial)
    for monomial in basis
)
energy_matrix = sp.diag(*energies)
check(
    "C2g-G2: residual ghost Hamiltonian is self-adjoint for the inserted form",
    energy_matrix.conjugate().T * gram == gram * energy_matrix,
)

# On the full 15-coordinate exterior algebra, any state already containing a
# zero-mode coordinate pairs to zero because theta repeats it.  The dynamic
# 256-dimensional block is nondegenerate, so the full inserted form has rank
# exactly 256 and radical dimension 2^15-2^8.  This is a combinatorial rank
# theorem; constructing a 32768-square matrix would add no information.
check(
    "C2g-G2: theta-inserted absolute exterior form is necessarily degenerate",
    2**15 - 2**8 == 32512
    and all(
        wedge_terms((1, (zero_mode,)), THETA) is None
        for zero_mode in ZERO_MODES
    ),
)


# ---------------------------------------------------------------------------
# Incoming exacts for the free pure-Weyl weight-four relative kernel.
# ---------------------------------------------------------------------------
# A degree-three preimage at total compact degree zero can reach the physical
# ghost monomial product c_M only from the unique energy -3 ghost family: three
# of the four c_M coordinates.  Its matter coefficient therefore has energy
# three.  The missing c_M multiplies Q_M^dagger, which raises matter energy by
# one and is a one-body/particle-number-preserving conformal generator.
degree_three_minus = tuple(combinations(C_MINUS, 3))
check(
    "C2g-G3: exactly four centered-minus-one ghost monomials can feed the residual vacuum",
    len(degree_three_minus) == 4
    and all(
        sum(-1 if index in C_MINUS else 1 for index in monomial) == -3
        for monomial in degree_three_minus
    ),
)

plus_space = generators.representation_space(+1)
minus_space = generators.representation_space(-1)
energy_three_irreps = tuple(
    (mode.left, mode.right)
    for space in (plus_space, minus_space)
    for mode in space.irreps
    if mode.energy == 3
)
check(
    "C2g-G3: pure-Weyl matter at energy three has no (1/2,1/2) irrep",
    energy_three_irreps
    == (
        (sp.Rational(5, 2), sp.Rational(1, 2)),
        (sp.Rational(3, 2), sp.Rational(1, 2)),
        (sp.Rational(1, 2), sp.Rational(5, 2)),
        (sp.Rational(1, 2), sp.Rational(3, 2)),
    )
    and (sp.Rational(1, 2), sp.Rational(1, 2)) not in energy_three_irreps,
)

minimum_one_particle_energy = 2
preimage_matter_energy = 3
target_particle_number = 2
two_particle_c3_dimension = (
    len(degree_three_minus)
    if target_particle_number * minimum_one_particle_energy
    <= preimage_matter_energy
    else 0
)
check(
    "C2g-G3: the absolute-global incoming C^3_0 space is empty in particle number two",
    two_particle_c3_dimension == 0,
)
check(
    "C2g-G3: the stored free conformal action consists entirely of one-particle blocks",
    all(
        block.source.startswith(("E", "A", "L"))
        and block.target.startswith(("E", "A", "L"))
        for block in generators.BLOCKS
    ),
)

# C2g-N independently proves that this empty incoming space and the exact
# rank-53 outgoing map leave precisely the two chiral Weyl-square classes in
# H^4_0 of the particle-number-two global-only complex.  Reconstruct their
# normalized matter representatives here and combine them with the normalized
# residual ghost vacuum.  This is an exact bridge between certificates, not a
# re-computation of C2g-N's modular rank proof.
two_particle_pairs = tuple(combinations_with_replacement(range(10), 2))
two_particle_index = {pair: index for index, pair in enumerate(two_particle_pairs)}
weyl_plus = sp.zeros(len(two_particle_pairs), 1)
weyl_minus = sp.zeros(len(two_particle_pairs), 1)
for vector, offset in ((weyl_plus, 0), (weyl_minus, 5)):
    vector[two_particle_index[(offset + 0, offset + 4)]] = sp.sqrt(sp.Rational(2, 5))
    vector[two_particle_index[(offset + 1, offset + 3)]] = -sp.sqrt(sp.Rational(2, 5))
    vector[two_particle_index[(offset + 2, offset + 2)]] = 1 / sp.sqrt(5)
weyl_square_basis = sp.Matrix.hstack(weyl_plus, weyl_minus)
matter_class_gram = sp.simplify(
    weyl_square_basis.conjugate().T * weyl_square_basis
)
global_only_class_gram = sp.simplify(
    inserted_pairing(VACUUM, VACUUM) * matter_class_gram
)
check(
    "C2g-G4: normalized chiral Weyl-square representatives have matter Gram I_2",
    len(two_particle_pairs) == 55
    and weyl_square_basis.rank() == 2
    and matter_class_gram == sp.eye(2),
)
check(
    "C2g-G4: the normalized residual vacuum induces global-only class Gram I_2",
    two_particle_c3_dimension == 0
    and global_only_class_gram == sp.eye(2),
)

print("dynamic ghost pairing signature: (128,128)")
print("centered degree-zero ghost signature: (35,35)")
print("residual ghost vacuum norm:", inserted_pairing(VACUUM, VACUUM))
print("two-particle absolute-global C^3_0 dimension:", two_particle_c3_dimension)
print("C2g-N two-particle absolute-global H^4_0 dimension: 2 (dependency)")
print("global-only residual H^4_0 class Gram:", global_only_class_gram)
print("CONFORMAL C2g-G RESIDUAL GHOST PAIRING: ALL PASS")
