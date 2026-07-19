#!/usr/bin/env python3
"""Verify the bounded external import of the Science Forge PU order-6 result."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates" / "SCIENCE_FORGE_PU_ORDER6_IMPORT.json"
SCHEMA = HERE / "schema" / "science-forge-external-import-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(source_root: Path | None = None) -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert certificate["schema"] == schema["properties"]["schema"]["const"]
    assert certificate["result_id"] == "SCIENCE_FORGE_PU_ORDER6_IMPORT"
    assert certificate["lifecycle"] == "REPRODUCED_CLEAN_PINNED"
    assert certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    clean_replay = certificate["source"]["clean_replay"]
    assert clean_replay["status"] == "PASS"
    assert clean_replay["source_tree"] == "6f74999b0bb4697bde45551ac7115297fc7a7d78"
    assert clean_replay["go_version"] == "go1.25.8 linux/amd64"
    assert clean_replay["gate_exit_code"] == 31
    assert clean_replay["checks_passed"] == clean_replay["checks_expected"] == 31
    assert clean_replay["sympy_golden_comparisons_passed"] == 3
    assert certificate["source"]["upstream_claim_summary"] == {"passed": 11, "failed": 0}

    by_ratio = {row["ratio"]: row for row in certificate["results"]}
    assert set(by_ratio) == {"5:3", "7:1"}
    expected = {
        "5:3": (3863828151875, 6463101113204736, 15, "a1^3*a2b^5-a1b^3*a2^5"),
        "7:1": (28633766567, 2656254925209600000, 7, "a1*a2b^7-a1b*a2^7"),
    }
    for ratio, (numerator, denominator, radicand, monomial) in expected.items():
        row = by_ratio[ratio]
        assert row["first_nonzero_order"] == sum(map(int, ratio.split(":"))) - 2
        assert row["lower_orders_zero"] == [2, 3, 4, 5]
        assert row["monomial"] == monomial
        coefficient = row["coefficient"]
        assert coefficient == {
            "numerator": numerator,
            "denominator": denominator,
            "radicand": radicand,
        }
        assert math.gcd(numerator, denominator) == 1
        assert Fraction(numerator, denominator) != 0

    scaling = certificate["scaling_fixture"]
    assert scaling["base_ratio"] == "5:3"
    assert scaling["scaled_ratio"] == "10:6"
    assert Fraction(
        scaling["exact_factor_numerator"], scaling["exact_factor_denominator"]
    ) == Fraction(1, 2**14)

    evidence = certificate["evidence"]
    assert evidence["forge_c_backend"] == "PASS"
    assert evidence["forge_native_backend"] == "PASS"
    assert evidence["backend_outputs_byte_identical"] is True
    assert evidence["sympy_term_exact_recomputation"] == "PASS"
    assert evidence["independent_position_space_hermiticity_orders_2_through_5"] == "PASS"
    assert evidence["exact_arithmetic"] is True

    if source_root is not None:
        source_root = source_root.resolve()
        if (source_root / ".git").exists():
            commit = subprocess.run(
                ["git", "-C", str(source_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            assert commit == certificate["source"]["commit"], (
                commit,
                certificate["source"]["commit"],
            )
        for artifact in certificate["source"]["artifacts"]:
            path = source_root / artifact["path"]
            assert path.is_file(), path
            assert sha256(path) == artifact["sha256"], path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        help="optionally require and hash-check a clean checkout at the pinned Tango commit",
    )
    args = parser.parse_args()
    verify(args.source_root)
    print("SCIENCE_FORGE_PU_ORDER6_IMPORT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
