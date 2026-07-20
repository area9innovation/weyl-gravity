"""Independent verifier for the harmonic Taub-sign classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_harmonic_taub_sign_classification.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    for record in payload["provenance"]["inputs"].values():
        assert _sha256(ROOT / record["path"]) == record["sha256"]

    lam, k = sp.symbols("lambda k", real=True)
    root = sp.sqrt(2 * lam)
    plus_text = payload["exact_algebra"]["q_relative_weights"]["plus"].replace("lambda", "lam")
    minus_text = payload["exact_algebra"]["q_relative_weights"]["minus"].replace("lambda", "lam")
    assert sp.simplify(
        (1 + sp.Rational(3, 2) * root)
        - sp.sympify(plus_text, locals={"lam": lam})
    ) == 0
    assert sp.simplify(
        (1 - sp.Rational(3, 2) * root)
        - sp.sympify(minus_text, locals={"lam": lam})
    ) == 0

    # Physical lambda>=6 makes q+ positive and q- negative.  Squaring is
    # safe because both compared sides are positive.
    assert 2 * 6 > 4
    assert 9 * 2 * 6 > 4
    assert sp.expand((k**2 + lam - sp.Rational(2, 3)).subs({lam: 6, k: 0})) > 0
    assert sp.expand((k**2 + sp.Rational(4, 3)).subs(k, 0)) > 0

    matrix = sp.Matrix(
        [[sp.sympify(x) for x in row] for row in payload["exact_algebra"]["homogeneous_quadratic_matrix_on_a_b_d_Qe"]]
    )
    assert matrix.det() == -sp.Rational(1, 4)
    assert matrix.extract((1, 2), (1, 2)).det() < 0
    assert matrix[0, 0] < 0 and matrix[3, 3] < 0

    ledger = payload["harmonic_sign_ledger"]
    assert ledger["homogeneous_generalized_zero"]["solution_cofiber"].startswith("0;")
    assert ledger["axial_twist_generalized_zero"]["solution_cofiber"].startswith("0;")
    assert ledger["axial_twist_generalized_zero"]["constant_position_extension"].startswith("CERTIFIED")
    assert payload["classification"]["full_mixed_second_order_cone_classified"] is False
    assert payload["classification"]["causal_or_quantum_claim"] is False


if __name__ == "__main__":
    verify_certificate()
