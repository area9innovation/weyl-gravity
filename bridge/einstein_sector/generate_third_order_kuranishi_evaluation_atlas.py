"""Generate fail-closed atlas rows for the balanced third-order verdict."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_EVALUATION_V1.json"
OUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    cert = json.loads(CERT.read_text())
    base_scope = dict(cert["scope"])
    evidence = [{"path": str(CERT.relative_to(ROOT)), "result_id": cert["result_id"], "sha256": sha(CERT)}]
    claim_boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result proves that the intrinsic global K3 class "
        "vanishes in the complete homogeneous-correction quotient for one balanced fixture. For the "
        "certified no-homogeneous-addition second-order representative, every occupied original shell "
        "has a nonzero bounded adjoint functional, while a finite exponential-polynomial third-order "
        "preimage exists with secular terms. The bounded shell quotient over arbitrary second-order "
        "homogeneous additions, causal inversion, all-orders integration, particles, positivity, "
        "unitarity and quantum theory remain open."
    )
    common = {
        "causal": "NO_CERTIFIED_MAP",
        "symplectic": "CERTIFIED",
        "observational": "NO_CERTIFIED_MAP",
        "quantum": "NO_CERTIFIED_MAP",
    }
    inherited = {
        "dispersion": {"status": "CERTIFIED", "statement": "The sixteen-point third-order frequency lattice and its four original-shell coincidences are exact."},
        "lee_wald": {"status": "CERTIFIED", "statement": "The shell adjoints use the action-normalized reduced axial Hessian and its certified Lee-Wald pairing."},
        "second_order": {
            "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
            "bounded_or_finite_quasiperiodic": {"status": "CERTIFIED", "statement": "The declared balanced tangent has the imported finite second-order correction."},
            "smooth_secular": {"status": "CERTIFIED", "statement": "The same second-order correction belongs to the finite exponential-polynomial module and is in fact finite quasiperiodic."},
            "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No retarded compact-product correction complex is supplied."},
        },
    }
    entries = [
        {
            "id": "einstein.ph.wm.balanced_ell2.third_order.global_kuranishi_quotient",
            "scope": {**base_scope, "boundaries": "closed S1_L x S2; global compact-stabilizer constraint quotient", "degree": "third-order global Kuranishi class"},
            "descriptions": {**common, "nonlinear": "CERTIFIED"},
            "mode_data": {
                **inherited,
                "taub_maps": {"status": "CERTIFIED", "statement": "K3=0 in O/im(l2), with im(l2)=span{H,J1,J2} and quotient basis {P_x,J3}."},
                "resonance": {"status": "NOT_APPLICABLE", "statement": "Local-in-time shell resonance is a separate cokernel and correction-class question."},
            },
            "evidence": evidence,
            "claim_boundary": claim_boundary,
        },
        {
            "id": "einstein.ph.wm.balanced_ell2.third_order.bounded_shells",
            "scope": {**base_scope, "boundaries": "closed S1_L x S2; bounded or finite-quasiperiodic correction class", "degree": "third-order bounded shell equation"},
            "descriptions": {**common, "nonlinear": "OBSTRUCTED"},
            "mode_data": {
                **inherited,
                "taub_maps": {"status": "CERTIFIED", "statement": "All five global stabilizer components vanish."},
                "resonance": {"status": "OBSTRUCTED", "statement": "For the certified no-homogeneous-addition second-order representative, each of the four original ell=2 shells has a nonzero exact adjoint functional; the quotient over all second-order corrections is open."},
            },
            "evidence": evidence,
            "claim_boundary": claim_boundary,
        },
        {
            "id": "einstein.ph.wm.balanced_ell2.third_order.smooth_secular",
            "scope": {**base_scope, "boundaries": "closed S1_L x S2; finite exponential-polynomial correction class allowing secular terms", "degree": "third-order finite exponential-polynomial equation"},
            "descriptions": {**common, "nonlinear": "CERTIFIED"},
            "mode_data": {
                **inherited,
                "taub_maps": {"status": "CERTIFIED", "statement": "The compact stabilizer Kuranishi class vanishes."},
                "resonance": {"status": "CERTIFIED", "statement": "Adjugate reduction of the nonzero-determinant axial pencil gives a finite exponential-polynomial secular preimage; this is not boundedness."},
            },
            "evidence": evidence,
            "claim_boundary": claim_boundary,
        },
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": sha(Path(__file__)),
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "entries": entries,
        "verification_commands": [
            "python3 -m bridge.einstein_sector.generate_third_order_kuranishi_evaluation_atlas --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-evaluation-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUT.read_text()) != value:
        raise AssertionError("stale third-order atlas fragment")


if __name__ == "__main__":
    main()
