#!/usr/bin/env python3
"""Assemble horizon/outgoing projective mismatch and stop at the first gate."""
from __future__ import annotations

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
OUTGOING = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_ecs_affine_projective_transport_v1/affine-run.json"
)
HORIZON = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_reciprocal_checkpoint_transport_v1/checkpoint-run.json"
)
RUN = HERE / "mismatch-run.json"


def add_radius(*values: str) -> arb:
    return sum((arb(value) for value in values), arb(0))


def panel_mismatch(panel: int) -> dict:
    outgoing = json.loads(OUTGOING.read_text())["rows"][panel]
    horizon = json.loads(HORIZON.read_text())["rows"][panel]
    out = outgoing["match_snapshot"]
    hor = horizon["checkpoints"][2]["q_recovered"]
    omega = parse_acb(outgoing["omega_center"])
    omega_radius = arb(outgoing["omega_remainder_radius"])

    # Physical logarithmic derivatives:
    # horizon psi=exp(+i*omega*x) P_H -> i*omega+q_H;
    # outgoing psi=exp(-i*omega*x) P_+ -> -i*omega+q_+.
    delta_center = (
        parse_acb(hor["q_center"]) - parse_acb(out["q_center"]) + 2j * omega
    )
    delta_radius = (
        add_radius(hor["q_radius"], out["q_remainder_radius"])
        + 2 * omega_radius
    )
    delta_tau_center = (
        parse_acb(hor["q_tau_center"]) - parse_acb(out["eta_center"])
    )
    delta_tau_radius = add_radius(
        hor["q_tau_radius"], out["eta_remainder_radius"]
    )
    delta_omega_center = (
        parse_acb(hor["q_omega_center"]) - parse_acb(out["xi_center"]) + 2j
    )
    delta_omega_radius = add_radius(
        hor["q_omega_radius"], out["xi_remainder_radius"]
    )
    delta_full = inflate(delta_center, delta_radius)
    modulus_lower = delta_full.abs_lower()
    return {
        "panel": panel,
        "match_radius": 32,
        "common_chart": "physical logarithmic derivative",
        "phase_formula": "Delta=q_H-q_out+2*I*omega",
        "delta": {
            "center": str(delta_center),
            "radius": str(delta_radius.upper()),
            "modulus_lower": str(modulus_lower),
            "excludes_zero": modulus_lower > 0,
        },
        "delta_tau": {
            "center": str(delta_tau_center),
            "radius": str(delta_tau_radius.upper()),
            "formula": "q_H_tau-q_out_tau",
        },
        "delta_omega": {
            "center": str(delta_omega_center),
            "radius": str(delta_omega_radius.upper()),
            "formula": "q_H_omega-q_out_omega+2*I",
        },
        "dependency_scope": {
            "common_panel_index": True,
            "common_omega_center_used_for_phase": True,
            "serialized_cross_endpoint_affine_generator_available": False,
            "assembly_rule": (
                "independent certified endpoint remainders are summed; "
                "no unrecorded cancellation is assumed"
            ),
        },
    }


def compute() -> dict:
    ctx.prec = 128
    rows = [panel_mismatch(panel) for panel in range(16)]
    boundary = all(row["delta"]["excludes_zero"] for row in rows)
    return {
        "schema": "phase3-axial-qnm-two-sided-projective-mismatch-run-v1",
        "panel_count": 16,
        "match_radius": 32,
        "physical_mismatch": "Delta=q_H-q_out+2*I*omega",
        "rows": rows,
        "gates": {
            "boundary_nonvanishing": {
                "status": "PASS" if boundary else "FAIL_CLOSED",
                "passed_panel_count": sum(
                    row["delta"]["excludes_zero"] for row in rows
                ),
                "failure": None if boundary else (
                    "SERIALIZED_CROSS_ENDPOINT_DEPENDENCY_WIDTH_CONTAINS_ZERO"
                ),
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
