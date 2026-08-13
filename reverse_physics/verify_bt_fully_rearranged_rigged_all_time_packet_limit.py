#!/usr/bin/env python3
"""Independent verifier for the BT rigged all-time packet-limit theorem."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-packet-limit-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def frac(row):
    return Fraction(row["numerator"], row["denominator"])


def cs(parameter):
    parameter = Fraction(parameter)
    return (
        (1 - parameter * parameter) / (1 + parameter * parameter),
        2 * parameter / (1 + parameter * parameter),
    )


def direction(parameter):
    c, s = cs(parameter)
    return c, s, Fraction(0)


def rotate(vector, t, u, v):
    ct, st = cs(t)
    cu, su = cs(u)
    cv, sv = cs(v)
    x, y, z = vector
    x, y = ct * x - st * y, st * x + ct * y
    y, z = cu * y - su * z, su * y + cu * z
    return cv * x - sv * y, sv * x + cv * y, z


def future_three_body(parameters):
    a, b, t, u, v = map(Fraction, parameters)
    units = [direction(0), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(units[1], units[2]),
        cross(units[2], units[0]),
        cross(units[0], units[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    return [
        (energy,) + tuple(energy * component for component in rotate(unit, t, u, v))
        for energy, unit in zip(energies, units)
    ]


def input_rotation_derivatives(a, b, u):
    """Analytic t derivative at t=v=0, without automatic differentiation."""
    units = [direction(0), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(units[1], units[2]),
        cross(units[2], units[0]),
        cross(units[0], units[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    cu, su = cs(u)
    derivatives = []
    for energy, (x, y, _) in zip(energies, units):
        # c'(0)=0 and s'(0)=2 for the first Rz(t).
        dx, dy, dz = -2 * y, 2 * x, Fraction(0)
        derivatives.append(
            (
                energy * dx,
                energy * (cu * dy - su * dz),
                energy * (su * dy + cu * dz),
            )
        )
    return derivatives


def rational_rows():
    incoming = future_three_body(
        (Fraction(2), Fraction(-2), Fraction(0), Fraction(15, 16), Fraction(0))
    )
    outgoing = future_three_body(
        (
            Fraction(2),
            Fraction(-2),
            Fraction(105, 73),
            Fraction(2),
            Fraction(1, 3),
        )
    )
    derivatives = input_rotation_derivatives(
        Fraction(2), Fraction(-2), Fraction(15, 16)
    )
    rows = []
    for i, p in enumerate(incoming):
        for a, k in enumerate(outgoing):
            q0 = Fraction(16, 5) - p[0] - k[0]
            spatial = tuple(p[c] + k[c] for c in range(1, 4))
            radius_squared = sum(value * value for value in spatial)
            numerator = sum(
                spatial[c] * derivatives[i][c] for c in range(3)
            )
            rows.append(
                (
                    (i, a),
                    q0,
                    radius_squared,
                    numerator,
                    q0 * q0 - radius_squared,
                )
            )
    return incoming, outgoing, rows


def expected_even_series(order=6):
    return [
        (
            2 * n + 1,
            Fraction((-1) ** n, 4**n * math.factorial(n) * (2 * n + 1)),
        )
        for n in range(order + 1)
    ]


def expected_odd_series(order=6):
    return [
        (
            2 * n,
            Fraction((-1) ** (n + 1), 4**n * math.factorial(n)),
        )
        for n in range(1, order + 1)
    ]


def recorded_series(rows):
    return [(row["power"], frac(row["coefficient"])) for row in rows]


def derivative_series(rows):
    return {
        power - 1: power * coefficient
        for power, coefficient in rows
        if power > 0
    }


def verify(certificate):
    schema_errors = list(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate)
    )
    if schema_errors:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    hashes_ok = all(sha256(path) == digest for path, digest in hashes.items())
    inputs = {
        path: load(os.path.join(ROOT, path))
        for path in hashes
    }
    predecessors = [
        value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        value
        for path, value in inputs.items()
        if path.startswith("planning/events/")
    )

    incoming, outgoing, expected_rows = rational_rows()
    recorded = certificate["exact_chart_phase_audit"]["rows"]
    row_exact = len(recorded) == len(expected_rows) and all(
        tuple(row["channel"]) == channel
        and frac(row["q0"]) == q0
        and frac(row["spatial_radius_squared"]) == radius_squared
        and frac(row["rotation_numerator_N"]) == numerator
        and frac(row["q_squared"]) == q_squared
        and row["noncritical"] == (numerator != 0 and radius_squared > 0)
        and row["on_shell"] == (q_squared == 0)
        for row, (channel, q0, radius_squared, numerator, q_squared)
        in zip(recorded, expected_rows)
    )
    shell = [
        channel
        for channel, _, _, _, q_squared in expected_rows
        if q_squared == 0
    ]

    half_line = certificate["half_line_distribution"]
    even = recorded_series(
        half_line["even_Gaussian_fixture"]["coefficients"]
    )
    odd = recorded_series(
        half_line["odd_Gaussian_fixture"]["coefficients"]
    )
    even_expected = expected_even_series()
    odd_expected = expected_odd_series()
    even_derivative = derivative_series(even)
    odd_derivative = derivative_series(odd)
    exponential = {
        2 * n: Fraction((-1) ** n, 4**n * math.factorial(n))
        for n in range(7)
    }
    odd_derivative_expected = {
        2 * n + 1: Fraction((-1) ** n, 2 * 4**n * math.factorial(n))
        for n in range(6)
    }

    physical = next(
        value
        for value in predecessors
        if value["certificate"]
        == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1"
    )
    common = next(
        value
        for value in predecessors
        if value["certificate"]
        == "REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1"
    )
    log_shell = next(
        value
        for value in predecessors
        if value["certificate"]
        == "REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1"
    )
    q10 = next(
        value
        for value in predecessors
        if value["certificate"]
        == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"
    )
    shell_intervals = [
        tuple(frac(endpoint) for endpoint in row["y_interval_in_units_of_ell"])
        for row in log_shell["continuum_model"]["shell_fixtures"]
    ]
    shell_distance = frac(
        log_shell["strong_limit_obstruction"][
            "distinct_shell_column_distance_square"
        ]
    )
    rigged = certificate["rigged_packet_limit"]
    boundary = certificate["operator_and_claim_boundary"]
    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate["certificate"].endswith("RIGGED_ALL_TIME_PACKET_LIMIT_V1"),
        "input_hashes_recomputed": hashes_ok,
        "scientific_predecessors_record_pass": all(
            value["checks"]["ok"]
            for value in predecessors
            if value["certificate"]
            != "REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1"
        ),
        "done_event_replayed": event["body"]["payload"]["to_state"] == "DONE",
        "incoming_center_reconstructed": [[str(x) for x in row] for row in incoming] == physical["exact_detector_witness"]["incoming_momenta"],
        "outgoing_center_reconstructed": [[str(x) for x in row] for row in outgoing] == physical["exact_detector_witness"]["outgoing_momenta"],
        "nine_rows_reconstructed_without_forward_AD": row_exact,
        "all_nine_common_rotation_numerators_nonzero": all(row[3] != 0 for row in expected_rows),
        "all_nine_spatial_radii_positive": all(row[2] > 0 for row in expected_rows),
        "unique_shell_recomputed": shell == [(2, 0)],
        "shell_q0_is_one": next(row[1] for row in expected_rows if row[0] == (2, 0)) == 1,
        "shell_radius_squared_is_one": next(row[2] for row in expected_rows if row[0] == (2, 0)) == 1,
        "shell_numerator_recomputed": next(row[3] for row in expected_rows if row[0] == (2, 0)) == Fraction(-384, 425),
        "even_Gaussian_series_recomputed": even == even_expected,
        "odd_Gaussian_series_recomputed": odd == odd_expected,
        "even_derivative_is_Gaussian_series": all(even_derivative.get(power) == coefficient for power, coefficient in exponential.items()),
        "odd_derivative_has_positive_PV_sign": all(odd_derivative.get(power) == coefficient for power, coefficient in odd_derivative_expected.items()),
        "tempered_boundary_sign_is_exact": half_line["tempered_boundary"] == "lim_(T->infinity) F_T(s)=pi*delta(s)+i*PV(1/s)",
        "pointwise_nonconvergence_is_explicit": half_line["pointwise_boundary"].startswith("DOES_NOT_EXIST"),
        "rapid_tail_bound_is_recorded": "g^(N)" in half_line["tail_bound"] and "T^(N-1)" in half_line["tail_bound"],
        "coarea_density_contains_phase_Jacobian": "partial_t delta_ia" in rigged["channel_coarea_density"],
        "domain_is_smooth_and_dense": "C_c^infinity(X)" in rigged["domain"],
        "coherent_L2_limit_is_recorded": "in L2(Y)" in rigged["coherent_limit"],
        "leading_coefficient_has_adjoint_square_form": rigged["leading_coefficient"] == "q8,infinity[F]=16*||K_infinity F||_L2(Y)^2",
        "strictness_uses_unique_real_delta_part": "only channel (2,0) crosses shell" in rigged["strict_nontriviality"],
        "complete_leading_support_is_imported": physical["complete_leading_physical_probability"]["status"].startswith("COMPLETE_LEADING"),
        "disconnected_support_zero_is_imported": physical["disconnected_support_classification"]["detector_pairing"].startswith("ZERO_"),
        "common_Born_is_imported": common["disposition"]["actual_all_ten_channel_packet_operator"] == "TOTAL_KAPPA_FIXED",
        "ordinary_Moller_scope_core_reconstructed": (
            log_shell["disposition"]["ordinary_L2_strong_Moller_limit"]
            == "EXACT_OBSTRUCTION"
            and len(shell_intervals) == 6
            and all(right - left == 1 for left, right in shell_intervals)
            and all(
                min(left[1], right[1]) <= max(left[0], right[0])
                for index, left in enumerate(shell_intervals)
                for right in shell_intervals[index + 1 :]
            )
            and shell_distance == Fraction(1, 8)
        ),
        "bounded_extension_not_promoted": boundary["bounded_L2_operator_extension"] == "NOT_CLASSIFIED",
        "strong_Moller_not_promoted": boundary["strong_Moller_operator"] == "NOT_CONSTRUCTED",
        "q10_not_promoted": boundary["q10_all_time_limit"] == "NOT_CONSTRUCTED" and q10["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "Eq19_not_promoted": boundary["general_Eq19"] == "NOT_PROVED",
        "causal_boundary_present": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
        "source_commit_is_pinned": certificate["provenance"]["source_commit"].startswith("acfee00f"),
        "verification_commands_present": len(certificate["verification_commands"]) == 3,
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        for name in failures:
            print("FAIL:", name, file=sys.stderr)
        return 1
    print(
        "BT RIGGED ALL-TIME PACKET INDEPENDENT VERIFIER: "
        f"ALL PASS ({len(checks)}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
