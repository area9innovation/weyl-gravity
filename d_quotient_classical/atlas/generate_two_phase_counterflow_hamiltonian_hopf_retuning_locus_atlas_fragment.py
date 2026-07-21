#!/usr/bin/env python3
"""Generate the fail-closed atlas row for the counterflow retuning no-go."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-hamiltonian-hopf-retuning-locus-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    entry = {
        "id": "classical.counterflow.berger.retuning_family.j_half_hamiltonian_hopf_no_go",
        "scope": {
            "theory": "same-field two-phase polar-clock Weyl action with repaired diagonal-U1 contractible sector",
            "background": "stationary biaxial Berger R x S3 family; (13-3*sqrt(17))/4<q<1/4, x>0, C>0",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "j=1/2 nonhomogeneous block; delta Q_rel=0 without deleting a charged orbit",
            "carrier": "complete both-k spin-j=1/2 physical quotient of the symbolic PBW Hessian",
            "degree": "14 physical metric coefficients after rank-six gauge and Noether quotients",
            "parity": "m=+/-1/2 reality pair; two physical polarizations per frequency root",
            "ell": "NOT_APPLICABLE: Berger Peter-Weyl spin j, not a round-S3 Hodge label",
            "m": "+/-1/2 paired by real structure",
            "k": "both internal weights +/-1/2 retained",
            "omega": "F2(q,z^2/x)=0 gives a nonzero-real-part frequency quartet for every admissible q",
        },
        "descriptions": {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "CERTIFIED",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("OBSTRUCTED", "disc_(z^2) F2=256*q^5*(9*q-8)<0 throughout the connected trace-healthy component."),
            "lee_wald": _claim("CERTIFIED", "The multiplicity-two modular residue pairing is nondegenerate and the real unstable sector has constant inertia (4,4,0)."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No q2 or tangent-cone map is imported into this retuning theorem."),
            "resonance": _claim("OPEN", "Three stable-sector cross-factor collisions are isolated exactly; their full polynomial Jordan types are not certified."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "The linear j=1/2 quotient has an unavoidable exponential-oscillatory sector."),
                "smooth_secular": _claim("OPEN", "The action-derived q2 source has not been evaluated on this family."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "The selected fixture has a causal parent, but a familywide Green homotopy has not been exported."),
            },
        },
        "evidence": [
            {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)},
            {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(PAYLOAD)},
        ],
        "claim_boundary": "This row is a same-field, same-derivative-order, j=1/2 retuning no-go. It does not identify modes across backgrounds by name, does not supply a familywide causal Green map, and does not establish all-isotype, nonlinear, observer, quantum, particle, positivity or unitarity claims.",
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
            "python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_hamiltonian_hopf_retuning_locus.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-hamiltonian-hopf-retuning-locus-fragment-v1.json",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text() != rendered:
            raise AssertionError("retuning-locus atlas fragment is stale")
    else:
        OUTPUT.write_text(rendered)
    print("TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_ATLAS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
