#!/usr/bin/env python3
"""Independent exact consumer for the Berger Einstein-incidence certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/berger_einstein_incidence.json"


def _matrix(rows: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals=symbols) for value in row] for row in rows])


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert payload["result_id"] == "BERGER_EINSTEIN_INCIDENCE"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    schema_path = ROOT / payload["schema_path"]
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == payload["schema_sha256"]
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    q, a, alpha_b = sp.symbols("q a alpha_B", positive=True, real=True)
    symbols = {"q": q, "a": a, "alpha_B": alpha_b}
    tensors = payload["exact_tensors"]
    eta = sp.diag(-1, 1, 1, 1)
    ricci = _matrix(tensors["ricci_orthonormal"], symbols)
    bach = _matrix(tensors["bach_orthonormal"], symbols)
    stress = _matrix(tensors["clock_stress_orthonormal"], symbols)
    tracefree = _matrix(tensors["tracefree_ricci_orthonormal"], symbols)
    scalar = sp.sympify(tensors["scalar_curvature"], locals=symbols)

    assert sp.simplify(sp.trace(eta * ricci) - scalar) == 0
    assert sp.simplify(sp.trace(eta * bach)) == 0
    assert sp.simplify(stress - alpha_b * bach) == sp.zeros(4)
    assert sp.simplify(tracefree - (ricci - scalar * eta / 4)) == sp.zeros(4)
    minor = sp.factor(tracefree[0, 0] * bach[1, 1] - tracefree[1, 1] * bach[0, 0])
    assert sp.simplify(minor + q * (1 - q) / (8 * a**6)) == 0
    assert sp.factor(bach[0, 0]) == (q - 1) ** 2 / (6 * a**4)

    fixture = payload["rational_fixture"]
    substitution = {q: sp.Rational(9, 40), a: 1, alpha_b: 5}
    assert _matrix(fixture["ricci_orthonormal"], symbols) == ricci.subs(substitution)
    assert _matrix(fixture["bach_orthonormal"], symbols) == bach.subs(substitution)
    assert _matrix(fixture["clock_stress_orthonormal"], symbols) == stress.subs(substitution)
    assert sp.sympify(fixture["proportionality_minor_00_11"]) == minor.subs(substitution)

    classification = payload["classification"]
    assert classification["berger_background_is_genuine_non_einstein_weyl_matter_branch"] is True
    assert classification["same_base_point_linearized_einstein_clock_complex_exists"] is False
    assert classification["retained_berger_q1_is_einstein_tangent_subcomplex"] is False
    assert payload["claim_flags"]["lorentzian_causal_claim"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_EINSTEIN_INCIDENCE_INDEPENDENT: PASS")
    print("Ricci, Bach, stress, trace, proportionality minor, and rational fixture: PASS")
    print("same-base-point Einstein tangent embedding: NOT APPLICABLE")


if __name__ == "__main__":
    main()
