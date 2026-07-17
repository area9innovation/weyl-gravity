#!/usr/bin/env python3
"""Generate the exact rank-one/global, rank-two/observer code fixture.

The construction specializes the encoding map and pointer-basis clone of
arXiv:2501.02359v2, equations (1.1), (3.7), and (4.1)--(4.6).  Rank is
computed from declared matrix data; it is never inserted as an input.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/rank_one_cloned_observer_input.json"
CERTIFICATE = PACKAGE / "certificates/RANK_ONE_CLONED_OBSERVER_FIXTURE.json"
SCHEMA = PACKAGE / "schema/rank-one-cloned-observer-fixture-v1.schema.json"
INPUT_SCHEMA = PACKAGE / "schema/rank-one-cloned-observer-input-v1.schema.json"
SOURCE_PATHS = (
    PACKAGE / "generate_rank_one_fixture.py",
    PACKAGE / "verify_rank_one_fixture.py",
    PACKAGE / "tests/test_rank_one_fixture.py",
    INPUT,
    INPUT_SCHEMA,
    SCHEMA,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | int) -> sp.Rational:
    fraction = Fraction(str(value))
    return sp.Rational(fraction.numerator, fraction.denominator)


def _strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.simplify(value)) for value in matrix.row(row)] for row in range(matrix.rows)]


def _minor(matrix: sp.Matrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> sp.Expr:
    return sp.simplify(matrix.extract(rows, columns).det())


def _apply_patch(data: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    mutated = deepcopy(data)
    for key, value in patch.items():
        mutated[key] = value
    return mutated


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    numerator = sp.Matrix(data["orthogonal_numerator"])
    denominator = _q(data["orthogonal_denominator"])
    orthogonal = numerator / denominator
    if orthogonal.rows != orthogonal.cols:
        raise AssertionError("O must be square")
    dimension = orthogonal.rows
    identity = sp.eye(dimension)
    orthogonality_residual = sp.simplify(orthogonal * orthogonal.T - identity)
    if orthogonality_residual != sp.zeros(dimension):
        raise AssertionError("declared O is not exactly orthogonal")

    observer_labels = data["effective_basis"]["observer_labels"]
    matter_labels = data["effective_basis"]["matter_labels"]
    observer_dimension = len(observer_labels)
    matter_dimension = len(matter_labels)
    if observer_dimension * matter_dimension != dimension:
        raise AssertionError("effective basis does not span O")
    projection_rows = data["projection_rows"]
    projection = sp.zeros(len(projection_rows), dimension)
    for output_row, source_row in enumerate(projection_rows):
        projection[output_row, source_row] = 1
    global_encoding = sp.sqrt(dimension) * projection * orthogonal
    global_gram = sp.Matrix(sp.simplify(global_encoding.T * global_encoding))
    for source_row in data["factorization_amplitude_rows"]:
        amplitude = sp.sqrt(dimension) * orthogonal.row(source_row)
        global_gram += amplitude.T * amplitude

    probabilities = [_q(value) for value in data["pointer_probabilities"]]
    if sum(probabilities, sp.S(0)) != 1 or any(value <= 0 for value in probabilities):
        raise AssertionError("pointer probabilities must be positive and normalized")
    clone_map = data["clone_map"]
    clone_injective = len(set(clone_map)) == observer_dimension
    pointer_overlap = sp.Matrix([[_q(value) for value in row] for row in data["pointer_basis_overlap_squared"]])
    pointer_basis_aligned = pointer_overlap == sp.eye(observer_dimension)
    output_clone_dimension = observer_dimension if data["observer_channel_enabled"] else 1
    observer_encoding = sp.zeros(output_clone_dimension * len(projection_rows), matter_dimension)
    for observer_index in range(observer_dimension):
        clone_index = clone_map[observer_index] if data["observer_channel_enabled"] else 0
        for projection_index, source_row in enumerate(projection_rows):
            output_index = clone_index * len(projection_rows) + projection_index
            for matter_index in range(matter_dimension):
                effective_index = observer_index * matter_dimension + matter_index
                observer_encoding[output_index, matter_index] += (
                    sp.sqrt(dimension * probabilities[observer_index])
                    * orthogonal[source_row, effective_index]
                )
    observer_gram = sp.simplify(observer_encoding.T * observer_encoding)

    global_rank = int(global_gram.rank())
    observer_rank = int(observer_encoding.rank())
    requirements = {
        "global_gram_rank_one": global_rank == 1,
        "global_fundamental_dimension_one": len(projection_rows) == 1,
        "observer_encoding_rank_gt_one": observer_rank > 1,
        "pointer_basis_aligned": pointer_basis_aligned,
        "pointer_reference_injective": data["observer_channel_enabled"] and clone_injective,
    }
    return {
        "orthogonality_residual": orthogonality_residual,
        "global_encoding": global_encoding,
        "global_gram": global_gram,
        "observer_encoding": observer_encoding,
        "observer_gram": observer_gram,
        "global_rank": global_rank,
        "observer_rank": observer_rank,
        "global_fundamental_dimension": len(projection_rows),
        "observer_output_dimension": observer_encoding.rows,
        "requirements": requirements,
    }


def build_certificate() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    result = evaluate(data)
    global_gram = result["global_gram"]
    observer_encoding = result["observer_encoding"]
    all_two_minors = []
    for row_a in range(global_gram.rows):
        for row_b in range(row_a + 1, global_gram.rows):
            for column_a in range(global_gram.cols):
                for column_b in range(column_a + 1, global_gram.cols):
                    value = _minor(global_gram, (row_a, row_b), (column_a, column_b))
                    all_two_minors.append(
                        {
                            "rows": [row_a, row_b],
                            "columns": [column_a, column_b],
                            "value": sp.sstr(value),
                        }
                    )
    mutation_results = []
    for mutation in data["mutations"]:
        mutated = evaluate(_apply_patch(data, mutation["patch"]))
        requirement = mutation["expected_failed_requirement"]
        mutation_results.append(
            {
                "name": mutation["name"],
                "breaks": mutation["breaks"],
                "expected_failed_requirement": requirement,
                "observed_requirement_value": mutated["requirements"][requirement],
                "observed_global_rank": mutated["global_rank"],
                "observed_observer_rank": mutated["observer_rank"],
                "expected_failure_passed": mutated["requirements"][requirement] is False,
            }
        )
    if not all(result["requirements"].values()):
        raise AssertionError(f"base fixture failed: {result['requirements']}")
    if not all(item["expected_failure_passed"] for item in mutation_results):
        raise AssertionError("one or more mutation tests did not fail closed")

    return {
        "schema": "closed-universe-rank-one-cloned-observer-fixture-v1",
        "result_id": "RANK_ONE_CLONED_OBSERVER_FIXTURE",
        "claim_status": "EXTERNAL_FIXTURE_REPRODUCED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "source_equations": data["source_model"],
        "declared_input_sha256": _sha256(INPUT),
        "dimensions": {
            "effective_input": len(data["orthogonal_numerator"]),
            "global_fundamental": result["global_fundamental_dimension"],
            "observer_effective_input": len(data["effective_basis"]["matter_labels"]),
            "observer_effective_output": result["observer_output_dimension"],
        },
        "generated_matrices": {
            "global_encoding": _strings(result["global_encoding"]),
            "global_gram": _strings(global_gram),
            "observer_encoding": _strings(observer_encoding),
            "observer_gram": _strings(result["observer_gram"]),
        },
        "exact_witnesses": {
            "orthogonality_residual_zero": result["orthogonality_residual"] == sp.zeros(4),
            "global_rank": result["global_rank"],
            "global_nonzero_minor": {"rows": [0], "columns": [0], "value": sp.sstr(global_gram[0, 0])},
            "global_all_2x2_minors": all_two_minors,
            "observer_rank": result["observer_rank"],
            "observer_full_rank_minor": {
                "rows": [0, 1],
                "columns": [0, 1],
                "value": sp.sstr(_minor(observer_encoding, (0, 1), (0, 1))),
            },
        },
        "mutation_results": mutation_results,
        "flags": {
            "GLOBAL_GRAM_RANK_ONE": result["requirements"]["global_gram_rank_one"],
            "GLOBAL_HILBERT_DIMENSION_ONE_IN_FIXTURE": result["requirements"]["global_fundamental_dimension_one"],
            "OBSERVER_EFFECTIVE_DIMENSION_GT_ONE": result["requirements"]["observer_encoding_rank_gt_one"],
            "POINTER_BASIS_ALIGNED": result["requirements"]["pointer_basis_aligned"],
            "POINTER_REFERENCE_INJECTIVE": result["requirements"]["pointer_reference_injective"],
            "BERGER_QUANTUM_COMPARISON": False,
            "LORENTZIAN_CAUSAL_CLAIM": False,
        },
        "claim_boundary": (
            "This exact finite specialization reproduces a rank-one global Gram matrix and a rank-two "
            "cloned-observer encoding from one declared fixed orthogonal map. It certifies the algebraic "
            "compatibility of global collapse with a nontrivial observer-effective carrier. It is not a "
            "gravitational path-integral derivation, a generic-Haar error bound, a causal model, or evidence "
            "about the Berger quantum Hilbert space."
        ),
        "not_established": [
            "a generic or typical fixed-O estimate",
            "a probability interpretation induced from a gravitational inner product",
            "a causal observer dynamics",
            "a localized detector or apparatus",
            "any identification with Taub-zero or the Berger D quotient",
            "any Lorentzian quantum result",
        ],
        "provenance": {
            "external_source": {
                "arxiv_id": "2501.02359v2",
                "pdf_sha256": "3627126670d3ddf97f8facc8bed261386ec9adc51281b964cc7815912e0f6cfc",
                "url": "https://arxiv.org/abs/2501.02359v2",
            },
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_PATHS
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("generated certificate is stale")
    else:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE.write_text(rendered)
    print("RANK_ONE_CLONED_OBSERVER_FIXTURE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
