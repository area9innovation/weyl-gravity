#!/usr/bin/env python3
"""Independent audit of the Phase-1 counterflow overview publication update."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "planning/paper-coverage/classical-phase1-counterflow-overview-publication-2026-07-21.json"
SCHEMA = ROOT / "planning/paper-coverage/classical-phase1-counterflow-overview-publication-v1.schema.json"
EXPECTED_SOURCES = {
    "claim_map": ("d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json", "PHASE1_CLASSICAL_COUNTERFLOW_CHAIN_FROZEN_TERMINAL_OBSTRUCTED"),
    "selected_causal_parent": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json", "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT"),
    "phase1_viability": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json", "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK"),
}
PAPERS = {
    "00": ("paper/00-ghosts-geometry-reality.tex", "paper/00-ghosts-geometry-reality.pdf"),
    "98": ("paper/98-physicist-executive-summary.md", "paper/98-physicist-executive-summary.pdf"),
    "99": ("paper/99-how-to-build-a-universe.md", "paper/99-how-to-build-a-universe.pdf"),
}
TEXT_WITNESSES = {
    "00": ["Causality is not physical", "no robust linearly healthy Phase~2 candidate", "not a no-go for changed field content"],
    "98": ["no open or structurally protected linearly", "selected-fixture causal parent", "not a no-go for changed field content"],
    "99": ["not selected for Phase 2", "this a theorem against every possible new clock", "rule out a genuinely changed"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(payload: dict[str, Any], check_hashes: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["result_state"] == "PUBLICATION_CURRENT_TERMINAL_PHASE1_COUNTERFLOW_DISPOSITION"
    assert set(payload["imports"]) == set(EXPECTED_SOURCES)
    if check_hashes:
        for role, (relative, state) in EXPECTED_SOURCES.items():
            ref = payload["imports"][role]
            assert ref["path"] == relative
            source = json.loads((ROOT / relative).read_text())
            assert source["result_state"] == state == ref["result_state"]
            assert source["result_id"] == ref["result_id"]
            assert sha(ROOT / relative) == ref["sha256"]
        for paper, (source, pdf) in PAPERS.items():
            ref = payload["publication_refs"][paper]
            assert ref["source_path"] == source and ref["pdf_path"] == pdf
            assert ref["source_sha256"] == sha(ROOT / source)
            assert ref["pdf_sha256"] == sha(ROOT / pdf)
            assert ref["publication_edit"] == "PERFORMED_AND_VERIFIED"
            text = (ROOT / source).read_text()
            assert all(witness in text for witness in TEXT_WITNESSES[paper])
    claims = payload["claims_propagated"]
    assert claims["selected_fixture_causal_parent"] is True
    assert claims["selected_fixture_dressed_trace_removed"] is True
    false_claims = set(claims) - {"selected_fixture_causal_parent", "selected_fixture_dressed_trace_removed"}
    assert all(claims[key] is False for key in false_claims)
    assert all(value == "REJECT" for value in payload["mutation_expectations"].values())


def reject(payload: dict[str, Any], mutate: Callable[[dict[str, Any]], None]) -> None:
    candidate = copy.deepcopy(payload)
    mutate(candidate)
    try:
        verify(candidate, check_hashes=False)
    except (AssertionError, KeyError, ValidationError):
        return
    raise AssertionError("publication contradiction mutation accepted")


def main() -> int:
    payload = json.loads(RECORD.read_text())
    verify(payload)
    mutations = [
        lambda p: p["claims_propagated"].update(causal_parent_implies_physical_health=True),
        lambda p: p["claims_propagated"].update(fixed_Q_rel_retains_physical_clock=True),
        lambda p: p["claims_propagated"].update(familywide_same_field_stable_candidate=True),
        lambda p: p["claims_propagated"].update(higher_isotype_retuning_spectrum_complete=True),
        lambda p: p["claims_propagated"].update(universal_changed_architecture_no_go=True),
        lambda p: p["claims_propagated"].update(phase2_candidate_selected=True),
    ]
    for mutation in mutations:
        reject(payload, mutation)
    print(f"CLASSICAL_PHASE1_COUNTERFLOW_OVERVIEW_PUBLICATION_UPDATE_V1 independent verification: PASS ({len(mutations)} mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
