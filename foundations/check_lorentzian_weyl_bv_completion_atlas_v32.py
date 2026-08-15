#!/usr/bin/env python3
"""Independently check Atlas V32 q2 promotion and q3 frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31.json"
ASSEMBLY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V14_RECONCILIATION.json"
DIFF = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V2.json"
MASS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v14_reconciliation", "strict_source_q2_common_assembly", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous, assembly, gate, diff, mass = (json.loads(path.read_text()) for path in (PREDECESSOR, ASSEMBLY, GATE, DIFF, MASS))
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor mismatch")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell atlas drift")
    q2 = value.get("strict_source_q2_common_assembly", {})
    expected = {"result_id": assembly["result_id"], "accepted_source_q2_sha256": assembly["source_q2_snapshot"]["sha256"], "minimal_ordered_symbolic_components": 22, "auxiliary_ordered_component_coefficients": 2064, "source_q2_families": 16, "graph_block_triples": assembly["graph_transport"]["graph_block_triples"], "q1_q2_defects": 0, "q2_cyclicity_defects": 0, "D_q2_defects": 0, "full_source_q3_assembled": False, "first_missing_q3_vertex": assembly["q3_boundary"]["first_missing_vertex"], "rejected_v1_q1_q2_defects": 336, "accepted_v2_q1_q2_defects": 0, "shifted_mass_cyclicity_equalities": 3000}
    if q2 != expected:
        errors.append("source-q2 assembly projection mismatch")
    g = value.get("strict_gate_v14_reconciliation", {})
    if g.get("gate_a_status") != "FAIL_CLOSED" or g.get("accepted_top_level_hashes") != 1 or g.get("full_source_q2_assembled") is not True or g.get("full_source_q3_assembled") is not False:
        errors.append("Gate V14 projection mismatch")
    routes = value.get("route_selection", [])
    if len(routes) != 10 or [row.get("rank") for row in routes] != list(range(1, 11)) or routes[0].get("route") != "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES":
        errors.append("ten-route q3 frontier mismatch")
    if value.get("research_queue", [{}])[0].get("object") != "STRICT_AUXILIARY_Q3_COMMON_ASSEMBLY_AND_ARITY3_IDENTITIES":
        errors.append("research queue frontier mismatch")
    flags = value.get("claim_flags", {})
    for key in ("strict_386_full_source_q2_assembled", "strict_386_full_source_q2_pullback_replayed", "strict_386_authoritative_full_q2_imported", "strict_386_full_carrier_q2_certified", "strict_386_d_q2_derivation_replayed", "strict_386_full_q1_q2_identity_replayed", "strict_386_full_q2_cyclicity_replayed", "strict_386_full_D_q2_derivation_replayed"):
        if flags.get(key) is not True:
            errors.append(f"positive flag drift: {key}")
    for key in ("strict_386_full_source_q3_pullback_replayed", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append(f"fail-closed flag drift: {key}")
    if diff["canonical_sign_repair"]["unrepaired_q1_q2_nonzero_coefficients"] != 336 or diff["canonical_sign_repair"]["repaired_q1_q2_nonzero_coefficients"] != 0 or mass["exact_replay"]["cyclicity_equalities_checked"] != 3000:
        errors.append("sign-repair or mass-cyclicity authority drift")
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, ASSEMBLY, GATE, DIFF, MASS):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"provenance pin mismatch: {path.name}")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V32: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
