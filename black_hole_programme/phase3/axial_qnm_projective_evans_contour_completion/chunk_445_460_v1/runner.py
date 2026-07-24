#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 445--460."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=445,
    stop=461,
    predecessor=HERE.parent / "chunk_437_444_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_445_460_v1"
    ),
    version="445-460-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
