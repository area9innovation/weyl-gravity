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
    if table["theorem_frozen"] is not True or table["paper_state"] != "THEOREM_FROZEN":
        raise AssertionError("Paper IX theorem freeze is absent")
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
        if "MAXWELL" in entry["certificate_result_id"]:
            raise AssertionError("Maxwell certificate entered the main theorem")
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
    for entry in table["independent_cross_checks"]:
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError("independent cross-check digest mismatch")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError("independent cross-check result id mismatch")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError("independent cross-check boundary mismatch")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"cross-check required true field failed: {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"cross-check required false field failed: {dotted}")
    crosscheck_ids = [entry["certificate_result_id"] for entry in table["independent_cross_checks"]]
    if crosscheck_ids != [
        "BERGER_Q3_ACTION_SECTOR_CROSSCHECK",
        "BERGER_GENERATOR_CONJUGATION_AUDIT",
    ]:
        raise AssertionError("independent cross-check sequence drifted")
    expected_signoffs = [
        ("nonlinear_team", "PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF", "SIGNED_SCOPED_K_THEOREM"),
        ("quantum_team", "PAPER09_QUANTUM_CLAIM_BOUNDARY_SIGNOFF", "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED"),
    ]
    if len(table["signoff_evidence"]) != 2:
        raise AssertionError("independent signoff evidence is incomplete")
    for entry, expected in zip(table["signoff_evidence"], expected_signoffs):
        observed = (entry["team"], entry["certificate_result_id"], entry["status"])
        if observed != expected:
            raise AssertionError(f"signoff identity or verdict mismatch: {observed}")
        certificate_path = ROOT / entry["certificate_path"]
        if _sha256(certificate_path) != entry["certificate_sha256"]:
            raise AssertionError(f"signoff digest mismatch: {entry['team']}")
        certificate = json.loads(certificate_path.read_text())
        if certificate["result_id"] != entry["certificate_result_id"]:
            raise AssertionError(f"signoff result id mismatch: {entry['team']}")
        if certificate["claim_boundary"] != entry["certificate_claim_boundary"]:
            raise AssertionError(f"signoff boundary mismatch: {entry['team']}")
        for dotted in entry["required_true"]:
            if _lookup(certificate, dotted) is not True:
                raise AssertionError(f"signoff required true field failed: {entry['team']} {dotted}")
        for dotted in entry["required_false"]:
            if _lookup(certificate, dotted) is not False:
                raise AssertionError(f"signoff forbidden promotion detected: {entry['team']} {dotted}")
    if table["required_signoffs"] != {
        "classical_team": "SIGNED_AND_FROZEN",
        "nonlinear_team": "SIGNED_K_GENERATOR_INTERPRETATION",
        "quantum_team": "SIGNED_OFF_CLASSICAL_K_ONLY_QUANTUM_BLOCKED",
        "einstein_team": "OPTIONAL_INTERNAL_REFEREE",
    }:
        raise AssertionError("authoritative signoff ledger drifted")
    if table["next_gate"] != "POST_FREEZE_OBSERVER_84_ROW_BACKGROUND_SUPPORT":
        raise AssertionError("post-freeze observer handoff drifted")
    if table["main_theorem_exclusions"][:2] != [
        "Maxwell signal or redshift results",
        "observer-apparatus or 84-row results",
    ]:
        raise AssertionError("main-theorem downstream exclusions drifted")
    print("PAPER_09_BERGER_CLAIM_TABLE independent audit: PASS")
    print("claims=10 cross_checks=2 signoffs=2 theorem_frozen=true maxwell_excluded hashes_and_boundaries=exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
