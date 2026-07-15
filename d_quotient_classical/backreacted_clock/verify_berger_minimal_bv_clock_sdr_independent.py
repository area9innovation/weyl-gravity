#!/usr/bin/env python3
"""Independent exact check of the minimal Berger-clock BV contraction.

This checker deliberately does not import the producer.  It reconstructs the
clock incidence, the differential field change, its cotangent lift, and the
eight-row cyclic contraction from the formulas recorded in the theorem.  It
also reads the emitted certificate only to check the scoped claim boundary.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_MINIMAL_BV_CLOCK_SDR.json"
)
LAYOUT_CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_RETAINED_MINIMAL_LAYOUT.json"
)


def main() -> None:
    eta = sp.diag(-1, 1, 1, 1)
    pairs = [(mu, nu) for mu in range(4) for nu in range(mu, 4)]
    rho, omega = sp.symbols("rho omega", nonzero=True)
    p0, p1, p2, p3 = sp.symbols("p0:4")
    p = (p0, p1, p2, p3)
    n_lower = (-1, 0, 0, 0)

    metric = sp.Matrix([eta[mu, nu] for mu, nu in pairs])
    temporal = sp.Matrix(
        [p[mu] * n_lower[nu] + p[nu] * n_lower[mu] for mu, nu in pairs]
    )
    spatial = sp.zeros(10, 3)
    for row, (mu, nu) in enumerate(pairs):
        for column, index in enumerate((1, 2, 3)):
            spatial[row, column] = (
                p[mu] * int(nu == index) + p[nu] * int(mu == index)
            )

    # old=(h,delta rho,delta theta), new=(h_hat,R,Theta)
    change = sp.eye(12)
    change[:10, 10] = 2 * metric / rho
    change[:10, 11] = -temporal / omega
    change[10, 10] = 1 / rho
    change[11, 11] = 1 / omega
    assert sp.factor(change.det()) == 1 / (rho * omega)

    raw = sp.zeros(12, 5)
    raw[:10, :3] = spatial
    raw[:10, 3] = temporal
    raw[:10, 4] = 2 * metric
    raw[10, 4] = -rho
    raw[11, 3] = omega
    dressed = sp.simplify(change * raw)
    expected = sp.zeros(12, 5)
    expected[:10, :3] = spatial
    expected[10, 4] = -1
    expected[11, 3] = 1
    assert dressed == expected

    # Verify the complete 34-coordinate cotangent lift independently.
    pairing = sp.zeros(34)
    pairing[0:5, 29:34] = sp.eye(5)
    pairing[29:34, 0:5] = -sp.eye(5)
    pairing[5:17, 17:29] = sp.eye(12)
    pairing[17:29, 5:17] = -sp.eye(12)
    lift = sp.eye(34)
    lift[5:17, 5:17] = change
    lift[17:29, 17:29] = change.inv().T
    assert sp.simplify(lift.inv().T * pairing * lift.inv()) == pairing

    # Clock order=(tau,sigma,Theta,R,Theta*,R*,tau*,sigma*).
    incidence = sp.diag(1, -1)
    differential = sp.zeros(8)
    differential[2:4, 0:2] = incidence
    differential[6:8, 4:6] = -incidence.T
    homotopy = sp.zeros(8)
    homotopy[0:2, 2:4] = incidence.inv()
    homotopy[4:6, 6:8] = -incidence.T.inv()
    clock_pairing = sp.zeros(8)
    clock_pairing[0:2, 6:8] = sp.eye(2)
    clock_pairing[6:8, 0:2] = -sp.eye(2)
    clock_pairing[2:4, 4:6] = sp.eye(2)
    clock_pairing[4:6, 2:4] = -sp.eye(2)
    zero = sp.zeros(8)
    assert differential**2 == zero
    assert differential * homotopy + homotopy * differential == sp.eye(8)
    assert homotopy**2 == zero
    assert differential.T * clock_pairing + clock_pairing * differential == zero
    assert homotopy.T * clock_pairing + clock_pairing * homotopy == zero

    payload = json.loads(CERTIFICATE.read_text())
    layout = json.loads(LAYOUT_CERTIFICATE.read_text())
    layout_digest = hashlib.sha256(
        json.dumps(layout, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert payload["claim_status"] == "CERTIFIED_MINIMAL_CLOCK_SECTOR_SDR"
    assert payload["sdr"]["contracted_clock_dimension"] == 8
    assert payload["sdr"]["retained_minimal_dimension"] == 26
    assert payload["retained_layout_ref"]["payload_sha256"] == layout_digest
    assert payload["retained_layout_ref"]["component_count"] == 26
    assert payload["next_gate"] == "BERGER_RETAINED_MINIMAL_OPERATOR"
    flags = payload["flags"]
    assert flags["support_local_clock_SDR_exact"] is True
    for open_flag in (
        "retained_dressed_metric_q1_coefficients_complete",
        "gauge_fixed_nonminimal_rows_complete",
        "retained_operator_stability_proved",
        "causal_green_homotopy_constructed",
        "full_Berger_clock_BV_theorem",
    ):
        assert flags[open_flag] is False

    print("BERGER_MINIMAL_BV_CLOCK_SDR_INDEPENDENT: PASS")
    print("dressed incidence and canonical lift: PASS")
    print("eight-row cyclic contraction: PASS")
    print("fail-closed claim boundary: PASS")


if __name__ == "__main__":
    main()
