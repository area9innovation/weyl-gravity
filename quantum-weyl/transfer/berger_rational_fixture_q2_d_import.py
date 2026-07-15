"""Pinned ND2 import of the exact rational Berger reduced-mode q2/D block."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from .arity_two_cartan import (
        ArityTwoCartanData,
        ArityTwoComplex,
        BilinearOperator,
        LinearOperator,
    )
except ImportError:
    from arity_two_cartan import (
        ArityTwoCartanData,
        ArityTwoComplex,
        BilinearOperator,
        LinearOperator,
    )


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "74311edb2fb907060e86f740977439f4db8b0ed5"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"
SCHEMA_RELATIVE = "d_quotient_classical/schema/berger-rational-fixture-q2-d-block-v1.schema.json"
PRODUCER_RELATIVE = "d_quotient_classical/backreacted_clock/berger_rational_fixture_q2_d_block.py"
VERIFIER_RELATIVE = "d_quotient_classical/backreacted_clock/verify_berger_rational_fixture_q2_d_block.py"
TEST_RELATIVE = "d_quotient_classical/backreacted_clock/tests/test_berger_rational_fixture_q2_d_block.py"
REPORT_RELATIVE = "d_quotient_classical/reports/berger-rational-fixture-q2-d-block.md"


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned classical artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }

def _fraction(value: object) -> Fraction:
    if not isinstance(value, str):
        raise ValueError("exact coefficient is not a string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"coefficient is not rational: {value!r}") from exc


def _matrix(rows: object, rank: int) -> list[list[Fraction]]:
    if not isinstance(rows, list) or len(rows) != rank:
        raise ValueError("matrix row count drifted")
    output: list[list[Fraction]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) != rank:
            raise ValueError("matrix column count drifted")
        output.append([_fraction(value) for value in row])
    return output


def _matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction()) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def _add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def _zero_matrix(rank: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(rank)] for _ in range(rank)]


def _zero_tensor(rank: int) -> list[list[list[Fraction]]]:
    return [[[Fraction() for _ in range(rank)] for _ in range(rank)] for _ in range(rank)]


def assemble_cartan_data() -> ArityTwoCartanData:
    """Return the fully validated exact Cartan input behind the import receipt."""

    # Keep the public solver input behind the same fail-closed import checks;
    # downstream verdicts must not reconstruct a competing classical payload.
    build_import()
    payload = _git_json(CERTIFICATE_RELATIVE)
    rows = payload["row_layout"]
    degrees = tuple(row["degree"] for row in rows)
    parities = tuple(row["parity"] for row in rows)
    q1 = LinearOperator.from_rows(
        "classical_unary_q1",
        1,
        _matrix(payload["classical_unary_q1"]["matrix"], 6),
    )
    lie_d = LinearOperator.from_rows(
        "D_action_cl",
        0,
        _matrix(payload["D_action_cl"]["matrix"], 6),
    )
    complex_ = ArityTwoComplex(degrees, parities, q1)
    tensor = _zero_tensor(6)
    for entry in payload["classical_binary_q2"]["entries"]:
        output, left, right = entry["output"], entry["left"], entry["right"]
        coefficient = _fraction(entry["coefficient"])
        tensor[output][left][right] = coefficient
        tensor[output][right][left] = coefficient
    return ArityTwoCartanData(
        complex=complex_,
        q2=BilinearOperator.from_entries("classical_binary_q2", 1, tensor),
        iota_D=LinearOperator.zero("iota_D_centered", -1, 6),
        lie_D=lie_d,
        lie_D2=BilinearOperator.zero("D_action_cl_arity_two", 0, 6),
    )


def build_import() -> dict[str, Any]:
    payload = _git_json(CERTIFICATE_RELATIVE)
    schema = _git_json(SCHEMA_RELATIVE)
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-rational-fixture-q2-d-block-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical reduced-mode schema identity or strictness drifted")
    if payload.get("result_id") != "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK":
        raise ValueError("classical reduced-mode result identity drifted")
    if payload.get("claim_status") != "CERTIFIED_REDUCED_MODE_Q2_D_BLOCK":
        raise ValueError("classical reduced-mode claim status drifted")
    if payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise ValueError("classical reduced-mode dependency tags drifted")
    scope = payload.get("scope")
    if not isinstance(scope, dict) or scope.get("not_support_local_q2") is not True:
        raise ValueError("classical reduced-mode boundary was erased")
    rows = payload.get("row_layout")
    if not isinstance(rows, list) or [row.get("index") for row in rows if isinstance(row, dict)] != list(range(6)):
        raise ValueError("classical six-row layout drifted")
    degrees = tuple(row["degree"] for row in rows)
    parities = tuple(row["parity"] for row in rows)
    weights = tuple(row["D_weight"] for row in rows)
    if degrees != (0, 0, 0, 1, 1, 1) or parities != degrees or weights != (0,) * 6:
        raise ValueError("classical grading or D-weight ledger drifted")

    q1_rows = _matrix(payload["classical_unary_q1"]["matrix"], 6)
    d_rows = _matrix(payload["D_action_cl"]["matrix"], 6)
    pairing = _matrix(payload["cyclic_pairing"]["matrix"], 6)
    q1 = LinearOperator.from_rows("classical_unary_q1", 1, q1_rows)
    lie_d = LinearOperator.from_rows("D_action_cl", 0, d_rows)
    complex_ = ArityTwoComplex(degrees, parities, q1)

    tensor = _zero_tensor(6)
    seen: set[tuple[int, int, int]] = set()
    entries = payload["classical_binary_q2"]["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("classical q2 is empty")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"output", "left", "right", "coefficient"}:
            raise ValueError("classical q2 entry shape drifted")
        output, left, right = entry["output"], entry["left"], entry["right"]
        if not all(type(index) is int and 0 <= index < 6 for index in (output, left, right)):
            raise ValueError("classical q2 index is invalid")
        if left > right or (output, left, right) in seen:
            raise ValueError("classical q2 canonical ordering drifted")
        coefficient = _fraction(entry["coefficient"])
        tensor[output][left][right] = coefficient
        tensor[output][right][left] = coefficient
        seen.add((output, left, right))
    q2 = BilinearOperator.from_entries("classical_binary_q2", 1, tensor)
    complex_.validate_bilinear(q2)

    data = ArityTwoCartanData(
        complex=complex_,
        q2=q2,
        iota_D=LinearOperator.zero("iota_D_centered", -1, 6),
        lie_D=lie_d,
        lie_D2=BilinearOperator.zero("D_action_cl_arity_two", 0, 6),
    )
    checks = data.checks()
    classification = data.classify()
    if not all(checks.values()) or classification.status != "ZERO_SOURCE":
        raise ValueError("ND2 exact identities failed on the reduced-mode fixture")

    if _add(_matmul(_transpose(q1_rows), pairing), _matmul(pairing, q1_rows)) != _zero_matrix(6):
        raise ValueError("classical q1 cyclicity failed")
    cyclic_q2 = True
    for a in range(3):
        for b in range(3):
            for c in range(3):
                values = [
                    sum((pairing[o][c] * tensor[o][a][b] for o in range(6)), Fraction()),
                    sum((pairing[o][a] * tensor[o][b][c] for o in range(6)), Fraction()),
                    sum((pairing[o][b] * tensor[o][c][a] for o in range(6)), Fraction()),
                ]
                cyclic_q2 = cyclic_q2 and values[0] == values[1] == values[2]
    if not cyclic_q2:
        raise ValueError("classical q2 cyclicity failed")
    if any(weights[o] != weights[l] + weights[r] for o, l, r in seen):
        raise ValueError("declared D-weight block is not closed")

    false_flags = (
        "CLASSICAL_SUPPORT_LOCAL_Q2",
        "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
        "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
        "ND2_PHYSICAL_EXECUTION_AUTHORIZED",
    )
    if any(payload["flags"].get(flag) is not False for flag in false_flags):
        raise ValueError("classical reduced-mode result crossed a full-theory gate")
    return {
        "schema": "quantum-weyl-berger-rational-fixture-q2-d-import-v1",
        "result_id": "ND2_REDUCED_MODE_FIXTURE_IMPORT",
        "claim_status": "CERTIFIED_REDUCED_MODE_ND2_INPUT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "classical_source": {
            "commit": CLASSICAL_COMMIT,
            "artifacts": {
                name: _artifact(relative)
                for name, relative in (
                    ("certificate", CERTIFICATE_RELATIVE),
                    ("schema", SCHEMA_RELATIVE),
                    ("producer", PRODUCER_RELATIVE),
                    ("independent_verifier", VERIFIER_RELATIVE),
                    ("tests", TEST_RELATIVE),
                    ("report", REPORT_RELATIVE),
                )
            },
        },
        "imported_block": {
            "row_count": 6,
            "row_ids": [row["row_id"] for row in rows],
            "degrees": list(degrees),
            "parities": list(parities),
            "input_D_weights": list(weights),
            "output_D_weights": list(weights),
            "q1_nonzero_count": sum(value != 0 for row in q1_rows for value in row),
            "q2_nonzero_canonical_count": len(seen),
            "coefficient_domain": "Q",
            "admissible_mode_block": scope["category"],
        },
        "nd2_checks": {
            **checks,
            "q1_cyclic": True,
            "q2_cyclic": cyclic_q2,
            "declared_mode_block_closed": True,
            "all_coefficients_rational": True,
        },
        "nd2_classification": {
            "status": classification.status,
            "cartan_source_nonzero_count": 0,
            "interpretation": "The centered weight-zero fixture has no arity-two D-Cartan source; it validates exact ingestion and identities but does not test a nonzero-weight obstruction.",
        },
        "authorization": {
            "reduced_mode_solver_input": True,
            "full_support_local_q2": False,
            "nonzero_weight_D_equivariance": False,
            "physical_ND2_execution": False,
        },
        "next_gate": "NONZERO_WEIGHT_REDUCED_MODE_BLOCK_OR_NORMALIZED_LEAKAGE_OBSTRUCTION",
        "claim_boundary": "This pinned consumer imports and independently evaluates the action-derived six-row rational REDUCED-MODE q2/D block. It is not the full support-local q2 and authorizes no physical or quantum conclusion.",
    }
