"""Independent verifier for the finite-harmonic Tier-3 provenance relock."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1.json"
RECEIPT = ROOT / "bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1_TIER_RECEIPT.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-finite-harmonic-tier3-provenance-relock-v1.schema.json"


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def old_bytes(commit: str, path: str) -> bytes | None:
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        text=True,
    ).strip()
    result = subprocess.run(
        ["git", "show", f"{commit}:{prefix}{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def main() -> None:
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)

    assert cert["lifecycle_state"] == "CERTIFIED"
    assert cert["provenance_graph"]["stale_reference_count"] == 0
    assert cert["provenance_graph"]["missing_input_count"] == 0
    assert set(cert["provenance_graph"]["dialect_counts"]) == {
        "paired_suffix",
        "parent",
        "path_key",
        "path_sha256",
    }
    assert cert["artifact_count"] == len(cert["artifact_manifest"])
    assert len({row["path"] for row in cert["artifact_manifest"]}) == cert["artifact_count"]
    for row in cert["artifact_manifest"]:
        current = (ROOT / row["path"]).read_bytes()
        assert sha256(current) == row["new_sha256"], row["path"]
        before = old_bytes(cert["base_commit"], row["path"])
        expected_old = None if before is None else sha256(before)
        assert expected_old == row["old_sha256"], row["path"]

    for edge in cert["provenance_graph"]["edges"]:
        assert sha256((ROOT / edge["dependency"]).read_bytes()) == edge["actual_sha256"]
        assert edge["expected_sha256"] == edge["actual_sha256"]

    attempts = cert["tier3_attempts"]
    assert attempts[-1]["status"] == "PASS"
    assert attempts[-1]["tests"] == 1255
    assert attempts[-1]["failures"] == attempts[-1]["errors"] == 0
    assert all(item["status"] == "FAIL" for item in attempts[:-1])
    assert all(item["status"] == "TIMEOUT_NONPASS" for item in cert["excluded_opt_in_replays"])
    assert cert["final_gate"]["structural_certificate"]["lifecycle_state"] == "THEOREM_FROZEN"
    assert cert["post_promotion_validation"]["status"] == "PASS"
    assert cert["post_promotion_validation"]["tests"] == 1258

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["certificate"]["sha256"] == sha256(CERT.read_bytes())
    assert receipt["tier_3"]["status"] == "PASS"
    assert receipt["post_promotion_tier_3"]["status"] == "PASS"
    assert receipt["post_promotion_tier_3"]["tests"] == 1258
    assert receipt["higher_cost_opt_in"]["status"] == "NOT_CERTIFIED"
    print("EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
