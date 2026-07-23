#!/usr/bin/env python3
"""Emit and independently verify fixed-frequency radial factor artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..affine_rail import MICROFACTOR_COUNT
from .emit_microfactor import parse_trace
from .run_point_microfactor_batch import (
    OMEGA0,
    build_point_context,
    point_trace_id,
    render_point_factor,
)
from .verify_handoff import (
    _require,
    _verify_affine_hull,
    canonical_sha256,
)


SCHEMA = "phase3-axial-exact-point-radial-factor-v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_factor(
    micro: int,
    trace: str,
    *,
    source_sha256: str,
    log_sha256: str,
) -> dict[str, Any]:
    matrix, rank, widths = parse_trace(trace, point_trace_id(micro))
    _require(
        all(value == "0/1" for row in matrix["linear"] for value in row),
        "point factor: nonzero frequency-linear coefficient",
    )
    payload = {
        "schema": SCHEMA,
        "status": "CERTIFIED_POINT_FACTOR",
        "frequency": {
            "parameter": "Momega",
            "value": f"{OMEGA0.numerator}/{OMEGA0.denominator}",
            "radius": "0/1",
        },
        "micro": micro,
        "domain": {
            "coordinate": "t=32-r",
            "start": str(Fraction(micro, 8)),
            "end": str(Fraction(micro + 1, 8)),
        },
        "matrix": matrix,
        "rank": rank,
        "block_max_width": widths,
        "source_sha256": source_sha256,
        "log_sha256": log_sha256,
        "proof": {
            "regenerated_at_exact_frequency": True,
            "frequency_linear_matrix_exactly_zero": True,
            "radial_remainder_outward": True,
            "factor_rank_certified": True,
            "upper_right_block_exactly_zero": True,
            "not_whole_cell_center_hull": True,
        },
        "does_not_establish": [
            "a joined radial map",
            "horizon-to-infinity matching",
            "a scattering channel",
            "flux, stability, ghost, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def verify_factor(
    data: Any,
    *,
    context: dict[str, Any] | None = None,
    rebuild_source: bool = True,
) -> bool:
    _require(data.get("schema") == SCHEMA, "point factor: wrong schema")
    _require(
        data.get("status") == "CERTIFIED_POINT_FACTOR",
        "point factor: wrong status",
    )
    micro = int(data["micro"])
    _require(0 <= micro < MICROFACTOR_COUNT, "point factor: bad micro")
    _require(
        data["frequency"] == {
            "parameter": "Momega",
            "value": "4097/8192",
            "radius": "0/1",
        },
        "point factor: frequency drift",
    )
    _verify_affine_hull(data["matrix"])
    _require(
        all(
            value == "0/1"
            for row in data["matrix"]["linear"] for value in row
        ),
        "point factor: nonzero frequency-linear coefficient",
    )
    _require(
        data["rank"] == 12
        and all(bool(value) for value in data["proof"].values()),
        "point factor: proof gate failed",
    )
    without_hash = dict(data)
    stored = without_hash.pop("payload_sha256")
    _require(
        stored == canonical_sha256(without_hash),
        "point factor: payload hash drift",
    )
    if rebuild_source:
        source, _ = render_point_factor(
            micro, context or build_point_context()
        )
        _require(
            data["source_sha256"]
            == hashlib.sha256(source.encode()).hexdigest(),
            "point factor: deterministic source drift",
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    if (
        summary.get("schema")
        != "phase3-axial-exact-point-microfactor-batch-v1"
        or not summary.get("all_passed")
        or summary.get("completed_factor_count") != MICROFACTOR_COUNT
    ):
        raise SystemExit("REFUSED: point batch is absent, partial, or failed")
    sources = {item["trace_id"]: item for item in summary["sources"]}
    results = {item["micro"]: item for item in summary["results"]}
    if len(sources) != MICROFACTOR_COUNT or len(results) != MICROFACTOR_COUNT:
        raise SystemExit("REFUSED: point batch trace inventory drift")

    context = build_point_context()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for micro in range(MICROFACTOR_COUNT):
        trace_id = point_trace_id(micro)
        source_record = sources[trace_id]
        result = results[trace_id]
        source, _ = render_point_factor(micro, context)
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        log = Path(result["log"])
        if (
            result.get("status") != "PASS"
            or source_record["source_sha256"] != source_hash
            or result["source_sha256"] != source_hash
            or not log.is_file()
        ):
            raise SystemExit(f"REFUSED: point trace {trace_id} drift")
        payload = build_factor(
            micro, log.read_text(), source_sha256=source_hash,
            log_sha256=_sha256(log),
        )
        verify_factor(payload, context=context)
        (args.output_dir / f"point_micro_{micro:03d}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
    print(f"PASS emitted {MICROFACTOR_COUNT} exact-point factors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
