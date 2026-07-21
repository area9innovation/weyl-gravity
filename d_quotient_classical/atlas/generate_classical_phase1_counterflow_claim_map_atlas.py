#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT_REL = "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json"
GEN_REL = "d_quotient_classical/atlas/generate_classical_phase1_counterflow_claim_map_atlas.py"
OUT = ROOT / "residual_atlas/classical-phase1-counterflow-claim-map-fragment-v1.json"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "classical",
        "generated_by": GEN_REL, "generated_by_sha256": sha(ROOT / GEN_REL),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "verification_commands": ["python3 d_quotient_classical/phase1/generate_classical_phase1_counterflow_claim_map.py --check", "python3 d_quotient_classical/phase1/verify_classical_phase1_counterflow_claim_map.py", "python3 residual_atlas/validate_fragment.py residual_atlas/classical-phase1-counterflow-claim-map-fragment-v1.json"],
        "entries": [{
            "id": "classical.counterflow.phase1.claim_chain.terminal_nonselection",
            "scope": {"theory": "typed chain from passive tau-adic and declared minimal repairs to the selected two-phase counterflow action", "background": "unit-cylinder source gates; selected Berger fixture; connected trace-healthy same-field Berger family", "boundaries": "closed S3 Cauchy slices", "charge_sector": "unrestricted and fixed-Q_rel explicitly separated", "carrier": "claim-chain synthesis; terminal physical witness is the both-k j=1/2 quotient", "degree": "claim map; terminal witness dimension 14", "parity": "reality-paired both-k sector", "ell": "NOT_APPLICABLE", "m": "+/-1/2 at terminal witness", "k": "+/-1/2 at terminal witness", "omega": "familywide Hamiltonian-Hopf quartet"},
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "OBSTRUCTED", "statement": "The same-field stationary family retains the j=1/2 Hamiltonian-Hopf factor everywhere."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The terminal unstable sector is nonradical with split inertia (4,4,0)."},
                "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "No nonlinear tangent-cone result enters the Classical claim freeze."},
                "resonance": {"status": "OPEN", "statement": "Stable-sector collision Jordan types remain open and cannot cure the persistent unstable factor."},
                "second_order": {"equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]", "bounded_or_finite_quasiperiodic": {"status": "OBSTRUCTED", "statement": "The linear Hamiltonian-Hopf sector excludes the proposed bounded clock."}, "smooth_secular": {"status": "NO_CERTIFIED_MAP", "statement": "No q2 family calculation is imported."}, "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "The Green homotopy is selected-fixture only, not familywide."}}
            },
            "evidence": [{"path": CERT_REL, "result_id": "CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1", "sha256": sha(ROOT / CERT_REL)}],
            "claim_boundary": "Causal certification applies to the selected fixture, not the retuning family. The terminal obstruction is same-field and j=1/2 sufficient for candidate nonselection, not an all-isotype or all-architecture no-go."
        }]
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--emit",action="store_true"); g.add_argument("--check",action="store_true"); a=ap.parse_args()
    t=json.dumps(build(),indent=2,sort_keys=True)+"\n"
    if a.emit: OUT.write_text(t); return 0
    if not OUT.exists() or OUT.read_text()!=t: raise SystemExit("FAIL: stale Classical Phase-1 atlas fragment")
    print("PASS: Classical Phase-1 atlas fragment is current"); return 0


if __name__ == "__main__": raise SystemExit(main())
