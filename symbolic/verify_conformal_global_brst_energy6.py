#!/usr/bin/env python3
"""C2g-N6: cutoff-complete absolute global BRST at degree two.

This certificate constructs the complete free bosonic matter inventory through
total cylinder energy six and tensors it, lazily, with the residual global
``so(4,2)`` ghost exterior algebra.  The target window is

    total compact degree delta = 2,       ghost number g = 4,

with adjacent cochains C3, C5 and C6 included for the differential and its
nilpotency audit.  Matter particle number is retained as an exact grading.

The large sparse matrices are not rank-reduced.  A stronger exact statement
is available.  If ``D`` is the compact-energy generator, the absolute
Chevalley--Eilenberg differential obeys Cartan's identity

    d i_D + i_D d = L_D = delta I.

Consequently ``h=i_D/2`` contracts the entire delta-two complex and H4 is
zero separately in every particle-number sector.  The script verifies all
ingredients of that identity in the conventions of C2g-N: the graded Lie
brackets, the ghost Cartan formula, the wedge/contraction anticommutator,
the all-level matter grading, representative columns of a lazy exact
differential, and the energy-six exterior-saturation boundary.

This is a global-only free-module result.  It does not contain the local
Diff x Weyl BV complex and does not identify this CE cohomology with the
physical interacting pure-Weyl state space.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement
from typing import TypeAlias

import sympy as sp

try:
    from symbolic import verify_conformal_fock_energy4 as fock_data
    from symbolic import verify_conformal_global_brst_window as global_brst
    from symbolic.verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_fock_energy4 as fock_data
    import verify_conformal_global_brst_window as global_brst
    from verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS


DELTA = 2
TARGET_GHOST_NUMBER = 4
MAX_ENERGY = 6
Occupation = tuple[int, ...]
CochainKey = tuple[global_brst.Monomial, Occupation]
SparseCochain: TypeAlias = dict[CochainKey, sp.Expr]


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def exact_zero(value: sp.Expr) -> bool:
    return sp.simplify(value) == 0


def add(output: dict[object, sp.Expr], key: object, value: sp.Expr) -> None:
    if value == 0:
        return
    output[key] = output.get(key, sp.Integer(0)) + value


def clean(output: dict[object, sp.Expr]) -> dict[object, sp.Expr]:
    return {
        key: simplified
        for key, value in output.items()
        if (simplified := sp.simplify(value)) != 0
    }


@dataclass(frozen=True)
class MatterWindow:
    one_particle: fock_data.OneParticleModule
    basis: tuple[Occupation, ...]
    energy: dict[Occupation, int]
    by_energy_particle: dict[tuple[int, int], tuple[Occupation, ...]]


def enumerate_energy_six_fock(
    one_particle: fock_data.OneParticleModule,
) -> tuple[Occupation, ...]:
    """Enumerate the complete bosonic Fock space of total energy <= 6.

    Since the lowest one-particle energy is two, there are at most three
    particles.  Three-particle states necessarily consist of three E2
    oscillators, so no large unconstrained Cartesian enumeration is needed.
    """

    by_energy = {
        energy: tuple(
            state.index for state in one_particle.states if state.energy == energy
        )
        for energy in range(MAX_ENERGY + 1)
    }
    output: list[Occupation] = [()]
    output.extend(
        (index,)
        for energy in range(2, MAX_ENERGY + 1)
        for index in by_energy[energy]
    )
    for first_energy in range(2, MAX_ENERGY + 1):
        for second_energy in range(first_energy, MAX_ENERGY + 1):
            if first_energy + second_energy > MAX_ENERGY:
                continue
            if first_energy == second_energy:
                output.extend(
                    combinations_with_replacement(by_energy[first_energy], 2)
                )
            else:
                output.extend(
                    (first, second)
                    for first in by_energy[first_energy]
                    for second in by_energy[second_energy]
                )
    output.extend(combinations_with_replacement(by_energy[2], 3))

    oscillator_energy = tuple(state.energy for state in one_particle.states)
    return tuple(sorted(
        output,
        key=lambda occupation: (
            sum(oscillator_energy[index] for index in occupation),
            len(occupation),
            occupation,
        ),
    ))


def build_matter_window() -> MatterWindow:
    one_particle = fock_data.assemble_one_particle(MAX_ENERGY)
    basis = enumerate_energy_six_fock(one_particle)
    oscillator_energy = tuple(state.energy for state in one_particle.states)
    energy = {
        occupation: sum(oscillator_energy[index] for index in occupation)
        for occupation in basis
    }
    grouped: dict[tuple[int, int], list[Occupation]] = defaultdict(list)
    for occupation in basis:
        grouped[(energy[occupation], len(occupation))].append(occupation)
    return MatterWindow(
        one_particle,
        basis,
        energy,
        {key: tuple(value) for key, value in grouped.items()},
    )


def verify_matter_inventory(window: MatterWindow) -> None:
    one_particle = Counter(state.energy for state in window.one_particle.states)
    total = Counter(window.energy.values())
    refined = Counter(
        (window.energy[occupation], len(occupation)) for occupation in window.basis
    )
    check(
        "C2g-N6: the exact one-particle E2--E6 dimensions are 10,40,82,136,202",
        one_particle == {2: 10, 3: 40, 4: 82, 5: 136, 6: 202}
        and window.one_particle.dimension == 470,
    )
    check(
        "C2g-N6: the complete Fock energy dimensions through six are 1,10,40,137,536,2062",
        total == {0: 1, 2: 10, 3: 40, 4: 137, 5: 536, 6: 2062}
        and len(window.basis) == 2786,
    )
    check(
        "C2g-N6: the energy-six split is 202 one-, 1640 two-, and 220 three-particle states",
        refined == {
            (0, 0): 1,
            (2, 1): 10,
            (3, 1): 40,
            (4, 1): 82,
            (4, 2): 55,
            (5, 1): 136,
            (5, 2): 400,
            (6, 1): 202,
            (6, 2): 1640,
            (6, 3): 220,
        },
    )
    check(
        "C2g-N6: no omitted four-particle state can occur below energy seven",
        all(len(occupation) <= 3 for occupation in window.basis)
        and 4 * min(state.energy for state in window.one_particle.states) > MAX_ENERGY,
    )


def ghost_monomials(
    data: global_brst.LieData, ghost_number: int, energy: int
) -> tuple[global_brst.Monomial, ...]:
    return tuple(
        monomial
        for monomial in combinations(range(15), ghost_number)
        if global_brst.ghost_energy(monomial, data.degrees) == energy
    )


@dataclass(frozen=True)
class InventoryRow:
    ghost_number: int
    matter_energy: int
    particle_number: int
    ghost_energy: int
    ghost_dimension: int
    matter_dimension: int

    @property
    def cochain_dimension(self) -> int:
        return self.ghost_dimension * self.matter_dimension


def build_inventory(
    data: global_brst.LieData, window: MatterWindow
) -> tuple[InventoryRow, ...]:
    rows: list[InventoryRow] = []
    ghost_counts = {
        (number, energy): len(ghost_monomials(data, number, energy))
        for number in range(3, 7)
        for energy in range(-4, 5)
    }
    for number in range(3, 7):
        for (matter_energy, particles), states in sorted(window.by_energy_particle.items()):
            required_ghost_energy = DELTA - matter_energy
            count = ghost_counts[(number, required_ghost_energy)]
            if count:
                rows.append(
                    InventoryRow(
                        number,
                        matter_energy,
                        particles,
                        required_ghost_energy,
                        count,
                        len(states),
                    )
                )
    return tuple(rows)


def verify_cochain_inventory(
    data: global_brst.LieData,
    window: MatterWindow,
    rows: tuple[InventoryRow, ...],
) -> None:
    ghost_distributions = {
        number: {
            energy: len(ghost_monomials(data, number, energy))
            for energy in range(-4, 5)
            if ghost_monomials(data, number, energy)
        }
        for number in range(3, 7)
    }
    check(
        "C2g-N6: exact ghost-energy multiplicities agree with Lambda^q(4_- + 7_0 + 4_+)",
        ghost_distributions == {
            3: {-3: 4, -2: 42, -1: 108, 0: 147, 1: 108, 2: 42, 3: 4},
            4: {-4: 1, -3: 28, -2: 142, -1: 308, 0: 407, 1: 308, 2: 142, 3: 28, 4: 1},
            5: {-4: 7, -3: 88, -2: 322, -1: 668, 0: 833, 1: 668, 2: 322, 3: 88, 4: 7},
            6: {-4: 21, -3: 168, -2: 552, -1: 1092, 0: 1339, 1: 1092, 2: 552, 3: 168, 4: 21},
        },
    )
    totals: dict[int, Counter[int]] = {
        number: Counter() for number in range(3, 7)
    }
    for row in rows:
        totals[row.ghost_number][row.particle_number] += row.cochain_dimension
    check(
        "C2g-N6: exact C3--C6 dimensions are 13730,53056,141088,266596",
        {
            number: (dict(totals[number]), sum(totals[number].values()))
            for number in range(3, 7)
        }
        == {
            3: ({0: 42, 1: 9778, 2: 3910}, 13730),
            4: ({0: 142, 1: 32044, 2: 20650, 3: 220}, 53056),
            5: ({0: 322, 1: 74836, 2: 64390, 3: 1540}, 141088),
            6: ({0: 552, 1: 129424, 2: 132000, 3: 4620}, 266596),
        },
    )
    check(
        "C2g-N6: C3 stops at E5 while C4,C5,C6 use the complete E6 boundary",
        {
            number: tuple(sorted({row.matter_energy for row in rows if row.ghost_number == number}))
            for number in range(3, 7)
        }
        == {
            3: (0, 2, 3, 4, 5),
            4: (0, 2, 3, 4, 5, 6),
            5: (0, 2, 3, 4, 5, 6),
            6: (0, 2, 3, 4, 5, 6),
        },
    )


def verify_cutoff_saturation(data: global_brst.LieData) -> None:
    raising = set(range(11, 15))
    check(
        "C2g-N6: the general buffer rule gives E<=6 for (delta,g)=(2,4)",
        global_brst.required_upper_energy(DELTA, TARGET_GHOST_NUMBER) == MAX_ENERGY,
    )
    check(
        "C2g-N6: every E6 monomial in C4,C5,C6 contains all four raising ghosts",
        all(
            raising.issubset(monomial)
            for number in range(4, 7)
            for monomial in ghost_monomials(data, number, DELTA - MAX_ENERGY)
        ),
    )
    check(
        "C2g-N6: no E6 source occurs in C3",
        not ghost_monomials(data, 3, DELTA - MAX_ENERGY),
    )
    check(
        "C2g-N6: wedging any missing top-shell raising action is killed before matter action",
        all(
            global_brst.wedge((generator,), monomial) is None
            for number in range(4, 7)
            for monomial in ghost_monomials(data, number, -4)
            for generator in raising
        ),
    )


def verify_lie_grading(data: global_brst.LieData) -> bool:
    d_action_ok = (
        data.names[0] == "D"
        and all(
            exact_zero(
                data.structure[0][generator][target]
                - (data.degrees[generator] if target == generator else 0)
            )
            for generator in range(15)
            for target in range(15)
        )
    )
    grading_ok = all(
        coefficient == 0
        or data.degrees[first] + data.degrees[second] == data.degrees[target]
        for first in range(15)
        for second in range(15)
        for target, coefficient in enumerate(data.structure[first][second])
    )
    check(
        "C2g-N6: D is generator zero and acts on every conformal generator with its declared grade",
        d_action_ok,
    )
    check(
        "C2g-N6: every nonzero structure constant preserves compact grade",
        grading_ok,
    )
    return d_action_ok and grading_ok


def contract_monomial(
    monomial: global_brst.Monomial,
) -> dict[global_brst.Monomial, sp.Expr]:
    if 0 not in monomial:
        return {}
    position = monomial.index(0)
    return {
        monomial[:position] + monomial[position + 1 :]: sp.Integer(-1) ** position
    }


def apply_ghost_differential(
    polynomial: dict[global_brst.Monomial, sp.Expr],
    dc: tuple[dict[global_brst.Monomial, sp.Expr], ...],
) -> dict[global_brst.Monomial, sp.Expr]:
    output: dict[global_brst.Monomial, sp.Expr] = {}
    for monomial, value in polynomial.items():
        for target, coefficient in global_brst.ce_on_monomial(monomial, dc).items():
            add(output, target, value * coefficient)
    return clean(output)


def apply_contraction(
    polynomial: dict[global_brst.Monomial, sp.Expr],
) -> dict[global_brst.Monomial, sp.Expr]:
    output: dict[global_brst.Monomial, sp.Expr] = {}
    for monomial, value in polynomial.items():
        for target, coefficient in contract_monomial(monomial).items():
            add(output, target, value * coefficient)
    return clean(output)


def left_wedge(
    ghost: int,
    polynomial: dict[global_brst.Monomial, sp.Expr],
) -> dict[global_brst.Monomial, sp.Expr]:
    output: dict[global_brst.Monomial, sp.Expr] = {}
    for monomial, value in polynomial.items():
        product = global_brst.wedge((ghost,), monomial)
        if product is not None:
            sign, target = product
            add(output, target, sign * value)
    return clean(output)


def verify_ghost_cartan(
    data: global_brst.LieData,
    dc: tuple[dict[global_brst.Monomial, sp.Expr], ...],
) -> tuple[bool, bool]:
    cartan_ok = True
    wedge_ok = True
    for number in range(3, 7):
        for monomial in combinations(range(15), number):
            singleton = {monomial: sp.Integer(1)}
            lhs = apply_contraction(apply_ghost_differential(singleton, dc))
            for target, value in apply_ghost_differential(
                apply_contraction(singleton), dc
            ).items():
                add(lhs, target, value)
            lhs = clean(lhs)
            expected_energy = global_brst.ghost_energy(monomial, data.degrees)
            expected = {} if expected_energy == 0 else {monomial: sp.Integer(expected_energy)}
            cartan_ok = cartan_ok and lhs == expected

            for ghost in range(15):
                anticommutator = apply_contraction(left_wedge(ghost, singleton))
                for target, value in left_wedge(
                    ghost, apply_contraction(singleton)
                ).items():
                    add(anticommutator, target, value)
                anticommutator = clean(anticommutator)
                expected_wedge = singleton if ghost == 0 else {}
                wedge_ok = wedge_ok and anticommutator == expected_wedge
    check(
        "C2g-N6: ghost CE differential obeys {d_ghost,i_D}=ghost compact degree on C3--C6",
        cartan_ok,
    )
    check(
        "C2g-N6: exterior multiplication obeys {i_D,c^a wedge}=delta_D^a on C3--C6",
        wedge_ok,
    )
    return cartan_ok, wedge_ok


def one_particle_generators(
    one_particle: fock_data.OneParticleModule,
) -> tuple[sp.Matrix, ...]:
    return (
        one_particle.compact["D"],
        *(one_particle.compact[f"L{axis}"] for axis in ("x", "y", "z")),
        *(one_particle.compact[f"R{axis}"] for axis in ("x", "y", "z")),
        *(one_particle.lowering[component] for component in MAGNETIC_COMPONENTS),
        *(one_particle.raising[component] for component in MAGNETIC_COMPONENTS),
    )


def verify_matter_grading(
    data: global_brst.LieData, window: MatterWindow, matrices: tuple[sp.Matrix, ...]
) -> bool:
    energies = tuple(state.energy for state in window.one_particle.states)
    order_ok = (
        len(matrices) == len(data.names) == 15
        and data.names[:7] == ("D", "Lx", "Ly", "Lz", "Rx", "Ry", "Rz")
    )
    entry_grading_ok = all(
        energies[row] - energies[column] == data.degrees[generator]
        for generator, matrix in enumerate(matrices)
        for (row, column), value in sp.SparseMatrix(matrix).todok().items()
        if value != 0
    )
    fock_energy_ok = all(
        window.energy[occupation]
        == sum(energies[index] for index in occupation)
        for occupation in window.basis
    )
    check(
        "C2g-N6: the all-level two-chirality generator order matches the fitted Lie basis",
        order_ok,
    )
    check(
        "C2g-N6: every exact one-particle generator entry has its declared compact grade",
        entry_grading_ok,
    )
    check(
        "C2g-N6: second quantization preserves particle number and assigns D the summed energy",
        fock_energy_ok,
    )
    return order_ok and entry_grading_ok and fock_energy_ok


def occupation_action(
    occupation: Occupation,
    entries: dict[int, tuple[tuple[int, sp.Expr], ...]],
) -> dict[Occupation, sp.Expr]:
    counts = Counter(occupation)
    output: dict[Occupation, sp.Expr] = {}
    for source, source_count in counts.items():
        for target, value in entries.get(source, ()):
            if target == source:
                result = occupation
                coefficient = source_count * value
            else:
                target_count = counts.get(target, 0)
                coefficient = sp.sqrt(source_count * (target_count + 1)) * value
                changed = list(occupation)
                changed.remove(source)
                changed.append(target)
                result = tuple(sorted(changed))
            add(output, result, coefficient)
    return clean(output)


@dataclass(frozen=True)
class LazyDifferential:
    data: global_brst.LieData
    window: MatterWindow
    dc: tuple[dict[global_brst.Monomial, sp.Expr], ...]
    action_columns: tuple[dict[int, tuple[tuple[int, sp.Expr], ...]], ...]

    def column(self, key: CochainKey) -> SparseCochain:
        monomial, occupation = key
        source_degree = self.window.energy[occupation] + global_brst.ghost_energy(
            monomial, self.data.degrees
        )
        if source_degree != DELTA:
            raise AssertionError("source lies outside the declared total degree")
        output: SparseCochain = {}
        for target_monomial, coefficient in global_brst.ce_on_monomial(
            monomial, self.dc
        ).items():
            add(output, (target_monomial, occupation), coefficient)

        for generator in range(15):
            product = global_brst.wedge((generator,), monomial)
            if product is None:
                continue
            if (
                self.window.energy[occupation] == MAX_ENERGY
                and self.data.degrees[generator] == 1
            ):
                raise AssertionError("unsaturated raising action left the E6 cutoff")
            sign, target_monomial = product
            for target_occupation, coefficient in occupation_action(
                occupation, self.action_columns[generator]
            ).items():
                if target_occupation not in self.window.energy:
                    raise AssertionError("matter action left the E<=6 Fock basis")
                target_degree = (
                    self.window.energy[target_occupation]
                    + global_brst.ghost_energy(target_monomial, self.data.degrees)
                )
                if target_degree != DELTA or len(target_occupation) != len(occupation):
                    raise AssertionError("differential violated a declared grading")
                add(
                    output,
                    (target_monomial, target_occupation),
                    sign * coefficient,
                )
        return clean(output)

    def apply(self, vector: SparseCochain) -> SparseCochain:
        output: SparseCochain = {}
        for key, value in vector.items():
            for target, coefficient in self.column(key).items():
                add(output, target, value * coefficient)
        return clean(output)


def contract_cochain(vector: SparseCochain) -> SparseCochain:
    output: SparseCochain = {}
    for (monomial, occupation), value in vector.items():
        for target, coefficient in contract_monomial(monomial).items():
            add(output, (target, occupation), value * coefficient)
    return clean(output)


def representative_keys(
    data: global_brst.LieData,
    window: MatterWindow,
    rows: tuple[InventoryRow, ...],
    ghost_number: int,
) -> tuple[CochainKey, ...]:
    output = []
    for row in rows:
        if row.ghost_number != ghost_number:
            continue
        monomial = ghost_monomials(data, ghost_number, row.ghost_energy)[0]
        occupation = window.by_energy_particle[
            (row.matter_energy, row.particle_number)
        ][0]
        output.append((monomial, occupation))
    return tuple(output)


def verify_lazy_differential(
    data: global_brst.LieData,
    window: MatterWindow,
    rows: tuple[InventoryRow, ...],
    dc: tuple[dict[global_brst.Monomial, sp.Expr], ...],
    matrices: tuple[sp.Matrix, ...],
) -> None:
    action_columns = tuple(fock_data.column_entries(matrix) for matrix in matrices)
    differential = LazyDifferential(data, window, dc, action_columns)

    cartan_ok = True
    for key in representative_keys(data, window, rows, 4):
        singleton = {key: sp.Integer(1)}
        lhs = differential.apply(contract_cochain(singleton))
        for target, value in contract_cochain(differential.apply(singleton)).items():
            add(lhs, target, value)
        cartan_ok = cartan_ok and clean(lhs) == {key: sp.Integer(DELTA)}
    check(
        "C2g-N6: lazy exact d obeys (d i_D+i_D d)=2I on every C4 energy/particle sector representative",
        cartan_ok,
    )

    nilpotent_ok = True
    for number in (3, 4):
        for key in representative_keys(data, window, rows, number):
            nilpotent_ok = nilpotent_ok and not differential.apply(
                differential.apply({key: sp.Integer(1)})
            )
    check(
        "C2g-N6: lazy exact columns obey d4*d3=d5*d4=0 on every energy/particle sector representative",
        nilpotent_ok,
    )


def verify_contraction_theorem(
    data: global_brst.LieData,
    window: MatterWindow,
    rows: tuple[InventoryRow, ...],
    *,
    lie_grading_ok: bool,
    ghost_cartan_ok: bool,
    wedge_cartan_ok: bool,
    matter_grading_ok: bool,
) -> None:
    middle = Counter()
    for row in rows:
        if row.ghost_number == TARGET_GHOST_NUMBER:
            middle[row.particle_number] += row.cochain_dimension
    total_degree_ok = all(
        row.matter_energy + row.ghost_energy == DELTA
        for row in rows
        if row.ghost_number == TARGET_GHOST_NUMBER
    )
    contraction_preserves_sector = all(
        global_brst.ghost_energy(target, data.degrees) == row.ghost_energy
        and len(target) == TARGET_GHOST_NUMBER - 1
        for row in rows
        if row.ghost_number == TARGET_GHOST_NUMBER
        for monomial in ghost_monomials(data, TARGET_GHOST_NUMBER, row.ghost_energy)
        for target in contract_monomial(monomial)
    )
    represented_matter_sectors = all(
        (row.matter_energy, row.particle_number) in window.by_energy_particle
        for row in rows
        if row.ghost_number == TARGET_GHOST_NUMBER
    )
    structural_premises = (
        lie_grading_ok
        and ghost_cartan_ok
        and wedge_cartan_ok
        and matter_grading_ok
        and total_degree_ok
        and contraction_preserves_sector
        and represented_matter_sectors
        and DELTA == 2
    )
    check(
        "C2g-N6: every C4 row has E_matter+E_ghost=2 and i_D preserves E,N and the cutoff",
        total_degree_ok
        and contraction_preserves_sector
        and represented_matter_sectors
        and dict(middle) == {0: 142, 1: 32044, 2: 20650, 3: 220},
    )
    check(
        "C2g-N6: exact full Cartan identity gives h=i_D/2 and H4(delta=2,N)=0 for N=0,1,2,3",
        structural_premises,
    )


def print_inventory(rows: tuple[InventoryRow, ...]) -> None:
    print("q  E  N  ghost-E  ghost-dim  matter-dim  cochain-dim")
    for row in rows:
        print(
            f"{row.ghost_number}  {row.matter_energy}  {row.particle_number}"
            f"  {row.ghost_energy:+d}       {row.ghost_dimension:4d}"
            f"       {row.matter_dimension:4d}       {row.cochain_dimension:7d}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-local-brst",
        action="store_true",
        help="fail closed: the local Diff x Weyl BV complex is not included",
    )
    parser.add_argument(
        "--require-materialized-ranks",
        action="store_true",
        help="fail closed: giant sparse ranks are superseded by an exact contracting homotopy",
    )
    parser.add_argument(
        "--require-physical-cohomology",
        action="store_true",
        help="fail closed: this certificate is global-only free-module CE cohomology",
    )
    args = parser.parse_args()

    if args.require_local_brst:
        raise SystemExit("local Diff x Weyl BV ghosts and contractible sectors are absent")
    if args.require_materialized_ranks:
        raise SystemExit(
            "the 13730 -> 53056 -> 141088 -> 266596 sparse matrices are "
            "exposed lazily; exact H4 follows instead from h=i_D/2"
        )
    if args.require_physical_cohomology:
        raise SystemExit("global-only CE cohomology is not the full physical BRST cohomology")

    data = global_brst.build_lie_data(+1)
    dc = global_brst.ghost_differentials(data)
    window = build_matter_window()
    rows = build_inventory(data, window)
    verify_matter_inventory(window)
    verify_cochain_inventory(data, window, rows)
    verify_cutoff_saturation(data)
    lie_grading_ok = verify_lie_grading(data)
    ghost_cartan_ok, wedge_cartan_ok = verify_ghost_cartan(data, dc)
    matrices = one_particle_generators(window.one_particle)
    matter_grading_ok = verify_matter_grading(data, window, matrices)
    verify_lazy_differential(data, window, rows, dc, matrices)
    verify_contraction_theorem(
        data,
        window,
        rows,
        lie_grading_ok=lie_grading_ok,
        ghost_cartan_ok=ghost_cartan_ok,
        wedge_cartan_ok=wedge_cartan_ok,
        matter_grading_ok=matter_grading_ok,
    )
    print_inventory(rows)
    print(
        "C2g-N6 STATUS: EXACT CUTOFF-COMPLETE GLOBAL-ONLY RESULT. "
        "The full E<=6 matter/ghost window is inventoried, its top boundary "
        "is exterior-saturated, and h=i_D/2 contracts the delta=2 complex. "
        "Therefore H4 is zero separately at particle numbers 0,1,2,3."
    )


if __name__ == "__main__":
    main()
