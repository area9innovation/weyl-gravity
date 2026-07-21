"""Generate fail-closed atlas row for the polar BV residual obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/einstein-weyl-polar-ungauged-bv-residual-obstruction-fragment-v1.json"


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
            "id": "einstein.ph.wm.polar.ungauged_bv.final_residual_descent",
            "scope": {
                "theory": "Einstein-Maxwell source to Weyl-Maxwell target",
                "background": "compactified magnetically supported Plebanski-Hacyan",
                "boundaries": "closed S1_L times S2; no asymptotic boundary carrier",
                "charge_sector": "fixed magnetic bundle; electric tangent and Wilson-line tangent retained",
                "carrier": "ungauged local ghost-field-equation-identity complexes plus separately typed exceptional/global endpoints",
                "degree": "linear BV/equation-Noether map and induced solution pairing",
                "parity": "generic polar obstruction; exceptional axial twist endpoint recorded separately",
                "ell": "generic ell>=2 plus independent ell=1 and ell=0 ledgers",
                "m": "all certified values; no cross-stratum identification",
                "k": "all allowed compact momenta, including zero, with endpoint split",
                "omega": "q-primary Einstein, p-primary extra, exceptional and generalized-zero shells",
            },
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "The imported generic and exceptional branch shells remain certified."},
                "lee_wald": {"status": "OBSTRUCTED", "statement": "The prequotient direct current is certified, but the fixed identity inclusion has full-rank cyclic defect D=R-I and cannot define a strict cyclic BV morphism with standard pairings."},
                "taub_maps": {"status": "OPEN", "statement": "The complete common moment-map-zero derived carrier needed to authorize a stabilizer quotient is absent."},
                "resonance": {"status": "NOT_APPLICABLE", "statement": "This is a linear cyclic/residual gate, not a second-order resonance calculation."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Not promoted by this linear obstruction."},
                    "smooth_secular": {"status": "OPEN", "statement": "Not promoted by this linear obstruction."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."}
                }
            },
            "evidence": [{"path": str(CERTIFICATE.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": _sha256(CERTIFICATE)}],
            "claim_boundary": certificate["claim_boundary"]
        }],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_polar_ungauged_bv_residual_obstruction_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-polar-ungauged-bv-residual-obstruction-fragment-v1.json"
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fragment = build_fragment()
    if args.write:
        OUTPUT.write_text(json.dumps(fragment, indent=2, sort_keys=True)+"\n")
    if args.check:
        assert json.loads(OUTPUT.read_text()) == fragment
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")


if __name__ == "__main__":
    main()
