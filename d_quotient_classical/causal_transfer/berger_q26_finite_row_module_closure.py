#!/usr/bin/env python3
"""Exact finite-field module-closure audit for the Berger q26 defects.

The scalar-symbol substitution is not multiplicative for the Berger PBW
algebra.  This module instead evaluates the exact operators in rational
finite-dimensional spin representations of the specialized Berger Lie
algebra.  It closes the square and evolution-commutator images under q, A and
their free algebraic dual actions.  A full closure in a representation of
dimension r proves that any free row carrier through which that closure
factors has at least 104 generators.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix
from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer import (
    berger_q26_cauchy_bv_carrier_obstruction as predecessor,
)


GRAPH = predecessor.GRAPH
ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_finite_row_module_closure_v1/spin4_closure_witness.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-q26-finite-row-module-closure-lower-bound-v1.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-finite-row-module-closure-lower-bound-v1.schema.json"
VERIFIER = HERE / "verify_berger_q26_finite_row_module_closure.py"
TESTS = HERE / "tests/test_berger_q26_finite_row_module_closure.py"
PRIME = 1009
SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
SEED = 26072030
PINNED_ORIGINAL_COMMIT = "988f8ee6c59b539ae516eb8a8f882a57a95f71e0"
PINNED_ORIGINAL_PATH = (
    "physics/symplectic-reconstruction/d_quotient_classical/certificates/"
    "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
)
PINNED_ORIGINAL_SHA256 = (
    "24d2db35fb3dc696081d1e93208fdbd0b8f31922cdac7a063033650a9e686a01"
)
SIX_ROW = ROOT / "d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json"
SIX_ROW_SHA256 = (
    "9c7e4c6db7eb39274852ba3fe5b45e9e0e25c6442fe20bbc4091ec6afec0cda7"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _load_operators() -> tuple[GRAPH.Matrix, GRAPH.Matrix]:
    evolution = GRAPH._canonical_symbols(
        GRAPH._load_hashed_operator(
            predecessor.DEPENDENCIES["full_A104_operator"], (104, 104)
        )
    )
    q_value = GRAPH._load_record(
        json.loads(
            predecessor.DEPENDENCIES["rejected_q_Cauchy_104"].read_text()
        ),
        (104, 104),
    )
    return q_value, evolution


def _rref(value: np.ndarray, prime: int) -> tuple[np.ndarray, list[int]]:
    result = value.copy() % prime
    pivot_row = 0
    pivots: list[int] = []
    for column in range(result.shape[1]):
        candidates = np.flatnonzero(result[pivot_row:, column])
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        result[[pivot_row, selected]] = result[[selected, pivot_row]]
        inverse = pow(int(result[pivot_row, column]), -1, prime)
        result[pivot_row] = result[pivot_row] * inverse % prime
        for row in range(result.shape[0]):
            if row != pivot_row and result[row, column]:
                result[row] = (
                    result[row]
                    - result[row, column] * result[pivot_row]
                ) % prime
        pivots.append(column)
        pivot_row += 1
        if pivot_row == result.shape[0]:
            break
    return result, pivots


def _monomials(degree: int) -> list[tuple[int, int, int]]:
    return [
        candidate
        for candidate in product(range(degree + 1), repeat=3)
        if sum(candidate) == degree
    ]


def _spin_representation(spin: int, prime: int) -> list[np.ndarray]:
    """Return the rational harmonic-polynomial spin-l representation."""
    source = _monomials(spin)
    target = _monomials(spin - 2)
    source_index = {value: index for index, value in enumerate(source)}
    target_index = {value: index for index, value in enumerate(target)}
    symmetric_dimension = len(source)
    representation_dimension = 2 * spin + 1
    base = [
        np.asarray(matrix.tolist(), dtype=np.int64) % prime
        for matrix in predecessor._representation()
    ]

    def induced(matrix: np.ndarray) -> np.ndarray:
        result = np.zeros(
            (symmetric_dimension, symmetric_dimension), dtype=np.int64
        )
        for column, exponents in enumerate(source):
            for old_axis, count in enumerate(exponents):
                if not count:
                    continue
                for new_axis in range(3):
                    coefficient = int(matrix[new_axis, old_axis])
                    if not coefficient:
                        continue
                    output = list(exponents)
                    output[old_axis] -= 1
                    output[new_axis] += 1
                    row = source_index[tuple(output)]
                    result[row, column] = (
                        result[row, column] + count * coefficient
                    ) % prime
        return result

    # The invariant vector metric is diag(1,1,3); contraction by it cuts out
    # the harmonic irreducible from Sym^l of the rational adjoint module.
    contraction = np.zeros(
        (len(target), symmetric_dimension), dtype=np.int64
    )
    for column, exponents in enumerate(source):
        for axis, weight in enumerate((1, 1, 3)):
            if exponents[axis] < 2:
                continue
            output = list(exponents)
            output[axis] -= 2
            contraction[target_index[tuple(output)], column] = (
                exponents[axis]
                * (exponents[axis] - 1)
                * weight
            ) % prime
    reduced, pivot_columns = _rref(contraction, prime)
    free_columns = [
        column
        for column in range(symmetric_dimension)
        if column not in pivot_columns
    ]
    harmonic = np.zeros(
        (symmetric_dimension, len(free_columns)), dtype=np.int64
    )
    for local_column, free_column in enumerate(free_columns):
        harmonic[free_column, local_column] = 1
        for row, pivot_column in enumerate(pivot_columns):
            harmonic[pivot_column, local_column] = (
                -reduced[row, free_column]
            ) % prime
    if harmonic.shape != (symmetric_dimension, representation_dimension):
        raise AssertionError("harmonic spin dimension drifted")
    if np.any(contraction @ harmonic % prime):
        raise AssertionError("harmonic kernel construction failed")

    _, pivot_rows = _rref(harmonic.T, prime)
    selected = pivot_rows[:representation_dimension]
    square = harmonic[selected, :]
    augmented = np.concatenate(
        [
            square.copy(),
            np.eye(representation_dimension, dtype=np.int64),
        ],
        axis=1,
    )
    for column in range(representation_dimension):
        candidates = np.flatnonzero(augmented[column:, column])
        if not len(candidates):
            raise AssertionError("harmonic section lost rank")
        row = column + int(candidates[0])
        augmented[[column, row]] = augmented[[row, column]]
        augmented[column] = (
            augmented[column]
            * pow(int(augmented[column, column]), -1, prime)
        ) % prime
        for other in range(representation_dimension):
            if other != column and augmented[other, column]:
                augmented[other] = (
                    augmented[other]
                    - augmented[other, column] * augmented[column]
                ) % prime
    left_inverse = np.zeros(
        (representation_dimension, symmetric_dimension), dtype=np.int64
    )
    left_inverse[:, selected] = augmented[:, representation_dimension:]
    if not np.array_equal(
        left_inverse @ harmonic % prime,
        np.eye(representation_dimension, dtype=np.int64),
    ):
        raise AssertionError("harmonic left inverse failed")

    representation = [np.eye(representation_dimension, dtype=np.int64)]
    representation.extend(
        left_inverse @ induced(base[axis]) % prime @ harmonic % prime
        for axis in range(1, 4)
    )
    relations = (
        (1, 2, 3, SPECIALIZATION["u"]),
        (2, 3, 1, SPECIALIZATION["v"]),
        (3, 1, 2, SPECIALIZATION["v"]),
    )
    for left, right, target_axis, coefficient in relations:
        if np.any(
            (
                representation[left] @ representation[right]
                - representation[right] @ representation[left]
                - coefficient * representation[target_axis]
            )
            % prime
        ):
            raise AssertionError("spin representation lost Berger relation")
    return representation


def _coefficient_mod(
    polynomial: GRAPH.Polynomial, prime: int
) -> int:
    result = 0
    for monomial, coefficient in polynomial.items():
        result += (
            coefficient.numerator
            * pow(coefficient.denominator, -1, prime)
            * pow(SPECIALIZATION["alpha_B"], monomial[0], prime)
            * pow(SPECIALIZATION["u"], monomial[1], prime)
            * pow(SPECIALIZATION["v"], monomial[2], prime)
        )
    return result % prime


def _evaluate_operator(
    operator: GRAPH.Operator,
    representation: list[np.ndarray],
    prime: int,
) -> np.ndarray:
    dimension = representation[0].shape[0]
    result = np.zeros((dimension, dimension), dtype=np.int64)
    for word, polynomial in operator.items():
        represented_word = np.eye(dimension, dtype=np.int64)
        for axis in word:
            represented_word = (
                represented_word @ representation[axis]
            ) % prime
        result = (
            result
            + _coefficient_mod(polynomial, prime) * represented_word
        ) % prime
    return result


def _evaluate_matrix(
    matrix: GRAPH.Matrix,
    representation: list[np.ndarray],
    prime: int,
) -> np.ndarray:
    dimension = representation[0].shape[0]
    result = np.zeros(
        (104 * dimension, 104 * dimension), dtype=np.int64
    )
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if operator:
                result[
                    dimension * row:dimension * (row + 1),
                    dimension * column:dimension * (column + 1),
                ] = _evaluate_operator(operator, representation, prime)
    return result


def _compress(
    parts: list[np.ndarray],
    generator: np.random.Generator,
    nonzeros_per_column: int,
    prime: int,
) -> np.ndarray:
    candidates = np.concatenate(parts, axis=1)
    rows, columns = candidates.shape
    indices = np.empty(rows * nonzeros_per_column, dtype=np.int32)
    data = np.empty(rows * nonzeros_per_column, dtype=np.int64)
    indptr = np.arange(
        0,
        (rows + 1) * nonzeros_per_column,
        nonzeros_per_column,
        dtype=np.int32,
    )
    for column in range(rows):
        start = column * nonzeros_per_column
        stop = start + nonzeros_per_column
        indices[start:stop] = generator.choice(
            columns, nonzeros_per_column, replace=False
        )
        data[start:stop] = generator.integers(
            1, prime, nonzeros_per_column
        )
    compression_transpose = csr_matrix(
        (data, indices, indptr), shape=(rows, columns)
    )
    return np.asarray(compression_transpose @ candidates.T).T % prime


def _leading_minor_witness(
    value: np.ndarray, prime: int
) -> dict[str, Any]:
    matrix = value.copy() % prime
    determinant = 1
    selected_rows = list(range(matrix.shape[0]))
    pivot_count = 0
    for column in range(matrix.shape[1]):
        candidates = np.flatnonzero(matrix[pivot_count:, column])
        if not len(candidates):
            break
        selected = pivot_count + int(candidates[0])
        if selected != pivot_count:
            matrix[[pivot_count, selected]] = matrix[
                [selected, pivot_count]
            ]
            selected_rows[pivot_count], selected_rows[selected] = (
                selected_rows[selected],
                selected_rows[pivot_count],
            )
            determinant = -determinant % prime
        pivot = int(matrix[pivot_count, column])
        determinant = determinant * pivot % prime
        matrix[pivot_count] = (
            matrix[pivot_count] * pow(pivot, -1, prime)
        ) % prime
        if pivot_count + 1 < matrix.shape[0]:
            factors = matrix[pivot_count + 1:, column].copy()
            matrix[pivot_count + 1:] = (
                matrix[pivot_count + 1:]
                - factors[:, None] * matrix[pivot_count]
            ) % prime
        pivot_count += 1
        if pivot_count == matrix.shape[0]:
            break
    return {
        "certified_independent_columns": pivot_count,
        "pivot_rows": selected_rows[:pivot_count],
        "leading_minor_columns": list(range(pivot_count)),
        "minor_determinant_mod_prime": int(determinant),
    }


@lru_cache(maxsize=None)
def closure_audit(spin: int = 4) -> dict[str, Any]:
    q_value, evolution = _load_operators()
    representation = _spin_representation(spin, PRIME)
    dimension = len(representation[0])
    q_matrix = _evaluate_matrix(q_value, representation, PRIME)
    evolution_matrix = _evaluate_matrix(
        evolution, representation, PRIME
    )
    square = q_matrix @ q_matrix % PRIME
    commutator = (
        evolution_matrix @ q_matrix - q_matrix @ evolution_matrix
    ) % PRIME
    generator = np.random.default_rng(SEED + spin)
    closure = _compress(
        [square, commutator], generator, 100, PRIME
    )
    levels = [_leading_minor_witness(closure, PRIME)]
    for _ in range(8):
        closure = _compress(
            [
                closure,
                q_matrix @ closure % PRIME,
                evolution_matrix @ closure % PRIME,
                q_matrix.T @ closure % PRIME,
                evolution_matrix.T @ closure % PRIME,
            ],
            generator,
            150,
            PRIME,
        )
        levels.append(_leading_minor_witness(closure, PRIME))
        if (
            levels[-1]["certified_independent_columns"]
            == 104 * dimension
        ):
            break
    return {
        "schema": "pure-weyl-berger-q26-spin-module-closure-witness-v1",
        "result_id": "BERGER_Q26_SPIN4_MODULE_CLOSURE_WITNESS_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "closure_definition": (
            "smallest represented linear subspace containing Im(q_C^2) and "
            "Im([A104,q_C]) and stable under q_C, A104 and their free "
            "algebraic dual/transposed actions"
        ),
        "spin": spin,
        "representation_dimension": dimension,
        "prime": PRIME,
        "specialization": SPECIALIZATION,
        "seed": SEED + spin,
        "ambient_dimension": 104 * dimension,
        "closure_levels": levels,
        "certified_row_lower_bound": (
            levels[-1]["certified_independent_columns"] + dimension - 1
        )
        // dimension,
    }


def build() -> dict[str, Any]:
    pinned = _git_blob(PINNED_ORIGINAL_COMMIT, PINNED_ORIGINAL_PATH)
    if hashlib.sha256(pinned).hexdigest() != PINNED_ORIGINAL_SHA256:
        raise AssertionError("pinned original obstruction drifted")
    if _sha(SIX_ROW) != SIX_ROW_SHA256:
        raise AssertionError("terminal six-row obstruction drifted")
    six = json.loads(SIX_ROW.read_text())
    if (
        six["classification"]["minimum_total_row_addition_lower_bound"] != 10
        or six["classification"]["ten_row_extension_sufficient"]
    ):
        raise AssertionError("six-row successor boundary drifted")
    payload = closure_audit(4)
    last = payload["closure_levels"][-1]
    if (
        payload["representation_dimension"] != 9
        or payload["ambient_dimension"] != 936
        or payload["certified_row_lower_bound"] != 104
        or [level["certified_independent_columns"] for level in payload["closure_levels"]]
        != [139, 522, 936]
        or last["minor_determinant_mod_prime"] != 384
    ):
        raise AssertionError("spin-four closure witness drifted")
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-q26-finite-row-module-closure-lower-bound-v1",
        "result_id": RESULT_ID,
        "result_state": "DEFECT_AND_FREE_DUAL_MODULE_CLOSURE_FORCES_AT_LEAST_104_ADDED_ROWS",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": "unquotiented retained-26 formal companion/Cauchy carrier",
            "carrier": "finite free representation-graded support-local extensions of the frozen 104-row carrier",
            "degree": "-1,0,1,2 on the frozen carrier",
            "parity": "free algebraic dual completion; physical Cauchy/Krein pairing still open",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "all finite-order Berger PBW derivatives",
            "omega": "stationary A104 formal evolution; no spectral split"
        },
        "pinned_inputs": {
            "original_obstruction": {
                "commit": PINNED_ORIGINAL_COMMIT,
                "path": PINNED_ORIGINAL_PATH,
                "sha256": PINNED_ORIGINAL_SHA256
            },
            "six_row_terminal": {
                "result_id": six["result_id"],
                "path": str(SIX_ROW.relative_to(ROOT)),
                "sha256": SIX_ROW_SHA256
            },
            "q_Cauchy": {
                "path": str(predecessor.DEPENDENCIES["rejected_q_Cauchy_104"].relative_to(ROOT)),
                "sha256": _sha(predecessor.DEPENDENCIES["rejected_q_Cauchy_104"])
            },
            "A104": {
                "path": str(predecessor.DEPENDENCIES["full_A104_operator"].relative_to(ROOT)),
                "sha256": _sha(predecessor.DEPENDENCIES["full_A104_operator"])
            }
        },
        "representation_module_closure": {
            "coefficient_field": "GF(1009)",
            "rational_specialization": SPECIALIZATION,
            "representation": "9-dimensional rational spin-4 harmonic-polynomial representation",
            "multiplicative": True,
            "Berger_relations_verified": True,
            "closure_generators": ["Im(q_C^2)", "Im([A104,q_C])"],
            "closure_actions": ["q_C", "A104", "q_C^vee", "A104^vee"],
            "compression_role": "deterministic candidate selection only; the nonzero finite-field minor is the exact certificate",
            "level_independent_columns": [139, 522, 936],
            "ambient_dimension": 936,
            "full_closure": True,
            "final_minor_determinant_mod_1009": 384,
            "row_generator_bound": "9*n_new >= 936",
            "added_rows_at_least": 104,
            "forced_free_row_degree_profile_at_least": {
                "degree_minus1": 12,
                "degree_0": 40,
                "degree_plus1": 40,
                "degree_plus2": 12
            }
        },
        "proof": {
            "finite_field_lift": "Every denominator is invertible modulo 1009. A nonzero 936-by-936 minor after exact reduction modulo 1009 is a nonzero rational minor, so the rational represented closure has full dimension 936.",
            "row_bound": "One free PBW carrier row evaluates to at most nine dimensions in the spin-4 representation. Factoring a 936-dimensional closure therefore requires at least ceil(936/9)=104 rows.",
            "field_redefinition_invariance": "Invertible degree-preserving support-local row and field redefinitions preserve free module rank and represented closure dimension.",
            "strict_improvement": "The previous cyclic rank bound was ten rows; defect-module and free-dual saturation raises the necessary bound to 104 rows."
        },
        "exact_payload": {
            "artifact_id": payload["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest()
        },
        "classification": {
            "defect_and_free_dual_closure_full_on_spin4": True,
            "minimum_added_free_rows_at_least": 104,
            "one_hundred_four_row_extension_sufficient": False,
            "smallest_finite_extension_constructed": False,
            "no_finite_closure_theorem": False,
            "physical_Cauchy_pairing_constructed": False,
            "real_involution_constructed": False,
            "Hadamard_or_quantum_claim": False
        },
        "next_gate": "SOLVE_OR_OBSTRUCT_THE_104_ROW_FREE_ADJOINT_COMPLETION_WITH_RETAINED_SOLUTION_MAP_AND_PHYSICAL_PAIRING",
        "claim_boundary": (
            "This exact multiplicative-representation theorem computes the "
            "defect-generated, free-algebraic-dual-saturated module closure "
            "required by the current gate and raises the necessary free-row "
            "extension bound from ten to 104. It is a lower bound, not a "
            "104-row construction or proof of sufficiency. It does not decide "
            "more economical non-free/projective module presentations unless "
            "they are admitted explicitly, construct the physical Cauchy/Krein "
            "pairing or real involution, prove a no-finite-closure theorem, or "
            "provide Hadamard, positivity, QME, particle, scattering or "
            "unitarity data."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=quantum-weyl:. python3 -m d_quotient_classical.causal_transfer.berger_q26_finite_row_module_closure --check --guards",
                "PYTHONPATH=quantum-weyl:. python3 -m d_quotient_classical.causal_transfer.verify_berger_q26_finite_row_module_closure",
                "PYTHONPATH=quantum-weyl:. python3 -m unittest d_quotient_classical.causal_transfer.tests.test_berger_q26_finite_row_module_closure",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-q26-finite-row-module-closure-lower-bound-v1.schema.json -d d_quotient_classical/certificates/BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json"
            ]
        }
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Berger q26 finite-row module closure: 104-row lower bound

The frozen \(104\)-row Cauchy graph has 157 square defects and 207 evolution
commutator defects.  The first cyclic rank audit raised the extension bound
from six to ten rows.  The present calculation closes the actual defect images
under \(q_C\), \(A_{104}\), and their free algebraic dual actions.

The calculation uses the exact nine-dimensional rational spin-four
harmonic-polynomial representation of the specialized Berger algebra over
\(\mathbf F_{1009}\).  It is multiplicative and verifies all three Berger
commutators.  Starting from

\[
\operatorname{Im}(q_C^2)+\operatorname{Im}([A_{104},q_C]),
\]

the certified independent-column counts are

\[
139\longrightarrow522\longrightarrow936.
\]

The ambient represented carrier also has dimension \(104\cdot9=936\).  The
final exact minor has determinant \(384\pmod{1009}\), so it is nonzero over
the rational source algebra as well.  Thus the defect/free-dual closure is the
entire represented carrier.  Since one free PBW row evaluates to at most nine
dimensions, every free carrier through which this closure factors requires
at least

\[
\left\lceil\frac{936}{9}\right\rceil=104
\]

new rows, with the full frozen degree profile
\((12,40,40,12)\) as the free-row lower bound.

This is a strict improvement of the ten-row cyclic rank bound.  It is not yet
the terminal finite-row theorem: no \(104\)-row extension, physical
Cauchy/Krein pairing, real involution or retained solution-map contraction is
constructed, and sufficiency remains open.  The next calculation is the exact
free-adjoint \(104\)-row completion system.
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = [
        ("representation_module_closure", "added_rows_at_least", 103),
        ("classification", "one_hundred_four_row_extension_sufficient", True),
        ("classification", "Hadamard_or_quantum_claim", True),
    ]
    for section, field, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][field] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation survived: {section}.{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = closure_audit(4)
    value = build()
    validate(value)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if PAYLOAD.read_text() != _render(payload):
            raise AssertionError("spin-four closure payload drifted")
        if OUTPUT.read_text() != _render(value):
            raise AssertionError("module-closure certificate drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("module-closure report drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
