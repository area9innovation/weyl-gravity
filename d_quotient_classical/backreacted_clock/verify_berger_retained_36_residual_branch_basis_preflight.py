#!/usr/bin/env python3
"""Independent replay of the retained branch-basis input preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
from sympy import QQ, sqrt
from sympy.polys.polyerrors import CoercionFailed


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-36-residual-branch-basis-preflight-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(cert)
    for ref in cert["dependency_refs"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drift: {ref['path']}")
    for ref in cert["provenance"]["source_manifest"]:
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"source drift: {ref['path']}")
    try:
        QQ.algebraic_field(sqrt(10)).from_sympy(sqrt(2))
    except CoercionFailed:
        pass
    else:
        raise AssertionError("sqrt(2) unexpectedly entered Q(sqrt(10))")
    field = cert["field_obstruction"]
    if field["declared_field"] != "Q(sqrt(10))" or field["sqrt2_is_member_of_declared_field"] is not False:
        raise AssertionError("field obstruction drifted")
    checks = cert["even_odd_matrix_receipt"]["exact_checks"]
    if not all(checks.values()):
        raise AssertionError("even/odd matrix receipt failed")
    flags = cert["flags"]
    for key in ("RETAINED_36_Q1_AVAILABLE", "RETAINED_36_TYPED_PAIRING_AVAILABLE", "RETAINED_MIXED_ELL3_AVAILABLE"):
        if flags[key] is not True:
            raise AssertionError(f"available input dropped: {key}")
    for key in ("CURRENT_INPUT_SCHEMA_FIELD_CONSISTENT_WITH_NORMALIZED_EO_BASIS", "DYNAMICAL_BRANCH_PROJECTOR_AVAILABLE", "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V1_READY", "ELL3_BRANCH_PROJECTION_AUTHORIZED", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise AssertionError(f"forbidden promotion: {key}")
    print("BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_PREFLIGHT independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
