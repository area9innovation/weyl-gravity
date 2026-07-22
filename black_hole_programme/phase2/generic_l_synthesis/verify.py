#!/usr/bin/env python3
"""Independent exact replay for the Phase-2 generic-ell parity synthesis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
CLAIM_MAP = HERE / "claim_map.json"
RECEIPT = HERE / "receipt.json"
Q21 = ROOT / "black_hole_programme/phase2/general_l_polar_extendible_current_closure/current_artifacts/q21-finite-line-factor.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_q21() -> tuple[sp.Symbol, sp.Symbol, sp.Expr]:
    data = json.loads(Q21.read_text())
    lam, x = sp.symbols("Lambda x", real=True)
    expression = sum(
        sp.Integer(coefficient) * lam ** monomial[0] * x ** (monomial[1] // 2)
        for monomial, coefficient in data["terms"]
    )
    return lam, x, sp.expand(expression)


def sign_variations(signs: list[int]) -> int:
    nonzero = [sign for sign in signs if sign]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


def positive_sturm_count(expression: sp.Expr, variable: sp.Symbol) -> int:
    """Count roots on (0,+infinity) from an explicit exact Sturm chain."""
    chain = [sp.Poly(item, variable, domain=sp.QQ) for item in sp.sturm(expression, variable)]
    at_zero = [sp.sign(poly.eval(0)) for poly in chain]
    at_infinity = [sp.sign(poly.LC()) for poly in chain]
    return sign_variations(at_zero) - sign_variations(at_infinity)


def replay_triangular_counts() -> dict[int, int]:
    lam, x, q21 = load_q21()
    return {
        ell: positive_sturm_count(q21.subs(lam, ell * (ell + 1)), x)
        for ell in range(2, 42)
    }


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator(schema).validate(certificate)

    for input_data in certificate["input_snapshot"].values():
        path = input_data.get("path")
        expected = input_data.get("certificate_sha256") or input_data.get("sha256")
        if path and expected:
            assert sha256(ROOT / path) == expected

    lam, x, q21 = load_q21()
    assert sp.Poly(q21, lam, x).degree_list() == (21, 21)
    fixture = certificate["q21_exceptional_frequency_count"]["legacy_fixture"]
    direct = sp.factor(q21.subs({lam: 6, x: sp.Rational(9, 25)}))
    prior = sp.factor(q21.subs({lam: 6, x: sp.Rational(81, 625)}))
    assert sp.sstr(direct) == fixture["Q21_value"]
    assert sp.sstr(prior) == fixture["evaluator_variable_correction"]["prior_value"]
    assert direct != prior and direct != 0 and prior != 0

    counts = replay_triangular_counts()
    assert counts[2] == 0 and counts[3] == 3
    assert all(counts[ell] == 1 for ell in range(4, 11))
    assert all(counts[ell] == 3 for ell in range(11, 41))
    assert counts[41] == 1

    q0 = sp.factor(q21.subs(x, 0))
    assert sp.sstr(q0) == certificate["q21_exceptional_frequency_count"]["boundary_factorization"]
    assert certificate["q21_exceptional_frequency_count"]["discriminant_factorization"]["factorization_evidence_type"] == "EXACT_RATIONAL"
    assert certificate["q21_exceptional_frequency_count"]["discriminant_factorization"]["root_isolation_evidence_type"] == "CERTIFIED_INTERVAL_NUMERIC"
    assert certificate["q21_exceptional_frequency_count"]["count_evidence_type"] == "EXACT_RATIONAL_STURM"

    claims = json.loads(CLAIM_MAP.read_text())
    statuses = {claim["claim_id"]: claim["status"] for claim in claims["claims"]}
    assert statuses["BH-P2-JOIN-PHASE-SPACE"] == "DOES_NOT_ESTABLISH"
    assert "not a Hilbert norm" in certificate["polar_phase"]["normalization_boundary"]

    receipt = json.loads(RECEIPT.read_text())
    assert receipt["status"] == "PASS_SCOPED"
    for path, expected in receipt["artifact_sha256"].items():
        assert sha256(ROOT / path) == expected
    print("verified Phase-2 generic-ell parity synthesis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
