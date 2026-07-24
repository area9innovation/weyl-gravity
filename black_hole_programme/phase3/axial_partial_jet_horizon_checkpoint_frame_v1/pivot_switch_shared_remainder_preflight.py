#!/usr/bin/env python3
"""One-step shared-reciprocal projective repair after corrected panel 30.

The eager formula forms the rectangular product ``s*s`` and loses the fact
that both factors are the same nonzero pivot.  Its enclosure contains zero,
so division returns NaN.  This preflight computes the reciprocal once and
reuses the same enclosure:

    b_i^new = b_i * inv_s
    t_i^new = (t_i - b_i^new * t_s) * inv_s.

The pivot coordinate and its tangent are then set by their exact identities
1 and 0.  This is algebraically the same dual projective quotient, but it
retains the shared denominator node instead of independently wrapping s^2.
"""
from __future__ import annotations

import json
from pathlib import Path

from flint import acb, ctx

from . import checkpoint_transport as transport
from . import pivot_switch as repair
from . import pivot_switch_continuation as continuation
from . import pivot_switch_subdivision_retry as retry

HERE = Path(__file__).resolve().parent
RUN = HERE / "pivot-switch-shared-remainder-preflight-run.json"
SOURCE_PANEL = 30
TARGET_PANEL = 31


def shared_reciprocal_normalize(
    line: transport.DualLine, pivot: int
) -> dict:
    scalar = line.base[pivot]
    tangent_scalar = line.tangent[pivot]
    lower = scalar.abs_lower()
    if not scalar.is_finite() or not lower.is_finite() or lower <= 0:
        return {
            "passed": False,
            "gate": "PIVOT_CONTAINS_ZERO_OR_NONFINITE",
            "pivot": pivot,
        }
    reciprocal = 1 / scalar
    if not reciprocal.is_finite():
        return {
            "passed": False,
            "gate": "NONFINITE_SHARED_RECIPROCAL",
            "pivot": pivot,
        }
    old_base = line.base
    old_tangent = line.tangent
    new_base = []
    new_tangent = []
    for index in range(len(old_base)):
        if index == pivot:
            new_base.append(acb(1))
            new_tangent.append(acb(0))
            continue
        base_value = old_base[index] * reciprocal
        tangent_value = (
            old_tangent[index] - base_value * tangent_scalar
        ) * reciprocal
        new_base.append(base_value)
        new_tangent.append(tangent_value)
    amplitude = line.amplitude * scalar
    amplitude_tangent = (
        line.amplitude_tangent * scalar
        + line.amplitude * tangent_scalar
    )
    if not all(
        value.is_finite()
        for value in [
            *new_base,
            *new_tangent,
            amplitude,
            amplitude_tangent,
        ]
    ):
        return {
            "passed": False,
            "gate": "NONFINITE_POST_SHARED_NORMALIZATION",
            "pivot": pivot,
            "pivot_modulus_lower": str(lower),
            "reciprocal": str(reciprocal),
        }
    line.base = new_base
    line.tangent = new_tangent
    line.amplitude = amplitude
    line.amplitude_tangent = amplitude_tangent
    line.pivot = pivot
    return {
        "passed": True,
        "gate": None,
        "pivot": pivot,
        "pivot_modulus_lower": str(lower),
        "shared_reciprocal": str(reciprocal),
        "exact_base_pivot": "1",
        "exact_tangent_pivot": "0",
        "evaluation_order": (
            "inv_s=1/s; base_i*=inv_s; "
            "tangent_i=(tangent_i-base_i_normalized*tangent_s)*inv_s"
        ),
    }


def eager_squared_denominator_mutant(
    line: transport.DualLine, pivot: int
) -> dict:
    """The old eager operation, retained only as a killed mutation witness."""
    scalar = line.base[pivot]
    tangent_scalar = line.tangent[pivot]
    denominator = scalar * scalar
    tangent = [
        (
            line.tangent[index] * scalar
            - line.base[index] * tangent_scalar
        )
        / denominator
        for index in range(len(line.base))
    ]
    return {
        "denominator": str(denominator),
        "denominator_contains_zero": denominator.abs_lower() <= 0,
        "normalized_tangent_finite": all(value.is_finite() for value in tangent),
        "mutant_accepts": all(value.is_finite() for value in tangent),
    }


def compute() -> dict:
    ctx.prec = 256
    checkpoint, rho, cumulative_chart, symbolic_generator = (
        retry.replay_to_panel_30()
    )
    if not retry.line_finite(checkpoint):
        raise RuntimeError("corrected panel-30 checkpoint drift")
    generator = transport.compile_matrix(symbolic_generator)
    step = transport.RHO0 / transport.PANELS
    next_state, step_meta = transport.taylor_step(
        generator, checkpoint.packed(), rho, step
    )
    if next_state is None or not all(value.is_finite() for value in next_state):
        raise RuntimeError("panel-31 raw Taylor state drift")
    raw_line = transport.DualLine.unpacked(
        next_state, checkpoint.amplitude, checkpoint.amplitude_tangent
    )
    if raw_line.base[2].abs_lower() <= 0:
        raise RuntimeError("panel-31 e2 pivot drift")

    mutant = eager_squared_denominator_mutant(
        retry.clone_line(raw_line), 2
    )
    if mutant["mutant_accepts"] or not mutant["denominator_contains_zero"]:
        raise RuntimeError("eager squared-denominator mutation witness drift")

    repaired_line = retry.clone_line(raw_line)
    normalization = shared_reciprocal_normalize(repaired_line, 2)
    if not normalization["passed"] or not retry.line_finite(repaired_line):
        raise RuntimeError(f"shared reciprocal repair failed: {normalization}")
    rho += step
    return {
        "schema": (
            "phase3-axial-horizon-pivot-switch-shared-remainder-preflight-run-v1"
        ),
        "frequency": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
        "precision_bits": ctx.prec,
        "source": {
            "result_id": (
                "PURE_WEYL_PHASE3_AXIAL_HORIZON_PIVOT_SWITCH_SUBDIVISION_RETRY"
            ),
            "last_valid_panel": SOURCE_PANEL,
            "rho": str(rho - step),
        },
        "target": {
            "panel": TARGET_PANEL,
            "rho": str(rho),
            "r": str(rho + 2),
            "step": str(step),
        },
        "raw_step": {
            "gate": step_meta,
            "state_finite": True,
            "e2_modulus_lower": str(raw_line.base[2].abs_lower()),
        },
        "representation": {
            "kind": "shared-reciprocal dual projective chart",
            "chart": "e2",
            "normalization": normalization,
            "eager_squared_denominator_mutant": mutant,
            "post_normalization_finite": True,
        },
        "checkpoint": continuation.checkpoint_payload(
            repaired_line, rho, cumulative_chart
        ),
        "claim_flags": {
            "corrected_panel_30_source_used": True,
            "one_next_radial_step_certified": True,
            "shared_remainder_normalization_certified": True,
            "post_normalization_finite": True,
            "eager_squared_denominator_mutant_killed": True,
            "next_dyadic_shell_reached": False,
            "r4_reached": False,
            "H4_certified": False,
            "T_plus_certified": False,
        },
    }


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
