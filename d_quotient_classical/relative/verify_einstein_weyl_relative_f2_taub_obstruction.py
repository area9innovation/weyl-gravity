#!/usr/bin/env python3
"""Independent consumer for the compact-product relative f2 obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-f2-taub-obstruction-v1.schema.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    certificate = _load(CERTIFICATE)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    dependencies = certificate["dependencies"]
    for item in dependencies.values():
        path = ROOT / item["path"]
        if _sha(path) != item["sha256"]:
            raise AssertionError(f"dependency hash drifted: {path}")
    for path_text, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / path_text
        if _sha(path) != digest:
            raise AssertionError(f"source manifest drifted: {path}")

    payload = _load(ROOT / dependencies["strict_delta2_payload"]["path"])
    row_ids = {row["row_id"]: index for index, row in enumerate(payload["source_rows"])}
    t, x, theta, phi = sp.symbols("t x theta phi", real=True)
    root = sp.sqrt(3)
    omega = sp.sqrt(6 + 2 * root)
    fields = {
        row_ids["g_13"]: 3 * sp.cos(omega * t) * sp.sin(theta) ** 2 * sp.cos(theta),
        row_ids["A_1"]: root * sp.cos(omega * t) * (3 * sp.cos(theta) ** 2 - 1) / 2,
    }
    coordinates = (t, x, theta, phi)
    point = {t: 0, x: 0, theta: sp.pi / 2, phi: 0}
    cache: dict[tuple[int, tuple[int, ...]], sp.Expr] = {}

    def value(row: int, word: list[int]) -> sp.Expr:
        key = (row, tuple(word))
        if key not in cache:
            expression = fields.get(row, sp.S.Zero)
            for axis in word:
                expression = sp.diff(expression, coordinates[axis])
            cache[key] = sp.simplify(expression.subs(point))
        return cache[key]

    result: dict[int, sp.Expr] = {}
    for term in payload["content"]["terms"]:
        left, right = term["inputs"]
        contribution = sp.Rational(term["coefficient"]) * value(left["row"], left["word"]) * value(right["row"], right["word"])
        if contribution:
            output = term["output_row"]
            result[output] = sp.simplify(result.get(output, sp.S.Zero) + contribution)
    actual = {
        payload["target_rows"][index]["row_id"]: sp.factor(entry)
        for index, entry in result.items()
        if sp.simplify(entry) != 0
    }
    stored = {
        row: sp.sympify(entry)
        for row, entry in certificate["local_delta2_normalization"]["nonzero_delta2_rows"].items()
    }
    if set(actual) != set(stored) or any(
        sp.simplify(actual[row] - stored[row]) != 0 for row in actual
    ):
        raise AssertionError(f"independent point replay failed: {actual}")

    mode = _load(ROOT / dependencies["periodic_graviton"]["path"])
    radiative = _load(ROOT / dependencies["radiative_restriction"]["path"])
    relative_form = _load(ROOT / dependencies["relative_solution_form"]["path"])
    if relative_form["cyclic_obstruction_theorem"]["solution_pairing_identity"] != "iota^*Omega_WM(u,v)-Omega_EM(u,v)=Omega_EM(u,Dv), D=R-I":
        raise AssertionError("relative solution-form identity drifted")
    mu_w = sp.sympify(mode["adjoint_cokernel_witness"]["normalized_source_pairing_at_t_zero"])
    lam = sp.Integer(6)
    weight = sp.sympify(
        radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"][0].replace("lambda", "lam"),
        locals={"lam": lam},
    )
    mu_e = sp.radsimp(mu_w / weight)
    relative = sp.simplify(mu_w - mu_e)
    stored_relative = sp.sympify(certificate["taub_pairing"]["relative_half_delta2_pairing"])
    if sp.simplify(relative - stored_relative) != 0 or relative == 0:
        raise AssertionError("relative Taub pairing replay failed")

    target = _load(ROOT / dependencies["target_adjoint_witness"]["path"])
    if not target["target_correction_domain"]["cauchy_slice_independent"]:
        raise AssertionError("target adjoint class lost slice independence")
    if target["target_correction_domain"]["fixed_bundle_magnetic_lift_allowed"]:
        raise AssertionError("forbidden magnetic lift was admitted")
    if certificate["classification"]["frozen_unary_full_domain_f2_exists"]:
        raise AssertionError("fail-closed f2 verdict was promoted")
    return {
        "result_id": certificate["result_id"],
        "status": "PASS",
        "nonzero_delta2_rows": sorted(actual),
        "relative_half_delta2_pairing": str(sp.factor(relative)),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
