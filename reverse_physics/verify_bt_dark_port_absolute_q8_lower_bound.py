#!/usr/bin/env python3
"""Independent exact verifier for the BT dark-port absolute-q8 theorem."""
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
    ROOT, "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_DARK_PORT_ABSOLUTE_Q8_LOWER_BOUND_V1.json"
)
SCHEMA = os.path.join(
    ROOT, "reverse_physics/schema/"
    "reverse-physics-bt-dark-port-absolute-q8-lower-bound-v1.schema.json"
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


def parse(value):
    return Fraction(value)


def receipt_ok(row):
    value = parse(row["exact"])
    canonical = f"{value.numerator}/{value.denominator}".encode()
    return hashlib.sha256(canonical).hexdigest() == row["canonical_sha256"]


def root_interval(value, digits=36):
    scale = 10**digits
    low = isqrt(value.numerator * scale * scale // value.denominator)
    while Fraction((low + 1) ** 2, scale**2) <= value:
        low += 1
    while Fraction(low**2, scale**2) > value:
        low -= 1
    return Fraction(low, scale), Fraction(low + 1, scale)


def alternating_sine(value, final_index):
    term = value
    total = term
    for index in range(final_index):
        term *= -value * value / ((2 * index + 2) * (2 * index + 3))
        total += term
    return total


def sine_gap_interval(radicand):
    low, high = root_interval(radicand)
    gap_low = Fraction(2, 5) * (low - 3)
    gap_high = Fraction(2, 5) * (high - 3)
    return alternating_sine(gap_low, 9), alternating_sine(gap_high, 8)


def H_partial(value, final_index):
    # Deliberately use the term definition, at two orders beyond the producer.
    return sum(
        Fraction((-1) ** (n + 1)) * value**n
        / (2 * n * (2 * n + 1) * factorial(2 * n))
        for n in range(1, final_index + 1)
    )


def H_interval(value):
    return H_partial(value, 10), H_partial(value, 9)


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


def probability_q8(x2, x4, x6, effect):
    return (
        real_effect(x2, effect, x6)
        + real_effect(x4, effect, x4)
        + real_effect(x6, effect, x2)
    )


def squared(value):
    return value[0] ** 2 + value[1] ** 2


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

    witness = certificate["exact_two_angle_witness"]
    stored_tree_low = parse(witness["tree_contrast_lower_receipt"]["exact"])
    stored_tree_high = parse(witness["tree_contrast_upper_receipt"]["exact"])
    stored_loop_low = parse(witness["loop_contrast_lower_receipt"]["exact"])
    stored_loop_high = parse(witness["loop_contrast_upper_receipt"]["exact"])

    s0 = sine_gap_interval(Fraction(17))
    st = sine_gap_interval(Fraction(61, 5))
    su = sine_gap_interval(Fraction(109, 5))
    tree_low = 10 * (
        st[0] / Fraction(64, 125)
        + su[0] / Fraction(256, 125)
        - 2 * s0[1] / Fraction(32, 25)
    )
    tree_high = 10 * (
        st[1] / Fraction(64, 125)
        + su[1] / Fraction(256, 125)
        - 2 * s0[0] / Fraction(32, 25)
    )

    h0 = H_interval(Fraction(32, 25))
    hm = H_interval(Fraction(64, 125))
    hp = H_interval(Fraction(256, 125))
    loop_low = 2 * (2 * h0[0] - hm[1] - hp[1])
    loop_high = 2 * (2 * h0[1] - hm[0] - hp[0])

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
    leading_killed = True
    x6_absent = True
    norm_identity = True
    cauchy_grid = True
    for lead, a1, a2, b1, b2 in itertools.product(
        leads, values, values, values[:2], values[2:]
    ):
        x2 = [lead, lead]
        x4 = [a1, a2]
        x6 = [b1, b2]
        q8 = probability_q8(x2, x4, x6, pminus)
        expected = (squared((a2[0] - a1[0], a2[1] - a1[1]))) / 2
        leading_killed &= apply(pminus, x2) == [(Fraction(0), Fraction(0))] * 2
        x6_absent &= q8 == real_effect(x4, pminus, x4)
        norm_identity &= q8 == expected
        q4_bar = squared(lead)
        delta = (a2[0] - a1[0], a2[1] - a1[1])
        delta_R = 2 * mul(conj(lead), delta)[0] / q4_bar
        cauchy_grid &= q8 / q4_bar >= delta_R**2 / 8

    simple_R = Fraction(5, 24) / Fraction(22, 7) ** 2 / 220
    simple_q8 = simple_R**2 / 8
    absolute_receipt = certificate["absolute_q8_bound"]["exact_rational_lower"]
    finite = certificate["finite_volume_complete_contrast"]
    ledger = certificate["dark_port_ledger"]
    inequality = certificate["q6_to_q8_inequality"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]

    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_DARK_PORT_ABSOLUTE_Q8_LOWER_BOUND_V1",
        "input_hashes_recomputed": hashes_ok,
        "six_predecessor_pass_flags_rechecked": len(predecessors) == 6 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_matches_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("dark-port-absolute-q8-lower-bound"),
        "lattice_angles_recorded": witness["angles"] == ["0", "3/5"] and witness["duration"] == "kappa*T=1",
        "tree_receipt_hashes_rechecked": receipt_ok(witness["tree_contrast_lower_receipt"]) and receipt_ok(witness["tree_contrast_upper_receipt"]),
        "independent_tree_interval_is_nested": stored_tree_low <= tree_low < tree_high <= stored_tree_high,
        "independent_tree_lower_exceeds_one_sixteenth": tree_low > Fraction(1, 16),
        "loop_receipt_hashes_rechecked": receipt_ok(witness["loop_contrast_lower_receipt"]) and receipt_ok(witness["loop_contrast_upper_receipt"]),
        "independent_loop_interval_is_nested": stored_loop_low <= loop_low < loop_high <= stored_loop_high,
        "independent_loop_lower_exceeds_one_over_220": loop_low > Fraction(1, 220),
        "loop_log_cancellation_identity": Fraction(64, 125) * Fraction(256, 125) / Fraction(32, 25) ** 2 == Fraction(16, 25),
        "loop_scale_scheme_cancellation_recorded": witness["scale_and_scheme_dependence"] == "CANCELS from DeltaB between the two angles",
        "dark_projector_kills_all_test_leads": leading_killed,
        "direct_q8_convolution_removes_all_test_X6": x6_absent,
        "direct_q8_convolution_is_half_difference_norm": norm_identity,
        "exact_cauchy_grid_satisfies_bound": cauchy_grid,
        "dark_probability_order_recorded": ledger["absolute_probability"] == "q_dark(lambda)=lambda^8*Q8_dark+O(lambda^10)",
        "X2_X6_absence_recorded": ledger["X2_X6_disposition"] == "ABSENT because <X2,P_minus X6>=<P_minus X2,X6>=0",
        "q6_contrast_relation_recorded": inequality["contrast_relation"] == "Re<x2,X4(c2)-X4(c1)>=q4_bar*DeltaR6/2",
        "Cauchy_bound_recorded": inequality["dark_lower_bound"] == "Q8_dark/q4_bar>=DeltaR6^2/8",
        "finite_volume_formula_recorded": finite["formula"] == "DeltaR6=2*sqrt(2)*DeltaW/(3*N_s)+5*DeltaB/(24*pi^2)",
        "tree_and_loop_signs_are_separate": finite["tree_sign"] == "STRICTLY_POSITIVE_FOR_EVERY_N_s_GT_ZERO" and finite["loop_sign"] == "STRICTLY_POSITIVE_AND_VOLUME_INDEPENDENT",
        "simple_q6_lower_recomputed": simple_R == Fraction(49, 511104) and finite["relative_q6_lower_bound"] == "DeltaR6>49/511104",
        "absolute_receipt_hash_rechecked": receipt_ok(absolute_receipt),
        "absolute_lower_recomputed": parse(absolute_receipt["exact"]) == simple_q8 == Fraction(2401, 2089818390528),
        "absolute_lower_exceeds_billionth": simple_q8 > Fraction(1, 1_000_000_000),
        "dark_absolute_status_computed": disposition["absolute_dark_port_q8_probability"] == "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
        "recorded_and_bright_remain_open": disposition["absolute_recorded_q8_probability"] == "NOT_COMPUTED" and disposition["absolute_bright_port_q8_probability"] == "NOT_COMPUTED",
        "compact_packet_remains_open": disposition["compact_continuum_packet_extension"] == "NOT_CONSTRUCTED",
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
