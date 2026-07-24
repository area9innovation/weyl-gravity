#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 637--652."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=637,
    stop=653,
    predecessor=HERE.parent / "chunk_621_636_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_637_652_v1"
    ),
    version="637-652-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
