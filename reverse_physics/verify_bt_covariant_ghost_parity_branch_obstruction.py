#!/usr/bin/env python3
"""Independent verifier for the BT covariant ghost-parity branch result."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-covariant-ghost-parity-branch-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def clean(poly):
    return {power: value for power, value in poly.items() if not value.is_zero_matrix}


def add(left, right):
    import sympy as sp

    if not left:
        return dict(right)
    if not right:
        return dict(left)
    size = next(iter(left.values())).rows
    return clean({
        power: left.get(power, sp.zeros(size)) + right.get(power, sp.zeros(size))
        for power in set(left) | set(right)
    })


def scale(value, poly):
    return clean({power: value * item for power, item in poly.items()})


def multiply(left, right):
    import sympy as sp

    if not left or not right:
        return {}
    size = next(iter(left.values())).rows
    answer = {}
    for p, a in left.items():
        for q, b in right.items():
            answer[p + q] = answer.get(p + q, sp.zeros(size)) + a * b
    return clean(answer)


def commutator(left, right):
    return add(multiply(left, right), scale(-1, multiply(right, left)))


def parity(poly, kappa):
    return clean({-power: kappa * value * kappa for power, value in poly.items()})


def sharp(poly, gram):
    return clean({power: gram * value.T * gram for power, value in poly.items()})


def charge_derivative(poly, charge):
    return clean({
        power: power * value + charge * value - value * charge
        for power, value in poly.items()
    })


def h_commutator(poly, hamiltonian):
    return clean({
        power: hamiltonian * value - value * hamiltonian
        for power, value in poly.items()
    })


def relative_trace(poly):
    import sympy as sp

    return sp.factor(sp.trace(poly[0])) if 0 in poly else sp.Rational(0)


def equal(left, right):
    import sympy as sp

    if not left and not right:
        return True
    sample = next(iter(left.values())) if left else next(iter(right.values()))
    for power in set(left) | set(right):
        if left.get(power, sp.zeros(sample.rows)) != right.get(power, sp.zeros(sample.rows)):
            return False
    return True


def parse_laurent(value):
    return {int(power): matrix(item) for power, item in value.items()}


def replay_series(generator, projector, max_order):
    series = [{0: projector}]
    nested = {0: projector}
    for order in range(1, max_order + 1):
        nested = commutator(generator, nested)
        series.append(scale(Fraction(1, math.factorial(order)), nested))
    return series


def verify(certificate):
    import sympy as sp

    schema_ok = not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if not schema_ok:
        return {"schema_validation": False}

    hashes = certificate["provenance"]["input_hashes"]
    inputs_ok = all(sha256(path) == digest for path, digest in hashes.items())
    predecessors = [
        load(os.path.join(ROOT, path))
        for path in hashes
        if path.startswith("reverse_physics/certificates/")
    ]
    event = load(os.path.join(
        ROOT,
        "planning/events/"
        "reverse-physics-bateman-covariant-ghost-parity-branch-obstruction-"
        "DONE-654759d8.json",
    ))

    block = certificate["finite_resonant_block"]
    gram = matrix(block["gram"])
    kappa = matrix(block["ghost_parity"])
    charge = matrix(block["species_charge"])
    hamiltonian = matrix(block["free_hamiltonian"])
    dmap = matrix(block["daughter_to_parent_map"])
    recorded_k = matrix(block["K_plus"])
    projector = matrix(block["P0"])
    recorded_tangent = matrix(block["commutator_K_plus_P0"])

    # Reconstruct the public block directly from its three coefficient formulas,
    # with normalized cross CCRs. This does not import the producer module.
    e1, e2, energy = sp.Rational(1), sp.Rational(2), sp.Rational(3)
    g1 = sp.Matrix([[0, 1], [1, 0]])
    g2 = sp.kronecker_product(g1, g1)
    expected_gram = sp.diag(g1, g2)
    expected_d = sp.Matrix([
        [0, -1/(4*energy*e2), -1/(4*energy*e1), 0],
        [0, 0, 0, 1/(4*e1*e2)],
    ])
    expected_dsharp = g2 * expected_d.T * g1
    expected_k = sp.zeros(6)
    expected_k[:2, 2:] = expected_d
    expected_k[2:, :2] = -expected_dsharp
    expected_p = sp.diag(1, 1, 0, 0, 0, 0)
    expected_tangent = expected_k * expected_p - expected_p * expected_k

    public = {-1: expected_k}
    public_first = {-1: expected_tangent}
    conjugate_first = parity(public_first, kappa)
    defect = add(conjugate_first, scale(-1, public_first))
    even_first = scale(Fraction(1, 2), add(public_first, conjugate_first))
    odd_first = scale(Fraction(1, 2), add(public_first, scale(-1, conjugate_first)))
    even_norm = relative_trace(multiply(sharp(even_first, gram), even_first))
    odd_norm = relative_trace(multiply(sharp(odd_first, gram), odd_first))
    overlap = relative_trace(multiply(sharp(even_first, gram), odd_first))
    public_norm = relative_trace(multiply(sharp(public_first, gram), public_first))
    repair_generator = scale(Fraction(1, 2), add(public, parity(public, kappa)))
    repair_first = commutator(repair_generator, {0: projector})
    series = replay_series(
        repair_generator,
        projector,
        certificate["minimal_two_branch_repair"]["coefficient_replay_order"],
    )

    series_ok = {
        "idempotent": True,
        "selfadjoint": True,
        "parity": True,
        "charge": True,
        "stationary": True,
    }
    for order, coefficient in enumerate(series):
        square = {}
        for left in range(order + 1):
            square = add(square, multiply(series[left], series[order-left]))
        series_ok["idempotent"] &= equal(square, coefficient)
        series_ok["selfadjoint"] &= equal(sharp(coefficient, gram), coefficient)
        series_ok["parity"] &= equal(parity(coefficient, kappa), coefficient)
        series_ok["charge"] &= not charge_derivative(coefficient, charge)
        series_ok["stationary"] &= not h_commutator(coefficient, hamiltonian)

    obstruction = certificate["public_branch_obstruction"]
    repair = certificate["minimal_two_branch_repair"]
    disposition = certificate["disposition"]
    hidden = certificate["hidden_source_parity_domain"]
    results = {
        "schema_validation": schema_ok,
        "certificate_identity": certificate["certificate"].endswith("BRANCH_OBSTRUCTION_V1"),
        "input_hashes_recomputed": inputs_ok,
        "predecessor_pass_flags_present": all(item["checks"]["ok"] for item in predecessors),
        "done_event_replayed": (
            event["body"]["payload"]["to_state"] == "DONE"
            and "rank-four" in event["body"]["payload"]["note"]
        ),
        "cross_gram_recomputed": gram == expected_gram and gram**2 == sp.eye(6),
        "public_daughter_map_recomputed": dmap == expected_d,
        "public_K_plus_recomputed": recorded_k == expected_k,
        "public_K_plus_is_Krein_skew": gram * expected_k.T * gram == -expected_k,
        "public_K_plus_has_species_charge_plus_one": (
            charge * expected_k - expected_k * charge == expected_k
        ),
        "input_projector_recomputed": projector == expected_p,
        "input_projector_is_even_neutral_stationary": (
            kappa * projector * kappa == projector
            and charge * projector == projector * charge
            and hamiltonian * projector == projector * hamiltonian
        ),
        "rank_four_tangent_recomputed": (
            recorded_tangent == expected_tangent and expected_tangent.rank() == 4
        ),
        "projector_tangent_and_selfadjointness_recomputed": (
            projector * expected_tangent + expected_tangent * projector == expected_tangent
            and gram * expected_tangent.T * gram == expected_tangent
        ),
        "public_Laurent_neutrality_recomputed": not charge_derivative(public_first, charge),
        "public_order_lambda_stationarity_recomputed": not h_commutator(public_first, hamiltonian),
        "ghost_parity_support_inversion_recomputed": set(conjugate_first) == {1},
        "two_power_ghost_defect_recomputed": (
            set(defect) == {-1, 1}
            and all(item.rank() == 4 for item in defect.values())
        ),
        "recorded_public_coefficient_matches": equal(
            parse_laurent(obstruction["public_first_coefficient"]), public_first
        ),
        "recorded_conjugate_coefficient_matches": equal(
            parse_laurent(obstruction["ghost_conjugate_first_coefficient"]), conjugate_first
        ),
        "recorded_ghost_defect_matches": equal(
            parse_laurent(obstruction["ghost_defect"]), defect
        ),
        "canonical_parity_split_recomputed": (
            equal(parse_laurent(obstruction["canonical_parity_split"]["B1_even"]), even_first)
            and equal(parse_laurent(obstruction["canonical_parity_split"]["C1_odd"]), odd_first)
        ),
        "canonical_even_odd_orthogonality_recomputed": overlap == 0,
        "canonical_even_norm_recomputed": even_norm == sp.Rational(7, 288),
        "canonical_odd_nonnull_norm_recomputed": odd_norm == -sp.Rational(7, 288),
        "unsplit_relative_nullity_recomputed": public_norm == 0,
        "formal_order_boundary_recorded": "cannot be canceled" in obstruction["formal_consequence"],
        "Q_zero_logic_is_scoped": (
            "Q_negative=0" in obstruction["Eq19_consequence"]
            and disposition["Eq19_charge_formula_on_declared_covariant_public_branch"]
            == "PROVED_WITH_Q_ZERO"
            and disposition["Eq19_ghost_even_neutral_term_on_declared_public_branch"]
            == "REFUTED"
        ),
        "hidden_parity_nonunit_test_recorded": (
            hidden["augmentation_of_F_at_the_Fock_vacuum"] == 0
            and hidden["formal_power_series_unit_test"].startswith("FAIL")
            and "field equation" in hidden["involution_boundary"]
        ),
        "repair_generator_recomputed": equal(
            parse_laurent(repair["generator_coefficients"]), repair_generator
        ),
        "repair_first_coefficient_recomputed": equal(
            parse_laurent(repair["first_projector_coefficient"]), repair_first
        ),
        "repair_is_skew_even_neutral_stationary": (
            equal(sharp(repair_generator, gram), scale(-1, repair_generator))
            and equal(parity(repair_generator, kappa), repair_generator)
            and not charge_derivative(repair_generator, charge)
            and not h_commutator(repair_generator, hamiltonian)
        ),
        "repair_series_idempotence_replayed": series_ok["idempotent"],
        "repair_series_selfadjointness_replayed": series_ok["selfadjoint"],
        "repair_series_parity_replayed": series_ok["parity"],
        "repair_series_charge_replayed": series_ok["charge"],
        "repair_series_stationarity_replayed": series_ok["stationary"],
        "repair_affiliation_remains_open": (
            repair["affiliation"] == "NOT_SUPPLIED_BY_THE_PUBLIC_RT_MAP"
            and disposition["repair_source_affiliation"] == "OPEN"
        ),
        "physical_and_causal_claims_not_promoted": (
            disposition["physical_probability"] == "NOT_ESTABLISHED"
            and any("LORENTZIAN-CAUSAL" in item for item in certificate["does_not_establish"])
        ),
    }
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    certificate = load(args.verify)
    results = verify(certificate)
    for name, ok in results.items():
        print(("PASS: " if ok else "FAIL: ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
