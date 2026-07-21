"""Generate the fail-closed alpha_B=3 canonical-crosswalk atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json"
OUT = ROOT / "residual_atlas/einstein-weyl-alpha-b3-ostrogradsky-canonical-crosswalk-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert = json.loads(CERT.read_text(encoding="utf-8"))
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
                "id": "einstein.ph.wm.alpha_b3.ostrogradsky_canonical_crosswalk",
                "scope": {
                    "theory": "Weyl-Maxwell from S=int sqrt(-g)[3 C^2/8-F^2/4]",
                    "background": "compactified magnetically supported Plebanski-Hacyan product",
                    "boundaries": "compact boundaryless Cauchy slice S1_L x S2",
                    "charge_sector": "fixed magnetic P_N,N=2 and fixed Q_e; based Maxwell gauge",
                    "carrier": "stored balanced ell=2,m=0,k=0 tangent and complete ell=0,2,4 second-order correction representatives",
                    "degree": "action-normalized linear canonical lift of the second-order correction",
                    "parity": "homogeneous and polar correction channels",
                    "ell": "0,2,4",
                    "m": "0",
                    "k": "0",
                    "omega": "all 27 actual signed correction rows, including real zero-frequency rows",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "Every stored correction frequency and conjugate is enumerated in 27 exact rows."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The declared Legendre convention gives the exact Poincare-Cartan form on the stored carrier; no new quantum norm claim is made."},
                    "taub_maps": {"status": "OPEN", "statement": "The crosswalk enables, but does not evaluate, the cubic Kuranishi projection."},
                    "resonance": {"status": "OPEN", "statement": "Third-order resonant source coefficients remain to be regenerated in this convention."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "CERTIFIED", "statement": "The previously certified balanced correction has a complete action-normalized canonical lift."},
                        "smooth_secular": {"status": "CERTIFIED", "statement": "The same finite correction rows lift canonically."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded compact-product complex is supplied."},
                    },
                },
                "evidence": [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha(CERT)}],
                "claim_boundary": cert["claim_boundary"],
            }
        ],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_alpha_b3_ostrogradsky_canonical_crosswalk_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-alpha-b3-ostrogradsky-canonical-crosswalk-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        assert json.loads(OUT.read_text(encoding="utf-8")) == payload


if __name__ == "__main__":
    main()
