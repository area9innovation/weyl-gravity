#!/usr/bin/env python3
"""Generate fail-closed atlas rows for the counterflow trace preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_trace_charge_atlas_fragment.py"
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_PAYLOAD_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-trace-charge-preflight-fragment-v1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _entry(suffix: str, background: str, charge: str, carrier: str, omega: str, status: str, statement: str, evidence: dict[str, str]) -> dict[str, object]:
    return {
        "id": f"classical.two_phase_counterflow.{suffix}",
        "scope": {
            "theory": "selected two positive phases with one auxiliary diagonal compact U(1), separate tau/scale sector, no Maxwell term",
            "background": background,
            "boundaries": "none; closed S3 Cauchy slices",
            "charge_sector": charge,
            "carrier": carrier,
            "degree": 0,
            "parity": "even homogeneous scalar",
            "ell": "0",
            "m": "0",
            "k": "0",
            "omega": omega,
        },
        "descriptions": {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "OPEN",
            "nonlinear": "OPEN",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "mode_data": {
            "dispersion": _claim(status, statement),
            "lee_wald": _claim("OPEN", "Only the reduced homogeneous kinetic/Hamiltonian form is computed; no full Lee-Wald carrier is imported."),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "No second-order Taub map is computed."),
            "resonance": _claim("NO_CERTIFIED_MAP", "No nonlinear resonance map is computed."),
            "second_order": {
                "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "No correction class is constructed."),
                "smooth_secular": _claim("NO_CERTIFIED_MAP", "No secular correction is constructed."),
                "causal_retarded": _claim("NO_CERTIFIED_MAP", "No retarded Green carrier is constructed."),
            },
        },
        "evidence": [evidence],
        "claim_boundary": "LOCAL-ALGEBRAIC/REDUCED-MODE homogeneous preflight only; no causal, nonlinear, observational, particle, Hadamard or quantum identification.",
    }


def build() -> dict[str, object]:
    result = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if result["result_id"] != "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1":
        raise AssertionError("certificate identity drifted")
    if _sha(PAYLOAD) != result["payload_ref"]["sha256"] or payload["content_sha256"] != result["payload_ref"]["content_sha256"]:
        raise AssertionError("certificate payload drifted")
    evidence = {"path": str(CERTIFICATE.relative_to(ROOT)), "result_id": result["result_id"], "sha256": _sha(CERTIFICATE)}
    entries = [
        _entry(
            "cylinder_trace",
            "unit round Einstein cylinder R x S3",
            "fixed relative charge implied by the linearized lapse constraint; diagonal U1 charge zero",
            "homogeneous spatial trace after lapse/Gauss reduction",
            "lambda=+/-2",
            "OBSTRUCTED",
            "The alpha_R=0 trace has negative kinetic sign and real exponential roots; alpha_R nonzero has split inertia.",
            evidence,
        ),
        _entry(
            "berger_fixed_charge_trace",
            "stationary Berger R x S3 with a=1 and c_squared=9/40",
            "fixed Q_rel leaf; Q_diag=0",
            "selected homogeneous trace u after lapse/Gauss reduction",
            "lambda=+/-i*sqrt(659/240)",
            "CERTIFIED",
            "For the serialized action the reduced Hamiltonian is positive and the two characteristic roots are simple imaginary roots.",
            evidence,
        ),
        _entry(
            "berger_unrestricted_d_charge",
            "stationary Berger R x S3 with a=1 and c_squared=9/40",
            "unrestricted union of relative-charge leaves",
            "D orbit with H_D=Omega*Q_rel modulo the closed diffeomorphism constraint",
            "NOT_APPLICABLE",
            "OBSTRUCTED",
            "D remains charged on the unrestricted union; it becomes presymplectic-null only after restriction to fixed Q_rel.",
            evidence,
        ),
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(PRODUCER.relative_to(ROOT)),
        "generated_by_sha256": _sha(PRODUCER),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": entries,
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_trace_charge_preflight.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_trace_charge_preflight.py",
            "python3 -m unittest -v d_quotient_classical.compensator.tests.test_two_phase_counterflow_trace_charge_preflight",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-trace-charge-preflight-fragment-v1.json",
        ],
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write() -> None:
    OUTPUT.write_text(_render(build()))


def check() -> None:
    if not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != build():
        raise AssertionError("generated atlas fragment drifted")
    print("TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_ATLAS_FRAGMENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
