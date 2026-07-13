#!/usr/bin/env python3
"""C2g-W: exact character rail for the on-shell Weyl-curvature module.

For one chirality, compare the cylinder ``E/A/L`` tower with the character
resolution

    V(2;2,0) - V(4;1,1) + V(5;1/2,1/2).

The first subtraction is the Bach equation and the last term is its
conservation identity.  The script proves the unrefined rational-character
identity and checks the fully ``SU(2)_L x SU(2)_R`` refined decomposition to
an arbitrary finite level.  A finite character check is not promoted to a
new proof of exactness of the differential sequence; the command-line guard
keeps that distinction explicit.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import sympy as sp


Weight = tuple[int, int]
Character = dict[Weight, int]


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def su2_weights(twice_spin: int) -> tuple[int, ...]:
    return tuple(range(-twice_spin, twice_spin + 1, 2))


def irrep_character(twice_left: int, twice_right: int) -> Character:
    return {
        (left, right): 1
        for left in su2_weights(twice_left)
        for right in su2_weights(twice_right)
    }


def multiply(first: Character, second: Character) -> Character:
    output: defaultdict[Weight, int] = defaultdict(int)
    for (left_a, right_a), multiplicity_a in first.items():
        for (left_b, right_b), multiplicity_b in second.items():
            output[left_a + left_b, right_a + right_b] += (
                multiplicity_a * multiplicity_b
            )
    return {weight: value for weight, value in output.items() if value}


TRANSLATION_WEIGHTS: tuple[Weight, ...] = (
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
)


def symmetric_translation_characters(maximum_level: int) -> tuple[Character, ...]:
    """Characters of ``Sym^level((1/2,1/2))`` through ``maximum_level``."""

    levels: list[defaultdict[Weight, int]] = [
        defaultdict(int) for _ in range(maximum_level + 1)
    ]
    levels[0][(0, 0)] = 1
    # Multiply the four geometric series, retaining total polynomial degree.
    for weight in TRANSLATION_WEIGHTS:
        updated: list[defaultdict[Weight, int]] = [
            defaultdict(int) for _ in range(maximum_level + 1)
        ]
        for old_level, character in enumerate(levels):
            for occupation in range(maximum_level - old_level + 1):
                for (left, right), multiplicity in character.items():
                    updated[old_level + occupation][
                        left + occupation * weight[0],
                        right + occupation * weight[1],
                    ] += multiplicity
        levels = updated
    return tuple(dict(character) for character in levels)


def add_scaled(target: defaultdict[Weight, int], source: Character, scale: int) -> None:
    for weight, multiplicity in source.items():
        target[weight] += scale * multiplicity
        if target[weight] == 0:
            del target[weight]


def resolution_character_at_energy(
    energy: int,
    translations: tuple[Character, ...],
) -> Character:
    """One-chirality weight character of the three-term resolution."""

    output: defaultdict[Weight, int] = defaultdict(int)
    terms = (
        (2, 4, 0, +1),   # self-dual Weyl primary (2;2,0)
        (4, 2, 2, -1),   # Bach equation (4;1,1)
        (5, 1, 1, +1),   # divergence identity (5;1/2,1/2)
    )
    for dimension, twice_left, twice_right, sign in terms:
        level = energy - dimension
        if level < 0:
            continue
        add_scaled(
            output,
            multiply(
                irrep_character(twice_left, twice_right),
                translations[level],
            ),
            sign,
        )
    return dict(output)


def irrep_multiplicities(character: Character) -> dict[Weight, int]:
    """Decompose a Weyl-invariant weight character into compact irreps."""

    maximum_left = max((abs(weight[0]) for weight in character), default=0)
    maximum_right = max((abs(weight[1]) for weight in character), default=0)

    def weight_multiplicity(left: int, right: int) -> int:
        return character.get((left, right), 0)

    output: dict[Weight, int] = {}
    for left in range(maximum_left + 1):
        for right in range(maximum_right + 1):
            multiplicity = (
                weight_multiplicity(left, right)
                - weight_multiplicity(left + 2, right)
                - weight_multiplicity(left, right + 2)
                + weight_multiplicity(left + 2, right + 2)
            )
            if multiplicity:
                output[left, right] = multiplicity
    return output


def expected_towers(energy: int) -> dict[Weight, int]:
    output: dict[Weight, int] = {}
    if energy >= 2:
        output[energy + 2, energy - 2] = 1
    if energy >= 3:
        output[energy, energy - 2] = 1
    if energy >= 4:
        output[energy, energy - 4] = 1
    return output


def irrep_dimension(twice_left: int, twice_right: int) -> int:
    return (twice_left + 1) * (twice_right + 1)


def tower_dimension(energy: int) -> int:
    return sum(
        multiplicity * irrep_dimension(*highest_weight)
        for highest_weight, multiplicity in expected_towers(energy).items()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-energy", type=int, default=12)
    parser.add_argument(
        "--claim-exact-sequence",
        action="store_true",
        help="fail closed: character equality alone does not prove exactness of the maps",
    )
    args = parser.parse_args()
    if args.max_energy < 6:
        raise SystemExit("max-energy must be at least six for the prediction rail")

    q = sp.symbols("q")
    one_chirality_resolution = sp.factor(
        (5 * q**2 - 9 * q**4 + 4 * q**5) / (1 - q) ** 4
    )
    # Closed tower expressions obtained directly from standard power sums.
    e_closed = q**2 * (5 - 3 * q) / (1 - q) ** 3
    a_closed = q**3 * (8 - 9 * q + 3 * q**2) / (1 - q) ** 3
    l_closed = q**4 * (5 - 3 * q) / (1 - q) ** 3
    one_chirality_towers = sp.factor(e_closed + a_closed + l_closed)
    published_two_chiralities = (
        10 * q**2 - 18 * q**4 + 8 * q**5
    ) / (1 - q) ** 4

    check(
        "C2g-W1: the Bach-resolution character equals the E/A/L tower character",
        sp.simplify(one_chirality_resolution - one_chirality_towers) == 0,
    )
    check(
        "C2g-W1: parity completion reproduces the published Weyl-graviton character",
        sp.simplify(2 * one_chirality_resolution - published_two_chiralities) == 0,
    )
    translations = symmetric_translation_characters(args.max_energy - 2)
    refined_decompositions: dict[int, dict[Weight, int]] = {}
    for energy in range(2, args.max_energy + 1):
        character = resolution_character_at_energy(energy, translations)
        decomposition = irrep_multiplicities(character)
        refined_decompositions[energy] = decomposition
        check(
            f"C2g-W2: refined resolution gives exactly E/A/L at energy {energy}",
            decomposition == expected_towers(energy),
        )
        check(
            f"C2g-W2: refined dimension matches the closed tower count at energy {energy}",
            sum(
                multiplicity * irrep_dimension(*highest_weight)
                for highest_weight, multiplicity in decomposition.items()
            )
            == tower_dimension(energy),
        )

    # At level two the unconstrained primary Verma module contains the Bach
    # irrep.  The resolution removes precisely this nine-dimensional block.
    raw_level_two = irrep_multiplicities(
        multiply(irrep_character(4, 0), translations[2])
    )
    check(
        "C2g-W3: the unconstrained level-two primary contains the (1,1) Bach irrep once",
        raw_level_two.get((2, 2)) == 1,
    )
    removed = dict(raw_level_two)
    removed[(2, 2)] -= 1
    if removed[(2, 2)] == 0:
        del removed[(2, 2)]
    check(
        "C2g-W3: removing the Bach primary leaves exactly the energy-four E/A/L inventory",
        removed == expected_towers(4),
    )

    expected_energy_five = {(7, 3): 1, (5, 3): 1, (5, 1): 1}
    expected_energy_six = {(8, 4): 1, (6, 4): 1, (6, 2): 1}
    check(
        "C2g-W4: energy-five irreps and one-chirality dimension are (32,24,12)",
        refined_decompositions[5] == expected_energy_five
        and tuple(irrep_dimension(*weight) for weight in expected_energy_five)
        == (32, 24, 12),
    )
    check(
        "C2g-W4: energy-six irreps and one-chirality dimension are (45,35,21)",
        refined_decompositions[6] == expected_energy_six
        and tuple(irrep_dimension(*weight) for weight in expected_energy_six)
        == (45, 35, 21),
    )
    two_chirality_dimensions = {
        energy: 2 * tower_dimension(energy) for energy in range(2, 7)
    }
    check(
        "C2g-W4: two-chirality dimensions through energy six are 10,40,82,136,202",
        tuple(two_chirality_dimensions.values()) == (10, 40, 82, 136, 202),
    )
    check(
        "C2g-W4: cumulative two-chirality buffer through energy six has dimension 470",
        sum(two_chirality_dimensions.values()) == 470,
    )

    print("one-chirality character:", one_chirality_resolution)
    print("energy-five decomposition:", refined_decompositions[5])
    print("energy-six decomposition:", refined_decompositions[6])
    print(
        "C2g-W STATUS: EXACT CHARACTER-LEVEL IDENTIFICATION OF THE E/A/L "
        "TOWER WITH THE ON-SHELL CHIRAL WEYL MODULE THROUGH THE BACH "
        "EQUATION AND ITS DIVERGENCE IDENTITY. Exactness of the differential "
        "sequence is taken from the field equations/operator resolution, not "
        "deduced from finite character matching alone."
    )
    if args.claim_exact_sequence:
        raise SystemExit(
            "character equality does not by itself certify exactness of the Bach complex"
        )


if __name__ == "__main__":
    main()
