#!/usr/bin/env python3
"""Inventory all representation-allowed proper-CK Taub blocks.

The proper conformal generators transform as ``(1/2,1/2)`` and lower or
raise compact energy by one.  Before computing further curvature components,
this certificate determines exactly which reduced one-particle kernels can
occur among the local gauge-reduced ``E/A/L`` oscillator towers.

Every allowed ``SU(2)_L x SU(2)_R`` coupling is multiplicity one.  Parity
pairs the two chiral copies, so one reduced coefficient per branch family
and energy level remains to be determined.  C2b currently fixes only two of
them: ``A_1 -> E_1`` and ``L_1 -> A_1``.

This is a workload and representation theorem, not the missing Taub map or
its symplectic moment-map identification.
The script does not infer a coefficient from representation allowance, does
not identify bilinear kernels with oscillator generators, and does not impose
the classical or global-BRST constraints.  ``--require-all-coefficients``
therefore fails closed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

try:
    from symbolic.verify_conformal_cubic_channels import (
        BRANCH_ORDER,
        Mode,
        so4_multiplicity,
        tower,
    )
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    from verify_conformal_cubic_channels import (
        BRANCH_ORDER,
        Mode,
        so4_multiplicity,
        tower,
    )


PROPER_CK_REP = (1, 1)  # doubled-spin notation
OFFSETS = {"E": 0, "A": 1, "L": 2}
DISPLACEMENTS = {"E": 2, "A": 1, "L": 2}
ALLOWED_BRANCH_FAMILIES = (
    ("E", "E"),
    ("A", "E"),
    ("A", "A"),
    ("L", "E"),
    ("L", "A"),
    ("L", "L"),
)


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


@dataclass(frozen=True)
class ProperBlock:
    source: Mode
    target: Mode

    @property
    def branch_family(self) -> tuple[str, str]:
        return self.source.branch, self.target.branch

    @property
    def parity_key(self) -> tuple[object, ...]:
        return (
            self.source.branch,
            self.source.twice_spin,
            self.target.branch,
            self.target.twice_spin,
        )

    @property
    def known_seed_family(self) -> str | None:
        if self.parity_key == ("A", 2, "E", 2):
            return "C2a/C2b A_1 -> E_1"
        if self.parity_key == ("L", 2, "A", 2):
            return "C2a/C2b L_1 -> A_1"
        return None

    def short(self) -> str:
        return f"{self.source.short()} -> {self.target.short()}"


def allowed_blocks(max_energy: int) -> tuple[ProperBlock, ...]:
    modes = tower(max_energy)
    blocks = [
        ProperBlock(source, target)
        for source in modes
        for target in modes
        if source.energy <= max_energy
        and target.energy == source.energy - 1
        and so4_multiplicity(source.rep, PROPER_CK_REP, target.rep) == 1
    ]
    return tuple(
        sorted(
            blocks,
            key=lambda block: (
                block.source.energy,
                BRANCH_ORDER[block.source.branch],
                BRANCH_ORDER[block.target.branch],
                block.source.chirality,
            ),
        )
    )


def parity_orbits(blocks: tuple[ProperBlock, ...]) -> dict[tuple[object, ...], tuple[ProperBlock, ...]]:
    output: dict[tuple[object, ...], list[ProperBlock]] = {}
    for block in blocks:
        output.setdefault(block.parity_key, []).append(block)
    return {key: tuple(value) for key, value in output.items()}


def expected_block_count(max_energy: int) -> int:
    if max_energy < 2:
        return 0
    if max_energy == 2:
        return 0
    if max_energy == 3:
        return 4
    return 14 + 12 * (max_energy - 4)


def expected_orbit_count(max_energy: int) -> int:
    return expected_block_count(max_energy) // 2


def stable_symbolic_blocks() -> set[tuple[str, str, int, int]]:
    """Solve the tensor-product conditions with the spin variable canceled.

    If the source has doubled spin ``n``, energy conservation fixes the
    target doubled spin to ``n+offset_source-1-offset_target``.  The two
    doubled magnetic highest weights must then differ from the source by
    ``+/-1``.  Both differences are independent of ``n``.
    """

    output: set[tuple[str, str, int, int]] = set()
    for source in OFFSETS:
        for target in OFFSETS:
            spin_shift = OFFSETS[source] - 1 - OFFSETS[target]
            for source_chirality in (-1, 1):
                for target_chirality in (-1, 1):
                    left_difference = (
                        spin_shift
                        + target_chirality * DISPLACEMENTS[target]
                        - source_chirality * DISPLACEMENTS[source]
                    )
                    right_difference = (
                        spin_shift
                        - target_chirality * DISPLACEMENTS[target]
                        + source_chirality * DISPLACEMENTS[source]
                    )
                    if abs(left_difference) == abs(right_difference) == 1:
                        output.add(
                            (
                                source,
                                target,
                                source_chirality,
                                target_chirality,
                            )
                        )
    return output


def level_families(blocks: tuple[ProperBlock, ...], energy: int) -> set[tuple[str, str]]:
    return {
        block.branch_family
        for block in blocks
        if block.source.energy == energy and block.source.chirality == 1
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-energy", type=int, default=8)
    parser.add_argument(
        "--require-all-coefficients",
        action="store_true",
        help="fail closed: this certificate inventories but does not compute every reduced coefficient",
    )
    parser.add_argument(
        "--require-full-moment-map",
        action="store_true",
        help="fail closed: charge polynomials and their zero locus are not supplied here",
    )
    args = parser.parse_args()
    if args.max_energy < 4:
        raise SystemExit("use --max-energy at least 4 to include both C2b seeds")

    for cutoff in range(3, args.max_energy + 1):
        blocks = allowed_blocks(cutoff)
        orbits = parity_orbits(blocks)
        check(
            f"C2c-I: exact block count through energy {cutoff}",
            len(blocks) == expected_block_count(cutoff),
        )
        check(
            f"C2c-I: exact parity-orbit count through energy {cutoff}",
            len(orbits) == expected_orbit_count(cutoff)
            and all(len(orbit) == 2 for orbit in orbits.values()),
        )

    blocks = allowed_blocks(args.max_energy)
    orbits = parity_orbits(blocks)
    symbolic_blocks = stable_symbolic_blocks()
    expected_symbolic_blocks = {
        (source, target, chirality, chirality)
        for source, target in ALLOWED_BRANCH_FAMILIES
        for chirality in (-1, 1)
    }
    check(
        "C2c-I: spin-independent tensor equations prove the six all-energy families",
        symbolic_blocks == expected_symbolic_blocks,
    )
    check(
        "C2c-I: every allowed proper-CK block preserves chirality",
        all(block.source.chirality == block.target.chirality for block in blocks),
    )
    check(
        "C2c-I: every spatial tensor-product multiplicity is exactly one",
        all(
            so4_multiplicity(block.source.rep, PROPER_CK_REP, block.target.rep)
            == 1
            for block in blocks
        ),
    )
    if args.max_energy >= 5:
        check(
            "C2c-I: the stable branch-family list has six entries per chirality",
            level_families(blocks, args.max_energy)
            == set(ALLOWED_BRANCH_FAMILIES),
        )
    check(
        "C2c-I: the energy-three boundary has E->E and A->E only",
        level_families(blocks, 3) == {("E", "E"), ("A", "E")},
    )
    check(
        "C2c-I: the energy-four boundary has five families before L->L starts",
        level_families(blocks, 4)
        == set(ALLOWED_BRANCH_FAMILIES) - {("L", "L")},
    )

    known = [orbit for orbit in orbits.values() if orbit[0].known_seed_family]
    check(
        "C2c-I: exactly two parity-reduced coefficients are fixed by C2b",
        len(known) == 2
        and {orbit[0].known_seed_family for orbit in known}
        == {"C2a/C2b A_1 -> E_1", "C2a/C2b L_1 -> A_1"},
    )

    through_four = parity_orbits(allowed_blocks(4))
    check(
        "C2c-I: five of seven parity-reduced coefficients through energy four remain unknown",
        len(through_four) == 7
        and sum(orbit[0].known_seed_family is None for orbit in through_four.values())
        == 5,
    )
    if args.max_energy >= 6:
        through_six = parity_orbits(allowed_blocks(6))
        check(
            "C2c-I: seventeen of nineteen parity-reduced coefficients through energy six remain unknown",
            len(through_six) == 19
            and sum(
                orbit[0].known_seed_family is None
                for orbit in through_six.values()
            )
            == 17,
        )

    print("maximum source energy:", args.max_energy)
    print("chiral block count:", len(blocks))
    print("parity-reduced coefficient count:", len(orbits))
    print(
        "known parity-reduced coefficients:",
        sum(orbit[0].known_seed_family is not None for orbit in orbits.values()),
    )
    print("stable source->target families:", ALLOWED_BRANCH_FAMILIES)
    print(
        "C2c-I STATUS: THE REPRESENTATION-ALLOWED PROPER-CK WORKLOAD "
        "IS EXACT. Values of the unseeded reduced coefficients, full "
        "equivariance, the fifteen charge polynomials, and global BRST "
        "cohomology remain open."
    )

    if args.require_all_coefficients:
        raise SystemExit(
            "representation allowance does not determine the unseeded reduced coefficients"
        )
    if args.require_full_moment_map:
        raise SystemExit(
            "the full fifteen-component quadratic moment map remains open"
        )


if __name__ == "__main__":
    main()
