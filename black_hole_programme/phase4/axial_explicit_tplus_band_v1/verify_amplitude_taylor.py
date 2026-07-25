#!/usr/bin/env python3
"""Independent structural audit of the T+ amplitude shortfall record."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from . import produce_amplitude_summary as producer


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def audit() -> None:
    certificate = json.loads(producer.CERTIFICATE.read_text())
    manifest = json.loads(producer.MANIFEST.read_text())
    receipt = json.loads(producer.RECEIPT.read_text())

    for name, document in (
        ("certificate", certificate),
        ("manifest", manifest),
    ):
        declared = document.pop("payload_sha256")
        if canonical_sha256(document) != declared:
            raise AssertionError(f"{name} payload hash mismatch")
        document["payload_sha256"] = declared
    if receipt["certificate_sha256"] != sha256(producer.CERTIFICATE):
        raise AssertionError("receipt/certificate hash mismatch")
    if receipt["manifest_sha256"] != sha256(producer.MANIFEST):
        raise AssertionError("receipt/manifest hash mismatch")
    if certificate["manifest_sha256"] != sha256(producer.MANIFEST):
        raise AssertionError("certificate/manifest hash mismatch")
    if certificate["status"] != "FAIL_CLOSED_REPRESENTATION_WRAPPING":
        raise AssertionError("shortfall status was promoted or changed")
    if certificate["claim_flags"]["explicit_Tplus_certified"]:
        raise AssertionError("explicit T+ must remain unproved")
    if certificate["validated_result"]["terminal_rank_certified"]:
        raise AssertionError("terminal rank must remain unproved")

    records = manifest["stage_records"]
    if [record["stage"] for record in records] != list(range(7)):
        raise AssertionError("stage ledger is not complete")
    for record in records:
        path = producer.ROOT / record["path"]
        if sha256(path) != record["file_sha256"]:
            raise AssertionError(f"stage {record['stage']} file hash mismatch")
        stage = json.loads(path.read_text())
        declared = stage.pop("payload_sha256")
        if canonical_sha256(stage) != declared:
            raise AssertionError(f"stage {record['stage']} payload drift")
        if declared != record["payload_sha256"]:
            raise AssertionError(f"stage {record['stage']} ledger drift")

    for diagnostic in certificate["validated_result"]["diagnostics"].values():
        ratio = Fraction(diagnostic["remainder_to_center_ratio_exact"])
        if ratio <= 1_000_000:
            raise AssertionError("wrapping margin no longer exceeds 10^6")


def main() -> int:
    audit()
    print("PASS independent T+ amplitude shortfall audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
