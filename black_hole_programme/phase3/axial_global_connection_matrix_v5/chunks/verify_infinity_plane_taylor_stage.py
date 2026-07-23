#!/usr/bin/env python3
"""Independent structural replay of one Taylor2 infinity-plane stage."""
from __future__ import annotations

import argparse
import itertools
import json
import math
import struct
from pathlib import Path
from typing import Any

from .child_cell_factor import cell_payload
from .infinity_plane_taylor_transport import (
    GENERATOR,
    IVTAYLOR_COMMIT,
    IVTAYLOR_PATH,
    IVTAYLOR_SHA256,
    SCHEMA,
    render_stage,
)
from .verify_handoff import _require, canonical_sha256


def _verify_model(
    model: Any, label: str, *, rows: int = 12, cols: int = 6
) -> None:
    _require(
        isinstance(model, dict)
        and model.get("schema") == "ivtaylor-degree2-v1"
        and model.get("generator") == GENERATOR
        and model.get("degree") == 2
        and model.get("rows") == rows
        and model.get("cols") == cols
        and model.get("refusal_code") == 0,
        f"{label}: incompatible Taylor model",
    )
    coefficients = model.get("coefficients")
    remainder = model.get("remainder_bits")
    _require(
        isinstance(coefficients, list) and len(coefficients) == 3,
        f"{label}: degree drift",
    )
    for matrix in coefficients:
        _require(
            len(matrix) == rows and all(len(row) == cols for row in matrix),
            f"{label}: coefficient shape drift",
        )
        for row in matrix:
            for value in row:
                text = str(value)
                if "/" in text:
                    num, den = text.split("/", 1)
                    _require(
                        int(den) > 0 and str(int(num)) == num,
                        f"{label}: malformed rational coefficient",
                    )
                else:
                    int(text)
    _require(
        isinstance(remainder, list)
        and len(remainder) == rows
        and all(len(row) == cols for row in remainder),
        f"{label}: remainder shape drift",
    )
    for row in remainder:
        for cell in row:
            _require(
                isinstance(cell, list) and len(cell) == 2,
                f"{label}: malformed remainder cell",
            )
            lo = struct.unpack(">d", (int(cell[0]) & ((1 << 64) - 1)).to_bytes(8, "big"))[0]
            hi = struct.unpack(">d", (int(cell[1]) & ((1 << 64) - 1)).to_bytes(8, "big"))[0]
            _require(
                math.isfinite(lo) and math.isfinite(hi) and lo <= hi,
                f"{label}: invalid interval remainder",
            )


def _graph_basis_standard(z: dict[str, Any], chart: int) -> dict[str, Any]:
    pairs = ((0, 4), (1, 5), (2, 6), (3, 7), (8, 10), (9, 11))
    charts = tuple(itertools.combinations(range(6), 3))
    _require(0 <= chart < len(charts), "Taylor stage: chart out of range")
    pivot_complex = charts[chart]
    graph_complex = tuple(i for i in range(6) if i not in pivot_complex)
    pivot_rows = tuple(pairs[i][0] for i in pivot_complex) + tuple(
        pairs[i][1] for i in pivot_complex
    )
    graph_rows = tuple(pairs[i][0] for i in graph_complex) + tuple(
        pairs[i][1] for i in graph_complex
    )
    coeffs = []
    for degree in range(3):
        matrix = [[0 for _ in range(6)] for _ in range(12)]
        if degree == 0:
            for i, row in enumerate(pivot_rows):
                matrix[row][i] = 1
        for i, row in enumerate(graph_rows):
            for col in range(6):
                matrix[row][col] = z["coefficients"][degree][i][col]
        coeffs.append(matrix)
    remainder = [[[0, 0] for _ in range(6)] for _ in range(12)]
    for i, row in enumerate(graph_rows):
        for col in range(6):
            remainder[row][col] = z["remainder_bits"][i][col]
    # Same exact block-to-standard row permutation as the Forge consumer.
    source_rows = (0, 1, 2, 3, 8, 9, 4, 5, 6, 7, 10, 11)
    return {
        "schema": "ivtaylor-degree2-v1",
        "generator": GENERATOR,
        "degree": 2,
        "rows": 12,
        "cols": 6,
        "refusal_code": 0,
        "coefficients": [
            [matrix[row] for row in source_rows] for matrix in coeffs
        ],
        "remainder_bits": [remainder[row] for row in source_rows],
    }


def _bits_float(bits: int) -> float:
    return struct.unpack(
        ">d", (int(bits) & ((1 << 64) - 1)).to_bytes(8, "big")
    )[0]


def _verify_basis_change_majorants(data: Any) -> None:
    _require(
        isinstance(data, dict) and set(data) == {"Iminus", "Iplus"},
        "Taylor stage: malformed basis-change majorants",
    )
    for label in ("Iminus", "Iplus"):
        record = data[label]
        _require(
            isinstance(record, dict)
            and set(record) == {"forward", "inverse"},
            f"{label}: malformed basis-change record",
        )
        for kind in ("forward", "inverse"):
            majorant = record[kind]
            _require(
                isinstance(majorant, dict)
                and set(majorant) == {
                    "mantissa_bits", "binary_exponent",
                }
                and isinstance(majorant["binary_exponent"], int),
                f"{label}: malformed {kind} majorant",
            )
            bits = majorant["mantissa_bits"]
            _require(
                isinstance(bits, list) and len(bits) == 2,
                f"{label}: malformed {kind} mantissa",
            )
            lo, hi = (_bits_float(value) for value in bits)
            _require(
                math.isfinite(lo) and math.isfinite(hi)
                and lo <= hi and hi > 0.0,
                f"{label}: invalid {kind} mantissa interval",
            )


def verify_stage(
    data: Any,
    artifact_dir: Path,
    repo_root: Path,
    *,
    previous: dict[str, Any] | None = None,
    rebuild_source: bool = True,
) -> bool:
    _require(data.get("schema") == SCHEMA, "Taylor stage: wrong schema")
    _require(
        data.get("status") == "CERTIFIED_STAGE",
        "Taylor stage: wrong status",
    )
    child, stage = int(data["child"]), int(data["stage"])
    _require(data["cell"] == cell_payload(child), "Taylor stage: cell drift")
    _require(
        data["ivtaylor"] == {
            "commit": IVTAYLOR_COMMIT,
            "path": IVTAYLOR_PATH,
            "sha256": IVTAYLOR_SHA256,
            "degree": 2,
        },
        "Taylor stage: math kernel pin drift",
    )
    _require(
        data["plane_representation"] == {
            "kind": "normalized-grassmann-graph-basis",
            "amplitude_at_each_chart": "identity-6",
            "preserves": [
                "propagated subspace",
                "separate and combined rank",
                "current-form inertia under congruence",
            ],
            "does_not_preserve": [
                "original infinity endpoint amplitude normalization",
                "connection or scattering amplitudes",
            ],
        },
        "Taylor stage: plane normalization drift",
    )
    _require(
        data["terminal_ranks"] == {
            "Iminus": 6, "Iplus": 6, "combined": 12,
        },
        "Taylor stage: terminal rank drift",
    )
    evidence = data["rank_evidence"]
    proof = evidence["proof"]
    _require(
        proof == {
            "minus": True,
            "plus": True,
            "combined": True,
            "derived_from_combined": True,
        },
        "Taylor stage: rank proof drift",
    )
    direct = evidence["direct"]
    _require(
        direct["certified"]["combined"]
        and direct["refusal_codes"]["combined"] == 0,
        "Taylor stage: combined rank lacks direct certificate",
    )
    _require(
        evidence["logical_derivation"].startswith("uniform rank 12"),
        "Taylor stage: missing subfamily rank derivation",
    )
    _verify_model(data["planes"]["Iminus"], "Iminus")
    _verify_model(data["planes"]["Iplus"], "Iplus")
    for label in ("Iminus", "Iplus"):
        state = data["chart_states"][label]
        _require(
            isinstance(state.get("chart"), int) and 0 <= state["chart"] < 20,
            f"{label}: chart out of range",
        )
        _verify_model(state["z"], f"{label} Z", rows=6, cols=6)
        _require(
            data["planes"][label]
            == _graph_basis_standard(state["z"], state["chart"]),
            f"{label}: emitted basis differs from G_chart(Z)",
        )
    _verify_basis_change_majorants(data["basis_change_majorants"])
    _require(
        data["basis_change_proof"] == {
            "norm": "induced matrix infinity norm, binary-scaled",
            "construction": (
                "outward interval products of every normalized propagation "
                "and rechart basis map and its certified inverse"
            ),
            "establishes": (
                "uniform boundedness and invertibility of the endpoint-to-"
                "normalized graph basis change on this compact child"
            ),
            "does_not_establish": (
                "the original endpoint-coordinate scattering amplitudes"
            ),
        },
        "Taylor stage: basis-change proof drift",
    )
    without_hash = dict(data)
    stored = without_hash.pop("payload_sha256")
    _require(
        stored == canonical_sha256(without_hash),
        "Taylor stage: payload hash drift",
    )
    if stage:
        _require(previous is not None, "Taylor stage: missing predecessor")
        _require(
            data["previous_payload_sha256"] == previous["payload_sha256"],
            "Taylor stage: predecessor hash drift",
        )
    if rebuild_source:
        source, metadata = render_stage(
            child=child,
            stage=stage,
            artifact_dir=artifact_dir,
            repo_root=repo_root,
            previous=previous,
        )
        _require(
            data["source_sha256"] == metadata["source_sha256"],
            "Taylor stage: deterministic source hash drift",
        )
        for key in (
            "cell", "radial", "factor_ordinals", "factor_count",
            "factor_manifest_payload_sha256",
            "plane_contract_payload_sha256", "ivtaylor",
            "plane_representation",
        ):
            _require(data[key] == metadata[key], f"Taylor stage: {key} drift")
        _require(bool(source), "Taylor stage: empty deterministic source")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    previous = (
        json.loads(args.previous.read_text()) if args.previous else None
    )
    verify_stage(
        json.loads(args.artifact.read_text()),
        args.artifact_dir,
        args.repo_root,
        previous=previous,
    )
    print("PASS independent infinity-plane Taylor stage verifier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
