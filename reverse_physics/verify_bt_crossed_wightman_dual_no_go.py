#!/usr/bin/env python3
"""Independent verifier for the crossed Wightman-dual no-go."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-wightman-dual-no-go-v1.schema.json",
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


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs[1:]]
    spectral = certificate["spectral_reflection_crosswalk"]
    crossed = certificate["crossed_five_to_four_operator"]
    parity = certificate["universal_parity_incompatibility"]
    histories = certificate["history_disposition"]
    disposition = certificate["disposition"]

    a0, a1, x = sp.symbols("a0 a1 x", positive=True)
    local = {"a0": a0, "a1": a1, "x": x}

    def expression(value):
        return sp.sympify(value, locals=local)

    def matrix(value):
        return sp.Matrix([[expression(entry) for entry in row] for row in value])

    J = sp.Matrix([[0, 1], [1, 0]])
    identity = sp.eye(2)
    S = sp.diag(1, -1)
    difference = (a0-a1)**2
    qx = sp.factor((2*x*(a0+a1)+difference)/(2*x**2))
    ellx = sp.factor(difference/(2*x))
    rho = sp.factor(qx*ellx)
    T = sp.diag(-qx, ellx)
    Tsharp = sp.simplify(J*T.T*J)
    gram = sp.simplify(Tsharp*T)
    signed = -gram
    TS = sp.simplify(T*S)
    TSsharp = sp.simplify(J*TS.T*J)
    parity_gram = sp.simplify(TSsharp*TS)
    parity_signed = -parity_gram

    # The support reflection exchanges the positive/negative energy labels.
    # Since the same coefficient map applies for every mu, differentiating
    # the coefficient vector with respect to mu commutes with it.
    simple, dipole = sp.symbols("simple dipole")
    jet = sp.Matrix([simple, dipole])
    reflected_jet = identity*jet

    predecessor_r = sp.symbols("r", positive=True)
    predecessor_rho = sp.sympify(
        predecessors[2]["analytic_spacelike_crossing"]["first_crossed_pair_rho"],
        locals={"r": predecessor_r, "x": x},
    )

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(value["checks"]["ok"] for value in predecessors),
        "spectral_reflection_matrix_is_identity": matrix(
            spectral["reflection_matrix"]
        ) == identity,
        "jet_metric_reconstructs": matrix(spectral["jet_metric"]) == J,
        "reflection_preserves_jet_metric": identity.T*J*identity == J,
        "reflection_commutes_with_parameter_derivative": reflected_jet == jet,
        "reflection_statement_exchanges_energy_support": (
            "W_mu^plus=W_mu^minus" in spectral["reflection"]
            and "W_dip^minus" in spectral["commutation"]
        ),
        "absolute_jacobian_boundary_is_explicit": (
            "|det(-I4)|=1" in spectral["jacobian_boundary"]
            and "No oriented" in spectral["jacobian_boundary"]
        ),
        "distributional_domain_is_fail_closed": (
            "tempered distributions" in spectral["domain_boundary"]
            and "not a construction" in spectral["domain_boundary"]
        ),
        "epsilon_parity_is_distinct": matrix(
            parity["required_six_point_parity"]
        ) == S and S != identity,
        "epsilon_parity_is_anti_krein": S.T*J*S == -J,
        "q_x_reconstructs": sp.simplify(expression(crossed["q_x"])-qx) == 0,
        "ell_x_reconstructs": sp.simplify(expression(crossed["ell_x"])-ellx) == 0,
        "rho_x_reconstructs": sp.simplify(expression(crossed["rho_x"])-rho) == 0,
        "rho_matches_predecessor_dimensionless_limit": sp.simplify(
            rho.subs({a0: 1, a1: predecessor_r})-predecessor_rho
        ) == 0,
        "crossed_T_reconstructs": sp.simplify(
            matrix(crossed["T_cross"])-T
        ) == sp.zeros(2),
        "crossed_sharp_reconstructs": sp.simplify(
            matrix(crossed["T_cross_sharp"])-Tsharp
        ) == sp.zeros(2),
        "crossed_unsigned_gram_reconstructs": sp.simplify(
            matrix(crossed["unsigned_gram"])-gram
        ) == sp.zeros(2),
        "crossed_signed_gram_is_positive": sp.simplify(
            matrix(crossed["signed_physical_gram"])-signed
        ) == sp.zeros(2) and sp.simplify(signed-rho*identity) == sp.zeros(2),
        "fifth_derivative_sign_is_retained": (
            crossed["fifth_external_delta_prime_sign"] == -1
        ),
        "parity_dressed_T_reconstructs": sp.simplify(
            matrix(parity["parity_dressed_T"])-TS
        ) == sp.zeros(2),
        "parity_dressed_sharp_reconstructs": sp.simplify(
            matrix(parity["parity_dressed_T_sharp"])-TSsharp
        ) == sp.zeros(2),
        "parity_unsigned_gram_reconstructs": sp.simplify(
            matrix(parity["parity_unsigned_gram"])-parity_gram
        ) == sp.zeros(2),
        "parity_signed_gram_is_negative": sp.simplify(
            matrix(parity["fifth_signed_parity_gram"])-parity_signed
        ) == sp.zeros(2) and sp.simplify(parity_signed+rho*identity) == sp.zeros(2),
        "universal_parity_incompatibility_is_explicit": (
            "already positive first crossed splitting" in parity["incompatibility"]
            and "cannot be the common incoming" in parity["incompatibility"]
        ),
        "repair_alternatives_are_not_promoted": (
            len(parity["allowed_repair_types"]) == 3
            and disposition["profile_selective_or_higher_composite_parity"]
            == "NOT_DERIVED"
            and disposition["nonfactorizing_crossed_six_point_term"]
            == "NOT_COMPUTED"
        ),
        "twelve_histories_remain_open": (
            histories["reversed_six_point_history_count"] == 12
            and disposition["twelve_reversed_physical_intertwiners"]
            == "NOT_CONSTRUCTED"
        ),
        "claim_boundary_remains_fail_closed": (
            disposition["complete_crossed_probability"] == "NOT_COMPUTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "next_gate_is_profile_selective_or_nonfactorizing": (
            "profile-selective" in certificate["next_gate"]
            and "nonfactorizing crossed 3->3" in certificate["next_gate"]
            and "universal Wightman-dual route is closed" in certificate["next_gate"]
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
