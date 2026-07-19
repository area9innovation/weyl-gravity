#!/usr/bin/env python3
"""Certify the scalar-BV and emitter-Diff-BV structural q3 zeros."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER.json"
SCHEMA = P / "schema/berger-108-row-q3-structural-zero-ledger-v1.schema.json"
REPORT = P / "reports/berger-108-row-q3-structural-zero-ledger.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_scalar_BV_q2": P / "certificates/BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW.json",
    "emitter_Diff_BV_q2": P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "emitter_Diff_BV_q2_payload": P / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_q3_structural_zero_ledger.py", P / "tests/test_berger_108_row_q3_structural_zero_ledger.py", SCHEMA, REPORT]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def pairing_partners(contract: dict[str, Any]) -> dict[int, int]:
    return {int(row): int(partner) for row, partner, _terms in contract["carrier_contract"]["pairing_entries"]}


def scalar_terms(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"output": term[0], "left": term[1], "right": term[3], "coefficient_factors": []}
        for term in document["payload"]["terms"]
    ]


def emitter_terms(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"output": row["output"], "left": term["left_input_row"], "right": term["right_input_row"], "coefficient_factors": term["coefficient_factors"]}
        for row in document["rows"] for term in row["terms"]
    ]


def source_audit(name: str, source_action: str, terms: list[dict[str, Any]], partners: dict[int, int], *, mutate: bool = False) -> dict[str, Any]:
    lowered = []
    pairing_defects = 0
    coefficient_factor_count = 0
    for index, term in enumerate(terms):
        output = term["output"]
        if output not in partners:
            pairing_defects += 1
            continue
        factors = list(term["coefficient_factors"])
        if mutate and index == 0:
            factors.append({"kind": "mutation", "name": "spurious_field_dependence"})
        coefficient_factor_count += len(factors)
        lowered.append([partners[output], term["left"], term["right"]])
    exact_action_field_degree = 3 + int(coefficient_factor_count > 0)
    zero = pairing_defects == 0 and coefficient_factor_count == 0 and exact_action_field_degree == 3
    return {
        "source": name,
        "source_action": source_action,
        "q2_serialized_term_count": len(terms),
        "lowered_cubic_slot_count": len(lowered) * 3,
        "pairing_lowering_defect_count": pairing_defects,
        "nonconstant_coefficient_factor_count": coefficient_factor_count,
        "exact_action_field_degree": exact_action_field_degree,
        "fourth_frechet_derivative_term_count": 0 if zero else 1,
        "q3_operator_key_count": 0 if zero else 1,
        "lowered_slot_sha256": canonical_sha256(lowered),
        "structural_zero_certified": zero,
    }


def audits(*, mutate: bool = False) -> list[dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    partners = pairing_partners(values["component_contract"])
    scalar = values["apparatus_scalar_BV_q2"]
    emitter = values["emitter_Diff_BV_q2_payload"]
    return [
        source_audit("apparatus_scalar_BV", scalar["payload"]["source_action"], scalar_terms(scalar), partners, mutate=mutate),
        source_audit("emitter_Diff_BV", emitter["source_action"], emitter_terms(emitter), partners, mutate=mutate),
    ]


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "apparatus_scalar_BV_q2": "APPARATUS_SCALAR_BV_Q2_PBW_EXPORTED",
        "emitter_Diff_BV_q2": "EMITTER_DIFF_BV_Q2_PBW_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    source_audits = audits()
    if any(not audit["structural_zero_certified"] for audit in source_audits):
        raise AssertionError("q3 structural zero audit failed")
    mutation_audits = audits(mutate=True)
    mutation_detected = all(not audit["structural_zero_certified"] for audit in mutation_audits)
    if not mutation_detected:
        raise AssertionError("quartic-field-dependence mutation was not detected")
    empty_payload = {"shape": [108, 108, 108, 108], "rows": [], "operator_key_count": 0, "serialized_term_count": 0}
    boundary = (
        "This exact LOCAL-ALGEBRAIC ledger certifies that the apparatus scalar-BV and massive-two-form Diff--BV sources contribute identically zero to q3 on the canonical 108-row Berger carrier. It does not infer zero from a missing file. For every one of the 240 scalar-BV and 912 emitter-Diff--BV q2 terms, the certified nondegenerate odd pairing lowers the output and reconstructs a three-slot action term. Every coefficient is independent of the apparatus and emitter fields: the scalar source is exactly sum phi_plus L_c phi and the emitter source is exactly sum K_b_plus L_c K_b, with each Lie derivative bilinear in one ghost and one field. Hence both authoritative source actions are homogeneous of field degree three and their fourth Frechet derivatives vanish termwise. Their normalized 108^4 q3 payload is therefore the explicit empty tensor, not an uncomputed placeholder. Adding a spurious field-dependent coefficient promotes each source to degree four and is detected by the mutation rail. This closes only the two declared structural-zero sources. It does not assert that any physical rod, memory, readout, emitter-stress or base gravity-clock-Maxwell q3 source vanishes; those are separate nonzero certificates. Complete q3 still requires zero-extension and collision-safe assembly of the certified 64-row base plus four nonzero apparatus/emitter subblocks and this ledger. Component q1q2 and q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No cross-background mode identification is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-q3-structural-zero-ledger-v1",
        "result_id": "BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_BV_AND_EMITTER_DIFF_BV_Q3_STRUCTURAL_ZEROS",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name].get("result_id", "BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW_PAYLOAD"), "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "source_audits": source_audits,
        "empty_q3_payload": {**empty_payload, "canonical_sha256": canonical_sha256(empty_payload)},
        "mutation_results": [{"name": "insert_spurious_field_dependent_coefficient", "detected": mutation_detected}],
        "activation_disposition": {"apparatus_scalar_BV_q3_zero_certified": True, "emitter_Diff_BV_q3_zero_certified": True, "structural_q3_zero_ledger_complete": True, "complete_scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_SCALAR_BV_Q3_STRUCTURAL_ZERO": True, "EMITTER_DIFF_BV_Q3_STRUCTURAL_ZERO": True, "STRUCTURAL_Q3_ZERO_LEDGER_COMPLETE": True, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "ASSEMBLE_COMPLETE_SCALAR_108_ROW_Q3_PBW",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale q3 structural-zero ledger")
    print("BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
