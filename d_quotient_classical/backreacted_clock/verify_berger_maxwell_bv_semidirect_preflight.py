#!/usr/bin/env python3
"""Independent replay of the Berger Maxwell BV semidirect preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-maxwell-bv-semidirect-preflight-v1.schema.json"


def _clean(expression: sp.Expr) -> sp.Expr:
    return sp.simplify(sp.expand(expression))


def _vector(prefix: str, x: tuple[sp.Symbol, ...]) -> list[sp.Expr]:
    return [sp.Function(f"{prefix}{index}")(*x) for index in range(4)]


def _bracket(left, right, x):
    return [
        sum(left[index] * sp.diff(right[component], x[index]) - right[index] * sp.diff(left[component], x[index]) for index in range(4))
        for component in range(4)
    ]


def _lie_scalar(vector, scalar, x):
    return sum(vector[index] * sp.diff(scalar, x[index]) for index in range(4))


def _lie_one(vector, form, x):
    return [
        sum(vector[index] * sp.diff(form[component], x[index]) + form[index] * sp.diff(vector[index], x[component]) for index in range(4))
        for component in range(4)
    ]


def _transform(vector, gauge, form, x):
    lie = _lie_one(vector, form, x)
    return [lie[index] + sp.diff(gauge, x[index]) for index in range(4)]


def _field(form, x):
    return {
        (first, second): sp.diff(form[second], x[first]) - sp.diff(form[first], x[second])
        for first in range(4)
        for second in range(first + 1, 4)
    }


def _two_component(form, first, second):
    if first == second:
        return sp.S.Zero
    return form[(first, second)] if first < second else -form[(second, first)]


def _lie_two(vector, form, x):
    return {
        (first, second): sum(
            vector[index] * sp.diff(_two_component(form, first, second), x[index])
            + _two_component(form, index, second) * sp.diff(vector[index], x[first])
            + _two_component(form, first, index) * sp.diff(vector[index], x[second])
            for index in range(4)
        )
        for first in range(4)
        for second in range(first + 1, 4)
    }


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
        if json.loads(path.read_text())["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency result mismatch: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source hash mismatch: {path}")

    x = sp.symbols("y0:4", real=True)
    xi, eta, zeta = (_vector(prefix, x) for prefix in ("u", "v", "w"))
    potential = _vector("B", x)
    lam, mu, nu = (sp.Function(name)(*x) for name in ("alpha", "beta", "gamma"))

    first = _transform(xi, lam, potential, x)
    second = _transform(eta, mu, potential, x)
    lhs = [
        _lie_one(xi, second, x)[component] - _lie_one(eta, first, x)[component]
        for component in range(4)
    ]
    ghost_vector = _bracket(xi, eta, x)
    ghost_scalar = _lie_scalar(xi, mu, x) - _lie_scalar(eta, lam, x)
    rhs = _transform(ghost_vector, ghost_scalar, potential, x)
    residual = [_clean(lhs[index] - rhs[index]) for index in range(4)]
    if residual != [0, 0, 0, 0]:
        raise AssertionError("independent semidirect action replay failed")

    def pair(left, right):
        return (
            _bracket(left[0], right[0], x),
            _lie_scalar(left[0], right[1], x) - _lie_scalar(right[0], left[1], x),
        )

    entries = ((xi, lam), (eta, mu), (zeta, nu))
    nested = [pair(entries[index], pair(entries[(index + 1) % 3], entries[(index + 2) % 3])) for index in range(3)]
    jacobi_vector = [_clean(sum(item[0][component] for item in nested)) for component in range(4)]
    jacobi_scalar = _clean(sum(item[1] for item in nested))
    if jacobi_vector != [0, 0, 0, 0] or jacobi_scalar != 0:
        raise AssertionError("independent semidirect Jacobi replay failed")

    curvature = _field(potential, x)
    shifted = [potential[index] + sp.diff(lam, x[index]) for index in range(4)]
    if any(_clean(_field(shifted, x)[key] - curvature[key]) != 0 for key in curvature):
        raise AssertionError("independent U(1) curvature replay failed")
    varied_curvature = _field(_transform(xi, lam, potential, x), x)
    lie_curvature = _lie_two(xi, curvature, x)
    if any(_clean(varied_curvature[key] - lie_curvature[key]) != 0 for key in curvature):
        raise AssertionError("independent field-strength covariance replay failed")

    if sum(row["multiplicity"] for row in certificate["maxwell_bv_complex"]["row_layout"]) != 10:
        raise AssertionError("Maxwell BV multiplicities do not sum to ten")
    if certificate["maxwell_bv_complex"]["combined_gravity_clock_maxwell_rows"] != 54 + 10:
        raise AssertionError("combined row layout is inconsistent")
    if certificate["dynamical_mixed_q2_ledger"]["status"] != "INPUT_BLOCKED":
        raise AssertionError("full mixed q2 was improperly promoted")
    if certificate["flags"]["BERGER_FIRST_GRAVITY_MAXWELL_TRANSFERRED_DRESSING"] is not False:
        raise AssertionError("transferred dressing was improperly promoted")
    if certificate["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] is not False:
        raise AssertionError("localized endpoints were improperly promoted")
    print("BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT independent replay: PASS")


if __name__ == "__main__":
    main()
