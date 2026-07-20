"""Independent verifier for candidate 18's complex singular resolution."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_complex_singular_resolution.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    x = sp.symbols("x0:10")
    minors = [x[i] * x[5 + j] - x[j] * x[5 + i] for i, j in combinations(range(5), 2)]
    jacobian = sp.Matrix(minors).jacobian(x)
    point = {value: 0 for value in x}
    point[x[0]] = 1
    assert jacobian.subs(point).rank() == 4
    assert jacobian.subs({value: 0 for value in x}).rank() == 0
    factor = payload["one_factor"]
    assert factor["complex_dimension"] == 6
    assert factor["singular_locus"] == "the vertex 0 only"
    complete = payload["complete_carrier"]
    assert complete["complex_dimension"] == 22
    assert complete["irreducible_singular_components"] == 2
    assert complete["component_complex_dimension"] == 16
    assert complete["intersection_complex_dimension"] == 10
    flags = payload["classification"]
    assert flags["ten_positive_spectators_retained"]
    assert not flags["fixed_occupation_real_singular_strata_classified"]
    assert not flags["lifted_rotation_singular_reduction_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_COMPLEX_SINGULAR_RESOLUTION verifier: PASS")


if __name__ == "__main__":
    verify()
