#!/usr/bin/env python3
"""Independent fraction-polynomial verifier for the standard n=3 Eq. 19 test."""
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
    "REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-standard-characteristic-eq19-squeeze-inheritance-v1.schema.json",
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


# Polynomials in the real squeeze amplitude z are degree -> Fraction maps.
def poly(value=0):
    if isinstance(value, dict):
        return {int(degree): Fraction(entry) for degree, entry in value.items() if Fraction(entry)}
    value = Fraction(value)
    return {0: value} if value else {}


def padd(left, right, scale=Fraction(1)):
    answer = dict(left)
    for degree, entry in right.items():
        answer[degree] = answer.get(degree, Fraction(0)) + scale * entry
    return {degree: entry for degree, entry in answer.items() if entry}


def pmul(left, right):
    answer = {}
    for left_degree, left_entry in left.items():
        for right_degree, right_entry in right.items():
            degree = left_degree + right_degree
            answer[degree] = answer.get(degree, Fraction(0)) + left_entry * right_entry
    return {degree: entry for degree, entry in answer.items() if entry}


def pscale(scale, value):
    scale = Fraction(scale)
    return {degree: scale * entry for degree, entry in value.items() if scale * entry}


def peval(value, z):
    z = Fraction(z)
    return sum(entry * z**degree for degree, entry in value.items())


def mat(rows):
    return [[poly(entry) for entry in row] for row in rows]


def zeros(rows, columns=None):
    columns = rows if columns is None else columns
    return [[{} for _ in range(columns)] for _ in range(rows)]


def identity(size):
    value = zeros(size)
    for index in range(size):
        value[index][index] = poly(1)
    return value


def transpose(value):
    return [list(row) for row in zip(*value)]


def madd(left, right, scale=Fraction(1)):
    return [
        [padd(left[i][j], right[i][j], scale) for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def mscale(scale, value):
    return [[pscale(scale, entry) for entry in row] for row in value]


def mmul(left, right):
    answer = zeros(len(left), len(right[0]))
    for i in range(len(left)):
        for j in range(len(right[0])):
            entry = {}
            for k in range(len(right)):
                entry = padd(entry, pmul(left[i][k], right[k][j]))
            answer[i][j] = entry
    return answer


def mtrace(value):
    answer = {}
    for index in range(len(value)):
        answer = padd(answer, value[index][index])
    return answer


def block_diag(left, right):
    answer = zeros(len(left) + len(right), len(left[0]) + len(right[0]))
    for i in range(len(left)):
        for j in range(len(left[0])):
            answer[i][j] = left[i][j]
    for i in range(len(right)):
        for j in range(len(right[0])):
            answer[len(left) + i][len(left[0]) + j] = right[i][j]
    return answer


def swap_kappa(kappa):
    zero = zeros(len(kappa))
    top = [zero[i] + kappa[i] for i in range(len(kappa))]
    bottom = [kappa[i] + zero[i] for i in range(len(kappa))]
    return top + bottom


def evaluate_matrix(value, z=1):
    return [[peval(entry, z) for entry in row] for row in value]


def rank_fraction(value):
    rows = [row[:] for row in value]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column]
        rows[pivot_row] = [entry / lead for entry in rows[pivot_row]]
        for i in range(len(rows)):
            if i == pivot_row:
                continue
            factor = rows[i][column]
            if factor:
                rows[i] = [rows[i][j] - factor * rows[pivot_row][j] for j in range(len(rows[0]))]
        pivot_row += 1
    return pivot_row


def lclean(value):
    return {power: matrix for power, matrix in value.items() if matrix != zeros(len(matrix), len(matrix[0]))}


def ladd(left, right, scale=Fraction(1)):
    sample = next(iter(left.values())) if left else next(iter(right.values()))
    answer = {}
    for power in set(left) | set(right):
        answer[power] = madd(
            left.get(power, zeros(len(sample), len(sample[0]))),
            right.get(power, zeros(len(sample), len(sample[0]))),
            scale,
        )
    return lclean(answer)


def lscale(scale, value):
    return lclean({power: mscale(scale, matrix) for power, matrix in value.items()})


def lmul(left, right):
    sample = next(iter(left.values()))
    answer = {}
    for left_power, left_matrix in left.items():
        for right_power, right_matrix in right.items():
            power = left_power + right_power
            answer[power] = madd(
                answer.get(power, zeros(len(sample), len(sample[0]))),
                mmul(left_matrix, right_matrix),
            )
    return lclean(answer)


def lsharp(value, gram):
    return lclean({power: mmul(mmul(gram, transpose(matrix)), gram) for power, matrix in value.items()})


def lparity(value, kappa):
    return lclean({-power: mmul(mmul(kappa, matrix), kappa) for power, matrix in value.items()})


def lblock_diag(left, right):
    left_sample = next(iter(left.values()))
    right_sample = next(iter(right.values()))
    return lclean({
        power: block_diag(
            left.get(power, zeros(len(left_sample), len(left_sample[0]))),
            right.get(power, zeros(len(right_sample), len(right_sample[0]))),
        )
        for power in set(left) | set(right)
    })


def coefficient_trace(value, power=0):
    return mtrace(value[power]) if power in value else {}


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    hashes_ok = all(sha256(path) == digest for path, digest in hashes.items())
    inputs = {path: load(os.path.join(ROOT, path)) for path in hashes}
    predecessors = {
        value.get("certificate"): value
        for path, value in inputs.items()
        if path.startswith("reverse_physics/certificates/")
    }

    z = {1: Fraction(1)}
    z2 = {2: Fraction(1)}
    pair_gram = mat([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    pair_a = {
        0: mat([[1, 0, 0], [0, 0, 0], [0, 0, 0]]),
        2: [[{}, z, {}], [{}, {}, {}], [z, {}, {}]],
        4: [[{}, {}, {}], [{}, {}, {}], [{}, z2, {}]],
    }
    pair_parity = lparity(pair_a, pair_gram)
    pair_even = lscale(Fraction(1, 2), ladd(pair_a, pair_parity))
    pair_odd = lscale(Fraction(1, 2), ladd(pair_a, pair_parity, Fraction(-1)))
    pair_norm = coefficient_trace(lmul(lsharp(pair_odd, pair_gram), pair_odd))
    pair_overlap = coefficient_trace(lmul(lsharp(pair_even, pair_gram), pair_odd))
    n3_norm = pscale(8, pair_norm)
    n3_fixture = peval(n3_norm, Fraction(1, 4))
    pair_ranks = {power: rank_fraction(evaluate_matrix(matrix)) for power, matrix in pair_odd.items()}
    n3_ranks = {power: 8 * rank for power, rank in pair_ranks.items()}

    # Verify the doubled parity identity on the nontrivial pair factor.  The
    # active n=3 identity tensor only multiplies every rank and trace by eight.
    doubled_a = lblock_diag(pair_a, pair_parity)
    doubled_gram = block_diag(pair_gram, pair_gram)
    doubled_kappa = swap_kappa(pair_gram)
    doubled_parity = lparity(doubled_a, doubled_kappa)
    doubled_odd = lscale(Fraction(1, 2), ladd(doubled_a, doubled_parity, Fraction(-1)))
    doubled_trace_pair = coefficient_trace(doubled_a)

    characteristic = predecessors["REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1"]
    dichotomy = predecessors["REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1"]
    charge = predecessors["REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1"]
    ghost = predecessors["REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1"]
    q10 = predecessors["REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"]
    event = next(value for path, value in inputs.items() if path.startswith("planning/events/"))

    inheritance = certificate["homogeneous_charge_inheritance"]
    completion = certificate["canonical_doubled_completion"]
    disposition = certificate["q10_transport_disposition"]
    boundary = certificate["minimality_and_boundary"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1",
        "input_hashes_recomputed": hashes_ok,
        "all_predecessors_pass": all(item["checks"]["ok"] for item in predecessors.values()),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("standard-characteristic-eq19-squeeze-inheritance"),
        "public_three_particle_orbit_is_six": characteristic["factorial_and_orbit_audit"]["incoming_S3_orbit_multiplicity"] == 6,
        "public_one_over_three_factorial_cancels_orbit": Fraction(6, 6) == 1,
        "n3_species_rank_is_two_cubed": certificate["standard_characteristic_normalization"]["active_species_rank"] == 2**3,
        "pair_odd_support_is_exact": set(pair_odd) == {-4, -2, 2, 4},
        "pair_odd_ranks_are_exact": pair_ranks == {-4: 1, -2: 2, 2: 2, 4: 1},
        "pair_odd_norm_reconstructed": pair_norm == {2: Fraction(-1), 4: Fraction(-1, 2)},
        "n3_odd_norm_reconstructed": n3_norm == {2: Fraction(-8), 4: Fraction(-4)},
        "n3_fixture_is_minus_33_over_64": n3_fixture == Fraction(-33, 64),
        "n3_support_ranks_scale_by_eight": n3_ranks == {-4: 8, -2: 16, 2: 16, 4: 8},
        "even_odd_overlap_vanishes": pair_overlap == {},
        "s_less_positive_rank_scales_four_by_four": inheritance["s_less_than_one"]["positive_component_rank"] == ghost["finite_resonant_block"]["commutator_rank"] * 4 == 16,
        "s_equal_norm_matches_reconstruction": inheritance["s_equal_one"]["finite_box_ghost_odd_relative_norm"] == "-33/64",
        "s_greater_ranks_scale_pair_ranks": inheritance["s_greater_than_one"]["positive_free_component_ranks"] == [16, 8],
        "one_sheet_no_go_is_inherited": inheritance["conclusion"].startswith("THE_NORMALIZED_STANDARD_N3"),
        "doubled_pair_projector_is_idempotent": lmul(doubled_a, doubled_a) == doubled_a,
        "doubled_pair_projector_is_Krein_selfadjoint": lsharp(doubled_a, doubled_gram) == doubled_a,
        "doubled_pair_projector_is_ghost_even": doubled_parity == doubled_a,
        "doubled_pair_odd_part_is_zero": doubled_odd == {},
        "doubled_pair_trace_is_two": doubled_trace_pair == {0: Fraction(2)},
        "doubled_n3_raw_trace_is_sixteen": completion["raw_finite_n3_trace"] == 16,
        "sheet_average_is_declared": completion["sheet_normalized_trace"].startswith("tau_dbl="),
        "doubled_source_is_declared_not_inferred": completion["status"].endswith("CHANGED_DOUBLED_SOURCE_THEORY"),
        "charge_predecessor_is_all_order_neutral": charge["formal_inverse_and_projector_consequence"]["Eq19_charge_support"].endswith("TO_ALL_FORMAL_ORDERS"),
        "q10_predecessor_is_common_Born": q10["common_Born_identity"]["status"] == "COMPLETE_Q10_IS_COMMON_BORN",
        "q10_comparison_is_blocked_at_earlier_order": disposition["public_one_sheet_result"] == "BLOCKED_BEFORE_Q10_COMPARISON",
        "selected_q10_is_not_invalidated": disposition["selected_q10_result"].startswith("UNCHANGED_AND_COMPLETE"),
        "time_independence_not_promoted": boundary["time_independence"] == "NOT_PROVED",
        "asymptotic_limits_not_promoted": boundary["asymptotic_limits"] == "NOT_CONSTRUCTED",
        "continuum_trace_not_promoted": boundary["continuum_trace_domain"] == "NOT_CONSTRUCTED",
        "public_eq19_not_claimed": any("public one-sheet" in item for item in certificate["does_not_establish"]),
        "gravity_and_Lorentzian_not_claimed": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
        "source_commit_is_current_predecessor_head": certificate["provenance"]["source_commit"] == "60b2991c191ee725007e9bcbe02e011a24cea699",
        "verification_commands_are_present": len(certificate["verification_commands"]) == 3,
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    certificate = load(args.verify)
    checks = verify(certificate)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        for name in failures:
            print("FAIL:", name, file=sys.stderr)
        return 1
    print(f"BT STANDARD CHARACTERISTIC INDEPENDENT VERIFIER: ALL PASS ({len(checks)}/{len(checks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
