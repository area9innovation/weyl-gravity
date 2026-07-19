#!/usr/bin/env python3
"""Independently verify the apparatus scalar-BV q2 PBW block."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_apparatus_scalar_bv_q2_pbw import (
    APPARATUS_PAIRS, CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA,
    canonical_sha256, clone_term, pairing_isometry_audit, scalar_template,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    template = scalar_template()
    assert len(template) == 24
    all_terms = []
    for block, (field, dual) in zip(value["payload"]["blocks"], APPARATUS_PAIRS, strict=True):
        expected = [clone_term(term, field, dual) for term in template]
        assert block["terms"] == expected
        assert block["canonical_sha256"] == canonical_sha256(expected)
        all_terms.extend(expected)
    assert value["payload"]["terms"] == all_terms
    assert value["payload"]["canonical_sha256"] == canonical_sha256(all_terms)
    assert pairing_isometry_audit(value["payload"]) == value["pairing_and_cyclicity_audit"]
    print("BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
