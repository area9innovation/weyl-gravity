#!/usr/bin/env python3
"""Independently check Atlas V33 q3 completion and freeze frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32.json"
Q3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
AUXILIARY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
QUARTIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v15_reconciliation", "strict_source_q2_common_assembly", "strict_source_q3_common_assembly", "route_selection", "research_queue")
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    previous, q3, gate, auxiliary, quartic = (json.loads(path.read_text()) for path in (PREDECESSOR, Q3, GATE, AUXILIARY, QUARTIC))
    errors: list[str] = []
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell atlas")
    projection = value.get("strict_source_q3_common_assembly", {})
    expected = {
        "result_id": q3["result_id"],
        "accepted_source_q2_sha256": q3["source_q3_snapshot"]["accepted_q2_snapshot_sha256"],
        "accepted_source_q3_sha256": q3["source_q3_snapshot"]["sha256"],
        "source_q3_families": 2, "classical_independent_monomials": 321,
        "classical_ordered_fourth_variations": 912, "auxiliary_ordered_q3_coefficients": 5952,
        "cyclic_equalities_checked": 40000, "Weyl_Ward_checks": 605,
        "graph_block_quadruples": 40, "arity_three_defects": 0,
        "q3_cyclicity_defects_mod_d": 0, "D_q3_defects": 0, "full_source_q3_assembled": True,
    }
    if projection != expected:
        errors.append("source q3 projection")
    gate_projection = value.get("strict_gate_v15_reconciliation", {})
    if gate_projection.get("gate_a_status") != "FAIL_CLOSED" or gate_projection.get("accepted_top_level_hashes") != 1 or gate_projection.get("remaining_top_level_hashes") != 6 or gate_projection.get("full_source_q3_assembled") is not True or len(gate_projection.get("minimal_missing_bundle", [])) != 5:
        errors.append("Gate V15 projection")
    routes = value.get("route_selection", [])
    if len(routes) != 10 or [row.get("rank") for row in routes] != list(range(1, 11)) or routes[0].get("route") != "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION":
        errors.append("freeze route frontier")
    if value.get("research_queue", [{}])[0].get("object") != "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION":
        errors.append("research queue frontier")
    if auxiliary["shifted_mass_q3_lift"]["component_counts"].get("total_ordered_q3_coefficients") != 5952 or auxiliary["exact_replay"].get("cyclicity_defects") != 0:
        errors.append("auxiliary q3 authority")
    vertex = quartic["shifted_auxiliary_quartic_mass_vertex"]
    if vertex.get("nonzero_independent_component_monomials") != 321 or vertex.get("nonzero_ordered_fourth_variation_coefficients") != 912:
        errors.append("classical quartic authority")
    flags = value.get("claim_flags", {})
    for key in ("strict_386_full_source_q3_pullback_replayed", "strict_386_authoritative_full_q3_imported", "strict_386_full_arity_three_identity_replayed", "strict_386_full_q3_cyclicity_replayed_mod_d", "strict_386_full_D_q3_derivation_replayed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_pure_weyl_classical_gate_passed", "strict_386_q2_q3_green_compatibility_certified", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, Q3, GATE, AUXILIARY, QUARTIC):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("provenance " + path.name)
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V33: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
