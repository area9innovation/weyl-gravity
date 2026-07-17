#!/usr/bin/env python3
"""Independent payload audit for the support-local coupled Maxwell q2."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json"
PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-payload-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: int | dict[str, int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _coefficient(value: dict[str, object]) -> sp.Expr:
    return sp.Rational(_fraction(value["rational"]).numerator, _fraction(value["rational"]).denominator) + sp.sqrt(10) * sp.Rational(
        _fraction(value["sqrt10"]).numerator, _fraction(value["sqrt10"]).denominator
    )


def _evaluate_row(row: dict[str, object], left: dict[int, sp.Expr], right: dict[int, sp.Expr], t: sp.Symbol) -> sp.Expr:
    total = sp.S.Zero
    for left_index, left_multi, right_index, right_multi, raw in row["terms"]:
        left_value = left.get(left_index, sp.S.Zero)
        right_value = right.get(right_index, sp.S.Zero)
        if any(left_multi[axis] for axis in (1, 2, 3)):
            left_value = sp.S.Zero
        else:
            left_value = sp.diff(left_value, t, left_multi[0])
        if any(right_multi[axis] for axis in (1, 2, 3)):
            right_value = sp.S.Zero
        else:
            right_value = sp.diff(right_value, t, right_multi[0])
        total += _coefficient(raw) * left_value * right_value
    return sp.factor(sp.trigsimp(total))


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(certificate)
    Draft202012Validator(payload_schema).validate(payload)
    if _sha256(PAYLOAD) != certificate["classical_binary_q2"]["payload_file_sha256"]:
        raise AssertionError("coupled Maxwell payload file hash mismatch")
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")
    for relative, digest in certificate["provenance"]["source_manifest"].items():
        path = ROOT / relative
        if _sha256(path) != digest:
            raise AssertionError(f"source hash mismatch: {path}")

    rows = payload["rows"]
    if len(rows) != 64 or [row["output"] for row in rows] != list(range(64)):
        raise AssertionError("independent 64-row ledger replay failed")
    parities = certificate["row_layout"]["parities"]
    total_terms = 0
    for row in rows:
        body = {"output": row["output"], "terms": row["terms"]}
        if row["canonical_sha256"] != _digest(body):
            raise AssertionError(f"independent row hash mismatch: {row['output']}")
        table = {}
        for left, left_multi, right, right_multi, raw in row["terms"]:
            coefficient = sp.expand(_coefficient(raw))
            if coefficient == 0:
                raise AssertionError("explicit zero overlay coefficient")
            key = (left, tuple(left_multi), right, tuple(right_multi))
            if key in table:
                raise AssertionError("duplicate overlay term")
            table[key] = coefficient
        for (left, left_multi, right, right_multi), coefficient in table.items():
            swapped = table.get((right, right_multi, left, left_multi))
            if swapped is None:
                raise AssertionError(
                    f"missing independent Koszul partner on row {row['output']}"
                )
            sign = -1 if parities[left] * parities[right] else 1
            if sp.expand(swapped - sign * coefficient) != 0:
                raise AssertionError(f"independent Koszul symmetry failure on row {row['output']}")
        total_terms += len(table)
    if total_terms != certificate["classical_binary_q2"]["overlay_term_count"]:
        raise AssertionError("independent overlay term count drifted")
    gravity_path = ROOT / payload["gravity_base"]["payload_path"]
    if _sha256(gravity_path) != payload["gravity_base"]["file_sha256"]:
        raise AssertionError("independent gravity base hash mismatch")
    if rows[37]["terms"] or not rows[38]["terms"]:
        raise AssertionError("Weyl-zero/clock-nonzero source support drifted")

    beta = 2 * sp.sqrt(10) / 3
    t = sp.symbols("t", real=True)
    standing = {56: 2 * sp.cos(beta * t)}
    metric = {
        5: sp.Rational(5120, 567),
        9: -sp.Rational(2466560, 147819),
        12: -sp.Rational(76705280, 4582389),
        14: -sp.Rational(14080, 1953),
    }
    expected_metric = [
        sp.Rational(160, 9), 0, 0, 0, -sp.Rational(160, 9),
        0, 0, sp.Rational(160, 9), 0, sp.Rational(160, 9),
    ]
    observed_metric = [_evaluate_row(rows[27 + index], standing, standing, t) for index in range(10)]
    if observed_metric != expected_metric:
        raise AssertionError("independent standing stress regression failed")
    observed_mixed = _evaluate_row(rows[60], metric, standing, t)
    expected_mixed = sp.Rational(564428800, 35920017) * sp.cos(beta * t)
    if sp.trigsimp(observed_mixed - expected_mixed) != 0:
        raise AssertionError("independent mixed Maxwell Euler regression failed")
    if certificate["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("persisted arity-two zero ledger drifted")
    if certificate["flags"]["BERGER_MAXWELL_UNARY_CONTRACTION"] is not False:
        raise AssertionError("q2 export was promoted to a Maxwell contraction")
    print("BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2 independent replay: PASS")


if __name__ == "__main__":
    main()
