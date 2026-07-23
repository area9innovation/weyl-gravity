"""Exact prefix/crosswalk/tail composition on one final frequency child."""
from __future__ import annotations

import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any

from .child_cell_factor import cell_payload
from .child_tail_join import verify_join as verify_tail_join
from .emit_join import parse_join_trace
from .join_microfactors import render_join_source
from .prefix_join import verify_artifact as verify_prefix_join
from .state_permutation import (
    permute_affine_block_to_standard,
    permutation_payload,
    verify_permutation,
)
from .verify_handoff import (
    _file_sha256,
    _require,
    _verify_affine_hull,
    canonical_sha256,
)


SCHEMA = "phase3-axial-final-frequency-child-global-map-v1"


def _float(bits: str) -> float:
    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


def _bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _directed(value: Fraction, direction: float) -> float:
    out = float(value)
    if (
        direction < 0 and Fraction.from_float(out) > value
    ) or (
        direction > 0 and Fraction.from_float(out) < value
    ):
        out = math.nextafter(out, direction)
    return out


def _hull(center: Fraction, linear: Fraction, remainder: list[str]) -> list[str]:
    rlo, rhi = map(_float, remainder)
    lo = math.nextafter(
        _directed(center - abs(linear), -math.inf) + rlo, -math.inf
    )
    hi = math.nextafter(
        _directed(center + abs(linear), math.inf) + rhi, math.inf
    )
    return [_bits(lo), _bits(hi)]


def restrict_prefix_matrix(matrix: dict, child: int) -> dict:
    shift = Fraction(2 * child - 15, 16)
    scale = Fraction(1, 16)
    center, linear, remainder, hull = [], [], [], []
    for row in range(12):
        crow, lrow, rrow, hrow = [], [], [], []
        for col in range(12):
            c = Fraction(matrix["center"][row][col])
            l = Fraction(matrix["linear"][row][col])
            cc, ll = c + shift * l, scale * l
            rem = list(matrix["remainder"][row][col])
            crow.append(_rational(cc))
            lrow.append(_rational(ll))
            rrow.append(rem)
            hrow.append(_hull(cc, ll, rem))
        center.append(crow)
        linear.append(lrow)
        remainder.append(rrow)
        hull.append(hrow)
    return {
        "center": center, "linear": linear,
        "remainder": remainder, "hull": hull,
    }


def crosswalk_matrix(crosswalk: dict) -> dict:
    zero = ["0000000000000000", "0000000000000000"]
    remainder = [[list(zero) for _ in range(12)] for _ in range(12)]
    hull = [
        [
            _hull(
                Fraction(crosswalk["center"][row][col]),
                Fraction(crosswalk["linear"][row][col]),
                zero,
            )
            for col in range(12)
        ]
        for row in range(12)
    ]
    return {
        "center": crosswalk["center"],
        "linear": crosswalk["linear"],
        "remainder": remainder,
        "hull": hull,
    }


def composition_factors(prefix: dict, tail: dict, child: int) -> list[dict]:
    return [
        {"matrix": restrict_prefix_matrix(prefix["matrix"], child)},
        {
            "matrix": crosswalk_matrix(
                tail["inherited_prefix_boundary_crosswalk"]
            )
        },
        {"matrix": tail["matrix"]},
    ]


def build_global(
    *,
    child: int,
    trace: str,
    prefix: dict,
    prefix_path: Path,
    tail: dict,
    tail_path: Path,
    source: Path,
    crosswalk_trace: str,
    crosswalk_source: Path,
    prefix_artifact_dir: Path,
    tail_artifact_dir: Path,
    repo_root: Path,
    prefix_context: dict,
    child_context: dict,
) -> dict[str, Any]:
    verify_prefix_join(
        prefix, prefix_artifact_dir, repo_root, context=prefix_context
    )
    verify_tail_join(
        tail, tail_artifact_dir, repo_root,
        context=child_context, prefix_context=prefix_context,
    )
    factors = composition_factors(prefix, tail, child)
    expected_source = render_join_source(factors, certify_join_rank=False)
    _require(source.read_text() == expected_source, "global map: source drift")
    block_matrix, widths = parse_join_trace(trace)
    crosswalk_factor = factors[1]
    expected_crosswalk_source = render_join_source([crosswalk_factor])
    _require(
        crosswalk_source.read_text() == expected_crosswalk_source,
        "global map: crosswalk rank source drift",
    )
    crosswalk_rank_matrix, crosswalk_widths = parse_join_trace(
        crosswalk_trace
    )
    standard_matrix = permute_affine_block_to_standard(block_matrix)
    permutation = permutation_payload()
    payload = {
        "schema": SCHEMA,
        "artifact_kind": "infinity-final-frequency-child-global-map",
        "status": "CERTIFIED",
        "cell": cell_payload(child),
        "domain": {
            "coordinate": "t=32-r",
            "orientation": "increasing-t/inward-r",
            "start": "0/1",
            "end": "28/1",
        },
        "composition": {
            "order": "tail * inherited-prefix-crosswalk * restricted-prefix",
            "physical_restart": False,
            "block_order_join_certified": True,
        },
        "block_order_map": block_matrix,
        "crosswalk_rank_witness": {
            "matrix": crosswalk_rank_matrix,
            "rank": 12,
            "block_max_width": crosswalk_widths,
        },
        "block_to_standard_permutation": permutation,
        "standard_realified_map": standard_matrix,
        "projection_contract": {
            "complex_infinity_projection_input": (
                "standard-realified-six-state-12"
            ),
            "permutation_applied_before_projection": True,
        },
        "integrity": {
            "producer": {
                "path": Path(__file__).resolve().relative_to(
                    repo_root.resolve()
                ).as_posix(),
                "sha256": _file_sha256(Path(__file__)),
            },
            "prefix": {
                "path": prefix_path.resolve().relative_to(
                    repo_root.resolve()
                ).as_posix(),
                "sha256": _file_sha256(prefix_path),
                "payload_sha256": canonical_sha256(prefix),
            },
            "tail": {
                "path": tail_path.resolve().relative_to(
                    repo_root.resolve()
                ).as_posix(),
                "sha256": _file_sha256(tail_path),
                "payload_sha256": canonical_sha256(tail),
            },
            "join_source_sha256": hashlib.sha256(
                expected_source.encode()
            ).hexdigest(),
            "crosswalk_rank_source_sha256": hashlib.sha256(
                expected_crosswalk_source.encode()
            ).hexdigest(),
            "crosswalk_rank_output_sha256": canonical_sha256(
                crosswalk_rank_matrix
            ),
            "block_output_sha256": canonical_sha256(block_matrix),
            "standard_output_sha256": canonical_sha256(standard_matrix),
        },
        "proof": {
            "ok": True,
            "factor_rank_certified": True,
            "factor_rank": 12,
            "rank_argument": (
                "certified prefix factors * certified boundary crosswalk * "
                "certified tail factors"
            ),
            "crosswalk_rank_certified": True,
            "crosswalk_rank": 12,
            "crosswalk_block_max_width": crosswalk_widths,
            "joined_interval_rank_not_required": True,
            "shared_generator_preserved": True,
            "block_max_width": widths,
            "exact_state_permutation_verified": True,
        },
    }
    verify_global(
        payload, prefix, tail, child,
    )
    return payload


def verify_global(
    data: Any,
    prefix: dict,
    tail: dict,
    child: int,
) -> bool:
    _require(data.get("schema") == SCHEMA, "global map: wrong schema")
    _require(data.get("status") == "CERTIFIED", "global map: not certified")
    _require(data["cell"] == cell_payload(child), "global map: cell drift")
    _require(
        data["composition"]["physical_restart"] is False
        and data["composition"]["block_order_join_certified"] is True,
        "global map: false restart or uncertified join",
    )
    _verify_affine_hull(data["block_order_map"])
    _verify_affine_hull(data["crosswalk_rank_witness"]["matrix"])
    verify_permutation(data["block_to_standard_permutation"])
    expected_standard = permute_affine_block_to_standard(
        data["block_order_map"]
    )
    _require(
        data["standard_realified_map"] == expected_standard,
        "global map: block-to-standard permutation not applied",
    )
    _require(
        data["projection_contract"][
            "permutation_applied_before_projection"
        ] is True,
        "global map: projection ordering contract violated",
    )
    factors = composition_factors(prefix, tail, child)
    _require(
        data["integrity"]["prefix"]["payload_sha256"]
        == canonical_sha256(prefix)
        and data["integrity"]["tail"]["payload_sha256"]
        == canonical_sha256(tail),
        "global map: prefix/tail payload drift",
    )
    _require(
        data["integrity"]["join_source_sha256"]
        == hashlib.sha256(
            render_join_source(factors, certify_join_rank=False).encode()
        ).hexdigest(),
        "global map: composition source drift",
    )
    expected_crosswalk_source = render_join_source([factors[1]])
    _require(
        data["integrity"]["crosswalk_rank_source_sha256"]
        == hashlib.sha256(expected_crosswalk_source.encode()).hexdigest()
        and data["proof"]["crosswalk_rank_certified"] is True
        and data["proof"]["crosswalk_rank"] == 12,
        "global map: boundary crosswalk rank certificate drift",
    )
    _require(
        data["crosswalk_rank_witness"]["rank"] == 12
        and data["integrity"]["crosswalk_rank_output_sha256"]
        == canonical_sha256(data["crosswalk_rank_witness"]["matrix"]),
        "global map: boundary crosswalk rank output drift",
    )
    _require(
        data["integrity"]["block_output_sha256"]
        == canonical_sha256(data["block_order_map"])
        and data["integrity"]["standard_output_sha256"]
        == canonical_sha256(data["standard_realified_map"]),
        "global map: output hash drift",
    )
    return True
