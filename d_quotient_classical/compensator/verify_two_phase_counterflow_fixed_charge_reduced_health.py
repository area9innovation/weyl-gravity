#!/usr/bin/env python3
"""Independent exact verifier for the fixed-charge reduction obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    certificate = json.loads(CERT.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload hash mismatch")
    for record in certificate["imports"].values():
        if _sha(ROOT / record["path"]) != record["sha256"]:
            raise AssertionError("import drift")
    fibre = payload["derived_fixed_charge_fibre"]
    differential = sp.Matrix([[sp.Integer(x) for x in row] for row in fibre["differential"]])
    homotopy = sp.Matrix([[sp.Integer(x) for x in row] for row in fibre["contracting_homotopy"]])
    if differential**2 != sp.zeros(4) or differential * homotopy + homotopy * differential != sp.eye(4):
        raise AssertionError("derived fibre is not exact")
    d_minus = differential[1:3, 0:1]
    d_zero = differential[3:4, 1:3]
    h_minus = 1 - d_minus.rank()
    h_zero = 2 - d_zero.rank() - d_minus.rank()
    h_plus = 1 - d_zero.rank()
    if [h_minus, h_zero, h_plus] != [0, 0, 0]:
        raise AssertionError("charge-fibre cohomology did not vanish")
    omega = sp.Matrix([[sp.Integer(x) for x in row] for row in fibre["shifted_pairing_matrix"]])
    if omega.rank() != 4:
        raise AssertionError("shifted pairing is degenerate before reduction")
    if certificate["terminal_verdict"]["positive_relative_clock_survives"]:
        raise AssertionError("clock-survival claim contradicts exact quotient")
    fixed = payload["charge_ledger"]["fixed_Q_rel_fibre"]
    if fixed["D"] != "null because i_D Omega=Omega_background*delta_Q_rel=0" or fixed["D_identified_with_K_before_reduction"]:
        raise AssertionError("D/K audit drifted")
    print("INDEPENDENT FIXED-CHARGE REDUCED-HEALTH VERIFIER: PASS")


if __name__ == "__main__":
    verify()
