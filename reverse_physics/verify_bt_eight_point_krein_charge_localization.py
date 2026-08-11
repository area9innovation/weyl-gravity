#!/usr/bin/env python3
"""Independent verifier for BT eight-point Krein charge localization."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-krein-charge-localization-v1.schema.json",
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


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    profile = load(os.path.join(ROOT, inputs[1]["path"]))
    eq19 = load(os.path.join(ROOT, inputs[2]["path"]))
    zero_mode = load(os.path.join(ROOT, inputs[3]["path"]))
    moller = load(os.path.join(ROOT, inputs[4]["path"]))
    fibre = certificate["charge_fibre"]
    line = certificate["canonical_negative_line"]
    decomposition = certificate["profile_charge_decomposition"]
    boundary = certificate["Eq19_boundary"]

    rho_q = frac(profile["fibrewise_krein_lift"]["rho"])
    rho = sp.Rational(rho_q.numerator, rho_q.denominator)
    G = sp.Matrix([[0, -rho], [-rho, -2]])
    J = sp.Matrix([[0, 1], [1, 0]])
    S = sp.Matrix([[1, 1], [0, -rho]])
    C = sp.Matrix([[-rho, -1], [0, 1]])
    H0 = sp.diag(1, -1)
    H = sp.simplify(S * H0 * S.inv())
    Pplus = sp.simplify((sp.eye(2) + H) / 2)
    Pminus = sp.simplify((sp.eye(2) - H) / 2)
    f2 = sp.Matrix([0, 1])
    fplus = sp.simplify(Pplus * f2)
    fminus = sp.simplify(Pminus * f2)
    eta = sp.diag(G, G)
    Hmodule = sp.diag(H, H)
    Pplus_module = sp.diag(Pplus, Pplus)
    Pminus_module = sp.diag(Pminus, Pminus)
    kappa = [
        sp.Rational(value["numerator"], value["denominator"])
        for value in profile["orientation_audit"]["profile_coefficients"]
    ]
    amplitudes = [sp.sqrt(-value / 2) for value in kappa]
    B = sp.zeros(4, 2)
    B[1, 0] = amplitudes[0]
    B[3, 1] = amplitudes[1]
    Bplus = sp.simplify(Pplus_module * B)
    Bminus = sp.simplify(Pminus_module * B)
    K4 = sp.diag(*kappa)
    plus = sp.simplify(Bplus.T * eta * Bplus)
    minus = sp.simplify(Bminus.T * eta * Bminus)
    pm = sp.simplify(Bplus.T * eta * Bminus)
    mp = sp.simplify(Bminus.T * eta * Bplus)
    exclusions = certificate["does_not_establish"]
    disposition = certificate["disposition"]

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "all_predecessor_checks_pass": all(
            value["checks"]["ok"] for value in (profile, eq19, zero_mode, moller)
        ),
        "rho_and_gram_reconstruction": (
            rho_q == frac(fibre["rho"]) == Fraction(819, 4000)
            and matrix(fibre["gram"]) == G
        ),
        "null_charge_basis_reconstruction": (
            matrix(fibre["null_charge_basis_S"]) == S
            and S.det() == -rho
            and matrix(fibre["charge_basis_gram"]) == S.T * G * S == rho**2 * J
        ),
        "certified_missing_leg_reconstruction": (
            moller["minimal_public_Rt_compression"]["missing_leg_C"]
            == [["-rho", "-1"], ["0", "1"]]
            and matrix(fibre["certified_missing_leg_C"]) == C
            and matrix(fibre["target_metric_J"]) == J
            and C.T * J * C == G
        ),
        "physical_charge_transport_through_missing_leg": (
            C.inv() * H0 * C == H
            and fibre["physical_transport_identity"]
            == "H_G=C^-1*diag(1,-1)*C"
        ),
        "charge_generator_reconstruction": (
            matrix(fibre["diagonal_charge_generator"]) == H0
            and matrix(fibre["transported_charge_generator"]) == H
            and H == sp.Matrix([[1, 2 / rho], [0, -1]])
        ),
        "charge_generator_involution": H**2 == sp.eye(2),
        "charge_generator_gram_invariance": sp.simplify(H.T * G + G * H)
        == sp.zeros(2),
        "charge_projector_reconstruction": (
            matrix(fibre["positive_projector"]) == Pplus
            and matrix(fibre["negative_projector"]) == Pminus
            and Pplus**2 == Pplus
            and Pminus**2 == Pminus
            and Pplus * Pminus == sp.zeros(2)
        ),
        "canonical_line_components_reconstructed": (
            matrix(line["f2"]) == f2
            and matrix(line["positive_component"]) == fplus
            and matrix(line["negative_component"]) == fminus
            and fplus + fminus == f2
        ),
        "one_sided_components_are_null": (
            frac(line["positive_self_pairing"]) == (fplus.T * G * fplus)[0] == 0
            and frac(line["negative_self_pairing"])
            == (fminus.T * G * fminus)[0]
            == 0
        ),
        "cross_pairings_are_minus_one": (
            frac(line["positive_negative_pairing"])
            == (fplus.T * G * fminus)[0]
            == -1
            and frac(line["negative_positive_pairing"])
            == (fminus.T * G * fplus)[0]
            == -1
        ),
        "full_norm_is_cross_localized": (
            frac(line["full_pairing"]) == (f2.T * G * f2)[0] == -2
            and line["localization"] == "FULL_NEGATIVE_NORM_IS_ENTIRELY_CROSS_CHARGE"
        ),
        "profile_blocks_reconstructed": (
            matrix(decomposition["full_forward_block"]) == B
            and matrix(decomposition["positive_charge_block"]) == Bplus
            and matrix(decomposition["negative_charge_block"]) == Bminus
            and Hmodule * Bplus == Bplus
            and Hmodule * Bminus == -Bminus
        ),
        "one_sided_profile_pullbacks_are_zero": (
            matrix(decomposition["positive_self_pullback"]) == plus == sp.zeros(2)
            and matrix(decomposition["negative_self_pullback"])
            == minus
            == sp.zeros(2)
        ),
        "cross_profile_pullbacks_reconstruct_effect": (
            matrix(decomposition["positive_negative_pullback"]) == pm == K4 / 2
            and matrix(decomposition["negative_positive_pullback"]) == mp == K4 / 2
            and matrix(decomposition["full_profile_effect"]) == pm + mp == K4
        ),
        "negative_Q_identification_is_refuted": (
            boundary["Q_remainder_identification"]
            == "EXACTLY_REFUTED_ON_DECLARED_FIBRE"
            and decomposition["one_sided_negative_Q_pullback"] == "ZERO"
            and minus == sp.zeros(2)
            and K4.rank() == 2
        ),
        "finite_order_lambda_boundary_replayed": (
            eq19["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
            and boundary["finite_mode_order_lambda_sector"]
            == "PROVED_WITH_Q1_ZERO_IN_PREDECESSOR"
        ),
        "zero_mode_warning_and_open_claims_replayed": (
            zero_mode["disposition"]["fixed_vacuum_charge_selection"]
            == "NOT_WELL_DEFINED_AS_AN_INVARIANT_QUOTIENT"
            and disposition["neutral_higher_composite_operator"] == "NOT_CONSTRUCTED"
            and disposition["generalized_Born_trace"] == "NOT_CONSTRUCTED"
            and disposition["physical_fourth_probability"] == "NOT_ESTABLISHED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
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
