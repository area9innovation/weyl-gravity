"""Exact four-dimensional Diff/mixed reduction for the AFN0 anomaly complex.

The ambient tensor-graph inventory is intentionally not expanded.  The Stora
total-form comparison reduces its tensorial part to diffeomorphism-invariant
top representatives, while a possible non-covariant gravitational anomaly is
controlled by a degree-three invariant polynomial of the metric structure
algebra.  This module checks the comparison hypotheses against the checked-in
jet/descent receipts and computes the latter invariant space exactly over Q.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, combinations_with_replacement
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

DEPENDENCIES = {
    "ambient_graphs": HERE / "certificates/AFN0_AMBIENT_TENSOR_GRAPH_REALIZATION_CERTIFICATE.json",
    "basis_gap": HERE / "certificates/BASIS_GAP_REPORT_AFN0.json",
    "horizontal_bicomplex": HERE / "certificates/HORIZONTAL_BICOMPLEX_CERTIFICATE.json",
    "descent_database": HERE / "descent/DESCENT_DATABASE_DIMENSION_FOUR.json",
    "euler": HERE / "certificates/EULER_TRANSGRESSION_CERTIFICATE.json",
    "H04": HERE / "certificates/AFN0_H04_CANONICAL_QUOTIENT.json",
    "H14_even": HERE / "certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
    "H14_odd": HERE / "certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json",
    "minimal_KT": HERE / "certificates/MINIMAL_BV_KOSZUL_TATE_COLLAPSE.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _matrix_multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _matrix_subtract(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[a - b for a, b in zip(x, y)] for x, y in zip(left, right)]


def _so4_structure() -> dict[str, Any]:
    """Return the vector-representation structure constants of so(4)."""

    pairs = tuple(combinations(range(4), 2))
    generators: list[list[list[int]]] = []
    for a, b in pairs:
        matrix = [[0 for _ in range(4)] for _ in range(4)]
        matrix[a][b] = 1
        matrix[b][a] = -1
        generators.append(matrix)

    structure: dict[tuple[int, int, int], int] = {}
    commutator_rows = []
    for left_index, left in enumerate(generators):
        for right_index, right in enumerate(generators):
            commutator = _matrix_subtract(
                _matrix_multiply(left, right), _matrix_multiply(right, left)
            )
            coefficients = [commutator[a][b] for a, b in pairs]
            reconstructed = [
                [
                    sum(
                        coefficients[index] * generators[index][i][j]
                        for index in range(len(generators))
                    )
                    for j in range(4)
                ]
                for i in range(4)
            ]
            if reconstructed != commutator:
                raise AssertionError("so(4) commutator reconstruction failed")
            nonzero = []
            for output, coefficient in enumerate(coefficients):
                if coefficient:
                    structure[left_index, right_index, output] = coefficient
                    nonzero.append({"output": output, "coefficient": coefficient})
            commutator_rows.append(
                {"left": left_index, "right": right_index, "terms": nonzero}
            )
    payload = {
        "basis": [f"M_{a}{b}" for a, b in pairs],
        "vector_generators": generators,
        "commutators": commutator_rows,
    }
    return {**payload, "structure": structure, "sha256": _canonical_hash(payload)}


def _rank(matrix: Iterable[Iterable[int]]) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    column_count = len(rows[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            coefficient = rows[row][column]
            rows[row] = [
                value - coefficient * pivot_entry
                for value, pivot_entry in zip(rows[row], rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def _rank_mod_prime(matrix: Iterable[Iterable[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(value * inverse) % prime for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            coefficient = rows[row][column]
            rows[row] = [
                (value - coefficient * pivot_entry) % prime
                for value, pivot_entry in zip(rows[row], rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def _symmetric_invariant_space(
    degree: int, structure: dict[tuple[int, int, int], int]
) -> dict[str, Any]:
    """Solve the adjoint-invariance equations for Sym^degree(so(4)^*)."""

    coordinates = tuple(combinations_with_replacement(range(6), degree))
    coordinate_index = {coordinate: index for index, coordinate in enumerate(coordinates)}
    equations: list[list[int]] = []
    for acting_generator in range(6):
        for coordinate in coordinates:
            row = [0 for _ in coordinates]
            for position, input_generator in enumerate(coordinate):
                for output_generator in range(6):
                    coefficient = structure.get(
                        (acting_generator, input_generator, output_generator), 0
                    )
                    if not coefficient:
                        continue
                    target = tuple(
                        sorted(
                            coordinate[:position]
                            + (output_generator,)
                            + coordinate[position + 1 :]
                        )
                    )
                    row[coordinate_index[target]] += coefficient
            if any(row):
                equations.append(row)
    rank = _rank(equations)
    modular_ranks = {str(prime): _rank_mod_prime(equations, prime) for prime in (101, 103, 107)}
    if set(modular_ranks.values()) != {rank}:
        raise AssertionError("rational and modular invariant-space ranks disagree")
    payload = {
        "degree": degree,
        "symmetric_coordinate_count": len(coordinates),
        "nonzero_invariance_equation_count": len(equations),
        "matrix_rank": rank,
        "independent_modular_ranks": modular_ranks,
        "invariant_dimension": len(coordinates) - rank,
        "coordinate_manifest_sha256": _canonical_hash(coordinates),
        "matrix_sha256": _canonical_hash(equations),
    }
    return {**payload, "proof_sha256": _canonical_hash(payload)}


def _fraction_tuple(rows: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(Fraction(row["numerator"], row["denominator"]) for row in rows)


def analysis() -> dict[str, Any]:
    values = _load()
    ambient = values["ambient_graphs"]
    gap = values["basis_gap"]
    bicomplex = values["horizontal_bicomplex"]
    database = values["descent_database"]
    euler = values["euler"]
    even = values["H14_even"]
    odd = values["H14_odd"]
    kt = values["minimal_KT"]

    if (
        ambient["totals"]["refined_signature_count"] != 720
        or ambient["totals"]["total_raw_graph_count"] != 2_860_932_903
        or ambient["checks"]["all_ambient_signatures_accounted_for"] != "VERIFIED"
    ):
        raise ValueError("ambient total-complex inventory drifted")
    if gap["result_state"] != "TOP_FORM_BASIS_GAPS_RESOLVED_TOTAL_COMPLEX_OPEN":
        raise ValueError("historical basis-gap boundary drifted")
    diff_refined_counts = [
        row["refined_signature_count"] for row in gap["diff_top_form_ledgers"]
    ]
    if diff_refined_counts != [7, 7]:
        raise ValueError("pure-Diff top-form signature inventory drifted")
    required_bicomplex = {
        "Q_squared_zero_on_density_generators": "VERIFIED",
        "d_h_squared_zero": "VERIFIED",
        "coordinate_Q_dh_commutator_zero": "VERIFIED",
        "counterterm_diff_descent_tower_equations": "VERIFIED",
        "anomaly_diff_descent_tower_equations": "VERIFIED",
        "bottom_brst_closure": "VERIFIED",
        "euler_intrinsic_weyl_descent": "NONTRIVIAL_COMPLETE",
    }
    if any(bicomplex["checks"].get(key) != value for key, value in required_bicomplex.items()):
        raise ValueError("universal Diff comparison input drifted")
    if (
        euler["result_state"] != "INTRINSIC_EULER_TOWER_VERIFIED"
        or euler["checks"]["euler_full_diff_completed_tower"] != "VERIFIED"
        or euler["checks"]["omega_E4_intrinsic_descent_continuation"]
        != "NONTRIVIAL_COMPLETE"
    ):
        raise ValueError("Euler total-form input drifted")

    expected_coefficients = (
        Fraction(1), Fraction(-1), Fraction(1, 2), Fraction(-1, 6), Fraction(1, 24)
    )
    entries = {row["representative_id"]: row for row in database["entries"]}
    required_entries = {
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_C_DUAL_C",
        "ANOM_OMEGA_BOX_R",
    }
    if not required_entries <= entries.keys():
        raise ValueError("Diff-completed anomaly entries are incomplete")
    for representative_id in required_entries:
        coefficients = _fraction_tuple(
            [row["coefficient"] for row in entries[representative_id]["diff_tower"]]
        )
        if coefficients != expected_coefficients:
            raise ValueError(f"universal Diff tower drifted: {representative_id}")

    structure = _so4_structure()
    invariant_spaces = [
        _symmetric_invariant_space(degree, structure["structure"])
        for degree in (1, 2, 3, 4)
    ]
    invariant_dimensions = [row["invariant_dimension"] for row in invariant_spaces]
    if invariant_dimensions != [0, 2, 0, 3]:
        raise AssertionError("so(4) invariant-polynomial controls drifted")

    even_classes = [row["representative_id"] for row in even["classes"]]
    odd_classes = [row["representative_id"] for row in odd["classes"]]
    if even_classes != ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4"]:
        raise ValueError("even Weyl quotient drifted")
    if odd_classes != ["ANOM_OMEGA_C_DUAL_C"]:
        raise ValueError("odd Weyl quotient drifted")
    exact_rows = [row["representative_id"] for row in even["exact_classes"]]
    if exact_rows != ["ANOM_OMEGA_BOX_R"]:
        raise ValueError("Weyl exact-row ledger drifted")
    if (
        kt["claim_flags"]["MINIMAL_KOSZUL_TATE_POSITIVE_AFN_ACYCLIC"] is not True
        or kt["open_sectors"]["full_minimal_BV_H14"] != "NOT_COMPUTED"
    ):
        raise ValueError("minimal Koszul--Tate input drifted")

    degree_counts = {
        str(degree): sum(
            row["refined_signature_count"]
            for row in ambient["counts_by_sector"]
            if row["total_degree"] == degree
        )
        for degree in (3, 4, 5, 6)
    }
    theorem_application = {
        "locality_domain": "CONTRACTIBLE_COORDINATE_PATCH_POLYNOMIAL_FINITE_JETS",
        "total_form_comparison": "H_G(s+d)_ISOMORPHIC_TO_H_gn(s_MOD_d)",
        "covariant_tensor_sector": "REPRESENTED_BY_DIFF_INVARIANT_TOP_FORMS_WITH_UNIVERSAL_DIFF_COMPLETION",
        "weyl_ghost_reduction": "DERIVATIVES_OF_OMEGA_REMOVED_BY_INTEGRATION_BY_PARTS",
        "mixed_sector": "FIXED_DESCENDANTS_OF_WEYL_TOP_REPRESENTATIVES_NOT_INDEPENDENT_CLASSES",
        "noncovariant_sector": "CHERN_WEIL_DEGREE_THREE_INVARIANTS",
        "metric_structure_algebra": "so(3,1)_C_ISOMORPHIC_TO_so(4,C)",
        "degree_three_invariant_dimension": invariant_spaces[2]["invariant_dimension"],
        "conclusion": "NO_PURE_DIFF_CLASS_AND_NO_ADDITIONAL_MIXED_CLASS_IN_D4",
    }
    proof_payload = {
        "dependency_hashes": {name: _sha256(path) for name, path in DEPENDENCIES.items()},
        "theorem_application": theorem_application,
        "so4_structure_sha256": structure["sha256"],
        "invariant_spaces": invariant_spaces,
        "universal_coefficients": [
            {"numerator": value.numerator, "denominator": value.denominator}
            for value in expected_coefficients
        ],
        "classes": {"even": even_classes, "odd": odd_classes, "exact": exact_rows},
    }
    return {
        "classical_commit": kt["classical_commit"],
        "dependency_hashes": proof_payload["dependency_hashes"],
        "ambient_accounting": {
            "refined_signature_count": 720,
            "raw_graph_count_not_materialized": 2_860_932_903,
            "refined_signatures_by_total_degree": degree_counts,
            "pure_Diff_top_form_refined_signatures": {"even": 7, "odd": 7},
            "reduction_mode": "THEOREM_ASSISTED_TOTAL_FORM_COMPARISON_PLUS_EXACT_SMALL_ALGEBRA",
        },
        "theorem_application": theorem_application,
        "primary_sources": [
            {
                "arxiv": "0704.2472",
                "title": "General solutions of the Wess-Zumino consistency condition for the Weyl anomalies",
                "application": "Stora total differential, generalized connections, undifferentiated Weyl-ghost reduction, and complete type-A/type-B Weyl classification",
            },
            {
                "arxiv": "hep-th/9505173",
                "title": "Local BRST cohomology in Einstein--Yang--Mills theory",
                "application": "antifield removal and gravitational candidate-anomaly classification in dimensions greater than two",
            },
        ],
        "small_algebra": {
            "structure_algebra": "so(4)_Q_VECTOR_REALIZATION",
            "basis": structure["basis"],
            "structure_sha256": structure["sha256"],
            "symmetric_invariant_spaces": invariant_spaces,
            "controls": {
                "degree_one_zero": "VERIFIED",
                "degree_two_dimension_two": "VERIFIED",
                "degree_three_zero": "VERIFIED",
                "degree_four_dimension_three": "VERIFIED",
            },
        },
        "AFN0_H14": {
            "pure_Diff": {"even_dimension": 0, "odd_dimension": 0},
            "mixed_independent": {"even_dimension": 0, "odd_dimension": 0},
            "Weyl_even_classes": even_classes,
            "Weyl_odd_classes": odd_classes,
            "exact_rows": exact_rows,
            "even_dimension": len(even_classes),
            "odd_dimension": len(odd_classes),
        },
        "minimal_BV_H14": {
            "positive_antifield_columns": "ZERO_BY_EXPLICIT_KOSZUL_TATE_CONTRACTION",
            "even_classes": even_classes,
            "odd_classes": odd_classes,
            "exact_rows": exact_rows,
            "even_dimension": len(even_classes),
            "odd_dimension": len(odd_classes),
            "regularity_scope": "REGULAR_BACH_LOCUS",
        },
        "proof_sha256": _canonical_hash(proof_payload),
    }
