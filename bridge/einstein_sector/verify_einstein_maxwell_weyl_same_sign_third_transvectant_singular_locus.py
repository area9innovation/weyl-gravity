"""Independent exact verifier for the third-transvectant singular locus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json"


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

    x, y, z = sp.symbols("x y z")
    B = sp.Matrix(
        [
            [0, 0, 0, -x, -y],
            [0, 0, 3 * x, 2 * y, -z],
            [0, -3 * x, 0, 3 * z, 0],
            [x, -2 * y, -3 * z, 0, 0],
            [y, z, 0, 0, 0],
        ]
    )
    v = sp.Matrix([3 * z**2, -3 * y * z, x * z + 2 * y**2, -3 * x * y, 3 * x**2])
    assert B.T == -B
    assert B.det() == 0
    assert sp.simplify(B * v) == sp.zeros(5, 1)
    assert sp.factor(B[:4, :4].det()) == 9 * x**4
    assert sp.factor(B[1:, 1:].det()) == 9 * z**4
    assert sp.factor(B.extract((0, 1, 3, 4), (0, 1, 3, 4)).det()) == (x * z + 2 * y**2) ** 2
    one = payload["one_factor_singular_locus"]
    assert one["complex_dimension"] == 4
    assert one["projectivization"] == "P^2 x P^1 embedded by O(2,1)"
    product = payload["two_parity_product"]
    assert product["ambient_complex_dimension"] == 14
    assert product["irreducible_components"] == 2
    assert product["component_complex_dimension"] == 11
    assert product["intersection_complex_dimension"] == 8
    flags = payload["classification"]
    assert flags["candidate17_complete_complex_singular_locus_classified"]
    assert flags["candidate20_complete_complex_singular_locus_classified"]
    assert not flags["fixed_occupation_real_singular_strata_classified"]
    assert not flags["lifted_rotation_singular_reduction_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_THIRD_TRANSVECTANT_SINGULAR_LOCUS verifier: PASS")


if __name__ == "__main__":
    verify()
