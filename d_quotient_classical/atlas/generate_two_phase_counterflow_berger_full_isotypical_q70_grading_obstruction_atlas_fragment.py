#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the q70 grading obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    evidence = [{
        "path": str(SOURCE.relative_to(ROOT)),
        "result_id": source["result_id"],
        "sha256": _sha(SOURCE),
    }]
    entry = {
        "id": "classical.counterflow.berger.full_isotypical_q70_grading_obstruction",
        "scope": {
            "theory": "selected fixed-action two-phase counterflow theory",
            "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "unrestricted carrier; no quotient by charged D or R_rel",
            "carrier": "fixed-(j,m), all-k, 70-row Peter-Weyl carrier imported from q54 plus the serialized diagonal-U1 table",
            "degree": "declared Z-graded BV chain; q54 shifts +1 while serialized U1 shifts -1",
            "parity": "full real BV carrier; conjugation pairs m with -m and k with -k",
            "ell": "j=two_j/2; finite dimension 70*(2*j+1); j=0 exceptional",
            "m": "fixed SU(2)_L label with the conjugate -m block retained by reality",
            "k": "all weights -j,...,j; no proper nonempty weight truncation is invariant for j>0",
            "omega": "arbitrary time frequency; obstruction is an algebraic grading mismatch before characteristic analysis",
        },
        "descriptions": {
            "causal": "OBSTRUCTED",
            "symplectic": "OBSTRUCTED",
            "nonlinear": "NO_CERTIFIED_MAP",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("NO_CERTIFIED_MAP", "The full all-k carrier closes ungraded, but a degreewise characteristic quotient is not defined on the mixed-orientation q70 import."),
            "lee_wald": _claim("OBSTRUCTED", "The imported U1 table and its prose pairing do not provide a homogeneous graded cyclic direct sum with q54; no descended physical Gram matrix is authorized."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No graded physical class is exported on which a Taub or moment-map obstruction could be evaluated."),
            "resonance": _claim("NO_CERTIFIED_MAP", "Characteristic roots and Jordan chains wait for the convention-correct graded q70 parent."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "The obstruction occurs at the unary import boundary."),
                "smooth_secular": _claim("NO_CERTIFIED_MAP", "No new nonlinear or secular conclusion follows."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "The separate q54 causal result remains certified, but its claimed graded 70-row direct sum requires a reissued U1 chain."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "The fixed-j all-k 70-row carrier is finite and ungraded-closed. The pinned U1 table is oppositely oriented to q54, so the declared Z-graded BV direct sum and its quotient are obstructed until a transpose-based parent repair is independently reissued. This does not revoke q54 causality or establish instability, Hadamard, observer, nonlinear, anomaly, QME, particle or unitarity claims.",
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
            "python3 d_quotient_classical/compensator/two_phase_counterflow_berger_full_isotypical_q70_grading_obstruction.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_berger_full_isotypical_q70_grading_obstruction.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-berger-full-isotypical-q70-grading-obstruction-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("full-isotypical q70 grading-obstruction atlas drifted")
        print("COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
