#!/usr/bin/env python3
"""Independent verifier for the BT Abel--Naimark asymptotic dilation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-abel-naimark-asymptotic-dilation-v1.schema.json",
)
SOFT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
)
DETECTOR = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json",
)
PHYSICAL = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
)
LOG_SHELL = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
)


def load(path):
    with open(path) as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def gaussian(value):
    return frac(value["real"]), frac(value["imaginary"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_abel(epsilon, deficit):
    denominator = epsilon * epsilon + deficit * deficit
    return (
        (-deficit * deficit / denominator, -epsilon * deficit / denominator),
        (deficit * deficit / denominator, -epsilon * deficit / denominator),
        deficit * deficit / denominator,
    )


def verify(certificate):
    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    abel = certificate.get("abel_time_intertwiner", {})
    time_map = certificate.get("time_resolution_map", {})
    chart = time_map.get("finite_soft_chart", {})
    obstruction = certificate.get("coherent_limit_obstruction", {})
    naimark = certificate.get("naimark_probability_dilation", {})
    typing = certificate.get("object_typing", {})
    disposition = certificate.get("disposition", {})
    soft_source = load(SOFT)
    detector_source = load(DETECTOR)
    physical_source = load(PHYSICAL)
    log_source = load(LOG_SHELL)

    coefficient_rows_ok = False
    chart_rows_ok = False
    scale_rows_ok = False
    try:
        fixtures = [(Fraction(1), Fraction(1)), (Fraction(1), Fraction(2)),
                    (Fraction(2), Fraction(3)), (Fraction(3), Fraction(1))]
        rows = abel["coefficient_fixtures"]
        coefficient_rows_ok = len(rows) == len(fixtures)
        for row, (epsilon, deficit) in zip(rows, fixtures):
            expected_lower, expected_raise, expected_norm = expected_abel(epsilon, deficit)
            coefficient_rows_ok &= (
                frac(row["epsilon"]) == epsilon
                and frac(row["deficit"]) == deficit
                and gaussian(row["lowering_coefficient"]) == expected_lower
                and gaussian(row["raising_coefficient"]) == expected_raise
                and frac(row["lowering_norm_square"]) == expected_norm
                and frac(row["logistic_profile_value"]) == expected_norm
                and expected_raise == (-expected_lower[0], expected_lower[1])
                and row["anti_sharp_relation"] is True
            )

        chart_rows = chart["exact_rows_for_c_equals_2"]
        chart_rows_ok = len(chart_rows) == 4
        previous_bound = None
        for row, x in zip(chart_rows, map(Fraction, (1, 4, 16, 64))):
            argument = (1 + 4 * x) / (1 + x)
            normalized = argument / 4
            bound = Fraction(3, 2 * (1 + 4 * x))
            chart_rows_ok &= (
                frac(row["x_equals_(alpha_r0_over_epsilon)_squared"]) == x
                and frac(row["twice_response_log_argument"]) == argument
                and frac(row["argument_divided_by_c_squared"]) == normalized
                and frac(row["upper_bound_on_logc_minus_response"]) == bound
                and normalized < 1
            )
            if previous_bound is not None:
                chart_rows_ok &= bound < previous_bound
            previous_bound = bound

        scale_rows = obstruction["scale_fixtures"]
        scale_rows_ok = len(scale_rows) == 3
        for row, c in zip(scale_rows, map(Fraction, (2, 3, 5))):
            coefficient = (c - 1) / (c + 1)
            scale_rows_ok &= (
                frac(row["c"]) == c
                and frac(row["coherent_coefficient_of_logc"]) == coefficient
                and frac(row["detector_response_coefficient_of_logc"]) == 1
                and frac(row["missing_orthogonal_increment_coefficient"])
                == 1 - coefficient
                and row["coherent_distance_square"]
                == f"({coefficient.numerator}/{coefficient.denominator})*log(c)"
                and 0 < coefficient < 1
            )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        coefficient_rows_ok = chart_rows_ok = scale_rows_ok = False

    response = physical_source.get("response_ledger", {})
    try:
        gamma = frac(response["real_per_pair_Born_normalized"])
        real = 3 * gamma
        hard = frac(response["forced_hard_survival_Born_normalized"])
        born = frac(response["Born_coefficient_without_common_factors"])
        physical_arithmetic = (
            gamma == Fraction(1, 48)
            and real == Fraction(1, 16)
            and hard == Fraction(-1, 16)
            and real + hard == 0
            and born * real == Fraction(3, 512)
            and born * hard == Fraction(-3, 512)
            and frac(naimark["real_norm_square"]) == real
            and frac(naimark["hard_survival_response"]) == hard
            and frac(naimark["inclusive_response"]) == 0
            and frac(naimark["absolute_real_coefficient"]) == Fraction(3, 512)
            and frac(naimark["absolute_hard_coefficient"]) == Fraction(-3, 512)
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        physical_arithmetic = False

    # Independent algebraic checks behind the analytic identities.  With
    # z=exp(2(y-s)), p_s dy becomes dz/(1+z)^2, whose primitive is z/(1+z).
    normalization_identity = all(
        z / (1 + z) + 1 / (1 + z) == 1
        for z in map(Fraction, (1, 2, 7, 19))
    )
    # d/ds (1+z)^-1 = 2z/(1+z)^2, equal to sech(y-s)^2/2.
    derivative_identity = all(
        Fraction(2) * z / (1 + z) ** 2
        == Fraction(2) / (z + 2 + 1 / z)
        for z in map(Fraction, (1, 2, 7, 19))
    )
    # Partial fractions give the coherent integral coefficient
    # (c-1)^2/(c^2-1)=(c-1)/(c+1), multiplying log(c).
    coherent_partial_fraction = all(
        (c - 1) ** 2 / (c * c - 1) == (c - 1) / (c + 1)
        for c in map(Fraction, (2, 3, 5, 11))
    )

    input_rows = certificate.get("provenance", {}).get("inputs", [])
    checks = {
        "schema": not schema_errors,
        "source_formal_hamiltonian": (
            soft_source.get("certificate") == "REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1"
            and soft_source.get("finite_cutoff_flow", {}).get("H_as_first_order")
            == "d*(exp(-i*d*t)*D+exp(+i*d*t)*D_sharp)"
            and abel.get("formal_hamiltonian")
            == "H_as(t)=d*(exp(-i*d*t)*D+exp(+i*d*t)*D_sharp)"
        ),
        "abel_coefficients_and_anti_sharp": coefficient_rows_ok,
        "logistic_norm_profile": (
            coefficient_rows_ok
            and time_map.get("profile")
            == "q_R(y)=|A_epsilon(alpha*exp(-y))|^2=1/(1+exp(2*(y-R)))"
            and time_map.get("resolution_origin") == "R=log(alpha/epsilon)=log(alpha*T)"
        ),
        "profile_derivative_identity": derivative_identity,
        "profile_normalization_identity": normalization_identity,
        "finite_chart_response_and_bound": chart_rows_ok,
        "coherent_distance_partial_fraction": coherent_partial_fraction and scale_rows_ok,
        "ordinary_strong_limit_is_rejected": (
            obstruction.get("disposition") == "NO_ORDINARY_STRONG_ABEL_WAVE_COLUMN_LIMIT"
            and disposition.get("ordinary_strong_Abel_wave_column_limit") == "EXACT_OBSTRUCTION"
            and log_source.get("disposition", {}).get("ordinary_L2_strong_Moller_limit")
            == "EXACT_OBSTRUCTION"
        ),
        "naimark_normalization_and_marginal": (
            normalization_identity
            and derivative_identity
            and naimark.get("unit_norm") == "integral ds dy |Xi_(R,a)|^2=1"
            and naimark.get("detector_marginal")
            == "integral_R^(R+a) p_s(y) ds / a=(q_(R+a)(y)-q_R(y))/a"
            and naimark.get("orthogonality")
            == "Xi_I is orthogonal to Xi_J for disjoint resolution intervals I,J"
        ),
        "detector_predecessor_matches": (
            detector_source.get("certificate") == "REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1"
            and detector_source.get("detector_algebra", {}).get("trace_theorem")
            == "integral_R d_(R,a)(y) dy=a"
            and detector_source.get("disposition", {}).get("time_asymptotic_Hamiltonian")
            == "NOT_CONSTRUCTED"
        ),
        "physical_response_arithmetic": physical_arithmetic,
        "object_boundary": (
            typing.get("identified_common_object")
            == "the detector-resolution automorphism and its positive logistic profile"
            and typing.get("not_identified")
            == "the public R_t number-lowering operator D is not proved equal to the physical S-matrix splitting operator"
            and disposition.get("public_Rt_equals_physical_S_operator") == "NOT_ESTABLISHED"
            and disposition.get("local_BT_asymptotic_Hamiltonian_affiliation") == "NOT_ESTABLISHED"
        ),
        "auxiliary_coordinate_not_spacetime": (
            naimark.get("interpretation")
            == "the extra s label is an auxiliary resolution/noise coordinate, not a spacetime dimension"
            and "that the Naimark resolution coordinate is a new spacetime or physical dimension"
            in certificate.get("does_not_establish", [])
        ),
        "no_claim_promotion": (
            disposition.get("complete_incoming_outgoing_sectors") == "NOT_CONSTRUCTED"
            and disposition.get("full_dressed_Moller_operator") == "NOT_CONSTRUCTED"
            and disposition.get("finite_complete_NLO_probability") == "NOT_ESTABLISHED"
            and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
            and disposition.get("Eq19_all_orders") == "NOT_PROVED"
            and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
        ),
        "hashes": (
            len(input_rows) == 5
            and all(row.get("sha256") == sha256(row.get("path", "")) for row in input_rows)
        ),
        "producer_ledger": (
            certificate.get("checks", {}).get("passed")
            == certificate.get("checks", {}).get("total")
            == 25
            and certificate.get("checks", {}).get("failures") == []
            and all(certificate.get("checks", {}).get("details", {}).values())
        ),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT ABEL NAIMARK ASYMPTOTIC DILATION VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(
        "BT ABEL NAIMARK ASYMPTOTIC DILATION VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
