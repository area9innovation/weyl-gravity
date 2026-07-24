#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 877--884."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=877,
    stop=885,
    predecessor=HERE.parent / "chunk_869_876_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_877_884_v1"
    ),
    version="877-884-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

