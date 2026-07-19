#!/usr/bin/env python3
"""Independent fast or exhaustive replay of physical triangle master completeness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from spectral.euclidean.generic_background_ghost_n3_pole3_relative_ibp import (
    _domain_matrix,
)
from spectral.euclidean.generic_background_physical_hessian_triangle_master_completeness import (
    NEW_MASTER_IDS,
    OUTPUT,
    POLE4,
    PROJECTION,
    ROOT,
    _canonical_digest,
    _fixture_ranks,
    _generic_target_ranks,
    _orbit_crosswalk,
    _s3_action,
    _system,
    validate,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_dependencies(value: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "physical_five_carrier_projection": PROJECTION,
        "pole4_relative_IBP_architecture": POLE4,
    }
    loaded = {}
    for key, expected_path in expected.items():
        reference = value["dependencies"][key]
        path = ROOT / reference["path"]
        if (
            path.resolve() != expected_path.resolve()
            or not path.is_file()
            or _sha256(path) != reference["sha256"]
        ):
            raise ValueError(f"triangle-master dependency drifted: {key}")
        loaded[key] = json.loads(path.read_text())
        if loaded[key]["result_id"] != reference["result_id"]:
            raise ValueError(f"triangle-master dependency identity drifted: {key}")
    return loaded


def verify(
    value: dict[str, Any] | None = None, *, exhaustive: bool = False, jobs: int = 1
) -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text()) if value is None else value
    validate(stored)
    loaded = _check_dependencies(stored)
    system = _system(loaded["physical_five_carrier_projection"])
    if list(system["pivot_columns"]) != stored["canonical_pivot_columns"]:
        raise ValueError("triangle-master pivot section drifted")
    tangent_pivots = [index for index in system["pivot_columns"] if index < 84]
    stages = []
    columns = [system["all_columns"][index] for index in tangent_pivots]
    for master_id, master in zip(
        ("J_triangle", "M_x1", "M_x2", *NEW_MASTER_IDS),
        (*system["old_masters"], *system["all_columns"][-3:]),
    ):
        columns.append(master)
        stages.append(
            {
                "added_master_id": master_id,
                "generic_rank": int(_domain_matrix(columns, system["basis"]).rank()),
            }
        )
    if stages != stored["rank_ladder"] or [row["generic_rank"] for row in stages] != [47, 48, 49, 50, 51, 52]:
        raise ValueError("independent triangle-master rank ladder failed")
    if _s3_action() != stored["S3_action"]:
        raise ValueError("independent standard-S3 action failed")
    if _orbit_crosswalk(loaded["physical_five_carrier_projection"], system["targets"]) != stored["physical_channel_orbit_crosswalk"]:
        raise ValueError("independent physical-channel S3 orbit crosswalk failed")
    if _fixture_ranks(system) != stored["exact_rank_fixtures"]:
        raise ValueError("independent triangle-master fixture ranks failed")
    if exhaustive:
        ranks = _generic_target_ranks(system, jobs)
        if ranks != [row["generic_augmented_rank"] for row in stored["physical_channel_rows"]]:
            raise ValueError("exhaustive physical-channel generic ranks failed")
    formula_payload = {
        key: stored[key]
        for key in (
            "ambient_alpha_monomial_count",
            "raw_tangent_column_count",
            "canonical_tangent_pivot_count",
            "canonical_pivot_columns",
            "rank_ladder",
            "new_master_numerators",
            "S3_action",
            "physical_channel_orbit_crosswalk",
            "physical_channel_rows",
            "exact_rank_fixtures",
        )
    }
    if _canonical_digest(formula_payload) != stored["formula_digest"]:
        raise ValueError("triangle-master formula digest drifted")
    rail = "exhaustive" if exhaustive else "fast"
    print(f"physical Hessian triangle-master completeness independent {rail} verification: PASS")
    return stored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    verify(exhaustive=args.exhaustive, jobs=max(1, args.jobs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
