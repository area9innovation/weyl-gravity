#!/usr/bin/env python3
"""Generate the Phase-1 counterflow overview publication coverage record."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "planning/paper-coverage/classical-phase1-counterflow-overview-publication-2026-07-21.json"
SOURCES = {
    "claim_map": (
        "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json",
        "PHASE1_CLASSICAL_COUNTERFLOW_CHAIN_FROZEN_TERMINAL_OBSTRUCTED",
    ),
    "selected_causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT",
    ),
    "phase1_viability": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
        "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
    ),
}
PAPERS = {
    "00": ("paper/00-ghosts-geometry-reality.tex", "paper/00-ghosts-geometry-reality.pdf"),
    "98": ("paper/98-physicist-executive-summary.md", "paper/98-physicist-executive-summary.pdf"),
    "99": ("paper/99-how-to-build-a-universe.md", "paper/99-how-to-build-a-universe.pdf"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build() -> dict[str, Any]:
    imports: dict[str, Any] = {}
    documents: dict[str, Any] = {}
    for role, (relative, state) in SOURCES.items():
        path = ROOT / relative
        data = json.loads(path.read_text())
        assert data["result_state"] == state
        imports[role] = {
            "path": relative,
            "result_id": data["result_id"],
            "result_state": state,
            "sha256": sha(path),
        }
        documents[role] = data

    claim_map = documents["claim_map"]
    viability = documents["phase1_viability"]
    assert claim_map["terminal_summary"] == {
        "familywide_same_field_stable_candidate": False,
        "fixed_Q_rel_retains_physical_clock": False,
        "phase2_candidate_selected": False,
        "selected_fixture_causal_parent": True,
        "selected_fixture_dressed_trace_removed": True,
        "selected_fixture_physically_healthy": False,
    }
    assert viability["decision"]["robust_stationary_retuning_exists"] is False

    publication_refs = {}
    for paper, (source, pdf) in PAPERS.items():
        publication_refs[paper] = {
            "source_path": source,
            "source_sha256": sha(ROOT / source),
            "pdf_path": pdf,
            "pdf_sha256": sha(ROOT / pdf),
            "publication_edit": "PERFORMED_AND_VERIFIED",
        }

    return {
        "$schema": "classical-phase1-counterflow-overview-publication-v1.schema.json",
        "schema": "classical-phase1-counterflow-overview-publication-v1",
        "result_id": "CLASSICAL_PHASE1_COUNTERFLOW_OVERVIEW_PUBLICATION_UPDATE_V1",
        "result_state": "PUBLICATION_CURRENT_TERMINAL_PHASE1_COUNTERFLOW_DISPOSITION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "publication_refs": publication_refs,
        "claims_propagated": {
            "selected_fixture_causal_parent": True,
            "selected_fixture_dressed_trace_removed": True,
            "causal_parent_implies_physical_health": False,
            "fixed_Q_rel_retains_physical_clock": False,
            "selected_fixture_physically_healthy": False,
            "familywide_same_field_stable_candidate": False,
            "phase2_candidate_selected": False,
            "higher_isotype_retuning_spectrum_complete": False,
            "universal_changed_architecture_no_go": False,
        },
        "paper_dispositions": {
            "00": "PROGRAMME_SYNTHESIS_CURRENT",
            "98": "EXECUTIVE_STATUS_CURRENT",
            "99": "PUBLIC_SCORECARD_CURRENT",
        },
        "mutation_expectations": {
            "causal_equals_healthy": "REJECT",
            "fixed_charge_retains_clock": "REJECT",
            "selected_point_only": "REJECT",
            "higher_isotype_extrapolation": "REJECT",
            "universal_no_go": "REJECT",
            "source_hash_changed": "REJECT",
            "paper_hash_changed": "REJECT",
        },
        "claim_boundary": {
            "establishes": [
                "Papers 00, 98 and 99 are publication-current for the terminal Classical Phase-1 counterflow chain",
                "selected-fixture causal success and familywide same-field physical-health obstruction are stated separately",
            ],
            "does_not_establish": [
                "a familywide causal Green homotopy",
                "a complete higher-isotype retuning spectrum",
                "a no-go for changed field content, derivative order or action architecture",
                "nonlinear, observer, quantum, particle, scattering, positivity or unitarity claims",
            ],
        },
        "provenance": {
            "generator": "planning/paper-coverage/generate_classical_phase1_counterflow_overview_publication.py",
            "generator_sha256": sha(Path(__file__)),
            "independent_verifier": "planning/paper-coverage/verify_classical_phase1_counterflow_overview_publication.py",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = dump(build())
    if args.emit:
        OUT.write_text(rendered)
    elif not OUT.exists() or OUT.read_text() != rendered:
        raise SystemExit("FAIL: stale Phase-1 overview publication record")
    print("CLASSICAL_PHASE1_COUNTERFLOW_OVERVIEW_PUBLICATION_UPDATE_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
