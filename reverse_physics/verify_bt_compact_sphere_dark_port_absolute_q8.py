#!/usr/bin/env python3
"""Independent exact verifier for compact-sphere BT dark-port q8."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from fractions import Fraction
from math import factorial, isqrt

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-sphere-dark-port-absolute-q8-v1.schema.json",
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


def parse_receipt(row):
    value = Fraction(row["exact"])
    canonical = f"{value.numerator}/{value.denominator}".encode()
    valid = hashlib.sha256(canonical).hexdigest() == row["canonical_sha256"]
    return value, valid


def parse_interval(row):
    lower, lower_ok = parse_receipt(row["lower"])
    upper, upper_ok = parse_receipt(row["upper"])
    return lower, upper, lower_ok and upper_ok


def root_interval(value, digits=36):
    scale = 10**digits
    floor = isqrt(value.numerator * scale * scale // value.denominator)
    while Fraction((floor + 1) ** 2, scale * scale) <= value:
        floor += 1
    while Fraction(floor**2, scale * scale) > value:
        floor -= 1
    return Fraction(floor, scale), Fraction(floor + 1, scale)


def sin_sum(value, final_index):
    term = value
    total = term
    for index in range(final_index):
        term *= -value * value / ((2 * index + 2) * (2 * index + 3))
        total += term
    return total


def cos_sum(value, final_index):
    term = Fraction(1)
    total = term
    for index in range(final_index):
        term *= -value * value / ((2 * index + 1) * (2 * index + 2))
        total += term
    return total


def independent_c_intervals(delta):
    sin_lower, sin_upper = sin_sum(delta, 5), sin_sum(delta, 4)
    cos_lower, cos_upper = cos_sum(delta, 5), cos_sum(delta, 4)
    c0 = -sin_upper, sin_upper
    c1 = (
        Fraction(3, 5) * cos_lower - Fraction(4, 5) * sin_upper,
        Fraction(3, 5) * cos_upper + Fraction(4, 5) * sin_upper,
    )
    return c0, c1


def independent_W_interval(c_lower, c_upper):
    yt = Fraction(17) - 8 * c_upper, Fraction(17) - 8 * c_lower
    yu = Fraction(17) + 8 * c_lower, Fraction(17) + 8 * c_upper
    rt = root_interval(yt[0])[0], root_interval(yt[1])[1]
    ru = root_interval(yu[0])[0], root_interval(yu[1])[1]
    at = Fraction(2, 5) * (rt[0] - 3), Fraction(2, 5) * (rt[1] - 3)
    au = Fraction(2, 5) * (ru[0] - 3), Fraction(2, 5) * (ru[1] - 3)
    st = sin_sum(at[0], 9), sin_sum(at[1], 8)
    su = sin_sum(au[0], 9), sin_sum(au[1], 8)
    dt = Fraction(32, 25) * (1 - c_upper), Fraction(32, 25) * (1 - c_lower)
    du = Fraction(32, 25) * (1 + c_lower), Fraction(32, 25) * (1 + c_upper)
    return (
        10 * st[0] / dt[1] + 10 * su[0] / du[1],
        10 * st[1] / dt[0] + 10 * su[1] / du[0],
    )


def H_coefficient(index):
    return Fraction(
        (-1) ** (index + 1),
        2 * index * (2 * index + 1) * factorial(2 * index),
    )


def independent_H_interval(y_lower, y_upper):
    lower = Fraction(0)
    for index in range(1, 13):
        coefficient = H_coefficient(index)
        lower += coefficient * (
            y_lower**index if coefficient > 0 else y_upper**index
        )
    upper = Fraction(0)
    for index in range(1, 12):
        coefficient = H_coefficient(index)
        upper += coefficient * (
            y_upper**index if coefficient > 0 else y_lower**index
        )
    return lower, upper


def independent_H_pair(c_lower, c_upper):
    yt = (
        Fraction(32, 25) * (1 - c_upper),
        Fraction(32, 25) * (1 - c_lower),
    )
    yu = (
        Fraction(32, 25) * (1 + c_lower),
        Fraction(32, 25) * (1 + c_upper),
    )
    ht = independent_H_interval(*yt)
    hu = independent_H_interval(*yu)
    return ht[0] + hu[0], ht[1] + hu[1]


def add(left, right):
    return left[0] + right[0], left[1] + right[1]


def mul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def conj(value):
    return value[0], -value[1]


def inner(left, right):
    result = (Fraction(0), Fraction(0))
    for lhs, rhs in zip(left, right):
        result = add(result, mul(conj(lhs), rhs))
    return result


def apply(effect, vector):
    output = []
    for row in effect:
        value = (Fraction(0), Fraction(0))
        for coefficient, entry in zip(row, vector):
            value = add(value, (coefficient * entry[0], coefficient * entry[1]))
        output.append(value)
    return output


def real_effect(left, effect, right):
    return inner(left, apply(effect, right))[0]


def squared(value):
    return value[0] ** 2 + value[1] ** 2


def direct_packet_grid():
    half = Fraction(1, 2)
    pminus = [[half, -half], [-half, half]]
    leads = [
        (Fraction(1), Fraction(0)),
        (Fraction(2, 3), Fraction(-1, 5)),
        (Fraction(-7, 6), Fraction(4, 9)),
    ]
    values = [
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(2)),
        (Fraction(-3), Fraction(1)),
        (Fraction(7, 4), Fraction(-2, 3)),
    ]
    killed = norm_identity = cauchy = True
    for lead, a0, a1 in itertools.product(leads, values, values):
        x2 = [lead, lead]
        x4 = [a0, a1]
        killed &= apply(pminus, x2) == [(Fraction(0), Fraction(0))] * 2
        q8 = real_effect(x4, pminus, x4)
        difference = (a1[0] - a0[0], a1[1] - a0[1])
        norm_identity &= q8 == squared(difference) / 2
        q4_bar = squared(lead)
        delta_R = 2 * mul(conj(lead), difference)[0] / q4_bar
        cauchy &= q8 / q4_bar >= delta_R**2 / 8
    return killed, norm_identity, cauchy


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs}
    predecessors = [
        value for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )
    fixed_sphere = next(
        row for row in predecessors
        if row["certificate"].endswith("FIXED_P_TWO_SPHERE_PACKET_DETECTOR_V1")
    )
    compact_tree = next(
        row for row in predecessors
        if row["certificate"].endswith("TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1")
    )
    finite_loop = next(
        row for row in predecessors
        if row["certificate"].endswith("FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1")
    )

    geometry = certificate["invariant_packet_geometry"]
    margins = certificate["exact_equatorial_margins"]
    thickening = certificate["compact_thickening"]
    absolute = certificate["absolute_dark_port_coefficient"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]

    stored_c0 = parse_interval(geometry["c_interval_0"])
    stored_c1 = parse_interval(geometry["c_interval_1"])
    stored_w0 = parse_interval(margins["W_angle_part_0"])
    stored_w1 = parse_interval(margins["W_angle_part_1"])
    stored_dw = parse_interval(margins["tree_contrast"])
    stored_h0 = parse_interval(margins["H_pair_0"])
    stored_h1 = parse_interval(margins["H_pair_1"])
    stored_db = parse_interval(margins["loop_contrast"])
    all_receipts_ok = all(
        row[2]
        for row in (stored_c0, stored_c1, stored_w0, stored_w1, stored_dw, stored_h0, stored_h1, stored_db)
    )

    delta = Fraction(1, 10_000)
    c0, c1 = independent_c_intervals(delta)
    w0, w1 = independent_W_interval(*c0), independent_W_interval(*c1)
    dw = w1[0] - w0[1], w1[1] - w0[0]
    h0, h1 = independent_H_pair(*c0), independent_H_pair(*c1)
    db = 2 * (h0[0] - h1[1]), 2 * (h0[1] - h1[0])

    c_nested = (
        stored_c0[0] <= c0[0] < c0[1] <= stored_c0[1]
        and stored_c1[0] <= c1[0] < c1[1] <= stored_c1[1]
    )
    W_nested = (
        stored_w0[0] <= w0[0] < w0[1] <= stored_w0[1]
        and stored_w1[0] <= w1[0] < w1[1] <= stored_w1[1]
        and stored_dw[0] <= dw[0] < dw[1] <= stored_dw[1]
    )
    H_nested = (
        stored_h0[0] <= h0[0] < h0[1] <= stored_h0[1]
        and stored_h1[0] <= h1[0] < h1[1] <= stored_h1[1]
        and stored_db[0] <= db[0] < db[1] <= stored_db[1]
    )

    killed, norm_identity, cauchy_grid = direct_packet_grid()
    delta_R = Fraction(5, 24) / Fraction(22, 7) ** 2 / 230
    dark_lower = delta_R**2 / 8
    stored_absolute, absolute_hash_ok = parse_receipt(absolute["exact_rational_lower"])

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1",
        "input_hashes_recomputed": hashes_ok,
        "six_predecessor_pass_flags_rechecked": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("compact-sphere-dark-port-absolute-q8"),
        "all_interval_receipt_hashes_rechecked": all_receipts_ok,
        "independent_c_intervals_are_nested": c_nested,
        "independent_bins_are_disjoint": c0[1] < c1[0],
        "independent_W_intervals_are_nested": W_nested,
        "independent_tree_margin_exceeds_one_twentieth": dw[0] > Fraction(1, 20),
        "independent_H_intervals_are_nested": H_nested,
        "independent_loop_margin_exceeds_one_over_225": db[0] > Fraction(1, 225),
        "fixed_sphere_measure_is_imported": fixed_sphere["fixed_P_shell"]["measure"] == "dPhi2=C(P^2)*dOmega with dOmega=d n_x dphi; C cancels from every norm ratio",
        "geometry_uses_invariant_measure_not_dc": geometry["measure"] == "dOmega=dn_x*dphi" and "dc" not in geometry["measure"],
        "equal_cell_measure_formula_recorded": geometry["positive_measure_cells"].endswith("measure(B_j)=4*epsilon*delta for every sufficiently small epsilon>0"),
        "compact_tree_kernel_formula_is_imported": compact_tree["compact_tree_cross_functional"]["time_kernel"].startswith("beta_A,T=F_T(delta_A)/D_A"),
        "compact_tree_hard_denominator_is_imported": compact_tree["compact_tree_cross_functional"]["compact_denominator_hypothesis"] == "D_A>=d0>0 on the declared packet support",
        "finite_loop_compact_status_is_imported": finite_loop["compact_packet"]["status"] == "FINITE_TIME_COMPACT_ACTIVE_PACKET_AFFILIATED",
        "strict_tree_continuity_slack_exists": dw[0] > Fraction(1, 40),
        "strict_loop_continuity_slack_exists": db[0] > Fraction(1, 230),
        "tree_continuity_argument_recorded": "continuous" in thickening["tree_kernel_input"] and "entire" in thickening["tree_kernel_input"] and "nonzero" in thickening["tree_kernel_input"],
        "loop_continuity_argument_recorded": "continuous" in thickening["loop_kernel_input"] and "nonzero" in thickening["loop_kernel_input"],
        "compact_uniformity_argument_recorded": "compact" in thickening["uniformity_argument"] and "one common open neighborhood" in thickening["uniformity_argument"],
        "normalized_positive_packet_choice_recorded": "nonnegative normalized compact" in thickening["packet_choice"],
        "continuity_radius_is_not_fabricated": thickening["radius_status"] == "EXISTS_BUT_NOT_NUMERICALLY_COMPUTED",
        "point_kernel_and_packet_functional_are_distinguished": thickening["pointwise_tree_kernel_contrast_after_thickening"].startswith("DeltaW_kernel>1/40") and thickening["packet_tree_functional_contrast"].startswith("DeltaC_tree>0;") and "not bounded below by 1/40" in thickening["packet_tree_functional_contrast"],
        "thickened_loop_bound_recorded": thickening["loop_contrast_after_thickening"] == "DeltaB_packet>1/230",
        "complete_packet_contrast_formula_recorded": thickening["complete_contrast"] == "DeltaR6=(2*sqrt(2)/3)*DeltaC_tree+5*DeltaB_packet/(24*pi^2)",
        "direct_dark_projector_kills_equal_leads": killed,
        "direct_dark_norm_is_half_packet_difference": norm_identity,
        "direct_Cauchy_grid_satisfies_bound": cauchy_grid,
        "relative_q6_lower_recomputed": delta_R == Fraction(49, 534336) and thickening["complete_lower_bound"] == "DeltaR6>49/534336",
        "absolute_receipt_hash_rechecked": absolute_hash_ok,
        "absolute_lower_recomputed": stored_absolute == dark_lower == Fraction(2401, 2284119687168),
        "absolute_lower_exceeds_billionth": dark_lower > Fraction(1, 1_000_000_000),
        "absolute_dark_status_computed": disposition["absolute_dark_port_q8_probability"] == "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
        "fixed_P_bandwidth_remains_open": disposition["finite_total_momentum_or_invariant_mass_bandwidth"] == "NOT_CONSTRUCTED",
        "local_apparatus_remains_open": disposition["local_detector_Hamiltonian_for_these_exact_packets"] == "NOT_CONSTRUCTED",
        "recorded_and_bright_remain_open": disposition["recorded_or_bright_port_absolute_q8"] == "NOT_COMPUTED",
        "Eq19_remains_open": disposition["general_Eq19"] == "NOT_PROVED_AND_NOT_USED",
        "gravity_remains_open": disposition["gravity_or_metric_BV_BRST_transfer"] == "NOT_CONSTRUCTED",
        "Lorentzian_boundary_present": any("LORENTZIAN-CAUSAL" in row for row in scope),
        "literature_priority_forbidden": "literature priority" in scope,
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
