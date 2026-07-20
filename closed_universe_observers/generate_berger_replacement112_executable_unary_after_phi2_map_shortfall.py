#!/usr/bin/env python3
"""Audit the executable replacement-112 unary after closing the Phi2 map."""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL.json"
X = P / "certificates/BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-executable-unary-after-phi2-map-shortfall-v1.schema.json"
REPORT = P / "reports/berger-replacement112-executable-unary-after-phi2-map-shortfall.md"
DEPS = {
    "replacement": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json",
    "replacement_payload": P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json",
    "phi2_map": P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json",
    "phi2_payload": P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD.json",
    "earlier_shortfall": P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL.json",
    "earlier_shortfall_payload": P / "certificates/BERGER_REPLACEMENT_112_EXECUTABLE_UNARY_VARIATIONAL_INPUT_SHORTFALL_PAYLOAD.json",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def build_payload() -> dict[str, Any]:
    v = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    for cert, payload in (("replacement", "replacement_payload"), ("phi2_map", "phi2_payload"), ("earlier_shortfall", "earlier_shortfall_payload")):
        if sha(DEPS[payload]) != v[cert]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert} payload hash mismatch")
    replacement, phi = v["replacement_payload"], v["phi2_payload"]
    rows = replacement["carrier"]["rows"]
    pairing = replacement["carrier"]["pairing_entries"]
    if len(rows) != 112 or len(pairing) != 112 or replacement["carrier"]["pairing_rank"] != 112:
        raise AssertionError("replacement carrier drifted")
    evaluated = phi["evaluated_nonrod_D3S"]
    if evaluated["dependent_source_term_count"] != 6171 or evaluated["unaffected_source_term_count"] != 288:
        raise AssertionError("Phi2 evaluation census drifted")
    unary = replacement["complete_unary"]
    action_rows = unary["action_variation_rows"]
    forbidden_fields = {
        "coefficient_ring", "operator_schema", "sparse_entries",
        "support_sector_matrices", "zero_mode_operator_blocks",
        "six_rod_removal_sparse_entries", "eight_rod_hessian_sparse_entries",
    }
    present = set(unary) | set(replacement["mixed_action"])
    if present & forbidden_fields:
        raise AssertionError("expected missing executable fields unexpectedly landed")
    return {
        "schema": "closed-universe-berger-replacement112-executable-unary-after-phi2-map-shortfall-payload-v1",
        "result_id": "BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL_PAYLOAD",
        "certified_inputs_now_executable": {
            "row_dictionary": rows,
            "row_count": 112,
            "pairing_entries": pairing,
            "pairing_rank": 112,
            "positive_mixed_Phi2_component_jets": phi["retained_to_local_map"],
            "evaluated_changed_nonrod_blocks": evaluated["blocks"],
            "evaluated_changed_nonrod_blocks_canonical_sha256": evaluated["blocks_canonical_sha256"],
            "dependent_term_count": evaluated["dependent_source_term_count"],
            "unaffected_term_count": evaluated["unaffected_source_term_count"],
            "unaffected_terms_canonical_sha256": evaluated["unaffected_terms_canonical_sha256"],
        },
        "exact_absence_replay": {
            "complete_unary_keys": sorted(unary),
            "mixed_action_keys": sorted(replacement["mixed_action"]),
            "action_variation_rows_are_descriptions": action_rows,
            "required_executable_fields_absent": sorted(forbidden_fields),
            "normalized_sparse_entry_count": 0,
        },
        "first_missing_action_derivative": {
            "status": "NO_CERTIFIED_MAP",
            "formula": "D_g D_R S_R,H[Phi0](delta_g,delta_R), together with its Diff-BV cotangent lift",
            "first_affected_rows": ["h_hat_00", "R0_1_plus"],
            "scope": "metric-to-eight-rod-cotangent mixed Hessian before any six-rod removal/eight-rod replacement composition",
            "why_required": "the replacement declares the old six-rod action removed and a positive-mixed eight-rod action inserted; these entries differ from the old 108-row matrix independently of the now-evaluated Phi2 nonrod correction",
            "missing_serialization": [
                "normalized local metric-rod Hessian coefficient factors",
                "row-indexed six-rod subtraction entries",
                "row-indexed eight-rod H-weighted addition entries",
                "formal Diff-BV adjoints",
                "support-sector and spatial-zero-mode matrices",
            ],
            "available_but_insufficient": {
                "kinetic_matrix_H": replacement["mixed_action"]["kinetic_matrix_H"],
                "Euler_formula": replacement["mixed_action"]["Euler_formula"],
                "action_row_descriptions": action_rows,
            },
        },
        "disposition": {
            "positive_mixed_Phi2_nonrod_variational_input": "CERTIFIED",
            "complete_112_row_dictionary_and_pairing": "CERTIFIED",
            "complete_executable_replacement112_q1": "NO_CERTIFIED_MAP",
            "replacement112_cohomology_and_160_row_consumer": "NOT_REACHED",
        },
    }

def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    v = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-replacement112-executable-unary-after-phi2-map-shortfall-v1",
        "result_id": "BERGER_REPLACEMENT112_EXECUTABLE_UNARY_AFTER_PHI2_MAP_SHORTFALL",
        "setting_id": v["replacement"]["setting_id"],
        "claim_status": "SHORTFALL_MISSING_NORMALIZED_MIXED_METRIC_ROD_ACTION_HESSIAN",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": v[name]["result_id"], "sha256": sha(path)} for name, path in DEPS.items()},
        "payload_ref": {"path": str(X.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(text.encode()).hexdigest(), "canonical_sha256": canonical(payload)},
        "gate_results": payload["disposition"],
        "next_gate": "EXPORT_NORMALIZED_MIXED_METRIC_EIGHT_ROD_HESSIAN_AND_SIX_ROD_REMOVAL_ENTRIES",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE audit resumes the requested executable positive-mixed replacement-112 producer after the retained-Phi2-to-local-component-jet repair. It imports the replacement action, the certified Phi2 map and the earlier variational shortfall by content hash. The Phi2 repair is genuinely consumed: all 6,171 dependent universal nonrod terms are evaluated, their normalized changed blocks are retained by canonical hash, and the 288 unaffected terms retain their separately certified hash. The complete 112-row dictionary, degrees, sectors and all 112 signed pairing entries are also machine-readable, with exact pairing rank 112. The earlier missing nonrod D3S input is therefore closed. The full q1 nevertheless remains undefined at the next action derivative. The replacement payload defines its unary as the complete old 108-row action Hessian with the six-rod action removed and the positive-mixed eight-rod action inserted. It supplies the exact kinetic matrix H, Euler formula and prose descriptions of rod, metric, ghost and cotangent variations, but no normalized sparse metric-to-rod-cotangent Hessian entries, no row-indexed six-rod subtraction, no row-indexed H-weighted eight-rod addition, no formal Diff-BV adjoints and no support-sector or zero-mode matrices. The first missing derivative is D_g D_R S_R,H at the replacement background, beginning in the metric-to-rod-cotangent block; h_hat_00 and R0_1_plus name the earliest rows in canonical order, not a guessed coefficient. This derivative is independent of the now-closed Phi2 nonrod correction and cannot be supplied by copying the old 108-row operator because the rod action and carrier changed. An independent verifier checks the payload hashes, row and pairing census, evaluated-term hashes and the literal absence of every executable Hessian field without importing this producer. This establishes an exact serialization/variational-input shortfall, not failure of the action-level nilpotency, cyclicity, reality or K identities. No sparse q1, cohomology, gauge reduction, 160-row pushout, q2, Z2, memory, redshift, recoil, causal metric-BV propagator, particle or quantum claim is promoted."
        ),
        "provenance": {"generator_command": "python3 -m closed_universe_observers.generate_berger_replacement112_executable_unary_after_phi2_map_shortfall --write", "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_replacement112_executable_unary_after_phi2_map_shortfall", "source_sha256": sha(Path(__file__))},
    }

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); args = ap.parse_args()
    payload = build_payload(); cert = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(cert)
    if args.write:
        X.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        C.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        REPORT.write_text("# Replacement-112 executable unary after Phi2 map\n\nThe Phi2-dependent nonrod terms are now exact. The next missing derivative is the normalized mixed metric/eight-rod action Hessian and its six-rod removal and Diff-BV lift.\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
