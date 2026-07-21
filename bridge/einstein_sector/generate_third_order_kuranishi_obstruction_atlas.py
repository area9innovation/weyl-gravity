"""Generate fail-closed third-order Kuranishi atlas disposition."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json"
OUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-obstruction-fragment-v1.json"


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
                "id": "einstein.ph.wm.mixed_charge.third_order_kuranishi_input_gate",
                "scope": cert["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "The complete third-frequency lattice has only the original ell=2 q-minus and p-extra shell resonances."},
                    "lee_wald": {"status": "CERTIFIED", "statement": "The correction-choice ambiguity is the image of l2(u,-); this is not a third-order current theorem."},
                    "taub_maps": {"status": "OPEN", "statement": "Five quadratic charges are imported, but their sufficiency through order three cannot be decided without D3C and mixed D2C[u,v]."},
                    "resonance": {"status": "CERTIFIED", "statement": "Angular outputs ell=2,4,6 and all sixteen signed third-frequency lattice points are enumerated exactly."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OBSTRUCTED", "statement": "Third-order resonant coefficients require the missing cubic and first/second mixed tensors."},
                        "smooth_secular": {"status": "OPEN", "statement": "No cubic source is available to determine secular coefficients."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No causal carrier."},
                    },
                },
                "evidence": [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha(CERT)}],
                "claim_boundary": cert["claim_boundary"],
            }
        ],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_third_order_kuranishi_obstruction_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-obstruction-fragment-v1.json",
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
