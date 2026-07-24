#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 262--269."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=262,
    stop=270,
    predecessor=HERE.parent / "chunk_254_261_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_262_269_v1"
    ),
    version="262-269-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
