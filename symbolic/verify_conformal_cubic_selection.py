#!/usr/bin/env python3
"""Exact C1c representation lemma for conformal cubic sign protection.

On the Einstein cylinder the three physical one-particle towers are

    E_J : energy 2J,   reps (J+1,J-1) + parity, positive sign;
    A_J : energy 2J+1, reps (J+1/2,J-1/2) + parity, negative sign;
    L_J : energy 2J+2, reps (J+1,J-1) + parity, negative sign.

The exact Einstein subsector removes every cubic matrix element containing
exactly one non-Einstein direction and otherwise E modes.  This script proves
that compact-energy conservation and the two SU(2) triangle rules then leave
only

    A_J A_K <-> L_(J+K)

as a possible opposite-sign one-to-two block.  It also verifies the universal
total-derivative identity seen in the exact C1b density hierarchy.  The latter
identity proves cancellation once the all-spin density formula is derived; it
does not itself derive that formula.
"""

from __future__ import annotations

from itertools import product

import sympy as sp


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


R = sp.Rational


def energy(branch: str, spin: sp.Rational) -> sp.Rational:
    offsets = {"E": 0, "A": 1, "L": 2}
    return 2 * spin + offsets[branch]


def spin_from_energy(branch: str, value: sp.Rational) -> sp.Rational:
    offsets = {"E": 0, "A": 1, "L": 2}
    return (value - offsets[branch]) / 2


def representation(
    branch: str, spin: sp.Rational, chirality: int
) -> tuple[sp.Rational, sp.Rational]:
    displacement = R(1, 2) if branch == "A" else R(1)
    return (
        spin + chirality * displacement,
        spin - chirality * displacement,
    )


def su2_contains(
    first: sp.Rational, second: sp.Rational, output: sp.Rational
) -> bool:
    return (
        abs(first - second) <= output <= first + second
        and (first + second - output).is_integer
    )


def product_contains(
    first: tuple[sp.Rational, sp.Rational],
    second: tuple[sp.Rational, sp.Rational],
    output: tuple[sp.Rational, sp.Rational],
) -> bool:
    return su2_contains(first[0], second[0], output[0]) and su2_contains(
        first[1], second[1], output[1]
    )


def representation_allowed(
    first_branch: str,
    second_branch: str,
    output_branch: str,
    first_spin: sp.Rational,
    second_spin: sp.Rational,
) -> list[tuple[int, int, int]]:
    output_spin = spin_from_energy(
        output_branch,
        energy(first_branch, first_spin) + energy(second_branch, second_spin),
    )
    if output_spin < 1 or not (2 * output_spin).is_integer:
        return []
    allowed = []
    for first_chirality, second_chirality, output_chirality in product(
        (-1, 1), repeat=3
    ):
        if product_contains(
            representation(first_branch, first_spin, first_chirality),
            representation(second_branch, second_spin, second_chirality),
            representation(output_branch, output_spin, output_chirality),
        ):
            allowed.append(
                (first_chirality, second_chirality, output_chirality)
            )
    return allowed


# ---------------------------------------------------------------------------
# C1c-1: exhaustive exact check of the all-spin triangle statement
# ---------------------------------------------------------------------------
half_integer_spins = [R(value, 2) for value in range(2, 13)]
surviving_families: set[tuple[str, str, str]] = set()
unexpected_examples = []
for first_branch, second_branch, output_branch in product(("A", "L"), repeat=3):
    for first_spin, second_spin in product(half_integer_spins, repeat=2):
        allowed = representation_allowed(
            first_branch,
            second_branch,
            output_branch,
            first_spin,
            second_spin,
        )
        if not allowed:
            continue
        family = (first_branch, second_branch, output_branch)
        surviving_families.add(family)
        if family != ("A", "A", "L"):
            unexpected_examples.append(
                (family, first_spin, second_spin, allowed)
            )

check(
    "C1c-1: exact half-integer scan leaves only A A -> L",
    surviving_families == {("A", "A", "L")} and not unexpected_examples,
)

# Prove the upper-triangle part for arbitrary spins, not only the finite scan.
# For every forbidden branch/chirality assignment, at least one output spin
# exceeds the sum of the two input spins by a positive spin-independent
# amount.  In the sole survivor, both gaps vanish exactly when all three
# chiralities agree.  SU(2) tensor products are multiplicity-free, so this
# also proves uniqueness of each reduced SO(4) matrix element.
j_symbol, k_symbol = sp.symbols("j_symbol k_symbol", positive=True)


def symbolic_representation(
    branch: str, spin: sp.Expr, chirality: int
) -> tuple[sp.Expr, sp.Expr]:
    displacement = R(1, 2) if branch == "A" else R(1)
    return (
        spin + chirality * displacement,
        spin - chirality * displacement,
    )


def symbolic_output_spin(
    first_branch: str, second_branch: str, output_branch: str
) -> sp.Expr:
    offsets = {"A": 1, "L": 2}
    return sp.simplify(
        (
            2 * j_symbol
            + offsets[first_branch]
            + 2 * k_symbol
            + offsets[second_branch]
            - offsets[output_branch]
        )
        / 2
    )


symbolic_failures = []
for first_branch, second_branch, output_branch in product(("A", "L"), repeat=3):
    family = (first_branch, second_branch, output_branch)
    output_spin = symbolic_output_spin(*family)
    for first_chirality, second_chirality, output_chirality in product(
        (-1, 1), repeat=3
    ):
        first_rep = symbolic_representation(
            first_branch, j_symbol, first_chirality
        )
        second_rep = symbolic_representation(
            second_branch, k_symbol, second_chirality
        )
        output_rep = symbolic_representation(
            output_branch, output_spin, output_chirality
        )
        gaps = tuple(
            sp.simplify(
                output_rep[index] - first_rep[index] - second_rep[index]
            )
            for index in range(2)
        )
        expected_survivor = (
            family == ("A", "A", "L")
            and first_chirality == second_chirality == output_chirality
        )
        if expected_survivor:
            valid = gaps == (0, 0)
        else:
            valid = any(bool(gap.is_positive) for gap in gaps)
        if not valid:
            symbolic_failures.append(
                (
                    family,
                    (first_chirality, second_chirality, output_chirality),
                    gaps,
                )
            )

check(
    "C1c-1: all-spin SU(2)xSU(2) upper-triangle proof is exact",
    not symbolic_failures,
)

# In the surviving family, energy fixes J_out=J_1+J_2.  The output irrep is
# attained only when all three chiralities agree; it is the maximal weight in
# both SU(2) factors.  The finite scan below is now a regression test of the
# symbolic proof rather than its logical basis.
for first_spin, second_spin in product(half_integer_spins, repeat=2):
    allowed = representation_allowed(
        "A", "A", "L", first_spin, second_spin
    )
    check_label = None
    if allowed != [(-1, -1, -1), (1, 1, 1)]:
        check_label = (first_spin, second_spin, allowed)
        break
check(
    "C1c-1: A A -> L requires the same chirality and J_out=J_1+J_2",
    check_label is None
    and all(
        spin_from_energy("L", energy("A", j) + energy("A", k)) == j + k
        for j, k in product(half_integer_spins, repeat=2)
    ),
)

# Opposite inherited signs before the Einstein selection rule are E<->EX and
# X<->EE or X<->YY, with X,Y in {A,L}.  The first two classes contain exactly
# one non-E direction and vanish.  Enumerate this reduction rather than
# inserting it as an assumption; the representation result above then
# classifies the remaining YY->X class.
branch_sign = {"E": 1, "A": -1, "L": -1}
opposite_after_einstein_selection = set()
for first_branch, second_branch, output_branch in product(
    ("E", "A", "L"), repeat=3
):
    if first_branch > second_branch:
        continue
    pair_sign = branch_sign[first_branch] * branch_sign[second_branch]
    if pair_sign == branch_sign[output_branch]:
        continue
    fields = (first_branch, second_branch, output_branch)
    if sum(field != "E" for field in fields) <= 1:
        continue
    opposite_after_einstein_selection.add(fields)

expected_nongeometric_candidates = {
    (first, second, output)
    for first, second in (("A", "A"), ("A", "L"), ("L", "L"))
    for output in ("A", "L")
}
check(
    "C1c-1: Einstein selection plus signatures reduce every opposite-sign cubic block to AA<->L",
    opposite_after_einstein_selection == expected_nongeometric_candidates
    and surviving_families == {("A", "A", "L")},
)


# ---------------------------------------------------------------------------
# C1c-2: exact boundary-term identity and measured hierarchy
# ---------------------------------------------------------------------------
t, constant = sp.symbols("t constant", positive=True, real=True)
n = sp.symbols("n", integer=True, positive=True)
density = constant * t * ((n - 1) * t**2 - 1) / (1 + t**2) ** n
measured_integrand = 2 * density / (1 + t**2)
primitive = -constant * t**2 / (1 + t**2) ** n
check(
    "C1c-2: the observed all-spin density ansatz is an exact boundary term",
    sp.simplify(measured_integrand - sp.diff(primitive, t)) == 0,
)

# The four C1b values have n=2(J_1+J_2)-1 >= 3, so both endpoints vanish.
measured_cases = [
    (R(1), R(1), 3, 3 * sp.sqrt(10) / (800 * sp.pi**3)),
    (R(1), R(3, 2), 4, 3 * sp.sqrt(35) / (1120 * sp.pi**3)),
    (R(3, 2), R(3, 2), 5, sp.sqrt(70) / (448 * sp.pi**3)),
    (R(1), R(2), 5, sp.sqrt(5) / (112 * sp.pi**3)),
]
check(
    "C1c-2: every measured exponent is n=2(J_1+J_2)-1 and has vanishing endpoints",
    all(
        n_value == 2 * (j + k) - 1 and n_value >= 3
        for j, k, n_value, _ in measured_cases
    )
    and sp.limit(-t**2 / (1 + t**2) ** 3, t, 0) == 0
    and sp.limit(-t**2 / (1 + t**2) ** 3, t, sp.oo) == 0,
)


def normalized_vector_prefactor(spin: sp.Rational) -> sp.Expr:
    # Highest-weight harmonic sqrt(2J)/(4pi), times the canonical oscillator
    # coefficient in Hamada--Horata Eq. (3.27).
    return sp.sqrt(2 * spin) / (
        8
        * sp.pi
        * sp.sqrt(
            (2 * spin - 1) * (2 * spin + 1) * (2 * spin + 3)
        )
    )


def normalized_upper_tt_prefactor(spin: sp.Rational) -> sp.Expr:
    # Highest-weight harmonic sqrt(2(2S-1))/(16pi), times Eq. (3.26).
    return sp.sqrt(2 * (2 * spin - 1)) / (
        64 * sp.pi * sp.sqrt((spin + 1) * (2 * spin + 1))
    )


def observed_prefactor_formula(
    first_spin: sp.Rational, second_spin: sp.Rational
) -> sp.Expr:
    total_spin = first_spin + second_spin
    return sp.simplify(
        64
        * (2 * first_spin + 1)
        * (2 * second_spin + 1)
        * (total_spin - 1)
        * normalized_vector_prefactor(first_spin)
        * normalized_vector_prefactor(second_spin)
        * normalized_upper_tt_prefactor(total_spin)
    )


check(
    "C1c-2: all four measured constants obey one normalized prefactor formula",
    all(
        sp.simplify(observed_prefactor_formula(j, k) - measured_constant) == 0
        for j, k, _, measured_constant in measured_cases
    ),
)


if not PASS:
    raise SystemExit("CONFORMAL C1C CUBIC SELECTION: FAIL")

print("CONFORMAL C1C CUBIC SELECTION: ALL PASS")
print("Only opposite-sign cubic family: A_J A_K <-> L_(J+K)")
print("Remaining proof obligation: derive the measured density form for all J,K")
