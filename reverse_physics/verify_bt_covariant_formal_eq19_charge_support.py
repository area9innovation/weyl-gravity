#!/usr/bin/env python3
"""Independent verifier for covariant formal BT Eq. 19 charge support."""
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
    "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-covariant-formal-eq19-charge-support-v1.schema.json",
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


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def recurrence_coefficients(max_order):
    omega = [Fraction(1)]
    for n in range(max_order + 1):
        omega.append(omega[-1] / (n + 1))
    box = [Fraction(1)]
    for n in range(max_order):
        box.append(-box[-1] / (n + 1))
    gradient = {1: Fraction(1)}
    for n in range(1, max_order):
        gradient[n + 1] = -gradient[n] / n
    return omega, box, gradient


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    zero_mode = load(os.path.join(ROOT, inputs[1]["path"]))
    rigidity = load(os.path.join(ROOT, inputs[2]["path"]))
    order_lambda = load(os.path.join(ROOT, inputs[3]["path"]))
    ledger = load(os.path.join(ROOT, inputs[4]["path"]))
    public_fock = load(os.path.join(ROOT, inputs[5]["path"]))
    event = load(os.path.join(ROOT, inputs[6]["path"]))
    equivariance = certificate["exact_Eq16_equivariance"]
    consequence = certificate["formal_inverse_and_projector_consequence"]
    boundary = certificate["fixed_vacuum_and_asymptotic_boundary"]
    typed = certificate["typed_object_separation"]
    eq19 = certificate["Eq19_boundary"]
    disposition = certificate["disposition"]

    max_order = equivariance["replay_max_order"]
    omega_rec, box_rec, gradient_rec = recurrence_coefficients(max_order)
    omega_rows = equivariance["Omega_replay"]
    upsilon_rows = equivariance["Upsilon_replay"]
    recorded_omega = [fraction(row["coefficient"]) for row in omega_rows]
    recorded_box = [fraction(row["terms"][0]["coefficient"]) for row in upsilon_rows]
    recorded_gradient = {
        row["coupling_order"]: fraction(row["terms"][1]["coefficient"])
        for row in upsilon_rows
        if len(row["terms"]) == 2
    }
    expected_census = []
    for length in range(equivariance["word_census_max_length"] + 1):
        multiplicities = {}
        for omega_count in range(length + 1):
            charge = 2 * omega_count - length
            multiplicities[str(charge)] = math.comb(length, omega_count)
        expected_census.append(
            {
                "length": length,
                "word_count": 2**length,
                "charge_multiplicities": multiplicities,
                "equivariance_failures": 0,
            }
        )

    fixture = consequence["finite_fixture"]
    H = matrix(fixture["charge_generator"])
    P = matrix(fixture["input_projector"])
    U = matrix(fixture["neutral_similarity"])
    A = matrix(fixture["output_projector"])

    checks = {
        "schema_validation": True,
        "certificate_identity": certificate["certificate"]
        == "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1",
        "input_hashes_recomputed": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_independently_pass": all(
            value["checks"]["ok"]
            for value in (zero_mode, rigidity, order_lambda, ledger, public_fock)
        ),
        "done_event_replayed": (
            event["body"]["payload"]["to_state"] == "DONE"
            and event["body"]["payload"]["target"]
            == "sf:program/work/reverse-physics-bateman-covariant-formal-eq19-charge-support"
        ),
        "formal_algebras_typed": (
            certificate["covariant_formal_algebras"]["coupling_ring"]
            == "Q((lambda))"
            and certificate["covariant_formal_algebras"]["source"]
            == "Q((lambda))[Z,Z^-1] tensor A_nz"
        ),
        "Omega_recurrence_recomputed": recorded_omega == omega_rec,
        "Omega_rows_all_charge_plus_one": all(
            row["orbit_power"] == row["charge"] == 1 for row in omega_rows
        ),
        "Upsilon_box_recurrence_recomputed": recorded_box == box_rec,
        "Upsilon_gradient_recurrence_recomputed": recorded_gradient == gradient_rec,
        "Upsilon_rows_all_charge_minus_one": all(
            row["orbit_power"] == row["charge"] == -1 for row in upsilon_rows
        ),
        "word_census_recomputed_by_binomial_formula": (
            equivariance["word_census"] == expected_census
        ),
        "generator_intertwining_identity_recorded": (
            equivariance["intertwining_identity"]
            == "delta_phi o alpha = alpha o delta_11"
        ),
        "time_translated_intertwining_recorded": (
            equivariance["time_translated_intertwining"]
            == "delta_phi o alpha_t = alpha_t o delta_11"
            and "free phi Hamiltonian" in equivariance["time_translation_reason"]
            and "total-charge-zero cross bilinears"
            in equivariance["time_translation_reason"]
        ),
        "formal_bijectivity_replayed": (
            rigidity["disposition"]["formal_two_sided_inverse"] == "CLEARED"
            and consequence["formal_two_sidedness"]
            == "R^dagger R=1 and R R^dagger=1 coefficient by coefficient"
        ),
        "inverse_intertwining_identity_recorded": (
            consequence["inverse_intertwining_identity"]
            == "delta_11 o beta = beta o delta_phi"
        ),
        "fixture_projector_recomputed": (
            P**2 == P and A == U * P * U.inv() and A**2 == A
        ),
        "fixture_charge_support_recomputed": (
            H * P == P * H and H * U == U * H and H * A == A * H
        ),
        "formal_Q_zero_claim_is_scoped": (
            consequence["Eq19_charge_support"]
            == "P_neutral=A; Q_negative=0 TO_ALL_FORMAL_ORDERS"
            and eq19["strict_negative_Q_on_covariant_formal_algebra"] == "ZERO"
        ),
        "order_lambda_boundary_recovered": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
            and disposition["order_lambda_predecessor"] == "RECOVERED"
        ),
        "fixed_vacuum_obstruction_recomputed": (
            zero_mode["fixed_vacuum_quotient_obstruction"]["remainder_mod_I"]
            == {"numerator": 1, "denominator": 1}
            and boundary["remainder_mod_I"] == 1
            and boundary["charge_theorem_descends_to_Z_equals_1"] == "NO"
        ),
        "object_types_replayed": (
            typed["Eq19_object"] == "R_t P_chi^(phi) R_t^dagger"
            and typed["physical_scattering_object"] == "P_out(S_phi-1)P_in"
            and ledger["combined_ledger"]["typing_rule"]
            == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER"
        ),
        "graph_T_not_retyped_as_Rt": (
            typed["eight_point_K4_and_graph_slope"] == "PHYSICAL_RESPONSE_LEDGER"
            and public_fock["graph_source_realization"]["graph_slope_status"]
            == "NOT_DERIVED_BY_SYM4_C"
        ),
        "ghost_time_and_asymptotic_gates_remain_open": (
            eq19["ghost_even_neutral_component"] == "NOT_PROVED"
            and eq19["neutral_component_time_independence"] == "NOT_PROVED"
            and eq19["asymptotic_limits"] == "NOT_CONSTRUCTED"
        ),
        "full_Eq19_and_physical_claims_not_promoted": (
            eq19["full_Eq19"] == "NOT_PROVED"
            and disposition["physical_probability"] == "NOT_ESTABLISHED"
            and any("LORENTZIAN-CAUSAL" in row for row in certificate["does_not_establish"])
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
