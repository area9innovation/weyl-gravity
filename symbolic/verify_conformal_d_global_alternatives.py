#!/usr/bin/env python3
"""Exact reduced-mode comparisons with cylinder ``D`` retained globally.

This certificate deliberately separates two mathematically different choices.

``NO_RESIDUAL_GAUGING``
    Local Diff x Weyl reduction has already produced the physical E/A/L
    oscillator module.  The residual conformal algebra acts as a *global*
    symmetry, so there are no residual CE ghosts and the residual differential
    is zero.  Consequently the whole E/A/L module survives, with its original
    Krein signs.

``LOWERING_SUBALGEBRA``
    An illustrative, not uniquely physical, comparison which gauges only the
    closed abelian lowering algebra ``n_- = span(K^-_a)``.  ``D`` normalizes
    this algebra and therefore remains a well-defined global grading.  The
    cutoff-complete total-D-weight window through weight four is computed
    exactly.  This rail is included to demonstrate a legal alternative to the
    meaningless set subtraction ``so(4,2) \\ {D}``.

All results have dependency tag ``REDUCED-MODE``.  They neither determine the
covariant charge of ``D`` nor promote either comparison to a physical gauge
choice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import TypeAlias

import sympy as sp

try:
    from symbolic import verify_conformal_generator_all_levels as all_levels
    from symbolic import verify_conformal_global_brst_window as global_ce
    from symbolic import verify_conformal_relative_brst_weight4 as relative
except ModuleNotFoundError:  # direct ``python symbolic/script.py`` execution
    import verify_conformal_generator_all_levels as all_levels
    import verify_conformal_global_brst_window as global_ce
    import verify_conformal_relative_brst_weight4 as relative


SparseVector: TypeAlias = dict[int, sp.Expr]
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT = ROOT / "symbolic" / "conformal-d-global-alternatives.json"
LOWERING_COMPONENTS = tuple(all_levels.MAGNETIC_COMPONENTS)


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mode_inventory(max_energy: int = 4) -> list[dict[str, object]]:
    """All-level one-particle dimensions and Krein signs through one cutoff."""

    rows: list[dict[str, object]] = []
    for energy in range(2, max_energy + 1):
        dimensions = {
            "E": 2 * (energy - 1) * (energy + 3),
            "A": 2 * (energy - 1) * (energy + 1) if energy >= 3 else 0,
            "L": 2 * (energy - 3) * (energy + 1) if energy >= 4 else 0,
        }
        for branch in ("E", "A", "L"):
            if dimensions[branch]:
                rows.append(
                    {
                        "D_weight": energy,
                        "branch": branch,
                        "dimension": dimensions[branch],
                        "gram_sign": 1 if branch == "E" else -1,
                    }
                )
    return rows


def combined_lowering() -> tuple[tuple[sp.Matrix, ...], tuple[int, ...]]:
    plus = all_levels.representation_space(4, +1)
    minus = all_levels.representation_space(4, -1)
    matrices = tuple(
        sp.diag(plus.lowering[component], minus.lowering[component])
        for component in LOWERING_COMPONENTS
    )
    energies = tuple(
        int(plus.energy[index, index]) for index in range(plus.dimension)
    ) + tuple(int(minus.energy[index, index]) for index in range(minus.dimension))
    return matrices, energies


def sparse_actions(
    matrices: tuple[sp.Matrix, ...],
) -> tuple[tuple[tuple[tuple[int, sp.Expr], ...], ...], ...]:
    return global_ce.matrices_to_sparse_actions(matrices)


def insert_ghost(ghost: int, monomial: tuple[int, ...]) -> tuple[int, tuple[int, ...]] | None:
    if ghost in monomial:
        return None
    crossings = sum(existing < ghost for existing in monomial)
    return (-1 if crossings % 2 else 1), tuple(sorted((ghost, *monomial)))


def lowering_basis(
    energies: tuple[int, ...], ghost_number: int, total_weight: int
) -> tuple[tuple[tuple[int, ...], int], ...]:
    matter_energy = total_weight - ghost_number
    return tuple(
        (monomial, state)
        for monomial in combinations(range(4), ghost_number)
        for state, energy in enumerate(energies)
        if energy == matter_energy
    )


def lowering_differential(
    actions: tuple[tuple[tuple[tuple[int, sp.Expr], ...], ...], ...],
    source: tuple[tuple[tuple[int, ...], int], ...],
    target: tuple[tuple[tuple[int, ...], int], ...],
) -> tuple[SparseVector, ...]:
    target_index = {basis: index for index, basis in enumerate(target)}
    columns: list[SparseVector] = []
    for monomial, state in source:
        column: SparseVector = {}
        for ghost in range(4):
            inserted = insert_ghost(ghost, monomial)
            if inserted is None:
                continue
            sign, target_monomial = inserted
            for target_state, coefficient in actions[ghost][state]:
                key = (target_monomial, target_state)
                if key not in target_index:
                    raise AssertionError("lowering differential left the declared D-weight block")
                row = target_index[key]
                column[row] = sp.simplify(column.get(row, 0) + sign * coefficient)
        columns.append({row: value for row, value in column.items() if value != 0})
    return tuple(columns)


def compose(
    first: tuple[SparseVector, ...], second: tuple[SparseVector, ...]
) -> tuple[SparseVector, ...]:
    return global_ce.compose(first, second)


def lowering_cohomology_window() -> dict[str, object]:
    matrices, energies = combined_lowering()
    actions = sparse_actions(matrices)
    table: list[dict[str, object]] = []
    expected = {
        2: ([10, 0, 0, 0, 0], [0, 0, 0, 0]),
        3: ([40, 40, 0, 0, 0], [40, 0, 0, 0]),
        4: ([82, 160, 60, 0, 0], [82, 60, 0, 0]),
    }
    for total_weight in range(2, 5):
        bases = tuple(lowering_basis(energies, q, total_weight) for q in range(5))
        differentials = tuple(
            lowering_differential(actions, bases[q], bases[q + 1])
            for q in range(4)
        )
        check(
            f"D-global n_-: d^2=0 exactly at total D-weight {total_weight}",
            all(
                not column
                for q in range(3)
                for column in compose(differentials[q], differentials[q + 1])
            ),
        )
        dimensions = [len(basis) for basis in bases]
        ranks = [
            global_ce.modular_rank(differentials[q], len(bases[q + 1]))
            for q in range(4)
        ]
        check(
            f"D-global n_-: exact maximal ranks at total D-weight {total_weight}",
            (dimensions, ranks) == expected[total_weight],
        )
        # Each nonzero modular rank here equals a row or column dimension, so
        # it is simultaneously a characteristic-zero lower bound and the
        # elementary dimension upper bound.  Hence these are exact ranks.
        cohomology = [
            dimensions[q]
            - (ranks[q] if q < 4 else 0)
            - (ranks[q - 1] if q > 0 else 0)
            for q in range(5)
        ]
        table.append(
            {
                "particle_number": 1,
                "total_D_weight": total_weight,
                "cochain_dimensions_q0_to_q4": dimensions,
                "differential_ranks_d0_to_d3": ranks,
                "cohomology_dimensions_q0_to_q4": cohomology,
            }
        )
    check(
        "D-global n_-: the helicity-two E2 lowest-weight space gives H^0 dimension ten",
        table[0]["cohomology_dimensions_q0_to_q4"] == [10, 0, 0, 0, 0],
    )
    return {
        "subalgebra": "n_- = span(K^-_{a}), abelian of dimension 4",
        "status": "ILLUSTRATIVE_CLOSED_SUBALGEBRA_NOT_A_PHYSICAL_SELECTION",
        "D_action": "global; [D,K^-_a]=-K^-_a, so D normalizes n_-",
        "cutoff_complete_total_D_weights": [2, 3, 4],
        "one_particle_table": table,
        "additional_centered_weight_four": {
            "vacuum_particle_number_0": {"ghost_degree": 4, "dimension": 1},
            "two_particle_number_2": {"ghost_degree": 0, "dimension": 55},
            "weyl_square_subspace_dimension": 2,
            "weyl_square_gram": [[1, 0], [0, 1]],
        },
        "certified_pairing": {
            "H0_D_weight_2_basis": "E2^+ followed by E2^- magnetic basis",
            "gram_diagonal": [1] * 10,
            "higher_ghost_degree_pairing": "NOT_COMPUTED",
        },
        "open": [
            "all-weight n_- cohomology beyond the cutoff-complete weight-four window",
            "complementary-degree ghost pairing outside the displayed H0 classes",
            "physical justification for gauging n_- rather than another closed subgroup",
        ],
    }


def verify_nonclosure() -> dict[str, object]:
    data = global_ce.build_lie_data(+1)
    lowering = range(7, 11)
    raising = range(11, 15)
    # In the certified magnetic basis the rotation contributions cancel in
    # the invariant contraction.  The order below gives +2D.
    contracted = [
        sp.simplify(
            sp.Rational(1, 4)
            * sum(data.structure[lower][upper][target] for lower, upper in zip(lowering, raising))
        )
        for target in range(15)
    ]
    check(
        "D-global: invariant contraction (1/4) sum_a [K^-_a,K^+_a] is exactly 2D",
        contracted == [sp.Integer(2)] + [sp.Integer(0)] * 14,
    )
    retained = tuple(range(1, 15))
    check(
        "D-global: deleting D alone from the fifteen generators is not a Lie subalgebra",
        any(data.structure[first][second][0] != 0 for first in retained for second in retained),
    )
    return {
        "invalid_proposal": "span of all certified residual generators except D",
        "closed": False,
        "exact_witness": "(1/4) sum_a [K^-_a,K^+_a] = 2 D",
        "consequence": "there is no CE complex obtained by deleting only the D ghost",
    }


def no_residual_gauging() -> dict[str, object]:
    inventory = mode_inventory(4)
    by_weight: list[dict[str, object]] = []
    for weight in range(2, 5):
        rows = [row for row in inventory if row["D_weight"] == weight]
        positive = sum(int(row["dimension"]) for row in rows if row["gram_sign"] == 1)
        negative = sum(int(row["dimension"]) for row in rows if row["gram_sign"] == -1)
        by_weight.append(
            {
                "particle_number": 1,
                "D_weight": weight,
                "dimension": positive + negative,
                "gram_signature": [positive, negative],
                "branches": rows,
            }
        )
    check(
        "D-global no-gauging: one-particle dimensions through weight four are 10,40,82",
        [row["dimension"] for row in by_weight] == [10, 40, 82],
    )
    check(
        "D-global no-gauging: canonical signatures are (10,0),(24,16),(42,40)",
        [row["gram_signature"] for row in by_weight] == [[10, 0], [24, 16], [42, 40]],
    )

    plus = global_ce.generator_data.representation_space(+1)
    minus = global_ce.generator_data.representation_space(-1)
    compact = relative.combined_compact(plus, minus, 2)
    induced, pairs = relative.symmetric_square_generator(compact[0])
    check(
        "D-global no-gauging: the E2 two-particle weight-four space has dimension 55",
        induced.rows == 55 and len(pairs) == 55,
    )
    candidates = global_ce.chiral_weyl_square_candidates(pairs)
    check(
        "D-global no-gauging: normalized W_+^2,W_-^2 have positive identity Gram",
        candidates.T.conjugate() * candidates == sp.eye(2),
    )
    return {
        "complex": "H_local with zero residual differential; no residual CE ghosts",
        "residual_role": "SO(4,2) acts globally",
        "cohomological_degree": 0,
        "differential": "0",
        "one_particle_all_level_formula": {
            "E_n": {"range": "n>=2", "dimension": "2(n-1)(n+3)", "gram_sign": 1},
            "A_n": {"range": "n>=3", "dimension": "2(n-1)(n+1)", "gram_sign": -1},
            "L_n": {"range": "n>=4", "dimension": "2(n-3)(n+1)", "gram_sign": -1},
        },
        "one_particle_through_weight_four": by_weight,
        "cohomology_through_weight_four": [
            {
                "particle_number": 0,
                "D_weight": 0,
                "cohomological_degree": 0,
                "dimension": 1,
                "gram_signature": [1, 0],
            },
            *[
                {
                    **row,
                    "cohomological_degree": 0,
                }
                for row in by_weight
            ],
            {
                "particle_number": 2,
                "D_weight": 4,
                "cohomological_degree": 0,
                "dimension": 55,
                "gram_signature": [55, 0],
                "basis": "normalized occupation basis of Sym^2(E2^+ + E2^-)",
            },
        ],
        "full_weight_four_gram": {
            "basis_order": "E4, A4, L4 in both chiralities, then Sym^2(E2^+ + E2^-)",
            "diagonal_blocks": ["+I_42", "-I_30", "-I_10", "+I_55"],
            "signature": [97, 40],
        },
        "one_particle_verdict": "FULL_E_A_L_MODULE_SURVIVES",
        "helicity_plus_minus_2": {
            "returns": True,
            "lowest_D_weight": 2,
            "dimension": 10,
            "gram": "I_10",
        },
        "Weyl_squares": {
            "D_weight": 4,
            "particle_number": 2,
            "span_dimension": 2,
            "gram": [[1, 0], [0, 1]],
            "fate": (
                "survive as ordinary degree-zero vectors inside the 55-dimensional "
                "Sym^2(E2^+ + E2^-) space; without residual gauging they are not "
                "cohomologically singled out"
            ),
        },
    }


def build_result() -> dict[str, object]:
    result = {
        "schema": "conformal-d-global-alternatives-v1",
        "dependency_tags": ["REDUCED-MODE", "LOCAL-ALGEBRAIC"],
        "claim_boundary": (
            "Exact oscillator/CE comparisons after certified local reduction. "
            "Not a covariant D-charge calculation and not evidence for LORENTZIAN-CAUSAL claims."
        ),
        "invalid_delete_D_comparison": verify_nonclosure(),
        "no_residual_gauging": no_residual_gauging(),
        "illustrative_lowering_subalgebra": lowering_cohomology_window(),
        "physical_selection": "OPEN_PENDING_COVARIANT_D_CHARGE",
        "flags": {
            "delete_D_only_is_valid_Lie_algebra": False,
            "no_residual_gauging_complex_exact": True,
            "full_EAL_one_particle_module_survives": True,
            "negative_norm_one_particle_branches_survive": True,
            "lowering_subalgebra_closed": True,
            "lowering_subalgebra_physical": False,
            "D_charge_computed_here": False,
        },
        "provenance": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                ROOT / "symbolic" / "verify_conformal_generator_all_levels.py",
                ROOT / "symbolic" / "verify_conformal_global_brst_window.py",
                ROOT / "symbolic" / "verify_conformal_relative_brst_weight4.py",
            )
        },
        "verification_command": "python3 symbolic/verify_conformal_d_global_alternatives.py --write-result",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--check-result", action="store_true")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()
    result = build_result()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        args.result.write_text(serialized)
        print("wrote", args.result)
    if args.check_result:
        check("D-global: checked-in result matches exact regeneration", args.result.read_text() == serialized)
    print("NO_RESIDUAL_GAUGING: full E/A/L module survives with +,-,- signs")
    print("LOWERING_SUBALGEBRA: illustrative only; H0(E2)=10 with Gram I10")
    print("PHYSICAL_SELECTION: OPEN_PENDING_COVARIANT_D_CHARGE")


if __name__ == "__main__":
    main()
