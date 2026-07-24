#!/usr/bin/env python3
"""Moving-phase horizon step and common-generator projective mismatch."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
)
from ..axial_qnm_horizon_projective_preflight_v1 import (
    horizon_preflight as hp,
)
from ..axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "rail-v2-run.json"
COMMON_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/certificate.json"
)
COMMON_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common-affine-run.json"
)

PANEL = 0
PANEL_COUNT = 512
ORDER = 26
R_START = Fraction(2) + Fraction(1, 2**22)
STEP = Fraction(1, 2**26)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite(*values: acb | arb) -> bool:
    return all(value.is_finite() for value in values)


def horizon_seed_with_pivot() -> tuple:
    """Reissue the moving-phase seed while retaining the chart pivot."""
    ecs = json.loads(hp.ECS.read_text())
    omega = hp.panel_box(
        PANEL,
        PANEL_COUNT,
        Fraction(ecs["disk"]["center_re"]),
        Fraction(ecs["disk"]["center_im"]),
        Fraction(ecs["disk"]["radius"]),
    )
    base, tau, frequency = hp.frobenius(omega)
    rho = hp.af(Fraction(1, 2**22))
    majorant = arb(10**6)
    growth = arb(100)
    scaled = growth * rho
    value_tail = majorant * scaled**16 / (1 - scaled)
    derivative_tail = (
        majorant * growth * 16 * scaled**15 / (1 - scaled) ** 2
    )

    def evaluate(coefficients: list) -> tuple[acb, acb]:
        value = acb(0)
        derivative = acb(0)
        for n, coefficient in enumerate(coefficients):
            value += coefficient * rho**n
            if n:
                derivative += n * coefficient * rho ** (n - 1)
        return hp.inflate(value, value_tail), hp.inflate(
            derivative, derivative_tail
        )

    p, p_r = evaluate(base)
    p_tau, p_tau_r = evaluate(tau)
    p_omega, p_omega_r = evaluate(frequency)
    if 0 in p:
        raise RuntimeError("moving-phase horizon pivot contains zero")
    lapse = rho / (2 + rho)
    p_x = lapse * p_r
    p_tau_x = lapse * p_tau_r
    p_omega_x = lapse * p_omega_r
    q = p_x / p
    q_tau = (p_tau_x * p - p_x * p_tau) / (p * p)
    q_omega = (p_omega_x * p - p_x * p_omega) / (p * p)
    if not _finite(p, q, q_tau, q_omega):
        raise RuntimeError("nonfinite post-normalization horizon seed")
    return omega, p, q, q_tau, q_omega


def one_horizon_step() -> dict:
    ecs = json.loads(hp.ECS.read_text())
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    omega, pivot, q, q_tau, q_omega = horizon_seed_with_pivot()
    omega_center = midpoint(omega)
    omega_radius = radius_from(omega, omega_center)
    q_center = midpoint(q)
    # The common reference solver uses the outgoing-sign equation.
    # Under omega'=-omega its sensitivity variables are
    # e=-q_tau and x=-q_omega.
    e_center = midpoint(-q_tau)
    x_center = midpoint(-q_omega)
    dq = radius_from(q, q_center)
    de = radius_from(-q_tau, e_center)
    dx = radius_from(-q_omega, x_center)
    reference, reference_gate = reference_step(
        R_START,
        STEP,
        q_center,
        e_center,
        x_center,
        -omega_center,
        order=ORDER,
    )
    if reference is None:
        return {
            "passed": False,
            "stage": "singleton_reference",
            "failure": reference_gate,
        }
    q1, e1, x1 = (midpoint(item) for item in reference)
    remainder, failure = hp.forward_remainder(
        dq,
        de,
        dx,
        R_START,
        STEP,
        omega_radius,
        omega_center,
        q_center,
        q1,
        e_center,
        e1,
        x_center,
        x1,
        omega_lower,
    )
    if remainder is None:
        return {
            "passed": False,
            "stage": "shared_parameter_remainder",
            "failure": failure,
        }
    dq, de, dx = remainder
    dq += radius_from(reference[0], q1)
    de += radius_from(reference[1], e1)
    dx += radius_from(reference[2], x1)
    q_next = hp.inflate(q1, dq)
    q_tau_next = hp.inflate(-e1, de)
    q_omega_next = hp.inflate(-x1, dx)
    finite = _finite(q_next, q_tau_next, q_omega_next)
    return {
        "passed": finite,
        "stage": None if finite else "post_normalization_finiteness",
        "failure": None if finite else "NONFINITE_POST_NORMALIZATION_STATE",
        "spectral_panel": {
            "panel": PANEL,
            "panel_count": PANEL_COUNT,
            "omega_box": str(omega),
            "omega_center": str(omega_center),
            "omega_remainder_radius": str(omega_radius.upper()),
        },
        "chart_gate": {
            "chart": "q_H=(partial_x P_H)/P_H",
            "phase": "psi=exp(+I*omega*r_star)*P_H",
            "pivot": "P_H",
            "pivot_ball": str(pivot),
            "pivot_modulus_lower": str(pivot.abs_lower()),
            "pivot_excludes_zero": 0 not in pivot,
            "fixed_chart": True,
            "chart_switch_used": False,
            "dot_lambda_H": "0",
            "tau_log_phase_absent": True,
        },
        "initial_state": {
            "radius": str(R_START),
            "q_H": str(q),
            "q_H_tau": str(q_tau),
            "q_H_omega": str(q_omega),
            "post_normalization_finite": _finite(q, q_tau, q_omega),
        },
        "transport": {
            "from_r": str(R_START),
            "to_r": str(R_START + STEP),
            "step": str(STEP),
            "taylor_order": ORDER,
            "q_H": str(q_next),
            "q_H_tau": str(q_tau_next),
            "q_H_omega": str(q_omega_next),
            "post_normalization_finite": finite,
            "reference_gate": reference_gate,
            "remainder_gate": {
                "failure": failure,
                "q_radius": str(dq.upper()),
                "q_tau_radius": str(de.upper()),
                "q_omega_radius": str(dx.upper()),
            },
        },
    }


def common_match() -> dict:
    """Independently assemble Delta and its sensitivities from typed exports."""
    certificate = json.loads(COMMON_CERT.read_text())
    recorded = json.loads(COMMON_RUN.read_text())
    if certificate["run"]["sha256"] != sha(COMMON_RUN):
        raise RuntimeError("common-affine run hash does not match certificate")
    if len(recorded["rows"]) != 1:
        raise RuntimeError("expected the bounded panel-0 common-affine run")
    row = recorded["rows"][0]
    horizon = row["horizon"]
    outgoing = row["outgoing"]
    generator_id = row["omega_generator_id"]
    shared_generator = (
        horizon["omega_generator_id"]
        == outgoing["omega_generator_id"]
        == generator_id
    )
    shared_center = (
        horizon["omega_center"]
        == outgoing["omega_center"]
        == row["omega_center"]
    )
    if not shared_generator or not shared_center:
        raise RuntimeError("endpoint exports do not share one omega generator")

    omega_center = parse_acb(row["omega_center"])
    generator_radius = arb(row["generator_modulus_upper"])
    hq = [parse_acb(v) for v in horizon["q_polynomial_coefficients"]]
    oq = [parse_acb(v) for v in outgoing["q_polynomial_coefficients"]]
    ht = parse_acb(horizon["q_tau_polynomial_coefficients"][0])
    ot = parse_acb(outgoing["q_tau_polynomial_coefficients"][0])
    hw = parse_acb(horizon["q_omega_polynomial_coefficients"][0])
    ow = parse_acb(outgoing["q_omega_polynomial_coefficients"][0])
    delta0 = hq[0] - oq[0] + 2j * omega_center
    delta1 = hq[1] - oq[1] + 2j
    delta_tau = ht - ot
    delta_omega = hw - ow + 2j
    derivative_sources_equal_affine_slopes = (
        horizon["q_omega_polynomial_coefficients"][0]
        == horizon["q_polynomial_coefficients"][1]
        and outgoing["q_omega_polynomial_coefficients"][0]
        == outgoing["q_polynomial_coefficients"][1]
    )
    delta_radius = (
        arb(horizon["independent_residual_radius"]["q"])
        + arb(outgoing["independent_residual_radius"]["q"])
    )
    delta_tau_radius = (
        arb(horizon["independent_residual_radius"]["q_tau"])
        + arb(outgoing["independent_residual_radius"]["q_tau"])
    )
    delta_omega_radius = (
        arb(horizon["independent_residual_radius"]["q_omega"])
        + arb(outgoing["independent_residual_radius"]["q_omega"])
    )
    lower = (
        delta0.abs_lower()
        - generator_radius * delta1.abs_upper()
        - delta_radius
    )
    values = (
        omega_center,
        generator_radius,
        *hq,
        *oq,
        ht,
        ot,
        hw,
        ow,
        delta0,
        delta1,
        delta_tau,
        delta_omega,
        delta_radius,
        delta_tau_radius,
        delta_omega_radius,
    )
    finite = _finite(*values)
    return {
        "passed": finite and lower > 0,
        "match_radius": recorded["match_radius"],
        "generator": {
            "id": generator_id,
            "shared_by_both_endpoints": shared_generator,
            "shared_center": shared_center,
            "omega_center": str(omega_center),
            "omega_center_source": row["omega_center"],
            "modulus_upper": str(generator_radius.upper()),
            "panel": row["panel"],
            "panel_count": row["panel_count"],
        },
        "typed_endpoint_fields": {
            "horizon": [
                "q_H",
                "q_H_tau",
                "q_H_omega",
            ],
            "outgoing": [
                "q_out",
                "q_out_tau",
                "q_out_omega",
            ],
            "all_post_normalization_values_finite": finite,
        },
        "mismatch": {
            "formula": "Delta=q_H-q_out+2*I*omega",
            "polynomial_coefficients": [str(delta0), str(delta1)],
            "independent_residual_radius": str(delta_radius.upper()),
            "modulus_lower": str(max(arb(0), lower)),
            "excludes_zero": lower > 0,
        },
        "tau_sensitivity": {
            "formula": "Delta_tau=q_H_tau-q_out_tau",
            "center": str(delta_tau),
            "independent_residual_radius": str(delta_tau_radius.upper()),
        },
        "omega_sensitivity": {
            "formula": "Delta_omega=q_H_omega-q_out_omega+2*I",
            "center": str(delta_omega),
            "independent_residual_radius": str(delta_omega_radius.upper()),
            "equals_affine_slope": derivative_sources_equal_affine_slopes,
            "equality_rule": (
                "both endpoint q_omega source coefficients are byte-identical "
                "to their q affine-slope source coefficients"
            ),
        },
    }


def compute() -> dict:
    ctx.prec = 128
    horizon = one_horizon_step()
    match = common_match()
    same_generator = (
        horizon.get("spectral_panel", {}).get("omega_center")
        == match["generator"]["omega_center_source"]
    )
    passed = horizon["passed"] and match["passed"] and same_generator
    return {
        "schema": "phase3-axial-qnm-projective-evans-riccati-run-v2",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "passed": passed,
        "horizon": horizon,
        "common_match": match,
        "interface_gates": {
            "same_refined_panel": (
                horizon.get("spectral_panel", {}).get("panel") == PANEL
                and match["generator"]["panel"] == PANEL
            ),
            "same_panel_count": (
                horizon.get("spectral_panel", {}).get("panel_count")
                == PANEL_COUNT
                and match["generator"]["panel_count"] == PANEL_COUNT
            ),
            "same_omega_center": same_generator,
            "shared_omega_generator": match["generator"][
                "shared_by_both_endpoints"
            ],
            "post_normalization_finiteness": (
                horizon.get("transport", {}).get(
                    "post_normalization_finite", False
                )
                and match["typed_endpoint_fields"][
                    "all_post_normalization_values_finite"
                ]
            ),
        },
        "scope": {
            "horizon_radial_panel_count": 1,
            "common_match_radius": 32,
            "common_match_panel_count": 1,
            "full_closed_contour": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
