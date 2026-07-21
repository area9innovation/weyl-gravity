#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the counterflow all-Hodge shortfall."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-unrestricted-all-hodge-health-shortfall-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    evidence = [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}]
    entry = {
        "id": "classical.counterflow.unrestricted.all_hodge_health_shortfall",
        "scope": {
            "theory": "selected fixed-action two-phase counterflow theory",
            "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "unrestricted Q_rel with physical D and R_rel retained",
            "carrier": "requested scalar/vector/tensor/exceptional physical quotient of the complete 70-row parent",
            "degree": "all BV degrees before physical quotient",
            "parity": "even and odd requested; block carriers absent",
            "ell": "NO_CERTIFIED_MAP",
            "m": "NO_CERTIFIED_MAP",
            "k": "NO_CERTIFIED_MAP",
            "omega": "NO_CERTIFIED_MAP",
        },
        "descriptions": {
            "causal": "CERTIFIED",
            "symplectic": "NO_CERTIFIED_MAP",
            "nonlinear": "NO_CERTIFIED_MAP",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("NO_CERTIFIED_MAP", "The first scalar Berger restriction pi q70 iota is undefined because same-background tensor-harmonic inclusion/projection maps are not exported."),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "A cyclic BV pairing exists on the local carrier, but no physical harmonic quotient or descended Gram matrix is exported."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "The spatial stabilizer row actions and moment maps remain separately unexported."),
            "resonance": _claim("NO_CERTIFIED_MAP", "No block characteristic matrix exists from which resonances or Jordan chains could be classified."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "The homogeneous action-angle result cannot be generalized to unresolved Berger harmonics."),
                "smooth_secular": _claim("NO_CERTIFIED_MAP", "Only the separate ell=0 family tangent is certified."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "Unary causal Green data do not supply a physical block quotient or nonlinear retarded correction."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "This row records an exact input shortfall. It is neither a physical instability nor a positive-carrier theorem. Round-S3 Hodge formulas are not a same-background crosswalk.",
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [entry],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_unrestricted_all_hodge_health_shortfall.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_unrestricted_all_hodge_health_shortfall.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-unrestricted-all-hodge-health-shortfall-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("all-Hodge shortfall atlas drifted")
        print("COUNTERFLOW_ALL_HODGE_SHORTFALL_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
