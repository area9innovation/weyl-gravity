#!/usr/bin/env python3
"""Non-certifying SVD diagnostic for the frozen shell-2 amplitude centre."""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np


def analyze(log_path: Path) -> dict:
    entries: dict[tuple[int, int], Fraction] = {}
    exact_rank = None
    for line in log_path.read_text().splitlines():
        fields = line.split()
        if fields[:1] == ["AMPLITUDE_CENTER_RANK"]:
            exact_rank = int(fields[1])
        elif fields[:1] == ["AC"]:
            entries[(int(fields[1]), int(fields[2]))] = Fraction(fields[3])
    if exact_rank is None or len(entries) != 36:
        raise ValueError("incomplete amplitude-centre diagnostic")
    matrix = np.array(
        [[float(entries[(i, j)]) for j in range(6)] for i in range(6)],
        dtype=np.float64,
    )
    singular = np.linalg.svd(matrix, compute_uv=False)
    return {
        "schema": "phase3-amplitude-centre-diagnostic-v1",
        "certifying": False,
        "source": str(log_path),
        "exact_center_rank": exact_rank,
        "singular_values_descending": [float(x) for x in singular],
        "smallest_singular_value": float(singular[-1]),
        "condition_2": float(singular[0] / singular[-1]),
        "interpretation": (
            "A full-rank, moderately conditioned centre supports enclosure "
            "blow-up as the proximate failure, but does not certify the "
            "uniform parameter family or exclude a physical singularity."
        ),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: analyze_center.py LOG")
    payload = analyze(Path(sys.argv[1]))
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")


if __name__ == "__main__":
    main()
