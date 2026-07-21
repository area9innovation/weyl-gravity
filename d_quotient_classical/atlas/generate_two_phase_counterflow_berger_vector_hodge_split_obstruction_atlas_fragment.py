#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the Berger vector Hodge obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-berger-vector-hodge-split-obstruction-fragment-v1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_berger_vector_hodge_split_obstruction.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_berger_vector_hodge_split_obstruction.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-berger-vector-hodge-split-obstruction-fragment-v1.json",
        ],
        "entries": [{
            "id": "classical.counterflow.berger.vector_hodge_split_obstruction",
            "scope": {
                "theory": "selected fixed-action two-phase counterflow theory",
                "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
                "boundaries": "none; closed S3 Cauchy slices",
                "charge_sector": "unrestricted Q_rel with physical D and R_rel retained",
                "carrier": "proposed longitudinal/coexact one-form split inside the complete gauge-fixed 70-row parent",
                "degree": "spatial Diff ghost degree -1 to antighost-dual degree 0 at the e0-squared endpoint",
                "parity": "longitudinal and coexact one-form sectors coupled by Berger anisotropy",
                "ell": "j=two_j/2, two_j in Z_>=1",
                "m": "-j,...,j (passive SU(2)_L multiplicity)",
                "k": "all right weights; exact generic obstruction for k!=0 and k=0 retained exceptional",
                "omega": "arbitrary; obstruction occurs in the omega-squared coefficient",
            },
            "descriptions": {"causal": "OBSTRUCTED", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "OBSTRUCTED", "statement": "The longitudinal/coexact split is not invariant: both cross blocks of the e0-squared Diff endpoint are nonzero."},
                "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "No pairing descends before the full coupled isotypical quotient exists."},
                "resonance": {"status": "NO_CERTIFIED_MAP", "statement": "Characteristic and Jordan data are undefined on the nonclosed split."},
                "taub_maps": {"status": "NO_CERTIFIED_MAP", "statement": "No physical vector/tensor class is exported."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "NO_CERTIFIED_MAP", "statement": "Unary carrier closure fails first."},
                    "smooth_secular": {"status": "NO_CERTIFIED_MAP", "statement": "Unary carrier closure fails first."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "The full q70 parent remains causal, but its Green homotopy is not restricted to this split."}
                }
            },
            "evidence": [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}],
            "claim_boundary": "Exact two-way obstruction to the longitudinal/coexact split, not to the full q70 parent. A complete coupled SU(2)_L x U(1)_R isotypical carrier remains open; no physical, stability, observer, Hadamard or quantum claim follows."
        }]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = _render(build())
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit("stale vector-Hodge obstruction atlas fragment")
    print("COUNTERFLOW_BERGER_VECTOR_HODGE_OBSTRUCTION_ATLAS: PASS")


if __name__ == "__main__":
    main()
