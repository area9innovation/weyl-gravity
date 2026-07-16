#!/usr/bin/env python3
"""Independent frozen-payload audit for ``BERGER_SUPPORT_LOCAL_Q2``.

This consumer does not import the nonlinear geometry producer.  It validates
the two strict schemas, hashes and sparse PBW normal form, recomputes the row
statistics, and checks graded symmetry directly from the serialized terms.
It therefore audits the exported operation independently, while deliberately
not claiming a second derivation of the Bach expansion from the action.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json"
PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
CERTIFICATE_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q2-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q2-payload-v1.schema.json"


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _fraction(value: int | dict[str, int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _coefficient(value: dict[str, object]) -> tuple[Fraction, Fraction]:
    return _fraction(value["rational"]), _fraction(value["sqrt10"])


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    certificate_schema = json.loads(CERTIFICATE_SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(certificate_schema)
    jsonschema.Draft202012Validator.check_schema(payload_schema)
    jsonschema.Draft202012Validator(certificate_schema).validate(certificate)
    jsonschema.Draft202012Validator(payload_schema).validate(payload)

    if hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() != certificate["classical_binary_q2"]["payload_file_sha256"]:
        raise AssertionError("q2 payload file hash mismatch")
    if _digest(payload) != certificate["classical_binary_q2"]["payload_canonical_sha256"]:
        raise AssertionError("q2 canonical payload hash mismatch")

    parities = certificate["row_layout"]["parities"]
    total_terms = 0
    nonzero_rows = 0
    maximum_order = 0
    for expected_output, row in enumerate(payload["rows"]):
        if row["output"] != expected_output:
            raise AssertionError("q2 output rows are not in canonical order")
        terms = row["terms"]
        total_terms += len(terms)
        nonzero_rows += bool(terms)
        table: dict[tuple[object, ...], tuple[Fraction, Fraction]] = {}
        previous = None
        for left, left_word, right, right_word, raw_coefficient in terms:
            key = (left, tuple(left_word), right, tuple(right_word))
            if previous is not None and key <= previous:
                raise AssertionError(f"row {expected_output}: PBW terms are not strictly ordered")
            previous = key
            coefficient = _coefficient(raw_coefficient)
            if coefficient == (Fraction(0), Fraction(0)):
                raise AssertionError(f"row {expected_output}: explicit zero coefficient")
            table[key] = coefficient
            maximum_order = max(maximum_order, sum(left_word) + sum(right_word))
        for (left, left_word, right, right_word), coefficient in table.items():
            swapped = table.get((right, right_word, left, left_word))
            sign = -1 if parities[left] * parities[right] else 1
            expected = (sign * coefficient[0], sign * coefficient[1])
            if swapped != expected:
                raise AssertionError(
                    f"row {expected_output}: Koszul mate missing at {(left, left_word, right, right_word)}"
                )

    summary = certificate["classical_binary_q2"]
    if total_terms != summary["term_count"]:
        raise AssertionError("q2 term count mismatch")
    if nonzero_rows != summary["nonzero_rows"]:
        raise AssertionError("q2 nonzero-row count mismatch")
    if maximum_order != summary["maximum_total_jet_order"]:
        raise AssertionError("q2 maximum jet order mismatch")
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("producer proof ledger contains a false check")

    print("BERGER_SUPPORT_LOCAL_Q2 independent payload audit: PASS")
    print(f"rows=54 nonzero_rows={nonzero_rows} terms={total_terms} max_total_jet_order={maximum_order}")
    print("audit boundary: frozen PBW operation checked; action expansion not independently rederived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
