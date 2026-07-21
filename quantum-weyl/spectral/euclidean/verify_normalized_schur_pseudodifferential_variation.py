#!/usr/bin/env python3
"""Independent exact replay of the normalized-Schur variation certificate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json"
MANIFEST = HERE / "generated/normalized_schur_pseudodifferential_variation_v1/operator_words.json"
SCHEMA = HERE / "schema/normalized-schur-pseudodifferential-variation-v1.schema.json"
MANIFEST_SCHEMA = HERE / "schema/normalized-schur-pseudodifferential-operator-words-v1.schema.json"
EXPECTED_HASHES = {
    "normalized_schur": "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
    "surrogate_obstruction": "687aa26ec62e34dfa9adde53f4d1793741a97b9829c7dee55b71f11f6d54f2d5",
    "berger_low_blocks": "58d8646e3aedc1a897a8e6d05d6128f0e0eb4f885225443b9133f1c1968914f0",
    "berger_low_oracle": "2c81c166ae2c16ed4c97244b26bd134e24381779f2a6e7921a2daca4f29021b3",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mat(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value) for value in row] for row in rows])


def _validate_schema(path: Path, value: dict[str, Any]) -> None:
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _verify_dependencies(certificate: dict[str, Any]) -> None:
    for name, expected in EXPECTED_HASHES.items():
        row = certificate["dependencies"][name]
        path = ROOT / row["path"]
        if row["sha256"] != expected or _sha(path) != expected:
            raise AssertionError(f"dependency drift: {name}")


def _verify_operator_words(manifest: dict[str, Any]) -> None:
    expected = [
        ["delta", "G", "W", "G", "d"],
        ["delta", "G", "W", "G", "W", "G", "d"],
        ["delta", "G", "W", "G", "W", "G", "W", "G", "d"],
    ]
    expected_reduced = [
        ["DeltaInv", "delta", "W", "d", "DeltaInv"],
        ["DeltaInv", "delta", "W", "G", "W", "d", "DeltaInv"],
        ["DeltaInv", "delta", "W", "G", "W", "G", "W", "d", "DeltaInv"],
    ]
    orders = {"delta": 1, "d": 1, "G": -2, "W": 0, "DeltaInv": -2}
    coefficients = [sp.Rational(-1, 3), sp.Rational(1, 3), sp.Rational(-1, 3)]
    derivatives = [sp.Rational(-1, 3), sp.Rational(2, 3), sp.Integer(-2)]
    for k, row in enumerate(manifest["schur_variations"], 1):
        if row["operator_word"] != expected[k - 1] or row["ward_reduced_word"] != expected_reduced[k - 1]:
            raise AssertionError("noncommuting operator word drifted")
        order = sum(orders[token] for token in row["operator_word"])
        reduced_order = sum(orders[token] for token in row["ward_reduced_word"])
        if order != -2 * k or reduced_order != order:
            raise AssertionError("pseudodifferential order drifted")
        if row["operator_order"] != order or row["principal_symbol_order"] != order or row["subprincipal_symbol_order"] != order - 1:
            raise AssertionError("symbol hierarchy drifted")
        if sp.sympify(row["taylor_coefficient"]) != coefficients[k - 1] or sp.sympify(row["derivative_at_zero_coefficient"]) != derivatives[k - 1]:
            raise AssertionError("variation coefficient drifted")
    expected_principal = [
        "-(1/3)<xi,W xi>/|xi|^4",
        "+(1/3)<xi,W^2 xi>/|xi|^6",
        "-(1/3)<xi,W^3 xi>/|xi|^8",
    ]
    if [row["principal_symbol"] for row in manifest["schur_variations"]] != expected_principal:
        raise AssertionError("principal symbol drifted")


def _verify_finite_fixture(manifest: dict[str, Any]) -> None:
    row = manifest["exact_noncommuting_fixture"]
    f, w, d, delta = (_mat(row[name]) for name in ("F", "W", "d", "delta"))
    delta0 = _mat(row["Delta0"])
    if f * d != d * delta0 or delta * f != delta0 * delta or delta * d != delta0:
        raise AssertionError("independent Ward replay failed")
    t = sp.symbols("t")
    exact = sp.Rational(2, 3) * sp.eye(2) + sp.Rational(1, 3) * delta * (f + t * w).inv() * d
    coefficients = [sp.simplify(exact.diff(t, k).subs(t, 0) / math.factorial(k)) for k in range(1, 4)]
    if any(_mat(stored) != computed for stored, computed in zip(row["taylor_coefficients"], coefficients)):
        raise AssertionError("direct Taylor replay failed")
    if any(_mat(stored) != math.factorial(k) * coefficients[k - 1] for k, stored in enumerate(row["derivatives_at_zero"], 1)):
        raise AssertionError("derivative normalization failed")
    reordered = -sp.Rational(1, 3) * delta * w * f.inv() * f.inv() * d
    if _mat(row["reordered_first_coefficient"]) != reordered or reordered == coefficients[0] or row["reordered_word_rejected"] is not True:
        raise AssertionError("ordering mutation was not rejected")


def _verify_projector(manifest: dict[str, Any]) -> None:
    row = manifest["moving_projector_control"]
    a0, adot, p0, pdot, rdot = (_mat(row[name]) for name in ("A0", "A_prime0", "P0", "P_prime0", "R_prime0"))
    if p0 != sp.eye(2) - a0 or pdot != -adot:
        raise AssertionError("projector control inputs drifted")
    naive = -a0 * adot * a0
    full = naive - pdot * a0 - a0 * pdot
    if _mat(row["naive_fixed_projector_term"]) != naive or _mat(row["full_projector_formula"]) != full or full != rdot or naive == rdot:
        raise AssertionError("moving-projector formula failed")
    domain = manifest["projector_and_domain"]
    if "P'R-RP'" not in domain["moving_formula"] or domain["rank_change_status"] != "NO_DIFFERENTIABLE_REDUCED_RESOLVENT_WITHOUT_A_STRATUM_OR_CONTOUR_CHOICE":
        raise AssertionError("projector/domain fail-closed boundary drifted")


def _verify_berger(manifest: dict[str, Any]) -> None:
    row = manifest["berger_low_block_control"]
    delta0 = sp.Rational(9, 16)
    dwd = sp.Rational(3, 4)
    correct = -dwd / (3 * delta0**2)
    surrogate = dwd / (3 * delta0)
    if correct != sp.Rational(-64, 81) or surrogate != sp.Rational(4, 9):
        raise AssertionError("independent Berger arithmetic failed")
    if sp.sympify(row["correct_first_variation"]) != correct or sp.sympify(row["one_inverse_surrogate"]) != surrogate or row["values_distinct"] is not True:
        raise AssertionError("Berger control drifted")


def verify(certificate: dict[str, Any], manifest: dict[str, Any]) -> None:
    _validate_schema(SCHEMA, certificate)
    _validate_schema(MANIFEST_SCHEMA, manifest)
    expected_manifest_hash = hashlib.sha256((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    if certificate["manifest"]["sha256"] != expected_manifest_hash:
        raise AssertionError("manifest hash mismatch")
    _verify_dependencies(certificate)
    _verify_operator_words(manifest)
    _verify_finite_fixture(manifest)
    _verify_projector(manifest)
    _verify_berger(manifest)
    flags = certificate["claim_flags"]
    for name in ("GLOBAL_FINITE_DETERMINANT_COMPUTED", "HEAT_KERNEL_COEFFICIENT_COMPUTED", "QME_OR_LORENTZIAN_PROMOTED"):
        if flags[name] is not False:
            raise AssertionError(f"forbidden promotion: {name}")
    if certificate["results"]["variation_orders"] != [-2, -4, -6] or certificate["results"]["berger_first_variation"] != "-64/81":
        raise AssertionError("certificate summary drifted")


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()), json.loads(MANIFEST.read_text()))
    print("normalized Schur pseudodifferential variation independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
