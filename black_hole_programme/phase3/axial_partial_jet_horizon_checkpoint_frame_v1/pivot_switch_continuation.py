#!/usr/bin/env python3
"""Continue the certified mixed-line chart repair to a dyadic checkpoint."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from flint import acb, ctx

from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt
from . import checkpoint_transport as transport
from . import pivot_switch as repair

HERE = Path(__file__).resolve().parent
RUN = HERE / "pivot-switch-continuation-run.json"

TARGET_RHO = 2 * transport.RHO0
ATLAS = {
    "e2": sp.eye(4),
    "e3": sp.Matrix(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
    ),
    "e2-e3": sp.Matrix(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -1], [0, 0, 0, 1]]
    ),
    "e2+e3": sp.Matrix(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
    ),
}


def row_value(name: str, line: transport.DualLine) -> acb:
    matrix = ATLAS[name]
    return sum(
        (
            transport.cf(matrix[2, column]) * line.base[column]
            for column in range(4)
        ),
        acb(0),
    )


def transformed_line(
    line: transport.DualLine, matrix: sp.Matrix
) -> transport.DualLine:
    dual = sp.diag(matrix, matrix)
    packed = repair.apply_matrix(dual, line.packed())
    return transport.DualLine.unpacked(
        packed, acb(line.amplitude), acb(line.amplitude_tangent)
    )


def choose_chart(line: transport.DualLine) -> tuple[str | None, dict[str, str]]:
    if not all(value.is_finite() for value in line.packed()):
        return None, {"nonfinite_state": "true"}
    lowers = {name: row_value(name, line).abs_lower() for name in ATLAS}
    best = max(lowers, key=lowers.get)
    serialized = {name: str(value) for name, value in lowers.items()}
    if lowers[best] <= 0:
        return None, serialized
    return best, serialized


def checkpoint_payload(
    line: transport.DualLine,
    rho: Fraction,
    cumulative_chart: sp.Matrix,
) -> dict:
    return {
        "rho": str(rho),
        "r": str(rho + 2),
        "cumulative_chart": [
            [str(cumulative_chart[i, j]) for j in range(4)] for i in range(4)
        ],
        "line": repair.line_payload(line),
    }


def compute() -> dict:
    ctx.prec = 192
    crosswalk = json.loads(transport.CROSSWALK.read_text())
    mixed = levelt.exact_data(crosswalk)
    mixed_tail = levelt.tail_majorant(mixed)
    original_symbolic = transport.block_generator(
        mixed["base"], mixed["tangent"]
    )
    symbolic_generator = original_symbolic
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
    switches = []
    panels = []
    terminal = None

    # Replay the source rail through panel 25 without changing its arithmetic.
    for panel in range(repair.SWITCH_AFTER_PANEL):
        next_state, meta = transport.taylor_step(generator, line.packed(), rho, step)
        if next_state is None:
            raise RuntimeError(f"source replay Taylor drift at panel {panel}")
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        pivot = line.normalize((2, 3))
        if not pivot["passed"]:
            raise RuntimeError(f"source replay pivot drift at panel {panel}")
        rho += step

    # Panel 26: reproduce the certified fixed e2-e3 transition exactly.
    panel = repair.SWITCH_AFTER_PANEL
    next_state, meta = transport.taylor_step(generator, line.packed(), rho, step)
    if next_state is None:
        raise RuntimeError("certified switch transition Taylor drift")
    line = transport.DualLine.unpacked(
        next_state, line.amplitude, line.amplitude_tangent
    )
    selected, lowers = choose_chart(line)
    if selected != "e2-e3":
        raise RuntimeError(f"certified fixed-atlas selection drift: {selected}")
    increment = ATLAS[selected]
    line = transformed_line(line, increment)
    cumulative_chart = increment * cumulative_chart
    dual = sp.diag(increment, increment)
    symbolic_generator = sp.simplify(
        dual * symbolic_generator * dual.inv()
    )
    generator = transport.compile_matrix(symbolic_generator)
    pivot = repair.exact_dual_normalize(line, (2,))
    if not pivot["passed"]:
        raise RuntimeError("certified switch normalization drift")
    rho += step
    switches.append(
        {
            "panel": panel,
            "rho": str(rho),
            "selected": selected,
            "atlas_modulus_lowers": lowers,
            "incremental_chart": [
                [str(increment[i, j]) for j in range(4)] for i in range(4)
            ],
            "cumulative_chart": [
                [str(cumulative_chart[i, j]) for j in range(4)]
                for i in range(4)
            ],
            "pivot": pivot,
        }
    )
    panels.append({"panel": panel, "rho": str(rho), "step": meta, "pivot": pivot})
    last_valid_checkpoint = checkpoint_payload(line, rho, cumulative_chart)

    # Continue with a pre-emptive fixed-atlas choice after every panel.
    for panel in range(repair.POST_SWITCH_PANEL, transport.PANELS):
        next_state, meta = transport.taylor_step(generator, line.packed(), rho, step)
        if next_state is None:
            terminal = {
                "gate": "TAYLOR_REFUSAL",
                "panel": panel,
                "rho": str(rho),
                "detail": meta,
            }
            break
        if not all(value.is_finite() for value in next_state):
            terminal = {
                "gate": "NONFINITE_TAYLOR_ENCLOSURE",
                "panel": panel,
                "rho": str(rho),
                "attempted_endpoint_rho": str(rho + step),
                "detail": meta,
            }
            break
        line = transport.DualLine.unpacked(
            next_state, line.amplitude, line.amplitude_tangent
        )
        selected, lowers = choose_chart(line)
        if selected is None:
            terminal = {
                "gate": "FIXED_ATLAS_CONTAINS_ZERO",
                "panel": panel,
                "rho": str(rho + step),
                "atlas_modulus_lowers": lowers,
            }
            break
        increment = ATLAS[selected]
        if selected != "e2":
            line = transformed_line(line, increment)
            cumulative_chart = increment * cumulative_chart
            dual = sp.diag(increment, increment)
            symbolic_generator = sp.simplify(
                dual * symbolic_generator * dual.inv()
            )
            generator = transport.compile_matrix(symbolic_generator)
        pivot = repair.exact_dual_normalize(line, (2,))
        if not pivot["passed"]:
            terminal = {
                "gate": "SELECTED_PIVOT_REFUSAL",
                "panel": panel,
                "rho": str(rho + step),
                "selected": selected,
                "atlas_modulus_lowers": lowers,
                "detail": pivot,
            }
            break
        rho += step
        if selected != "e2":
            switches.append(
                {
                    "panel": panel,
                    "rho": str(rho),
                    "selected": selected,
                    "atlas_modulus_lowers": lowers,
                    "incremental_chart": [
                        [str(increment[i, j]) for j in range(4)]
                        for i in range(4)
                    ],
                    "cumulative_chart": [
                        [str(cumulative_chart[i, j]) for j in range(4)]
                        for i in range(4)
                    ],
                    "pivot": pivot,
                }
            )
        panels.append(
            {
                "panel": panel,
                "rho": str(rho),
                "step": meta,
                "selected": selected,
                "atlas_modulus_lowers": lowers,
                "pivot": pivot,
            }
        )
        last_valid_checkpoint = checkpoint_payload(
            line, rho, cumulative_chart
        )

    reached = terminal is None and rho == TARGET_RHO
    if terminal is None and not reached:
        raise RuntimeError(f"continuation ended at unexpected rho {rho}")
    return {
        "schema": "phase3-axial-partial-jet-horizon-pivot-switch-continuation-run-v1",
        "frequency": f"{transport.OMEGA.numerator}/{transport.OMEGA.denominator}",
        "precision_bits": ctx.prec,
        "source_checkpoint": "pivot-switch-run.json",
        "scope": {
            "rho_start": str(transport.RHO0),
            "rho_target": str(TARGET_RHO),
            "panels": transport.PANELS,
            "step": str(step),
            "fixed_atlas": list(ATLAS),
        },
        "source_replayed_panels": repair.SWITCH_AFTER_PANEL,
        "accepted_panels_total": repair.SWITCH_AFTER_PANEL + len(panels),
        "accepted_panels_from_switch_transition": len(panels),
        "switch_count": len(switches),
        "switches": switches,
        "terminal": terminal,
        "reached_next_dyadic_shell": reached,
        "last_valid_checkpoint": last_valid_checkpoint,
        "checkpoint": (
            checkpoint_payload(line, rho, cumulative_chart) if reached else None
        ),
        "panel_ledger": panels,
        "claim_flags": {
            "common_dual_correlation_preserved_at_every_switch": True,
            "every_switch_serialized": True,
            "next_dyadic_shell_reached": reached,
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
