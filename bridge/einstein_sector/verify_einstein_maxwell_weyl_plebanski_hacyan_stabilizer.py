"""Independent verifier for the Plebański--Hacyan stabilizer descent gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rotation_matrices(ell: int) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    magnetic = list(range(-ell, ell + 1))
    index = {m: position for position, m in enumerate(magnetic)}
    j_zero = sp.diag(*magnetic)
    j_plus = sp.zeros(2 * ell + 1)
    j_minus = sp.zeros(2 * ell + 1)
    for m in magnetic:
        if m < ell:
            j_plus[index[m + 1], index[m]] = ell - m
        if m > -ell:
            j_minus[index[m - 1], index[m]] = ell + m
    form = sp.diag(*[sp.Rational(1, sp.binomial(2 * ell, ell + m)) for m in magnetic])
    return j_zero, j_plus, j_minus, form


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    assert payload["provenance"]["generator_sha256"] == _sha256(ROOT / payload["provenance"]["generator_path"])
    for record in payload["provenance"]["inputs"].values():
        assert record["sha256"] == _sha256(ROOT / record["path"])

    for ell in range(2, 10):
        j_zero, j_plus, j_minus, form = _rotation_matrices(ell)
        assert j_zero * j_plus - j_plus * j_zero == j_plus
        assert j_zero * j_minus - j_minus * j_zero == -j_minus
        assert j_plus * j_minus - j_minus * j_plus == 2 * j_zero
        assert j_plus.T * form == form * j_minus
        assert j_zero.T * form == form * j_zero
        assert all(value > 0 for value in form.diagonal())

    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    p = frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3)
    mu = frequency**2 - momentum**2
    q = mu**2 - 2 * eigenvalue * mu + eigenvalue * (eigenvalue - 2)
    assert sp.factor(sp.resultant(p, q, frequency)) == sp.Rational(4, 81) * (9 * eigenvalue - 2) ** 2

    polar_path = ROOT / payload["provenance"]["inputs"]["polar_pairing"]["path"]
    polar = json.loads(polar_path.read_text(encoding="utf-8"))["shell_pairing"]
    gram = sp.Matrix(
        [[sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue, "k": momentum}) for value in row] for row in polar["extra_Hermitian_current_Gram"]]
    )
    determinant = sp.sympify(
        polar["extra_Gram_determinant"].replace("lambda", "lam"),
        locals={"lam": eigenvalue, "k": momentum},
    )
    assert sp.factor(gram.det() - determinant) == 0
    assert sp.factor(gram[0, 0]).subs({eigenvalue: 6, momentum: 0}) > 0
    assert sp.factor(determinant).subs({eigenvalue: 6, momentum: 0}) > 0

    classification = payload["classification"]
    assert classification["connected_background_stabilizer_certified"] is True
    assert classification["full_SO42_stabilizer_rejected"] is True
    assert classification["universal_stabilizer_nullity_refuted"] is True
    assert classification["absolute_residual_gauge_quotient_certified"] is False
    assert classification["cyclic_BV_enhancement_certified"] is False
    assert payload["residual_dispositions"]["stabilizers_gauged_in_an_absolute_CE_complex"] == "NOT_AUTHORIZED"
    assert payload["verification_receipt"]["tier_0"]["status"] == "PASS"
    assert payload["verification_receipt"]["tier_1"]["status"] == "PASS"


if __name__ == "__main__":
    verify_certificate()
