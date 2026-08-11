#!/usr/bin/env python3
"""Independent structural checker for the bounded low-hanging closure audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1.json"

PROMOTIONS = {
    ("CLASSICAL_STANDARD", "SMOOTH_DISTRIBUTIONAL", "GAUGE_BV_COHOMOLOGY", "PIECES_ONLY", "LOCAL_RESULT"),
    ("CLASSICAL_STANDARD", "SMOOTH_DISTRIBUTIONAL", "INTERACTION_RENORMALIZATION_QME", "PRIORITY_GAP", "LOCAL_RESULT"),
    ("FINITE_DISCRETE", "FINITE_EXACT", "DYNAMICS_PROPAGATION", "PRIORITY_GAP", "LOCAL_RESULT"),
}


def canonical_digest(result: dict[str, Any]) -> str:
    payload = {
        "promotions": sorted(
            (
                item.get("foundation"), item.get("carrier"), item.get("obligation"),
                item.get("old_status"), item.get("new_status"),
            )
            for item in result.get("promotions", [])
        ),
        "remaining": sorted(
            (
                item.get("foundation"), item.get("carrier"), item.get("obligation"),
                item.get("status"), item.get("missing_gate"),
            )
            for item in result.get("remaining_assessed_open_cells", [])
        ),
        "h04": result.get("local_bv_evidence", {}).get("h04"),
        "h14": result.get("local_bv_evidence", {}).get("h14"),
        "finite": result.get("finite_dynamics_evidence"),
        "summary": result.get("audit_summary"),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(result: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = json.loads(RESULT.read_text()) if result is None else result
    errors: list[str] = []
    promotions = {
        (
            item.get("foundation"), item.get("carrier"), item.get("obligation"),
            item.get("old_status"), item.get("new_status"),
        )
        for item in result.get("promotions", [])
    }
    if promotions != PROMOTIONS:
        errors.append("three-cell promotion set")

    local = result.get("local_bv_evidence", {})
    expected_cohomology = {
        "h04": (0, {"even": 2, "odd": 1}, ["CT_C2", "CT_E4", "CT_C_DUAL_C"], ["CT_BOX_R"]),
        "h14": (1, {"even": 2, "odd": 1}, ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"], ["ANOM_OMEGA_BOX_R"]),
    }
    for key, (ghost, dimensions, representatives, exact_rows) in expected_cohomology.items():
        item = local.get(key, {})
        if (
            item.get("result_state") != "GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE"
            or item.get("form_degree") != 4
            or item.get("ghost_number") != ghost
            or item.get("parity_dimensions") != dimensions
            or item.get("nontrivial_representatives") != representatives
            or item.get("exact_rows") != exact_rows
        ):
            errors.append("exact " + key + " data")
    if local.get("regularity_scope") != "REGULAR_BACH_LOCUS":
        errors.append("regularity scope")
    if local.get("contraction_state") != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN":
        errors.append("local-BV contraction state")
    if local.get("classical_import_gate") != "FAIL_CLOSED":
        errors.append("classical import gate preservation")

    finite = result.get("finite_dynamics_evidence", {})
    expected_finite = {
        "source_result": "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "maximum_energy": 8,
        "representative_modes": 18,
        "matrix_units": 324,
        "star_degree_checks": 324,
        "matrix_unit_composition_checks": 5832,
        "derivation_leibniz_checks": 5832,
        "formal_time_pair_checks": 15876,
        "arithmetic": "exact integers and formal Laurent exponents only",
        "axis_separation": "Finite dynamics belongs to DYNAMICS_PROPAGATION. Controlled comparison with the smooth continuum remains in RECONSTRUCTION_LIMITS.",
    }
    if finite != expected_finite:
        errors.append("finite dynamics witness")

    remaining = result.get("remaining_assessed_open_cells", [])
    coordinates = [
        (item.get("foundation"), item.get("carrier"), item.get("obligation"))
        for item in remaining
    ]
    if len(remaining) != 22 or len(set(coordinates)) != 22:
        errors.append("remaining open-cell cardinality/uniqueness")
    if any(item.get("status") not in {"PIECES_ONLY", "PRIORITY_GAP"} or not item.get("missing_gate") for item in remaining):
        errors.append("remaining open-cell status/gate")
    summary = result.get("audit_summary", {})
    expected_summary = {
        "assessed_open_before": 25,
        "promoted_local_results": 3,
        "assessed_open_after": 22,
        "pieces_only_after": 5,
        "priority_gaps_after": 17,
        "not_mapped_outside_audit": 157,
        "bounded_exhaustion_status": "NO_FURTHER_SEMANTIC_OR_EXISTING_CERTIFICATE_CLOSURE_IDENTIFIED",
    }
    if summary != expected_summary:
        errors.append("audit summary")
    if sum(item.get("status") == "PIECES_ONLY" for item in remaining) != 5:
        errors.append("pieces-only recount")
    if sum(item.get("status") == "PRIORITY_GAP" for item in remaining) != 17:
        errors.append("priority-gap recount")

    digest = canonical_digest(result)
    if digest != result.get("independent_checker", {}).get("expected_digest"):
        errors.append("canonical audit digest")
    return errors, {"passed": not errors, "digest": digest, **expected_summary}


def main() -> int:
    errors, summary = check()
    print("FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1: " + ("PASS" if not errors else "FAIL"))
    print(json.dumps({"errors": errors, **summary}, indent=2, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
