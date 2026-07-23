#!/usr/bin/env python3
"""Render the two exact dyadic q00 Plücker children."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from black_hole_programme.phase3.axial_horizon_h4_plucker_v1 import (
    produce as parent,
)

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
CHILDREN_DIR = HERE / "children"
MANIFEST = HERE / "child_cover_manifest.json"

PARENT_CERTIFICATE = (
    HERE.parent / "axial_horizon_h4_plucker_v1" / "certificate.json"
)
SHORTFALL_CERTIFICATE = (
    HERE.parent
    / "axial_horizon_h4_plucker_continuation_v1"
    / "certificate.json"
)
EXPECTED_PARENT_CERTIFICATE_SHA256 = (
    "230173e50fed0933530ae43c6033bb0b2e4e667ae190224bf33a63a3d7cfb857"
)
EXPECTED_SHORTFALL_CERTIFICATE_SHA256 = (
    "e51af25bb2f5d9b5fd66941aba4a2c60db7a300800f4a4a6f8ff59914ee8defb"
)

Q00 = (Fraction(1, 2), Fraction(2049, 4096))
MIDPOINT = Fraction(4097, 8192)
CHILD_CELLS = (
    (Q00[0], MIDPOINT),
    (MIDPOINT, Q00[1]),
)
TARGET_SEGMENTS = tuple(
    (shell, segment) for shell in range(5) for segment in range(4)
)


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def checked_dependencies() -> None:
    if sha256(PARENT_CERTIFICATE) != EXPECTED_PARENT_CERTIFICATE_SHA256:
        raise RuntimeError("parent certificate hash drift")
    if sha256(SHORTFALL_CERTIFICATE) != (
        EXPECTED_SHORTFALL_CERTIFICATE_SHA256
    ):
        raise RuntimeError("shortfall certificate hash drift")
    parent_certificate = json.loads(PARENT_CERTIFICATE.read_text())
    shortfall = json.loads(SHORTFALL_CERTIFICATE.read_text())
    if parent_certificate.get("status") != "CERTIFIED":
        raise RuntimeError("parent is not certified")
    if shortfall.get("status") != "CERTIFIED_BOUNDED_SHORTFALL":
        raise RuntimeError("split trigger is not a certified shortfall")


def paths(index: int) -> dict[str, Path]:
    stem = f"q00_child_{index}"
    return {
        "source": CHILDREN_DIR / f"{stem}.forge",
        "metadata": CHILDREN_DIR / f"{stem}_metadata.json",
        "compile_log": CHILDREN_DIR / f"{stem}_compile.txt",
        "run_log": CHILDREN_DIR / f"{stem}_run.txt",
    }


def render_child(index: int) -> str:
    if not 0 <= index < len(CHILD_CELLS):
        raise ValueError("child index out of range")
    checked_dependencies()
    old_cell = parent.CELL
    old_targets = parent.TARGET_SEGMENTS
    try:
        parent.CELL = CHILD_CELLS[index]
        parent.TARGET_SEGMENTS = TARGET_SEGMENTS
        source = parent.render()
    finally:
        parent.CELL = old_cell
        parent.TARGET_SEGMENTS = old_targets
    source = source.replace(
        "target=shell3-segment0", "target=shell4-segment3"
    )
    source = source.replace(
        "PLUCKER_PASS reached_shell=3 reached_segment=0",
        "PLUCKER_PASS reached_shell=4 reached_segment=3",
    )
    if source.count("target=shell4-segment3") != 1:
        raise RuntimeError("child target marker drift")
    if source.count(
        "PLUCKER_PASS reached_shell=4 reached_segment=3"
    ) != 1:
        raise RuntimeError("child PASS marker drift")
    return source


def write_child(index: int) -> dict:
    CHILDREN_DIR.mkdir(parents=True, exist_ok=True)
    child_paths = paths(index)
    cell = CHILD_CELLS[index]
    source = render_child(index)
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    metadata = {
        "schema": "phase3-axial-h4-plucker-q00-split-child-source-v1",
        "status": "RENDERED_NOT_YET_VERIFIED",
        "child_index": index,
        "frequency_cell": [rational_text(value) for value in cell],
        "frequency_center": rational_text((cell[0] + cell[1]) / 2),
        "frequency_radius": rational_text((cell[1] - cell[0]) / 2),
        "parent_cell": [rational_text(value) for value in Q00],
        "target": {"shell": 4, "segment": 3},
        "target_segments": [list(value) for value in TARGET_SEGMENTS],
        "shared_parameter_generator": parent.GENERATOR,
        "typed_layouts": {
            "initializer": "block-realified",
            "runtime_generator": "standard Re(6),Im(6)",
            "plucker_state": "Re(20),Im(20)",
        },
        "projective_normalization": (
            "exact dyadic power-of-two per panel"
        ),
        "parent_certificate_sha256": (
            EXPECTED_PARENT_CERTIFICATE_SHA256
        ),
        "shortfall_certificate_sha256": (
            EXPECTED_SHORTFALL_CERTIFICATE_SHA256
        ),
        "induced_inventory_sha256": parent.canonical_hash(
            parent.induced_inventory()
        ),
        "relation_inventory_sha256": parent.canonical_hash(
            parent.relation_inventory()
        ),
        "source_sha256": source_sha,
        "does_not_establish": [
            "transport beyond shell 4 segment 3",
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity scattering theorem",
        ],
    }
    child_paths["source"].write_text(source)
    child_paths["metadata"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    return metadata


def write_sources() -> list[dict]:
    return [write_child(index) for index in range(len(CHILD_CELLS))]


def main() -> int:
    metadata = write_sources()
    print("\n".join(value["source_sha256"] for value in metadata))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
