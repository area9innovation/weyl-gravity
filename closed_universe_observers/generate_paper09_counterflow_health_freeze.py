#!/usr/bin/env python3
"""Generate the publication-current Paper 9 claim/evidence map."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def import_row(path: str, materiality: str, covered_by: list[str]) -> dict:
    file_path = ROOT / path
    data = json.loads(file_path.read_text()) if file_path.suffix == ".json" else {}
    return {
        "path": path,
        "result_id": data.get("result_id", file_path.stem),
        "sha256": sha256(file_path),
        "materiality": materiality,
        "covered_by": covered_by,
    }


def claim(claim_id: str, statement: str, classification: str, status: str,
          anchors: list[str], evidence: list[str], does_not_establish: list[str]) -> dict:
    return {
        "claim_id": claim_id,
        "statement": statement,
        "classification": classification,
        "status": status,
        "paper_anchors": anchors,
        "evidence_result_ids": evidence,
        "materiality": "MATERIAL",
        "does_not_establish": does_not_establish,
    }


def main() -> None:
    old_table_path = "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"
    old = load(old_table_path)
    phase_path = "closed_universe_observers/certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json"
    phase_payload = "closed_universe_observers/certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD.json"
    phase_receipt = "closed_universe_observers/receipts/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_TIER_RECEIPT.json"
    health_path = "closed_universe_observers/certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json"
    health_payload = "closed_universe_observers/certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD.json"
    health_receipt = "closed_universe_observers/receipts/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_TIER_RECEIPT.json"
    assembly_path = "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
    assembly = load(assembly_path)
    phase = load(phase_path)
    all_claim_ids = [f"P09-C{i}" for i in range(1, 11)] + [f"P09-O{i}" for i in range(1, 13)]

    claims: list[dict] = []
    old_classes = {
        "P09-C1": "KINEMATIC_FIXTURE", "P09-C2": "KINEMATIC_FIXTURE",
        "P09-C3": "KINEMATIC_FIXTURE", "P09-C4": "KINEMATIC_FIXTURE",
        "P09-C5": "ACTION_INTEGRATION", "P09-C6": "ACTION_INTEGRATION",
        "P09-C7": "ACTION_INTEGRATION", "P09-C8": "ACTION_INTEGRATION",
        "P09-C9": "ACTION_INTEGRATION", "P09-C10": "ACTION_INTEGRATION",
    }
    for item in old["claims"]:
        cid = item["claim_id"]
        claims.append(claim(
            cid, item["claim"], old_classes[cid], "CERTIFIED",
            ["main:" + cid, "supplement:" + cid], [item["certificate_result_id"]],
            ["operational observer algebra", "quantum or Lorentzian-causal theorem"],
        ))

    claims.extend([
        claim("P09-O1", "Charged physical time defines a BV-closed event-map current conditional on a nonzero descended receiver period.", "CONDITIONAL_THEOREM", "CERTIFIED_CONDITIONAL", ["main:charged physical time", "supplement:P09-O1"], ["CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1"], ["existence of a nonzero receiver period"]),
        claim("P09-O2", "Finite-resolution clock sampling preserves the conditional event-map identities and has the certified profile error bound.", "CONDITIONAL_THEOREM", "CERTIFIED_CONDITIONAL", ["main:finite clock resolution", "supplement:P09-O2"], ["CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1"], ["restoration of a clock removed by fixed-charge reduction"]),
        claim("P09-O3", "Frequency-comparison reciprocity, composition and loop laws hold only with declared retarded paths, fibre crosswalks and nonzero sampled records.", "CONDITIONAL_THEOREM", "CERTIFIED_CONDITIONAL", ["main:conditional frequency comparisons", "supplement:P09-O3"], ["CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1"], ["a physical redshift on the counterflow carrier"]),
        claim("P09-O4", "The physical-receiver and charge-fibre crosswalk is a conditional admissibility interface, not a populated receiver.", "CONDITIONAL_THEOREM", "CERTIFIED_INTERFACE", ["main:physical-receiver interface", "supplement:P09-O4"], ["CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1"], ["existence of an action-derived receiver"]),
        claim("P09-O5", "The legacy G0 value one-plus-z=2 is certified only as a spatially global retarded probe-mode observable on its hashed carrier and is not an operational redshift.", "KINEMATIC_FIXTURE", "CERTIFIED_CARRIER_SCOPED", ["main:legacy Berger apparatus", "supplement:P09-O5"], ["BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE"], ["localized receiver record", "operational redshift"]),
        claim("P09-O6", "Three legacy source-to-probe transfer matrices retain exact rank two on their distinct pre-quotient carriers.", "KINEMATIC_FIXTURE", "CERTIFIED_CARRIER_SCOPED", ["main:three exact matrices", "supplement:P09-O6"], ["BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1"], ["physical detector algebra", "cross-carrier mode identity"]),
        claim("P09-O7", "The legacy receiver census has no operational frequency-ratio domain; its homogeneous coordinate ratio one is not relational redshift.", "NOT_ACTIVATED", "NO_CERTIFIED_MAP", ["main:no operational frequency ratio", "supplement:P09-O7"], ["BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1"], ["operational observable"]),
        claim("P09-O8", "The standalone D0 memory-shift receiver has a certified local BV descent only.", "LOCAL_BV_CLASS", "CERTIFIED_LOCAL_ONLY", ["main:standalone D0 receiver", "supplement:P09-O8"], ["POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1"], ["ambient action integration", "physical descent"]),
        claim("P09-O9", "The degree-zero local-cochain to repaired-q70 chain inclusion is obstructed by the opposite differential degrees.", "ACTION_INTEGRATION", "OBSTRUCTED", ["main:fresh rederivation", "supplement:P09-O9"], ["POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1", "POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1"], ["receiver quotient", "suspension bridge"]),
        claim("P09-O10", "Phase 1 ends with no residual nonradical receiver period and no operational frequency-ratio map.", "PHYSICAL_DESCENT", "NO_CERTIFIED_MAP", ["main:Phase 1 exact-obstruction endpoint", "supplement:P09-O10"], ["POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1", "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1"], ["operational observable", "new receiver architecture"]),
        claim("P09-O11", "For repaired-q70 modes with j at least 3/2, the physical quotient, divisor and pairing remain open with NO_CERTIFIED_MAP.", "OPEN", "NO_CERTIFIED_MAP", ["main:j greater than or equal to three halves", "supplement:P09-O11"], ["TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1"], ["higher-mode health extrapolation"]),
        claim("P09-O12", "Every certified repaired-q70 physical block at j=0,1/2,1 is unstable; fixed Q_rel removes the clock, so the thirteen-field operational ratio domain is empty and NOT_ACTIVATED.", "NOT_ACTIVATED", "NO_CERTIFIED_MAP", ["main:certified block is physically unstable", "supplement:P09-O12"], ["COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1", "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1"], ["healthy receiver carrier", "detector value", "relational redshift"]),
    ])

    imports: list[dict] = []
    seen: set[str] = set()

    def add(path: str, materiality: str, covered_by: list[str]) -> None:
        if path not in seen:
            imports.append(import_row(path, materiality, covered_by))
            seen.add(path)

    add(old_table_path, "authoritative ten-claim classical ledger", [f"P09-C{i}" for i in range(1, 11)])
    theorem_paths = {
        "closed_universe_observers/certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json": ["P09-O1"],
        "closed_universe_observers/certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json": ["P09-O2"],
        "closed_universe_observers/certificates/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1.json": ["P09-O3"],
    }
    for path, edge in theorem_paths.items():
        add(path, "observer conditional theorem headline", edge)
    dep_to_claim = {
        "charged_time_admissibility": ["P09-O4"], "legacy_g0_probe_observable": ["P09-O5"],
        "legacy_receiver_replay": ["P09-O6"], "legacy_ratio_nonactivation": ["P09-O7"],
        "standalone_receiver_preflight": ["P09-O8"], "original_grading_obstruction": ["P09-O9"],
        "regraded_integration_obstruction": ["P09-O9"], "terminal_physical_nonactivation": ["P09-O10"],
    }
    for key, ref in phase["dependency_refs"].items():
        add(ref["path"], "Phase 1 observer headline or negative result", dep_to_claim[key])
    for path in (phase_path, phase_payload, phase_receipt):
        add(path, "terminal Phase 1 result, payload or verification receipt", ["P09-O10"])
    for path in (health_path, health_payload, health_receipt):
        add(path, "terminal health-based receiver nonactivation result, payload or receipt", ["P09-O12"])
    add(assembly_path, "action-derived maximal certified health assembly", ["P09-O11", "P09-O12"])
    assembly_payload = "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
    assembly_receipt = "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1_TIER_RECEIPT.json"
    add(assembly_payload, "health assembly exact payload", ["P09-O11", "P09-O12"])
    add(assembly_receipt, "health assembly verification receipt", ["P09-O11", "P09-O12"])
    for ref in assembly["imports"].values():
        add(ref["path"], "transitive action-derived health input", ["P09-O11", "P09-O12"])
    event_globs = (
        "planning/events/observer-phase1-relational-observable-disposition-synthesis-DONE-*.json",
        "planning/events/observer-phase1-relational-observable-disposition-synthesis-REPORT-*.json",
        "planning/events/observer-phase1-relational-observable-disposition-synthesis-LEASE-RELEASE-excl-*.json",
        "planning/events/observer-counterflow-charged-time-physical-instantiation-after-repaired-q70-health-DONE-*.json",
        "planning/events/observer-counterflow-charged-time-physical-instantiation-after-repaired-q70-health-REPORT-*.json",
        "planning/events/observer-counterflow-charged-time-physical-instantiation-after-repaired-q70-health-LEASE-RELEASE-excl-*.json",
    )
    for pattern in event_globs:
        matches = sorted(ROOT.glob(pattern))
        if len(matches) != 1:
            raise RuntimeError(f"expected one terminal event for {pattern}, got {len(matches)}")
        edge = ["P09-O10"] if "phase1-relational" in pattern else ["P09-O12"]
        add(str(matches[0].relative_to(ROOT)), "terminal Science Forge lifecycle evidence", edge)

    final_dependency_imports = {
        "d_quotient_classical/receipts/PAPER_09_LEGACY_CLAIM_BINDING_REPIN_V1_TIER_RECEIPT.json": (
            "terminal Classical Paper 9 source-binding repin receipt", [f"P09-C{i}" for i in range(1, 11)]
        ),
        "closed_universe_observers/receipts/PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1_TIER_RECEIPT.json": (
            "predecessor Paper 9 DRAFT_ALLOWED evidence receipt", all_claim_ids
        ),
        "reports/observer-paper09-counterflow-health-nonactivation-freeze-closeout-2026-07-21.md": (
            "predecessor Paper 9 DRAFT_ALLOWED closeout", all_claim_ids
        ),
        "planning/events/observer-paper09-counterflow-health-nonactivation-freeze-OBSTRUCTED-c004263fe35d9f83.json": (
            "terminal predecessor publication lifecycle disposition", all_claim_ids
        ),
        "closed_universe_observers/receipts/OBSERVER_LEGACY_RECEIVER_HISTORICAL_BASE_BINDING_REPAIR_V1_MANIFEST.json": (
            "immutable historical five-row binding repair manifest", ["P09-O6", "P09-O7"]
        ),
        "reports/observer-legacy-receiver-historical-base-binding-repair-v1-closeout-2026-07-21.md": (
            "historical-base repair closeout", ["P09-O6", "P09-O7"]
        ),
        "closed_universe_observers/receipts/OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1_OBSTRUCTION.json": (
            "fresh post-repair Observer Tier-3 obstruction", all_claim_ids
        ),
        "closed_universe_observers/receipts/OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1_TIER_RECEIPT.json": (
            "fresh post-repair Observer Tier-3 verification receipt", all_claim_ids
        ),
        "reports/observer-tier3-fixed-point-after-historical-base-binding-repair-v1-closeout-2026-07-21.md": (
            "fresh post-repair Observer Tier-3 closeout", all_claim_ids
        ),
        "closed_universe_observers/receipts/OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1.json": (
            "standalone current-input revalidation with unchanged scientific projections",
            ["P09-O10", "P09-O12"],
        ),
    }
    for path, (materiality, edge) in final_dependency_imports.items():
        add(path, materiality, edge)

    classifications = [item["classification"] for item in claims]
    counts = Counter(classifications)
    for allowed in ("CONDITIONAL_THEOREM", "KINEMATIC_FIXTURE", "LOCAL_BV_CLASS", "ACTION_INTEGRATION", "PHYSICAL_DESCENT", "OPERATIONAL_OBSERVABLE", "NOT_ACTIVATED", "OPEN"):
        counts.setdefault(allowed, 0)
    source_files = [
        "paper/09-relational-clocks-berger-d-cartan.tex",
        "paper/09-relational-clocks-berger-d-cartan-computational-supplement.tex",
    ]
    result = {
        "schema": "paper09-publication-claim-map-v1",
        "result_id": "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1",
        "paper": "09-relational-clocks-berger-d-cartan",
        "freeze_decision": "DRAFT_ALLOWED",
        "draft_allowed_gates": [
            {
                "gate": "LEGACY_TEN_CLAIM_SOURCE_BINDING_SUPERSESSION",
                "status": "OBSTRUCTED_RECURSIVE_EXACT_HASH_EDGE",
                "failure": "Regenerating this 22-claim map imports the repinned PAPER_09_BERGER_CLAIM_TABLE exactly, but that table pins the pre-regeneration 22-claim map hash; the two current-path hash edges have no simultaneous fixed point.",
                "closure": "Issue an acyclic source-binding authority: the legacy ledger may bind immutable source objects, but must not content-address the mutable publication map that content-addresses the ledger.",
            },
            {
                "gate": "OBSERVER_STREAM_TIER3_GREEN",
                "status": "OBSTRUCTED_TEST_HARNESS_MATERIALIZATION_INTERFACE_DEFECT",
                "failure": "The single fresh post-repair fail-fast traversal passed 300 tests, then stopped because the exact archive lacked Git administrative metadata required by generate_berger_detector_records.py.",
                "closure": "Run the typed Git-attached exact-materialization successor from zero and require a complete green Observer suite; no prior partial run is credited.",
            },
        ],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "claim_boundary": "The ten classical theorem claims retain their prior scientific scope. The publication-current edition remains DRAFT_ALLOWED at two exact terminal evidence boundaries: a recursive bidirectional source-hash edge and a non-green post-repair Observer Tier-3 traversal. Observer entries preserve conditional theorems and carrier-scoped kinematic responses, but certify no populated operational observable on the tested counterflow point.",
        "source_hashes": [{"path": path, "sha256": sha256(ROOT / path)} for path in source_files],
        "exact_hash_imports": imports,
        "claims": claims,
        "classification_counts": dict(sorted(counts.items())),
        "operational_observable_disposition": {
            "classified_claim_count": counts["OPERATIONAL_OBSERVABLE"],
            "status": "NOT_ACTIVATED",
            "reason": "No certified carrier combines a healthy physical clock, action-derived descended receiver, nonradical period, retarded record and positive sampled denominator.",
        },
        "health_disposition": {
            "certified_modes": ["j=0", "j=1/2", "j=1"],
            "all_certified_physical_blocks": "UNSTABLE",
            "fixed_Q_rel": "CLOCK_REMOVED",
            "higher_j": "NO_CERTIFIED_MAP",
            "thirteen_field_operational_ratio_domain": "EMPTY",
        },
        "generator_semantics": {"K": "D-omega R", "K_equals_D": False, "raw_D_affine": True},
        "final_disposition": {
            "version": 2,
            "status": "DRAFT_ALLOWED",
            "theorem_frozen": False,
            "classical_source_binding_item": "DONE_BUT_NO_BIDIRECTIONAL_HASH_FIXED_POINT",
            "historical_base_binding": "CERTIFIED_IMMUTABLE_BLOB",
            "post_repair_observer_tier3": "OBSTRUCTED_TEST_HARNESS_MATERIALIZATION_INTERFACE_DEFECT",
            "transitive_health_nonactivation": "OBSTRUCTED_THREE_STALE_HISTORICAL_BASE_DEPENDENCY_HASHES",
            "reason_codes": [
                "RECURSIVE_PUBLICATION_LEDGER_HASH_EDGE",
                "OBSERVER_TIER3_NOT_GREEN",
                "TRANSITIVE_HEALTH_NONACTIVATION_CERTIFICATE_STALE_AFTER_HISTORICAL_REPAIR",
            ],
        },
        "source_binding_fixed_point": {
            "publication_map_imports_current_legacy_table": True,
            "legacy_table_imports_regenerated_publication_map": False,
            "cycle_present": True,
            "classification": "NO_SIMULTANEOUS_CONTENT_HASH_FIXED_POINT",
        },
        "coverage": {
            "material_import_count": len(imports),
            "uncovered_material_results": [],
            "all_material_imports_have_result_to_paper_edges": all(row["covered_by"] for row in imports),
        },
        "mutation_guards": [
            "STALE_HEALTHY_CARRIER", "COORDINATE_RATIO_AS_REDSHIFT", "K_EQUALS_D",
            "TIER3_OBSTRUCTION_AS_GREEN", "SOURCE_BINDING_CYCLE_AS_PASS",
            "HISTORICAL_BLOB_AS_MUTABLE_CURRENT_PATH", "DRAFT_ALLOWED_AS_THEOREM_FROZEN",
        ],
        "does_not_establish": [
            "a new receiver, suspension, apparatus, compensator or action architecture",
            "a healthy retuned point", "a detector or relational-redshift value",
            "an affine D-Cartan theorem", "a quantum, particle, phenomenology or unitarity claim",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(claims)} claims, {len(imports)} imports)")


if __name__ == "__main__":
    main()
