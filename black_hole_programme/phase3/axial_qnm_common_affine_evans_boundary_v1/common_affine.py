#!/usr/bin/env python3
"""Shared-generator endpoint Taylor exports and physical Evans mismatch."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from flint import acb, arb, ctx

import black_hole_programme.phase3.axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer as ci
import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
import black_hole_programme.phase3.axial_qnm_horizon_reciprocal_chart_transport_v1.reciprocal_transport as rc
from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
    remainder_step,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    af,
    inflate,
)
from ..axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "common-affine-run.json"

BASE_PANEL_COUNT = 16
REFINEMENT = 32
PANEL_COUNT = BASE_PANEL_COUNT * REFINEMENT
PANEL_LIMIT = 1
MATCH_RADIUS = Fraction(32)
TIGHT_TAYLOR_ORDER = 26


def _omega_lower() -> Fraction:
    return Fraction(json.loads(ECS.read_text())["disk"]["omega_modulus_lower"])


def _panel_geometry(panel: int, panel_count: int = PANEL_COUNT) -> tuple:
    ecs = json.loads(ECS.read_text())
    center_re = Fraction(ecs["disk"]["center_re"])
    center_im = Fraction(ecs["disk"]["center_im"])
    disk_radius = Fraction(ecs["disk"]["radius"])
    omega_box = ci.panel_box(
        panel, panel_count, center_re, center_im, disk_radius
    )
    omega_center = midpoint(omega_box)
    # This is the maximum distance from the midpoint of the circular arc to
    # either endpoint.  The acb rectangle used by the endpoint transports is
    # larger, but the shared generator itself ranges only over the arc.
    generator_radius = (
        2 * af(disk_radius)
        * (arb.pi() / (2 * panel_count)).sin()
    )
    return omega_box, omega_center, generator_radius


def _outgoing_transport(
    omega_box: acb,
    order: int = TIGHT_TAYLOR_ORDER,
) -> dict:
    """Certify the outgoing q, q_tau and q_omega balls at r=32."""
    with patch.object(ci, "panel_box", return_value=omega_box):
        _, q_box, eta_box, xi_box = ci.certified_panel_state(0, 1)
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(q_box)
    eta_center = midpoint(eta_box)
    xi_center = midpoint(xi_box)
    q_radius = radius_from(q_box, q_center)
    eta_radius = radius_from(eta_box, eta_center)
    xi_radius = radius_from(xi_box, xi_center)
    r = Fraction(45)
    accepted_steps = 0
    rejected_trials = 0
    while r > MATCH_RADIUS:
        step = max(Fraction(-1, 20), MATCH_RADIUS - r)
        while True:
            reference, metadata = reference_step(
                r, step, q_center, eta_center, xi_center, omega_center,
                order=order,
            )
            if reference is not None:
                q1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, metadata = remainder_step(
                    q_radius=q_radius,
                    eta_radius=eta_radius,
                    xi_radius=xi_radius,
                    r0=r,
                    step=step,
                    omega_radius=omega_radius,
                    omega_center=omega_center,
                    q0=q_center,
                    q1=q1,
                    eta0=eta_center,
                    eta1=eta1,
                    xi0=xi_center,
                    xi1=xi1,
                    omega_lower=_omega_lower(),
                )
            else:
                remainder = None
            if remainder is not None:
                break
            rejected_trials += 1
            step /= 2
            if abs(step) < Fraction(1, 320):
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": metadata["failure"],
                    "accepted_steps": accepted_steps,
                    "rejected_trials": rejected_trials,
                }
        q_radius, eta_radius, xi_radius = remainder
        q_radius += radius_from(reference[0], q1)
        eta_radius += radius_from(reference[1], eta1)
        xi_radius += radius_from(reference[2], xi1)
        q_center, eta_center, xi_center = q1, eta1, xi1
        r += step
        accepted_steps += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "q_tau": inflate(eta_center, eta_radius),
        "q_omega": inflate(xi_center, xi_radius),
        "accepted_steps": accepted_steps,
        "rejected_trials": rejected_trials,
        "chart": "q",
        "taylor_order": order,
    }


def _horizon_transport_reciprocal_baseline(omega_box: acb) -> dict:
    """Earlier repaired reciprocal rail, retained as a diagnostic baseline."""
    with patch.object(hp, "panel_box", return_value=omega_box):
        obstruction = rc.first_obstruction(0)
    q_full = inflate(obstruction["q_center"], obstruction["q_radius"])
    e_full = inflate(obstruction["e_center"], obstruction["e_radius"])
    x_full = inflate(obstruction["x_center"], obstruction["x_radius"])
    if q_full.abs_lower() <= 0:
        return {
            "passed": False,
            "radius": str(obstruction["radius"]),
            "failure": "RECIPROCAL_DENOMINATOR_CONTAINS_ZERO",
        }
    # The predecessor variables are E=-q_tau and X=-q_omega, so the
    # reciprocal sensitivities are E/q^2 and X/q^2.
    p_full = 1 / q_full
    eta_full = e_full / (q_full * q_full)
    xi_full = x_full / (q_full * q_full)
    p_center = midpoint(p_full)
    eta_center = midpoint(eta_full)
    xi_center = midpoint(xi_full)
    dp = radius_from(p_full, p_center)
    de = radius_from(eta_full, eta_center)
    dx = radius_from(xi_full, xi_center)
    r = obstruction["radius"]
    omega_center = obstruction["omega_center"]
    omega_radius = obstruction["omega_radius"]
    accepted_steps = 0
    rejected_trials = 0
    while r < MATCH_RADIUS:
        if r < 4:
            # An absolute step floor is invalid arbitrarily close to the
            # regular singular point.  Keep the Taylor disk inside r>2.
            nominal = min((r - 2) / 16, Fraction(1, 100))
        else:
            nominal = Fraction(1, 50) if r < 8 else Fraction(1, 20)
        step = min(nominal, MATCH_RADIUS - r)
        while True:
            reference, metadata = rc.p_reference_step(
                r, step, p_center, eta_center, xi_center, omega_center
            )
            if reference is not None:
                p1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, failure = rc.p_remainder_step(
                    dp, de, dx, r, step, omega_radius, omega_center,
                    p_center, p1, eta_center, eta1, xi_center, xi1,
                    _omega_lower(),
                )
            else:
                remainder = None
                failure = metadata["failure"]
            if remainder is not None:
                break
            rejected_trials += 1
            step /= 2
            # Near r=2 an absolute floor is still too coarse: the singleton
            # rail needs a step measured relative to the horizon distance.
            if step < (r - 2) / 2**24:
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                    "accepted_steps": accepted_steps,
                    "rejected_trials": rejected_trials,
                }
        dp, de, dx = remainder
        dp += radius_from(reference[0], p1)
        de += radius_from(reference[1], eta1)
        dx += radius_from(reference[2], xi1)
        p_center, eta_center, xi_center = p1, eta1, xi1
        r += step
        accepted_steps += 1
    p = inflate(p_center, dp)
    p_tau = inflate(eta_center, de)
    p_omega = inflate(xi_center, dx)
    if p.abs_lower() <= 0:
        return {
            "passed": False,
            "radius": str(r),
            "failure": "P_CHART_Q_RECOVERY_DENOMINATOR_CONTAINS_ZERO",
        }
    return {
        "passed": True,
        "q": 1 / p,
        "q_tau": -p_tau / (p * p),
        "q_omega": -p_omega / (p * p),
        "accepted_steps": accepted_steps,
        "rejected_trials": rejected_trials,
        "chart": "p=1/q",
        "taylor_order": 14,
    }


def _horizon_transport(
    omega_box: acb,
    order: int = TIGHT_TAYLOR_ORDER,
) -> dict:
    """Tight direct-q horizon export with adaptive high-order recentering."""
    with patch.object(hp, "panel_box", return_value=omega_box):
        _, q_box, eta_box, xi_box, *_ = hp.horizon_seed(0)
    omega_center = midpoint(omega_box)
    omega_radius = radius_from(omega_box, omega_center)
    q_center = midpoint(q_box)
    # hp.reference_step uses the infinity sign convention.  Under
    # omega'=-omega its sensitivity variables are E=-q_tau, X=-q_omega.
    eta_center = midpoint(-eta_box)
    xi_center = midpoint(-xi_box)
    q_radius = radius_from(q_box, q_center)
    eta_radius = radius_from(-eta_box, eta_center)
    xi_radius = radius_from(-xi_box, xi_center)
    r = Fraction(2) + Fraction(1, 2**22)
    accepted_steps = 0
    rejected_trials = 0
    while r < MATCH_RADIUS:
        nominal = min(
            (r - 2) / 16,
            Fraction(1, 100) if r < 4 else Fraction(1, 20),
            MATCH_RADIUS - r,
        )
        step = nominal
        while True:
            reference, metadata = reference_step(
                r, step, q_center, eta_center, xi_center, -omega_center,
                order=order,
            )
            if reference is not None:
                q1, eta1, xi1 = (midpoint(value) for value in reference)
                remainder, failure = hp.forward_remainder(
                    q_radius, eta_radius, xi_radius, r, step,
                    omega_radius, omega_center, q_center, q1,
                    eta_center, eta1, xi_center, xi1, _omega_lower(),
                )
            else:
                remainder = None
                failure = metadata["failure"]
            if remainder is not None:
                break
            rejected_trials += 1
            step /= 2
            if step < (r - 2) / 2**28:
                return {
                    "passed": False,
                    "radius": str(r),
                    "failure": failure,
                    "accepted_steps": accepted_steps,
                    "rejected_trials": rejected_trials,
                }
        q_radius, eta_radius, xi_radius = remainder
        q_radius += radius_from(reference[0], q1)
        eta_radius += radius_from(reference[1], eta1)
        xi_radius += radius_from(reference[2], xi1)
        q_center, eta_center, xi_center = q1, eta1, xi1
        r += step
        accepted_steps += 1
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "q_tau": inflate(-eta_center, eta_radius),
        "q_omega": inflate(-xi_center, xi_radius),
        "accepted_steps": accepted_steps,
        "rejected_trials": rejected_trials,
        "chart": "q",
        "taylor_order": order,
    }


def _endpoint_export(
    endpoint: str,
    box_state: dict,
    center_state: dict,
    generator_id: str,
    omega_center: acb,
    generator_radius: arb,
) -> dict:
    phase = (
        "psi=exp(+I*omega*r_star)*P_H"
        if endpoint == "horizon" else
        "psi=exp(-I*omega*r_star)*P_out"
    )
    if not box_state["passed"] or not center_state["passed"]:
        failed_name = "box" if not box_state["passed"] else "center"
        failed = box_state if failed_name == "box" else center_state
        return {
            "passed": False,
            "omega_generator_id": generator_id,
            "omega_center": str(omega_center),
            "omega_polynomial_basis": "zeta=omega-omega_center",
            "generator_modulus_upper": str(generator_radius.upper()),
            "q_polynomial_coefficients": None,
            "q_tau_polynomial_coefficients": None,
            "q_omega_polynomial_coefficients": None,
            "independent_residual_radius": None,
            "phase_convention": phase,
            "box_transport_passed": box_state["passed"],
            "center_transport_passed": center_state["passed"],
            "failed_transport": failed_name,
            "failure": failed["failure"],
            "radius": failed["radius"],
        }
    q0 = midpoint(center_state["q"])
    qt0 = midpoint(center_state["q_tau"])
    qw0 = midpoint(center_state["q_omega"])
    # Fundamental theorem of calculus on the common arc generator:
    # q(w)-q(wc)-qw0*(w-wc) is bounded by the center coefficient error plus
    # |w-wc| sup |q_w(w)-qw0|.
    q_center_error = radius_from(center_state["q"], q0)
    q_omega_deviation = (box_state["q_omega"] - qw0).abs_upper()
    q_residual = q_center_error + generator_radius * q_omega_deviation
    qt_residual = (box_state["q_tau"] - qt0).abs_upper()
    qw_residual = q_omega_deviation
    return {
        "passed": True,
        "omega_generator_id": generator_id,
        "omega_center": str(omega_center),
        "omega_polynomial_basis": "zeta=omega-omega_center",
        "generator_modulus_upper": str(generator_radius.upper()),
        "q_polynomial_coefficients": [str(q0), str(qw0)],
        "q_tau_polynomial_coefficients": [str(qt0)],
        "q_omega_polynomial_coefficients": [str(qw0)],
        "independent_residual_radius": {
            "q": str(q_residual.upper()),
            "q_tau": str(qt_residual.upper()),
            "q_omega": str(qw_residual.upper()),
        },
        "phase_convention": phase,
        "transport_diagnostics": {
            "box": {
                "accepted_steps": box_state["accepted_steps"],
                "rejected_trials": box_state["rejected_trials"],
                "chart": box_state["chart"],
                "taylor_order": box_state["taylor_order"],
            },
            "center": {
                "accepted_steps": center_state["accepted_steps"],
                "rejected_trials": center_state["rejected_trials"],
                "chart": center_state["chart"],
                "taylor_order": center_state["taylor_order"],
            },
        },
        "residual_rule": (
            "q residual follows from the certified q_omega enclosure and "
            "the fundamental theorem of calculus after subtracting the "
            "centered affine polynomial"
        ),
    }


def compute_panel(panel: int, panel_count: int = PANEL_COUNT) -> dict:
    omega_box, omega_center, generator_radius = _panel_geometry(
        panel, panel_count
    )
    singleton = acb(
        float(omega_center.real.mid()), float(omega_center.imag.mid())
    )
    generator_id = f"qnm-boundary-omega-{panel:04d}-of-{panel_count:04d}"
    outgoing_box = _outgoing_transport(omega_box)
    outgoing_center = _outgoing_transport(singleton)
    horizon_box = _horizon_transport(omega_box)
    horizon_center = _horizon_transport(singleton)
    outgoing = _endpoint_export(
        "outgoing", outgoing_box, outgoing_center, generator_id,
        omega_center, generator_radius,
    )
    horizon = _endpoint_export(
        "horizon", horizon_box, horizon_center, generator_id,
        omega_center, generator_radius,
    )
    row = {
        "panel": panel,
        "panel_count": panel_count,
        "omega_box": str(omega_box),
        "omega_generator_id": generator_id,
        "omega_center": str(omega_center),
        "generator_modulus_upper": str(generator_radius.upper()),
        "horizon": horizon,
        "outgoing": outgoing,
    }
    if not horizon["passed"] or not outgoing["passed"]:
        row["boundary_nonvanishing"] = {
            "status": "FAIL_CLOSED",
            "failure": "ENDPOINT_EXPORT_TRANSPORT_FAILED",
        }
        return row
    hq = [parse_acb(value) for value in horizon["q_polynomial_coefficients"]]
    oq = [parse_acb(value) for value in outgoing["q_polynomial_coefficients"]]
    delta0 = hq[0] - oq[0] + 2j * omega_center
    delta1 = hq[1] - oq[1] + 2j
    residual = (
        arb(horizon["independent_residual_radius"]["q"])
        + arb(outgoing["independent_residual_radius"]["q"])
    )
    lower = (
        delta0.abs_lower()
        - generator_radius * delta1.abs_upper()
        - residual
    )
    row["physical_mismatch"] = {
        "formula": "Delta=q_H-q_out+2*I*omega",
        "polynomial_coefficients": [str(delta0), str(delta1)],
        "independent_residual_radius": str(residual.upper()),
        "modulus_lower": str(max(arb(0), lower)),
    }
    row["boundary_nonvanishing"] = {
        "status": "PASS" if lower > 0 else "FAIL_CLOSED",
        "failure": None if lower > 0 else (
            "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO"
        ),
    }
    return row


def compute(panel_count: int = PANEL_COUNT, panel_limit: int = PANEL_LIMIT) -> dict:
    ctx.prec = 128
    rows = []
    first_failure = None
    for panel in range(min(panel_count, panel_limit)):
        row = compute_panel(panel, panel_count)
        rows.append(row)
        if row["boundary_nonvanishing"]["status"] != "PASS":
            first_failure = {
                "panel": panel,
                "failure": row["boundary_nonvanishing"]["failure"],
            }
            break
    boundary = first_failure is None and len(rows) == panel_limit
    endpoint_exports = all(
        row["horizon"]["passed"] and row["outgoing"]["passed"]
        for row in rows
    )
    return {
        "schema": "phase3-axial-qnm-common-affine-evans-boundary-run-v1",
        "base_panel_count": BASE_PANEL_COUNT,
        "refinement": panel_count // BASE_PANEL_COUNT,
        "panel_count": panel_count,
        "panel_limit": panel_limit,
        "match_radius": int(MATCH_RADIUS),
        "shared_generator": (
            "one panel-local zeta=omega-omega_center generator is used by "
            "both endpoint exports and the physical mismatch"
        ),
        "rows": rows,
        "gates": {
            "endpoint_polynomial_exports": {
                "status": "PASS" if endpoint_exports else "FAIL_CLOSED",
                "scope": "panel 0 only",
            },
            "tightened_panel0_boundary_nonvanishing": {
                "status": "PASS" if boundary else "FAIL_CLOSED",
                "scope": "panel 0 only",
                "method": (
                    "order-26 direct-q endpoint transports with adaptive "
                    "radial recentering and one shared omega generator"
                ),
            },
            "boundary_nonvanishing": {
                "status": "PASS" if boundary else "FAIL_CLOSED",
                "passed_panel_count": sum(
                    row["boundary_nonvanishing"]["status"] == "PASS"
                    for row in rows
                ),
                "first_failure": first_failure,
            },
            "argument_principle_root_count": {
                "status": "NOT_RUN",
                "prerequisite": (
                    "full-contour boundary_nonvanishing=PASS; this bounded "
                    "repair run covers panel 0 only"
                ),
            },
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
