#!/usr/bin/env python3
"""Method-distinct verifier for the BT full-map Eq. (19) charge dichotomy."""
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
    "REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eq19-spurion-squeeze-dichotomy-no-go-v1.schema.json",
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


# A polynomial is a finite degree -> rational dictionary in the real variable z.
def poly(value=0):
    if isinstance(value, dict):
        return {int(k): Fraction(v) for k, v in value.items() if Fraction(v)}
    value = Fraction(value)
    return {0: value} if value else {}


def padd(left, right, scale=Fraction(1)):
    answer = dict(left)
    for degree, value in right.items():
        answer[degree] = answer.get(degree, Fraction(0)) + scale * value
    return {degree: value for degree, value in answer.items() if value}


def pmul(left, right):
    answer = {}
    for left_degree, left_value in left.items():
        for right_degree, right_value in right.items():
            degree = left_degree + right_degree
            answer[degree] = answer.get(degree, Fraction(0)) + left_value * right_value
    return {degree: value for degree, value in answer.items() if value}


def pscale(scale, value):
    return {degree: Fraction(scale) * entry for degree, entry in value.items() if scale * entry}


def peval(value, z_value):
    z_value = Fraction(z_value)
    return sum(entry * z_value**degree for degree, entry in value.items())


def pconst(value):
    return poly(value)


PZERO = poly(0)
PONE = poly(1)
PZ = {1: Fraction(1)}
PZ2 = {2: Fraction(1)}


def mat(rows):
    return [[pconst(value) for value in row] for row in rows]


def fraction_mat(rows):
    return [[Fraction(value) for value in row] for row in rows]


def zeros(n, m=None):
    m = n if m is None else m
    return [[{} for _ in range(m)] for _ in range(n)]


def identity(n):
    answer = zeros(n)
    for index in range(n):
        answer[index][index] = PONE
    return answer


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


def kron(left, right):
    answer = zeros(len(left) * len(right), len(left[0]) * len(right[0]))
    for i in range(len(left)):
        for j in range(len(left[0])):
            for k in range(len(right)):
                for ell in range(len(right[0])):
                    answer[i * len(right) + k][j * len(right[0]) + ell] = pmul(
                        left[i][j], right[k][ell]
                    )
    return answer


def mtrace(value):
    answer = {}
    for index in range(len(value)):
        answer = padd(answer, value[index][index])
    return answer


def evaluate_matrix(value, z_value):
    return [[peval(entry, z_value) for entry in row] for row in value]


def rank_fraction(value):
    rows = [row[:] for row in value]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (candidate for candidate in range(pivot_row, len(rows)) if rows[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column]
        rows[pivot_row] = [entry / lead for entry in rows[pivot_row]]
        for candidate in range(len(rows)):
            if candidate == pivot_row:
                continue
            factor = rows[candidate][column]
            if factor:
                rows[candidate] = [
                    rows[candidate][j] - factor * rows[pivot_row][j]
                    for j in range(len(rows[0]))
                ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def rank(value, z_value=1):
    return rank_fraction(evaluate_matrix(value, z_value))


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
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            answer[power] = madd(
                answer.get(power, zeros(len(sample), len(sample[0]))),
                mmul(left_value, right_value),
            )
    return lclean(answer)


def lsharp(value, gram):
    return lclean(
        {power: mmul(mmul(gram, transpose(matrix)), gram) for power, matrix in value.items()}
    )


def lparity(value, kappa):
    return lclean(
        {-power: mmul(mmul(kappa, matrix), kappa) for power, matrix in value.items()}
    )


def coefficient_trace(value, power=0):
    return mtrace(value[power]) if power in value else {}


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs_ok = all(sha256(path) == digest for path, digest in hashes.items())
    predecessors = {}
    for path in hashes:
        if path.startswith("reverse_physics/certificates/"):
            item = load(os.path.join(ROOT, path))
            predecessors[item["certificate"]] = item
    ghost = predecessors["REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1"]
    squeeze = predecessors["REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1"]
    squeezed_fock = predecessors["REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1"]
    old = predecessors["REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1"]
    block = ghost["finite_resonant_block"]

    gram_n1 = mat(block["gram"])
    kappa_n1 = mat(block["ghost_parity"])
    p_n1 = mat(block["P0"])
    k_plus = mat(block["K_plus"])
    tangent = madd(mmul(k_plus, p_n1), mmul(p_n1, k_plus), Fraction(-1))

    pair_gram = mat([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    pair_kappa = pair_gram
    pair_q = [
        [PZERO, pscale(-1, PZ), PZERO],
        [PZERO, PZERO, PZERO],
        [PZ, PZERO, PZERO],
    ]
    pair_p = mat([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
    pair_q2 = mmul(pair_q, pair_q)
    pair_q3 = mmul(pair_q2, pair_q)
    pair_s = madd(madd(identity(3), pair_q), mscale(Fraction(1, 2), pair_q2))
    pair_s_inverse = madd(
        madd(identity(3), pair_q, Fraction(-1)), mscale(Fraction(1, 2), pair_q2)
    )
    pair_a_matrix = mmul(mmul(pair_s, pair_p), pair_s_inverse)
    pair_a = {
        0: pair_p,
        2: [
            [PZERO, PZ, PZERO],
            [PZERO, PZERO, PZERO],
            [PZ, PZERO, PZERO],
        ],
        4: [
            [PZERO, PZERO, PZERO],
            [PZERO, PZERO, PZERO],
            [PZERO, PZ2, PZERO],
        ],
    }
    pair_parity = lparity(pair_a, pair_kappa)
    pair_even = lscale(Fraction(1, 2), ladd(pair_a, pair_parity))
    pair_odd = lscale(Fraction(1, 2), ladd(pair_a, pair_parity, Fraction(-1)))
    pair_norm = coefficient_trace(lmul(lsharp(pair_odd, pair_gram), pair_odd))
    pair_overlap = coefficient_trace(lmul(lsharp(pair_even, pair_gram), pair_odd))

    full_gram = kron(gram_n1, pair_gram)
    full_kappa = kron(kappa_n1, pair_kappa)
    full_a = {power: kron(p_n1, value) for power, value in pair_a.items()}
    full_parity = lparity(full_a, full_kappa)
    full_even = lscale(Fraction(1, 2), ladd(full_a, full_parity))
    full_odd = lscale(Fraction(1, 2), ladd(full_a, full_parity, Fraction(-1)))
    full_norm = coefficient_trace(lmul(lsharp(full_odd, full_gram), full_odd))
    full_overlap = coefficient_trace(lmul(lsharp(full_even, full_gram), full_odd))

    event_path = next(path for path in hashes if path.startswith("planning/events/"))
    event = load(os.path.join(ROOT, event_path))
    witness = certificate["exact_squeezed_n1_witness"]
    cases = certificate["homogeneous_charge_exhaustion"]["cases"]
    disposition = certificate["disposition"]
    predecessor_scope = certificate["predecessor_scope"]
    physical_z = squeezed_fock["finite_box_carrier"]["unordered_pair_amplitude"]

    expected_pair_matrix = madd(madd(pair_a[0], pair_a[2]), pair_a[4])
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1",
        "input_hashes_recomputed": inputs_ok,
        "all_predecessor_pass_flags_present": all(item["checks"]["ok"] for item in predecessors.values()),
        "done_event_targets_successor_item": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"].endswith("eq19-spurion-squeeze-dichotomy-no-go")
        ),
        "public_factorization_is_imported": squeeze["operator_identity"]["factorization"].startswith("R(lambda)=S U(lambda)"),
        "unordered_pair_amplitude_is_nonzero_one_quarter": physical_z == {"denominator": 4, "numerator": 1},
        "pair_generator_cube_recomputed_zero": pair_q3 == zeros(3),
        "pair_generator_recomputed_Krein_skew": mmul(mmul(pair_gram, transpose(pair_q)), pair_gram) == mscale(-1, pair_q),
        "pair_exponential_inverse_recomputed": mmul(pair_s, pair_s_inverse) == identity(3),
        "pair_projector_derived_from_exponential": pair_a_matrix == expected_pair_matrix,
        "pair_projector_recomputed_idempotent": lmul(pair_a, pair_a) == pair_a,
        "pair_projector_recomputed_Krein_selfadjoint": lsharp(pair_a, pair_gram) == pair_a,
        "pair_projector_trace_recomputed_one": coefficient_trace(pair_a) == PONE,
        "pair_odd_support_recomputed": set(pair_odd) == {-4, -2, 2, 4},
        "pair_odd_ranks_recomputed": {power: rank(value) for power, value in pair_odd.items()} == {-4: 1, -2: 2, 2: 2, 4: 1},
        "pair_odd_norm_polynomial_recomputed": pair_norm == {2: Fraction(-1), 4: Fraction(-1, 2)},
        "pair_even_odd_overlap_recomputed": pair_overlap == {},
        "n1_tangent_recomputed_from_imported_matrices": tangent == mat(block["commutator_K_plus_P0"]),
        "n1_tangent_rank_recomputed_four": rank(tangent) == 4,
        "full_projector_recomputed_idempotent": lmul(full_a, full_a) == full_a,
        "full_projector_recomputed_Krein_selfadjoint": lsharp(full_a, full_gram) == full_a,
        "full_projector_trace_recomputed_two": coefficient_trace(full_a) == {0: Fraction(2)},
        "full_odd_ranks_recomputed": {power: rank(value) for power, value in full_odd.items()} == {-4: 2, -2: 4, 2: 4, 4: 2},
        "full_odd_norm_polynomial_recomputed": full_norm == {2: Fraction(-2), 4: Fraction(-1)},
        "full_even_odd_overlap_recomputed": full_overlap == {},
        "physical_fixture_norm_recomputed": peval(full_norm, Fraction(1, 4)) == Fraction(-33, 256),
        "recorded_pair_norm_matches": witness["pair_ghost_odd_relative_norm"] == "-z^2*(z^2+2)/2",
        "recorded_full_norm_matches": witness["n1_tensor_ghost_odd_relative_norm"] == "-z^2*(z^2+2)",
        "recorded_fixture_norm_matches": witness["physical_fixture_n1_odd_norm"] == "-33/256",
        "recorded_support_ranks_match": witness["ghost_odd_rank_by_support"] == {"-4": 2, "-2": 4, "2": 4, "4": 2},
        "charge_locking_formula_recorded_exactly": certificate["full_map_factorization"]["locking_identity"] == "q_S=-2q_K",
        "three_sign_cases_recorded_in_order": [row["case"] for row in cases] == ["s<1", "s=1", "s>1"],
        "s_less_case_has_unique_positive_rank_four_head": (
            cases[0]["order_lambda_full_charges"] == ["q_K", "-q_K", "-3q_K"]
            and cases[0]["rank_by_component"] == [4, 8, 4]
            and cases[0]["conclusion"] == "FORBIDDEN_POSITIVE_CHARGE"
        ),
        "s_equal_case_uses_neutral_non_null_parity_defect": (
            cases[1]["charges"] == ["q_K=0", "q_S=0"]
            and cases[1]["conclusion"] == "NEUTRAL_TERM_NOT_GHOST_EVEN"
        ),
        "s_greater_case_has_positive_free_squeeze": (
            cases[2]["free_full_charges"] == ["0", "q_S", "2q_S"]
            and cases[2]["rank_by_positive_component"] == [4, 2]
            and cases[2]["conclusion"] == "FORBIDDEN_POSITIVE_CHARGE"
        ),
        "exhaustive_conclusion_is_explicit": certificate["homogeneous_charge_exhaustion"]["exhaustive_conclusion"] == "NO_REAL_HOMOGENEOUS_s_SATISFIES_THE_EQ19_PACKAGE",
        "old_certificate_is_not_silently_rewritten": old["certificate"] == predecessor_scope["predecessor"],
        "old_full_map_route_is_explicitly_superseded": predecessor_scope["disposition"] == "SUPERSEDED_AS_FULL_MAP_PROOF_ROUTE_RETAINED_AS_UNSQUEEZED_FACTOR_WITNESS",
        "fixed_vacuum_case_is_now_scoped_refuted": disposition["fixed_vacuum_s_zero"] == "REFUTED_BY_POSITIVE_ORDER_LAMBDA_COMPONENT",
        "covariant_case_is_now_scoped_refuted": disposition["covariant_orbit_s_one"] == "REFUTED_BY_NEUTRAL_NON_GHOST_EVEN_SQUEEZED_PROJECTOR",
        "enlarged_and_non_Fock_routes_remain_open": (
            disposition["nonhomogeneous_or_enlarged_charge_architecture"] == "NOT_RULED_OUT"
            and disposition["continuum_or_non_Fock_Eq19"] == "NOT_RULED_OUT"
        ),
        "physical_probability_not_used_as_Eq19_evidence": disposition["selected_q6_physical_probability"] == "UNCHANGED_AND_NOT_USED_AS_EQ19_EVIDENCE",
        "Lorentzian_boundary_is_present": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
        "universal_no_go_is_explicitly_forbidden": any("universal refutation" in item for item in certificate["does_not_establish"]),
    }
    return checks


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
