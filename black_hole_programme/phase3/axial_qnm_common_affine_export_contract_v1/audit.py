#!/usr/bin/env python3
"""Audit serialized endpoint artifacts for a common centered-omega algebra."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from flint import arb, ctx

import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
    reference_step,
)
from ..axial_qnm_horizon_projective_preflight_v1.horizon_preflight import (
    forward_remainder,
)
from ..axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
    parse_acb,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTGOING = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_ecs_affine_projective_transport_v1/affine-run.json"
)
HORIZON = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_reciprocal_checkpoint_transport_v1/checkpoint-run.json"
)
RUN = HERE / "audit-run.json"

REQUIRED_FIELDS = [
    "omega_generator_id",
    "omega_center",
    "omega_polynomial_basis",
    "q_polynomial_coefficients",
    "q_tau_polynomial_coefficients",
    "q_omega_polynomial_coefficients",
    "independent_residual_radius",
    "phase_convention",
]


def singleton_horizon_witness() -> dict:
    """Reproduce the first centered singleton self-map obstruction."""
    outgoing = json.loads(OUTGOING.read_text())
    omega_center = parse_acb(outgoing["rows"][0]["omega_center"])
    with patch.object(hp, "panel_box", return_value=omega_center):
        _, q_box, eta_box, xi_box, *_ = hp.horizon_seed(0)
    q = midpoint(q_box)
    eta = midpoint(-eta_box)
    xi = midpoint(-xi_box)
    dq = radius_from(q_box, q)
    de = radius_from(-eta_box, eta)
    dx = radius_from(-xi_box, xi)
    r = Fraction(2) + Fraction(1, 2**22)
    step = (r - 2) / 16
    reference, metadata = reference_step(
        r, step, q, eta, xi, -omega_center
    )
    assert reference is not None, metadata
    q1, eta1, xi1 = (midpoint(value) for value in reference)
    remainder, failure = forward_remainder(
        dq, de, dx, r, step, arb(0), omega_center,
        q, q1, eta, eta1, xi, xi1, Fraction(1, 4),
    )
    return {
        "panel": 0,
        "omega_is_singleton": True,
        "omega_radius": "0",
        "radius": str(r),
        "attempted_step": str(step),
        "reference_step_passed": True,
        "remainder_step_passed": remainder is not None,
        "failure": failure,
        "seed_q_radius": str(dq.upper()),
        "seed_tau_radius": str(de.upper()),
        "seed_omega_radius": str(dx.upper()),
        "reference_q_width": str(radius_from(reference[0], q1).upper()),
    }


def compute() -> dict:
    ctx.prec = 128
    outgoing = json.loads(OUTGOING.read_text())
    horizon = json.loads(HORIZON.read_text())
    out_fields = set(outgoing["rows"][0]["match_snapshot"])
    hor_fields = set(horizon["rows"][0]["checkpoints"][2])
    return {
        "schema": "phase3-axial-qnm-common-affine-export-audit-run-v1",
        "required_common_export_contract": REQUIRED_FIELDS,
        "current_artifacts": {
            "outgoing_missing_fields": sorted(set(REQUIRED_FIELDS) - out_fields),
            "horizon_missing_fields": sorted(set(REQUIRED_FIELDS) - hor_fields),
            "common_generator_available": False,
            "independent_residuals_after_polynomial_subtraction_available": False,
        },
        "physical_phase_rule": {
            "mismatch": "Delta=q_H-q_out+2*I*omega",
            "omega_derivative": "Delta_omega=q_H_omega-q_out_omega+2*I",
            "must_be_applied_symbolically": True,
        },
        "bounded_joint_rerun_attempt": singleton_horizon_witness(),
        "gates": {
            "boundary_nonvanishing": {
                "status": "NOT_RUN",
                "failure": "COMMON_AFFINE_EXPORT_CONTRACT_UNAVAILABLE",
            },
            "argument_principle_root_count": {
                "status": "NOT_RUN",
                "prerequisite": "boundary_nonvanishing=PASS",
            },
            "K0_or_interval_newton_defect": {
                "status": "NOT_RUN",
                "prerequisite": "argument_principle_root_count certified",
            },
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
