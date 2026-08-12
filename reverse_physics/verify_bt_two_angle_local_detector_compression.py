#!/usr/bin/env python3
"""Fraction verifier for BT local two-angle compression and leakage no-go."""
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
    "REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-local-detector-compression-v1.schema.json",
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


ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))


def add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def neg(value):
    return (-value[0], -value[1])


def mul(left, right):
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def inv(value):
    denominator = value[0] * value[0] + value[1] * value[1]
    return (value[0] / denominator, -value[1] / denominator)


def power(value, exponent):
    result = ONE
    for _ in range(exponent):
        result = mul(result, value)
    return result


def matrix_rank(rows):
    value = [[entry for entry in row] for row in rows]
    rank = 0
    columns = len(value[0]) if value else 0
    for column in range(columns):
        pivot = next((row for row in range(rank, len(value)) if value[row][column] != ZERO), None)
        if pivot is None:
            continue
        value[rank], value[pivot] = value[pivot], value[rank]
        pivot_inverse = inv(value[rank][column])
        value[rank] = [mul(pivot_inverse, entry) for entry in value[rank]]
        for row in range(len(value)):
            if row == rank:
                continue
            coefficient = value[row][column]
            if coefficient != ZERO:
                value[row] = [
                    add(entry, neg(mul(coefficient, pivot_entry)))
                    for entry, pivot_entry in zip(value[row], value[rank])
                ]
        rank += 1
        if rank == len(value):
            break
    return rank


def parse_vector(row):
    return [Fraction(value) for value in row]


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    hashes_ok = all(sha256(row["path"]) == row["sha256"] for row in inputs)
    imported = {
        row["path"]: load(os.path.join(ROOT, row["path"])) for row in inputs
    }
    predecessors = [
        value
        for path, value in imported.items()
        if path.startswith("reverse_physics/certificates/")
    ]
    event = next(
        value for path, value in imported.items() if path.startswith("planning/events/")
    )
    apparatus = next(
        row for row in predecessors if row["certificate"].endswith("TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1")
    )
    q6 = next(
        row for row in predecessors if row["certificate"].endswith("TWO_ANGLE_COHERENT_Q6_DETECTOR_V1")
    )
    continuous = next(
        row for row in predecessors if row["certificate"].endswith("CONTINUOUS_ANGLE_Q6_FAMILY_V1")
    )

    outgoing = q6["rational_two_mode_fixture"]["outgoing"]
    pairs = [
        (parse_vector(row["k1"]), parse_vector(row["k2"])) for row in outgoing
    ]
    totals = [
        [left[index] + right[index] for index in range(4)] for left, right in pairs
    ]
    derivative = [-left[2] * right[2] for left, right in pairs]
    contrast = [Fraction(1) - Fraction(625, 72) * row for row in derivative]

    phases = [
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
        (Fraction(-1), Fraction(0)),
        (Fraction(3, 5), Fraction(4, 5)),
    ]
    phase_synthesis = True
    # Remove the common 1/sqrt(2): alpha'=(1-zbar)/2,
    # beta'=(1+zbar)/2 must give weights (1,-zbar).
    for z in phases:
        zbar = (z[0], -z[1])
        alpha = ((Fraction(1) - zbar[0]) / 2, -zbar[1] / 2)
        beta = ((Fraction(1) + zbar[0]) / 2, zbar[1] / 2)
        weight_one = add(alpha, beta)
        weight_two = add(alpha, neg(beta))
        phase_synthesis &= weight_one == ONE and weight_two == neg(zbar)

    vandermonde = []
    all_vandermonde = True
    for degree in range(7):
        points = []
        for t_integer in range(2 * degree + 1):
            t = Fraction(t_integer)
            denominator = 1 + t * t
            points.append(((1 - t * t) / denominator, 2 * t / denominator))
        rows = [[power(point, exponent) for exponent in range(2 * degree + 1)] for point in points]
        rank = matrix_rank(rows)
        vandermonde.append((degree, len(points), rank))
        all_vandermonde &= rank == len(points)

    matrix_elements = certificate["rational_pair_matrix_elements"]
    synthesis = certificate["phase_quadrature_synthesis"]
    compression = certificate["selected_sector_compression"]
    no_go = certificate["continuum_locality_no_go"]
    leakage = certificate["leakage_boundary"]
    disposition = certificate["disposition"]
    scope = certificate["does_not_establish"]
    recorded_vandermonde = [
        (row["degree"], row["point_count"], row["rank"])
        for row in no_go["vandermonde_witnesses"]
    ]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1",
        "input_hashes_recomputed": hashes_ok,
        "three_predecessor_pass_flags_rechecked": len(predecessors) == 3 and all(row["checks"]["ok"] for row in predecessors),
        "obstructed_event_matches_work_item": event["body"]["payload"]["to_state"] == "OBSTRUCTED" and event["body"]["payload"]["target"].endswith("two-angle-local-detector-compression"),
        "pair_momenta_reconstructed": len(pairs) == 2,
        "common_total_momentum_recomputed": totals == [[Fraction(2), Fraction(-6, 5), Fraction(0), Fraction(0)]] * 2,
        "derivative_weights_recomputed": derivative == [Fraction(0), Fraction(144, 625)],
        "contrast_weights_recomputed": contrast == [Fraction(1), Fraction(-1)],
        "matrix_element_claims_match": matrix_elements["normalized_derivative_weights"] == ["0", "144/625"] and matrix_elements["D_minus_weights"] == ["1", "-1"],
        "four_exact_phase_syntheses_recomputed": phase_synthesis,
        "alpha_beta_claims_match": synthesis["alpha"] == "[1-exp(-i*phi)]/[2*sqrt(2)]" and synthesis["beta"] == "[1+exp(-i*phi)]/[2*sqrt(2)]",
        "Hermitian_quadrature_claim_is_explicit": synthesis["Hermitian_two_quadrature_interaction"].startswith("H_loc=sigma_x tensor"),
        "compressed_Hamiltonian_matrix_matches": compression["Hamiltonian_over_G"] == [["0", "0", "0"], ["0", "0", "1"], ["0", "1", "0"]],
        "compressed_effects_match_apparatus": compression["E_pass"].endswith("P_minus(phi)") and compression["E_absorb"] == "sin(G*tau)^2 P_minus(phi)" and apparatus["derived_instrument"]["E_no"].endswith("epsilon*P_minus(phi)"),
        "seven_vandermonde_ranks_recomputed": all_vandermonde and recorded_vandermonde == vandermonde,
        "finite_Laurent_claim_recorded": "finite d" in no_go["finite_derivative_fact"],
        "root_theorem_recorded": "infinitely many roots" in no_go["root_argument"],
        "nonzero_two_point_support_is_rejected": no_go["status"] == "EXACT_TWO_POINT_ANGLE_SUPPORT_IMPOSSIBLE_FOR_NONZERO_FINITE_DERIVATIVE_LOCAL_DENSITY",
        "continuous_angle_input_rechecked": continuous["continuous_tagged_family"]["domain"] == "-1<c<1",
        "local_vertex_only_is_computed": leakage["local_vertex_on_selected_modes"] == "COMPUTED",
        "full_invariance_remains_open": leakage["selected_sector_invariance_under_full_local_Hamiltonian"].startswith("NOT_ESTABLISHED"),
        "compressed_exponential_not_promoted": leakage["full_compressed_exponential_identity"] == "NOT_ESTABLISHED",
        "disposition_is_fail_closed": disposition["exact_continuum_two_angle_local_selectivity"] == "OBSTRUCTED" and disposition["full_local_detector_evolution"] == "NOT_CONSTRUCTED",
        "absolute_q8_remains_open": disposition["absolute_q8_probability"] == "NOT_COMPUTED",
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
    sys.exit(main())
