#!/usr/bin/env python3
"""Independently check Atlas V31 projections, routes, and firewalls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31.json"
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V30.json"
MANIFEST = ROOT / "d_quotient_classical/certificates/CLASSICAL_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V13_RECONCILIATION.json"


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_v13_reconciliation", "strict_nonlinear_weyl_boost_ghost_manifest", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    previous, manifest, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, MANIFEST, GATE))
    if value.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31" or value.get("predecessor", {}).get("result_id") != previous.get("result_id"):
        errors.append("result identity or predecessor mismatch")
    if len(value.get("branches", [])) != 7 or sum(len(branch.get("stages", [])) for branch in value.get("branches", [])) != 77:
        errors.append("77-cell atlas drift")
    m = value.get("strict_nonlinear_weyl_boost_ghost_manifest", {})
    if m.get("nonzero_ghost_antifield_families") != manifest.get("manifest_summary", {}).get("nonzero_ghost_antifield_families") or m.get("additional_nonlinear_Weyl_boost_ghost_antifield_families") != 0 or m.get("exhaustive_in_declared_scope") is not True or m.get("full_386_source_q2_assembled") is not False:
        errors.append("manifest projection or assembly firewall mismatch")
    g = value.get("strict_gate_v13_reconciliation", {})
    if g.get("gate_a_status") != "FAIL_CLOSED" or g.get("accepted_top_level_hashes") != 0 or g.get("exhaustive_auxiliary_family_census") is not True or g.get("full_source_q2_assembled") is not False:
        errors.append("Gate V13 projection mismatch")
    routes = value.get("route_selection", [])
    if len(routes) != 10 or [row.get("rank") for row in routes] != list(range(1, 11)) or routes[0].get("route") != "STRICT_SOURCE_Q2_Q3_COMMON_ASSEMBLY_AND_IDENTITIES" or any(row.get("route") == "STRICT_NONLINEAR_WEYL_BOOST_GHOST_MANIFEST" for row in routes):
        errors.append("ten-route frontier mismatch")
    flags = value.get("claim_flags", {})
    for key in ("strict_386_exhaustive_full_nonlinear_bv_family_census", "strict_nonlinear_weyl_boost_ghost_manifest_complete"):
        if flags.get(key) is not True:
            errors.append(f"positive flag drift: {key}")
    for key in ("strict_386_full_source_q2_assembled", "strict_386_full_source_q2_pullback_replayed", "strict_386_full_source_q3_pullback_replayed", "strict_pure_weyl_classical_gate_passed", "strict_386_full_bv_hadamard_state_constructed", "strict_pure_weyl_qme_restored", "lorentzian_full_theory_certified"):
        if flags.get(key) is not False:
            errors.append(f"fail-closed flag drift: {key}")
    pins = {row.get("path"): row.get("sha256") for row in value.get("provenance", {}).get("inputs", [])}
    for path in (PREDECESSOR, MANIFEST, GATE):
        if pins.get(str(path.relative_to(ROOT))) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"provenance pin mismatch: {path.name}")
    if value.get("independent_checker", {}).get("expected_digest") != digest(value):
        errors.append("independent digest mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V31: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
