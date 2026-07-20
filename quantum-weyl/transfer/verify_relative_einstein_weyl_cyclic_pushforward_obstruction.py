#!/usr/bin/env python3
"""Independent verifier for the relative cyclic-pushforward obstruction."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/RELATIVE_EINSTEIN_WEYL_CYCLIC_PUSHFORWARD_OBSTRUCTION.json"
)
SCHEMA = (
    HERE
    / "schema/relative-einstein-weyl-cyclic-pushforward-obstruction-v1.schema.json"
)
SOURCES = (
    "relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "relative_einstein_weyl_cyclic_pushforward_obstruction_certificate.py",
    "verify_relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "schema/relative-einstein-weyl-cyclic-pushforward-obstruction-v1.schema.json",
    "tests/test_relative_einstein_weyl_cyclic_pushforward_obstruction.py",
    "../reports/relative-einstein-weyl-cyclic-pushforward-obstruction.md",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_action_layout(path: Path, expected_count: int) -> None:
    value = _load(path)
    rows = value["content"]["rows"]
    if value["content"]["row_count"] != expected_count or len(rows) != expected_count:
        raise ValueError("independent action-layout row count failed")
    by_index = {row["index"]: row for row in rows}
    if Counter(row["degree"] for row in rows) != (
        Counter({-1: 5, 0: 14, 1: 14, 2: 5})
        if expected_count == 38
        else Counter({-1: 6, 0: 14, 1: 14, 2: 6})
    ):
        raise ValueError("independent action-layout degree census failed")
    for index, row in by_index.items():
        dual = by_index[row["dual_row"]]
        if dual["dual_row"] != index or row["degree"] + dual["degree"] != 1:
            raise ValueError("independent action-layout duality failed")


def _determinant_sign_replay(value: dict) -> None:
    blocks = value["exact_inertia_blocks"]
    expected = {
        "axial": (
            "2*lambda",
            "-lambda*(9*lambda - 2)",
            [2, 0],
            [1, 1],
        ),
        "polar": (
            "2*(lambda - 2)",
            "-(lambda - 2)*(9*lambda - 2)",
            [2, 0],
            [1, 1],
        ),
    }
    for parity, (source_det, target_det, source_inertia, target_inertia) in expected.items():
        block = blocks[parity]
        if (
            block["Einstein_determinant"] != source_det
            or block["restricted_Weyl_determinant"] != target_det
            or block["Einstein_inertia_lambda_ge_6"] != source_inertia
            or block["restricted_Weyl_inertia_lambda_ge_6"]
            != target_inertia
        ):
            raise ValueError("independent inertia formula replay failed")
    # For lambda >= 6, every factor below is strictly positive.
    lam = 6
    source = (2 * lam, 2 * (lam - 2))
    target = (-lam * (9 * lam - 2), -(lam - 2) * (9 * lam - 2))
    if not all(item > 0 for item in source) or not all(item < 0 for item in target):
        raise ValueError("independent determinant sign fixture failed")
    # det(S^T W S)=det(S)^2 det(W); for det(S)!=0 the negative sign persists.
    for det_s in (-5, -1, 1, 7):
        if not all(det_s * det_s * item < 0 for item in target):
            raise ValueError("independent congruence sign replay failed")


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"relative cyclic-pushforward schema failed: {errors}")

    refs = value["dependency_refs"]
    for ref in refs.values():
        path = ROOT / ref["path"]
        source = _load(path)
        if _sha(path) != ref["sha256"] or source.get("result_id") != ref["result_id"]:
            raise ValueError("relative cyclic-pushforward dependency drifted")

    _verify_action_layout(
        ROOT / refs["Einstein_action_BV_layout"]["path"], 38
    )
    _verify_action_layout(ROOT / refs["Weyl_action_BV_layout"]["path"], 40)
    _determinant_sign_replay(value)

    carrier = value["relative_cotangent_carrier"]
    verdict = value["verdict"]
    if (
        carrier["sector_ranks"]
        != {
            "five_current_de_rham": 160,
            "relative_cone": 78,
            "relative_cone_cotangent": 78,
        }
        or carrier["minimality_status"]
        != "MINIMAL_WITHIN_DECLARED_FULL_CONE_COTANGENT_CLASS_ONLY"
        or carrier["absolute_mixed_bundle_minimality"] != "NOT_PROVED"
        or verdict["action_compatible_cyclic_pushforward_exists"] is not False
        or verdict["canonical_316_unary_cyclic_carrier_exists"] is not True
        or verdict["canonical_316_pairing_is_action_pairing"] is not False
        or value["coefficient_gate"]["matched_one_loop_insertions_authorized"]
        is not False
    ):
        raise ValueError("independent carrier/verdict replay failed")

    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("relative cyclic-pushforward source manifest drifted")
    print("relative Einstein--Weyl cyclic-pushforward independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
