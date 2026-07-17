"""Independent algebraic verifier for the generic polar target operator."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_full_tensor.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_operator(l: sp.Symbol, k: sp.Symbol, w: sp.Symbol) -> sp.Matrix:
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


def _expression(value: str, local: dict[str, sp.Expr]) -> sp.Expr:
    # ``lambda`` is a Python keyword, so give it a parser-safe spelling.
    return sp.sympify(value.replace("lambda", "lam"), locals=local)


def _matrix(values: list[list[str]], local: dict[str, sp.Expr]) -> sp.Matrix:
    return sp.Matrix([[_expression(value, local) for value in row] for row in values])


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(SCHEMA)
    generator = ROOT / payload["provenance"]["generator_path"]
    assert payload["provenance"]["generator_sha256"] == _sha256(generator)
    for relative, digest in payload["provenance"]["engines"].items():
        assert digest == _sha256(ROOT / relative)
    for relative, digest in payload["provenance"]["inputs"].items():
        assert digest == _sha256(ROOT / relative)

    l, k, w = sp.symbols("lambda k omega", real=True)
    at, b, ct, u = sp.symbols("A_t B C_t U")
    local = {"lam": l, "k": k, "omega": w, "A_t": at, "B": b, "C_t": ct, "U": u, "I": sp.I}
    tensor = _matrix(payload["target_operator"]["tensor_matrix"], local)
    action = _matrix(payload["target_operator"]["action_matrix"], local)
    field_map = _matrix(payload["chain_square"]["target_field_map"], local)
    equation_map = _matrix(payload["chain_square"]["equation_row_map"], local)
    source = _source_operator(l, k, w)
    assert tensor.shape == (8, 4)
    assert (action - sp.diag(-1, 2, -1, 2 * l) * tensor[[0, 1, 2, 7], :]).applyfunc(sp.factor) == sp.zeros(4)
    assert (action - action.subs({w: -w, k: -k}, simultaneous=True).T).applyfunc(sp.factor) == sp.zeros(4)
    assert (action * field_map - equation_map * source).applyfunc(sp.factor) == sp.zeros(4, 5)
    assert all(sp.denom(value).is_number for value in equation_map)
    assert sp.Matrix([-tensor[0, column] + tensor[2, column] + 2 * tensor[5, column] for column in range(4)]).applyfunc(sp.factor) == sp.zeros(4, 1)

    p = w**2 - k**2 - l + sp.Rational(2, 3)
    q = (w**2 - k**2) ** 2 - 2 * l * (w**2 - k**2) + l * (l - 2)
    assert sp.factor(action.det()) == sp.factor(sp.Rational(9, 16) * l**3 * (l - 2) * p**2 * q)
    assert sp.factor(sp.resultant(p, q, w)) == sp.Rational(4, 81) * (9 * l - 2) ** 2

    coefficient_field = sp.QQ.frac_field(l, k)
    divisors = []
    for size in range(1, 5):
        gcd = None
        for rows in itertools.combinations(range(4), size):
            for columns in itertools.combinations(range(4), size):
                minor = sp.factor(action.extract(rows, columns).det())
                if minor == 0:
                    continue
                polynomial = sp.Poly(minor, w, domain=coefficient_field)
                gcd = polynomial if gcd is None else sp.polys.polytools.gcd(gcd, polynomial)
        assert gcd is not None
        divisors.append(sp.factor(gcd.monic().as_expr()))
    expected_divisors = [1, 1, p, sp.factor(p**2 * q)]
    assert all(sp.factor(actual - expected) == 0 for actual, expected in zip(divisors, expected_divisors))

    row_order = payload["row_order"]
    generic = {name: _expression(value, local) for name, value in payload["lambda_reconstruction"]["generic_rows"].items()}
    for sample in payload["samples"].values():
        physical_lambda = sample["lambda"]
        for name in row_order:
            direct = _expression(sample["rows"][name], local)
            assert sp.factor(direct - generic[name].subs(l, physical_lambda)) == 0


if __name__ == "__main__":
    verify_certificate()
