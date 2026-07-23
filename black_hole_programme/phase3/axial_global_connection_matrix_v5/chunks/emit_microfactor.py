#!/usr/bin/env python3
"""Convert one complete Forge microfactor trace into a canonical v3 handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .verify_handoff import CELL, STANDARD_ORDER, canonical_sha256
from .verify_microfactor import BLOCK_ORDER, SCHEMA, verify_microfactor


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
DEFAULT_INPUTS = (
    PACKAGE / "affine_rail.py",
    PACKAGE / "affine_codegen.py",
    HERE / "manifest.json",
    PACKAGE.parent / "axial_complete_reconstruction_repair" / "certificate.json",
    PACKAGE.parent
    / "axial_structured_lower_transition_preflight"
    / "actual_fixture.forge",
)


class TraceError(ValueError):
    pass


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _rational(value: str) -> str:
    q = Fraction(value)
    return f"{q.numerator}/{q.denominator}"


def _bits(value: str) -> str:
    n = int(value)
    return f"{n & ((1 << 64) - 1):016x}"


def parse_trace(text: str, micro: int) -> tuple[dict, int, dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != f"BEGIN {micro}" or lines[-1] != f"END {micro}":
        raise TraceError("missing or truncated BEGIN/END envelope")
    expected_flows = {"carrier": False, "kernel": False, "structured": False}
    layout_seen = False
    entries: dict[tuple[int, int], tuple[str, ...]] = {}
    rank = None
    block_widths = None
    for line in lines[1:-1]:
        fields = line.split()
        if fields[:1] == ["FLOW"]:
            if len(fields) != 5 or fields[1] not in expected_flows:
                raise TraceError(f"malformed FLOW record: {line}")
            if fields[2:] != ["true", "0", "-1"]:
                raise TraceError(f"refused FLOW record: {line}")
            if expected_flows[fields[1]]:
                raise TraceError(f"duplicate FLOW record: {fields[1]}")
            expected_flows[fields[1]] = True
        elif fields[:1] == ["LAYOUT"]:
            if fields != ["LAYOUT", "contiguous-block-lower-v1"] or layout_seen:
                raise TraceError(f"malformed LAYOUT record: {line}")
            layout_seen = True
        elif fields[:1] == ["RESULT"]:
            if len(fields) != 4 or int(fields[1]) != micro or rank is not None:
                raise TraceError(f"malformed RESULT record: {line}")
            rank = int(fields[2])
            float(fields[3])
        elif fields[:1] == ["WIDTH"]:
            if len(fields) != 4 or block_widths is not None:
                raise TraceError(f"malformed WIDTH record: {line}")
            values = [float(value) for value in fields[1:]]
            if any(value < 0.0 for value in values):
                raise TraceError(f"negative WIDTH record: {line}")
            block_widths = dict(zip(("carrier", "lower", "kernel"), fields[1:]))
        elif fields[:1] == ["A"]:
            if len(fields) != 9:
                raise TraceError(f"malformed affine entry: {line}")
            i, j = int(fields[1]), int(fields[2])
            if not (0 <= i < 12 and 0 <= j < 12) or (i, j) in entries:
                raise TraceError(f"duplicate/out-of-range affine entry: {line}")
            entries[i, j] = (
                _rational(fields[3]),
                _rational(fields[4]),
                _bits(fields[5]),
                _bits(fields[6]),
                _bits(fields[7]),
                _bits(fields[8]),
            )
        else:
            raise TraceError(f"unexpected trace record: {line}")
    if not all(expected_flows.values()):
        raise TraceError("missing flow disposition")
    if not layout_seen:
        raise TraceError("missing structured storage-layout tag")
    if rank != 12:
        raise TraceError(f"factor rank is {rank}, expected 12")
    if block_widths is None:
        raise TraceError("missing structured block widths")
    if len(entries) != 144:
        raise TraceError(f"affine payload has {len(entries)} entries, expected 144")

    center = [[None for _ in range(12)] for _ in range(12)]
    linear = [[None for _ in range(12)] for _ in range(12)]
    remainder = [[None for _ in range(12)] for _ in range(12)]
    hull = [[None for _ in range(12)] for _ in range(12)]
    for (i, j), values in entries.items():
        center[i][j], linear[i][j] = values[:2]
        remainder[i][j] = list(values[2:4])
        hull[i][j] = list(values[4:6])
    matrix = {
        "center": center,
        "linear": linear,
        "remainder": remainder,
        "hull": hull,
    }
    zero_bits = ["0000000000000000", "0000000000000000"]
    for i in range(8):
        for j in range(8, 12):
            if (
                center[i][j] != "0/1"
                or linear[i][j] != "0/1"
                or remainder[i][j] != zero_bits
            ):
                raise TraceError("structured upper-right block is not exactly zero")
    return matrix, rank, block_widths


def build_handoff(micro: int, trace: str, root: Path) -> dict:
    if not 0 <= micro < 224:
        raise TraceError("microfactor id out of range")
    manifest = json.loads((HERE / "manifest.json").read_text())
    if manifest.get("schema") != "axial-affine-microfactor-runner-manifest-v3":
        raise TraceError("wrong runner manifest schema")
    entry = manifest["chunks"][micro]
    if entry["start"] != micro:
        raise TraceError("manifest microfactor ordering differs")
    runner = HERE / entry["path"]
    if not runner.is_file() or entry["sha256"] != _sha256(runner):
        raise TraceError("microfactor runner missing or hash differs")
    matrix, rank, block_widths = parse_trace(trace, micro)
    producer = Path(__file__)
    inputs = [
        {"path": _relative(path, root), "sha256": _sha256(path)}
        for path in (*DEFAULT_INPUTS, runner)
    ]
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-moving-frame-microfactor",
        "chunk_id": f"micro-{micro:03d}",
        "status": "CERTIFIED",
        "cell": dict(CELL),
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": f"{Fraction(micro, 8).numerator}/{Fraction(micro, 8).denominator}",
            "end": f"{Fraction(micro + 1, 8).numerator}/{Fraction(micro + 1, 8).denominator}",
        },
        "state": {
            "rows": 12,
            "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "solver": {
            "panels": 8,
            "resets": 1,
            "local_steps": 8,
            "order": 12,
            "rank_cells": 16,
            "global_panel_start": 8 * micro,
            "global_panel_end": 8 * (micro + 1),
            "structured_panels": 8,
            "structured_order": 12,
            "structured_rebase_bits": 128,
            "structured_global_panel_start": 8 * micro,
            "structured_global_panel_end": 8 * (micro + 1),
            "rank_argument": "block-lower-determinant",
        },
        "frames": {
            "table_sha256": manifest["frame_table_sha256"],
            "left_boundary_sha256": entry["left_boundary_sha256"],
            "right_boundary_sha256": entry["right_boundary_sha256"],
            "generation": "single-global-exact-table-sliced-with-byte-identical-overlap",
        },
        "matrix": matrix,
        "integrity": {
            "producer": {
                "path": _relative(producer, root),
                "sha256": _sha256(producer),
            },
            "inputs": inputs,
            "input_sha256": canonical_sha256(inputs),
            "output_sha256": canonical_sha256(matrix),
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
            "dyadic_rebase_bits": 128,
            "rank_argument": "block-lower-determinant",
            "block_max_width": block_widths,
            "storage_layout": "contiguous-block-lower-v1",
            "coefficient_layout": "standard-interleaved-v1",
            "transition_extractor": "contiguous-8-plus-4-v1",
        },
    }
    verify_microfactor(payload, root)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--micro", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build_handoff(args.micro, args.log.read_text(), args.repo_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
