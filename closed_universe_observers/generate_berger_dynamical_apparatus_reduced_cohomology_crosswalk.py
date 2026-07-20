#!/usr/bin/env python3
"""Fail-closed combined-q1 contract for apparatus cohomology reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json"
)
CONTRACT = (
    P
    / "certificates/BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT.json"
)
REPORT = (
    P
    / "reports/berger-dynamical-apparatus-reduced-cohomology-crosswalk.md"
)
DEPENDENCIES = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "global_rods": P / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rank_two": P / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_contract() -> dict[str, Any]:
    parent = json.loads(DEPENDENCIES["parent"].read_text())
    payload = json.loads(DEPENDENCIES["parent_payload"].read_text())
    absent = {
        "row_level_q1_entries": "q1_entries" not in payload,
        "combined_carrier_embedding": "combined_carrier" not in payload,
        "row_level_pairing_entries": "odd_pairing_entries" not in payload["carrier"],
        "row_level_K_action": "K_Berger_matrix" not in payload,
        "cohomological_degrees": "cohomological_degrees" not in payload["carrier"],
        "real_structure_matrix": "real_structure_matrix" not in payload,
        "smearing_to_Maxwell_chain_map": "smearing_to_Maxwell_chain_map" not in payload,
        "zero_mode_support_category": "zero_mode_support_category" not in payload,
    }
    if not all(absent.values()):
        raise AssertionError("combined-q1 capability audit drifted")
    if parent["action_gate"]["q1_and_q2_action_derived"] != "CERTIFIED":
        raise AssertionError("parent action gate drifted")
    return {
        "schema": "closed-universe-berger-dynamical-apparatus-combined-q1-crosswalk-contract-v1",
        "result_id": "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT",
        "status": "REQUIRED_NOT_YET_INSTANTIATED",
        "coefficient_field": "Q(sqrt(10)) with declared differential-symbol localization",
        "background": "same pinned positive Berger gravity-clock-Maxwell background",
        "base_carrier_choice": {
            "status": "UNRESOLVED",
            "candidates": [
                "108-row completed unary carrier (already contains rods, memories and emitters)",
                "minimal gravity-clock-Maxwell subcarrier with a new disjoint apparatus extension",
            ],
            "required_decision": (
                "Choose one carrier and give an explicit same-background chain "
                "map; semantic row names do not identify duplicate rod/memory rows."
            ),
        },
        "required_row_table_columns": [
            "global_row",
            "source_carrier",
            "source_row",
            "field_name",
            "cohomological_degree",
            "Grassmann_parity",
            "odd_partner_row",
            "real_conjugate_row",
            "Berger_U1_weight",
            "boundary_or_zero_mode_sector",
        ],
        "required_exact_objects": {
            "combined_q1": "sparse exact entries with differential/PBW monomials",
            "inclusion_base": "chain map from the selected imported base",
            "inclusion_apparatus": "chain map from all 56 parent rows",
            "projection_base": "declared retraction or explicit NO_MAP witness",
            "odd_pairing": "all row-level entries and signs, not rank alone",
            "real_structure": "row-level antilinear involution",
            "K_Berger": "row-level rigid-family generator commuting with q1",
            "detector_chain_map": (
                "explicit map from local Maxwell carrier rows to both F_a "
                "smearings and memory equations"
            ),
            "support_category": (
                "generic nonzero clock covector and every retained s=0 "
                "memory/rigid-family sector typed separately"
            ),
        },
        "required_verification": [
            "q1 squared equals zero",
            "combined odd cyclicity",
            "real-structure commutation",
            "K_Berger commutator equals zero",
            "exact kernels/images/cohomology by declared degree and support sector",
            "radical and signature of the descended pairing",
            "canonical inclusion/projection/contraction where it exists",
            "both detector memories represented by nonzero reduced classes",
            "rank-two response descends under the detector chain map",
            "row-deletion, sign and duplicate-row mutations are rejected",
        ],
        "acceptance_outputs": [
            "machine-readable combined carrier and q1",
            "canonical cohomology representatives",
            "pairing radical/sign table",
            "K_Berger and real-structure descent",
            "detector-memory class crosswalk",
            "independent verifier not reusing the producer reduction",
        ],
        "current_absence_audit": absent,
        "forbid": [
            "isolated 56-row cohomology called the combined physical reduction",
            "principal-symbol invertibility called zero-mode cohomology",
            "rigid Berger-U1 direction quotiented as a gauge ghost",
            "pairing rank substituted for row-level pairing descent",
            "raw detector functional identified with a Maxwell carrier row",
        ],
    }


def build_certificate(contract: dict[str, Any]) -> dict[str, Any]:
    deps = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    contract_text = json.dumps(contract, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-dynamical-apparatus-reduced-cohomology-crosswalk-v1",
        "result_id": "BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK",
        "setting_id": deps["parent"]["setting_id"],
        "claim_status": "SHORTFALL_MISSING_COMPLETE_COMBINED_Q1_CROSSWALK",
        "atlas_status": "OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": deps[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "contract_ref": {
            "path": str(CONTRACT.relative_to(ROOT)),
            "result_id": contract["result_id"],
            "sha256": hashlib.sha256(contract_text.encode()).hexdigest(),
        },
        "capability_audit": {
            "parent_action_and_principal_blocks": "CERTIFIED",
            "complete_combined_row_level_q1": "NO_CERTIFIED_MAP",
            "complete_combined_pairing": "NO_CERTIFIED_MAP",
            "cohomology_and_contraction": "NO_CERTIFIED_MAP",
            "reduced_memory_classes": "NO_CERTIFIED_MAP",
            "reduced_response_rank": "NO_CERTIFIED_MAP",
            "verdict": "CROSSWALK_REQUIRED_BEFORE_REDUCTION",
        },
        "downstream_disposition": {
            "apparatus_physical_classes": "NO_CERTIFIED_MAP",
            "pairing_radical_and_signature": "NO_CERTIFIED_MAP",
            "memory_representatives": "NO_CERTIFIED_MAP",
            "rank_two_on_reduction": "NO_CERTIFIED_MAP",
            "Z2_response": "NO_CERTIFIED_MAP",
            "redshift": "NO_CERTIFIED_MAP",
            "q2_q3_and_quantum": "NO_CERTIFIED_MAP",
        },
        "next_gate": "INSTANTIATE_AND_VERIFY_BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK",
        "claim_boundary": (
            "This exact audit imports the action-derived 56-row apparatus "
            "parent and the existing 108-row Berger unary carrier by content "
            "hash. The parent serializes field names, parity counts, pairing "
            "rank, an action formula and principal-symbol identities, but it "
            "does not serialize row-level q1 entries, a choice and embedding "
            "of the combined gravity-clock-Maxwell carrier, row-level odd "
            "pairing signs, cohomological degrees, real/K matrices, the "
            "detector-smearing chain map or the zero-mode support category. "
            "The 108-row carrier already contains semantically related rods, "
            "memories and emitters, so concatenation by name would double "
            "count rather than define a chain complex. Consequently no exact "
            "combined kernel, image, cohomology, contraction, descended "
            "pairing, memory class or reduced rank-two response is computed. "
            "The emitted crosswalk contract is the complete prerequisite for "
            "that calculation. This SHORTFALL does not retract the action "
            "parent or leading probe rank, and it makes no Z2, redshift, "
            "positivity, q2/q3, particle or quantum claim."
        ),
        "provenance": {
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_dynamical_apparatus_reduced_cohomology_crosswalk --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_dynamical_apparatus_reduced_cohomology_crosswalk"
            ),
            "source_sha256": sha256(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Berger dynamical-apparatus reduced-cohomology crosswalk

The parent action and transport symbols are exact, but the combined
gravity-clock-Maxwell-plus-apparatus q1 is not serialized.  The missing
objects include the base-carrier choice, row embeddings, row-level q1 and
pairing entries, degrees, real and K actions, the smearing-to-Maxwell chain
map and the zero-mode category.

Because the existing 108-row carrier already has rods, memories and emitters,
concatenating the 56 parent rows would double count semantic roles rather
than define a complex.  No isolated 56-row cohomology is promoted.

The accompanying contract states every exact input, verification and output
required before physical apparatus classes or reduced detector rank can be
computed.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    contract = build_contract()
    certificate = build_certificate(contract)
    if args.write:
        CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    else:
        print(json.dumps(certificate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
