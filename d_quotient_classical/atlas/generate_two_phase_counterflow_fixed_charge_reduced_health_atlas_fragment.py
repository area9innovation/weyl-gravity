#!/usr/bin/env python3
"""Generate the fixed-charge reduced-health obstruction atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-fixed-charge-reduced-health-fragment-v1.json"
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_fixed_charge_reduced_health_atlas_fragment.py"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    if source["result_state"] != "OBSTRUCTED_FIXED_CHARGE_REDUCTION_REMOVES_RELATIVE_CLOCK":
        raise AssertionError("fixed-charge obstruction not certified")
    evidence = [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}]
    entry = {
        "id": "classical.two_phase_counterflow.fixed_charge_relative_clock_reduction",
        "scope": {
            "theory": "selected two-phase counterflow action",
            "background": "stationary Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": "derived fixed-Q_rel leaf followed by R_rel quotient",
            "carrier": "70-component causal parent with explicit global charge fibre",
            "degree": 0,
            "parity": "relative phase scalar zero mode",
            "ell": 0,
            "m": 0,
            "k": "NOT_APPLICABLE",
            "omega": "background Omega=3/4",
        },
        "descriptions": {"causal": "CERTIFIED", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
        "mode_data": {
            "dispersion": claim("NO_CERTIFIED_MAP", "The relative-clock direction is removed before a physical propagation polynomial can be assigned."),
            "lee_wald": claim("OBSTRUCTED", "On delta Q_rel=0 the pullback pairing has radical span(delta psi_0), and the R_rel quotient removes that entire line."),
            "taub_maps": claim("NO_CERTIFIED_MAP", "No q2 map is defined on a surviving relative-clock class."),
            "resonance": claim("NO_CERTIFIED_MAP", "No surviving relative-clock mode remains for a resonance test."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": claim("NO_CERTIFIED_MAP", "The reduced relative-clock carrier is zero."),
                "smooth_secular": claim("NO_CERTIFIED_MAP", "The reduced relative-clock carrier is zero."),
                "causal_retarded": claim("NO_CERTIFIED_MAP", "The unary parent is causal, but no relative-clock physical class survives reduction."),
            },
        },
        "evidence": evidence,
        "claim_boundary": "The causal parent remains certified before reduction. The fixed-charge symplectic quotient removes the relative clock, so no physical relative-clock, observer, nonlinear, Hadamard, quantum or particle map is certified.",
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": STATUSES,
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [entry],
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_fixed_charge_reduced_health.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_fixed_charge_reduced_health.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-fixed-charge-reduced-health-fragment-v1.json"
        ]
    }


def write() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


def check() -> None:
    if json.loads(OUTPUT.read_text()) != build():
        raise AssertionError("fixed-charge atlas drifted")
    print("TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_ATLAS_FRAGMENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
