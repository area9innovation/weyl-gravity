#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 845--852."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=845,
    stop=853,
    predecessor=HERE.parent / "chunk_837_844_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_845_852_v1"
    ),
    version="845-852-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

