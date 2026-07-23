#!/usr/bin/env python3
"""Emit the canonical global moving-frame join artifact from a Forge trace."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .emit_microfactor import _bits, _rational
from .verify_handoff import CELL, canonical_sha256
from .verify_join import SCHEMA, verify_join
from .verify_microfactor import BLOCK_ORDER, COUNT, verify_microfactor_chain


class JoinTraceError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def parse_join_trace(text: str) -> tuple[dict, dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "BEGIN JOIN" or lines[-1] != "END JOIN":
        raise JoinTraceError("missing or truncated join envelope")
    layout = False
    widths = None
    rank = None
    entries = {}
    for line in lines[1:-1]:
        fields = line.split()
        if fields[:1] == ["LAYOUT"]:
            if fields != ["LAYOUT", "contiguous-block-lower-v1"] or layout:
                raise JoinTraceError(f"malformed layout: {line}")
            layout = True
        elif fields[:1] == ["WIDTH"]:
            if len(fields) != 4 or widths is not None:
                raise JoinTraceError(f"malformed width: {line}")
            for value in fields[1:]:
                parsed = float(value)
                if not math.isfinite(parsed) or parsed < 0.0:
                    raise JoinTraceError(f"negative width: {line}")
            widths = dict(zip(("carrier", "lower", "kernel"), fields[1:]))
        elif fields[:1] == ["RESULT"]:
            if len(fields) != 3 or rank is not None:
                raise JoinTraceError(f"malformed result: {line}")
            rank = int(fields[1])
            if not math.isfinite(float(fields[2])):
                raise JoinTraceError(f"nonfinite result width: {line}")
        elif fields[:1] == ["A"]:
            if len(fields) != 9:
                raise JoinTraceError(f"malformed entry: {line}")
            i, j = int(fields[1]), int(fields[2])
            if not (0 <= i < 12 and 0 <= j < 12) or (i, j) in entries:
                raise JoinTraceError(f"duplicate/out-of-range entry: {line}")
            entries[i, j] = (
                _rational(fields[3]), _rational(fields[4]),
                _bits(fields[5]), _bits(fields[6]),
                _bits(fields[7]), _bits(fields[8]),
            )
        else:
            raise JoinTraceError(f"unexpected record: {line}")
    if not layout or widths is None or rank != 12 or len(entries) != 144:
        raise JoinTraceError("incomplete/refused join trace")
    center = [[None for _ in range(12)] for _ in range(12)]
    linear = [[None for _ in range(12)] for _ in range(12)]
    remainder = [[None for _ in range(12)] for _ in range(12)]
    hull = [[None for _ in range(12)] for _ in range(12)]
    for (i, j), values in entries.items():
        center[i][j], linear[i][j] = values[:2]
        remainder[i][j] = list(values[2:4])
        hull[i][j] = list(values[4:6])
    matrix = {
        "center": center, "linear": linear,
        "remainder": remainder, "hull": hull,
    }
    zero = ["0000000000000000", "0000000000000000"]
    for row in range(8):
        for col in range(8, 12):
            if (
                center[row][col] != "0/1"
                or linear[row][col] != "0/1"
                or remainder[row][col] != zero
            ):
                raise JoinTraceError("upper-right block is not exactly zero")
    return matrix, widths


def build_join(
    *, trace: str, artifacts: Path, source: Path, receipt: Path,
    producer: Path, repo_root: Path
) -> dict:
    paths = sorted(artifacts.glob("microfactor_*.json"))
    payloads = [json.loads(path.read_text()) for path in paths]
    verify_microfactor_chain(payloads, repo_root)
    matrix, widths = parse_join_trace(trace)
    factor_set = [
        {"micro": micro, "path": _relative(path, repo_root), "sha256": _sha256(path)}
        for micro, path in enumerate(paths)
    ]
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-moving-frame-global-join",
        "status": "CERTIFIED",
        "cell": dict(CELL),
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": "0/1",
            "end": "28/1",
        },
        "state": {
            "rows": 12, "cols": 12,
            "chart": "global-moving-block-lower-12",
            "order": list(BLOCK_ORDER),
        },
        "composition": {
            "factor_count": COUNT,
            "radial_order": "left-multiply-increasing-micro-id",
            "dyadic_rebase_bits_after_each_join": 128,
            "standard_basis_materialized": False,
        },
        "frames": {
            "table_sha256": payloads[0]["frames"]["table_sha256"],
            "left_boundary_sha256": payloads[0]["frames"]["left_boundary_sha256"],
            "right_boundary_sha256": payloads[-1]["frames"]["right_boundary_sha256"],
            "adjacent_hashes_verified": True,
        },
        "matrix": matrix,
        "integrity": {
            "producer": {"path": _relative(producer, repo_root), "sha256": _sha256(producer)},
            "join_source": {"path": _relative(source, repo_root), "sha256": _sha256(source)},
            "join_receipt": {"path": _relative(receipt, repo_root), "sha256": _sha256(receipt)},
            "factor_artifacts": factor_set,
            "factor_set_sha256": canonical_sha256(factor_set),
            "output_sha256": canonical_sha256(matrix),
        },
        "proof": {
            "ok": True,
            "factor_chain_verified": True,
            "factor_rank_certified": True,
            "factor_rank": 12,
            "rank_argument": "product-of-block-diagonal-determinants",
            "upper_right_exact_zero": True,
            "shared_generator_preserved": True,
            "block_max_width": widths,
        },
    }
    verify_join(payload, repo_root)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build_join(
            trace=args.log.read_text(), artifacts=args.artifacts,
            source=args.source, receipt=args.receipt,
            producer=Path(__file__), repo_root=args.repo_root,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"PASS {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
