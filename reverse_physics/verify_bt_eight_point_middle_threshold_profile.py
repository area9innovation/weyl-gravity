#!/usr/bin/env python3
"""Independent verifier for the BT eight-point middle-threshold profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator

import verify_bt_eight_point_outer_threshold_profile as outer_rail


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-middle-threshold-profile-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    analysis = certificate["profile_analysis"]
    chain = certificate["threshold_chain"]
    rows = analysis["rows"]
    tau3, tau4 = sp.symbols("tau3 tau4")
    profiles = [sp.sympify(row["middle_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected = (
        3 * (27213 * tau3**2 - 13462 * tau3 + 29485)
        / (156800 * tau3**2 * tau4)
    )
    after_outer = sp.factor(difference * tau4)
    a3 = Fraction(2)
    middle = Fraction(3, 156800) * (
        27213 * a3 - 13462 + Fraction(29485) / a3
    )
    inputs = certificate["provenance"]["inputs"]
    checks = {
        "schema_validation": True,
        "profile_hashes_and_lengths": all(
            text_sha256(row["middle_profile"]) == row["middle_profile_sha256"]
            and len(row["middle_profile"]) == row["middle_profile_length"]
            for row in rows
        ),
        "symbolic_difference_identity": sp.cancel(difference - expected) == 0,
        "recorded_difference_hash": text_sha256(str(difference))
        == analysis["difference_sha256"],
        "tau3_four_sample_replay": difference.subs({tau3: 4, tau4: 1})
        == sp.Rational(246627, 501760),
        "tau3_five_outer_replay": difference.subs({tau3: 5, tau4: 1})
        == sp.Rational(771, 1568),
        "outer_functional_identity": sp.cancel(
            after_outer - sp.sympify(chain["after_outer_functional"])
        )
        == 0
        and text_sha256(chain["after_outer_functional"])
        == chain["after_outer_functional_sha256"],
        "independent_J1_J2_J3_unit_coefficients": outer_rail.exact_J_coefficients()[
            :3
        ]
        == [1, 1, 1],
        "middle_scaling_and_coefficient": middle
        == frac(chain["middle_threshold_difference"])
        == Fraction(334239, 313600),
        "middle_difference_nonzero": middle != 0,
        "input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "final_moment_and_Eq19_stay_open": (
            certificate["disposition"]["threshold_integrated_fourth_moment"]
            == "NOT_COMPUTED"
            and certificate["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
        ),
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
