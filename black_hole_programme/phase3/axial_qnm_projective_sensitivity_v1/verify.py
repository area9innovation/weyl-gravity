#!/usr/bin/env python3
"""Independent symbolic verifier for projective sensitivity laws."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent


def verify(document: dict) -> list[str]:
    errors = []
    if document.get("schema") != "phase3-axial-qnm-projective-sensitivity-v1":
        errors.append("schema mismatch")
    q, p, omega, tau, V, Ical = sp.symbols(
        "q p omega tau V Ical"
    )
    q_rhs = 2 * sp.I * omega * q + V - tau * Ical - q**2
    p_direct = sp.factor(-q_rhs.subs(tau, 0) / q**2)
    p_expected = sp.factor(
        (1 - 2 * sp.I * omega * p - V * p**2).subs(p, 1 / q)
    )
    if sp.factor(p_direct - p_expected) != 0:
        errors.append("reciprocal base chart identity failed")
    eta, xi = sp.symbols("eta xi")
    if sp.diff(q_rhs, q).subs(tau, 0) * eta - Ical != (
        (2 * sp.I * omega - 2 * q) * eta - Ical
    ):
        errors.append("tau linearization failed")
    if (
        sp.diff(q_rhs, q).subs(tau, 0) * xi
        + sp.diff(q_rhs, omega).subs(tau, 0)
        != (2 * sp.I * omega - 2 * q) * xi + 2 * sp.I * q
    ):
        errors.append("omega linearization failed")
    flags = document["claim_flags"]
    for key in (
        "exact_two_chart_base_system",
        "exact_tau_sensitivity_system",
        "exact_omega_sensitivity_system",
        "exact_correlated_mobius_switch",
    ):
        if flags.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "two_sided_endpoint_lines_constructed",
        "contour_mismatch_enclosed",
        "interval_newton_gate_passed",
        "QNM_root_count_certified",
        "QNM_or_EP2_certified",
    ):
        if flags.get(key) is not False:
            errors.append(f"{key} must remain false")
    return errors


def main() -> int:
    errors = verify(json.loads((HERE / "certificate.json").read_text()))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS exact projective base and sensitivity system")
    return 0


if __name__ == "__main__":
    sys.exit(main())
