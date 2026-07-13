#!/usr/bin/env python3
"""Exact reduced-channel enumerator for cubic Weyl gravity on R x S^3.

The local gauge-reduced oscillator spectrum used here is the three-tower
cylinder spectrum certified in ``verify_conformal_cylinder_form.py``:

    E_J : Delta=2J,   (J+1,J-1) plus parity, sign +;
    A_J : Delta=2J+1, (J+1/2,J-1/2) plus parity, sign -;
    L_J : Delta=2J+2, (J+1,J-1) plus parity, sign -.

All spins are stored as twice-spins, so the calculation uses integer
arithmetic only.  The script enumerates one-to-two resonant reduced matrix
elements.  Spectator copies in higher Fock sectors introduce no new reduced
cubic family.

There are two logically separate outputs.

* An all-energy affine triangle analysis proves which branch/chirality
  families can occur for arbitrary half-integer J>=1.
* A configurable finite-energy enumeration is a deterministic regression of
  the full parity-completed tower.  It is evidence about counts only; it is
  not used as the all-energy proof.

The enumeration imposes compact-energy resonance, both SU(2) triangle and
integrality rules, Bose symmetry for identical inputs, parity pairing, the
inherited Fock signs, and the exact Einstein-subsector selection rule
``A(E,E,X)=0``.  Each fixed chiral SU(2)_L x SU(2)_R product is
multiplicity-free.  More than one parity orbit for a fixed process is
reported as reduced-channel multiplicity.

This representation calculation does not impose the compact-space global
conformal/Taub constraints.  It therefore classifies candidate oscillator
channels, not by itself matrix elements on the final full BRST cohomology.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations_with_replacement, product


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


def twice_representation(
    branch: str, twice_spin: int, chirality: int
) -> tuple[int, int]:
    """Return (2 j_L, 2 j_R) for one parity component."""
    displacement = TWICE_DISPLACEMENT[branch]
    return (
        twice_spin + chirality * displacement,
        twice_spin - chirality * displacement,
    )


def compact_energy(branch: str, twice_spin: int) -> int:
    return twice_spin + OFFSET[branch]


def irrep_dimension(rep: tuple[int, int]) -> int:
    return (rep[0] + 1) * (rep[1] + 1)


def su2_multiplicity(first: int, second: int, output: int) -> int:
    """Multiplicity in an SU(2) tensor product, using twice-spins."""
    return int(
        abs(first - second) <= output <= first + second
        and (first + second - output) % 2 == 0
    )


def so4_multiplicity(
    first: tuple[int, int],
    second: tuple[int, int],
    output: tuple[int, int],
) -> int:
    return su2_multiplicity(first[0], second[0], output[0]) * su2_multiplicity(
        first[1], second[1], output[1]
    )


def symmetric_square_allows(
    source: tuple[int, int], output: tuple[int, int]
) -> bool:
    """Whether output occurs in Sym^2(source), rather than its wedge square."""
    if so4_multiplicity(source, source, output) != 1:
        return False
    # In j tensor j -> J the exchange sign is (-1)^(2j-J).  A bosonic
    # SO(4) product carries the product of the two SU(2) exchange signs.
    assert output[0] % 2 == 0 and output[1] % 2 == 0
    exponent = (
        source[0]
        - output[0] // 2
        + source[1]
        - output[1] // 2
    )
    return exponent % 2 == 0


@dataclass(frozen=True)
class Mode:
    branch: str
    twice_spin: int
    chirality: int

    @property
    def energy(self) -> int:
        return compact_energy(self.branch, self.twice_spin)

    @property
    def rep(self) -> tuple[int, int]:
        return twice_representation(
            self.branch, self.twice_spin, self.chirality
        )

    @property
    def sign(self) -> int:
        return ONE_PARTICLE_SIGN[self.branch]

    @property
    def dimension(self) -> int:
        return irrep_dimension(self.rep)

    @property
    def sort_key(self) -> tuple[int, int, int, int]:
        return (
            self.energy,
            BRANCH_ORDER[self.branch],
            self.twice_spin,
            self.chirality,
        )

    @property
    def input_sort_key(self) -> tuple[int, int, int]:
        """Canonical order for the unordered pair in a cubic channel."""
        return (BRANCH_ORDER[self.branch], self.twice_spin, self.chirality)

    def parity(self) -> "Mode":
        return Mode(self.branch, self.twice_spin, -self.chirality)

    def short(self) -> str:
        handedness = "+" if self.chirality > 0 else "-"
        return (
            f"{self.branch}(2J={self.twice_spin},D={self.energy},"
            f"{handedness};2j=({self.rep[0]},{self.rep[1]}))"
        )


def ordered_modes(first: Mode, second: Mode) -> tuple[Mode, Mode]:
    return tuple(  # type: ignore[return-value]
        sorted((first, second), key=lambda mode: mode.input_sort_key)
    )


@dataclass(frozen=True)
class Channel:
    inputs: tuple[Mode, Mode]
    output: Mode

    @property
    def input_sign(self) -> int:
        return self.inputs[0].sign * self.inputs[1].sign

    @property
    def output_sign(self) -> int:
        return self.output.sign

    @property
    def sign_relation(self) -> str:
        return "same" if self.input_sign == self.output_sign else "opposite"

    @property
    def fields(self) -> tuple[str, str, str]:
        return (
            self.inputs[0].branch,
            self.inputs[1].branch,
            self.output.branch,
        )

    @property
    def family(self) -> str:
        return "".join(sorted(self.fields, key=BRANCH_ORDER.__getitem__))

    @property
    def killed_by_einstein_selection(self) -> bool:
        # Exact consistent-subsector consequence: EEE and EEX vanish.
        return sum(branch != "E" for branch in self.fields) <= 1

    def parity(self) -> "Channel":
        return Channel(
            ordered_modes(self.inputs[0].parity(), self.inputs[1].parity()),
            self.output.parity(),
        )

    def process_key(self) -> tuple[object, ...]:
        return (
            self.inputs[0].branch,
            self.inputs[0].twice_spin,
            self.inputs[1].branch,
            self.inputs[1].twice_spin,
            self.output.branch,
            self.output.twice_spin,
        )

    def sort_key(self) -> tuple[object, ...]:
        return (
            self.output.energy,
            self.process_key(),
            self.inputs[0].chirality,
            self.inputs[1].chirality,
            self.output.chirality,
        )

    def short(self) -> str:
        return (
            f"{self.inputs[0].short()} + {self.inputs[1].short()}"
            f" -> {self.output.short()}"
        )


def tower(max_energy: int) -> list[Mode]:
    modes: list[Mode] = []
    for branch in BRANCHES:
        for twice_spin in range(2, max_energy - OFFSET[branch] + 1):
            if compact_energy(branch, twice_spin) > max_energy:
                continue
            for chirality in (-1, 1):
                mode = Mode(branch, twice_spin, chirality)
                assert min(mode.rep) >= 0
                modes.append(mode)
    return sorted(modes, key=lambda mode: mode.sort_key)


def enumerate_channels(max_energy: int) -> list[Channel]:
    modes = tower(max_energy)
    by_energy: dict[int, list[Mode]] = defaultdict(list)
    for mode in modes:
        by_energy[mode.energy].append(mode)

    channels: list[Channel] = []
    for first, second in combinations_with_replacement(modes, 2):
        output_energy = first.energy + second.energy
        if output_energy > max_energy:
            continue
        for output in by_energy[output_energy]:
            if so4_multiplicity(first.rep, second.rep, output.rep) != 1:
                continue
            if first == second and not symmetric_square_allows(
                first.rep, output.rep
            ):
                continue
            channels.append(Channel(ordered_modes(first, second), output))
    return sorted(set(channels), key=lambda channel: channel.sort_key())


def parity_orbits(channels: list[Channel]) -> list[frozenset[Channel]]:
    channel_set = set(channels)
    unseen = set(channels)
    orbits = []
    while unseen:
        channel = min(unseen, key=lambda item: item.sort_key())
        orbit = frozenset((channel, channel.parity()))
        assert orbit <= channel_set
        unseen -= orbit
        orbits.append(orbit)
    return orbits


@dataclass(frozen=True)
class AffineChannel:
    input_branches: tuple[str, str]
    output_branch: str
    chiralities: tuple[int, int, int]
    first_minimum: Fraction
    second_minimum: Fraction
    left_depth: int
    right_depth: int

    @property
    def orientation(self) -> str:
        return "".join(self.input_branches) + "->" + self.output_branch


def affine_channel(
    first_branch: str,
    second_branch: str,
    output_branch: str,
    chiralities: tuple[int, int, int],
) -> AffineChannel | None:
    """Solve both SU(2) products for arbitrary input spins exactly.

    Energy fixes J_out=J_1+J_2+delta.  In either SU(2) factor write
    j_out=j_1+j_2-r.  Tensor-product membership is equivalent to integer
    r>=0 and r<=2 min(j_1,j_2).  The latter gives exact lower bounds on
    J_1,J_2, with no finite scan.
    """
    first_chirality, second_chirality, output_chirality = chiralities
    delta = Fraction(
        OFFSET[first_branch]
        + OFFSET[second_branch]
        - OFFSET[output_branch],
        2,
    )
    displacement = {
        branch: Fraction(TWICE_DISPLACEMENT[branch], 2)
        for branch in BRANCHES
    }
    left_gap = (
        delta
        + output_chirality * displacement[output_branch]
        - first_chirality * displacement[first_branch]
        - second_chirality * displacement[second_branch]
    )
    right_gap = (
        delta
        - output_chirality * displacement[output_branch]
        + first_chirality * displacement[first_branch]
        + second_chirality * displacement[second_branch]
    )
    depths = (-left_gap, -right_gap)
    if any(depth < 0 or depth.denominator != 1 for depth in depths):
        return None

    first_minimum = max(
        Fraction(1),
        depths[0] / 2
        - first_chirality * displacement[first_branch],
        depths[1] / 2
        + first_chirality * displacement[first_branch],
    )
    second_minimum = max(
        Fraction(1),
        depths[0] / 2
        - second_chirality * displacement[second_branch],
        depths[1] / 2
        + second_chirality * displacement[second_branch],
    )
    return AffineChannel(
        (first_branch, second_branch),
        output_branch,
        chiralities,
        first_minimum,
        second_minimum,
        int(depths[0]),
        int(depths[1]),
    )


def all_affine_channels() -> list[AffineChannel]:
    channels = []
    for first_branch, second_branch in combinations_with_replacement(
        BRANCHES, 2
    ):
        for output_branch in BRANCHES:
            for chiralities in product((-1, 1), repeat=3):
                channel = affine_channel(
                    first_branch,
                    second_branch,
                    output_branch,
                    chiralities,
                )
                if channel is not None:
                    channels.append(channel)
    return channels


def parity_representative(
    chiralities: tuple[int, int, int]
) -> tuple[int, int, int]:
    conjugate = tuple(-value for value in chiralities)
    return min(chiralities, conjugate)


def run(max_energy: int, show_channels: bool, show_modes: bool) -> None:
    check("P2-1: cutoff includes the first EAA and AAL shells", max_energy >= 6)

    # Tower/character regression: summing both parity irreps reproduces the
    # exact C0b degeneracies at every energy below the chosen cutoff.
    modes = tower(max_energy)
    dimensions = Counter()
    signed_dimensions = Counter()
    for mode in modes:
        dimensions[mode.energy] += mode.dimension
        signed_dimensions[mode.energy] += mode.sign * mode.dimension

    def expected_dimensions(energy: int) -> tuple[int, int]:
        lower = 2 * (energy - 1) * (energy + 3) if energy >= 2 else 0
        vector = 2 * (energy - 1) * (energy + 1) if energy >= 3 else 0
        upper = 2 * (energy - 3) * (energy + 1) if energy >= 4 else 0
        return lower + vector + upper, lower - vector - upper

    check(
        "P2-1: parity-completed towers reproduce the C0b character exactly",
        all(
            (dimensions[energy], signed_dimensions[energy])
            == expected_dimensions(energy)
            for energy in range(2, max_energy + 1)
        ),
    )

    # All-energy theorem.  This classification uses affine tensor-product
    # depths, not the finite cutoff enumeration below.
    affine = all_affine_channels()
    orientations = {channel.orientation for channel in affine}
    expected_orientations = {"EE->A", "EE->L", "EA->A", "EA->L", "AA->L"}
    check(
        "P2-2: exact all-energy triangle analysis leaves five orientations",
        orientations == expected_orientations,
    )
    surviving_orientations = {
        channel.orientation
        for channel in affine
        if sum(
            branch != "E"
            for branch in (*channel.input_branches, channel.output_branch)
        )
        >= 2
    }
    check(
        "P2-2: Einstein selection leaves exactly EAA, EAL, and AAL",
        surviving_orientations == {"EA->A", "EA->L", "AA->L"},
    )

    affine_by_orientation: dict[str, list[AffineChannel]] = defaultdict(list)
    for channel in affine:
        affine_by_orientation[channel.orientation].append(channel)

    eaa = affine_by_orientation["EA->A"]
    aal = affine_by_orientation["AA->L"]
    eal = affine_by_orientation["EA->L"]
    check(
        "P2-3: EAA is one parity orbit for all J_E,J_A>=1",
        {
            (
                parity_representative(channel.chiralities),
                channel.first_minimum,
                channel.second_minimum,
            )
            for channel in eaa
        }
        == {((-1, 1, -1), Fraction(1), Fraction(1))},
    )
    check(
        "P2-3: AAL is one same-chirality parity orbit for all J_1,J_2>=1",
        {
            (
                parity_representative(channel.chiralities),
                channel.first_minimum,
                channel.second_minimum,
            )
            for channel in aal
        }
        == {((-1, -1, -1), Fraction(1), Fraction(1))},
    )
    check(
        "P2-3: EAL has a second reduced channel precisely for J_E>=3/2",
        {
            (
                parity_representative(channel.chiralities),
                channel.first_minimum,
                channel.second_minimum,
            )
            for channel in eal
        }
        == {
            ((-1, -1, -1), Fraction(1), Fraction(1)),
            ((-1, 1, -1), Fraction(3, 2), Fraction(1)),
        },
    )

    # The only identical surviving input is AA->L.  At J_1=J_2 its extremal
    # same-chirality output belongs to the symmetric square for every 2J.
    check(
        "P2-4: Bose symmetry retains the all-spin identical-A AAL channel",
        all(
            symmetric_square_allows(
                twice_representation("A", twice_spin, chirality),
                twice_representation("L", 2 * twice_spin, chirality),
            )
            for twice_spin in range(2, 30)
            for chirality in (-1, 1)
        ),
    )

    channels = enumerate_channels(max_energy)
    orbits = parity_orbits(channels)
    surviving = [
        channel for channel in channels if not channel.killed_by_einstein_selection
    ]
    surviving_orbits = parity_orbits(surviving)

    check(
        "P2-5: finite enumerator contains only the all-energy orientations",
        {
            "".join(channel.inputs[index].branch for index in range(2))
            + "->"
            + channel.output.branch
            for channel in channels
        }
        <= expected_orientations,
    )
    check(
        "P2-5: finite surviving families are exactly EAA, EAL, AAL",
        {channel.family for channel in surviving} == {"EAA", "EAL", "AAL"},
    )
    check(
        "P2-5: every fixed-chirality SO(4) reduced product has multiplicity one",
        all(
            so4_multiplicity(
                channel.inputs[0].rep,
                channel.inputs[1].rep,
                channel.output.rep,
            )
            == 1
            for channel in channels
        ),
    )

    processes: dict[tuple[object, ...], list[Channel]] = defaultdict(list)
    for channel in surviving:
        processes[channel.process_key()].append(channel)
    process_multiplicities = {
        key: len(parity_orbits(value)) for key, value in processes.items()
    }
    multiply_reduced = {
        key: multiplicity
        for key, multiplicity in process_multiplicities.items()
        if multiplicity > 1
    }
    check(
        "P2-6: finite multiplicity>1 processes are exactly high-spin EAL",
        bool(multiply_reduced)
        and all(
            key[0] == "E"
            and key[2] == "A"
            and key[4] == "L"
            and key[1] >= 3
            and multiplicity == 2
            for key, multiplicity in multiply_reduced.items()
        ),
    )

    # Freeze the first complete nontrivial shells independently of the CLI
    # cutoff.  These counts make changes to parity/Bose bookkeeping visible.
    low_channels = enumerate_channels(6)
    low_orbits = parity_orbits(low_channels)
    low_surviving = [
        channel
        for channel in low_channels
        if not channel.killed_by_einstein_selection
    ]
    low_processes: dict[tuple[object, ...], list[Channel]] = defaultdict(list)
    for channel in low_surviving:
        low_processes[channel.process_key()].append(channel)
    low_family_processes = Counter()
    low_family_orbits = Counter()
    for process_channels in low_processes.values():
        family = process_channels[0].family
        low_family_processes[family] += 1
        low_family_orbits[family] += len(parity_orbits(process_channels))
    check(
        "P2-7: exact Delta<=6 regression fixes all parity/Bose counts",
        len(low_channels) == 32
        and len(low_orbits) == 16
        and len(low_surviving) == 16
        and len(parity_orbits(low_surviving)) == 8
        and low_family_processes == Counter({"EAA": 3, "EAL": 3, "AAL": 1})
        and low_family_orbits == Counter({"EAL": 4, "EAA": 3, "AAL": 1}),
    )

    family_orbit_counts = Counter()
    family_process_counts = Counter()
    family_signs: dict[str, set[str]] = defaultdict(set)
    for key, process_channels in processes.items():
        family = process_channels[0].family
        family_process_counts[family] += 1
        family_orbit_counts[family] += len(parity_orbits(process_channels))
        family_signs[family].add(process_channels[0].sign_relation)

    print("\nALL-ENERGY RESULT (proved by affine SU(2)xSU(2) depths)")
    print("  representation-allowed: EE->A, EE->L, EA->A, EA->L, AA->L")
    print("  Einstein-selected zeros: EE->A, EE->L")
    print("  surviving families: EAA (same sign), EAL (same sign), AAL (opposite sign)")
    print("  EAL multiplicity: 1 parity orbit at J_E=1; 2 at J_E>=3/2")
    print("  all fixed-chirality SU(2)xSU(2) tensor products have multiplicity 1")

    print(f"\nFINITE REGRESSION (D_out <= {max_energy}; not the theorem proof)")
    print(
        f"  one-particle chiral irreps={len(modes)}, "
        f"total state dimension at D<=cutoff={sum(dimensions.values())}"
    )
    print(
        f"  chiral reduced channels={len(channels)}, parity orbits={len(orbits)}, "
        f"surviving channels={len(surviving)}, surviving parity orbits={len(surviving_orbits)}"
    )
    for family in ("EAA", "EAL", "AAL"):
        signs = ",".join(sorted(family_signs[family]))
        print(
            f"  {family}: processes={family_process_counts[family]}, "
            f"parity-reduced channels={family_orbit_counts[family]}, sign={signs}"
        )
    print(f"  multiplicity>1 process count={len(multiply_reduced)} (all EAL)")

    if show_modes:
        print("\nPHYSICAL ONE-PARTICLE COHOMOLOGY IRREPS")
        for mode in modes:
            print(
                f"  {mode.short()}; sign={mode.sign:+d}; dim={mode.dimension}"
            )

    if show_channels:
        print("\nSURVIVING PARITY-ORBIT REPRESENTATIVES")
        for orbit in surviving_orbits:
            representative = min(orbit, key=lambda channel: channel.sort_key())
            process_channels = processes[representative.process_key()]
            multiplicity = len(parity_orbits(process_channels))
            print(
                f"  [{representative.family}; {representative.sign_relation}; "
                f"process multiplicity={multiplicity}] {representative.short()}"
            )

    if not PASS:
        raise SystemExit("CONFORMAL CUBIC CHANNEL ENUMERATOR: FAIL")
    print("\nCONFORMAL CUBIC CHANNEL ENUMERATOR: ALL PASS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-energy",
        type=int,
        default=12,
        help="maximum compact output energy for the finite regression (default: 12)",
    )
    parser.add_argument(
        "--show-channels",
        action="store_true",
        help="print one representative of every parity orbit",
    )
    parser.add_argument(
        "--show-modes",
        action="store_true",
        help="print every physical chiral one-particle irrep through the cutoff",
    )
    args = parser.parse_args()
    if args.max_energy < 6:
        parser.error("--max-energy must be at least 6")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    run(arguments.max_energy, arguments.show_channels, arguments.show_modes)
