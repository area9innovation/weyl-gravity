#!/usr/bin/env python3
"""Generate the fail-closed Berger observer-apparatus interaction import gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_observer_interaction_import_gate_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json"

DEPENDENCIES = {
    "linear_transfer": PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
    "detector_preflight": PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "causal_q2_repair": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "support_local_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "k_signoff": ROOT / "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json",
    "raw_d_nullity": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
}
REQUIRED_FLAGS = {
    "linear_transfer": ["SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO", "TWO_CAUSALLY_ACQUIRED_MEMORY_RECORDS_DISTINGUISHABLE"],
    "detector_preflight": ["LOCAL_STANDARD_SIGN_ROD_SOLUTIONS", "TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS", "PERSISTENT_PROBE_MEMORY_REGISTERS"],
    "causal_q2_repair": ["BERGER_MIXED_Q2_CYCLICITY"],
    "support_local_q2": ["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2", "BERGER_FULL_SUPPORT_LOCAL_AA_TO_HPLUS", "BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"],
    "k_signoff": ["K_BERGER_CARTAN_THROUGH_ARITY_THREE"],
    "raw_d_nullity": ["scoped_D_verdict_promoted", "total_helical_presymplectic_contraction_zero"],
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_observer_interaction_import_gate.py",
    "tests": PACKAGE / "tests/test_berger_observer_interaction_import_gate.py",
    "report": PACKAGE / "reports/berger-observer-interaction-import-gate.md",
    "input": INPUT,
    "input_schema": INPUT_SCHEMA,
    "certificate_schema": SCHEMA,
}


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _snapshot_bytes(commit: str, path: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{_prefix()}{path.relative_to(ROOT)}"], cwd=ROOT)


def _dependency_refs(snapshot: str) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    refs: dict[str, dict[str, Any]] = {}
    live_payloads: dict[str, dict[str, Any]] = {}
    for name, path in DEPENDENCIES.items():
        raw = _snapshot_bytes(snapshot, path)
        pinned = json.loads(raw)
        live = json.loads(path.read_text())
        if live.get("result_id") != pinned.get("result_id"):
            raise AssertionError(f"live dependency result changed: {name}")
        for flag in REQUIRED_FLAGS[name]:
            if live.get("flags", {}).get(flag) is not True:
                raise AssertionError(f"live dependency flag dropped: {name}.{flag}")
        refs[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": pinned["result_id"],
            "snapshot_commit": snapshot,
            "sha256": _hash_bytes(raw),
            "claim_boundary": pinned["claim_boundary"],
            "live_required_flags": REQUIRED_FLAGS[name],
        }
        live_payloads[name] = live
    return refs, live_payloads


def evaluate(data: dict[str, Any], patch: dict[str, Any] | None = None) -> dict[str, Any]:
    value = deepcopy(data)
    override = patch or {}
    imported = deepcopy(value["imported_complex"])
    linear = deepcopy(value["linear_record_sector"])
    for key, item in override.items():
        if key in imported:
            imported[key] = item
        elif key in linear:
            linear[key] = item
        else:
            value[key] = item

    exported = [row for row in value["required_operation_blocks"] if row["status"] == "EXPORTED_VERIFIED"]
    missing = [row for row in value["required_operation_blocks"] if row["status"] != "EXPORTED_VERIFIED"]
    repaired = (
        imported["row_count"] == 64
        and imported["q2_repair_applied"]
        and imported["q1_q2_defect_count"] == 0
        and imported["cyclicity_defect_count"] == 0
        and imported["k_berger_arity_two_equivariant"]
        and imported["maxwell_stress_vertex_exported"]
    )
    linear_survives = linear["transfer_rank"] == 2 and linear["persistent_records_distinguishable"]
    apparatus_complete = not missing
    higher_arity = value["relational_smearing_depends_on_rods"] and value["memory_couples_to_maxwell_readout"]
    generator_boundary = not value["treat_raw_d_as_k_berger"] and not imported["raw_d_arity_two_equivariant"]
    promotion_blocked = not value["request_nonlinear_promotion"] and not apparatus_complete
    requirements = {
        "repaired_q2_import_exact": repaired,
        "linear_rank_two_records_survive": linear_survives,
        "apparatus_extension_incomplete": not apparatus_complete,
        "higher_arity_observer_terms_identified": higher_arity,
        "generator_boundary_preserved": generator_boundary,
        "nonlinear_promotion_fail_closed": promotion_blocked,
    }
    return {
        "requirements": requirements,
        "exported_block_count": len(exported),
        "missing_block_count": len(missing),
        "missing_block_ids": [row["id"] for row in missing],
        "minimum_required_maximum_arity": max(row["minimum_arity"] for row in value["required_operation_blocks"]),
    }


def _validate_dependency_facts(payloads: dict[str, dict[str, Any]], data: dict[str, Any]) -> None:
    support = payloads["support_local_q2"]
    causal = payloads["causal_q2_repair"]
    transfer = payloads["linear_transfer"]
    facts = data["imported_complex"]
    exact = support["exact_checks"]
    if support["row_layout"]["total_rows"] != facts["row_count"]:
        raise AssertionError("imported row count does not match support-local q2")
    if not exact["q1_q2_arity_two_identity_all_64_combined_rows_coefficientwise"]:
        raise AssertionError("support-local q1-q2 identity dropped")
    if not exact["BV_cyclicity_from_common_Maxwell_master_action"] or not causal["exact_checks"]["transferred_q2_cyclicity_repaired"]:
        raise AssertionError("q2 cyclicity repair dropped")
    if support["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("nonzero support-local arity-two defect")
    if transfer["transfer_matrix"]["rank"] != data["linear_record_sector"]["transfer_rank"]:
        raise AssertionError("linear transfer rank drifted")


def build() -> dict[str, Any]:
    data = json.loads(INPUT.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    refs, payloads = _dependency_refs(data["dependency_snapshot_commit"])
    _validate_dependency_facts(payloads, data)
    base = evaluate(data)
    if not all(base["requirements"].values()):
        raise AssertionError(f"base import gate failed: {base['requirements']}")
    mutations = []
    for mutation in data["mutations"]:
        replay = evaluate(data, mutation["patch"])
        required = mutation["expected_failed_requirement"]
        mutations.append({
            "name": mutation["name"],
            "expected_failed_requirement": required,
            "observed_requirement_value": replay["requirements"][required],
            "expected_failure_passed": replay["requirements"][required] is False,
        })
    if not all(row["expected_failure_passed"] for row in mutations):
        raise AssertionError("interaction import mutation rail did not fail closed")

    return {
        "schema": "closed-universe-berger-observer-interaction-import-gate-v1",
        "result_id": "BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE",
        "setting_id": data["setting_id"],
        "claim_status": "CERTIFIED_REPAIRED_Q2_IMPORT_LINEAR_SURVIVAL_EXTENDED_OBSERVER_COMPLEX_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "imported_interaction_complex": {
            "rows": 64,
            "scope": "gravity, positive clock, and Maxwell BV rows only",
            "repair": "factor-two Maxwell-output normalization plus the BV-canonical cotangent lift of c_M -> c_M-2 i_c A",
            "q1_q2_defect_term_counts": [0] * 64,
            "cyclicity_defect_count": 0,
            "maxwell_stress_backreaction_vertex": "q2(A,A)->h_hat_plus is exported and exact",
            "k_berger_arity_two_equivariant": True,
        },
        "linear_survival": {
            "reason": "adjoining interactions does not alter the already certified first-order coefficient of the source-to-record map",
            "transfer_matrix": [["C_00", "0"], ["0", "C_11"]],
            "rank": 2,
            "persistent_records_distinguishable": True,
            "backreacted_transfer_recomputed": False,
        },
        "apparatus_extension_ledger": {
            "families": data["apparatus_families"],
            "required_operation_blocks": data["required_operation_blocks"],
            "exported_verified_block_count": base["exported_block_count"],
            "missing_or_unverified_block_count": base["missing_block_count"],
            "missing_or_unverified_block_ids": base["missing_block_ids"],
            "first_typed_obstruction": "the 64-row pairing and q1/q2 coefficient ledgers contain no rod, polarization, memory, or emitter rows, so extended cyclicity is not yet a well-typed calculation",
        },
        "arity_analysis": {
            "fixed_probe_term": "p_a q_a[F] is bilinear in p_a and A only when rho_a and P_a are fixed external apparatus data",
            "dynamical_rod_term": "rho_a(Theta,R) p_a <dA,P_a> produces a p-A-R Taylor block and therefore requires q3 (and potentially higher Taylor terms for a nonlinear bump)",
            "minimum_required_maximum_arity": base["minimum_required_maximum_arity"],
            "q2_only_extension_sufficient": False,
        },
        "gauge_quotient_boundary": {
            "k_berger": "certified through arity three only on the existing gravity-clock complex and at arity two on the 64-row gravity-clock-Maxwell complex; no apparatus action is exported",
            "raw_d": "presymplectic null only on the declared fixed-coupling linearized tangent sector and not action-equivariant on the 64-row q2 complex",
            "raw_d_may_not_be_substituted_for_k_berger": True,
            "observer_evaluation_chain_morphism": False,
        },
        "mutation_results": mutations,
        "flags": {
            "REPAIRED_64_ROW_Q2_IMPORTED_EXACTLY": True,
            "LINEAR_RANK_TWO_RECORD_TRANSFER_PRESERVED": True,
            "MAXWELL_STRESS_BACKREACTION_VERTEX_AVAILABLE": True,
            "OBSERVER_APPARATUS_ROWS_ADJOINED_TO_REPAIRED_COMPLEX": False,
            "EXTENDED_Q1_Q2_IDENTITY_CERTIFIED": False,
            "EXTENDED_CYCLICITY_CERTIFIED": False,
            "K_BERGER_EQUIVARIANCE_WITH_APPARATUS_CERTIFIED": False,
            "RAW_D_DESCENT_WITH_APPARATUS_CERTIFIED": False,
            "BACKREACTED_RANK_TWO_RECORDS_CERTIFIED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "a BV pairing and q1/q2 row layout containing rod, polarization, memory, and emitter variables and antifields",
            "the extended q1 square, q1-q2 identity, or cyclicity identities",
            "the rod-dependent q3 memory vertex and its cyclic cotangent partners",
            "K_Berger equivariance or raw-D descent for the extended apparatus complex",
            "a second-order metric solution sourced by Maxwell and apparatus stress",
            "rank two after gravitational backreaction, recoil, and detector self-interaction",
            "a nonlinear classical observer algebra or any quantum observer state",
        ],
        "provenance": {
            "declared_input_sha256": _hash(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _hash(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This classical gate imports the repaired cyclic q2 and exact K_Berger arity-two action on the existing 64 gravity-clock-Maxwell BV rows, and proves that the previously certified first-order rank-two detector transfer remains a valid linear coefficient. It also certifies the first obstruction to nonlinear promotion: rod, polarization, memory, and emitter BV rows and their q1/q2/q3 cotangent blocks are absent, so extended cyclicity and observer-map descent cannot yet be formed. The Maxwell stress vertex is available, but no backreacted solution or backreacted rank-two transfer is claimed. Raw D is not identified with K_Berger, and no quantum claim is made.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("observer interaction import gate certificate is stale")
    else:
        CERTIFICATE.write_text(rendered)
    print("BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
