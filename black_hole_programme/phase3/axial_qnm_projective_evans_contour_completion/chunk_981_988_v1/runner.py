#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 981--988."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=981,
    stop=989,
    predecessor=HERE.parent / "chunk_973_980_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_981_988_v1"
    ),
    version="981-988-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

