#!/usr/bin/env python3
"""Verify the nonlinear source/transfer dictionary and cone invariance law."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nonlinear-source-transfer-tangent-cone-dictionary-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/nonlinear-source-transfer-tangent-cone-dictionary.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_nonlinear_source_transfer_tangent_cone_dictionary.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_nonlinear_source_transfer_tangent_cone_dictionary.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_fixture() -> dict[str, object]:
    """Audit the Hessian/cokernel transformation law over exact rationals."""

    a = sp.symbols("a")
    L = sp.Matrix([[1, 0], [0, 0]])
    T = sp.diag(2, 3)
    U = sp.diag(7, 11)
    u = sp.Matrix([0, a])
    source_at_Tu = sp.Matrix([9 * a**2, 18 * a**2])
    coordinate_hessian = sp.Matrix([5 * a**2, 13 * a**2])
    transformed_source = U * (source_at_Tu + L * coordinate_hessian)
    cokernel = sp.Matrix([[0, 1]])
    transformed_cokernel = cokernel * U.inv()
    original_obstruction = sp.expand((cokernel * source_at_Tu)[0])
    transformed_obstruction = sp.expand((transformed_cokernel * transformed_source)[0])
    if L * T * u != sp.zeros(2, 1):
        raise AssertionError("linear field map did not preserve the tangent kernel")
    if transformed_obstruction != original_obstruction or original_obstruction != 18 * a**2:
        raise AssertionError("cokernel obstruction transformation law failed")
    return {
        "L": [[int(value) for value in row] for row in L.tolist()],
        "T": [[int(value) for value in row] for row in T.tolist()],
        "U": [[int(value) for value in row] for row in U.tolist()],
        "coordinate_hessian": [str(value) for value in coordinate_hessian],
        "original_obstruction": str(original_obstruction),
        "transformed_obstruction": str(transformed_obstruction),
        "zero_locus": "a=0 over characteristic zero",
    }


def validate(value: Mapping[str, object], *, verify_sources: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["exact_fixture"] != exact_fixture():
        raise ValueError("exact transformation fixture drifted")
    if verify_sources:
        for relative, digest in value["dependency_refs"].items():
            if _sha(ROOT / relative) != digest:
                raise ValueError(f"dependency digest drifted: {relative}")
        for relative, digest in value["source_manifest"].items():
            if _sha(ROOT / relative) != digest:
                raise ValueError(f"source digest drifted: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-source-check", action="store_true")
    args = parser.parse_args()
    value = json.loads(OUTPUT.read_text())
    validate(value, verify_sources=not args.no_source_check)
    print(f"{value['result_id']} verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
