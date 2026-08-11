#!/usr/bin/env python3
"""Independent verifier for the BT fourth-profile positivity obstruction."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-profile-positivity-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if schema_errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    inner = load(os.path.join(ROOT, inputs[1]["path"]))
    separation = load(os.path.join(ROOT, inputs[2]["path"]))
    moller = load(os.path.join(ROOT, inputs[3]["path"]))
    hp = load(os.path.join(ROOT, inputs[4]["path"]))
    audit = certificate["orientation_audit"]
    positive = certificate["positive_profile_test"]
    lift = certificate["fibrewise_krein_lift"]

    kappa = [
        frac(value)
        for value in inner["inner_threshold"]["fixture_r_log_r_coefficients"]
    ]
    rho = frac(separation["shared_fixture"]["rho"])
    lower_rates = [
        frac(value)
        for value in moller["physical_vacuum_moller_column"]["conditional_rates"]
    ]
    lower_chain = lower_rates[0] * lower_rates[1] * lower_rates[2]
    born_divisor = frac(moller["finite_model_inclusive_response"]["Born_coefficient"])
    fourth_history_count = (
        moller["physical_vacuum_moller_column"]["history_counts"][-1] * 6
    )
    G = sp.Matrix(
        [
            [sp.Rational(frac(value).numerator, frac(value).denominator)
             for value in row]
            for row in separation["shared_fixture"]["forced_missing_gram"]
        ]
    )
    K4 = sp.diag(
        *[sp.Rational(value.numerator, value.denominator) for value in kappa]
    )
    eta = sp.diag(G, G)
    amplitudes = [
        sp.sqrt(-sp.Rational(value.numerator, value.denominator) / 2)
        for value in kappa
    ]
    B = sp.zeros(4, 2)
    B[1, 0] = amplitudes[0]
    B[3, 1] = amplitudes[1]
    pullback = sp.simplify(B.T * eta * B)
    total_metric = sp.diag(sp.eye(2), eta)
    Kjet = sp.zeros(6, 6)
    Kjet[:2, 2:] = -(B.T * eta)
    Kjet[2:, :2] = B
    skew_defect = sp.simplify(Kjet.T * total_metric + total_metric * Kjet)
    w = sp.symbols("w", real=True)
    convex = sp.factor(w * K4[0, 0] + (1 - w) * K4[1, 1])

    recorded_effect = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in positive["effect_matrix"]]
    )
    recorded_G = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in lift["single_fibre_gram"]]
    )
    recorded_eta = sp.Matrix(
        [[sp.sympify(value) for value in row]
         for row in lift["two_point_module_gram"]]
    )
    recorded_B = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in lift["forward_block_B"]]
    )
    recorded_pullback = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in lift["pullback"]]
    )
    exclusions = certificate["does_not_establish"]
    disposition = certificate["disposition"]

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "all_predecessor_checks_pass": all(
            value["checks"]["ok"] for value in (inner, separation, moller, hp)
        ),
        "coefficient_and_orientation_replay": (
            kappa == [Fraction(-6699, 128), Fraction(-7149, 128)]
            and [frac(value) for value in audit["profile_coefficients"]] == kappa
            and audit["eight_external_delta_prime_sign"] == (-1) ** 8 == 1
        ),
        "positive_predecessor_scale_and_chain": (
            frac(audit["first_three_threshold_scale"]) == 6
            and lower_chain == frac(audit["lower_selected_history_chain"])
            == Fraction(9, 81920)
            and [frac(value) for value in audit["lower_conditional_rates"]]
            == lower_rates
        ),
        "hard_born_divisor_replay_is_positive": (
            born_divisor == Fraction(3, 32)
            == frac(audit["remaining_normalization_signs"]["Born_divisor"])
        ),
        "fourth_history_and_simplex_replay_are_positive": (
            fourth_history_count
            == audit["remaining_normalization_signs"]["labeled_fourth_histories"]
            == 360
            and frac(audit["remaining_normalization_signs"]["ordered_four_simplex"])
            == Fraction(1, 24)
        ),
        "remaining_normalization_orientation_is_fixed_positive": (
            audit["remaining_normalization_signs"]["squared_amplitude_phase_sign"]
            == 1
            and audit["remaining_normalization_signs"][
                "Kallen_phase_space_orientation"
            ]
            == 1
        ),
        "negative_rank_two_effect_reconstruction": (
            recorded_effect == K4
            and K4.rank() == 2
            and all(K4[index, index] < 0 for index in range(2))
            and positive["effect_inertia"]
            == {"positive": 0, "negative": 2, "zero": 0}
        ),
        "faithful_convex_trace_is_strictly_negative": (
            positive["convex_trace"] == str(convex)
            and [frac(value) for value in positive["closed_weight_interval"]]
            == [Fraction(-7149, 128), Fraction(-6699, 128)]
            and max(kappa) < 0
        ),
        "ordinary_CP_HP_effect_is_impossible": (
            positive["ordinary_CP_or_HP_jump"]
            == "EXACTLY_OBSTRUCTED_ON_DECLARED_DIAGONAL_PROFILE_CARRIER"
            and hp["hudson_parthasarathy_cocycle"]["drift"]
            == "D=(1/2)sum_e J_e^dagger J_e"
        ),
        "rho_and_single_fibre_gram_replay": (
            rho == frac(lift["rho"]) == Fraction(819, 4000)
            and recorded_G == G
            and G.det() == -sp.Rational(819, 4000) ** 2
        ),
        "single_fibre_inertia_and_negative_line": (
            G.rank() == 2
            and G.det() < 0
            and G[1, 1] == -2
            and lift["single_fibre_inertia"]
            == {"positive": 1, "negative": 1, "zero": 0}
        ),
        "two_point_module_reconstruction": (
            recorded_eta == eta
            and eta.rank() == 4
            and lift["two_point_module_inertia"]
            == {"positive": 2, "negative": 2, "zero": 0}
        ),
        "forward_block_is_independently_reconstructed": (
            recorded_B == B
            and lift["forward_amplitudes"] == [str(value) for value in amplitudes]
        ),
        "exact_pullback_identity": (
            recorded_pullback == pullback == K4
            and lift["pullback_identity"]
            == "B^sharp B=diag(-6699/128,-7149/128)"
        ),
        "minimal_negative_index_two": (
            B.rank() == K4.rank() == 2
            and positive["effect_inertia"]["negative"] == 2
            and lift["two_point_module_inertia"]["negative"] == 2
        ),
        "krein_skew_generator_identity": (
            skew_defect == sp.zeros(6)
            and lift["status"] == "EXACT_ALGEBRAIC_KREIN_JET_NOT_BT_DERIVED"
        ),
        "probability_and_Eq19_claims_stay_open": (
            disposition["physical_fourth_probability"] == "NOT_ESTABLISHED"
            and disposition["BT_charge_compatible_history_operator"]
            == "NOT_CONSTRUCTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "gravity_and_Lorentzian_claims_stay_open": (
            any("gravitational" in value for value in exclusions)
            and any("LORENTZIAN-CAUSAL" in value for value in exclusions)
        )
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
