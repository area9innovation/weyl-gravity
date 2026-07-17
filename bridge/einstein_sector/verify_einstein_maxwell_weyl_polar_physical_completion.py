"""Independent verifier for the polar physical-ring completion."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_physical_completion.schema.json"
OPERATOR = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expr(value, local) for value in row] for row in values])


def _source(l: sp.Symbol, k: sp.Symbol, w: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([
        [0, 0, l / 2, k**2 + l / 2, -l],
        [0, l / 2, 0, -k * w, 0],
        [l / 2, 0, 0, w**2 - l / 2, l],
        [0, sp.I * k / 2, sp.I * w / 2, sp.I * w / 2, -sp.I * w],
        [sp.I * k / 2, sp.I * w / 2, 0, -sp.I * k / 2, sp.I * k],
        [(k**2 + l / 2) / 2, k * w, (w**2 - l / 2) / 2, (w**2 - k**2 + 2) / 2, -l],
        [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 0, 0],
        [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, w**2 - k**2 - l],
    ])


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    operator = json.loads(OPERATOR.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == _sha256(generator)
    for relative, digest in payload["provenance"]["inputs"].items():
        assert digest == _sha256(ROOT / relative)

    l, k, w = sp.symbols("lambda k omega", real=True)
    local = {"lam": l, "k": k, "omega": w, "I": sp.I}
    tensor = _matrix(operator["target_operator"]["tensor_matrix"], local)
    hessian = _matrix(operator["target_operator"]["action_matrix"], local)
    field_map = _matrix(operator["chain_square"]["target_field_map"], local)
    equation_map = _matrix(operator["chain_square"]["equation_row_map"], local)
    assert (hessian - sp.diag(-1, 2, -1, 2 * l) * tensor[[0, 1, 2, 7], :]).applyfunc(sp.factor) == sp.zeros(4)
    assert (hessian * field_map - equation_map * _source(l, k, w)).applyfunc(sp.factor) == sp.zeros(4, 5)

    theta = sp.symbols("theta", real=True)
    for record in payload["action_normalization"]["direct_Legendre_checks"]:
        ell = record["ell"]
        harmonic = sp.legendre(ell, sp.cos(theta))
        scalar = sp.integrate(sp.sin(theta) * harmonic**2, (theta, 0, sp.pi))
        axial = sp.integrate(sp.sin(theta) * sp.diff(harmonic, theta) ** 2, (theta, 0, sp.pi))
        assert sp.simplify(axial - ell * (ell + 1) * scalar) == 0
        assert str(scalar) == record["scalar_norm_without_2pi"]
        assert str(axial) == record["axial_one_form_norm_without_2pi"]

    p = w**2 - k**2 - l + sp.Rational(2, 3)
    q = (w**2 - k**2) ** 2 - 2 * l * (w**2 - k**2) + l * (l - 2)
    audit = payload["physical_ring"]
    assert hessian[0, 3] == l
    i2 = audit["I2_Bezout_witness"]
    i2_generators = []
    for (rows, columns), stored in zip(i2["minor_labels"], i2["normalized_generators"]):
        actual = sp.factor(hessian.extract(rows, columns).det() / l)
        assert sp.factor(actual - _expr(stored, local)) == 0
        i2_generators.append(actual)
    i2_coefficients = [_expr(value, local) for value in i2["coefficients"]]
    assert sp.factor(sum(c * g for c, g in zip(i2_coefficients, i2_generators)) - _expr(i2["unit_target"], local)) == 0

    i3 = audit["I3_Bezout_witness"]
    i3_generators = []
    for (rows, columns), stored in zip(i3["minor_labels"], i3["normalized_generators"]):
        actual = sp.factor(hessian.extract(rows, columns).det() / (3 * l**2 * p))
        assert sp.factor(actual - _expr(stored, local)) == 0
        i3_generators.append(actual)
    i3_coefficients = [_expr(value, local) for value in i3["coefficients"]]
    assert sp.factor(sum(c * g for c, g in zip(i3_coefficients, i3_generators)) - _expr(i3["unit_target"], local)) == 0
    nonzero_three = 0
    for rows in itertools.combinations(range(4), 3):
        for columns in itertools.combinations(range(4), 3):
            minor = sp.factor(hessian.extract(rows, columns).det())
            if minor != 0:
                nonzero_three += 1
                assert sp.denom(sp.cancel(minor / p)).is_number
    assert nonzero_three == i3["number_nonzero_three_minors"]
    assert sp.factor(hessian.det()) == sp.factor(sp.Rational(9, 16) * l**3 * (l - 2) * p**2 * q)
    assert sp.factor(sp.resultant(p, q, w)) == sp.Rational(4, 81) * (9 * l - 2) ** 2

    zero = audit["zero_momentum_audit"]
    representatives = _matrix(zero["extra_representatives_order_At_B_Ct_U"], local)
    coefficient_field = sp.QQ.frac_field(l)
    shell = sp.Poly(p.subs(k, 0), w, domain=coefficient_field)
    for value in hessian.subs(k, 0) * representatives:
        assert sp.rem(sp.Poly(value, w, domain=coefficient_field), shell).is_zero
    assert sp.factor(representatives[[1, 3], :].det() - 3 * (3 * l - 2)) == 0

    master = sp.Matrix([[w**2 - k**2 - l, 2 * l], [1, w**2 - k**2 - l]])
    assert sp.factor(master.det() - q) == 0
    assert payload["Einstein_primary_image"]["source_module_K_dimension"] == 4
    assert payload["Einstein_primary_image"]["target_q_primary_K_dimension"] == 4
    assert payload["Einstein_primary_image"]["Einstein_image_equals_complete_q_primary_summand"] is True


if __name__ == "__main__":
    verify_certificate()
