#!/usr/bin/env python3
"""Independent exact audit of the portable coupled unary/pairing/SDR."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _is_zero,
    _matrix_add,
    _one,
    _sparse_multiply,
    _zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    _adjoint_matrix,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    _fixture_linear,
)


CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _parse_record(record: dict, shape: tuple[int, int], name: str):
    if record.get("shape") != list(shape):
        raise AssertionError(f"{name} shape drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record.get("sha256") != _digest(body):
        raise AssertionError(f"{name} record hash drifted")
    matrix = _zero(*shape)
    previous = None
    for target, source, terms in record["entries"]:
        if previous is not None and (target, source) <= previous:
            raise AssertionError(f"{name} entries are not strictly ordered")
        operator_terms = []
        for exponents, raw in terms:
            if len(exponents) != 4 or any(type(value) is not int or value < 0 for value in exponents):
                raise AssertionError(f"{name} has an invalid PBW multiindex")
            coefficient = sp.sympify(raw, locals={"sqrt": sp.sqrt})
            if coefficient.atoms(sp.Float):
                raise AssertionError(f"{name} contains floating-point arithmetic")
            word = tuple(
                axis for axis, multiplicity in enumerate(exponents) for _ in range(multiplicity)
            )
            operator_terms.append((0, word, coefficient))
        matrix[target][source] = _fixture_linear(LinearOperator.from_terms(operator_terms))
        previous = (target, source)
    return matrix


def _fixture(matrix):
    return [[_fixture_linear(entry) for entry in row] for row in matrix]


def _multiply(left, right):
    return _fixture(_sparse_multiply(left, right))


def _add(left, right):
    return _fixture(_matrix_add(left, right))


def _negative(matrix):
    return [[entry.scale(-1) for entry in row] for row in matrix]


def _subtract(left, right):
    return _add(left, _negative(right))


def _adjoint(matrix):
    return _fixture(_adjoint_matrix(matrix))


def _identity(size: int):
    output = _zero(size, size)
    for index in range(size):
        output[index][index] = _one()
    return output


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / relative
        if _sha256(path) != digest:
            raise AssertionError(f"source hash mismatch: {path}")

    full = certificate["full_complex"]
    retained = certificate["retained_complex"]
    contraction = certificate["contraction"]
    if [row["index"] for row in full["component_rows"]] != list(range(64)):
        raise AssertionError("full row ledger is not ordered")
    if [row["index"] for row in retained["component_rows"]] != list(range(36)):
        raise AssertionError("retained row ledger is not ordered")
    if [row["row_id"] for row in retained["component_rows"][26:]] != [
        row["row_id"] for row in full["component_rows"][54:]
    ]:
        raise AssertionError("Maxwell retained row identities drifted")

    q64 = _parse_record(full["classical_unary_q1"], (64, 64), "q64")
    omega64 = _parse_record(full["cyclic_pairing"], (64, 64), "omega64")
    q36 = _parse_record(retained["classical_unary_q1"], (36, 36), "q36")
    omega36 = _parse_record(retained["cyclic_pairing"], (36, 36), "omega36")
    iota = _parse_record(contraction["iota_36_to_64"], (64, 36), "iota")
    projection = _parse_record(contraction["pi_64_to_36"], (36, 64), "projection")
    homotopy = _parse_record(contraction["S_64"], (64, 64), "homotopy")

    checks = {
        "q64_squared_zero": _is_zero(_multiply(q64, q64)),
        "q64_odd_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q64), omega64), _multiply(omega64, q64))),
        "omega64_antisymmetric": _is_zero(_add(_adjoint(omega64), omega64)),
        "pi36_iota36_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "iota36_chain_map": _is_zero(_subtract(_multiply(q64, iota), _multiply(iota, q36))),
        "pi36_chain_map": _is_zero(_subtract(_multiply(projection, q64), _multiply(q36, projection))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q64, homotopy), _multiply(homotopy, q64)), _subtract(_identity(64), _multiply(iota, projection)))),
        "homotopy_square_zero": _is_zero(_multiply(homotopy, homotopy)),
        "projection_homotopy_zero": _is_zero(_multiply(projection, homotopy)),
        "homotopy_inclusion_zero": _is_zero(_multiply(homotopy, iota)),
        "homotopy_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega64), _multiply(omega64, homotopy))),
        "q36_squared_zero": _is_zero(_multiply(q36, q36)),
        "q36_odd_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q36), omega36), _multiply(omega36, q36))),
        "Maxwell_rows_retained_by_identity": all(
            iota[54 + index][26 + index] == _one()
            and projection[26 + index][54 + index] == _one()
            and not homotopy[54 + index][54 + index].terms
            for index in range(10)
        ),
    }
    if checks != certificate["exact_checks"] or not all(checks.values()):
        raise AssertionError(f"independent exact check mismatch: {checks}")

    expected_pairs = {54: (63, 1), 63: (54, -1)}
    for component in range(4):
        expected_pairs[55 + component] = (59 + component, -1)
        expected_pairs[59 + component] = (55 + component, 1)
    for row, (column, sign) in expected_pairs.items():
        if omega64[row][column] != _one(sign):
            raise AssertionError("Maxwell odd-pairing sign drifted")
    if certificate["flags"]["MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO"] is not False:
        raise AssertionError("photon cohomology was contracted to zero")
    if certificate["flags"]["MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER"] is not False:
        raise AssertionError("local carrier was promoted to causal evidence")
    if certificate["flags"]["CLASSICAL_MAXWELL_CAUSAL_TRANSFER_DEPENDENCY_PINNED"] is not True:
        raise AssertionError("classical causal transfer dependency is not pinned")
    print("BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR independent replay: PASS")


if __name__ == "__main__":
    main()
