"""Generate the fail-closed atlas row for the symplectic extension classification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json"
OUTPUT = ROOT / "residual_atlas/einstein-weyl-symplectic-extension-classification-fragment-v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fragment() -> dict:
    certificate = json.loads(CERTIFICATE.read_text())
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "entries": [{
            "id": "einstein.ph.wm.parity_complete.symplectic_extension",
            "scope": certificate["scope"],
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "Coprime generic and exceptional primary shells give algebraic CRT splittings before residual reduction."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The target-internal orthogonal split is unique; its quotient form is the lift-invariant Schur complement. Raw lift XX signs are not invariant."},
                "taub_maps": {"status": "OPEN", "statement": "No common moment-map-zero quotient carrier has been constructed."},
                "resonance": {"status": "NOT_APPLICABLE", "statement": "Linear extension classification only."},
                "second_order": {"equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]", "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Not promoted."}, "smooth_secular": {"status": "OPEN", "statement": "Not promoted."}, "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No causal carrier."}}
            },
            "evidence": [{"path": str(CERTIFICATE.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": _sha256(CERTIFICATE)}],
            "claim_boundary": certificate["claim_boundary"],
        }],
        "verification_commands": ["python3 -m bridge.einstein_sector.generate_symplectic_extension_classification_atlas --check", "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-symplectic-extension-classification-fragment-v1.json"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fragment = build_fragment()
    if args.write:
        OUTPUT.write_text(json.dumps(fragment, indent=2, sort_keys=True) + "\n")
    if args.check:
        assert json.loads(OUTPUT.read_text()) == fragment
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")


if __name__ == "__main__":
    main()
