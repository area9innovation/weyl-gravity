#!/usr/bin/env python3
"""Generate the counterflow residual-BFV obstruction atlas fragment."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-residual-bfv-receiver-obstruction-fragment-v1.json"
GENERATOR = Path(__file__).resolve()
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def claim(status, statement): return {"status": status, "statement": statement}


def build():
    source = json.loads(SOURCE.read_text())
    if source["result_state"] != "OBSTRUCTED_MISSING_SPATIAL_STABILIZER_LIFT_AND_MOMENT_MAPS":
        raise AssertionError("receiver obstruction not certified")
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)), "generated_by_sha256": sha(GENERATOR),
        "status_vocabulary": STATUSES, "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "classical.two_phase_counterflow.residual_bfv_receiver",
            "scope": {"theory": "selected two-phase counterflow action", "background": "stationary Berger R x S3, a=1, c_squared=9/40", "boundaries": "none; closed S3 Cauchy slices", "charge_sector": "derived fixed-Q_rel leaf", "carrier": "candidate five-generator residual BFV receiver over the certified 70-row causal parent", "degree": "all BFV degrees", "parity": "mixed", "ell": "all", "m": "all", "k": "NOT_APPLICABLE", "omega": "all supported frequencies"},
            "descriptions": {"causal": "CERTIFIED", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": claim("NO_CERTIFIED_MAP", "No residual mode is promoted because the spatial stabilizer action is not serialized on the 70-row carrier."),
                "lee_wald": claim("NO_CERTIFIED_MAP", "The parent pairing is certified, but the five moment maps and descended receiver pairing are not defined."),
                "taub_maps": claim("NO_CERTIFIED_MAP", "The four spatial Hamiltonian matrices needed to form the five-generator Taub ideal are missing."),
                "resonance": claim("NO_CERTIFIED_MAP", "No background-correct residual quotient exists on which to test resonance."),
                "second_order": {"equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]", "bounded_or_finite_quasiperiodic": claim("NO_CERTIFIED_MAP", "Residual receiver missing."), "smooth_secular": claim("NO_CERTIFIED_MAP", "Residual receiver missing."), "causal_retarded": claim("NO_CERTIFIED_MAP", "The unary parent is causal, but the bulk-to-five-generator time-slice map is missing.")}
            },
            "evidence": [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": sha(SOURCE)}],
            "claim_boundary": "The abstract su(2)_L plus u(1)_R3 plus R_K CE algebra is certified. No physical residual mode, BFV quotient, anomaly image, observer class or quantum state is certified until the spatial row actions and moment maps land."
        }],
        "verification_commands": ["python3 d_quotient_classical/compensator/two_phase_counterflow_residual_bfv_receiver_obstruction.py --check", "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_residual_bfv_receiver_obstruction.py", "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-residual-bfv-receiver-obstruction-fragment-v1.json"]
    }


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    if args.check:
        if json.loads(OUTPUT.read_text()) != build(): raise AssertionError("residual-BFV atlas drifted")
        print("TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_ATLAS: PASS")
    else: OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__": main()
