#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT_REL = "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json"
OUT = ROOT / "residual_atlas/two-phase-counterflow-phase1-viability-classification-fragment-v1.json"


def build():
    cert = ROOT / CERT_REL
    generator = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_phase1_viability_classification_atlas.py"
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "classical",
        "generated_by": "d_quotient_classical/atlas/generate_two_phase_counterflow_phase1_viability_classification_atlas.py",
        "generated_by_sha256": hashlib.sha256(generator.read_bytes()).hexdigest(),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_phase1_viability_classification.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_phase1_viability_classification.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-phase1-viability-classification-fragment-v1.json"],
        "entries": [{
            "id": "classical.counterflow.berger.phase1_viability_terminal_obstruction",
            "scope": {"theory": "same-field two-phase polar-clock Weyl action", "background": "connected stationary trace-healthy biaxial Berger family", "boundaries": "closed S3 Cauchy slices", "charge_sector": "unrestricted and fixed-Q_rel", "carrier": "familywide j=1/2 physical quotient decision joined to selected-fixture repaired q70 causal parent", "degree": "14 at j=1/2", "parity": "reality-paired both-k sector", "ell": "NOT_APPLICABLE", "m": "+/-1/2", "k": "+/-1/2", "omega": "Hamiltonian-Hopf quartet throughout the component"},
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "OBSTRUCTED", "statement": "The F2 frequency factor has negative w-discriminant throughout the connected trace-healthy family."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The unstable multiplicity-two residue sector is nonradical with constant real inertia (4,4,0)."},
                "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "No nonlinear q2 or tangent-cone map is used in this linear viability decision."},
                "resonance": {"status": "OPEN", "statement": "Three stable-sector collision points are isolated but cannot remove the persistent F2 quartet."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OBSTRUCTED", "statement": "The unavoidable linear Hamiltonian-Hopf sector rules out a bounded quasiperiodic clock on this family."},
                    "smooth_secular": {"status": "NO_CERTIFIED_MAP", "statement": "No q2 source was evaluated for the retuning family."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "A causal parent is certified only at the selected fixture, not familywide."}
                }
            },
            "claim_boundary": "The causal status is imported only for the selected repaired fixture; there is no familywide Green map. The row terminates the declared same-field Phase-1 clock candidate and makes no nonlinear, observer or quantum identification.",
            "evidence": [{"path": CERT_REL, "result_id": "TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1", "sha256": hashlib.sha256(cert.read_bytes()).hexdigest()}]
        }]
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--emit",action="store_true"); g.add_argument("--check",action="store_true"); a=ap.parse_args()
    text=json.dumps(build(),indent=2,sort_keys=True)+"\n"
    if a.emit: OUT.write_text(text); return 0
    if not OUT.exists() or OUT.read_text()!=text: raise SystemExit("FAIL: stale atlas fragment")
    print("PASS: Phase-1 atlas fragment is current"); return 0


if __name__ == "__main__": raise SystemExit(main())
