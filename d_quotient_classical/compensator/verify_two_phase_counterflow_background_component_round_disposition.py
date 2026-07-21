#!/usr/bin/env python3
"""Independent resultant/direct-substitution verifier for the component theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload byte hash mismatch")
    for record in certificate["imports"].values():
        if _sha(ROOT / record["path"]) != record["sha256"]:
            raise AssertionError("import hash mismatch")

    q, x, energy = sp.symbols("q x C", real=True)
    rows = [sp.sympify(row, locals={"q": q, "x": x, "C": energy}) for row in payload["stationary_component_stratification"]["orthonormal_stationary_rows_times_1920"]]
    first_difference = sp.factor(rows[1] - rows[0])
    second_difference = sp.factor(rows[2] - rows[0])
    q_resultant = sp.factor(sp.resultant(first_difference, second_difference, x))
    x_resultant = sp.factor(sp.resultant(first_difference, second_difference, q))
    expected_q = 14622720000 * (q - 1) ** 2 * (16 * q - 5) * (40 * q - 9)
    expected_x = -39321600000 * x**4 * (x - 1) * (5 * x + 2) * (160 * x + 119)
    if q_resultant != expected_q or x_resultant != expected_x:
        raise AssertionError("independent resultant classification failed")

    expected = {
        (sp.Rational(9, 40), sp.Integer(1), sp.Rational(9, 16)),
        (sp.Rational(5, 16), -sp.Rational(2, 5), sp.Rational(1, 8)),
        (sp.Integer(1), -sp.Rational(119, 160), sp.Rational(119, 1920)),
    }
    recorded = {(sp.Rational(row["q"]), sp.Rational(row["x"]), sp.Rational(row["C"])) for row in payload["stationary_component_stratification"]["solutions"]}
    if recorded != expected:
        raise AssertionError("solution ledger is incomplete")
    for point in recorded:
        sub = {q: point[0], x: point[1], energy: point[2]}
        if any(sp.factor(row.subs(sub)) != 0 for row in rows):
            raise AssertionError("recorded solution is not stationary")
    physical = [point for point in recorded if all(value > 0 for value in point)]
    if physical != [(sp.Rational(9, 40), sp.Integer(1), sp.Rational(9, 16))]:
        raise AssertionError("positive component classification failed")

    r1, r2 = sp.symbols("r1 r2")
    if sp.factor(sp.resultant(r1 + r2 - 4, r1 * r2 - 4, r2)) != -(r1 - 2) ** 2:
        raise AssertionError("phase-weight uniqueness failed")

    round_row = payload["round_cylinder_disposition"]
    if round_row["same_action_round_stationarity"]["contradiction"] != "-1/3 != 119/1920":
        raise AssertionError("fixed-action cylinder contradiction lost")
    if round_row["imported_retuned_round_boundary"]["not_recomputed"] is not True:
        raise AssertionError("round boundary was not kept imported")
    if certificate["claim_flags"]["CAUSAL_TRANSPORT_AWAY_FROM_SELECTED"]:
        raise AssertionError("causal claim exceeded the imported parent")
    print("INDEPENDENT TWO_PHASE_COUNTERFLOW COMPONENT VERIFIER: PASS")


if __name__ == "__main__":
    verify()
