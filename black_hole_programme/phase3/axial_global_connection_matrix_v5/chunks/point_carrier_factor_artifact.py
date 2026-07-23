#!/usr/bin/env python3
"""Emit one uniform 8x8 carrier-factor chain from mixed producer traces."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from fractions import Fraction
from typing import Any

from ..affine_rail import MICROFACTOR_COUNT
from .emit_microfactor import parse_trace
from .run_point_carrier_factor_batch import (
    SCHEMA as TAIL_SCHEMA,
    render_point_carrier_factor,
)
from .run_point_microfactor_batch import (
    build_point_context,
    point_trace_id,
    render_point_factor,
)
from .verify_handoff import _require, _verify_affine_hull, canonical_sha256


SCHEMA = "phase3-axial-exact-point-carrier-factor-v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bits(value: str) -> str:
    return f"{int(value) & ((1 << 64) - 1):016x}"


def _float_from_bits(value: str) -> float:
    return struct.unpack(">d", struct.pack(">Q", int(value, 16)))[0]


def _float_bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _fraction_bound(value: Fraction, *, upper: bool) -> float:
    out = float(value)
    represented = Fraction.from_float(out)
    if (upper and represented < value) or (not upper and represented > value):
        out = math.nextafter(out, math.inf if upper else -math.inf)
    return out


def _carrier_block(matrix: dict[str, Any]) -> dict[str, Any]:
    return {
        field: [row[:8] for row in matrix[field][:8]]
        for field in ("center", "linear", "remainder", "hull")
    }


def _verify_carrier_hull(matrix: dict[str, Any]) -> None:
    """Reuse the canonical affine verifier through a zero-padded 12x12 view."""
    padded: dict[str, list[list[Any]]] = {}
    for field in ("center", "linear", "remainder", "hull"):
        zero: Any = (
            "0/1" if field in ("center", "linear")
            else ["0000000000000000", "0000000000000000"]
        )
        rows = [[zero for _ in range(12)] for _ in range(12)]
        _require(len(matrix[field]) == 8, f"carrier {field} row drift")
        for i, row in enumerate(matrix[field]):
            _require(len(row) == 8, f"carrier {field} column drift")
            for j, value in enumerate(row):
                rows[i][j] = value
        padded[field] = rows
    _verify_affine_hull(padded)


def _parse_carrier_trace(text: str, trace_id: int) -> tuple[dict, int, str]:
    matrix = {
        "center": [["0/1" for _ in range(8)] for _ in range(8)],
        "linear": [["0/1" for _ in range(8)] for _ in range(8)],
        "remainder": [[None for _ in range(8)] for _ in range(8)],
        "hull": [[None for _ in range(8)] for _ in range(8)],
    }
    rank, width = None, None
    entries = 0
    for line in text.splitlines():
        fields = line.split()
        if fields[:1] == ["C"] and len(fields) == 6:
            row, col = int(fields[1]), int(fields[2])
            # At the exact-frequency tail the rational center can grow to
            # millions of digits even though its outward interval hull stays
            # narrow.  The certificate therefore serializes the mathematically
            # sufficient hull and represents it as zero center plus remainder.
            center_bits = _bits(fields[3])
            lo_bits, hi_bits = _bits(fields[4]), _bits(fields[5])
            center = _float_from_bits(center_bits)
            lo, hi = _float_from_bits(lo_bits), _float_from_bits(hi_bits)
            center_q = Fraction.from_float(center)
            matrix["center"][row][col] = (
                f"{center_q.numerator}/{center_q.denominator}"
            )
            rem_lo = _fraction_bound(
                Fraction.from_float(lo) - center_q, upper=False
            )
            rem_hi = _fraction_bound(
                Fraction.from_float(hi) - center_q, upper=True
            )
            matrix["remainder"][row][col] = [
                _float_bits(rem_lo), _float_bits(rem_hi)
            ]
            # Store the enclosure of the recentered representation itself.
            # This contains the producer hull and accounts exactly for the
            # outward addition performed by the independent verifier.
            need_lo = (
                center + rem_lo if center == 0.0 or rem_lo == 0.0
                else math.nextafter(center + rem_lo, -math.inf)
            )
            need_hi = (
                center + rem_hi if center == 0.0 or rem_hi == 0.0
                else math.nextafter(center + rem_hi, math.inf)
            )
            hull_lo = min(lo, need_lo)
            hull_hi = max(hi, need_hi)
            matrix["hull"][row][col] = [
                _float_bits(hull_lo), _float_bits(hull_hi)
            ]
            entries += 1
        elif fields[:1] == ["CARRIER_RESULT"] and len(fields) == 4:
            _require(int(fields[1]) == trace_id, "carrier trace id drift")
            rank, width = int(fields[2]), fields[3]
    _require(entries == 64, "carrier trace entry count drift")
    _require(rank == 8 and width is not None, "carrier trace rank missing")
    return matrix, rank, width


def build_payload(
    micro: int,
    matrix: dict[str, Any],
    *,
    child: int | None,
    split: int,
    trace_id: int,
    width: str,
    source_kind: str,
    source_sha256: str,
    log_sha256: str,
) -> dict[str, Any]:
    _verify_carrier_hull(matrix)
    _require(
        all(value == "0/1" for row in matrix["linear"] for value in row),
        "carrier artifact has frequency-linear drift",
    )
    payload = {
        "schema": SCHEMA,
        "status": "CERTIFIED_POINT_CARRIER_FACTOR",
        "frequency": {
            "parameter": "Momega",
            "value": "4097/8192",
            "radius": "0/1",
        },
        "micro": micro,
        "child": child,
        "trace_id": trace_id,
        "domain": {
            "coordinate": "t=32-r",
            "start": str(
                Fraction(micro, 8)
                if child is None else Fraction(split * micro + child, 8 * split)
            ),
            "end": str(
                Fraction(micro + 1, 8)
                if child is None else
                Fraction(split * micro + child + 1, 8 * split)
            ),
        },
        "split": split,
        "source_kind": source_kind,
        "matrix": matrix,
        "rank": 8,
        "max_width": width,
        "source_sha256": source_sha256,
        "log_sha256": log_sha256,
        "proof": {
            "regenerated_at_exact_frequency": True,
            "frequency_linear_matrix_exactly_zero": True,
            "carrier_factor_rank_certified": True,
            "radial_remainder_outward": True,
        },
        "does_not_establish": [
            "a joined radial map",
            "horizon-to-infinity matching",
            "a scattering channel",
            "flux, stability, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def verify_carrier_factor(
    payload: Any, *, rebuild_source: bool = False,
) -> bool:
    _require(payload.get("schema") == SCHEMA, "carrier factor schema drift")
    _require(
        payload.get("status") == "CERTIFIED_POINT_CARRIER_FACTOR",
        "carrier factor status drift",
    )
    micro = int(payload["micro"])
    _require(0 <= micro < MICROFACTOR_COUNT, "carrier factor micro drift")
    _require(payload["rank"] == 8, "carrier factor rank drift")
    _verify_carrier_hull(payload["matrix"])
    _require(
        all(
            value == "0/1"
            for row in payload["matrix"]["linear"] for value in row
        ),
        "carrier factor linear drift",
    )
    without_hash = dict(payload)
    stored = without_hash.pop("payload_sha256")
    _require(stored == canonical_sha256(without_hash), "carrier hash drift")
    if rebuild_source:
        context = build_point_context()
        if payload["source_kind"] == "complete-block-lower":
            source, _ = render_point_factor(micro, context)
        elif payload["source_kind"] in (
            "carrier-only", "carrier-only-split8", "carrier-only-split32",
        ):
            _require(
                payload["source_kind"] != "carrier-only-split32",
                "split32 deterministic rebuild requires its local frame table",
            )
            source, _, trace = render_point_carrier_factor(
                micro, context,
                child=(
                    None if payload["child"] is None
                    else int(payload["child"])
                ),
            )
            _require(trace == payload["trace_id"], "carrier trace drift")
        else:
            raise RuntimeError("unknown carrier source kind")
        _require(
            payload["source_sha256"]
            == hashlib.sha256(source.encode()).hexdigest(),
            "carrier deterministic source drift",
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--tail-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    full = json.loads(args.full_summary.read_text())
    tail = json.loads(args.tail_summary.read_text())
    _require(
        full.get("schema")
        == "phase3-axial-exact-point-microfactor-batch-v1",
        "full point summary drift",
    )
    _require(tail.get("schema") == TAIL_SCHEMA, "tail summary drift")
    full_sources = {item["trace_id"]: item for item in full["sources"]}
    full_results = {item["micro"]: item for item in full["results"]}
    split = int(tail.get("split", 8 if tail.get("split8") else 1))
    _require(split in (1, 8, 32), "tail split drift")
    split_tail = split > 1
    tail_sources = {
        (item["micro"], item["child"]): item for item in tail["sources"]
    }
    tail_results = {
        (item["micro"], item["child"]): item for item in tail["results"]
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for micro in range(MICROFACTOR_COUNT):
        trace_id = point_trace_id(micro)
        complete = full_results.get(trace_id)
        if complete and complete.get("status") == "PASS":
            log = Path(complete["log"])
            matrix12, rank, widths = parse_trace(log.read_text(), trace_id)
            _require(rank == 12, "full factor rank drift")
            payload = build_payload(
                micro, _carrier_block(matrix12),
                child=None,
                split=1,
                trace_id=trace_id,
                width=widths["carrier"],
                source_kind="complete-block-lower",
                source_sha256=full_sources[trace_id]["source_sha256"],
                log_sha256=_sha256(log),
            )
        else:
            if not split_tail:
                result = tail_results.get((micro, None))
                source = tail_sources.get((micro, None))
                _require(
                    result is not None and result.get("status") == "PASS"
                    and source is not None,
                    f"no certified carrier factor for micro {micro}",
                )
                log = Path(result["log"])
                child_trace = int(result["trace_id"])
                matrix, rank, width = _parse_carrier_trace(
                    log.read_text(), child_trace
                )
                _require(rank == 8, "tail carrier rank drift")
                payload = build_payload(
                    micro, matrix, child=None, trace_id=child_trace,
                    split=1,
                    width=width,
                    source_kind="carrier-only",
                    source_sha256=source["source_sha256"],
                    log_sha256=_sha256(log),
                )
                verify_carrier_factor(payload)
                (args.output_dir / f"point_carrier_{micro:03d}.json").write_text(
                    json.dumps(payload, indent=2, sort_keys=True) + "\n"
                )
                continue
            for child in range(split):
                result = tail_results.get((micro, child))
                source = tail_sources.get((micro, child))
                _require(
                    result is not None and result.get("status") == "PASS"
                    and source is not None,
                    f"no certified carrier split for micro {micro}/{child}",
                )
                log = Path(result["log"])
                child_trace = int(result["trace_id"])
                matrix, rank, width = _parse_carrier_trace(
                    log.read_text(), child_trace
                )
                _require(rank == 8, "tail carrier rank drift")
                child_payload = build_payload(
                    micro, matrix, child=child, split=split,
                    trace_id=child_trace,
                    width=width,
                    source_kind=f"carrier-only-split{split}",
                    source_sha256=source["source_sha256"],
                    log_sha256=_sha256(log),
                )
                verify_carrier_factor(child_payload)
                (
                    args.output_dir
                    / f"point_carrier_{micro:03d}_{child}.json"
                ).write_text(
                    json.dumps(child_payload, indent=2, sort_keys=True) + "\n"
                )
            continue
        verify_carrier_factor(payload)
        (args.output_dir / f"point_carrier_{micro:03d}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
    print(f"PASS emitted {MICROFACTOR_COUNT} point carrier factors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
