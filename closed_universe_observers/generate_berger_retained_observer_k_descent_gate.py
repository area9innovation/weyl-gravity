#!/usr/bin/env python3
"""Certify the typed obstruction to K-descent on the retained 36-row complex."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-retained-observer-k-descent-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_RETAINED_OBSERVER_K_DESCENT_GATE.json"

DEPENDENCIES = {
    "coupled_k_cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "retained_36_sdr": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "detector_records": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "rank_two_transfer": PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
    "apparatus_import_gate": PACKAGE / "certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json",
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
}
REQUIRED_FLAGS = {
    "coupled_k_cartan": ["BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"],
    "retained_36_sdr": ["BERGER_ALGEBRAIC_64_TO_36_CYCLIC_SDR"],
    "detector_records": ["TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS", "PERSISTENT_PROBE_MEMORY_REGISTERS"],
    "rank_two_transfer": ["FULL_MAXWELL_RETARDED_SOLUTIONS_EXACT", "SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"],
    "apparatus_import_gate": ["PROBE_LIMIT_RANK_TWO_BASELINE_IMPORTED"],
    "global_rods": ["DETECTOR_INDEXED_ROD_ALLOCATION", "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"],
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_retained_observer_k_descent_gate.py",
    "tests": PACKAGE / "tests/test_berger_retained_observer_k_descent_gate.py",
    "report": PACKAGE / "reports/berger-retained-observer-k-descent-gate.md",
    "certificate_schema": SCHEMA,
}


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _snapshot_bytes(commit: str, path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{_prefix()}{path.relative_to(ROOT)}"], cwd=ROOT
    )


def _dependencies(snapshot: str) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    refs: dict[str, dict[str, Any]] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, path in DEPENDENCIES.items():
        raw = _snapshot_bytes(snapshot, path)
        payload = json.loads(raw)
        for flag in REQUIRED_FLAGS[name]:
            if payload.get("flags", {}).get(flag) is not True:
                raise AssertionError(f"required dependency flag is false: {name}.{flag}")
        refs[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "snapshot_commit": snapshot,
            "sha256": _hash_bytes(raw),
            "required_flags": REQUIRED_FLAGS[name],
        }
        payloads[name] = payload
    return refs, payloads


def _witness(detector_id: str, center: sp.Rational, phase: sp.Expr) -> dict[str, Any]:
    nu = sp.sqrt(58) / 6
    delta = sp.Rational(1, 96)
    spatial_profile = 3 * sp.sqrt(10) * sp.cos(phase) / 10
    value = -nu * spatial_profile * sp.sin(nu * delta)
    # Exact elementary bounds: sqrt(58)<8 and pi>3 imply 0<nu*delta<pi;
    # sqrt(10)<4 and phase<=sqrt(10)/6<2/3<pi/2 imply cos(phase)>0.
    if not (delta < sp.Rational(1, 48)):
        raise AssertionError("witness left the detector time window")
    if not (phase <= sp.sqrt(10) / 6):
        raise AssertionError("unexpected detector phase")
    if sp.simplify(value) == 0:
        raise AssertionError("rod K-variation witness vanished")
    return {
        "detector_id": detector_id,
        "rod_row": f"R{detector_id[-1]}_1",
        "evaluation_time": str(center + delta),
        "event_time": str(center),
        "time_offset": "1/96",
        "spatial_point": {"x0": "0", "x1": "0", "x2": "0", "x3": "1"},
        "spatial_profile_value": str(spatial_profile),
        "k_variation_value": str(value),
        "sign": "strictly_negative",
        "nonzero_proof": "0<sqrt(58)/576<1/72<pi and 0<phase<=sqrt(10)/6<2/3<pi/2, so sin and cos are strictly positive",
        "inside_detector_window": True,
    }


def build(snapshot: str) -> dict[str, Any]:
    snapshot = subprocess.check_output(["git", "rev-parse", snapshot], cwd=ROOT, text=True).strip()
    refs, deps = _dependencies(snapshot)
    retained_rows = deps["retained_36_sdr"]["retained_complex"]["component_rows"]
    retained_ids = [row["row_id"] for row in retained_rows]
    rods = deps["global_rods"]
    allocation = rods["allocation_correction"]
    required_degree_zero = allocation["new_degree_zero_rows"]
    required_degree_one = allocation["new_degree_one_rows"]
    overlap = sorted(set(retained_ids) & set(required_degree_zero + required_degree_one))
    if overlap:
        raise AssertionError(f"apparatus rows unexpectedly occur in retained36: {overlap}")
    if len(retained_rows) != 36 or allocation["corrected_proposed_total_rows"] != 84:
        raise AssertionError("retained/apparatus dimensions drifted")
    if len(required_degree_zero) != 10 or len(required_degree_one) != 10:
        raise AssertionError("apparatus allocation is not ten cyclic row pairs")
    if deps["rank_two_transfer"]["transfer_matrix"]["rank"] != 2:
        raise AssertionError("probe rank-two baseline drifted")

    witnesses = [
        _witness("D0", sp.Rational(1, 4), sp.sqrt(10) / 12),
        _witness("D1", sp.Rational(1, 2), sp.sqrt(10) / 6),
    ]
    result = {
        "schema": "closed-universe-berger-retained-observer-k-descent-gate-v1",
        "result_id": "BERGER_RETAINED_OBSERVER_K_DESCENT_GATE",
        "setting_id": "berger_retained36_observer_vertex_typed_k_descent_audit",
        "claim_status": "EXACT_TYPED_OBSTRUCTION_MISSING_84_ROW_APPARATUS_COMPLEX",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "imported_positive_results": {
            "retained_row_count": 36,
            "coupled_k_cartan_through_arity_three": True,
            "probe_transfer_rank": 2,
            "full_maxwell_retarded_solutions_exact": True,
            "six_global_detector_indexed_rods_exported": True,
        },
        "required_apparatus_extension": {
            "current_full_row_count_before_algebraic_retract": 64,
            "new_degree_zero_rows": required_degree_zero,
            "new_degree_one_rows": required_degree_one,
            "new_cyclic_row_pairs": 10,
            "required_total_row_count": 84,
            "retained36_overlap": overlap,
            "missing_carrier": "six detector-indexed rod fields and four memory/multiplier fields, together with their cyclic partners",
        },
        "observer_vertex": {
            "functional": "Q_a[F]=integral rho_a(Theta,R) <F,dTheta wedge dR^a>_gHat dvol_gHat",
            "memory_action": "sum_a p_a(d_Theta m_a-Q_a[F])",
            "first_failed_typed_map": "the K-variation differentiates rho_a(Theta,R) and dR^a through K R_{aI}, but retained36 contains neither rod nor memory rows on which those terms can land",
            "failure_is_coefficient_defect": False,
            "failure_is_missing_domain_and_codomain_rows": True,
        },
        "exact_k_rod_witnesses": {
            "generator": "K=D-omega R_internal",
            "rod_internal_charge": "zero",
            "therefore": "K R_{aI}=D R_{aI}",
            "rod_frequency": "sqrt(58)/6",
            "physical_detector_half_width": "1/48",
            "witnesses": witnesses,
            "all_nonzero_inside_detector_windows": True,
        },
        "descent_verdict": {
            "retained36_observer_vertex_is_typed": False,
            "retained36_k_cocycle_can_be_asserted": False,
            "reason": "freezing the rods as external profiles discards nonzero K-variation terms; they cannot be cancelled inside the retained36 BV carrier",
            "minimal_next_gate": "construct the action-derived cyclic 84-row q1/pairing/K package and its causal homotopy, then replay the observer-evaluation chain-map identity",
            "global_no_go_for_observer_programme": False,
        },
        "flags": {
            "PROBE_RANK_TWO_BASELINE": True,
            "K_ROD_VARIATION_NONZERO_ON_DETECTOR_WINDOWS": True,
            "RETAINED36_APPARATUS_ROWS_ABSENT": True,
            "RETAINED36_OBSERVER_VERTEX_TYPED": False,
            "RETAINED36_K_DESCENT_CERTIFIED": False,
            "APPARATUS_84_ROW_COMPLEX_REQUIRED": True,
            "APPARATUS_84_ROW_COMPLEX_CERTIFIED": False,
            "APPARATUS_84_ROW_CAUSAL_GREEN_HOMOTOPY_CERTIFIED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "GLOBAL_OBSERVER_PROGRAMME_NO_GO": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "the 84-row unary BV differential and cyclic pairing",
            "the 84-row K action and equivariance",
            "the 84-row causal Green homotopy",
            "the apparatus q2/q3 interactions",
            "the observer-evaluation chain morphism",
            "a complete classical or quantum relational observable",
        ],
        "provenance": {
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _hash(path)}
                for role, path in SOURCE_FILES.items()
            ]
        },
        "claim_boundary": "This certificate proves a scoped typing obstruction: the exact rank-two probe record is not yet a K-cocycle of retained36 because its six rods and four memory/multiplier fields (and cyclic partners) are absent and the rods have explicit nonzero K-variation on the detector windows. It neither disproves the observer programme nor substitutes for construction of the 84-row apparatus BV complex.",
    }
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="HEAD")
    parser.add_argument("--output", type=Path, default=CERTIFICATE)
    args = parser.parse_args()
    result = build(args.snapshot)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
