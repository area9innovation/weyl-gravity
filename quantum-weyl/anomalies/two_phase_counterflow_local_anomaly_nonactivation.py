#!/usr/bin/env python3
"""Generate the Phase 1 counterflow local-anomaly nonactivation disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/anomalies/certificates/TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-local-anomaly-nonactivation-fragment-v1.json"
MATERIALITY = ROOT / "planning/paper-coverage/quantum-counterflow-anomaly-nonactivation-2026-07-21.json"
REPORT = ROOT / "quantum-weyl/reports/two-phase-counterflow-local-anomaly-nonactivation-v1.md"
SOURCES = {
    "q70_v2": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
    "q70_v2_receipt": ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2_TIER_RECEIPT.json",
    "phase1_viability": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
    "phase1_viability_receipt": ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1_TIER_RECEIPT.json",
    "quantum_phase1_synthesis": ROOT / "quantum-weyl/phase1/certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json",
    "quantum_phase1_synthesis_receipt": ROOT / "quantum-weyl/transfer/receipts/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1_TIER_RECEIPT.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    src = {name: json.loads(path.read_text()) for name, path in SOURCES.items()}
    q70 = src["q70_v2"]
    viability = src["phase1_viability"]
    synthesis = src["quantum_phase1_synthesis"]
    refs = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "result_id": str(src[name].get("result_id")),
            "sha256": sha(path),
        }
        for name, path in SOURCES.items()
    }
    counterflow_row = next(row for row in synthesis["theory_rows"] if row["id"] == "TWO_PHASE_COUNTERFLOW_SUCCESSOR")
    cert = {
        "$schema": "../schema/two-phase-counterflow-local-anomaly-nonactivation-v1.schema.json",
        "schema": "two-phase-counterflow-local-anomaly-nonactivation-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1",
        "result_state": "NOT_ACTIVATED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
        "lifecycle_state": "NOT_ACTIVATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "source_refs": refs,
        "gate_evaluation": {
            "q70_v2_imported": q70["result_state"] == "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT",
            "stale_v1_rejected": True,
            "selected_fixture_causal_parent": viability["decision"]["selected_fixture_causal_parent"],
            "robust_stationary_counterflow_locus": viability["decision"]["robust_stationary_retuning_exists"],
            "first_exact_obstruction": viability["decision"]["first_exact_obstruction"],
            "candidate_specific_quantum_activated": viability["downstream_activation"]["candidate_specific_quantum"],
            "stop_branch": "TERMINAL_HEALTH_FAILURE_THEREFORE_DO_NOT_COMPUTE_ACTION_SPECIFIC_ANOMALY",
        },
        "local_anomaly_disposition": {
            "jet_algebra": "NOT_DECLARED_BECAUSE_COMPUTATION_NOT_ACTIVATED",
            "ghost_number_one_quotient": "NOT_COMPUTED",
            "diff_sector": "NOT_COMPUTED",
            "diagonal_u1_sector": "NOT_COMPUTED",
            "weyl_compensator_sector": "NOT_COMPUTED",
            "mixed_sector": "NOT_COMPUTED",
            "cohomology_coefficients": "NOT_COMPUTED",
            "regulator": "NOT_ACTIVATED",
            "qap": "NOT_ACTIVATED",
            "qme": "NOT_ACTIVATED",
            "hadamard": "NOT_ACTIVATED",
        },
        "strict_weyl_import": {
            "imported_as_counterflow_result": False,
            "C2_coefficient": None,
            "E4_coefficient": None,
            "reason": "The strict action and the repaired two-phase action are distinct BV theories; the Phase 1 health gate terminates before an action-specific coefficient calculation."
        },
        "rejected_inputs": [
            "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
            "strict pure-Weyl anomaly coefficients",
            "earlier positive-Berger complex-clock anomaly quotient",
        ],
        "phase1_crosscheck": {
            "synthesis_state": synthesis["result_state"],
            "counterflow_lifecycle": counterflow_row["lifecycle"]["state"],
            "counterflow_promotions": counterflow_row["quantum_promotions"],
        },
        "mutation_expectations": {
            "stale_v1_parent": "REJECT",
            "unstable_fixture_called_selected": "REJECT",
            "strict_coefficients_copied": "REJECT",
            "local_quotient_invented": "REJECT",
            "qme_promoted": "REJECT",
            "hadamard_promoted": "REJECT",
            "source_hash_changed": "REJECT",
        },
        "claim_boundary": "The repaired q70 V2 causal parent is real classical evidence on the selected fixture, but the terminal Phase 1 health theorem proves that no robust stationary same-field counterflow clock survives. The action-specific local anomaly calculation and all determinant, coefficient, regulator, QAP, QME and Hadamard promotions are therefore NOT_ACTIVATED. This is not an anomaly-vanishing theorem, not a failure of the causal parent and not a no-go for a changed action architecture.",
        "provenance": {
            "generator": "quantum-weyl/anomalies/two_phase_counterflow_local_anomaly_nonactivation.py",
            "generator_sha256": sha(Path(__file__)),
            "independent_verifier": "quantum-weyl/anomalies/verify_two_phase_counterflow_local_anomaly_nonactivation.py",
        },
    }
    scope = {
        "theory": "same-field two-phase polar-clock Weyl action",
        "background": "selected Berger causal fixture plus connected trace-healthy stationary family",
        "boundaries": "closed S3 Cauchy slices",
        "charge_sector": "unrestricted and fixed Q_rel kept distinct",
        "carrier": "repaired q70 V2 classical causal parent; no quantum anomaly carrier activated",
        "degree": "classical q70 plus uncomputed ghost-number-one form-degree-four local quotient",
        "parity": "NOT_COMPUTED",
        "ell": "NOT_APPLICABLE",
        "m": "+/-1/2 on the terminal physical-health witness",
        "k": "+/-1/2",
        "omega": "Hamiltonian-Hopf quartet throughout the connected family",
    }
    atlas = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": "quantum-weyl/anomalies/two_phase_counterflow_local_anomaly_nonactivation.py",
        "generated_by_sha256": sha(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "quantum.counterflow.phase1.local_anomaly_nonactivation",
            "scope": scope,
            "descriptions": {"causal": "CERTIFIED", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "evidence": [refs["q70_v2"], refs["phase1_viability"], refs["quantum_phase1_synthesis"]],
            "mode_data": {
                "dispersion": claim("OBSTRUCTED", "The persistent j=1/2 Hamiltonian-Hopf quartet terminates candidate selection."),
                "lee_wald": claim("CERTIFIED", "The selected classical carrier has an exact cyclic pairing; no quantum pairing is inferred."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "Candidate-specific nonlinear and quantum branches were not activated."),
                "resonance": claim("OPEN", "No action-specific quantum resonance calculation was activated."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": claim("OBSTRUCTED", "No robust bounded same-field clock survives the prior linear-health gate."),
                    "smooth_secular": claim("NO_CERTIFIED_MAP", "No candidate-specific q2 source is used here."),
                    "causal_retarded": claim("CERTIFIED", "The repaired q70 V2 causal parent is certified only on the selected fixture."),
                },
            },
            "claim_boundary": cert["claim_boundary"],
        }],
        "verification_commands": [
            "python3 quantum-weyl/anomalies/two_phase_counterflow_local_anomaly_nonactivation.py --check",
            "python3 quantum-weyl/anomalies/verify_two_phase_counterflow_local_anomaly_nonactivation.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-local-anomaly-nonactivation-fragment-v1.json",
        ],
    }
    materiality = {
        "schema": "pure-weyl-paper-materiality-record-v1",
        "result_id": "QUANTUM_COUNTERFLOW_ANOMALY_NONACTIVATION_MATERIALITY_2026_07_21",
        "source_result_id": cert["result_id"],
        "source_sha256": hashlib.sha256(dump(cert)).hexdigest(),
        "records": [{
            "paper": "12",
            "materiality": "COUNTERFLOW_SUCCESSOR_QUANTUM_BRANCH_NOT_ACTIVATED",
            "required_scope": "Preserve the strict-Weyl and formal compensator theorems; do not add a counterflow anomaly coefficient, quotient, QME or Hadamard claim.",
            "publication_edit": "NOT_REQUIRED_EXISTING_PHASE1_BOUNDARY_CURRENT",
        }],
        "claim_boundary": "This reverse materiality record changes no Paper 12 theorem or lifecycle state.",
    }
    report = """# Two-phase counterflow local-anomaly nonactivation

The repaired 70-row V2 complex is an exact graded-cyclic classical causal BV
parent on the selected Berger fixture. It is not a quantum anomaly result.
The terminal Phase 1 viability theorem is evaluated first and finds no robust
stationary same-field clock: the j=1/2 Hamiltonian-Hopf quartet persists on
the connected trace-healthy family. Candidate-specific quantum activation is
therefore false.

Under the work package's explicit branch rule, no action-specific jet algebra,
ghost-number-one quotient, determinant or coefficient calculation is run.
Diff, diagonal-U1, Weyl/compensator and mixed sectors remain NOT_COMPUTED;
regulator, QAP, QME and Hadamard rows remain NOT_ACTIVATED. Strict-Weyl
coefficients and the earlier complex-clock quotient are not imported across
the changed theory boundary. This is a terminal activation disposition, not
an anomaly-vanishing result and not a failure of the classical causal parent.
"""
    return cert, atlas, materiality, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert, atlas, materiality, report = build()
    outputs = {CERT: dump(cert), ATLAS: dump(atlas), MATERIALITY: dump(materiality), REPORT: report.encode()}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in outputs.items():
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f"STALE: {path.relative_to(ROOT)}")
    print("TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
