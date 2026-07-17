#!/usr/bin/env python3
"""Independent consumer for the Paper IX claim-to-certificate table."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-berger-claim-table-v1.schema.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _lookup(payload: dict[str, object], dotted: str) -> object:
    value: object = payload
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise AssertionError(f"missing required field: {dotted}")
        value = value[part]
    return value


def main() -> int:
    table = json.loads(TABLE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(table)
    if table["theorem_frozen"] is not False:
        raise AssertionError("working draft was prematurely frozen")
    ids = [entry["claim_id"] for entry in table["claims"]]
    if ids != [f"P09-C{index}" for index in range(1, 11)]:
        raise AssertionError("claim ids are not the complete canonical sequence")

    paper_text = ""
    for relative, expected in table["paper_sources"].items():
        path = ROOT / relative
        if _sha256(path) != expected:
            raise AssertionError(f"paper source hash mismatch: {relative}")
        paper_text += path.read_text()
    for entry in table["claims"]:
        if entry["claim_id"] not in paper_text:
            raise AssertionError(f"claim id absent from paper sources: {entry['claim_id']}")
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError(f"certificate digest mismatch: {entry['claim_id']}")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError(f"certificate result id mismatch: {entry['claim_id']}")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError(f"certificate boundary mismatch: {entry['claim_id']}")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"required true field failed: {entry['claim_id']} {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"required false field failed: {entry['claim_id']} {dotted}")
    print("PAPER_09_BERGER_CLAIM_TABLE independent audit: PASS")
    print("claims=10 theorem_frozen=false hashes_and_boundaries=exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
