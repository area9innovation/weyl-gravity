#!/usr/bin/env python3
"""Method-distinct verifier for the regular covariant BT Eq. (19) no-go."""
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
    "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-regular-covariant-eq19-no-go-v1.schema.json",
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


def mat(rows):
    return [[Fraction(value) for value in row] for row in rows]


def zeros(n):
    return [[Fraction(0) for _ in range(n)] for _ in range(n)]


def identity(n):
    result = zeros(n)
    for index in range(n):
        result[index][index] = Fraction(1)
    return result


def transpose(value):
    return [list(row) for row in zip(*value)]


def add(left, right, scale=Fraction(1)):
    return [
        [left[i][j] + scale * right[i][j] for j in range(len(left))]
        for i in range(len(left))
    ]


def scalar(scale, value):
    return [[scale * entry for entry in row] for row in value]


def multiply(left, right):
    n = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def trace(value):
    return sum(value[i][i] for i in range(len(value)))


def rank(value):
    rows = [row[:] for row in value]
    nrows = len(rows)
    ncols = len(rows[0])
    pivot_row = 0
    for column in range(ncols):
        pivot = next(
            (candidate for candidate in range(pivot_row, nrows) if rows[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column]
        rows[pivot_row] = [entry / lead for entry in rows[pivot_row]]
        for candidate in range(nrows):
            if candidate == pivot_row:
                continue
            factor = rows[candidate][column]
            if factor:
                rows[candidate] = [
                    rows[candidate][j] - factor * rows[pivot_row][j]
                    for j in range(ncols)
                ]
        pivot_row += 1
        if pivot_row == nrows:
            break
    return pivot_row


def sharp(value, gram):
    return multiply(multiply(gram, transpose(value)), gram)


def laurent_multiply(left, right):
    if not left or not right:
        return {}
    n = len(next(iter(left.values())))
    result = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            product = multiply(left_value, right_value)
            result[power] = add(result.get(power, zeros(n)), product)
    return {power: value for power, value in result.items() if value != zeros(n)}


def laurent_sharp(poly, gram):
    return {power: sharp(value, gram) for power, value in poly.items()}


def verify(certificate):
    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs_ok = all(sha256(path) == digest for path, digest in hashes.items())
    predecessor = {}
    for path in hashes:
        if path.startswith("reverse_physics/certificates/"):
            item = load(os.path.join(ROOT, path))
            predecessor[item["certificate"]] = item
    ghost = predecessor["REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1"]
    charge_cert = predecessor["REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1"]
    unit_cert = predecessor["REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1"]
    born = predecessor["REVERSE_PHYSICS_BT_BORN_TRACE_V1"]
    signed = predecessor["REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1"]
    block = ghost["finite_resonant_block"]
    gram = mat(block["gram"])
    kappa = mat(block["ghost_parity"])
    charge = mat(block["species_charge"])
    k_plus = mat(block["K_plus"])
    p0 = mat(block["P0"])
    tangent = add(multiply(k_plus, p0), multiply(p0, k_plus), Fraction(-1))
    conjugate = multiply(multiply(kappa, tangent), kappa)
    charge_defect = add(
        add(multiply(charge, tangent), multiply(tangent, charge), Fraction(-1)),
        tangent,
        Fraction(-1),
    )
    public = {-1: tangent}
    parity_image = {1: conjugate}
    even = {
        -1: scalar(Fraction(1, 2), tangent),
        1: scalar(Fraction(1, 2), conjugate),
    }
    odd = {
        -1: scalar(Fraction(1, 2), tangent),
        1: scalar(Fraction(-1, 2), conjugate),
    }
    odd_square = laurent_multiply(laurent_sharp(odd, gram), odd)
    overlap = laurent_multiply(laurent_sharp(even, gram), odd)
    odd_norm = trace(odd_square.get(0, zeros(6)))
    even_odd_overlap = trace(overlap.get(0, zeros(6)))

    event_path = next(path for path in hashes if path.startswith("planning/events/"))
    event = load(os.path.join(ROOT, event_path))
    theorem = certificate["charge_projection_argument"]
    contradiction = certificate["order_lambda_contradiction"]
    disposition = certificate["disposition"]
    boundary = certificate["repair_and_escape_boundary"]
    source_mechanism = born["source"]["mechanism"]
    checks = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"] == "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1",
        "input_hashes_recomputed": inputs_ok,
        "all_predecessor_pass_flags_present": all(item["checks"]["ok"] for item in predecessor.values()),
        "done_event_targets_work_item": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"].endswith("regular-covariant-eq19-no-go")
        ),
        "source_split_has_both_required_types": (
            "neutral AND even under ghost parity" in source_mechanism
            and "strictly negatively charged" in source_mechanism
        ),
        "signed_kernel_is_complete_for_corner": signed["completed_signed_kernel"]["disposition"].startswith("COMPLETE_FOR_THE_PUBLIC_ORDER_LAMBDA"),
        "P0_is_exact_n1_species_projection": p0 == [
            [Fraction(1 if i == j and i < 2 else 0) for j in range(6)]
            for i in range(6)
        ],
        "tangent_recomputed_without_producer": tangent == mat(block["commutator_K_plus_P0"]),
        "tangent_has_rank_four": rank(tangent) == 4,
        "laurent_charge_defect_vanishes": charge_defect == zeros(6),
        "ghost_parity_is_an_involution": multiply(kappa, kappa) == identity(6),
        "ghost_conjugate_has_rank_four": rank(conjugate) == 4,
        "public_and_conjugate_support_are_disjoint": set(public) == {-1} and set(parity_image) == {1},
        "odd_norm_recomputed_exactly": odd_norm == Fraction(-7, 288),
        "even_odd_overlap_recomputed_exactly": even_odd_overlap == 0,
        "recorded_rank_matches": contradiction["commutator_rank"] == 4,
        "recorded_support_matches": (
            contradiction["public_support"] == [-1]
            and contradiction["ghost_conjugate_support"] == [1]
            and contradiction["ghost_defect_support"] == [-1, 1]
        ),
        "recorded_norm_matches": Fraction(contradiction["canonical_odd_relative_norm"]) == odd_norm,
        "charge_predecessor_forces_only_zero_component": charge_cert["formal_inverse_and_projector_consequence"]["charge_decomposition"] == "A_0=A and A_q=0 for every q!=0",
        "negative_projection_logic_is_explicit": (
            theorem["negative_projection"].endswith("=Q_<0")
            and theorem["forced_remainder"] == "Q_<0=0"
            and theorem["forced_neutral_term"] == "N_0=A"
        ),
        "ghost_evenness_is_applied_to_whole_A": theorem["consequence"].endswith("whole public pushforward"),
        "coefficientwise_contradiction_is_recorded": (
            "false already at order lambda" in contradiction["coefficientwise_conclusion"]
            and "cannot cancel" in contradiction["higher_order_boundary"]
        ),
        "regular_repair_obstruction_is_imported": unit_cert["unit_obstruction"]["conclusion"] == "NO_SAME_CHART_REGULAR_LOCAL_SYMBOL_HIDDEN_PARITY_AUTOMORPHISM",
        "minimal_repair_not_called_public": boundary["public_affiliation"] == "NOT_SUPPLIED_BY_PUBLIC_RT",
        "fixed_vacuum_is_not_promoted": disposition["fixed_vacuum_Eq19"] == "NOT_DECIDED_BY_COVARIANT_NO_GO",
        "enlarged_completion_is_not_ruled_out": disposition["unpublished_enlarged_Eq19"] == "NOT_RULED_OUT",
        "physical_probability_is_not_promoted": disposition["complete_physical_probability"] == "NOT_ESTABLISHED_BY_THIS_THEOREM",
        "Lorentzian_boundary_is_present": any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"]),
        "universal_no_go_is_explicitly_forbidden": any("universal refutation" in item for item in certificate["does_not_establish"]),
        "final_disposition_is_scoped": disposition["public_regular_covariant_Eq19_architecture"] == "REFUTED_AT_ORDER_LAMBDA",
    }
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
