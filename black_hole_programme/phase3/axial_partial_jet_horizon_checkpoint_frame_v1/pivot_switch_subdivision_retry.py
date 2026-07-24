#!/usr/bin/env python3
"""Supersede the panel-31 checkpoint and audit bounded retry strategies.

This append-only repair does not modify the earlier continuation artifact.
It replays the certified fixed-GL path, checks finiteness both before and
after projective normalization, serializes the true last valid checkpoint at
panel 30, and tests a fixed grid of Taylor orders and radial subdivisions.
"""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp
from flint import acb, ctx

from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt
from . import checkpoint_transport as transport
from . import pivot_switch as repair
from . import pivot_switch_continuation as continuation

HERE = Path(__file__).resolve().parent
RUN = HERE / "pivot-switch-subdivision-retry-run.json"

ORDERS = (16, 20, 24, 32, 40)
SUBDIVISIONS = (2, 4, 8, 16, 32, 64)
LAST_VALID_PANEL = 30
FAILED_PANEL = 31


def clone_line(line: transport.DualLine) -> transport.DualLine:
    return transport.DualLine(
        [acb(value) for value in line.tangent],
        [acb(value) for value in line.base],
        acb(line.amplitude),
        acb(line.amplitude_tangent),
        line.pivot,
    )


def line_finite(line: transport.DualLine) -> bool:
    return all(
        value.is_finite()
        for value in [
            *line.packed(),
            line.amplitude,
            line.amplitude_tangent,
        ]
    )


def accepts_projective_step(
    raw_state_finite: bool,
    pivot_gate_passed: bool,
    normalized_state_finite: bool,
) -> bool:
    """Correct acceptance predicate; the third conjunct kills the old mutant."""
    return raw_state_finite and pivot_gate_passed and normalized_state_finite


def replay_to_panel_30() -> tuple[
    transport.DualLine,
    object,
    sp.Matrix,
    object,
]:
    crosswalk = json.loads(transport.CROSSWALK.read_text())
    mixed = levelt.exact_data(crosswalk)
    mixed_tail = levelt.tail_majorant(mixed)
    symbolic_generator = transport.block_generator(
        mixed["base"], mixed["tangent"]
    )
    generator = transport.compile_matrix(symbolic_generator)
    line = transport.DualLine(
        tangent=transport.seed_vector(
            mixed["tangent_seed"], mixed_tail["tail_tangent"]
        ),
        base=transport.seed_vector(
            mixed["base_seed"], mixed_tail["tail_base"]
        ),
        amplitude=acb(1),
        amplitude_tangent=acb(0),
    )
    initial = line.normalize((2, 3))
    if not initial["passed"]:
        raise RuntimeError("mixed seed pivot drift")
    rho = transport.RHO0
    step = transport.RHO0 / transport.PANELS
    cumulative_chart = sp.eye(4)

    for panel in range(repair.SWITCH_AFTER_PANEL):
        next_state, meta = transport.taylor_step(
            generator, line.packed(), rho, step
        )
        if next_state is None:
            raise RuntimeError(f"source replay Taylor drift at panel {panel}: {meta}")
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        pivot = line.normalize((2, 3))
        if not pivot["passed"]:
            raise RuntimeError(f"source replay pivot drift at panel {panel}")
        rho += step

    # Certified fixed e2-e3 transition at panel 26.
    next_state, meta = transport.taylor_step(
        generator, line.packed(), rho, step
    )
    if next_state is None:
        raise RuntimeError(f"switch transition drift: {meta}")
    line = transport.DualLine.unpacked(
        next_state, line.amplitude, line.amplitude_tangent
    )
    increment = continuation.ATLAS["e2-e3"]
    line = continuation.transformed_line(line, increment)
    cumulative_chart = increment * cumulative_chart
    dual = sp.diag(increment, increment)
    symbolic_generator = sp.simplify(
        dual * symbolic_generator * dual.inv()
    )
    generator = transport.compile_matrix(symbolic_generator)
    pivot = repair.exact_dual_normalize(line, (2,))
    if not pivot["passed"] or not line_finite(line):
        raise RuntimeError("certified switch checkpoint drift")
    rho += step

    for panel in range(repair.POST_SWITCH_PANEL, LAST_VALID_PANEL + 1):
        next_state, meta = transport.taylor_step(
            generator, line.packed(), rho, step
        )
        if next_state is None or not all(value.is_finite() for value in next_state):
            raise RuntimeError(f"pre-checkpoint Taylor drift at panel {panel}")
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        if line.base[2].abs_lower() <= 0:
            raise RuntimeError(f"e2 chart drift at panel {panel}")
        pivot = repair.exact_dual_normalize(line, (2,))
        if not pivot["passed"] or not line_finite(line):
            raise RuntimeError(f"post-normalization drift at panel {panel}")
        rho += step
    return line, rho, cumulative_chart, symbolic_generator


def failed_panel_audit(
    checkpoint: transport.DualLine,
    rho,
    generator,
) -> dict:
    step = transport.RHO0 / transport.PANELS
    next_state, meta = transport.taylor_step(
        generator, checkpoint.packed(), rho, step
    )
    if next_state is None:
        raise RuntimeError("panel-31 mutation audit changed to Taylor refusal")
    raw_finite = all(value.is_finite() for value in next_state)
    line = transport.DualLine.unpacked(
        next_state, checkpoint.amplitude, checkpoint.amplitude_tangent
    )
    lower = line.base[2].abs_lower()
    pivot = repair.exact_dual_normalize(line, (2,))
    normalized_finite = line_finite(line)
    if not raw_finite or lower <= 0 or not pivot["passed"] or normalized_finite:
        raise RuntimeError("panel-31 post-normalization mutation witness drift")
    return {
        "panel": FAILED_PANEL,
        "rho_start": str(rho),
        "rho_endpoint": str(rho + step),
        "step_gate": meta,
        "raw_taylor_state_finite": raw_finite,
        "e2_modulus_lower_before_normalization": str(lower),
        "pivot_gate_passed": pivot["passed"],
        "normalized_state_finite": normalized_finite,
        "old_check_order_would_accept": raw_finite and pivot["passed"],
        "corrected_check_accepts": accepts_projective_step(
            raw_finite, pivot["passed"], normalized_finite
        ),
        "corrected_gate": "NONFINITE_PROJECTIVE_NORMALIZATION",
    }


def retry_one_panel(
    checkpoint: transport.DualLine,
    rho,
    generator,
    order: int,
    subdivisions: int,
) -> dict:
    original_order = transport.ORDER
    transport.ORDER = order
    try:
        line = clone_line(checkpoint)
        full_step = transport.RHO0 / transport.PANELS
        step = full_step / subdivisions
        current = rho
        completed = 0
        terminal = None
        for substep in range(subdivisions):
            next_state, meta = transport.taylor_step(
                generator, line.packed(), current, step
            )
            if next_state is None:
                terminal = {
                    "gate": "TAYLOR_REFUSAL",
                    "substep": substep,
                    "detail": meta,
                }
                break
            if not all(value.is_finite() for value in next_state):
                terminal = {
                    "gate": "NONFINITE_TAYLOR_ENCLOSURE",
                    "substep": substep,
                    "detail": meta,
                }
                break
            line = transport.DualLine.unpacked(
                next_state, line.amplitude, line.amplitude_tangent
            )
            lower = line.base[2].abs_lower()
            if not lower.is_finite() or lower <= 0:
                terminal = {
                    "gate": "E2_PIVOT_CONTAINS_ZERO",
                    "substep": substep,
                    "e2_modulus_lower": str(lower),
                }
                break
            pivot = repair.exact_dual_normalize(line, (2,))
            if not pivot["passed"]:
                terminal = {
                    "gate": "E2_PIVOT_REFUSAL",
                    "substep": substep,
                    "detail": pivot,
                }
                break
            if not line_finite(line):
                terminal = {
                    "gate": "NONFINITE_PROJECTIVE_NORMALIZATION",
                    "substep": substep,
                    "e2_modulus_lower": str(lower),
                    "detail": pivot,
                }
                break
            current += step
            completed += 1
        return {
            "order": order,
            "subdivisions": subdivisions,
            "completed_substeps": completed,
            "rho_reached": str(current),
            "completed_full_panel": terminal is None and completed == subdivisions,
            "terminal": terminal,
        }
    finally:
        transport.ORDER = original_order


def compute() -> dict:
    ctx.prec = 256
    checkpoint, rho, cumulative_chart, symbolic_generator = replay_to_panel_30()
    generator = transport.compile_matrix(symbolic_generator)
    correction = failed_panel_audit(
        clone_line(checkpoint), rho, generator
    )
    attempts = [
        retry_one_panel(
            checkpoint,
            rho,
            generator,
            order,
            subdivisions,
        )
        for order in ORDERS
        for subdivisions in SUBDIVISIONS
    ]
    successful = [row for row in attempts if row["completed_full_panel"]]
    if successful:
        raise RuntimeError("bounded retry unexpectedly succeeded; extend producer")
    return {
        "schema": "phase3-axial-horizon-pivot-switch-subdivision-retry-run-v1",
        "frequency": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
        "precision_bits": ctx.prec,
        "supersedes": {
            "result_id": (
                "PURE_WEYL_PHASE3_AXIAL_HORIZON_MIXED_PIVOT_SWITCH_CONTINUATION"
            ),
            "reason": (
                "the earlier rail checked finiteness before projective "
                "normalization but not after it"
            ),
        },
        "corrected_last_valid_checkpoint": {
            "panel": LAST_VALID_PANEL,
            **continuation.checkpoint_payload(
                checkpoint, rho, cumulative_chart
            ),
        },
        "panel_31_mutation_witness": correction,
        "retry_grid": {
            "orders": list(ORDERS),
            "subdivisions": list(SUBDIVISIONS),
            "chart": "e2 only",
            "attempts": attempts,
            "successful_attempts": successful,
        },
        "target": {
            "next_base_panel_endpoint": str(
                rho + transport.RHO0 / transport.PANELS
            ),
            "next_dyadic_shell": str(2 * transport.RHO0),
            "reached": False,
        },
        "claim_flags": {
            "prior_panel_31_checkpoint_demoted": True,
            "panel_30_checkpoint_certified": True,
            "post_normalization_finiteness_gate_added": True,
            "bounded_retry_grid_exhausted": True,
            "next_base_panel_completed": False,
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
