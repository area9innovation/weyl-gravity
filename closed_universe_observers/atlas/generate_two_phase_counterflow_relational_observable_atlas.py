#!/usr/bin/env python3
"""Generate the fail-closed counterflow Observer atlas row."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "closed_universe_observers/atlas/generate_two_phase_counterflow_relational_observable_atlas.py"
CERTIFICATE = ROOT / "closed_universe_observers/certificates/TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-relational-observable-fragment-v1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def build() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    if not value["flags"]["FIXED_CHARGE_RELATIVE_CLOCK_OBSTRUCTED"]:
        raise AssertionError("observer obstruction unavailable")
    evidence = [{"path": str(CERTIFICATE.relative_to(ROOT)), "result_id": value["result_id"], "sha256": _sha(CERTIFICATE)}]
    entry = {
        "id": "observer.two_phase_counterflow.fixed_charge_relational_observable_obstruction",
        "scope": {
            "theory": "selected two-phase counterflow action; apparatus extension not activated",
            "background": "stationary Berger R x S3, a=1, c_squared=9/40",
            "boundaries": "closed S3 Cauchy slices; no timelike boundary",
            "charge_sector": "derived fixed-Q_rel leaf followed by R_rel quotient; Q_diag=0",
            "carrier": "relative phase zero-mode candidate for a clock-labelled detector",
            "degree": 0,
            "parity": "relative scalar zero mode; no gravitational branch parity identification",
            "ell": 0,
            "m": 0,
            "k": "NOT_APPLICABLE",
            "omega": "background Omega=3/4; physical clock carrier is zero",
        },
        "descriptions": {"causal": "CERTIFIED", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "OBSTRUCTED", "quantum": "NO_CERTIFIED_MAP"},
        "mode_data": {
            "dispersion": claim("NO_CERTIFIED_MAP", "The causal parent survives, but the reduced relative-clock carrier is zero before a detector dispersion can be assigned."),
            "lee_wald": claim("OBSTRUCTED", "delta psi_0 is the R_rel radical on delta Q_rel=0; the quotient has dimension and pairing rank zero."),
            "taub_maps": claim("NO_CERTIFIED_MAP", "No observer q2 receiver exists without a physical clock class."),
            "resonance": claim("NO_CERTIFIED_MAP", "No physical clock-labelled signal remains for a resonance test."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": claim("NO_CERTIFIED_MAP", "The observer carrier is zero before correction-class restriction."),
                "smooth_secular": claim("NO_CERTIFIED_MAP", "The observer carrier is zero before correction-class restriction."),
                "causal_retarded": claim("NO_CERTIFIED_MAP", "Parent causal homotopies do not supply a surviving physical clock-labelled receiver."),
            },
        },
        "evidence": evidence,
        "claim_boundary": value["claim_boundary"],
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "observer",
        "generated_by": str(PRODUCER.relative_to(ROOT)), "generated_by_sha256": _sha(PRODUCER),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [entry],
        "verification_commands": [
            "python3 closed_universe_observers/generate_two_phase_counterflow_relational_observable.py --check --guards",
            "python3 closed_universe_observers/verify_two_phase_counterflow_relational_observable.py",
            "python3 -m pytest -q closed_universe_observers/tests/test_two_phase_counterflow_relational_observable.py",
            "python3 closed_universe_observers/atlas/generate_two_phase_counterflow_relational_observable_atlas.py --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-relational-observable-fragment-v1.json"
        ],
    }


def render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        OUTPUT.write_text(render(value))
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != render(value)):
        raise AssertionError("counterflow observer obstruction atlas drifted")
    print("TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_OBSTRUCTION_ATLAS: PASS")
