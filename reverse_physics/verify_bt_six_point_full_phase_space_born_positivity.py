#!/usr/bin/env python3
"""Independent explicit-tree verification of full-phase-space BT positivity."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_full_phase_space_born_positivity import (
    CHANNELS,
    FIXTURES,
    channel_square,
    physical_chart,
)
from verify_bt_six_point_planar_physical_born_density import FULL, explicit_tree_family


CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-full-phase-space-born-positivity-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def species_incidence():
    rows = []
    for assignment in CHANNELS:
        row = []
        for channel in CHANNELS:
            omega_count = (assignment & channel).bit_count()
            # A quartic Omega^2 Upsilon^2 vertex with three external legs can
            # be completed by one internal leg exactly for a 1+2 split.
            row.append(int(omega_count in (1, 2)))
        rows.append(row)
    return rows


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    hashes_ok = all(row["sha256"] == sha256(row["path"]) for row in certificate["provenance"]["inputs"])
    fixture_rows = []
    for a, b, t, u, v in FIXTURES:
        result = explicit_tree_family(
            parameter_value=t,
            tilt_value=u,
            final_rotation_value=v,
            shape_values=(a, b),
        )
        momenta, _ = physical_chart(a, b, t, u, v)
        amplitude = result["amplitude"]
        middle = {mask: value for mask, value in amplitude.coefficients.items() if mask.bit_count() == 3}
        fraction_formula = {
            mask: Fraction(1, 4) * sum(
                Fraction(1, channel_square(momenta, other))
                for other in CHANNELS if other != mask
            )
            for mask in CHANNELS
        }
        formula = {
            mask: result["base"](value.numerator, value.denominator)
            for mask, value in fraction_formula.items()
        }
        squarefree = (amplitude * amplitude).coefficients[FULL]
        square_sum = 2 * sum(value * value for value in formula.values())
        fixture_rows.append({
            "trees": result["tree_count"] == 220,
            "topologies": result["topology_counts"] == {(4, 0): 105, (2, 1): 105, (0, 2): 10},
            "support": len(amplitude.coefficients) == 42 and sorted({mask.bit_count() for mask in amplitude.coefficients}) == [3, 4, 5, 6],
            "formula": len(middle) == 20 and all(middle[mask] == middle[FULL ^ mask] == formula[mask] for mask in CHANNELS),
            "square": squarefree == square_sum and squarefree > 0,
        })
    incidence = species_incidence()
    interpretation = certificate["interpretation"]
    return {
        "schema_validation": schema_ok,
        "all_input_hashes_match": hashes_ok,
        "species_flow_independently_reconstructs_J_minus_I": incidence == certificate["universal_complement_formula"]["incidence_matrix"],
        "forbidden_channel_is_exactly_the_like_species_split": all(row[i] == 0 and sum(row) == 9 for i, row in enumerate(incidence)),
        "six_independent_full_chart_fixtures": len(fixture_rows) == 6,
        "all_fixtures_enumerate_220_trees": all(row["trees"] for row in fixture_rows),
        "all_fixtures_retain_105_105_10_topologies": all(row["topologies"] for row in fixture_rows),
        "all_full_amplitudes_have_42_terms_in_degrees_three_to_six": all(row["support"] for row in fixture_rows),
        "all_complete_tree_sums_match_the_universal_formula": all(row["formula"] for row in fixture_rows),
        "all_full_square_free_kernels_match_and_are_positive": all(row["square"] for row in fixture_rows),
        "rank_five_chart_is_recorded": certificate["full_physical_chart"]["jacobian_certificate"]["rank"] == 5,
        "strict_local_claim_is_complete_only_away_from_poles": interpretation["complete_regular_massless_three_to_three_local_phase_space"] == "STRICTLY_POSITIVE" and interpretation["internal_channel_poles"] == "EXCLUDED_NOT_REGULATED",
        "integration_and_normalization_are_not_promoted": interpretation["integrated_normalized_probability"] == "NOT_COMPUTED",
        "eq19_and_gravity_are_not_promoted": interpretation["Eq19_all_orders"] == "NOT_PROVED" and interpretation["metric_BV_BRST_lift"] == "NOT_CONSTRUCTED",
    }


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
