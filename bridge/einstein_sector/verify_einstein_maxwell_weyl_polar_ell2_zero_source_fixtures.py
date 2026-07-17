"""Independent algebraic verifier for the five direct polar zero-source fixtures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell2_zero_source_fixture.schema.json"
GENERATOR = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_ell2_zero_source_fixture.py"
CASES = ("plus", "minus", "extra_e1", "extra_e2", "extra_cross")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_fixtures() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    records = {}
    for case in CASES:
        path = ROOT / f"bridge/certificates/einstein_maxwell_weyl_polar_ell2_{case}_zero_source_fixture.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(payload)
        assert payload["schema_sha256"] == _sha256(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == _sha256(GENERATOR)
        assert payload["case"] == case
        records[case] = [sp.sympify(value) for value in payload["homogeneous_source_rows_E00_E11_E22_Maxwell1"]]

    diagonal = sp.Matrix.hstack(*(sp.Matrix(records[name]) for name in ("plus", "minus", "extra_e1", "extra_e2")))
    assert diagonal.rank() == 1
    for source in (records[name] for name in ("plus", "minus", "extra_e1", "extra_e2")):
        assert source[1] == 0 and source[3] == 0
        assert sp.simplify(2 * source[2] - source[0]) == 0
    assert records["extra_cross"] == [0, 0, 0, 0]
    root = sp.sqrt(3)
    assert sp.simplify(records["minus"][0] - records["plus"][0].xreplace({root: -root})) == 0


if __name__ == "__main__":
    verify_fixtures()
