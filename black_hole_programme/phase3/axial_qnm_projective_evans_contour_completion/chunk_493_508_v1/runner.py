#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 493--508."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=493,
    stop=509,
    predecessor=HERE.parent / "chunk_477_492_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_493_508_v1"
    ),
    version="493-508-v1",
)


if __name__ == "__main__":
    produce(CONFIG)
