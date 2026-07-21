#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the Berger scalar-Hodge obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_SCALAR_HODGE_BLOCK_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-berger-scalar-hodge-block-obstruction-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    evidence = [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}]
    entry = {
        "id": "classical.counterflow.berger.scalar_hodge_subcomplex_obstruction",
        "scope": {
            "theory": "selected fixed-action two-phase counterflow theory",
            "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "unrestricted Q_rel with physical D and R_rel retained",
            "carrier": "proposed exact-one-form scalar Hodge subcomplex of the complete gauge-fixed 70-row parent",
            "degree": "spatial Diff ghost degree -1 to antighost-dual degree 0 at the first closure test",
            "parity": "scalar-derived even spatial parity; generic right weight k nonzero",
            "ell": "j=two_j/2, two_j in Z_>=1",
            "m": "-j,-j+1,...,j (passive SU(2)_L label)",
            "k": "-j,-j+1,...,j; obstruction certified for k!=0; k=0 exceptional/open",
            "omega": "arbitrary time frequency; nonzero obstruction already in the omega^2 coefficient",
        },
        "descriptions": {
            "causal": "OBSTRUCTED",
            "symplectic": "NO_CERTIFIED_MAP",
            "nonlinear": "NO_CERTIFIED_MAP",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("OBSTRUCTED", "The proposed scalar restriction is not a subcomplex: d1 q[bar_c_star_diff,c_spatial] d0 has leading coefficient 93 i k omega^2/40 for every k nonzero."),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "No physical quotient exists on the nonclosed proposed carrier, so the cyclic BV pairing cannot yet descend to a scalar Gram matrix."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No scalar physical cohomology class is exported on which a Taub map could be evaluated."),
            "resonance": _claim("NO_CERTIFIED_MAP", "Characteristic roots and Jordan chains are not defined before a closed isotypical or gauge-adapted carrier is constructed."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "The obstruction is unary and precedes a scalar tangent-cone calculation."),
                "smooth_secular": _claim("NO_CERTIFIED_MAP", "Only the separate homogeneous global action-angle sector has a certified secular family tangent."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "The full q70 parent remains causal, but its Green identity cannot be restricted to this nonclosed scalar carrier."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "This is an exact obstruction to the proposed round-style scalar Hodge subcomplex on the selected Berger background, not a defect of q70, a physical instability, or an obstruction to complete SU(2)_L x U(1)_R isotypical blocks. The k=0 exceptional family remains open.",
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
            "python3 d_quotient_classical/compensator/two_phase_counterflow_berger_scalar_hodge_block_obstruction.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_berger_scalar_hodge_block_obstruction.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-berger-scalar-hodge-block-obstruction-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("scalar-Hodge obstruction atlas drifted")
        print("COUNTERFLOW_BERGER_SCALAR_HODGE_OBSTRUCTION_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
