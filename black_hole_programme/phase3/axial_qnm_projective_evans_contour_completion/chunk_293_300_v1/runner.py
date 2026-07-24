#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 293--300."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=293,
    stop=301,
    predecessor=HERE.parent / "panel_292_subdivision_repair_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_293_300_v1"
    ),
    version="293-300-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
