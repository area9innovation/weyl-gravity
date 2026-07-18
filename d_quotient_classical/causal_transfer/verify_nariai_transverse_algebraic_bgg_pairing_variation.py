#!/usr/bin/env python3
"""Independent adjoint replay for transverse algebraic BGG data."""

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

from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import fixture


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-algebraic-bgg-pairing-variation-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(record: dict) -> sp.Matrix:
    value = sp.zeros(*record["shape"])
    for row, column, coefficient in record["entries"]:
        value[row, column] = sp.Rational(coefficient)
    return value


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    data = fixture()["algebraic"]
    correction = _matrix(payload["exact_data"]["incidence_correction"])
    dual = _matrix(payload["exact_data"]["formal_adjoint_dual"])
    expected = data.adjoint_pairing.inv() * correction.T * data.one_form_pairing
    if dual != expected or data.adjoint_pairing * dual != correction.T * data.one_form_pairing:
        raise AssertionError("independent formal adjoint failed")
    if dual.rank() != 4:
        raise AssertionError("dual rank drifted")
    for record in payload["dependency_refs"].values():
        path = ROOT / record["path"]
        if not path.is_file() or _sha(path) != record["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {record['path']}")
        if "result_id" in record and json.loads(path.read_text())["result_id"] != record["result_id"]:
            raise AssertionError(f"dependency id mismatch: {record['path']}")
    for record in payload["exact_data"]["algebraic_maps"].values():
        if _matrix(record["first_variation"]) != sp.zeros(*record["first_variation"]["shape"]):
            raise AssertionError("algebraic variation is nonzero")
    for record in payload["exact_data"]["fibre_pairings"].values():
        if _matrix(record["first_variation"]) != sp.zeros(*record["first_variation"]["shape"]):
            raise AssertionError("pairing variation is nonzero")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source hash mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1 independent verification: PASS")
