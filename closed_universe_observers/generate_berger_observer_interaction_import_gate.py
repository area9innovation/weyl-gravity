#!/usr/bin/env python3
"""Generate the corrected Berger observer-apparatus interaction import gate."""

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
INPUT_SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-input-v2.schema.json"
SCHEMA = PACKAGE / "schema/berger-observer-interaction-import-gate-v2.schema.json"
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
    payloads: dict[str, dict[str, Any]] = {}
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
        payloads[name] = live
    return refs, payloads


def evaluate(data: dict[str, Any], patch: dict[str, Any] | None = None) -> dict[str, Any]:
    value = deepcopy(data)
    override = patch or {}
    imported = value["imported_complex"]
    baseline = value["probe_record_baseline"]
    model = value["apparatus_model"]
    for key, item in override.items():
        if key in imported:
            imported[key] = item
        elif key in baseline:
            baseline[key] = item
        elif key == "linear_relational_operation":
            value["action_arity_ledger"][1]["induced_operation"] = item
        elif key == "polarization_model":
            model["polarization"] = item
        else:
            value[key] = item

    repaired = (
        imported["row_count"] == 64
        and imported["q2_repair_applied"]
        and imported["q1_q2_defect_count"] == 0
        and imported["cyclicity_defect_count"] == 0
        and imported["k_berger_arity_two_equivariant"]
        and imported["maxwell_stress_vertex_exported"]
    )
    probe_baseline = baseline["transfer_rank"] == 2 and baseline["persistent_records_distinguishable"]
    arity_exact = all(
        row["action_degree"] == row["input_arity"] + 1
        and row["induced_operation"] == f"q{row['input_arity']}"
        for row in value["action_arity_ledger"]
    )
    model_explicit = (
        model["polarization"] == "COMPOSITE_P_A_EQUALS_DTHETA_WEDGE_DRA_NO_INDEPENDENT_POLARIZATION_ROWS"
        and model["source_role"] == "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE_AT_THIS_GATE"
        and model["dynamical_emitter_deferred"]
    )
    missing = [row for row in value["required_interface_blocks"] if row["status"] != "EXPORTED_VERIFIED"]
    extended_linear_fail_closed = (
        not value["request_extended_linear_survival_promotion"]
        and not baseline["extended_q1_exported"]
        and not baseline["extended_retarded_green_exported"]
    )
    requirements = {
        "repaired_q2_import_exact": repaired,
        "probe_rank_two_baseline_exact": probe_baseline,
        "action_arity_convention_exact": arity_exact,
        "apparatus_model_boundary_explicit": model_explicit,
        "extended_linear_survival_fail_closed": extended_linear_fail_closed,
        "team_handoff_preserved": not value["construct_interaction_tensors_locally"],
        "generator_boundary_preserved": not value["treat_raw_d_as_k_berger"] and not imported["raw_d_arity_two_equivariant"],
        "nonlinear_promotion_fail_closed": not value["request_nonlinear_promotion"] and bool(missing),
    }
    return {
        "requirements": requirements,
        "missing_block_count": len(missing),
        "formal_determinant_constant_nonzero": probe_baseline,
    }


def _validate_dependency_facts(payloads: dict[str, dict[str, Any]], data: dict[str, Any]) -> None:
    support = payloads["support_local_q2"]
    causal = payloads["causal_q2_repair"]
    transfer = payloads["linear_transfer"]
    facts = data["imported_complex"]
    if support["row_layout"]["total_rows"] != facts["row_count"]:
        raise AssertionError("imported row count does not match support-local q2")
    exact = support["exact_checks"]
    if not exact["q1_q2_arity_two_identity_all_64_combined_rows_coefficientwise"]:
        raise AssertionError("support-local q1-q2 identity dropped")
    if not exact["BV_cyclicity_from_common_Maxwell_master_action"] or not causal["exact_checks"]["transferred_q2_cyclicity_repaired"]:
        raise AssertionError("q2 cyclicity repair dropped")
    if support["exact_diagnostics"]["arity_two_defect_term_counts"] != [0] * 64:
        raise AssertionError("nonzero support-local arity-two defect")
    if transfer["transfer_matrix"]["rank"] != data["probe_record_baseline"]["transfer_rank"]:
        raise AssertionError("probe transfer rank drifted")


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
        "schema": "closed-universe-berger-observer-interaction-import-gate-v2",
        "result_id": "BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE",
        "setting_id": data["setting_id"],
        "claim_status": "CERTIFIED_Q2_IMPORT_AND_APPARATUS_INTERFACE_PROBE_BASELINE_ONLY",
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
        "probe_baseline": {
            "transfer_matrix": [["C_00", "0"], ["0", "C_11"]],
            "rank": 2,
            "persistent_records_distinguishable": True,
            "status": "IMPORTED_PROBE_LIMIT_BASELINE_NOT_AN_EXTENDED_LINEAR_THEOREM",
            "extended_q1_exported": False,
            "extended_retarded_green_exported": False,
        },
        "apparatus_interface_contract": {
            "model": data["apparatus_model"],
            "required_blocks": data["required_interface_blocks"],
            "missing_or_unverified_block_count": base["missing_block_count"],
            "first_typed_obstruction": "the memory readout p*A is a unary cross-block, but no common rod-memory-Maxwell q1, cyclic pairing, or retarded Green homotopy has been exported",
        },
        "action_arity_analysis": {
            "convention": "q_n has n inputs and is paired with the (n+1)-st action derivative",
            "ledger": data["action_arity_ledger"],
            "generic_smooth_profile_scope": data["profile_taylor_scope"],
            "q3_trigger": "quadratic dependence of rho_a, P_a, or the metric volume/pairing on apparatus fluctuations produces quartic action terms and q3; the cubic p*A*deltaR term produces q2",
            "q2_only_extension_sufficient_for_generic_smooth_profile": False,
        },
        "formal_rank_stability_lemma": {
            "hypothesis": "if a gauge-compatible interacting observer deformation M(kappa)=M0+kappa M1+... exists over a formal power-series coefficient ring",
            "determinant_constant_term": "C_00*C_11>0",
            "conclusion": "det M(kappa) is a unit because its constant term is nonzero, so the two-record map remains rank two as a formal deformation",
            "actual_interacting_deformation_constructed": False,
        },
        "gauge_and_team_boundary": {
            "k_berger": "certified through arity three on the existing gravity-clock complex and at arity two on the 64-row gravity-clock-Maxwell complex only",
            "raw_d": "fixed-coupling linearized presymplectic nullity is not a substitute for K_Berger equivariance on the apparatus extension",
            "nonlinear_team_supplies": "the nonlinear team supplies the action-derived apparatus q1/q2/q3 and any higher operations, cyclicity, K_Berger identities, backreaction, and the extended retarded Green homotopy",
            "closed_universe_team_supplies": "the closed-universe team supplies this interface, dependency import, observer-evaluation morphism test, causal record interpretation, and the conditional formal determinant lemma",
            "observer_evaluation_chain_morphism": False,
        },
        "mutation_results": mutations,
        "flags": {
            "REPAIRED_64_ROW_Q2_IMPORTED_EXACTLY": True,
            "PROBE_LIMIT_RANK_TWO_BASELINE_IMPORTED": True,
            "FORMAL_RANK_TWO_STABILITY_CONDITIONAL_LEMMA": True,
            "COMPOSITE_DETECTOR_POLARIZATION_DECLARED": True,
            "EXTERNAL_Q_CLOSED_SOURCE_BOUNDARY_DECLARED": True,
            "EXTENDED_APPARATUS_Q1_CERTIFIED": False,
            "EXTENDED_RETARDED_GREEN_CERTIFIED": False,
            "EXTENDED_LINEAR_RANK_TWO_TRANSFER_CERTIFIED": False,
            "EXTENDED_Q1_Q2_IDENTITY_CERTIFIED": False,
            "EXTENDED_CYCLICITY_CERTIFIED": False,
            "K_BERGER_EQUIVARIANCE_WITH_APPARATUS_CERTIFIED": False,
            "RAW_D_DESCENT_WITH_APPARATUS_CERTIFIED": False,
            "INTERACTING_OBSERVER_DEFORMATION_CONSTRUCTED": False,
            "CLASSICAL_OBSERVER_MAP_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "not_established": [
            "a common BV pairing and q1 row layout containing the rod and memory variables and antifields",
            "the block-triangular extended q1 square, unary cyclicity, or retarded Green homotopy",
            "rank two for the extended linear rod-memory-Maxwell complex rather than the imported probe baseline",
            "the action-derived apparatus q2, conditional q3, higher smooth-profile operations, or their cyclic cotangent partners",
            "K_Berger equivariance or raw-D descent for the extended apparatus complex",
            "a dynamical emitter sector or spatially localized emitter worldtubes",
            "an actual backreacted observer deformation to which the conditional determinant lemma applies",
            "a nonlinear classical observer algebra or any quantum observer state",
        ],
        "provenance": {
            "declared_input_sha256": _hash(INPUT),
            "source_manifest": [
                {"role": role, "path": str(path.relative_to(ROOT)), "sha256": _hash(path)}
                for role, path in SOURCE_FILES.items()
            ],
        },
        "claim_boundary": "This corrected classical gate imports the repaired cyclic q2 on the existing 64 gravity-clock-Maxwell BV rows and the previously certified rank-two detector matrix only as a probe-limit baseline. It fixes the action-arity convention: p*A is a q1 cross-block, p*A*deltaR produces q2, and quadratic apparatus dependence first produces q3. Detector polarization is the composite dTheta wedge dR^a, while J_b remains an external q-closed conserved source at this gate. No extended apparatus q1 or retarded Green operator exists yet, so linear survival in the adjoined theory is not claimed. Conditional on a gauge-compatible formal interacting deformation, the nonzero determinant constant term proves formal rank-two stability. The nonlinear team owns the interaction tensors, cyclicity, K_Berger identities, and backreaction; this team owns their import and the observer-morphism test. Raw D is not identified with K_Berger, and no quantum claim is made.",
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
    print("BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE v2 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
