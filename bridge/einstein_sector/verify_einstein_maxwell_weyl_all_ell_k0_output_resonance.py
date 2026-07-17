"""Independent verifier for the all-ell k=0 output-resonance theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_all_ell_k0_output_resonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_all_ell_k0_output_resonance.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]

    n, lam, capital_lambda, z = sp.symbols("ell lambda Lambda z", integer=True, positive=True)
    physical_lam = n * (n + 1)
    p_target = z - (capital_lambda - sp.Rational(2, 3))
    q_target = (z - capital_lambda) ** 2 - 2 * capital_lambda
    double_einstein = 3 * z - 12 * lam + 8
    double_extra = z**2 - 8 * lam * z + 16 * lam**2 - 32 * lam
    einstein_pair = z**2 - 4 * lam * z + 8 * lam
    mixed = (
        81 * z**4
        + (216 - 648 * lam) * z**3
        + (1296 * lam**2 - 1188 * lam + 216) * z**2
        + (-1296 * lam**2 + 1008 * lam + 96) * z
        + 324 * lam**2 - 144 * lam + 16
    )

    checks = [
        (double_einstein, 2 * n, 6 * (n - 1), -4 * (9 * n**2 + 33 * n - 16)),
        (double_extra, 2 * n - 1, sp.Rational(4, 9) * (9 * n**2 - 54 * n + 1), -144 * n**2 * (n - 1) * (7 * n + 9)),
        (einstein_pair, 2 * n, -sp.Rational(4, 9) * (18 * n**3 - 3 * n**2 - 18 * n - 1), -16 * n**2 * (n + 1) * (4 * n**3 + 12 * n**2 - 9 * n - 9)),
    ]
    for polynomial, output_ell, expected_p, expected_q in checks:
        polynomial = polynomial.subs(lam, physical_lam)
        target_lambda = sp.expand(output_ell * (output_ell + 1))
        assert sp.factor(sp.resultant(polynomial, p_target.subs(capital_lambda, target_lambda), z) - expected_p) == 0
        assert sp.factor(sp.resultant(polynomial, q_target.subs(capital_lambda, target_lambda), z) - expected_q) == 0

    top_lambda = (2 * n) * (2 * n + 1)
    mixed = mixed.subs(lam, physical_lam)
    mixed_top_p = sp.factor(sp.resultant(mixed, p_target.subs(capital_lambda, top_lambda), z))
    mixed_top_q = sp.factor(sp.resultant(mixed, q_target.subs(capital_lambda, top_lambda), z))
    recorded_top = payload["candidate_resultants"]["extra_minus_einstein_sum_at_2ell"]
    assert str(mixed_top_p) == recorded_top["p_resultant"]
    assert str(mixed_top_q) == recorded_top["q_resultant"]
    assert all(sp.Rational(value) > 0 for value in recorded_top["p_core_shift_ell_minus_2_coefficients"])
    assert all(sp.Rational(value) > 0 for value in recorded_top["q_core_shift_ell_minus_2_coefficients"])

    finite = payload["candidate_resultants"]["extra_minus_einstein_sum_at_2ell_minus_1"]["exact_finite_values"]
    assert set(finite) == {str(value) for value in range(2, 8)}
    assert all(int(record["p_resultant"]) != 0 and int(record["q_resultant"]) != 0 for record in finite.values())
    classification = payload["classification"]
    assert classification["all_nonzero_output_channels_off_physical_target_shells"]
    assert not classification["zero_frequency_source_cokernel_classified"]


if __name__ == "__main__":
    verify_certificate()
