#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 365--372."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=365,
    stop=373,
    predecessor=HERE.parent / "chunk_357_364_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_365_372_v1"
    ),
    version="365-372-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
