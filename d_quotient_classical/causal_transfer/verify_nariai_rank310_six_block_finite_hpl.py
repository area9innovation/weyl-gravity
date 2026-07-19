#!/usr/bin/env python3
"""Independent structural replay of the six-block finite HPL theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-rank310-six-block-finite-hpl-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compose(
    left: set[tuple[int, int, tuple[str, ...]]],
    right: set[tuple[int, int, tuple[str, ...]]],
) -> list[tuple[int, int, tuple[str, ...]]]:
    return [(row, column, a + b) for row, middle, a in left for middle2, column, b in right if middle == middle2]


def _observed_blocks(value: dict, name: str) -> set[tuple[int, int, str]]:
    return {(item["row"], item["column"], item["value"]) for item in value["exact_fixture"][name]}


def verify() -> dict:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, ref in value["dependency_refs"].items():
        path = ROOT / ref["path"]
        payload = json.loads(path.read_text())
        if _sha(path) != ref["sha256"] or payload["result_id"] != ref["artifact_id"]:
            raise ValueError(f"dependency drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise ValueError(f"source drifted: {relative}")

    # Independent block-path audit.  Each product has one composable
    # length-two loop.  The complement relation p0 L0D=0 kills (H Delta)^2;
    # its cyclic dual L0sharpD p0sharp=0 kills (Delta H)^2.
    h_delta = {
        (0, 0, ("L0D", "p0")),
        (4, 2, ("MD",)),
        (5, 7, ("Jsharp", "ksharpD")),
    }
    delta_h = {
        (3, 1, ("kD", "J")),
        (6, 8, ("MD",)),
        (9, 9, ("p0sharp", "L0sharpD")),
    }
    expected_h_delta = {
        (0, 0, "-1 L0D p0"),
        (4, 2, "-1/2 MD"),
        (5, 7, "Jsharp ksharpD"),
    }
    expected_delta_h = {
        (3, 1, "kD J"),
        (6, 8, "-1/2 MD"),
        (9, 9, "-1 p0sharp L0sharpD"),
    }
    if _observed_blocks(value, "H_delta_nonzero_blocks") != expected_h_delta:
        raise ValueError("HDelta block table drifted")
    if _observed_blocks(value, "delta_H_nonzero_blocks") != expected_delta_h:
        raise ValueError("DeltaH block table drifted")
    hd2 = _compose(h_delta, h_delta)
    dh2 = _compose(delta_h, delta_h)
    if hd2 != [(0, 0, ("L0D", "p0", "L0D", "p0"))]:
        raise ValueError(f"unexpected HDelta length-two paths: {hd2}")
    if dh2 != [(9, 9, ("p0sharp", "L0sharpD", "p0sharp", "L0sharpD"))]:
        raise ValueError(f"unexpected DeltaH length-two paths: {dh2}")
    relations = set(value["exact_fixture"]["finite_relations"])
    for relation in ("p0 L0D=0", "L0sharpD p0sharp=0"):
        if relation not in relations:
            raise ValueError(f"square-zero loop has no annihilating relation: {relation}")

    corrections = value["exact_fixture"]["metric_quadratic_cross_corrections"]
    expected = {
        (1, 0, "-1 kD L0D"),
        (3, 2, "-1 L0sharpD ksharpD"),
    }
    observed = {(item["row"], item["column"], item["value"]) for item in corrections}
    if observed != expected:
        raise ValueError("metric quadratic cross corrections drifted")
    if value["analytic_consequence"]["quadratic_metric_cross_terms_may_be_dropped"]:
        raise ValueError("quadratic metric corrections were dropped")
    if value["flags"]["TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER"]:
        raise ValueError("common-slab theorem was promoted before geometric binding")
    print("NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
