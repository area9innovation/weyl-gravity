#!/usr/bin/env python3
"""Independent verification of the corrected observer interaction import gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_observer_interaction_import_gate_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-input-v2.schema.json"
SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-v2.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json"


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _requirements(data: dict, patch: dict | None = None) -> dict[str, bool]:
    clone = json.loads(json.dumps(data))
    imported = clone["imported_complex"]
    baseline = clone["probe_record_baseline"]
    model = clone["apparatus_model"]
    for key, value in (patch or {}).items():
        if key in imported:
            imported[key] = value
        elif key in baseline:
            baseline[key] = value
        elif key == "linear_relational_operation":
            clone["action_arity_ledger"][1]["induced_operation"] = value
        elif key == "polarization_model":
            model["polarization"] = value
        else:
            clone[key] = value
    missing = [row for row in clone["required_interface_blocks"] if row["status"] != "EXPORTED_VERIFIED"]
    return {
        "repaired_q2_import_exact": imported["row_count"] == 64 and imported["q2_repair_applied"] and imported["q1_q2_defect_count"] == 0 and imported["cyclicity_defect_count"] == 0 and imported["k_berger_arity_two_equivariant"] and imported["maxwell_stress_vertex_exported"],
        "probe_rank_two_baseline_exact": baseline["transfer_rank"] == 2 and baseline["persistent_records_distinguishable"],
        "action_arity_convention_exact": all(row["action_degree"] == row["input_arity"] + 1 and row["induced_operation"] == f"q{row['input_arity']}" for row in clone["action_arity_ledger"]),
        "apparatus_model_boundary_explicit": model["polarization"] == "COMPOSITE_P_A_EQUALS_DTHETA_WEDGE_DRA_NO_INDEPENDENT_POLARIZATION_ROWS" and model["source_role"] == "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE_AT_THIS_GATE" and model["dynamical_emitter_deferred"],
        "extended_linear_survival_fail_closed": not clone["request_extended_linear_survival_promotion"] and not baseline["extended_q1_exported"] and not baseline["extended_retarded_green_exported"],
        "team_handoff_preserved": not clone["construct_interaction_tensors_locally"],
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
    if support["row_layout"]["total_rows"] != 64 or support["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("support-local 64-row q2 identity drifted")
    row_ids = {row["row_id"] for row in support["row_layout"]["component_rows"]}
    if any(row.startswith(("rod_", "memory_", "detector_", "emitter_", "m_", "p_")) for row in row_ids):
        raise AssertionError("apparatus row unexpectedly entered the pinned 64-row ledger")
    if not all(_requirements(data).values()):
        raise AssertionError("base corrected import gate failed")
    persisted = {row["name"]: row for row in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        required = mutation["expected_failed_requirement"]
        if _requirements(data, mutation["patch"])[required] is not False:
            raise AssertionError(f"mutation did not fail: {mutation['name']}")
        if persisted[mutation["name"]]["observed_requirement_value"] is not False:
            raise AssertionError(f"persisted mutation mismatch: {mutation['name']}")
    ledger = certificate["action_arity_analysis"]["ledger"]
    if [(row["action_degree"], row["induced_operation"]) for row in ledger] != [(2, "q1"), (3, "q2"), (4, "q3")]:
        raise AssertionError("action-to-operation arity is off by one")
    flags = certificate["flags"]
    if not flags["PROBE_LIMIT_RANK_TWO_BASELINE_IMPORTED"] or not flags["FORMAL_RANK_TWO_STABILITY_CONDITIONAL_LEMMA"]:
        raise AssertionError("probe baseline or conditional determinant lemma dropped")
    for forbidden in ["EXTENDED_APPARATUS_Q1_CERTIFIED", "EXTENDED_RETARDED_GREEN_CERTIFIED", "EXTENDED_LINEAR_RANK_TWO_TRANSFER_CERTIFIED", "EXTENDED_CYCLICITY_CERTIFIED", "INTERACTING_OBSERVER_DEFORMATION_CONSTRUCTED", "CLASSICAL_OBSERVER_MAP_CERTIFIED"]:
        if flags[forbidden] is not False:
            raise AssertionError(f"illegal promotion: {forbidden}")
    print("BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE v2 independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
