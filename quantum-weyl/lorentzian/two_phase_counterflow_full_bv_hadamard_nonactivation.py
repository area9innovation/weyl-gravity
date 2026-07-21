#!/usr/bin/env python3
"""Generate the counterflow full-BV Hadamard nonactivation disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/lorentzian/certificates/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-full-bv-hadamard-nonactivation-fragment-v1.json"
REPORT = ROOT / "quantum-weyl/reports/two-phase-counterflow-full-bv-hadamard-nonactivation-v1.md"
SOURCES = {
    "q70_v2": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
    "q70_v2_receipt": ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2_TIER_RECEIPT.json",
    "phase1_viability": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
    "phase1_viability_receipt": ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1_TIER_RECEIPT.json",
    "local_anomaly_nonactivation": ROOT / "quantum-weyl/anomalies/certificates/TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1.json",
    "local_anomaly_receipt": ROOT / "quantum-weyl/anomalies/receipts/TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1_TIER_RECEIPT.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> tuple[dict[str, Any], dict[str, Any], str]:
    src = {name: json.loads(path.read_text()) for name, path in SOURCES.items()}
    q70 = src["q70_v2"]
    viability = src["phase1_viability"]
    anomaly = src["local_anomaly_nonactivation"]
    refs = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "result_id": str(src[name]["result_id"]),
            "sha256": sha(path),
        }
        for name, path in SOURCES.items()
    }
    cert = {
        "$schema": "../schema/two-phase-counterflow-full-bv-hadamard-nonactivation-v1.schema.json",
        "schema": "two-phase-counterflow-full-bv-hadamard-nonactivation-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1",
        "result_state": "NOT_ACTIVATED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
        "lifecycle_state": "NOT_ACTIVATED",
        "dependency_tags": ["LORENTZIAN-CAUSAL", "REDUCED-MODE", "LOCAL-ALGEBRAIC"],
        "source_refs": refs,
        "activation_gate": {
            "q70_v2_imported": q70["result_state"] == "CERTIFIED_GRADED_CYCLIC_70_ROW_CAUSAL_BV_PARENT",
            "stale_v1_rejected": True,
            "selected_fixture_causal_parent": viability["decision"]["selected_fixture_causal_parent"],
            "robust_stationary_counterflow_locus": viability["decision"]["robust_stationary_retuning_exists"],
            "candidate_specific_quantum_activated": viability["downstream_activation"]["candidate_specific_quantum"],
            "first_exact_obstruction": viability["decision"]["first_exact_obstruction"],
            "stop_branch": "TERMINAL_HEALTH_FAILURE_THEREFORE_DO_NOT_CONSTRUCT_FULL_BV_HADAMARD_COVARIANCE",
        },
        "classical_quantum_boundary": {
            "classical_mode_imported": True,
            "classical_causal_parent": "CERTIFIED_SELECTED_FIXTURE_ONLY",
            "classical_q70_pairing": "CERTIFIED_GRADED_CYCLIC",
            "classical_advanced_retarded_homotopies": "CERTIFIED_SELECTED_FIXTURE_ONLY",
            "robust_physical_clock_carrier": "OBSTRUCTED",
            "classical_causal_propagator_is_quantum_state": False,
        },
        "full_bv_hadamard_disposition": {
            "distribution_spaces": "NOT_DECLARED_BECAUSE_CONSTRUCTION_NOT_ACTIVATED",
            "zero_mode_domain": "NOT_DECLARED_BECAUSE_CONSTRUCTION_NOT_ACTIVATED",
            "all_70_rows_covered": "NOT_COMPUTED",
            "antisymmetric_part_equals_causal_propagator": "NOT_COMPUTED",
            "q54_hadamard_wavefront_set": "NOT_COMPUTED",
            "q16_contractible_block_treatment": "NOT_COMPUTED",
            "brst_q_ward_identity": "NOT_COMPUTED",
            "graded_adjoint_reality": "NOT_COMPUTED",
            "k_stationarity": "NOT_COMPUTED",
            "compatible_complex_structure": "NOT_ACTIVATED",
            "hadamard_two_point_function": "NOT_ACTIVATED",
            "state_space_status": "NOT_ACTIVATED",
            "physical_positivity": "NOT_ACTIVATED",
        },
        "brst_and_qme_status": {
            "brst_cocycle": "NOT_EVALUATED",
            "brst_exactness": "NOT_EVALUATED",
            "local_anomaly": anomaly["lifecycle_state"],
            "qme": "NOT_ACTIVATED",
            "renormalized_time_ordered_products": "NOT_ACTIVATED",
        },
        "rejected_substitutions": [
            "reduced E/A/L covariance called full BV",
            "retained-26 covariance called full BV",
            "omitted ghost, equation or antifield rows",
            "causal propagator called a Hadamard two-point function",
            "indefinite Krein form called a positive state",
            "raw D substituted for K=D-Omega R_rel",
            "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        ],
        "downstream_activation": {
            "physical_state_positivity": False,
            "particle_interpretation": False,
            "interacting_qme": False,
        },
        "mutation_expectations": {
            "robust_locus_invented": "REJECT",
            "stale_v1_parent": "REJECT",
            "omitted_rows": "REJECT",
            "wavefront_claim_invented": "REJECT",
            "ward_identity_invented": "REJECT",
            "complex_structure_invented": "REJECT",
            "positivity_invented": "REJECT",
            "qme_promoted": "REJECT",
            "source_hash_changed": "REJECT",
        },
        "claim_boundary": "The repaired q70 V2 object remains a certified graded-cyclic classical causal BV parent on its selected Berger fixture. The terminal Phase 1 health theorem supplies no robust stationary same-field counterflow clock locus, so the work package's first stop branch applies: no full-BV Hadamard covariance, compatible complex structure, quantum state-space sign, physical positivity or QME construction is activated. This is not a microlocal nonexistence theorem and not a failure of the classical causal parent.",
        "provenance": {
            "generator": "quantum-weyl/lorentzian/two_phase_counterflow_full_bv_hadamard_nonactivation.py",
            "generator_sha256": sha(Path(__file__)),
            "independent_verifier": "quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_nonactivation.py",
        },
    }
    atlas = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": cert["provenance"]["generator"],
        "generated_by_sha256": cert["provenance"]["generator_sha256"],
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "quantum.counterflow.phase1.full_bv_hadamard_nonactivation",
            "scope": {
                "theory": "same-field two-phase polar-clock Weyl action",
                "background": "selected Berger causal fixture plus connected trace-healthy stationary family",
                "boundaries": "closed S3 Cauchy slices",
                "charge_sector": "unrestricted and fixed Q_rel kept distinct",
                "carrier": "repaired q70 V2 classical causal parent; no full-BV quantum covariance activated",
                "degree": "all 70 classical BV rows; quantum bidistribution not constructed",
                "parity": "NOT_COMPUTED",
                "ell": "NOT_APPLICABLE",
                "m": "+/-1/2 on the health obstruction",
                "k": "+/-1/2",
                "omega": "Hamiltonian-Hopf quartet throughout the connected family",
            },
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": "OBSTRUCTED",
                "nonlinear": "NO_CERTIFIED_MAP",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "evidence": [refs["q70_v2"], refs["phase1_viability"], refs["local_anomaly_nonactivation"]],
            "mode_data": {
                "dispersion": claim("OBSTRUCTED", "The persistent j=1/2 Hamiltonian-Hopf quartet terminates candidate selection."),
                "lee_wald": claim("CERTIFIED", "The classical q70 pairing is graded cyclic; no quantum covariance or positivity is inferred."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "The candidate-specific quantum branch is not activated."),
                "resonance": claim("OPEN", "No full-BV quantum resonance or state calculation is activated."),
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": claim("OBSTRUCTED", "No robust bounded same-field clock survives the earlier health gate."),
                    "smooth_secular": claim("NO_CERTIFIED_MAP", "No candidate-specific quantum insertion is constructed."),
                    "causal_retarded": claim("CERTIFIED", "Advanced/retarded homotopies exist for the classical q70 V2 parent on the selected fixture."),
                },
            },
            "claim_boundary": cert["claim_boundary"],
        }],
        "verification_commands": [
            "python3 quantum-weyl/lorentzian/two_phase_counterflow_full_bv_hadamard_nonactivation.py --check",
            "python3 quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_nonactivation.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-full-bv-hadamard-nonactivation-fragment-v1.json",
        ],
    }
    report = """# Two-phase counterflow full-BV Hadamard nonactivation

The repaired q70 V2 complex remains a certified graded-cyclic classical causal
BV parent on the selected Berger fixture. That supplies the antisymmetric
classical causal data, but it is not a positive-frequency covariance or a
quantum state.

The work package requires the terminal Phase 1 health verdict to be evaluated
before constructing a bidistribution. That verdict is obstructed: the
Hamiltonian-Hopf quartet persists on the connected trace-healthy stationary
family, so no robust stationary same-field counterflow clock locus survives.
The explicit first stop branch therefore applies.

No full-70-row covariance, wavefront-set check, BRST Ward identity, compatible
complex structure, state-space sign or physical positivity calculation is
run. These rows are `NOT_ACTIVATED`, not failed and not certified absent. The
result is not a microlocal nonexistence theorem, not an anomaly theorem, not a
QME theorem and not a failure of the classical q70 causal parent.
"""
    return cert, atlas, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert, atlas, report = build()
    outputs = {CERT: dump(cert), ATLAS: dump(atlas), REPORT: report.encode()}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in outputs.items():
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f"STALE: {path.relative_to(ROOT)}")
    print("TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
