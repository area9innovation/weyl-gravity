"""Generate the fail-closed residual-atlas row for the polar direct current."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json"
OUTPUT = ROOT / "residual_atlas/einstein-weyl-polar-direct-lee-wald-fragment-v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fragment() -> dict:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert certificate["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1"
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "entries": [{
            "id": "einstein.ph.wm.polar.generic.direct_lee_wald",
            "scope": {
                "theory": "Weyl-Maxwell target with exact Einstein-Maxwell q-primary image",
                "background": "compactified magnetically supported Plebanski-Hacyan",
                "boundaries": "closed S1_L times S2, before final residual quotient",
                "charge_sector": "fixed magnetic U(1) bundle P_N",
                "carrier": "local-gauge-reduced generic polar solution module",
                "degree": 1,
                "parity": "polar only; not identified with the axial representatives",
                "ell": "every integer ell>=2",
                "m": "every m=-ell,...,ell by SO(3) equivariance",
                "k": "every allowed compact k=2*pi*n/L, including zero",
                "omega": "q-primary Einstein shell and doubled p-primary extra shell",
            },
            "descriptions": {
                "causal": "NO_CERTIFIED_MAP",
                "symplectic": "CERTIFIED",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "NO_CERTIFIED_MAP",
            },
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "q(mu)=mu^2-2*lambda*mu+lambda*(lambda-2); p=omega^2-k^2-lambda+2/3, with two p-primary polar representatives."},
                "lee_wald": {"status": "CERTIFIED", "statement": "The direct 4D polar extra block is nonradical with normalized positive-frequency inertia (2,0), is orthogonal to the Einstein image, and gives complete polar inertia (3,1)."},
                "taub_maps": {"status": "OPEN", "statement": "No new quadratic Taub map is inferred from the linear current completion."},
                "resonance": {"status": "OPEN", "statement": "No second-order resonant functional is computed by this linear certificate."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Not determined by the direct current."},
                    "smooth_secular": {"status": "OPEN", "statement": "Not determined by the direct current."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded complex is imported."},
                },
            },
            "evidence": [{
                "path": str(CERTIFICATE.relative_to(ROOT)),
                "result_id": certificate["result_id"],
                "sha256": _sha256(CERTIFICATE),
            }],
            "claim_boundary": certificate["claim_boundary"],
        }],
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_polar_direct_lee_wald_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-polar-direct-lee-wald-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fragment = build_fragment()
    if args.write:
        OUTPUT.write_text(json.dumps(fragment, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    if args.check:
        assert json.loads(OUTPUT.read_text(encoding="utf-8")) == fragment
    if not args.write and not args.check:
        parser.error("one of --write or --check is required")


if __name__ == "__main__":
    main()
