"""Generate the fail-closed atlas row for the mixed-charge correspondence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json"
OUT = ROOT / "residual_atlas/einstein-weyl-mixed-charge-derived-correspondence-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert = json.loads(CERT.read_text())
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": sha(Path(__file__)),
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "entries": [
            {
                "id": "einstein.ph.wm.mixed_charge.derived_correspondence.two_jet",
                "scope": cert["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "CERTIFIED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "NOT_APPLICABLE", "statement": "Two-jet Cauchy correspondence; branch frequencies are labels only."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "j^*Omega_W and p_X^*S_X are honest pullbacks; no quotient pairing through separately neutral fibres exists."},
                    "taub_maps": {"status": "CERTIFIED", "statement": "The anti-diagonal transfer c records kappa_E=c and kappa_X=-c for all five compact stabilizer charges."},
                    "resonance": {"status": "OPEN", "statement": "Spacetime resonance functionals remain carrier-class dependent and are not inferred here."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "No evolution-space promotion."},
                        "smooth_secular": {"status": "OPEN", "statement": "Not established by the Cauchy correspondence."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded carrier."},
                    },
                },
                "evidence": [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha(CERT)}],
                "claim_boundary": cert["claim_boundary"],
            }
        ],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_mixed_charge_derived_correspondence_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-mixed-charge-derived-correspondence-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.check:
        assert json.loads(OUT.read_text()) == payload


if __name__ == "__main__":
    main()
