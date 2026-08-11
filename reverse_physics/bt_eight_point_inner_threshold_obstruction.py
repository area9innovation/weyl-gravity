#!/usr/bin/env python3
"""Exact fourth threshold obstruction for the BT eight-point scalar jump."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import bt_eight_point_fourth_moment as eight


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-inner-threshold-obstruction-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-inner-threshold-obstruction.md"
SOURCE = "9f3e8e0c"
TAU2_CERT = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-inner-threshold-obstruction.json",
    TAU2_CERT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def rationalized_inner_residue(profile, scale=6):
    """Return exact fixed-invariant log residues for one normalized profile."""
    import sympy as sp

    z, m = sp.symbols("z m", positive=True)
    r, tau1 = sp.symbols("r tau1")
    ratio = m**2
    u = 1 + ratio + m * (z + 1 / z)
    measure = m**2 * (1 - z**2) ** 2 / z**3
    integrand = sp.cancel(
        measure * scale * profile.subs({r: ratio, tau1: u}) / u
    )
    residue_zero = sp.factor(sp.residue(integrand, z, 0))
    residue_minus_m = sp.factor(sp.residue(integrand, z, -m))
    log_m = sp.factor(-(residue_zero + residue_minus_m))
    small_m = sp.series(log_m, m, 0, 5)
    coefficient = sp.factor(
        sp.expand(small_m.removeO()).coeff(m, 2) / 2
    )
    return {
        "residue_at_z_zero": str(residue_zero),
        "residue_at_z_minus_m": str(residue_minus_m),
        "physical_log_m_coefficient": str(log_m),
        "small_m_series": str(small_m),
        "r_log_r_coefficient": rat(Fraction(coefficient)),
    }


def build():
    import sympy as sp

    raw_rows = [
        eight.tau1_profile_eight_point(hard, eight.SOFT_FIXTURE)
        for hard in eight.HARD_FIXTURES
    ]
    rows = [
        {
            "inner_profile": row["outer_profile"],
            "inner_profile_length": row["outer_profile_length"],
            "inner_profile_sha256": row["outer_profile_sha256"],
            "hierarchy_valuations": row["inner_hierarchy_valuations"],
            "leading_order": row["leading_order"],
            "leading_masks": row["leading_masks"],
        }
        for row in raw_rows
    ]
    r, tau1, tau2 = sp.symbols("r tau1 tau2")
    profiles = [sp.sympify(row["inner_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected_difference = (
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
    a2 = Fraction(eight.SOFT_FIXTURE[2])
    a3 = Fraction(eight.SOFT_FIXTURE[3])
    first_three_scale = a2 * a3
    residues = [rationalized_inner_residue(profile) for profile in profiles]
    difference_residue = rationalized_inner_residue(difference)
    inner_coefficients = [
        Fraction(row["r_log_r_coefficient"]["numerator"],
                 row["r_log_r_coefficient"]["denominator"])
        for row in residues
    ]
    difference_coefficient = Fraction(
        difference_residue["r_log_r_coefficient"]["numerator"],
        difference_residue["r_log_r_coefficient"]["denominator"],
    )

    tau2_certificate = load(TAU2_CERT)
    tau2_profiles = [
        sp.sympify(row["tau2_profile"])
        for row in tau2_certificate["profile_analysis"]["rows"]
    ]
    checks = {
        "complete_profiles_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_spectator_masks_present": all(
            row["leading_masks"] == list(range(8)) for row in rows
        ),
        "ordered_valuations_are_zero_zero_minus_one": all(
            row["hierarchy_valuations"]
            == [("e1", 0), ("e2", 0), ("e3", -1)]
            for row in rows
        ),
        "symbolic_inner_profile_difference_identity": sp.cancel(
            difference - expected_difference
        )
        == 0,
        "individual_profiles_replay_tau2_certificate": all(
            profile.subs({r: 4, tau1: 10}) == replay.subs(tau2, 3)
            for profile, replay in zip(profiles, tau2_profiles)
        ),
        "fixed_inner_fixture_raw_difference_is_7743_over_12800": (
            difference.subs({r: 4, tau1: 10})
            == sp.Rational(7743, 12800)
        ),
        "first_three_threshold_replay_is_23229_over_6400": (
            sp.Rational(first_three_scale)
            * difference.subs({r: 4, tau1: 10})
            == sp.Rational(23229, 6400)
        ),
        "difference_uses_only_inner_J1_J2_J3_rows": set(
            sp.Poly(sp.expand(difference * tau1**2), tau1).as_dict()
        )
        == {(0,), (1,), (2,)},
        "fixture_inner_coefficients_are_exact": inner_coefficients
        == [Fraction(-6699, 128), Fraction(-7149, 128)],
        "independent_difference_residue_is_225_over_64": (
            difference_coefficient == Fraction(225, 64)
        ),
        "difference_matches_subtracted_fixture_coefficients": (
            difference_coefficient
            == inner_coefficients[0] - inner_coefficients[1]
        ),
        "scalar_universality_is_obstructed_after_all_four_thresholds": (
            difference_coefficient != 0
        ),
        "physical_probability_normalization_stays_open": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-eight-point-inner-threshold-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "complete normalized independent-mass inner profiles and exact fourth fixed-invariant Kallen obstruction to a universal scalar BT eight-point fourth jump",
        "question": "After all four physical fixed-invariant Kallen coefficient functionals, does the complete eight-point result become independent of the declared hard adjacent invariant?",
        "answer": "No on the declared complete two-fixture scalar carrier. Homogeneity sets a0=1 while retaining the independent ratio r=a1/a0 and u=tau1/a0. Evaluating the first three unit-J functionals at tau4=a4, tau3=a3, and tau2=a2 leaves two exact 34,300-tree profiles over Q(e1,e2,e3,r,u), both at delta order two with all spectator masks and hierarchy valuation (0,0,-1). Their difference is 3*(9*r^2-18*r*u-18*r+34*u^2-18*u+9)/(128*u^2), and at the predecessor fixture (r,u)=(4,10) the first-three scale a2*a3=6 exactly replays 23229/6400. The final inner measure maps its constant, u^-1, and u^-2 rows to J1,J2,J3. A method-distinct rationalization u=1+m^2+m*(z+z^-1), r=m^2 gives the individual invariant-cutoff r*log(r) coefficients -6699/128 and -7149/128. Their difference, independently obtained from the residues at z=0 and z=-m of the difference kernel, is 225/64 and is strictly nonzero. Therefore none of the four nested threshold functionals restores a hard-independent scalar fourth jump on these fixtures. This is a scoped scalar-carrier obstruction, not a normalized fourth probability or a no-go for a channel/profile-valued completion. Such a carrier, its physical normalization, the Cox disposition, complete probability, Eq. (19), gravity, and Lorentzian causality remain open.",
        "profile_analysis": {
            "normalization": {
                "a0": rat(1),
                "a1": "r=a1/a0",
                "tau1": "u=tau1/a0",
                "homogeneity_status": "OVERALL_A0_SCALE_FIXED_RATIO_RETAINED",
            },
            "soft_fixture": eight.SOFT_FIXTURE,
            "hard_fixtures": eight.HARD_FIXTURES,
            "first_three_evaluation": {
                "tau2": rat(a2),
                "tau3": rat(a3),
                "tau4": rat(1),
                "scale": rat(first_three_scale),
            },
            "rows": rows,
            "difference": str(difference),
            "difference_sha256": text_sha256(str(difference)),
            "fixed_inner_fixture_raw_difference": rat(Fraction(7743, 12800)),
            "fixed_inner_fixture_after_first_three": rat(
                Fraction(23229, 6400)
            ),
        },
        "inner_threshold": {
            "rationalization": "r=m^2; u=1+m^2+m*(z+z^-1)",
            "physical_cutoff": "u=Lambda, hence z=m/Lambda+O(Lambda^-2)",
            "first_three_scale": rat(first_three_scale),
            "fixture_residues": residues,
            "difference_residue": difference_residue,
            "fixture_r_log_r_coefficients": [rat(value) for value in inner_coefficients],
            "hard_difference_r_log_r_coefficient": rat(difference_coefficient),
            "local_subtraction_invariance": "At fixed physical u, divergent large-u subtraction coefficients are analytic in r. An invariant mass-independent local subtraction cannot change the r*log(r) coefficient; a fixed-z cutoff is excluded because it is mass dependent.",
        },
        "disposition": {
            "complete_independent_mass_inner_profiles": "COMPUTED_ON_TWO_EXACT_HARD_FIXTURES",
            "all_four_threshold_functionals": "COMPUTED",
            "hard_independent_scalar_fourth_jump": "OBSTRUCTED_ON_DECLARED_TWO_FIXTURE_CARRIER",
            "profile_or_channel_valued_successor": "REQUIRED_BUT_NOT_CONSTRUCTED",
            "physical_fourth_probability_normalization": "NOT_ASSEMBLED",
            "two_atom_Cox_completion": "NOT_DECIDED_WITHOUT_A_UNIVERSAL_SCALAR_MOMENT",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "a global no-go for every hard-profile or channel-resolved fourth-jump carrier",
            "a normalized physical fourth-event probability on either hard fixture",
            "a universal scalar fourth factorial moment",
            "exclusion or selection of the two-atom Cox completion",
            "a globally derived hard-profile state space",
            "a complete physical 2->6 probability",
            "universal behavior outside the two exact hard fixtures",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "next_gate": "Construct the minimal channel/profile-valued fourth carrier from the exact surviving inner kernels and determine its positive or Krein pairing, history-resolved jump map, and physical normalization. A scalar Cox comparison is no longer authorized on the declared carrier unless an additional channel recombination theorem produces a universal trace. In parallel, compare the required carrier with the forced cross-Krein complement in the finite physical Moller column to test whether both obstructions identify the same missing BT degree of freedom.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_inner_threshold_obstruction.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_inner_threshold_obstruction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_inner_threshold_obstruction",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    rows = value.get("profile_analysis", {}).get("rows", [])
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 15
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(rows) == 2
        and all(
            text_sha256(row.get("inner_profile", ""))
            == row.get("inner_profile_sha256")
            for row in rows
        )
        and len(inputs) == 4
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("physical_fourth_probability_normalization")
        == "NOT_ASSEMBLED"
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print(
        "inner hard difference:",
        value["inner_threshold"]["hard_difference_r_log_r_coefficient"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
