#!/usr/bin/env python3
"""Independent verifier for the BT physical Moller defect completion."""
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
    "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-physical-moller-defect-completion-v1.schema.json",
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


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix(value):
    import sympy as sp

    return sp.Matrix([[sp.sympify(entry) for entry in row] for row in value])


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    moller = load(os.path.join(ROOT, inputs[1]["path"]))
    continuum = load(os.path.join(ROOT, inputs[2]["path"]))
    theorem = certificate["universal_completion_theorem"]
    witness = certificate["finite_exact_witness"]
    consequence = certificate["continuum_consequence"]
    disposition = certificate["disposition"]

    probabilities = [frac(value) for value in witness["outcome_probabilities"]]
    p = [sp.Rational(value.numerator, value.denominator) for value in probabilities]
    v = sp.Matrix([sp.sqrt(value) for value in p])
    e0 = sp.Matrix([1, 0, 0, 0])
    I2 = sp.eye(2)
    inclusion = sp.kronecker_product(e0, I2)
    column = sp.kronecker_product(v, I2)
    pin = inclusion * inclusion.T
    pout = sp.simplify(column * column.T)
    din = sp.eye(8) - pin
    dout = sp.eye(8) - pout

    # Reconstruct the first extension from the recorded Householder matrix,
    # then derive the second from the independently recorded defect rotation.
    H = matrix(witness["householder_outcome_matrix"])
    R = matrix(witness["defect_rotation_outcome_matrix"])
    S0 = sp.kronecker_product(H, I2)
    Udef = sp.kronecker_product(R, I2)
    S1 = sp.simplify(S0 * Udef)
    W0 = sp.simplify(S0 * din)
    W1 = sp.simplify(S1 * din)

    # Verify the Julia formula independently from the same contraction.
    julia = column.row_join(dout).col_join(
        sp.zeros(2, 2).row_join(-column.T)
    )
    exclusions = certificate["does_not_establish"]

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessor_certificates_pass": (
            moller["checks"]["ok"] and continuum["checks"]["ok"]
        ),
        "predecessor_column_isometry_is_explicit": (
            moller["physical_vacuum_moller_column"]["definition"]
            == "M_a=A_<=3 U_a I_Omega"
            and "M_a^* M_a=I2" in moller["physical_vacuum_moller_column"]["isometry"]
        ),
        "predecessor_continuum_has_all_marks": (
            continuum["seventy_five_mark_completion"]
            ["physically_intertwined_edge_marks"]
            == list(range(75))
        ),
        "fixture_probabilities_reconstruct": (
            probabilities
            == [Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 8)]
            and sum(probabilities) == 1
        ),
        "fixture_amplitude_column_reconstructs": (
            matrix(witness["outcome_amplitude_column"]) == v
        ),
        "isometries_and_projection_ranks": (
            inclusion.T * inclusion == I2
            and sp.simplify(column.T * column) == I2
            and pin.rank() == pout.rank() == 2
        ),
        "defect_ranks_are_six": (
            din.rank() == dout.rank()
            == witness["incoming_defect_rank"]
            == witness["outgoing_defect_rank"]
            == 6
        ),
        "recorded_householder_is_orthogonal_and_maps_column": (
            sp.simplify(H.T * H) == sp.eye(4) and H * e0 == v
        ),
        "recorded_defect_rotation_is_nontrivial_orthogonal": (
            R != sp.eye(4)
            and R.T * R == sp.eye(4)
            and R * e0 == e0
        ),
        "both_extensions_are_unitary": (
            sp.simplify(S0.T * S0) == sp.eye(8)
            and sp.simplify(S0 * S0.T) == sp.eye(8)
            and sp.simplify(S1.T * S1) == sp.eye(8)
            and sp.simplify(S1 * S1.T) == sp.eye(8)
        ),
        "both_extensions_have_same_column": (
            S0 * inclusion == S1 * inclusion == column
            and witness["same_column"] == "S0*I=S1*I=M"
        ),
        "defect_actions_are_distinct": W0 != W1,
        "both_defect_actions_are_partial_unitaries": (
            sp.simplify(W0.T * W0) == din
            and sp.simplify(W0 * W0.T) == dout
            and sp.simplify(W1.T * W1) == din
            and sp.simplify(W1 * W1.T) == dout
        ),
        "universal_formula_matches_both_witnesses": (
            sp.simplify(column * inclusion.T + W0 * din) == S0
            and sp.simplify(column * inclusion.T + W1 * din) == S1
            and theorem["all_completions"] == "S_W=M_a I^*+W D_in"
        ),
        "julia_formula_is_unitary": (
            julia.shape == (10, 10)
            and sp.simplify(julia.T * julia) == sp.eye(10)
            and sp.simplify(julia * julia.T) == sp.eye(10)
            and julia[:8, :2] == column
        ),
        "finite_unitary_hashes_match": (
            witness["first_unitary_sha256"]
            == hashlib.sha256(str([[str(sp.factor(S0[i, j])) for j in range(8)] for i in range(8)]).encode()).hexdigest()
            and witness["second_unitary_sha256"]
            == hashlib.sha256(str([[str(sp.factor(S1[i, j])) for j in range(8)] for i in range(8)]).encode()).hexdigest()
        ),
        "continuum_infinite_defect_has_source_witness": (
            "compactly supported sections" in consequence["dense_core"]
            and consequence["defect_dimension"]
            == "COUNTABLY_INFINITE_FOR_EVERY_a>0"
            and moller["declared_carriers"]["incoming"].startswith("C2_species")
        ),
        "minimal_new_input_is_recorded": (
            "incoming continuum" in consequence["minimal_new_input"]
            and "unitary defect map W" in consequence["minimal_new_input"]
        ),
        "nonuniqueness_is_not_promoted": (
            disposition["completion_selected_by_public_amplitudes"]
            == "EXACTLY_UNDERDETERMINED"
            and disposition["BT_asymptotic_hamiltonian_affiliation"]
            == "NOT_CONSTRUCTED"
        ),
        "spacetime_and_eq19_boundaries_are_closed": (
            disposition["spacetime_Moller_LSZ_S_operator"] == "NOT_CONSTRUCTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and any("LORENTZIAN-CAUSAL" in value for value in exclusions)
        ),
        "public_source_audit_is_scoped": (
            certificate["provenance"]["public_source_audit"]["result"].startswith(
                "No public companion"
            )
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
