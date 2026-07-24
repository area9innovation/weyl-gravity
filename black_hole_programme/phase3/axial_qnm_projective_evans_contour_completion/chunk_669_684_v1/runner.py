#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 669--684."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=669,
    stop=685,
    predecessor=HERE.parent / "chunk_653_668_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_669_684_v1"
    ),
    version="669-684-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
