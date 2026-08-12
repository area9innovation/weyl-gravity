#!/usr/bin/env python3
"""Independent explicit-tree checks for the BT two-angle density theorem."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from verify_bt_six_point_planar_physical_born_density import (
    FULL,
    explicit_tree_family,
)


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_TWO_ANGLE_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-two-angle-physical-born-density-v1.schema.json",
)
FIXTURES = [
    (Fraction(1, 2), Fraction(2, 3)),
    (Fraction(1, 2), Fraction(1, 3)),
    (Fraction(1), Fraction(2, 5)),
    (Fraction(3, 2), Fraction(4, 5)),
    (Fraction(5, 3), Fraction(7, 6)),
    (Fraction(2, 3), Fraction(3, 7)),
]


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    hashes_ok = all(
        row["sha256"] == sha256(row["path"])
        for row in certificate["provenance"]["inputs"]
    )
    fixture_rows = []
    for t_value, u_value in FIXTURES:
        result = explicit_tree_family(
            parameter_value=t_value,
            tilt_value=u_value,
        )
        amplitude = result["amplitude"]
        middle = {
            mask: value
            for mask, value in amplitude.coefficients.items()
            if mask.bit_count() == 3
        }
        representatives = [
            mask for mask in sorted(middle) if mask < (FULL ^ mask)
        ]
        squarefree = (amplitude * amplitude).coefficients.get(
            FULL, result["base"].zero
        )
        square_sum = 2 * sum(
            (middle[mask] * middle[mask] for mask in representatives),
            result["base"].zero,
        )
        total_momentum = [
            sum((row[index] for row in result["momenta"]), result["base"].zero)
            for index in range(4)
        ]
        mass_shell = [
            row[0] * row[0]
            - sum((entry * entry for entry in row[1:]), result["base"].zero)
            for row in result["momenta"]
        ]
        fixture_rows.append(
            {
                "tree_count": result["tree_count"] == 220,
                "topology_counts": result["topology_counts"]
                == {(4, 0): 105, (2, 1): 105, (0, 2): 10},
                "massless_and_conserved": all(
                    value == 0 for value in mass_shell + total_momentum
                ),
                "complete_support": len(amplitude.coefficients) == 42
                and sorted(
                    {mask.bit_count() for mask in amplitude.coefficients}
                )
                == [3, 4, 5, 6],
                "twenty_middle_terms": len(middle) == 20
                and len(representatives) == 10,
                "complement_equal": all(
                    middle[mask] == middle[FULL ^ mask]
                    for mask in representatives
                ),
                "square_identity": squarefree == square_sum,
                "strict_at_fixture": squarefree > 0,
                "independent_angles": u_value != t_value / 2,
            }
        )
    disposition = certificate["interpretation"]
    checks = {
        "schema_validation": schema_ok,
        "all_input_hashes_match": hashes_ok,
        "six_method_distinct_explicit_tree_fixtures": len(fixture_rows) == 6,
        "all_fixtures_have_220_trees": all(row["tree_count"] for row in fixture_rows),
        "all_fixtures_have_105_105_10_topologies": all(
            row["topology_counts"] for row in fixture_rows
        ),
        "all_fixture_momenta_are_massless_and_conserved": all(
            row["massless_and_conserved"] for row in fixture_rows
        ),
        "all_fixture_amplitudes_have_complete_support": all(
            row["complete_support"] for row in fixture_rows
        ),
        "all_fixtures_retain_twenty_middle_terms": all(
            row["twenty_middle_terms"] for row in fixture_rows
        ),
        "all_fixtures_reproduce_ten_complement_equalities": all(
            row["complement_equal"] for row in fixture_rows
        ),
        "all_fixtures_reproduce_the_ten_square_kernel": all(
            row["square_identity"] for row in fixture_rows
        ),
        "all_six_selected_regular_fixtures_are_strictly_positive": all(
            row["strict_at_fixture"] for row in fixture_rows
        ),
        "fixtures_are_not_confined_to_the_old_diagonal": all(
            row["independent_angles"] for row in fixture_rows
        ),
        "global_claim_is_nonnegative_not_everywhere_strict": disposition[
            "possible_isolated_or_lower_dimensional_regular_zero_set"
        ]
        == "NOT_EXCLUDED",
        "full_phase_space_integration_and_eq19_remain_open": disposition[
            "complete_five_dimensional_final_state_phase_space"
        ]
        == "NOT_COMPUTED"
        and disposition["integrated_normalized_probability"] == "NOT_COMPUTED"
        and disposition["Eq19_all_orders"] == "NOT_PROVED",
    }
    return checks


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    if failures:
        print("failures:", ", ".join(failures))
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
