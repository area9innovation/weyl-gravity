"""Generate fail-closed atlas row for the cubic canonical export obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json"
OUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-fragment-v1.json"


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
                "id": "einstein.ph.wm.compact_cauchy.cubic_constraint_tensor_export_gate",
                "scope": cert["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "NO_CERTIFIED_MAP",
                    "nonlinear": "OBSTRUCTED",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {"status": "CERTIFIED", "statement": "The imported sixteen-point lattice remains certified; no cubic coefficient is supplied."},
                    "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "A covariant current does not provide the missing action-to-canonical momentum crosswalk."},
                    "taub_maps": {"status": "OBSTRUCTED", "statement": "The first action-normalized H_perp cubic row is undefined because the Ostrogradsky normalization and momenta are not fixed."},
                    "resonance": {"status": "OPEN", "statement": "Shell locations are known, source projections are not."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OBSTRUCTED", "statement": "No cubic canonical tensor can be projected onto the resonant shells."},
                        "smooth_secular": {"status": "OPEN", "statement": "No source coefficient to classify."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No causal carrier."},
                    },
                },
                "evidence": [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha(CERT)}],
                "claim_boundary": cert["claim_boundary"],
            }
        ],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_cubic_constraint_tensor_export_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-fragment-v1.json",
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
