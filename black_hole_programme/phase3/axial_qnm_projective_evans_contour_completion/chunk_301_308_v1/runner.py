#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 301--308."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=301,
    stop=309,
    predecessor=HERE.parent / "chunk_293_300_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_301_308_v1"
    ),
    version="301-308-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
