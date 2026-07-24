#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 509--524."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=509,
    stop=525,
    predecessor=HERE.parent / "chunk_493_508_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_509_524_v1"
    ),
    version="509-524-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
