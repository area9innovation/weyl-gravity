#!/usr/bin/env python3
"""Generate the direct aligned global-orbit self-source fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_global_orbit_self_source import direct_source


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_source_fixture.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    blocks = direct_source()
    return {
        "schema": "einstein-maxwell-weyl-global-orbit-self-source-fixture-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_ORBIT_SELF_SOURCE_FIXTURE",
        "result_state": "DIRECT_FOUR_DIMENSIONAL_ALIGNED_TWIST_ELECTRIC_SELF_SOURCE_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": "aligned real twist position A, twist velocity B and electric tangent Q_e at k=0 on the fixed N=2 magnetic bundle",
        "parameter_order": ["A", "B", "Q_e"],
        "projected_action_sources": {
            block: {name: str(sp.factor(value)) for name, value in rows.items()}
            for block, rows in blocks.items()
        },
        "classification": {
            "direct_four_dimensional_source": True,
            "angular_output_complete_L0_L1_L2": True,
            "spectator_c_and_Wx_sources_zero_by_separate_certificates": True,
            "correction_constructed": False,
        },
        "source_manifest": {
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            "bridge/einstein_sector/einstein_maxwell_weyl_global_orbit_self_source.py": _sha256(ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_global_orbit_self_source.py"),
        },
        "claim_boundary": "This fixture computes only the global/global source. Its homogeneous obstruction cancels only after the extra conjugate-self source is added on the certified balance; no complete orbit correction is inferred here.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_orbit_self_source_fixture --check"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("global-orbit self-source fixture is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_ORBIT_SELF_SOURCE_FIXTURE: PASS")


if __name__ == "__main__":
    main()
