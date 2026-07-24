#!/usr/bin/env python3
"""Certified fixed-GL repair of the first mixed horizon pivot obstruction.

The original checkpoint rail divided a ball by itself when it normalized a
projective pivot.  Ball arithmetic then forgot the exact identities

    s / s = 1,       (t s - s t) / s^2 = 0,

and the artificial width eventually made every coordinate ball contain zero.
This focused rail replays the mixed line to the last successful transition,
selects the fixed row e_2-e_3, conjugates the full dual generator by the same
GL(4) matrix, and enforces those two exact projective identities.  It then
certifies one panel beyond the former obstruction and emits a resumable
checkpoint in the switched chart.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import acb, ctx

from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt
from . import checkpoint_transport as transport

HERE = Path(__file__).resolve().parent
RUN = HERE / "pivot-switch-run.json"

SWITCH_AFTER_PANEL = 26
POST_SWITCH_PANEL = 27


def clone(values: list[acb]) -> list[acb]:
    return [acb(value) for value in values]


def apply_matrix(matrix: sp.Matrix, vector: list[acb]) -> list[acb]:
    return [
        sum(
            (
                transport.cf(matrix[row, column]) * vector[column]
                for column in range(matrix.cols)
            ),
            acb(0),
        )
        for row in range(matrix.rows)
    ]


def exact_dual_normalize(
    line: transport.DualLine, allowed: tuple[int, ...]
) -> dict:
    """Normalize by one dual scalar while retaining its exact self-correlation."""
    result = line.normalize(allowed)
    if not result["passed"]:
        return result
    pivot = result["pivot"]
    line.base[pivot] = acb(1)
    line.tangent[pivot] = acb(0)
    result["exact_base_pivot"] = "1"
    result["exact_tangent_pivot"] = "0"
    result["correlation_identity"] = (
        "base_pivot=s/s=1; tangent_pivot=(t*s-s*t)/s^2=0"
    )
    return result


def line_payload(line: transport.DualLine) -> dict:
    return {
        "pivot": line.pivot,
        "tangent": transport.serialize_vector(line.tangent),
        "base": transport.serialize_vector(line.base),
        "amplitude": transport.serialize_vector([line.amplitude])[0],
        "amplitude_tangent": transport.serialize_vector(
            [line.amplitude_tangent]
        )[0],
    }


def compute() -> dict:
    ctx.prec = 192
    crosswalk = json.loads(transport.CROSSWALK.read_text())
    mixed = levelt.exact_data(crosswalk)
    mixed_tail = levelt.tail_majorant(mixed)
    original_symbolic = transport.block_generator(
        mixed["base"], mixed["tangent"]
    )
    original_generator = transport.compile_matrix(original_symbolic)

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
    step = rho / transport.PANELS
    last_raw = None
    for panel in range(SWITCH_AFTER_PANEL + 1):
        next_state, meta = transport.taylor_step(
            original_generator, line.packed(), rho, step
        )
        if next_state is None:
            raise RuntimeError(f"pre-switch transport failed at panel {panel}: {meta}")
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        if panel == SWITCH_AFTER_PANEL:
            last_raw = transport.DualLine(
                clone(line.tangent),
                clone(line.base),
                acb(line.amplitude),
                acb(line.amplitude_tangent),
            )
            break
        pivot = line.normalize((2, 3))
        if not pivot["passed"]:
            raise RuntimeError(f"pre-switch pivot drift at panel {panel}: {pivot}")
        rho += step
    if last_raw is None:
        raise RuntimeError("missing last raw transition")

    # Reproduce the former failure on the next panel.
    old_line = transport.DualLine(
        clone(last_raw.tangent),
        clone(last_raw.base),
        acb(last_raw.amplitude),
        acb(last_raw.amplitude_tangent),
    )
    old_last_pivot = old_line.normalize((2, 3))
    if not old_last_pivot["passed"]:
        raise RuntimeError("former last accepted pivot drift")
    old_next, old_step_meta = transport.taylor_step(
        original_generator, old_line.packed(), rho, step
    )
    if old_next is None:
        raise RuntimeError("former obstruction changed to a Taylor refusal")
    old_line = transport.DualLine.unpacked(
        old_next, old_line.amplitude, old_line.amplitude_tangent
    )
    old_failure = old_line.normalize((2, 3))
    if old_failure["passed"] or old_failure.get("gate") != "PIVOT_CONTAINS_ZERO":
        raise RuntimeError("former mixed pivot obstruction was not reproduced")

    # Fixed GL(4,Q) chart.  The selected projective coordinate is e_2-e_3.
    chart = sp.eye(4)
    chart[2, :] = sp.Matrix([[0, 0, 1, -1]])
    chart[3, :] = sp.Matrix([[0, 0, 0, 1]])
    if chart.det() != 1:
        raise RuntimeError("fixed chart determinant drift")
    dual_chart = sp.diag(chart, chart)
    switched_symbolic = sp.simplify(
        dual_chart * original_symbolic * dual_chart.inv()
    )
    switched_generator = transport.compile_matrix(switched_symbolic)

    atlas_rows = {
        "e2": (0, 0, 1, 0),
        "e3": (0, 0, 0, 1),
        "e2-e3": (0, 0, 1, -1),
        "e2+e3": (0, 0, 1, 1),
    }
    atlas_values = {
        name: sum(
            (
                transport.cf(sp.Integer(coefficient)) * last_raw.base[index]
                for index, coefficient in enumerate(row)
            ),
            acb(0),
        )
        for name, row in atlas_rows.items()
    }
    atlas_lowers = {
        name: value.abs_lower() for name, value in atlas_values.items()
    }
    if max(atlas_lowers, key=atlas_lowers.get) != "e2-e3":
        raise RuntimeError("adaptive fixed-atlas selection drift")
    switched_packed = apply_matrix(dual_chart, last_raw.packed())
    switched_line = transport.DualLine.unpacked(
        switched_packed,
        acb(last_raw.amplitude),
        acb(last_raw.amplitude_tangent),
    )
    selected_lower = switched_line.base[2].abs_lower()
    alternate_lower = switched_line.base[3].abs_lower()
    if selected_lower <= 0:
        raise RuntimeError("selected fixed GL row does not exclude zero")
    switched_pivot = exact_dual_normalize(switched_line, (2, 3))
    if not switched_pivot["passed"] or switched_pivot["pivot"] != 2:
        raise RuntimeError("fixed GL chart did not select row e2-e3")
    rho += step

    post_state, post_step_meta = transport.taylor_step(
        switched_generator, switched_line.packed(), rho, step
    )
    if post_state is None:
        raise RuntimeError(f"post-switch panel refused: {post_step_meta}")
    switched_line = transport.DualLine.unpacked(
        post_state,
        switched_line.amplitude,
        switched_line.amplitude_tangent,
    )
    post_pivot = exact_dual_normalize(switched_line, (2, 3))
    if not post_pivot["passed"]:
        raise RuntimeError(f"post-switch pivot refused: {post_pivot}")
    rho += step

    return {
        "schema": "phase3-axial-partial-jet-horizon-pivot-switch-run-v1",
        "frequency": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
        "precision_bits": ctx.prec,
        "former_obstruction": {
            "rho": str(rho - step),
            "panel": POST_SWITCH_PANEL,
            "reproduced": True,
            "last_accepted_pivot": old_last_pivot,
            "next_step": old_step_meta,
            "failure": old_failure,
        },
        "switch": {
            "after_panel": SWITCH_AFTER_PANEL,
            "rho_before_switch": str(rho - step),
            "matrix": [[str(chart[i, j]) for j in range(4)] for i in range(4)],
            "determinant": str(chart.det()),
            "dual_action": "diag(M,M) on (tangent,base)",
            "generator_action": "diag(M,M)*G*diag(M,M)^(-1)",
            "selected_row": "e2-e3",
            "selection_rule": (
                "maximal modulus lower bound over fixed atlas "
                "[e2,e3,e2-e3,e2+e3]"
            ),
            "atlas_modulus_lowers": {
                name: str(value) for name, value in atlas_lowers.items()
            },
            "selected_modulus_lower": str(selected_lower),
            "alternate_modulus_lower": str(alternate_lower),
            "pivot": switched_pivot,
        },
        "post_switch_checkpoint": {
            "rho": str(rho),
            "r": str(rho + 2),
            "accepted_post_switch_panels": 1,
            "step": str(step),
            "step_gate": post_step_meta,
            "pivot": post_pivot,
            "chart": "fixed GL row e2-e3",
            "resume_payload": line_payload(switched_line),
        },
        "claim_flags": {
            "former_pivot_obstruction_reproduced": True,
            "fixed_gl_chart_certified": True,
            "common_dual_correlation_preserved": True,
            "one_post_switch_panel_certified": True,
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
