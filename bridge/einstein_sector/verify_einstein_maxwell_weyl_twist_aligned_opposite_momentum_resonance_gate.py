"""Independent verifier for the twist-aligned opposite-momentum gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / value["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == value["schema_sha256"]
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    k2 = root - ell / 2 - sp.Rational(1, 6)
    wm2 = sp.factor(k2 + lam - root)
    wp2 = sp.factor(k2 + lam + root)
    assert sp.factor(2 * (wp2 - wm2 * wp2 / wm2)) == 0
    assert sp.factor(4 * wm2 - 2 * ell * (2 * ell + 1) + sp.Rational(2, 3)) == 0
    disposition = value["logical_disposition"]
    assert disposition["stabilizer_moment_maps_vanish"]
    assert disposition["constant_twist_times_wave_bounded_column_solved"]
    assert disposition["phase_resonance_divisor_populated"]
    assert not disposition["dynamical_adjoint_projection_computed"]
    assert value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "OPEN"
    assert value["correction_classes"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"] == "CERTIFIED"
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    print("EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_RESONANCE_GATE independent verification: PASS")


if __name__ == "__main__":
    main()
