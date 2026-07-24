#!/usr/bin/env python3
"""Continue the certified horizon reciprocal chart to geometric checkpoints."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

from ..axial_qnm_ecs_affine_projective_transport_v1.affine_transport import (
    midpoint,
    radius_from,
)
from ..axial_qnm_ecs_centered_projective_initializer_v1.centered_initializer import (
    ECS,
    inflate,
)
from ..axial_qnm_horizon_reciprocal_chart_transport_v1.reciprocal_transport import (
    first_obstruction,
    p_reference_step,
    p_remainder_step,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_reciprocal_chart_transport_v1/reciprocal-run.json"
)
RUN = HERE / "checkpoint-run.json"
CHECKPOINTS = (Fraction(8), Fraction(16), Fraction(32))


def parse_acb(text: str) -> acb:
    real, imag = text.rsplit(" + ", 1)
    return acb(arb(real), arb(imag[:-1]))


def snapshot(
    p_center: acb,
    p_tau_center: acb,
    p_omega_center: acb,
    p_radius: arb,
    p_tau_radius: arb,
    p_omega_radius: arb,
) -> dict:
    """Emit p data and a certified conversion back to the q projective line."""
    p_full = inflate(p_center, p_radius)
    p_tau_full = inflate(p_tau_center, p_tau_radius)
    p_omega_full = inflate(p_omega_center, p_omega_radius)
    p_modulus_lower = p_full.abs_lower()
    result = {
        "p_center": str(p_center),
        "p_radius": str(p_radius.upper()),
        "p_tau_center": str(p_tau_center),
        "p_tau_radius": str(p_tau_radius.upper()),
        "p_omega_center": str(p_omega_center),
        "p_omega_radius": str(p_omega_radius.upper()),
        "p_modulus_lower": str(p_modulus_lower),
        "q_recovery_denominator_excludes_zero": p_modulus_lower > 0,
    }
    if p_modulus_lower <= 0:
        result["q_recovered"] = None
        return result
    q_full = 1 / p_full
    q_tau_full = -p_tau_full / (p_full * p_full)
    q_omega_full = -p_omega_full / (p_full * p_full)
    q_center = midpoint(q_full)
    q_tau_center = midpoint(q_tau_full)
    q_omega_center = midpoint(q_omega_full)
    result["q_recovered"] = {
        "q_center": str(q_center),
        "q_radius": str(radius_from(q_full, q_center).upper()),
        "q_tau_center": str(q_tau_center),
        "q_tau_radius": str(radius_from(q_tau_full, q_tau_center).upper()),
        "q_omega_center": str(q_omega_center),
        "q_omega_radius": str(radius_from(q_omega_full, q_omega_center).upper()),
        "shared_derivative_rule": (
            "q=1/p; q_tau=-p_tau/p^2; q_omega=-p_omega/p^2"
        ),
    }
    return result


def initial_state(panel: int) -> tuple:
    parent = json.loads(PARENT_RUN.read_text())
    row = parent["rows"][panel]["checkpoint_r4"]
    obstruction = first_obstruction(panel)
    return (
        obstruction,
        parse_acb(row["p_center"]),
        parse_acb(row["p_tau_center"]),
        parse_acb(row["p_omega_center"]),
        arb(row["p_radius"]),
        arb(row["p_tau_radius"]),
        arb(row["p_omega_radius"]),
    )


def continue_panel(panel: int) -> dict:
    ecs = json.loads(ECS.read_text())
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    obstruction, p_center, eta_center, xi_center, dp, de, dx = initial_state(panel)
    r = Fraction(4)
    accepted = 0
    rejected = 0
    checkpoint_rows = []
    minimum_step = Fraction(1, 2**22)
    for target in CHECKPOINTS:
        while r < target:
            nominal = Fraction(1, 50) if r < 8 else Fraction(1, 20)
            step = min(nominal, target - r)
            while True:
                reference, metadata = p_reference_step(
                    r, step, p_center, eta_center, xi_center,
                    obstruction["omega_center"],
                )
                if reference is not None:
                    p1, eta1, xi1 = (midpoint(value) for value in reference)
                    remainder, failure = p_remainder_step(
                        dp, de, dx, r, step, obstruction["omega_radius"],
                        obstruction["omega_center"], p_center, p1,
                        eta_center, eta1, xi_center, xi1, omega_lower,
                    )
                else:
                    remainder = None
                    failure = metadata["failure"]
                if remainder is not None:
                    break
                rejected += 1
                step /= 2
                if step < minimum_step:
                    return {
                        "panel": panel,
                        "reached_r32": False,
                        "accepted_steps": accepted,
                        "rejected_trials": rejected,
                        "mobius_recentering_used": False,
                        "checkpoints": checkpoint_rows,
                        "terminal": {
                            "radius": str(r),
                            "failure": failure,
                            "attempted_step": str(step * 2),
                            "stage": "reciprocal_self_map",
                        },
                    }
            dp, de, dx = remainder
            dp += radius_from(reference[0], p1)
            de += radius_from(reference[1], eta1)
            dx += radius_from(reference[2], xi1)
            p_center, eta_center, xi_center = p1, eta1, xi1
            r += step
            accepted += 1
        checkpoint = snapshot(
            p_center, eta_center, xi_center, dp, de, dx
        )
        checkpoint_rows.append({"radius": int(target), **checkpoint})
        if not checkpoint["q_recovery_denominator_excludes_zero"]:
            # This is the only point at which a second Möbius chart would be
            # required. Stop fail-closed rather than silently changing charts.
            return {
                "panel": panel,
                "reached_r32": False,
                "accepted_steps": accepted,
                "rejected_trials": rejected,
                "mobius_recentering_used": False,
                "checkpoints": checkpoint_rows,
                "terminal": {
                    "radius": str(r),
                    "failure": "P_CHART_Q_RECOVERY_DENOMINATOR_CONTAINS_ZERO",
                    "stage": "checkpoint_chart_gate",
                },
            }
    return {
        "panel": panel,
        "reached_r32": True,
        "accepted_steps": accepted,
        "rejected_trials": rejected,
        "mobius_recentering_used": False,
        "checkpoints": checkpoint_rows,
        "terminal": None,
    }


def compute() -> dict:
    ctx.prec = 128
    return {
        "schema": "phase3-axial-qnm-horizon-reciprocal-checkpoint-run-v1",
        "panel_count": 16,
        "initial_radius": 4,
        "checkpoint_radii": [8, 16, 32],
        "rows": [continue_panel(panel) for panel in range(16)],
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
