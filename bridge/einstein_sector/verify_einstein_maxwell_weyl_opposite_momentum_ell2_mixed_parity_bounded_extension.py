"""Independent verifier for the tuned mixed-parity bounded extension."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for entry in payload["provenance"]["inputs"].values():
        path = ROOT / entry["path"]
        assert entry["sha256"] == _sha256(path)

    root = sp.sqrt(3)
    k_squared = 2 * root - sp.Rational(7, 6)
    minus_squared = sp.Rational(29, 6)
    plus_squared = minus_squared + 4 * root
    minus = sp.sqrt(minus_squared)
    plus = sp.sqrt(plus_squared)
    frequency_squares = {
        "zero": sp.Integer(0),
        "two_omega_minus": 4 * minus_squared,
        "two_omega_plus": 4 * plus_squared,
        "omega_plus_plus_omega_minus": sp.expand((plus + minus) ** 2),
        "omega_plus_minus_omega_minus": sp.expand((plus - minus) ** 2),
    }
    momentum_squares = {"K_zero": sp.Integer(0), "K_two_k": 4 * k_squared}
    collisions: list[tuple[str, str, int, str]] = []
    exact_rows = payload["collision_census"]["checks"]
    assert len(exact_rows) == 80
    x = sp.Symbol("x")
    for row in exact_rows:
        frequency = frequency_squares[row["frequency"]]
        momentum = momentum_squares[row["momentum"]]
        ell = row["ell"]
        if ell == 1:
            residual = frequency - momentum - (4 if row["target"] == "exceptional_four" else sp.Rational(4, 3))
        else:
            eigenvalue = ell * (ell + 1)
            if row["target"] == "p":
                residual = frequency - momentum - eigenvalue + sp.Rational(2, 3)
            else:
                residual = (frequency - momentum - eigenvalue) ** 2 - 2 * eigenvalue
        collision = residual.equals(0) is True
        assert row["collision"] is collision
        if collision:
            collisions.append((row["frequency"], row["momentum"], ell, row["target"]))
        else:
            witness = row["nonzero_witness"]
            assert sp.simplify(sp.sympify(witness["residual"]) - residual) == 0
            minimal = sp.Poly(sp.minpoly(residual, x), x)
            assert minimal.nth(0) != 0
            assert sp.sympify(witness["minimal_polynomial_constant"]) != 0
    assert collisions == [("two_omega_minus", "K_zero", 4, "p")]

    null_face = payload["declared_tangent"]["Einstein_minus_raw_coefficients"]
    assert "sqrt(3)" in null_face and "p_+=p_-=1" in null_face
    proof = payload["bounded_blockwise_proof"]
    assert "stab^*" in proof["wave_wave_zero_block"]
    assert proof["unique_collision"] == "L=4,K=0,Omega=2omega_- on the p-primary"
    assert payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    flags = payload["classification"]
    assert flags["one_nonzero_tuned_bounded_second_order_tangent_certified"] is True
    assert flags["general_mixed_null_face_classified"] is False
    assert flags["causal_or_quantum_claim"] is False
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_MIXED_PARITY_BOUNDED_EXTENSION independent verification: PASS")


if __name__ == "__main__":
    main()
