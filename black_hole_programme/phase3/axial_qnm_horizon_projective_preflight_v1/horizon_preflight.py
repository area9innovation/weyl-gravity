#!/usr/bin/env python3
"""Phase-reduced horizon germ and affine projective preflight."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
    strict_candidate,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    af,
    inflate,
    panel_box,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MOVING = ROOT / "black_hole_programme/phase3/axial_partial_jet_horizon_moving_phase_v1/certificate.json"
INFINITY_RUN = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_affine_projective_transport_v1/affine-run.json"
RUN = HERE / "horizon-run.json"


def frobenius(omega: acb, order: int = 16) -> tuple[list, list, list]:
    # r^2(r-2)P_rr+(2r+2*i*w*r^3)P_r-6(r-1)P
    # +tau*i*(2*w^2*r+3*w^2+12)/(5*w)P=0.
    aa = [0, 4, 4, 1]
    bb = [4 + 16j * omega, 2 + 24j * omega, 12j * omega, 2j * omega]
    bb_dot = [16j, 24j, 12j, 2j]
    cc = [-6, -6]
    source = [1j * (7 * omega * omega + 12) / (5 * omega), 2j * omega / 5]
    base = [acb(1)]
    tau = [acb(0)]
    frequency = [acb(0)]
    for n in range(order - 1):
        target = n + 1
        pivot = acb(0)
        pivot_dot = acb(0)
        known = acb(0)
        known_tau = acb(0)
        known_frequency = acb(0)
        for j, value in enumerate(aa):
            k = n - j + 2
            if k >= 0:
                term = value * k * (k - 1)
                if k == target:
                    pivot += term
                elif k < len(base):
                    known += term * base[k]
                    known_tau += term * tau[k]
                    known_frequency += term * frequency[k]
        for j, value in enumerate(bb):
            k = n - j + 1
            if k >= 0:
                term = value * k
                term_dot = bb_dot[j] * k
                if k == target:
                    pivot += term
                    pivot_dot += term_dot
                elif k < len(base):
                    known += term * base[k]
                    known_tau += term * tau[k]
                    known_frequency += (
                        term * frequency[k] + term_dot * base[k]
                    )
        for j, value in enumerate(cc):
            k = n - j
            if 0 <= k < len(base):
                known += value * base[k]
                known_tau += value * tau[k]
                known_frequency += value * frequency[k]
        for j, value in enumerate(source):
            k = n - j
            if 0 <= k < len(base):
                known_tau += value * base[k]
        next_base = -known / pivot
        next_tau = -known_tau / pivot
        next_frequency = -(
            known_frequency * pivot - known * pivot_dot
        ) / (pivot * pivot)
        base.append(next_base)
        tau.append(next_tau)
        frequency.append(next_frequency)
    return base, tau, frequency


def horizon_seed(panel: int, panel_count: int = 16) -> tuple:
    ecs = json.loads(ECS.read_text())
    omega = panel_box(
        panel, panel_count, Fraction(ecs["disk"]["center_re"]),
        Fraction(ecs["disk"]["center_im"]),
        Fraction(ecs["disk"]["radius"]),
    )
    base, tau, frequency = frobenius(omega)
    rho = af(Fraction(1, 2**22))
    # The recurrence induction uses |f_n|,|g_n|,|u_n| <= 10^6*100^n.
    # At n>=16 the base/tau multiplier is <2 and the frequency multiplier
    # is <30; the first sixteen coefficients are checked by the producer.
    majorant = arb(10**6)
    growth = arb(100)
    x = growth * rho
    value_tail = majorant * x**16 / (1 - x)
    derivative_tail = (
        majorant * growth * 16 * x**15 / (1 - x) ** 2
    )

    def evaluate(coefficients: list) -> tuple[acb, acb]:
        value = acb(0)
        derivative = acb(0)
        for n, coefficient in enumerate(coefficients):
            value += coefficient * rho**n
            if n:
                derivative += n * coefficient * rho ** (n - 1)
        return inflate(value, value_tail), inflate(
            derivative, derivative_tail
        )

    p, p_r = evaluate(base)
    p_tau, p_tau_r = evaluate(tau)
    p_omega, p_omega_r = evaluate(frequency)
    lapse = rho / (2 + rho)
    p_x = lapse * p_r
    p_tau_x = lapse * p_tau_r
    p_omega_x = lapse * p_omega_r
    q = p_x / p
    eta = (p_tau_x * p - p_x * p_tau) / (p * p)
    xi = (p_omega_x * p - p_x * p_omega) / (p * p)
    return omega, q, eta, xi, base, tau, frequency


def forward_remainder(
    dq: arb, de: arb, dx: arb, r0: Fraction, step: Fraction,
    delta: arb, omega: acb, q0: acb, q1: acb, e0: acb, e1: acb,
    x0: acb, x1: acb, omega_lower: Fraction,
) -> tuple[tuple | None, str | None]:
    h = af(step)
    c_bound = af(r0) / af(r0 - 2)
    q_ref = max(q0.abs_upper(), q1.abs_upper())
    e_ref = max(e0.abs_upper(), e1.abs_upper())
    x_ref = max(x0.abs_upper(), x1.abs_upper())
    mu = c_bound * (
        2 * omega.imag.upper() - 2 * min(q0.real.lower(), q1.real.lower())
    )
    linear = mu + 2 * c_bound * delta
    forcing = 2 * c_bound * delta * q_ref
    qa = h * c_bound
    qb = h * linear - 1
    qc = dq + h * forcing
    disc = qb * qb - 4 * qa * qc
    if disc.lower() <= 0:
        return None, "HORIZON_Q_REMAINDER_DISCRIMINANT"
    proposed = (
        -float(qb.mid()) - float(disc.lower()) ** 0.5
    ) / (2 * float(qa.lower()))
    bq = arb(proposed * 1.000001)
    if (
        dq + h * (linear * bq + c_bound * bq * bq + forcing)
    ).upper() >= bq.lower():
        return None, "HORIZON_Q_REMAINDER_SELF_MAP"
    r_lower = af(r0)
    om = af(omega_lower)
    di = delta / 5 * (
        2 / r_lower**2
        + (12 / om**2 + 1) / r_lower**3
        + (6 + 24 / om**2) / r_lower**4
    )
    sensitivity_linear = mu + 2 * c_bound * delta + 2 * c_bound * bq
    denominator = 1 - h * sensitivity_linear
    if denominator.lower() <= 0:
        return None, "HORIZON_SENSITIVITY_REMAINDER_LINEAR"
    be = strict_candidate((
        de + h * (
            2 * c_bound * (delta + bq) * e_ref + c_bound * di
        )
    ) / denominator)
    bx = strict_candidate((
        dx + h * (
            2 * c_bound * (delta + bq) * x_ref + 2 * c_bound * bq
        )
    ) / denominator)
    if (
        de + h * (
            sensitivity_linear * be
            + 2 * c_bound * (delta + bq) * e_ref + c_bound * di
        )
    ).upper() >= be.lower():
        return None, "HORIZON_ETA_REMAINDER_SELF_MAP"
    if (
        dx + h * (
            sensitivity_linear * bx
            + 2 * c_bound * (delta + bq) * x_ref + 2 * c_bound * bq
        )
    ).upper() >= bx.lower():
        return None, "HORIZON_XI_REMAINDER_SELF_MAP"
    return (bq, be, bx), None


def compute() -> dict:
    ctx.prec = 128
    ecs = json.loads(ECS.read_text())
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    infinity = json.loads(INFINITY_RUN.read_text())
    rows = []
    for panel in range(16):
        omega_box, q_box, eta_box, xi_box, base, tau, frequency = horizon_seed(panel)
        coefficient_gate = all(
            coefficient.abs_upper() <= arb(10**6) * arb(100) ** n
            for sequence in (base, tau, frequency)
            for n, coefficient in enumerate(sequence)
        )
        omega_center = midpoint(omega_box)
        delta = radius_from(omega_box, omega_center)
        # Under omega'=-omega, (q,-eta,-xi) obeys the same reference
        # equations as the infinity reduced-amplitude rail.
        q_center = midpoint(q_box)
        e_center = midpoint(-eta_box)
        x_center = midpoint(-xi_box)
        dq = radius_from(q_box, q_center)
        de = radius_from(-eta_box, e_center)
        dx = radius_from(-xi_box, x_center)
        r = Fraction(2) + Fraction(1, 2**22)
        terminal = None
        match = None
        steps = 0
        while r < 32:
            rho = r - 2
            step = min(rho / 16, Fraction(1, 20), Fraction(32) - r)
            reference, metadata = reference_step(
                r, step, q_center, e_center, x_center, -omega_center
            )
            if reference is None:
                terminal = {
                    "radius": str(r), "failure": metadata["failure"],
                    "stage": "reference",
                }
                break
            qb, eb, xb = reference
            q1, e1, x1 = midpoint(qb), midpoint(eb), midpoint(xb)
            remainder, failure = forward_remainder(
                dq, de, dx, r, step, delta, omega_center,
                q_center, q1, e_center, e1, x_center, x1, omega_lower,
            )
            if remainder is None:
                terminal = {
                    "radius": str(r), "failure": failure,
                    "stage": "remainder",
                    "q_radius": str(dq.upper()),
                    "eta_radius": str(de.upper()),
                    "xi_radius": str(dx.upper()),
                }
                break
            dq, de, dx = remainder
            dq += radius_from(qb, q1)
            de += radius_from(eb, e1)
            dx += radius_from(xb, x1)
            q_center, e_center, x_center = q1, e1, x1
            r += step
            steps += 1
            if r == 32:
                match = {
                    "q_reduced_center": str(q_center),
                    "eta_reduced_center": str(-e_center),
                    "xi_reduced_center": str(-x_center),
                    "q_radius": str(dq.upper()),
                    "eta_radius": str(de.upper()),
                    "xi_radius": str(dx.upper()),
                }
        mismatch = None
        if match is not None:
            infinity_match = infinity["rows"][panel]["match_snapshot"]
            mismatch = {
                "status": "NOT_ASSEMBLED_IN_PREFLIGHT",
                "reason": (
                    "the infinity artifact stores midpoint/radius data; "
                    "a common affine omega generator must be reissued before "
                    "subtracting the two endpoint lines without double "
                    "counting parameter remainder"
                ),
                "infinity_match_snapshot": infinity_match,
            }
        rows.append({
            "panel": panel,
            "coefficient_majorant_seed_gate": coefficient_gate,
            "steps": steps,
            "last_radius": str(r),
            "reached_r32": match is not None,
            "match_snapshot": match,
            "terminal": terminal,
            "projective_mismatch": mismatch,
        })
    return {
        "schema": "phase3-axial-qnm-horizon-projective-run-v1",
        "panel_count": 16,
        "seed_radius": "2+2^-22",
        "moving_phase": "psi=exp(I*omega*r_star)*P",
        "dot_lambda_H": "0",
        "rows": rows,
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
