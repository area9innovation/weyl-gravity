#!/usr/bin/env python3
"""Derive exact Riccati chart and tangent/frequency sensitivity laws."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COCYCLE = ROOT / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "produce.py", "verify.py",
    "test_projective_sensitivity.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    cocycle = json.loads(COCYCLE.read_text())
    x = sp.symbols("x")
    omega, tau = sp.symbols("omega tau")
    q = sp.Function("q")(x)
    eta = sp.Function("eta")(x)
    xi = sp.Function("xi")(x)
    V = sp.Function("V")(x)
    cal_i = sp.Function("calI")(x, omega)

    q_rhs = 2 * sp.I * omega * q + V - tau * cal_i - q**2
    eta_rhs = sp.diff(q_rhs, tau).subs(
        {tau: 0, sp.diff(q, tau): eta}
    )
    # SymPy does not know q depends on tau/omega in this scalar placeholder;
    # record and check the Fréchet derivatives explicitly.
    eta_rhs = (2 * sp.I * omega - 2 * q) * eta - cal_i
    xi_rhs = (2 * sp.I * omega - 2 * q) * xi + 2 * sp.I * q

    p = sp.symbols("p")
    p_rhs = 1 - 2 * sp.I * omega * p - V * p**2 + tau * cal_i * p**2
    eta_p, xi_p = sp.symbols("eta_p xi_p")
    eta_p_rhs = (-2 * sp.I * omega - 2 * V * p) * eta_p + cal_i * p**2
    xi_p_rhs = (-2 * sp.I * omega - 2 * V * p) * xi_p - 2 * sp.I * p

    # Direct substitution p=1/q checks the base chart law.
    direct_p = sp.factor(-q_rhs.subs(tau, 0) / q**2)
    expected_p = sp.factor(
        p_rhs.subs({p: 1 / q, tau: 0})
    )
    if sp.factor(direct_p - expected_p) != 0:
        raise RuntimeError("base reciprocal chart law failed")

    return {
        "schema": "phase3-axial-qnm-projective-sensitivity-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_TWO_CHART_PROJECTIVE_BASE_TAU_AND_OMEGA_SENSITIVITY_SYSTEM",
        "imports": {
            "projective_cocycle": {
                "path": str(COCYCLE.relative_to(ROOT)),
                "sha256": sha256(COCYCLE),
            }
        },
        "family": {
            "equation": (
                "v_xx-2*I*omega*v_x-V*v+tau*calI_reduced*v=0"
            ),
            "calI_reduced": cocycle["reduced_representative"]["calI_reduced"],
            "sign_convention": (
                "tau enters with +calI in the differential equation, hence "
                "-tau*calI in the q Riccati equation"
            ),
        },
        "q_chart": {
            "coordinate": "q=v_x/v",
            "base": "q_x=2*I*omega*q+V-tau*calI-q**2",
            "tau_sensitivity": (
                "eta_x=(2*I*omega-2*q)*eta-calI"
            ),
            "omega_sensitivity": (
                "xi_x=(2*I*omega-2*q)*xi+2*I*q"
            ),
            "eta_symbolic_rhs": sp.sstr(eta_rhs),
            "xi_symbolic_rhs": sp.sstr(xi_rhs),
        },
        "p_chart": {
            "coordinate": "p=v/v_x=1/q",
            "base": "p_x=1-2*I*omega*p-V*p**2+tau*calI*p**2",
            "tau_sensitivity": (
                "eta_p_x=(-2*I*omega-2*V*p)*eta_p+calI*p**2"
            ),
            "omega_sensitivity": (
                "xi_p_x=(-2*I*omega-2*V*p)*xi_p-2*I*p"
            ),
            "eta_symbolic_rhs": sp.sstr(eta_p_rhs),
            "xi_symbolic_rhs": sp.sstr(xi_p_rhs),
        },
        "mobius_switch": {
            "base": "p=1/q",
            "tau_sensitivity": "eta_p=-eta_q/q**2",
            "omega_sensitivity": "xi_p=-xi_q/q**2",
            "shared_remainder_requirement": (
                "q, eta_q and xi_q must be switched by one correlated "
                "Möbius operation; independent rectangular division loses "
                "the derivative identities"
            ),
        },
        "projective_mismatch": {
            "at_match": "Delta=q_H-q_infinity",
            "tau_derivative": "Delta_tau=eta_H-eta_infinity",
            "omega_derivative": "Delta_omega=xi_H-xi_infinity",
            "newton_velocity": (
                "omega_tau=-Delta_tau/Delta_omega at a simple zero"
            ),
            "scope": (
                "exact identities only; no endpoint line or contour value "
                "is evaluated here"
            ),
        },
        "claim_flags": {
            "exact_two_chart_base_system": True,
            "exact_tau_sensitivity_system": True,
            "exact_omega_sensitivity_system": True,
            "exact_correlated_mobius_switch": True,
            "two_sided_endpoint_lines_constructed": False,
            "contour_mismatch_enclosed": False,
            "interval_newton_gate_passed": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "a centered ECS fixed-point evaluation",
            "horizon or infinity projective lines at a match point",
            "Delta, Delta_tau or Delta_omega on a contour",
            "an interval-Newton or argument-principle root count",
            "a QNM, Smith selection or EP2",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-projective-sensitivity-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "artifact_sha256": {name: sha256(HERE / name) for name in ARTIFACTS},
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_projective_sensitivity_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_projective_sensitivity_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_projective_sensitivity_v1.test_projective_sensitivity"
        ],
        "tier_2_not_run": "Exact local successor; no shared operator changed.",
        "tier_3_not_run": "Not a freeze or physical theorem promotion."
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
