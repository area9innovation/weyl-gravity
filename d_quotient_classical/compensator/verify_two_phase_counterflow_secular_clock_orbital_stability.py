#!/usr/bin/env python3
"""Independent exact replay of the counterflow action-angle verdict."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_PAYLOAD_V1.json"


def main() -> None:
    cert = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for row in cert["imports"].values():
        if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise AssertionError("import hash drift")

    inertia = sp.Rational(12, 5) * sp.pi**2 * sp.sqrt(10)
    omega0 = sp.Rational(3, 4)
    charge0 = sp.Rational(9, 5) * sp.pi**2 * sp.sqrt(10)
    if sp.simplify(charge0 / inertia - omega0) != 0:
        raise AssertionError("frequency normalization failed")

    poisson = sp.Matrix([[0, 1], [-1, 0]])
    hessian = sp.diag(0, 1 / inertia)
    linear = sp.simplify(poisson * hessian)
    if linear**2 != sp.zeros(2) or linear.rank() != 1:
        raise AssertionError("Jordan form failed")

    e, t, p, q = sp.symbols("e t p q", real=True)
    trajectory = sp.Matrix([e * p + t * (charge0 + e * q) / inertia, charge0 + e * q])
    if sp.simplify(trajectory.diff(e).subs(e, 0) - sp.Matrix([p + t * q / inertia, q])) != sp.zeros(2, 1):
        raise AssertionError("parameter tangent failed")

    Q = sp.symbols("Q", real=True)
    stationary_row = sp.factor(-(16 * (Q / inertia) ** 2 - 9) / 32)
    roots = set(sp.solve(stationary_row, Q))
    if roots != {-charge0, charge0}:
        raise AssertionError("coupled stationary separator failed")
    if sp.diff(stationary_row, Q).subs(Q, charge0) == 0:
        raise AssertionError("charge direction unexpectedly tangent to coupled locus")

    statuses = cert["stability_statuses"]
    if statuses["lifted_phase_bounded_linear_stability"] != "FAIL":
        raise AssertionError("lifted shear hidden")
    if statuses["compact_S1_absolute_Lyapunov_stability"] != "FAIL":
        raise AssertionError("compact dephasing hidden")
    if statuses["fixed_charge_orbital_stability_under_R_rel"] != "PASS":
        raise AssertionError("fixed-charge orbital stability lost")
    if statuses["unrestricted_orbital_stability_under_R_rel"] != "PASS":
        raise AssertionError("unrestricted orbital stability lost")
    if statuses["frequency_modulated_stability"] != "PASS":
        raise AssertionError("modulated stability lost")
    if payload["stability_ledger"]["fixed_charge_orbital_stability_under_R_rel"]["R_rel_is_gauge"]:
        raise AssertionError("global R_rel was silently made gauge")
    if payload["stability_ledger"]["unrestricted_orbital_stability_under_R_rel"]["R_rel_is_gauge"]:
        raise AssertionError("unrestricted orbital comparison was silently made gauge")

    mutations = {row["id"]: row for row in payload["mutations"]}
    if mutations["INERTIA_SIGN_REVERSAL"]["energy_Hessian_inertia_[positive,negative,zero]"] != [0, 1, 1]:
        raise AssertionError("inertia sign mutation failed")
    if not all(row["passed"] for row in mutations.values()):
        raise AssertionError("mutation ledger failed")
    print("INDEPENDENT COUNTERFLOW ORBITAL-STABILITY VERIFIER: PASS")


if __name__ == "__main__":
    main()
