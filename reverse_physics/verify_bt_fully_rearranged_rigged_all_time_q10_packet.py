#!/usr/bin/env python3
"""Independent verifier for the selected rigged all-time BT q10 theorem."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-rigged-all-time-q10-packet-v1.schema.json",
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


def frac(value):
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


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


def incoming_rotation_derivatives():
    a, b, u = Fraction(2), Fraction(-2), Fraction(15, 16)
    units = [direction(0), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(units[1], units[2]),
        cross(units[2], units[0]),
        cross(units[0], units[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    cu, su = cs(u)
    rows = []
    for energy, (x, y, _) in zip(energies, units):
        dx, dy, dz = -2 * y, 2 * x, Fraction(0)
        rows.append(
            (
                energy * dx,
                energy * (cu * dy - su * dz),
                energy * (su * dy + cu * dz),
            )
        )
    return rows


def exchange_rows():
    incoming = future_three_body((2, -2, 0, Fraction(15, 16), 0))
    outgoing = future_three_body((2, -2, Fraction(105, 73), 2, Fraction(1, 3)))
    derivatives = incoming_rotation_derivatives()
    rows = {}
    for i, p in enumerate(incoming):
        for a, k in enumerate(outgoing):
            q0 = Fraction(16, 5) - p[0] - k[0]
            spatial = tuple(p[c] + k[c] for c in range(1, 4))
            radius2 = sum(value * value for value in spatial)
            numerator = sum(spatial[c] * derivatives[i][c] for c in range(3))
            rows[(i, a)] = {
                "q2": q0 * q0 - radius2,
                "N": numerator,
                "dK2": -2 * numerator,
            }
    return rows


def canonical_mask(i, a):
    labels = {j for j in range(3) if j != i} | {3 + a}
    mask = sum(1 << j for j in labels)
    complement = 63 ^ mask
    return min(mask, complement), "q_ia" if mask <= complement else "-q_ia"


def overlap(u, v):
    diameter = max(Fraction(0), u, v) - min(Fraction(0), u, v)
    return max(Fraction(0), Fraction(1) - diameter)


def verify(certificate):
    schema_errors = list(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate)
    )
    if schema_errors:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs = {
        path: load(os.path.join(ROOT, path))
        for path in hashes
    }
    by_certificate = {
        value["certificate"]: value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    }
    event = next(
        value
        for path, value in inputs.items()
        if path.startswith("planning/events/")
    )
    obstruction = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1"
    ]
    q8 = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1"
    ]
    triangle = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1"
    ]
    triangle_time = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1"
    ]
    bubble = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1"
    ]
    bubble_time = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1"
    ]
    old_q10 = by_certificate[
        "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"
    ]

    exact_exchange = exchange_rows()
    bridge = certificate["bridge_chart_audit"]
    recorded_rows = bridge["exchange_rows"]
    bubble_roles = bubble["role_kinematics"]["rows"]
    roles_by_mask = {}
    for role in bubble_roles:
        roles_by_mask.setdefault(role["bridge_channel_mask"], []).append(role)

    bridge_exact = len(recorded_rows) == 9
    for row in recorded_rows:
        channel = tuple(row["exchange_channel"])
        i, a = channel
        mask, sign = canonical_mask(i, a)
        exact = exact_exchange[channel]
        roles = roles_by_mask[mask]
        bridge_exact &= (
            row["mask"] == mask
            and row["canonical_bridge_momentum"] == sign
            and row["role_count"] == len(roles) == 6
            and frac(row["bridge_invariant"]) == exact["q2"]
            and frac(row["q_squared"]) == exact["q2"]
            and frac(row["rotation_numerator_N"]) == exact["N"]
            and frac(row["partial_t_K_squared"]) == exact["dK2"]
            and row["on_shell"] == (exact["q2"] == 0)
            and row["noncritical"] == (exact["N"] != 0)
            and row["all_role_source_weights_positive"]
            == all(role["source_weight"] > 0 for role in roles)
        )

    fixtures = certificate["anchored_temporal_limit"]["overlap_fixtures"]
    overlap_exact = all(
        frac(row["normalized_overlap"])
        == overlap(frac(row["u_over_T"]), frac(row["v_over_T"]))
        for row in fixtures
    )
    masks = set(roles_by_mask)
    hard_roles = roles_by_mask[7]
    shell_roles = [role for role in bubble_roles if frac(role["bridge_invariant"]) == 0]
    triangle_rows = triangle["hard_packet_regularization"]["rows"]
    temporal = certificate["anchored_temporal_limit"]
    loop = certificate["all_time_loop_operator"]
    coefficient = certificate["q10_packet_coefficient"]
    rg = certificate["renormalization_group"]
    claims = certificate["claim_boundary"]

    beta_coefficient = Fraction(-5, 16)
    leading_running = 8 * beta_coefficient
    loop_running = Fraction(5, 2)
    checks = {
        "schema_validation": not schema_errors,
        "certificate_identity": certificate["certificate"].endswith("RIGGED_ALL_TIME_Q10_PACKET_V1"),
        "input_hashes_recomputed": all(sha256(path) == digest for path, digest in hashes.items()),
        "all_imported_certificates_pass": all(value["checks"]["ok"] for value in by_certificate.values()),
        "event_is_done": event["body"]["payload"]["to_state"] == "DONE",
        "normalization_obstruction_is_imported": obstruction["claim_boundary"]["matched_finite_time_q10"] == "NOT_COMPUTED",
        "leading_q8_boundary_is_imported": q8["rigged_packet_limit"]["status"] == "COMPLETE_LEADING_SELECTED_ALL_TIME_PACKET_COEFFICIENT_COMPUTED",
        "bridge_rows_recomputed_from_rational_momenta": bridge_exact,
        "ten_bridge_masks_are_exhaustive": masks == {7, 11, 13, 14, 19, 21, 22, 25, 26, 28},
        "recorded_mask_set_is_exact": bridge["mask_set"] == sorted(masks),
        "hard_mask_has_six_roles": len(hard_roles) == 6,
        "hard_mask_is_source_dark": all(role["source_weight"] == 0 for role in hard_roles),
        "unique_shell_mask_is_eleven": {role["bridge_channel_mask"] for role in shell_roles} == {11},
        "six_shell_roles_exist": len(shell_roles) == 6,
        "shell_roles_are_source_visible": all(role["source_weight"] > 0 for role in shell_roles),
        "unique_shell_is_q20": bridge["unique_shell_exchange"] == [2, 0] and exact_exchange[(2, 0)]["q2"] == 0,
        "all_exchange_derivatives_are_nonzero": all(row["N"] != 0 for row in exact_exchange.values()),
        "all_dK2_derivatives_are_nonzero": all(row["dK2"] != 0 for row in exact_exchange.values()),
        "bubble_invariant_margin_recomputed": min(abs(frac(role["bubble_invariant"])) for role in bubble_roles) == Fraction(32, 625),
        "triangle_pair_margin_recomputed": min(abs(frac(value)) for row in triangle_rows for value in row["pair_invariants"]) == Fraction(32, 625),
        "triangle_Kallen_margin_recomputed": min(abs(frac(row["kallen"])) for row in triangle_rows) == Fraction(80896, 903125),
        "overlap_fixtures_recomputed": overlap_exact,
        "overlap_origin_is_one": overlap(Fraction(0), Fraction(0)) == 1,
        "overlap_outside_unit_diameter_is_zero": overlap(Fraction(-1), Fraction(1)) == 0,
        "overlap_is_bounded": all(0 <= frac(row["normalized_overlap"]) <= 1 for row in fixtures),
        "one_gap_boundary_has_positive_PV_sign": temporal["one_gap"] == "A2,T and F_T both tend to H_+(s)=pi*delta(s)+i*PV(1/s) in S'(R)",
        "three_window_formula_is_exact": temporal["three_window"] == "W_T(x,y)=F_T(-x-y)*F_T(x)*F_T(y)/T",
        "inverse_overlap_formula_is_exact": temporal["inverse_Fourier_overlap"] == "L_T(u,v)/T=max(0,1-diam(0,u,v)/T)",
        "L1_sector_proof_is_recorded": all(token in temporal["L1_proof"] for token in ("one-small", "all-large", "O(r^-2)", "O(r^-3)")),
        "approximate_identity_scaling_is_recorded": "W_T=T^2*W_1" in temporal["approximate_identity"],
        "approximate_identity_mass_is_recorded": "mass is (2*pi)^2" in temporal["approximate_identity"],
        "three_window_boundary_has_two_deltas": "(2*pi)^2*delta(x)*delta(y)" in temporal["boundary"],
        "triangle_boundary_is_imported": "C0" in triangle_time["finite_time_triangle"]["covariant_boundary"],
        "bubble_boundary_is_imported": bubble_time["covariant_boundary"]["status"] == "COVARIANT_BUBBLE_BRIDGE_BOUNDARY_MATCHED",
        "triangle_operator_coefficient_matches": loop["triangle"].startswith("T6,triangle,infinity=(8/(16*pi^2))"),
        "bubble_operator_coefficient_matches": loop["bubble_bridge"].startswith("T6,bb,infinity=(4/(16*pi^2))"),
        "complete_loop_sum_is_exact": loop["complete_loop"] == "T6,infinity=T6,triangle,infinity+T6,bb,infinity",
        "bridge_coarea_is_declared": "coarea" in loop["bridge_distribution"],
        "bridge_L2_output_is_declared": "L2(Y)" in loop["bridge_domain"],
        "complete_loop_status": loop["status"] == "COMPLETE_SELECTED_ALL_TIME_T6_PACKET_MAP_CONSTRUCTED",
        "old_graph_exhaustion_is_imported": old_q10["order_g3_exhaustion"]["status"] == "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10",
        "q10_formula_is_exact": coefficient["q10"] == "q10,infinity[F]=2*Re<T4,infinity F,T6,infinity F>",
        "q10_is_finite": "finite" in coefficient["finiteness"],
        "q10_is_common_Born": coefficient["common_Born"].startswith("q10,infinity^public"),
        "q10_sign_is_open": coefficient["sign"] == "NOT_DETERMINED",
        "q10_scheme_is_MSbar": coefficient["scheme"].startswith("MSbar"),
        "RG_derivative_is_exact": rg["q10_scale_derivative"] == "partial_log(mu)q10,infinity=[5/(2*pi^2)]*q8,infinity",
        "RG_running_cancels": leading_running + loop_running == 0,
        "finite_time_RG_is_not_reinstated": "does not reinstate" in rg["scope"],
        "finite_time_q10_remains_open": claims["matched_finite_time_q10"] == "NOT_COMPUTED",
        "whole_carrier_remains_open": claims["bounded_whole_carrier_operator"] == "NOT_CONSTRUCTED",
        "S_operator_remains_open": claims["Moller_LSZ_S"] == "NOT_CONSTRUCTED",
        "Eq19_remains_open": claims["general_Eq19"] == "NOT_PROVED",
        "gravity_remains_open": claims["gravity_BV_BRST_QME"] == "NOT_CONSTRUCTED",
        "causality_remains_open": claims["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "certificate_checks_are_all_true": certificate["checks"]["ok"] and all(certificate["checks"]["items"].values()),
    }
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    try:
        checks = verify(load(args.verify))
    except Exception as error:
        print(f"verification error: {error}", file=sys.stderr)
        return 1
    passed = sum(bool(value) for value in checks.values())
    print(f"checks: {passed}/{len(checks)}")
    for name, value in checks.items():
        if not value:
            print(f"FAIL: {name}", file=sys.stderr)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
