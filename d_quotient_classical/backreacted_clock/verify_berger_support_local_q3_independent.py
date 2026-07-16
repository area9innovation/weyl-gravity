#!/usr/bin/env python3
"""Independent row-bounded audit of the frozen Berger ``q3`` export.

This consumer does not import the nonlinear geometry producer.  It validates
strict schemas, manifest/chunk hashes, exact sparse PBW normal form, summary
statistics, and adjacent graded symmetries one compressed row at a time.  It
does not independently rederive the Bach--clock expansion from the action.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
CERTIFICATE_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q3-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q3-payload-v1.schema.json"
ROW_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q3-row-v1.schema.json"
RECEIPT = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_TIER2_RECEIPT.json"
RECEIPT_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-q3-tier2-receipt-v1.schema.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Tier-1 schema/hash smoke rail; skip unchanged row-chunk replay",
    )
    args = parser.parse_args()
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    receipt = json.loads(RECEIPT.read_text())
    schemas = [
        json.loads(path.read_text())
        for path in (CERTIFICATE_SCHEMA, PAYLOAD_SCHEMA, ROW_SCHEMA, RECEIPT_SCHEMA)
    ]
    for schema in schemas:
        jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schemas[0]).validate(certificate)
    jsonschema.Draft202012Validator(schemas[1]).validate(payload)
    jsonschema.Draft202012Validator(schemas[3]).validate(receipt)

    summary = certificate["classical_ternary_q3"]
    if _sha256(PAYLOAD) != summary["payload_file_sha256"]:
        raise AssertionError("q3 payload manifest file hash mismatch")
    if _digest(payload) != summary["payload_canonical_sha256"]:
        raise AssertionError("q3 canonical manifest hash mismatch")
    if receipt["artifact_hashes"]["portable_manifest_file_sha256"] != _sha256(PAYLOAD):
        raise AssertionError("q3 receipt manifest file hash mismatch")
    if receipt["artifact_hashes"]["portable_manifest_canonical_sha256"] != _digest(payload):
        raise AssertionError("q3 receipt manifest canonical hash mismatch")
    if certificate["tier_receipts"]["publication_receipt_path"] != str(RECEIPT.relative_to(ROOT)):
        raise AssertionError("q3 publication receipt path mismatch")
    if certificate["tier_receipts"]["publication_receipt_sha256"] != _sha256(RECEIPT):
        raise AssertionError("q3 publication receipt hash mismatch")
    if args.manifest_only:
        print("BERGER_SUPPORT_LOCAL_Q3 independent manifest audit: PASS")
        print("Tier-1 rail only; exhaustive row-chunk audit is the recorded Tier-2 stage")
        return 0

    parities = certificate["row_layout"]["parities"]
    total_terms = 0
    nonzero_rows = 0
    maximum_order = 0
    for expected_output, chunk in enumerate(payload["chunks"]):
        if chunk["output"] != expected_output:
            raise AssertionError("q3 chunks are not in canonical output order")
        path = ROOT / chunk["path"]
        if _sha256(path) != chunk["file_sha256"]:
            raise AssertionError(f"row {expected_output}: compressed file hash mismatch")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        jsonschema.Draft202012Validator(schemas[2]).validate(row)
        if row["output"] != expected_output:
            raise AssertionError(f"row {expected_output}: embedded output mismatch")
        if _digest(row) != chunk["canonical_sha256"]:
            raise AssertionError(f"row {expected_output}: canonical hash mismatch")

        terms = row["terms"]
        if len(terms) != chunk["term_count"]:
            raise AssertionError(f"row {expected_output}: term count mismatch")
        total_terms += len(terms)
        nonzero_rows += bool(terms)
        table: dict[tuple[object, ...], tuple[Fraction, Fraction]] = {}
        previous = None
        row_maximum = 0
        for first, first_word, second, second_word, third, third_word, raw_coefficient in terms:
            key = (first, tuple(first_word), second, tuple(second_word), third, tuple(third_word))
            if previous is not None and key <= previous:
                raise AssertionError(f"row {expected_output}: PBW terms are not strictly ordered")
            previous = key
            coefficient = _coefficient(raw_coefficient)
            if coefficient == (Fraction(0), Fraction(0)):
                raise AssertionError(f"row {expected_output}: explicit zero coefficient")
            table[key] = coefficient
            row_maximum = max(row_maximum, sum(first_word) + sum(second_word) + sum(third_word))
        if row_maximum != chunk["maximum_total_jet_order"]:
            raise AssertionError(f"row {expected_output}: maximum order mismatch")
        maximum_order = max(maximum_order, row_maximum)

        for key, coefficient in table.items():
            first, first_word, second, second_word, third, third_word = key
            for mate_key, exponent in (
                ((second, second_word, first, first_word, third, third_word), parities[first] * parities[second]),
                ((first, first_word, third, third_word, second, second_word), parities[second] * parities[third]),
            ):
                sign = -1 if exponent else 1
                expected = (sign * coefficient[0], sign * coefficient[1])
                if table.get(mate_key) != expected:
                    raise AssertionError(f"row {expected_output}: graded-symmetry mate missing at {key}")
        del table, row

    if total_terms != summary["term_count"]:
        raise AssertionError("q3 total term count mismatch")
    if nonzero_rows != summary["nonzero_rows"]:
        raise AssertionError("q3 nonzero-row count mismatch")
    if maximum_order != summary["maximum_total_jet_order"]:
        raise AssertionError("q3 maximum jet order mismatch")
    if certificate["local_D_arity_three"]["L_D3"] != "ZERO":
        raise AssertionError("L_D3 was not explicitly declared")
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("producer proof ledger contains a false check")

    print("BERGER_SUPPORT_LOCAL_Q3 independent row-chunk audit: PASS")
    print(f"rows=54 nonzero_rows={nonzero_rows} terms={total_terms} max_total_jet_order={maximum_order} L_D3=ZERO")
    print("audit boundary: frozen PBW operation checked; action expansion not independently rederived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
