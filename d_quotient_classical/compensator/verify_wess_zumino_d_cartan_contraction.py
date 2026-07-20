#!/usr/bin/env python3
"""Independent exact verifier for the WZ compensator D-Cartan export."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "wess-zumino-d-cartan-contraction-v1.schema.json"
)

Matrix = list[list[Fraction]]


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _coefficient(value: int | dict[str, int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _matrix(record: dict[str, Any]) -> Matrix:
    canonical = {
        "row_count": record["row_count"],
        "column_count": record["column_count"],
        "entries": record["entries"],
    }
    if _digest(canonical) != record["sha256"]:
        raise AssertionError("matrix hash mismatch")
    value = [
        [Fraction() for _ in range(record["column_count"])]
        for _ in range(record["row_count"])
    ]
    for entry in record["entries"]:
        row = entry["row"]
        column = entry["column"]
        if not (
            0 <= row < record["row_count"]
            and 0 <= column < record["column_count"]
        ):
            raise AssertionError("matrix entry outside its declared shape")
        if value[row][column]:
            raise AssertionError("duplicate sparse matrix entry")
        value[row][column] = _coefficient(entry["coefficient"])
    return value


def _zero(rows: int, columns: int) -> Matrix:
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def _identity(dimension: int) -> Matrix:
    value = _zero(dimension, dimension)
    for index in range(dimension):
        value[index][index] = Fraction(1)
    return value


def _transpose(value: Matrix) -> Matrix:
    return [list(row) for row in zip(*value)]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _scale(coefficient: int, value: Matrix) -> Matrix:
    return [[coefficient * item for item in row] for row in value]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _check_dependencies(value: dict[str, Any]) -> None:
    for reference in value["dependencies"].values():
        path = ROOT / reference["path"]
        if not path.exists():
            raise AssertionError(f"missing dependency: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            artifact_id = (
                payload.get("result_id")
                or payload.get("schema")
                or "UNIDENTIFIED_JSON"
            )
        else:
            artifact_id = path.stem
        if artifact_id != reference["artifact_id"]:
            raise AssertionError(f"dependency identity mismatch: {path}")


def verify(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise AssertionError(
            "schema failure: "
            + "; ".join(error.message for error in errors[:5])
        )
    _check_dependencies(value)

    fixtures = value["matrix_fixtures"]
    q4 = _matrix(fixtures["quartet_Q0"])
    h4 = _matrix(fixtures["quartet_h"])
    omega4 = _matrix(fixtures["quartet_pairing"])
    zero4 = _zero(4, 4)
    identity4 = _identity(4)
    expected_q4 = _zero(4, 4)
    expected_q4[1][0] = Fraction(1)
    expected_q4[3][2] = Fraction(1)
    expected_h4 = _zero(4, 4)
    expected_h4[0][1] = Fraction(1)
    expected_h4[2][3] = Fraction(1)
    expected_omega4 = _zero(4, 4)
    expected_omega4[0][3] = Fraction(1)
    expected_omega4[3][0] = Fraction(-1)
    expected_omega4[1][2] = Fraction(-1)
    expected_omega4[2][1] = Fraction(1)
    if (q4, h4, omega4) != (
        expected_q4,
        expected_h4,
        expected_omega4,
    ):
        raise AssertionError("quartet convention matrix changed")
    if (
        _multiply(q4, q4) != zero4
        or _add(_multiply(q4, h4), _multiply(h4, q4)) != identity4
        or _multiply(h4, h4) != zero4
        or _add(
            _multiply(_transpose(q4), omega4),
            _multiply(omega4, q4),
        )
        != zero4
        or _add(
            _multiply(_transpose(h4), omega4),
            _multiply(omega4, h4),
        )
        != zero4
    ):
        raise AssertionError("quartet exact/cyclic identities failed")

    retract = fixtures["unit_plus_quartet"]
    q5 = _matrix(retract["Q0"])
    inclusion = _matrix(retract["inclusion"])
    projection = _matrix(retract["projection"])
    homotopy5 = _matrix(retract["homotopy"])
    projector = _multiply(inclusion, projection)
    if (
        _multiply(projection, inclusion) != _identity(1)
        or _add(
            _multiply(q5, homotopy5),
            _multiply(homotopy5, q5),
        )
        != _add(_identity(5), _scale(-1, projector))
        or _multiply(homotopy5, homotopy5) != _zero(5, 5)
        or _multiply(projection, homotopy5) != _zero(1, 5)
        or _multiply(homotopy5, inclusion) != _zero(5, 1)
    ):
        raise AssertionError("unit-plus-quartet SDR failed")

    weights = []
    for row in fixtures["cartan_weight_fixtures"]:
        weight = row["D_weight"]
        weights.append(weight)
        matrices = row["matrices"]
        q = _matrix(matrices["Q0"])
        iota = _matrix(matrices["iota_D0"])
        lie = _matrix(matrices["L_D0"])
        homotopy = _matrix(matrices["homotopy"])
        if (
            _multiply(q, q) != _zero(8, 8)
            or _add(_multiply(q, iota), _multiply(iota, q)) != lie
            or _add(
                _multiply(q, homotopy),
                _multiply(homotopy, q),
            )
            != _identity(8)
            or lie != _scale(weight, _identity(8))
        ):
            raise AssertionError(f"Cartan replay failed at weight {weight}")
    if weights != [-2, 0, 3]:
        raise AssertionError("Cartan mutation-sensitive weights changed")

    weight_pairs = []
    for row in fixtures["cyclic_weight_pair_fixtures"]:
        weight_pair = row["weight_pair"]
        weight_pairs.append(weight_pair)
        matrices = row["matrices"]
        pairing = _matrix(matrices["pairing"])
        for name in ("Q0", "homotopy", "L_D0"):
            operator = _matrix(matrices[name])
            if _add(
                _multiply(_transpose(operator), pairing),
                _multiply(pairing, operator),
            ) != _zero(8, 8):
                raise AssertionError(
                    f"opposite-weight cyclicity failed: {name} {weight_pair}"
                )
    if weight_pairs != [[0, 0], [2, -2]]:
        raise AssertionError("cyclic weight-pair fixtures changed")

    affine = value["affine_Weyl_component_gate"]["rows"]
    cylinder = affine["vacuum_cylinder_D_compact"]
    minkowski = affine["minkowski_D_M_cross_check"]
    if (
        cylinder["sigma_D"] != 0
        or cylinder["pi_LD_tau_minus_LD_pi_tau"] != 0
        or cylinder["contraction_equivariant"] is not True
        or minkowski["sigma_D"] != -1
        or minkowski["pi_LD_tau_minus_LD_pi_tau"] != -1
        or minkowski["contraction_equivariant"] is not False
    ):
        raise AssertionError("affine Weyl-component gate failed")

    if value["claim_flags"] != {
        "SAME_BACKGROUND_TAU_ADIC_COMPENSATOR_D_CONTRACTION": True,
        "RAW_D_COMPACT_USED": True,
        "RAW_D_REPLACED_BY_K_BERGER": False,
        "WZ_TAU_IDENTIFIED_WITH_BERGER_CLOCK": False,
        "MINKOWSKI_DILATION_CONTRACTION_EXPORTED": False,
        "QUANTUM_D_CARTAN_DEFECT_CLASSIFIED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        "HADAMARD_OR_POSITIVITY_CLAIM": False,
    }:
        raise AssertionError("claim boundary changed")


def main() -> int:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify(value)
    print(
        "WESS-ZUMINO D-CARTAN independent verification: "
        "RAW D_COMPACT PASS; MINKOWSKI AFFINE PROJECTION REJECTED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
