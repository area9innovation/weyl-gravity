#!/usr/bin/env python3
"""Exact P4b certificate for energy-six cylinder intermediates.

The selected parity-reduced target has three two-particle channels in the
common SO(4) irrep (2,2), written with doubled spins as (4,4),

    AA = A3^+ A3^-,
    EA = E2^+ A4^- + parity,
    EL = E2^+ L4^- + parity.

This script classifies candidate intermediate states in the normalizable
local gauge-reduced oscillator towers created by one normal-ordered cubic
Hamiltonian.  Acting on two particles,
the connected/relevant number changes are 2 -> 1 and 2 -> 3.  A 2 -> 5
term is a disconnected vacuum-emission sector at second order and is not
part of the normalized connected four-point operator.

There are three distinct facts, which must not be conflated.

1. No one-particle E/A/L oscillator candidate transforms in (4,4).
2. Before the final P6 projection is imposed, the three-particle image of
   each target channel is infinite.  The exact affine tails are enumerated
   without a spin cutoff.
3. In a connected one-internal-line tree contraction, the final external
   state fixes one of the two particles created at the first vertex.  This
   reduces the oscillator three-particle candidates to a finite list.  The
   remaining infinite high-pair tails are loop/self-energy or reducible
   external-state contractions, not t/u tree exchange.

Compact cylinder D is semisimple on these oscillator towers.  Every Q state
therefore carries the ordinary denominator 1/(Delta_Q-6).  The sole
representation-allowed Delta=6 three-particle incidence found before the
Einstein selection rule is an E2 E2 E2 state in the EL route.  It belongs
to P6, never to Q; its LEE current vanishes by the exact Einstein-subsector
selection rule.

Run with ``--show-families`` to print every exact affine tail.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from typing import Iterable


PASS = True


def check(label: str, condition: object) -> None:
    global PASS
    ok = bool(condition)
    print(("[OK ] " if ok else "[FAIL] ") + label)
    PASS = PASS and ok


BRANCHES = ("E", "A", "L")
BRANCH_ORDER = {branch: index for index, branch in enumerate(BRANCHES)}
OFFSET = {"E": 0, "A": 1, "L": 2}
TWICE_DISPLACEMENT = {"E": 2, "A": 1, "L": 2}
ONE_PARTICLE_SIGN = {"E": 1, "A": -1, "L": -1}
TARGET_REP = (4, 4)
SHELL_ENERGY = 6


def su2_contains(first2: int, second2: int, output2: int) -> bool:
    return (
        abs(first2 - second2) <= output2 <= first2 + second2
        and (first2 + second2 - output2) % 2 == 0
    )


def so4_contains(
    first: tuple[int, int],
    second: tuple[int, int],
    output: tuple[int, int],
) -> bool:
    return su2_contains(first[0], second[0], output[0]) and su2_contains(
        first[1], second[1], output[1]
    )


def symmetric_square_allows(
    source: tuple[int, int], output: tuple[int, int]
) -> bool:
    """Bosonic exchange parity in one SO(4) irrep square."""
    if not so4_contains(source, source, output):
        return False
    if output[0] % 2 or output[1] % 2:
        return False
    exponent = (
        source[0]
        - output[0] // 2
        + source[1]
        - output[1] // 2
    )
    return exponent % 2 == 0


@dataclass(frozen=True, order=True)
class Mode:
    branch: str
    twice_spin: int
    chirality: int

    def __post_init__(self) -> None:
        if self.branch not in BRANCHES:
            raise ValueError(f"unknown branch {self.branch}")
        if self.twice_spin < 2:
            raise ValueError("oscillator towers start at J=1")
        if self.chirality not in (-1, 1):
            raise ValueError("chirality must be +/-1")

    @property
    def energy(self) -> int:
        return self.twice_spin + OFFSET[self.branch]

    @property
    def rep(self) -> tuple[int, int]:
        displacement = self.chirality * TWICE_DISPLACEMENT[self.branch]
        return self.twice_spin + displacement, self.twice_spin - displacement

    @property
    def sign(self) -> int:
        return ONE_PARTICLE_SIGN[self.branch]

    def parity(self) -> "Mode":
        return Mode(self.branch, self.twice_spin, -self.chirality)

    def short(self) -> str:
        chirality = "+" if self.chirality > 0 else "-"
        return f"{self.branch}{self.energy}^{chirality}"


def vertex_allows(first: Mode, second: Mode, output: Mode) -> bool:
    if not so4_contains(first.rep, second.rep, output.rep):
        return False
    return first != second or symmetric_square_allows(first.rep, output.rep)


def killed_by_einstein_selection(branches: Iterable[str]) -> bool:
    """EEE and EEX have at most one non-E direction and vanish exactly."""
    return sum(branch != "E" for branch in branches) <= 1


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


@dataclass(frozen=True)
class PairTail:
    """All pairs (b,N,chi_b),(c,N+delta,chi_c), N>=N_min."""

    output: Mode
    first_branch: str
    second_branch: str
    first_chirality: int
    second_chirality: int
    delta: int
    minimum_n: int
    einstein_killed: bool

    @property
    def pair_sign(self) -> int:
        return (
            ONE_PARTICLE_SIGN[self.first_branch]
            * ONE_PARTICLE_SIGN[self.second_branch]
        )

    @property
    def branch_pair(self) -> str:
        return self.first_branch + self.second_branch

    def pair(self, n: int) -> tuple[Mode, Mode]:
        if n < self.minimum_n:
            raise ValueError("tail parameter is below its exact minimum")
        return (
            Mode(self.first_branch, n, self.first_chirality),
            Mode(self.second_branch, n + self.delta, self.second_chirality),
        )

    def pair_energy(self, n: int) -> int:
        first, second = self.pair(n)
        return first.energy + second.energy

    def parity_pair(self, n: int) -> tuple[Mode, Mode]:
        return tuple(mode.parity() for mode in self.pair(n))  # type: ignore[return-value]

    def short(self) -> str:
        first_chi = "+" if self.first_chirality > 0 else "-"
        second_chi = "+" if self.second_chirality > 0 else "-"
        killed = " [Einstein-zero]" if self.einstein_killed else ""
        return (
            f"{self.output.short()} <- "
            f"{self.first_branch}(2J=N)^{first_chi} + "
            f"{self.second_branch}(2J=N{self.delta:+d})^{second_chi}, "
            f"N>={self.minimum_n}{killed}"
        )


def pair_tail_families(
    output: Mode, *, apply_einstein_selection: bool
) -> list[PairTail]:
    """Derive every affine high-spin pair family exactly.

    Put n_1=N and n_2=N+delta.  The lower SU(2) triangle inequalities
    bound delta but not N.  The upper inequalities only set N_min.  Thus
    every returned row is an infinite tail, and the finite delta scan below
    is an exact derivation rather than an energy cutoff.
    """
    result: list[PairTail] = []
    output_left, output_right = output.rep
    for first_branch, second_branch in combinations_with_replacement(
        BRANCHES, 2
    ):
        for first_chirality, second_chirality in product((-1, 1), repeat=2):
            # Canonicalize equal-branch chirality order.  When both complete
            # mode types coincide, delta>=0 canonicalizes particle exchange.
            if (
                first_branch == second_branch
                and first_chirality > second_chirality
            ):
                continue
            first_shift = (
                first_chirality * TWICE_DISPLACEMENT[first_branch]
            )
            second_shift = (
                second_chirality * TWICE_DISPLACEMENT[second_branch]
            )

            delta_min = max(
                first_shift - second_shift - output_left,
                -first_shift + second_shift - output_right,
            )
            delta_max = min(
                first_shift - second_shift + output_left,
                -first_shift + second_shift + output_right,
            )
            for delta in range(delta_min, delta_max + 1):
                same_mode_type = (
                    first_branch == second_branch
                    and first_chirality == second_chirality
                )
                if same_mode_type and delta < 0:
                    continue

                # SU(2) integrality/parity is independent of N because its
                # coefficient is 2.
                if (
                    delta
                    + first_shift
                    + second_shift
                    - output_left
                ) % 2:
                    continue
                if (
                    delta
                    - first_shift
                    - second_shift
                    - output_right
                ) % 2:
                    continue

                minimum_n = max(
                    2,
                    2 - delta,
                    ceil_div(
                        output_left
                        - delta
                        - first_shift
                        - second_shift,
                        2,
                    ),
                    ceil_div(
                        output_right
                        - delta
                        + first_shift
                        + second_shift,
                        2,
                    ),
                )
                first = Mode(
                    first_branch, minimum_n, first_chirality
                )
                second = Mode(
                    second_branch,
                    minimum_n + delta,
                    second_chirality,
                )
                if not vertex_allows(first, second, output):
                    continue
                killed = killed_by_einstein_selection(
                    (output.branch, first_branch, second_branch)
                )
                if apply_einstein_selection and killed:
                    continue
                result.append(
                    PairTail(
                        output,
                        first_branch,
                        second_branch,
                        first_chirality,
                        second_chirality,
                        delta,
                        minimum_n,
                        killed,
                    )
                )
    return result


def mode_pair_key(first: Mode, second: Mode) -> tuple[Mode, Mode]:
    return tuple(sorted((first, second)))  # type: ignore[return-value]


def brute_pairs(output: Mode, maximum_n: int) -> set[tuple[Mode, Mode]]:
    modes = [
        Mode(branch, n, chirality)
        for branch in BRANCHES
        for n in range(2, maximum_n + 1)
        for chirality in (-1, 1)
    ]
    result = set()
    for first, second in combinations_with_replacement(modes, 2):
        if killed_by_einstein_selection(
            (output.branch, first.branch, second.branch)
        ):
            continue
        if vertex_allows(first, second, output):
            result.add(mode_pair_key(first, second))
    return result


def tail_pairs(output: Mode, maximum_n: int) -> set[tuple[Mode, Mode]]:
    result = set()
    for tail in pair_tail_families(output, apply_einstein_selection=True):
        for n in range(tail.minimum_n, maximum_n + 1):
            first, second = tail.pair(n)
            if max(first.twice_spin, second.twice_spin) <= maximum_n:
                result.add(mode_pair_key(first, second))
    return result


@dataclass(frozen=True)
class TargetRoute:
    label: str
    split: Mode
    spectator: Mode

    @property
    def tails(self) -> list[PairTail]:
        return pair_tail_families(
            self.split, apply_einstein_selection=True
        )

    def intermediate_energy(self, tail: PairTail, n: int) -> int:
        return self.spectator.energy + tail.pair_energy(n)

    def intermediate_sign(self, tail: PairTail) -> int:
        return self.spectator.sign * tail.pair_sign


A3_PLUS = Mode("A", 2, 1)
A3_MINUS = A3_PLUS.parity()
E2_PLUS = Mode("E", 2, 1)
E2_MINUS = E2_PLUS.parity()
A4_MINUS = Mode("A", 3, -1)
L4_MINUS = Mode("L", 2, -1)

TARGETS = {
    "AA": (A3_PLUS, A3_MINUS),
    "EA": (E2_PLUS, A4_MINUS),
    "EL": (E2_PLUS, L4_MINUS),
}
ROUTES = (
    TargetRoute("AA / split A3", A3_PLUS, A3_MINUS),
    TargetRoute("EA / split E2", E2_PLUS, A4_MINUS),
    TargetRoute("EA / split A4", A4_MINUS, E2_PLUS),
    TargetRoute("EL / split E2", E2_PLUS, L4_MINUS),
    TargetRoute("EL / split L4", L4_MINUS, E2_PLUS),
)


# ---------------------------------------------------------------------------
# Target and one-particle sector
# ---------------------------------------------------------------------------
check(
    "P4b-1: every selected target component contains the common (2,2) irrep",
    all(so4_contains(first.rep, second.rep, TARGET_REP) for first, second in TARGETS.values()),
)
check(
    "P4b-1: target Fock signs are AA=+, EA=EL=-",
    tuple(first.sign * second.sign for first, second in TARGETS.values())
    == (1, -1, -1),
)

# Every enumerated one-particle oscillator irrep has
# |2j_L-2j_R|=4 (E,L) or 2 (A),
# whereas TARGET_REP has zero difference.  This is an all-spin proof.
check(
    "P4b-2: no E/A/L oscillator one-particle candidate transforms in (2,2)",
    {
        abs(2 * TWICE_DISPLACEMENT[branch])
        for branch in BRANCHES
    }
    == {2, 4}
    and not any(
        Mode(branch, n, chirality).rep == TARGET_REP
        for branch in BRANCHES
        for n in range(2, 41)
        for chirality in (-1, 1)
    ),
)


# ---------------------------------------------------------------------------
# Complete affine three-particle image of each constituent split
# ---------------------------------------------------------------------------
for output in (A3_PLUS, E2_PLUS, A4_MINUS, L4_MINUS):
    check(
        f"P4b-3: affine tails exactly reproduce brute SO(4) pairs for {output.short()}",
        tail_pairs(output, 12) == brute_pairs(output, 12),
    )

expected_route_data = {
    "AA / split A3": (17, Counter({"EA": 4, "EL": 4, "AA": 3, "AL": 4, "LL": 2}), Counter({1: 8, -1: 9}), 8),
    "EA / split E2": (7, Counter({"AA": 3, "AL": 2, "LL": 2}), Counter({-1: 7}), 10),
    # Four naive identical-pair channels lie in the antisymmetric square
    # and are absent for bosonic creation operators.
    "EA / split A4": (28, Counter({"EA": 8, "EL": 6, "AA": 4, "AL": 8, "LL": 2}), Counter({1: 14, -1: 14}), 8),
    "EL / split E2": (7, Counter({"AA": 3, "AL": 2, "LL": 2}), Counter({-1: 7}), 10),
    "EL / split L4": (11, Counter({"EA": 2, "EL": 2, "AA": 3, "AL": 2, "LL": 2}), Counter({1: 7, -1: 4}), 8),
}

for route in ROUTES:
    tails = route.tails
    branch_counts = Counter(tail.branch_pair for tail in tails)
    sign_counts = Counter(route.intermediate_sign(tail) for tail in tails)
    minimum_energy = min(
        route.intermediate_energy(tail, tail.minimum_n) for tail in tails
    )
    expected = expected_route_data[route.label]
    check(
        f"P4b-3: complete tail classification for {route.label}",
        (len(tails), branch_counts, sign_counts, minimum_energy) == expected,
    )
    check(
        f"P4b-4: every selected Q tail for {route.label} has a safe semisimple D denominator",
        all(
            route.intermediate_energy(tail, tail.minimum_n) > SHELL_ENERGY
            and route.intermediate_energy(tail, tail.minimum_n)
            - SHELL_ENERGY
            >= 2
            for tail in tails
        ),
    )


# Explicit all-N witnesses.  Subscripts in the comments are compact energies:
# E_N has 2J=N and A_(N+1) has 2J=N.
def find_tail(
    output: Mode,
    first_branch: str,
    second_branch: str,
    first_chirality: int,
    second_chirality: int,
    delta: int,
) -> PairTail:
    matches = [
        tail
        for tail in pair_tail_families(
            output, apply_einstein_selection=True
        )
        if (
            tail.first_branch,
            tail.second_branch,
            tail.first_chirality,
            tail.second_chirality,
            tail.delta,
        )
        == (
            first_branch,
            second_branch,
            first_chirality,
            second_chirality,
            delta,
        )
    ]
    if len(matches) != 1:
        raise AssertionError("explicit infinite-family witness is not unique")
    return matches[0]


infinite_witnesses = (
    # A3+ -> E_N+ + A_(N+1)+; AA spectator A3-.
    (ROUTES[0], find_tail(A3_PLUS, "E", "A", 1, 1, 0), 2, 4, 1),
    # E2+ -> A_(N+1)+ + A_(N+1)+; EA spectator A4-.
    (ROUTES[1], find_tail(E2_PLUS, "A", "A", 1, 1, 0), 2, 6, -1),
    # A4- -> E_N- + A_(N+2)-; EA spectator E2+.
    (ROUTES[2], find_tail(A4_MINUS, "E", "A", -1, -1, 1), 2, 4, -1),
    # E2+ -> A_(N+1)+ + A_(N+1)+; EL spectator L4-.
    (ROUTES[3], find_tail(E2_PLUS, "A", "A", 1, 1, 0), 2, 6, -1),
    # L4- -> A_(N+1)- + A_(N+1)-; EL spectator E2+.
    (ROUTES[4], find_tail(L4_MINUS, "A", "A", -1, -1, 0), 2, 4, 1),
)
check(
    "P4b-5: every target route has an explicit unbounded all-spin three-particle family",
    all(
        tail.minimum_n <= minimum_n
        and all(
            vertex_allows(*tail.pair(n), tail.output)
            and route.intermediate_energy(tail, n) == 2 * n + constant
            and route.intermediate_sign(tail) == expected_sign
            for n in range(minimum_n, minimum_n + 8)
        )
        for route, tail, minimum_n, constant, expected_sign in infinite_witnesses
    ),
)


# Before applying the Einstein selection rule, solve Delta_Q=6 exactly on
# every route.  The one surviving incidence is E2+ spectator with
# L4- -> E2- E2-.  It is a P6 state and its EEL vertex is exactly zero.
on_shell_incidences: list[
    tuple[TargetRoute, PairTail, int, tuple[Mode, Mode]]
] = []
for route in ROUTES:
    for tail in pair_tail_families(
        route.split, apply_einstein_selection=False
    ):
        constant = (
            route.spectator.energy
            + OFFSET[tail.first_branch]
            + OFFSET[tail.second_branch]
            + tail.delta
        )
        numerator = SHELL_ENERGY - constant
        if numerator % 2:
            continue
        n = numerator // 2
        if n >= tail.minimum_n:
            on_shell_incidences.append((route, tail, n, tail.pair(n)))

check(
    "P4b-6: the only representation-allowed on-shell 3-particle incidence is the Einstein-zero E2^3 state",
    len(on_shell_incidences) == 1
    and on_shell_incidences[0][0].label == "EL / split L4"
    and on_shell_incidences[0][1].einstein_killed
    and sorted(mode.branch for mode in on_shell_incidences[0][3])
    == ["E", "E"],
)
check(
    "P4b-6: the E2^3 state is projected into P6 before any resolvent is formed",
    on_shell_incidences[0][0].spectator.energy
    + sum(mode.energy for mode in on_shell_incidences[0][3])
    == SHELL_ENERGY,
)


# ---------------------------------------------------------------------------
# Connected one-internal-line tree subset after the final P projection
# ---------------------------------------------------------------------------
def parity_components(channel: str) -> set[tuple[Mode, Mode]]:
    first, second = TARGETS[channel]
    component = mode_pair_key(first, second)
    conjugate = mode_pair_key(first.parity(), second.parity())
    return {component, conjugate}


def oscillator_modes(maximum_n: int) -> list[Mode]:
    return [
        Mode(branch, n, chirality)
        for branch in BRANCHES
        for n in range(2, maximum_n + 1)
        for chirality in (-1, 1)
    ]


@dataclass(frozen=True)
class ConnectedTreeCandidate:
    initial: str
    final: str
    intermediate: tuple[Mode, Mode, Mode]
    internal: Mode

    @property
    def energy(self) -> int:
        return sum(mode.energy for mode in self.intermediate)

    @property
    def sign(self) -> int:
        value = 1
        for mode in self.intermediate:
            value *= mode.sign
        return value


def connected_tree_candidates(
    initial_label: str, final_label: str
) -> set[ConnectedTreeCandidate]:
    """Finite oscillator t/u candidates selected by both external ends.

    At the first vertex a -> c+q while b is a spectator.  At the second,
    b+q -> d while c is already a final external particle.  Therefore q
    lies in two finite external tensor products.  Searching through n=16
    is exhaustive because either product bounds each component of q by the
    sum of two external doubled spins, which is at most eight here.
    """
    result = set()
    for initial in parity_components(initial_label):
        for final in parity_components(final_label):
            for active_index in range(2):
                active = initial[active_index]
                initial_spectator = initial[1 - active_index]
                for emitted_index in range(2):
                    emitted = final[emitted_index]
                    final_active = final[1 - emitted_index]
                    for internal in oscillator_modes(16):
                        if not vertex_allows(emitted, internal, active):
                            continue
                        if not vertex_allows(
                            initial_spectator, internal, final_active
                        ):
                            continue
                        if killed_by_einstein_selection(
                            (active.branch, emitted.branch, internal.branch)
                        ):
                            continue
                        if killed_by_einstein_selection(
                            (
                                final_active.branch,
                                initial_spectator.branch,
                                internal.branch,
                            )
                        ):
                            continue
                        intermediate = tuple(
                            sorted(
                                (initial_spectator, emitted, internal)
                            )
                        )
                        result.add(
                            ConnectedTreeCandidate(
                                initial_label,
                                final_label,
                                intermediate,  # type: ignore[arg-type]
                                internal,
                            )
                        )
    return result


expected_connected = {
    ("AA", "AA"): (4, Counter({10: 4}), Counter({-1: 4})),
    ("AA", "EA"): (8, Counter({8: 2, 10: 4, 12: 2}), Counter({1: 4, -1: 4})),
    ("AA", "EL"): (0, Counter(), Counter()),
    ("EA", "AA"): (8, Counter({8: 2, 10: 4, 12: 2}), Counter({1: 4, -1: 4})),
    ("EA", "EA"): (8, Counter({8: 2, 10: 2, 12: 2, 14: 2}), Counter({-1: 8})),
    ("EA", "EL"): (0, Counter(), Counter()),
    ("EL", "AA"): (0, Counter(), Counter()),
    ("EL", "EA"): (0, Counter(), Counter()),
    ("EL", "EL"): (0, Counter(), Counter()),
}

for initial_label, final_label in product(TARGETS, repeat=2):
    candidates = connected_tree_candidates(initial_label, final_label)
    actual = (
        len(candidates),
        Counter(candidate.energy for candidate in candidates),
        Counter(candidate.sign for candidate in candidates),
    )
    check(
        f"P4b-7: finite oscillator connected-tree candidates {initial_label}->{final_label}",
        actual == expected_connected[(initial_label, final_label)],
    )
    check(
        f"P4b-7: no connected oscillator candidate {initial_label}->{final_label} lies in P6",
        all(candidate.energy != SHELL_ENERGY for candidate in candidates),
    )


# Exact finiteness bound: if q occurs in c tensor a, each doubled component
# obeys q_i <= a_i+c_i.  The largest external component is four, hence no
# connected internal oscillator irrep can have a component above eight.
check(
    "P4b-7: the final P projection bounds every connected internal SO(4) component by eight",
    max(component for pair in TARGETS.values() for mode in pair for component in mode.rep)
    == 4
    and all(
        max(candidate.internal.rep) <= 8
        for initial_label, final_label in product(TARGETS, repeat=2)
        for candidate in connected_tree_candidates(initial_label, final_label)
    ),
)


# Ordinary compact-D denominator rail.  No flat-P0 nilpotent is present.
for route, tail, minimum_n, constant, _ in infinite_witnesses:
    for n in range(minimum_n, minimum_n + 4):
        delta_q = route.intermediate_energy(tail, n) - SHELL_ENERGY
        check(
            f"P4b-8: {route.label} N={n} uses 1/({delta_q})",
            delta_q == 2 * n + constant - SHELL_ENERGY and delta_q != 0,
        )


def print_summary(show_families: bool) -> None:
    print("\nTarget routes (one chirality; parity supplies the conjugate):")
    for route in ROUTES:
        tails = route.tails
        branch_counts = Counter(tail.branch_pair for tail in tails)
        sign_counts = Counter(route.intermediate_sign(tail) for tail in tails)
        minimum_energy = min(
            route.intermediate_energy(tail, tail.minimum_n)
            for tail in tails
        )
        print(
            f"  {route.label:15s} tails={len(tails):2d} "
            f"branches={dict(sorted(branch_counts.items()))} "
            f"signs={dict(sorted(sign_counts.items()))} "
            f"Delta_min={minimum_energy}"
        )
        if show_families:
            for tail in tails:
                denominator_constant = (
                    route.spectator.energy
                    + OFFSET[tail.first_branch]
                    + OFFSET[tail.second_branch]
                    + tail.delta
                    - SHELL_ENERGY
                )
                print(
                    "    "
                    + tail.short()
                    + f"; Delta_Q-6=2N{denominator_constant:+d}; "
                    + f"Fock sign={route.intermediate_sign(tail):+d}"
                )

    print("\nFinite connected oscillator t/u candidates after final P projection:")
    for initial_label, final_label in product(TARGETS, repeat=2):
        candidates = connected_tree_candidates(initial_label, final_label)
        energies = Counter(candidate.energy for candidate in candidates)
        signs = Counter(candidate.sign for candidate in candidates)
        print(
            f"  {initial_label}->{final_label}: {len(candidates)} candidates, "
            f"energies={dict(sorted(energies.items()))}, "
            f"signs={dict(sorted(signs.items()))}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-families", action="store_true")
    arguments = parser.parse_args()
    print_summary(arguments.show_families)
    if not PASS:
        raise SystemExit("CONFORMAL P4B INTERMEDIATES: FAIL")
    print("\nCONFORMAL P4B INTERMEDIATES: ALL PASS")
    print("Oscillator one-particle Q: empty in selected (2,2) block")
    print("Raw oscillator three-particle Q image: infinite affine spin tails")
    print("Connected one-internal-line tree subset after final P: finite")
    print("Full order-g^2 quantum resolvent requires the infinite spectral sum")


if __name__ == "__main__":
    main()
