#!/usr/bin/env python3
"""Independent verifier for the BT eight-point inner-threshold obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-inner-threshold-obstruction-v1.schema.json",
)
TAU2 = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1.json",
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


def residue_data(profile):
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    r, tau1 = sp.symbols("r tau1")
    ratio = m**2
    u = 1 + ratio + m * (z + 1 / z)
    measure = m**2 * (1 - z**2) ** 2 / z**3
    integrand = sp.cancel(measure * 6 * profile.subs({r: ratio, tau1: u}) / u)
    zero = sp.factor(sp.residue(integrand, z, 0))
    minus_m = sp.factor(sp.residue(integrand, z, -m))
    log_m = sp.factor(-(zero + minus_m))
    series = sp.series(log_m, m, 0, 5)
    coefficient = sp.factor(series.removeO().expand().coeff(m, 2) / 2)
    return {
        "residue_at_z_zero": str(zero),
        "residue_at_z_minus_m": str(minus_m),
        "physical_log_m_coefficient": str(log_m),
        "small_m_series": str(series),
        "r_log_r_coefficient": Fraction(coefficient),
    }


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    analysis = certificate["profile_analysis"]
    threshold = certificate["inner_threshold"]
    rows = analysis["rows"]
    r, tau1, tau2 = sp.symbols("r tau1 tau2")
    profiles = [sp.sympify(row["inner_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected = (
        3
        * (
            9 * r**2
            - 18 * r * tau1
            - 18 * r
            + 34 * tau1**2
            - 18 * tau1
            + 9
        )
        / (128 * tau1**2)
    )
    tau2_profiles = [
        sp.sympify(row["tau2_profile"])
        for row in load(TAU2)["profile_analysis"]["rows"]
    ]
    derived = [residue_data(profile) for profile in profiles]
    derived_difference = residue_data(difference)
    recorded = threshold["fixture_residues"]
    recorded_difference = threshold["difference_residue"]
    inputs = certificate["provenance"]["inputs"]

    def residue_strings_match(left, right):
        return all(
            left[name] == right[name]
            for name in (
                "residue_at_z_zero",
                "residue_at_z_minus_m",
                "physical_log_m_coefficient",
                "small_m_series",
            )
        )

    coefficients = [row["r_log_r_coefficient"] for row in derived]
    difference_coefficient = derived_difference["r_log_r_coefficient"]
    checks = {
        "schema_validation": True,
        "profile_hashes_and_lengths": all(
            text_sha256(row["inner_profile"]) == row["inner_profile_sha256"]
            and len(row["inner_profile"]) == row["inner_profile_length"]
            for row in rows
        ),
        "symbolic_difference_identity": sp.cancel(difference - expected) == 0,
        "recorded_difference_hash": text_sha256(str(difference))
        == analysis["difference_sha256"],
        "individual_tau2_profile_replay": all(
            profile.subs({r: 4, tau1: 10}) == predecessor.subs(tau2, 3)
            for profile, predecessor in zip(profiles, tau2_profiles)
        ),
        "fixed_fixture_raw_and_scaled_replay": (
            difference.subs({r: 4, tau1: 10})
            == sp.Rational(7743, 12800)
            and 6 * difference.subs({r: 4, tau1: 10})
            == sp.Rational(23229, 6400)
        ),
        "difference_laurent_support_is_J1_J2_J3": set(
            sp.Poly(sp.expand(difference * tau1**2), tau1).as_dict()
        )
        == {(0,), (1,), (2,)},
        "first_fixture_residue_is_minus_6699_over_128": coefficients[0]
        == Fraction(-6699, 128),
        "second_fixture_residue_is_minus_7149_over_128": coefficients[1]
        == Fraction(-7149, 128),
        "difference_residue_is_225_over_64": difference_coefficient
        == Fraction(225, 64),
        "difference_residue_matches_fixture_subtraction": difference_coefficient
        == coefficients[0] - coefficients[1],
        "all_recorded_residue_expressions_match": all(
            residue_strings_match(actual, expected_row)
            and actual["r_log_r_coefficient"]
            == frac(expected_row["r_log_r_coefficient"])
            for actual, expected_row in zip(derived, recorded)
        )
        and residue_strings_match(derived_difference, recorded_difference)
        and difference_coefficient
        == frac(recorded_difference["r_log_r_coefficient"]),
        "input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "scoped_scalar_obstruction_is_recorded": (
            certificate["disposition"]["all_four_threshold_functionals"]
            == "COMPUTED"
            and certificate["disposition"]["hard_independent_scalar_fourth_jump"]
            == "OBSTRUCTED_ON_DECLARED_TWO_FIXTURE_CARRIER"
        ),
        "probability_Eq19_gravity_and_Lorentzian_claims_stay_open": (
            certificate["disposition"]["physical_fourth_probability_normalization"]
            == "NOT_ASSEMBLED"
            and certificate["disposition"]["complete_BT_probability"]
            == "NOT_CONSTRUCTED"
            and certificate["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            and any("LORENTZIAN-CAUSAL" in row for row in certificate["does_not_establish"])
            and any("gravitational" in row for row in certificate["does_not_establish"])
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
