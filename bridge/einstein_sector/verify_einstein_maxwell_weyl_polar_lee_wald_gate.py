"""Independent fast verifier for the polar Lee--Wald gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_lee_wald_gate.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expr(value, local) for value in row] for row in values])


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == _sha256(generator)
    for relative, digest in payload["provenance"]["inputs"].items():
        assert digest == _sha256(ROOT / relative)

    l, k, w1, w2 = sp.symbols("lambda k omega_1 omega_2", real=True)
    local = {"lam": l, "k": k, "omega_1": w1, "omega_2": w2, "I": sp.I, "pi": sp.pi}
    generic = _matrix(payload["direct_Lee_Wald_match"]["generic_action_current_per_scalar_harmonic_norm"], local)
    expected = sp.Matrix([
        [0, -sp.I * k * (k**2 + l) / 2, -sp.I * (2 * k**2 - l) * (w1 + w2) / 8, 0],
        [-sp.I * k * (k**2 + l) / 2, -sp.I * (4 * k**2 + 3 * l) * (w1 + w2) / 4, sp.I * k * (l - w1**2 - w1 * w2 - w2**2) / 2, 0],
        [-sp.I * (2 * k**2 - l) * (w1 + w2) / 8, sp.I * k * (l - w1**2 - w1 * w2 - w2**2) / 2, sp.I * (w1 + w2) * (2 * l - w1**2 - w2**2) / 4, 0],
        [0, 0, 0, -sp.I * l * (w1 + w2)],
    ])
    assert (generic - expected).applyfunc(sp.factor) == sp.zeros(4)
    degree_audit = payload["direct_Lee_Wald_match"]["spectral_interpolation"]
    actual_degrees = []
    for value in generic:
        if value != 0:
            assert sp.denom(sp.cancel(value)).is_number
            actual_degrees.append(sp.Poly(sp.expand(value), l).degree())
    assert max(actual_degrees) == degree_audit["generic_action_current_maximum_lambda_degree"]
    assert max(actual_degrees) <= degree_audit["direct_natural_current_degree_in_lambda_at_most"]
    for sample in payload["direct_Lee_Wald_match"]["samples"]:
        ell = sample["ell"]
        norm = 4 * sp.pi / (2 * ell + 1)
        direct = _matrix(sample["entrywise_sparse_direct_matrix"], local)
        assert (direct - norm * expected.subs(l, ell * (ell + 1))).applyfunc(sp.factor) == sp.zeros(4)
        assert _matrix(sample["direct_minus_action_Green_remainder"], local) == sp.zeros(4)

    gram = _matrix(payload["shell_pairing"]["extra_Hermitian_current_Gram"], local)
    determinant = sp.factor(gram.det())
    expected_determinant = 9 * l**2 * (l - 2) * (9 * l - 2) * (3 * k**2 + 3 * l - 2) * (6 * k**2 + 3 * l - 2) ** 2
    assert sp.factor(determinant - expected_determinant) == 0
    assert payload["shell_pairing"]["extra_Gram_determinant"] == str(expected_determinant)
    assert sp.factor(gram[0, 0]) == 18 * l * (4 * k**2 + l - 2) * (12 * k**2 + 9 * l - 2)
    assert payload["shell_pairing"]["Einstein_extra_mixed_remainder_mod_p_q"] == ["0", "0"]
    assert payload["shell_pairing"]["extra_positive_frequency_inertia"] == [2, 0]
    assert payload["shell_pairing"]["complete_polar_target_inertia_before_residual_quotient"] == [3, 1]
    assert payload["classification"]["final_residual_descent_certified"] is False
    assert payload["classification"]["quantum_norm_or_ghost_theorem"] is False
    receipt = payload["verification_receipt"]
    assert receipt["tier_0"]["status"] == "PASS"
    assert receipt["tier_1"]["status"] == "PASS"
    assert receipt["tier_2"]["status"] == "PASS"
    assert receipt["tier_2"]["elapsed_seconds"] == sum(receipt["tier_2"]["per_sample_elapsed_seconds"].values())
    assert receipt["tier_3"]["status"] == "NOT_RUN"


if __name__ == "__main__":
    verify_certificate()
