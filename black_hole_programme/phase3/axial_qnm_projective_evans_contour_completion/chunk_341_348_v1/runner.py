#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 341--348."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=341,
    stop=349,
    predecessor=HERE.parent / "chunk_333_340_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_341_348_v1"
    ),
    version="341-348-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
