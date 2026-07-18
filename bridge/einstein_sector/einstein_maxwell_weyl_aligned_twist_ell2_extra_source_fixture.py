#!/usr/bin/env python3
"""Generate the direct aligned twist--ell2-extra L=1,3 source fixture."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_source import (
    aligned_source,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_source_fixture.json"
ENGINE = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_aligned_twist_ell2_extra_source.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _one(case: tuple[str, str, str, int]) -> tuple[str, dict[str, list[str]]]:
    parity, mode, twist_case, output_ell = case
    axial, polar = aligned_source(parity, mode, twist_case, output_ell)
    key = f"{parity}_{mode}_{twist_case}_L{output_ell}"
    return key, {
        "axial_action_source": [str(value) for value in axial],
        "polar_action_source": [str(value) for value in polar],
    }


def build(workers: int = 4) -> dict[str, Any]:
    cases = list(
        itertools.product(
            ("axial", "polar"),
            ("e1", "e2"),
            ("position", "velocity"),
            (1, 3),
        )
    )
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = dict(executor.map(_one, cases))
    ordered = {key: results[key] for key in sorted(results)}
    return {
        "schema": "einstein-maxwell-weyl-aligned-twist-ell2-extra-source-fixture-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ALIGNED_TWIST_EXTRA_L1_L3_ACTION_SOURCES",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": "m=0 axial twist position/velocity crossed with all four axial/polar ell=2,k=0 extra representatives; L=1,3 outputs at omega_e^2=16/3",
        "normalization": {
            "scalar": "integral_-1^1 P_L(z)^2 dz=2/(2L+1)",
            "axial": "integral_-1^1 (1-z^2)(P_L'(z))^2 dz=2L(L+1)/(2L+1)",
            "axial_action_rows": ["lambda*metric_t", "-lambda*metric_x", "maxwell_t", "maxwell_x"],
            "polar_action_rows": ["-metric_00", "2*metric_01", "-metric_11", "2lambda*maxwell_axial_density"],
        },
        "sources": ordered,
        "classification": {
            "all_four_extra_representatives": True,
            "twist_position_and_velocity": True,
            "aligned_L1_and_L3_outputs": True,
            "direct_four_dimensional_source": True,
            "correction_constructed": False,
        },
        "source_manifest": {
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            str(ENGINE.relative_to(ROOT)): _sha256(ENGINE),
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_twist_ell2_extra_source_fixture --check --workers 4"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    arguments = parser.parse_args()
    value = build(arguments.workers)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("aligned twist--extra source fixture is stale")
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_TWIST_ELL2_EXTRA_SOURCE_FIXTURE: PASS")


if __name__ == "__main__":
    main()
