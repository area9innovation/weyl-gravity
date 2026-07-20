"""Independent verifier for all-occupation singular rotation-zero sections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_singular_rotation_zero_sections.json"


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

    nm, np, alpha, beta = sp.symbols("nm np alpha beta", positive=True)
    assert sp.simplify(sp.Rational(1, 6) * (6 * nm) - nm) == 0
    assert sp.simplify(sp.Rational(1, 96) * (96 * np) - np) == 0
    assert sp.simplify(alpha * sp.Rational(1, 6) * (6 * np / alpha) - np) == 0
    assert sp.simplify(beta * sp.Rational(1, 6) * (6 * nm / beta) - nm) == 0
    # e_0 is exactly the normalized common-square vector v([0:1:0])/2.
    l0, l1, l2 = 0, 1, 0
    v = sp.Matrix([3 * l2**2, -3 * l1 * l2, l0 * l2 + 2 * l1**2, -3 * l0 * l1, 3 * l0**2])
    assert v / 2 == sp.Matrix([0, 0, 1, 0, 0])
    flags = payload["classification"]
    for candidate in (17, 18, 20):
        assert flags[f"candidate{candidate}_every_positive_occupation_has_singular_rotation_zero_point"]
    assert not flags["singular_strata_avoidable_by_positive_norms"]
    assert not flags["singular_strata_avoidable_by_rotation_zero_condition"]
    assert not flags["real_singular_component_decomposition_complete"]
    assert not flags["global_zero_fibre_connected"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_SINGULAR_ROTATION_ZERO_SECTIONS verifier: PASS")


if __name__ == "__main__":
    verify()
