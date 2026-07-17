#!/usr/bin/env python3
"""Independent exact replay of the explicit typed 64/36 carrier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock.berger_portable_coupled_64_unary_pairing_sdr import (
    _add, _adjoint, _identity, _is_zero, _multiply, _one, _subtract,
)
from d_quotient_classical.backreacted_clock.verify_berger_portable_coupled_64_unary_pairing_sdr import (
    _parse_record,
)

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-portable-coupled-64-typed-pairing-36-sdr-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for source in value["dependency_refs"].values():
        if _sha256(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"dependency hash drifted: {source['path']}")
    for relative, digest in value["source_manifest"].items():
        if _sha256(ROOT / relative) != digest:
            raise AssertionError(f"source hash drifted: {relative}")

    full, retained, contraction = value["full_complex"], value["retained_complex"], value["contraction"]
    q64 = _parse_record(full["classical_unary_q1"], (64, 64), "q64")
    omega64 = _parse_record(full["typed_cyclic_pairing"], (64, 64), "omega64")
    scale64 = _parse_record(full["typing_scale"], (64, 64), "scale64")
    q36 = _parse_record(retained["classical_unary_q1"], (36, 36), "q36")
    omega36 = _parse_record(retained["typed_cyclic_pairing"], (36, 36), "omega36")
    scale36 = _parse_record(retained["typing_scale"], (36, 36), "scale36")
    iota = _parse_record(contraction["iota_36_to_64"], (64, 36), "iota")
    projection = _parse_record(contraction["pi_64_to_36"], (36, 64), "projection")
    homotopy = _parse_record(contraction["S_64"], (64, 64), "homotopy")
    checks = {
        "typed_pairing64_antisymmetric": _is_zero(_add(_adjoint(omega64), omega64)),
        "typed_pairing36_antisymmetric": _is_zero(_add(_adjoint(omega36), omega36)),
        "q64_typed_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q64), omega64), _multiply(omega64, q64))),
        "q36_typed_pairing_cyclic": _is_zero(_add(_multiply(_adjoint(q36), omega36), _multiply(omega36, q36))),
        "typed_pairing_induced_by_iota": _is_zero(_subtract(_multiply(_multiply(_adjoint(iota), omega64), iota), omega36)),
        "pi_iota_identity": _is_zero(_subtract(_multiply(projection, iota), _identity(36))),
        "contraction_identity": _is_zero(_subtract(_add(_multiply(q64, homotopy), _multiply(homotopy, q64)), _subtract(_identity(64), _multiply(iota, projection)))),
        "homotopy_typed_cyclic": _is_zero(_add(_multiply(_adjoint(homotopy), omega64), _multiply(omega64, homotopy))),
        "scale_intertwines_iota": _is_zero(_subtract(_multiply(scale64, iota), _multiply(iota, scale36))),
        "scale_intertwines_projection": _is_zero(_subtract(_multiply(projection, scale64), _multiply(scale36, projection))),
    }
    if checks != value["exact_checks"] or not all(checks.values()):
        raise AssertionError(f"typed carrier checks failed: {checks}")
    for index in range(54):
        if scale64[index][index] != _one(): raise AssertionError("gravity scale drifted")
    for index in range(54, 64):
        if scale64[index][index] != _one(2): raise AssertionError("Maxwell scale drifted")
    if value["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] or value["flags"]["QUANTUM_CLAIM"]:
        raise AssertionError("typed carrier overclaim")


if __name__ == "__main__":
    verify()
    print("BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR independent replay: PASS")
