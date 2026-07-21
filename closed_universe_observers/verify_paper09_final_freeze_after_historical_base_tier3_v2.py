#!/usr/bin/env python3
"""Independent final-disposition verifier for the Paper 9 v2 publication gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json"
TABLE = ROOT / "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"
COVERAGE = ROOT / "planning/paper-coverage/observer-phase1-relational-observable-dispositions-2026-07-21.json"
OUT = ROOT / "closed_universe_observers/receipts/PAPER09_FINAL_FREEZE_AFTER_HISTORICAL_BASE_TIER3_V2_OBSTRUCTION.json"


class VerificationError(AssertionError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim_map_verifier():
    path = ROOT / "paper/verify_09_relational_clocks_claim_map.py"
    spec = importlib.util.spec_from_file_location("paper09_claim_map_v2_independent", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def verify_final_disposition(doc: dict, root: Path = ROOT) -> dict:
    module = _claim_map_verifier()
    try:
        coverage = module.verify_document(doc, root)
    except Exception as exc:  # preserve one typed public error for mutation tests
        raise VerificationError(str(exc)) from exc

    table = json.loads((root / TABLE.relative_to(ROOT)).read_text())
    binding = table["source_binding_disposition"]
    current_map_sha = digest(root / MAP.relative_to(ROOT))
    table_sha = digest(root / TABLE.relative_to(ROOT))
    pinned_map_sha = binding["publication_claim_map"]["sha256"]
    map_table_import = next(
        row for row in doc["exact_hash_imports"]
        if row["path"] == str(TABLE.relative_to(ROOT))
    )
    if map_table_import["sha256"] != table_sha:
        raise VerificationError("regenerated map does not bind the current legacy table")
    if pinned_map_sha == current_map_sha:
        raise VerificationError("source-binding cycle unexpectedly reports a fixed point")

    tier3_path = root / "closed_universe_observers/receipts/OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1_OBSTRUCTION.json"
    tier3 = json.loads(tier3_path.read_text())
    if tier3["flags"]["AUTHORITATIVE_RUN_GREEN"] is not False:
        raise VerificationError("failed post-repair Tier-3 traversal was credited as green")
    if tier3["authoritative_run"]["passed_before_first_failure"] != 300:
        raise VerificationError("post-repair Tier-3 first-failure frontier drifted")
    if tier3["first_failure"]["classification"] != "TEST_HARNESS_MATERIALIZATION_INTERFACE_DEFECT":
        raise VerificationError("post-repair Tier-3 obstruction class drifted")

    historical_path = root / "closed_universe_observers/receipts/OBSERVER_LEGACY_RECEIVER_HISTORICAL_BASE_BINDING_REPAIR_V1_MANIFEST.json"
    historical = json.loads(historical_path.read_text())
    historical_ref = historical["input_refs"]["historical_five_row_contract"]
    if historical_ref["object_type"] != "blob" or historical_ref["source_commit"] != "aa5ca7814798dfbcc92ee52e462d25af74806515":
        raise VerificationError("historical receiver base is not the certified immutable Git blob")

    final = doc["final_disposition"]
    if doc["freeze_decision"] != "DRAFT_ALLOWED" or final["theorem_frozen"] is not False:
        raise VerificationError("obstructed publication evidence was promoted to theorem freeze")
    if coverage["status"] != "NONVACUOUS_PASS" or coverage["claims_total"] != 22:
        raise VerificationError("22-claim publication coverage is vacuous or incomplete")

    health_path = root / "closed_universe_observers/certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json"
    health = json.loads(health_path.read_text())
    health_dependency_drift = []
    for name, ref in health["dependency_refs"].items():
        observed = digest(root / ref["path"])
        if observed != ref["sha256"]:
            health_dependency_drift.append({
                "name": name,
                "path": ref["path"],
                "pinned_sha256": ref["sha256"],
                "current_sha256": observed,
            })
    if [row["name"] for row in health_dependency_drift] != [
        "legacy_ratio_nonactivation", "legacy_receiver_replay", "receiver_admissibility"
    ]:
        raise VerificationError("transitive health nonactivation drift frontier changed")
    expected_current = {
        "legacy_ratio_nonactivation": "e0deee0fdfadd1d3ea61ce11718c302ba7954756745974e126c457982a26637c",
        "legacy_receiver_replay": "3851a46dc9ab2b2f1ca092a67ffd17c7ecdb21b18b8a238f72c8de091835fde5",
        "receiver_admissibility": "78cdd1853698a82866b8e7891a9817c3fae6279d9afbab6bb2c0f4dc84252fde",
    }
    if {row["name"]: row["current_sha256"] for row in health_dependency_drift} != expected_current:
        raise VerificationError("transitive health nonactivation current dependency hashes drifted")

    return {
        "schema": "paper09-final-freeze-after-historical-base-tier3-v2-obstruction-v1",
        "result_id": "PAPER09_FINAL_FREEZE_AFTER_HISTORICAL_BASE_TIER3_V2_OBSTRUCTION",
        "science_forge_work_item": "sf:program/work/observer-paper09-final-freeze-after-historical-base-tier3-v2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "decision": "DRAFT_ALLOWED",
        "theorem_frozen": False,
        "claim_map": {
            "path": str(MAP.relative_to(ROOT)),
            "sha256": current_map_sha,
            "claims": 22,
            "exact_imports": len(doc["exact_hash_imports"]),
            "coverage_status": coverage["status"],
        },
        "source_binding_obstruction": {
            "classification": "NO_SIMULTANEOUS_CONTENT_HASH_FIXED_POINT",
            "legacy_table_path": str(TABLE.relative_to(ROOT)),
            "legacy_table_sha256": table_sha,
            "publication_map_imports_current_legacy_table": True,
            "legacy_table_pinned_publication_map_sha256": pinned_map_sha,
            "regenerated_publication_map_sha256": current_map_sha,
            "legacy_table_imports_regenerated_publication_map": False,
            "scientific_claim_change": False,
        },
        "historical_base": {
            "path": str(historical_path.relative_to(root)),
            "sha256": digest(historical_path),
            "object_type": "blob",
            "source_commit": historical_ref["source_commit"],
            "source_sha256": historical_ref["sha256"],
            "dispositions_unchanged": True,
        },
        "post_repair_tier3": {
            "path": str(tier3_path.relative_to(root)),
            "sha256": digest(tier3_path),
            "status": "OBSTRUCTED",
            "passed_before_first_failure": 300,
            "first_failure_classification": tier3["first_failure"]["classification"],
            "green": False,
        },
        "transitive_health_nonactivation": {
            "path": str(health_path.relative_to(root)),
            "sha256": digest(health_path),
            "status": "OBSTRUCTED_PERSISTED_DEPENDENCY_DRIFT",
            "stale_dependency_count": len(health_dependency_drift),
            "stale_dependencies": health_dependency_drift,
            "scientific_disposition_changed": False,
        },
        "flags": {
            "SOURCE_BINDING_FIXED_POINT": False,
            "HISTORICAL_BASE_IMMUTABLE": True,
            "OBSERVER_TIER3_GREEN": False,
            "TRANSITIVE_HEALTH_CERTIFICATE_CURRENT": False,
            "OPERATIONAL_OBSERVABLE_PROMOTED": False,
            "THEOREM_FROZEN": False,
        },
        "does_not_establish": [
            "a theorem-frozen publication edition",
            "a complete green Observer Tier-3 traversal",
            "an operational receiver, frequency ratio or relational redshift",
            "a healthy repaired-q70 carrier",
            "a nonlinear, particle or quantum theorem",
        ],
        "next_typed_gate": "GIT_ATTACHED_EXACT_MATERIALIZATION_PREFLIGHT_AND_FRESH_TIER3_RUN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    doc = json.loads(MAP.read_text())
    receipt = verify_final_disposition(doc)
    if args.write_receipt:
        OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    print(
        "PASS PAPER09_FINAL_FREEZE_AFTER_HISTORICAL_BASE_TIER3_V2_OBSTRUCTION: "
        "DRAFT_ALLOWED source_binding_fixed_point=false observer_tier3_green=false"
    )


if __name__ == "__main__":
    main()
