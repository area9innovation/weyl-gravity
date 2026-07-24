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
MATCH_RADIUS = Fraction(32)


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


def _outgoing_transport(omega_box: acb) -> dict:
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
    while r > MATCH_RADIUS:
        step = max(Fraction(-1, 20), MATCH_RADIUS - r)
        reference, metadata = reference_step(
            r, step, q_center, eta_center, xi_center, omega_center
        )
        if reference is None:
            return {
                "passed": False,
                "radius": str(r),
                "failure": metadata["failure"],
            }
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
        if remainder is None:
            return {
                "passed": False,
                "radius": str(r),
                "failure": metadata["failure"],
            }
        q_radius, eta_radius, xi_radius = remainder
        q_radius += radius_from(reference[0], q1)
        eta_radius += radius_from(reference[1], eta1)
        xi_radius += radius_from(reference[2], xi1)
        q_center, eta_center, xi_center = q1, eta1, xi1
        r += step
    return {
        "passed": True,
        "q": inflate(q_center, q_radius),
        "q_tau": inflate(eta_center, eta_radius),
        "q_omega": inflate(xi_center, xi_radius),
    }


def _horizon_transport(omega_box: acb) -> dict:
    """Certify the horizon q, q_tau and q_omega balls at r=32."""
    with patch.object(hp, "panel_box", return_value=omega_box):
        obstruction = rc.first_obstruction(0)
    continuation = rc.reciprocal_continue(obstruction)
    if not continuation["reached_r4"]:
        return {
            "passed": False,
            "radius": continuation["terminal"]["radius"],
            "failure": continuation["terminal"]["failure"],
        }
    checkpoint = continuation["checkpoint_r4"]
    p_center = parse_acb(checkpoint["p_center"])
    eta_center = parse_acb(checkpoint["p_tau_center"])
    xi_center = parse_acb(checkpoint["p_omega_center"])
    dp = arb(checkpoint["p_radius"])
    de = arb(checkpoint["p_tau_radius"])
    dx = arb(checkpoint["p_omega_radius"])
    r = Fraction(4)
    omega_center = obstruction["omega_center"]
    omega_radius = obstruction["omega_radius"]
    while r < MATCH_RADIUS:
        nominal = Fraction(1, 50) if r < 8 else Fraction(1, 20)
        step = min(nominal, MATCH_RADIUS - r)
        reference, metadata = rc.p_reference_step(
            r, step, p_center, eta_center, xi_center, omega_center
        )
        if reference is None:
            return {
                "passed": False,
                "radius": str(r),
                "failure": metadata["failure"],
            }
        p1, eta1, xi1 = (midpoint(value) for value in reference)
        remainder, failure = rc.p_remainder_step(
            dp, de, dx, r, step, omega_radius, omega_center,
            p_center, p1, eta_center, eta1, xi_center, xi1,
            _omega_lower(),
        )
        if remainder is None:
            return {
                "passed": False,
                "radius": str(r),
                "failure": failure,
            }
        dp, de, dx = remainder
        dp += radius_from(reference[0], p1)
        de += radius_from(reference[1], eta1)
        dx += radius_from(reference[2], xi1)
        p_center, eta_center, xi_center = p1, eta1, xi1
        r += step
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


def compute(panel_count: int = PANEL_COUNT) -> dict:
    ctx.prec = 128
    rows = []
    first_failure = None
    for panel in range(panel_count):
        row = compute_panel(panel, panel_count)
        rows.append(row)
        if row["boundary_nonvanishing"]["status"] != "PASS":
            first_failure = {
                "panel": panel,
                "failure": row["boundary_nonvanishing"]["failure"],
            }
            break
    boundary = first_failure is None and len(rows) == panel_count
    return {
        "schema": "phase3-axial-qnm-common-affine-evans-boundary-run-v1",
        "base_panel_count": BASE_PANEL_COUNT,
        "refinement": panel_count // BASE_PANEL_COUNT,
        "panel_count": panel_count,
        "match_radius": int(MATCH_RADIUS),
        "shared_generator": (
            "one panel-local zeta=omega-omega_center generator is used by "
            "both endpoint exports and the physical mismatch"
        ),
        "rows": rows,
        "gates": {
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
                "prerequisite": "boundary_nonvanishing=PASS",
            },
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
