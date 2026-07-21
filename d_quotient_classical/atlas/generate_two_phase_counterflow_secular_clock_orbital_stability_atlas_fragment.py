#!/usr/bin/env python3
"""Generate fail-closed atlas rows for the counterflow action-angle verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-secular-clock-orbital-stability-fragment-v1.json"
GENERATOR = Path(__file__).resolve()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    evidence = [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}]
    common_scope = {
        "theory": "selected fixed-action two-phase counterflow theory",
        "background": "stationary Berger R x S3, a=1, c_squared=9/40",
        "boundaries": "none; closed S3 Cauchy slices",
        "degree": 0,
        "parity": "scalar homogeneous zero mode",
        "ell": 0,
        "m": 0,
        "k": "NOT_APPLICABLE",
        "omega": "background relative frequency 3/4; linearized characteristic root 0",
    }
    reduced = {
        "id": "classical.counterflow.unrestricted_clock.action_angle_orbital_stability",
        "scope": {
            **common_scope,
            "charge_sector": "unrestricted variable-Q_rel reduced homogeneous phase-charge subsystem",
            "carrier": "global Darboux pair (psi mod 2*pi,Q_rel) imported from the 70-row causal parent",
        },
        "descriptions": {
            "causal": "CERTIFIED",
            "symplectic": "CERTIFIED",
            "nonlinear": "NO_CERTIFIED_MAP",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("CERTIFIED", "The exact homogeneous Hamiltonian has a size-two zero Jordan block and no exponential root."),
            "lee_wald": _claim("CERTIFIED", "The unrestricted global pair has canonical two-form dQ_rel wedge dpsi and positive transverse augmented-energy curvature 1/I."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No second-order Taub map is inferred from the homogeneous action-angle normal form."),
            "resonance": _claim("CERTIFIED", "The secular linear solution is exactly the Q_rel derivative of the physical relative-equilibrium family, not a gauge direction."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("OBSTRUCTED", "Lifted boundedness and absolute compact-clock Lyapunov stability fail by physical dephasing."),
                "smooth_secular": _claim("CERTIFIED", "Phi_t(psi,Q)=(psi+t Q/I,Q) and d_Q Phi_t=(t/I,1): the shear is an exact action-angle family tangent; fixed-charge orbital and shifted-frequency modulated stability pass."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "The imported unary causal carrier does not turn this finite-dimensional stability result into nonlinear causal response."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "Orbital comparison uses the charged global R_rel action without declaring it gauge. No all-Hodge, observer or quantum promotion follows.",
    }
    coupled = {
        "id": "classical.counterflow.coupled_berger.charge_family_separator",
        "scope": {
            **common_scope,
            "charge_sector": "positive-frequency local component near Q_rel=9*pi^2*sqrt(10)/5",
            "carrier": "complete fixed-action homogeneous Berger stationarity equations, not merely the relative phase subsystem",
        },
        "descriptions": {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "CERTIFIED",
            "nonlinear": "OBSTRUCTED",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim("NOT_APPLICABLE", "This row is a stationary-locus separator, not a propagating mode."),
            "lee_wald": _claim("CERTIFIED", "The charge direction exists on the unrestricted parent but is transverse to the full coupled stationary locus."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No tangent-cone or Taub identification is made."),
            "resonance": _claim("OBSTRUCTED", "At fixed geometry all three stationary rows equal -(16*(Q/I)^2-9)/32, with only isolated roots +/-Q0."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NOT_APPLICABLE", "The separator decides existence of nearby coupled backgrounds, not time stability."),
                "smooth_secular": _claim("OBSTRUCTED", "The stationary separator is -(5*Q_rel^2-162*pi^4)/(576*pi^4): the reduced family tangent does not lift to a nearby complete fixed-action Berger family, and the full linearized constraint requires delta Q_rel=0."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "Causal transport away from the isolated selected background is not certified."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "The exact reduced helical family and the isolated complete coupled stationary locus are distinct carriers. Name matching does not identify them.",
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [reduced, coupled],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_secular_clock_orbital_stability.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_secular_clock_orbital_stability.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-secular-clock-orbital-stability-fragment-v1.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise AssertionError("orbital-stability atlas fragment drifted")
        print("COUNTERFLOW_ORBITAL_STABILITY_ATLAS: PASS")
    else:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
