#!/usr/bin/env python3
"""Independent verification of the Berger observer interaction import gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_observer_interaction_import_gate_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json"


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _requirements(data: dict, patch: dict | None = None) -> dict[str, bool]:
    clone = json.loads(json.dumps(data))
    override = patch or {}
    imported = clone["imported_complex"]
    linear = clone["linear_record_sector"]
    for key, value in override.items():
        if key in imported:
            imported[key] = value
        elif key in linear:
            linear[key] = value
        else:
            clone[key] = value
    missing = [row for row in clone["required_operation_blocks"] if row["status"] != "EXPORTED_VERIFIED"]
    return {
        "repaired_q2_import_exact": imported["row_count"] == 64 and imported["q2_repair_applied"] and imported["q1_q2_defect_count"] == 0 and imported["cyclicity_defect_count"] == 0 and imported["k_berger_arity_two_equivariant"] and imported["maxwell_stress_vertex_exported"],
        "linear_rank_two_records_survive": linear["transfer_rank"] == 2 and linear["persistent_records_distinguishable"],
        "apparatus_extension_incomplete": bool(missing),
        "higher_arity_observer_terms_identified": clone["relational_smearing_depends_on_rods"] and clone["memory_couples_to_maxwell_readout"],
        "generator_boundary_preserved": not clone["treat_raw_d_as_k_berger"] and not imported["raw_d_arity_two_equivariant"],
        "nonlinear_promotion_fail_closed": not clone["request_nonlinear_promotion"] and bool(missing),
    }


def main() -> int:
    data = json.loads(INPUT.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    for path, payload in [(INPUT_SCHEMA, data), (SCHEMA, certificate)]:
        schema = json.loads(path.read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(payload)
    if certificate["provenance"]["declared_input_sha256"] != _hash(INPUT):
        raise AssertionError("interaction gate input drifted")
    for source in certificate["provenance"]["source_manifest"]:
        if _hash(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")
    pinned_payloads = {}
    for name, dependency in certificate["dependency_refs"].items():
        raw = subprocess.check_output(["git", "show", f"{dependency['snapshot_commit']}:{_prefix()}{dependency['path']}"], cwd=ROOT)
        pinned = json.loads(raw)
        pinned_payloads[name] = pinned
        if _hash_bytes(raw) != dependency["sha256"] or pinned["result_id"] != dependency["result_id"]:
            raise AssertionError(f"pinned dependency mismatch: {name}")
        live = json.loads((ROOT / dependency["path"]).read_text())
        if any(live.get("flags", {}).get(flag) is not True for flag in dependency["live_required_flags"]):
            raise AssertionError(f"live dependency compatibility dropped: {name}")
    support = pinned_payloads["support_local_q2"]
    if support["row_layout"]["total_rows"] != 64:
        raise AssertionError("support-local complex is no longer 64 rows")
    if support["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("support-local q1-q2 defect reappeared")
    if not support["exact_checks"]["BV_cyclicity_from_common_Maxwell_master_action"]:
        raise AssertionError("support-local cyclicity dropped")
    row_ids = {row["row_id"] for row in support["row_layout"]["component_rows"]}
    forbidden_prefixes = ("rod_", "memory_", "detector_", "emitter_", "m_", "p_")
    if any(row.startswith(forbidden_prefixes) for row in row_ids):
        raise AssertionError("apparatus row unexpectedly entered the pinned 64-row ledger")
    if not all(_requirements(data).values()):
        raise AssertionError("base interaction import gate failed")
    persisted = {row["name"]: row for row in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        required = mutation["expected_failed_requirement"]
        if _requirements(data, mutation["patch"])[required] is not False:
            raise AssertionError(f"mutation did not fail: {mutation['name']}")
        if persisted[mutation["name"]]["observed_requirement_value"] is not False:
            raise AssertionError(f"persisted mutation mismatch: {mutation['name']}")
    flags = certificate["flags"]
    if flags["LINEAR_RANK_TWO_RECORD_TRANSFER_PRESERVED"] is not True:
        raise AssertionError("linear survival flag dropped")
    for forbidden in ["OBSERVER_APPARATUS_ROWS_ADJOINED_TO_REPAIRED_COMPLEX", "EXTENDED_CYCLICITY_CERTIFIED", "RAW_D_DESCENT_WITH_APPARATUS_CERTIFIED", "BACKREACTED_RANK_TWO_RECORDS_CERTIFIED", "CLASSICAL_OBSERVER_MAP_CERTIFIED"]:
        if flags[forbidden] is not False:
            raise AssertionError(f"illegal promotion: {forbidden}")
    print("BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
