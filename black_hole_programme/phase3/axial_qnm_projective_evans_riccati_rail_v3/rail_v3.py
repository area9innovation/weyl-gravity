#!/usr/bin/env python3
"""Audit typed two-sided projective data on the certified boundary chunk."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    inflate,
)
from ..axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "rail-v3-run.json"
CHUNK_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v1/certificate.json"
)
CHUNK_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v1/chunk-run.json"
)
V1 = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v1/certificate.json"
)
V2 = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v2/certificate.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite(*values: acb | arb) -> bool:
    return all(value.is_finite() for value in values)


def typed_row(row: dict) -> dict:
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
    qh = [parse_acb(item) for item in horizon[
        "q_polynomial_coefficients"
    ]]
    qo = [parse_acb(item) for item in outgoing[
        "q_polynomial_coefficients"
    ]]
    qht = parse_acb(horizon["q_tau_polynomial_coefficients"][0])
    qot = parse_acb(outgoing["q_tau_polynomial_coefficients"][0])
    qhw = parse_acb(horizon["q_omega_polynomial_coefficients"][0])
    qow = parse_acb(outgoing["q_omega_polynomial_coefficients"][0])
    omega_center = parse_acb(row["omega_center"])
    generator_radius = arb(row["generator_modulus_upper"])
    delta0 = qh[0] - qo[0] + 2j * omega_center
    delta1 = qh[1] - qo[1] + 2j
    delta_tau = qht - qot
    delta_omega = qhw - qow + 2j
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
    delta_tau_ball = inflate(delta_tau, delta_tau_radius)
    delta_omega_ball = inflate(delta_omega, delta_omega_radius)
    lower = (
        delta0.abs_lower()
        - generator_radius * delta1.abs_upper()
        - delta_radius
    )
    affine_derivative_identity = (
        horizon["q_omega_polynomial_coefficients"][0]
        == horizon["q_polynomial_coefficients"][1]
        and outgoing["q_omega_polynomial_coefficients"][0]
        == outgoing["q_polynomial_coefficients"][1]
    )
    values = (
        omega_center,
        generator_radius,
        *qh,
        *qo,
        qht,
        qot,
        qhw,
        qow,
        delta0,
        delta1,
        delta_tau,
        delta_omega,
        delta_radius,
        delta_tau_radius,
        delta_omega_radius,
    )
    finite = _finite(*values)
    fixed_q_chart = (
        horizon["transport_diagnostics"]["box"]["chart"] == "q"
        and horizon["transport_diagnostics"]["center"]["chart"] == "q"
        and outgoing["transport_diagnostics"]["box"]["chart"] == "q"
        and outgoing["transport_diagnostics"]["center"]["chart"] == "q"
    )
    return {
        "panel": row["panel"],
        "panel_count": row["panel_count"],
        "match_radius": 32,
        "omega_generator_id": generator_id,
        "interface_gates": {
            "shared_generator": shared_generator,
            "shared_center": shared_center,
            "fixed_q_chart": fixed_q_chart,
            "post_normalization_finite": finite,
            "opposite_moving_phases": (
                horizon["phase_convention"]
                == "psi=exp(+I*omega*r_star)*P_H"
                and outgoing["phase_convention"]
                == "psi=exp(-I*omega*r_star)*P_out"
            ),
        },
        "delta": {
            "formula": "Delta=q_H-q_out+2*I*omega",
            "polynomial_coefficients": [str(delta0), str(delta1)],
            "independent_residual_radius": str(delta_radius.upper()),
            "modulus_lower": str(max(arb(0), lower)),
            "excludes_zero": lower > 0,
        },
        "delta_tau": {
            "formula": "Delta_tau=q_H_tau-q_out_tau",
            "center": str(delta_tau),
            "independent_residual_radius": str(
                delta_tau_radius.upper()
            ),
            "ball": str(delta_tau_ball),
            "excludes_zero": 0 not in delta_tau_ball,
        },
        "delta_omega": {
            "formula": "Delta_omega=q_H_omega-q_out_omega+2*I",
            "center": str(delta_omega),
            "independent_residual_radius": str(
                delta_omega_radius.upper()
            ),
            "ball": str(delta_omega_ball),
            "excludes_zero": 0 not in delta_omega_ball,
            "equals_affine_slope": affine_derivative_identity,
        },
    }


def compute() -> dict:
    ctx.prec = 128
    chunk_certificate = json.loads(CHUNK_CERT.read_text())
    chunk = json.loads(CHUNK_RUN.read_text())
    if chunk_certificate["run"]["sha256"] != sha(CHUNK_RUN):
        raise RuntimeError("chunk run hash does not match its certificate")
    rows = [typed_row(row) for row in chunk["rows"]]
    co_location = all(
        all(row["interface_gates"].values()) for row in rows
    )
    nonzero = all(row["delta"]["excludes_zero"] for row in rows)
    tau_nonzero_count = sum(
        row["delta_tau"]["excludes_zero"] for row in rows
    )
    omega_nonzero_count = sum(
        row["delta_omega"]["excludes_zero"] for row in rows
    )
    completed = len(rows)
    full = chunk["full_contour_panel_count"]
    first_missing = completed if completed < full else None

    v1 = json.loads(V1.read_text())
    v2 = json.loads(V2.read_text())
    pivot_gate = {
        "panel": 0,
        "outgoing_seed_pivot_excludes_zero": v1["claim_flags"][
            "outgoing_seed_pivot_excludes_zero"
        ],
        "horizon_seed_pivot_excludes_zero": v2["result"]["horizon"][
            "chart_gate"
        ]["pivot_excludes_zero"],
        "horizon_dot_lambda_H": v2["result"]["horizon"][
            "chart_gate"
        ]["dot_lambda_H"],
        "fixed_mobius_chart": "q",
        "switch_required_on_completed_chunk": False,
        "scope": (
            "explicit seed pivots are imported for panel 0; panels 1--15 "
            "carry certified finite direct-q self-map transports but no "
            "separate serialized amplitude-pivot lower bound"
        ),
    }
    return {
        "schema": "phase3-axial-qnm-projective-evans-riccati-run-v3",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "status": "BOUNDED_PROGRESS_FAIL_CLOSED_BEFORE_LOCAL_QNM_TEST",
        "rows": rows,
        "summary": {
            "completed_panel_count": completed,
            "full_contour_panel_count": full,
            "two_sided_co_location_passed": co_location,
            "all_completed_deltas_exclude_zero": nonzero,
            "delta_tau_excludes_zero_panel_count": tau_nonzero_count,
            "delta_omega_excludes_zero_panel_count": omega_nonzero_count,
            "minimum_delta_modulus_lower": chunk_certificate["result"][
                "minimum_modulus_lower"
            ],
            "minimum_delta_modulus_lower_panel": chunk_certificate[
                "result"
            ]["minimum_modulus_lower_panel"],
        },
        "chart_and_pivot_gate": pivot_gate,
        "local_qnm_gate": {
            "status": "FAIL_CLOSED",
            "first_obstruction": {
                "code": "INCOMPLETE_CLOSED_BOUNDARY_COVERAGE",
                "completed_panels": completed,
                "required_panels": full,
                "first_missing_panel": first_missing,
                "missing_field": (
                    f"shared-generator horizon/outgoing q,q_tau,q_omega "
                    f"exports at r=32 for panel {first_missing}/{full}"
                ),
            },
            "parallel_quantitative_obstruction": {
                "code": "PROJECTIVE_SENSITIVITY_BALLS_CONTAIN_ZERO",
                "delta_tau_excludes_zero_panel_count": tau_nonzero_count,
                "delta_omega_excludes_zero_panel_count": omega_nonzero_count,
                "completed_panel_count": completed,
                "meaning": (
                    "current rectangular sensitivity remainders cannot "
                    "certify either a nonzero intrinsic selector or a "
                    "simple-root Newton denominator on the completed arc"
                ),
            },
            "interval_newton_run": False,
            "argument_principle_run": False,
            "reason": (
                "a local root enclosure or closed-contour root count is a "
                "prerequisite; neither is available after 16/512 panels"
            ),
        },
        "scope": {
            "common_match_radius": 32,
            "two_sided_boundary_panels": completed,
            "full_closed_contour": False,
            "QNM_or_EP2": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
