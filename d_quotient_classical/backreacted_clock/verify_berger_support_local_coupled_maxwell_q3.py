#!/usr/bin/env python3
"""Independent portable replay for the typed mixed Maxwell q3 export."""

from __future__ import annotations

from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json"
Q2_TYPED = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
Q3_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
Q2_LEGACY = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json"
SCHEMAS = {
    CERTIFICATE: ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-v1.schema.json",
    Q2_TYPED: ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-typed-payload-v1.schema.json",
    Q3_PAYLOAD: ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-payload-v1.schema.json",
}
ROW_SCHEMA = ROOT / "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-row-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rational(value: int | dict[str, int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _coefficient(value: dict[str, object]) -> tuple[Fraction, Fraction]:
    return _rational(value["rational"]), _rational(value["sqrt10"])


def _bilinear_mapping(payload: dict) -> dict[tuple, tuple[Fraction, Fraction]]:
    output = {}
    for row in payload["rows"]:
        for left, left_word, right, right_word, coefficient in row["terms"]:
            key = (row["output"], left, tuple(left_word), right, tuple(right_word))
            if key in output:
                raise AssertionError(f"duplicate q2 key: {key}")
            output[key] = _coefficient(coefficient)
    return output


def verify() -> None:
    values = {}
    for artifact, schema_path in SCHEMAS.items():
        value = json.loads(artifact.read_text())
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        values[artifact] = value
    certificate = values[CERTIFICATE]
    q2_typed = values[Q2_TYPED]
    q3_payload = values[Q3_PAYLOAD]

    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise AssertionError(f"dependency hash drifted: {dependency['path']}")
    for relative, expected_hash in certificate["source_manifest"].items():
        if _sha256(ROOT / relative) != expected_hash:
            raise AssertionError(f"source hash drifted: {relative}")
    if _sha256(Q2_TYPED) != certificate["classical_binary_q2_typed"]["payload_file_sha256"]:
        raise AssertionError("typed q2 payload file hash drifted")
    if _digest(q2_typed) != certificate["classical_binary_q2_typed"]["payload_canonical_sha256"]:
        raise AssertionError("typed q2 payload canonical hash drifted")
    if _sha256(Q3_PAYLOAD) != certificate["classical_ternary_q3_mixed"]["payload_file_sha256"]:
        raise AssertionError("mixed q3 payload file hash drifted")
    if _digest(q3_payload) != certificate["classical_ternary_q3_mixed"]["payload_canonical_sha256"]:
        raise AssertionError("mixed q3 payload canonical hash drifted")

    legacy = json.loads(Q2_LEGACY.read_text())
    typed_map = _bilinear_mapping(q2_typed)
    legacy_map = _bilinear_mapping(legacy)
    expected = {
        key: (
            coefficient[0] * (2 if key[0] >= 54 else 1),
            coefficient[1] * (2 if key[0] >= 54 else 1),
        )
        for key, coefficient in typed_map.items()
    }
    if expected != legacy_map:
        raise AssertionError("typed/legacy lowered cubic tensor relation failed")
    if len(typed_map) != 1890:
        raise AssertionError("typed q2 coefficient count drifted")

    row_schema = json.loads(ROW_SCHEMA.read_text())
    Draft202012Validator.check_schema(row_schema)
    row_validator = Draft202012Validator(row_schema)
    seen = set()
    total_terms = 0
    nonzero_rows = 0
    maximum_order = 0
    for chunk in q3_payload["chunks"]:
        path = ROOT / chunk["path"]
        if path.read_bytes()[4:8] != b"\x00\x00\x00\x00":
            raise AssertionError(f"gzip mtime is not deterministic: {chunk['path']}")
        if _sha256(path) != chunk["file_sha256"]:
            raise AssertionError(f"q3 row hash drifted: {chunk['output']}")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        row_validator.validate(row)
        body = {"output": row["output"], "terms": row["terms"]}
        if _digest(body) != row["canonical_sha256"] or row["canonical_sha256"] != chunk["canonical_sha256"]:
            raise AssertionError(f"q3 row canonical hash drifted: {chunk['output']}")
        if row["output"] != chunk["output"] or row["output"] in seen:
            raise AssertionError("q3 row output order/uniqueness failed")
        seen.add(row["output"])
        row_maximum = max(
            (sum(term[1]) + sum(term[3]) + sum(term[5]) for term in row["terms"]),
            default=0,
        )
        if len(row["terms"]) != chunk["term_count"] or row_maximum != chunk["maximum_total_jet_order"]:
            raise AssertionError(f"q3 row summary drifted: {chunk['output']}")
        total_terms += len(row["terms"])
        nonzero_rows += bool(row["terms"])
        maximum_order = max(maximum_order, row_maximum)
    if seen != set(range(64)):
        raise AssertionError("q3 row ledger is incomplete")
    summary = certificate["classical_ternary_q3_mixed"]
    if (total_terms, nonzero_rows, maximum_order) != (
        summary["term_count"], summary["nonzero_rows"], summary["maximum_total_jet_order"]
    ):
        raise AssertionError("q3 aggregate summary drifted")

    flags = certificate["flags"]
    if flags["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] is not False:
        raise AssertionError("retained ell3 was overclaimed")
    if flags["BERGER_MIXED_Q3_INDEPENDENT_QUANTUM_ACCEPTANCE"] is not False:
        raise AssertionError("quantum acceptance was overclaimed")
    if flags["QUANTUM_CLAIM"] is not False:
        raise AssertionError("quantum result was overclaimed")


if __name__ == "__main__":
    verify()
    print("BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3 portable replay: PASS")
    print("1,890 typed q2 coefficients; 59,598 mixed q3 coefficients; 64 rows hash-checked")
    print("retained ell3 and quantum acceptance are not asserted by this upstream artifact")
