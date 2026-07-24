#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 989--996."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=989,
    stop=997,
    predecessor=HERE.parent / "chunk_981_988_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_989_996_v1"
    ),
    version="989-996-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

