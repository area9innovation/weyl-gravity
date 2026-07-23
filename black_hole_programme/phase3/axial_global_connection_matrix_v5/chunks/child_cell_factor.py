"""Typed local-reset factors on the final 16-cell frequency partition."""
from __future__ import annotations

import hashlib
import json
import math
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_codegen import FrameTaylor
from ..affine_rail import (
    GENERATOR,
    OMEGA_CENTER,
    build_microfactor_render_context,
    render_microfactor_adapter,
)
from .emit_microfactor import DEFAULT_INPUTS, parse_trace
from .split_microfactor import WIDTH_LIMIT
from .verify_handoff import (
    HandoffError,
    _file_sha256,
    _require,
    _verify_affine_hull,
    canonical_sha256,
)
from .verify_microfactor import BLOCK_ORDER


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SCHEMA = "phase3-axial-child-cell-local-reset-factor-v1"
FREQUENCY_CHILDREN = 16
TAIL_START_PARENT = 191
TAIL_END_PARENT = 224
PREFIX_BOUNDARY_FRAME_INDEX = 8 * TAIL_START_PARENT
CARRIER_INDICES = (0, 1, 2, 3, 6, 7, 8, 9)
KERNEL_INDICES = (4, 5, 10, 11)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def frequency_cell(child: int) -> tuple[Fraction, Fraction]:
    if not 0 <= child < FREQUENCY_CHILDREN:
        raise ValueError("frequency child out of range")
    return (
        Fraction(1, 2) + Fraction(child, 4096),
        Fraction(1, 2) + Fraction(child + 1, 4096),
    )


def cell_payload(child: int) -> dict[str, Any]:
    lo, hi = frequency_cell(child)
    return {
        "parameter": "Momega",
        "generator": GENERATOR,
        "lower": rational_text(lo),
        "upper": rational_text(hi),
        "center": rational_text((lo + hi) / 2),
        "radius": rational_text((hi - lo) / 2),
        "parent_lower": "1/2",
        "parent_upper": "129/256",
        "parent_child_index": child,
        "parent_child_count": FREQUENCY_CHILDREN,
    }


def _matrix_text(matrix: tuple[tuple[Fraction, ...], ...]) -> list[list[str]]:
    return [[rational_text(value) for value in row] for row in matrix]


def prefix_boundary_crosswalk(
    child: int, prefix_context: dict | None = None
) -> dict[str, Any]:
    """Restrict the inherited prefix frame to one final frequency child.

    The moving-frame prefix ends at ``t=191/8``.  Its terminal frame maps
    contiguous carrier/kernel moving coordinates back to the standard
    realified six-state chart.  This is a coordinate crosswalk, not a
    physical restart.
    """
    prefix_context = prefix_context or build_microfactor_render_context()
    frame = prefix_context["frames"][PREFIX_BOUNDARY_FRAME_INDEX]
    lo, hi = frequency_cell(child)
    center, radius = (lo + hi) / 2, (hi - lo) / 2
    delta = center - OMEGA_CENTER
    raw_center = tuple(
        tuple(value + delta * derivative
              for value, derivative in zip(row, drow))
        for row, drow in zip(frame.center, frame.derivative)
    )
    raw_linear = tuple(
        tuple(radius * derivative for derivative in row)
        for row in frame.derivative
    )
    zero = Fraction(0)

    def to_standard_block(raw: tuple[tuple[Fraction, ...], ...]):
        rows = []
        for state_row in range(12):
            if state_row in CARRIER_INDICES:
                rows.append(
                    tuple(raw[state_row][col] for col in CARRIER_INDICES)
                    + tuple(zero for _ in KERNEL_INDICES)
                )
            else:
                rows.append(
                    tuple(raw[state_row][col] for col in CARRIER_INDICES)
                    + tuple(raw[state_row][col] for col in KERNEL_INDICES)
                )
        return tuple(rows)

    payload = {
        "schema": "phase3-axial-prefix-boundary-crosswalk-v1",
        "radial_boundary": "191/8",
        "parameter_cell": cell_payload(child),
        "generator": GENERATOR,
        "input_chart": "global-moving-block-lower-12",
        "output_chart": "standard-realified-six-state-12",
        "center": _matrix_text(to_standard_block(raw_center)),
        "linear": _matrix_text(to_standard_block(raw_linear)),
        "remainder": "exact-zero-coordinate-choice",
        "physical_restart": False,
        "construction": (
            "restrict the one global prefix frame Taylor model to the exact "
            "frequency child, assemble carrier/kernel block-lower order, "
            "then restore standard state-row order"
        ),
        "global_frame_table_sha256": prefix_context["frame_table_sha256"],
        "global_boundary_frame_sha256": prefix_context["frame_sha256"][
            PREFIX_BOUNDARY_FRAME_INDEX
        ],
    }
    payload["crosswalk_sha256"] = canonical_sha256(payload)
    return payload


def identity_frames() -> tuple[FrameTaylor, ...]:
    zero, one = Fraction(0), Fraction(1)
    center = tuple(
        tuple(one if row == col else zero for col in range(12))
        for row in range(12)
    )
    derivative = tuple(tuple(zero for _ in range(12)) for _ in range(12))
    return tuple(FrameTaylor(center, derivative) for _ in range(9))


def radial_geometry(parent: int, leaf: int) -> tuple[int, int, int]:
    if not TAIL_START_PARENT <= parent < TAIL_END_PARENT:
        raise ValueError("tail parent out of range")
    if leaf not in (0, 1):
        raise ValueError("tail leaf must be 0 or 1")
    # Two half-parent leaves.  Each leaf contains eight refined panels of
    # width 1/128, so it spans four base 1/64 panels.
    return 16 * parent + 8 * leaf, 8, 128


def trace_id(child: int, parent: int, leaf: int) -> int:
    frequency_cell(child)
    radial_geometry(parent, leaf)
    return 300_000 + 1000 * child + 10 * parent + leaf


def render_factor(
    child: int,
    parent: int,
    leaf: int,
    *,
    context: dict | None = None,
) -> tuple[str, dict, dict]:
    context = context or build_microfactor_render_context(frequency_cell(child))
    start, count, denominator = radial_geometry(parent, leaf)
    text, metadata = render_microfactor_adapter(
        parent,
        context=context,
        panel_start=start,
        panel_count=count,
        panel_denominator=denominator,
        trace_id=trace_id(child, parent, leaf),
        local_frames=identity_frames(),
        base_frame_table_sha256=context["frame_table_sha256"],
    )
    return text, metadata, context


def build_factor(
    child: int,
    parent: int,
    leaf: int,
    trace: str,
    root: Path,
    *,
    runner: Path,
    context: dict,
    prefix_context: dict,
) -> dict:
    source, metadata, _ = render_factor(
        child, parent, leaf, context=context
    )
    if not runner.is_file() or runner.read_text() != source:
        raise HandoffError("child-cell runner differs from deterministic source")
    tid = trace_id(child, parent, leaf)
    matrix, rank, widths = parse_trace(trace, tid)
    if any(
        not math.isfinite(float(value)) or float(value) > WIDTH_LIMIT
        for value in widths.values()
    ):
        raise HandoffError("child-cell leaf exceeds width budget")
    start, count, denominator = radial_geometry(parent, leaf)
    end = start + count
    inputs = [
        {"path": relative(path, root), "sha256": sha256(path)}
        for path in DEFAULT_INPUTS
    ]
    identity = [
        ["1/1" if row == col else "0/1" for col in range(12)]
        for row in range(12)
    ]
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-child-cell-local-reset-factor",
        "factor_id": f"q{child:02d}-micro-{parent:03d}-leaf-{leaf}",
        "status": "CERTIFIED",
        "cell": cell_payload(child),
        "radial": {
            "parent_micro": parent,
            "leaf": leaf,
            "trace_id": tid,
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": rational_text(Fraction(start, denominator)),
            "end": rational_text(Fraction(end, denominator)),
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "standard-realified-six-state-12",
            "order": list(BLOCK_ORDER),
        },
        "solver": {
            "frequency_partition": "exact-16-child-affine-v1",
            "radial_leaf_partition": "two-halves-eight-refined-panels-v1",
            "panels": count,
            "panel_denominator": denominator,
            "resets": 1,
            "local_steps": count,
            "order": 12,
            "rank_cells": 16,
            "global_panel_start": start,
            "global_panel_end": end,
            "structured_rebase_bits": 128,
        },
        "frame_reset": {
            "left_change_of_coordinates": identity,
            "right_change_of_coordinates": identity,
            "parameter_derivative": "exact-zero",
            "physical_restart": False,
            "continuity": (
                "the factor is emitted in the same standard state chart at "
                "both endpoints; adjacent factors compose by exact identity"
            ),
            "left_boundary_sha256": metadata["left_boundary_sha256"],
            "right_boundary_sha256": metadata["right_boundary_sha256"],
        },
        "inherited_prefix_boundary_crosswalk": prefix_boundary_crosswalk(
            child, prefix_context
        ),
        "matrix": matrix,
        "integrity": {
            "producer": {
                "path": relative(Path(__file__), root),
                "sha256": sha256(Path(__file__)),
            },
            "inputs": inputs,
            "input_sha256": canonical_sha256(inputs),
            "output_sha256": canonical_sha256(matrix),
            "generated_source": {
                "renderer_path": relative(PACKAGE / "affine_rail.py", root),
                "renderer_sha256": sha256(PACKAGE / "affine_rail.py"),
                "frame_codegen_path": relative(PACKAGE / "affine_codegen.py", root),
                "frame_codegen_sha256": sha256(PACKAGE / "affine_codegen.py"),
                "frequency_child": child,
                "parent_micro": parent,
                "leaf": leaf,
                "trace_id": tid,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "retained_in_git": False,
            },
        },
        "proof": {
            "ok": True,
            "refusal_code": 0,
            "existence_certified": True,
            "uniqueness_certified": True,
            "factor_rank_certified": True,
            "factor_rank": rank,
            "outward_remainders": True,
            "lower_lift_included": True,
            "upper_right_exact_zero": True,
            "structured_lower_recurrence": True,
            "local_reset_coordinate_change_certified": True,
            "shared_generator_preserved": True,
            "width_limit_enforced": True,
            "block_max_width": widths,
        },
    }
    verify_factor(
        payload, root, context=context, prefix_context=prefix_context
    )
    return payload


def verify_factor(
    data: Any,
    repo_root: Path | None = None,
    *,
    context: dict | None = None,
    prefix_context: dict | None = None,
) -> bool:
    _require(data.get("schema") == SCHEMA, "child factor: wrong schema")
    _require(data.get("status") == "CERTIFIED", "child factor: not certified")
    child = data["cell"]["parent_child_index"]
    parent = data["radial"]["parent_micro"]
    leaf = data["radial"]["leaf"]
    _require(data["cell"] == cell_payload(child), "child factor: cell drift")
    start, count, denominator = radial_geometry(parent, leaf)
    _require(
        data["radial"]["trace_id"] == trace_id(child, parent, leaf)
        and data["radial"]["start"] == rational_text(Fraction(start, denominator))
        and data["radial"]["end"] == rational_text(Fraction(start + count, denominator)),
        "child factor: radial geometry drift",
    )
    _require(
        data["state"]["order"] == list(BLOCK_ORDER)
        and data["state"]["chart"] == "standard-realified-six-state-12",
        "child factor: state chart drift",
    )
    identity = [
        ["1/1" if row == col else "0/1" for col in range(12)]
        for row in range(12)
    ]
    reset = data["frame_reset"]
    _require(
        reset["left_change_of_coordinates"] == identity
        and reset["right_change_of_coordinates"] == identity
        and reset["parameter_derivative"] == "exact-zero"
        and reset["physical_restart"] is False,
        "child factor: local reset is not an exact coordinate identity",
    )
    crosswalk = data["inherited_prefix_boundary_crosswalk"]
    expected_crosswalk = prefix_boundary_crosswalk(child, prefix_context)
    _require(
        crosswalk == expected_crosswalk
        and crosswalk["physical_restart"] is False
        and crosswalk["crosswalk_sha256"]
        == canonical_sha256({
            key: value for key, value in crosswalk.items()
            if key != "crosswalk_sha256"
        }),
        "child factor: inherited prefix boundary crosswalk drift",
    )
    _verify_affine_hull(data["matrix"])
    for value in data["proof"]["block_max_width"].values():
        width = float(value)
        _require(
            math.isfinite(width) and 0.0 <= width <= WIDTH_LIMIT,
            "child factor: width budget exceeded",
        )
    _require(
        data["proof"]["ok"] is True
        and data["proof"]["factor_rank_certified"] is True
        and data["proof"]["factor_rank"] == 12
        and data["proof"]["local_reset_coordinate_change_certified"] is True
        and data["proof"]["shared_generator_preserved"] is True,
        "child factor: incomplete proof",
    )
    integrity = data["integrity"]
    _require(
        integrity["output_sha256"] == canonical_sha256(data["matrix"])
        and integrity["input_sha256"] == canonical_sha256(integrity["inputs"]),
        "child factor: content hash mismatch",
    )
    if repo_root is not None:
        for item in (integrity["producer"], *integrity["inputs"]):
            path = repo_root / item["path"]
            _require(
                path.is_file() and _file_sha256(path) == item["sha256"],
                f"child factor: input drift {item['path']}",
            )
        generated = integrity["generated_source"]
        for path_key, hash_key in (
            ("renderer_path", "renderer_sha256"),
            ("frame_codegen_path", "frame_codegen_sha256"),
        ):
            path = repo_root / generated[path_key]
            _require(
                path.is_file() and _file_sha256(path) == generated[hash_key],
                f"child factor: {path_key} drift",
            )
        context = context or build_microfactor_render_context(frequency_cell(child))
        source, metadata, _ = render_factor(
            child, parent, leaf, context=context
        )
        _require(
            hashlib.sha256(source.encode()).hexdigest()
            == generated["source_sha256"],
            "child factor: source rerender differs",
        )
        _require(
            metadata["left_boundary_sha256"] == reset["left_boundary_sha256"]
            and metadata["right_boundary_sha256"] == reset["right_boundary_sha256"],
            "child factor: reset frame hash drift",
        )
    return True


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--frequency-child", type=int, required=True)
    parser.add_argument("--parent", type=int, required=True)
    parser.add_argument("--leaf", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    context = build_microfactor_render_context(frequency_cell(args.frequency_child))
    prefix_context = build_microfactor_render_context()
    source, _, _ = render_factor(
        args.frequency_child, args.parent, args.leaf, context=context
    )
    with tempfile.TemporaryDirectory(prefix="axial-child-cell-") as temp:
        runner = Path(temp) / "runner.forge"
        runner.write_text(source)
        payload = build_factor(
            args.frequency_child, args.parent, args.leaf,
            args.log.read_text(), args.repo_root, runner=runner, context=context,
            prefix_context=prefix_context,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {payload['factor_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
