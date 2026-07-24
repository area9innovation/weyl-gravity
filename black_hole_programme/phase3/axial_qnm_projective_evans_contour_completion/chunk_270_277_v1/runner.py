#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 270--277."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=270,
    stop=278,
    predecessor=HERE.parent / "chunk_262_269_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_270_277_v1"
    ),
    version="270-277-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
