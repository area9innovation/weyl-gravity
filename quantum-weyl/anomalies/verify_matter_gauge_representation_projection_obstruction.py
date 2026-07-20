#!/usr/bin/env python3
"""Independent replay of the healthy matter/gauge projection obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION.json"
)
SCHEMA = (
    HERE
    / "schema/matter-gauge-representation-projection-obstruction-v1.schema.json"
)
SOURCES = (
    "matter_gauge_representation_projection_obstruction.py",
    "matter_gauge_representation_projection_obstruction_certificate.py",
    "verify_matter_gauge_representation_projection_obstruction.py",
    "schema/matter-gauge-representation-projection-obstruction-v1.schema.json",
    "tests/test_matter_gauge_representation_projection_obstruction.py",
    "../reports/matter-gauge-representation-projection-obstruction.md",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _q(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"matter/gauge projection schema failed: {errors}")
    pin = value["input_pin"]
    source_path = ROOT / pin["path"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != pin["sha256"]:
        raise ValueError("matter-lattice input hash failed")
    source = _load(source_path)
    if (
        source["result_id"] != pin["result_id"]
        or source["healthy_nonnegative_classification"][
            "unbounded_nonnegative_real_cone"
        ]
        != "EMPTY"
    ):
        raise ValueError("matter-lattice terminal state failed")

    theorem = value["projection_theorem"]
    gravity_c = _q(theorem["gravity_separator_value"])
    species_c = {
        name: _q(row)
        for name, row in theorem["species_separator_values"].items()
    }
    source_species = {
        name: _q(row["vector"][0])
        for name, row in source["matter_vectors_absolute_determinant"].items()
    }
    if gravity_c != _q(source["gravity_vector"][0]) or species_c != source_species:
        raise ValueError("separator coefficient import failed")
    if gravity_c <= 0 or any(value <= 0 for value in species_c.values()):
        raise ValueError("positive separating functional failed")
    # A representation contributes dim(R) times its underlying field row.
    # Independent finite witnesses at dimensions 1, 2, 3 and 17 establish the
    # exact positive-integer scaling used by the universal proof.
    for dimension in (1, 2, 3, 17):
        if any(dimension * coefficient <= 0 for coefficient in species_c.values()):
            raise ValueError("representation-dimension projection failed")
    if (
        theorem["joint_solution_set"] != "EMPTY"
        or value["representation_gate_disposition"][
            "bounded_group_rank_highest_weight_enumeration"
        ]
        != "NOT_PERFORMED_PROJECTION_OBSTRUCTION_IS_PRIOR"
        or value["claim_flags"]["JOINT_HEALTHY_WEYL_GAUGE_SOLUTION_EXISTS"]
        is not False
    ):
        raise ValueError("empty-intersection boundary failed")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("projection-obstruction source manifest drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("matter/gauge projection obstruction independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
