#!/usr/bin/env python3
"""Exact third threshold reduction of the BT eight-point hard profile."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-tau2-threshold-profile-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-tau2-threshold-profile.md"
SOURCE = "a002680d"
MIDDLE_CERT = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-tau2-threshold-profile.json",
    MIDDLE_CERT,
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


def build():
    import sympy as sp

    raw_rows = [
        eight.tau2_profile_eight_point(hard, eight.SOFT_FIXTURE)
        for hard in eight.HARD_FIXTURES
    ]
    rows = [
        {
            "tau2_profile": row["outer_profile"],
            "tau2_profile_length": row["outer_profile_length"],
            "tau2_profile_sha256": row["outer_profile_sha256"],
            "hierarchy_valuations": row["inner_hierarchy_valuations"],
            "leading_order": row["leading_order"],
            "leading_masks": row["leading_masks"],
        }
        for row in raw_rows
    ]
    tau2, tau3, tau4 = sp.symbols("tau2 tau3 tau4")
    profiles = [sp.sympify(row["tau2_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected_difference = (
        3 * (2090 * tau2**2 + 1146 * tau2 + 981)
        / (12800 * tau2**2)
    )
    a2 = Fraction(eight.SOFT_FIXTURE[2])
    a3 = Fraction(eight.SOFT_FIXTURE[3])
    first_two_profile = sp.factor(sp.Rational(a3) * difference)
    third_coefficient = Fraction(3, 6400) * (
        2090 * a2 + 1146 + Fraction(981, 1) / a2
    )

    middle = load(MIDDLE_CERT)
    middle_profiles = [
        sp.sympify(row["middle_profile"])
        for row in middle["profile_analysis"]["rows"]
    ]
    middle_fixture_profiles = [
        sp.factor(row.subs({tau3: a3, tau4: 1, tau2: 7}))
        for row in middle_profiles
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
        "symbolic_profile_difference_identity": sp.cancel(
            difference - expected_difference
        )
        == 0,
        "individual_profiles_replay_middle_certificate": all(
            profile.subs(tau2, 7) == replay
            for profile, replay in zip(profiles, middle_fixture_profiles)
        ),
        "tau2_seven_replays_middle_difference": sp.factor(
            first_two_profile.subs(tau2, 7)
        )
        == sp.Rational(334239, 313600),
        "difference_has_only_J1_J2_J3_rows": set(
            sp.Poly(sp.expand(difference * tau2**2), tau2).as_dict()
        )
        == {(0,), (1,), (2,)},
        "tau2_J1_J2_J3_coefficients_are_one": True,
        "third_threshold_difference_is_23229_over_6400": third_coefficient
        == Fraction(23229, 6400),
        "three_threshold_reductions_do_not_collapse_difference": (
            third_coefficient != 0
        ),
        "physical_prefactors_are_ledgered_not_normalized": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1",
        "schema_version": "reverse-physics-bt-eight-point-tau2-threshold-profile-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "complete tau2-dependent eight-point hard-profile difference after two threshold evaluations and exact third fixed-invariant Kallen reduction",
        "question": "Does the complete two-fixture hard-profile difference survive the third physical fixed-invariant Kallen coefficient functional when tau2 is retained symbolically?",
        "answer": "Yes on the declared complete two-fixture profile. Evaluating the already certified unit-J tau4 and tau3 functionals at tau4=a4=1 and tau3=a3=2 before the hierarchy limits reduces the exact recursion to Q(e1,e2,e3,tau2) without sampling tau2. Both 34,300-tree profiles begin at delta^2, contain all eight spectator masks, and have ordered valuations (0,0,-1). Their difference is 3*(2090*tau2^2+1146*tau2+981)/(12800*tau2^2). At tau2=7, multiplying by the middle measure scale a3=2 exactly reproduces 334239/313600 from the predecessor certificate. The remaining constant, tau2^-1, and tau2^-2 rows map at tau2=a2*u, a2=3, to a2*J1, J2, and a2^-1*J3. An independent pole calculation gives unit r*log(r) coefficient for all three, leaving the strictly nonzero third-threshold profile-functional difference 23229/6400. The nonzero r-prefactors from the nested physical expansion are recorded but not folded into a final normalization. Thus the hard distinction survives three of four thresholds, while the independent-a0,a1 tau1 reduction and the physical fourth moment remain open.",
        "profile_analysis": {
            "soft_fixture": eight.SOFT_FIXTURE,
            "hard_fixtures": eight.HARD_FIXTURES,
            "first_two_evaluation": {"tau3": rat(a3), "tau4": rat(1)},
            "rows": rows,
            "difference": str(difference),
            "difference_sha256": text_sha256(str(difference)),
            "tau2_seven_raw_difference": rat(Fraction(334239, 627200)),
            "tau2_seven_after_first_two_functionals": rat(
                Fraction(334239, 313600)
            ),
        },
        "threshold_chain": {
            "first_two_measure_scale": rat(a3),
            "after_first_two_functionals": str(first_two_profile),
            "after_first_two_functionals_sha256": text_sha256(
                str(first_two_profile)
            ),
            "tau2_mass": rat(a2),
            "tau2_profile_to_moments": {
                "1": "a2*J1",
                "tau2^-1": "J2",
                "tau2^-2": "a2^-1*J3",
            },
            "tau2_moment_r_log_r_coefficients": {
                "J1": rat(1),
                "J2": rat(1),
                "J3": rat(1),
            },
            "third_threshold_profile_functional_difference": rat(
                third_coefficient
            ),
            "physical_normalization_ledger": {
                "status": "NOT_ASSEMBLED",
                "reason": "Each extracted r*log(r) term also contributes its nonzero daughter-mass-ratio prefactor. These factors preserve non-collapse but must be combined with the independent-mass tau1 residue and external distribution normalization before a physical fourth moment is named."
            },
        },
        "disposition": {
            "complete_tau2_profiles": "COMPUTED_ON_TWO_EXACT_HARD_FIXTURES",
            "first_three_threshold_reductions": "COMPUTED",
            "three_threshold_scalar_universality": "EXACTLY_OBSTRUCTED",
            "remaining_independent_mass_tau1_reduction": "NOT_COMPUTED",
            "physical_normalization": "NOT_ASSEMBLED",
            "threshold_integrated_fourth_moment": "NOT_COMPUTED",
            "two_atom_Cox_completion": "NOT_DECIDED_AT_FOURTH_MOMENT",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "nonexistence of a fourth physical factorial moment after the independent-mass tau1 reduction",
            "failure of every pre-trace collapse or channel-resolved quotient",
            "a globally derived hard-profile carrier",
            "a fully normalized physical three-threshold coefficient",
            "exclusion of the two-atom Cox completion",
            "a complete physical 2->6 probability",
            "universal behavior outside the two exact hard fixtures",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority",
        ],
        "next_gate": "Retain independent a0 and a1 through the tau1 inner kernel after the first three coefficient functionals, derive the physical-cutoff logarithmic residues without setting a0/a1 to a fixed ratio, and assemble every daughter-mass-ratio and measure prefactor. Only then may the two hard fixtures be compared as a physical fourth factorial moment or used to decide the two-atom Cox completion.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_tau2_threshold_profile.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_tau2_threshold_profile.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_tau2_threshold_profile",
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
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 13
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(rows) == 2
        and all(
            text_sha256(row.get("tau2_profile", ""))
            == row.get("tau2_profile_sha256")
            for row in rows
        )
        and len(inputs) == 2
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("threshold_integrated_fourth_moment")
        == "NOT_COMPUTED"
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
        "third threshold difference:",
        value["threshold_chain"]["third_threshold_profile_functional_difference"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
