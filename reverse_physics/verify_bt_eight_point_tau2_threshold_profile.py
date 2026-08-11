#!/usr/bin/env python3
"""Independent verifier for the BT eight-point tau2-threshold profile."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-tau2-threshold-profile-v1.schema.json",
)
MIDDLE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1.json",
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
    tau2, tau3, tau4 = sp.symbols("tau2 tau3 tau4")
    profiles = [sp.sympify(row["tau2_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected = (
        3 * (2090 * tau2**2 + 1146 * tau2 + 981)
        / (12800 * tau2**2)
    )
    a2 = Fraction(3)
    a3 = Fraction(2)
    after_first_two = sp.factor(sp.Rational(a3) * difference)
    third = Fraction(3, 6400) * (
        2090 * a2 + 1146 + Fraction(981, 1) / a2
    )
    middle_profiles = [
        sp.sympify(row["middle_profile"])
        for row in load(MIDDLE)["profile_analysis"]["rows"]
    ]
    inputs = certificate["provenance"]["inputs"]
    checks = {
        "schema_validation": True,
        "profile_hashes_and_lengths": all(
            text_sha256(row["tau2_profile"]) == row["tau2_profile_sha256"]
            and len(row["tau2_profile"]) == row["tau2_profile_length"]
            for row in rows
        ),
        "symbolic_difference_identity": sp.cancel(difference - expected) == 0,
        "recorded_difference_hash": text_sha256(str(difference))
        == analysis["difference_sha256"],
        "individual_middle_profile_replay": all(
            profile.subs(tau2, 7)
            == middle.subs({tau3: 2, tau4: 1})
            for profile, middle in zip(profiles, middle_profiles)
        ),
        "tau2_seven_raw_and_scaled_replay": (
            difference.subs(tau2, 7) == sp.Rational(334239, 627200)
            and after_first_two.subs(tau2, 7)
            == sp.Rational(334239, 313600)
        ),
        "difference_laurent_support_is_J1_J2_J3": set(
            sp.Poly(sp.expand(difference * tau2**2), tau2).as_dict()
        )
        == {(0,), (1,), (2,)},
        "independent_J1_J2_J3_unit_coefficients": outer_rail.exact_J_coefficients()[
            :3
        ]
        == [1, 1, 1],
        "after_first_two_functional_identity": sp.cancel(
            after_first_two - sp.sympify(chain["after_first_two_functionals"])
        )
        == 0
        and text_sha256(chain["after_first_two_functionals"])
        == chain["after_first_two_functionals_sha256"],
        "third_scaling_and_coefficient": third
        == frac(chain["third_threshold_profile_functional_difference"])
        == Fraction(23229, 6400),
        "third_difference_nonzero": third != 0,
        "input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "inner_moment_normalization_and_Eq19_stay_open": (
            certificate["disposition"]["remaining_independent_mass_tau1_reduction"]
            == "NOT_COMPUTED"
            and certificate["disposition"]["physical_normalization"]
            == "NOT_ASSEMBLED"
            and certificate["disposition"]["threshold_integrated_fourth_moment"]
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
