"""Independent verifier for the fixed-ell k=0 combined cone theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]

    c, k, omega, lam, g0, g1 = sp.symbols("c k omega lambda g0 g1", real=True)
    s = omega**2 - k**2 / (1 + c)
    volume_gram = sp.sqrt(1 + c) * (g0 + g1 * c)
    p = s - lam + sp.Rational(2, 3)
    q = (s - lam) ** 2 - 2 * lam
    p_pressure = sp.factor(sp.diff(volume_gram * p, c).subs(c, 0))
    q_pressure = sp.factor(sp.diff(volume_gram * q, c).subs(c, 0))
    assert sp.factor(p_pressure.subs({k: 0, omega**2: lam - sp.Rational(2, 3)})) == 0
    assert sp.factor(q_pressure.subs({k: 0, omega**2: lam + sp.sqrt(2 * lam)})) == 0
    assert sp.factor(q_pressure.subs({k: 0, omega**2: lam - sp.sqrt(2 * lam)})) == 0

    L = sp.symbols("L", integer=True, positive=True)
    capital_lambda = L * (L + 1)
    assert sp.factor(-capital_lambda + sp.Rational(2, 3)) != 0
    q_zero = sp.factor(capital_lambda * (capital_lambda - 2))
    assert all(value > 0 for value in sp.Poly(sp.expand(q_zero.subs(L, L + 2)), L).all_coeffs())

    fixture = payload["exact_ell3_fixture"]
    assert fixture["E00_source_matrix"] == [["-73440/7", "0"], ["0", "-7208/63"]]
    assert fixture["sphere_trace_source_matrix"] == [["-36720/7", "0"], ["0", "-3604/63"]]
    assert fixture["ell2_direct_calibration_remainder"] == [["0", "0"], ["0", "0"]]
    classification = payload["classification"]
    assert classification["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"]
    assert not classification["cross_ell_superpositions_classified"]


if __name__ == "__main__":
    verify_certificate()
