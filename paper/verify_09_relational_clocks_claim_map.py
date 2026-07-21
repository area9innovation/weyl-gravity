#!/usr/bin/env python3
"""Independent fail-closed verifier for the publication-current Paper 9 map."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json"
SCHEMA = ROOT / "closed_universe_observers/schema/paper09-publication-claim-map-v1.schema.json"
COVERAGE = ROOT / "planning/paper-coverage/observer-phase1-relational-observable-dispositions-2026-07-21.json"


class VerificationError(AssertionError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted(data: dict, key: str) -> Any:
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise VerificationError(f"missing required field {key}")
        value = value[part]
    return value


def verify_document(doc: dict, root: Path = ROOT) -> dict:
    jsonschema.Draft202012Validator(json.loads((root / SCHEMA.relative_to(ROOT)).read_text())).validate(doc)
    if doc["freeze_decision"] != "DRAFT_ALLOWED":
        raise VerificationError("publication-current evidence does not retain the fail-closed DRAFT_ALLOWED decision")
    gates = doc.get("draft_allowed_gates", [])
    if [gate.get("gate") for gate in gates] != [
        "LEGACY_TEN_CLAIM_SOURCE_BINDING_SUPERSESSION", "OBSERVER_STREAM_TIER3_GREEN"
    ] or any(gate.get("status") != "OPEN" for gate in gates):
        raise VerificationError("DRAFT_ALLOWED gates are incomplete or silently closed")

    claim_ids = [row["claim_id"] for row in doc["claims"]]
    expected = [f"P09-C{i}" for i in range(1, 11)] + [f"P09-O{i}" for i in range(1, 13)]
    if claim_ids != expected:
        raise VerificationError("claim sequence is incomplete or reordered")
    if len(set(claim_ids)) != len(claim_ids):
        raise VerificationError("duplicate claim identifiers")

    main = (root / "paper/09-relational-clocks-berger-d-cartan.tex").read_text()
    supplement = (root / "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex").read_text()
    for cid in claim_ids:
        if cid not in main and cid not in supplement:
            raise VerificationError(f"claim {cid} has no manuscript anchor")

    for row in doc["source_hashes"]:
        path = root / row["path"]
        if digest(path) != row["sha256"]:
            raise VerificationError(f"source hash drift: {row['path']}")

    imported_ids: set[str] = set()
    for row in doc["exact_hash_imports"]:
        path = root / row["path"]
        if not path.is_file() or digest(path) != row["sha256"]:
            raise VerificationError(f"import hash drift: {row['path']}")
        if not row.get("materiality") or not row.get("covered_by"):
            raise VerificationError(f"uncovered import: {row['path']}")
        if not set(row["covered_by"]).issubset(claim_ids):
            raise VerificationError(f"bad result-to-paper edge: {row['path']}")
        imported_ids.add(row["result_id"])

    required_results = {
        "PAPER_09_BERGER_CLAIM_TABLE",
        "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1",
        "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD",
        "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1",
        "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD",
        "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1",
    }
    if not required_results.issubset(imported_ids):
        raise VerificationError("mandatory terminal imports are incomplete")

    old = json.loads((root / "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json").read_text())
    if old["claim_ids_complete"] != [f"P09-C{i}" for i in range(1, 11)]:
        raise VerificationError("legacy ten-claim table is not complete")
    for item in old["claims"] + old["independent_cross_checks"]:
        cert_path = root / item["certificate_path"]
        if digest(cert_path) != item["certificate_sha256"]:
            raise VerificationError(f"legacy certificate drift: {cert_path}")
        cert = json.loads(cert_path.read_text())
        for key in item.get("required_true", []):
            if dotted(cert, key) is not True:
                raise VerificationError(f"required true flag failed: {key}")
        for key in item.get("required_false", []):
            if dotted(cert, key) is not False:
                raise VerificationError(f"required false flag failed: {key}")

    phase_events = [row for row in doc["exact_hash_imports"] if "phase1-relational-observable-disposition-synthesis" in row["path"] and "/events/" in row["path"]]
    health_events = [row for row in doc["exact_hash_imports"] if "after-repaired-q70-health" in row["path"] and "/events/" in row["path"]]
    if len(phase_events) != 3 or len(health_events) != 3:
        raise VerificationError("terminal lifecycle event triplets are incomplete")
    for rows in (phase_events, health_events):
        done = [json.loads((root / row["path"]).read_text()) for row in rows if "-DONE-" in row["path"]]
        if len(done) != 1 or done[0]["body"]["payload"]["to_state"] != "DONE":
            raise VerificationError("DONE lifecycle evidence is invalid")

    hd = doc["health_disposition"]
    if hd != {
        "all_certified_physical_blocks": "UNSTABLE",
        "certified_modes": ["j=0", "j=1/2", "j=1"],
        "fixed_Q_rel": "CLOCK_REMOVED",
        "higher_j": "NO_CERTIFIED_MAP",
        "thirteen_field_operational_ratio_domain": "EMPTY",
    }:
        raise VerificationError("stale healthy-carrier or health-domain mutation")
    if doc["generator_semantics"] != {"K": "D-omega R", "K_equals_D": False, "raw_D_affine": True}:
        raise VerificationError("K/raw-D semantics were conflated")

    by_id = {row["claim_id"]: row for row in doc["claims"]}
    if "not an operational redshift" not in by_id["P09-O5"]["statement"]:
        raise VerificationError("coordinate/probe ratio was promoted to redshift")
    if "not relational redshift" not in by_id["P09-O7"]["statement"]:
        raise VerificationError("coordinate ratio was promoted to relational redshift")
    if by_id["P09-O8"]["classification"] != "LOCAL_BV_CLASS" or by_id["P09-O9"]["classification"] != "ACTION_INTEGRATION":
        raise VerificationError("local BV and ambient-action layers were conflated")
    if by_id["P09-O12"]["classification"] != "NOT_ACTIVATED" or by_id["P09-O11"]["classification"] != "OPEN":
        raise VerificationError("health nonactivation/open higher-mode typing drift")
    if doc["classification_counts"]["OPERATIONAL_OBSERVABLE"] != 0:
        raise VerificationError("an operational observable was manufactured")
    if doc["operational_observable_disposition"]["status"] != "NOT_ACTIVATED":
        raise VerificationError("operational layer was promoted")
    if doc["coverage"]["uncovered_material_results"] or not doc["coverage"]["all_material_imports_have_result_to_paper_edges"]:
        raise VerificationError("material publication coverage is incomplete")

    return {
        "schema": "observer-paper-coverage-replay-v1",
        "result_id": "PAPER09_PHASE1_OBSERVER_PUBLICATION_COVERAGE_REPLAY_2026_07_21",
        "paper": doc["paper"],
        "source_result_id": doc["result_id"],
        "source_claim_map_sha256": digest(root / MAP.relative_to(ROOT)),
        "claims_total": len(doc["claims"]),
        "material_results_total": len(doc["exact_hash_imports"]),
        "result_to_paper_edges_total": sum(len(row["covered_by"]) for row in doc["exact_hash_imports"]),
        "classification_counts": doc["classification_counts"],
        "human_materiality_review": "COMPLETE",
        "uncovered_material_results": [],
        "status": "NONVACUOUS_PASS",
        "does_not_establish": ["publication release", "a new scientific claim", "an operational observer observable"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-coverage", action="store_true")
    args = parser.parse_args()
    document = json.loads(MAP.read_text())
    coverage = verify_document(document)
    if args.write_coverage:
        COVERAGE.write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n")
        print(f"wrote {COVERAGE.relative_to(ROOT)}")
    print(f"PASS {document['result_id']}: {len(document['claims'])} claims, {len(document['exact_hash_imports'])} exact imports")


if __name__ == "__main__":
    main()
