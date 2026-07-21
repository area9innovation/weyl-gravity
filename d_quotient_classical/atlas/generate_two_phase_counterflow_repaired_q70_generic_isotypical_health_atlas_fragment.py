#!/usr/bin/env python3
"""Generate the first generic repaired-q70 physical-health atlas row."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    evidence = [
        {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)},
        {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(PAYLOAD)},
    ]
    entry = {
        "id": "classical.counterflow.berger.repaired_q70.j_half_physical_instability",
        "scope": {
            "theory": "selected fixed-action two-phase counterflow theory with repaired diagonal-U1 chain",
            "background": "stationary biaxial Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "unrestricted and fixed-Q_rel coincide on this nonhomogeneous block; R_rel orbit is absent rather than quotiented",
            "carrier": "complete repaired 70-row Peter-Weyl isotype, 140 components per fixed m, reduced to the exact 14-row physical Hessian",
            "degree": "physical H0/H1 at the characteristic divisor; local gauge and contractible rows removed by explicit maps",
            "parity": "complex m=+/-1/2 reality pair; two physical polarizations per characteristic root",
            "ell": "NOT_APPLICABLE: Berger Peter-Weyl spin j=1/2, not a round-S3 Hodge label",
            "m": "-1/2 and +1/2 paired by reality",
            "k": "both internal weights -1/2,+1/2 retained; neither is a subcomplex",
            "omega": "z quartet from 40*z^4+773*z^2+3748; growth rate sqrt((8*sqrt(9370)-773)/160)",
        },
        "descriptions": {
            "causal": "CERTIFIED",
            "symplectic": "CERTIFIED",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("OBSTRUCTED", "A physical multiplicity-two factor 40*z^4+773*z^2+3748 has y=z^2 discriminant -2151, hence a complex-frequency quartet with nonzero growth rate."),
            "lee_wald": _claim("CERTIFIED", "The residue pairing is nondegenerate and the real eight-dimensional unstable sector has exact energy inertia (4,4,0)."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No q2 result has been replayed against this V2 physical quotient."),
            "resonance": _claim("CERTIFIED", "Every root of the unstable factor is semisimple with geometric multiplicity two; there is no polynomial-time Jordan partner."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "The linear physical carrier already contains exponentially growing oscillatory solutions."),
                "smooth_secular": _claim("OPEN", "The nonlinear source and correction class have not been computed on this quotient."),
                "causal_retarded": _claim("CERTIFIED", "The parent remains Green-hyperbolic; causal solvability does not remove the physical complex-frequency block."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "This is a same-background, all-k, first non-stabilizer physical quotient. The unstable directions are not local gauge, diagonal-U1, R_rel orbit, the j=0 action-angle tangent or a pairing radical. It obstructs full linear health but is not a nonlinear blow-up, Hadamard, QME, particle, positivity or unitarity theorem, and it does not classify every higher-j or low-j stabilizer block.",
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
            "python3 d_quotient_classical/compensator/two_phase_counterflow_repaired_q70_generic_isotypical_health.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_repaired_q70_generic_isotypical_health.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-repaired-q70-first-generic-isotypical-health-obstruction-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("generic q70 health atlas drifted")
        print("COUNTERFLOW_REPAIRED_Q70_GENERIC_ISOTYPICAL_HEALTH_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
